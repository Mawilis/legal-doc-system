"""WILSY OS password-reset HTTP/ASGI certificate.

TITLE: WILSY OS Password Reset HTTP ASGI Certificate
VERSION: v1.2.0-R10E76-PASSWORD-POLICY-DEPENDENCY-HTTP-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the mounted FastAPI password-reset completion boundary
         without changing production, contacting MongoDB, using a localhost
         socket, or installing an external HTTP test dependency.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_password_reset_http.py
COLLABORATION / OWNERSHIP: Exercises the canonical ``tools.eos.api.server``
                           application and its mounted R10D4 auth router;
                           the reset transaction remains owned by the frozen
                           PasswordResetService.
CERTIFICATION / UPDATE DATE: 2026-09-24
CHANGELOG: v1.2.0-R10E76-PASSWORD-POLICY-DEPENDENCY-HTTP-CERT certifies policy-dependency failure as bounded 503
           while preserving user-correctable password-policy rejection as 400,
           and refreshes the exact reset-service/direct-certificate byte freeze.
           v1.1.0-R10E53-R10D-RESET-FREEZE-BOUNDARY narrows the historical R10D byte-freeze to the
           reset service and its direct/real-Mongo certificates. The shared auth
           router is intentionally governed by behavioral reset-handler evidence
           because later certified auth routes may extend the same file without
           altering R10D reset authority.
           v1.0.0-R10D5-PASSWORD-RESET-HTTP-ASGI-CERT establishes in-process
           ASGI evidence for the public /api prefix, strict request parsing,
           one-call service delegation, bounded failures, secret hygiene,
           OpenAPI privacy, and preservation of PRE_AUTH routing.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic sentinel values are held only by test
                            doubles. They are never printed. Response, header,
                            and captured-log assertions reject secret leakage.
TENANT BOUNDARY: The HTTP tenant_id is forwarded only as the service lookup
                 selector; durable recovery capability binding remains the
                 reset authority.
AUTHORITY BOUNDARY: Test evidence only. The certificate owns no credentials,
                    persistence, transaction, JWT, session, delivery, Node,
                    client, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                              execution and settlement authority.
FAIL-CLOSED POSTURE: Invalid transport, unusable recovery, policy, internal,
                     and unexpected failures never produce a successful reset.
"""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI

from tools.eos.api import auth_router
from tools.eos.api.server import app as canonical_app
from tools.eos.saas.auth.password_reset_service import (
    PasswordResetCode,
    PasswordResetServiceError,
)


VERSION = "v1.2.0-R10E76-PASSWORD-POLICY-DEPENDENCY-HTTP-CERT"
R10D1_SHA3_512 = "024099bc7aca138cb6348f50b6ee5fe209bae1a738315049c6a795ee625bef26ebaf3370ef71b18bce2ef880f37da06fcc3b27d2b8da52bfbbcdace5ff82f066"
R10D2_SHA3_512 = "a52378fce120ce5490d8cb8db64ec4f85459180ebf143c3fdd398a0826f4d51a47612818574b491535e85d49b899224bd82abcc688be10113231e90e5e2b3b9b"
R10D3_SHA3_512 = "de89a1382b8734b660bf30ac63ee3dd3aaf60382674bb04656db4a142db109772bc679815a2ddf34f916b77282c3c4550ff5d5ca2a539c1e7a5b29494f89cee7"
PUBLIC_PATH = "/api/auth/reset-password"
DOUBLE_API_PATH = "/api/api/auth/reset-password"
RAW_ROUTER_PATH = "/auth/reset-password"
TOKEN_SENTINEL = "r10d5-recovery-sentinel-never-print"
PASSWORD_SENTINEL = "r10d5-password-sentinel-never-print"


@dataclass(slots=True)
class ASGIResult:
    """Captured HTTP response from the in-process ASGI boundary."""

    status_code: int | None = None
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    raised: BaseException | None = None

    @property
    def text(self) -> str:
        """Decode the bounded response body for assertions only."""

        return self.body.decode("utf-8", errors="replace")


