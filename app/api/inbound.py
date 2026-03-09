from fastapi import APIRouter, HTTPException
from app.models.email import InboundEmail, ClassifiedEmail
from app.services.classifier import classify_email
from app.services.router import route_email

router = APIRouter(prefix="/api/v1", tags=["inbound"])


@router.post("/inbound", response_model=ClassifiedEmail)
async def receive_email(email: InboundEmail):
    """Receive an inbound email, classify it with AI, and route it."""
    try:
        # Step 1: Classify
        classified = await classify_email(email)

        # Step 2: Route
        routed_to = await route_email(classified)
        classified.routed_to = routed_to

        return classified

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/classify", response_model=ClassifiedEmail)
async def classify_only(email: InboundEmail):
    """Classify an email without routing (for testing)."""
    try:
        return await classify_email(email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")
