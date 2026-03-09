from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/api-key")
async def generate_api_key():
    """Generate an API key. (Coming soon)"""
    return {"message": "API key auth coming in a future update"}
