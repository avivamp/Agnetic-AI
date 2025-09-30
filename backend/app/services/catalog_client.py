# Replace with real catalog API client (read-only) or DB connector.
from typing import List, Dict

MOCK_PRODUCTS = [
    {"sku": "WX-1234", "name": "Highland Single Malt Whisky 12Y", "price": 185.0, "currency": "AED", "thumbnail": "", "description": "Premium single malt."},
    {"sku": "PF-9012", "name": "Eau de Parfum 50ml", "price": 95.0, "currency": "AED", "thumbnail": "", "description": "Classic perfume."},
    {"sku": "SN-1001", "name": "Vegan Snack Bars (10 pack)", "price": 18.0, "currency": "AED", "thumbnail": "", "description": "Plant-based snack."}
]

def fetch_products(intent: Dict, filters: Dict) -> List[Dict]:
    # naive filter
    data = MOCK_PRODUCTS
    if "price_max" in intent:
        data = [p for p in data if p.get("price", 0) <= intent["price_max"]]
    # Add other filters based on real catalog schema
    return data
