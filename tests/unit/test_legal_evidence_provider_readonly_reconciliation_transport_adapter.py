"""Adversarial tests for the raw-ASGI signed-workload request adapter."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import pytest

from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_transport_adapter import (
    LegalEvidenceProviderReadOnlyReconciliationTransportError,
    extract_signed_workload_request,
)


BODY = b'{"opaque":"exact bytes"}'
HEADERS = [
    (b"x-wilsy-auth-version", b"v1"),
    (b"x-wilsy-service-id", b"internal-eos"),
    (b"x-wilsy-audience", b"legal-reconciliation"),
    (b"x-wilsy-key-id", b"key-1"),
    (b"x-wilsy-timestamp", b"1792920000"),
    (b"x-wilsy-nonce", b"0123456789abcdef0123456789abcdef"),
    (b"x-wilsy-body-sha3-512", b"0" * 128),
    (b"x-wilsy-correlation-id", b"corr-20261025-001"),
    (b"x-wilsy-signature", b"0" * 64),
]


class _FakeASGIRequest:
    def __init__(self, scope, body: bytes) -> None:
        self.scope = scope
        self._body = body

    async def body(self) -> bytes:
        return self._body


def _request(*, headers=None, body: bytes = BODY, method: str = "POST",
             raw_path: bytes = b"/internal/reconciliation", query: bytes = b"batch=1"):
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": raw_path.decode("ascii", errors="replace"),
        "raw_path": raw_path,
        "query_string": query,
        "root_path": "",
        "headers": list(HEADERS if headers is None else headers),
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }
    return _FakeASGIRequest(scope, body)


def _extract(request):
    fixed = datetime(2026, 10, 25, 9, 30, tzinfo=timezone.utc)
    return asyncio.run(extract_signed_workload_request(request, clock=lambda: fixed))


def test_adapter_binds_signed_fields_to_actual_method_path_and_exact_body():
    envelope = _extract(_request())

    assert envelope.body == BODY
    assert envelope.request["method"] == "POST"
    assert envelope.request["path"] == "/internal/reconciliation?batch=1"
    assert envelope.request["service_id"] == "internal-eos"
    assert envelope.request["audience"] == "legal-reconciliation"
    assert envelope.request["correlation_id"] == "corr-20261025-001"
    assert envelope.idempotency_key == "corr-20261025-001"
    assert envelope.observed_at == datetime(2026, 10, 25, 9, 30, tzinfo=timezone.utc)
    assert "tenant_id" not in envelope.request
    assert "provider_name" not in envelope.request
    assert "principal_id" not in envelope.request


def test_adapter_preserves_empty_body_and_path_without_query():
    envelope = _extract(_request(body=b"", query=b""))
    assert envelope.body == b""
    assert envelope.request["path"] == "/internal/reconciliation"


def test_adapter_rejects_duplicate_signed_header():
    headers = list(HEADERS) + [(b"X-Wilsy-Service-ID", b"attacker-controlled")]
    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationTransportError,
        match="SIGNED_WORKLOAD_HEADER_DUPLICATE",
    ):
        _extract(_request(headers=headers))


def test_adapter_rejects_missing_signed_header():
    headers = [pair for pair in HEADERS if pair[0] != b"x-wilsy-signature"]
    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationTransportError,
        match="SIGNED_WORKLOAD_HEADER_MISSING",
    ):
        _extract(_request(headers=headers))


def test_adapter_rejects_non_ascii_signed_header_value():
    headers = [(name, b"internal-\xff" if name == b"x-wilsy-service-id" else value)
               for name, value in HEADERS]
    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationTransportError,
        match="SIGNED_WORKLOAD_HEADER_ENCODING_INVALID",
    ):
        _extract(_request(headers=headers))


def test_adapter_rejects_non_uppercase_method_and_non_origin_path():
    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationTransportError,
        match="ACTUAL_HTTP_METHOD_INVALID",
    ):
        _extract(_request(method="post"))
    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationTransportError,
        match="ACTUAL_HTTP_PATH_INVALID",
    ):
        _extract(_request(raw_path=b"//attacker.invalid/path"))


def test_adapter_rejects_untrusted_request_object_and_naive_clock():
    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationTransportError,
        match="ACTUAL_ASGI_REQUEST_REQUIRED",
    ):
        asyncio.run(extract_signed_workload_request(object()))  # type: ignore[arg-type]

    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationTransportError,
        match="SERVER_CLOCK_INVALID",
    ):
        asyncio.run(
            extract_signed_workload_request(
                _request(),
                clock=lambda: datetime(2026, 10, 25, 9, 30),
            )
        )
