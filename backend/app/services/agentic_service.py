import os
import json
import logging
from openai import OpenAI
from app.services.search_service import get_embedding, get_index_name, pc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_filters_with_llm(nl_query: str) -> dict:
    """
    Use GPT-4o-mini to extract structured filters from natural language.
    """
    system_prompt = """
    You are a product search parser. 
    Convert natural language product queries into a JSON object of filters.
    Supported fields: category, brand, notes, use_case, price (with $gte/$lte).
    Use lowercase keys. Omit fields if not present.
    Respond ONLY with valid JSON, no extra text.
    """

    logger.info(f"[AgenticSearch] Extracting filters for query: {nl_query}")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": nl_query}
        ],
        temperature=0
    )

    try:
        filters = json.loads(response.choices[0].message.content.strip())
        logger.info(f"[AgenticSearch] LLM-extracted filters: {filters}")
    except Exception as e:
        logger.error(f"[AgenticSearch] Failed to parse filters: {e}")
        filters = {}

    return filters

def search_products_nl(nl_query: str, merchant_id: str, limit: int = 10, offset: int = 0):
    # 1. Extract filters with LLM
    filters = extract_filters_with_llm(nl_query)

    # 2. Generate embedding
    logger.info("[AgenticSearch] Generating embedding...")
    vector = get_embedding(nl_query)

    # 3. Select Pinecone index based on merchant
    index_name = get_index_name(merchant_id)
    logger.info(f"[AgenticSearch] Using Pinecone index: {index_name}")
    index = pc.Index(index_name)

    # 4. Query Pinecone with pagination
    pinecone_query = {
        "vector": vector,
        "top_k": limit + offset,  # fetch extra, then slice manually
        "include_metadata": True,
    }
    if filters:
        pinecone_query["filter"] = filters

    logger.info(f"[AgenticSearch] Pinecone query params: {pinecone_query}")

    results = index.query(**pinecone_query)
    matches = results.get("matches", [])[offset: offset + limit]

    logger.info(f"[AgenticSearch] Retrieved {len(matches)} results after pagination")

    # 5. Return structured response
    return {
        "interpreted_filters": filters,
        "pagination": {"limit": limit, "offset": offset, "total_fetched": len(matches)},
        "results": [
            {"id": m["id"], "score": m["score"], "metadata": m["metadata"]}
            for m in matches
        ]
    }
