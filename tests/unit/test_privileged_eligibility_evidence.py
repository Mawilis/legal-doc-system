"""
Direct certificate for immutable privileged-eligibility evidence.

VERSION:
v1.0.0-P2-R2-A1-PRIVILEGED-ELIGIBILITY-EVIDENCE-CERT
"""

from dataclasses import (
    FrozenInstanceError,
)
from datetime import (
    datetime,
    timezone,
)
import inspect

import pytest

from tools.eos.auth.privileged_eligibility import (
    ENTERPRISE_ADMIN,
    SOVEREIGN_ARCHITECT,
    PrivilegedEligibilityReason,
    evaluate_privileged_eligibility,
)
from tools.eos.auth.privileged_eligibility_evidence import (
    PrivilegedEligibilityEvidence,
    PrivilegedEligibilityEvidenceError,
    PrivilegedEligibilityEvidencePersistedRecordInvalidError,
)


NOW = datetime(
    2026,
    10,
    14,
    1,
    0,
    tzinfo=timezone.utc,
)


def tenant_decision(
    *,
    eligible: bool = True,
):
    if eligible:
        return evaluate_privileged_eligibility(
            principal_id="principal-a",
            privileged_role_id=
                ENTERPRISE_ADMIN,
            principal_current=True,
            tenant_id="tenant-a",
            tenant_membership_current=True,
            workforce_required=True,
            tenant_workforce_current=True,
        )

    return evaluate_privileged_eligibility(
        principal_id="principal-a",
        privileged_role_id=
            ENTERPRISE_ADMIN,
        principal_current=False,
        tenant_id="tenant-a",
        tenant_membership_current=True,
        workforce_required=True,
        tenant_workforce_current=True,
    )


def evidence(
    *,
    decision=None,
    evidence_id: str = "eligibility-001",
    idempotency_key: str = "idem-001",
):
    return PrivilegedEligibilityEvidence.from_decision(
        eligibility_evidence_id=
            evidence_id,
        decision=(
            tenant_decision()
            if decision is None
            else decision
        ),
        evaluated_at=NOW,
        idempotency_key=
            idempotency_key,
    )


def test_eligible_tenant_snapshot_is_exact_and_fingerprinted() -> None:
    value = evidence()

    assert (
        value.eligibility_evidence_id,
        value.principal_id,
        value.privileged_role_id,
        value.tenant_id,
        value.eligible,
        value.reason,
    ) == (
        "eligibility-001",
        "principal-a",
        ENTERPRISE_ADMIN,
        "tenant-a",
        True,
        PrivilegedEligibilityReason
        .ELIGIBLE,
    )

    assert (
        len(
            value.eligibility_evidence_fingerprint
        )
        == 128
    )

    int(
        value.eligibility_evidence_fingerprint,
        16,
    )


def test_ineligible_decision_is_lawful_durable_evidence() -> None:
    value = evidence(
        decision=tenant_decision(
            eligible=False,
        )
    )

    assert value.eligible is False

    assert (
        value.reason
        is PrivilegedEligibilityReason
        .PRINCIPAL_NOT_CURRENT
    )


def test_platform_snapshot_retains_exact_root_scope_without_tenant() -> None:
    decision = evaluate_privileged_eligibility(
        principal_id="principal-root",
        privileged_role_id=
            SOVEREIGN_ARCHITECT,
        principal_current=True,
        platform_prerequisite_proven=True,
    )

    value = PrivilegedEligibilityEvidence.from_decision(
        eligibility_evidence_id=
            "eligibility-root",
        decision=decision,
        evaluated_at=NOW,
        idempotency_key=
            "idem-root",
        platform_prerequisite_id=
            "platform-prerequisite-root",
        platform_prerequisite_revision=
            1,
        platform_prerequisite_fingerprint=
            "a" * 128,
        platform_prerequisite_source_evidence_reference=
            "core-governance-root",
    )

    assert value.tenant_id is None

    assert (
        value.privileged_role_id
        == SOVEREIGN_ARCHITECT
    )


def test_evidence_is_immutable() -> None:
    value = evidence()

    with pytest.raises(
        FrozenInstanceError
    ):
        value.eligible = False  # type: ignore[misc]


def test_exact_persisted_round_trip() -> None:
    value = evidence()

    row = value.to_persisted()

    restored = (
        PrivilegedEligibilityEvidence
        .from_persisted(
            row
        )
    )

    assert restored == value
    assert (
        restored.to_persisted()
        == row
    )


