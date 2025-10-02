import os
import json
from pathlib import Path
from openai import OpenAI

# Define categories here (edit if needed)
CATEGORIES = [
    "Fragrance & Beauty",
    "Electronics",
    "Comfort",
    "Food & Beverage",
    "Connectivity",
    "Travel Essentials",
    "Baby & Kids",
    "Luxury Goods"
]

client = OpenAI(api_key="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")

def get_embedding(text: str, model="text-embedding-3-small"):
    """Fetch embedding from OpenAI."""
    response = client.embeddings.create(model=model, input=text)
    return response.data[0].embedding

def main():
    category_embeddings = {}

    for cat in CATEGORIES:
        print(f"🔹 Generating embedding for: {cat}")
        category_embeddings[cat] = get_embedding(cat)

    # Path to backend config file
    config_path = Path(__file__).resolve().parent.parent / "backend" / "app" / "config" / "category_embeddings.py"

    # Write directly to Python config file
    with open(config_path, "w") as f:
        f.write("# Auto-generated category embeddings\n")
        f.write("CATEGORY_EMBEDDINGS = ")
        json.dump(category_embeddings, f, indent=2)

    print(f"✅ category_embeddings.py generated successfully at {config_path}")

if __name__ == "__main__":
    main()
