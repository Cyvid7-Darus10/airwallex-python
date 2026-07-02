# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres
to [Semantic Versioning](https://semver.org/).

## [0.1.0] - Unreleased

### Added

- Sync (`Airwallex`) and async (`AsyncAirwallex`) clients built on httpx.
- Automatic bearer-token authentication with pre-expiry refresh and single
  re-login on 401.
- Automatic retries with full-jitter exponential backoff on 408/409/429/5xx and
  network errors, honouring `Retry-After`.
- Auto-generated `request_id` on money-moving calls for idempotency.
- Resources: balances, transfers (payouts), beneficiaries, conversions, rates,
  global accounts, deposits, reference data, webhook endpoint management.
- Typed, immutable, forward-compatible Pydantic v2 response models.
- Auto-pagination via `SyncPage.auto_paging_iter()` / `AsyncPage.auto_paging_iter()`.
- Webhook signature verification (`airwallex.webhooks`) with replay protection.
- Typed error hierarchy carrying Airwallex error `code`, `source`, and `request_id`.
