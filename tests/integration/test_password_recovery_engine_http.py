"""ASGI certificate for the WILSY OS password-recovery engine.

TITLE: WILSY OS Password Recovery Engine HTTP ASGI Certificate
VERSION: v1.0.2-R10E49-PASSWORD-RECOVERY-ENGINE-HTTP-MESSAGE-TYPE-CLOSURE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the mounted recovery-request and recovery-contact verification
         HTTP boundaries through the canonical FastAPI app without Mongo, SMTP,
         sockets, or production authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_password_recovery_engine_http.py
COLLABORATION / OWNERSHIP: Exercises tools.eos.api.server.app and the R10E auth
                           router with service doubles at orchestration seams.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.2-R10E49-PASSWORD-RECOVERY-ENGINE-HTTP-MESSAGE-TYPE-CLOSURE introduces mounted
           ASGI evidence for generic 202 recovery initiation, strict transport
           schemas, uniform anti-enumeration failure behavior, authenticated
           no-body recovery-email verification issuance, capability-only
           verification completion, bounded 429/400/503 mapping, secret hygiene,
           and OpenAPI authority exclusion.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic sentinels only; responses/log assertions
                            reject verification/recovery secret disclosure.
TENANT BOUNDARY: Public tenant values remain lookup selectors; authenticated
                 verification uses server identity and no browser tenant body.
AUTHORITY BOUNDARY: Mounted transport evidence only; no persistence, delivery,
                    password, JWT, session, MFA, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any

import pytest
from starlette.types import Message

from tools.eos.api import auth_router
from tools.eos.api.server import app as canonical_app
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.saas.auth.password_recovery_contact_verification_request_service import (
    RecoveryContactVerificationRequestError,
    RecoveryContactVerificationRequestResult,
)
from tools.eos.saas.auth.password_recovery_contact_verification_service import (
    RecoveryContactVerificationCode,
    RecoveryContactVerificationResult,
    RecoveryContactVerificationServiceError,
)
from tools.eos.saas.auth.password_recovery_request_service import (
    PasswordRecoveryRequestRateLimitedError,
    PasswordRecoveryRequestResult,
)

REQUEST_PATH = "/api/auth/request-password-reset"
VERIFY_REQUEST_PATH = "/api/auth/recovery-contact/request-verification"
VERIFY_COMPLETE_PATH = "/api/auth/recovery-contact/verify"
TENANT = "WILSY-TENANT-R10E34"
EMAIL = "verified.user@example.com"
RECOVERY_SENTINEL = "r10e34-recovery-token-never-print"
VERIFICATION_SENTINEL = "r10e34-verification-token-never-print"


@dataclass(slots=True)
class ASGIResult:
    status_code: int | None = None
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    raised: BaseException | None = None

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


async def _invoke_asgi(
    *,
    method: str,
    path: str,
    payload: object | None = None,
) -> ASGIResult:
    body = b"" if payload is None else json.dumps(payload, separators=(",", ":")).encode()
    headers = [(b"host", b"r10e34.test"), (b"content-length", str(len(body)).encode())]
    if payload is not None:
        headers.append((b"content-type", b"application/json"))
    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": b"",
        "headers": headers,
        "client": ("r10e34-test", 1),
        "server": ("r10e34-asgi", 80),
        "root_path": "",
    }
    incoming = [{"type": "http.request", "body": body, "more_body": False}]
    messages: list[Message] = []

    async def receive() -> dict[str, Any]:
        if incoming:
            return incoming.pop(0)
        return {"type": "http.disconnect"}

    async def send(message: Message) -> None:
        messages.append(message)

    result = ASGIResult()
    try:
        await canonical_app(scope, receive, send)
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


def _request(method: str, path: str, payload: object | None = None) -> ASGIResult:
    return asyncio.run(_invoke_asgi(method=method, path=path, payload=payload))


class _RecoveryRequestService:
    def __init__(self) -> None:
        self.calls = []
        self.mode = "success"

    def request_password_reset(self, **kwargs):
        self.calls.append(dict(kwargs))
        if self.mode == "rate":
            raise PasswordRecoveryRequestRateLimitedError("RECOVERY_REQUEST_RATE_LIMITED")
        if self.mode == "internal":
            raise RuntimeError("synthetic internal")
        return PasswordRecoveryRequestResult()


class _VerificationRequestService:
    def __init__(self) -> None:
        self.calls = []
        self.mode = "sent"

    def request_verification(self, **kwargs):
        self.calls.append(dict(kwargs))
        if self.mode == "rate":
            raise RecoveryContactVerificationRequestError(
                "RECOVERY_CONTACT_VERIFICATION_RATE_LIMITED"
            )
        if self.mode == "internal":
            raise RecoveryContactVerificationRequestError(
                "RECOVERY_CONTACT_VERIFICATION_CREATE_FAILED"
            )
        status = (
            "VERIFICATION_NOT_REQUIRED"
            if self.mode == "not-required"
            else "VERIFICATION_SENT"
        )
        return RecoveryContactVerificationRequestResult(status=status)


class _VerificationCompletionService:
    def __init__(self) -> None:
        self.calls = []
        self.code: RecoveryContactVerificationCode | None = None

    def verify_contact(self, **kwargs):
        self.calls.append(dict(kwargs))
        if self.code is not None:
            raise RecoveryContactVerificationServiceError(self.code)
        return RecoveryContactVerificationResult()


@pytest.fixture
def identity() -> SovereignIdentity:
    return SovereignIdentity(
        identity_id="WILSY-PRINCIPAL-R10E34",
        tenant_id=TENANT,
        username="r10e34",
        email="projection@example.invalid",
        roles=[],
        permissions=[],
        auth_method="jwt",
        status=PrincipalStatus.ACTIVE,
    )


@pytest.fixture
def service_doubles(monkeypatch, identity):
    recovery = _RecoveryRequestService()
    verification_request = _VerificationRequestService()
    verification_complete = _VerificationCompletionService()

    monkeypatch.setattr(auth_router, "_password_recovery_request_service", lambda: recovery)
    monkeypatch.setattr(
        auth_router,
        "_recovery_contact_verification_request_service",
        lambda: verification_request,
    )
    monkeypatch.setattr(
        auth_router,
        "_recovery_contact_verification_completion_service",
        lambda: verification_complete,
    )
    canonical_app.dependency_overrides[auth_router.get_current_identity] = lambda: identity
    try:
        yield recovery, verification_request, verification_complete
    finally:
        canonical_app.dependency_overrides.pop(auth_router.get_current_identity, None)


def _assert_secret_free(result: ASGIResult) -> None:
    rendered = result.text + repr(result.headers)
    assert RECOVERY_SENTINEL not in rendered
    assert VERIFICATION_SENTINEL not in rendered


def test_recovery_request_success_is_generic_202(service_doubles) -> None:
    recovery, _, _ = service_doubles
    result = _request(
        "POST",
        REQUEST_PATH,
        {"tenant_id": TENANT, "email": EMAIL},
    )

    assert result.raised is None
    assert result.status_code == 202
    assert len(recovery.calls) == 1
    assert recovery.calls[0]["tenant_id"] == TENANT
    assert recovery.calls[0]["email"] == EMAIL
    body = json.loads(result.text)
    assert body == {
        "status": "accepted",
        "message": "If recovery is available for this account, instructions will be sent.",
    }
    _assert_secret_free(result)


def test_recovery_internal_failure_remains_generic_202(service_doubles) -> None:
    recovery, _, _ = service_doubles
    recovery.mode = "internal"

    result = _request("POST", REQUEST_PATH, {"tenant_id": TENANT, "email": EMAIL})

    assert result.status_code == 202
    assert len(recovery.calls) == 1
    assert json.loads(result.text)["status"] == "accepted"


def test_recovery_rate_limit_is_uniform_429(service_doubles) -> None:
    recovery, _, _ = service_doubles
    recovery.mode = "rate"

    result = _request("POST", REQUEST_PATH, {"tenant_id": TENANT, "email": EMAIL})

    assert result.status_code == 429
    assert "too many" in result.text.lower()
    assert len(recovery.calls) == 1


@pytest.mark.parametrize("field", ["principal_id", "verified", "recovery_token", "password"])
def test_recovery_request_rejects_extra_authority_fields(service_doubles, field) -> None:
    recovery, _, _ = service_doubles
    payload = {"tenant_id": TENANT, "email": EMAIL, field: "caller-authority"}

    result = _request("POST", REQUEST_PATH, payload)

    assert result.status_code == 422
    assert recovery.calls == []


def test_authenticated_verification_request_accepts_no_body_and_uses_identity(
    service_doubles,
    identity,
) -> None:
    _, verification, _ = service_doubles

    result = _request("POST", VERIFY_REQUEST_PATH)

    assert result.status_code == 202
    assert len(verification.calls) == 1
    assert verification.calls[0]["identity"] == identity
    assert "observed_at" in verification.calls[0]
    assert json.loads(result.text) == {"status": "VERIFICATION_SENT"}


def test_authenticated_verification_not_required_is_projected(service_doubles) -> None:
    _, verification, _ = service_doubles
    verification.mode = "not-required"

    result = _request("POST", VERIFY_REQUEST_PATH)

    assert result.status_code == 202
    assert json.loads(result.text) == {"status": "VERIFICATION_NOT_REQUIRED"}


def test_authenticated_verification_rate_and_internal_failures_are_bounded(service_doubles) -> None:
    _, verification, _ = service_doubles
    verification.mode = "rate"
    rate = _request("POST", VERIFY_REQUEST_PATH)
    assert rate.status_code == 429

    verification.mode = "internal"
    internal = _request("POST", VERIFY_REQUEST_PATH)
    assert internal.status_code == 503
    assert "temporarily unavailable" in internal.text.lower()


def test_verification_completion_success_is_bodyless_204(service_doubles) -> None:
    _, _, completion = service_doubles

    result = _request(
        "POST",
        VERIFY_COMPLETE_PATH,
        {"tenant_id": TENANT, "verification_token": VERIFICATION_SENTINEL},
    )

    assert result.status_code == 204
    assert result.body == b""
    assert completion.calls == [
        {"tenant_id": TENANT, "verification_token": VERIFICATION_SENTINEL}
    ]
    _assert_secret_free(result)


@pytest.mark.parametrize(
    "code",
    [
        RecoveryContactVerificationCode.INVALID_REQUEST,
        RecoveryContactVerificationCode.VERIFICATION_INVALID,
        RecoveryContactVerificationCode.VERIFICATION_REPLAYED,
        RecoveryContactVerificationCode.PRINCIPAL_MISMATCH,
        RecoveryContactVerificationCode.EMAIL_CHANGED,
    ],
)
def test_verification_invalid_states_share_one_400_response(service_doubles, code) -> None:
    _, _, completion = service_doubles
    completion.code = code

    result = _request(
        "POST",
        VERIFY_COMPLETE_PATH,
        {"tenant_id": TENANT, "verification_token": VERIFICATION_SENTINEL},
    )

    assert result.status_code == 400
    assert "invalid or expired" in result.text.lower()
    _assert_secret_free(result)


@pytest.mark.parametrize(
    "code",
    [
        RecoveryContactVerificationCode.PERSISTENCE_FAILURE,
        RecoveryContactVerificationCode.TRANSACTION_FAILURE,
    ],
)
def test_verification_internal_failures_are_bounded_503(service_doubles, code) -> None:
    _, _, completion = service_doubles
    completion.code = code

    result = _request(
        "POST",
        VERIFY_COMPLETE_PATH,
        {"tenant_id": TENANT, "verification_token": VERIFICATION_SENTINEL},
    )

    assert result.status_code == 503
    assert "temporarily unavailable" in result.text.lower()
    _assert_secret_free(result)


@pytest.mark.parametrize("field", ["principal_id", "email", "verified", "contact_id"])
def test_verification_completion_rejects_extra_authority_fields(service_doubles, field) -> None:
    _, _, completion = service_doubles
    payload = {
        "tenant_id": TENANT,
        "verification_token": VERIFICATION_SENTINEL,
        field: "caller-authority",
    }

    result = _request("POST", VERIFY_COMPLETE_PATH, payload)

    assert result.status_code == 422
    assert completion.calls == []


def test_openapi_exposes_exact_recovery_authority_shapes() -> None:
    schema = canonical_app.openapi()

    request_operation = schema["paths"][REQUEST_PATH]["post"]
    request_ref = request_operation["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    request_model = schema["components"]["schemas"][request_ref.rsplit("/", 1)[-1]]
    assert set(request_model["properties"]) == {"tenant_id", "email"}
    assert request_model.get("additionalProperties") is False

    verify_request_operation = schema["paths"][VERIFY_REQUEST_PATH]["post"]
    assert "requestBody" not in verify_request_operation

    complete_operation = schema["paths"][VERIFY_COMPLETE_PATH]["post"]
    complete_ref = complete_operation["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    complete_model = schema["components"]["schemas"][complete_ref.rsplit("/", 1)[-1]]
    assert set(complete_model["properties"]) == {"tenant_id", "verification_token"}
    assert complete_model.get("additionalProperties") is False


def test_routes_are_post_only() -> None:
    for path in (REQUEST_PATH, VERIFY_REQUEST_PATH, VERIFY_COMPLETE_PATH):
        result = _request("GET", path)
        assert result.status_code == 405


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_password_recovery_engine_http.py
# VERSION: v1.0.2-R10E49-PASSWORD-RECOVERY-ENGINE-HTTP-MESSAGE-TYPE-CLOSURE
# AUTHORITY BOUNDARY: mounted ASGI transport evidence only
# TENANT POSTURE: public tenant values are selectors; authenticated route uses identity
# FAIL-CLOSED POSTURE: malformed/rate/invalid/internal states never become success
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
