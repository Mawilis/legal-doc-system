"""TITLE: Sheriff Appointment Evidence Registry Unit Certificate
VERSION: v1.0.1-SHERIFF-APPOINTMENT-EVIDENCE-REGISTRY-UNIT-CERT
AUTHORITY: Unit certification of immutable tenant-scoped registry persistence.
EPITOME: Verify caller transaction boundaries, tenant-first indexes, strict
    append-only lineage, exact replay, divergent replay and corruption rejection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_sheriff_appointment_source_evidence_registry.py
COLLABORATION / OWNERSHIP: Registry-only certificate; no source trust root,
    identity authentication, IAM, office queue or execution behavior.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG:
    2026-11-02 v1.0.1-SHERIFF-APPOINTMENT-EVIDENCE-REGISTRY-UNIT-CERT
    Adds scope-drift, strict-document-shape, transaction and disputed-source
    currentness adversarial cases.
    2026-11-02 v1.0.0-SHERIFF-APPOINTMENT-EVIDENCE-REGISTRY-UNIT-CERT
    Adds deterministic in-memory Mongo contract tests for append-only history,
    tenant isolation, transaction requirements, replay and corruption.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only.
TENANT BOUNDARY: Exact tenant; pseudo tenants reject.
AUTHORITY BOUNDARY: Persistence evidence only; no appointment or access grant.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from tools.eos.legal_operations.domain.sheriff_appointment_source_evidence import (
    SheriffAppointmentCapacity,
    SheriffAppointmentIssuerAuthority,
    SheriffAppointmentSourceEvidence,
    SheriffAppointmentStatutoryBasis,
    SheriffSourceObservationState,
    SheriffSourceVerificationMethod,
)
from tools.eos.legal_operations.registry.sheriff_appointment_source_evidence_registry import (
    INDEX_NAMES,
    SheriffAppointmentEvidenceConflict,
    SheriffAppointmentEvidenceNotFound,
    SheriffAppointmentEvidencePersistedInvalid,
    SheriffAppointmentEvidenceRevision,
    SheriffAppointmentEvidenceRegistry,
    SheriffAppointmentEvidenceTransactionRequired,
)


NOW = datetime(2026, 11, 2, 10, 0, tzinfo=timezone.utc)


class Session:
    """Minimal session contract exposing only active-transaction state."""

    in_transaction = True


class Cursor(list[dict[str, object]]):
    """Small deterministic cursor implementing the Mongo sort/limit contract."""

    def sort(self, key: str, direction: int) -> "Cursor":
        return Cursor(sorted(self, key=lambda row: row[key], reverse=direction < 0))

    def limit(self, count: int) -> "Cursor":
        return Cursor(self[:count])


class Collection:
    """In-memory Mongo-compatible collection for deterministic unit tests."""

    def __init__(self) -> None:
        self.documents: list[dict[str, object]] = []
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, object]]] = []

    def create_index(self, keys: list[tuple[str, int]], **options: object) -> str:
        self.indexes.append((keys, dict(options)))
        return str(options.get("name", ""))

    def find(self, query: dict[str, object], *, session: object) -> Cursor:
        return Cursor(
            deepcopy(row)
            for row in self.documents
            if all(row.get(key) == value for key, value in query.items())
        )

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object,
    ) -> dict[str, object] | None:
        for row in self.documents:
            if all(row.get(key) == value for key, value in query.items()):
                return deepcopy(row)
        return None

    def insert_one(self, document: dict[str, object], *, session: object) -> None:
        self.documents.append(deepcopy(document))


def evidence(**overrides: object) -> SheriffAppointmentSourceEvidence:
    """Build one synthetic, non-authorizing section 2(1) observation."""
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "evidence_id": "appointment-evidence-1",
        "revision": 1,
        "principal_id": "principal-sheriff",
        "verified_subject_reference": "subject-1",
        "sheriff_office_id": "office-jhb",
        "district_id": "district-jhb",
        "court_reference": "court-jhb",
        "service_area_references": ("area-jhb-central",),
        "capacity": SheriffAppointmentCapacity.SHERIFF,
        "statutory_basis": SheriffAppointmentStatutoryBasis.SECTION_2_1,
        "issuer_authority": SheriffAppointmentIssuerAuthority.MINISTER,
        "instrument_reference": "ministerial-instrument-1",
        "instrument_fingerprint": "a" * 128,
        "source_uri": "https://www.justice.gov.za/notice/appointment-1",
        "source_observation_state": SheriffSourceObservationState.HUMAN_OBSERVED_PUBLIC_RECORD,
        "source_verification_method": SheriffSourceVerificationMethod.PUBLIC_WEB_OBSERVATION,
        "source_verification_reference": "observation-1",
        "verified_by_principal_id": "independent-verifier",
        "observed_at": NOW,
        "effective_from": NOW - timedelta(days=1),
        "effective_until": None,
    }
    values.update(overrides)
    return SheriffAppointmentSourceEvidence(**values)  # type: ignore[arg-type]


def revision(
    item: SheriffAppointmentSourceEvidence,
    predecessor: str | None = None,
) -> SheriffAppointmentEvidenceRevision:
    """Bind a domain observation to the registry lineage fingerprint."""
    return SheriffAppointmentEvidenceRevision(
        revision=item.revision,
        predecessor_registry_fingerprint=predecessor,
        evidence=item,
    )


def test_every_read_and_write_requires_active_caller_transaction() -> None:
    registry = SheriffAppointmentEvidenceRegistry(Collection())
    with pytest.raises(SheriffAppointmentEvidenceTransactionRequired):
        registry.get_history_if_any(
            tenant_id="tenant-a",
            evidence_id="appointment-evidence-1",
            session=None,
        )
    with pytest.raises(SheriffAppointmentEvidenceTransactionRequired):
        registry.persist_revision(revision(evidence()), session=None)


def test_indexes_are_deterministic_tenant_first_and_never_ttl() -> None:
    collection = Collection()
    registry = SheriffAppointmentEvidenceRegistry(collection)
    registry.ensure_indexes()
    assert tuple(options["name"] for _, options in collection.indexes) == INDEX_NAMES
    assert all(keys[0] == ("tenant_id", 1) for keys, _ in collection.indexes)
    assert not any(options.get("expireAfterSeconds") is not None for _, options in collection.indexes)
    assert collection.indexes[1][1]["partialFilterExpression"] == {"revision": 1}
    assert collection.indexes[2][1]["partialFilterExpression"] == {
        "supersedes_fingerprint": {"$type": "string"}
    }


@pytest.mark.parametrize("tenant", ["default", "global", "root", "*"])
def test_pseudo_tenant_reads_reject(tenant: str) -> None:
    registry = SheriffAppointmentEvidenceRegistry(Collection())
    with pytest.raises(SheriffAppointmentEvidenceConflict):
        registry.get_history_if_any(
            tenant_id=tenant,
            evidence_id="appointment-evidence-1",
            session=Session(),
        )


def test_append_exact_replay_and_tenant_isolation() -> None:
    collection = Collection()
    registry = SheriffAppointmentEvidenceRegistry(collection)
    item = revision(evidence())
    first = registry.persist_revision(item, session=Session())
    replay = registry.persist_revision(item, session=Session())
    assert first == replay
    assert first.permits_operational_access is False
    assert first.permits_legal_execution is False
    assert len(collection.documents) == 1
    assert len(
        registry.get_history(
            tenant_id="tenant-a",
            evidence_id="appointment-evidence-1",
            session=Session(),
        )
    ) == 1
    assert registry.get_history_if_any(
        tenant_id="tenant-b",
        evidence_id="appointment-evidence-1",
        session=Session(),
    ) == ()


def test_divergent_replay_rejects_without_replacing_durable_truth() -> None:
    collection = Collection()
    registry = SheriffAppointmentEvidenceRegistry(collection)
    first = revision(evidence())
    registry.persist_revision(first, session=Session())
    divergent = revision(evidence(instrument_fingerprint="b" * 128))
    with pytest.raises(SheriffAppointmentEvidenceConflict):
        registry.persist_revision(divergent, session=Session())
    assert len(collection.documents) == 1
    assert collection.documents[0]["fingerprint"] == first.evidence.fingerprint


def test_successor_requires_both_registry_and_source_predecessors() -> None:
    collection = Collection()
    registry = SheriffAppointmentEvidenceRegistry(collection)
    first = revision(evidence())
    registry.persist_revision(first, session=Session())
    second_evidence = evidence(
        revision=2,
        supersedes_fingerprint=first.evidence.fingerprint,
        effective_from=NOW + timedelta(days=1),
        observed_at=NOW + timedelta(seconds=1),
        instrument_reference="ministerial-instrument-2",
        instrument_fingerprint="b" * 128,
    )
    second = revision(second_evidence, first.registry_fingerprint)
    stored = registry.persist_revision(second, session=Session())
    assert stored == second
    history = registry.get_history(
        tenant_id="tenant-a",
        evidence_id="appointment-evidence-1",
        session=Session(),
    )
    assert tuple(item.revision for item in history) == (1, 2)


def test_wrong_predecessor_and_revision_gap_reject() -> None:
    collection = Collection()
    registry = SheriffAppointmentEvidenceRegistry(collection)
    first = revision(evidence())
    registry.persist_revision(first, session=Session())
    successor = evidence(
        revision=2,
        supersedes_fingerprint=first.evidence.fingerprint,
        effective_from=NOW + timedelta(days=1),
        observed_at=NOW + timedelta(seconds=1),
    )
    wrong_parent = revision(successor, "0" * 128)
    with pytest.raises(SheriffAppointmentEvidenceConflict):
        registry.persist_revision(wrong_parent, session=Session())
    gap = evidence(
        revision=3,
        supersedes_fingerprint=successor.fingerprint,
        effective_from=NOW + timedelta(days=2),
        observed_at=NOW + timedelta(seconds=2),
    )
    with pytest.raises(SheriffAppointmentEvidenceConflict):
        registry.persist_revision(revision(gap, first.registry_fingerprint), session=Session())


def test_corrupt_persisted_fingerprint_fails_closed() -> None:
    collection = Collection()
    registry = SheriffAppointmentEvidenceRegistry(collection)
    registry.persist_revision(revision(evidence()), session=Session())
    collection.documents[0]["fingerprint"] = "0" * 128
    with pytest.raises(SheriffAppointmentEvidencePersistedInvalid):
        registry.get_history_if_any(
            tenant_id="tenant-a",
            evidence_id="appointment-evidence-1",
            session=Session(),
        )


def test_history_absence_is_tenant_scoped_and_not_found_is_explicit() -> None:
    registry = SheriffAppointmentEvidenceRegistry(Collection())
    with pytest.raises(SheriffAppointmentEvidenceNotFound):
        registry.get_history(
            tenant_id="tenant-a",
            evidence_id="appointment-evidence-1",
            session=Session(),
        )


def test_currentness_is_derived_from_history_and_expiry_fails_closed() -> None:
    collection = Collection()
    registry = SheriffAppointmentEvidenceRegistry(collection)
    item = evidence(effective_until=NOW + timedelta(days=1))
    registry.persist_revision(revision(item), session=Session())
    assert registry.resolve_current(
        tenant_id="tenant-a",
        evidence_id="appointment-evidence-1",
        at=NOW,
        session=Session(),
    ) is not None
    assert registry.resolve_current(
        tenant_id="tenant-a",
        evidence_id="appointment-evidence-1",
        at=NOW + timedelta(days=1),
        session=Session(),
    ) is None


def test_currentness_requires_transaction_and_disputed_observation_blocks() -> None:
    registry = SheriffAppointmentEvidenceRegistry(Collection())
    with pytest.raises(SheriffAppointmentEvidenceTransactionRequired):
        registry.resolve_current(
            tenant_id="tenant-a",
            evidence_id="appointment-evidence-1",
            at=NOW,
            session=None,
        )

    collection = Collection()
    registry = SheriffAppointmentEvidenceRegistry(collection)
    disputed = evidence(
        source_observation_state=SheriffSourceObservationState.DISPUTED,
    )
    registry.persist_revision(revision(disputed), session=Session())
    assert registry.resolve_current(
        tenant_id="tenant-a",
        evidence_id="appointment-evidence-1",
        at=NOW,
        session=Session(),
    ) is None


def test_successor_cannot_change_appointment_identity_or_statutory_scope() -> None:
    collection = Collection()
    registry = SheriffAppointmentEvidenceRegistry(collection)
    first = revision(evidence())
    registry.persist_revision(first, session=Session())
    changed_scope = evidence(
        revision=2,
        principal_id="different-principal",
        supersedes_fingerprint=first.evidence.fingerprint,
        effective_from=NOW + timedelta(days=1),
        observed_at=NOW + timedelta(seconds=1),
    )
    successor = revision(changed_scope, first.registry_fingerprint)
    with pytest.raises(SheriffAppointmentEvidenceConflict):
        registry.persist_revision(successor, session=Session())


def test_persisted_document_shape_rejects_unrecognized_fields() -> None:
    collection = Collection()
    registry = SheriffAppointmentEvidenceRegistry(collection)
    registry.persist_revision(revision(evidence()), session=Session())
    collection.documents[0]["unexpected_authority"] = "ADMIN"
    with pytest.raises(SheriffAppointmentEvidencePersistedInvalid):
        registry.get_history_if_any(
            tenant_id="tenant-a",
            evidence_id="appointment-evidence-1",
            session=Session(),
        )


def test_registry_revision_must_match_domain_revision() -> None:
    item = evidence()
    with pytest.raises(SheriffAppointmentEvidenceConflict):
        SheriffAppointmentEvidenceRevision(
            revision=2,
            predecessor_registry_fingerprint="a" * 128,
            evidence=item,
        )


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: tests/unit/test_sheriff_appointment_source_evidence_registry.py
# VERSION: v1.0.1-SHERIFF-APPOINTMENT-EVIDENCE-REGISTRY-UNIT-CERT
# AUTHORITY BOUNDARY: deterministic unit certification of immutable persistence only
# TENANT POSTURE: exact tenant-first reads, writes, replay and history
# FAIL-CLOSED POSTURE: absent transaction, pseudo tenant, divergent replay, gap, fork and corruption reject
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
