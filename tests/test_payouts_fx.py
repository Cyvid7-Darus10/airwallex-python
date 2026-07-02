from __future__ import annotations

import json
import uuid

import respx

from airwallex import Airwallex
from airwallex.resources.batch_transfers import BatchTransfers
from airwallex.resources.conversion_amendments import ConversionAmendments
from airwallex.resources.fx_quotes import AsyncQuotes, Quotes
from airwallex.resources.payers import Payers
from airwallex.resources.wallet_transfers import WalletTransfers

_BATCH = {"id": "bat_1", "status": "CREATED", "name": "July run", "total_item_count": 0}


def test_batch_transfer_lifecycle(api: respx.MockRouter, client: Airwallex):
    batch_transfers = BatchTransfers(client._api)

    create_route = api.post("/api/v1/batch_transfers/create").respond(200, json=_BATCH)
    batch = batch_transfers.create(name="July run", transfer_date="2026-07-15")
    assert batch.id == "bat_1"
    body = json.loads(create_route.calls[0].request.content)
    uuid.UUID(body["request_id"])  # valid auto-generated uuid
    assert body["name"] == "July run"

    add_route = api.post("/api/v1/batch_transfers/bat_1/add_items").respond(
        200, json={**_BATCH, "total_item_count": 2, "valid_item_count": 2}
    )
    items = [{"beneficiary_id": "ben_1", "transfer_amount": 10, "transfer_currency": "PHP"}] * 2
    batch = batch_transfers.add_items("bat_1", items=items)
    assert batch.total_item_count == 2
    assert json.loads(add_route.calls[0].request.content) == {"items": items}

    quote_route = api.post("/api/v1/batch_transfers/bat_1/quote").respond(
        200,
        json={
            **_BATCH,
            "status": "QUOTED",
            "quote_summary": {"validity": "1_HOUR", "quotes": [{"currency_pair": "USDPHP"}]},
        },
    )
    quoted = batch_transfers.quote("bat_1", validity="1_HOUR")
    assert quoted.quote_summary.quotes[0].currency_pair == "USDPHP"
    assert json.loads(quote_route.calls[0].request.content) == {"validity": "1_HOUR"}

    submit_route = api.post("/api/v1/batch_transfers/bat_1/submit").respond(
        200, json={**_BATCH, "status": "SUBMITTED"}
    )
    submitted = batch_transfers.submit("bat_1")
    assert submitted.status == "SUBMITTED"
    assert submit_route.called


def test_batch_transfer_items_delete_and_list(api: respx.MockRouter, client: Airwallex):
    batch_transfers = BatchTransfers(client._api)

    items_route = api.get("/api/v1/batch_transfers/bat_1/items").respond(
        200, json={"has_more": False, "items": [{"id": "bti_1", "status": "VALID"}]}
    )
    items = batch_transfers.items("bat_1", page_size=50)
    assert items.items[0].id == "bti_1"
    assert items_route.calls[0].request.url.params["page_size"] == "50"

    delete_items_route = api.post("/api/v1/batch_transfers/bat_1/delete_items").respond(
        200, json={**_BATCH, "total_item_count": 0}
    )
    batch_transfers.delete_items("bat_1", item_ids=["bti_1"])
    assert json.loads(delete_items_route.calls[0].request.content) == {"item_ids": ["bti_1"]}

    list_route = api.get("/api/v1/batch_transfers").respond(
        200, json={"has_more": False, "items": [_BATCH]}
    )
    page = batch_transfers.list(status="CREATED")
    assert page.items[0].id == "bat_1"
    assert list_route.calls[0].request.url.params["status"] == "CREATED"

    retrieve_route = api.get("/api/v1/batch_transfers/bat_1").respond(200, json=_BATCH)
    assert batch_transfers.retrieve("bat_1").name == "July run"
    assert retrieve_route.called

    delete_route = api.post("/api/v1/batch_transfers/bat_1/delete").respond(
        200, json={**_BATCH, "status": "DELETED"}
    )
    assert batch_transfers.delete("bat_1").status == "DELETED"
    assert delete_route.called


def test_wallet_transfer_create_with_request_id(api: respx.MockRouter, client: Airwallex):
    wallet_transfers = WalletTransfers(client._api)

    create_route = api.post("/api/v1/wallet_transfers/create").respond(
        200, json={"wallet_transfer_id": "wtr_1", "status": "SETTLED", "transfer_amount": 100}
    )
    transfer = wallet_transfers.create(
        beneficiary={"account_number": "1234567"},
        transfer_amount=100,
        transfer_currency="USD",
        reference="Invoice 42",
        reason="business_expenses",
    )
    assert transfer.wallet_transfer_id == "wtr_1"
    body = json.loads(create_route.calls[0].request.content)
    uuid.UUID(body["request_id"])  # valid auto-generated uuid
    assert body["transfer_currency"] == "USD"

    api.get("/api/v1/wallet_transfers/wtr_1").respond(
        200, json={"wallet_transfer_id": "wtr_1", "beneficiary": {"account_name": "Acme"}}
    )
    fetched = wallet_transfers.retrieve("wtr_1")
    assert fetched.beneficiary.account_name == "Acme"

    list_route = api.get("/api/v1/wallet_transfers").respond(
        200, json={"has_more": False, "items": [{"wallet_transfer_id": "wtr_1"}]}
    )
    page = wallet_transfers.list(status="SETTLED", transfer_currency="USD")
    assert page.items[0].wallet_transfer_id == "wtr_1"
    assert list_route.calls[0].request.url.params["transfer_currency"] == "USD"