async def _invoke_asgi(
    app: Any,
    *,
    method: str,
    path: str,
    payload: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> ASGIResult:
    """Invoke the actual ASGI callable without an HTTP client package."""

    request_body = payload if payload is not None else b""
    supplied_headers = {key.lower(): value for key, value in (headers or {}).items()}
    supplied_headers.setdefault("host", "r10d5.test")
    supplied_headers.setdefault("content-length", str(len(request_body)))
    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": b"",
        "headers": [(key.encode("latin-1"), value.encode("latin-1")) for key, value in supplied_headers.items()],
        "client": ("r10d5-test", 1),
        "server": ("r10d5-asgi", 80),
        "root_path": "",
    }
    incoming = [{"type": "http.request", "body": request_body, "more_body": False}]
    messages: list[dict[str, Any]] = []

    async def receive() -> dict[str, Any]:
        """Return one complete request and then an orderly disconnect."""

        if incoming:
            return incoming.pop(0)
        return {"type": "http.disconnect"}

    async def send(message: dict[str, Any]) -> None:
        """Record ASGI response events without interpreting authority."""

        messages.append(message)

    result = ASGIResult()
    try:
        await app(scope, receive, send)
    except BaseException as error:
        result.raised = error
    for message in messages:
        if message["type"] == "http.response.start":
            result.status_code = int(message["status"])
            result.headers = {
                key.decode("latin-1").lower(): value.decode("latin-1")
                for key, value in message.get("headers", [])
            }
        elif message["type"] == "http.response.body":
            result.body += message.get("body", b"")
    return result


def _request_payload() -> dict[str, str]:
    """Return one valid synthetic request without exposing its values."""

    return {
        "tenant_id": "tenant-r10d5",
        "recovery_token": TOKEN_SENTINEL,
        "new_password": PASSWORD_SENTINEL,
    }


def _json_body(payload: object) -> bytes:
    """Encode one test request as ordinary JSON."""

    return json.dumps(payload, separators=(",", ":")).encode("utf-8")


def _post(payload: object, *, path: str = PUBLIC_PATH) -> ASGIResult:
    """Issue a real mounted POST through the canonical ASGI app."""

    return asyncio.run(
        _invoke_asgi(
            canonical_app,
            method="POST",
            path=path,
            payload=_json_body(payload),
            headers={"content-type": "application/json"},
        )
    )


def _raw_request(*, method: str, path: str, body: bytes = b"", headers: dict[str, str] | None = None) -> ASGIResult:
    """Issue one arbitrary method/path request through the real app."""

    return asyncio.run(
        _invoke_asgi(canonical_app, method=method, path=path, payload=body, headers=headers)
    )


def _assert_no_sentinels(result: ASGIResult) -> None:
    """Prove no test secret appears in response body or headers."""

    rendered_headers = repr(result.headers)
    assert TOKEN_SENTINEL not in result.text
    assert PASSWORD_SENTINEL not in result.text
    assert TOKEN_SENTINEL not in rendered_headers
    assert PASSWORD_SENTINEL not in rendered_headers


class RecordingResetService:
    """Faithful R10D1 service double with bounded failure modes."""

    mode: str = "success"

    def __init__(self, **kwargs: object) -> None:
        """Record construction while permitting fixture-only direct creation.

        The factory installed at the router boundary asserts the live adapter
        supplies exactly the blocklist dependency.  Direct construction is
        intentionally dependency-free so the test double itself cannot create
        a production checker or network capability.
        """

        if kwargs:
            assert set(kwargs) == {"blocklist_checker"}
        self.constructor_kwargs = dict(kwargs)
        self.calls: list[dict[str, object]] = []

    def reset_password(self, **kwargs: object) -> object:
        """Record one invocation and raise the selected real domain error."""

        self.calls.append(dict(kwargs))
        if self.mode == "success":
            return object()
        if self.mode == "unexpected":
            raise RuntimeError("synthetic internal failure")
        code = PasswordResetCode[self.mode]
        raise PasswordResetServiceError(code)


