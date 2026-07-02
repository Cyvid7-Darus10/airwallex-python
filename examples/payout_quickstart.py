"""End-to-end payout example against the Airwallex demo environment.

Set AIRWALLEX_CLIENT_ID and AIRWALLEX_API_KEY (demo credentials) and run:

    uv run python examples/payout_quickstart.py
"""

from airwallex import Airwallex, APIStatusError


def main() -> None:
    with Airwallex(environment="demo") as client:
        print("Wallet balances:")
        for balance in client.balances.current():
            print(f"  {balance.currency}: {balance.available_amount}")

        print("\nIndicative USD->PHP rate:")
        quote = client.rates.quote(sell_currency="USD", buy_currency="PHP", sell_amount=100)
        print(f"  {quote.currency_pair} @ {quote.client_rate}")

        print("\nSaved beneficiaries:")
        for beneficiary in client.beneficiaries.list(page_size=10).auto_paging_iter():
            print(f"  {beneficiary.beneficiary_id}: {beneficiary.nickname}")

        try:
            transfer = client.transfers.create(
                beneficiary_id="replace_with_a_real_beneficiary_id",
                source_currency="USD",
                transfer_currency="PHP",
                transfer_amount=100,
                transfer_method="LOCAL",
                reference="SDK quickstart",
                reason="professional_service_fees",
            )
            print(f"\nCreated transfer {transfer.id} ({transfer.status})")
        except APIStatusError as err:
            print(f"\nTransfer failed: {err.code} — {err.message} (request {err.request_id})")


if __name__ == "__main__":
    main()
