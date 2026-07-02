from __future__ import annotations

from typing import Any, Optional

from .._pagination import AsyncPage, SyncPage
from ..types.beneficiary import Beneficiary
from ._base import AsyncResource, SyncResource

_BASE = "/api/v1/beneficiaries"


class Beneficiaries(SyncResource):
    def list(
        self,
        *,
        entity_type: Optional[str] = None,
        name: Optional[str] = None,
        nick_name: Optional[str] = None,
        company_name: Optional[str] = None,
        bank_account_number: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
    ) -> SyncPage[Beneficiary]:
        """List saved beneficiaries, optionally filtered."""
        return self._paged(
            _BASE,
            Beneficiary,
            {
                "entity_type": entity_type,
                "name": name,
                "nick_name": nick_name,
                "company_name": company_name,
                "bank_account_number": bank_account_number,
                "from_date": from_date,
                "to_date": to_date,
                "page_num": page_num,
                "page_size": page_size,
            },
        )

    def retrieve(self, beneficiary_id: str) -> Beneficiary:
        """Fetch a single beneficiary by id."""
        return Beneficiary.model_validate(self._client.get(f"{_BASE}/{beneficiary_id}"))

    def create(self, **payload: Any) -> Beneficiary:
        """Save a new beneficiary.

        Pass the payload documented by Airwallex, e.g. ``beneficiary={...}``,
        ``nickname=...``. Use :meth:`validate` first to check the details.
        """
        return Beneficiary.model_validate(self._client.post(f"{_BASE}/create", json=payload))

    def update(self, beneficiary_id: str, **payload: Any) -> Beneficiary:
        """Update an existing beneficiary."""
        return Beneficiary.model_validate(
            self._client.post(f"{_BASE}/update/{beneficiary_id}", json=payload)
        )

    def delete(self, beneficiary_id: str) -> None:
        """Delete a beneficiary."""
        self._client.post(f"{_BASE}/delete/{beneficiary_id}")

    def validate(self, **payload: Any) -> Any:
        """Validate beneficiary details without saving them.

        Returns the raw validation result (shape depends on the payout corridor).
        """
        return self._client.post(f"{_BASE}/validate", json=payload)


class AsyncBeneficiaries(AsyncResource):
    async def list(
        self,
        *,
        entity_type: Optional[str] = None,
        name: Optional[str] = None,
        nick_name: Optional[str] = None,
        company_name: Optional[str] = None,
        bank_account_number: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
    ) -> AsyncPage[Beneficiary]:
        """List saved beneficiaries, optionally filtered."""
        return await self._paged(
            _BASE,
            Beneficiary,
            {
                "entity_type": entity_type,
                "name": name,
                "nick_name": nick_name,
                "company_name": company_name,
                "bank_account_number": bank_account_number,
                "from_date": from_date,
                "to_date": to_date,
                "page_num": page_num,
                "page_size": page_size,
            },
        )

    async def retrieve(self, beneficiary_id: str) -> Beneficiary:
        """Fetch a single beneficiary by id."""
        return Beneficiary.model_validate(await self._client.get(f"{_BASE}/{beneficiary_id}"))

    async def create(self, **payload: Any) -> Beneficiary:
        """Save a new beneficiary. See :meth:`Beneficiaries.create`."""
        return Beneficiary.model_validate(await self._client.post(f"{_BASE}/create", json=payload))

    async def update(self, beneficiary_id: str, **payload: Any) -> Beneficiary:
        """Update an existing beneficiary."""
        return Beneficiary.model_validate(
            await self._client.post(f"{_BASE}/update/{beneficiary_id}", json=payload)
        )

    async def delete(self, beneficiary_id: str) -> None:
        """Delete a beneficiary."""
        await self._client.post(f"{_BASE}/delete/{beneficiary_id}")

    async def validate(self, **payload: Any) -> Any:
        """Validate beneficiary details without saving them."""
        return await self._client.post(f"{_BASE}/validate", json=payload)
