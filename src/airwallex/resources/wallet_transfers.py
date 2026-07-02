from __future__ import annotations

from typing import Any, Optional

from .._pagination import AsyncPage, SyncPage
from ..types.wallet_transfer import WalletTransfer
from ._base import AsyncResource, SyncResource, ensure_request_id, pid

_BASE = "/api/v1/wallet_transfers"


class WalletTransfers(SyncResource):
    """Transfers between Airwallex wallets."""

    def list(
        self,
        *,
        status: Optional[str] = None,
        transfer_currency: Optional[str] = None,
        request_id: Optional[str] = None,
        short_reference_id: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> SyncPage[WalletTransfer]:
        """List wallet transfers, optionally filtered by status/currency/date."""
        return self._paged(
            _BASE,
            WalletTransfer,
            {
                "status": status,
                "transfer_currency": transfer_currency,
                "request_id": request_id,
                "short_reference_id": short_reference_id,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    def retrieve(self, wallet_transfer_id: str) -> WalletTransfer:
        """Fetch a single wallet transfer by id."""
        return WalletTransfer.model_validate(self._client.get(f"{_BASE}/{pid(wallet_transfer_id)}"))

    def create(self, **payload: Any) -> WalletTransfer:
        """Send funds to another Airwallex wallet.

        A ``request_id`` is generated automatically when not supplied, making
        the call idempotent — Airwallex will never execute the same
        ``request_id`` twice, even across the SDK's automatic retries.

        Example::

            client.wallet_transfers.create(
                beneficiary={"account_number": "1234567"},
                transfer_amount=100,
                transfer_currency="USD",
                reference="Invoice 42",
                reason="business_expenses",
            )
        """
        body = ensure_request_id(payload)
        return WalletTransfer.model_validate(self._client.post(f"{_BASE}/create", json=body))


class AsyncWalletTransfers(AsyncResource):
    """Async counterpart of :class:`WalletTransfers`."""

    async def list(
        self,
        *,
        status: Optional[str] = None,
        transfer_currency: Optional[str] = None,
        request_id: Optional[str] = None,
        short_reference_id: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> AsyncPage[WalletTransfer]:
        """List wallet transfers, optionally filtered by status/currency/date."""
        return await self._paged(
            _BASE,
            WalletTransfer,
            {
                "status": status,
                "transfer_currency": transfer_currency,
                "request_id": request_id,
                "short_reference_id": short_reference_id,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    async def retrieve(self, wallet_transfer_id: str) -> WalletTransfer:
        """Fetch a single wallet transfer by id."""
        return WalletTransfer.model_validate(
            await self._client.get(f"{_BASE}/{pid(wallet_transfer_id)}")
        )

    async def create(self, **payload: Any) -> WalletTransfer:
        """Send funds to another Airwallex wallet. See :meth:`WalletTransfers.create`."""
        body = ensure_request_id(payload)
        return WalletTransfer.model_validate(await self._client.post(f"{_BASE}/create", json=body))
