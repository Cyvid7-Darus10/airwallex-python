from __future__ import annotations

from typing import Any

from ._base import AsyncResource, SyncResource, pid

_BASE = "/api/v1/simulation"


class Simulation(SyncResource):
    """Sandbox-only helpers for driving resources through their lifecycle.

    These endpoints only work in the demo environment
    (``environment="demo"``); calling them against production returns an
    error. Responses are returned as raw JSON since their shapes vary by
    scenario.
    """

    def create_deposit(self, **payload: Any) -> Any:
        """Simulate an incoming deposit to a global account."""
        return self._client.post(f"{_BASE}/deposit/create", json=payload)

    def settle_deposit(self, deposit_id: str) -> Any:
        """Settle a simulated deposit."""
        return self._client.post(f"{_BASE}/deposits/{pid(deposit_id)}/settle")

    def reject_deposit(self, deposit_id: str) -> Any:
        """Reject a simulated deposit."""
        return self._client.post(f"{_BASE}/deposits/{pid(deposit_id)}/reject")

    def reverse_deposit(self, deposit_id: str) -> Any:
        """Reverse a simulated deposit."""
        return self._client.post(f"{_BASE}/deposits/{pid(deposit_id)}/reverse")

    def transition_transfer(self, transfer_id: str, **payload: Any) -> Any:
        """Move a transfer to another status, e.g. ``next_status="PAID"``."""
        return self._client.post(f"{_BASE}/transfers/{pid(transfer_id)}/transition", json=payload)

    def transition_payment(self, payment_id: str, **payload: Any) -> Any:
        """Move a legacy payment to another status."""
        return self._client.post(f"{_BASE}/payments/{pid(payment_id)}/transition", json=payload)


class AsyncSimulation(AsyncResource):
    """Async counterpart of :class:`Simulation`.

    These endpoints only work in the demo environment
    (``environment="demo"``); calling them against production returns an
    error.
    """

    async def create_deposit(self, **payload: Any) -> Any:
        """Simulate an incoming deposit to a global account."""
        return await self._client.post(f"{_BASE}/deposit/create", json=payload)

    async def settle_deposit(self, deposit_id: str) -> Any:
        """Settle a simulated deposit."""
        return await self._client.post(f"{_BASE}/deposits/{pid(deposit_id)}/settle")

    async def reject_deposit(self, deposit_id: str) -> Any:
        """Reject a simulated deposit."""
        return await self._client.post(f"{_BASE}/deposits/{pid(deposit_id)}/reject")

    async def reverse_deposit(self, deposit_id: str) -> Any:
        """Reverse a simulated deposit."""
        return await self._client.post(f"{_BASE}/deposits/{pid(deposit_id)}/reverse")

    async def transition_transfer(self, transfer_id: str, **payload: Any) -> Any:
        """Move a transfer to another status, e.g. ``next_status="PAID"``."""
        return await self._client.post(
            f"{_BASE}/transfers/{pid(transfer_id)}/transition", json=payload
        )

    async def transition_payment(self, payment_id: str, **payload: Any) -> Any:
        """Move a legacy payment to another status."""
        return await self._client.post(
            f"{_BASE}/payments/{pid(payment_id)}/transition", json=payload
        )
