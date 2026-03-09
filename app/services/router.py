from typing import Optional
from app.models.email import ClassifiedEmail, EmailCategory
from app.config import settings

# Default routing rules (can be overridden by DB rules)
DEFAULT_ROUTES = {
    EmailCategory.complaint: {"type": "email", "target": "complaints@company.com"},
    EmailCategory.lead: {"type": "email", "target": "sales@company.com"},
    EmailCategory.billing: {"type": "email", "target": "billing@company.com"},
    EmailCategory.support: {"type": "email", "target": "support@company.com"},
    EmailCategory.partnership: {"type": "email", "target": "partnerships@company.com"},
    EmailCategory.spam: {"type": "discard", "target": None},
    EmailCategory.other: {"type": "email", "target": "inbox@company.com"},
}


async def route_email(classified: ClassifiedEmail, custom_rules: Optional[dict] = None) -> str:
    """Route a classified email to the appropriate destination."""
    rules = custom_rules or DEFAULT_ROUTES
    rule = rules.get(classified.category)

    if not rule:
        return f"unrouted:{classified.category.value}"

    destination_type = rule.get("type", "email")
    target = rule.get("target")

    if destination_type == "discard":
        return "discarded:spam"

    if destination_type == "slack":
        if settings.slack_bot_token:
            await _send_to_slack(classified, target)
        return f"slack:{target}"

    if destination_type == "webhook":
        await _send_to_webhook(classified, target)
        return f"webhook:{target}"

    # Default: email forwarding
    if settings.default_forward_email:
        return f"email:{settings.default_forward_email}"

    return f"email:{target}"


async def _send_to_slack(classified: ClassifiedEmail, channel: str) -> None:
    """Send email notification to a Slack channel."""
    import httpx

    if not settings.slack_bot_token:
        return

    message = {
        "channel": channel,
        "text": f"📧 New *{classified.category.value}* email",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Category:* {classified.category.value} "
                        f"({classified.confidence:.0%} confidence)\n"
                        f"*From:* {classified.sender}\n"
                        f"*Subject:* {classified.subject}\n"
                        f"*Reason:* {classified.reasoning}"
                    ),
                },
            }
        ],
    }

    async with httpx.AsyncClient() as client:
        await client.post(
            "https://slack.com/api/chat.postMessage",
            json=message,
            headers={"Authorization": f"Bearer {settings.slack_bot_token}"},
        )


async def _send_to_webhook(classified: ClassifiedEmail, url: str) -> None:
    """Send classified email data to a webhook URL."""
    import httpx

    payload = {
        "sender": classified.sender,
        "subject": classified.subject,
        "category": classified.category.value,
        "confidence": classified.confidence,
        "reasoning": classified.reasoning,
        "routed_to": classified.routed_to,
    }

    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload, timeout=10.0)
