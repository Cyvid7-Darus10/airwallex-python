from __future__ import annotations

from typing import Any, Optional

import httpx

__all__ = [
    "APIConnectionError",
    "APIError",
    "APIStatusError",
    "AirwallexError",
    "AuthenticationError",
    "BadRequestError",
    "ConflictError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "ServerError",
    "WebhookSignatureError",
]


class AirwallexError(Exception):
    """Base class for every error raised by this SDK."""


class APIError(AirwallexError):
    """Base class for errors that occur while talking to the Airwallex API."""

    def __init__(self, message: str, *, request: Optional[httpx.Request] = None) -> None:
        super().__init__(message)
        self.message = message
        self.request = request


class APIConnectionError(APIError):
    """The request never received a valid response (network failure, timeout)."""


class APIStatusError(APIError):
    """The API responded with a non-success HTTP status code.

    Attributes:
        status_code: HTTP status code of the response.
        code: Airwallex machine-readable error code (e.g. ``validation_error``).
        source: Field or parameter the error refers to, when provided.
        request_id: Airwallex request id — include it when contacting support.
        body: Parsed JSON body of the error response, if any.
    """

    def __init__(
        self,
        message: str,
        *,
        response: httpx.Response,
        body: Optional[Any] = None,
    ) -> None:
        super().__init__(message, request=response.request)
        self.response = response
        self.status_code = response.status_code
        self.body = body
        details = body if isinstance(body, dict) else {}
        self.code: Optional[str] = details.get("code")
        self.source: Optional[str] = details.get("source")
        self.request_id: Optional[str] = response.headers.get("x-request-id")

    def __str__(self) -> str:
        parts = [f"[{self.status_code}] {self.message}"]
        if self.code:
            parts.append(f"code={self.code}")
        if self.source:
            parts.append(f"source={self.source}")
        if self.request_id:
            parts.append(f"request_id={self.request_id}")
        return " ".join(parts)


class BadRequestError(APIStatusError):
    """400 — the request was malformed or failed validation."""


class AuthenticationError(APIStatusError):
    """401 — credentials are missing, invalid, or the token expired."""


class PermissionDeniedError(APIStatusError):
    """403 — the credentials lack permission for this operation."""


class NotFoundError(APIStatusError):
    """404 — the requested resource does not exist."""


class ConflictError(APIStatusError):
    """409 — the request conflicts with the current resource state."""


class RateLimitError(APIStatusError):
    """429 — too many requests; retry after backing off."""


class ServerError(APIStatusError):
    """5xx — Airwallex had an internal problem."""


class WebhookSignatureError(AirwallexError):
    """A webhook payload failed signature verification."""


_STATUS_TO_ERROR: dict[int, type[APIStatusError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    409: ConflictError,
    429: RateLimitError,
}


def error_from_response(response: httpx.Response) -> APIStatusError:
    """Build the most specific error type for an HTTP error response."""
    try:
        body: Any = response.json()
    except ValueError:
        body = None
    if isinstance(body, dict):
        message = str(body.get("message") or body.get("error") or response.reason_phrase)
    else:
        message = response.text[:200] or response.reason_phrase
    error_cls = _STATUS_TO_ERROR.get(response.status_code)
    if error_cls is None:
        error_cls = ServerError if response.status_code >= 500 else APIStatusError
    return error_cls(message, response=response, body=body)
