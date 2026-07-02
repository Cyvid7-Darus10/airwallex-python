from __future__ import annotations

from typing import Any, Optional

from .._models import AirwallexModel


class PayerDetails(AirwallexModel):
    """The payer entity itself (person or company)."""

    entity_type: Optional[str] = None
    company_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[dict[str, Any]] = None
    additional_info: Optional[dict[str, Any]] = None


class Payer(AirwallexModel):
    """A saved payment sender (``/api/v1/payers``)."""

    payer_id: Optional[str] = None
    nickname: Optional[str] = None
    payer: Optional[PayerDetails] = None
