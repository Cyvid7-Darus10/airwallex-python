"""Transactional FX: indicative rate → lockable quote → conversion.

Set AIRWALLEX_CLIENT_ID / AIRWALLEX_API_KEY, then:

    python examples/fx_conversion.py

Note: FX endpoints are versioned independently by Airwallex. On some
accounts ``conversions`` requires ``api_version="2024-01-31"`` while
``rates``/``fx_quotes`` require the account default — hence two clients.
"""

from __future__ import annotations

from airwallex import Airwallex


def main() -> None:
    with (
        Airwallex(environment="demo") as fx,
        Airwallex(environment="demo", api_version="2024-01-31") as legacy,
    ):
        # 1. Indicative rate — free to call, nothing is locked.
        rate = fx.rates.current(sell_currency="USD", buy_currency="SGD", sell_amount=1000)
        print(f"indicative {rate.currency_pair}: {rate.rate}")

        # 2. Lockable quote — freezes a rate for the validity window so you can
        #    show a guaranteed price before executing.
        quote = fx.fx_quotes.create(
            sell_currency="USD", buy_currency="SGD", sell_amount=1000, validity="HR_24"
        )
        print(f"locked quote {quote.quote_id}: {quote.client_rate} until {quote.valid_to_at}")

        # 3. Execute the conversion (moves funds between wallet currencies).
        conversion = legacy.conversions.create(
            sell_currency="USD",
            buy_currency="SGD",
            sell_amount=1000,
            term_agreement=True,
            reason="Fund_SGD_account",
        )
        print("conversion:", conversion.conversion_id, conversion.status)

        # 4. Need to change a booked conversion? Quote an amendment first.
        #    amendment = legacy.conversion_amendments.quote(
        #        conversion_id=conversion.conversion_id, type="CANCEL"
        #    )


if __name__ == "__main__":
    main()
