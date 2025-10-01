import os
from openai import OpenAI
from pinecone import Pinecone

# Initialize clients
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))  # already in your env

INDEX_NAME = "products-airlinex"

def get_embedding(text: str) -> list[float]:
    """Call OpenAI API to get embeddings"""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def search_products(query: str, top_k: int = 5):
    """Search Pinecone using OpenAI embeddings"""
    # Get query vector
    vector = get_embedding(query)

    # Query Pinecone
    index = pc.Index(INDEX_NAME)
    results = index.query(
        vector=vector,
        top_k=top_k,
        include_metadata=True
    )

    return [
        {
            "id": match["id"],
            "score": match["score"],
            "metadata": match["metadata"]
        }
        for match in results["matches"]
    ]
