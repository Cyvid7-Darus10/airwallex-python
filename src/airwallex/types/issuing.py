from __future__ import annotations

from typing import Any, Optional

from .._models import AirwallexModel


class Cardholder(AirwallexModel):
    """A person who can be issued cards (``/api/v1/issuing/cardholders``)."""

    cardholder_id: Optional[str] = None
    email: Optional[str] = None
    mobile_number: Optional[str] = None
    status: Optional[str] = None

    individual: Optional[dict[str, Any]] = None
    address: Optional[dict[str, Any]] = None
    postal_address: Optional[dict[str, Any]] = None


class Card(AirwallexModel):
    """An issued card (``/api/v1/issuing/cards``).

    Field names cover both the full card payload and the summary returned by
    the list endpoint. ``card_number`` is always masked — full PANs are only
    available via the PCI-scoped ``/details`` endpoint, which this SDK does
    not implement.
    """

    card_id: Optional[str] = None
    request_id: Optional[str] = None
    card_status: Optional[str] = None
    card_number: Optional[str] = None
    cardholder_id: Optional[str] = None

    brand: Optional[str] = None
    form_factor: Optional[str] = None
    type: Optional[str] = None
    issue_to: Optional[str] = None
    purpose: Optional[str] = None

    name_on_card: Optional[str] = None
    nick_name: Optional[str] = None
    note: Optional[str] = None
    client_data: Optional[str] = None
    created_by: Optional[str] = None
    activate_on_issue: Optional[bool] = None

    authorization_controls: Optional[dict[str, Any]] = None
    postal_address: Optional[dict[str, Any]] = None
    primary_contact_details: Optional[dict[str, Any]] = None
    delivery_details: Optional[dict[str, Any]] = None
    metadata: Optional[dict[str, Any]] = None

    card_version: Optional[int] = None
    all_card_versions: Optional[list[dict[str, Any]]] = None

    created_at: Optional[str] = None


class CardLimits(AirwallexModel):
    """Remaining spend limits for a card (``/api/v1/issuing/cards/{id}/limits``)."""

    currency: Optional[str] = None
    limits: Optional[list[dict[str, Any]]] = None
    cash_withdrawal_limits: Optional[list[dict[str, Any]]] = None


class IssuingTransaction(AirwallexModel):
    """A cleared card transaction (``/api/v1/issuing/transactions``)."""

    transaction_id: Optional[str] = None
    transaction_type: Optional[str] = None
    status: Optional[str] = None

    card_id: Optional[str] = None
    card_nickname: Optional[str] = None
    masked_card_number: Optional[str] = None
    digital_wallet_token_id: Optional[str] = None

    transaction_amount: Optional[float] = None
    transaction_currency: Optional[str] = None
    billing_amount: Optional[float] = None
    billing_currency: Optional[str] = None
    fee_details: Optional[list[dict[str, Any]]] = None

    merchant: Optional[dict[str, Any]] = None
    acquiring_institution_identifier: Optional[str] = None
    auth_code: Optional[str] = None
    network_transaction_id: Optional[str] = None
    retrieval_ref: Optional[str] = None
    lifecycle_id: Optional[str] = None
    matched_authorizations: Optional[list[str]] = None

    risk_details: Optional[dict[str, Any]] = None
    failure_reason: Optional[str] = None
    client_data: Optional[str] = None

    transaction_date: Optional[str] = None
    posted_date: Optional[str] = None


class IssuingAuthorization(AirwallexModel):
    """A pending card authorization (``/api/v1/issuing/authorizations``)."""

    transaction_id: Optional[str] = None
    status: Optional[str] = None

    card_id: Optional[str] = None
    card_nickname: Optional[str] = None
    masked_card_number: Optional[str] = None
    digital_wallet_token_id: Optional[str] = None

    transaction_amount: Optional[float] = None
    transaction_currency: Optional[str] = None
    billing_amount: Optional[float] = None
    billing_currency: Optional[str] = None
    fee_details: Optional[list[dict[str, Any]]] = None

    merchant: Optional[dict[str, Any]] = None
    acquiring_institution_identifier: Optional[str] = None
    auth_code: Optional[str] = None
    network_transaction_id: Optional[str] = None
    retrieval_ref: Optional[str] = None
    lifecycle_id: Optional[str] = None
    updated_by_transaction: Optional[str] = None

    risk_details: Optional[dict[str, Any]] = None
    failure_reason: Optional[str] = None
    client_data: Optional[str] = None

    create_time: Optional[str] = None
    expiry_date: Optional[str] = None
