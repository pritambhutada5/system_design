from fastapi import HTTPException, Header
from app.logging.logging_config import auth_logger
from dotenv import load_dotenv
import os
load_dotenv()

api_keys_env = os.getenv("API_KEYS", "")
API_KEYS = dict(pair.split(":") for pair in api_keys_env.split(",") if pair and ":" in pair)

def authenticate(api_key: str = Header(...)):
    if api_key not in API_KEYS:
        auth_logger.info(f"Unauthorized access attempt with key: {api_key}")
        raise HTTPException(status_code=401, detail="Unauthorized")
    auth_logger.info(f"Authenticated API key: {api_key}")
    return API_KEYS[api_key]
