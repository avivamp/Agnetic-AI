import os
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

# Config
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "pcsk_4VBUYR_FxWc6NekokadYpMEcXY6W95PhWQBCTpAHgVZ7kb5NZ2bCAAjfcE9wX7AEsYRF4T")
INDEX_NAME = "products-airlinex"

# Init Pinecone + HuggingFace model once
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)
model = SentenceTransformer("all-MiniLM-L6-v2")

async def search_products(query: str, top_k: int = 5):
    # Convert query to embedding
    embedding = model.encode([query])[0].tolist()

    # Query Pinecone
    results = index.query(vector=embedding, top_k=top_k, include_metadata=True)

    # Format results
    items = []
    for match in results["matches"]:
        items.append({
            "id": match["id"],
            "score": match["score"],
            "name": match["metadata"]["name"],
            "category": match["metadata"]["category"],
            "price": match["metadata"]["price"],
            "description": match["metadata"]["description"]
        })

    return {"query": query, "results": items}
