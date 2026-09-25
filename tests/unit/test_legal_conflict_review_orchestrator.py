"""Direct certificate for L8-8J authorized conflict-review issuance.

VERSION: v1.0.0-L8-8J-LEGAL-CONFLICT-REVIEW-ISSUANCE-CERT
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_conflict_review_orchestrator.py
AUTHORITY BOUNDARY: Transactional composition evidence only; underlying IAM,
                    screening, review-domain and registry authorities remain
                    independently owned.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceAuthorizationDeniedError,
    TenantAuthorizationDecisionEvidenceConflictError,
)
from tools.eos.legal_operations.domain.legal_conflict_review import (
    LegalConflictReviewDetermination,
    LegalConflictReviewOutcome,
)
from tools.eos.legal_operations.domain.legal_conflict_screening import (
    LegalConflictMatchKind,
    LegalConflictMatchSignal,
    LegalConflictScreeningResult,
    LegalConflictScreeningStatus,
)
from tools.eos.legal_operations.orchestration import (
    legal_conflict_review_orchestrator as orchestrator,
)
from tools.eos.legal_operations.registry.legal_conflict_review_registry import (
    LegalConflictReviewRegistryConflictError,
    LegalConflictReviewRegistryRetryRequiredError,
)
from tools.eos.legal_operations.registry.legal_conflict_screening_registry import (
    LegalConflictScreeningRegistryNotFoundError,
    LegalConflictScreeningRegistryRetryRequiredError,
)


NOW = datetime(2026, 9, 25, 20, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128
TENANT = "tenant-law"
PRINCIPAL = "principal-reviewer-1"


class Session:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class FakeAuthorizationRegistry:
    """Observable canonical-evidence registry seam for orchestration tests."""

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self.error: Exception | None = None
        self.override: dict[str, object] = {}

    def issue(self, **kwargs: object) -> Any:
        self.calls.append(dict(kwargs))
        if self.error is not None:
            raise self.error
        values: dict[str, object] = {
            "tenant_id": kwargs["tenant_id"],
            "principal_id": kwargs["principal_id"],
            "operation": kwargs["operation"],
            "permission": kwargs["permission"],
            "subject_reference": kwargs["subject_reference"],
            "subject_evidence_fingerprint": kwargs["subject_evidence_fingerprint"],
            "authorization_evidence_reference": (
                "tenant-authorization-decision:decision-1"
            ),
            "authorization_evidence_fingerprint": FP_A,
        }
        values.update(self.override)
        return SimpleNamespace(**values)


def screening_value(
    *,
    status: LegalConflictScreeningStatus = (
        LegalConflictScreeningStatus.REVIEW_REQUIRED
    ),
) -> LegalConflictScreeningResult:
    matches = (
        (
            LegalConflictMatchSignal(
                tenant_id=TENANT,
                subject_identity_fingerprint=FP_B,
                source_party_id="party-1",
                source_case_matter_id="matter-1",
                source_party_fingerprint=FP_A,
                matched_party_id="party-2",
                matched_case_matter_id="matter-2",
                matched_party_fingerprint=FP_C,
                match_kind=(
                    LegalConflictMatchKind.CROSS_MATTER_EXACT_SUBJECT_MATCH
                ),
            ),
        )
        if status is LegalConflictScreeningStatus.REVIEW_REQUIRED
        else ()
    )
    return LegalConflictScreeningResult(
        tenant_id=TENANT,
        screening_id="screening-1",
        source_party_id="party-1",
        source_case_matter_id="matter-1",
        source_party_fingerprint=FP_A,
        subject_identity_fingerprint=FP_B,
        screened_at=NOW,
        status=status,
        matches=matches,
        source_evidence_reference="screening-source:1",
        source_evidence_fingerprint=FP_C,
    )


def invoke(
    auth: FakeAuthorizationRegistry,
    *,
    outcome: LegalConflictReviewOutcome = (
        LegalConflictReviewOutcome.CONFLICT_IDENTIFIED
    ),
    session: Session | None = None,
) -> LegalConflictReviewDetermination:
    return orchestrator.issue_legal_conflict_review(
        tenant_id=TENANT,
        reviewer_principal_id=PRINCIPAL,
        screening_id="screening-1",
        review_id="review-1",
        outcome=outcome,
        review_reason_reference="review-reason:1",
        reviewed_at=NOW + timedelta(minutes=5),
        screening_collection=object(),
        review_collection=object(),
        authorization_evidence_registry=auth,  # type: ignore[arg-type]
        session=session or Session(),
    )


@pytest.fixture(autouse=True)
def accept_fake_authorization_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        orchestrator,
        "TenantAuthorizationDecisionEvidenceRegistry",
        FakeAuthorizationRegistry,
    )


def test_success_reads_screening_issues_exact_authorization_then_persists(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []
    source = screening_value()
    auth = FakeAuthorizationRegistry()

    def read_screening(*args: object, **kwargs: object) -> LegalConflictScreeningResult:
        events.append("screening")
        assert args[:2] == (TENANT, "screening-1")
        assert getattr(kwargs["session"], "in_transaction", False) is True
        return source

    def persist_review(
        review: LegalConflictReviewDetermination,
        _collection: object,
        *,
        session: Any,
    ) -> LegalConflictReviewDetermination:
        events.append("review")
        assert session.in_transaction is True
        return review

    monkeypatch.setattr(
        orchestrator.LegalConflictScreeningRegistry,
        "get_screening",
        read_screening,
    )
    monkeypatch.setattr(
        orchestrator.LegalConflictReviewRegistry,
        "persist_review",
        persist_review,
    )

    result = invoke(auth)

    assert events == ["screening", "review"]
    assert len(auth.calls) == 1
    call = auth.calls[0]
    assert call["tenant_id"] == TENANT
    assert call["principal_id"] == PRINCIPAL
    assert call["operation"] == orchestrator.OPERATION
    assert call["permission"] == orchestrator.PERMISSION
    assert call["subject_reference"] == "legal-conflict-screening:screening-1"
    assert call["subject_evidence_fingerprint"] == source.fingerprint
    assert call["idempotency_key"] == "legal-conflict-review:review-1"
    assert result.screening_fingerprint == source.fingerprint
    assert result.reviewer_principal_id == PRINCIPAL
    assert result.reviewer_authorization_fingerprint == FP_A


def test_missing_active_transaction_rejects_before_any_authority_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def read(*_args: object, **_kwargs: object) -> Any:
        nonlocal called
        called = True
        return screening_value()

    monkeypatch.setattr(
        orchestrator.LegalConflictScreeningRegistry,
        "get_screening",
        read,
    )
    auth = FakeAuthorizationRegistry()

    with pytest.raises(orchestrator.LegalConflictReviewOrchestrationError) as raised:
        invoke(auth, session=Session(False))
    assert raised.value.code == "L8_8J_ACTIVE_TRANSACTION_REQUIRED"
    assert called is False
    assert auth.calls == []


def test_missing_persisted_screening_is_bounded_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        orchestrator.LegalConflictScreeningRegistry,
        "get_screening",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            LegalConflictScreeningRegistryNotFoundError()
        ),
    )
    auth = FakeAuthorizationRegistry()
    with pytest.raises(orchestrator.LegalConflictReviewOrchestrationError) as raised:
        invoke(auth)
    assert raised.value.code == "L8_8J_SCREENING_NOT_FOUND"
    assert auth.calls == []


def test_screening_retry_signal_requires_whole_transaction_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        orchestrator.LegalConflictScreeningRegistry,
        "get_screening",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            LegalConflictScreeningRegistryRetryRequiredError()
        ),
    )
    with pytest.raises(
        orchestrator.LegalConflictReviewOrchestrationRetryRequiredError
    ) as raised:
        invoke(FakeAuthorizationRegistry())
    assert raised.value.code == "L8_8J_WHOLE_TRANSACTION_RETRY_REQUIRED"


def test_authorization_denial_prevents_review_persistence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        orchestrator.LegalConflictScreeningRegistry,
        "get_screening",
        lambda *_args, **_kwargs: screening_value(),
    )
    persisted = False

    def persist(*_args: object, **_kwargs: object) -> Any:
        nonlocal persisted
        persisted = True
        raise AssertionError("review must not persist")

    monkeypatch.setattr(
        orchestrator.LegalConflictReviewRegistry,
        "persist_review",
        persist,
    )
    auth = FakeAuthorizationRegistry()
    auth.error = TenantAuthorizationDecisionEvidenceAuthorizationDeniedError(
        "AUTHORIZATION_DENIED"
    )

    with pytest.raises(orchestrator.LegalConflictReviewOrchestrationError) as raised:
        invoke(auth)
    assert raised.value.code == "L8_8J_REVIEWER_AUTHORIZATION_REQUIRED"
    assert persisted is False


def test_authorization_evidence_conflict_requires_whole_transaction_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        orchestrator.LegalConflictScreeningRegistry,
        "get_screening",
        lambda *_args, **_kwargs: screening_value(),
    )
    auth = FakeAuthorizationRegistry()
    auth.error = TenantAuthorizationDecisionEvidenceConflictError(
        "IDEMPOTENCY_CONFLICT"
    )
    with pytest.raises(
        orchestrator.LegalConflictReviewOrchestrationRetryRequiredError
    ) as raised:
        invoke(auth)
    assert raised.value.code == "L8_8J_WHOLE_TRANSACTION_RETRY_REQUIRED"


def test_authorization_evidence_must_correlate_to_exact_screening(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        orchestrator.LegalConflictScreeningRegistry,
        "get_screening",
        lambda *_args, **_kwargs: screening_value(),
    )
    auth = FakeAuthorizationRegistry()
    auth.override = {"subject_evidence_fingerprint": FP_C}

    with pytest.raises(orchestrator.LegalConflictReviewOrchestrationError) as raised:
        invoke(auth)
    assert raised.value.code == "L8_8J_AUTHORIZATION_EVIDENCE_CORRELATION_INVALID"


def test_incompatible_human_outcome_is_rejected_before_persistence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = screening_value(
        status=LegalConflictScreeningStatus.NO_MATCH_FOUND,
    )
    monkeypatch.setattr(
        orchestrator.LegalConflictScreeningRegistry,
        "get_screening",
        lambda *_args, **_kwargs: source,
    )
    persisted = False

    def persist(*_args: object, **_kwargs: object) -> Any:
        nonlocal persisted
        persisted = True
        raise AssertionError("invalid review must not persist")

    monkeypatch.setattr(
        orchestrator.LegalConflictReviewRegistry,
        "persist_review",
        persist,
    )
    with pytest.raises(orchestrator.LegalConflictReviewOrchestrationError) as raised:
        invoke(
            FakeAuthorizationRegistry(),
            outcome=LegalConflictReviewOutcome.CONFLICT_IDENTIFIED,
        )
    assert raised.value.code == "L8_8J_REVIEW_DETERMINATION_INVALID"
    assert persisted is False


def test_review_identity_divergence_is_not_reclassified_as_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        orchestrator.LegalConflictScreeningRegistry,
        "get_screening",
        lambda *_args, **_kwargs: screening_value(),
    )
    monkeypatch.setattr(
        orchestrator.LegalConflictReviewRegistry,
        "persist_review",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            LegalConflictReviewRegistryConflictError()
        ),
    )

    with pytest.raises(orchestrator.LegalConflictReviewOrchestrationError) as raised:
        invoke(FakeAuthorizationRegistry())
    assert raised.value.code == "L8_8J_REVIEW_CONFLICT"


def test_review_registry_retry_propagates_as_whole_transaction_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        orchestrator.LegalConflictScreeningRegistry,
        "get_screening",
        lambda *_args, **_kwargs: screening_value(),
    )
    monkeypatch.setattr(
        orchestrator.LegalConflictReviewRegistry,
        "persist_review",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            LegalConflictReviewRegistryRetryRequiredError()
        ),
    )

    with pytest.raises(
        orchestrator.LegalConflictReviewOrchestrationRetryRequiredError
    ) as raised:
        invoke(FakeAuthorizationRegistry())
    assert raised.value.code == "L8_8J_WHOLE_TRANSACTION_RETRY_REQUIRED"


def test_post_write_correlation_must_match_composed_review(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        orchestrator.LegalConflictScreeningRegistry,
        "get_screening",
        lambda *_args, **_kwargs: screening_value(),
    )

    def divergent(
        review: LegalConflictReviewDetermination,
        *_args: object,
        **_kwargs: object,
    ) -> LegalConflictReviewDetermination:
        return replace(
            review,
            review_reason_reference="review-reason:different",
            fingerprint="",
        )

    monkeypatch.setattr(
        orchestrator.LegalConflictReviewRegistry,
        "persist_review",
        divergent,
    )

    with pytest.raises(orchestrator.LegalConflictReviewOrchestrationError) as raised:
        invoke(FakeAuthorizationRegistry())
    assert raised.value.code == "L8_8J_REVIEW_POST_WRITE_CORRELATION_INVALID"


# ARTIFACT: test_legal_conflict_review_orchestrator.py
# VERSION: v1.0.0-L8-8J-LEGAL-CONFLICT-REVIEW-ISSUANCE-CERT
# AUTHORITY BOUNDARY: authorized review composition evidence only
# TENANT POSTURE: exact tenant + persisted screening + reviewer principal + durable auth subject
# FAIL-CLOSED POSTURE: transaction/screening/IAM/domain/persistence divergence rejects; retry taxonomy preserved
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
