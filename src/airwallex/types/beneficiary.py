from __future__ import annotations

from typing import Any, Optional

from .._models import AirwallexModel


class BankDetails(AirwallexModel):
    """Bank account details of a beneficiary."""

    account_currency: Optional[str] = None
    account_name: Optional[str] = None
    account_number: Optional[str] = None
    account_routing_type1: Optional[str] = None
    account_routing_value1: Optional[str] = None
    account_routing_type2: Optional[str] = None
    account_routing_value2: Optional[str] = None
    bank_country_code: Optional[str] = None
    bank_name: Optional[str] = None
    bank_branch: Optional[str] = None
    iban: Optional[str] = None
    swift_code: Optional[str] = None
    local_clearing_system: Optional[str] = None


class BeneficiaryDetails(AirwallexModel):
    """The beneficiary entity itself (person or company)."""

    entity_type: Optional[str] = None
    company_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    bank_details: Optional[BankDetails] = None
    address: Optional[dict[str, Any]] = None
    additional_info: Optional[dict[str, Any]] = None


class Beneficiary(AirwallexModel):
    """A saved payout destination (``/api/v1/beneficiaries``)."""

    beneficiary_id: Optional[str] = None
    nickname: Optional[str] = None
    payer_entity_type: Optional[str] = None
    payment_methods: Optional[list[str]] = None
    beneficiary: Optional[BeneficiaryDetails] = None
