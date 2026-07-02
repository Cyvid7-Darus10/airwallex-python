from __future__ import annotations

import httpx
import respx

from airwallex import Airwallex


def _page(names: list[str], has_more: bool) -> dict:
    return {
        "has_more": has_more,
        "items": [{"beneficiary_id": name} for name in names],
    }


def test_single_page_iteration(api: respx.MockRouter, client: Airwallex):
    api.get("/api/v1/beneficiaries").respond(200, json=_page(["a", "b"], has_more=False))
    page = client.beneficiaries.list()
    assert [b.beneficiary_id for b in page] == ["a", "b"]
    assert len(page) == 2
    assert page.has_more is False


def test_auto_paging_walks_all_pages(api: respx.MockRouter, client: Airwallex):
    route = api.get("/api/v1/beneficiaries").mock(
        side_effect=[
            httpx.Response(200, json=_page(["a", "b"], has_more=True)),
            httpx.Response(200, json=_page(["c"], has_more=True)),
            httpx.Response(200, json=_page([], has_more=False)),
        ]
    )
    ids = [b.beneficiary_id for b in client.beneficiaries.list(page_size=2).auto_paging_iter()]
    assert ids == ["a", "b", "c"]
    assert route.call_count == 3
    # page_num advances while other params are preserved
    assert route.calls[0].request.url.params["page_num"] == "0"
    assert route.calls[1].request.url.params["page_num"] == "1"
    assert route.calls[2].request.url.params["page_num"] == "2"
    assert route.calls[2].request.url.params["page_size"] == "2"


def test_none_params_are_omitted(api: respx.MockRouter, client: Airwallex):
    route = api.get("/api/v1/beneficiaries").respond(200, json=_page([], has_more=False))
    client.beneficiaries.list(entity_type="COMPANY")
    params = route.calls[0].request.url.params
    assert params["entity_type"] == "COMPANY"
    assert "name" not in params
    assert "page_size" not in params


async def test_async_auto_paging(api: respx.MockRouter, async_client):
    api.get("/api/v1/beneficiaries").mock(
        side_effect=[
            httpx.Response(200, json=_page(["a"], has_more=True)),
            httpx.Response(200, json=_page(["b"], has_more=False)),
        ]
    )
    page = await async_client.beneficiaries.list()
    ids = [b.beneficiary_id async for b in page.auto_paging_iter()]
    assert ids == ["a", "b"]
