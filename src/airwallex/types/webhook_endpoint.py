from __future__ import annotations

from typing import Optional

from .._models import AirwallexModel


class WebhookEndpoint(AirwallexModel):
    """A registered webhook subscription (``/api/v1/webhooks``)."""

    id: Optional[str] = None
    request_id: Optional[str] = None
    url: Optional[str] = None
    secret: Optional[str] = None
    version: Optional[str] = None
    events: Optional[list[str]] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
