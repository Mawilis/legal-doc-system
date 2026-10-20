"""TITLE: WILSY OS Practitioner Access Codec Consumer Migration Certificate.
VERSION: v1.0.0-P47-R33-PRACTITIONER-ACCESS-CONSUMER-CERTIFICATE
AUTHORITY: Direct currentness, history-reader and registry verification only.
EPITOME: Proves codec-backed DENY precedence, exact tenant scope, caller-owned
    sessions, persisted tamper rejection, exact replay and lineage fail-closure.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_practitioner_matter_access_migration.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-20
CHANGELOG:
    2026-10-20 v1.0.0-P47-R33-PRACTITIONER-ACCESS-CONSUMER-CERTIFICATE
    Add reproducible migration coverage for three codec consumers.
COMPLIANCE: LAW EK-006; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Exact tenant predicates and post-hydration checks mandatory.
AUTHORITY BOUNDARY: Documentary reads/projection/persistence only; no access.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_practitioner_matter_access import (
    LegalPractitionerMatterAccessDecision,
)
from tools.eos.legal_operations.registry.legal_practitioner_matter_access_history_reader import (
    PractitionerMatterAccessHistoryReadError,
    read_practitioner_matter_access_history,
)
from tools.eos.legal_operations.registry.legal_practitioner_matter_access_registry import (
    PractitionerMatterAccessConflict,
    PractitionerMatterAccessPersistedInvalid,
    PractitionerMatterAccessTransactionRequired,
    append_evidence,
    get_by_id,
)
from tools.eos.legal_operations.service.legal_practitioner_matter_access_codec import (
    create_practitioner_matter_access,
    encode_practitioner_matter_access,
)
from tools.eos.legal_operations.service.legal_practitioner_matter_access_currentness import (
    LegalPractitionerMatterAccessCurrentnessState,
    project_legal_practitioner_matter_access_currentness,
)


T0 = datetime(2026, 10, 20, 8, 0, tzinfo=timezone.utc)


class Session:
    """Represent only the active transaction marker required by consumers."""

    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class Collection:
    """Record exact predicates, sessions and documents for direct tests."""

    def __init__(self, rows: list[dict[str, object]] | None = None) -> None:
        self.rows = list(rows or [])
        self.calls: list[tuple[str, dict[str, object], object]] = []

    def find(self, query: dict[str, object], *, session: object) -> list[dict[str, object]]:
        self.calls.append(("find", query, session))
        return [row for row in self.rows if all(row.get(k) == v for k, v in query.items())]

    def find_one(
        self, query: dict[str, object], *, session: object
    ) -> dict[str, object] | None:
        self.calls.append(("find_one", query, session))
        return next(
            (row for row in self.rows if all(row.get(k) == v for k, v in query.items())),
            None,
        )

    def insert_one(self, document: dict[str, object], *, session: object) -> None:
        self.calls.append(("insert_one", document, session))
        self.rows.append(dict(document))


def _evidence(
    *,
    evidence_id: str = "access-1",
    tenant: str = "tenant-1",
    revision: int = 1,
    decision: LegalPractitionerMatterAccessDecision = (
        LegalPractitionerMatterAccessDecision.ALLOW
    ),
    effective_from: datetime = T0,
    predecessor: str | None = None,
):
    return create_practitioner_matter_access(
        access_evidence_id=evidence_id,
        tenant_id=tenant,
        case_matter_id="matter-1",
        practitioner_principal_id="practitioner-1",
        revision=revision,
        decision=decision,
        effective_from=effective_from,
        effective_until=None,
        issued_by_principal_id="actor-1",
        source_evidence_fingerprint="a" * 128,
        supersedes_fingerprint=predecessor,
    )


def test_currentness_preserves_explicit_deny_precedence_and_no_authority() -> None:
    allow = _evidence()
    deny = _evidence(
        evidence_id="deny-1",
        decision=LegalPractitionerMatterAccessDecision.DENY,
    )
    result = project_legal_practitioner_matter_access_currentness(
        tenant_id="tenant-1",
        case_matter_id="matter-1",
        practitioner_principal_id="practitioner-1",
        evaluation_time=T0 + timedelta(seconds=1),
        evidence=(allow, deny),
    )
    assert result.state is LegalPractitionerMatterAccessCurrentnessState.DENY_BLOCKED
    assert result.decisive_fingerprints == (deny.fingerprint,)
    assert result.permits_access is False


def test_currentness_rejects_cross_tenant_and_forged_frozen_values() -> None:
    foreign = _evidence(tenant="tenant-2")
    result = project_legal_practitioner_matter_access_currentness(
        tenant_id="tenant-1",
        case_matter_id="matter-1",
        practitioner_principal_id="practitioner-1",
        evaluation_time=T0,
        evidence=(foreign,),
    )
    assert result.state is LegalPractitionerMatterAccessCurrentnessState.CORRUPT_BLOCKED
    forged = _evidence()
    object.__setattr__(forged, "case_matter_id", "matter-2")
    result = project_legal_practitioner_matter_access_currentness(
        tenant_id="tenant-1",
        case_matter_id="matter-1",
        practitioner_principal_id="practitioner-1",
        evaluation_time=T0,
        evidence=(forged,),
    )
    assert result.state is LegalPractitionerMatterAccessCurrentnessState.CORRUPT_BLOCKED


def test_history_reader_uses_exact_scope_and_same_session() -> None:
    value = _evidence()
    row = {**encode_practitioner_matter_access(value), "_id": "mongo-id"}
    collection = Collection([row])
    session = Session()
    result = read_practitioner_matter_access_history(
        tenant_id="tenant-1",
        case_matter_id="matter-1",
        practitioner_principal_id="practitioner-1",
        collection=collection,
        session=session,
    )
    assert result == (value,)
    assert collection.calls == [
        (
            "find",
            {
                "tenant_id": "tenant-1",
                "case_matter_id": "matter-1",
                "practitioner_principal_id": "practitioner-1",
            },
            session,
        )
    ]


def test_history_reader_rejects_inactive_transaction_and_tamper() -> None:
    with pytest.raises(PractitionerMatterAccessHistoryReadError) as inactive:
        read_practitioner_matter_access_history(
            tenant_id="tenant-1",
            case_matter_id="matter-1",
            practitioner_principal_id="practitioner-1",
            collection=Collection(),
            session=Session(False),
        )
    assert inactive.value.code == "P9_R99_ACTIVE_TRANSACTION_REQUIRED"
    corrupt = encode_practitioner_matter_access(_evidence())
    corrupt["issued_by_principal_id"] = "forged-actor"
    with pytest.raises(PractitionerMatterAccessHistoryReadError) as invalid:
        read_practitioner_matter_access_history(
            tenant_id="tenant-1",
            case_matter_id="matter-1",
            practitioner_principal_id="practitioner-1",
            collection=Collection([corrupt]),
            session=Session(),
        )
    assert invalid.value.code == "P9_R99_PERSISTED_HISTORY_INVALID"


def test_registry_appends_once_and_returns_exact_replay() -> None:
    value = _evidence()
    collection = Collection()
    session = Session()
    assert append_evidence(evidence=value, collection=collection, session=session) == value
    assert append_evidence(evidence=value, collection=collection, session=session) == value
    assert len(collection.rows) == 1
    assert get_by_id(
        tenant_id="tenant-1",
        access_evidence_id="access-1",
        collection=collection,
        session=session,
    ) == value


def test_registry_rejects_inactive_transaction_corruption_and_successor() -> None:
    value = _evidence()
    with pytest.raises(PractitionerMatterAccessTransactionRequired):
        append_evidence(evidence=value, collection=Collection(), session=Session(False))
    corrupt = encode_practitioner_matter_access(value)
    corrupt["case_matter_id"] = "matter-2"
    with pytest.raises(PractitionerMatterAccessPersistedInvalid):
        get_by_id(
            tenant_id="tenant-1",
            access_evidence_id="access-1",
            collection=Collection([corrupt]),
            session=Session(),
        )
    successor = _evidence(
        evidence_id="access-2",
        revision=2,
        effective_from=T0 + timedelta(days=1),
        predecessor=value.fingerprint,
    )
    with pytest.raises(PractitionerMatterAccessConflict) as blocked:
        append_evidence(
            evidence=successor,
            collection=Collection(),
            session=Session(),
        )
    assert str(blocked.value) == "P9_R105_SUCCESSOR_LINEAGE_NOT_CERTIFIED"


def test_registry_does_not_expose_foreign_tenant_absence() -> None:
    collection = Collection([encode_practitioner_matter_access(_evidence(tenant="tenant-2"))])
    assert get_by_id(
        tenant_id="tenant-1",
        access_evidence_id="access-1",
        collection=collection,
        session=Session(),
    ) is None


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practitioner_matter_access_migration.py
# VERSION: v1.0.0-P47-R33-PRACTITIONER-ACCESS-CONSUMER-CERTIFICATE
# AUTHORITY BOUNDARY: DIRECT CURRENTNESS, HISTORY AND REGISTRY CERTIFICATE
# TENANT POSTURE: EXACT SCOPE; FOREIGN TENANT NON-DISCLOSURE
# FAIL-CLOSED POSTURE: DENY, TAMPER, INACTIVE SESSION AND LINEAGE REJECT
# ACCESS / ISSUANCE / REASSIGNMENT / FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
