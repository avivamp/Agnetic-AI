import os
import logging
import json
import numpy as np
import time
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from pydantic import BaseModel, ValidationError
from openai import OpenAI
from app.services.search_service import pc, get_embedding, get_index_name
from app.config.categories import CATEGORY_EMBEDDINGS
from app.models.search_log import SearchLog
from app.services.ranking_service import rank_products

logger = logging.getLogger("app.services.agentic_service")
logger.setLevel(logging.INFO)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------------------
# Filter Schema for Validation
# ----------------------------
class FilterSchema(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None

# ----------------------------
# Category Mapping
# ----------------------------
def best_category(query: str) -> str:
    """Find most relevant category by cosine similarity with precomputed embeddings."""
    q_vec = get_embedding(query)
    best_cat, best_sim = None, -1

    for cat, c_vec in CATEGORY_EMBEDDINGS.items():
        sim = np.dot(q_vec, c_vec) / (np.linalg.norm(q_vec) * np.linalg.norm(c_vec))
        if sim > best_sim:
            best_cat, best_sim = cat, sim

    logger.info(f"[AgenticSearch] Category mapping → {best_cat} (score={best_sim:.3f})")
    return best_cat

# ----------------------------
# Filter Extraction
# ----------------------------
async def extract_filters_with_llm(query: str) -> dict:
    """Extract brand/price filters with LLM, map category separately."""
    prompt = f"""
    Extract structured filters from this shopping search query.
    Only extract brand and price range (price_min, price_max). 
    Do NOT guess category — category will be mapped separately.
    Return JSON only.

    Query: {query}
    """

    logger.info(f"[AgenticSearch] Extracting filters for query: {query}")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"}  # ✅ ensures JSON output
    )

    raw_content = response.choices[0].message.content.strip()
    logger.info(f"[AgenticSearch] Raw LLM content: {raw_content}")

    try:
        filters = json.loads(raw_content)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.warning(f"[AgenticSearch] Failed to parse filters, ignoring. Error: {e}")
        filters = {}

    # Always map category deterministically
    filters["category"] = best_category(query)

    # ✅ Validate with Pydantic schema
    try:
        filters = FilterSchema(**filters).dict(exclude_none=True)
    except ValidationError as e:
        logger.warning(f"[AgenticSearch] Validation failed: {e}")
        filters = {}

    logger.info(f"[AgenticSearch] LLM-extracted filters (validated): {filters}")
    return filters

# ----------------------------
# Main Search
# ----------------------------
async def search_products_nl(
        query: str, 
        merchant_id: str, 
        db: AsyncSession, 
        offset: int = 0, 
        limit: int = 10,
        context: Optional[Dict[str, Any]] = None
    ):

    """Perform natural language search with embeddings + Pinecone + filters."""
    logger.info(f"[Metrics] Query: {query}")
    
    # Extract filters (safe fallback)
    filters = await extract_filters_with_llm(query)

    # Build Pinecone filter structure
    structured_filter = {}
    if filters.get("category"):
        structured_filter["category"] = filters["category"]
    if filters.get("brand"):
        structured_filter["brand"] = filters["brand"]
    if "price_min" in filters or "price_max" in filters:
        structured_filter["price"] = {}
        if filters.get("price_min") is not None:
            structured_filter["price"]["$gte"] = filters["price_min"]
        if filters.get("price_max") is not None:
            structured_filter["price"]["$lte"] = filters["price_max"]

    logger.info(f"[AgenticSearch] Structured filters applied: {structured_filter}")

    # Enrich query with context (soft influence)
    enriched_query = query
    if context:
        enrich_parts = []
        if context.get("cabin"):
            enrich_parts.append(f"cabin: {context['cabin']}")
        if context.get("loyalty_tier"):
            enrich_parts.append(f"loyalty: {context['loyalty_tier']}")
        if context.get("trip"):
            trip = context["trip"]
            enrich_parts.append(f"trip from {trip.get('from')} to {trip.get('to')}")
        enriched_query = query + " | " + ", ".join(enrich_parts)
        logger.info(f"[AgenticSearch] Enriched query with context: {enriched_query}")

    # Generate embedding
    logger.info("[AgenticSearch] Generating embedding...")
    query_embedding = get_embedding(enriched_query)

    # Choose merchant-specific Pinecone index
    index_name = get_index_name(merchant_id)
    index = pc.Index(index_name)

    # Query Pinecone
    pinecone_query = {
        "vector": query_embedding,
        "top_k": offset + limit,
        "include_metadata": True
    }
    if structured_filter:
        pinecone_query["filter"] = structured_filter

    # Log params safely
    qlog = dict(pinecone_query)
    qlog["vector"] = f"[{len(query_embedding)}-dim embedding]"
    logger.info(f"[AgenticSearch] Pinecone query params: {json.dumps(qlog, indent=2)}")

    # Measure latency
    start = time.time()
    try:
        results = index.query(**pinecone_query)
    except Exception as e:
        logger.error(f"[AgenticSearch] Pinecone query failed: {e}")
        return {"interpreted_filters": {}, "results": []}
    duration = int((time.time() - start) * 1000)

    matches = results.get("matches", [])[offset: offset + limit]

    # Rank the mathes
    matches = rank_products(matches, merchant_id, context)

    # Fallback if no results with filters
    if not matches and "filter" in pinecone_query:
        logger.warning("[AgenticSearch] No results with filters. Retrying without filters...")
        pinecone_query.pop("filter")
        results = index.query(**pinecone_query)
        matches = results.get("matches", [])[offset: offset + limit]

    # Extract top result info
    top_result_id, top_result_score = None, None
    if matches:
        top_result_id = matches[0].get("id")
        top_result_score = matches[0].get("score")
        logger.info(f"[AgenticSearch] Example result metadata: {matches[0].get('metadata', {})}")
    else:
        logger.warning("[AgenticSearch] Still 0 results after fallback.")

    # Step 8: Save log in Supabase (via SQLAlchemy model)
    log = SearchLog(
        merchant_id=merchant_id,
        session_id="demo-session",   # you can later replace with real session tracking
        query=query,
        query_embedding=query_embedding,   # JSONB in table
        latency_ms=duration,
        results_count=len(results.get("matches", [])),
        top_result_id=top_result_id,
        top_result_score=top_result_score,
        error_flag=False,
        client_type="mobile_app",
        country="UAE"
    )
    db.add(log)
    await db.commit()

    # Step 9: Return safe JSON serializable response
    return {
        "interpreted_filters": json.loads(json.dumps(structured_filter)),  # safe dict
        "context_used": context or {},
        "results": [
            {
                "id": match.get("id"),
                "score": match.get("score"),
                "metadata": match.get("metadata", {})
            }
            for match in matches
        ]
    }
