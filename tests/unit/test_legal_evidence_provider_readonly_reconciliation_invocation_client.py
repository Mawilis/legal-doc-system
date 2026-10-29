"""Adversarial tests for the Python-only signed reconciliation caller."""

from __future__ import annotations

import hashlib
import json

import pytest

from tools.eos.auth.internal_service_trust import verify_internal_service_request
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_invocation_client import (
    RECONCILIATION_PATH,
    ReconciliationInvocationClientError,
    build_signed_invocation,
    invoke_legal_evidence_reconciliation,
)

SERVICE = "synthetic-reconciliation-caller"
AUDIENCE = "synthetic-reconciliation-audience"
KEY_ID = "synthetic-key-1"
SECRET = "synthetic-only-secret"
OPERATION = "reconciliation-test-20261025"
NONCE = "0123456789abcdef0123456789abcdef"
CORRELATION = "corr-reconciliation-test-1"


class _ReplayStore:
    def __init__(self) -> None:
        self.seen: set[tuple[str, str, str]] = set()

    def consume_once(self, *, service_id: str, key_id: str, nonce: str, expires_at: int) -> bool:
        identity = (service_id, key_id, nonce)
        if identity in self.seen:
            return False
        self.seen.add(identity)
        return True


def _canonical_request(body: bytes, headers: dict[str, str]) -> dict[str, str]:
    return {
        "version": headers["X-Wilsy-Auth-Version"],
        "service_id": headers["X-Wilsy-Service-ID"],
        "audience": headers["X-Wilsy-Audience"],
        "key_id": headers["X-Wilsy-Key-ID"],
        "timestamp": headers["X-Wilsy-Timestamp"],
        "nonce": headers["X-Wilsy-Nonce"],
        "body_sha3_512": headers["X-Wilsy-Body-Sha3-512"],
        "correlation_id": headers["X-Wilsy-Correlation-ID"],
        "signature": headers["X-Wilsy-Signature"],
        "method": "POST",
        "path": RECONCILIATION_PATH,
    }


def test_caller_signature_verifies_with_canonical_eos_verifier() -> None:
    body, headers, correlation = build_signed_invocation(
        service_id=SERVICE,
        audience=AUDIENCE,
        key_id=KEY_ID,
        secret=SECRET,
        idempotency_key=OPERATION,
        now=1_700_000_000,
        nonce=NONCE,
        correlation_id=CORRELATION,
    )

    assert body == b'{"idempotency_key":"reconciliation-test-20261025"}'
    assert hashlib.sha3_512(body).hexdigest() == headers["X-Wilsy-Body-Sha3-512"]
    assert correlation == CORRELATION
    assert headers["X-Wilsy-Auth-Version"] == "v1"
    assert headers["X-Wilsy-Nonce"] == NONCE

    result = verify_internal_service_request(
        request=_canonical_request(body, headers),
        body=body,
        keys={KEY_ID: (SERVICE, SECRET)},
        replay_store=_ReplayStore(),
        now=1_700_000_000,
    )
    assert result.service_id == SERVICE
    assert result.audience == AUDIENCE
    assert result.key_id == KEY_ID
    assert result.correlation_id == CORRELATION


def test_operation_identity_is_only_the_exact_idempotency_key() -> None:
    body, _, _ = build_signed_invocation(
        service_id=SERVICE,
        audience=AUDIENCE,
        key_id=KEY_ID,
        secret=SECRET,
        idempotency_key=OPERATION,
        now=1_700_000_000,
        nonce=NONCE,
        correlation_id=CORRELATION,
    )
    assert json.loads(body) == {"idempotency_key": OPERATION}


@pytest.mark.parametrize(
    "value",
    ["", "contains space", "wildcard*", "../path", "x" * 161, 42, None],
)
def test_caller_rejects_invalid_operation_idempotency_keys(value: object) -> None:
    with pytest.raises(ReconciliationInvocationClientError, match="OPERATION_IDEMPOTENCY_KEY_INVALID"):
        build_signed_invocation(
            service_id=SERVICE,
            audience=AUDIENCE,
            key_id=KEY_ID,
            secret=SECRET,
            idempotency_key=value,  # type: ignore[arg-type]
            now=1_700_000_000,
            nonce=NONCE,
            correlation_id=CORRELATION,
        )


def test_caller_rejects_newlines_and_invalid_nonce() -> None:
    with pytest.raises(ReconciliationInvocationClientError, match="WORKLOAD_SERVICE_ID_REQUIRED"):
        build_signed_invocation(
            service_id="service\nforged",
            audience=AUDIENCE,
            key_id=KEY_ID,
            secret=SECRET,
            idempotency_key=OPERATION,
        )

    with pytest.raises(ReconciliationInvocationClientError, match="WORKLOAD_NONCE_INVALID"):
        build_signed_invocation(
            service_id=SERVICE,
            audience=AUDIENCE,
            key_id=KEY_ID,
            secret=SECRET,
            idempotency_key=OPERATION,
            nonce="not-a-nonce",
        )


@pytest.mark.parametrize(
    "endpoint",
    [
        "http://eos.example.test",
        "https://user:password@eos.example.test",
        "https://eos.example.test/unapproved/path",
        "https://eos.example.test?override=1",
        "https://eos.example.test#fragment",
    ],
)
def test_invocation_rejects_noncanonical_endpoint_before_network_io(endpoint: str) -> None:
    with pytest.raises(ReconciliationInvocationClientError, match="RECONCILIATION_ENDPOINT_MUST_BE_HTTPS_ORIGIN"):
        invoke_legal_evidence_reconciliation(
            endpoint=endpoint,
            service_id=SERVICE,
            audience=AUDIENCE,
            key_id=KEY_ID,
            secret=SECRET,
            idempotency_key=OPERATION,
        )


def test_invocation_rejects_invalid_timeout_before_network_io() -> None:
    with pytest.raises(ReconciliationInvocationClientError, match="RECONCILIATION_TIMEOUT_INVALID"):
        invoke_legal_evidence_reconciliation(
            endpoint="https://eos.example.test",
            service_id=SERVICE,
            audience=AUDIENCE,
            key_id=KEY_ID,
            secret=SECRET,
            idempotency_key=OPERATION,
            timeout_seconds=0,
        )
