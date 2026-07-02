# Examples

Every example reads credentials from the environment and targets the **demo**
(sandbox) environment — no real money moves:

```bash
export AIRWALLEX_CLIENT_ID=...   # from the Airwallex web app: Developer → API Keys
export AIRWALLEX_API_KEY=...
python examples/<name>.py
```

| Example | What it shows |
|---|---|
| [`payout_quickstart.py`](payout_quickstart.py) | Balances, FX rate, beneficiaries, creating a transfer |
| [`accept_payment.py`](accept_payment.py) | Payment intent lifecycle: create → retrieve → cancel, plus customers and refunds |
| [`issue_cards.py`](issue_cards.py) | Issuing: cardholder + virtual card creation, limits, transactions |
| [`fx_conversion.py`](fx_conversion.py) | Indicative rate → lockable quote → conversion, and amendment quoting |
| [`webhook_server.py`](webhook_server.py) | Verifying webhook signatures in a web server (stdlib; FastAPI/Flask snippets included) |
| [`async_quickstart.py`](async_quickstart.py) | `AsyncAirwallex` with concurrent requests and async auto-pagination |
| [`error_handling.py`](error_handling.py) | Typed errors, retry configuration, idempotency, connected accounts, raw escape hatch |
| [`local_smoke_test.py`](local_smoke_test.py) | Read-mostly health check across 14 endpoint groups (uses `.env.demo`) |
| [`local_lifecycle_test.py`](local_lifecycle_test.py) | Full write lifecycles against the sandbox (uses `.env.demo`) |
