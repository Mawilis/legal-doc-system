"""
TITLE:
    WILSY OS Signed Internal Workload HTTP Request Adapter

VERSION:
    v1.0.0-L10A2R-C4D7C-RAW-ASGI-REQUEST-BOUNDARY

AUTHORITY:
    Wilsy OS Core Governance / Python EOS Legal Operations

EPITOME:
    Extract the canonical signed internal-workload envelope from one actual
    ASGI request without accepting caller-selected identity, tenant, provider,
    method, or path assertions.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_transport_adapter.py

COLLABORATION / OWNERSHIP:
    This adapter translates the existing X-Wilsy internal-service HTTP header
    contract into the canonical request mapping consumed by P3 verification.
    The authorization gate verifies the signature and canonical currentness.
    The invocation owner supplies an already-active business transaction and
    remains responsible for commit/abort. This module is not mounted as a route.

CERTIFICATION OR UPDATE DATE:
    2026-10-25

CHANGELOG:
    v1.0.0-L10A2R-C4D7C-RAW-ASGI-REQUEST-BOUNDARY
        Adds strict raw-ASGI header extraction, actual method/path binding,
        exact body-byte preservation, duplicate-header rejection, and a signed
        correlation identifier as the operation idempotency key.

COMPLIANCE:
    Fail-closed transport normalization. The adapter establishes no identity,
    permission, activation, tenant membership, provider scope, or route access.

SECURITY / PRIVACY POSTURE:
    Never accepts signed fields from JSON body or request context. Required
    headers must appear exactly once. Method and origin-form path come from the
    actual ASGI scope. Body bytes are passed unchanged for downstream HMAC and
    digest verification. No secret or signature is logged or persisted here.

TENANT BOUNDARY:
    No tenant, bucket, provider, object, or principal selection is accepted.

AUTHORITY BOUNDARY:
    Transport extraction only; not authentication or authorization. The
    resulting envelope must be passed to the canonical P5 reconciliation gate.
    The caller must provide an already-active session to the composition root.

FINANCIAL AUTHORITY BOUNDARY:
    NONE. Kennel EOS remains the exclusive financial execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Mapping

from starlette.requests import Request


VERSION = "v1.0.0-L10A2R-C4D7C-RAW-ASGI-REQUEST-BOUNDARY"

_HEADER_FIELDS: tuple[tuple[bytes, str], ...] = (
    (b"x-wilsy-auth-version", "version"),
    (b"x-wilsy-service-id", "service_id"),
    (b"x-wilsy-audience", "audience"),
    (b"x-wilsy-key-id", "key_id"),
    (b"x-wilsy-timestamp", "timestamp"),
    (b"x-wilsy-nonce", "nonce"),
    (b"x-wilsy-body-sha3-512", "body_sha3_512"),
    (b"x-wilsy-correlation-id", "correlation_id"),
    (b"x-wilsy-signature", "signature"),
)


class LegalEvidenceProviderReadOnlyReconciliationTransportError(RuntimeError):
    """Fail-closed error for malformed or ambiguous signed HTTP envelopes."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class SignedWorkloadRequestEnvelope:
    """Transport facts extracted from one actual request, not an auth grant.

    The envelope preserves exact body bytes and binds method/path to the ASGI
    request scope. Its request mapping is only input to canonical HMAC and
    workload-currentness verification; callers must not treat it as trusted
    identity or authorization evidence.

    The signed correlation identifier is used as the operation idempotency key
    so an unsigned auxiliary header cannot select a different decision key.
    The invocation owner still owns the active database transaction.
    """

    request: Mapping[str, str]
    body: bytes
    idempotency_key: str
    observed_at: datetime


