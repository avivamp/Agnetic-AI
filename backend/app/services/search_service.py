import os
from openai import OpenAI
from pinecone import Pinecone

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
INDEX_NAME = os.getenv("PINECONE_INDEX", "products-airlinex")

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def search_products(query: str, top_k: int = 5, filters=None, merchant_id=None):
    vector = get_embedding(query)
    index = pc.Index(INDEX_NAME)

    pinecone_query = {
        "vector": vector,
        "top_k": top_k,
        "include_metadata": True,
    }
    if filters:
        pinecone_query["filter"] = filters

    results = index.query(**pinecone_query)

    return [
        {
            "id": match["id"],
            "score": match["score"],
            "metadata": match["metadata"]
        }
        for match in results["matches"]
    ]
