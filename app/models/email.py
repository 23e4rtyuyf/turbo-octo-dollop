from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field


class EmailCategory(str, Enum):
    """AI-classified email categories."""
    COMPLAINT = "complaint"
    LEAD = "lead"
    BILLING = "billing"
    SUPPORT = "support"
    PARTNERSHIP = "partnership"
    SPAM = "spam"
    OTHER = "other"


class InboundEmail(BaseModel):
    """Represents an incoming email received via webhook."""
    sender: str
    recipient: str
    subject: str
    body_plain: str
    body_html: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ClassifiedEmail(BaseModel):
    """An email after AI classification."""
    email: InboundEmail
    category: EmailCategory
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    routed_to: str = ""
