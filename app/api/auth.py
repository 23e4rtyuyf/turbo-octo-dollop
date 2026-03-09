import secrets
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.db.database import get_db, APIKey, Organization

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header), db: Session = Depends(get_db)):
    """Verify API key and return the organization."""
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key. Include X-API-Key header.")

    key_record = db.query(APIKey).filter(APIKey.key == api_key, APIKey.is_active == True).first()
    if not key_record:
        raise HTTPException(status_code=403, detail="Invalid or revoked API key.")

    org = db.query(Organization).filter(Organization.slug == key_record.organization_id).first()
    if org and org.email_quota > 0 and org.emails_used >= org.email_quota:
        raise HTTPException(status_code=429, detail="Monthly email quota exceeded. Upgrade your plan.")

    return key_record


@router.post("/api-key")
async def generate_api_key(name: str = "default", org_id: str = "default", db: Session = Depends(get_db)):
    """Generate a new API key."""
    key = f"air_{secrets.token_urlsafe(32)}"
    api_key = APIKey(key=key, name=name, organization_id=org_id)
    db.add(api_key)
    db.commit()
    return {"api_key": key, "name": name, "message": "Save this key — it won't be shown again."}


@router.get("/api-keys")
async def list_api_keys(org_id: str = "default", db: Session = Depends(get_db)):
    """List all API keys for an organization (keys are masked)."""
    keys = db.query(APIKey).filter(APIKey.organization_id == org_id).all()
    return [
        {
            "id": k.id,
            "name": k.name,
            "key_preview": f"{k.key[:8]}...",
            "is_active": k.is_active,
            "created_at": str(k.created_at),
        }
        for k in keys
    ]


@router.delete("/api-key/{key_id}")
async def revoke_api_key(key_id: int, db: Session = Depends(get_db)):
    """Revoke an API key."""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    key.is_active = False
    db.commit()
    return {"message": "API key revoked"}
