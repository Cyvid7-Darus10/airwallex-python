from __future__ import annotations

from ..types.account import Account
from ._base import AsyncResource, SyncResource

_BASE = "/api/v1/account"


class Accounts(SyncResource):
    """Details of the Airwallex account the API credentials belong to."""

    def retrieve(self) -> Account:
        """Fetch your own account details."""
        return Account.model_validate(self._client.get(_BASE))


class AsyncAccounts(AsyncResource):
    """Async counterpart of :class:`Accounts`."""

    async def retrieve(self) -> Account:
        """Fetch your own account details."""
        return Account.model_validate(await self._client.get(_BASE))
