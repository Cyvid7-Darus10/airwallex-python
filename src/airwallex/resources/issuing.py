from __future__ import annotations

from typing import Any, Optional

from .._pagination import AsyncPage, SyncPage
from ..types.issuing import (
    Card,
    Cardholder,
    CardLimits,
    IssuingAuthorization,
    IssuingTransaction,
)
from ._base import AsyncResource, SyncResource, ensure_request_id, pid

_CARDHOLDERS = "/api/v1/issuing/cardholders"
_CARDS = "/api/v1/issuing/cards"
_TRANSACTIONS = "/api/v1/issuing/transactions"
_AUTHORIZATIONS = "/api/v1/issuing/authorizations"


class IssuingCardholders(SyncResource):
    """People who can be issued corporate cards."""

    def list(
        self,
        *,
        cardholder_status: Optional[str] = None,
        email: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> SyncPage[Cardholder]:
        """List cardholders, optionally filtered by status/email."""
        return self._paged(
            _CARDHOLDERS,
            Cardholder,
            {
                "cardholder_status": cardholder_status,
                "email": email,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    def retrieve(self, cardholder_id: str) -> Cardholder:
        """Fetch a single cardholder by id."""
        return Cardholder.model_validate(self._client.get(f"{_CARDHOLDERS}/{pid(cardholder_id)}"))

    def create(self, **payload: Any) -> Cardholder:
        """Create a cardholder.

        Example::

            cardholders.create(
                email="jane@example.com",
                individual={
                    "name": {"first_name": "Jane", "last_name": "Doe"},
                    "date_of_birth": "1990-01-01",
                },
                mobile_number="+6591234567",
            )
        """
        return Cardholder.model_validate(self._client.post(f"{_CARDHOLDERS}/create", json=payload))

    def update(self, cardholder_id: str, **payload: Any) -> Cardholder:
        """Update an existing cardholder."""
        return Cardholder.model_validate(
            self._client.post(f"{_CARDHOLDERS}/{pid(cardholder_id)}/update", json=payload)
        )

    def delete(self, cardholder_id: str) -> Cardholder:
        """Delete a cardholder that has no active cards.

        The response carries ``cardholder_id`` and a ``deleted`` flag.
        """
        return Cardholder.model_validate(
            self._client.post(f"{_CARDHOLDERS}/{pid(cardholder_id)}/delete")
        )


class IssuingCards(SyncResource):
    """Issued corporate cards.

    The PCI-scoped endpoints (``/details`` and ``/provision_digital_token``)
    are intentionally not implemented; card numbers returned here are masked.
    """

    def list(
        self,
        *,
        card_status: Optional[str] = None,
        cardholder_id: Optional[str] = None,
        nick_name: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        from_updated_at: Optional[str] = None,
        to_updated_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> SyncPage[Card]:
        """List cards, optionally filtered by status/cardholder/date."""
        return self._paged(
            _CARDS,
            Card,
            {
                "card_status": card_status,
                "cardholder_id": cardholder_id,
                "nick_name": nick_name,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "from_updated_at": from_updated_at,
                "to_updated_at": to_updated_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    def retrieve(self, card_id: str) -> Card:
        """Fetch a single card by id."""
        return Card.model_validate(self._client.get(f"{_CARDS}/{pid(card_id)}"))

    def create(self, **payload: Any) -> Card:
        """Issue a new card.

        A ``request_id`` is generated automatically when not supplied, making
        the call idempotent — Airwallex will never execute the same
        ``request_id`` twice, even across the SDK's automatic retries.

        Example::

            cards.create(
                cardholder_id="chd_123",
                created_by="Jane Doe",
                form_factor="VIRTUAL",
                issue_to="INDIVIDUAL",
                purpose="COMMERCIAL",
                authorization_controls={
                    "allowed_transaction_count": "MULTIPLE",
                },
            )
        """
        body = ensure_request_id(payload)
        return Card.model_validate(self._client.post(f"{_CARDS}/create", json=body))

    def update(self, card_id: str, **payload: Any) -> Card:
        """Update an existing card (status, nickname, controls, ...)."""
        return Card.model_validate(
            self._client.post(f"{_CARDS}/{pid(card_id)}/update", json=payload)
        )

    def activate(self, card_id: str) -> None:
        """Activate a physical card so it can be used."""
        self._client.post(f"{_CARDS}/{pid(card_id)}/activate")

    def limits(self, card_id: str) -> CardLimits:
        """Fetch the card's remaining spend and cash-withdrawal limits."""
        return CardLimits.model_validate(self._client.get(f"{_CARDS}/{pid(card_id)}/limits"))


class IssuingTransactions(SyncResource):
    """Cleared card transactions (read-only)."""

    def list(
        self,
        *,
        card_id: Optional[str] = None,
        billing_currency: Optional[str] = None,
        transaction_type: Optional[str] = None,
        digital_wallet_token_id: Optional[str] = None,
        lifecycle_id: Optional[str] = None,
        retrieval_ref: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> SyncPage[IssuingTransaction]:
        """List card transactions, optionally filtered by card/type/date."""
        return self._paged(
            _TRANSACTIONS,
            IssuingTransaction,
            {
                "card_id": card_id,
                "billing_currency": billing_currency,
                "transaction_type": transaction_type,
                "digital_wallet_token_id": digital_wallet_token_id,
                "lifecycle_id": lifecycle_id,
                "retrieval_ref": retrieval_ref,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    def retrieve(self, transaction_id: str) -> IssuingTransaction:
        """Fetch a single card transaction by id."""
        return IssuingTransaction.model_validate(
            self._client.get(f"{_TRANSACTIONS}/{pid(transaction_id)}")
        )


class IssuingAuthorizations(SyncResource):
    """Pending card authorizations (read-only)."""

    def list(
        self,
        *,
        card_id: Optional[str] = None,
        status: Optional[str] = None,
        billing_currency: Optional[str] = None,
        digital_wallet_token_id: Optional[str] = None,
        lifecycle_id: Optional[str] = None,
        retrieval_ref: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> SyncPage[IssuingAuthorization]:
        """List card authorizations, optionally filtered by card/status/date."""
        return self._paged(
            _AUTHORIZATIONS,
            IssuingAuthorization,
            {
                "card_id": card_id,
                "status": status,
                "billing_currency": billing_currency,
                "digital_wallet_token_id": digital_wallet_token_id,
                "lifecycle_id": lifecycle_id,
                "retrieval_ref": retrieval_ref,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    def retrieve(self, authorization_id: str) -> IssuingAuthorization:
        """Fetch a single card authorization by id."""
        return IssuingAuthorization.model_validate(
            self._client.get(f"{_AUTHORIZATIONS}/{pid(authorization_id)}")
        )


class AsyncIssuingCardholders(AsyncResource):
    """Async counterpart of :class:`IssuingCardholders`."""

    async def list(
        self,
        *,
        cardholder_status: Optional[str] = None,
        email: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> AsyncPage[Cardholder]:
        """List cardholders, optionally filtered by status/email."""
        return await self._paged(
            _CARDHOLDERS,
            Cardholder,
            {
                "cardholder_status": cardholder_status,
                "email": email,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    async def retrieve(self, cardholder_id: str) -> Cardholder:
        """Fetch a single cardholder by id."""
        return Cardholder.model_validate(
            await self._client.get(f"{_CARDHOLDERS}/{pid(cardholder_id)}")
        )

    async def create(self, **payload: Any) -> Cardholder:
        """Create a cardholder. See :meth:`IssuingCardholders.create`."""
        return Cardholder.model_validate(
            await self._client.post(f"{_CARDHOLDERS}/create", json=payload)
        )

    async def update(self, cardholder_id: str, **payload: Any) -> Cardholder:
        """Update an existing cardholder."""
        return Cardholder.model_validate(
            await self._client.post(f"{_CARDHOLDERS}/{pid(cardholder_id)}/update", json=payload)
        )

    async def delete(self, cardholder_id: str) -> Cardholder:
        """Delete a cardholder. See :meth:`IssuingCardholders.delete`."""
        return Cardholder.model_validate(
            await self._client.post(f"{_CARDHOLDERS}/{pid(cardholder_id)}/delete")
        )


class AsyncIssuingCards(AsyncResource):
    """Async counterpart of :class:`IssuingCards`."""

    async def list(
        self,
        *,
        card_status: Optional[str] = None,
        cardholder_id: Optional[str] = None,
        nick_name: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        from_updated_at: Optional[str] = None,
        to_updated_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> AsyncPage[Card]:
        """List cards, optionally filtered by status/cardholder/date."""
        return await self._paged(
            _CARDS,
            Card,
            {
                "card_status": card_status,
                "cardholder_id": cardholder_id,
                "nick_name": nick_name,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "from_updated_at": from_updated_at,
                "to_updated_at": to_updated_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    async def retrieve(self, card_id: str) -> Card:
        """Fetch a single card by id."""
        return Card.model_validate(await self._client.get(f"{_CARDS}/{pid(card_id)}"))

    async def create(self, **payload: Any) -> Card:
        """Issue a new card. See :meth:`IssuingCards.create`."""
        body = ensure_request_id(payload)
        return Card.model_validate(await self._client.post(f"{_CARDS}/create", json=body))

    async def update(self, card_id: str, **payload: Any) -> Card:
        """Update an existing card (status, nickname, controls, ...)."""
        return Card.model_validate(
            await self._client.post(f"{_CARDS}/{pid(card_id)}/update", json=payload)
        )

    async def activate(self, card_id: str) -> None:
        """Activate a physical card so it can be used."""
        await self._client.post(f"{_CARDS}/{pid(card_id)}/activate")

    async def limits(self, card_id: str) -> CardLimits:
        """Fetch the card's remaining spend and cash-withdrawal limits."""
        return CardLimits.model_validate(await self._client.get(f"{_CARDS}/{pid(card_id)}/limits"))


class AsyncIssuingTransactions(AsyncResource):
    """Async counterpart of :class:`IssuingTransactions`."""

    async def list(
        self,
        *,
        card_id: Optional[str] = None,
        billing_currency: Optional[str] = None,
        transaction_type: Optional[str] = None,
        digital_wallet_token_id: Optional[str] = None,
        lifecycle_id: Optional[str] = None,
        retrieval_ref: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> AsyncPage[IssuingTransaction]:
        """List card transactions, optionally filtered by card/type/date."""
        return await self._paged(
            _TRANSACTIONS,
            IssuingTransaction,
            {
                "card_id": card_id,
                "billing_currency": billing_currency,
                "transaction_type": transaction_type,
                "digital_wallet_token_id": digital_wallet_token_id,
                "lifecycle_id": lifecycle_id,
                "retrieval_ref": retrieval_ref,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    async def retrieve(self, transaction_id: str) -> IssuingTransaction:
        """Fetch a single card transaction by id."""
        return IssuingTransaction.model_validate(
            await self._client.get(f"{_TRANSACTIONS}/{pid(transaction_id)}")
        )


class AsyncIssuingAuthorizations(AsyncResource):
    """Async counterpart of :class:`IssuingAuthorizations`."""

    async def list(
        self,
        *,
        card_id: Optional[str] = None,
        status: Optional[str] = None,
        billing_currency: Optional[str] = None,
        digital_wallet_token_id: Optional[str] = None,
        lifecycle_id: Optional[str] = None,
        retrieval_ref: Optional[str] = None,
        from_created_at: Optional[str] = None,
        to_created_at: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> AsyncPage[IssuingAuthorization]:
        """List card authorizations, optionally filtered by card/status/date."""
        return await self._paged(
            _AUTHORIZATIONS,
            IssuingAuthorization,
            {
                "card_id": card_id,
                "status": status,
                "billing_currency": billing_currency,
                "digital_wallet_token_id": digital_wallet_token_id,
                "lifecycle_id": lifecycle_id,
                "retrieval_ref": retrieval_ref,
                "from_created_at": from_created_at,
                "to_created_at": to_created_at,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    async def retrieve(self, authorization_id: str) -> IssuingAuthorization:
        """Fetch a single card authorization by id."""
        return IssuingAuthorization.model_validate(
            await self._client.get(f"{_AUTHORIZATIONS}/{pid(authorization_id)}")
        )
