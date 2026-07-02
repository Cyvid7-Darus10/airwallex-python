"""Local smoke test against the Airwallex demo environment.

Read-only calls plus demo-only simulation helpers — no real money moves and
nothing is written back to the account except sandbox simulation deposits.

Credentials are read from .env.demo (gitignored) in the project root:

    AIRWALLEX_CLIENT_ID=...
    AIRWALLEX_API_KEY=...

Run:  uv run python examples/local_smoke_test.py
"""

from __future__ import annotations

import pathlib
import sys

from airwallex import Airwallex, APIStatusError

GREEN, RED, YELLOW, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[0m"


def load_env() -> dict[str, str]:
    env_file = pathlib.Path(__file__).resolve().parents[1] / ".env.demo"
    if not env_file.exists():
        sys.exit(
            f"{RED}Missing {env_file} — create it with AIRWALLEX_CLIENT_ID/AIRWALLEX_API_KEY{RESET}"
        )
    values: dict[str, str] = {}
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def check(name: str, fn) -> bool:
    try:
        result = fn()
    except APIStatusError as err:
        if err.status_code in (403, 404) or (err.code or "").lower() in {
            "unauthorized",
            "access_denied",
            "not_found",
        }:
            print(
                f"  {YELLOW}SKIP{RESET} {name}: {err.status_code} {err.code} "
                "(feature not enabled on this account)"
            )
            return True
        print(f"  {RED}FAIL{RESET} {name}: {err}")
        return False
    except Exception as exc:  # smoke test wants everything surfaced
        print(f"  {RED}FAIL{RESET} {name}: {type(exc).__name__}: {exc}")
        return False
    print(f"  {GREEN}OK{RESET}   {name}: {result}")
    return True


def main() -> None:
    env = load_env()
    client = Airwallex(
        client_id=env.get("AIRWALLEX_CLIENT_ID"),
        api_key=env.get("AIRWALLEX_API_KEY"),
        environment="demo",
        # Coherent across this SDK's surface: transfers require >=2024-01-31 and
        # conversions.list rejects newer versions on some accounts.
        api_version="2024-01-31",
    )
    # fx/rates/current rejects 2024-01-31 while conversions.list requires it —
    # Airwallex versions endpoint groups independently, so use a second,
    # unpinned client for the modern FX rates endpoint.
    rates_client = Airwallex(
        client_id=env.get("AIRWALLEX_CLIENT_ID"),
        api_key=env.get("AIRWALLEX_API_KEY"),
        environment="demo",
    )
    ok = True
    with client, rates_client:
        print("Read-only checks:")

        def _account_summary() -> str:
            details = client.accounts.retrieve().to_dict().get("account_details") or {}
            return f"account retrieved ({details.get('legal_entity_type', 'ok')})"

        ok &= check("auth + account", _account_summary)
        ok &= check(
            "balances.current", lambda: f"{len(client.balances.current())} currency balance(s)"
        )

        def _live_rate() -> str:
            quote = rates_client.rates.current(
                buy_currency="SGD", sell_currency="USD", sell_amount=100
            )
            return f"rate={quote.rate}"

        ok &= check("rates.current USD->SGD", _live_rate)
        ok &= check(
            "reference.supported_currencies",
            lambda: (
                lambda r: f"{len(r.get('items', r) if isinstance(r, dict) else r)} currencies"
            )(client.reference.supported_currencies()),
        )
        ok &= check(
            "beneficiaries.list",
            lambda: f"{len(client.beneficiaries.list(page_size=10).items)} on first page",
        )
        ok &= check(
            "transfers.list",
            lambda: f"{len(client.transfers.list(page_size=10).items)} on first page",
        )
        ok &= check(
            "global_accounts.list",
            lambda: f"{len(client.global_accounts.list(page_size=10).items)} on first page",
        )
        ok &= check(
            "deposits.list",
            lambda: f"{len(client.deposits.list(page_size=10).items)} on first page",
        )
        ok &= check(
            "conversions.list",
            lambda: f"{len(client.conversions.list(page_size=10).items)} on first page",
        )
        ok &= check(
            "payment_intents.list",
            lambda: f"{len(client.payment_intents.list(page_size=10).items)} on first page",
        )
        ok &= check(
            "customers.list",
            lambda: f"{len(client.customers.list(page_size=10).items)} on first page",
        )
        ok &= check(
            "issuing_cards.list",
            lambda: f"{len(client.issuing_cards.list(page_size=10).items)} on first page",
        )
        ok &= check(
            "financial_transactions.list",
            lambda: f"{len(client.financial_transactions.list(page_size=10).items)} on first page",
        )
        ok &= check(
            "webhook_endpoints.list",
            lambda: f"{len(client.webhook_endpoints.list(page_size=10).items)} on first page",
        )

        print("\nDemo-only simulation (money-in, sandbox):")

        def _simulated_deposit() -> str:
            accounts = client.global_accounts.list(page_size=10).items
            if not accounts:
                return "skipped: no global accounts on this demo account"
            ga = accounts[0]
            result = client.simulation.create_deposit(
                amount=100, currency=ga.currency or "USD", global_account_id=ga.id
            )
            return f"deposit created: {(result or {}).get('id', 'ok')}"

        ok &= check("simulation.create_deposit 100", _simulated_deposit)
        ok &= check(
            "balances.current (after deposit)",
            lambda: f"{[(b.currency, b.available_amount) for b in client.balances.current()][:3]}",
        )

        print("\nError handling against the live API:")
        ok &= check("invalid id maps to typed error", lambda: _expect_404(client))

    print(f"\n{'ALL CHECKS PASSED' if ok else 'SOME CHECKS FAILED'}")
    sys.exit(0 if ok else 1)


def _expect_404(client: Airwallex) -> str:
    from airwallex import BadRequestError, NotFoundError

    try:
        client.transfers.retrieve("tra_does_not_exist_12345")
    except NotFoundError as err:
        return f"NotFoundError with request_id={err.request_id}"
    except BadRequestError as err:
        # Airwallex validates id format before existence
        return f"BadRequestError (format check) code={err.code} request_id={err.request_id}"
    raise AssertionError("expected a typed 4xx error")


if __name__ == "__main__":
    main()
