"""TITLE: R63 Professional Standing Evidence Registry Adversarial Certificate.
VERSION: v1.0.0-R63-REGULATORY-EVIDENCE-FOUNDATION-CERT
AUTHORITY: Direct in-memory contract certificate; no operational authority.
EPITOME: Prove transaction, source, replay, lineage, tenant, corruption,
    revocation, staleness, jurisdiction, and no-authority invariants.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_practitioner_professional_standing_evidence_registry.py
COLLABORATION / OWNERSHIP: Wilsy OS Legal Operations and Core Governance.
CERTIFICATION / UPDATE DATE: 2026-10-21
CHANGELOG: 2026-10-21 v1.0.0 introduces the R63 adversarial certificate.
COMPLIANCE: Synthetic opaque fixtures only; POPIA §19 / GDPR Art. 32 / SOC2 CC7.2.
TENANT BOUNDARY: Exact tenant scope; cross-tenant reads disclose no existence.
AUTHORITY BOUNDARY: No practising, FFC, IAM, matter, or reassignment grant.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any, cast

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_practitioner_professional_standing_evidence import (
    LegalPractitionerProfessionalStandingEvidence as Evidence,
    ProfessionalStandingCurrentnessState,
)
from tools.eos.legal_operations.registry.legal_practitioner_professional_standing_evidence_registry import (
    INDEX_NAMES,
    LPC_FFC_VERIFICATION_ISSUER,
    LPC_FFC_VERIFICATION_URI,
    LPC_PRACTITIONER_DIRECTORY_ISSUER,
    LPC_PRACTITIONER_DIRECTORY_URI,
    ProfessionalStandingEvidenceConflict,
    ProfessionalStandingEvidencePersistedInvalid,
    ProfessionalStandingEvidenceRegistry,
    ProfessionalStandingEvidenceRetryTransaction,
    ProfessionalStandingEvidenceRevision,
    ProfessionalStandingEvidenceTransactionRequired,
)


NOW = datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)


class Session:
    """Represent only the active caller-owned transaction marker."""

    in_transaction = True


class Cursor:
    """Provide the bounded cursor behavior consumed by the registry."""

    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def sort(self, field: str, _direction: object) -> Cursor:
        self.rows.sort(key=lambda row: cast(Any, row[field]))
        return self

    def limit(self, count: int) -> Cursor:
        self.rows = self.rows[:count]
        return self

    def __iter__(self):
        return iter(deepcopy(self.rows))


class Collection:
    """Exercise registry decisions without simulating Mongo authority."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[tuple[object, dict[str, object]]] = []
        self.force_duplicate = False

    def create_index(self, keys: object, **kwargs: object) -> None:
        self.indexes.append((keys, kwargs))

    def find(self, query: dict[str, object], *, session: object) -> Cursor:
        assert session is not None
        return Cursor([
            row for row in self.rows
            if all(row.get(key) == value for key, value in query.items())
        ])

    def find_one(
        self, query: dict[str, object], *, session: object
    ) -> dict[str, object] | None:
        return next(iter(self.find(query, session=session)), None)

    def insert_one(self, document: dict[str, object], *, session: object) -> None:
        assert session is not None
        if self.force_duplicate:
            raise DuplicateKeyError("race")
        self.rows.append(deepcopy(document))


def evidence(**overrides: object) -> Evidence:
    values: dict[str, object] = {
        "evidence_id": "evidence-1",
        "tenant_id": "tenant-a",
        "practitioner_principal_id": "principal-a",
        "verified_subject_id": "lpc-106800",
        "issuer_source_id": LPC_PRACTITIONER_DIRECTORY_ISSUER,
        "jurisdiction": "ZA",
        "evidence_kind": "PRACTISING_STATUS",
        "outcome": "VERIFIED_CURRENT",
        "verification_method": "PUBLIC_WEB_OBSERVATION",
        "evidence_reference": "lpc-observation-1",
        "source_uri": LPC_PRACTITIONER_DIRECTORY_URI,
        "observed_at": NOW,
        "valid_until": NOW + timedelta(days=1),
    }
    values.update(overrides)
    return Evidence(**values)  # type: ignore[arg-type]


