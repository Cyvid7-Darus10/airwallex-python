from __future__ import annotations

import httpx
import pytest
import respx

from airwallex import (
    Airwallex,
    APIConnectionError,
    BadRequestError,
    NotFoundError,
    RateLimitError,
    ServerError,
)


def test_retries_on_500_then_succeeds(api: respx.MockRouter, client: Airwallex):
    route = api.get("/api/v1/balances/current").mock(
        side_effect=[
            httpx.Response(500, json={"message": "boom"}),
            httpx.Response(200, json=[{"currency": "USD", "available_amount": 5}]),
        ]
    )
    balances = client.balances.current()
    assert balances[0].available_amount == 5
    assert route.call_count == 2


def test_retries_exhausted_raises_server_error(api: respx.MockRouter, client: Airwallex):
    route = api.get("/api/v1/balances/current").respond(503, json={"message": "down"})
    with pytest.raises(ServerError):
        client.balances.current()
    assert route.call_count == 3  # initial + 2 retries (default max_retries=2)


def test_429_honours_retry_after(api: respx.MockRouter, client: Airwallex):
    route = api.get("/api/v1/balances/current").mock(
        side_effect=[
            httpx.Response(429, json={"message": "slow down"}, headers={"retry-after": "0"}),
            httpx.Response(200, json=[]),
        ]
    )
    assert client.balances.current() == []
    assert route.call_count == 2


def test_429_exhausted_raises_rate_limit_error(api: respx.MockRouter):
    with Airwallex(
        client_id="c", api_key="k", environment="demo", max_retries=0
    ) as no_retry_client:
        api.get("/api/v1/balances/current").respond(429, json={"message": "slow down"})
        with pytest.raises(RateLimitError):
            no_retry_client.balances.current()


def test_connection_errors_retry_then_raise(api: respx.MockRouter, client: Airwallex):
    route = api.get("/api/v1/balances/current").mock(side_effect=httpx.ConnectError("refused"))
    with pytest.raises(APIConnectionError, match="3 attempt"):
        client.balances.current()
    assert route.call_count == 3


def test_400_maps_to_bad_request_with_details(api: respx.MockRouter, client: Airwallex):
    api.post("/api/v1/transfers/create").respond(
        400,
        json={"code": "validation_error", "source": "transfer_amount", "message": "invalid"},
        headers={"x-request-id": "req_123"},
    )
    with pytest.raises(BadRequestError) as exc_info:
        client.transfers.create(transfer_amount=-1)
    err = exc_info.value
    assert err.code == "validation_error"
    assert err.source == "transfer_amount"
    assert err.request_id == "req_123"
    assert "400" in str(err)


def test_404_maps_to_not_found(api: respx.MockRouter, client: Airwallex):
    api.get("/api/v1/transfers/tra_missing").respond(404, json={"message": "not found"})
    with pytest.raises(NotFoundError):
        client.transfers.retrieve("tra_missing")


def test_non_json_error_body_is_tolerated(api: respx.MockRouter, client: Airwallex):
    api.get("/api/v1/balances/current").respond(502, text="<html>bad gateway</html>")
    with pytest.raises(ServerError, match="bad gateway"):
        client.balances.current()


def test_invalid_environment_rejected():
    with pytest.raises(ValueError, match="environment"):
        Airwallex(client_id="c", api_key="k", environment="staging")  # type: ignore[arg-type]


def test_default_headers_sent(api: respx.MockRouter):
    with Airwallex(
        client_id="c",
        api_key="k",
        environment="demo",
        api_version="2026-05-29",
        on_behalf_of="acct_123",
    ) as configured:
        route = api.get("/api/v1/balances/current").respond(200, json=[])
        configured.balances.current()
        request = route.calls[0].request
        assert request.headers["x-api-version"] == "2026-05-29"
        assert request.headers["x-on-behalf-of"] == "acct_123"
        assert request.headers["user-agent"].startswith("airwallex-python/")


async def test_async_retry_and_error(api: respx.MockRouter, async_client):
    route = api.get("/api/v1/balances/current").mock(
        side_effect=[
            httpx.Response(500, json={"message": "boom"}),
            httpx.Response(200, json=[]),
        ]
    )
    assert await async_client.balances.current() == []
    assert route.call_count == 2
