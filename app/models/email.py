from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EmailCategory(str, Enum):
    complaint = "complaint"
    lead = "lead"
    billing = "billing"
    support = "support"
    partnership = "partnership"
    spam = "spam"
    other = "other"


class InboundEmail(BaseModel):
    sender: str = Field(..., description="Sender email address")
    recipient: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject line")
    body_plain: str = Field(..., description="Plain text email body")
    body_html: Optional[str] = Field(None, description="HTML email body (optional)")


class ClassifiedEmail(BaseModel):
    sender: str
    recipient: str
    subject: str
    category: EmailCategory
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence (0-1)")
    reasoning: str = Field(..., description="AI reasoning for classification")
    routed_to: Optional[str] = Field(None, description="Where the email was routed")
