import stripe
from app.config import settings

stripe.api_key = getattr(settings, 'stripe_secret_key', '')

PRICING_PLANS = {
    "free": {
        "price": 0,
        "email_quota": 100,
        "features": ["basic_classification", "email_routing"],
    },
    "pro": {
        "price": 4900,
        "price_id": "price_pro_monthly",
        "email_quota": 5000,
        "features": ["basic_classification", "email_routing", "slack_integration", "analytics", "custom_rules"],
    },
    "business": {
        "price": 19900,
        "price_id": "price_business_monthly",
        "email_quota": 50000,
        "features": ["all_pro", "webhook_integration", "api_access", "priority_support", "custom_categories"],
    },
    "enterprise": {
        "price": 99900,
        "price_id": "price_enterprise_monthly",
        "email_quota": -1,
        "features": ["all_business", "sso", "sla", "dedicated_support", "white_label"],
    },
}


async def create_checkout_session(plan: str, org_id: str, success_url: str, cancel_url: str) -> str:
    """Create a Stripe checkout session for upgrading."""
    plan_data = PRICING_PLANS.get(plan)
    if not plan_data or plan == "free":
        raise ValueError("Invalid plan")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price": plan_data["price_id"], "quantity": 1}],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"org_id": org_id, "plan": plan},
    )
    return session.url


async def handle_webhook(payload: bytes, sig_header: str) -> dict:
    """Handle Stripe webhook events."""
    endpoint_secret = getattr(settings, 'stripe_webhook_secret', '')
    event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        return {
            "action": "upgrade",
            "org_id": session["metadata"]["org_id"],
            "plan": session["metadata"]["plan"],
        }
    elif event["type"] == "customer.subscription.deleted":
        return {"action": "downgrade", "plan": "free"}

    return {"action": "ignored"}
