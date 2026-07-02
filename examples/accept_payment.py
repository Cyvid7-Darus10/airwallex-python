"""Payment acceptance: customers, payment intents, and refunds.

Set AIRWALLEX_CLIENT_ID / AIRWALLEX_API_KEY, then:

    python examples/accept_payment.py
"""

from __future__ import annotations

import uuid

from airwallex import Airwallex


def main() -> None:
    run = uuid.uuid4().hex[:8]
    with Airwallex(environment="demo") as client:
        # Optionally attach payments to a customer you manage.
        customer = client.customers.create(
            merchant_customer_id=f"example-{run}",
            first_name="Ada",
            last_name="Lovelace",
            email=f"ada+{run}@example.com",
        )
        print("customer:", customer.id)

        # A payment intent is the money you intend to collect. Your frontend
        # (Airwallex.js / mobile SDKs) confirms it with the shopper's card;
        # confirmation needs a payment method, so here we just create + cancel.
        intent = client.payment_intents.create(
            amount=25.00,
            currency="USD",
            merchant_order_id=f"order-{run}",
            customer_id=customer.id,
        )
        print("intent:", intent.id, intent.status)

        cancelled = client.payment_intents.cancel(
            intent.id, cancellation_reason="requested_by_customer"
        )
        print("cancelled:", cancelled.status)

        # After a successful payment you can refund part or all of it:
        #   client.refunds.create(payment_intent_id=intent.id, amount=5.00)

        # List recent intents (auto-pagination walks every page).
        recent = [i.id for i in client.payment_intents.list(page_size=10)]
        print(f"{len(recent)} recent intents on first page")


if __name__ == "__main__":
    main()
