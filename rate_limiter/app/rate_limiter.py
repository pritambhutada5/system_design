import time
import logging
import redis.asyncio as redis
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable

logger = logging.getLogger("app")


class DistributedTokenBucketMiddleware(BaseHTTPMiddleware):
    """
    A distributed token bucket rate limiter middleware for FastAPI using Redis.
    This middleware uses a Lua script to ensure atomic operations on token
    buckets stored in Redis, making it safe for distributed environments.
    """
    LUA_SCRIPT = """
    local key = KEYS[1]
    local capacity = tonumber(ARGV[1])
    local refill_rate = tonumber(ARGV[2])
    local current_time = tonumber(ARGV[3])
    local requested = tonumber(ARGV[4])

    local data = redis.call('HMGET', key, 'tokens', 'timestamp')
    local tokens = tonumber(data[1])
    local timestamp = tonumber(data[2])

    if tokens == nil then
        tokens = capacity
        timestamp = current_time
    end

    -- Refill tokens based on elapsed time
    local delta = math.max(0, current_time - timestamp)
    -- IMPORTANT: Use math.floor to only add whole tokens and avoid float issues
    local refill = math.floor(delta * refill_rate)

    tokens = math.min(capacity, tokens + refill)

    local allowed = 0
    if tokens >= requested then
        tokens = tokens - requested
        allowed = 1
    end

    -- Update timestamp only when a token is successfully consumed.
    -- This prevents many small, non-refilling time deltas from causing writes.
    if allowed == 1 then
        redis.call('HMSET', key, 'tokens', tokens, 'timestamp', current_time)
    else
        -- If not allowed, only update the token count which might have refilled.
        redis.call('HSET', key, 'tokens', tokens)
    end

    redis.call('EXPIRE', key, 3600)
    return {allowed, tokens}
    """

    def __init__(
            self,
            app: ASGIApp,
            capacity: int,
            refill_rate: float,
    ):
        super().__init__(app)
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._script_sha = None

    async def _load_script(self, redis_client: redis.Redis):
        """Loads the Lua script into Redis and stores its SHA hash."""
        if self._script_sha is None:
            self._script_sha = await redis_client.script_load(self.LUA_SCRIPT)
            logger.info(f"Loaded rate limiter Lua script into Redis (SHA: {self._script_sha})")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get the redis client from the application state AT REQUEST TIME.
        try:
            redis_client: redis.Redis = request.app.state.redis
        except AttributeError:
            logger.error("Redis client not found in app state. Rate limiting is disabled.")
            return await call_next(request)
        await self._load_script(redis_client)

        # Prioritize the X-Forwarded-For header to identify the client
        client_id = request.headers.get("x-forwarded-for", request.client.host)
        key = f"rate-limit:{client_id}"

        try:
            result = await redis_client.evalsha(
                self._script_sha,
                1,  # Number of keys
                key,
                self.capacity,
                self.refill_rate,
                time.time(),
                1,  # Consume 1 token per request
            )

            allowed, tokens_left = result[0], result[1]

            logger.info(f"Client '{client_id}': Allowed={bool(allowed)}, Tokens Left={float(tokens_left):.2f}")

            if bool(allowed):
                response = await call_next(request)
                response.headers["X-RateLimit-Remaining"] = str(round(tokens_left))
                response.headers["X-RateLimit-Limit"] = str(self.capacity)
                return response
            else:
                logger.warning(f"Rate limit exceeded for client '{client_id}'. Request blocked.")
                return Response(
                    content="Too Many Requests",
                    status_code=429,
                    headers={"Retry-After": str(int(1 / self.refill_rate))}
                )
        except Exception as e:
            logger.error(f"Error during rate limiting check: {e}. Allowing request to proceed.")
            return await call_next(request)

