from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.email import InboundEmail, ClassifiedEmail
from app.services.classifier import classify_email
from app.services.router import route_email
from app.db.database import get_db, EmailLog

router = APIRouter(prefix="/api/v1", tags=["inbound"])


@router.post("/inbound", response_model=ClassifiedEmail)
async def receive_email(email: InboundEmail, db: Session = Depends(get_db)):
    """Receive an inbound email, classify it with AI, and route it."""
    try:
        classified = await classify_email(email)
        routed_to = await route_email(classified)
        classified.routed_to = routed_to

        # Log to database
        log = EmailLog(
            sender=email.sender,
            recipient=email.recipient,
            subject=email.subject,
            body_preview=email.body_plain[:500],
            category=classified.category.value,
            confidence=classified.confidence,
            reasoning=classified.reasoning,
            routed_to=routed_to,
        )
        db.add(log)
        db.commit()

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
