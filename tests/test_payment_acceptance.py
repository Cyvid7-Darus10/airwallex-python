from __future__ import annotations

import json
import uuid

import pytest
import respx

from airwallex import Airwallex, NotFoundError
from airwallex.resources.payment_acceptance import (
    AsyncPaymentIntents,
    Customers,
    PaymentIntents,
    Refunds,
)


def test_payment_intent_create_auto_generates_request_id(api: respx.MockRouter, client: Airwallex):
    route = api.post("/api/v1/pa/payment_intents/create").respond(
        201, json={"id": "int_1", "status": "REQUIRES_PAYMENT_METHOD", "amount": 25.0}
    )
    intents = PaymentIntents(client._api)
    intent = intents.create(amount=25.0, currency="USD", merchant_order_id="order_42")
    assert intent.id == "int_1"
    assert intent.status == "REQUIRES_PAYMENT_METHOD"
    body = json.loads(route.calls[0].request.content)
    uuid.UUID(body["request_id"])  # valid auto-generated uuid
    assert body["merchant_order_id"] == "order_42"


def test_payment_intent_create_respects_explicit_request_id(
    api: respx.MockRouter, client: Airwallex
):
    route = api.post("/api/v1/pa/payment_intents/create").respond(201, json={"id": "int_1"})
    PaymentIntents(client._api).create(request_id="my-id-1", amount=10.0, currency="USD")
    body = json.loads(route.calls[0].request.content)
    assert body["request_id"] == "my-id-1"


def test_payment_intent_retrieve_and_list(api: respx.MockRouter, client: Airwallex):
    api.get("/api/v1/pa/payment_intents/int_1").respond(
        200, json={"id": "int_1", "status": "SUCCEEDED", "currency": "USD", "amount": 25.0}
    )
    intents = PaymentIntents(client._api)
    intent = intents.retrieve("int_1")
    assert intent.status == "SUCCEEDED"
    assert intent.amount == 25.0

    list_route = api.get("/api/v1/pa/payment_intents").respond(
        200, json={"has_more": False, "items": [{"id": "int_1"}]}
    )
    page = intents.list(status="SUCCEEDED", currency="USD", page_num=2, page_size=5)
    assert page.items[0].id == "int_1"
    params = list_route.calls[0].request.url.params
    assert params["status"] == "SUCCEEDED"
    assert params["currency"] == "USD"
    assert params["page_num"] == "2"
    assert params["page_size"] == "5"


def test_payment_intent_capture(api: respx.MockRouter, client: Airwallex):
    route = api.post("/api/v1/pa/payment_intents/int_1/capture").respond(
        200, json={"id": "int_1", "status": "SUCCEEDED", "captured_amount": 25.0}
    )
    captured = PaymentIntents(client._api).capture("int_1", amount=25.0)
    assert captured.captured_amount == 25.0
    body = json.loads(route.calls[0].request.content)
    assert body["amount"] == 25.0
    uuid.UUID(body["request_id"])  # spec: request_id required on intent actions


def test_customer_crud_and_client_secret(api: respx.MockRouter, client: Airwallex):
    create_route = api.post("/api/v1/pa/customers/create").respond(
        201, json={"id": "cus_1", "merchant_customer_id": "cust_42"}
    )
    customers = Customers(client._api)
    created = customers.create(merchant_customer_id="cust_42", email="jo@example.com")
    assert created.id == "cus_1"
    body = json.loads(create_route.calls[0].request.content)
    assert "request_id" in body
    assert body["email"] == "jo@example.com"

    api.get("/api/v1/pa/customers/cus_1").respond(
        200, json={"id": "cus_1", "first_name": "Jo", "merchant_customer_id": "cust_42"}
    )
    fetched = customers.retrieve("cus_1")
    assert fetched.first_name == "Jo"

    update_route = api.post("/api/v1/pa/customers/cus_1/update").respond(
        200, json={"id": "cus_1", "first_name": "Joan"}
    )
    updated = customers.update("cus_1", first_name="Joan")
    assert updated.first_name == "Joan"
    update_body = json.loads(update_route.calls[0].request.content)
    assert update_body["first_name"] == "Joan"
    uuid.UUID(update_body["request_id"])  # spec: request_id required on customer update

    api.get("/api/v1/pa/customers/cus_1/generate_client_secret").respond(
        200, json={"client_secret": "cs_x", "expired_time": "2099-01-01T00:00:00+0000"}
    )
    secret = customers.generate_client_secret("cus_1")
    assert secret.client_secret == "cs_x"

    list_route = api.get("/api/v1/pa/customers").respond(
        200, json={"has_more": False, "items": [{"id": "cus_1"}]}
    )
    page = customers.list(merchant_customer_id="cust_42")
    assert page.items[0].id == "cus_1"
    assert list_route.calls[0].request.url.params["merchant_customer_id"] == "cust_42"


