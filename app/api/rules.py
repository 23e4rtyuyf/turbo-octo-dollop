from fastapi import APIRouter
from app.models.email import EmailCategory
from app.models.rule import RoutingRule, RoutingDestination
from app.services.router import custom_rules, DEFAULT_RULES

router = APIRouter(prefix="/api/v1/rules", tags=["rules"])


@router.get("/")
async def list_rules():
    """List all active routing rules."""
    all_rules = {}
    for cat in EmailCategory:
        dest = custom_rules.get(cat, DEFAULT_RULES.get(cat))
        if dest:
            all_rules[cat.value] = {"type": dest.type, "target": dest.target}
    return all_rules


@router.put("/{category}")
async def update_rule(category: EmailCategory, destination: RoutingDestination):
    """Create or update a routing rule for a category."""
    custom_rules[category] = destination
    return {
        "message": f"Rule updated: {category.value} → {destination.type}:{destination.target}"
    }


@router.delete("/{category}")
async def delete_rule(category: EmailCategory):
    """Remove a custom rule (falls back to default)."""
    custom_rules.pop(category, None)
    return {"message": f"Custom rule for {category.value} removed"}
