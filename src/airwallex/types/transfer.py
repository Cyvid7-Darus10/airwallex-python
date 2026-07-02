from __future__ import annotations

from typing import Any, Optional

from .._models import AirwallexModel
from .beneficiary import BeneficiaryDetails


class Transfer(AirwallexModel):
    """A payout to a beneficiary (``/api/v1/transfers``).

    Field names cover both the current API version and the legacy
    ``/api/v1/payments`` payload, since accounts pinned to older API
    versions receive the legacy names.
    """

    id: Optional[str] = None
    request_id: Optional[str] = None
    status: Optional[str] = None
    short_reference_id: Optional[str] = None

    source_amount: Optional[float] = None
    source_currency: Optional[str] = None
    transfer_amount: Optional[float] = None
    transfer_currency: Optional[str] = None
    transfer_method: Optional[str] = None
    transfer_date: Optional[str] = None

    amount_beneficiary_receives: Optional[float] = None
    amount_payer_pays: Optional[float] = None
    fee_amount: Optional[float] = None
    fee_currency: Optional[str] = None
    fee_paid_by: Optional[str] = None
    swift_charge_option: Optional[str] = None

    beneficiary: Optional[BeneficiaryDetails] = None
    beneficiary_id: Optional[str] = None
    payer: Optional[dict[str, Any]] = None

    reference: Optional[str] = None
    reason: Optional[str] = None
    remarks: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None

    failure_reason: Optional[str] = None
    failure_type: Optional[str] = None

    created_at: Optional[str] = None
    updated_at: Optional[str] = None
