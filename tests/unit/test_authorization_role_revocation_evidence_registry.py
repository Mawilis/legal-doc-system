"""Direct certificate for authorization-role revocation evidence registry.

TITLE: Authorization Role Revocation Evidence Registry Direct Certificate
VERSION: v1.1.0-P1-R3C-E1-AUTHORIZATION-ROLE-REVOCATION-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance / Sovereign IAM Design
EPITOME: Prove exact indexes, strict hydration, transaction admission, replay, collision, and dependency boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_authorization_role_revocation_evidence_registry.py
COLLABORATION / OWNERSHIP: Certifies only authorization_role_revocation_evidence_registry.py.
CERTIFICATION / UPDATE DATE: 2026-10-13
CHANGELOG: v1.1.0-P1-R3C-E1 certifies the exact tenant/idempotency historical
           read, None absence, session forwarding, strict hydration, and zero
           write authority; v1.0.0-P1-R3B-G1 established direct registry proof.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: In-memory deterministic doubles; no credentials or PII.
TENANT BOUNDARY: Exact tenant/revocation and tenant/idempotency predicates certified.
AUTHORITY BOUNDARY: Test-only persistence verification; no authorization or role mutation.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, OperationFailure

from tools.eos.auth.authorization_role_revocation_evidence import (
    AuthorizationRoleRevocationEvidence,
)
from tools.eos.auth.authorization_role_revocation_evidence_registry import (
    COLLECTION,
    REVOCATION_ID_INDEX,
    TARGET_ROLE_TIMELINE_INDEX,
    TENANT_IDEMPOTENCY_INDEX,
    AuthorizationRoleRevocationEvidenceConflictError,
    AuthorizationRoleRevocationEvidenceNotFoundError,
    AuthorizationRoleRevocationEvidencePersistedRecordInvalidError,
    AuthorizationRoleRevocationEvidenceRegistry,
    AuthorizationRoleRevocationEvidenceTransactionRequiredError,
)

VERSION = "v1.1.0-P1-R3C-E1-AUTHORIZATION-ROLE-REVOCATION-REGISTRY-CERT"
PRODUCTION = Path("tools/eos/auth/authorization_role_revocation_evidence_registry.py")


class Session:
    """Minimal caller-owned transaction marker."""

    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class Collection:
    """Deterministic collection double recording every persistence call."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.calls: list[tuple[object, ...]] = []
        self.duplicate_on_insert = False
        self.unusable_after_duplicate = False

    def create_index(self, keys: list[tuple[str, int]], **kwargs: object) -> str:
        self.calls.append(("index", keys, kwargs))
        return str(kwargs.get("name"))

    def find_one(self, query: dict[str, object], *, session: object = None) -> dict[str, object] | None:
        self.calls.append(("find", query, session))
        if self.unusable_after_duplicate:
            raise OperationFailure("transaction unusable")
        return next(
            (row for row in self.rows if all(row.get(key) == value for key, value in query.items())),
            None,
        )

    def insert_one(self, row: dict[str, object], *, session: object) -> object:
        self.calls.append(("insert", row, session))
        if self.duplicate_on_insert:
            self.duplicate_on_insert = False
            if self.unusable_after_duplicate:
                raise DuplicateKeyError("duplicate")
            raise DuplicateKeyError("duplicate")
        self.rows.append(dict(row))
        return object()


def evidence(**changes: object) -> AuthorizationRoleRevocationEvidence:
    """Build one deterministic E1 evidence value for registry tests."""
    values: dict[str, object] = {
        "revocation_id": "revoke-001",
        "tenant_id": "tenant-a",
        "actor_principal_id": "principal-admin",
        "target_principal_id": "principal-target",
        "target_role_id": "AUDITOR",
        "target_assignment_prior_revision": 0,
        "target_assignment_result_revision": 1,
        "operation": "role_revoke",
        "reason_reference": "ticket:ACCESS-42",
        "authorization_evidence_reference": "tenant-authorization-decision:auth-001",
        "authorization_evidence_fingerprint": "a" * 128,
        "idempotency_key": "idem-001",
        "revoked_at": datetime(2026, 10, 13, 8, 30, tzinfo=timezone.utc),
    }
    values.update(changes)
    return AuthorizationRoleRevocationEvidence(**values)  # type: ignore[arg-type]


