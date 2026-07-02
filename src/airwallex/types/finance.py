from __future__ import annotations

from typing import Optional

from .._models import AirwallexModel


class FinancialTransaction(AirwallexModel):
    """One ledger entry from ``GET /api/v1/pa/financial/transactions``."""

    id: Optional[str] = None
    batch_id: Optional[str] = None
    source_id: Optional[str] = None
    funding_source_id: Optional[str] = None
    source_type: Optional[str] = None
    transaction_type: Optional[str] = None

    currency: Optional[str] = None
    amount: Optional[float] = None
    net: Optional[float] = None
    fee: Optional[float] = None
    client_rate: Optional[float] = None
    currency_pair: Optional[str] = None

    description: Optional[str] = None
    status: Optional[str] = None

    estimated_settled_at: Optional[str] = None
    settled_at: Optional[str] = None
    created_at: Optional[str] = None


class Settlement(AirwallexModel):
    """One settlement batch from ``GET /api/v1/pa/financial/settlements``."""

    id: Optional[str] = None
    currency: Optional[str] = None
    amount: Optional[float] = None
    fee: Optional[float] = None
    status: Optional[str] = None

    estimated_settled_at: Optional[str] = None
    settled_at: Optional[str] = None
    created_at: Optional[str] = None
