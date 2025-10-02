from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.db import get_db
from app.models.search_log import SearchLog

router = APIRouter(prefix="/metrics")

@router.get("/")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """Return aggregated search metrics from DB instead of in-memory stats."""
    
    # Total queries
    total_queries = await db.scalar(select(func.count(SearchLog.id)))

    # Average latency
    avg_latency = await db.scalar(select(func.avg(SearchLog.latency_ms)))

    # Top 5 search terms
    top_terms_query = await db.execute(
        select(SearchLog.query, func.count(SearchLog.query))
        .group_by(SearchLog.query)
        .order_by(func.count(SearchLog.query).desc())
        .limit(5)
    )
    top_terms = {q: c for q, c in top_terms_query.all()}

    return {
        "total_queries": total_queries or 0,
        "avg_latency_ms": round(avg_latency or 0, 2),
        "top_terms": top_terms
    }
