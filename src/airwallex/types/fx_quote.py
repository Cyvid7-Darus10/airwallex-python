from __future__ import annotations

from typing import Any, Optional

from .._models import AirwallexModel


class FxQuote(AirwallexModel):
    """A lockable FX quote (``/api/v1/fx/quotes``).

    Unlike the indicative rate returned by ``client.rates.current``, a quote
    created here has an ``id`` that can be referenced when executing a
    conversion, locking in the quoted rate until ``expires_at``.
    """

    id: Optional[str] = None
    request_id: Optional[str] = None
    status: Optional[str] = None

    currency_pair: Optional[str] = None
    buy_amount: Optional[float] = None
    buy_currency: Optional[str] = None
    sell_amount: Optional[float] = None
    sell_currency: Optional[str] = None
    dealt_currency: Optional[str] = None

    awx_rate: Optional[float] = None
    client_rate: Optional[float] = None
    mid_rate: Optional[float] = None
    rate_details: Optional[list[dict[str, Any]]] = None

    validity: Optional[str] = None
    conversion_date: Optional[str] = None
    expires_at: Optional[str] = None
    created_at: Optional[str] = None
