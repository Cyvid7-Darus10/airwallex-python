from __future__ import annotations

import hashlib
import hmac
import json
import time

import pytest

from airwallex import WebhookSignatureError, webhooks

SECRET = "whsec_test_secret"


def _sign(payload: bytes, timestamp: str, secret: str = SECRET) -> str:
    return hmac.new(secret.encode(), timestamp.encode() + payload, hashlib.sha256).hexdigest()


def _event_payload() -> bytes:
    return json.dumps(
        {
            "id": "evt_1",
            "name": "transfer.settled",
            "account_id": "acct_1",
            "created_at": "2026-07-02T00:00:00+0000",
            "data": {"id": "tra_1", "status": "SETTLED"},
        }
    ).encode()


def test_valid_signature_passes_and_parses():
    payload = _event_payload()
    ts = str(int(time.time()))
    event = webhooks.construct_event(
        payload=payload, timestamp=ts, signature=_sign(payload, ts), secret=SECRET
    )
    assert event.name == "transfer.settled"
    assert event.data == {"id": "tra_1", "status": "SETTLED"}


def test_wrong_signature_rejected():
    payload = _event_payload()
    ts = str(int(time.time()))
    with pytest.raises(WebhookSignatureError, match="does not match"):
        webhooks.verify_signature(payload=payload, timestamp=ts, signature="0" * 64, secret=SECRET)


def test_wrong_secret_rejected():
    payload = _event_payload()
    ts = str(int(time.time()))
    with pytest.raises(WebhookSignatureError):
        webhooks.verify_signature(
            payload=payload,
            timestamp=ts,
            signature=_sign(payload, ts, secret="other"),
            secret=SECRET,
        )


def test_tampered_payload_rejected():
    payload = _event_payload()
    ts = str(int(time.time()))
    signature = _sign(payload, ts)
    with pytest.raises(WebhookSignatureError):
        webhooks.verify_signature(
            payload=payload + b" ", timestamp=ts, signature=signature, secret=SECRET
        )


def test_old_timestamp_rejected_as_replay():
    payload = _event_payload()
    ts = str(int(time.time()) - 3600)
    with pytest.raises(WebhookSignatureError, match="tolerance"):
        webhooks.verify_signature(
            payload=payload, timestamp=ts, signature=_sign(payload, ts), secret=SECRET
        )


def test_tolerance_none_skips_replay_check():
    payload = _event_payload()
    ts = str(int(time.time()) - 3600)
    webhooks.verify_signature(
        payload=payload,
        timestamp=ts,
        signature=_sign(payload, ts),
        secret=SECRET,
        tolerance_seconds=None,
    )


def test_millisecond_timestamps_supported():
    payload = _event_payload()
    ts = str(int(time.time() * 1000))
    webhooks.verify_signature(
        payload=payload, timestamp=ts, signature=_sign(payload, ts), secret=SECRET
    )


def test_string_payload_accepted():
    payload = _event_payload()
    ts = str(int(time.time()))
    event = webhooks.construct_event(
        payload=payload.decode(), timestamp=ts, signature=_sign(payload, ts), secret=SECRET
    )
    assert event.id == "evt_1"


def test_invalid_timestamp_header_rejected():
    with pytest.raises(WebhookSignatureError, match="x-timestamp"):
        webhooks.verify_signature(
            payload=b"{}", timestamp="not-a-number", signature="sig", secret=SECRET
        )


def test_missing_secret_rejected():
    with pytest.raises(ValueError, match="secret"):
        webhooks.verify_signature(payload=b"{}", timestamp="1", signature="sig", secret="")


def test_non_json_payload_rejected():
    payload = b"not json"
    ts = str(int(time.time()))
    with pytest.raises(WebhookSignatureError, match="JSON"):
        webhooks.construct_event(
            payload=payload, timestamp=ts, signature=_sign(payload, ts), secret=SECRET
        )
