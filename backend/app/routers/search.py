from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import uuid
from ..services.llm import parse_query_intent
from ..services.ranker import rank_products
from ..services.catalog_client import fetch_products

router = APIRouter()

class Product(BaseModel):
    sku: str
    name: str
    price: float
    currency: str
    thumbnail: Optional[str] = None
    score: Optional[float] = None
    description: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    locale: Optional[str] = "en-AE"
    currency: Optional[str] = "AED"
    filters: Optional[dict] = None
    paging: Optional[dict] = {"page": 1, "size": 10}

class SearchResponse(BaseModel):
    results: List[Product]
    diagnostics: dict

@router.post("/search", response_model=SearchResponse)
def search_products(req: SearchRequest):
    qid = str(uuid.uuid4())
    intent = parse_query_intent(req.query)
    products = fetch_products(intent=intent, filters=req.filters or {})
    ranked = rank_products(products=products, intent=intent)

    return {
        "results": ranked,
        "diagnostics": {
            "qid": qid,
            "intent": intent,
            "strategy": "mock-llm + mock-ranker",
        },
    }

@router.get("/products/{sku}", response_model=Product)
def get_product(sku: str):
    products = fetch_products(intent={}, filters={})
    for p in products:
        if p["sku"] == sku:
            return p
    return {"sku": sku, "name": "Not found", "price": 0.0, "currency": "AED"}

@router.get("/diag/{qid}")
def diagnostics(qid: str):
    return {"qid": qid, "status": "ok", "note": "Diagnostics stub"}