def revision(number: int = 1, previous: str | None = None, **overrides: object):
    return ProfessionalStandingEvidenceRevision(
        revision=number,
        predecessor_registry_fingerprint=previous,
        evidence=evidence(**overrides),
    )


def registry() -> tuple[ProfessionalStandingEvidenceRegistry, Collection]:
    collection = Collection()
    return ProfessionalStandingEvidenceRegistry(collection), collection


def persist(registry: ProfessionalStandingEvidenceRegistry, item):
    return registry.create_or_replay(item, session=Session())


def test_indexes_are_named_unique_where_required_and_never_ttl() -> None:
    subject, collection = registry()
    subject.ensure_indexes()
    assert {options["name"] for _, options in collection.indexes} == set(INDEX_NAMES)
    assert all("expireAfterSeconds" not in options for _, options in collection.indexes)
    assert sum(options.get("unique") is True for _, options in collection.indexes) == 5


def test_active_caller_owned_transaction_is_required_for_reads_and_writes() -> None:
    subject, _ = registry()
    with pytest.raises(ProfessionalStandingEvidenceTransactionRequired):
        subject.create_or_replay(revision(), session=None)
    with pytest.raises(ProfessionalStandingEvidenceTransactionRequired):
        subject.get_history_if_any(
            tenant_id="tenant-a", practitioner_principal_id="principal-a",
            verified_subject_id="lpc-106800", jurisdiction="ZA",
            evidence_kind="PRACTISING_STATUS", session=object(),
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"issuer_source_id": "attacker"},
        {"source_uri": "https://attacker.invalid/"},
        {"verification_method": "ATTESTED_DOCUMENT_REVIEW"},
        {"jurisdiction": "GB"},
        {
            "evidence_kind": "FIDELITY_FUND_CERTIFICATE_STATUS",
            "issuer_source_id": LPC_PRACTITIONER_DIRECTORY_ISSUER,
            "source_uri": LPC_PRACTITIONER_DIRECTORY_URI,
        },
    ],
)
def test_issuer_impersonation_source_mismatch_and_jurisdiction_fail_closed(
    changes: dict[str, object],
) -> None:
    with pytest.raises(ProfessionalStandingEvidenceConflict) as error:
        ProfessionalStandingEvidenceRevision(1, None, evidence(**changes))
    assert str(error.value) == "R63_PROFESSIONAL_EVIDENCE_ISSUER_SOURCE_UNAUTHORIZED"


def test_ffc_is_separate_and_requires_its_own_official_source() -> None:
    item = revision(
        evidence_kind="FIDELITY_FUND_CERTIFICATE_STATUS",
        issuer_source_id=LPC_FFC_VERIFICATION_ISSUER,
        source_uri=LPC_FFC_VERIFICATION_URI,
    )
    assert str(item.evidence.evidence_kind) == "FIDELITY_FUND_CERTIFICATE_STATUS"
    assert item.permits_operational_access is False
    assert item.permits_reassignment_execution is False


def test_exact_replay_returns_same_record_and_divergent_replay_rejects() -> None:
    subject, _ = registry()
    first = revision()
    assert persist(subject, first) == first
    assert persist(subject, first) == first
    divergent = revision(outcome="NOT_CURRENT")
    with pytest.raises(ProfessionalStandingEvidenceConflict) as error:
        persist(subject, divergent)
    assert str(error.value) == "R63_PROFESSIONAL_EVIDENCE_DIVERGENT_REPLAY"


def test_lineage_requires_exact_next_revision_and_predecessor() -> None:
    subject, _ = registry()
    first = persist(subject, revision())
    with pytest.raises(ProfessionalStandingEvidenceConflict):
        persist(subject, revision(3, first.registry_fingerprint))
    with pytest.raises(ProfessionalStandingEvidenceConflict):
        persist(subject, revision(2, "0" * 128, evidence_id="evidence-2",
                                  evidence_reference="lpc-observation-2"))


