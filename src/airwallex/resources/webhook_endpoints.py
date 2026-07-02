from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Optional

from .._pagination import AsyncPage, SyncPage
from ..types.webhook_endpoint import WebhookEndpoint
from ._base import AsyncResource, SyncResource, ensure_request_id

_BASE = "/api/v1/webhooks"


class WebhookEndpoints(SyncResource):
    """Manage webhook subscriptions (where Airwallex sends event notifications)."""

    def list(
        self, *, page_num: int = 0, page_size: Optional[int] = None
    ) -> SyncPage[WebhookEndpoint]:
        """List registered webhook endpoints."""
        return self._paged(_BASE, WebhookEndpoint, {"page_num": page_num, "page_size": page_size})

    def retrieve(self, webhook_id: str) -> WebhookEndpoint:
        """Fetch a single webhook endpoint by id."""
        return WebhookEndpoint.model_validate(self._client.get(f"{_BASE}/{webhook_id}"))

    def create(self, *, url: str, events: Sequence[str], **payload: Any) -> WebhookEndpoint:
        """Register a webhook endpoint for the given event names."""
        body = ensure_request_id({"url": url, "events": list(events), **payload})
        return WebhookEndpoint.model_validate(self._client.post(f"{_BASE}/create", json=body))

    def update(self, webhook_id: str, **payload: Any) -> WebhookEndpoint:
        """Update a webhook endpoint's url or subscribed events."""
        return WebhookEndpoint.model_validate(
            self._client.post(f"{_BASE}/{webhook_id}/update", json=payload)
        )

    def delete(self, webhook_id: str) -> None:
        """Delete a webhook endpoint."""
        self._client.post(f"{_BASE}/{webhook_id}/delete")


class AsyncWebhookEndpoints(AsyncResource):
    """Async counterpart of :class:`WebhookEndpoints`."""

    async def list(
        self, *, page_num: int = 0, page_size: Optional[int] = None
    ) -> AsyncPage[WebhookEndpoint]:
        """List registered webhook endpoints."""
        return await self._paged(
            _BASE, WebhookEndpoint, {"page_num": page_num, "page_size": page_size}
        )

    async def retrieve(self, webhook_id: str) -> WebhookEndpoint:
        """Fetch a single webhook endpoint by id."""
        return WebhookEndpoint.model_validate(await self._client.get(f"{_BASE}/{webhook_id}"))

    async def create(self, *, url: str, events: Sequence[str], **payload: Any) -> WebhookEndpoint:
        """Register a webhook endpoint for the given event names."""
        body = ensure_request_id({"url": url, "events": list(events), **payload})
        return WebhookEndpoint.model_validate(await self._client.post(f"{_BASE}/create", json=body))

    async def update(self, webhook_id: str, **payload: Any) -> WebhookEndpoint:
        """Update a webhook endpoint's url or subscribed events."""
        return WebhookEndpoint.model_validate(
            await self._client.post(f"{_BASE}/{webhook_id}/update", json=payload)
        )

    async def delete(self, webhook_id: str) -> None:
        """Delete a webhook endpoint."""
        await self._client.post(f"{_BASE}/{webhook_id}/delete")
