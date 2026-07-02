# Security Policy

## Reporting a vulnerability

Please do **not** open a public issue for security problems. Email
**cyrus@pastelero.ph** with the details, or use GitHub's
[private vulnerability reporting](https://github.com/Cyvid7-Darus10/airwallex-python/security/advisories/new).
You should receive a response within 72 hours.

## Supported versions

Only the latest released version receives security fixes.

## Design notes for integrators

- API credentials are read from constructor arguments or the
  `AIRWALLEX_CLIENT_ID` / `AIRWALLEX_API_KEY` environment variables — never
  hardcode them.
- The SDK redacts credentials and bearer tokens from `repr()`, pickling, and
  exceptions. Avoid logging raw `httpx` objects you obtain by other means.
- `base_url` must be HTTPS (plain HTTP is allowed only for localhost mocks).
- Webhook handlers must verify signatures with `airwallex.webhooks.construct_event`
  using the raw request body; replay protection rejects stale timestamps.
