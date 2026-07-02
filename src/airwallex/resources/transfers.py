from __future__ import annotations

from typing import Any, Optional

from .._pagination import AsyncPage, SyncPage
from ..types.transfer import Transfer
from ._base import AsyncResource, SyncResource, ensure_request_id, pid

_BASE = "/api/v1/transfers"


class Transfers(SyncResource):
    """Payouts to beneficiaries.

    Requires an API version of 2024-01-31 or later (earlier versions call this
    resource ``payments``). Set ``api_version`` on the client if your account
    default is older.
    """

    def list(
        self,
        *,
        status: Optional[str] = None,
        currency: Optional[str] = None,
        request_id: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> SyncPage[Transfer]:
        """List transfers, optionally filtered by status/currency/date."""
        return self._paged(
            _BASE,
            Transfer,
            {
                "status": status,
                "currency": currency,
                "request_id": request_id,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    def retrieve(self, transfer_id: str) -> Transfer:
        """Fetch a single transfer by id."""
        return Transfer.model_validate(self._client.get(f"{_BASE}/{pid(transfer_id)}"))

    def create(self, **payload: Any) -> Transfer:
        """Create a payout.

        A ``request_id`` is generated automatically when not supplied, making
        the call idempotent — Airwallex will never execute the same
        ``request_id`` twice, even across the SDK's automatic retries.

        Example::

            client.transfers.create(
                beneficiary_id="ben_123",
                source_currency="USD",
                transfer_amount=100,
                transfer_currency="PHP",
                transfer_method="LOCAL",
                reference="Invoice 42",
                reason="professional_service_fees",
            )
        """
        body = ensure_request_id(payload)
        return Transfer.model_validate(self._client.post(f"{_BASE}/create", json=body))

    def cancel(self, transfer_id: str) -> Transfer:
        """Cancel a transfer that has not yet been dispatched."""
        return Transfer.model_validate(self._client.post(f"{_BASE}/{pid(transfer_id)}/cancel"))

    def validate(self, **payload: Any) -> Any:
        """Validate a transfer payload without creating it.

        Returns the raw validation result from Airwallex.
        """
        return self._client.post(f"{_BASE}/validate", json=payload)

    def confirm_funding(self, transfer_id: str, **payload: Any) -> Transfer:
        """Confirm funding for a transfer that is awaiting funds.

        Used with transfers created ahead of funding: once the money has
        arrived (or you choose the funding source), confirming releases the
        transfer for processing. Pass any funding details documented by
        Airwallex, e.g. ``funding_source_id=...``.
        """
        return Transfer.model_validate(
            self._client.post(f"{_BASE}/{pid(transfer_id)}/confirm_funding", json=payload or None)
        )


class AsyncTransfers(AsyncResource):
    """Async counterpart of :class:`Transfers`."""

    async def list(
        self,
        *,
        status: Optional[str] = None,
        currency: Optional[str] = None,
        request_id: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> AsyncPage[Transfer]:
        """List transfers, optionally filtered by status/currency/date."""
        return await self._paged(
            _BASE,
            Transfer,
            {
                "status": status,
                "currency": currency,
                "request_id": request_id,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    async def retrieve(self, transfer_id: str) -> Transfer:
        """Fetch a single transfer by id."""
        return Transfer.model_validate(await self._client.get(f"{_BASE}/{pid(transfer_id)}"))

    async def create(self, **payload: Any) -> Transfer:
        """Create a payout. See :meth:`Transfers.create`."""
        body = ensure_request_id(payload)
        return Transfer.model_validate(await self._client.post(f"{_BASE}/create", json=body))

    async def cancel(self, transfer_id: str) -> Transfer:
        """Cancel a transfer that has not yet been dispatched."""
        return Transfer.model_validate(
            await self._client.post(f"{_BASE}/{pid(transfer_id)}/cancel")
        )

    async def validate(self, **payload: Any) -> Any:
        """Validate a transfer payload without creating it."""
        return await self._client.post(f"{_BASE}/validate", json=payload)

    async def confirm_funding(self, transfer_id: str, **payload: Any) -> Transfer:
        """Confirm funding for a transfer awaiting funds. See :meth:`Transfers.confirm_funding`."""
        return Transfer.model_validate(
            await self._client.post(
                f"{_BASE}/{pid(transfer_id)}/confirm_funding", json=payload or None
            )
        )
