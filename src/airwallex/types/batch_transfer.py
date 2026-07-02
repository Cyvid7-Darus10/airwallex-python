from __future__ import annotations

from typing import Any, Optional

from .._models import AirwallexModel


class BatchQuoteDetails(AirwallexModel):
    """A per-currency-pair quote inside a batch quote summary."""

    amount_beneficiary_receives: Optional[float] = None
    amount_payer_pays: Optional[float] = None
    client_rate: Optional[float] = None
    currency_pair: Optional[str] = None
    fee_amount: Optional[float] = None
    fee_currency: Optional[str] = None
    payment_currency: Optional[str] = None
    source_currency: Optional[str] = None


class BatchQuoteSummary(AirwallexModel):
    """The aggregated FX quotes locked for a batch transfer."""

    expires_at: Optional[str] = None
    last_quoted_at: Optional[str] = None
    quotes: Optional[list[BatchQuoteDetails]] = None
    validity: Optional[str] = None


class BatchFunding(AirwallexModel):
    """Funding status of a batch transfer."""

    deposit_type: Optional[str] = None
    failure_details: Optional[dict[str, Any]] = None
    failure_reason: Optional[str] = None
    funding_source_id: Optional[str] = None
    reference: Optional[str] = None
    status: Optional[str] = None


class BatchTransfer(AirwallexModel):
    """A batch of payouts processed together (``/api/v1/batch_transfers``)."""

    id: Optional[str] = None
    request_id: Optional[str] = None
    short_reference_id: Optional[str] = None
    status: Optional[str] = None
    name: Optional[str] = None
    remarks: Optional[str] = None

    funding: Optional[BatchFunding] = None
    quote_summary: Optional[BatchQuoteSummary] = None

    total_item_count: Optional[int] = None
    valid_item_count: Optional[int] = None
    transfer_date: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    updated_at: Optional[str] = None


class BatchTransferItem(AirwallexModel):
    """A single payout inside a batch (``/api/v1/batch_transfers/{id}/items``)."""

    id: Optional[str] = None
    request_id: Optional[str] = None
    status: Optional[str] = None
    transfer_draft: Optional[dict[str, Any]] = None
    transfer_id: Optional[str] = None
    errors: Optional[list[dict[str, Any]]] = None
    updated_at: Optional[str] = None
