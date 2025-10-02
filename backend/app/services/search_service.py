import os
import json
from openai import OpenAI
from pinecone import Pinecone


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# merchant → index mapping
INDEX_MAP = {
    "airlinex": "products-airlinex",
    "default": "products-airlinex"
}

def get_index_name(merchant_id: str):
    return INDEX_MAP.get(merchant_id, INDEX_MAP["default"])

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def search_products(query: str, top_k: int = 5, filters=None, merchant_id=None):
    vector = get_embedding(query)
    index_name = get_index_name(merchant_id)
    index = pc.Index(index_name)

    pinecone_query = {
        "vector": vector,
        "top_k": top_k,
        "include_metadata": True,
    }
    if filters:
        pinecone_query["filter"] = filters

    # Log without dumping the whole embedding vector
    query_log = {**pinecone_query, "vector": f"[{len(vector)}-dim embedding]"}
    logger.info(f"[Pinecone Query] {json.dumps(query_log, indent=2)}")

    results = index.query(**pinecone_query)

    return [
        {
            "id": match["id"],
            "score": match["score"],
            "metadata": match["metadata"]
        }
        for match in results["matches"]
    ]
