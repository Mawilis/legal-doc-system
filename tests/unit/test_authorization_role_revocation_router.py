"""
Direct certificate for the governed authorization-role revocation HTTP router.

VERSION:
v1.0.0-P1-R3D-B1-AUTHORIZATION-ROLE-REVOCATION-ROUTER-DIRECT-CERT
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, cast

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

import tools.eos.api.authorization_role_revocation_router as subject
from tools.eos.api.tenant_authorization_http import (
    TenantAuthorizationContext,
)
from tools.eos.auth.authorization_role_revocation_command import (
    AuthorizationRoleRevocationCommandAuthorizationDeniedError,
    AuthorizationRoleRevocationCommandPolicyDeniedError,
    AuthorizationRoleRevocationCommandReplayConflictError,
    AuthorizationRoleRevocationCommandTargetInvalidError,
    AuthorizationRoleRevocationResultState,
)


class _Session:
    def __init__(self) -> None:
        self.started = 0
        self.committed = 0
        self.aborted = 0
        self.in_transaction = False

    def __enter__(self) -> "_Session":
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc: Any,
        tb: Any,
    ) -> None:
        return None

    def start_transaction(self) -> None:
        self.started += 1
        self.in_transaction = True

    def commit_transaction(self) -> None:
        self.committed += 1
        self.in_transaction = False

    def abort_transaction(self) -> None:
        self.aborted += 1
        self.in_transaction = False


class _Client:
    def __init__(self, session: _Session) -> None:
        self.session = session
        self.started_sessions = 0

    def start_session(self) -> _Session:
        self.started_sessions += 1
        return self.session


class _LabeledError(RuntimeError):
    def __init__(self, label: str) -> None:
        super().__init__(label)
        self.label = label

    def has_error_label(
        self,
        label: str,
    ) -> bool:
        return label == self.label


@dataclass(frozen=True)
class _Evidence:
    revocation_id: str
    tenant_id: str
    actor_principal_id: str
    target_principal_id: str
    target_role_id: str
    target_assignment_prior_revision: int
    target_assignment_result_revision: int
    operation: str
    reason_reference: str
    authorization_evidence_reference: str
    authorization_evidence_fingerprint: str
    idempotency_key: str
    revoked_at: str
    revocation_evidence_fingerprint: str


@dataclass(frozen=True)
class _Assignment:
    principal_id: str
    tenant_id: str
    role_id: str
    status: str
    revision: int


@dataclass(frozen=True)
class _Result:
    state: AuthorizationRoleRevocationResultState
    revocation_evidence: _Evidence
    resulting_role_assignment: _Assignment


def _command() -> subject.AuthorizationRoleRevocationHttpCommand:
    return subject.AuthorizationRoleRevocationHttpCommand(
        target_principal_id="target-principal",
        target_role_id="AUDITOR",
        expected_target_assignment_revision=0,
        reason_reference="case:P1-R3D-B1",
        idempotency_key="idempotency-p1-r3d-b1",
    )


def _context() -> TenantAuthorizationContext:
    return cast(
        TenantAuthorizationContext,
        SimpleNamespace(
            identity=SimpleNamespace(
                identity_id="actor-principal"
            ),
            tenant_id="tenant-alpha",
            decision=SimpleNamespace(),
        ),
    )


def _result() -> _Result:
    return _Result(
        state=AuthorizationRoleRevocationResultState.NEWLY_REVOKED,
        revocation_evidence=_Evidence(
            revocation_id="revocation-1",
            tenant_id="tenant-alpha",
            actor_principal_id="actor-principal",
            target_principal_id="target-principal",
            target_role_id="AUDITOR",
            target_assignment_prior_revision=0,
            target_assignment_result_revision=1,
            operation="role_revoke",
            reason_reference="case:P1-R3D-B1",
            authorization_evidence_reference="auth-evidence-1",
            authorization_evidence_fingerprint="a" * 128,
            idempotency_key="idempotency-p1-r3d-b1",
            revoked_at="2026-10-14T00:00:00+00:00",
            revocation_evidence_fingerprint="b" * 128,
        ),
        resulting_role_assignment=_Assignment(
            principal_id="target-principal",
            tenant_id="tenant-alpha",
            role_id="AUDITOR",
            status="REVOKED",
            revision=1,
        ),
    )


def test_body_forbids_actor_and_tenant_authority() -> None:
    with pytest.raises(ValidationError):
        subject.AuthorizationRoleRevocationHttpCommand.model_validate(
            {
                "target_principal_id": "target",
                "target_role_id": "AUDITOR",
                "expected_target_assignment_revision": 0,
                "reason_reference": "case:1",
                "idempotency_key": "idem-1",
                "actor_principal_id": "attacker",
            }
        )

    with pytest.raises(ValidationError):
        subject.AuthorizationRoleRevocationHttpCommand.model_validate(
            {
                "target_principal_id": "target",
                "target_role_id": "AUDITOR",
                "expected_target_assignment_revision": 0,
                "reason_reference": "case:1",
                "idempotency_key": "idem-1",
                "tenant_id": "foreign",
            }
        )


def test_body_requires_trimmed_command_material() -> None:
    for field in (
        "target_principal_id",
        "target_role_id",
        "reason_reference",
        "idempotency_key",
    ):
        values: dict[str, Any] = {
            "target_principal_id": "target",
            "target_role_id": "AUDITOR",
            "expected_target_assignment_revision": 0,
            "reason_reference": "case:1",
            "idempotency_key": "idem-1",
        }

        values[field] = " invalid "

        with pytest.raises(ValidationError):
            subject.AuthorizationRoleRevocationHttpCommand(
                **values
            )


def test_transaction_commits_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _Session()
    client = _Client(session)
    database = object()

    monkeypatch.setattr(
        subject,
        "get_client",
        lambda: client,
    )
    monkeypatch.setattr(
        subject,
        "get_database",
        lambda: database,
    )

    seen: list[tuple[Any, Any]] = []

    def callback(
        passed_session: Any,
        passed_database: Any,
    ) -> str:
        seen.append(
            (
                passed_session,
                passed_database,
            )
        )
        return "ok"

    assert subject._transaction(callback) == "ok"

    assert seen == [(session, database)]
    assert client.started_sessions == 1
    assert session.started == 1
    assert session.committed == 1
    assert session.aborted == 0


def test_transaction_aborts_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _Session()
    client = _Client(session)

    monkeypatch.setattr(
        subject,
        "get_client",
        lambda: client,
    )
    monkeypatch.setattr(
        subject,
        "get_database",
        lambda: object(),
    )

    class Failure(RuntimeError):
        pass

    def callback(
        passed_session: Any,
        passed_database: Any,
    ) -> str:
        del passed_session, passed_database
        raise Failure("stop")

    with pytest.raises(Failure):
        subject._transaction(callback)

    assert session.started == 1
    assert session.committed == 0
    assert session.aborted == 1


@pytest.mark.parametrize(
    ("label", "detail"),
    (
        (
            "TransientTransactionError",
            "AUTHORIZATION_ROLE_REVOCATION_RETRY_REQUIRED",
        ),
        (
            "UnknownTransactionCommitResult",
            "AUTHORIZATION_ROLE_REVOCATION_RECONCILIATION_REQUIRED",
        ),
    ),
)
def test_transaction_labels_are_bounded_409(
    monkeypatch: pytest.MonkeyPatch,
    label: str,
    detail: str,
) -> None:
    session = _Session()
    client = _Client(session)

    monkeypatch.setattr(
        subject,
        "get_client",
        lambda: client,
    )
    monkeypatch.setattr(
        subject,
        "get_database",
        lambda: object(),
    )

    def callback(
        passed_session: Any,
        passed_database: Any,
    ) -> str:
        del passed_session, passed_database
        raise _LabeledError(label)

    with pytest.raises(HTTPException) as caught:
        subject._transaction(callback)

    assert caught.value.status_code == 409
    assert caught.value.detail == detail
    assert session.aborted == 1


def test_missing_persistence_is_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        subject,
        "get_client",
        lambda: None,
    )
    monkeypatch.setattr(
        subject,
        "get_database",
        lambda: None,
    )

    with pytest.raises(HTTPException) as caught:
        subject._transaction(
            lambda session, database: None
        )

    assert caught.value.status_code == 503
    assert (
        caught.value.detail
        == "AUTHORIZATION_ROLE_REVOCATION_PERSISTENCE_UNAVAILABLE"
    )


@pytest.mark.parametrize(
    ("error", "status_code", "detail"),
    (
        (
            AuthorizationRoleRevocationCommandReplayConflictError(
                "IDEMPOTENCY_DIVERGENT_REPLAY"
            ),
            409,
            "AUTHORIZATION_ROLE_REVOCATION_REPLAY_CONFLICT",
        ),
        (
            AuthorizationRoleRevocationCommandAuthorizationDeniedError(
                "CURRENT_AUTHORIZATION_DENIED"
            ),
            403,
            "AUTHORIZATION_ROLE_REVOCATION_AUTHORIZATION_REQUIRED",
        ),
        (
            AuthorizationRoleRevocationCommandPolicyDeniedError(
                "REVOCATION_POLICY_DENIED"
            ),
            403,
            "AUTHORIZATION_ROLE_REVOCATION_POLICY_DENIED",
        ),
        (
            AuthorizationRoleRevocationCommandTargetInvalidError(
                "TARGET_ASSIGNMENT_UNAVAILABLE"
            ),
            404,
            "AUTHORIZATION_ROLE_REVOCATION_TARGET_NOT_AVAILABLE",
        ),
        (
            AuthorizationRoleRevocationCommandTargetInvalidError(
                "TARGET_ASSIGNMENT_NOT_CURRENT"
            ),
            409,
            "AUTHORIZATION_ROLE_REVOCATION_TARGET_CONFLICT",
        ),
    ),
)
def test_command_error_map(
    error: BaseException,
    status_code: int,
    detail: str,
) -> None:
    http_error = subject._http_error(error)

    assert http_error.status_code == status_code
    assert http_error.detail == detail


def test_endpoint_derives_actor_and_tenant_from_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _Session()
    client = _Client(session)
    database = object()
    captured: dict[str, Any] = {}

    class FakeProductionCommand:
        def execute(
            self,
            **kwargs: Any,
        ) -> Any:
            captured.update(kwargs)
            return _result()

    monkeypatch.setattr(
        subject,
        "get_client",
        lambda: client,
    )
    monkeypatch.setattr(
        subject,
        "get_database",
        lambda: database,
    )
    monkeypatch.setattr(
        subject,
        "_build_command",
        lambda passed_database: (
            FakeProductionCommand()
            if passed_database is database
            else (_ for _ in ()).throw(
                AssertionError(
                    "wrong database"
                )
            )
        ),
    )

    response = asyncio.run(
        subject.revoke_authorization_role(
            _command(),
            _context(),
        )
    )

    assert response["data"]["state"] == (
        AuthorizationRoleRevocationResultState.NEWLY_REVOKED
    )

    assert captured[
        "actor_principal_id"
    ] == "actor-principal"

    assert captured[
        "tenant_id"
    ] == "tenant-alpha"

    assert captured[
        "target_principal_id"
    ] == "target-principal"

    assert captured[
        "target_role_id"
    ] == "AUDITOR"

    assert captured[
        "expected_target_assignment_revision"
    ] == 0

    assert captured[
        "reason_reference"
    ] == "case:P1-R3D-B1"

    assert captured[
        "idempotency_key"
    ] == "idempotency-p1-r3d-b1"

    assert captured["session"] is session

    assert session.committed == 1
    assert session.aborted == 0


def test_endpoint_failure_aborts_and_maps(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _Session()
    client = _Client(session)

    class FakeProductionCommand:
        def execute(
            self,
            **kwargs: Any,
        ) -> Any:
            del kwargs
            raise (
                AuthorizationRoleRevocationCommandPolicyDeniedError(
                    "REVOCATION_POLICY_DENIED"
                )
            )

    monkeypatch.setattr(
        subject,
        "get_client",
        lambda: client,
    )
    monkeypatch.setattr(
        subject,
        "get_database",
        lambda: object(),
    )
    monkeypatch.setattr(
        subject,
        "_build_command",
        lambda database: FakeProductionCommand(),
    )

    with pytest.raises(HTTPException) as caught:
        asyncio.run(
            subject.revoke_authorization_role(
                _command(),
                _context(),
            )
        )

    assert caught.value.status_code == 403
    assert (
        caught.value.detail
        == "AUTHORIZATION_ROLE_REVOCATION_POLICY_DENIED"
    )

    assert session.committed == 0
    assert session.aborted == 1


def test_router_contract_is_exact() -> None:
    routes = [
        route
        for route in subject.router.routes
        if getattr(route, "path", None)
        == "/tenants/role-assignments/revocations"
    ]

    assert len(routes) == 1

    route = routes[0]

    assert getattr(
        route,
        "methods",
        set(),
    ) == {"POST"}


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_authorization_role_revocation_router.py
# VERSION: v1.0.0-P1-R3D-B1-AUTHORIZATION-ROLE-REVOCATION-ROUTER-DIRECT-CERT
# AUTHORITY BOUNDARY: direct HTTP-host composition certificate only; no production Mongo, server mount, root lifecycle, JIT, break-glass, session lifecycle, or finance
# TENANT POSTURE: request body cannot assert actor or tenant; exact context identity and tenant are passed to the unchanged certified command
# FAIL-CLOSED POSTURE: transaction failure aborts; bounded authorization, policy, target, replay, retry, reconciliation, and persistence errors expose no partial success
# FINANCIAL EXECUTION AUTHORITY: None. Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
