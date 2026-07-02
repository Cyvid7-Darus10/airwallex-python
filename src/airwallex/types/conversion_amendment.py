from __future__ import annotations

from typing import Any, Optional

from .._models import AirwallexModel


class AmendmentCharge(AirwallexModel):
    """A charge (or credit) applied by a conversion amendment."""

    amount: Optional[float] = None
    currency: Optional[str] = None
    type: Optional[str] = None
    currency_pair: Optional[str] = None
    awx_rate: Optional[float] = None
    client_rate: Optional[float] = None


class ConversionAmendment(AirwallexModel):
    """An amendment to a conversion (``/api/v1/conversion_amendments``)."""

    amendment_id: Optional[str] = None
    request_id: Optional[str] = None
    short_reference_id: Optional[str] = None
    conversion_id: Optional[str] = None
    type: Optional[str] = None

    charges: Optional[list[AmendmentCharge]] = None
    metadata: Optional[dict[str, Any]] = None

    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ConversionAmendmentQuote(AirwallexModel):
    """The quoted charges for a conversion amendment before executing it."""

    request_id: Optional[str] = None
    short_reference_id: Optional[str] = None
    conversion_id: Optional[str] = None
    type: Optional[str] = None
    charges: Optional[list[AmendmentCharge]] = None
    metadata: Optional[dict[str, Any]] = None
