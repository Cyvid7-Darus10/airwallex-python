from __future__ import annotations

from typing import Any, Optional

from .._models import AirwallexModel


class Account(AirwallexModel):
    """Details of your own Airwallex account (``GET /api/v1/account``)."""

    id: Optional[str] = None
    identifier: Optional[str] = None
    nickname: Optional[str] = None
    status: Optional[str] = None
    view_type: Optional[str] = None

    account_details: Optional[dict[str, Any]] = None
    primary_contact: Optional[dict[str, Any]] = None
    reactivate_details: Optional[dict[str, Any]] = None
    suspend_details: Optional[list[dict[str, Any]]] = None
    metadata: Optional[dict[str, Any]] = None

    created_at: Optional[str] = None
