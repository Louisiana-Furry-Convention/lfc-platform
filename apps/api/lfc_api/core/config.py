import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lfc_edge.db")
JWT_SECRET = os.getenv("JWT_SECRET", "dev_change_me")
JWT_ALG = "HS256"
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "720"))  # 12 hours
BADGE_SECRET = "lfc_super_secret_badge_key_2027"
