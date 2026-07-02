from __future__ import annotations

from typing import Any, Optional

from .._pagination import AsyncPage, SyncPage
from ..types.payment_acceptance import Customer, CustomerClientSecret, PaymentIntent, Refund
from ._base import AsyncResource, SyncResource, ensure_request_id, pid

_INTENTS = "/api/v1/pa/payment_intents"
_CUSTOMERS = "/api/v1/pa/customers"
_REFUNDS = "/api/v1/pa/refunds"


class PaymentIntents(SyncResource):
    """Payments collected from shoppers (``/api/v1/pa/payment_intents``)."""

    def list(
        self,
        *,
        status: Optional[str] = None,
        currency: Optional[str] = None,
        merchant_order_id: Optional[str] = None,
        payment_consent_id: Optional[str] = None,
        connected_account_id: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> SyncPage[PaymentIntent]:
        """List payment intents, optionally filtered by status/currency/order."""
        return self._paged(
            _INTENTS,
            PaymentIntent,
            {
                "status": status,
                "currency": currency,
                "merchant_order_id": merchant_order_id,
                "payment_consent_id": payment_consent_id,
                "connected_account_id": connected_account_id,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    def retrieve(self, payment_intent_id: str) -> PaymentIntent:
        """Fetch a single payment intent by id."""
        return PaymentIntent.model_validate(
            self._client.get(f"{_INTENTS}/{pid(payment_intent_id)}")
        )

    def create(self, **payload: Any) -> PaymentIntent:
        """Create a payment intent.

        A ``request_id`` is generated automatically when not supplied, making
        the call idempotent — Airwallex will never execute the same
        ``request_id`` twice, even across the SDK's automatic retries.

        Example::

            client.payment_intents.create(
                amount=25.00,
                currency="USD",
                merchant_order_id="order_42",
            )
        """
        body = ensure_request_id(payload)
        return PaymentIntent.model_validate(self._client.post(f"{_INTENTS}/create", json=body))

    def confirm(self, payment_intent_id: str, **payload: Any) -> PaymentIntent:
        """Confirm a payment intent with a payment method or consent."""
        return PaymentIntent.model_validate(
            self._client.post(f"{_INTENTS}/{pid(payment_intent_id)}/confirm", json=payload)
        )

    def confirm_continue(self, payment_intent_id: str, **payload: Any) -> PaymentIntent:
        """Continue confirming a payment intent (e.g. after a 3DS challenge)."""
        return PaymentIntent.model_validate(
            self._client.post(f"{_INTENTS}/{pid(payment_intent_id)}/confirm_continue", json=payload)
        )

    def capture(self, payment_intent_id: str, **payload: Any) -> PaymentIntent:
        """Capture funds authorized by a payment intent."""
        return PaymentIntent.model_validate(
            self._client.post(f"{_INTENTS}/{pid(payment_intent_id)}/capture", json=payload)
        )

    def cancel(self, payment_intent_id: str, **payload: Any) -> PaymentIntent:
        """Cancel a payment intent that has not been captured."""
        return PaymentIntent.model_validate(
            self._client.post(f"{_INTENTS}/{pid(payment_intent_id)}/cancel", json=payload)
        )


class Customers(SyncResource):
    """Shoppers whose payment details can be saved (``/api/v1/pa/customers``)."""

    def list(
        self,
        *,
        merchant_customer_id: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> SyncPage[Customer]:
        """List customers, optionally filtered by merchant customer id/date."""
        return self._paged(
            _CUSTOMERS,
            Customer,
            {
                "merchant_customer_id": merchant_customer_id,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    def retrieve(self, customer_id: str) -> Customer:
        """Fetch a single customer by id."""
        return Customer.model_validate(self._client.get(f"{_CUSTOMERS}/{pid(customer_id)}"))

    def create(self, **payload: Any) -> Customer:
        """Create a customer.

        A ``request_id`` is generated automatically when not supplied, making
        the call idempotent. Example::

            client.customers.create(merchant_customer_id="cust_42", email="jo@example.com")
        """
        body = ensure_request_id(payload)
        return Customer.model_validate(self._client.post(f"{_CUSTOMERS}/create", json=body))

    def update(self, customer_id: str, **payload: Any) -> Customer:
        """Update an existing customer."""
        return Customer.model_validate(
            self._client.post(f"{_CUSTOMERS}/{pid(customer_id)}/update", json=payload)
        )

    def generate_client_secret(self, customer_id: str) -> CustomerClientSecret:
        """Generate a short-lived client secret for customer-scoped calls."""
        return CustomerClientSecret.model_validate(
            self._client.get(f"{_CUSTOMERS}/{pid(customer_id)}/generate_client_secret")
        )


class Refunds(SyncResource):
    """Full or partial refunds of payments (``/api/v1/pa/refunds``)."""

    def list(
        self,
        *,
        status: Optional[str] = None,
        currency: Optional[str] = None,
        payment_intent_id: Optional[str] = None,
        payment_attempt_id: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> SyncPage[Refund]:
        """List refunds, optionally filtered by status/currency/payment."""
        return self._paged(
            _REFUNDS,
            Refund,
            {
                "status": status,
                "currency": currency,
                "payment_intent_id": payment_intent_id,
                "payment_attempt_id": payment_attempt_id,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    def retrieve(self, refund_id: str) -> Refund:
        """Fetch a single refund by id."""
        return Refund.model_validate(self._client.get(f"{_REFUNDS}/{pid(refund_id)}"))

    def create(self, **payload: Any) -> Refund:
        """Create a refund.

        A ``request_id`` is generated automatically when not supplied, making
        the call idempotent. Example::

            client.refunds.create(payment_intent_id="int_1", amount=10.00)
        """
        body = ensure_request_id(payload)
        return Refund.model_validate(self._client.post(f"{_REFUNDS}/create", json=body))


class AsyncPaymentIntents(AsyncResource):
    """Async counterpart of :class:`PaymentIntents`."""

    async def list(
        self,
        *,
        status: Optional[str] = None,
        currency: Optional[str] = None,
        merchant_order_id: Optional[str] = None,
        payment_consent_id: Optional[str] = None,
        connected_account_id: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> AsyncPage[PaymentIntent]:
        """List payment intents, optionally filtered by status/currency/order."""
        return await self._paged(
            _INTENTS,
            PaymentIntent,
            {
                "status": status,
                "currency": currency,
                "merchant_order_id": merchant_order_id,
                "payment_consent_id": payment_consent_id,
                "connected_account_id": connected_account_id,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    async def retrieve(self, payment_intent_id: str) -> PaymentIntent:
        """Fetch a single payment intent by id."""
        return PaymentIntent.model_validate(
            await self._client.get(f"{_INTENTS}/{pid(payment_intent_id)}")
        )

    async def create(self, **payload: Any) -> PaymentIntent:
        """Create a payment intent. See :meth:`PaymentIntents.create`."""
        body = ensure_request_id(payload)
        return PaymentIntent.model_validate(
            await self._client.post(f"{_INTENTS}/create", json=body)
        )

    async def confirm(self, payment_intent_id: str, **payload: Any) -> PaymentIntent:
        """Confirm a payment intent with a payment method or consent."""
        return PaymentIntent.model_validate(
            await self._client.post(f"{_INTENTS}/{pid(payment_intent_id)}/confirm", json=payload)
        )

    async def confirm_continue(self, payment_intent_id: str, **payload: Any) -> PaymentIntent:
        """Continue confirming a payment intent (e.g. after a 3DS challenge)."""
        return PaymentIntent.model_validate(
            await self._client.post(
                f"{_INTENTS}/{pid(payment_intent_id)}/confirm_continue", json=payload
            )
        )

    async def capture(self, payment_intent_id: str, **payload: Any) -> PaymentIntent:
        """Capture funds authorized by a payment intent."""
        return PaymentIntent.model_validate(
            await self._client.post(f"{_INTENTS}/{pid(payment_intent_id)}/capture", json=payload)
        )

    async def cancel(self, payment_intent_id: str, **payload: Any) -> PaymentIntent:
        """Cancel a payment intent that has not been captured."""
        return PaymentIntent.model_validate(
            await self._client.post(f"{_INTENTS}/{pid(payment_intent_id)}/cancel", json=payload)
        )


class AsyncCustomers(AsyncResource):
    """Async counterpart of :class:`Customers`."""

    async def list(
        self,
        *,
        merchant_customer_id: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> AsyncPage[Customer]:
        """List customers, optionally filtered by merchant customer id/date."""
        return await self._paged(
            _CUSTOMERS,
            Customer,
            {
                "merchant_customer_id": merchant_customer_id,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    async def retrieve(self, customer_id: str) -> Customer:
        """Fetch a single customer by id."""
        return Customer.model_validate(await self._client.get(f"{_CUSTOMERS}/{pid(customer_id)}"))

    async def create(self, **payload: Any) -> Customer:
        """Create a customer. See :meth:`Customers.create`."""
        body = ensure_request_id(payload)
        return Customer.model_validate(await self._client.post(f"{_CUSTOMERS}/create", json=body))

    async def update(self, customer_id: str, **payload: Any) -> Customer:
        """Update an existing customer."""
        return Customer.model_validate(
            await self._client.post(f"{_CUSTOMERS}/{pid(customer_id)}/update", json=payload)
        )

    async def generate_client_secret(self, customer_id: str) -> CustomerClientSecret:
        """Generate a short-lived client secret for customer-scoped calls."""
        return CustomerClientSecret.model_validate(
            await self._client.get(f"{_CUSTOMERS}/{pid(customer_id)}/generate_client_secret")
        )


class AsyncRefunds(AsyncResource):
    """Async counterpart of :class:`Refunds`."""

    async def list(
        self,
        *,
        status: Optional[str] = None,
        currency: Optional[str] = None,
        payment_intent_id: Optional[str] = None,
        payment_attempt_id: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> AsyncPage[Refund]:
        """List refunds, optionally filtered by status/currency/payment."""
        return await self._paged(
            _REFUNDS,
            Refund,
            {
                "status": status,
                "currency": currency,
                "payment_intent_id": payment_intent_id,
                "payment_attempt_id": payment_attempt_id,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    async def retrieve(self, refund_id: str) -> Refund:
        """Fetch a single refund by id."""
        return Refund.model_validate(await self._client.get(f"{_REFUNDS}/{pid(refund_id)}"))

    async def create(self, **payload: Any) -> Refund:
        """Create a refund. See :meth:`Refunds.create`."""
        body = ensure_request_id(payload)
        return Refund.model_validate(await self._client.post(f"{_REFUNDS}/create", json=body))
