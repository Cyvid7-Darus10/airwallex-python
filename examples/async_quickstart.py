"""AsyncAirwallex: concurrent requests and async pagination.

Set AIRWALLEX_CLIENT_ID / AIRWALLEX_API_KEY, then:

    python examples/async_quickstart.py
"""

from __future__ import annotations

import asyncio

from airwallex import AsyncAirwallex


async def main() -> None:
    async with AsyncAirwallex(environment="demo") as client:
        # Fire independent calls concurrently — one client, one token.
        balances, transfers, rate = await asyncio.gather(
            client.balances.current(),
            client.transfers.list(page_size=10),
            client.rates.current(sell_currency="USD", buy_currency="SGD", sell_amount=100),
        )
        print(f"{len(balances)} balances | {len(transfers.items)} transfers | rate {rate.rate}")

        # Async auto-pagination walks every page lazily.
        page = await client.beneficiaries.list(page_size=10)
        count = 0
        async for _beneficiary in page.auto_paging_iter():
            count += 1
        print(f"{count} beneficiaries across all pages")


if __name__ == "__main__":
    asyncio.run(main())
