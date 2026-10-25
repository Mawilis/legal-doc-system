"""
TITLE: WILSY EOS Legal Evidence Reconciliation Workload Client
VERSION: v1.0.0-L10A2R-C4D7-PYTHON-CALLER
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Issue one explicitly requested, signed, idempotent HTTP invocation to the dedicated reconciliation route.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_invocation_client.py
COLLABORATION / OWNERSHIP: A deployment-owned Python workload invokes the canonical EOS route. Caller identity, audience, key identifier and secret are injected from approved deployment configuration; this module creates no credential, authority, tenant scope or provider selection.
CERTIFICATION OR UPDATE DATE: 2026-10-25
CHANGELOG: v1.0.0 establishes the Python-only signed caller for the exact mounted reconciliation path, using the canonical EOS HMAC contract, exact body bytes, fresh nonce and caller-supplied operation idempotency key.
COMPLIANCE: Fail-closed transport; bounded response handling; TLS required; no automatic retries.
SECURITY / PRIVACY POSTURE: Never logs or returns secret/signature material. Secret is passed only in memory and is not read from command arguments or payloads.
TENANT BOUNDARY: No tenant, provider, bucket, object, principal or authorization field is accepted by the caller.
AUTHORITY BOUNDARY: Authenticates a configured workload only. Server-side current credential, activation, permission, tenant and provider authorities remain mandatory.
FINANCIAL AUTHORITY BOUNDARY: NONE.
TRANSACTION BOUNDARY: The server owns the business transaction; this caller owns one HTTP attempt. A timeout is ambiguous and must be reconciled by retrying the same operation idempotency key with a fresh signed nonce.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from uuid import uuid4

VERSION = "v1.0.0-L10A2R-C4D7-PYTHON-CALLER"
RECONCILIATION_PATH = "/api/legal-operations/evidence-provider/reconciliation"
PROTOCOL_VERSION = "v1"
MAX_RESPONSE_BYTES = 1_048_576
_KEY = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,159}\Z")
_TEXT = re.compile(r"[^\r\n]{1,256}\Z")


class ReconciliationInvocationClientError(RuntimeError):
    """Bounded caller error that never includes secrets or signed headers."""


@dataclass(frozen=True, slots=True)
class ReconciliationInvocationResult:
    """One HTTP response, preserving status and bounded response bytes."""

    status_code: int
    body: bytes
    correlation_id: str


def _required_text(value: str, code: str) -> str:
    if not isinstance(value, str) or not _TEXT.fullmatch(value) or not value.strip():
        raise ReconciliationInvocationClientError(code)
    return value


def _canonical_request(
    *, service_id: str, audience: str, method: str, path: str, timestamp: str,
    nonce: str, body_digest: str, correlation_id: str,
) -> bytes:
    fields = (
        PROTOCOL_VERSION, service_id, audience, method, path, timestamp, nonce,
        body_digest, correlation_id,
    )
    if any(not isinstance(value, str) or not value or "\r" in value or "\n" in value for value in fields):
        raise ReconciliationInvocationClientError("SIGNED_REQUEST_FIELDS_INVALID")
    return "\n".join(fields).encode("utf-8")


def build_signed_invocation(
    *,
    service_id: str,
    audience: str,
    key_id: str,
    secret: str,
    idempotency_key: str,
    now: int | None = None,
    nonce: str | None = None,
    correlation_id: str | None = None,
) -> tuple[bytes, dict[str, str], str]:
    """Build the exact signed JSON body and required X-Wilsy headers.

    The operation key is caller-supplied and stable across retries. Nonce and
    correlation are fresh per attempt. This function does not authorize use.
    Optional clock/nonce/correlation parameters exist only for deterministic
    tests and must not be used to override production defaults.
    """
    service_id = _required_text(service_id, "WORKLOAD_SERVICE_ID_REQUIRED")
    audience = _required_text(audience, "WORKLOAD_AUDIENCE_REQUIRED")
    key_id = _required_text(key_id, "WORKLOAD_KEY_ID_REQUIRED")
    if not isinstance(secret, str) or not secret or "\r" in secret or "\n" in secret:
        raise ReconciliationInvocationClientError("WORKLOAD_SECRET_REQUIRED")
    if not isinstance(idempotency_key, str) or not _KEY.fullmatch(idempotency_key) or "*" in idempotency_key:
        raise ReconciliationInvocationClientError("OPERATION_IDEMPOTENCY_KEY_INVALID")

    timestamp = str(int(time.time()) if now is None else now)
    request_nonce = secrets.token_hex(16) if nonce is None else nonce
    request_correlation = uuid4().hex if correlation_id is None else correlation_id
    if not re.fullmatch(r"[0-9a-f]{32}", request_nonce):
        raise ReconciliationInvocationClientError("WORKLOAD_NONCE_INVALID")
    _required_text(request_correlation, "WORKLOAD_CORRELATION_ID_INVALID")

    body = json.dumps(
        {"idempotency_key": idempotency_key},
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    digest = hashlib.sha3_512(body).hexdigest()
    canonical = _canonical_request(
        service_id=service_id,
        audience=audience,
        method="POST",
        path=RECONCILIATION_PATH,
        timestamp=timestamp,
        nonce=request_nonce,
        body_digest=digest,
        correlation_id=request_correlation,
    )
    signature = hmac.new(secret.encode("utf-8"), canonical, hashlib.sha256).hexdigest()
    headers = {
        "X-Wilsy-Auth-Version": PROTOCOL_VERSION,
        "X-Wilsy-Service-ID": service_id,
        "X-Wilsy-Audience": audience,
        "X-Wilsy-Key-ID": key_id,
        "X-Wilsy-Timestamp": timestamp,
        "X-Wilsy-Nonce": request_nonce,
        "X-Wilsy-Body-Sha3-512": digest,
        "X-Wilsy-Correlation-ID": request_correlation,
        "X-Wilsy-Signature": signature,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    return body, headers, request_correlation


def invoke_legal_evidence_reconciliation(
    *,
    endpoint: str,
    service_id: str,
    audience: str,
    key_id: str,
    secret: str,
    idempotency_key: str,
    timeout_seconds: float = 15.0,
) -> ReconciliationInvocationResult:
    """Invoke the exact EOS route once; never retry an ambiguous HTTP result.

    endpoint must be the HTTPS origin (scheme and authority only), not a URL
    containing a path, query, fragment, user information or embedded secret.
    Deployment configuration must inject the actual issued service identity,
    expected audience, active key ID and secret from approved secret storage.
    """
    if not isinstance(endpoint, str):
        raise ReconciliationInvocationClientError("RECONCILIATION_ENDPOINT_INVALID")
    parsed = urllib.parse.urlsplit(endpoint)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise ReconciliationInvocationClientError("RECONCILIATION_ENDPOINT_MUST_BE_HTTPS_ORIGIN")
    if not isinstance(timeout_seconds, (int, float)) or isinstance(timeout_seconds, bool) or not 0 < timeout_seconds <= 60:
        raise ReconciliationInvocationClientError("RECONCILIATION_TIMEOUT_INVALID")

    body, headers, correlation_id = build_signed_invocation(
        service_id=service_id,
        audience=audience,
        key_id=key_id,
        secret=secret,
        idempotency_key=idempotency_key,
    )
    request = urllib.request.Request(
        endpoint.rstrip("/") + RECONCILIATION_PATH,
        data=body,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=float(timeout_seconds)) as response:
            response_body = response.read(MAX_RESPONSE_BYTES + 1)
            if len(response_body) > MAX_RESPONSE_BYTES:
                raise ReconciliationInvocationClientError("RECONCILIATION_RESPONSE_TOO_LARGE")
            return ReconciliationInvocationResult(int(response.status), response_body, correlation_id)
    except urllib.error.HTTPError as error:
        try:
            response_body = error.read(MAX_RESPONSE_BYTES + 1)
        finally:
            error.close()
        if len(response_body) > MAX_RESPONSE_BYTES:
            raise ReconciliationInvocationClientError("RECONCILIATION_RESPONSE_TOO_LARGE") from None
        return ReconciliationInvocationResult(int(error.code), response_body, correlation_id)
    except ReconciliationInvocationClientError:
        raise
    except (urllib.error.URLError, TimeoutError, OSError):
        # Do not retry automatically: the server may have committed before the
        # connection failed. A caller must retry with the same idempotency key.
        raise ReconciliationInvocationClientError(
            "RECONCILIATION_TRANSPORT_OUTCOME_UNKNOWN"
        ) from None


# ARTIFACT: legal_evidence_provider_readonly_reconciliation_invocation_client.py
# VERSION: v1.0.0-L10A2R-C4D7-PYTHON-CALLER
# AUTHORITY BOUNDARY: Signed transport only; EOS retains all authorization.
# TENANT POSTURE: Server-owned tenant/provider scope only.
# FAIL-CLOSED POSTURE: Invalid config and ambiguous transport outcomes never trigger automatic retry.
# FINANCIAL EXECUTION AUTHORITY: NONE.
# END OF WILSY OS SOVEREIGN ARTIFACT
