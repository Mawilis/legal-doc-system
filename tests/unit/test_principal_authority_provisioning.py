"""R1D-B0F-B4-R6 direct principal-provisioning certificate.

TITLE: Durable PrincipalAuthority Provisioning Certificate
VERSION: v1.0.0-R1D-B0F-B4-R6
AUTHORITY: Deterministic unit evidence for the explicit provisioning owner.
EPITOME: Proves revision-zero creation, replay, divergence refusal, status
         non-inference, exact legacy dry-run, and the final session barrier.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_principal_authority_provisioning.py
COLLABORATION / OWNERSHIP: Exercises principal provisioning, reconciliation,
                           and AuthRegistry session issuance.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.0-R1D-B0F-B4-R6 adds bounded in-memory certification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identities only; no network or secrets.
TENANT BOUNDARY: Legacy fixture requires exact canonical tenant.
AUTHORITY BOUNDARY: Unit evidence only; no real authority or token grant.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace
from typing import Any, cast

import pytest
from bson import ObjectId

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_provisioning import (
    PrincipalAuthorityProvisioningError,
    provision_principal_authority,
)
from tools.eos.auth.principal_initial_status_authority import (
    AUTHORITY_SOURCE_ID,
    PRINCIPAL_INITIAL_STATUS_OPERATION,
    PrincipalInitialStatusAuthorityEvidence,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.saas.auth.auth_registry import AuthRegistry, AuthRegistryTenantError
from tools.eos.saas.domain.auth import User
from tools.eos.saas.auth.migrations.reconcile_legacy_principal_authority import (
    LEGACY_PRINCIPAL_ID,
    LegacyPrincipalReconciliationError,
    reconcile_legacy_principal_authority,
)


class Collection:
    def __init__(self, rows: list[dict[str, Any]] | None = None) -> None:
        self.rows = deepcopy(rows or [])
        self.writes = 0

    def find_one(self, query: dict[str, Any], **_: Any) -> dict[str, Any] | None:
        return next((dict(row) for row in self.rows if all(row.get(k) == v for k, v in query.items())), None)

    def find(self, query: dict[str, Any], **_: Any) -> list[dict[str, Any]]:
        return [dict(row) for row in self.rows if all(row.get(k) == v for k, v in query.items())]

    def insert_one(self, document: dict[str, Any], **_: Any) -> None:
        self.writes += 1
        if self.find_one({"principal_id": document["principal_id"]}) is not None:
            from pymongo.errors import DuplicateKeyError
            raise DuplicateKeyError("duplicate")
        self.rows.append(dict(document))


class Database:
    name = "wilsy"

    def __init__(self, authority_rows: list[dict[str, Any]] | None = None) -> None:
        self.collections = {
            "principal_authorities": Collection(authority_rows),
            "sessions": Collection(),
            "refresh_tokens": Collection(),
            "users": Collection([{
                "_id": ObjectId(LEGACY_PRINCIPAL_ID), "user_id": None,
                "tenantId": "WILSYTENANT-4CD2FZ4O", "status": "ACTIVE", "role": "SUPER_ADMIN",
            }]),
            "tenants": Collection([{"tenant_id": "WILSYTENANT-4CD2FZ4O", "status": "ACTIVE"}]),
        }

    def __getitem__(self, name: str) -> Collection:
        return self.collections[name]


class Session:
    def __init__(self, database: Database) -> None:
        self.database = database

    def __enter__(self) -> "Session":
        return self

    def __exit__(self, *_args: Any) -> None:
        return None

    def with_transaction(self, callback: Any) -> None:
        callback(self)


class Client:
    def __init__(self, database: Database) -> None:
        self.database = database

    def start_session(self) -> Session:
        return Session(self.database)


def _evidence(principal_id: str, status: PrincipalStatus) -> PrincipalInitialStatusAuthorityEvidence:
    return PrincipalInitialStatusAuthorityEvidence(
        principal_id, status, PRINCIPAL_INITIAL_STATUS_OPERATION, AUTHORITY_SOURCE_ID
    )


def test_explicit_admission_owner_creates_revision_zero_once() -> None:
    collection = Collection()
    first = provision_principal_authority(
        principal_id="principal-1", status=PrincipalStatus.SUSPENDED,
        authority_evidence=_evidence("principal-1", PrincipalStatus.SUSPENDED), collection=cast(Any, collection),
    )
    replay = provision_principal_authority(
        principal_id="principal-1", status=PrincipalStatus.SUSPENDED,
        authority_evidence=_evidence("principal-1", PrincipalStatus.SUSPENDED), collection=cast(Any, collection),
    )
    assert first.created is True and replay.created is False
    assert first.authority == PrincipalAuthority("principal-1", PrincipalStatus.SUSPENDED, 0)
    assert collection.writes == 1


def test_role_or_users_status_is_not_an_initial_status_authority() -> None:
    with pytest.raises(PrincipalAuthorityProvisioningError, match="EVIDENCE_REQUIRED"):
        provision_principal_authority(principal_id="principal-1", status=PrincipalStatus.ACTIVE, collection=cast(Any, Collection()))


def test_divergent_replay_never_overwrites() -> None:
    collection = Collection([{"principal_id": "principal-1", "status": "ACTIVE", "revision": 0}])
    with pytest.raises(PrincipalAuthorityProvisioningError, match="CONFLICT"):
        provision_principal_authority(
            principal_id="principal-1", status=PrincipalStatus.SUSPENDED,
            authority_evidence=_evidence("principal-1", PrincipalStatus.SUSPENDED), collection=cast(Any, collection),
        )
    assert collection.writes == 0


def test_legacy_reconciliation_defaults_to_write_free_blocked_status(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WILSY_PRINCIPAL_INITIAL_STATUS_AUTHORITY", raising=False)
    database = Database()
    before = deepcopy(database["principal_authorities"].rows)
    report = reconcile_legacy_principal_authority(database=database)
    assert report.state == "dry_run_pending_status_authority"
    assert report.writes_performed == 0
    assert database["principal_authorities"].rows == before
    assert database["users"].rows[0]["user_id"] is None


def test_legacy_reconciliation_valid_authority_dry_run_is_write_free(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WILSY_PRINCIPAL_INITIAL_STATUS_AUTHORITY", '{"principal_id":"695e423c9d355c0675c6835d","initial_status":"ACTIVE"}')
    database = Database()
    report = reconcile_legacy_principal_authority(database=database, dry_run=True)
    assert report.state == "dry_run_pending"
    assert report.target_status == "ACTIVE" and report.target_revision == 0
    assert report.writes_performed == 0
    assert database["principal_authorities"].rows == []


def test_legacy_reconciliation_refuses_execution_without_sanctioned_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WILSY_PRINCIPAL_INITIAL_STATUS_AUTHORITY", raising=False)
    report = reconcile_legacy_principal_authority(database=Database(), dry_run=False)
    assert report.state == "blocked_status_authority"


def test_explicit_activation_authority_executes_once_and_replays(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WILSY_PRINCIPAL_INITIAL_STATUS_AUTHORITY", '{"principal_id":"695e423c9d355c0675c6835d","initial_status":"ACTIVE"}')
    database = Database()
    client = Client(database)
    first = reconcile_legacy_principal_authority(
        database=database, client=client, dry_run=False,
    )
    second = reconcile_legacy_principal_authority(
        database=database, client=client, dry_run=False,
    )
    assert first.state == "reconciled" and second.state == "already_reconciled"
    assert database["principal_authorities"].rows == [{
        "principal_id": LEGACY_PRINCIPAL_ID, "status": "ACTIVE", "revision": 0,
    }]
    assert database["principal_authorities"].writes == 1


def test_legacy_conflict_never_overwrites() -> None:
    database = Database([{"principal_id": LEGACY_PRINCIPAL_ID, "status": "SUSPENDED", "revision": 0}])
    with pytest.raises(LegacyPrincipalReconciliationError, match="CONFLICT"):
        reconcile_legacy_principal_authority(database=database)
    assert database["principal_authorities"].writes == 0


def test_reconciliation_rejects_noncanonical_database() -> None:
    database = Database()
    database.name = "other"  # type: ignore[attr-defined]
    with pytest.raises(LegacyPrincipalReconciliationError, match="CANONICAL_DATABASE_REQUIRED"):
        reconcile_legacy_principal_authority(database=database)


def test_final_session_requires_active_durable_authority(monkeypatch: pytest.MonkeyPatch) -> None:
    database = Database()
    monkeypatch.setattr("tools.eos.saas.auth.auth_registry.kernel_db.get_database", lambda: database)
    registry = AuthRegistry(cast(Any, SimpleNamespace(resolve_canonical_tenant=lambda *_args, **_kwargs: SimpleNamespace(tenant_id="WILSYTENANT-4CD2FZ4O"))))
    user = User(id="principal-1", email="p@example.com", firstName="P", lastName="One", role="USER", permissions=[], tenantId="WILSYTENANT-4CD2FZ4O", passwordHash="hash")
    with pytest.raises(AuthRegistryTenantError, match="PRINCIPAL_AUTHORITY_REQUIRED"):
        registry.create_session(user)
    database["principal_authorities"].rows.append({"principal_id": "principal-1", "status": "SUSPENDED", "revision": 0})
    with pytest.raises(AuthRegistryTenantError, match="PRINCIPAL_AUTHORITY_NOT_ACTIVE"):
        registry.create_session(user)


# ARTIFACT: test_principal_authority_provisioning.py
# VERSION: v1.0.0-R1D-B0F-B4-R6
# AUTHORITY BOUNDARY: deterministic provisioning and reconciliation evidence only
# TENANT POSTURE: exact canonical legacy fixture; no cross-tenant inference
# FAIL-CLOSED POSTURE: absent status authority, conflicts, and noncanonical DB deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
