import httpx
from app.models.email import ClassifiedEmail


async def send_webhook(url: str, classified: ClassifiedEmail) -> bool:
    """Send classified email data to a webhook URL (e.g., CRM)."""
    payload = {
        "event": "email.classified",
        "category": classified.category.value,
        "confidence": classified.confidence,
        "reasoning": classified.reasoning,
        "sender": classified.email.sender,
        "subject": classified.email.subject,
        "body": classified.email.body_plain[:1000],
        "timestamp": classified.email.timestamp.isoformat(),
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=10.0)
        return response.status_code < 400
