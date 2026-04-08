import json
from openai import AsyncOpenAI
from app.models.email import InboundEmail, ClassifiedEmail, EmailCategory
from app.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """You are an AI email classifier for a business. Classify incoming emails into one of these categories:
- complaint: Customer expressing dissatisfaction or filing a complaint
- lead: Potential new customer, sales inquiry, or business opportunity
- billing: Payment, invoice, subscription, or financial questions
- support: Technical support, how-to questions, bug reports
- partnership: Business partnership, collaboration, or vendor inquiries
- spam: Unsolicited bulk email, phishing, or irrelevant content
- other: Anything that doesn't fit the above categories

Respond ONLY with a JSON object in this exact format:
{
  "category": "<category>",
  "confidence": <float between 0 and 1>,
  "reasoning": "<brief explanation>"
}"""


async def classify_email(email: InboundEmail) -> ClassifiedEmail:
    """Classify an email using OpenAI GPT."""
    if not settings.openai_api_key:
        # Fallback classification when no API key is set
        return ClassifiedEmail(
            sender=email.sender,
            recipient=email.recipient,
            subject=email.subject,
            category=EmailCategory.other,
            confidence=0.5,
            reasoning="No OpenAI API key configured. Defaulting to 'other' category.",
        )

    user_message = f"""Subject: {email.subject}
From: {email.sender}
Body: {email.body_plain[:2000]}"""

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.1,
        max_tokens=200,
    )

    content = response.choices[0].message.content.strip()
    result = json.loads(content)

    return ClassifiedEmail(
        sender=email.sender,
        recipient=email.recipient,
        subject=email.subject,
        category=EmailCategory(result["category"]),
        confidence=float(result["confidence"]),
        reasoning=result["reasoning"],
    )
