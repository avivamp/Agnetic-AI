import os, json
from openai import OpenAI
from app.config.categories import CATEGORIES

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

embeddings = {}
for cat in CATEGORIES:
    resp = client.embeddings.create(model="text-embedding-3-small", input=cat)
    embeddings[cat] = resp.data[0].embedding

with open("backend/app/config/category_embeddings.json", "w") as f:
    json.dump(embeddings, f)

print("✅ Saved category embeddings to backend/app/config/category_embeddings.json")
