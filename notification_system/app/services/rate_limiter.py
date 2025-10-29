import time
from fastapi import HTTPException
from app.logging.logging_config import rate_limiter_logger

RATE_LIMIT = 5  # requests per minute
rate_limit_cache = {}

def rate_limiter(api_key: str):
    now = int(time.time() / 60)
    key = f"{api_key}:{now}"
    if key not in rate_limit_cache:
        rate_limit_cache[key] = 1
    else:
        rate_limit_cache[key] += 1
    rate_limiter_logger.info(f"API key {api_key} count for {now}: {rate_limit_cache[key]}")
    if rate_limit_cache[key] > RATE_LIMIT:
        rate_limiter_logger.warning(f"Rate limit exceeded for {api_key}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
