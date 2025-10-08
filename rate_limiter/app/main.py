import uvicorn
import logging
import redis.asyncio as redis
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .logging_config import setup_logging
from .rate_limiter import DistributedTokenBucketMiddleware
from .config import settings, rate_limit_rules


setup_logging()
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown events."""
    logger.info("Application startup...")
    app.state.redis = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True
    )
    try:
        await app.state.redis.ping()
        logger.info(f"Successfully connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    except Exception as e:
        logger.error(f"Could not connect to Redis: {e}")

    yield

    logger.info("Application shutdown...")
    await app.state.redis.close()
    logger.info("Redis connection closed.")


app = FastAPI(title="Distributed Rate Limiter", lifespan=lifespan)

default_rule = rate_limit_rules.get("default", {"capacity": 10, "refill_rate": 1})

app.add_middleware(
    DistributedTokenBucketMiddleware,
    capacity=default_rule["capacity"],
    refill_rate=default_rule["refill_rate"]
)


@app.get("/limited")
async def get_limited_endpoint():
    """A sample endpoint protected by the rate limiter."""
    return {"message": "This endpoint is rate-limited by the 'default' rule."}


@app.get("/unlimited")
async def get_unlimited_endpoint():
    """
    This endpoint demonstrates how different rules could be applied,
    though currently it shares the same default rate limit.
    """
    return {"message": "This endpoint is also checked by the default rate limit."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

