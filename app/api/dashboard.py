from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db, EmailLog

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_stats(days: int = 30, org_id: str = "default", db: Session = Depends(get_db)):
    """Get email routing statistics."""
    since = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)

    total = db.query(EmailLog).filter(
        EmailLog.organization_id == org_id,
        EmailLog.created_at >= since,
    ).count()

    by_category = dict(
        db.query(EmailLog.category, func.count(EmailLog.id))
        .filter(EmailLog.organization_id == org_id, EmailLog.created_at >= since)
        .group_by(EmailLog.category)
        .all()
    )

    avg_confidence = (
        db.query(func.avg(EmailLog.confidence))
        .filter(EmailLog.organization_id == org_id, EmailLog.created_at >= since)
        .scalar()
        or 0
    )

    recent = (
        db.query(EmailLog)
        .filter(EmailLog.organization_id == org_id)
        .order_by(EmailLog.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "period_days": days,
        "total_processed": total,
        "by_category": by_category,
        "avg_confidence": round(float(avg_confidence), 3),
        "recent_emails": [
            {
                "id": e.id,
                "sender": e.sender,
                "subject": e.subject,
                "category": e.category,
                "confidence": e.confidence,
                "routed_to": e.routed_to,
                "created_at": str(e.created_at),
            }
            for e in recent
        ],
    }


@router.get("/usage")
async def get_usage(org_id: str = "default", db: Session = Depends(get_db)):
    """Get current billing period usage."""
    from app.db.database import Organization

    org = db.query(Organization).filter(Organization.slug == org_id).first()
    if not org:
        return {"emails_used": 0, "email_quota": 100, "plan": "free"}
    return {
        "emails_used": org.emails_used,
        "email_quota": org.email_quota,
        "plan": org.plan,
        "percent_used": round(org.emails_used / max(org.email_quota, 1) * 100, 1),
    }
