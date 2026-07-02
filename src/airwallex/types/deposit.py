from __future__ import annotations

from typing import Any, Optional

from .._models import AirwallexModel


class Deposit(AirwallexModel):
    """An incoming deposit into the wallet (``GET /api/v1/deposits``)."""

    id: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    reference: Optional[str] = None
    payer: Optional[dict[str, Any]] = None
    fee: Optional[dict[str, Any]] = None
    funding_source_id: Optional[str] = None
    global_account_id: Optional[str] = None
    provider_transaction_id: Optional[str] = None
    estimated_settled_at: Optional[str] = None
    created_at: Optional[str] = None
