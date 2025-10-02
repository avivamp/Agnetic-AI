import os
import logging
from openai import OpenAI
from app.services.search_service import pc, get_embedding, get_index_name

logger = logging.getLogger("app.services.agentic_service")
logger.setLevel(logging.INFO)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Only allow these filters to be applied
VALID_FILTER_KEYS = {"category", "brand", "price"}


async def extract_filters_with_llm(query: str) -> dict:
    """Ask LLM to extract structured filters from natural language query."""
    prompt = f"""
    Extract filters from this shopping search query. 
    Allowed keys: category, brand, price_min, price_max.
    If price range is given, output both min and max. 
    Return JSON only.

    Query: {query}
    """

    logger.info(f"[AgenticSearch] Extracting filters for query: {query}")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    try:
        filters = eval(response["choices"][0]["message"]["content"])
    except Exception as e:
        logger.warning(f"[AgenticSearch] Failed to parse filters: {e}")
        filters = {}

    logger.info(f"[AgenticSearch] LLM-extracted filters: {filters}")
    return filters


async def search_products_nl(query: str, merchant_id: str, offset: int = 0, limit: int = 10):
    """Perform natural language search with embeddings + Pinecone + filters."""
    # Step 1: Extract filters
    filters = await extract_filters_with_llm(query)

    # Step 2: Keep only valid filters
    structured_filter = {}
    if "category" in filters:
        structured_filter["category"] = filters["category"]
    if "brand" in filters:
        structured_filter["brand"] = filters["brand"]
    if "price_min" in filters or "price_max" in filters:
        structured_filter["price"] = {}
        if "price_min" in filters:
            structured_filter["price"]["$gte"] = filters["price_min"]
        if "price_max" in filters:
            structured_filter["price"]["$lte"] = filters["price_max"]

    logger.info(f"[AgenticSearch] Structured filters applied: {structured_filter}")

    # Step 3: Generate embedding
    logger.info("[AgenticSearch] Generating embedding...")
    query_embedding = get_embedding(query)

    # Step 4: Choose merchant-specific Pinecone index
    index_name = get_index_name(merchant_id)
    index = pc.Index(index_name)

    # Step 5: Query Pinecone with filters
    pinecone_query = {
        "vector": query_embedding,
        "top_k": offset + limit,
        "include_metadata": True
    }
    if structured_filter:
        pinecone_query["filter"] = structured_filter

    logger.info(f"[AgenticSearch] Pinecone query params: {pinecone_query}")

    results = index.query(**pinecone_query)
    matches = results.get("matches", [])[offset: offset + limit]

    # Step 6: Fallback if no results
    if not matches and "filter" in pinecone_query:
        logger.warning("[AgenticSearch] No results with filters. Retrying without filters...")
        pinecone_query.pop("filter")
        results = index.query(**pinecone_query)
        matches = results.get("matches", [])[offset: offset + limit]

    # Step 7: Log sample product metadata
    if matches:
        logger.info(f"[AgenticSearch] Example result metadata: {matches[0]['metadata']}")
    else:
        logger.warning("[AgenticSearch] Still 0 results after fallback.")

    return {
        "interpreted_filters": structured_filter,
        "results": matches
    }
