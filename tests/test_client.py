from __future__ import annotations

import datetime

import httpx
import pytest
import respx

from airwallex import (
    Airwallex,
    APIConnectionError,
    APIError,
    BadRequestError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    ServerError,
)
from airwallex._client import _retry_delay


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


def test_409_raises_conflict_without_retry(api: respx.MockRouter, client: Airwallex):
    route = api.post("/api/v1/transfers/create").respond(
        409, json={"code": "duplicate_request", "message": "request_id already used"}
    )
    with pytest.raises(ConflictError):
        client.transfers.create(beneficiary_id="ben_1")
    assert route.call_count == 1  # business conflicts must never be retried


def test_retry_after_http_date_parsed():
    from email.utils import format_datetime

    request = httpx.Request("GET", "https://api-demo.airwallex.com/x")
    retry_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=2)
    response = httpx.Response(
        429, headers={"retry-after": format_datetime(retry_at)}, request=request
    )
    delay = _retry_delay(0, response)
    assert 0.0 <= delay <= 2.5

    bad = httpx.Response(429, headers={"retry-after": "not-a-date"}, request=request)
    assert 0.0 <= _retry_delay(0, bad) <= 0.5  # falls back to jittered backoff


def test_unparseable_success_body_raises_api_error(api: respx.MockRouter, client: Airwallex):
    api.get("/api/v1/balances/current").respond(
        200, text="<html>proxy page</html>", headers={"content-type": "text/html"}
    )
    with pytest.raises(APIError, match="unparseable"):
        client.balances.current()


def test_credentials_redacted_in_reprs(client: Airwallex):
    config_repr = repr(client._api._config)
    state_repr = repr(client._api._token_manager._state)
    for text in (config_repr, state_repr):
        assert "key_test" not in text
        assert "[REDACTED]" in text


def test_http_base_url_rejected_except_localhost():
    with pytest.raises(ValueError, match="https"):
        Airwallex(client_id="c", api_key="k", base_url="http://evil-proxy.example.com")
    # loopback mocks are allowed
    with Airwallex(client_id="c", api_key="k", base_url="http://localhost:8080") as local:
        assert local._api._config.base_url == "http://localhost:8080"


def test_error_request_has_redacted_authorization(api: respx.MockRouter, client: Airwallex):
    api.get("/api/v1/transfers/tra_x").respond(404, json={"message": "not found"})
    with pytest.raises(NotFoundError) as exc_info:
        client.transfers.retrieve("tra_x")
    err = exc_info.value
    assert err.request is not None
    assert err.request.headers["authorization"] == "[REDACTED]"
    assert err.response.request.headers["authorization"] == "[REDACTED]"


def test_config_and_state_pickle_safe(client: Airwallex):
    import pickle

    dumped = pickle.dumps(client._api._config)
    assert b"key_test" not in dumped
    state = client._api._token_manager._state.__getstate__()
    assert state["api_key"] == "[REDACTED]"


def test_custom_http_client_gets_base_url_and_headers(api: respx.MockRouter):
    own_http = httpx.Client()
    client = Airwallex(
        client_id="c",
        api_key="k",
        environment="demo",
        on_behalf_of="acct_777",
        http_client=own_http,
    )
    route = api.get("/api/v1/balances/current").respond(200, json=[])
    client.balances.current()
    request = route.calls[0].request
    assert request.url.host == "api-demo.airwallex.com"
    assert request.headers["x-on-behalf-of"] == "acct_777"
    assert request.headers["user-agent"].startswith("airwallex-python/")
    client.close()
    assert not own_http.is_closed  # SDK must not close a client it doesn't own
    own_http.close()


def test_list_accepts_extra_query_params(api: respx.MockRouter, client: Airwallex):
    route = api.get("/api/v1/transfers").respond(200, json={"has_more": False, "items": []})
    client.transfers.list(status="PAID", short_reference_id="REF123")
    params = route.calls[0].request.url.params
    assert params["short_reference_id"] == "REF123"
    assert params["status"] == "PAID"
