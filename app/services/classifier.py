import json
from openai import AsyncOpenAI
from app.config import settings
from app.models.email import InboundEmail, EmailCategory, ClassifiedEmail

client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """You are an advanced email classification AI. Your job is to 
analyze incoming emails and classify them into exactly ONE category.

Categories:
- complaint: Customer is unhappy, reporting a problem, expressing frustration
- lead: Someone interested in buying, requesting a demo, asking about pricing
- billing: Invoice questions, payment issues, refund requests, subscription changes
- support: Technical help requests, how-to questions, bug reports (without anger)
- partnership: Business collaboration proposals, affiliate requests, integration offers
- spam: Unsolicited marketing, phishing, irrelevant mass emails
- other: Anything that doesn't fit the above categories

Respond with valid JSON only:
{
    "category": "<category>",
    "confidence": <0.0 to 1.0>,
    "reasoning": "<one sentence explanation>"
}"""


async def classify_email(email: InboundEmail) -> ClassifiedEmail:
    """Classify an inbound email using AI."""

    user_message = f"""Classify this email:

From: {email.sender}
Subject: {email.subject}

Body:
{email.body_plain[:2000]}"""

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.1,
        max_tokens=200,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)

    return ClassifiedEmail(
        email=email,
        category=EmailCategory(result["category"]),
        confidence=result["confidence"],
        reasoning=result["reasoning"],
    )
