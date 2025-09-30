# Stub for LLM/NLP integration.
# Replace this with your preferred provider (OpenAI, local HF model, etc.)
# For Phase 1 we just do a naive parse.

from typing import Dict

def parse_query_intent(query: str) -> Dict:
    q = query.lower()
    intent = {}
    # toy rules
    if "whisky" in q or "whiskey" in q:
        intent["category"] = "whisky"
    if "perfume" in q:
        intent["category"] = "perfume"
    # detect price mentions like 'under 200'
    import re
    m = re.search(r"under\s+(\d+)", q)
    if m:
        intent["price_max"] = float(m.group(1))
    return intent
