from __future__ import annotations

from typing import Any, Optional

from .._pagination import AsyncPage, SyncPage
from ..types.global_account import GlobalAccount, GlobalAccountTransaction
from ._base import AsyncResource, SyncResource, ensure_request_id

_BASE = "/api/v1/global_accounts"


class GlobalAccounts(SyncResource):
    def list(
        self,
        *,
        currency: Optional[str] = None,
        country_code: Optional[str] = None,
        status: Optional[str] = None,
        nick_name: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
    ) -> SyncPage[GlobalAccount]:
        """List global accounts."""
        return self._paged(
            _BASE,
            GlobalAccount,
            {
                "currency": currency,
                "country_code": country_code,
                "status": status,
                "nick_name": nick_name,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
            },
        )

    def retrieve(self, global_account_id: str) -> GlobalAccount:
        """Fetch a single global account by id."""
        return GlobalAccount.model_validate(self._client.get(f"{_BASE}/{global_account_id}"))

    def create(self, **payload: Any) -> GlobalAccount:
        """Open a new global account. ``request_id`` is auto-generated if omitted."""
        body = ensure_request_id(payload)
        return GlobalAccount.model_validate(self._client.post(f"{_BASE}/create", json=body))

    def update(self, global_account_id: str, **payload: Any) -> GlobalAccount:
        """Update a global account (e.g. its nickname)."""
        return GlobalAccount.model_validate(
            self._client.post(f"{_BASE}/update/{global_account_id}", json=payload)
        )

    def close(self, global_account_id: str) -> GlobalAccount:
        """Close a global account."""
        return GlobalAccount.model_validate(self._client.post(f"{_BASE}/{global_account_id}/close"))

    def transactions(
        self,
        global_account_id: str,
        *,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
    ) -> SyncPage[GlobalAccountTransaction]:
        """List transactions received into a global account."""
        return self._paged(
            f"{_BASE}/{global_account_id}/transactions",
            GlobalAccountTransaction,
            {
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
            },
        )


class AsyncGlobalAccounts(AsyncResource):
    async def list(
        self,
        *,
        currency: Optional[str] = None,
        country_code: Optional[str] = None,
        status: Optional[str] = None,
        nick_name: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
    ) -> AsyncPage[GlobalAccount]:
        """List global accounts."""
        return await self._paged(
            _BASE,
            GlobalAccount,
            {
                "currency": currency,
                "country_code": country_code,
                "status": status,
                "nick_name": nick_name,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
            },
        )

    async def retrieve(self, global_account_id: str) -> GlobalAccount:
        """Fetch a single global account by id."""
        return GlobalAccount.model_validate(await self._client.get(f"{_BASE}/{global_account_id}"))

    async def create(self, **payload: Any) -> GlobalAccount:
        """Open a new global account. ``request_id`` is auto-generated if omitted."""
        body = ensure_request_id(payload)
        return GlobalAccount.model_validate(await self._client.post(f"{_BASE}/create", json=body))

    async def update(self, global_account_id: str, **payload: Any) -> GlobalAccount:
        """Update a global account (e.g. its nickname)."""
        return GlobalAccount.model_validate(
            await self._client.post(f"{_BASE}/update/{global_account_id}", json=payload)
        )

    async def close(self, global_account_id: str) -> GlobalAccount:
        """Close a global account."""
        return GlobalAccount.model_validate(
            await self._client.post(f"{_BASE}/{global_account_id}/close")
        )

    async def transactions(
        self,
        global_account_id: str,
        *,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
    ) -> AsyncPage[GlobalAccountTransaction]:
        """List transactions received into a global account."""
        return await self._paged(
            f"{_BASE}/{global_account_id}/transactions",
            GlobalAccountTransaction,
            {
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
            },
        )
