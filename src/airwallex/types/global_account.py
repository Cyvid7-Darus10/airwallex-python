from __future__ import annotations

from typing import Any, Optional

from .._models import AirwallexModel


class GlobalAccount(AirwallexModel):
    """A local currency account for collecting funds."""

    id: Optional[str] = None
    request_id: Optional[str] = None
    account_name: Optional[str] = None
    account_number: Optional[str] = None
    account_routing_type: Optional[str] = None
    account_routing_value: Optional[str] = None
    branch_code: Optional[str] = None
    clearing_systems: Optional[list[str]] = None
    country_code: Optional[str] = None
    currency: Optional[str] = None
    institution_name: Optional[str] = None
    nick_name: Optional[str] = None
    payment_methods: Optional[list[str]] = None
    status: Optional[str] = None
    swift_code: Optional[str] = None
    registered_email: Optional[str] = None
    alternate_account_identifiers: Optional[dict[str, Any]] = None


class GlobalAccountTransaction(AirwallexModel):
    """A transaction on a global account."""

    amount: Optional[float] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    fee: Optional[float] = None
    payer_name: Optional[str] = None
    reference: Optional[str] = None
    status: Optional[str] = None
    transaction_date: Optional[str] = None
