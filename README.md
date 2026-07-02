# airwallex-python

**Unofficial** Python SDK for the [Airwallex API](https://www.airwallex.com/docs/api) — payouts, FX, balances, global accounts, beneficiaries, deposits, and webhooks.

[![CI](https://github.com/Cyvid7-Darus10/airwallex-python/actions/workflows/ci.yml/badge.svg)](https://github.com/Cyvid7-Darus10/airwallex-python/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/airwallex?style=flat)](https://pypi.org/project/airwallex/)
[![Python](https://img.shields.io/pypi/pyversions/airwallex?style=flat)](https://pypi.org/project/airwallex/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Beta](https://img.shields.io/badge/status-beta-orange.svg)](#status)

> [!IMPORTANT]
> This is an **unofficial, community-maintained** library. It is **not** affiliated with, endorsed by, or supported by Airwallex Pty Ltd — "Airwallex" is their trademark, used here only to describe compatibility. The SDK is in **beta**: the public interface may change before v1.0, so pin your version. For vendor-supported tooling, use the [official Node.js SDK](https://www.npmjs.com/package/@airwallex/node-sdk).

Airwallex's only official server-side SDK is Node.js. This library brings the same developer experience to Python:

- **Sync and async clients** (`Airwallex` / `AsyncAirwallex`) built on [httpx](https://www.python-httpx.org/)
- **Automatic authentication** — token fetched on first use and refreshed before expiry; no manual login calls
- **Idempotent by default** — `request_id` is auto-generated for money-moving calls, so retries never double-pay
- **Automatic retries** with full-jitter exponential backoff on 408/429/5xx/network failures (honours `Retry-After`; 409 business conflicts are never retried)
- **Typed responses** — Pydantic v2 models that are immutable and forward-compatible (unknown fields preserved, never dropped)
- **Auto-pagination** — iterate every page with one loop
- **Webhook signature verification** with replay protection
- **Typed errors** — `RateLimitError`, `AuthenticationError`, … each carrying the Airwallex error `code`, `source`, and `request_id`

## Installation

Available on [PyPI](https://pypi.org/project/airwallex/):

```bash
pip install airwallex
```

Requires Python 3.9+. Releases follow [semantic versioning](#status); see the [changelog](CHANGELOG.md).

## Quickstart

Create API credentials in the Airwallex web app under **Developer → API keys**, then:

```python
from airwallex import Airwallex

client = Airwallex(
    client_id="your_client_id",   # or set AIRWALLEX_CLIENT_ID
    api_key="your_api_key",       # or set AIRWALLEX_API_KEY
    environment="demo",           # "production" (default) or "demo" sandbox
)

# Current wallet balances
for balance in client.balances.current():
    print(balance.currency, balance.available_amount)
```

### Send a payout

> Payouts use `/api/v1/transfers`, which requires API version 2024-01-31 or later. If your account default is older, pass `api_version="2024-01-31"` (or newer) to the client.

```python
transfer = client.transfers.create(
    beneficiary_id="ben_abc123",
    source_currency="USD",
    transfer_currency="PHP",
    transfer_amount=5000,
    transfer_method="LOCAL",
    reference="Invoice 42",
    reason="professional_service_fees",
)
print(transfer.id, transfer.status)
```

`request_id` is generated for you (pass your own to control idempotency). Airwallex will never execute the same `request_id` twice — including across the SDK's automatic retries.

### FX: quote and convert

```python
rate = client.rates.current(buy_currency="USD", sell_currency="SGD", buy_amount=1000)
print(rate.client_rate)

conversion = client.conversions.create(
    buy_currency="USD",
    sell_currency="SGD",
    buy_amount=1000,
    term_agreement=True,
)
```

### Accept a payment

```python
intent = client.payment_intents.create(
    amount=25.00,
    currency="USD",
    merchant_order_id="order_42",
)
confirmed = client.payment_intents.confirm(intent.id, payment_method={"type": "card", "card": {...}})
refund = client.refunds.create(payment_intent_id=intent.id, amount=5.00)
```

### Issue a card

```python
cardholder = client.issuing_cardholders.create(
    email="employee@example.com",
    individual={"name": {"first_name": "Ada", "last_name": "Lovelace"}},
    type="INDIVIDUAL",
)
card = client.issuing_cards.create(
    cardholder_id=cardholder.cardholder_id,
    form_factor="VIRTUAL",
    created_by="Ada Lovelace",
    program={"purpose": "COMMERCIAL"},
)
```

### Test flows in the sandbox

```python
client.simulation.create_deposit(amount=1000, currency="USD")   # demo environment only
client.simulation.transition_transfer("tra_123", next_status="PAID")
```

### Auto-pagination

```python
# Iterates page by page under the hood
for beneficiary in client.beneficiaries.list(page_size=100).auto_paging_iter():
    print(beneficiary.beneficiary_id, beneficiary.nickname)
```

### Async

```python
import asyncio
from airwallex import AsyncAirwallex

async def main() -> None:
    async with AsyncAirwallex(environment="demo") as client:
        page = await client.transfers.list(status="PAID")
        async for transfer in page.auto_paging_iter():
            print(transfer.id)

asyncio.run(main())
```

### Webhooks

Verify and parse incoming notifications (get the secret when you create the webhook endpoint):

```python
from airwallex import webhooks, WebhookSignatureError

def handle(request):  # any web framework
    try:
        event = webhooks.construct_event(
            payload=request.body,                      # raw bytes — do not re-serialise
            timestamp=request.headers["x-timestamp"],
            signature=request.headers["x-signature"],
            secret=WEBHOOK_SECRET,
        )
    except WebhookSignatureError:
        return 400
    if event.name == "transfer.settled":
        ...
    return 200
```

### Error handling

```python
from airwallex import Airwallex, RateLimitError, APIStatusError

try:
    client.transfers.retrieve("tra_missing")
except RateLimitError:
    ...  # already retried automatically; back off further
except APIStatusError as err:
    print(err.status_code, err.code, err.message, err.request_id)
```

All API errors inherit from `airwallex.APIError`; network failures raise `airwallex.APIConnectionError`.

### Calling endpoints the SDK doesn't wrap yet

Every list method accepts extra query params as keyword arguments, and the client exposes a raw escape hatch with auth, retries, and error mapping intact:

```python
page = client.transfers.list(short_reference_id="REF123")          # extra filter
disputes = client.request("GET", "/api/v1/pa/payment_disputes", params={"status": "OPEN"})
```

### Typed responses

Response models live in `airwallex.types` and preserve unknown fields for forward compatibility:

```python
from airwallex.types import Transfer, Balance

def settle(transfer: Transfer) -> None: ...
```

### Bring your own httpx client

```python
import httpx
client = Airwallex(http_client=httpx.Client(proxy="http://proxy:3128"))
```

The SDK applies the base URL and default headers per request, so proxies and custom TLS work without extra configuration; the SDK will not close a client you own.

### Connected accounts (platforms)

```python
client = Airwallex(on_behalf_of="acct_connected_account_id")  # sets x-on-behalf-of
```

### Pinning an API version

```python
client = Airwallex(api_version="2024-08-07")  # sets x-api-version on every request
```

## Resources covered

| Resource | Methods |
|---|---|
| `client.balances` | `current`, `history` |
| `client.transfers` | `create`, `retrieve`, `list`, `cancel`, `validate`, `confirm_funding` |
| `client.batch_transfers` | `create`, `retrieve`, `list`, `add_items`, `delete_items`, `items`, `quote`, `submit`, `delete` |
| `client.wallet_transfers` | `create`, `retrieve`, `list` |
| `client.payers` | `create`, `retrieve`, `update`, `delete`, `list`, `validate` |
| `client.beneficiaries` | `create`, `retrieve`, `update`, `delete`, `list`, `validate` |
| `client.conversions` | `create`, `retrieve`, `list` |
| `client.rates` | `current` |
| `client.fx_quotes` | `create`, `retrieve` |
| `client.conversion_amendments` | `create`, `quote`, `retrieve`, `list` |
| `client.payment_intents` | `create`, `retrieve`, `list`, `confirm`, `confirm_continue`, `capture`, `cancel` |
| `client.customers` | `create`, `retrieve`, `update`, `list`, `generate_client_secret` |
| `client.refunds` | `create`, `retrieve`, `list` |
| `client.issuing_cardholders` | `create`, `retrieve`, `update`, `delete`, `list` |
| `client.issuing_cards` | `create`, `retrieve`, `update`, `activate`, `limits`, `list` |
| `client.issuing_transactions` | `retrieve`, `list` |
| `client.issuing_authorizations` | `retrieve`, `list` |
| `client.accounts` | `retrieve` |
| `client.financial_transactions` | `retrieve`, `list` |
| `client.settlements` | `retrieve`, `list` |
| `client.simulation` | demo-only: deposit create/settle/reject/reverse, transfer/payment transitions |
| `client.global_accounts` | `create`, `retrieve`, `update`, `close`, `list`, `transactions` |
| `client.deposits` | `list` |
| `client.reference` | `supported_currencies`, `settlement_accounts`, `invalid_conversion_dates` |
| `client.webhook_endpoints` | `create`, `retrieve`, `update`, `delete`, `list` |
| `airwallex.webhooks` | `verify_signature`, `construct_event` |

Coverage now matches (and in webhooks/pagination/simulation, exceeds) the official Node.js SDK's main surfaces — contributions welcome for the remaining areas (disputes, payment consents, linked accounts, scale/platform APIs).

## Status

This SDK is **beta** software:

- The wrapped endpoints are grounded in Airwallex's published API spec and covered by tests, but they have not yet been exercised against every account configuration.
- Semantic versioning applies: breaking changes only in minor versions while `0.x`, and patch releases never change behavior.
- Response models tolerate unknown fields, so new Airwallex API versions won't break parsing.
- Test in the `demo` environment before pointing at production, and pin the version in your dependency file (e.g. `airwallex==0.2.0`).

## Development

```bash
uv sync                 # install dependencies
uv run pytest           # run tests
uv run ruff check .     # lint
uv run mypy             # type-check
```

## Disclaimer

This project is an independent, unofficial SDK maintained by the community. It is not affiliated with, endorsed by, sponsored by, or supported by Airwallex Pty Ltd. "Airwallex" and related marks are trademarks of Airwallex Pty Ltd; they are used here solely to indicate API compatibility. This software is provided "as is" under the MIT license — review the [SECURITY policy](SECURITY.md) and test against the demo environment before moving real money. If you need vendor support or SLAs, use the [official Node.js SDK](https://www.npmjs.com/package/@airwallex/node-sdk).

## License

[MIT](LICENSE)
