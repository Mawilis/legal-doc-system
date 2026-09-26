"""Direct P2B3 certificate for authorized matter-instrument approvals."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import inspect
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth import permission_namespace, roles, tenant_authority_policy, tenant_authorization
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument import (
    record_legal_client_matter_acceptance_instrument,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_lifecycle import (
    LegalClientMatterAcceptanceInstrumentLifecycleStatus,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.orchestration import (
    legal_client_matter_acceptance_instrument_approval_orchestrator as orchestrator,
)


TENANT = "tenant-firm"
PRINCIPAL = "principal-partner"
MATTER_ID = "matter-1"
INSTRUMENT_ID = "instrument-1"
VERSION = "1.0.0"
APPROVAL_ID = "approval-1"
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
        if self.error:
            raise self.error
        return SimpleNamespace(
            tenant_id=kwargs["tenant_id"], principal_id=kwargs["principal_id"],
            operation=kwargs["operation"], permission=kwargs["permission"],
            subject_reference=kwargs["subject_reference"],
            subject_evidence_fingerprint=kwargs["subject_evidence_fingerprint"],
            authorization_evidence_reference="auth-evidence:1",
            authorization_evidence_fingerprint=FP_A,
            authorized_at=NOW,
        )


def _identity(status: PrincipalStatus = PrincipalStatus.ACTIVE) -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=PRINCIPAL, tenant_id=TENANT, username=None, email=None,
        roles=[], permissions=[], auth_method="synthetic", status=status,
    )


def _matter() -> CaseMatter:
    return CaseMatter(
        tenant_id=TENANT, case_matter_id=MATTER_ID,
        matter_reference="matter-reference", opened_at=NOW,
        evidence_reference="matter-evidence",
    )


def _instrument() -> Any:
    return record_legal_client_matter_acceptance_instrument(
        case_matter=_matter(), instrument_id=INSTRUMENT_ID, version=VERSION,
        instrument_kind="MATTER_REVIEW", title="Matter review",
        review_scope="Bounded firm review", content_reference="content:1",
        content_fingerprint=FP_B, created_at=NOW, effective_from=NOW,
        approval_evidence_reference="source-approval:1",
        approval_evidence_fingerprint=FP_A,
    )


def _lifecycle(instrument: Any, status: LegalClientMatterAcceptanceInstrumentLifecycleStatus) -> Any:
    return SimpleNamespace(status=status, instrument_fingerprint=instrument.fingerprint)


@pytest.fixture(autouse=True)
def seams(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(orchestrator, "TenantAuthorizationDecisionEvidenceRegistry", FakeAuthorizationRegistry)
    monkeypatch.setattr(orchestrator.matter_registry.LegalOperationsLifecycleRegistry, "get_entity_history", staticmethod(lambda *_a, **_k: (_matter(),)))
    monkeypatch.setattr(orchestrator.instrument_registry, "get_instrument", staticmethod(lambda *_a, **_k: _instrument()))
    monkeypatch.setattr(orchestrator.instrument_registry, "get_latest_effective_version", staticmethod(lambda *_a, **_k: _instrument()))
    monkeypatch.setattr(orchestrator.lifecycle_registry, "get_current_lifecycle", staticmethod(lambda *_a, **_k: _lifecycle(_instrument(), LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE)))
    monkeypatch.setattr(orchestrator.approval_registry, "persist_approval", staticmethod(lambda value, _collection, *, session: value))


def _invoke(auth: FakeAuthorizationRegistry, **changes: object) -> Any:
    values: dict[str, object] = dict(
        identity=_identity(), case_matter_id=MATTER_ID, instrument_id=INSTRUMENT_ID,
        version=VERSION, approval_id=APPROVAL_ID, idempotency_key="idem-1",
        decision="APPROVED", approver_capacity_reference="capacity:partner",
        approval_evidence_reference="approval-evidence:1",
        approval_evidence_fingerprint=FP_A, matter_lifecycle_collection=object(),
        instrument_collection=object(), instrument_lifecycle_collection=object(),
        approval_collection=object(), authorization_evidence_registry=auth,
        session=Session(),
    )
    values.update(changes)
    return orchestrator.issue_legal_client_matter_acceptance_instrument_approval(**values)  # type: ignore[arg-type]


def test_iam_permission_binding_and_least_privilege() -> None:
    metadata = permission_namespace.permission_metadata(orchestrator.PERMISSION)
    assert metadata.namespace == "TENANT" and metadata.tenant_membership_required
    assert roles.ROLE_PERMISSIONS_MAP["LEGAL_PARTNER"].count(orchestrator.PERMISSION) == 1
    assert roles.ROLE_PERMISSIONS_MAP["LEGAL_ATTORNEY"].count(orchestrator.PERMISSION) == 1
    assert orchestrator.PERMISSION not in roles.ROLE_PERMISSIONS_MAP["LEGAL_PARALEGAL"]
    assert tenant_authority_policy.permission_for_business_role_operation(orchestrator.OPERATION) == orchestrator.PERMISSION
    assert tenant_authority_policy.tenant_role_operation_eligibility("tenant_legal_attorney", orchestrator.OPERATION) == tenant_authority_policy.ELIGIBLE
    assert tenant_authority_policy.tenant_role_operation_eligibility("tenant_legal_client", orchestrator.OPERATION) == tenant_authority_policy.DENY
    assert tenant_authorization._BINDINGS[orchestrator.OPERATION] == orchestrator.PERMISSION


def test_success_derives_scope_and_reuses_one_session() -> None:
    auth = FakeAuthorizationRegistry()
    result = _invoke(auth)
    assert result.tenant_id == TENANT and result.approver_principal_id == PRINCIPAL
    assert result.case_matter_id == MATTER_ID and result.instrument_id == INSTRUMENT_ID
    assert result.decision.value == "APPROVED"
    assert auth.calls[0]["tenant_id"] == TENANT
    assert auth.calls[0]["principal_id"] == PRINCIPAL
    assert auth.calls[0]["session"] is not None
    assert auth.calls[0]["operation"] == orchestrator.OPERATION
    assert auth.calls[0]["permission"] == orchestrator.PERMISSION


def test_rejected_decision_is_supported() -> None:
    result = _invoke(FakeAuthorizationRegistry(), decision="REJECTED")
    assert result.decision.value == "REJECTED"


def test_inactive_identity_and_missing_transaction_fail_closed() -> None:
    with pytest.raises(orchestrator.LegalClientMatterAcceptanceInstrumentApprovalOrchestrationError) as inactive:
        _invoke(FakeAuthorizationRegistry(), identity=_identity(PrincipalStatus.SUSPENDED))
    assert inactive.value.code == "L9A4_P2B3_PRINCIPAL_INACTIVE"
    with pytest.raises(orchestrator.LegalClientMatterAcceptanceInstrumentApprovalOrchestrationError) as missing:
        _invoke(FakeAuthorizationRegistry(), session=SimpleNamespace(in_transaction=False))
    assert missing.value.code == "L9A4_P2B3_ACTIVE_TRANSACTION_REQUIRED"


@pytest.mark.parametrize("status", [
    LegalClientMatterAcceptanceInstrumentLifecycleStatus.SUPERSEDED,
    LegalClientMatterAcceptanceInstrumentLifecycleStatus.RETIRED,
    LegalClientMatterAcceptanceInstrumentLifecycleStatus.WITHDRAWN,
])
def test_terminal_lifecycle_rejects(status: LegalClientMatterAcceptanceInstrumentLifecycleStatus, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(orchestrator.lifecycle_registry, "get_current_lifecycle", staticmethod(lambda *_a, **_k: _lifecycle(_instrument(), status)))
    with pytest.raises(orchestrator.LegalClientMatterAcceptanceInstrumentApprovalOrchestrationError) as error:
        _invoke(FakeAuthorizationRegistry())
    assert error.value.code == "L9A4_P2B3_INSTRUMENT_NOT_ACTIVE"


def test_stale_latest_version_rejects(monkeypatch: pytest.MonkeyPatch) -> None:
    other = SimpleNamespace(version="2.0.0", fingerprint=FP_B)
    monkeypatch.setattr(orchestrator.instrument_registry, "get_latest_effective_version", staticmethod(lambda *_a, **_k: other))
    with pytest.raises(orchestrator.LegalClientMatterAcceptanceInstrumentApprovalOrchestrationError) as error:
        _invoke(FakeAuthorizationRegistry())
    assert error.value.code == "L9A4_P2B3_INSTRUMENT_VERSION_NOT_LATEST"


def test_authorization_denial_is_fail_closed() -> None:
    auth = FakeAuthorizationRegistry()
    auth.error = orchestrator.TenantAuthorizationDecisionEvidenceAuthorizationDeniedError("DENIED")
    with pytest.raises(orchestrator.LegalClientMatterAcceptanceInstrumentApprovalOrchestrationError) as error:
        _invoke(auth)
    assert error.value.code == "L9A4_P2B3_APPROVER_AUTHORIZATION_REQUIRED"


def test_invalid_decision_and_cross_scope_identity_reject() -> None:
    with pytest.raises(orchestrator.LegalClientMatterAcceptanceInstrumentApprovalOrchestrationError):
        _invoke(FakeAuthorizationRegistry(), decision="PENDING")
    with pytest.raises(orchestrator.LegalClientMatterAcceptanceInstrumentApprovalOrchestrationError):
        _invoke(FakeAuthorizationRegistry(), case_matter_id="other-matter")


def test_exact_replay_material_is_stable_and_divergent_intent_changes_fingerprint() -> None:
    first = FakeAuthorizationRegistry()
    _invoke(first)
    second = FakeAuthorizationRegistry()
    _invoke(second)
    assert first.calls[0]["subject_evidence_fingerprint"] == second.calls[0]["subject_evidence_fingerprint"]
    divergent = FakeAuthorizationRegistry()
    _invoke(divergent, decision="REJECTED")
    assert divergent.calls[0]["subject_evidence_fingerprint"] != first.calls[0]["subject_evidence_fingerprint"]


def test_caller_cannot_supply_server_derived_fingerprints_or_tenant() -> None:
    parameters = inspect.signature(orchestrator.issue_legal_client_matter_acceptance_instrument_approval).parameters
    for forbidden in ("tenant_id", "principal_id", "matter_fingerprint", "instrument_fingerprint", "content_fingerprint", "authorization_evidence_fingerprint"):
        assert forbidden not in parameters


def test_no_financial_or_acceptance_authority_is_imported() -> None:
    source = inspect.getsource(orchestrator)
    assert "LegalClientAcceptance" not in source
    assert "financial" in source.lower()
    assert "ClientAcceptance" not in source


# ARTIFACT: test_legal_client_matter_acceptance_instrument_approval_orchestrator.py
# VERSION: v1.0.0-L9A4-P2B3-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL-ISSUANCE-CERT
# AUTHORITY BOUNDARY: direct approval-issuance composition only
# TENANT POSTURE: authenticated exact tenant/matter/instrument/lifecycle binding
# FAIL-CLOSED POSTURE: inactive, stale, terminal, denied and divergent inputs reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
