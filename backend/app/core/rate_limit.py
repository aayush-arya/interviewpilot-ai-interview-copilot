"""Fixed-window rate limiting. Redis-backed when REDIS_URL is set,
in-memory fallback otherwise (fine for single-process deployments)."""
import time
from collections import defaultdict

from fastapi import HTTPException, Request, status

from app.core.config import get_settings

_memory_windows: dict[str, tuple[int, float]] = defaultdict(lambda: (0, 0.0))
_redis_client = None


def _get_redis():
    global _redis_client
    if _redis_client is None and get_settings().REDIS_URL:
        import redis

        _redis_client = redis.from_url(get_settings().REDIS_URL, decode_responses=True)
    return _redis_client


def rate_limit(bucket: str, limit: int, window_s: int = 60):
    """Dependency factory: raises 429 when `limit` calls per window is exceeded."""

    def dependency(request: Request):
        client = request.client.host if request.client else "unknown"
        auth = request.headers.get("authorization", "")
        key = f"rl:{bucket}:{auth[-24:] or client}"
        r = _get_redis()
        if r is not None:
            try:
                count = r.incr(key)
                if count == 1:
                    r.expire(key, window_s)
                if count > limit:
                    raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Rate limit exceeded")
                return
            except HTTPException:
                raise
            except Exception:
                pass  # Redis down → fall through to memory
        count, window_start = _memory_windows[key]
        now = time.monotonic()
        if now - window_start > window_s:
            _memory_windows[key] = (1, now)
            return
        if count + 1 > limit:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Rate limit exceeded")
        _memory_windows[key] = (count + 1, window_start)

    return dependency
