"""Canonical ASGI certificate for enumeration-safe password-recovery initiation.

TITLE: WILSY OS Password Recovery Request HTTP ASGI Certificate
VERSION: v1.1.0-R10E30-ENUMERATION-SAFE-EDGE-THROTTLE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the mounted public Forgot Password initiation route, bodyless
         202 contract, strict request shape, and post-response work scheduling
         without MongoDB, Node, SMTP, sockets, or recovery issuance.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_password_recovery_request_http.py
COLLABORATION / OWNERSHIP: Exercises tools.eos.api.server.app and the real auth
                           router while patching only the background worker.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.1.0-R10E30-ENUMERATION-SAFE-EDGE-THROTTLE-CERT — Certifies enumeration-safe process-local edge throttling:
    permitted requests still schedule exactly one background task, throttled
    requests retain the identical bodyless 202 and schedule none, and account
    email never becomes visible in the public response contract.
  v1.0.0-R10E8-PASSWORD-RECOVERY-REQUEST-HTTP-ASGI-CERT — Adds in-process ASGI evidence for
    canonical /api prefix, public unauthenticated 202 acceptance, strict body
    validation, exact background scheduling, no account-state projection, route
    uniqueness, OpenAPI shape, and preservation of reset completion.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic email/tenant selectors only; no recovery
                            bearer or password enters this certificate.
TENANT BOUNDARY: tenant_id remains a request selector, never browser authority.
AUTHORITY BOUNDARY: HTTP transport evidence only; issuance/delivery stay separate.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusively financial.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any

import pytest

from tools.eos.api import auth_router
from tools.eos.api.server import app as canonical_app


PUBLIC_PATH = "/api/auth/request-password-reset"
RESET_PATH = "/api/auth/reset-password"
RAW_ROUTER_PATH = "/auth/request-password-reset"
DOUBLE_API_PATH = "/api/api/auth/request-password-reset"
EMAIL_SENTINEL = "person-r10e8@example.com"
TENANT_SENTINEL = "TENANT-R10E8"


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
    supplied.setdefault("host", "r10e8.test")
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
        "client": ("r10e8-test", 1),
        "server": ("r10e8-asgi", 80),
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


def _request(
    payload: object, *, method: str = "POST", path: str = PUBLIC_PATH
) -> ASGIResult:
    return asyncio.run(
        _invoke_asgi(
            method=method,
            path=path,
            payload=_json(payload),
            headers={"content-type": "application/json"},
        )
    )


@pytest.fixture
def background_calls(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, str]]:
    calls: list[tuple[str, str]] = []

    def record(tenant_id: str, email: str) -> None:
        calls.append((tenant_id, email))

    monkeypatch.setattr(auth_router, "_execute_password_recovery_request", record)
    monkeypatch.setattr(auth_router, "_password_recovery_edge_allowed", lambda *_args: True)
    return calls


def _valid_payload() -> dict[str, str]:
    return {"tenant_id": TENANT_SENTINEL, "email": EMAIL_SENTINEL}


def test_public_request_is_bodyless_202_and_schedules_one_background_call(
    background_calls: list[tuple[str, str]],
) -> None:
    result = _request(_valid_payload())
    assert result.raised is None
    assert result.status_code == 202
    assert result.body == b""
    assert background_calls == [(TENANT_SENTINEL, EMAIL_SENTINEL)]
    rendered_headers = repr(result.headers)
    assert EMAIL_SENTINEL not in result.text and EMAIL_SENTINEL not in rendered_headers
    assert TENANT_SENTINEL not in result.text and TENANT_SENTINEL not in rendered_headers


def test_edge_throttle_preserves_bodyless_202_and_schedules_nothing(
    monkeypatch: pytest.MonkeyPatch,
    background_calls: list[tuple[str, str]],
) -> None:
    monkeypatch.setattr(auth_router, "_password_recovery_edge_allowed", lambda *_args: False)

    result = _request(_valid_payload())

    assert result.raised is None
    assert result.status_code == 202
    assert result.body == b""
    assert background_calls == []
    assert EMAIL_SENTINEL not in result.text
    assert TENANT_SENTINEL not in result.text


def test_route_is_public_and_does_not_require_access_bearer(
    background_calls: list[tuple[str, str]],
) -> None:
    result = asyncio.run(
        _invoke_asgi(
            method="POST",
            path=PUBLIC_PATH,
            payload=_json(_valid_payload()),
            headers={"content-type": "application/json"},
        )
    )
    assert result.status_code == 202
    assert "authorization" not in result.headers
    assert background_calls == [(TENANT_SENTINEL, EMAIL_SENTINEL)]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"tenant_id": TENANT_SENTINEL},
        {"email": EMAIL_SENTINEL},
        {"tenant_id": 7, "email": EMAIL_SENTINEL},
        {"tenant_id": TENANT_SENTINEL, "email": {"value": EMAIL_SENTINEL}},
        {"tenant_id": TENANT_SENTINEL, "email": EMAIL_SENTINEL, "principal_id": "forbidden"},
        {"tenant_id": TENANT_SENTINEL, "email": EMAIL_SENTINEL, "recovery_token": "forbidden"},
    ],
)
def test_malformed_or_extra_authority_fields_are_422_and_schedule_nothing(
    background_calls: list[tuple[str, str]], payload: object
) -> None:
    result = _request(payload)
    assert result.status_code == 422
    assert background_calls == []
    assert EMAIL_SENTINEL not in result.text


def test_path_and_method_shape_are_exact(
    background_calls: list[tuple[str, str]],
) -> None:
    assert _request(_valid_payload(), method="GET").status_code == 405
    assert _request(_valid_payload(), path=RAW_ROUTER_PATH).status_code == 404
    assert _request(_valid_payload(), path=DOUBLE_API_PATH).status_code == 404
    assert background_calls == []


def test_openapi_projects_only_tenant_and_email_and_preserves_reset_route() -> None:
    schema = canonical_app.openapi()
    assert PUBLIC_PATH in schema["paths"]
    assert set(schema["paths"][PUBLIC_PATH]) == {"post"}
    assert RESET_PATH in schema["paths"]
    operation = schema["paths"][PUBLIC_PATH]["post"]
    assert operation["responses"]["202"]["description"]
    request_ref = operation["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    model_name = request_ref.rsplit("/", 1)[-1]
    model = schema["components"]["schemas"][model_name]
    assert set(model["properties"]) == {"tenant_id", "email"}
    assert set(model["required"]) == {"tenant_id", "email"}
    assert "recovery_token" not in json.dumps(operation)
    assert "principal_id" not in json.dumps(operation)


def test_effective_route_is_mounted_once() -> None:
    matching = [
        route
        for route in canonical_app.routes
        if getattr(route, "path", None) == PUBLIC_PATH
    ]
    assert len(matching) == 1
    assert matching[0].methods == {"POST"}


# ARTIFACT: tests/integration/test_password_recovery_request_http.py
# VERSION: v1.1.0-R10E30-ENUMERATION-SAFE-EDGE-THROTTLE-CERT
# AUTHORITY BOUNDARY: canonical ASGI recovery-initiation transport evidence only
# TENANT POSTURE: tenant_id is selector-only and never grants membership
# FAIL-CLOSED POSTURE: malformed/extra caller authority cannot schedule recovery work
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
