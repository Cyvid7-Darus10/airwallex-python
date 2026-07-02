from __future__ import annotations

from typing import Any, Optional

from .._pagination import AsyncPage, SyncPage
from ..types.finance import FinancialTransaction, Settlement
from ._base import AsyncResource, SyncResource, pid

_TRANSACTIONS_BASE = "/api/v1/pa/financial/transactions"
_SETTLEMENTS_BASE = "/api/v1/pa/financial/settlements"


class FinancialTransactions(SyncResource):
    """Ledger entries behind every money movement on the account."""

    def list(
        self,
        *,
        batch_id: Optional[str] = None,
        currency: Optional[str] = None,
        source_id: Optional[str] = None,
        status: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> SyncPage[FinancialTransaction]:
        """List financial transactions, optionally filtered by batch/currency/status/date."""
        return self._paged(
            _TRANSACTIONS_BASE,
            FinancialTransaction,
            {
                "batch_id": batch_id,
                "currency": currency,
                "source_id": source_id,
                "status": status,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    def retrieve(self, transaction_id: str) -> FinancialTransaction:
        """Fetch a single financial transaction by id."""
        return FinancialTransaction.model_validate(
            self._client.get(f"{_TRANSACTIONS_BASE}/{pid(transaction_id)}")
        )


class AsyncFinancialTransactions(AsyncResource):
    """Async counterpart of :class:`FinancialTransactions`."""

    async def list(
        self,
        *,
        batch_id: Optional[str] = None,
        currency: Optional[str] = None,
        source_id: Optional[str] = None,
        status: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> AsyncPage[FinancialTransaction]:
        """List financial transactions, optionally filtered by batch/currency/status/date."""
        return await self._paged(
            _TRANSACTIONS_BASE,
            FinancialTransaction,
            {
                "batch_id": batch_id,
                "currency": currency,
                "source_id": source_id,
                "status": status,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    async def retrieve(self, transaction_id: str) -> FinancialTransaction:
        """Fetch a single financial transaction by id."""
        return FinancialTransaction.model_validate(
            await self._client.get(f"{_TRANSACTIONS_BASE}/{pid(transaction_id)}")
        )


class Settlements(SyncResource):
    """Settlement batches paid out to the account."""

    def list(
        self,
        *,
        currency: Optional[str] = None,
        status: Optional[str] = None,
        from_settled_at: Optional[str] = None,
        to_settled_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> SyncPage[Settlement]:
        """List settlements, optionally filtered by currency/status/settled date."""
        return self._paged(
            _SETTLEMENTS_BASE,
            Settlement,
            {
                "currency": currency,
                "status": status,
                "from_settled_at": from_settled_at,
                "to_settled_at": to_settled_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    def retrieve(self, settlement_id: str) -> Settlement:
        """Fetch a single settlement by id."""
        return Settlement.model_validate(
            self._client.get(f"{_SETTLEMENTS_BASE}/{pid(settlement_id)}")
        )


class AsyncSettlements(AsyncResource):
    """Async counterpart of :class:`Settlements`."""

    async def list(
        self,
        *,
        currency: Optional[str] = None,
        status: Optional[str] = None,
        from_settled_at: Optional[str] = None,
        to_settled_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> AsyncPage[Settlement]:
        """List settlements, optionally filtered by currency/status/settled date."""
        return await self._paged(
            _SETTLEMENTS_BASE,
            Settlement,
            {
                "currency": currency,
                "status": status,
                "from_settled_at": from_settled_at,
                "to_settled_at": to_settled_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    async def retrieve(self, settlement_id: str) -> Settlement:
        """Fetch a single settlement by id."""
        return Settlement.model_validate(
            await self._client.get(f"{_SETTLEMENTS_BASE}/{pid(settlement_id)}")
        )
