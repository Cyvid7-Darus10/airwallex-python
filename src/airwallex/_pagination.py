from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Iterator
from typing import (
    Any,
    Callable,
    Generic,
    TypeVar,
)

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

_FetchPage = Callable[[int], Any]
_AsyncFetchPage = Callable[[int], Awaitable[Any]]


def _parse_items(data: Any, item_cls: type[T]) -> list[T]:
    raw_items = (data or {}).get("items") or []
    return [item_cls.model_validate(item) for item in raw_items]


class SyncPage(Generic[T]):
    """One page of results with lazy access to the following pages.

    Iterate the page itself for just its items, or call
    :meth:`auto_paging_iter` to transparently walk every page::

        page = client.beneficiaries.list()
        for beneficiary in page.auto_paging_iter():
            ...
    """

    def __init__(self, *, fetch: _FetchPage, page_num: int, data: Any, item_cls: type[T]) -> None:
        self._fetch = fetch
        self._page_num = page_num
        self._item_cls = item_cls
        self.items: list[T] = _parse_items(data, item_cls)
        self.has_more: bool = bool((data or {}).get("has_more", False))

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def next_page(self) -> SyncPage[T]:
        """Fetch the page after this one. Check :attr:`has_more` first."""
        data = self._fetch(self._page_num + 1)
        return SyncPage(
            fetch=self._fetch, page_num=self._page_num + 1, data=data, item_cls=self._item_cls
        )

    def auto_paging_iter(self) -> Iterator[T]:
        """Yield every item across this page and all following pages."""
        page: SyncPage[T] = self
        while True:
            yield from page.items
            if not page.has_more or not page.items:
                return
            page = page.next_page()


class AsyncPage(Generic[T]):
    """Async counterpart of :class:`SyncPage`.

    Use ``async for item in page.auto_paging_iter()`` to walk every page.
    """

    def __init__(
        self, *, fetch: _AsyncFetchPage, page_num: int, data: Any, item_cls: type[T]
    ) -> None:
        self._fetch = fetch
        self._page_num = page_num
        self._item_cls = item_cls
        self.items: list[T] = _parse_items(data, item_cls)
        self.has_more: bool = bool((data or {}).get("has_more", False))

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    async def next_page(self) -> AsyncPage[T]:
        """Fetch the page after this one. Check :attr:`has_more` first."""
        data = await self._fetch(self._page_num + 1)
        return AsyncPage(
            fetch=self._fetch, page_num=self._page_num + 1, data=data, item_cls=self._item_cls
        )

    async def auto_paging_iter(self) -> AsyncIterator[T]:
        """Yield every item across this page and all following pages."""
        page: AsyncPage[T] = self
        while True:
            for item in page.items:
                yield item
            if not page.has_more or not page.items:
                return
            page = await page.next_page()