def test_payer_crud(api: respx.MockRouter, client: Airwallex):
    payers = Payers(client._api)

    create_route = api.post("/api/v1/payers/create").respond(
        201, json={"payer_id": "pay_1", "nickname": "Acme"}
    )
    created = payers.create(nickname="Acme", payer={"entity_type": "COMPANY"})
    assert created.payer_id == "pay_1"
    assert json.loads(create_route.calls[0].request.content) == {
        "nickname": "Acme",
        "payer": {"entity_type": "COMPANY"},
    }

    api.get("/api/v1/payers/pay_1").respond(
        200, json={"payer_id": "pay_1", "payer": {"company_name": "Acme Pte Ltd"}}
    )
    fetched = payers.retrieve("pay_1")
    assert fetched.payer.company_name == "Acme Pte Ltd"

    update_route = api.post("/api/v1/payers/update/pay_1").respond(
        200, json={"payer_id": "pay_1", "nickname": "Renamed"}
    )
    updated = payers.update("pay_1", nickname="Renamed")
    assert updated.nickname == "Renamed"
    assert json.loads(update_route.calls[0].request.content) == {"nickname": "Renamed"}

    validate_route = api.post("/api/v1/payers/validate").respond(200, json={})
    payers.validate(payer={"entity_type": "COMPANY"})
    assert validate_route.called

    delete_route = api.post("/api/v1/payers/delete/pay_1").respond(200)
    payers.delete("pay_1")
    assert delete_route.called


def test_fx_quote_create_and_retrieve(api: respx.MockRouter, client: Airwallex):
    quotes = Quotes(client._api)

    create_route = api.post("/api/v1/fx/quotes/create").respond(
        201,
        json={
            "id": "quo_1",
            "currency_pair": "USDSGD",
            "client_rate": 1.351,
            "validity": "1_HOUR",
        },
    )
    quote = quotes.create(
        buy_currency="USD", sell_currency="SGD", buy_amount=1000, validity="1_HOUR"
    )
    assert quote.id == "quo_1"
    assert quote.client_rate == 1.351
    body = json.loads(create_route.calls[0].request.content)
    uuid.UUID(body["request_id"])  # valid auto-generated uuid
    assert body["validity"] == "1_HOUR"

    api.get("/api/v1/fx/quotes/quo_1").respond(
        200, json={"id": "quo_1", "expires_at": "2026-07-02T10:00:00+0000"}
    )
    fetched = quotes.retrieve("quo_1")
    assert fetched.expires_at == "2026-07-02T10:00:00+0000"


def test_conversion_amendment_create_and_quote(api: respx.MockRouter, client: Airwallex):
    conversion_amendments = ConversionAmendments(client._api)

    quote_route = api.post("/api/v1/conversion_amendments/quote").respond(
        200,
        json={
            "conversion_id": "con_1",
            "type": "CANCELLATION",
            "charges": [{"amount": 5.0, "currency": "USD", "type": "LOSS"}],
        },
    )
    quote = conversion_amendments.quote(conversion_id="con_1", type="CANCELLATION")
    assert quote.charges[0].amount == 5.0
    quote_body = json.loads(quote_route.calls[0].request.content)
    uuid.UUID(quote_body["request_id"])  # valid auto-generated uuid

    create_route = api.post("/api/v1/conversion_amendments/create").respond(
        201, json={"amendment_id": "ame_1", "conversion_id": "con_1", "type": "CANCELLATION"}
    )
    amendment = conversion_amendments.create(conversion_id="con_1", type="CANCELLATION")
    assert amendment.amendment_id == "ame_1"
    assert "request_id" in json.loads(create_route.calls[0].request.content)

    api.get("/api/v1/conversion_amendments/ame_1").respond(
        200, json={"amendment_id": "ame_1", "type": "CANCELLATION"}
    )
    assert conversion_amendments.retrieve("ame_1").type == "CANCELLATION"

    list_route = api.get("/api/v1/conversion_amendments").respond(
        200, json={"has_more": False, "items": [{"amendment_id": "ame_1"}]}
    )
    page = conversion_amendments.list(conversion_id="con_1")
    assert page.items[0].amendment_id == "ame_1"
    assert list_route.calls[0].request.url.params["conversion_id"] == "con_1"


def test_transfer_confirm_funding(api: respx.MockRouter, client: Airwallex):
    route = api.post("/api/v1/transfers/tra_1/confirm_funding").respond(
        200, json={"id": "tra_1", "status": "PROCESSING"}
    )
    confirmed = client.transfers.confirm_funding("tra_1", funding_source_id="fs_1")
    assert confirmed.status == "PROCESSING"
    assert json.loads(route.calls[0].request.content) == {"funding_source_id": "fs_1"}


def test_batch_transfer_path_ids_are_url_escaped(api: respx.MockRouter, client: Airwallex):
    # A traversal-style id must stay inside the batch_transfers endpoint, encoded.
    route = api.get("/api/v1/batch_transfers/..%2Fcreate").respond(200, json={"id": "x"})
    BatchTransfers(client._api).retrieve("../create")
    assert route.called
    # raw_path is what goes on the wire; .path would show the decoded form
    assert route.calls[0].request.url.raw_path.endswith(b"/api/v1/batch_transfers/..%2Fcreate")


async def test_async_fx_quote_create(api: respx.MockRouter, async_client):
    quotes = AsyncQuotes(async_client._api)

    route = api.post("/api/v1/fx/quotes/create").respond(
        201, json={"id": "quo_1", "currency_pair": "USDSGD"}
    )
    quote = await quotes.create(buy_currency="USD", sell_currency="SGD", buy_amount=1000)
    assert quote.id == "quo_1"
    assert "request_id" in json.loads(route.calls[0].request.content)
