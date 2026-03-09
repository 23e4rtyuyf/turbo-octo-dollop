from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db, Organization
from app.services.billing import create_checkout_session, handle_webhook, PRICING_PLANS

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])


@router.get("/plans")
async def list_plans():
    """List all available pricing plans."""
    return {
        name: {
            "price_cents": plan["price"],
            "email_quota": plan["email_quota"],
            "features": plan["features"],
        }
        for name, plan in PRICING_PLANS.items()
    }


@router.post("/checkout")
async def create_checkout(plan: str, org_id: str = "default"):
    """Create a Stripe checkout session to upgrade."""
    try:
        url = await create_checkout_session(
            plan=plan,
            org_id=org_id,
            success_url="https://yourdomain.com/billing/success",
            cancel_url="https://yourdomain.com/billing/cancel",
        )
        return {"checkout_url": url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    try:
        result = await handle_webhook(payload, sig)
        if result["action"] == "upgrade":
            org = db.query(Organization).filter(Organization.slug == result["org_id"]).first()
            if org:
                plan_data = PRICING_PLANS[result["plan"]]
                org.plan = result["plan"]
                org.email_quota = plan_data["email_quota"]
                db.commit()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
