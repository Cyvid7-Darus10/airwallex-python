from __future__ import annotations

from typing import Any, Optional

from .._pagination import AsyncPage, SyncPage
from ..types.conversion_amendment import ConversionAmendment, ConversionAmendmentQuote
from ._base import AsyncResource, SyncResource, ensure_request_id, pid

_BASE = "/api/v1/conversion_amendments"


class ConversionAmendments(SyncResource):
    """Amendments (e.g. cancellations) to existing FX conversions."""

    def list(
        self,
        *,
        conversion_id: str,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> SyncPage[ConversionAmendment]:
        """List the amendments applied to a conversion."""
        return self._paged(
            _BASE,
            ConversionAmendment,
            {
                "conversion_id": conversion_id,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    def retrieve(self, conversion_amendment_id: str) -> ConversionAmendment:
        """Fetch a single conversion amendment by id."""
        return ConversionAmendment.model_validate(
            self._client.get(f"{_BASE}/{pid(conversion_amendment_id)}")
        )

    def create(self, **payload: Any) -> ConversionAmendment:
        """Execute a conversion amendment (e.g. cancel a conversion).

        A ``request_id`` is generated automatically when not supplied, making
        the call idempotent — Airwallex will never execute the same
        ``request_id`` twice, even across the SDK's automatic retries.

        Example::

            client.conversion_amendments.create(
                conversion_id="con_123", type="CANCELLATION"
            )
        """
        body = ensure_request_id(payload)
        return ConversionAmendment.model_validate(self._client.post(f"{_BASE}/create", json=body))

    def quote(self, **payload: Any) -> ConversionAmendmentQuote:
        """Quote the charges of an amendment without executing it.

        Takes the same payload as :meth:`create`; a ``request_id`` is
        generated automatically when not supplied.
        """
        body = ensure_request_id(payload)
        return ConversionAmendmentQuote.model_validate(
            self._client.post(f"{_BASE}/quote", json=body)
        )


class AsyncConversionAmendments(AsyncResource):
    """Async counterpart of :class:`ConversionAmendments`."""

    async def list(
        self,
        *,
        conversion_id: str,
        page_num: int = 0,
        page_size: Optional[int] = None,
        **extra_params: Any,
    ) -> AsyncPage[ConversionAmendment]:
        """List the amendments applied to a conversion."""
        return await self._paged(
            _BASE,
            ConversionAmendment,
            {
                "conversion_id": conversion_id,
                "page_num": page_num,
                "page_size": page_size,
                **extra_params,
            },
        )

    async def retrieve(self, conversion_amendment_id: str) -> ConversionAmendment:
        """Fetch a single conversion amendment by id."""
        return ConversionAmendment.model_validate(
            await self._client.get(f"{_BASE}/{pid(conversion_amendment_id)}")
        )

    async def create(self, **payload: Any) -> ConversionAmendment:
        """Execute a conversion amendment. See :meth:`ConversionAmendments.create`."""
        body = ensure_request_id(payload)
        return ConversionAmendment.model_validate(
            await self._client.post(f"{_BASE}/create", json=body)
        )

    async def quote(self, **payload: Any) -> ConversionAmendmentQuote:
        """Quote the charges of an amendment without executing it."""
        body = ensure_request_id(payload)
        return ConversionAmendmentQuote.model_validate(
            await self._client.post(f"{_BASE}/quote", json=body)
        )
