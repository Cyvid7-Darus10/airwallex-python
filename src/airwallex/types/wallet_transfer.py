from __future__ import annotations

from typing import Optional

from .._models import AirwallexModel


class WalletTransferBeneficiary(AirwallexModel):
    """The receiving Airwallex wallet of a wallet transfer."""

    account_name: Optional[str] = None
    account_number: Optional[str] = None


class WalletTransfer(AirwallexModel):
    """A transfer between Airwallex wallets (``/api/v1/wallet_transfers``)."""

    wallet_transfer_id: Optional[str] = None
    request_id: Optional[str] = None
    short_reference_id: Optional[str] = None
    status: Optional[str] = None

    transfer_amount: Optional[float] = None
    transfer_currency: Optional[str] = None
    beneficiary: Optional[WalletTransferBeneficiary] = None

    reason: Optional[str] = None
    reference: Optional[str] = None

    created_at: Optional[str] = None
    settled_at: Optional[str] = None
