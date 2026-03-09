from pydantic import BaseModel


class User(BaseModel):
    """User model. (Coming soon)"""
    id: int | None = None
    email: str
    organization: str = ""
    api_key: str = ""
