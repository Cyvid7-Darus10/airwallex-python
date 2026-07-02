from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

import pytest
import respx

from airwallex import Airwallex, AsyncAirwallex

BASE_URL = "https://api-demo.airwallex.com"
LOGIN_URL = f"{BASE_URL}/api/v1/authentication/login"

TOKEN_RESPONSE = {"token": "tok_test", "expires_at": "2099-01-01T00:00:00+0000"}


@pytest.fixture
def api() -> Iterator[respx.MockRouter]:
    """A respx router with the login endpoint pre-mocked."""
    with respx.mock(base_url=BASE_URL, assert_all_called=False) as router:
        router.post("/api/v1/authentication/login", name="login").respond(201, json=TOKEN_RESPONSE)
        yield router


@pytest.fixture
def client(api: respx.MockRouter) -> Iterator[Airwallex]:
    with Airwallex(client_id="cid_test", api_key="key_test", environment="demo") as c:
        yield c


@pytest.fixture
async def async_client(api: respx.MockRouter) -> AsyncIterator[AsyncAirwallex]:
    async with AsyncAirwallex(client_id="cid_test", api_key="key_test", environment="demo") as c:
        yield c
