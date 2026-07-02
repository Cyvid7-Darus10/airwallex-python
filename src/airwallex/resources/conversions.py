from __future__ import annotations

from typing import Any, Optional

from .._models import clean_params
from .._pagination import AsyncPage, SyncPage
from ..types.conversion import Conversion, RateQuote
from ._base import AsyncResource, SyncResource, ensure_request_id, pid

_BASE = "/api/v1/conversions"
_RATES_CURRENT = "/api/v1/fx/rates/current"


class Conversions(SyncResource):
    def list(
        self,
        *,
        status: Optional[str] = None,
        buy_currency: Optional[str] = None,
        sell_currency: Optional[str] = None,
        request_id: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> SyncPage[Conversion]:
        """List FX conversions."""
        return self._paged(
            _BASE,
            Conversion,
            {
                "status": status,
                "buy_currency": buy_currency,
                "sell_currency": sell_currency,
                "request_id": request_id,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    def retrieve(self, conversion_id: str) -> Conversion:
        """Fetch a single conversion by id."""
        return Conversion.model_validate(self._client.get(f"{_BASE}/{pid(conversion_id)}"))

    def create(self, **payload: Any) -> Conversion:
        """Execute an FX conversion between wallet currencies.

        A ``request_id`` is generated automatically when not supplied so the
        conversion is idempotent. Specify exactly one of ``buy_amount`` or
        ``sell_amount``::

            client.conversions.create(
                buy_currency="USD", sell_currency="SGD", buy_amount=1000, term_agreement=True
            )
        """
        body = ensure_request_id(payload)
        return Conversion.model_validate(self._client.post(f"{_BASE}/create", json=body))


class Rates(SyncResource):
    def current(
        self,
        *,
        buy_currency: str,
        sell_currency: str,
        buy_amount: Optional[float] = None,
        sell_amount: Optional[float] = None,
        conversion_date: Optional[str] = None,
    ) -> RateQuote:
        """Get the current indicative FX rate (no funds move).

        Specify at most one of ``buy_amount`` / ``sell_amount``; Airwallex
        defaults to a notional amount of 10,000 when neither is given.
        """
        params = clean_params(
            {
                "buy_currency": buy_currency,
                "sell_currency": sell_currency,
                "buy_amount": buy_amount,
                "sell_amount": sell_amount,
                "conversion_date": conversion_date,
            }
        )
        return RateQuote.model_validate(self._client.get(_RATES_CURRENT, params=params))


class AsyncConversions(AsyncResource):
    async def list(
        self,
        *,
        status: Optional[str] = None,
        buy_currency: Optional[str] = None,
        sell_currency: Optional[str] = None,
        request_id: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> AsyncPage[Conversion]:
        """List FX conversions."""
        return await self._paged(
            _BASE,
            Conversion,
            {
                "status": status,
                "buy_currency": buy_currency,
                "sell_currency": sell_currency,
                "request_id": request_id,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    async def retrieve(self, conversion_id: str) -> Conversion:
        """Fetch a single conversion by id."""
        return Conversion.model_validate(await self._client.get(f"{_BASE}/{pid(conversion_id)}"))

    async def create(self, **payload: Any) -> Conversion:
        """Execute an FX conversion. See :meth:`Conversions.create`."""
        body = ensure_request_id(payload)
        return Conversion.model_validate(await self._client.post(f"{_BASE}/create", json=body))


class AsyncRates(AsyncResource):
    async def current(
        self,
        *,
        buy_currency: str,
        sell_currency: str,
        buy_amount: Optional[float] = None,
        sell_amount: Optional[float] = None,
        conversion_date: Optional[str] = None,
    ) -> RateQuote:
        """Get the current indicative FX rate. See :meth:`Rates.current`."""
        params = clean_params(
            {
                "buy_currency": buy_currency,
                "sell_currency": sell_currency,
                "buy_amount": buy_amount,
                "sell_amount": sell_amount,
                "conversion_date": conversion_date,
            }
        )
        return RateQuote.model_validate(await self._client.get(_RATES_CURRENT, params=params))
