"""
Key-safe HTTP helpers for optional third-party APIs (Tavily, Exa, Firecrawl, etc.).

Never logs raw API keys. Retries transient failures (429, 5xx) with backoff.
"""

from __future__ import annotations

import random
import time
from typing import Any, Dict, Optional, Tuple

import requests

from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class KeyedAdapterError(Exception):
    """Normalized failure for keyed adapters."""

    def __init__(
        self,
        message: str,
        *,
        error_type: str = "unknown",
        http_status: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.http_status = http_status


def _should_retry(status: Optional[int]) -> bool:
    if status is None:
        return False
    return status == 429 or (500 <= status <= 599)


def safe_request_json(
    method: str,
    url: str,
    *,
    max_retries: int = 2,
    session: Optional[requests.Session] = None,
    timeout: Optional[int] = None,
    **kwargs: Any,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Perform HTTP request and parse JSON. Returns (data, meta).

    meta keys: attempted, ok, error_type, http_status, retries_used
    """
    sess = session or requests.Session()
    timeout = timeout if timeout is not None else Config.RESEARCH_SOURCE_TIMEOUT
    meta: Dict[str, Any] = {
        "attempted": True,
        "ok": False,
        "error_type": None,
        "http_status": None,
        "retries_used": 0,
    }
    last_exc: Optional[Exception] = None
    attempts = max(1, max_retries + 1)
    for attempt in range(attempts):
        try:
            resp = sess.request(method, url, timeout=timeout, **kwargs)
            meta["http_status"] = resp.status_code
            if _should_retry(resp.status_code) and attempt < attempts - 1:
                meta["retries_used"] = attempt + 1
                time.sleep(0.5 * (2**attempt) + random.random() * 0.2)
                continue
            resp.raise_for_status()
            try:
                data = resp.json()
            except ValueError as e:
                meta["error_type"] = "json_error"
                raise KeyedAdapterError("Invalid JSON in response", error_type="json_error", http_status=resp.status_code) from e
            meta["ok"] = True
            return data, meta
        except requests.exceptions.Timeout as e:
            last_exc = e
            meta["error_type"] = "timeout"
            meta["http_status"] = None
            if attempt < attempts - 1:
                meta["retries_used"] = attempt + 1
                time.sleep(0.5 * (2**attempt))
                continue
            raise KeyedAdapterError(str(e), error_type="timeout") from e
        except requests.exceptions.RequestException as e:
            last_exc = e
            status = getattr(getattr(e, "response", None), "status_code", None)
            meta["http_status"] = status
            if _should_retry(status) and attempt < attempts - 1:
                meta["retries_used"] = attempt + 1
                time.sleep(0.5 * (2**attempt) + random.random() * 0.2)
                continue
            meta["error_type"] = "http_error"
            raise KeyedAdapterError(str(e), error_type="http_error", http_status=status) from e
    raise KeyedAdapterError(str(last_exc or "request failed"), error_type="http_error")


def safe_request_text(
    method: str,
    url: str,
    *,
    max_retries: int = 2,
    session: Optional[requests.Session] = None,
    timeout: Optional[int] = None,
    **kwargs: Any,
) -> Tuple[str, Dict[str, Any]]:
    """Return (text body, meta) with same retry semantics as safe_request_json."""
    sess = session or requests.Session()
    timeout = timeout if timeout is not None else Config.RESEARCH_SOURCE_TIMEOUT
    meta: Dict[str, Any] = {
        "attempted": True,
        "ok": False,
        "error_type": None,
        "http_status": None,
        "retries_used": 0,
    }
    attempts = max(1, max_retries + 1)
    for attempt in range(attempts):
        try:
            resp = sess.request(method, url, timeout=timeout, **kwargs)
            meta["http_status"] = resp.status_code
            if _should_retry(resp.status_code) and attempt < attempts - 1:
                meta["retries_used"] = attempt + 1
                time.sleep(0.5 * (2**attempt) + random.random() * 0.2)
                continue
            resp.raise_for_status()
            meta["ok"] = True
            return resp.text, meta
        except requests.exceptions.Timeout as e:
            meta["error_type"] = "timeout"
            if attempt < attempts - 1:
                meta["retries_used"] = attempt + 1
                time.sleep(0.5 * (2**attempt))
                continue
            raise KeyedAdapterError(str(e), error_type="timeout") from e
        except requests.exceptions.RequestException as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            meta["http_status"] = status
            if _should_retry(status) and attempt < attempts - 1:
                meta["retries_used"] = attempt + 1
                time.sleep(0.5 * (2**attempt) + random.random() * 0.2)
                continue
            meta["error_type"] = "http_error"
            raise KeyedAdapterError(str(e), error_type="http_error", http_status=status) from e
    return "", meta


def empty_meta_no_key(provider: str) -> Dict[str, Any]:
    return {
        "attempted": False,
        "ok": True,
        "error_type": "no_key",
        "http_status": None,
        "normalized_count": 0,
        "provider": provider,
    }
