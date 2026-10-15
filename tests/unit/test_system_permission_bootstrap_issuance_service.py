"""TITLE: D11-R5 bootstrap issuance service direct certificate.
VERSION: v1.0.0-P4-R4-D11-R5-ISSUANCE-SERVICE-CERTIFICATE
AUTHORITY: Direct composition, replay, and negative-authority proof.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_system_permission_bootstrap_issuance_service.py
CERTIFICATION DATE: 2026-10-14
CHANGELOG: v1.0.0 proves caller-owned transaction issuance semantics.
BOUNDARY: No permission mutation, activation, break-glass, or finance.
"""
from __future__ import annotations

import base64
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.system_permission_bootstrap_authority import SystemPermissionBootstrapAuthority
from tools.eos.auth.system_permission_bootstrap_authority_registry import SystemPermissionBootstrapAuthorityConflictError
from tools.eos.auth.system_permission_bootstrap_creation_authorization import SystemPermissionBootstrapCreationAuthorization
from tools.eos.auth.system_permission_bootstrap_creation_trust import OPERATION, SCOPE, SystemPermissionBootstrapCreationTrustedKey, SystemPermissionBootstrapCreationTrustRoot, SystemPermissionBootstrapCreationTrustStatus
from tools.eos.auth.system_permission_bootstrap_issuance_service import SystemPermissionBootstrapIssuanceError, SystemPermissionBootstrapIssuanceService

NOW = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc)
PURPOSE = "SEED_SYSTEM_PERMISSION_ASSIGNMENT_COMMAND_AUTHORITY"


class _Session:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active
        self.lifecycle_calls: list[str] = []


class _PrincipalCollection:
    def __init__(self, rows: dict[str, str]) -> None:
        self.rows = rows
        self.sessions: list[object] = []

    def find_one(self, query: dict[str, object], *, session: object = None) -> dict[str, object] | None:
        self.sessions.append(session)
        principal_id = query["principal_id"]
        status = self.rows.get(str(principal_id))
        return None if status is None else {"principal_id": principal_id, "status": status, "revision": 1}


class _Registry:
    def __init__(self) -> None:
        self.rows: dict[str, tuple[object, str]] = {}
        self.sessions: list[object] = []

    def create_or_replay(self, authority: object, *, idempotency_key: str, session: object) -> Any:
        self.sessions.append(session)
        existing = self.rows.get(idempotency_key)
        if existing is None:
            self.rows[idempotency_key] = (authority, idempotency_key)
            return authority
        prior = existing[0]
        if prior != authority:
            raise SystemPermissionBootstrapAuthorityConflictError("BOOTSTRAP_CREATE_REPLAY_CONFLICT")
        return prior


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _authorization() -> tuple[SystemPermissionBootstrapCreationAuthorization, SystemPermissionBootstrapCreationTrustRoot]:
    private = Ed25519PrivateKey.generate()
    public = _b64(private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw))
    key = SystemPermissionBootstrapCreationTrustedKey.create(
        creator_principal_id="principal-creator",
        public_key_base64url=public,
        valid_from=NOW - timedelta(hours=1),
        valid_until=NOW + timedelta(hours=1),
        status=SystemPermissionBootstrapCreationTrustStatus.ACTIVE,
        revision=1,
        provenance="installation-ceremony:evidence-1",
    )
    unsigned = SystemPermissionBootstrapCreationAuthorization(
        operation=OPERATION, scope=SCOPE, creator_principal_id="principal-creator",
        target_principal_id="principal-target", bootstrap_id="bootstrap-1",
        bootstrap_purpose=PURPOSE, evidence_reference="evidence:create-1",
        key_id=key.key_id, trust_fingerprint=key.trust_fingerprint,
        issued_at=NOW - timedelta(minutes=1), expires_at=NOW + timedelta(minutes=10),
        nonce="nonce-1", idempotency_key="idem-1", signature_base64url=_b64(bytes(64)),
    )
    return replace(unsigned, signature_base64url=_b64(private.sign(unsigned.signed_payload()))), SystemPermissionBootstrapCreationTrustRoot((key,))


