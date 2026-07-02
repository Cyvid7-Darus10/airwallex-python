from __future__ import annotations

import json
import uuid

import pytest
import respx

from airwallex import Airwallex, NotFoundError
from airwallex.resources.issuing import (
    AsyncIssuingCards,
    IssuingAuthorizations,
    IssuingCardholders,
    IssuingCards,
    IssuingTransactions,
)


def test_card_create_auto_generates_request_id(api: respx.MockRouter, client: Airwallex):
    route = api.post("/api/v1/issuing/cards/create").respond(
        202, json={"card_id": "crd_1", "card_status": "PENDING", "request_id": "ignored"}
    )
    card = IssuingCards(client._api).create(
        cardholder_id="chd_1",
        created_by="Jane Doe",
        form_factor="VIRTUAL",
        issue_to="INDIVIDUAL",
        purpose="COMMERCIAL",
    )
    assert card.card_id == "crd_1"
    body = json.loads(route.calls[0].request.content)
    uuid.UUID(body["request_id"])  # valid auto-generated uuid
    assert body["form_factor"] == "VIRTUAL"


def test_card_create_respects_explicit_request_id(api: respx.MockRouter, client: Airwallex):
    route = api.post("/api/v1/issuing/cards/create").respond(202, json={"card_id": "crd_1"})
    IssuingCards(client._api).create(request_id="my-id-1", cardholder_id="chd_1")
    body = json.loads(route.calls[0].request.content)
    assert body["request_id"] == "my-id-1"


def test_card_retrieve_and_list_with_filters(api: respx.MockRouter, client: Airwallex):
    cards = IssuingCards(client._api)
    api.get("/api/v1/issuing/cards/crd_1").respond(
        200,
        json={
            "card_id": "crd_1",
            "card_status": "ACTIVE",
            "card_number": "************4242",
            "brand": "VISA",
        },
    )
    card = cards.retrieve("crd_1")
    assert card.card_status == "ACTIVE"
    assert card.brand == "VISA"

    list_route = api.get("/api/v1/issuing/cards").respond(
        200, json={"has_more": False, "items": [{"card_id": "crd_1", "cardholder_id": "chd_1"}]}
    )
    page = cards.list(card_status="ACTIVE", cardholder_id="chd_1")
    assert page.items[0].card_id == "crd_1"
    params = list_route.calls[0].request.url.params
    assert params["card_status"] == "ACTIVE"
    assert params["cardholder_id"] == "chd_1"


def test_card_update_activate_and_limits(api: respx.MockRouter, client: Airwallex):
    cards = IssuingCards(client._api)
    update_route = api.post("/api/v1/issuing/cards/crd_1/update").respond(
        200, json={"card_id": "crd_1", "nick_name": "Team lunches"}
    )
    updated = cards.update("crd_1", nick_name="Team lunches")
    assert updated.nick_name == "Team lunches"
    assert json.loads(update_route.calls[0].request.content) == {"nick_name": "Team lunches"}

    activate_route = api.post("/api/v1/issuing/cards/crd_1/activate").respond(202)
    assert cards.activate("crd_1") is None
    assert activate_route.called

    api.get("/api/v1/issuing/cards/crd_1/limits").respond(
        200,
        json={
            "currency": "USD",
            "limits": [{"amount": 5000, "interval": "PER_TRANSACTION", "remaining": 4200}],
        },
    )
    limits = cards.limits("crd_1")
    assert limits.currency == "USD"
    assert limits.limits[0]["remaining"] == 4200


