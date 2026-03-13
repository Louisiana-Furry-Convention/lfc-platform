import os

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
