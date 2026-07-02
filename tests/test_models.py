from __future__ import annotations

import pydantic
import pytest

from airwallex.types import Balance, BankDetails, Beneficiary, BeneficiaryDetails, Transfer


def test_models_are_immutable():
    balance = Balance(currency="USD", available_amount=10.0)
    with pytest.raises(pydantic.ValidationError):
        balance.currency = "SGD"  # type: ignore[misc]


def test_unknown_fields_preserved_and_accessible():
    transfer = Transfer.model_validate({"id": "tra_1", "future_field": {"deeply": ["nested", 1]}})
    assert transfer.future_field == {"deeply": ["nested", 1]}
    assert transfer.to_dict()["future_field"] == {"deeply": ["nested", 1]}


def test_to_dict_excludes_unset_fields():
    transfer = Transfer.model_validate({"id": "tra_1"})
    dumped = transfer.to_dict()
    assert dumped == {"id": "tra_1"}
    assert "status" not in dumped


def test_nested_models_parse():
    beneficiary = Beneficiary.model_validate(
        {
            "beneficiary_id": "ben_1",
            "beneficiary": {
                "entity_type": "COMPANY",
                "company_name": "Acme Pte Ltd",
                "bank_details": {
                    "account_number": "12345678",
                    "bank_country_code": "SG",
                    "swift_code": "DBSSSGSG",
                },
            },
        }
    )
    assert isinstance(beneficiary.beneficiary, BeneficiaryDetails)
    assert isinstance(beneficiary.beneficiary.bank_details, BankDetails)
    assert beneficiary.beneficiary.bank_details.swift_code == "DBSSSGSG"


def test_unicode_and_large_amounts_roundtrip():
    transfer = Transfer.model_validate(
        {
            "id": "tra_1",
            "reference": "発票 №42 — Ñüñez & Söhne",
            "source_amount": 99_999_999_999.99,
        }
    )
    assert transfer.reference == "発票 №42 — Ñüñez & Söhne"
    assert transfer.source_amount == 99_999_999_999.99


def test_none_and_empty_payloads_tolerated():
    assert Transfer.model_validate({}).id is None
    balance = Balance.model_validate({"currency": None})
    assert balance.currency is None
