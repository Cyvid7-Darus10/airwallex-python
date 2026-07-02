# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres
to [Semantic Versioning](https://semver.org/).

## [0.2.1] - 2026-07-02

### Fixed

- Payment-acceptance lifecycle actions (`payment_intents.confirm`/`confirm_continue`/`capture`/`cancel`) and `customers.update` now auto-generate the `request_id` the API requires — previously these calls failed with `400 validation_error`.
- `RateQuote` types the `rate`, `conversion_date`, and `created_at` fields returned by the live `fx/rates/current` endpoint.

### Added

- Live demo-environment smoke and lifecycle test scripts under `examples/` (verified: 40+ checks against the real sandbox, including funded transfers and FX conversions).
- README notes on live-API quirks: per-endpoint-group version requirements, minimum `page_size` of 10, `version` required on webhook creation.

## [0.2.0] - 2026-07-02

### Added

- **Payment acceptance**: `payment_intents` (create/retrieve/list/confirm/confirm_continue/capture/cancel), `customers` (CRUD + `generate_client_secret`), `refunds`.
- **Issuing**: `issuing_cardholders`, `issuing_cards` (incl. activate/limits), `issuing_transactions`, `issuing_authorizations`.
- **Payouts completion**: `batch_transfers` (full lifecycle), `wallet_transfers`, `payers`, `transfers.confirm_funding`.
- **FX completion**: `fx_quotes` (lockable quotes), `conversion_amendments`.
- **Platform**: `accounts.retrieve`, `financial_transactions`, `settlements`, and demo-only `simulation` helpers (deposits, transfer/payment transitions).
- Client wiring test guaranteeing every resource is exposed on both sync and async clients.
- Expanded core test suite (models, pagination edge cases, unicode payloads, context-manager lifecycle); coverage gate raised to 88%.

## [0.1.0] - 2026-07-02

### Added

- Sync (`Airwallex`) and async (`AsyncAirwallex`) clients built on httpx.
- Automatic bearer-token authentication with pre-expiry refresh and single
  re-login on 401.
- Automatic retries with full-jitter exponential backoff on 408/429/5xx and
  network errors, honouring `Retry-After` (both seconds and HTTP-date forms).
  409 conflicts are never retried and surface as `ConflictError`.
- Auto-generated `request_id` on money-moving calls for idempotency.
- Resources: balances, transfers (payouts), beneficiaries, conversions, rates,
  global accounts, deposits, reference data, webhook endpoint management.
- Typed, immutable, forward-compatible Pydantic v2 response models.
- Auto-pagination via `SyncPage.auto_paging_iter()` / `AsyncPage.auto_paging_iter()`.
- Webhook signature verification (`airwallex.webhooks`) with replay protection.
- Typed error hierarchy carrying Airwallex error `code`, `source`, and `request_id`.
