from __future__ import annotations

from typing import Literal

Environment = Literal["production", "demo"]

BASE_URLS: dict[str, str] = {
    "production": "https://api.airwallex.com",
    "demo": "https://api-demo.airwallex.com",
}

LOGIN_PATH = "/api/v1/authentication/login"

# Airwallex bearer tokens live ~30 minutes; refresh this many seconds early
# so an in-flight request never carries a token that expires mid-request.
TOKEN_REFRESH_LEEWAY_SECONDS = 60.0

DEFAULT_TIMEOUT_SECONDS = 60.0
DEFAULT_MAX_RETRIES = 2
DEFAULT_INITIAL_RETRY_DELAY_SECONDS = 0.5
DEFAULT_MAX_RETRY_DELAY_SECONDS = 8.0

RETRYABLE_STATUS_CODES = frozenset({408, 409, 429, 500, 502, 503, 504})

# Webhook signatures older than this are rejected to limit replay attacks.
DEFAULT_WEBHOOK_TOLERANCE_SECONDS = 300
