"""
Direct certificate for privileged-eligibility evidence registry.

VERSION:
v1.0.0-P2-R2-A2-PRIVILEGED-ELIGIBILITY-EVIDENCE-REGISTRY-CERT
"""

from datetime import datetime, timezone
import ast
from pathlib import Path
from types import SimpleNamespace

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.auth.privileged_eligibility import (
    ENTERPRISE_ADMIN,
    SOVEREIGN_ARCHITECT,
    evaluate_privileged_eligibility,
)
from tools.eos.auth.privileged_eligibility_evidence import (
    PrivilegedEligibilityEvidence,
)
from tools.eos.auth.privileged_eligibility_evidence_registry import (
    COLLECTION,
    PrivilegedEligibilityEvidenceConflictError,
    PrivilegedEligibilityEvidenceNotFoundError,
    PrivilegedEligibilityEvidencePersistedInvalidError,
    PrivilegedEligibilityEvidenceRegistry,
    PrivilegedEligibilityEvidenceTransactionRequiredError,
)


NOW = datetime(
    2026,
    10,
    14,
    1,
    30,
    tzinfo=timezone.utc,
)

PRODUCTION = Path(
    "tools/eos/auth/"
    "privileged_eligibility_evidence_registry.py"
)


class Session:
    def __init__(
        self,
        *,
        active: bool = True,
    ) -> None:
        self.in_transaction = active


class Collection:
    def __init__(
        self,
    ) -> None:
        self.rows: list[
            dict[str, object]
        ] = []

        self.calls: list[
            tuple[object, ...]
        ] = []

        self.indexes: list[
            tuple[
                tuple[tuple[str, object], ...],
                bool,
                str,
            ]
        ] = []

        self.duplicate_on_insert = False
        self.invalidate_on_duplicate = False
        self.hidden_reads = 0

    def create_index(
        self,
        keys,
        *,
        unique: bool = False,
        name: str,
    ):
        normalized = tuple(
            tuple(item)
            for item in keys
        )

        self.indexes.append(
            (
                normalized,
                unique,
                name,
            )
        )

        return name

    def find_one(
        self,
        query,
        *,
        session=None,
    ):
        self.calls.append(
            (
                "find",
                dict(query),
                session,
            )
        )

        if self.hidden_reads > 0:
            self.hidden_reads -= 1
            return None

        for row in self.rows:
            if all(
                row.get(key) == value
                for key, value
                in query.items()
            ):
                return dict(row)

        return None

    def insert_one(
        self,
        row,
        *,
        session,
    ):
        self.calls.append(
            (
                "insert",
                dict(row),
                session,
            )
        )

        if self.duplicate_on_insert:
            if self.invalidate_on_duplicate:
                session.in_transaction = False

            raise DuplicateKeyError(
                "duplicate"
            )

        self.rows.append(
            dict(row)
        )

        return SimpleNamespace(
            inserted_id="id"
        )


def tenant_evidence(
    *,
    evidence_id: str = "eligibility-001",
    idempotency_key: str = "idem-001",
    principal_id: str = "principal-a",
):
    decision = evaluate_privileged_eligibility(
        principal_id=principal_id,
        privileged_role_id=
            ENTERPRISE_ADMIN,
        principal_current=True,
        tenant_id="tenant-a",
        tenant_membership_current=True,
        workforce_required=True,
        tenant_workforce_current=True,
    )

    return PrivilegedEligibilityEvidence.from_decision(
        eligibility_evidence_id=
            evidence_id,
        decision=decision,
        evaluated_at=NOW,
        idempotency_key=
            idempotency_key,
    )


def platform_evidence(
    *,
    evidence_id: str = "eligibility-root",
    idempotency_key: str = "idem-root",
):
    decision = evaluate_privileged_eligibility(
        principal_id="principal-root",
        privileged_role_id=
            SOVEREIGN_ARCHITECT,
        principal_current=True,
        platform_prerequisite_proven=True,
    )

    return PrivilegedEligibilityEvidence.from_decision(
        eligibility_evidence_id=
            evidence_id,
        decision=decision,
        evaluated_at=NOW,
        idempotency_key=
            idempotency_key,
        platform_prerequisite_id=
            "platform-prerequisite-root",
        platform_prerequisite_revision=
            1,
        platform_prerequisite_fingerprint=
            "a" * 128,
        platform_prerequisite_source_evidence_reference=
            "core-governance-root",
    )


def test_collection_constant_is_exact() -> None:
    assert (
        COLLECTION
        == "privileged_eligibility_evidence"
    )


