from __future__ import annotations

from typing import Any, Optional

from .._models import clean_params
from ._base import AsyncResource, SyncResource

_BASE = "/api/v1/reference"


class Reference(SyncResource):
    """Static reference data (currencies, settlement accounts, FX calendar)."""

    def supported_currencies(self) -> Any:
        """List currencies supported for collection and payout."""
        return self._client.get(f"{_BASE}/supported_currencies")

    def settlement_accounts(
        self, *, country_code: Optional[str] = None, currency: Optional[str] = None
    ) -> Any:
        """List settlement accounts available for the given corridor."""
        params = clean_params({"country_code": country_code, "currency": currency})
        return self._client.get(f"{_BASE}/settlement_accounts", params=params)

    def invalid_conversion_dates(self, *, currency_pair: str) -> Any:
        """List dates on which the given currency pair cannot settle."""
        return self._client.get(
            f"{_BASE}/invalid_conversion_dates", params={"currency_pair": currency_pair}
        )


class AsyncReference(AsyncResource):
    """Async counterpart of :class:`Reference`."""

    async def supported_currencies(self) -> Any:
        """List currencies supported for collection and payout."""
        return await self._client.get(f"{_BASE}/supported_currencies")

    async def settlement_accounts(
        self, *, country_code: Optional[str] = None, currency: Optional[str] = None
    ) -> Any:
        """List settlement accounts available for the given corridor."""
        params = clean_params({"country_code": country_code, "currency": currency})
        return await self._client.get(f"{_BASE}/settlement_accounts", params=params)

    async def invalid_conversion_dates(self, *, currency_pair: str) -> Any:
        """List dates on which the given currency pair cannot settle."""
        return await self._client.get(
            f"{_BASE}/invalid_conversion_dates", params={"currency_pair": currency_pair}
        )
