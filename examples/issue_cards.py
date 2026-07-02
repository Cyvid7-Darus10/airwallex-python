"""Issuing: create a cardholder, issue a virtual card, inspect activity.

Requires issuing to be enabled on your Airwallex account.
Set AIRWALLEX_CLIENT_ID / AIRWALLEX_API_KEY, then:

    python examples/issue_cards.py
"""

from __future__ import annotations

import uuid

from airwallex import Airwallex, APIStatusError


def main() -> None:
    run = uuid.uuid4().hex[:8]
    with Airwallex(environment="demo") as client:
        try:
            cardholder = client.issuing_cardholders.create(
                email=f"employee+{run}@example.com",
                type="INDIVIDUAL",
                individual={
                    "name": {"first_name": "Grace", "last_name": "Hopper"},
                    "date_of_birth": "1990-01-01",
                },
            )
        except APIStatusError as err:
            print(f"issuing not enabled on this account ({err.code}) — stopping")
            return
        print("cardholder:", cardholder.cardholder_id)

        card = client.issuing_cards.create(
            cardholder_id=cardholder.cardholder_id,
            form_factor="VIRTUAL",
            created_by="Grace Hopper",
            is_personalized=False,
            program={"purpose": "COMMERCIAL"},
            authorization_controls={
                "allowed_transaction_count": "MULTIPLE",
                "transaction_limits": {
                    "currency": "USD",
                    "limits": [{"amount": 1000, "interval": "PER_TRANSACTION"}],
                },
            },
        )
        print("card:", card.card_id or card.id, card.card_status or card.status)

        limits = client.issuing_cards.limits(card.card_id or card.id)
        print("limits:", limits.to_dict())

        # Card activity, newest first.
        transactions = client.issuing_transactions.list(page_size=10)
        print(f"{len(transactions.items)} recent issuing transactions")

        authorizations = client.issuing_authorizations.list(page_size=10)
        print(f"{len(authorizations.items)} recent authorizations")


if __name__ == "__main__":
    main()
