from fastapi import APIRouter, Query
from app.services.search_service import search_products

router = APIRouter()

@router.get("/search")
async def search(query: str = Query(..., description="Search query")):
    results = search_products(query)
    return {"results": results}
