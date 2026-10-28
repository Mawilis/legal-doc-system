"""TITLE: WILSY OS Ethical Wall Policy Registry Unit Certificate.
VERSION: v1.0.0-G76-B-TRANSACTIONAL-REGISTRY-CERT
AUTHORITY: Transactional evidence-persistence verification only.
EPITOME: Certifies immutable revisions, CAS currentness, terminal revocation,
    tenant/matter isolation, corruption rejection and non-authorizing storage.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_work_ethical_wall_policy_registry.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering / Legal Operations.
CERTIFICATION / UPDATE DATE: 2026-10-21.
CHANGELOG: 2026-10-21 v1.0.0 introduces the G76-B registry certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque identities and fingerprints; no content.
TENANT BOUNDARY: Exact tenant, matter and policy predicates.
AUTHORITY BOUNDARY: Persistence cannot grant operational access.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_work_ethical_wall_policy import (
    EthicalWallPolicyRevision as Revision,
    EthicalWallPolicyStatus,
    InstitutionalRatificationState,
    evaluate_ethical_wall_access,
)
from tools.eos.legal_operations.registry import (
    legal_work_ethical_wall_policy_registry as reg,
)
from tools.eos.legal_operations.service.legal_work_ethical_wall_authorization_fence import (
    CanonicalWallAuthorizationFence,
    FENCE_INDEX_FIELDS,
    FENCE_INDEX_NAME,
)

NOW = datetime(2026, 10, 21, 12, 0, tzinfo=UTC)


class Session:
    """Minimal active caller-owned transaction test double."""

    in_transaction = True


class Cursor:
    def __init__(self, documents: list[dict[str, Any]]) -> None:
        self.documents = documents

    def sort(self, key: str, direction: int) -> "Cursor":
        self.documents.sort(key=lambda item: item[key], reverse=direction < 0)
        return self

    def limit(self, maximum: int) -> list[dict[str, Any]]:
        return self.documents[:maximum]


class MemoryCollection:
    """Strict-enough Mongo collection double for deterministic unit evidence."""

    def __init__(self) -> None:
        self.documents: list[dict[str, Any]] = []
        self.indexes: list[tuple[tuple[tuple[str, int], ...], dict[str, Any]]] = []
        self.fail_write = False
        self.fail_cas = False

    def create_index(self, keys: list[tuple[str, int]], **kwargs: Any) -> str:
        self.indexes.append((tuple(keys), kwargs))
        return str(kwargs["name"])

    @staticmethod
    def _matches(document: dict[str, Any], query: dict[str, Any]) -> bool:
        return all(document.get(key) == value for key, value in query.items())

    def find(self, query: dict[str, Any], *, session: Session) -> Cursor:
        assert session.in_transaction
        return Cursor([dict(item) for item in self.documents if self._matches(item, query)])

    def find_one(self, query: dict[str, Any], *, session: Session) -> dict[str, Any] | None:
        return next(iter(self.find(query, session=session).documents), None)

    def insert_one(self, document: dict[str, Any], *, session: Session) -> SimpleNamespace:
        assert session.in_transaction
        if self.fail_write:
            raise OSError("storage unavailable")
        if any(self._matches(item, {k: document[k] for k in document if k != "_id"})
               for item in self.documents):
            raise DuplicateKeyError("duplicate")
        self.documents.append(dict(document))
        return SimpleNamespace(inserted_id=len(self.documents))

    def update_one(self, query: dict[str, Any], update: dict[str, Any], *, session: Session) -> SimpleNamespace:
        assert session.in_transaction
        if self.fail_write:
            raise OSError("storage unavailable")
        if self.fail_cas:
            return SimpleNamespace(modified_count=0)
        for item in self.documents:
            if self._matches(item, query):
                item.update(update["$set"])
                return SimpleNamespace(modified_count=1)
        return SimpleNamespace(modified_count=0)


class MemoryFenceCollection:
    def __init__(self) -> None:
        self.rows: dict[tuple[str, str, str, str], dict[str, object]] = {}
        self.indexes: list[tuple[tuple[tuple[str, int], ...], dict[str, Any]]] = []

    def create_index(self, keys: list[tuple[str, int]], **options: Any) -> str:
        self.indexes.append((tuple(keys), options))
        return str(options["name"])

    def update_one(self, scope: dict[str, str], update: dict[str, Any], *, upsert: bool, session: Any) -> SimpleNamespace:
        assert session.in_transaction is True
        key = (scope["tenant_id"], scope["case_matter_id"], scope["practitioner_principal_id"], scope["policy_id"])
        row = self.rows.get(key)
        if row is None:
            row = {**scope, "epoch": 0, "schema_version": 1}
            self.rows[key] = row
        row["epoch"] = int(row["epoch"]) + int(update["$inc"]["epoch"])
        return SimpleNamespace(matched_count=1, upserted_id=None)

    def find_one(self, scope: dict[str, str], *, session: Any) -> dict[str, object] | None:
        assert session.in_transaction is True
        key = (scope["tenant_id"], scope["case_matter_id"], scope["practitioner_principal_id"], scope["policy_id"])
        row = self.rows.get(key)
        return dict(row) if row is not None else None


def revision(**changes: object) -> Revision:
    values: dict[str, object] = {
        "policy_id": "wall-1", "revision": 1, "predecessor_fingerprint": None,
        "tenant_id": "tenant-a", "case_matter_id": "matter-a",
        "protected_subject_fingerprints": ("a" * 128,),
        "restricted_principal_ids": ("principal-denied",),
        "permitted_principal_ids": ("principal-allowed",),
        "status": EthicalWallPolicyStatus.ACTIVE,
        "effective_from": NOW, "effective_until": NOW + timedelta(days=30),
        "source_evidence_reference": "source-1",
        "source_evidence_fingerprint": "b" * 128,
        "administrator_principal_id": "admin-1",
        "administrator_authorization_reference": "admin-auth-1",
        "administrator_authorization_fingerprint": "c" * 128,
        "ratification_state": InstitutionalRatificationState.APPROVED,
        "ratification_reference": "ratification-1",
        "ratification_fingerprint": "d" * 128,
    }
    values.update(changes)
    return Revision(**values)  # type: ignore[arg-type]


def successor(root: Revision, **changes: object) -> Revision:
    values: dict[str, object] = {
        "revision": root.revision + 1,
        "predecessor_fingerprint": root.fingerprint,
        "effective_from": root.effective_from + timedelta(days=1),
    }
    values.update(changes)
    return replace(root, **values)


def registry() -> tuple[Any, MemoryCollection, MemoryCollection]:
    revisions, current = MemoryCollection(), MemoryCollection()
    fence = CanonicalWallAuthorizationFence(MemoryFenceCollection())
    return reg.EthicalWallPolicyRegistry(revisions, current, fence), revisions, current


@pytest.mark.parametrize("session", [None, SimpleNamespace(in_transaction=False)])
def test_transaction_required_before_every_read_or_write(session: object) -> None:
    value, _, _ = registry()
    with pytest.raises(reg.EthicalWallPolicyTransactionRequired):
        value.append(revision(), session=session)
    with pytest.raises(reg.EthicalWallPolicyTransactionRequired):
        value.get_current("tenant-a", "matter-a", "wall-1", session=session)


def test_index_contract_has_unique_identity_lineage_fingerprint_pointer_and_no_ttl() -> None:
    value, revisions, current = registry()
    value.ensure_indexes()
    all_indexes = revisions.indexes + current.indexes
    assert len(all_indexes) == 6
    assert sum(index[1].get("unique") is True for index in all_indexes) == 5
    assert not any("expireAfterSeconds" in index[1] for index in all_indexes)
    assert {index[1]["name"] for index in all_indexes} == set(reg.INDEX_NAMES)


def test_valid_initial_revision_exact_replay_and_currentness() -> None:
    value, revisions, current = registry()
    root = revision()
    assert value.append(root, session=Session()) == root
    assert value.append(root, session=Session()) == root
    assert value.get_current("tenant-a", "matter-a", "wall-1", session=Session()) == root
    assert len(revisions.documents) == len(current.documents) == 1


def test_divergent_replay_and_second_root_reject() -> None:
    value, revisions, _ = registry()
    root = revision()
    value.append(root, session=Session())
    with pytest.raises(reg.EthicalWallPolicyConflict, match="DIVERGENT_REPLAY"):
        value.append(replace(root, source_evidence_reference="other"), session=Session())
    with pytest.raises(reg.EthicalWallPolicyConflict, match="DIVERGENT_REPLAY"):
        value.append(revision(policy_id="wall-1", source_evidence_reference="root-2"), session=Session())
    assert len(revisions.documents) == 1


def test_stale_revision_and_competing_successor_reject() -> None:
    value, revisions, _ = registry()
    root = revision()
    first = successor(root, source_evidence_reference="source-2")
    stale = replace(
        first, revision=3, predecessor_fingerprint=root.fingerprint,
        source_evidence_reference="source-stale",
        effective_from=first.effective_from + timedelta(days=1),
    )
    value.append(root, session=Session())
    value.append(first, session=Session())
    with pytest.raises(reg.EthicalWallPolicyConflict, match="STALE_REVISION"):
        value.append(stale, session=Session())
    assert len(revisions.documents) == 2


def test_pointer_cas_failure_requires_whole_transaction_retry() -> None:
    value, revisions, current = registry()
    root = revision()
    value.append(root, session=Session())
    current.fail_cas = True
    with pytest.raises(reg.EthicalWallPolicyRetryTransaction):
        value.append(successor(root), session=Session())
    # In Mongo the caller aborts the whole transaction. The memory double exposes
    # that the revision insert happened before CAS and therefore must not commit.
    assert len(revisions.documents) == 2


def test_terminal_revocation_cannot_reopen() -> None:
    value, revisions, _ = registry()
    root = revision()
    revoked = successor(
        root, status=EthicalWallPolicyStatus.REVOKED,
        ratification_state=InstitutionalRatificationState.REVOKED,
        ratification_reference="ratification-revoked",
        ratification_fingerprint="e" * 128,
    )
    value.append(root, session=Session())
    value.append(revoked, session=Session())
    with pytest.raises(reg.EthicalWallPolicyConflict, match="TERMINAL_REVOKED"):
        value.append(successor(revoked, status=EthicalWallPolicyStatus.ACTIVE,
                               ratification_state=InstitutionalRatificationState.APPROVED),
                     session=Session())
    assert len(revisions.documents) == 2


@pytest.mark.parametrize("mutation", ["missing", "revision", "fingerprint", "matter"])
def test_missing_or_invalid_current_pointer_fails_closed(mutation: str) -> None:
    value, _, current = registry()
    root = revision()
    value.append(root, session=Session())
    if mutation == "missing":
        current.documents.clear()
    elif mutation == "revision":
        current.documents[0]["revision"] = 2
    elif mutation == "fingerprint":
        current.documents[0]["fingerprint"] = "f" * 128
    else:
        current.documents[0]["case_matter_id"] = "matter-b"
    with pytest.raises(reg.EthicalWallPolicyPersistedInvalid):
        value.get_current("tenant-a", "matter-a", "wall-1", session=Session())


def test_stored_fingerprint_and_unknown_field_corruption_reject() -> None:
    value, revisions, _ = registry()
    value.append(revision(), session=Session())
    revisions.documents[0]["fingerprint"] = "f" * 128
    revisions.documents[0]["operational_access"] = True
    with pytest.raises(reg.EthicalWallPolicyPersistedInvalid):
        value.list_history("tenant-a", "matter-a", "wall-1", session=Session())


def test_tenant_and_matter_isolation_including_malformed_persisted_scope() -> None:
    value, revisions, _ = registry()
    value.append(revision(), session=Session())
    assert value.list_history("tenant-b", "matter-a", "wall-1", session=Session()) == ()
    assert value.list_history("tenant-a", "matter-b", "wall-1", session=Session()) == ()
    revisions.documents[0]["case_matter_id"] = "matter-forged"
    revisions.documents[0]["fingerprint"] = revision(case_matter_id="matter-forged").fingerprint
    with pytest.raises(reg.EthicalWallPolicyPersistedInvalid):
        value.get_current("tenant-a", "matter-a", "wall-1", session=Session())


def test_storage_failures_are_stable_and_never_authorize() -> None:
    value, revisions, _ = registry()
    revisions.fail_write = True
    with pytest.raises(reg.EthicalWallPolicyPersistenceUnavailable):
        value.append(revision(), session=Session())
    assert not hasattr(value, "authorize")
    assert revision().permits_operational_access is False


def test_recorded_approval_and_explicit_deny_remain_non_authorizing() -> None:
    value, _, _ = registry()
    root = revision(permitted_principal_ids=("principal-allowed", "principal-denied"))
    value.append(root, session=Session())
    persisted = value.get_current("tenant-a", "matter-a", "wall-1", session=Session())
    allowed = evaluate_ethical_wall_access(
        tenant_id="tenant-a", case_matter_id="matter-a",
        practitioner_principal_id="principal-allowed", evaluation_time=NOW,
        revisions=(persisted,),
    )
    denied = evaluate_ethical_wall_access(
        tenant_id="tenant-a", case_matter_id="matter-a",
        practitioner_principal_id="principal-denied", evaluation_time=NOW,
        revisions=(persisted,),
    )
    assert allowed.state.value == "ALLOW_RECORDED_UNVERIFIED"
    assert allowed.permits_operational_access is False
    assert denied.state.value == "DENIED_RESTRICTED"


# ARTIFACT: test_legal_work_ethical_wall_policy_registry.py
# VERSION: v1.0.0-G76-B-TRANSACTIONAL-REGISTRY-CERT
# AUTHORITY BOUNDARY: transactional evidence persistence only; no access grants
# TENANT POSTURE: exact tenant/matter/policy and corruption-blocked
# FAIL-CLOSED POSTURE: stale, forked, revoked, malformed or unavailable denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
