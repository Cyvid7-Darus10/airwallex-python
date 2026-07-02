from __future__ import annotations

from typing import Any, Optional

from .._models import AirwallexModel


class Conversion(AirwallexModel):
    """An FX conversion between wallet currencies (``/api/v1/conversions``)."""

    conversion_id: Optional[str] = None
    request_id: Optional[str] = None
    short_reference_id: Optional[str] = None
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

    quote_id: Optional[str] = None
    conversion_date: Optional[str] = None
    settlement_cutoff_time: Optional[str] = None
    reason: Optional[str] = None

    created_at: Optional[str] = None
    last_updated_at: Optional[str] = None


class RateQuote(AirwallexModel):
    """An indicative or lockable FX quote (``/api/v1/rates/quote``)."""

    currency_pair: Optional[str] = None
    client_rate: Optional[float] = None
    mid_rate: Optional[float] = None
    dealt_currency: Optional[str] = None
    client_buy_amount: Optional[float] = None
    client_buy_currency: Optional[str] = None
    client_sell_amount: Optional[float] = None
    client_sell_currency: Optional[str] = None
    settlement_cutoff_time: Optional[str] = None
    settlement_date: Optional[str] = None
    rate_details: Optional[list[dict[str, Any]]] = None
