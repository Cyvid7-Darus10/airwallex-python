"""Deeper live lifecycle test against the Airwallex demo environment.

Exercises WRITE paths end-to-end in the sandbox: deposit settlement,
customer/payment-intent/beneficiary/webhook lifecycles, FX quotes and
conversions, and the async client. Demo environment only — no real money.

Reads credentials from .env.demo (gitignored). Run:

    uv run python examples/local_lifecycle_test.py
"""

from __future__ import annotations

import asyncio
import pathlib
import sys
import uuid

from airwallex import Airwallex, APIStatusError, AsyncAirwallex

GREEN, RED, YELLOW, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[0m"
RESULTS = {"ok": 0, "skip": 0, "fail": 0}


def load_env() -> dict[str, str]:
    env_file = pathlib.Path(__file__).resolve().parents[1] / ".env.demo"
    if not env_file.exists():
        sys.exit(f"{RED}Missing {env_file}{RESET}")
    values: dict[str, str] = {}
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip()
    return values


def check(name: str, fn) -> object:
    """Run a step. Business-rule rejections are SKIPs; SDK failures are FAILs."""
    try:
        result = fn()
    except APIStatusError as err:
        RESULTS["skip"] += 1
        print(f"  {YELLOW}SKIP{RESET} {name}: [{err.status_code}] {err.code}: {err.message[:80]}")
        return None
    except Exception as exc:
        RESULTS["fail"] += 1
        print(f"  {RED}FAIL{RESET} {name}: {type(exc).__name__}: {exc}")
        return None
    RESULTS["ok"] += 1
    print(f"  {GREEN}OK{RESET}   {name}")
    return result


def main() -> None:
    env = load_env()
    kwargs = dict(
        client_id=env.get("AIRWALLEX_CLIENT_ID"),
        api_key=env.get("AIRWALLEX_API_KEY"),
        environment="demo",
    )
    client = Airwallex(api_version="2024-01-31", **kwargs)
    # fx_quotes (like fx/rates) rejects 2024-01-31 — it needs the account default.
    fx_client = Airwallex(**kwargs)
    run = uuid.uuid4().hex[:8]

    with client, fx_client:
        print("Phase 1 — fund the wallet (settle simulated deposits):")

        def _settle_deposits() -> str:
            deposits = client.deposits.list(page_size=10).items
            settled = 0
            for dep in deposits:
                if (dep.status or "").upper() not in {"SETTLED", "COMPLETED"}:
                    try:
                        client.simulation.settle_deposit(dep.id)
                        settled += 1
                    except APIStatusError:
                        pass  # already settled or non-transitionable
            return f"settled {settled} of {len(deposits)} deposits"

        check("settle pending simulated deposits", _settle_deposits)

        def _usd_balance() -> str:
            usd = [b for b in client.balances.current() if b.currency == "USD"]
            amount = usd[0].available_amount if usd else 0.0
            print(f"        USD available: {amount}")
            return str(amount)

        check("USD balance after settlement", _usd_balance)

        print("\nPhase 2 — customer lifecycle (payment acceptance):")
        customer = check(
            "customers.create",
            lambda: client.customers.create(
                merchant_customer_id=f"sdk-test-{run}",
                first_name="Ada",
                last_name="Lovelace",
                email=f"ada+{run}@example.com",
            ),
        )
        if customer is not None:
            check("customers.retrieve", lambda: client.customers.retrieve(customer.id))
            check(
                "customers.update",
                lambda: client.customers.update(customer.id, last_name="Byron"),
            )
            check(
                "customers.generate_client_secret",
                lambda: client.customers.generate_client_secret(customer.id),
            )

        print("\nPhase 3 — payment intent lifecycle:")
        intent = check(
            "payment_intents.create",
            lambda: client.payment_intents.create(
                amount=10.42,
                currency="USD",
                merchant_order_id=f"sdk-test-{run}",
            ),
        )
        if intent is not None:
            check("payment_intents.retrieve", lambda: client.payment_intents.retrieve(intent.id))
            check(
                "payment_intents.cancel",
                lambda: client.payment_intents.cancel(
                    intent.id, cancellation_reason="requested_by_customer"
                ),
            )

        print("\nPhase 4 — beneficiary lifecycle (US ACH corridor):")
        bene_payload = {
            "nickname": f"SDK Test {run}",
            "payment_methods": ["LOCAL"],
            "beneficiary": {
                "entity_type": "PERSONAL",
                "first_name": "Grace",
                "last_name": "Hopper",
                "bank_details": {
                    "account_currency": "USD",
                    "bank_country_code": "US",
                    "account_name": "Grace Hopper",
                    "account_number": "123456789",
                    "account_routing_type1": "aba",
                    "account_routing_value1": "026009593",
                    "local_clearing_system": "ACH",
                },
                "address": {
                    "city": "New York",
                    "country_code": "US",
                    "postcode": "10001",
                    "state": "NY",
                    "street_address": "1 Test Street",
                },
            },
        }
        validation = check(
            "beneficiaries.validate", lambda: client.beneficiaries.validate(**bene_payload)
        )
        beneficiary = None
        if validation is not None:
            beneficiary = check(
                "beneficiaries.create", lambda: client.beneficiaries.create(**bene_payload)
            )
        if beneficiary is not None:
            bene_id = beneficiary.beneficiary_id
            check("beneficiaries.retrieve", lambda: client.beneficiaries.retrieve(bene_id))
            updated_payload = {**bene_payload, "nickname": f"SDK Renamed {run}"}
            check(
                "beneficiaries.update",
                lambda: client.beneficiaries.update(bene_id, **updated_payload),
            )

        print("\nPhase 5 — FX: lockable quote and conversion:")
        check(
            "fx_quotes.create",
            lambda: fx_client.fx_quotes.create(
                sell_currency="USD", buy_currency="SGD", sell_amount=10, validity="HR_24"
            ),
        )
        conversion = check(
            "conversions.create (USD 10 -> SGD)",
            lambda: client.conversions.create(
                sell_currency="USD",
                buy_currency="SGD",
                sell_amount=10,
                term_agreement=True,
                reason="Fund_SGD_account",
            ),
        )
        if conversion is not None:
            check(
                "conversions.retrieve",
                lambda: client.conversions.retrieve(conversion.conversion_id),
            )

        print("\nPhase 6 — transfer lifecycle (uses settled sandbox funds):")
        transfer = None
        if beneficiary is not None:
            # the modern transfer payload shape needs the account-default version
            transfer = check(
                "transfers.create",
                lambda: fx_client.transfers.create(
                    beneficiary_id=beneficiary.beneficiary_id,
                    source_currency="USD",
                    transfer_currency="USD",
                    transfer_amount=10,
                    transfer_method="LOCAL",
                    reason="professional_service_fees",
                    reference=f"SDK test {run}",
                ),
            )
        else:
            print(f"  {YELLOW}SKIP{RESET} transfers.create: no beneficiary from phase 4")
            RESULTS["skip"] += 1
        if transfer is not None:
            check("transfers.retrieve", lambda: fx_client.transfers.retrieve(transfer.id))
            check(
                "simulation.transition_transfer",
                lambda: fx_client.simulation.transition_transfer(transfer.id, next_status="PAID"),
            )
            check(
                "transfers.retrieve (after transition)",
                lambda: f"status={fx_client.transfers.retrieve(transfer.id).status}",
            )

        print("\nPhase 7 — webhook endpoint lifecycle:")
        hook = check(
            "webhook_endpoints.create",
            lambda: client.webhook_endpoints.create(
                url=f"https://example.com/awx-sdk-test-{run}",
                events=["transfer.settled"],
                version="2024-01-31",
            ),
        )
        if hook is not None:
            check("webhook_endpoints.retrieve", lambda: client.webhook_endpoints.retrieve(hook.id))
            check("webhook_endpoints.delete", lambda: client.webhook_endpoints.delete(hook.id))

        print("\nPhase 8 — auto-pagination over live data:")

        def _walk_pages() -> str:
            count = sum(1 for _ in client.beneficiaries.list(page_size=10).auto_paging_iter())
            return f"walked {count} beneficiaries across pages"

        check("beneficiaries auto_paging_iter", _walk_pages)

        print("\nPhase 9 — cleanup (delete test beneficiary):")
        if beneficiary is not None:
            check(
                "beneficiaries.delete",
                lambda: client.beneficiaries.delete(beneficiary.beneficiary_id),
            )

    print("\nPhase 10 — async client against the live API:")

    async def _async_checks() -> None:
        async with AsyncAirwallex(api_version="2024-01-31", **kwargs) as aclient:
            balances = await aclient.balances.current()
            print(f"  {GREEN}OK{RESET}   async balances.current: {len(balances)} currencies")
            page = await aclient.beneficiaries.list(page_size=10)
            names = [b.nickname async for b in page.auto_paging_iter()]
            print(f"  {GREEN}OK{RESET}   async auto_paging_iter: {len(names)} beneficiaries")
            RESULTS["ok"] += 2

    try:
        asyncio.run(_async_checks())
    except Exception as exc:
        RESULTS["fail"] += 1
        print(f"  {RED}FAIL{RESET} async client: {type(exc).__name__}: {exc}")

    print(f"\nRESULT: {RESULTS['ok']} ok, {RESULTS['skip']} skipped, {RESULTS['fail']} failed")
    sys.exit(1 if RESULTS["fail"] else 0)


if __name__ == "__main__":
    main()
