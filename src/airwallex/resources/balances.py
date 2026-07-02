from __future__ import annotations

from typing import Optional

from .._pagination import AsyncPage, SyncPage
from ..types.balance import Balance, BalanceHistoryItem
from ._base import AsyncResource, SyncResource

_CURRENT_PATH = "/api/v1/balances/current"
_HISTORY_PATH = "/api/v1/balances/history"


class Balances(SyncResource):
    def current(self) -> list[Balance]:
        """Retrieve the current balance for every wallet currency."""
        data = self._client.get(_CURRENT_PATH) or []
        return [Balance.model_validate(item) for item in data]

    def history(
        self,
        *,
        currency: Optional[str] = None,
        from_post_at: Optional[str] = None,
        to_post_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
    ) -> SyncPage[BalanceHistoryItem]:
        """List ledger movements, newest first."""
        return self._paged(
            _HISTORY_PATH,
            BalanceHistoryItem,
            {
                "currency": currency,
                "from_post_at": from_post_at,
                "to_post_at": to_post_at,
                "page_num": page_num,
                "page_size": page_size,
            },
        )


class AsyncBalances(AsyncResource):
    async def current(self) -> list[Balance]:
        """Retrieve the current balance for every wallet currency."""
        data = await self._client.get(_CURRENT_PATH) or []
        return [Balance.model_validate(item) for item in data]

    async def history(
        self,
        *,
        currency: Optional[str] = None,
        from_post_at: Optional[str] = None,
        to_post_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
    ) -> AsyncPage[BalanceHistoryItem]:
        """List ledger movements, newest first."""
        return await self._paged(
            _HISTORY_PATH,
            BalanceHistoryItem,
            {
                "currency": currency,
                "from_post_at": from_post_at,
                "to_post_at": to_post_at,
                "page_num": page_num,
                "page_size": page_size,
            },
        )
