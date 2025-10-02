from fastapi import APIRouter

router = APIRouter(prefix="/metrics")

stats = {
    "total_queries": 0,
    "top_terms": {},
}

def log_query(query: str):
    stats["total_queries"] += 1
    stats["top_terms"][query] = stats["top_terms"].get(query, 0) + 1

@router.get("/")
async def get_metrics():
    return stats
