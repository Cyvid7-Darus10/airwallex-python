from __future__ import annotations

import asyncio
import datetime as dt
import email.utils
import random
import time
from collections.abc import Mapping
from typing import Any, Optional, Union

import httpx

from ._auth import AsyncTokenManager, TokenManager
from ._constants import (
    BASE_URLS,
    DEFAULT_INITIAL_RETRY_DELAY_SECONDS,
    DEFAULT_MAX_RETRIES,
    DEFAULT_MAX_RETRY_DELAY_SECONDS,
    DEFAULT_TIMEOUT_SECONDS,
    RETRYABLE_STATUS_CODES,
    Environment,
)
from ._errors import APIConnectionError, APIError, error_from_response
from ._version import __version__

Query = Optional[Mapping[str, Any]]
Body = Optional[Mapping[str, Any]]


class _ClientConfig:
    """Configuration shared by the sync and async clients."""

    def __init__(
        self,
        *,
        client_id: str,
        api_key: str,
        environment: Environment = "production",
        base_url: Optional[str] = None,
        api_version: Optional[str] = None,
        on_behalf_of: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        if environment not in BASE_URLS:
            raise ValueError(f"environment must be one of {sorted(BASE_URLS)}, got {environment!r}")
        if max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        self.base_url = (base_url or BASE_URLS[environment]).rstrip("/")
        self.environment = environment
        self.api_version = api_version
        self.on_behalf_of = on_behalf_of
        self.timeout = timeout
        self.max_retries = max_retries
        self.client_id = client_id
        self.api_key = api_key

    def __repr__(self) -> str:
        return (
            f"_ClientConfig(client_id={self.client_id!r}, api_key='[REDACTED]', "
            f"environment={self.environment!r}, base_url={self.base_url!r})"
        )

    def default_headers(self) -> dict[str, str]:
        headers = {
            "User-Agent": f"airwallex-python/{__version__}",
            "Accept": "application/json",
        }
        if self.api_version:
            headers["x-api-version"] = self.api_version
        if self.on_behalf_of:
            headers["x-on-behalf-of"] = self.on_behalf_of
        return headers


def _parse_retry_after(value: str) -> Optional[float]:
    """Parse a Retry-After header: either delta-seconds or an HTTP-date (RFC 7231)."""
    try:
        return max(0.0, float(value))
    except ValueError:
        pass
    try:
        retry_at = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if retry_at.tzinfo is None:
        retry_at = retry_at.replace(tzinfo=dt.timezone.utc)
    now = dt.datetime.now(dt.timezone.utc)
    return max(0.0, (retry_at - now).total_seconds())


def _retry_delay(attempt: int, response: Optional[httpx.Response]) -> float:
    """Full-jitter exponential backoff, honouring Retry-After when present."""
    if response is not None:
        retry_after = response.headers.get("retry-after")
        if retry_after is not None:
            delay = _parse_retry_after(retry_after)
            if delay is not None:
                return delay
    cap = min(
        DEFAULT_MAX_RETRY_DELAY_SECONDS,
        DEFAULT_INITIAL_RETRY_DELAY_SECONDS * (2**attempt),
    )
    return random.uniform(0, cap)


def _parse_body(response: httpx.Response) -> Any:
    if not response.content:
        return None
    try:
        return response.json()
    except ValueError as exc:
        raise APIError(
            f"Airwallex returned a {response.status_code} response with an unparseable "
            f"body (content-type: {response.headers.get('content-type', 'unknown')})",
            request=response.request,
        ) from exc


class SyncAPIClient:
    """Low-level synchronous HTTP layer. Use :class:`airwallex.Airwallex` instead."""

    def __init__(self, config: _ClientConfig, http: Optional[httpx.Client] = None) -> None:
        self._config = config
        self._http = http or httpx.Client(
            base_url=config.base_url,
            timeout=config.timeout,
            headers=config.default_headers(),
        )
        self._token_manager = TokenManager(config.client_id, config.api_key)

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Query = None,
        json: Body = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        """Send an authenticated request, retrying transient failures."""
        auth_retried = False
        attempt = 0
        while True:
            token = self._token_manager.get_token(self._http)
            request_headers = {"Authorization": f"Bearer {token}", **(headers or {})}
            try:
                response = self._http.request(
                    method, path, params=params, json=json, headers=request_headers
                )
            except httpx.TransportError as exc:
                if attempt >= self._config.max_retries:
                    raise APIConnectionError(
                        f"Request failed after {attempt + 1} attempt(s): {exc}"
                    ) from exc
                time.sleep(_retry_delay(attempt, None))
                attempt += 1
                continue

            if response.status_code == 401 and not auth_retried:
                self._token_manager.invalidate()
                auth_retried = True
                continue
            retryable = response.status_code in RETRYABLE_STATUS_CODES
            if retryable and attempt < self._config.max_retries:
                time.sleep(_retry_delay(attempt, response))
                attempt += 1
                continue
            if response.status_code >= 400:
                raise error_from_response(response)
            return _parse_body(response)

    def get(self, path: str, *, params: Query = None) -> Any:
        return self.request("GET", path, params=params)

    def post(self, path: str, *, json: Body = None, params: Query = None) -> Any:
        return self.request("POST", path, json=json, params=params)

    def close(self) -> None:
        self._http.close()


class AsyncAPIClient:
    """Low-level asynchronous HTTP layer. Use :class:`airwallex.AsyncAirwallex` instead."""

    def __init__(self, config: _ClientConfig, http: Optional[httpx.AsyncClient] = None) -> None:
        self._config = config
        self._http = http or httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers=config.default_headers(),
        )
        self._token_manager = AsyncTokenManager(config.client_id, config.api_key)

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Query = None,
        json: Body = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        """Send an authenticated request, retrying transient failures."""
        auth_retried = False
        attempt = 0
        while True:
            token = await self._token_manager.get_token(self._http)
            request_headers = {"Authorization": f"Bearer {token}", **(headers or {})}
            try:
                response = await self._http.request(
                    method, path, params=params, json=json, headers=request_headers
                )
            except httpx.TransportError as exc:
                if attempt >= self._config.max_retries:
                    raise APIConnectionError(
                        f"Request failed after {attempt + 1} attempt(s): {exc}"
                    ) from exc
                await asyncio.sleep(_retry_delay(attempt, None))
                attempt += 1
                continue

            if response.status_code == 401 and not auth_retried:
                self._token_manager.invalidate()
                auth_retried = True
                continue
            retryable = response.status_code in RETRYABLE_STATUS_CODES
            if retryable and attempt < self._config.max_retries:
                await asyncio.sleep(_retry_delay(attempt, response))
                attempt += 1
                continue
            if response.status_code >= 400:
                raise error_from_response(response)
            return _parse_body(response)

    async def get(self, path: str, *, params: Query = None) -> Any:
        return await self.request("GET", path, params=params)

    async def post(self, path: str, *, json: Body = None, params: Query = None) -> Any:
        return await self.request("POST", path, json=json, params=params)

    async def close(self) -> None:
        await self._http.aclose()


AnyAPIClient = Union[SyncAPIClient, AsyncAPIClient]