def test_cardholder_crud(api: respx.MockRouter, client: Airwallex):
    cardholders = IssuingCardholders(client._api)
    create_route = api.post("/api/v1/issuing/cardholders/create").respond(
        202, json={"cardholder_id": "chd_1", "email": "jane@example.com", "status": "PENDING"}
    )
    created = cardholders.create(
        email="jane@example.com",
        individual={"name": {"first_name": "Jane", "last_name": "Doe"}},
    )
    assert created.cardholder_id == "chd_1"
    # The cardholders/create endpoint takes no request_id — none should be injected.
    assert "request_id" not in json.loads(create_route.calls[0].request.content)

    api.get("/api/v1/issuing/cardholders/chd_1").respond(
        200, json={"cardholder_id": "chd_1", "status": "READY"}
    )
    fetched = cardholders.retrieve("chd_1")
    assert fetched.status == "READY"

    list_route = api.get("/api/v1/issuing/cardholders").respond(
        200, json={"has_more": False, "items": [{"cardholder_id": "chd_1"}]}
    )
    page = cardholders.list(cardholder_status="READY")
    assert page.items[0].cardholder_id == "chd_1"
    assert list_route.calls[0].request.url.params["cardholder_status"] == "READY"

    update_route = api.post("/api/v1/issuing/cardholders/chd_1/update").respond(
        202, json={"cardholder_id": "chd_1", "mobile_number": "+6591234567"}
    )
    updated = cardholders.update("chd_1", mobile_number="+6591234567")
    assert updated.mobile_number == "+6591234567"
    assert json.loads(update_route.calls[0].request.content) == {"mobile_number": "+6591234567"}

    api.post("/api/v1/issuing/cardholders/chd_1/delete").respond(
        200, json={"cardholder_id": "chd_1", "deleted": True}
    )
    deleted = cardholders.delete("chd_1")
    assert deleted.cardholder_id == "chd_1"
    assert deleted.deleted is True  # unknown fields are preserved


def test_transactions_list_and_retrieve(api: respx.MockRouter, client: Airwallex):
    transactions = IssuingTransactions(client._api)
    list_route = api.get("/api/v1/issuing/transactions").respond(
        200,
        json={
            "has_more": False,
            "items": [{"transaction_id": "txn_1", "billing_amount": -12.5}],
        },
    )
    page = transactions.list(card_id="crd_1", transaction_type="CLEARING")
    assert page.items[0].billing_amount == -12.5
    params = list_route.calls[0].request.url.params
    assert params["card_id"] == "crd_1"
    assert params["transaction_type"] == "CLEARING"

    api.get("/api/v1/issuing/transactions/txn_1").respond(
        200,
        json={
            "transaction_id": "txn_1",
            "status": "CLEARED",
            "merchant": {"name": "Coffee Shop", "country": "SG"},
        },
    )
    transaction = transactions.retrieve("txn_1")
    assert transaction.status == "CLEARED"
    assert transaction.merchant["name"] == "Coffee Shop"


def test_authorizations_list_and_retrieve(api: respx.MockRouter, client: Airwallex):
    authorizations = IssuingAuthorizations(client._api)
    list_route = api.get("/api/v1/issuing/authorizations").respond(
        200,
        json={"has_more": False, "items": [{"transaction_id": "auth_1", "status": "PENDING"}]},
    )
    page = authorizations.list(status="PENDING", card_id="crd_1")
    assert page.items[0].transaction_id == "auth_1"
    assert list_route.calls[0].request.url.params["status"] == "PENDING"

    api.get("/api/v1/issuing/authorizations/auth_1").respond(
        200, json={"transaction_id": "auth_1", "billing_amount": 20.0, "auth_code": "123456"}
    )
    authorization = authorizations.retrieve("auth_1")
    assert authorization.billing_amount == 20.0
    assert authorization.auth_code == "123456"


def test_card_retrieve_404_maps_to_not_found(api: respx.MockRouter, client: Airwallex):
    api.get("/api/v1/issuing/cards/crd_missing").respond(
        404, json={"code": "not_found", "message": "Card not found"}
    )
    with pytest.raises(NotFoundError) as exc_info:
        IssuingCards(client._api).retrieve("crd_missing")
    assert exc_info.value.status_code == 404
    assert exc_info.value.code == "not_found"


async def test_async_card_create_and_retrieve(api: respx.MockRouter, async_client):
    cards = AsyncIssuingCards(async_client._api)
    route = api.post("/api/v1/issuing/cards/create").respond(
        202, json={"card_id": "crd_1", "card_status": "PENDING"}
    )
    card = await cards.create(cardholder_id="chd_1", form_factor="VIRTUAL")
    assert card.card_id == "crd_1"
    assert "request_id" in json.loads(route.calls[0].request.content)

    api.get("/api/v1/issuing/cards/crd_1").respond(
        200, json={"card_id": "crd_1", "card_status": "ACTIVE"}
    )
    fetched = await cards.retrieve("crd_1")
    assert fetched.card_status == "ACTIVE"
