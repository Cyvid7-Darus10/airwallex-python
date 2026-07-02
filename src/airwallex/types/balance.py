from __future__ import annotations

from typing import Optional

from .._models import AirwallexModel


class Balance(AirwallexModel):
    """A wallet balance in one currency (``GET /api/v1/balances/current``)."""

    currency: Optional[str] = None
    available_amount: Optional[float] = None
    pending_amount: Optional[float] = None
    reserved_amount: Optional[float] = None
    total_amount: Optional[float] = None


class BalanceHistoryItem(AirwallexModel):
    """One ledger movement from ``GET /api/v1/balances/history``."""

    currency: Optional[str] = None
    amount: Optional[float] = None
    balance: Optional[float] = None
    fee: Optional[float] = None
    description: Optional[str] = None
    source: Optional[str] = None
    source_type: Optional[str] = None
    posted_at: Optional[str] = None
