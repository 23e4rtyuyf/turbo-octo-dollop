from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import secrets


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = ConfigDict(env_file=".env")

    app_name: str = "AI Email Router"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./email_router.db"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Integrations
    slack_bot_token: str = ""
    default_forward_email: str = ""

    # Auth — override via API_SECRET_KEY environment variable in production
    api_secret_key: str = "change-me-in-production"


settings = Settings()

if not settings.debug and settings.api_secret_key == "change-me-in-production":
    import warnings
    warnings.warn(
        "API_SECRET_KEY is set to the insecure default value. "
        "Set a strong secret via the API_SECRET_KEY environment variable.",
        stacklevel=1,
    )