@pytest.mark.parametrize(
    "field",
    (
        "principal_current",
        "tenant_membership_current",
        "workforce_required",
        "tenant_workforce_current",
        "eligible",
        "reason",
        "evaluated_at",
        "idempotency_key",
    ),
)
def test_material_changes_change_fingerprint(
    field: str,
) -> None:
    original = evidence()

    row = original.to_persisted()

    if field == "principal_current":
        row[field] = False
    elif field == "tenant_membership_current":
        row[field] = False
    elif field == "workforce_required":
        row[field] = False
    elif field == "tenant_workforce_current":
        row[field] = False
    elif field == "eligible":
        row[field] = False
    elif field == "reason":
        row[field] = (
            "PRINCIPAL_NOT_CURRENT"
        )
    elif field == "evaluated_at":
        row[field] = (
            "2026-10-14T02:00:00+00:00"
        )
    else:
        row[field] = "idem-other"

    with pytest.raises(
        PrivilegedEligibilityEvidencePersistedRecordInvalidError
    ):
        PrivilegedEligibilityEvidence.from_persisted(
            row
        )


@pytest.mark.parametrize(
    "mutation",
    (
        "unknown",
        "missing",
        "schema",
        "version",
        "fingerprint",
        "target_class",
        "tenant_scope",
    ),
)
def test_persisted_corruption_fails_closed(
    mutation: str,
) -> None:
    row = evidence().to_persisted()

    if mutation == "unknown":
        row["unknown"] = "forbidden"

    elif mutation == "missing":
        row.pop(
            "principal_current"
        )

    elif mutation == "schema":
        row["schema"] = "OTHER/V1"

    elif mutation == "version":
        row["version"] = "other"

    elif mutation == "fingerprint":
        row[
            "eligibility_evidence_fingerprint"
        ] = "f" * 128

    elif mutation == "target_class":
        row[
            "target_class"
        ] = "UNKNOWN"

    else:
        row[
            "tenant_id"
        ] = None

    with pytest.raises(
        PrivilegedEligibilityEvidencePersistedRecordInvalidError
    ):
        PrivilegedEligibilityEvidence.from_persisted(
            row
        )


def test_decision_without_privileged_target_class_rejects() -> None:
    decision = evaluate_privileged_eligibility(
        principal_id="principal-a",
        privileged_role_id="AUDITOR",
        principal_current=True,
        tenant_id="tenant-a",
        tenant_membership_current=True,
    )

    with pytest.raises(
        PrivilegedEligibilityEvidenceError
    ):
        PrivilegedEligibilityEvidence.from_decision(
            eligibility_evidence_id=
                "eligibility-x",
            decision=decision,
            evaluated_at=NOW,
            idempotency_key=
                "idem-x",
        )


def test_naive_time_rejects() -> None:
    with pytest.raises(
        PrivilegedEligibilityEvidenceError
    ):
        PrivilegedEligibilityEvidence.from_decision(
            eligibility_evidence_id=
                "eligibility-x",
            decision=tenant_decision(),
            evaluated_at=NOW.replace(
                tzinfo=None
            ),
            idempotency_key=
                "idem-x",
        )


def test_no_sequence_chain_or_expiry_surface() -> None:
    names = set(
        PrivilegedEligibilityEvidence
        .__dataclass_fields__
    )

    forbidden = {
        "revision",
        "sequence_number",
        "previous_fingerprint",
        "supersedes_fingerprint",
        "expires_at",
        "valid_until",
        "ttl",
    }

    assert not names.intersection(
        forbidden
    )


def test_no_provenance_authority_is_invented() -> None:
    names = set(
        PrivilegedEligibilityEvidence
        .__dataclass_fields__
    )

    assert not names.intersection(
        {
            "source_reference",
            "source_fingerprint",
            "authorization_evidence",
            "security_assurance",
            "mfa_registered",
        }
    )


def test_evidence_has_no_role_activation_session_or_finance_api() -> None:
    import tools.eos.auth.privileged_eligibility_evidence as module

    source = inspect.getsource(
        module
    ).casefold()

    for forbidden in (
        "role_assignment_repository",
        "tenant_membership_repository",
        "activate_privilege",
        "privileged_activation_registry",
        "refresh_token",
        "create_session",
        "break_glass_registry",
        "financial_execution_repository",
        "pymongo",
        "fastapi",
    ):
        assert forbidden not in source


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_privileged_eligibility_evidence.py
# VERSION: v1.0.0-P2-R2-A1-PRIVILEGED-ELIGIBILITY-EVIDENCE-CERT
# EVIDENCE: immutable eligible/ineligible decision snapshots
# CURRENTNESS: no historic snapshot creates current authority
# CHAIN: no sequence/revision chain
# TTL: none
# AUTHORITY: none beyond audit evidence
# FINANCIAL EXECUTION AUTHORITY: None
# END OF WILSY OS SOVEREIGN ARTIFACT