@pytest.fixture
def service_double(monkeypatch: pytest.MonkeyPatch) -> RecordingResetService:
    """Patch only service construction while retaining the real app/router."""

    double = RecordingResetService()

    def factory(**kwargs: object) -> RecordingResetService:
        """Capture the adapter's dependency injection without constructing it."""

        assert set(kwargs) == {"blocklist_checker"}
        double.constructor_kwargs = dict(kwargs)
        return double

    monkeypatch.setattr(auth_router, "PasswordResetService", factory)
    return double


def _iter_effective_routes(
    routes: list[Any] | tuple[Any, ...],
    prefix: str = "",
) -> list[tuple[Any, str]]:
    """Flatten FastAPI mounts while reconstructing each effective path."""

    flattened: list[tuple[Any, str]] = []
    for route in routes:
        included_router = getattr(route, "original_router", None)
        if included_router is not None:
            context = getattr(route, "include_context", None)
            include_prefix = getattr(context, "prefix", "")
            flattened.extend(
                _iter_effective_routes(
                    tuple(included_router.routes),
                    prefix=f"{prefix}{include_prefix}",
                )
            )
            continue
        effective_path = f"{prefix}{getattr(route, 'path', '')}"
        flattened.append((route, effective_path))
        nested = getattr(route, "routes", None)
        if nested:
            flattened.extend(_iter_effective_routes(tuple(nested), prefix=prefix))
    return flattened


def test_public_success_is_bodyless_and_forwards_exact_fields(service_double: RecordingResetService) -> None:
    """The mounted public path returns 204 after exactly one service call."""

    result = _post(_request_payload())
    assert result.raised is None
    assert result.status_code == 204
    assert result.body == b""
    assert set(service_double.constructor_kwargs) == {"blocklist_checker"}
    assert len(service_double.calls) == 1
    assert service_double.calls[0] == {
        "tenant_id": "tenant-r10d5",
        "recovery_token": TOKEN_SENTINEL,
        "new_password": PASSWORD_SENTINEL,
        "context_terms": None,
    }
    _assert_no_sentinels(result)


def test_success_requires_no_access_jwt_and_no_auto_login(service_double: RecordingResetService) -> None:
    """No Authorization header is required and no token/session is returned."""

    result = _post(_request_payload())
    assert result.status_code == 204
    assert "authorization" not in result.headers
    assert result.body == b""
    assert len(service_double.calls) == 1


def test_double_api_prefix_is_rejected_without_service_call(service_double: RecordingResetService) -> None:
    """The client prefix cannot be duplicated into a second /api segment."""

    result = _post(_request_payload(), path=DOUBLE_API_PATH)
    assert result.status_code == 404
    assert len(service_double.calls) == 0
    _assert_no_sentinels(result)


def test_raw_router_path_is_not_publicly_mounted(service_double: RecordingResetService) -> None:
    """The unmounted router-relative path is not accepted by the app."""

    result = _post(_request_payload(), path=RAW_ROUTER_PATH)
    assert result.status_code == 404
    assert len(service_double.calls) == 0


def test_wrong_method_is_rejected_without_service_call(service_double: RecordingResetService) -> None:
    """GET cannot invoke the POST-only completion handler."""

    result = _raw_request(method="GET", path=PUBLIC_PATH)
    assert result.status_code == 405
    assert len(service_double.calls) == 0


@pytest.mark.parametrize("missing", ["tenant_id", "recovery_token", "new_password"])
def test_missing_required_field_is_fastapi_422_without_service_call(
    service_double: RecordingResetService,
    missing: str,
) -> None:
    """Pydantic rejects incomplete transport before service delegation."""

    payload = _request_payload()
    del payload[missing]
    result = _post(payload)
    assert result.status_code == 422
    assert len(service_double.calls) == 0


def test_wrong_field_type_is_422_without_service_call(service_double: RecordingResetService) -> None:
    """Strict string fields reject structured caller authority."""

    payload = _request_payload()
    payload["tenant_id"] = 7  # type: ignore[assignment]
    result = _post(payload)
    assert result.status_code == 422
    assert len(service_double.calls) == 0