async def extract_signed_workload_request(
    request: Request,
    *,
    clock: Callable[[], datetime] | None = None,
) -> SignedWorkloadRequestEnvelope:
    """Extract the existing X-Wilsy signed request contract from ASGI.

    Required headers are mapped to the canonical fields consumed by
    verify_internal_service_request. Duplicate required headers, invalid byte
    encoding, a missing raw path, or an invalid server clock fail closed.
    Query bytes are included in the signed path exactly as received. No body
    parsing, tenant/provider selection, transaction operation, or authority
    decision occurs here.
    """
    if not isinstance(request, Request):
        raise LegalEvidenceProviderReadOnlyReconciliationTransportError(
            "ACTUAL_ASGI_REQUEST_REQUIRED"
        )

    raw_headers = request.scope.get("headers")
    if not isinstance(raw_headers, list):
        raise LegalEvidenceProviderReadOnlyReconciliationTransportError(
            "ASGI_RAW_HEADERS_REQUIRED"
        )

    values: dict[bytes, list[bytes]] = {}
    required_names = {name for name, _ in _HEADER_FIELDS}
    for item in raw_headers:
        if (
            not isinstance(item, tuple)
            or len(item) != 2
            or not isinstance(item[0], bytes)
            or not isinstance(item[1], bytes)
        ):
            raise LegalEvidenceProviderReadOnlyReconciliationTransportError(
                "ASGI_RAW_HEADER_INVALID"
            )
        name, value = item
        lower_name = name.lower()
        if lower_name in required_names:
            values.setdefault(lower_name, []).append(value)

    mapped: dict[str, str] = {}
    for header_name, field_name in _HEADER_FIELDS:
        occurrences = values.get(header_name, [])
        if len(occurrences) != 1:
            code = (
                "SIGNED_WORKLOAD_HEADER_DUPLICATE"
                if len(occurrences) > 1
                else "SIGNED_WORKLOAD_HEADER_MISSING"
            )
            raise LegalEvidenceProviderReadOnlyReconciliationTransportError(
                code
            )
        try:
            mapped[field_name] = occurrences[0].decode("ascii")
        except UnicodeDecodeError as error:
            raise LegalEvidenceProviderReadOnlyReconciliationTransportError(
                "SIGNED_WORKLOAD_HEADER_ENCODING_INVALID"
            ) from error

    method = request.scope.get("method")
    raw_path = request.scope.get("raw_path")
    query_string = request.scope.get("query_string", b"")
    if (
        not isinstance(method, str)
        or not method
        or method != method.upper()
        or not method.isascii()
    ):
        raise LegalEvidenceProviderReadOnlyReconciliationTransportError(
            "ACTUAL_HTTP_METHOD_INVALID"
        )
    if not isinstance(raw_path, bytes) or not raw_path.startswith(b"/"):
        raise LegalEvidenceProviderReadOnlyReconciliationTransportError(
            "ACTUAL_HTTP_PATH_INVALID"
        )
    if not isinstance(query_string, bytes):
        raise LegalEvidenceProviderReadOnlyReconciliationTransportError(
            "ACTUAL_HTTP_QUERY_INVALID"
        )
    try:
        path = raw_path.decode("ascii")
        if query_string:
            path += "?" + query_string.decode("ascii")
    except UnicodeDecodeError as error:
        raise LegalEvidenceProviderReadOnlyReconciliationTransportError(
            "ACTUAL_HTTP_PATH_ENCODING_INVALID"
        ) from error

    mapped["method"] = method
    mapped["path"] = path
    correlation_id = mapped["correlation_id"]
    if not correlation_id or correlation_id != correlation_id.strip():
        raise LegalEvidenceProviderReadOnlyReconciliationTransportError(
            "SIGNED_WORKLOAD_CORRELATION_INVALID"
        )

    try:
        body = await request.body()
    except Exception as error:
        raise LegalEvidenceProviderReadOnlyReconciliationTransportError(
            "ACTUAL_HTTP_BODY_UNAVAILABLE"
        ) from error

    observed_at = (clock or (lambda: datetime.now(timezone.utc)))()
    if not isinstance(observed_at, datetime) or observed_at.tzinfo is None:
        raise LegalEvidenceProviderReadOnlyReconciliationTransportError(
            "SERVER_CLOCK_INVALID"
        )

    return SignedWorkloadRequestEnvelope(
        request=mapped,
        body=body,
        idempotency_key=correlation_id,
        observed_at=observed_at.astimezone(timezone.utc),
    )


__all__ = [
    "VERSION",
    "LegalEvidenceProviderReadOnlyReconciliationTransportError",
    "SignedWorkloadRequestEnvelope",
    "extract_signed_workload_request",
]

# ARTIFACT: legal_evidence_provider_readonly_reconciliation_transport_adapter.py
# VERSION: v1.0.0-L10A2R-C4D7C-RAW-ASGI-REQUEST-BOUNDARY
# AUTHORITY BOUNDARY: Request normalization only; P3/P5 and the reconciliation gate decide trust.
# TENANT POSTURE: No caller-selected tenant or provider scope.
# FAIL-CLOSED POSTURE: Missing/duplicate/malformed signed headers, body, method, or path reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