def test_refund_create_retrieve_and_list(api: respx.MockRouter, client: Airwallex):
    create_route = api.post("/api/v1/pa/refunds/create").respond(
        201, json={"id": "rfd_1", "status": "RECEIVED", "payment_intent_id": "int_1"}
    )
    refunds = Refunds(client._api)
    refund = refunds.create(payment_intent_id="int_1", amount=10.0)
    assert refund.id == "rfd_1"
    assert "request_id" in json.loads(create_route.calls[0].request.content)

    api.get("/api/v1/pa/refunds/rfd_1").respond(
        200, json={"id": "rfd_1", "status": "SUCCEEDED", "amount": 10.0}
    )
    fetched = refunds.retrieve("rfd_1")
    assert fetched.status == "SUCCEEDED"

    list_route = api.get("/api/v1/pa/refunds").respond(
        200, json={"has_more": False, "items": [{"id": "rfd_1"}]}
    )
    page = refunds.list(payment_intent_id="int_1", status="SUCCEEDED")
    assert page.items[0].id == "rfd_1"
    params = list_route.calls[0].request.url.params
    assert params["payment_intent_id"] == "int_1"
    assert params["status"] == "SUCCEEDED"


def test_payment_intent_not_found_maps_to_error(api: respx.MockRouter, client: Airwallex):
    api.get("/api/v1/pa/payment_intents/missing").respond(
        404, json={"code": "not_found", "message": "The requested resource was not found"}
    )
    with pytest.raises(NotFoundError):
        PaymentIntents(client._api).retrieve("missing")


def test_payment_acceptance_path_ids_are_url_escaped(api: respx.MockRouter, client: Airwallex):
    # A traversal-style id must stay inside the payment_intents endpoint, encoded.
    route = api.get("/api/v1/pa/payment_intents/..%2Fcreate").respond(200, json={"id": "x"})
    PaymentIntents(client._api).retrieve("../create")
    assert route.called
    assert route.calls[0].request.url.raw_path.endswith(b"/api/v1/pa/payment_intents/..%2Fcreate")


async def test_async_payment_intent_confirm(api: respx.MockRouter, async_client):
    route = api.post("/api/v1/pa/payment_intents/int_1/confirm").respond(
        200, json={"id": "int_1", "status": "SUCCEEDED"}
    )
    confirmed = await AsyncPaymentIntents(async_client._api).confirm(
        "int_1", payment_method={"type": "card"}
    )
    assert confirmed.status == "SUCCEEDED"
    body = json.loads(route.calls[0].request.content)
    assert body["payment_method"] == {"type": "card"}


def test_intent_actions_auto_generate_request_id(api: respx.MockRouter, client: Airwallex):
    intents = PaymentIntents(client._api)
    route = api.post("/api/v1/pa/payment_intents/int_1/cancel").respond(200, json={"id": "int_1"})
    intents.cancel("int_1", cancellation_reason="requested_by_customer")
    body = json.loads(route.calls[0].request.content)
    uuid.UUID(body["request_id"])  # spec: request_id is required on intent actions
    assert body["cancellation_reason"] == "requested_by_customer"


def test_customer_update_auto_generates_request_id(api: respx.MockRouter, client: Airwallex):
    customers = Customers(client._api)
    route = api.post("/api/v1/pa/customers/cus_1/update").respond(200, json={"id": "cus_1"})
    customers.update("cus_1", last_name="Byron")
    body = json.loads(route.calls[0].request.content)
    uuid.UUID(body["request_id"])  # spec: request_id is required on customer update
