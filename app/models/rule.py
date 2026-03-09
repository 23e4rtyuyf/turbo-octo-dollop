from pydantic import BaseModel
from app.models.email import EmailCategory


class RoutingDestination(BaseModel):
    """Where to route a classified email."""
    type: str  # "slack", "email", "webhook"
    target: str  # channel name, email address, or URL


class RoutingRule(BaseModel):
    """Maps an email category to a destination."""
    id: int | None = None
    category: EmailCategory
    destination: RoutingDestination
    enabled: bool = True
