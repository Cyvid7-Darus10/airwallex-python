# Contributing

Thanks for helping improve the unofficial Airwallex Python SDK!

## Setup

```bash
git clone https://github.com/Cyvid7-Darus10/airwallex-python
cd airwallex-python
uv sync
```

## Before opening a PR

```bash
uv run ruff format .        # format
uv run ruff check .         # lint
uv run mypy                 # strict type-check
uv run pytest --cov         # tests (coverage must stay >= 80%)
```

All four must pass; CI runs them on Python 3.9–3.13.

## Guidelines

- **Tests first.** Every behavior change needs a test that fails without it.
  Tests use [respx](https://lundberg.github.io/respx/) — no network calls.
- **Ground new endpoints in the official spec** (`https://www.airwallex.com/docs/api/schema.json`)
  rather than guessing field names.
- Keep the sync and async clients in exact behavioral parity.
- Response models are frozen and `extra="allow"` — type the documented fields,
  let unknown fields pass through.
- Money-moving `create` calls must go through `ensure_request_id` for idempotency.
- Conventional commits: `feat: ...`, `fix: ...`, `docs: ...`, etc.

## Releases (maintainers)

1. Bump `version` in `pyproject.toml` and `src/airwallex/_version.py`, update `CHANGELOG.md`.
2. Tag: `git tag v<version> && git push --tags`.
3. The `release.yml` workflow builds and publishes to PyPI via trusted publishing.
