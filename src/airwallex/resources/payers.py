from __future__ import annotations

from typing import Any, Optional

from .._pagination import AsyncPage, SyncPage
from ..types.payer import Payer
from ._base import AsyncResource, SyncResource, pid

_BASE = "/api/v1/payers"


class Payers(SyncResource):
    """Saved payment senders used when creating transfers on behalf of a payer."""

    def list(
        self,
        *,
        entity_type: Optional[str] = None,
        name: Optional[str] = None,
        nick_name: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> SyncPage[Payer]:
        """List saved payers, optionally filtered."""
        return self._paged(
            _BASE,
            Payer,
            {
                "entity_type": entity_type,
                "name": name,
                "nick_name": nick_name,
                "from_date": from_date,
                "to_date": to_date,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    def retrieve(self, payer_id: str) -> Payer:
        """Fetch a single payer by id."""
        return Payer.model_validate(self._client.get(f"{_BASE}/{pid(payer_id)}"))

    def create(self, **payload: Any) -> Payer:
        """Save a new payer.

        Pass the payload documented by Airwallex, e.g. ``payer={...}``,
        ``nickname=...``. Use :meth:`validate` first to check the details.
        """
        return Payer.model_validate(self._client.post(f"{_BASE}/create", json=payload))

    def update(self, payer_id: str, **payload: Any) -> Payer:
        """Update an existing payer."""
        return Payer.model_validate(
            self._client.post(f"{_BASE}/update/{pid(payer_id)}", json=payload)
        )

    def delete(self, payer_id: str) -> None:
        """Delete a payer."""
        self._client.post(f"{_BASE}/delete/{pid(payer_id)}")

    def validate(self, **payload: Any) -> Any:
        """Validate payer details without saving them.

        Returns the raw validation result.
        """
        return self._client.post(f"{_BASE}/validate", json=payload)


class AsyncPayers(AsyncResource):
    """Async counterpart of :class:`Payers`."""

    async def list(
        self,
        *,
        entity_type: Optional[str] = None,
        name: Optional[str] = None,
        nick_name: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> AsyncPage[Payer]:
        """List saved payers, optionally filtered."""
        return await self._paged(
            _BASE,
            Payer,
            {
                "entity_type": entity_type,
                "name": name,
                "nick_name": nick_name,
                "from_date": from_date,
                "to_date": to_date,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    async def retrieve(self, payer_id: str) -> Payer:
        """Fetch a single payer by id."""
        return Payer.model_validate(await self._client.get(f"{_BASE}/{pid(payer_id)}"))

    async def create(self, **payload: Any) -> Payer:
        """Save a new payer. See :meth:`Payers.create`."""
        return Payer.model_validate(await self._client.post(f"{_BASE}/create", json=payload))

    async def update(self, payer_id: str, **payload: Any) -> Payer:
        """Update an existing payer."""
        return Payer.model_validate(
            await self._client.post(f"{_BASE}/update/{pid(payer_id)}", json=payload)
        )

    async def delete(self, payer_id: str) -> None:
        """Delete a payer."""
        await self._client.post(f"{_BASE}/delete/{pid(payer_id)}")

    async def validate(self, **payload: Any) -> Any:
        """Validate payer details without saving them."""
        return await self._client.post(f"{_BASE}/validate", json=payload)