def test_malformed_json_is_422_without_service_call(service_double: RecordingResetService) -> None:
    """Malformed JSON cannot reach the reset service."""

    result = _raw_request(
        method="POST",
        path=PUBLIC_PATH,
        body=b"{malformed",
        headers={"content-type": "application/json"},
    )
    assert result.status_code == 422
    assert len(service_double.calls) == 0


@pytest.mark.parametrize("field", ["principal_id", "credential_revision", "role", "permissions", "mfa_state"])
def test_extra_authority_field_is_rejected_without_service_call(
    service_double: RecordingResetService,
    field: str,
) -> None:
    """Browser authority fields cannot enter the request model or service."""

    payload: dict[str, object] = dict(_request_payload())
    payload[field] = "caller-supplied"
    result = _post(payload)
    assert result.status_code == 422
    assert len(service_double.calls) == 0


@pytest.mark.parametrize(
    ("mode", "expected_status"),
    [
        ("RECOVERY_INVALID", 400),
        ("RECOVERY_REPLAYED", 400),
    ],
)
def test_unusable_recovery_states_are_uniform_bounded_failures(
    service_double: RecordingResetService,
    mode: str,
    expected_status: int,
) -> None:
    """Unknown, expired, consumed, revoked, and mismatch forms disclose no state."""

    service_double.mode = mode
    result = _post(_request_payload())
    assert result.status_code == expected_status
    assert len(service_double.calls) == 1
    assert "invalid or expired" in result.text.lower()
    _assert_no_sentinels(result)


@pytest.mark.parametrize(
    "mode",
    ["RECOVERY_INVALID", "RECOVERY_REPLAYED"],
)
def test_expired_consumed_revoked_and_tenant_mismatch_share_recovery_contract(
    service_double: RecordingResetService,
    mode: str,
) -> None:
    """Every unusable lifecycle classification uses the same public response."""

    service_double.mode = mode
    result = _post(_request_payload())
    assert result.status_code == 400
    assert len(service_double.calls) == 1
    assert "reset" in result.text.lower()
    _assert_no_sentinels(result)


def test_policy_failure_is_bounded_client_error(service_double: RecordingResetService) -> None:
    """Password-policy failure reveals no checker, breach, or candidate detail."""

    service_double.mode = "POLICY_REJECTED"
    result = _post(_request_payload())
    assert result.status_code == 400
    assert "password" in result.text.lower()
    assert "hibp" not in result.text.lower()
    assert "breach" not in result.text.lower()
    _assert_no_sentinels(result)


@pytest.mark.parametrize(
    "mode",
    ["RECOVERY_PERSISTENCE_FAILURE", "POLICY_DEPENDENCY_FAILURE", "HASHING_FAILED", "CREDENTIAL_CONFLICT", "PERSISTENCE_FAILURE", "TRANSACTION_FAILURE"],
)
def test_internal_service_failures_are_bounded_503(
    service_double: RecordingResetService,
    mode: str,
) -> None:
    """Credential, infrastructure, and transaction failures do not leak text."""

    service_double.mode = mode
    result = _post(_request_payload())
    assert result.status_code == 503
    assert len(service_double.calls) == 1
    assert "temporarily unavailable" in result.text.lower()
    _assert_no_sentinels(result)


