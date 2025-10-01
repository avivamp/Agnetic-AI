import re
from app.services.search_service import get_embedding, get_index_name, pc

def extract_filters(nl_query: str) -> dict:
    filters = {}

    # Example extraction rules (replace with LLM later)
    if "perfume" in nl_query.lower():
        filters["category"] = "perfume"
    if "lavender" in nl_query.lower():
        filters["notes"] = "lavender"

    # Regex for price ranges
    match = re.search(r'(\d+)\s*(?:to|-|between)\s*(\d+)', nl_query.lower())
    if match:
        filters["price"] = {"$gte": int(match.group(1)), "$lte": int(match.group(2))}

    # Keywords for gifting
    if "gift" in nl_query.lower() or "gifting" in nl_query.lower():
        filters["use_case"] = "gift"

    return filters

def search_products_nl(nl_query: str, merchant_id: str):
    filters = extract_filters(nl_query)
    vector = get_embedding(nl_query)
    index = pc.Index(get_index_name(merchant_id))

    results = index.query(
        vector=vector,
        top_k=10,
        filter=filters if filters else None,
        include_metadata=True
    )

    return {
        "interpreted_filters": filters,
        "results": [
            {"id": m["id"], "score": m["score"], "metadata": m["metadata"]}
            for m in results["matches"]
        ]
    }
