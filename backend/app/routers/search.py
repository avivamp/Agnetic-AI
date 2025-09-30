from fastapi import APIRouter
from pydantic import BaseModel
from app.services.search_service import search_products

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@router.post("/search")
async def search(req: SearchRequest):
    return await search_products(req.query, req.top_k)
