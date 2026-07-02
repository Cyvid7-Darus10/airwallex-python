"""Unofficial Python SDK for the Airwallex API.

Quickstart::

    from airwallex import Airwallex

    client = Airwallex(client_id="...", api_key="...", environment="demo")
    balances = client.balances.current()
"""

from . import webhooks
from ._errors import (
    AirwallexError,
    APIConnectionError,
    APIError,
    APIStatusError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    WebhookSignatureError,
)
from ._pagination import AsyncPage, SyncPage
from ._version import __version__
from .client import Airwallex, AsyncAirwallex
from .webhooks import WebhookEvent

__all__ = [
    "APIConnectionError",
    "APIError",
    "APIStatusError",
    "Airwallex",
    "AirwallexError",
    "AsyncAirwallex",
    "AsyncPage",
    "AuthenticationError",
    "BadRequestError",
    "ConflictError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "ServerError",
    "SyncPage",
    "WebhookEvent",
    "WebhookSignatureError",
    "__version__",
    "webhooks",
]
