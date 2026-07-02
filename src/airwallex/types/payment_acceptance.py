from __future__ import annotations

from typing import Any, Optional

from .._models import AirwallexModel


class PaymentIntent(AirwallexModel):
    """A payment to be collected from a shopper (``/api/v1/pa/payment_intents``)."""

    id: Optional[str] = None
    request_id: Optional[str] = None
    status: Optional[str] = None

    amount: Optional[float] = None
    captured_amount: Optional[float] = None
    currency: Optional[str] = None

    merchant_order_id: Optional[str] = None
    invoice_id: Optional[str] = None
    payment_link_id: Optional[str] = None
    connected_account_id: Optional[str] = None
    conversion_quote_id: Optional[str] = None
    descriptor: Optional[str] = None
    return_url: Optional[str] = None
    client_secret: Optional[str] = None
    triggered_by: Optional[str] = None

    customer_id: Optional[str] = None
    customer: Optional[dict[str, Any]] = None
    payment_consent_id: Optional[str] = None
    payment_consent: Optional[dict[str, Any]] = None
    payment_method_options: Optional[dict[str, Any]] = None
    latest_payment_attempt: Optional[dict[str, Any]] = None
    next_action: Optional[dict[str, Any]] = None

    order: Optional[dict[str, Any]] = None
    additional_info: Optional[dict[str, Any]] = None
    funds_split_data: Optional[list[dict[str, Any]]] = None
    risk_control_options: Optional[dict[str, Any]] = None
    metadata: Optional[dict[str, Any]] = None

    cancellation_reason: Optional[str] = None
    cancelled_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class Customer(AirwallexModel):
    """A shopper whose payment details can be saved (``/api/v1/pa/customers``)."""

    id: Optional[str] = None
    request_id: Optional[str] = None
    merchant_customer_id: Optional[str] = None

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    business_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[dict[str, Any]] = None

    client_secret: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None

    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CustomerClientSecret(AirwallexModel):
    """A short-lived client secret for customer-scoped browser/mobile calls."""

    client_secret: Optional[str] = None
    expired_time: Optional[str] = None


class Refund(AirwallexModel):
    """A full or partial refund of a payment (``/api/v1/pa/refunds``)."""

    id: Optional[str] = None
    request_id: Optional[str] = None
    status: Optional[str] = None

    amount: Optional[float] = None
    currency: Optional[str] = None
    reason: Optional[str] = None

    payment_intent_id: Optional[str] = None
    payment_attempt_id: Optional[str] = None
    acquirer_reference_number: Optional[str] = None

    failure_details: Optional[dict[str, Any]] = None
    metadata: Optional[dict[str, Any]] = None

    created_at: Optional[str] = None
    updated_at: Optional[str] = None
