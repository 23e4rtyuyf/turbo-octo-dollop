import httpx
from app.models.email import ClassifiedEmail


async def forward_email(target_email: str, classified: ClassifiedEmail) -> bool:
    """Forward a classified email to a target address.

    In production, integrate with SendGrid/Mailgun/SES.
    """
    print(
        f"[EMAIL FORWARD] → {target_email}\n"
        f"  Subject: [AI:{classified.category.value}] {classified.email.subject}\n"
        f"  Original sender: {classified.email.sender}"
    )
    # TODO: Integrate with email provider API
    return True
