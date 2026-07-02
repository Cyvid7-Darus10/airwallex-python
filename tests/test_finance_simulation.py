from __future__ import annotations

import json

import respx

from airwallex import Airwallex, AsyncAirwallex
from airwallex.resources.accounts import Accounts
from airwallex.resources.finance import (
    AsyncFinancialTransactions,
    FinancialTransactions,
    Settlements,
)
from airwallex.resources.simulation import Simulation


def test_account_retrieve(api: respx.MockRouter, client: Airwallex):
    api.get("/api/v1/account").respond(
        200,
        json={
            "id": "acct_1",
            "nickname": "Main",
            "status": "ACTIVE",
            "account_details": {"legal_entity_type": "COMPANY"},
        },
    )
    account = Accounts(client._api).retrieve()
    assert account.id == "acct_1"
    assert account.status == "ACTIVE"
    assert account.account_details == {"legal_entity_type": "COMPANY"}


def test_financial_transactions_list_with_filters(api: respx.MockRouter, client: Airwallex):
    route = api.get("/api/v1/pa/financial/transactions").respond(
        200,
        json={
            "has_more": False,
            "items": [{"id": "ftx_1", "amount": 25.5, "status": "SETTLED"}],
        },
    )
    page = FinancialTransactions(client._api).list(
        currency="USD", status="SETTLED", batch_id="batch_9"
    )
    assert page.items[0].id == "ftx_1"
    assert page.items[0].amount == 25.5
    params = route.calls[0].request.url.params
    assert params["currency"] == "USD"
    assert params["status"] == "SETTLED"
    assert params["batch_id"] == "batch_9"
    assert params["page_num"] == "0"


def test_financial_transaction_retrieve(api: respx.MockRouter, client: Airwallex):
    api.get("/api/v1/pa/financial/transactions/ftx_1").respond(
        200, json={"id": "ftx_1", "source_type": "PAYOUT", "net": 99.0}
    )
    transaction = FinancialTransactions(client._api).retrieve("ftx_1")
    assert transaction.source_type == "PAYOUT"
    assert transaction.net == 99.0


def test_settlements_list_and_retrieve(api: respx.MockRouter, client: Airwallex):
    list_route = api.get("/api/v1/pa/financial/settlements").respond(
        200, json={"has_more": False, "items": [{"id": "stl_1", "currency": "USD"}]}
    )
    page = Settlements(client._api).list(
        currency="USD", status="SETTLED", from_settled_at="2026-01-01", to_settled_at="2026-02-01"
    )
    assert page.items[0].id == "stl_1"
    params = list_route.calls[0].request.url.params
    assert params["from_settled_at"] == "2026-01-01"
    assert params["status"] == "SETTLED"

    api.get("/api/v1/pa/financial/settlements/stl_1").respond(
        200, json={"id": "stl_1", "amount": 500.0, "status": "SETTLED"}
    )
    settlement = Settlements(client._api).retrieve("stl_1")
    assert settlement.amount == 500.0


def test_simulation_deposit_lifecycle(api: respx.MockRouter, client: Airwallex):
    create_route = api.post("/api/v1/simulation/deposit/create").respond(
        201, json={"id": "dep_1", "status": "PENDING"}
    )
    simulation = Simulation(client._api)
    created = simulation.create_deposit(global_account_id="ga_1", amount=100, currency="USD")
    assert created == {"id": "dep_1", "status": "PENDING"}
    body = json.loads(create_route.calls[0].request.content)
    assert body["global_account_id"] == "ga_1"
    assert body["amount"] == 100

    settle_route = api.post("/api/v1/simulation/deposits/dep_1/settle").respond(
        200, json={"id": "dep_1", "status": "SETTLED"}
    )
    settled = simulation.settle_deposit("dep_1")
    assert settled["status"] == "SETTLED"
    assert settle_route.called


def test_simulation_transfer_transition(api: respx.MockRouter, client: Airwallex):
    route = api.post("/api/v1/simulation/transfers/tra_1/transition").respond(
        200, json={"id": "tra_1", "status": "PAID"}
    )
    result = Simulation(client._api).transition_transfer("tra_1", next_status="PAID")
    assert result["status"] == "PAID"
    assert json.loads(route.calls[0].request.content) == {"next_status": "PAID"}


def test_simulation_path_ids_are_url_escaped(api: respx.MockRouter, client: Airwallex):
    # A traversal-style id must stay inside the deposits endpoint, encoded.
    route = api.post("/api/v1/simulation/deposits/..%2Fcreate/settle").respond(200, json={})
    Simulation(client._api).settle_deposit("../create")
    assert route.called
    assert b"/api/v1/simulation/deposits/..%2Fcreate/settle" in (
        route.calls[0].request.url.raw_path
    )


async def test_async_financial_transactions_list(
    api: respx.MockRouter, async_client: AsyncAirwallex
):
    route = api.get("/api/v1/pa/financial/transactions").respond(
        200, json={"has_more": False, "items": [{"id": "ftx_2", "fee": 1.25}]}
    )
    page = await AsyncFinancialTransactions(async_client._api).list(status="PENDING")
    assert page.items[0].fee == 1.25
    assert route.calls[0].request.url.params["status"] == "PENDING"
