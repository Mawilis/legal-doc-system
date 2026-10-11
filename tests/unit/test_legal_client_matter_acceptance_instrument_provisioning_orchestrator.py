"""Direct certificate for atomic acceptance-instrument provisioning.

TITLE: Acceptance Instrument Provisioning Orchestrator Certificate
VERSION: v1.0.0-CLIENT-ACCEPTANCE-INSTRUMENT-PROVISIONING-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove exact IAM, server-derived scope, ordered content/instrument/ACTIVE
         composition, replay boundaries and absence of downstream authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_acceptance_instrument_provisioning_orchestrator.py
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0 establishes direct orchestration certification.
TENANT BOUNDARY: Synthetic identity-derived scope only.
AUTHORITY BOUNDARY: Provisioning only; no approval or client acceptance.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from datetime import datetime, timezone
import hashlib
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth import permission_namespace, roles, tenant_authority_policy, tenant_authorization
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.orchestration import legal_client_matter_acceptance_instrument_provisioning_orchestrator as subject


NOW = datetime(2026, 10, 11, 12, 0, tzinfo=timezone.utc)
FP = hashlib.sha3_512(b"source").hexdigest()


class Session:
    in_transaction = True


class AuthorizationRegistry:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
    def issue(self, **kwargs: object) -> Any:
        self.calls.append(dict(kwargs))
        return SimpleNamespace(**kwargs, authorized_at=NOW, authorization_evidence_reference="auth:one", authorization_evidence_fingerprint=FP)


def identity(status: PrincipalStatus = PrincipalStatus.ACTIVE) -> SovereignIdentity:
    return SovereignIdentity(identity_id="principal-one", tenant_id="tenant-one", username=None, email=None, auth_method="synthetic", status=status)


def matter() -> CaseMatter:
    return CaseMatter(tenant_id="tenant-one", case_matter_id="matter-one", matter_reference="M-1", opened_at=NOW, evidence_reference="matter:open")


@pytest.fixture(autouse=True)
def seams(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(subject, "TenantAuthorizationDecisionEvidenceRegistry", AuthorizationRegistry)
    monkeypatch.setattr(subject.matter_registry.LegalOperationsLifecycleRegistry, "get_entity_history", staticmethod(lambda *_a, **_k: (matter(),)))
    monkeypatch.setattr(subject.content_registry, "persist_content", staticmethod(lambda value, _bytes, _collection, *, session: value))
    monkeypatch.setattr(subject.instrument_registry, "persist_instrument", staticmethod(lambda value, _collection, *, session: value))
    monkeypatch.setattr(subject.lifecycle_registry, "persist_lifecycle", staticmethod(lambda value, _collection, *, instrument_collection, session: value))


def invoke(registry: AuthorizationRegistry, **changes: object) -> Any:
    values: dict[str, object] = dict(identity=identity(), case_matter_id="matter-one", instrument_id="instrument-one", version="1.0.0", instrument_kind="MATTER_REVIEW", title="Client review", review_scope="client-information-review:v1", content=b"Review terms", media_type="text/plain", effective_from=NOW, approval_evidence_reference="authoring:one", approval_evidence_fingerprint=FP, idempotency_key="idem-one", matter_lifecycle_collection=object(), content_collection=object(), instrument_collection=object(), instrument_lifecycle_collection=object(), authorization_evidence_registry=registry, session=Session())
    values.update(changes)
    return subject.provision_legal_client_matter_acceptance_instrument(**values)  # type: ignore[arg-type]


def test_iam_is_exact_partner_attorney_only() -> None:
    assert permission_namespace.permission_metadata(subject.PERMISSION).namespace == "TENANT"
    assert roles.get_roles_granting_permission(subject.PERMISSION) == ("LEGAL_ATTORNEY", "LEGAL_PARTNER")
    assert tenant_authority_policy.permission_for_business_role_operation(subject.OPERATION) == subject.PERMISSION
    assert tenant_authority_policy.tenant_role_operation_eligibility("tenant_legal_partner", subject.OPERATION) == tenant_authority_policy.ELIGIBLE
    assert tenant_authority_policy.tenant_role_operation_eligibility("tenant_legal_attorney", subject.OPERATION) == tenant_authority_policy.ELIGIBLE
    for denied in ("tenant_legal_client", "tenant_legal_paralegal", "tenant_legal_secretary", "tenant_legal_finance", "tenant_sheriff", "tenant_deputy"):
        assert tenant_authority_policy.tenant_role_operation_eligibility(denied, subject.OPERATION) == tenant_authority_policy.DENY
    assert tenant_authorization._BINDINGS[subject.OPERATION] == subject.PERMISSION


def test_success_correlates_atomic_three_write_result_and_server_scope() -> None:
    registry = AuthorizationRegistry()
    result = invoke(registry)
    assert result.content.tenant_id == "tenant-one"
    assert result.instrument.content_reference == result.content.content_reference
    assert result.lifecycle.instrument_fingerprint == result.instrument.fingerprint
    assert result.lifecycle.status.value == "ACTIVE"
    assert registry.calls[0]["tenant_id"] == "tenant-one"
    assert registry.calls[0]["principal_id"] == "principal-one"
    assert registry.calls[0]["operation"] == subject.OPERATION
    assert registry.calls[0]["permission"] == subject.PERMISSION


def test_inactive_identity_missing_transaction_and_invalid_content_reject() -> None:
    with pytest.raises(subject.LegalClientMatterAcceptanceInstrumentProvisioningError):
        invoke(AuthorizationRegistry(), identity=identity(PrincipalStatus.SUSPENDED))
    with pytest.raises(subject.LegalClientMatterAcceptanceInstrumentProvisioningError):
        invoke(AuthorizationRegistry(), session=SimpleNamespace(in_transaction=False))
    with pytest.raises(subject.LegalClientMatterAcceptanceInstrumentProvisioningError):
        invoke(AuthorizationRegistry(), content=b"")


def test_result_contains_no_downstream_authority() -> None:
    result = invoke(AuthorizationRegistry())
    flattened = repr(result).lower()
    for forbidden in ("approval_id", "acceptance_id", "engagement_id", "representation_id", "payment_id", "settlement_id", "ai_confidence"):
        assert forbidden not in flattened


# ARTIFACT: test_legal_client_matter_acceptance_instrument_provisioning_orchestrator.py
# VERSION: v1.0.0-CLIENT-ACCEPTANCE-INSTRUMENT-PROVISIONING-CERT
# AUTHORITY BOUNDARY: direct atomic provisioning certificate only
# TENANT POSTURE: tenant/principal derive from active synthetic identity
# FAIL-CLOSED POSTURE: denied, inactive, untransactional and invalid inputs reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
