from fastapi import APIRouter
from pydantic import BaseModel
from app.services.agentic_service import search_products_nl

router = APIRouter()

class AgenticSearchRequest(BaseModel):
    query: str
    merchant_id: str
    offset: int = 0
    limit: int = 10

@router.post("/agentic-search")
async def agentic_search(req: AgenticSearchRequest):
    return await search_products_nl(req.query, req.merchant_id, req.offset, req.limit)
