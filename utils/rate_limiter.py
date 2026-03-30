"""
Simple token-bucket rate limiter for TrustWise.

Controls the rate of outgoing HTTP requests to avoid overwhelming
external services and to be a polite web citizen.
"""

import logging
import threading
import time

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Thread-safe token-bucket rate limiter.

    Allows up to ``max_requests`` requests within a sliding window of
    ``period`` seconds. Calls to :meth:`acquire` block until a token
    is available.

    Args:
        max_requests: Maximum number of requests allowed per period.
        period: Time window in seconds.
    """

    def __init__(self, max_requests: int = 5, period: float = 1.0):
        if max_requests < 1:
            raise ValueError("max_requests must be at least 1")
        if period <= 0:
            raise ValueError("period must be positive")

        self.max_requests = max_requests
        self.period = period
        self._lock = threading.Lock()
        self._timestamps: list[float] = []

    def acquire(self) -> None:
        """
        Block until a request token is available, then consume one.

        This method is thread-safe.
        """
        while True:
            with self._lock:
                now = time.monotonic()
                # Discard timestamps outside the current window
                self._timestamps = [
                    ts for ts in self._timestamps if now - ts < self.period
                ]

                if len(self._timestamps) < self.max_requests:
                    self._timestamps.append(now)
                    return

                # Calculate how long to wait for the oldest token to expire
                wait_time = self._timestamps[0] + self.period - now

            if wait_time > 0:
                logger.debug(
                    "[RateLimiter] Rate limit reached (%d/%d). Waiting %.2fs",
                    self.max_requests,
                    self.max_requests,
                    wait_time,
                )
                time.sleep(wait_time)

    @property
    def available_tokens(self) -> int:
        """Return the number of tokens currently available (non-blocking)."""
        with self._lock:
            now = time.monotonic()
            active = [ts for ts in self._timestamps if now - ts < self.period]
            return max(0, self.max_requests - len(active))


# Module-level default limiter for web requests (5 requests per second)
web_limiter = RateLimiter(max_requests=5, period=1.0)