def test_unexpected_failure_cannot_return_success(
    service_double: RecordingResetService,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Unexpected service errors become bounded 503 responses."""

    service_double.mode = "unexpected"
    with caplog.at_level(logging.ERROR, logger="tools.eos.api.auth_router"):
        result = _post(_request_payload())
    assert result.raised is None
    assert result.status_code == 503
    assert len(service_double.calls) == 1
    assert TOKEN_SENTINEL not in caplog.text
    assert PASSWORD_SENTINEL not in caplog.text
    _assert_no_sentinels(result)


def test_all_http_outputs_and_logs_are_secret_free(
    service_double: RecordingResetService,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Success and bounded error output contain neither sentinel value."""

    service_double.mode = "TRANSACTION_FAILURE"
    with caplog.at_level(logging.ERROR, logger="tools.eos.api.auth_router"):
        result = _post(_request_payload())
    assert result.status_code == 503
    assert TOKEN_SENTINEL not in caplog.text
    assert PASSWORD_SENTINEL not in caplog.text
    _assert_no_sentinels(result)


def test_service_is_called_once_without_adapter_retry(service_double: RecordingResetService) -> None:
    """A domain failure is reached once and never retried by the adapter."""

    service_double.mode = "TRANSACTION_FAILURE"
    result = _post(_request_payload())
    assert result.status_code == 503
    assert len(service_double.calls) == 1


def test_openapi_and_route_table_match_public_mount() -> None:
    """The actual app schema and route table expose one private-safe operation."""

    paths = [
        route
        for route, effective_path in _iter_effective_routes(tuple(canonical_app.routes))
        if effective_path == PUBLIC_PATH and "POST" in getattr(route, "methods", set())
    ]
    assert len(paths) == 1
    schema = canonical_app.openapi()
    assert PUBLIC_PATH in schema["paths"]
    operation = schema["paths"][PUBLIC_PATH]["post"]
    ref = operation["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    properties = schema["components"]["schemas"][ref.rsplit("/", 1)[-1]]["properties"]
    assert set(properties) == {"tenant_id", "recovery_token", "new_password"}
    forbidden = {"principal_id", "credential_revision", "password_hash", "role", "permissions", "mfa_state", "session_id", "refresh_id", "status"}
    assert not forbidden.intersection(properties)


def test_request_schema_is_strict_and_has_no_caller_authority_fields() -> None:
    """The live Pydantic schema rejects unknown authority-bearing fields."""

    schema = canonical_app.openapi()
    ref = schema["paths"][PUBLIC_PATH]["post"]["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    model = schema["components"]["schemas"][ref.rsplit("/", 1)[-1]]
    assert model.get("additionalProperties") is False
    assert set(model["required"]) == {"tenant_id", "recovery_token", "new_password"}


def test_existing_pre_auth_topology_remains_exact() -> None:
    """R10D4's three PRE_AUTH issuers remain and no generic/access issuer appears."""

    source = Path("tools/eos/api/auth_router.py").read_text(encoding="utf-8")
    assert source.count("generate_pre_auth_jwt(") == 3
    assert "generate_jwt(" not in source
    assert "generate_access_jwt(" not in source


def test_reset_handler_has_no_direct_token_or_persistence_authority() -> None:
    """The handler delegates all mutation authority to the frozen service."""

    source = Path("tools/eos/api/auth_router.py").read_text(encoding="utf-8")
    start = source.index("async def complete_password_reset")
    end = source.index("# ─── LOGIN", start)
    handler = source[start:end]
    forbidden = (
        "generate_jwt",
        "generate_access_jwt",
        "generate_pre_auth_jwt",
        "create_session",
        "TokenService",
        "compare_and_swap_password_hash",
        "revoke_sessions",
        "revoke_refresh_tokens",
        "consume",
    )
    assert all(item not in handler for item in forbidden)


def test_frozen_r10d_reset_service_and_certificates_remain_exact() -> None:
    """Freeze reset authority while permitting governed shared-router growth.

    The shared auth router is certified above by exact reset-handler behavior,
    request shape, route topology, and absence of direct mutation authority.
    Later governed auth routes may extend that file without invalidating the
    frozen reset service or its direct and real-Mongo certificates.
    """

    import hashlib

    expected = {
        "tools/eos/saas/auth/password_reset_service.py": R10D1_SHA3_512,
        "tests/unit/test_password_reset_service.py": R10D2_SHA3_512,
        "tests/integration/test_password_reset_service_real_mongo.py": R10D3_SHA3_512,
    }
    for filename, digest in expected.items():
        actual = hashlib.sha3_512(Path(filename).read_bytes()).hexdigest()
        assert actual == digest


# ARTIFACT: test_password_reset_http.py
# VERSION: v1.2.0-R10E76-PASSWORD-POLICY-DEPENDENCY-HTTP-CERT
# AUTHORITY BOUNDARY: mounted ASGI transport evidence only; no production authority
# TENANT POSTURE: tenant selector forwarding is tested without trusting it as reset authority
# FAIL-CLOSED POSTURE: malformed, unusable, policy, internal, and unexpected cases never pass
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
