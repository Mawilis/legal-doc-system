"""Direct certificate for the Python-to-Node recovery delivery adapter.

TITLE: Node Password Recovery Delivery Adapter Direct Unit Certificate
VERSION: v1.0.0-R10E7-NODE-RECOVERY-DELIVERY-ADAPTER-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies exact cross-runtime JSON/HMAC transport without network,
         SMTP, recovery issuance, or tenant authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_recovery_delivery.py
COLLABORATION / OWNERSHIP: Test-only evidence for the R10E7 adapter; the Node
                           route and SMTP transport are separately certified.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10E7-NODE-RECOVERY-DELIVERY-ADAPTER-CERT — Adds exact endpoint, payload,
    SHA3-512 HMAC, timestamp, timeout, 204-only success, failure mapping,
    configuration, secret-retention boundary, and no-tenant-transfer evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic bearer/shared secret only; no network.
TENANT BOUNDARY: Delivery JSON explicitly excludes tenant identity.
AUTHORITY BOUNDARY: Transport adapter evidence only; no recovery grant.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusively financial.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Any
from urllib import error as urllib_error

import pytest

from tools.eos.saas.auth.password_recovery_delivery import (
    INTERNAL_DELIVERY_PATH,
    NodePasswordRecoveryDelivery,
    PasswordRecoveryDeliveryCode,
    PasswordRecoveryDeliveryError,
    SIGNATURE_HEADER,
    TIMESTAMP_HEADER,
)


NOW = datetime(2026, 9, 22, 17, 30, 0, tzinfo=timezone.utc)
EXPIRY = datetime(2026, 9, 22, 18, 0, 0, tzinfo=timezone.utc)
SECRET = "synthetic-recovery-delivery-secret-0123456789"
TOKEN = "synthetic-recovery-token-0123456789-ABCDE"


class _Response:
    def __init__(self, status: int) -> None:
        self.status = status
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_exact_signed_request_and_204_success() -> None:
    calls: list[dict[str, Any]] = []
    response = _Response(204)

    def opener(request: Any, *, timeout: float) -> _Response:
        calls.append({"request": request, "timeout": timeout})
        return response

    adapter = NodePasswordRecoveryDelivery(
        base_url="https://node.internal.example",
        shared_secret=SECRET,
        timeout_seconds=7,
        opener=opener,
        clock=lambda: NOW,
    )
    adapter.deliver_password_recovery(
        recipient_email=" Person@Example.COM ",
        recovery_token=TOKEN,
        expires_at=EXPIRY,
    )

    assert len(calls) == 1
    request = calls[0]["request"]
    assert request.full_url == "https://node.internal.example" + INTERNAL_DELIVERY_PATH
    assert request.get_method() == "POST"
    assert calls[0]["timeout"] == 7.0
    body = json.loads(request.data.decode("utf-8"))
    assert body == {
        "recipient_email": "person@example.com",
        "recovery_token": TOKEN,
        "expires_at": "2026-09-22T18:00:00Z",
    }
    assert "tenant_id" not in body and "principal_id" not in body
    timestamp = request.headers[TIMESTAMP_HEADER]
    assert timestamp == str(int(NOW.timestamp()))
    payload = "\n".join(
        (timestamp, body["recipient_email"], body["recovery_token"], body["expires_at"])
    ).encode("utf-8")
    expected = hmac.new(SECRET.encode("utf-8"), payload, hashlib.sha3_512).hexdigest()
    assert request.headers[SIGNATURE_HEADER] == expected
    assert response.closed is True
    assert TOKEN not in repr(adapter.__dict__)
    assert "person@example.com" not in repr(adapter.__dict__)


@pytest.mark.parametrize(
    "environment",
    [
        {},
        {"WILSY_NODE_INTERNAL_URL": "https://node.internal.example"},
        {"WILSY_RECOVERY_DELIVERY_SECRET": SECRET},
        {
            "WILSY_NODE_INTERNAL_URL": "http://user:pass@node.internal.example/path",
            "WILSY_RECOVERY_DELIVERY_SECRET": SECRET,
        },
    ],
)
def test_missing_or_untrusted_configuration_fails_closed(environment: dict[str, str]) -> None:
    with pytest.raises(PasswordRecoveryDeliveryError) as error:
        NodePasswordRecoveryDelivery(environment=environment)
    assert error.value.code is PasswordRecoveryDeliveryCode.CONFIGURATION_INVALID
    assert SECRET not in str(error.value)


@pytest.mark.parametrize(
    ("email", "token", "expiry"),
    [
        ("invalid", TOKEN, EXPIRY),
        ("person@example.com", "short", EXPIRY),
        ("person@example.com", TOKEN, datetime(2026, 9, 22, 18, 0, 0)),
    ],
)
def test_invalid_delivery_input_fails_before_http(
    email: str, token: str, expiry: datetime
) -> None:
    calls = 0

    def opener(*_args: Any, **_kwargs: Any) -> _Response:
        nonlocal calls
        calls += 1
        return _Response(204)

    adapter = NodePasswordRecoveryDelivery(
        base_url="https://node.internal.example",
        shared_secret=SECRET,
        opener=opener,
        clock=lambda: NOW,
    )
    with pytest.raises(PasswordRecoveryDeliveryError) as error:
        adapter.deliver_password_recovery(
            recipient_email=email, recovery_token=token, expires_at=expiry
        )
    assert error.value.code is PasswordRecoveryDeliveryCode.REQUEST_INVALID
    assert calls == 0


def test_non_204_response_is_unconfirmed_and_response_is_closed() -> None:
    response = _Response(200)
    adapter = NodePasswordRecoveryDelivery(
        base_url="https://node.internal.example",
        shared_secret=SECRET,
        opener=lambda *_args, **_kwargs: response,
        clock=lambda: NOW,
    )
    with pytest.raises(PasswordRecoveryDeliveryError) as error:
        adapter.deliver_password_recovery(
            recipient_email="person@example.com", recovery_token=TOKEN, expires_at=EXPIRY
        )
    assert error.value.code is PasswordRecoveryDeliveryCode.DELIVERY_UNCONFIRMED
    assert response.closed is True


def test_network_failure_maps_code_only_without_secret_leakage() -> None:
    def opener(*_args: Any, **_kwargs: Any) -> _Response:
        raise urllib_error.URLError("provider details person@example.com " + TOKEN)

    adapter = NodePasswordRecoveryDelivery(
        base_url="https://node.internal.example",
        shared_secret=SECRET,
        opener=opener,
        clock=lambda: NOW,
    )
    with pytest.raises(PasswordRecoveryDeliveryError) as error:
        adapter.deliver_password_recovery(
            recipient_email="person@example.com", recovery_token=TOKEN, expires_at=EXPIRY
        )
    assert error.value.code is PasswordRecoveryDeliveryCode.TRANSPORT_FAILED
    assert TOKEN not in str(error.value)
    assert "person@example.com" not in str(error.value)
    assert SECRET not in str(error.value)


def test_adapter_retains_only_transport_configuration() -> None:
    adapter = NodePasswordRecoveryDelivery(
        base_url="https://node.internal.example",
        shared_secret=SECRET,
        opener=lambda *_args, **_kwargs: _Response(204),
        clock=lambda: NOW,
    )
    assert set(adapter.__dict__) == {
        "_base_url", "_shared_secret", "_timeout_seconds", "_opener", "_clock"
    }
    assert not any(
        key in adapter.__dict__ for key in ("recipient_email", "recovery_token", "expires_at")
    )


# ARTIFACT: tests/unit/test_password_recovery_delivery.py
# VERSION: v1.0.0-R10E7-NODE-RECOVERY-DELIVERY-ADAPTER-CERT
# AUTHORITY BOUNDARY: exact Python-to-Node recovery delivery transport evidence only
# TENANT POSTURE: no tenant or principal field crosses the adapter boundary
# FAIL-CLOSED POSTURE: invalid config/input/network/status returns code-only failure
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
