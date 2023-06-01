import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Database config
    mongodb_uri = os.getenv("MONGODB_URI")
    mongodb_db_name = os.getenv("MONGODB_DB_NAME", "")

    # JWT
    jwt_secret_key = os.getenv("JWT_SECRET_KEY", "")
    jwt_expires_after_seconds = 60 * 60 * 24  # 24h

    # Log config
    log_level = int(os.getenv("LOG_LEVEL", "40"))

    # Institution IDs
    bg_filozofski_id = 1
    ns_filozofski_id = 2

