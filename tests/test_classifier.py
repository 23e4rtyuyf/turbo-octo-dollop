import pytest
from app.models.email import InboundEmail, EmailCategory


def make_email(sender: str, subject: str, body: str) -> InboundEmail:
    return InboundEmail(
        sender=sender,
        recipient="info@company.com",
        subject=subject,
        body_plain=body,
    )


class TestEmailModels:
    def test_complaint_category_exists(self):
        assert EmailCategory.COMPLAINT == "complaint"

    def test_lead_category_exists(self):
        assert EmailCategory.LEAD == "lead"

    def test_inbound_email_creation(self):
        email = make_email("test@test.com", "Hello", "Test body")
        assert email.sender == "test@test.com"
        assert email.subject == "Hello"
        assert email.body_plain == "Test body"

    def test_inbound_email_defaults(self):
        email = make_email("test@test.com", "Hello", "Body")
        assert email.body_html == ""
        assert email.timestamp is not None
