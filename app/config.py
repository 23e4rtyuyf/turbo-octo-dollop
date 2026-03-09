from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
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

    # Auth
    api_secret_key: str = "change-me-in-production"

    # Stripe Billing
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_publishable_key: str = ""


settings = Settings()
