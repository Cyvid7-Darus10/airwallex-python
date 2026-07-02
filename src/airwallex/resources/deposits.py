from __future__ import annotations

from typing import Optional

from .._pagination import AsyncPage, SyncPage
from ..types.deposit import Deposit
from ._base import AsyncResource, SyncResource

_BASE = "/api/v1/deposits"


class Deposits(SyncResource):
    def list(
        self,
        *,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
    ) -> SyncPage[Deposit]:
        """List deposits received into the wallet."""
        return self._paged(
            _BASE,
            Deposit,
            {
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
            },
        )


class AsyncDeposits(AsyncResource):
    async def list(
        self,
        *,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
    ) -> AsyncPage[Deposit]:
        """List deposits received into the wallet."""
        return await self._paged(
            _BASE,
            Deposit,
            {
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
            },
        )
