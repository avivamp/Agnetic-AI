# Stub ranker. Replace with vector search + cross-encoder etc.
from typing import List, Dict

def rank_products(products: List[Dict], intent: Dict) -> List[Dict]:
    # naive scoring based on price and category match
    scored = []
    for p in products:
        score = 0.5
        if intent.get("category") and intent["category"].lower() in p["name"].lower():
            score += 0.3
        if "price_max" in intent and p.get("price") is not None and p["price"] <= intent["price_max"]:
            score += 0.2
        p2 = dict(p)
        p2["score"] = round(score, 2)
        scored.append(p2)
    # sort desc by score
    scored.sort(key=lambda x: x.get("score", 0), reverse=True)
    return scored
