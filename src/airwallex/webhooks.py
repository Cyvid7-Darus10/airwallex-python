"""Verify and parse incoming Airwallex webhook notifications.

Airwallex signs every webhook with your endpoint's secret:
``x-signature = HMAC_SHA256(secret, x-timestamp + raw_body)`` (hex encoded).

Typical usage inside a request handler::

    from airwallex import webhooks

    event = webhooks.construct_event(
        payload=request.body,           # raw bytes, NOT parsed/re-serialised JSON
        timestamp=request.headers["x-timestamp"],
        signature=request.headers["x-signature"],
        secret=WEBHOOK_SECRET,
    )
    if event.name == "transfer.settled":
        ...
"""

from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import json
from typing import Any, Optional, Union

from ._constants import DEFAULT_WEBHOOK_TOLERANCE_SECONDS
from ._errors import WebhookSignatureError
from ._models import AirwallexModel

__all__ = ["WebhookEvent", "construct_event", "verify_signature"]


class WebhookEvent(AirwallexModel):
    """A parsed webhook notification.

    ``data`` holds the resource payload; its exact shape depends on
    :attr:`name` — see the Airwallex event types documentation.
    """

    id: Optional[str] = None
    name: Optional[str] = None
    account_id: Optional[str] = None
    data: Optional[dict[str, Any]] = None
    created_at: Optional[str] = None


def verify_signature(
    *,
    payload: Union[bytes, str],
    timestamp: str,
    signature: str,
    secret: str,
    tolerance_seconds: Optional[int] = DEFAULT_WEBHOOK_TOLERANCE_SECONDS,
) -> None:
    """Raise :class:`~airwallex.WebhookSignatureError` unless the payload is authentic.

    Pass the *raw* request body exactly as received — re-serialising the JSON
    will change the bytes and invalidate the signature.

    Set ``tolerance_seconds=None`` to skip the replay-protection timestamp
    check (useful when replaying stored deliveries in tests).
    """
    if not secret:
        raise ValueError("secret is required to verify webhook signatures")
    body = payload.encode("utf-8") if isinstance(payload, str) else payload

    if tolerance_seconds is not None:
        try:
            sent_at = float(timestamp)
        except (TypeError, ValueError) as exc:
            raise WebhookSignatureError(f"Invalid x-timestamp header: {timestamp!r}") from exc
        # Airwallex sends unix timestamps in milliseconds.
        if sent_at > 1e12:
            sent_at /= 1000.0
        now = dt.datetime.now(dt.timezone.utc).timestamp()
        if abs(now - sent_at) > tolerance_seconds:
            raise WebhookSignatureError(
                f"Webhook timestamp is outside the allowed tolerance of "
                f"{tolerance_seconds}s; possible replay"
            )

    expected = hmac.new(
        secret.encode("utf-8"),
        timestamp.encode("utf-8") + body,
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, (signature or "").strip()):
        raise WebhookSignatureError("Webhook signature does not match the payload")


def construct_event(
    *,
    payload: Union[bytes, str],
    timestamp: str,
    signature: str,
    secret: str,
    tolerance_seconds: Optional[int] = DEFAULT_WEBHOOK_TOLERANCE_SECONDS,
) -> WebhookEvent:
    """Verify the signature and return the parsed :class:`WebhookEvent`."""
    verify_signature(
        payload=payload,
        timestamp=timestamp,
        signature=signature,
        secret=secret,
        tolerance_seconds=tolerance_seconds,
    )
    body = payload.decode("utf-8") if isinstance(payload, bytes) else payload
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise WebhookSignatureError("Webhook payload is not valid JSON") from exc
    return WebhookEvent.model_validate(parsed)
