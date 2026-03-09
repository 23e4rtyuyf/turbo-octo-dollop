from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_stats():
    """Get email routing statistics. (Coming soon)"""
    return {
        "total_processed": 0,
        "by_category": {},
        "message": "Dashboard stats coming in a future update",
    }
