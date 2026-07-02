from __future__ import annotations

import json
import uuid

import respx

from airwallex import Airwallex


def test_transfer_create_auto_generates_request_id(api: respx.MockRouter, client: Airwallex):
    route = api.post("/api/v1/transfers/create").respond(
        201, json={"id": "tra_1", "status": "NEW", "request_id": "ignored"}
    )
    transfer = client.transfers.create(
        beneficiary_id="ben_1",
        source_currency="USD",
        transfer_currency="PHP",
        transfer_amount=100,
    )
    assert transfer.id == "tra_1"
    body = json.loads(route.calls[0].request.content)
    uuid.UUID(body["request_id"])  # valid auto-generated uuid
    assert body["transfer_amount"] == 100


def test_transfer_create_respects_explicit_request_id(api: respx.MockRouter, client: Airwallex):
    route = api.post("/api/v1/transfers/create").respond(201, json={"id": "tra_1"})
    client.transfers.create(request_id="my-id-1", beneficiary_id="ben_1")
    body = json.loads(route.calls[0].request.content)
    assert body["request_id"] == "my-id-1"


def test_transfer_retrieve_and_list(api: respx.MockRouter, client: Airwallex):
    api.get("/api/v1/transfers/tra_1").respond(
        200, json={"id": "tra_1", "status": "PAID", "transfer_currency": "PHP"}
    )
    transfer = client.transfers.retrieve("tra_1")
    assert transfer.status == "PAID"

    list_route = api.get("/api/v1/transfers").respond(
        200, json={"has_more": False, "items": [{"id": "tra_1"}]}
    )
    page = client.transfers.list(status="PAID", currency="PHP")
    assert page.items[0].id == "tra_1"
    params = list_route.calls[0].request.url.params
    assert params["status"] == "PAID"
    assert params["currency"] == "PHP"


def test_models_preserve_unknown_fields(api: respx.MockRouter, client: Airwallex):
    api.get("/api/v1/transfers/tra_1").respond(
        200, json={"id": "tra_1", "brand_new_field": {"nested": True}}
    )
    transfer = client.transfers.retrieve("tra_1")
    assert transfer.brand_new_field == {"nested": True}
    assert transfer.to_dict()["brand_new_field"] == {"nested": True}


def test_beneficiary_crud(api: respx.MockRouter, client: Airwallex):
    api.post("/api/v1/beneficiaries/create").respond(
        201, json={"beneficiary_id": "ben_1", "nickname": "Supplier"}
    )
    created = client.beneficiaries.create(
        nickname="Supplier", beneficiary={"entity_type": "COMPANY"}
    )
    assert created.beneficiary_id == "ben_1"

    api.get("/api/v1/beneficiaries/ben_1").respond(
        200,
        json={
            "beneficiary_id": "ben_1",
            "beneficiary": {"bank_details": {"account_number": "123", "bank_name": "BDO"}},
        },
    )
    fetched = client.beneficiaries.retrieve("ben_1")
    assert fetched.beneficiary.bank_details.bank_name == "BDO"

    update_route = api.post("/api/v1/beneficiaries/update/ben_1").respond(
        200, json={"beneficiary_id": "ben_1", "nickname": "Renamed"}
    )
    updated = client.beneficiaries.update("ben_1", nickname="Renamed")
    assert updated.nickname == "Renamed"
    assert json.loads(update_route.calls[0].request.content) == {"nickname": "Renamed"}

    delete_route = api.post("/api/v1/beneficiaries/delete/ben_1").respond(200)
    client.beneficiaries.delete("ben_1")
    assert delete_route.called


def test_conversion_create_and_rates_quote(api: respx.MockRouter, client: Airwallex):
    route = api.post("/api/v1/conversions/create").respond(
        201, json={"conversion_id": "con_1", "status": "SETTLED", "client_rate": 1.35}
    )
    conversion = client.conversions.create(
        buy_currency="USD", sell_currency="SGD", buy_amount=100, term_agreement=True
    )
    assert conversion.conversion_id == "con_1"
    assert "request_id" in json.loads(route.calls[0].request.content)

    quote_route = api.get("/api/v1/rates/quote").respond(
        200, json={"currency_pair": "USDSGD", "client_rate": 1.351}
    )
    quote = client.rates.quote(buy_currency="USD", sell_currency="SGD", buy_amount=100)
    assert quote.client_rate == 1.351
    assert quote_route.calls[0].request.url.params["buy_amount"] == "100"


def test_global_accounts(api: respx.MockRouter, client: Airwallex):
    api.get("/api/v1/global_accounts/ga_1").respond(
        200, json={"id": "ga_1", "currency": "USD", "account_number": "9001"}
    )
    account = client.global_accounts.retrieve("ga_1")
    assert account.account_number == "9001"

    api.get("/api/v1/global_accounts/ga_1/transactions").respond(
        200, json={"has_more": False, "items": [{"amount": 10.5, "currency": "USD"}]}
    )
    transactions = client.global_accounts.transactions("ga_1")
    assert transactions.items[0].amount == 10.5

    close_route = api.post("/api/v1/global_accounts/ga_1/close").respond(
        200, json={"id": "ga_1", "status": "CLOSED"}
    )
    closed = client.global_accounts.close("ga_1")
    assert closed.status == "CLOSED"
    assert close_route.called


def test_deposits_and_reference(api: respx.MockRouter, client: Airwallex):
    api.get("/api/v1/deposits").respond(
        200, json={"has_more": False, "items": [{"id": "dep_1", "amount": 55.0}]}
    )
    deposits = client.deposits.list()
    assert deposits.items[0].amount == 55.0

    api.get("/api/v1/reference/supported_currencies").respond(
        200, json={"items": [{"currency": "PHP"}]}
    )
    currencies = client.reference.supported_currencies()
    assert currencies["items"][0]["currency"] == "PHP"


def test_webhook_endpoints(api: respx.MockRouter, client: Airwallex):
    create_route = api.post("/api/v1/webhooks/create").respond(
        201, json={"id": "wh_1", "url": "https://example.com/hook", "secret": "whsec_x"}
    )
    endpoint = client.webhook_endpoints.create(
        url="https://example.com/hook", events=["transfer.settled"]
    )
    assert endpoint.secret == "whsec_x"
    body = json.loads(create_route.calls[0].request.content)
    assert body["events"] == ["transfer.settled"]
    assert "request_id" in body

    api.get("/api/v1/webhooks").respond(200, json={"has_more": False, "items": [{"id": "wh_1"}]})
    page = client.webhook_endpoints.list()
    assert page.items[0].id == "wh_1"

    delete_route = api.post("/api/v1/webhooks/wh_1/delete").respond(200)
    client.webhook_endpoints.delete("wh_1")
    assert delete_route.called


def test_balances_history_paged(api: respx.MockRouter, client: Airwallex):
    route = api.get("/api/v1/balances/history").respond(
        200,
        json={"has_more": False, "items": [{"currency": "USD", "amount": -20.0}]},
    )
    history = client.balances.history(currency="USD")
    assert history.items[0].amount == -20.0
    assert route.calls[0].request.url.params["currency"] == "USD"
