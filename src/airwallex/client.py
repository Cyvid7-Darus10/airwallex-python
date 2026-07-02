from __future__ import annotations

import os
from collections.abc import Mapping
from types import TracebackType
from typing import Any, Optional

import httpx

from ._client import AsyncAPIClient, SyncAPIClient, _ClientConfig
from ._constants import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT_SECONDS, Environment
from .resources import (
    Accounts,
    AsyncAccounts,
    AsyncBalances,
    AsyncBatchTransfers,
    AsyncBeneficiaries,
    AsyncConversionAmendments,
    AsyncConversions,
    AsyncCustomers,
    AsyncDeposits,
    AsyncFinancialTransactions,
    AsyncGlobalAccounts,
    AsyncIssuingAuthorizations,
    AsyncIssuingCardholders,
    AsyncIssuingCards,
    AsyncIssuingTransactions,
    AsyncPayers,
    AsyncPaymentIntents,
    AsyncQuotes,
    AsyncRates,
    AsyncReference,
    AsyncRefunds,
    AsyncSettlements,
    AsyncSimulation,
    AsyncTransfers,
    AsyncWalletTransfers,
    AsyncWebhookEndpoints,
    Balances,
    BatchTransfers,
    Beneficiaries,
    ConversionAmendments,
    Conversions,
    Customers,
    Deposits,
    FinancialTransactions,
    GlobalAccounts,
    IssuingAuthorizations,
    IssuingCardholders,
    IssuingCards,
    IssuingTransactions,
    Payers,
    PaymentIntents,
    Quotes,
    Rates,
    Reference,
    Refunds,
    Settlements,
    Simulation,
    Transfers,
    WalletTransfers,
    WebhookEndpoints,
)

__all__ = ["Airwallex", "AsyncAirwallex"]


def _resolve_credential(value: Optional[str], env_var: str) -> str:
    resolved = value if value is not None else os.environ.get(env_var, "")
    if not resolved:
        raise ValueError(
            f"Missing credential: pass it to the client or set the {env_var} environment variable."
        )
    return resolved


