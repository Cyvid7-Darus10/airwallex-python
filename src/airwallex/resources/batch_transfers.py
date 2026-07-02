from __future__ import annotations

from typing import Any, Optional

from .._pagination import AsyncPage, SyncPage
from ..types.batch_transfer import BatchTransfer, BatchTransferItem
from ._base import AsyncResource, SyncResource, ensure_request_id, pid

_BASE = "/api/v1/batch_transfers"

# Module-level aliases: inside the class bodies below, ``list`` refers to the
# resource's ``list`` method, so the builtin must be aliased out here.
_ItemDrafts = list[dict[str, Any]]
_ItemIds = list[str]


class BatchTransfers(SyncResource):
    """Batches of payouts created, quoted and submitted as a unit."""

    def list(
        self,
        *,
        status: Optional[str] = None,
        request_id: Optional[str] = None,
        short_reference_id: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> SyncPage[BatchTransfer]:
        """List batch transfers, optionally filtered by status/reference."""
        return self._paged(
            _BASE,
            BatchTransfer,
            {
                "status": status,
                "request_id": request_id,
                "short_reference_id": short_reference_id,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    def retrieve(self, batch_transfer_id: str) -> BatchTransfer:
        """Fetch a single batch transfer by id."""
        return BatchTransfer.model_validate(self._client.get(f"{_BASE}/{pid(batch_transfer_id)}"))

    def create(self, **payload: Any) -> BatchTransfer:
        """Create an empty batch to add transfer items to.

        A ``request_id`` is generated automatically when not supplied, making
        the call idempotent — Airwallex will never execute the same
        ``request_id`` twice, even across the SDK's automatic retries.

        Example::

            client.batch_transfers.create(
                name="July supplier run",
                transfer_date="2026-07-15",
            )
        """
        body = ensure_request_id(payload)
        return BatchTransfer.model_validate(self._client.post(f"{_BASE}/create", json=body))

    def add_items(self, batch_transfer_id: str, *, items: _ItemDrafts) -> BatchTransfer:
        """Add transfer items (payout drafts) to a batch."""
        return BatchTransfer.model_validate(
            self._client.post(f"{_BASE}/{pid(batch_transfer_id)}/add_items", json={"items": items})
        )

    def delete_items(self, batch_transfer_id: str, *, item_ids: _ItemIds) -> BatchTransfer:
        """Remove transfer items from a batch by item id."""
        return BatchTransfer.model_validate(
            self._client.post(
                f"{_BASE}/{pid(batch_transfer_id)}/delete_items", json={"item_ids": item_ids}
            )
        )

    def items(
        self,
        batch_transfer_id: str,
        *,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> SyncPage[BatchTransferItem]:
        """List the transfer items in a batch."""
        return self._paged(
            f"{_BASE}/{pid(batch_transfer_id)}/items",
            BatchTransferItem,
            {"page_num": page_num, "page_size": page_size, **extra_params},
        )

    def quote(self, batch_transfer_id: str, **payload: Any) -> BatchTransfer:
        """Lock FX quotes for every item in the batch.

        Optionally pass ``validity`` to control how long the quotes hold.
        """
        return BatchTransfer.model_validate(
            self._client.post(f"{_BASE}/{pid(batch_transfer_id)}/quote", json=payload or None)
        )

    def submit(self, batch_transfer_id: str) -> BatchTransfer:
        """Submit a quoted batch for execution."""
        return BatchTransfer.model_validate(
            self._client.post(f"{_BASE}/{pid(batch_transfer_id)}/submit")
        )

    def delete(self, batch_transfer_id: str) -> BatchTransfer:
        """Delete a batch that has not yet been submitted."""
        return BatchTransfer.model_validate(
            self._client.post(f"{_BASE}/{pid(batch_transfer_id)}/delete")
        )


class AsyncBatchTransfers(AsyncResource):
    """Async counterpart of :class:`BatchTransfers`."""

    async def list(
        self,
        *,
        status: Optional[str] = None,
        request_id: Optional[str] = None,
        short_reference_id: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> AsyncPage[BatchTransfer]:
        """List batch transfers, optionally filtered by status/reference."""
        return await self._paged(
            _BASE,
            BatchTransfer,
            {
                "status": status,
                "request_id": request_id,
                "short_reference_id": short_reference_id,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    async def retrieve(self, batch_transfer_id: str) -> BatchTransfer:
        """Fetch a single batch transfer by id."""
        return BatchTransfer.model_validate(
            await self._client.get(f"{_BASE}/{pid(batch_transfer_id)}")
        )

    async def create(self, **payload: Any) -> BatchTransfer:
        """Create an empty batch. See :meth:`BatchTransfers.create`."""
        body = ensure_request_id(payload)
        return BatchTransfer.model_validate(await self._client.post(f"{_BASE}/create", json=body))

    async def add_items(self, batch_transfer_id: str, *, items: _ItemDrafts) -> BatchTransfer:
        """Add transfer items (payout drafts) to a batch."""
        return BatchTransfer.model_validate(
            await self._client.post(
                f"{_BASE}/{pid(batch_transfer_id)}/add_items", json={"items": items}
            )
        )

    async def delete_items(self, batch_transfer_id: str, *, item_ids: _ItemIds) -> BatchTransfer:
        """Remove transfer items from a batch by item id."""
        return BatchTransfer.model_validate(
            await self._client.post(
                f"{_BASE}/{pid(batch_transfer_id)}/delete_items", json={"item_ids": item_ids}
            )
        )

    async def items(
        self,
        batch_transfer_id: str,
        *,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> AsyncPage[BatchTransferItem]:
        """List the transfer items in a batch."""
        return await self._paged(
            f"{_BASE}/{pid(batch_transfer_id)}/items",
            BatchTransferItem,
            {"page_num": page_num, "page_size": page_size, **extra_params},
        )

    async def quote(self, batch_transfer_id: str, **payload: Any) -> BatchTransfer:
        """Lock FX quotes for every item in the batch. See :meth:`BatchTransfers.quote`."""
        return BatchTransfer.model_validate(
            await self._client.post(f"{_BASE}/{pid(batch_transfer_id)}/quote", json=payload or None)
        )

    async def submit(self, batch_transfer_id: str) -> BatchTransfer:
        """Submit a quoted batch for execution."""
        return BatchTransfer.model_validate(
            await self._client.post(f"{_BASE}/{pid(batch_transfer_id)}/submit")
        )

    async def delete(self, batch_transfer_id: str) -> BatchTransfer:
        """Delete a batch that has not yet been submitted."""
        return BatchTransfer.model_validate(
            await self._client.post(f"{_BASE}/{pid(batch_transfer_id)}/delete")
        )
