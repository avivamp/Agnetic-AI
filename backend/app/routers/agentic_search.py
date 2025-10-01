from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.agentic_service import search_products_nl

router = APIRouter()

class AgenticSearchRequest(BaseModel):
    query: str
    merchant_id: Optional[str] = None
    limit: Optional[int] = 10
    offset: Optional[int] = 0

@router.post("/agentic-search")
async def agentic_search(request: AgenticSearchRequest):
    return search_products_nl(
        nl_query=request.query,
        merchant_id=request.merchant_id,
        limit=request.limit,
        offset=request.offset
    )