class Airwallex:
    """Synchronous Airwallex API client.

    Example::

        from airwallex import Airwallex

        client = Airwallex(environment="demo")  # reads AIRWALLEX_CLIENT_ID / AIRWALLEX_API_KEY
        for balance in client.balances.current():
            print(balance.currency, balance.available_amount)

    Authentication happens lazily on the first request and the bearer token is
    refreshed automatically before it expires.

    Args:
        client_id: Airwallex client id (default: ``AIRWALLEX_CLIENT_ID`` env var).
        api_key: Airwallex API key (default: ``AIRWALLEX_API_KEY`` env var).
        environment: ``"production"`` or ``"demo"`` (sandbox).
        base_url: Override the API host entirely (advanced; wins over environment).
        api_version: Pin an ``x-api-version`` (e.g. ``"2026-05-29"``) instead of
            your account's default version.
        on_behalf_of: Act on a connected account (sets ``x-on-behalf-of``).
        timeout: Per-request timeout in seconds.
        max_retries: Automatic retries for transient failures (429/5xx/network).
        http_client: Bring your own ``httpx.Client`` (proxies, custom TLS, ...).
    """

    def __init__(
        self,
        *,
        client_id: Optional[str] = None,
        api_key: Optional[str] = None,
        environment: Environment = "production",
        base_url: Optional[str] = None,
        api_version: Optional[str] = None,
        on_behalf_of: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        config = _ClientConfig(
            client_id=_resolve_credential(client_id, "AIRWALLEX_CLIENT_ID"),
            api_key=_resolve_credential(api_key, "AIRWALLEX_API_KEY"),
            environment=environment,
            base_url=base_url,
            api_version=api_version,
            on_behalf_of=on_behalf_of,
            timeout=timeout,
            max_retries=max_retries,
        )
        self._api = SyncAPIClient(config, http=http_client)

        self.accounts = Accounts(self._api)
        self.balances = Balances(self._api)
        self.batch_transfers = BatchTransfers(self._api)
        self.beneficiaries = Beneficiaries(self._api)
        self.conversion_amendments = ConversionAmendments(self._api)
        self.conversions = Conversions(self._api)
        self.customers = Customers(self._api)
        self.deposits = Deposits(self._api)
        self.financial_transactions = FinancialTransactions(self._api)
        self.fx_quotes = Quotes(self._api)
        self.global_accounts = GlobalAccounts(self._api)
        self.issuing_authorizations = IssuingAuthorizations(self._api)
        self.issuing_cardholders = IssuingCardholders(self._api)
        self.issuing_cards = IssuingCards(self._api)
        self.issuing_transactions = IssuingTransactions(self._api)
        self.payers = Payers(self._api)
        self.payment_intents = PaymentIntents(self._api)
        self.rates = Rates(self._api)
        self.reference = Reference(self._api)
        self.refunds = Refunds(self._api)
        self.settlements = Settlements(self._api)
        self.simulation = Simulation(self._api)
        self.transfers = Transfers(self._api)
        self.wallet_transfers = WalletTransfers(self._api)
        self.webhook_endpoints = WebhookEndpoints(self._api)

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        """Call any Airwallex endpoint, including ones this SDK has no wrapper for.

        Authentication, retries, and error mapping still apply::

            cards = client.request("GET", "/api/v1/issuing/cards", params={"card_status": "ACTIVE"})
        """
        return self._api.request(method, path, params=params, json=json, headers=headers)

    def close(self) -> None:
        """Release the underlying HTTP connection pool."""
        self._api.close()

    def __enter__(self) -> Airwallex:
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        self.close()


class AsyncAirwallex:
    """Asynchronous Airwallex API client.

    Example::

        from airwallex import AsyncAirwallex

        async with AsyncAirwallex(environment="demo") as client:
            balances = await client.balances.current()

    See :class:`Airwallex` for the full list of constructor arguments.
    """

    def __init__(
        self,
        *,
        client_id: Optional[str] = None,
        api_key: Optional[str] = None,
        environment: Environment = "production",
        base_url: Optional[str] = None,
        api_version: Optional[str] = None,
        on_behalf_of: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        config = _ClientConfig(
            client_id=_resolve_credential(client_id, "AIRWALLEX_CLIENT_ID"),
            api_key=_resolve_credential(api_key, "AIRWALLEX_API_KEY"),
            environment=environment,
            base_url=base_url,
            api_version=api_version,
            on_behalf_of=on_behalf_of,
            timeout=timeout,
            max_retries=max_retries,
        )
        self._api = AsyncAPIClient(config, http=http_client)

        self.accounts = AsyncAccounts(self._api)
        self.balances = AsyncBalances(self._api)
        self.batch_transfers = AsyncBatchTransfers(self._api)
        self.beneficiaries = AsyncBeneficiaries(self._api)
        self.conversion_amendments = AsyncConversionAmendments(self._api)
        self.conversions = AsyncConversions(self._api)
        self.customers = AsyncCustomers(self._api)
        self.deposits = AsyncDeposits(self._api)
        self.financial_transactions = AsyncFinancialTransactions(self._api)
        self.fx_quotes = AsyncQuotes(self._api)
        self.global_accounts = AsyncGlobalAccounts(self._api)
        self.issuing_authorizations = AsyncIssuingAuthorizations(self._api)
        self.issuing_cardholders = AsyncIssuingCardholders(self._api)
        self.issuing_cards = AsyncIssuingCards(self._api)
        self.issuing_transactions = AsyncIssuingTransactions(self._api)
        self.payers = AsyncPayers(self._api)
        self.payment_intents = AsyncPaymentIntents(self._api)
        self.rates = AsyncRates(self._api)
        self.reference = AsyncReference(self._api)
        self.refunds = AsyncRefunds(self._api)
        self.settlements = AsyncSettlements(self._api)
        self.simulation = AsyncSimulation(self._api)
        self.transfers = AsyncTransfers(self._api)
        self.wallet_transfers = AsyncWalletTransfers(self._api)
        self.webhook_endpoints = AsyncWebhookEndpoints(self._api)

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        """Call any Airwallex endpoint. See :meth:`Airwallex.request`."""
        return await self._api.request(method, path, params=params, json=json, headers=headers)

    async def close(self) -> None:
        """Release the underlying HTTP connection pool."""
        await self._api.close()

    async def __aenter__(self) -> AsyncAirwallex:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        await self.close()
