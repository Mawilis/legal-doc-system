"""Direct L9A3 certificate for authorized client-acceptance issuance.

The certificate composes pure/domain and registry seams with deterministic
fakes. No canonical Mongo, HTTP, engagement, representation, Court, billing,
payment, or financial execution authority is exercised.
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceAuthorizationDeniedError,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.orchestration import (
    legal_client_acceptance_orchestrator as orchestrator,
)


TENANT = "tenant-client"
PRINCIPAL = "principal-client"
MATTER_ID = "matter-1"
PARTY_ID = "party-1"
ACCEPTANCE_ID = "acceptance-1"
FP_A = "a" * 128
FP_B = "b" * 128
NOW = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)


class Session:
    in_transaction = True


class FakeAuthorizationRegistry:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self.error: Exception | None = None

    def issue(self, **kwargs: object) -> Any:
        self.calls.append(dict(kwargs))
        if self.error is not None:
            raise self.error
        return SimpleNamespace(
            tenant_id=kwargs["tenant_id"],
            principal_id=kwargs["principal_id"],
            operation=kwargs["operation"],
            permission=kwargs["permission"],
            subject_reference=kwargs["subject_reference"],
            subject_evidence_fingerprint=kwargs["subject_evidence_fingerprint"],
            authorization_evidence_reference="tenant-auth-evidence:1",
            authorization_evidence_fingerprint=FP_A,
            authorized_at=NOW,
        )


def identity(status: PrincipalStatus = PrincipalStatus.ACTIVE) -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id=TENANT,
        username=None,
        email=None,
        roles=[],
        permissions=[],
        auth_method="test",
        status=status,
    )


def matter() -> CaseMatter:
    return CaseMatter(
        tenant_id=TENANT,
        case_matter_id=MATTER_ID,
        matter_reference="matter-reference-1",
        opened_at=NOW,
        evidence_reference="matter-source:1",
    )


def invoke(auth: FakeAuthorizationRegistry, *, session: Any = None) -> Any:
    return orchestrator.issue_legal_client_acceptance(
        identity=identity(),
        case_matter_id=MATTER_ID,
        acceptance_id=ACCEPTANCE_ID,
        party_id=PARTY_ID,
        subject_reference="client:subject-1",
        subject_identity_fingerprint=FP_B,
        acceptance_scope="platform-use",
        source_evidence_reference="client-source:1",
        source_evidence_fingerprint=FP_A,
        lifecycle_collection=object(),
        party_collection=object(),
        acceptance_collection=object(),
        authorization_evidence_registry=auth,  # type: ignore[arg-type]
        session=session or Session(),
    )


@pytest.fixture(autouse=True)
def seams(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        orchestrator,
        "TenantAuthorizationDecisionEvidenceRegistry",
        FakeAuthorizationRegistry,
    )
    monkeypatch.setattr(
        orchestrator.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        staticmethod(lambda *_args, **_kwargs: (matter(),)),
    )
    monkeypatch.setattr(
        orchestrator.LegalMatterPartyRegistry,
        "get_party",
        staticmethod(
            lambda *_args, **_kwargs: SimpleNamespace(
                tenant_id=TENANT,
                case_matter_id=MATTER_ID,
                matter_fingerprint=matter().fingerprint,
                party_id=PARTY_ID,
                subject_reference="client:subject-1",
                subject_identity_fingerprint=FP_B,
            )
        ),
    )
    monkeypatch.setattr(
        orchestrator.LegalClientAcceptanceRegistry,
        "persist_acceptance",
        staticmethod(lambda value, _collection, *, session: value),
    )


def test_success_binds_identity_sources_authorization_and_session() -> None:
    auth = FakeAuthorizationRegistry()
    result = invoke(auth)
    assert result.tenant_id == TENANT
    assert result.actor_principal_id == PRINCIPAL
    assert result.case_matter_id == MATTER_ID
    assert result.acceptance_id == ACCEPTANCE_ID
    assert result.accepted_at == NOW
    assert len(auth.calls) == 1
    call = auth.calls[0]
    assert call["tenant_id"] == TENANT
    assert call["principal_id"] == PRINCIPAL
    assert call["operation"] == orchestrator.OPERATION
    assert call["permission"] == orchestrator.PERMISSION
    assert call["subject_reference"] == "legal-client-acceptance:acceptance-1"
    assert call["idempotency_key"] == "legal-client-acceptance:acceptance-1"
    assert getattr(call["session"], "in_transaction", False) is True


def test_inactive_identity_rejects_before_source_reads() -> None:
    with pytest.raises(orchestrator.LegalClientAcceptanceOrchestrationError) as error:
        orchestrator.issue_legal_client_acceptance(
            identity=identity(PrincipalStatus.SUSPENDED),
            case_matter_id=MATTER_ID,
            acceptance_id=ACCEPTANCE_ID,
            party_id=PARTY_ID,
            subject_reference="client:subject-1",
            subject_identity_fingerprint=FP_B,
            acceptance_scope="platform-use",
            source_evidence_reference="client-source:1",
            source_evidence_fingerprint=FP_A,
            lifecycle_collection=object(),
            party_collection=object(),
            acceptance_collection=object(),
            authorization_evidence_registry=FakeAuthorizationRegistry(),  # type: ignore[arg-type]
            session=Session(),
        )
    assert error.value.code == "L9A3_PRINCIPAL_INACTIVE"


def test_party_scope_mismatch_rejects_before_authorization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        orchestrator.LegalMatterPartyRegistry,
        "get_party",
        staticmethod(
            lambda *_args, **_kwargs: SimpleNamespace(
                tenant_id=TENANT,
                case_matter_id="other-matter",
                matter_fingerprint=FP_A,
                party_id=PARTY_ID,
                subject_reference="client:subject-1",
                subject_identity_fingerprint=FP_B,
            )
        ),
    )
    auth = FakeAuthorizationRegistry()
    with pytest.raises(orchestrator.LegalClientAcceptanceOrchestrationError) as error:
        invoke(auth)
    assert error.value.code == "L9A3_PARTY_SCOPE_MISMATCH"
    assert auth.calls == []


def test_authorization_denial_is_fail_closed() -> None:
    auth = FakeAuthorizationRegistry()
    auth.error = TenantAuthorizationDecisionEvidenceAuthorizationDeniedError(
        "AUTHORIZATION_DENIED"
    )
    with pytest.raises(orchestrator.LegalClientAcceptanceOrchestrationError) as error:
        invoke(auth)
    assert error.value.code == "L9A3_CLIENT_AUTHORIZATION_REQUIRED"


def test_missing_transaction_rejects_before_any_read() -> None:
    with pytest.raises(orchestrator.LegalClientAcceptanceOrchestrationError) as error:
        invoke(FakeAuthorizationRegistry(), session=SimpleNamespace(in_transaction=False))
    assert error.value.code == "L9A3_ACTIVE_TRANSACTION_REQUIRED"


# ARTIFACT: test_legal_client_acceptance_orchestrator.py
# VERSION: v1.0.0-L9A3-LEGAL-CLIENT-ACCEPTANCE-ISSUANCE-CERT
# AUTHORITY BOUNDARY: direct composition certificate only
# TENANT POSTURE: exact identity, matter and party correlation are asserted
# FAIL-CLOSED POSTURE: inactive, divergent, denied and missing-transaction paths reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