def test_complete_lineage_currentness_handles_stale_revoked_and_verified() -> None:
    subject, _ = registry()
    first = persist(subject, revision())
    verified = subject.evaluate_currentness(
        tenant_id="tenant-a", practitioner_principal_id="principal-a",
        verified_subject_id="lpc-106800", jurisdiction="ZA",
        evidence_kind="PRACTISING_STATUS", evaluation_time=NOW, session=Session(),
    )
    assert verified.state is ProfessionalStandingCurrentnessState.VERIFIED_DOCUMENTARY_ONLY
    second = revision(
        2, first.registry_fingerprint, evidence_id="evidence-2",
        evidence_reference="lpc-observation-2", outcome="REVOKED",
        revoked_at=NOW + timedelta(hours=1), observed_at=NOW + timedelta(hours=1),
        valid_until=NOW + timedelta(days=2),
    )
    persist(subject, second)
    revoked = subject.evaluate_currentness(
        tenant_id="tenant-a", practitioner_principal_id="principal-a",
        verified_subject_id="lpc-106800", jurisdiction="ZA",
        evidence_kind="PRACTISING_STATUS", evaluation_time=NOW + timedelta(hours=2),
        session=Session(),
    )
    assert revoked.state is ProfessionalStandingCurrentnessState.REVOKED_BLOCKED
    assert revoked.permits_operational_access is False
    stale = subject.evaluate_currentness(
        tenant_id="tenant-a", practitioner_principal_id="principal-a",
        verified_subject_id="lpc-106800", jurisdiction="ZA",
        evidence_kind="PRACTISING_STATUS", evaluation_time=NOW + timedelta(days=3),
        session=Session(),
    )
    assert stale.state is ProfessionalStandingCurrentnessState.EXPIRED_BLOCKED


def test_cross_tenant_read_is_empty_and_does_not_disclose_existing_lineage() -> None:
    subject, _ = registry()
    persist(subject, revision())
    assert subject.get_history_if_any(
        tenant_id="tenant-b", practitioner_principal_id="principal-a",
        verified_subject_id="lpc-106800", jurisdiction="ZA",
        evidence_kind="PRACTISING_STATUS", session=Session(),
    ) == ()


def test_persisted_tampering_and_ambiguous_lineage_are_deterministically_rejected() -> None:
    subject, collection = registry()
    persist(subject, revision())
    collection.rows[0]["source_uri"] = "https://attacker.invalid/"
    with pytest.raises((ProfessionalStandingEvidencePersistedInvalid, ProfessionalStandingEvidenceConflict)):
        subject.get_history_if_any(
            tenant_id="tenant-a", practitioner_principal_id="principal-a",
            verified_subject_id="lpc-106800", jurisdiction="ZA",
            evidence_kind="PRACTISING_STATUS", session=Session(),
        )


def test_duplicate_key_race_requires_whole_transaction_retry() -> None:
    subject, collection = registry()
    collection.force_duplicate = True
    with pytest.raises(ProfessionalStandingEvidenceRetryTransaction) as error:
        persist(subject, revision())
    assert str(error.value) == "R63_PROFESSIONAL_EVIDENCE_CONCURRENT_WRITE_RETRY"


def test_firm_affiliation_iam_and_matter_access_fields_cannot_be_supplied() -> None:
    for field in (
        "firm_id", "tenant_affiliation_current", "iam_allowed",
        "matter_access_allowed", "reassignment_allowed",
    ):
        with pytest.raises(TypeError):
            evidence(**{field: True})


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practitioner_professional_standing_evidence_registry.py
# VERSION: v1.0.0-R63-REGULATORY-EVIDENCE-FOUNDATION-CERT
# AUTHORITY BOUNDARY: direct adversarial certificate only; no operational grant
# TENANT POSTURE: exact tenant scope and non-disclosing cross-tenant absence
# FAIL-CLOSED POSTURE: source, replay, lineage, corruption and race reject
# REASSIGNMENT / FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
