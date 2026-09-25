"""Direct certificate for L8-8K authenticated conflict-review command API.

VERSION: v1.0.0-L8-8K-CONFLICT-REVIEW-COMMAND-API-CERT
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_conflict_review_command_router.py
AUTHORITY BOUNDARY: HTTP/transaction wiring only; L8-8D/E/G/H/I/J remain
                    canonical conflict-screening/review authorities.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from pydantic import ValidationError

import tools.eos.api.legal_operations_command_router as command_api
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.domain.legal_conflict_review import (
    LegalConflictReviewOutcome,
)
from tools.eos.legal_operations.orchestration.legal_conflict_review_orchestrator import (
    LegalConflictReviewOrchestrationError,
    LegalConflictReviewOrchestrationRetryRequiredError,
)


TENANT = "tenant-law"
PRINCIPAL = "principal-reviewer"
NOW = datetime(2026, 9, 25, 22, 0, tzinfo=timezone.utc)
FP = "a" * 128


class Database:
    def __init__(self) -> None:
        self.requested: list[str] = []

    def get_collection(self, name: str) -> Any:
        self.requested.append(name)
        return SimpleNamespace(name=name)


class FakeEvidenceRegistry:
    created: list["FakeEvidenceRegistry"] = []

    def __init__(
        self,
        collection: Any,
        *,
        principal_repository: Any,
        membership_repository: Any,
        role_assignment_repository: Any,
        business_role_repository: Any,
    ) -> None:
        self.collection = collection
        self.principal_repository = principal_repository
        self.membership_repository = membership_repository
        self.role_assignment_repository = role_assignment_repository
        self.business_role_repository = business_role_repository
        type(self).created.append(self)


def context() -> TenantAuthorizationContext:
    identity = SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id=TENANT,
        username="reviewer",
        email="reviewer@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )
    decision = TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        "tenant_legal_partner",
        "LEGAL_PARTNER",
    )
    return TenantAuthorizationContext(identity, TENANT, decision)


def command(**overrides: object) -> command_api.ConflictReviewCommand:
    values: dict[str, object] = {
        "screening_id": "screening-1",
        "review_id": "review-1",
        "outcome": LegalConflictReviewOutcome.CONFLICT_IDENTIFIED,
        "review_reason_reference": "reason:conflict-observed",
    }
    values.update(overrides)
    return command_api.ConflictReviewCommand(**values)


def review_value() -> Any:
    return SimpleNamespace(
        review_id="review-1",
        screening_id="screening-1",
        outcome=LegalConflictReviewOutcome.CONFLICT_IDENTIFIED,
        reviewed_at=NOW,
        fingerprint=FP,
    )


@pytest.fixture(autouse=True)
def reset_fake_registry() -> None:
    FakeEvidenceRegistry.created.clear()


def test_command_body_accepts_only_human_review_choice_fields() -> None:
    value = command()
    assert set(value.model_dump()) == {
        "screening_id",
        "review_id",
        "outcome",
        "review_reason_reference",
    }

    forbidden = {
        "tenant_id": TENANT,
        "reviewer_principal_id": PRINCIPAL,
        "reviewed_at": NOW,
        "screening_fingerprint": FP,
        "reviewer_authorization_reference": "forged",
        "reviewer_authorization_fingerprint": FP,
        "source_evidence_reference": "forged",
        "source_evidence_fingerprint": FP,
        "waiver": True,
        "client_accepted": True,
    }
    for field, value_for_field in forbidden.items():
        with pytest.raises(ValidationError):
            command(**{field: value_for_field})


def test_route_dependency_is_exact_conflict_review_permission_operation() -> None:
    dependency = command_api._CONFLICT_REVIEW
    assert dependency.permission_id == "legal_operations:conflict_review:write"
    assert dependency.operation == "legal_conflict_review_write"


def test_route_derives_server_scope_time_and_durable_authorization_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = Database()
    session = SimpleNamespace(in_transaction=True)
    principal_repository = object()
    membership_repository = object()
    role_assignment_repository = object()
    captured: dict[str, Any] = {}

    def transaction(callback: Any) -> Any:
        return callback(session, database)

    def issue(**kwargs: Any) -> Any:
        captured.update(kwargs)
        return review_value()

    monkeypatch.setattr(command_api, "_transaction", transaction)
    monkeypatch.setattr(command_api, "_utcnow", lambda: NOW)
    monkeypatch.setattr(
        command_api,
        "TenantAuthorizationDecisionEvidenceRegistry",
        FakeEvidenceRegistry,
    )
    monkeypatch.setattr(command_api, "issue_legal_conflict_review", issue)

    result = asyncio.run(
        command_api.record_legal_conflict_review_command(
            command(),
            context(),
            principal_repository,
            membership_repository,
            role_assignment_repository,
        )
    )

    assert captured["tenant_id"] == TENANT
    assert captured["reviewer_principal_id"] == PRINCIPAL
    assert captured["screening_id"] == "screening-1"
    assert captured["review_id"] == "review-1"
    assert captured["reviewed_at"] == NOW
    assert captured["session"] is session
    assert captured["outcome"] is LegalConflictReviewOutcome.CONFLICT_IDENTIFIED
    assert captured["review_reason_reference"] == "reason:conflict-observed"
    assert captured["screening_collection"].name == (
        command_api.LEGAL_CONFLICT_SCREENING_COLLECTION
    )
    assert captured["review_collection"].name == (
        command_api.LEGAL_CONFLICT_REVIEW_COLLECTION
    )

    assert len(FakeEvidenceRegistry.created) == 1
    evidence = FakeEvidenceRegistry.created[0]
    assert evidence.collection.name == (
        command_api.TENANT_AUTHORIZATION_EVIDENCE_COLLECTION
    )
    assert evidence.principal_repository is principal_repository
    assert evidence.membership_repository is membership_repository
    assert evidence.role_assignment_repository is role_assignment_repository
    assert evidence.business_role_repository is role_assignment_repository

    assert set(database.requested) == {
        command_api.TENANT_AUTHORIZATION_EVIDENCE_COLLECTION,
        command_api.LEGAL_CONFLICT_SCREENING_COLLECTION,
        command_api.LEGAL_CONFLICT_REVIEW_COLLECTION,
    }
    assert result == {
        "data": {
            "review_id": "review-1",
            "screening_id": "screening-1",
            "outcome": "CONFLICT_IDENTIFIED",
            "reviewed_at": NOW.isoformat(),
            "fingerprint": FP,
        }
    }


def test_response_never_exposes_authorization_or_party_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        command_api,
        "_transaction",
        lambda callback: callback(SimpleNamespace(in_transaction=True), Database()),
    )
    monkeypatch.setattr(command_api, "_utcnow", lambda: NOW)
    monkeypatch.setattr(
        command_api,
        "TenantAuthorizationDecisionEvidenceRegistry",
        FakeEvidenceRegistry,
    )
    monkeypatch.setattr(
        command_api,
        "issue_legal_conflict_review",
        lambda **_kwargs: review_value(),
    )

    result = asyncio.run(
        command_api.record_legal_conflict_review_command(
            command(),
            context(),
            object(),
            object(),
            object(),
        )
    )
    serialized = str(result)
    for forbidden in (
        "authorization",
        "principal",
        "party",
        "subject_identity",
        "source_evidence",
    ):
        assert forbidden not in serialized.lower()


@pytest.mark.parametrize(
    ("error", "status_code", "detail"),
    [
        (
            LegalConflictReviewOrchestrationRetryRequiredError(
                "L8_8J_WHOLE_TRANSACTION_RETRY_REQUIRED"
            ),
            409,
            "LEGAL_OPERATIONS_RETRY_REQUIRED",
        ),
        (
            LegalConflictReviewOrchestrationError(
                "L8_8J_REVIEWER_AUTHORIZATION_REQUIRED"
            ),
            403,
            "LEGAL_CONFLICT_REVIEW_AUTHORIZATION_REQUIRED",
        ),
        (
            LegalConflictReviewOrchestrationError(
                "L8_8J_SCREENING_NOT_FOUND"
            ),
            404,
            "LEGAL_OPERATION_NOT_FOUND",
        ),
        (
            LegalConflictReviewOrchestrationError(
                "L8_8J_REVIEW_CONFLICT"
            ),
            409,
            "LEGAL_CONFLICT_REVIEW_CONFLICT",
        ),
        (
            LegalConflictReviewOrchestrationError(
                "L8_8J_SCREENING_AUTHORITY_UNAVAILABLE"
            ),
            503,
            "LEGAL_OPERATIONS_UNAVAILABLE",
        ),
        (
            LegalConflictReviewOrchestrationError(
                "L8_8J_AUTHORIZATION_EVIDENCE_UNAVAILABLE"
            ),
            503,
            "LEGAL_OPERATIONS_UNAVAILABLE",
        ),
        (
            LegalConflictReviewOrchestrationError(
                "L8_8J_REVIEW_DETERMINATION_INVALID"
            ),
            422,
            "LEGAL_OPERATIONS_COMMAND_INVALID",
        ),
    ],
)
def test_conflict_review_error_taxonomy_is_bounded(
    error: BaseException,
    status_code: int,
    detail: str,
) -> None:
    projected = command_api._http_error(error)
    assert projected.status_code == status_code
    assert projected.detail == detail


def test_route_aborts_and_projects_orchestration_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Session:
        def __init__(self) -> None:
            self.in_transaction = False
            self.events: list[str] = []

        def start_transaction(self) -> None:
            self.in_transaction = True
            self.events.append("start")

        def commit_transaction(self) -> None:
            self.in_transaction = False
            self.events.append("commit")

        def abort_transaction(self) -> None:
            self.in_transaction = False
            self.events.append("abort")

        def __enter__(self) -> "Session":
            return self

        def __exit__(self, *_args: object) -> None:
            self.events.append("end")

    session = Session()
    client = SimpleNamespace(start_session=lambda: session)
    database = Database()
    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (client, database),
    )
    monkeypatch.setattr(
        command_api,
        "TenantAuthorizationDecisionEvidenceRegistry",
        FakeEvidenceRegistry,
    )
    monkeypatch.setattr(
        command_api,
        "issue_legal_conflict_review",
        lambda **_kwargs: (_ for _ in ()).throw(
            LegalConflictReviewOrchestrationError(
                "L8_8J_REVIEWER_AUTHORIZATION_REQUIRED"
            )
        ),
    )

    with pytest.raises(Exception) as raised:
        asyncio.run(
            command_api.record_legal_conflict_review_command(
                command(),
                context(),
                object(),
                object(),
                object(),
            )
        )

    assert getattr(raised.value, "status_code", None) == 403
    assert getattr(raised.value, "detail", None) == (
        "LEGAL_CONFLICT_REVIEW_AUTHORIZATION_REQUIRED"
    )
    assert session.events == ["start", "abort", "end"]


# ARTIFACT: test_legal_conflict_review_command_router.py
# VERSION: v1.0.0-L8-8K-CONFLICT-REVIEW-COMMAND-API-CERT
# AUTHORITY BOUNDARY: authenticated transport/transaction certificate only
# TENANT POSTURE: tenant/reviewer/time/IAM evidence are server-owned
# FAIL-CLOSED POSTURE: extra authority fields, retry, denial, absence, conflict and outage map boundedly
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
