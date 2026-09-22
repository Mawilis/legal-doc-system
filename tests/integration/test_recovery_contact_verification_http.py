"""Canonical ASGI certificate for recovery-contact verification HTTP authority.

TITLE: WILSY OS Recovery Contact Verification HTTP ASGI Certificate
VERSION: v1.1.0-R10E29-DELIVERY-INDEPENDENT-HTTP-COMPLETION-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies authenticated initiation/completion transport for explicit
         recovery-contact possession verification without MongoDB, Node, SMTP,
         or browser-asserted tenant/principal/VERIFIED authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_recovery_contact_verification_http.py
COLLABORATION / OWNERSHIP: Exercises tools.eos.api.server.app and the real auth
                           router while replacing only identity/service delivery
                           collaborators with deterministic test doubles.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.1.0-R10E29-DELIVERY-INDEPENDENT-HTTP-COMPLETION-CERT — Adds mounted evidence that completion never constructs the
  Node delivery adapter and remains available after challenge delivery even when
  transport configuration is absent, while initiation still requires delivery.
  v1.0.0-R10E19-RECOVERY-CONTACT-VERIFICATION-HTTP-ASGI-CERT — Adds mounted ASGI evidence for ACCESS-bound tenant/principal
  identity, strict initiation/completion request shapes, bodyless 202/204 success,
  bounded service/delivery failures, route uniqueness, and no recovery-secret
  response projection.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic addresses and bearer values only; no live
                            Mongo, Node, SMTP, provider credentials, or secrets.
TENANT BOUNDARY: tenant/principal binding comes only from protected ACCESS identity.
AUTHORITY BOUNDARY: HTTP transport evidence only; Python services own verification.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusively financial.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any

import pytest
from fastapi import HTTPException

from tools.eos.api import auth_router
from tools.eos.api.server import app as canonical_app
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.saas.auth.recovery_contact_verification_delivery import (
    RecoveryContactVerificationDeliveryCode,
    RecoveryContactVerificationDeliveryError,
)
from tools.eos.saas.auth.recovery_contact_verification_service import (
    RecoveryContactVerificationServiceCode,
    RecoveryContactVerificationServiceError,
)


REQUEST_PATH = "/api/auth/recovery-contact/verification"
COMPLETE_PATH = "/api/auth/recovery-contact/verification/complete"
TENANT_SENTINEL = "TENANT-R10E19"
PRINCIPAL_SENTINEL = "PRINCIPAL-R10E19"
ADDRESS_SENTINEL = "recovery-r10e19@example.com"
TOKEN_SENTINEL = "R10E19-" + ("x" * 40)


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
    *, method: str, path: str, payload: bytes = b"", headers: dict[str, str] | None = None
) -> ASGIResult:
    supplied = {key.lower(): value for key, value in (headers or {}).items()}
    supplied.setdefault("host", "r10e19.test")
    supplied.setdefault("content-length", str(len(payload)))
    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": b"",
        "headers": [
            (key.encode("latin-1"), value.encode("latin-1"))
            for key, value in supplied.items()
        ],
        "client": ("r10e19-test", 1),
        "server": ("r10e19-asgi", 80),
        "root_path": "",
    }
    incoming = [{"type": "http.request", "body": payload, "more_body": False}]
    messages: list[dict[str, Any]] = []

    async def receive() -> dict[str, Any]:
        if incoming:
            return incoming.pop(0)
        return {"type": "http.disconnect"}

    async def send(message: dict[str, Any]) -> None:
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


def _json(payload: object) -> bytes:
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")


def _post(path: str, payload: object) -> ASGIResult:
    return asyncio.run(
        _invoke_asgi(
            method="POST",
            path=path,
            payload=_json(payload),
            headers={"content-type": "application/json"},
        )
    )


@pytest.fixture(autouse=True)
def _clean_dependency_override() -> Any:
    original = dict(canonical_app.dependency_overrides)
    try:
        yield
    finally:
        canonical_app.dependency_overrides.clear()
        canonical_app.dependency_overrides.update(original)


@pytest.fixture
def identity() -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=PRINCIPAL_SENTINEL,
        tenant_id=TENANT_SENTINEL,
        email="login-r10e19@example.com",
        roles=[],
        permissions=[],
        auth_method="ACCESS",
        status=PrincipalStatus.ACTIVE,
    )


@pytest.fixture
def service_calls(
    monkeypatch: pytest.MonkeyPatch,
    identity: SovereignIdentity,
) -> list[tuple[str, dict[str, str]]]:
    calls: list[tuple[str, dict[str, str]]] = []
    canonical_app.dependency_overrides[auth_router.get_current_identity] = lambda: identity

    class FakeDelivery:
        pass

    class FakeService:
        def __init__(self, *, delivery: object | None = None) -> None:
            if delivery is not None:
                assert isinstance(delivery, FakeDelivery)

        def request_verification(
            self, *, tenant_id: str, principal_id: str, address: str
        ) -> object:
            calls.append(
                (
                    "request",
                    {
                        "tenant_id": tenant_id,
                        "principal_id": principal_id,
                        "address": address,
                    },
                )
            )
            return object()

        def complete_verification(
            self, *, tenant_id: str, principal_id: str, verification_token: str
        ) -> object:
            calls.append(
                (
                    "complete",
                    {
                        "tenant_id": tenant_id,
                        "principal_id": principal_id,
                        "verification_token": verification_token,
                    },
                )
            )
            return object()

    monkeypatch.setattr(auth_router, "NodeRecoveryContactVerificationDelivery", FakeDelivery)
    monkeypatch.setattr(auth_router, "RecoveryContactVerificationService", FakeService)
    return calls


def test_initiation_is_bodyless_202_and_binds_access_identity(
    service_calls: list[tuple[str, dict[str, str]]],
) -> None:
    result = _post(REQUEST_PATH, {"address": ADDRESS_SENTINEL})
    assert result.raised is None
    assert result.status_code == 202
    assert result.body == b""
    assert service_calls == [
        (
            "request",
            {
                "tenant_id": TENANT_SENTINEL,
                "principal_id": PRINCIPAL_SENTINEL,
                "address": ADDRESS_SENTINEL,
            },
        )
    ]
    assert ADDRESS_SENTINEL not in result.text
    assert PRINCIPAL_SENTINEL not in result.text
    assert TENANT_SENTINEL not in result.text


def test_completion_is_bodyless_204_and_binds_access_identity(
    service_calls: list[tuple[str, dict[str, str]]],
) -> None:
    result = _post(COMPLETE_PATH, {"verification_token": TOKEN_SENTINEL})
    assert result.raised is None
    assert result.status_code == 204
    assert result.body == b""
    assert service_calls == [
        (
            "complete",
            {
                "tenant_id": TENANT_SENTINEL,
                "principal_id": PRINCIPAL_SENTINEL,
                "verification_token": TOKEN_SENTINEL,
            },
        )
    ]
    assert TOKEN_SENTINEL not in result.text


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        (REQUEST_PATH, {}),
        (REQUEST_PATH, {"address": ADDRESS_SENTINEL, "tenant_id": "forbidden"}),
        (REQUEST_PATH, {"address": ADDRESS_SENTINEL, "principal_id": "forbidden"}),
        (REQUEST_PATH, {"address": ADDRESS_SENTINEL, "verified": True}),
        (COMPLETE_PATH, {}),
        (COMPLETE_PATH, {"verification_token": TOKEN_SENTINEL, "tenant_id": "forbidden"}),
        (COMPLETE_PATH, {"verification_token": TOKEN_SENTINEL, "principal_id": "forbidden"}),
        (COMPLETE_PATH, {"verification_token": "short"}),
    ],
)
def test_malformed_or_caller_authority_fields_are_422_and_call_nothing(
    service_calls: list[tuple[str, dict[str, str]]],
    path: str,
    payload: object,
) -> None:
    result = _post(path, payload)
    assert result.status_code == 422
    assert service_calls == []


def test_access_identity_dependency_is_required(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reject() -> None:
        raise HTTPException(status_code=401, detail="authentication required")

    canonical_app.dependency_overrides[auth_router.get_current_identity] = reject

    class ForbiddenService:
        def __init__(self, **_: object) -> None:
            raise AssertionError("service must not construct before ACCESS identity")

    monkeypatch.setattr(auth_router, "RecoveryContactVerificationService", ForbiddenService)
    assert _post(REQUEST_PATH, {"address": ADDRESS_SENTINEL}).status_code == 401
    assert _post(COMPLETE_PATH, {"verification_token": TOKEN_SENTINEL}).status_code == 401


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        (RecoveryContactVerificationServiceCode.INVALID_REQUEST, 400),
        (RecoveryContactVerificationServiceCode.CHALLENGE_INVALID, 400),
        (RecoveryContactVerificationServiceCode.PRINCIPAL_UNAVAILABLE, 403),
        (RecoveryContactVerificationServiceCode.REPLACEMENT_FORBIDDEN, 409),
        (RecoveryContactVerificationServiceCode.PERSISTENCE_FAILURE, 503),
        (RecoveryContactVerificationServiceCode.TRANSACTION_FAILURE, 503),
        (RecoveryContactVerificationServiceCode.DELIVERY_FAILURE, 503),
    ],
)
def test_service_failures_map_to_bounded_http_status(
    monkeypatch: pytest.MonkeyPatch,
    identity: SovereignIdentity,
    code: RecoveryContactVerificationServiceCode,
    expected: int,
) -> None:
    canonical_app.dependency_overrides[auth_router.get_current_identity] = lambda: identity

    class FakeDelivery:
        pass

    class FailingService:
        def __init__(self, *, delivery: object | None = None) -> None:
            if delivery is not None:
                assert isinstance(delivery, FakeDelivery)

        def request_verification(self, **_: object) -> object:
            raise RecoveryContactVerificationServiceError(code)

        def complete_verification(self, **_: object) -> object:
            raise RecoveryContactVerificationServiceError(code)

    monkeypatch.setattr(auth_router, "NodeRecoveryContactVerificationDelivery", FakeDelivery)
    monkeypatch.setattr(auth_router, "RecoveryContactVerificationService", FailingService)

    assert _post(REQUEST_PATH, {"address": ADDRESS_SENTINEL}).status_code == expected
    assert _post(COMPLETE_PATH, {"verification_token": TOKEN_SENTINEL}).status_code == expected


def test_completion_never_constructs_delivery_adapter(
    monkeypatch: pytest.MonkeyPatch,
    identity: SovereignIdentity,
) -> None:
    canonical_app.dependency_overrides[auth_router.get_current_identity] = lambda: identity

    class ForbiddenDelivery:
        def __init__(self) -> None:
            raise AssertionError("completion must not construct delivery transport")

    class CompletionOnlyService:
        def __init__(self, *, delivery: object | None = None) -> None:
            assert delivery is None

        def complete_verification(self, **kwargs: object) -> object:
            assert kwargs == {
                "tenant_id": TENANT_SENTINEL,
                "principal_id": PRINCIPAL_SENTINEL,
                "verification_token": TOKEN_SENTINEL,
            }
            return object()

    monkeypatch.setattr(auth_router, "NodeRecoveryContactVerificationDelivery", ForbiddenDelivery)
    monkeypatch.setattr(auth_router, "RecoveryContactVerificationService", CompletionOnlyService)

    result = _post(COMPLETE_PATH, {"verification_token": TOKEN_SENTINEL})
    assert result.raised is None
    assert result.status_code == 204
    assert result.body == b""


def test_delivery_configuration_failure_is_503_without_secret_projection(
    monkeypatch: pytest.MonkeyPatch,
    identity: SovereignIdentity,
) -> None:
    canonical_app.dependency_overrides[auth_router.get_current_identity] = lambda: identity

    class FailingDelivery:
        def __init__(self) -> None:
            raise RecoveryContactVerificationDeliveryError(
                RecoveryContactVerificationDeliveryCode.CONFIGURATION_INVALID
            )

    monkeypatch.setattr(auth_router, "NodeRecoveryContactVerificationDelivery", FailingDelivery)
    result = _post(REQUEST_PATH, {"address": ADDRESS_SENTINEL})
    assert result.status_code == 503
    assert ADDRESS_SENTINEL not in result.text


def test_route_shape_and_openapi_are_exact() -> None:
    schema = canonical_app.openapi()
    assert REQUEST_PATH in schema["paths"]
    assert COMPLETE_PATH in schema["paths"]
    assert set(schema["paths"][REQUEST_PATH]) == {"post"}
    assert set(schema["paths"][COMPLETE_PATH]) == {"post"}

    request_operation = schema["paths"][REQUEST_PATH]["post"]
    completion_operation = schema["paths"][COMPLETE_PATH]["post"]
    request_ref = request_operation["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    completion_ref = completion_operation["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    request_model = schema["components"]["schemas"][request_ref.rsplit("/", 1)[-1]]
    completion_model = schema["components"]["schemas"][completion_ref.rsplit("/", 1)[-1]]

    assert set(request_model["properties"]) == {"address"}
    assert set(request_model["required"]) == {"address"}
    assert set(completion_model["properties"]) == {"verification_token"}
    assert set(completion_model["required"]) == {"verification_token"}

    rendered = json.dumps(
        {"request": request_operation, "completion": completion_operation},
        sort_keys=True,
    )
    assert "tenant_id" not in rendered
    assert "principal_id" not in rendered
    assert "verified" not in rendered


def test_effective_routes_are_each_mounted_once() -> None:
    for path in (REQUEST_PATH, COMPLETE_PATH):
        matching = [
            route
            for route in canonical_app.routes
            if getattr(route, "path", None) == path
        ]
        assert len(matching) == 1
        assert matching[0].methods == {"POST"}


# ARTIFACT: tests/integration/test_recovery_contact_verification_http.py
# VERSION: v1.1.0-R10E29-DELIVERY-INDEPENDENT-HTTP-COMPLETION-CERT
# AUTHORITY BOUNDARY: mounted ASGI recovery-contact verification transport evidence only
# TENANT POSTURE: tenant/principal binding derives only from protected ACCESS identity
# FAIL-CLOSED POSTURE: malformed, caller-authority, lifecycle, delivery, and persistence failures do not verify contact
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusively financial
# END OF WILSY OS SOVEREIGN ARTIFACT