def test_indexes_are_exact_unique_and_have_no_ttl() -> None:
    collection = Collection()

    registry = (
        PrivilegedEligibilityEvidenceRegistry(
            collection
        )
    )

    registry.ensure_indexes()

    assert len(
        collection.indexes
    ) == 4

    by_name = {
        name: (
            keys,
            unique,
        )
        for keys, unique, name
        in collection.indexes
    }

    assert (
        by_name[
            "privileged_eligibility_evidence_identity_unique"
        ][1]
        is True
    )

    assert (
        by_name[
            "privileged_eligibility_scope_idempotency_unique"
        ][1]
        is True
    )

    assert (
        by_name[
            "privileged_eligibility_role_timeline"
        ][1]
        is False
    )

    assert (
        by_name[
            "privileged_eligibility_principal_timeline"
        ][1]
        is False
    )

    source = PRODUCTION.read_text(
        encoding="utf-8"
    )

    assert (
        "expireAfterSeconds"
        not in source
    )


def test_missing_or_inactive_transaction_rejects_before_read() -> None:
    collection = Collection()
    registry = PrivilegedEligibilityEvidenceRegistry(
        collection
    )

    with pytest.raises(
        PrivilegedEligibilityEvidenceTransactionRequiredError
    ):
        registry.create_or_replay(
            tenant_evidence(),
            session=None,
        )

    assert collection.calls == []

    with pytest.raises(
        PrivilegedEligibilityEvidenceTransactionRequiredError
    ):
        registry.create_or_replay(
            tenant_evidence(),
            session=Session(
                active=False
            ),
        )

    assert collection.calls == []


def test_fresh_insert_uses_exact_session() -> None:
    collection = Collection()

    registry = PrivilegedEligibilityEvidenceRegistry(
        collection
    )

    session = Session()
    value = tenant_evidence()

    assert (
        registry.create_or_replay(
            value,
            session=session,
        )
        == value
    )

    assert len(
        collection.rows
    ) == 1

    assert [
        call[0]
        for call in collection.calls
    ] == [
        "find",
        "find",
        "insert",
    ]

    assert all(
        call[-1] is session
        for call in collection.calls
    )


def test_exact_replay_returns_existing_without_insert() -> None:
    collection = Collection()

    value = tenant_evidence()
    row = value.to_persisted()
    row["_scope_tenant_key"] = "tenant-a"

    collection.rows.append(
        row
    )

    registry = PrivilegedEligibilityEvidenceRegistry(
        collection
    )

    result = registry.create_or_replay(
        value,
        session=Session(),
    )

    assert result == value

    assert [
        call[0]
        for call in collection.calls
    ] == [
        "find",
    ]


def test_divergent_idempotency_replay_rejects() -> None:
    collection = Collection()

    historic = tenant_evidence()
    row = historic.to_persisted()
    row["_scope_tenant_key"] = "tenant-a"

    collection.rows.append(
        row
    )

    registry = PrivilegedEligibilityEvidenceRegistry(
        collection
    )

    divergent = tenant_evidence(
        evidence_id="eligibility-other"
    )

    with pytest.raises(
        PrivilegedEligibilityEvidenceConflictError
    ) as captured:
        registry.create_or_replay(
            divergent,
            session=Session(),
        )

    assert (
        captured.value.code
        == "IDEMPOTENCY_KEY_DIVERGENT_REPLAY"
    )

    assert len(
        collection.rows
    ) == 1


def test_global_evidence_id_collision_rejects() -> None:
    collection = Collection()

    historic = tenant_evidence()
    row = historic.to_persisted()
    row["_scope_tenant_key"] = "tenant-a"

    collection.rows.append(
        row
    )

    registry = PrivilegedEligibilityEvidenceRegistry(
        collection
    )

    other = tenant_evidence(
        idempotency_key="idem-other",
        principal_id="principal-other",
    )

    with pytest.raises(
        PrivilegedEligibilityEvidenceConflictError
    ) as captured:
        registry.create_or_replay(
            other,
            session=Session(),
        )

    # Force same immutable identity while changing replay scope.
    collision = PrivilegedEligibilityEvidence.from_decision(
        eligibility_evidence_id=
            historic.eligibility_evidence_id,
        decision=evaluate_privileged_eligibility(
            principal_id="principal-other",
            privileged_role_id=
                ENTERPRISE_ADMIN,
            principal_current=True,
            tenant_id="tenant-a",
            tenant_membership_current=True,
        ),
        evaluated_at=NOW,
        idempotency_key=
            "idem-other",
    )

    with pytest.raises(
        PrivilegedEligibilityEvidenceConflictError
    ) as captured:
        registry.create_or_replay(
            collision,
            session=Session(),
        )

    assert (
        captured.value.code
        == "ELIGIBILITY_EVIDENCE_ID_COLLISION"
    )


def test_get_exact_and_absence() -> None:
    collection = Collection()

    value = tenant_evidence()
    row = value.to_persisted()
    row["_scope_tenant_key"] = "tenant-a"
    collection.rows.append(row)

    registry = PrivilegedEligibilityEvidenceRegistry(
        collection
    )

    assert (
        registry.get(
            eligibility_evidence_id=
                value.eligibility_evidence_id
        )
        == value
    )

    with pytest.raises(
        PrivilegedEligibilityEvidenceNotFoundError
    ):
        registry.get(
            eligibility_evidence_id=
                "missing"
        )


