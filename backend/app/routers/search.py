from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.search_service import search_products

router = APIRouter()

# Request schema
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    filters: Optional[Dict[str, Any]] = None
    merchant_id: Optional[str] = None

# Response schema (optional for clarity)
class SearchResponse(BaseModel):
    results: list

@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    results = search_products(
        query=request.query,
        top_k=request.top_k,
        filters=request.filters,
        merchant_id=request.merchant_id
    )
    return {"results": results}
