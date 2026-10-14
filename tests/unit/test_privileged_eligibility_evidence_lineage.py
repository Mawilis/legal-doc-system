"""Direct certificate for versioned P2 durable prerequisite lineage."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

import tools.eos.auth.privileged_eligibility_evidence as evidence_module
from tools.eos.auth.privileged_eligibility import (
    evaluate_privileged_eligibility,
)
from tools.eos.auth.privileged_eligibility_evidence import (
    LEGACY_SCHEMA,
    LEGACY_VERSION,
    SCHEMA,
    VERSION,
    PrivilegedEligibilityEvidence,
    PrivilegedEligibilityEvidenceError,
)


AT = datetime(
    2026,
    10,
    14,
    18,
    0,
    tzinfo=timezone.utc,
)

PREREQUISITE_ID = "platform-prerequisite-001"
PREREQUISITE_REVISION = 7
PREREQUISITE_FINGERPRINT = "a" * 128
SOURCE_REFERENCE = "core-governance-evidence-001"


def platform_decision():
    return evaluate_privileged_eligibility(
        principal_id="principal-platform",
        privileged_role_id="SOVEREIGN_ARCHITECT",
        principal_current=True,
        platform_prerequisite_proven=True,
    )


def tenant_decision():
    return evaluate_privileged_eligibility(
        principal_id="principal-tenant",
        privileged_role_id="ENTERPRISE_ADMIN",
        principal_current=True,
        tenant_id="tenant-001",
        tenant_membership_current=True,
    )


def platform_evidence(
    *,
    source_reference: str = SOURCE_REFERENCE,
) -> PrivilegedEligibilityEvidence:
    return PrivilegedEligibilityEvidence.from_decision(
        eligibility_evidence_id="evidence-platform-001",
        decision=platform_decision(),
        evaluated_at=AT,
        idempotency_key="idem-platform-001",
        platform_prerequisite_id=PREREQUISITE_ID,
        platform_prerequisite_revision=PREREQUISITE_REVISION,
        platform_prerequisite_fingerprint=
            PREREQUISITE_FINGERPRINT,
        platform_prerequisite_source_evidence_reference=
            source_reference,
    )


def test_new_platform_evidence_is_v2_and_carries_complete_lineage() -> None:
    value = platform_evidence()
    row = value.to_persisted()

    assert row["schema"] == SCHEMA
    assert row["version"] == VERSION

    assert row["platform_prerequisite_id"] == PREREQUISITE_ID
    assert (
        row["platform_prerequisite_revision"]
        == PREREQUISITE_REVISION
    )
    assert (
        row["platform_prerequisite_fingerprint"]
        == PREREQUISITE_FINGERPRINT
    )
    assert (
        row["platform_prerequisite_source_evidence_reference"]
        == SOURCE_REFERENCE
    )

    assert (
        PrivilegedEligibilityEvidence.from_persisted(row)
        == value
    )


@pytest.mark.parametrize(
    (
        "platform_prerequisite_id",
        "platform_prerequisite_revision",
        "platform_prerequisite_fingerprint",
        "platform_prerequisite_source_evidence_reference",
    ),
    [
        (
            None,
            PREREQUISITE_REVISION,
            PREREQUISITE_FINGERPRINT,
            SOURCE_REFERENCE,
        ),
        (
            PREREQUISITE_ID,
            None,
            PREREQUISITE_FINGERPRINT,
            SOURCE_REFERENCE,
        ),
        (
            PREREQUISITE_ID,
            PREREQUISITE_REVISION,
            None,
            SOURCE_REFERENCE,
        ),
        (
            PREREQUISITE_ID,
            PREREQUISITE_REVISION,
            PREREQUISITE_FINGERPRINT,
            None,
        ),
    ],
)
def test_new_platform_partial_lineage_rejects(
    platform_prerequisite_id: object,
    platform_prerequisite_revision: object,
    platform_prerequisite_fingerprint: object,
    platform_prerequisite_source_evidence_reference: object,
) -> None:
    with pytest.raises(
        PrivilegedEligibilityEvidenceError
    ):
        PrivilegedEligibilityEvidence.from_decision(
            eligibility_evidence_id="evidence-platform-partial",
            decision=platform_decision(),
            evaluated_at=AT,
            idempotency_key="idem-platform-partial",
            platform_prerequisite_id=
                platform_prerequisite_id,
            platform_prerequisite_revision=
                platform_prerequisite_revision,
            platform_prerequisite_fingerprint=
                platform_prerequisite_fingerprint,
            platform_prerequisite_source_evidence_reference=
                platform_prerequisite_source_evidence_reference,
        )


def test_platform_lineage_is_fingerprinted() -> None:
    first = platform_evidence(
        source_reference="source-a",
    )

    second = PrivilegedEligibilityEvidence.from_decision(
        eligibility_evidence_id="evidence-platform-001",
        decision=platform_decision(),
        evaluated_at=AT,
        idempotency_key="idem-platform-001",
        platform_prerequisite_id=PREREQUISITE_ID,
        platform_prerequisite_revision=PREREQUISITE_REVISION,
        platform_prerequisite_fingerprint=
            PREREQUISITE_FINGERPRINT,
        platform_prerequisite_source_evidence_reference=
            "source-b",
    )

    assert (
        first.eligibility_evidence_fingerprint
        != second.eligibility_evidence_fingerprint
    )


def test_new_tenant_evidence_requires_no_platform_lineage() -> None:
    value = PrivilegedEligibilityEvidence.from_decision(
        eligibility_evidence_id="evidence-tenant-001",
        decision=tenant_decision(),
        evaluated_at=AT,
        idempotency_key="idem-tenant-001",
    )

    row = value.to_persisted()

    assert row["schema"] == SCHEMA
    assert row["version"] == VERSION
    assert row["platform_prerequisite_id"] is None
    assert row["platform_prerequisite_revision"] is None
    assert row["platform_prerequisite_fingerprint"] is None
    assert (
        row[
            "platform_prerequisite_source_evidence_reference"
        ]
        is None
    )


def test_tenant_platform_lineage_is_forbidden() -> None:
    with pytest.raises(
        PrivilegedEligibilityEvidenceError,
        match="TENANT_PLATFORM_LINEAGE_FORBIDDEN",
    ):
        PrivilegedEligibilityEvidence.from_decision(
            eligibility_evidence_id="evidence-tenant-bad",
            decision=tenant_decision(),
            evaluated_at=AT,
            idempotency_key="idem-tenant-bad",
            platform_prerequisite_id=PREREQUISITE_ID,
            platform_prerequisite_revision=
                PREREQUISITE_REVISION,
            platform_prerequisite_fingerprint=
                PREREQUISITE_FINGERPRINT,
            platform_prerequisite_source_evidence_reference=
                SOURCE_REFERENCE,
        )


def test_legacy_v1_row_remains_exactly_hydratable_without_lineage() -> None:
    payload = {
        "schema": LEGACY_SCHEMA,
        "version": LEGACY_VERSION,
        "eligibility_evidence_id": "legacy-platform-001",
        "principal_id": "principal-platform",
        "privileged_role_id": "SOVEREIGN_ARCHITECT",
        "target_class": "PLATFORM_SYSTEM_ROOT",
        "tenant_id": None,
        "principal_current": True,
        "tenant_membership_current": None,
        "workforce_required": False,
        "tenant_workforce_current": None,
        "platform_prerequisite_proven": True,
        "eligible": True,
        "reason": "ELIGIBLE",
        "evaluated_at": AT.isoformat(),
        "idempotency_key": "legacy-idem-001",
    }

    row = {
        **payload,
        "eligibility_evidence_fingerprint":
            evidence_module._fingerprint(payload),
    }

    restored = PrivilegedEligibilityEvidence.from_persisted(
        row
    )

    assert restored.platform_prerequisite_id is None
    assert restored.platform_prerequisite_revision is None
    assert restored.platform_prerequisite_fingerprint is None
    assert (
        restored.platform_prerequisite_source_evidence_reference
        is None
    )

    assert restored.to_persisted() == row


def test_legacy_v1_cannot_be_silently_upgraded_by_extra_lineage() -> None:
    payload = {
        "schema": LEGACY_SCHEMA,
        "version": LEGACY_VERSION,
        "eligibility_evidence_id": "legacy-platform-002",
        "principal_id": "principal-platform",
        "privileged_role_id": "SOVEREIGN_ARCHITECT",
        "target_class": "PLATFORM_SYSTEM_ROOT",
        "tenant_id": None,
        "principal_current": True,
        "tenant_membership_current": None,
        "workforce_required": False,
        "tenant_workforce_current": None,
        "platform_prerequisite_proven": True,
        "eligible": True,
        "reason": "ELIGIBLE",
        "evaluated_at": AT.isoformat(),
        "idempotency_key": "legacy-idem-002",
    }

    row = {
        **payload,
        "platform_prerequisite_id": PREREQUISITE_ID,
        "eligibility_evidence_fingerprint":
            evidence_module._fingerprint(payload),
    }

    with pytest.raises(Exception):
        PrivilegedEligibilityEvidence.from_persisted(
            row
        )
