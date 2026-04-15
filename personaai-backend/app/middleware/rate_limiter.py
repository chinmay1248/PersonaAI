import time
from collections import defaultdict

from fastapi import HTTPException, Request, status


class RateLimiter:
    """Simple in-memory sliding-window rate limiter.

    Tracks request timestamps per client IP and rejects requests
    that exceed the configured rate.  Suitable for single-process
    deployments; production clusters should use Redis-backed limiting.
    """

    def __init__(self, max_requests: int = 60, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _cleanup(self, client_id: str, now: float) -> None:
        """Remove timestamps older than the sliding window."""
        cutoff = now - self.window_seconds
        self._requests[client_id] = [
            ts for ts in self._requests[client_id] if ts > cutoff
        ]

    def check(self, client_id: str) -> None:
        """Raise HTTP 429 if the client has exceeded the rate limit."""
        now = time.time()
        self._cleanup(client_id, now)

        if len(self._requests[client_id]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please slow down.",
            )

        self._requests[client_id].append(now)


# Singleton instance – 60 requests per 60-second window
_limiter = RateLimiter(max_requests=60, window_seconds=60)


async def rate_limit_guard(request: Request) -> None:
    """FastAPI dependency that enforces per-IP rate limiting."""
    client_ip = request.client.host if request.client else "unknown"
    _limiter.check(client_ip)
    request.state.rate_limited = False
