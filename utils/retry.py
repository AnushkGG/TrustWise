"""
Retry utility with exponential backoff for TrustWise.

Provides a decorator and helper function that retries failed operations
with configurable exponential backoff, jitter, and exception filtering.
"""

import functools
import logging
import random
import time
from typing import Callable, Tuple, Type

logger = logging.getLogger(__name__)

DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 1.0
DEFAULT_MAX_DELAY = 30.0
DEFAULT_BACKOFF_FACTOR = 2.0


def retry_with_backoff(
    max_retries: int = DEFAULT_MAX_RETRIES,
    base_delay: float = DEFAULT_BASE_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    retryable_exceptions: Tuple[Type[BaseException], ...] = (Exception,),
):
    """
    Decorator that retries a function with exponential backoff on failure.

    Args:
        max_retries: Maximum number of retry attempts (0 means no retries).
        base_delay: Initial delay in seconds before the first retry.
        max_delay: Maximum delay in seconds between retries.
        backoff_factor: Multiplier applied to the delay after each retry.
        retryable_exceptions: Tuple of exception types that trigger a retry.

    Returns:
        Decorated function with retry logic.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_retries + 2):  # 1 initial call + max_retries retries
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as exc:
                    last_exception = exc
                    if attempt > max_retries:
                        logger.error(
                            "[Retry] %s failed after %d attempt(s): %s",
                            func.__name__,
                            attempt,
                            exc,
                        )
                        raise
                    delay = min(
                        base_delay * (backoff_factor ** (attempt - 1)),
                        max_delay,
                    )
                    # Add jitter (±25%) to avoid thundering herd
                    jitter = delay * 0.25 * (2 * random.random() - 1)
                    actual_delay = max(0, delay + jitter)
                    logger.warning(
                        "[Retry] %s attempt %d/%d failed (%s). "
                        "Retrying in %.1fs...",
                        func.__name__,
                        attempt,
                        max_retries + 1,
                        exc,
                        actual_delay,
                    )
                    time.sleep(actual_delay)

            # Should not reach here, but just in case
            if last_exception is not None:
                raise last_exception

        return wrapper

    return decorator


def execute_with_retry(
    func: Callable,
    *args,
    max_retries: int = DEFAULT_MAX_RETRIES,
    base_delay: float = DEFAULT_BASE_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    retryable_exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    **kwargs,
):
    """
    Execute a callable with retry logic (non-decorator form).

    Args:
        func: The callable to execute.
        *args: Positional arguments for the callable.
        max_retries: Maximum number of retry attempts.
        base_delay: Initial delay in seconds.
        max_delay: Maximum delay in seconds.
        backoff_factor: Multiplier for delay after each retry.
        retryable_exceptions: Exception types that trigger a retry.
        **kwargs: Keyword arguments for the callable.

    Returns:
        The return value of the callable.

    Raises:
        The last exception if all retries are exhausted.
    """
    wrapped = retry_with_backoff(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        backoff_factor=backoff_factor,
        retryable_exceptions=retryable_exceptions,
    )(func)
    return wrapped(*args, **kwargs)
