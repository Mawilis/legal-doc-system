"""TITLE: G79 Practitioner Disclosure Coordinator Adversarial Certificate.
VERSION: v1.0.0-G79-TRANSACTION-BOUND-DENIAL-CERT
AUTHORITY: Fail-closed coordinator tests; no positive disclosure certification.
"""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.service import legal_practitioner_disclosure_coordinator as coordinator
from tools.eos.legal_operations.service.legal_work_ethical_wall_enforcement import (
    EthicalWallEnforcementDenied,
)


class Session:
    in_transaction = True


class Reader:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def read_content(self, **kwargs: object) -> bytes:
        self.calls.append(kwargs)
        return b"confidential legal content"


def context(*, tenant_id: str = "tenant-a", principal_id: str = "principal-a") -> TenantAuthorizationContext:
    return TenantAuthorizationContext(
        identity=SimpleNamespace(identity_id=principal_id, tenant_id=tenant_id),  # type: ignore[arg-type]
        tenant_id=tenant_id,
        decision=TenantAuthorizationDecision(
            authorized=True,
            reason=TenantAuthorizationReason.AUTHORIZED,
        ),
    )


def request(reader: Reader, *, ctx: object | None = None, session: object | None = None) -> dict[str, object]:
    return {
        "authorization_context": context() if ctx is None else ctx,
        "case_matter_id": "matter-a",
        "content_reference": "content-a",
        "policy_id": "policy-a",
        "evaluation_time": datetime(2026, 10, 26, tzinfo=timezone.utc),
        "iam_source": object(),
        "binding_source": object(),
        "assignment_source": object(),
        "conflict_source": object(),
        "review_source": object(),
        "wall_source": object(),
        "content_reader": reader,
        "session": Session() if session is None else session,
    }


def test_missing_authenticated_context_denies_before_reader() -> None:
    reader = Reader()
    with pytest.raises(coordinator.PractitionerDisclosureDenied, match="AUTHENTICATED_CONTEXT_REQUIRED"):
        coordinator.read_practitioner_document_content(**request(reader, ctx=object()))
    assert reader.calls == []


def test_inactive_transaction_denies_before_source_reads_or_content() -> None:
    reader = Reader()
    with pytest.raises(coordinator.PractitionerDisclosureDenied, match="ACTIVE_TRANSACTION_REQUIRED"):
        coordinator.read_practitioner_document_content(**request(reader, session=SimpleNamespace(in_transaction=False)))
    assert reader.calls == []


def test_authenticated_identity_tenant_mismatch_denies_before_content() -> None:
    reader = Reader()
    with pytest.raises(coordinator.PractitionerDisclosureDenied, match="AUTHENTICATED_TENANT_MISMATCH"):
        coordinator.read_practitioner_document_content(**request(reader, ctx=context(tenant_id="tenant-b")))
    assert reader.calls == []


def test_canonical_source_denial_prevents_content_read(monkeypatch: pytest.MonkeyPatch) -> None:
    reader = Reader()

    def deny(**kwargs: object) -> None:
        raise EthicalWallEnforcementDenied("G77_INSTITUTIONAL_AUTHORITY_UNRATIFIED")

    monkeypatch.setattr(coordinator, "require_source_verified_ethical_wall_access", deny)
    with pytest.raises(coordinator.PractitionerDisclosureDenied, match="SOURCE_CHAIN_DENIED"):
        coordinator.read_practitioner_document_content(**request(reader))
    assert reader.calls == []


def test_institutional_readiness_is_independent_backstop(monkeypatch: pytest.MonkeyPatch) -> None:
    reader = Reader()
    monkeypatch.setattr(coordinator, "require_source_verified_ethical_wall_access", lambda **kwargs: None)
    with pytest.raises(coordinator.PractitionerDisclosureDenied, match="INSTITUTIONAL_AUTHORITY_UNRATIFIED"):
        coordinator.read_practitioner_document_content(**request(reader))
    assert reader.calls == []


def test_content_admission_denial_prevents_reader_even_if_readiness_claims_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    reader = Reader()
    monkeypatch.setattr(coordinator, "require_source_verified_ethical_wall_access", lambda **kwargs: None)
    monkeypatch.setattr(
        coordinator,
        "evaluate_policy_readiness",
        lambda: SimpleNamespace(
            permits_operational_access=True,
            permits_reviewer_authorization=True,
            permits_wall_enforcement_claim=True,
        ),
    )

    def deny(**kwargs: object) -> None:
        raise coordinator.PractitionerDisclosureDenied("simulated G72 denial")

    monkeypatch.setattr(coordinator, "require_practitioner_content_admission", deny)
    with pytest.raises(coordinator.PractitionerDisclosureDenied, match="CONTENT_ADMISSION_UNAVAILABLE"):
        coordinator.read_practitioner_document_content(**request(reader))
    assert reader.calls == []


def test_coordinator_does_not_release_content_from_caller_supplied_approval_flags() -> None:
    reader = Reader()
    with pytest.raises(coordinator.PractitionerDisclosureDenied):
        coordinator.read_practitioner_document_content(**request(reader))
    assert reader.calls == []
