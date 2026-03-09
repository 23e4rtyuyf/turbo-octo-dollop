import httpx
from app.models.email import ClassifiedEmail, EmailCategory
from app.models.rule import RoutingRule, RoutingDestination
from app.services.integrations.slack import send_slack_message
from app.services.integrations.email_forward import forward_email
from app.services.integrations.webhook import send_webhook

# Default routing rules (can be overridden via API)
DEFAULT_RULES: dict[EmailCategory, RoutingDestination] = {
    EmailCategory.COMPLAINT: RoutingDestination(type="slack", target="#support-urgent"),
    EmailCategory.LEAD: RoutingDestination(type="slack", target="#sales"),
    EmailCategory.BILLING: RoutingDestination(type="slack", target="#billing"),
    EmailCategory.SUPPORT: RoutingDestination(type="slack", target="#support"),
    EmailCategory.PARTNERSHIP: RoutingDestination(type="slack", target="#partnerships"),
    EmailCategory.SPAM: RoutingDestination(type="webhook", target=""),  # discard
}

# In-memory rule store (replace with DB in production)
custom_rules: dict[EmailCategory, RoutingDestination] = {}


def get_destination(category: EmailCategory) -> RoutingDestination | None:
    """Look up the routing destination for a category."""
    return custom_rules.get(category, DEFAULT_RULES.get(category))


async def route_email(classified: ClassifiedEmail) -> str:
    """Route a classified email to the correct destination."""

    destination = get_destination(classified.category)
    if not destination:
        return "no_route_configured"

    # Format the message
    message = (
        f"📧 *New {classified.category.value.upper()} email*\n"
        f"*From:* {classified.email.sender}\n"
        f"*Subject:* {classified.email.subject}\n"
        f"*Confidence:* {classified.confidence:.0%}\n"
        f"*Reasoning:* {classified.reasoning}\n"
        f"---\n"
        f"{classified.email.body_plain[:500]}"
    )

    # Dispatch to the right integration
    match destination.type:
        case "slack":
            await send_slack_message(destination.target, message)
        case "email":
            await forward_email(destination.target, classified)
        case "webhook":
            if destination.target:
                await send_webhook(destination.target, classified)
            else:
                return "discarded"

    classified.routed_to = f"{destination.type}:{destination.target}"
    return classified.routed_to
