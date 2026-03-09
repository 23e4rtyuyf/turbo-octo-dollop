import pytest
from app.models.email import EmailCategory
from app.models.rule import RoutingDestination
from app.services.router import get_destination, DEFAULT_RULES, custom_rules


@pytest.fixture(autouse=True)
def clean_custom_rules():
    """Ensure custom_rules is clean before and after each test."""
    custom_rules.clear()
    yield
    custom_rules.clear()


class TestRouter:
    def test_default_complaint_routes_to_support_urgent(self):
        dest = get_destination(EmailCategory.COMPLAINT)
        assert dest is not None
        assert dest.type == "slack"
        assert dest.target == "#support-urgent"

    def test_default_lead_routes_to_sales(self):
        dest = get_destination(EmailCategory.LEAD)
        assert dest is not None
        assert dest.target == "#sales"

    def test_custom_rule_overrides_default(self):
        custom_rules[EmailCategory.LEAD] = RoutingDestination(
            type="webhook", target="https://crm.example.com/leads"
        )
        dest = get_destination(EmailCategory.LEAD)
        assert dest.type == "webhook"
        assert dest.target == "https://crm.example.com/leads"

    def test_spam_is_discarded(self):
        dest = get_destination(EmailCategory.SPAM)
        assert dest is not None
        assert dest.target == ""
