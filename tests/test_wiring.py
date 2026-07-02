from __future__ import annotations

from airwallex import Airwallex, AsyncAirwallex

EXPECTED_RESOURCES = [
    "accounts",
    "balances",
    "batch_transfers",
    "beneficiaries",
    "conversion_amendments",
    "conversions",
    "customers",
    "deposits",
    "financial_transactions",
    "fx_quotes",
    "global_accounts",
    "issuing_authorizations",
    "issuing_cardholders",
    "issuing_cards",
    "issuing_transactions",
    "payers",
    "payment_intents",
    "rates",
    "reference",
    "refunds",
    "settlements",
    "simulation",
    "transfers",
    "wallet_transfers",
    "webhook_endpoints",
]


def test_sync_client_exposes_every_resource():
    with Airwallex(client_id="c", api_key="k", environment="demo") as client:
        for name in EXPECTED_RESOURCES:
            resource = getattr(client, name)
            assert resource._client is client._api, name


async def test_async_client_exposes_every_resource():
    async with AsyncAirwallex(client_id="c", api_key="k", environment="demo") as client:
        for name in EXPECTED_RESOURCES:
            resource = getattr(client, name)
            assert resource._client is client._api, name
            assert type(resource).__name__.startswith("Async"), name
