import os

from pydantic_settings import BaseSettings, SettingsConfigDict

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lfc_edge.db")

JWT_SECRET = os.getenv("JWT_SECRET", "dev_change_me")
JWT_ALG = "HS256"
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "720"))  # 12 hours

BADGE_SECRET = os.getenv("BADGE_SECRET", "lfc_super_secret_badge_key_2027")

# Clover config
CLOVER_ENV = os.getenv("CLOVER_ENV", "sandbox")  # sandbox or production
CLOVER_MERCHANT_ID = os.getenv("CLOVER_MERCHANT_ID", "")
CLOVER_API_TOKEN = os.getenv("CLOVER_API_TOKEN", "")
CLOVER_WEBHOOK_SECRET = os.getenv("CLOVER_WEBHOOK_SECRET", "")
CLOVER_BASE_URL = os.getenv("CLOVER_BASE_URL", "").rstrip("/")

# Public URLs
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.frostyfurfest.com")
WEB_BASE_URL = os.getenv("WEB_BASE_URL", "https://frostyfurfest.com").rstrip("/")

# Redirects after Clover checkout
CLOVER_SUCCESS_URL = os.getenv(
    "CLOVER_SUCCESS_URL",
    f"{WEB_BASE_URL}/purchase/success"
)

CLOVER_CANCEL_URL = os.getenv(
    "CLOVER_CANCEL_URL",
    f"{WEB_BASE_URL}/purchase/cancel"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "dev"
    app_name: str = "lfc-platform"
    app_version: str = "v0.1.5-dev"

    database_url: str = "sqlite:///./lfc.db"
    secret_key: str = "change-me"

    api_base_url: str = "http://127.0.0.1:8000"
    frontend_base_url: str = "http://127.0.0.1:3000"

    clover_merchant_id: str | None = None
    clover_api_key: str | None = None
    clover_webhook_secret: str | None = None


settings = Settings()
