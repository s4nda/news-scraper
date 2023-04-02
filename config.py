import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Database config
    mongodb_uri = os.getenv("MONGODB_URI")
    mongodb_db_name = os.getenv("MONGODB_DB_NAME", "")

    log_level = int(os.getenv("LOG_LEVEL", "40"))
