from __future__ import annotations

import uuid
from typing import Any, Optional, TypeVar

from pydantic import BaseModel

from .._client import AsyncAPIClient, SyncAPIClient
from .._models import clean_params
from .._pagination import AsyncPage, SyncPage

T = TypeVar("T", bound=BaseModel)


def ensure_request_id(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of ``payload`` with a ``request_id`` present.

    Airwallex uses ``request_id`` for idempotency: retries of the same request
    (including the SDK's automatic retries) must reuse the same id so a payout
    or conversion is never executed twice. Generating it up front makes every
    create call idempotent by default.
    """
    if payload.get("request_id"):
        return dict(payload)
    return {**payload, "request_id": str(uuid.uuid4())}


class SyncResource:
    def __init__(self, client: SyncAPIClient) -> None:
        self._client = client

    def _paged(
        self,
        path: str,
        item_cls: type[T],
        params: Optional[dict[str, Any]] = None,
    ) -> SyncPage[T]:
        query = clean_params(params or {})
        page_num = int(query.pop("page_num", 0))

        def fetch(num: int) -> Any:
            return self._client.get(path, params={**query, "page_num": num})

        return SyncPage(fetch=fetch, page_num=page_num, data=fetch(page_num), item_cls=item_cls)


class AsyncResource:
    def __init__(self, client: AsyncAPIClient) -> None:
        self._client = client

    async def _paged(
        self,
        path: str,
        item_cls: type[T],
        params: Optional[dict[str, Any]] = None,
    ) -> AsyncPage[T]:
        query = clean_params(params or {})
        page_num = int(query.pop("page_num", 0))

        async def fetch(num: int) -> Any:
            return await self._client.get(path, params={**query, "page_num": num})

        data = await fetch(page_num)
        return AsyncPage(fetch=fetch, page_num=page_num, data=data, item_cls=item_cls)
