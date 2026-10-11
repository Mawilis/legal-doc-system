"""Direct certificate for D6 deadline intelligence projection.

TITLE: Wilsy OS Legal Matter Deadline Intelligence Projection Certificate
VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D6-DEADLINE-INTELLIGENCE-CERT
AUTHORITY: Pure projection certificate only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_matter_deadline_intelligence.py
CERTIFICATION / UPDATE DATE: 2026-10-11
TENANT BOUNDARY: Mixed tenant/matter input rejects.
AUTHORITY BOUNDARY: Read-only explicit-time observation only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.intelligence.domain.legal_matter_deadline_intelligence import (
    LegalMatterDeadlineIntelligenceError,
    LegalMatterDeadlineIntelligenceProjection,
    VERSION,
    project_legal_matter_deadline_intelligence,
)
from tools.eos.legal_operations.domain.legal_matter_deadline import (
    LegalMatterDeadline,
    LegalMatterDeadlineKind,
    LegalMatterDeadlineSourceType,
    LegalMatterDeadlineStatus,
)

TENANT = "tenant-d6"
MATTER = "matter-d6"
OBSERVED = datetime(2026, 10, 11, 13, 30, tzinfo=timezone.utc)


def _deadline(
    deadline_id: str,
    due_at: datetime,
    *,
    tenant_id: str = TENANT,
    matter_id: str = MATTER,
    status: LegalMatterDeadlineStatus = LegalMatterDeadlineStatus.ACTIVE,
) -> LegalMatterDeadline:
    return LegalMatterDeadline(
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        deadline_id=deadline_id,
        deadline_kind=LegalMatterDeadlineKind.FILING,
        title="Private title",
        due_at=due_at,
        source_type=LegalMatterDeadlineSourceType.COURT_ORDER,
        source_reference="evidence://private/source",
        source_evidence_fingerprint="e" * 128,
        jurisdiction_reference="jurisdiction://court/example",
        created_at=OBSERVED - timedelta(days=1),
        status=status,
    )


def test_temporal_counts_order_and_bounded_projection() -> None:
    values = (
        _deadline("upcoming", OBSERVED + timedelta(hours=1)),
        _deadline("due", OBSERVED),
        _deadline("overdue", OBSERVED - timedelta(hours=1)),
        _deadline(
            "inactive",
            OBSERVED - timedelta(days=2),
            status=LegalMatterDeadlineStatus.SATISFIED,
        ),
    )
    result = project_legal_matter_deadline_intelligence(
        values,
        tenant_id=TENANT,
        case_matter_id=MATTER,
        observed_at=OBSERVED,
    )
    assert result.version == VERSION
    assert (
        result.active_count,
        result.upcoming_count,
        result.due_count,
        result.overdue_count,
        result.inactive_count,
    ) == (3, 1, 1, 1, 1)
    assert [item.deadline_id for item in result.items] == [
        "inactive",
        "overdue",
        "due",
        "upcoming",
    ]
    payload = result.to_dict()
    rendered = str(payload)
    assert "source_reference" not in rendered
    assert "source_evidence_fingerprint" not in rendered
    assert "Private title" not in rendered


def test_scope_duplicate_and_naive_time_reject() -> None:
    source = _deadline("same", OBSERVED)
    with pytest.raises(
        LegalMatterDeadlineIntelligenceError, match="D6_DUPLICATE_DEADLINE"
    ):
        project_legal_matter_deadline_intelligence(
            (source, source),
            tenant_id=TENANT,
            case_matter_id=MATTER,
            observed_at=OBSERVED,
        )
    with pytest.raises(
        LegalMatterDeadlineIntelligenceError, match="D6_SCOPE_MISMATCH"
    ):
        project_legal_matter_deadline_intelligence(
            (_deadline("foreign", OBSERVED, tenant_id="tenant-other"),),
            tenant_id=TENANT,
            case_matter_id=MATTER,
            observed_at=OBSERVED,
        )
    with pytest.raises(
        LegalMatterDeadlineIntelligenceError,
        match="D6_OBSERVATION_TIME_INVALID",
    ):
        project_legal_matter_deadline_intelligence(
            (source,),
            tenant_id=TENANT,
            case_matter_id=MATTER,
            observed_at=datetime(2026, 10, 11, 13, 30),
        )


def test_fingerprint_is_deterministic_and_tamper_detecting() -> None:
    source = _deadline("fp", OBSERVED + timedelta(days=1))
    first = project_legal_matter_deadline_intelligence(
        (source,), tenant_id=TENANT, case_matter_id=MATTER, observed_at=OBSERVED
    )
    second = project_legal_matter_deadline_intelligence(
        (source,), tenant_id=TENANT, case_matter_id=MATTER, observed_at=OBSERVED
    )
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 128
    with pytest.raises(
        LegalMatterDeadlineIntelligenceError, match="D6_FINGERPRINT_MISMATCH"
    ):
        LegalMatterDeadlineIntelligenceProjection(
            tenant_id=TENANT,
            case_matter_id=MATTER,
            observed_at=OBSERVED,
            items=first.items,
            active_count=first.active_count,
            upcoming_count=first.upcoming_count,
            due_count=first.due_count,
            overdue_count=first.overdue_count,
            inactive_count=first.inactive_count,
            fingerprint="f" * 128,
        )


def test_empty_projection_is_valid_and_source_has_no_mutation_seam() -> None:
    result = project_legal_matter_deadline_intelligence(
        (), tenant_id=TENANT, case_matter_id=MATTER, observed_at=OBSERVED
    )
    assert result.items == ()
    assert result.active_count == result.inactive_count == 0

    import tools.eos.intelligence.domain.legal_matter_deadline_intelligence as module

    source = open(module.__file__, encoding="utf-8").read().lower()
    for forbidden in ("insert_one(", "update_one(", "delete_one(", "payment_state"):
        assert forbidden not in source


# ARTIFACT: test_legal_matter_deadline_intelligence.py
# VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D6-DEADLINE-INTELLIGENCE-CERT
# AUTHORITY BOUNDARY: deterministic explicit-time observation certificate only
# TENANT POSTURE: mixed tenant/matter input rejects
# FAIL-CLOSED POSTURE: invalid time, duplicate, wrong scope and tamper reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
