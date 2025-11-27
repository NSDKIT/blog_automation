"""
Simple in-memory rate limiter dependency.
"""
from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from typing import Callable

from fastapi import HTTPException, Request, status


class InMemoryRateLimiter:
    def __init__(self):
        self._events = defaultdict(deque)
        self._lock = threading.Lock()

    def hit(self, key: str, limit: int, window_seconds: int) -> None:
        now = time.monotonic()
        window = float(window_seconds)
        with self._lock:
            bucket = self._events[key]
            while bucket and now - bucket[0] > window:
                bucket.popleft()
            if len(bucket) >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please slow down and try again later.",
                )
            bucket.append(now)


_limiter = InMemoryRateLimiter()


def rate_limit(limit: int, window_seconds: int) -> Callable[[Request], None]:
    async def dependency(request: Request) -> None:
        client_host = request.client.host if request.client else "unknown"
        user_id = getattr(request.state, "user_id", None)
        identity = user_id or client_host
        key = f"{request.url.path}:{identity}"
        _limiter.hit(key, limit, window_seconds)

    return dependency