def _service(rows: dict[str, str]) -> tuple[SystemPermissionBootstrapIssuanceService, _PrincipalCollection, _Registry]:
    authorization, root = _authorization()
    del authorization
    principals = _PrincipalCollection(rows)
    registry = _Registry()
    return SystemPermissionBootstrapIssuanceService(principal_collection=principals, bootstrap_registry=registry, trust_root=root), principals, registry  # type: ignore[arg-type]


def test_active_transaction_current_creator_and_exact_bindings_issue_revision_one() -> None:
    authorization, root = _authorization()
    principals = _PrincipalCollection({"principal-creator": PrincipalStatus.ACTIVE.value})
    registry = _Registry()
    service = SystemPermissionBootstrapIssuanceService(principal_collection=principals, bootstrap_registry=registry, trust_root=root)  # type: ignore[arg-type]
    session = _Session()
    authority = service.issue(authorization, now=NOW, session=session)
    assert (authority.bootstrap_id, authority.actor_principal_id, authority.purpose) == ("bootstrap-1", "principal-target", PURPOSE)
    assert authority.evidence_reference == "evidence:create-1"
    assert authority.revision == 1 and authority.status.value == "ACTIVE"
    assert principals.sessions == [session] and registry.sessions == [session]
    assert session.lifecycle_calls == []


@pytest.mark.parametrize("session", [None, _Session(False)])
def test_active_transaction_is_required(session: object) -> None:
    authorization, root = _authorization()
    service = SystemPermissionBootstrapIssuanceService(principal_collection=_PrincipalCollection({"principal-creator": "ACTIVE"}), bootstrap_registry=_Registry(), trust_root=root)  # type: ignore[arg-type]
    with pytest.raises(SystemPermissionBootstrapIssuanceError, match="ACTIVE_TRANSACTION_REQUIRED"):
        service.issue(authorization, now=NOW, session=session)


@pytest.mark.parametrize(
    ("rows", "expected"),
    [({}, "CREATOR_PRINCIPAL_NOT_FOUND"), ({"principal-creator": "SUSPENDED"}, "CREATOR_PRINCIPAL_NOT_CURRENT")],
)
def test_missing_or_nonactive_creator_fails_closed(rows: dict[str, str], expected: str) -> None:
    authorization, root = _authorization()
    service = SystemPermissionBootstrapIssuanceService(principal_collection=_PrincipalCollection(rows), bootstrap_registry=_Registry(), trust_root=root)  # type: ignore[arg-type]
    with pytest.raises(SystemPermissionBootstrapIssuanceError, match=expected):
        service.issue(authorization, now=NOW, session=_Session())


def test_exact_replay_is_one_row_and_divergence_conflicts() -> None:
    authorization, root = _authorization()
    registry = _Registry()
    service = SystemPermissionBootstrapIssuanceService(principal_collection=_PrincipalCollection({"principal-creator": "ACTIVE"}), bootstrap_registry=registry, trust_root=root)  # type: ignore[arg-type]
    session = _Session()
    first = service.issue(authorization, now=NOW, session=session)
    assert service.issue(authorization, now=NOW, session=session) == first
    assert len(registry.rows) == 1
    registry.rows[authorization.idempotency_key] = (
        SystemPermissionBootstrapAuthority.issue(
            bootstrap_id=authorization.bootstrap_id,
            actor_principal_id=authorization.target_principal_id,
            purpose=authorization.bootstrap_purpose,
            evidence_reference="evidence:divergent-durable-command",
            issued_at=authorization.issued_at,
        ),
        authorization.idempotency_key,
    )
    with pytest.raises(SystemPermissionBootstrapAuthorityConflictError, match="BOOTSTRAP_CREATE_REPLAY_CONFLICT"):
        service.issue(authorization, now=NOW, session=session)


def test_service_has_no_forbidden_authority_or_transaction_lifecycle_surface() -> None:
    names = set(dir(SystemPermissionBootstrapIssuanceService))
    assert not {"assign_permission", "activate", "break_glass", "execute_payment", "start_session", "commit", "abort"} & names


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_system_permission_bootstrap_issuance_service.py
# VERSION: v1.0.0-P4-R4-D11-R5-ISSUANCE-SERVICE-CERTIFICATE
# POSTURE: CALLER TRANSACTION; NO PERMISSION OR EXECUTION SIDE EFFECT
# END OF WILSY OS SOVEREIGN ARTIFACT
