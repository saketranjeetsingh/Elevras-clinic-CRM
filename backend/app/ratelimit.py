import os
import threading
import time

from fastapi import HTTPException
from fastapi import Request


class SlidingWindowRateLimiter:

    def __init__(self, limit: int, window_seconds: int, key_prefix: str):
        self.limit = limit
        self.window_seconds = window_seconds
        self.key_prefix = key_prefix
        self._hits = {}
        self._lock = threading.Lock()

    def reset(self):
        with self._lock:
            self._hits.clear()

    def _enabled(self) -> bool:
        return os.environ.get("RATE_LIMIT_ENABLED", "true").strip().lower() != "false"

    def check(self, key: str) -> int | None:
        """Record a hit and return Retry-After seconds if over the limit."""
        if not self._enabled():
            return None

        now = time.monotonic()

        with self._lock:
            timestamps = self._hits.get(key, [])
            timestamps = [t for t in timestamps if now - t < self.window_seconds]

            if len(timestamps) >= self.limit:
                retry_after = int(self.window_seconds - (now - timestamps[0])) + 1
                self._hits[key] = timestamps
                return max(retry_after, 1)

            timestamps.append(now)
            self._hits[key] = timestamps

        return None


AUTH_LIMITER = SlidingWindowRateLimiter(limit=5, window_seconds=60, key_prefix="auth")
IMPORT_LIMITER = SlidingWindowRateLimiter(limit=10, window_seconds=60, key_prefix="import")


def _build_dependency(limiter):
    def dependency(request: Request) -> None:
        client_host = request.client.host if request.client else "unknown"
        retry_after = limiter.check(f"{limiter.key_prefix}:{client_host}")
        if retry_after is not None:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later.",
                headers={"Retry-After": str(retry_after)},
            )

    return dependency


auth_rate_limit = _build_dependency(AUTH_LIMITER)
import_rate_limit = _build_dependency(IMPORT_LIMITER)
