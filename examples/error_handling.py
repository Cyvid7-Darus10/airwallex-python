"""Typed errors, retries, idempotency, connected accounts, and the raw escape hatch.

Set AIRWALLEX_CLIENT_ID / AIRWALLEX_API_KEY, then:

    python examples/error_handling.py
"""

from __future__ import annotations

import logging

from airwallex import (
    Airwallex,
    APIConnectionError,
    APIStatusError,
    NotFoundError,
    RateLimitError,
)


def main() -> None:
    # See every request, retry, and token refresh the SDK makes:
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("airwallex").setLevel(logging.DEBUG)

    client = Airwallex(
        environment="demo",
        max_retries=3,  # 408/429/5xx/network errors retry with jittered backoff
        timeout=30.0,
        # on_behalf_of="acct_...",          # platforms: act on a connected account
        # http_client=httpx.Client(proxy="http://proxy:3128"),  # bring your own transport
    )

    with client:
        # Typed error handling — every error carries the Airwallex code,
        # source field, and the x-request-id to quote to support.
        try:
            client.transfers.retrieve("6f63544d-0000-0000-0000-000000000000")
        except NotFoundError as err:
            print(f"not found: code={err.code} request_id={err.request_id}")
        except RateLimitError:
            print("rate limited — the SDK already retried with backoff")
        except APIStatusError as err:
            print(f"API error {err.status_code}: {err.code} on {err.source}")
        except APIConnectionError as err:
            print(f"network problem after retries: {err}")

        # Idempotency: pass your own request_id to make retries across process
        # restarts safe too (the SDK generates one per call otherwise).
        #   client.transfers.create(request_id=f"payout-{invoice_id}", ...)

        # Raw escape hatch — any endpoint, with auth/retries/errors intact:
        disputes = client.request("GET", "/api/v1/pa/payment_disputes", params={"page_size": 10})
        print(f"{len((disputes or {}).get('items', []))} open disputes")


if __name__ == "__main__":
    main()
