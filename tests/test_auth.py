from __future__ import annotations

import httpx
import pytest
import respx

from airwallex import Airwallex, AuthenticationError
from airwallex._auth import _parse_expires_at

from .conftest import TOKEN_RESPONSE


def test_login_happens_once_and_token_is_reused(api: respx.MockRouter, client: Airwallex):
    login = api["login"]
    balances = api.get("/api/v1/balances/current").respond(200, json=[])

    client.balances.current()
    client.balances.current()

    assert login.call_count == 1
    assert balances.call_count == 2
    auth_header = balances.calls[0].request.headers["authorization"]
    assert auth_header == "Bearer tok_test"


def test_login_sends_credential_headers(api: respx.MockRouter, client: Airwallex):
    api.get("/api/v1/balances/current").respond(200, json=[])
    client.balances.current()

    login_request = api["login"].calls[0].request
    assert login_request.headers["x-client-id"] == "cid_test"
    assert login_request.headers["x-api-key"] == "key_test"


def test_401_triggers_single_relogin(api: respx.MockRouter, client: Airwallex):
    login = api["login"]
    api.get("/api/v1/balances/current").mock(
        side_effect=[
            httpx.Response(401, json={"code": "unauthorized", "message": "expired"}),
            httpx.Response(200, json=[]),
        ]
    )

    assert client.balances.current() == []
    assert login.call_count == 2


def test_persistent_401_raises_authentication_error(api: respx.MockRouter, client: Airwallex):
    api.get("/api/v1/balances/current").respond(
        401, json={"code": "unauthorized", "message": "bad key"}
    )
    with pytest.raises(AuthenticationError) as exc_info:
        client.balances.current()
    assert exc_info.value.code == "unauthorized"


def test_failed_login_raises(api: respx.MockRouter, client: Airwallex):
    api["login"].respond(401, json={"code": "invalid_api_key", "message": "nope"})
    with pytest.raises(AuthenticationError):
        client.balances.current()


def test_missing_credentials_rejected():
    with pytest.raises(ValueError, match="AIRWALLEX_CLIENT_ID"):
        Airwallex(client_id=None, api_key="k", environment="demo")


async def test_async_login_and_request(api: respx.MockRouter, async_client):
    api.get("/api/v1/balances/current").respond(200, json=[{"currency": "USD"}])
    balances = await async_client.balances.current()
    assert balances[0].currency == "USD"
    assert api["login"].call_count == 1


def test_parse_expires_at_formats():
    assert _parse_expires_at("2099-01-01T00:00:00+0000") > 4e9
    assert _parse_expires_at("2099-01-01T00:00:00Z") > 4e9
    # unparseable input falls back to a ~30 minute TTL instead of crashing
    import time

    fallback = _parse_expires_at("garbage")
    assert time.time() + 25 * 60 < fallback < time.time() + 35 * 60
    assert TOKEN_RESPONSE["token"]  # keep fixture import meaningful


def test_login_5xx_is_retried(api: respx.MockRouter, client: Airwallex):
    api["login"].mock(
        side_effect=[
            httpx.Response(503, json={"message": "auth outage"}),
            httpx.Response(201, json=TOKEN_RESPONSE),
        ]
    )
    api.get("/api/v1/balances/current").respond(200, json=[])
    assert client.balances.current() == []
    assert api["login"].call_count == 2


def test_login_non_json_body_raises_authentication_error(api: respx.MockRouter, client: Airwallex):
    api["login"].mock(return_value=httpx.Response(201, text="<html>maintenance</html>"))
    with pytest.raises(AuthenticationError, match="unparseable"):
        client.balances.current()
