from __future__ import annotations

import asyncio
import datetime as dt
import threading
from typing import Optional

import httpx

from ._constants import LOGIN_PATH, TOKEN_REFRESH_LEEWAY_SECONDS
from ._errors import AuthenticationError, error_from_response

_EXPIRES_AT_FORMATS = (
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%S.%f%z",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S.%fZ",
)

# Fallback TTL when the API returns an unparseable expiry; Airwallex tokens
# are documented to last 30 minutes.
_FALLBACK_TTL_SECONDS = 30 * 60


def _parse_expires_at(raw: Optional[str]) -> float:
    """Convert the login response ``expires_at`` into a unix timestamp."""
    now = dt.datetime.now(dt.timezone.utc).timestamp()
    if not raw:
        return now + _FALLBACK_TTL_SECONDS
    for fmt in _EXPIRES_AT_FORMATS:
        try:
            parsed = dt.datetime.strptime(raw, fmt)
        except ValueError:
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.timestamp()
    return now + _FALLBACK_TTL_SECONDS


class _TokenState:
    """Shared token bookkeeping for the sync and async managers."""

    def __init__(self, client_id: str, api_key: str) -> None:
        if not client_id or not api_key:
            raise ValueError(
                "Both client_id and api_key are required. Create API credentials in "
                "the Airwallex web app under Developer > API keys."
            )
        self.client_id = client_id
        self.api_key = api_key
        self.token: Optional[str] = None
        self.expires_at: float = 0.0

    def is_fresh(self) -> bool:
        now = dt.datetime.now(dt.timezone.utc).timestamp()
        return self.token is not None and now < self.expires_at - TOKEN_REFRESH_LEEWAY_SECONDS

    def login_headers(self) -> dict[str, str]:
        return {"x-client-id": self.client_id, "x-api-key": self.api_key}

    def store(self, response: httpx.Response) -> str:
        if response.status_code >= 400:
            raise error_from_response(response)
        body = response.json()
        token = body.get("token")
        if not isinstance(token, str) or not token:
            raise AuthenticationError(
                "Login succeeded but no token was returned", response=response, body=body
            )
        self.token = token
        self.expires_at = _parse_expires_at(body.get("expires_at"))
        return token

    def invalidate(self) -> None:
        self.token = None
        self.expires_at = 0.0


class TokenManager:
    """Fetches and caches the bearer token for a sync client (thread-safe)."""

    def __init__(self, client_id: str, api_key: str) -> None:
        self._state = _TokenState(client_id, api_key)
        self._lock = threading.Lock()

    def get_token(self, http: httpx.Client) -> str:
        with self._lock:
            if self._state.is_fresh():
                assert self._state.token is not None
                return self._state.token
            response = http.post(LOGIN_PATH, headers=self._state.login_headers())
            return self._state.store(response)

    def invalidate(self) -> None:
        with self._lock:
            self._state.invalidate()


class AsyncTokenManager:
    """Fetches and caches the bearer token for an async client."""

    def __init__(self, client_id: str, api_key: str) -> None:
        self._state = _TokenState(client_id, api_key)
        self._lock = asyncio.Lock()

    async def get_token(self, http: httpx.AsyncClient) -> str:
        async with self._lock:
            if self._state.is_fresh():
                assert self._state.token is not None
                return self._state.token
            response = await http.post(LOGIN_PATH, headers=self._state.login_headers())
            return self._state.store(response)

    def invalidate(self) -> None:
        self._state.invalidate()