def test_platform_and_tenant_scope_replay_are_distinct() -> None:
    collection = Collection()

    tenant = tenant_evidence(
        idempotency_key="same-key",
    )

    platform = platform_evidence(
        idempotency_key="same-key",
    )

    tenant_row = tenant.to_persisted()
    tenant_row["_scope_tenant_key"] = (
        "tenant-a"
    )

    platform_row = platform.to_persisted()
    platform_row["_scope_tenant_key"] = ""

    collection.rows.extend(
        [
            tenant_row,
            platform_row,
        ]
    )

    registry = PrivilegedEligibilityEvidenceRegistry(
        collection
    )

    assert (
        registry.get_by_scope_idempotency(
            target_class=
                tenant.target_class.value,
            tenant_id=
                tenant.tenant_id,
            principal_id=
                tenant.principal_id,
            privileged_role_id=
                tenant.privileged_role_id,
            idempotency_key=
                tenant.idempotency_key,
        )
        == tenant
    )

    assert (
        registry.get_by_scope_idempotency(
            target_class=
                platform.target_class.value,
            tenant_id=None,
            principal_id=
                platform.principal_id,
            privileged_role_id=
                platform.privileged_role_id,
            idempotency_key=
                platform.idempotency_key,
        )
        == platform
    )


def test_corrupt_historic_row_fails_closed() -> None:
    collection = Collection()

    value = tenant_evidence()
    row = value.to_persisted()
    row["_scope_tenant_key"] = "tenant-a"

    row[
        "eligibility_evidence_fingerprint"
    ] = "f" * 128

    collection.rows.append(
        row
    )

    registry = PrivilegedEligibilityEvidenceRegistry(
        collection
    )

    with pytest.raises(
        PrivilegedEligibilityEvidencePersistedInvalidError
    ):
        registry.get(
            eligibility_evidence_id=
                value.eligibility_evidence_id
        )


def test_duplicate_race_exact_replay_converges() -> None:
    collection = Collection()

    value = tenant_evidence()

    durable = value.to_persisted()
    durable["_scope_tenant_key"] = "tenant-a"

    collection.rows.append(
        durable
    )

    collection.hidden_reads = 2
    collection.duplicate_on_insert = True

    registry = PrivilegedEligibilityEvidenceRegistry(
        collection
    )

    assert (
        registry.create_or_replay(
            value,
            session=Session(),
        )
        == value
    )


def test_duplicate_invalidated_transaction_requires_host_retry() -> None:
    collection = Collection()

    value = tenant_evidence()

    collection.duplicate_on_insert = True
    collection.invalidate_on_duplicate = True

    registry = PrivilegedEligibilityEvidenceRegistry(
        collection
    )

    with pytest.raises(
        PrivilegedEligibilityEvidenceConflictError
    ) as captured:
        registry.create_or_replay(
            value,
            session=Session(),
        )

    assert (
        captured.value.code
        == "WHOLE_TRANSACTION_RETRY_REQUIRED"
    )


def test_registry_surface_is_append_only_and_non_authorizing() -> None:
    registry_type = (
        PrivilegedEligibilityEvidenceRegistry
    )

    public = {
        name
        for name
        in vars(
            registry_type
        )
        if not name.startswith(
            "_"
        )
    }

    assert public == {
        "ensure_indexes",
        "get",
        "get_by_scope_idempotency",
        "create_or_replay",
    }

    source = PRODUCTION.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source
    )

    calls = {
        (
            node.func.attr
            if isinstance(
                node.func,
                ast.Attribute,
            )
            else node.func.id
        )
        for node in ast.walk(
            tree
        )
        if (
            isinstance(
                node,
                ast.Call,
            )
            and isinstance(
                node.func,
                (
                    ast.Attribute,
                    ast.Name,
                ),
            )
        )
    }

    assert calls.isdisjoint(
        {
            "update_one",
            "replace_one",
            "delete_one",
            "delete_many",
            "start_session",
            "start_transaction",
            "commit_transaction",
            "abort_transaction",
            "compare_and_swap",
        }
    )

    lowered = source.casefold()

    for forbidden in (
        "role_assignment_repository",
        "tenant_membership_repository",
        "tenant_business_role",
        "refresh_token",
        "privileged_activation",
        "break_glass",
        "financial_execution_repository",
        "fastapi",
    ):
        assert forbidden not in lowered


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_privileged_eligibility_evidence_registry.py
# VERSION: v1.0.0-P2-R2-A2-PRIVILEGED-ELIGIBILITY-EVIDENCE-REGISTRY-CERT
# TRANSACTION: caller-owned; active required before persistence access
# REPLAY: exact replay, divergence rejection, identity-collision rejection
# SCOPE: tenant/platform exact discriminator
# MUTATION: append-only insert only
# TTL: none
# AUTHORITY: no assignment, activation, session, break glass, or finance
# END OF WILSY OS SOVEREIGN ARTIFACT
