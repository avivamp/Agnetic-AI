from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from typing import Optional, Dict, Any
from app.services.agentic_service import search_products_nl

router = APIRouter()

class AgenticSearchRequest(BaseModel):
    query: str
    merchant_id: str
    offset: int = 0
    limit: int = 10
    context: Optional[Dict[str, Any]] = None

@router.post("/agentic-search")
async def agentic_search(
    req: AgenticSearchRequest,
    db: AsyncSession = Depends(get_db)   # ✅ inject DB session
):
    return await search_products_nl(
        query=req.query,
        merchant_id=req.merchant_id,
        db=db,                          # ✅ pass DB session
        offset=req.offset,
        limit=req.limit,
        context=req.context
    )