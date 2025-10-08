import json
import logging
from pydantic_settings import BaseSettings
from typing import Dict, Any

logger = logging.getLogger("app")

class Settings(BaseSettings):
    """
    Loads configuration from environment variables and a .env file.
    """
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    RATE_LIMIT_RULES_PATH: str = "rate_limits.json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def load_rate_limit_rules(path: str) -> Dict[str, Any]:
    """
    Loads rate limiting rules from a JSON file.
    Returns default rules if the file is not found or invalid.
    """
    try:
        with open(path, "r") as f:
            rules = json.load(f)
            logger.info(f"Successfully loaded rate limiting rules from {path}")
            return rules
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Could not load rate limit rules from {path}: {e}. Using default rules.")
        # Return a safe default if the file is missing or corrupt
        return {
            "default": {"capacity": 10, "refill_rate": 1}
        }

settings = Settings()
rate_limit_rules = load_rate_limit_rules(settings.RATE_LIMIT_RULES_PATH)
