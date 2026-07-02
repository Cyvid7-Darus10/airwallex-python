from __future__ import annotations

from typing import Any

from ..types.fx_quote import FxQuote
from ._base import AsyncResource, SyncResource, ensure_request_id, pid

_BASE = "/api/v1/fx/quotes"


class Quotes(SyncResource):
    """Lockable FX quotes (``/api/v1/fx/quotes``).

    A quote locks a rate for a currency pair until it expires; pass its id
    when executing a conversion to trade at exactly the quoted rate. For a
    purely indicative rate, use ``client.rates.current`` instead.
    """

    def create(self, **payload: Any) -> FxQuote:
        """Create a lockable FX quote.

        A ``request_id`` is generated automatically when not supplied, making
        the call idempotent — Airwallex will never execute the same
        ``request_id`` twice, even across the SDK's automatic retries.

        Example::

            quotes.create(
                buy_currency="USD",
                sell_currency="SGD",
                buy_amount=1000,
                validity="1_HOUR",
            )
        """
        body = ensure_request_id(payload)
        return FxQuote.model_validate(self._client.post(f"{_BASE}/create", json=body))

    def retrieve(self, quote_id: str) -> FxQuote:
        """Fetch a single FX quote by id."""
        return FxQuote.model_validate(self._client.get(f"{_BASE}/{pid(quote_id)}"))


class AsyncQuotes(AsyncResource):
    """Async counterpart of :class:`Quotes`."""

    async def create(self, **payload: Any) -> FxQuote:
        """Create a lockable FX quote. See :meth:`Quotes.create`."""
        body = ensure_request_id(payload)
        return FxQuote.model_validate(await self._client.post(f"{_BASE}/create", json=body))

    async def retrieve(self, quote_id: str) -> FxQuote:
        """Fetch a single FX quote by id."""
        return FxQuote.model_validate(await self._client.get(f"{_BASE}/{pid(quote_id)}"))