def test_collection_and_index_contract_is_exact_and_idempotent() -> None:
    """Certify exact names, keys, uniqueness, no fingerprint index, and no TTL."""
    assert COLLECTION == "authorization_role_revocation_evidence"
    collection = Collection()
    registry = AuthorizationRoleRevocationEvidenceRegistry(collection)
    registry.ensure_indexes()
    registry.ensure_indexes()
    expected = [
        ("index", [("revocation_id", ASCENDING)], {"unique": True, "name": REVOCATION_ID_INDEX}),
        ("index", [("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)], {"unique": True, "name": TENANT_IDEMPOTENCY_INDEX}),
        ("index", [("tenant_id", ASCENDING), ("target_principal_id", ASCENDING), ("target_role_id", ASCENDING), ("revoked_at", ASCENDING)], {"unique": False, "name": TARGET_ROLE_TIMELINE_INDEX}),
    ]
    assert collection.calls == expected + expected
    encoded = repr(collection.calls).lower()
    assert "fingerprint" not in encoded
    assert "expireafterseconds" not in encoded and "ttl" not in encoded


def test_get_uses_exact_tenant_identity_and_caller_session() -> None:
    """Read lookup is exact, hydrated, session-forwarded, and creates no session."""
    collection = Collection()
    value = evidence()
    collection.rows.append(value.to_persisted())
    session = Session()
    result = AuthorizationRoleRevocationEvidenceRegistry(collection).get(
        tenant_id=value.tenant_id,
        revocation_id=value.revocation_id,
        session=session,
    )
    assert result == value
    assert collection.calls == [("find", {"tenant_id": "tenant-a", "revocation_id": "revoke-001"}, session)]


def test_get_not_found_and_cross_tenant_are_indistinguishable_absence() -> None:
    """Missing and foreign-tenant evidence both fail as exact-scope not found."""
    collection = Collection()
    collection.rows.append(evidence().to_persisted())
    registry = AuthorizationRoleRevocationEvidenceRegistry(collection)
    with pytest.raises(AuthorizationRoleRevocationEvidenceNotFoundError):
        registry.get(tenant_id="tenant-a", revocation_id="missing")
    with pytest.raises(AuthorizationRoleRevocationEvidenceNotFoundError):
        registry.get(tenant_id="tenant-b", revocation_id="revoke-001")


def test_get_corruption_fails_closed() -> None:
    """Stored digest corruption is never repaired or returned."""
    collection = Collection()
    row = evidence().to_persisted()
    row["revocation_evidence_fingerprint"] = "f" * 128
    collection.rows.append(row)
    with pytest.raises(AuthorizationRoleRevocationEvidencePersistedRecordInvalidError):
        AuthorizationRoleRevocationEvidenceRegistry(collection).get(
            tenant_id="tenant-a", revocation_id="revoke-001"
        )


@pytest.mark.parametrize("session", [None, Session()])
def test_get_by_tenant_idempotency_exact_hydrated_and_session_forwarded(session: object) -> None:
    """Return a strict value using the exact scoped key and unchanged optional session."""
    collection = Collection()
    value = evidence()
    collection.rows.append(value.to_persisted())
    result = AuthorizationRoleRevocationEvidenceRegistry(collection).get_by_tenant_idempotency(
        tenant_id=value.tenant_id,
        idempotency_key=value.idempotency_key,
        session=session,
    )
    assert result == value
    assert type(result) is AuthorizationRoleRevocationEvidence
    assert collection.calls == [
        ("find", {"tenant_id": "tenant-a", "idempotency_key": "idem-001"}, session)
    ]


@pytest.mark.parametrize(
    ("tenant_id", "idempotency_key"),
    (("tenant-b", "idem-001"), ("tenant-a", "idem-missing")),
)
def test_get_by_tenant_idempotency_absence_is_none(
    tenant_id: str, idempotency_key: str
) -> None:
    """Wrong tenant and wrong replay key both yield non-disclosing ordinary absence."""
    collection = Collection()
    collection.rows.append(evidence().to_persisted())
    assert AuthorizationRoleRevocationEvidenceRegistry(collection).get_by_tenant_idempotency(
        tenant_id=tenant_id,
        idempotency_key=idempotency_key,
    ) is None
    assert [call[0] for call in collection.calls] == ["find"]


@pytest.mark.parametrize(
    "mutation",
    ("fingerprint", "schema", "missing", "unknown", "revision", "timestamp"),
)
def test_get_by_tenant_idempotency_corruption_fails_closed(mutation: str) -> None:
    """Every representative persisted-domain fracture rejects without raw BSON escape."""
    collection = Collection()
    row = evidence().to_persisted()
    if mutation == "fingerprint":
        row["revocation_evidence_fingerprint"] = "f" * 128
    elif mutation == "schema":
        row["schema"] = "WILSY-AUTHORIZATION-ROLE-REVOCATION-EVIDENCE/V2"
    elif mutation == "missing":
        row.pop("reason_reference")
    elif mutation == "unknown":
        row["unknown"] = "forbidden"
    elif mutation == "revision":
        row["target_assignment_result_revision"] = 99
    else:
        row["revoked_at"] = "malformed"
    collection.rows.append(row)
    with pytest.raises(AuthorizationRoleRevocationEvidencePersistedRecordInvalidError):
        AuthorizationRoleRevocationEvidenceRegistry(collection).get_by_tenant_idempotency(
            tenant_id="tenant-a",
            idempotency_key="idem-001",
        )
    assert [call[0] for call in collection.calls] == ["find"]


@pytest.mark.parametrize("session", [None, Session(False)])
def test_create_rejects_missing_or_inactive_transaction_before_read(session: object) -> None:
    """Transaction admission occurs before the first persistence operation."""
    collection = Collection()
    with pytest.raises(AuthorizationRoleRevocationEvidenceTransactionRequiredError):
        AuthorizationRoleRevocationEvidenceRegistry(collection).create_or_replay(
            evidence(), session=session
        )
    assert collection.calls == []


def test_fresh_evidence_inserts_once_with_exact_session() -> None:
    """Both preflight reads and the insert use the caller's exact session."""
    collection = Collection()
    session = Session()
    value = evidence()
    assert AuthorizationRoleRevocationEvidenceRegistry(collection).create_or_replay(value, session=session) == value
    assert len(collection.rows) == 1
    assert [call[0] for call in collection.calls] == ["find", "find", "insert"]
    assert all(call[-1] is session for call in collection.calls)


def test_exact_scoped_replay_returns_historic_without_insert() -> None:
    """Exact tenant/idempotency material returns strict historic evidence."""
    collection = Collection()
    value = evidence()
    collection.rows.append(value.to_persisted())
    result = AuthorizationRoleRevocationEvidenceRegistry(collection).create_or_replay(value, session=Session())
    assert result == value
    assert [call[0] for call in collection.calls] == ["find"]


def test_divergent_idempotency_replay_rejects() -> None:
    """Same tenant/key with any material drift conflicts."""
    collection = Collection()
    collection.rows.append(evidence().to_persisted())
    with pytest.raises(AuthorizationRoleRevocationEvidenceConflictError) as captured:
        AuthorizationRoleRevocationEvidenceRegistry(collection).create_or_replay(
            evidence(revocation_id="revoke-002", reason_reference="ticket:OTHER"),
            session=Session(),
        )
    assert captured.value.code == "IDEMPOTENCY_KEY_DIVERGENT_REPLAY"


def test_revocation_id_collision_with_different_material_rejects() -> None:
    """Global durable revocation identity cannot bind different evidence."""
    collection = Collection()
    collection.rows.append(evidence().to_persisted())
    with pytest.raises(AuthorizationRoleRevocationEvidenceConflictError) as captured:
        AuthorizationRoleRevocationEvidenceRegistry(collection).create_or_replay(
            evidence(tenant_id="tenant-b", idempotency_key="idem-002"),
            session=Session(),
        )
    assert captured.value.code == "REVOCATION_ID_COLLISION"


def test_corrupt_historic_row_rejects_instead_of_replay() -> None:
    """Replay classification always passes through strict E1 hydration."""
    collection = Collection()
    row = evidence().to_persisted()
    row.pop("reason_reference")
    collection.rows.append(row)
    with pytest.raises(AuthorizationRoleRevocationEvidencePersistedRecordInvalidError):
        AuthorizationRoleRevocationEvidenceRegistry(collection).create_or_replay(
            evidence(), session=Session()
        )


def test_duplicate_key_exact_replay_and_divergence_are_classified() -> None:
    """Readable duplicate races replay only exact durable evidence."""
    exact_collection = Collection()
    value = evidence()
    exact_collection.rows.append(value.to_persisted())
    exact_collection.duplicate_on_insert = True
    # Simulate a race after both initial reads by hiding the row for two reads.
    original_find = exact_collection.find_one
    reads = 0
    def delayed_find(query: dict[str, object], *, session: object = None) -> dict[str, object] | None:
        nonlocal reads
        reads += 1
        exact_collection.calls.append(("find", query, session))
        if reads <= 2:
            return None
        return next((row for row in exact_collection.rows if all(row.get(k) == v for k, v in query.items())), None)
    exact_collection.find_one = delayed_find  # type: ignore[method-assign]
    assert AuthorizationRoleRevocationEvidenceRegistry(exact_collection).create_or_replay(value, session=Session()) == value

    divergent_collection = Collection()
    historic = evidence(reason_reference="ticket:HISTORIC")
    divergent_collection.rows.append(historic.to_persisted())
    divergent_collection.duplicate_on_insert = True
    reads = 0
    def divergent_find(query: dict[str, object], *, session: object = None) -> dict[str, object] | None:
        nonlocal reads
        reads += 1
        divergent_collection.calls.append(("find", query, session))
        if reads <= 2:
            return None
        return next((row for row in divergent_collection.rows if all(row.get(k) == v for k, v in query.items())), None)
    divergent_collection.find_one = divergent_find  # type: ignore[method-assign]
    with pytest.raises(AuthorizationRoleRevocationEvidenceConflictError):
        AuthorizationRoleRevocationEvidenceRegistry(divergent_collection).create_or_replay(value, session=Session())


def test_unusable_transaction_after_duplicate_requires_whole_transaction_retry() -> None:
    """No unsafe success is invented when Mongo invalidates the transaction."""
    collection = Collection()
    collection.duplicate_on_insert = True
    collection.unusable_after_duplicate = False
    original_insert = collection.insert_one
    def duplicate_then_unusable(row: dict[str, object], *, session: object) -> object:
        collection.calls.append(("insert", row, session))
        collection.unusable_after_duplicate = True
        raise DuplicateKeyError("duplicate")
    collection.insert_one = duplicate_then_unusable  # type: ignore[method-assign]
    with pytest.raises(AuthorizationRoleRevocationEvidenceConflictError) as captured:
        AuthorizationRoleRevocationEvidenceRegistry(collection).create_or_replay(
            evidence(), session=Session()
        )
    assert captured.value.code == "WHOLE_TRANSACTION_RETRY_REQUIRED"
    del original_insert


def test_registry_surface_is_append_only_and_non_authorizing() -> None:
    """Certify absent mutation APIs and forbidden authority dependencies."""
    registry_type = AuthorizationRoleRevocationEvidenceRegistry
    assert {name for name in vars(registry_type) if not name.startswith("_")} == {
        "ensure_indexes", "get", "get_by_tenant_idempotency", "create_or_replay"
    }
    source = PRODUCTION.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert "tools.eos.auth.role_assignment_repository" not in imports
    assert all(not name.startswith(("fastapi", "tools.eos.legal_operations")) for name in imports)
    lowered = source.lower()
    for forbidden in (
        "compare_and_swap", "upsert", "refresh_token", "membership_repository",
        "business_role_repository", "authorize_tenant_operation", "collection_name",
    ):
        assert forbidden not in lowered
    called = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))
    }
    assert called.isdisjoint({"update_one", "replace_one", "delete_one", "delete_many", "start_session", "start_transaction", "commit_transaction", "abort_transaction"})
    assert "financial execution authority: none" in lowered


# ARTIFACT: test_authorization_role_revocation_evidence_registry.py
# VERSION: v1.1.0-P1-R3C-E1-AUTHORIZATION-ROLE-REVOCATION-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct append-only registry verification only; no authorization, policy, role mutation, session/transaction lifecycle, or finance
# TENANT POSTURE: exact tenant/revocation and tenant/idempotency scope certified
# FAIL-CLOSED POSTURE: missing transaction/evidence, corruption, divergence, collisions, duplicate races, and outages reject
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
# REAL MONGO: NOT EXECUTED IN THIS GATE
# END OF WILSY OS SOVEREIGN ARTIFACT
