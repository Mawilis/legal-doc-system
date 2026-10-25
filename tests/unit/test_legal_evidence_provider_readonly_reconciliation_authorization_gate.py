from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Mapping

import pytest

from tools.eos.auth.current_system_permission_possession import (
    CurrentSystemPermissionPossessionResolver,
)
from tools.eos.auth.privileged_activation import PrivilegedActivation
from tools.eos.auth.privileged_activation_use_authority import (
    PrivilegedActivationUseAuthority,
)
from tools.eos.auth.privileged_channel_currentness import (
    WorkloadTrustFact,
    WorkloadTrustStatus,
)
from tools.eos.auth.privileged_eligibility import PrivilegedTargetClass
from tools.eos.auth.privileged_security_assurance import PrivilegedAssurancePurpose
from tools.eos.auth.system_permission_assignment import (
    SystemPermissionAssignment,
    SystemPermissionAssignmentStatus,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceProviderDiscoveryScope,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_authorization_gate import (
    RECONCILIATION_READ_PERMISSION,
    LegalEvidenceProviderReadOnlyReconciliationAuthorizationError,
    LegalEvidenceProviderReadOnlyReconciliationAuthorizationGate,
    ServerOwnedReconciliationScopeResolutionError,
)


NOW = datetime(2026, 10, 25, 7, 0, tzinfo=timezone.utc)
SESSION = type("ActiveSession", (), {"in_transaction": True})()
ELIGIBILITY_FP = hashlib.sha3_512(b"eligibility-platform").hexdigest()
ASSURANCE_FP = hashlib.sha3_512(b"assurance-platform").hexdigest()
SCOPE_FP = hashlib.sha3_512("tenant-a".encode("utf-8")).hexdigest()
TRUSTED_REQUEST = {
    "version": "v1",
    "service_id": "internal-legal-ops",
    "audience": "wilsy-eos-reconciliation",
    "key_id": "key-a",
    "timestamp": "1792911600",
    "nonce": "nonce-a",
    "body_sha3_512": hashlib.sha3_512(b"{}").hexdigest(),
    "correlation_id": "corr-a",
    "signature": "signature-a",
    "method": "POST",
    "path": "/internal/reconciliation",
}


@dataclass(frozen=True)
class Eligibility:
    eligibility_evidence_id: str = "eligibility-platform-a"
    eligibility_evidence_fingerprint: str = ELIGIBILITY_FP
    tenant_id: str | None = None
    principal_id: str = "operator-a"
    privileged_role_id: str = "SOVEREIGN_ARCHITECT"
    target_class: PrivilegedTargetClass = PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT


@dataclass(frozen=True)
class Decision:
    sufficient: bool = True


@dataclass(frozen=True)
class AssuranceEvidence:
    assurance_purpose: PrivilegedAssurancePurpose = (
        PrivilegedAssurancePurpose.PRIVILEGED_ACTIVATION_USE
    )
    principal_id: str = "operator-a"


@dataclass(frozen=True)
class AssuranceResult:
    decision: Decision = Decision()
    evidence: AssuranceEvidence = AssuranceEvidence()
    workload_fact: WorkloadTrustFact = WorkloadTrustFact(
        proof_reference="workload-proof-a",
        principal_id="operator-a",
        credential_or_attestation_reference="credential-a",
        observed_at=NOW,
        status=WorkloadTrustStatus.CURRENT,
    )


class ActivationRegistry:
    def __init__(self, item: PrivilegedActivation | None = None) -> None:
        self.item = item or PrivilegedActivation.issue(
            activation_id="activation-a",
            tenant_id=None,
            principal_id="operator-a",
            actor_principal_id="operator-a",
            privileged_role_id="SOVEREIGN_ARCHITECT",
            target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT,
            eligibility_evidence_id="eligibility-platform-a",
            eligibility_evidence_fingerprint=ELIGIBILITY_FP,
            assurance_evidence_id="activation-assurance-a",
            assurance_evidence_fingerprint=ASSURANCE_FP,
            creation_assurance_purpose=(
                PrivilegedAssurancePurpose.PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
            ),
            activated_at=NOW,
            effective_until=NOW + timedelta(minutes=15),
            issuance_idempotency_key="activation-issue-a",
        )
        self.calls: list[dict[str, object]] = []

    def resolve_current(self, **kwargs: object) -> PrivilegedActivation | None:
        self.calls.append(kwargs)
        return self.item


class EligibilityResolver:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def resolve(self, **kwargs: object) -> Eligibility:
        self.calls.append(kwargs)
        return Eligibility()


class NoninteractiveAssurance:
    def __init__(self, result: AssuranceResult | None = None) -> None:
        self.result = result or AssuranceResult()
        self.calls: list[dict[str, object]] = []

    def compose(
        self,
        *,
        request: Mapping[str, str],
        body: bytes,
        keys: Mapping[str, tuple[str, str]],
        expected_audience: str,
        assurance_purpose: PrivilegedAssurancePurpose,
        idempotency_key: str,
        session: object,
    ) -> AssuranceResult:
        self.calls.append({
            "request": request,
            "body": body,
            "keys": keys,
            "expected_audience": expected_audience,
            "assurance_purpose": assurance_purpose,
            "idempotency_key": idempotency_key,
            "session": session,
        })
        return self.result


class ScopeResolver:
    provider_name = "aws_s3"

    def __init__(
        self,
        scope: LegalEvidenceProviderDiscoveryScope | None = None,
        error: bool = False,
    ) -> None:
        self.scope = scope or LegalEvidenceProviderDiscoveryScope(
            tenant_id="tenant-a",
            tenant_scope_fingerprint=SCOPE_FP,
        )
        self.error = error
        self.calls: list[dict[str, object]] = []

    def resolve_scope(
        self,
        *,
        principal_id: str,
        activation_id: str,
        at: datetime,
        session: object,
    ) -> LegalEvidenceProviderDiscoveryScope:
        self.calls.append({
            "principal_id": principal_id,
            "activation_id": activation_id,
            "at": at,
            "session": session,
        })
        if self.error:
            raise ServerOwnedReconciliationScopeResolutionError(
                "SCOPE_CONFIGURATION_UNAVAILABLE"
            )
        return self.scope


def assignment() -> SystemPermissionAssignment:
    return SystemPermissionAssignment(
        assignment_id="permission-assignment-a",
        principal_id="operator-a",
        permission_id=RECONCILIATION_READ_PERMISSION,
        status=SystemPermissionAssignmentStatus.ACTIVE,
        assigned_by_principal_id="system-grantor-a",
        assigned_at=NOW,
        assignment_evidence_reference="assignment-evidence-a",
        revision=1,
        previous_assignment_fingerprint=None,
        revoked_by_principal_id=None,
        revoked_at=None,
        revocation_evidence_reference=None,
    )


def build(
    monkeypatch: pytest.MonkeyPatch,
    *,
    permission_assignment: SystemPermissionAssignment | None = None,
    scope_resolver: ScopeResolver | None = None,
) -> tuple[
    LegalEvidenceProviderReadOnlyReconciliationAuthorizationGate,
    NoninteractiveAssurance,
    ScopeResolver,
]:
    activation_registry = ActivationRegistry()
    eligibility_resolver = EligibilityResolver()
    assurance = NoninteractiveAssurance()
    use_authority = PrivilegedActivationUseAuthority(
        activation_registry=activation_registry,
        eligibility_resolver=eligibility_resolver,
        noninteractive_assurance_service=assurance,
    )
    possession = object.__new__(CurrentSystemPermissionPossessionResolver)
    selected_assignment = assignment() if permission_assignment is None else permission_assignment
    monkeypatch.setattr(
        type(possession),
        "resolve",
        lambda self, **kwargs: selected_assignment,
    )
    selected_scope = scope_resolver or ScopeResolver()
    gate = LegalEvidenceProviderReadOnlyReconciliationAuthorizationGate(
        use_authority=use_authority,
        permission_possession_resolver=possession,
        scope_resolver=selected_scope,
        workload_keys={"key-a": ("internal-legal-ops", "secret-a")},
        expected_audience="wilsy-eos-reconciliation",
        provider_name="aws_s3",
    )
    return gate, assurance, selected_scope


def authorize(
    gate: LegalEvidenceProviderReadOnlyReconciliationAuthorizationGate,
    *,
    request: Mapping[str, str] = TRUSTED_REQUEST,
    session: object = SESSION,
):
    return gate.authorize(
        request=request,
        body=b"{}",
        idempotency_key="reconciliation-attempt-a",
        at=NOW + timedelta(minutes=1),
        session=session,
    )


def test_authorizes_exact_platform_operator_and_server_owned_scope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gate, assurance, scope_resolver = build(monkeypatch)

    result = authorize(gate)

    assert result.principal_id == "operator-a"
    assert result.activation_id == "activation-a"
    assert result.permission_assignment_id == "permission-assignment-a"
    assert result.scope.tenant_id == "tenant-a"
    assert result.provider_name == "aws_s3"
    assert result.authorized_at == NOW + timedelta(minutes=1)
    assert len(assurance.calls) == 1
    assert assurance.calls[0]["session"] is SESSION
    assert scope_resolver.calls == [{
        "principal_id": "operator-a",
        "activation_id": "activation-a",
        "at": NOW + timedelta(minutes=1),
        "session": SESSION,
    }]


def test_denies_without_current_reconciliation_permission(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gate, _, scope_resolver = build(
        monkeypatch,
        permission_assignment=None,
    )
    monkeypatch.setattr(
        CurrentSystemPermissionPossessionResolver,
        "resolve",
        lambda self, **kwargs: None,
    )

    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationAuthorizationError,
        match="RECONCILIATION_READ_PERMISSION_REQUIRED",
    ):
        authorize(gate)
    assert not scope_resolver.calls


def test_rejects_request_selected_tenant_or_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gate, _, scope_resolver = build(monkeypatch)
    request = dict(TRUSTED_REQUEST)
    request["tenant_id"] = "tenant-attacker"

    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationAuthorizationError,
        match="TRUSTED_WORKLOAD_REQUEST_INVALID",
    ):
        authorize(gate, request=request)
    assert not scope_resolver.calls


def test_rejects_scope_resolver_bound_to_another_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gate, _, _ = build(monkeypatch)
    bad_scope_resolver = ScopeResolver()
    bad_scope_resolver.provider_name = "other_provider"

    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationAuthorizationError,
        match="SERVER_OWNED_SCOPE_PROVIDER_MISMATCH",
    ):
        LegalEvidenceProviderReadOnlyReconciliationAuthorizationGate(
            use_authority=gate._use_authority,
            permission_possession_resolver=gate._permission_possession_resolver,
            scope_resolver=bad_scope_resolver,
            workload_keys={"key-a": ("internal-legal-ops", "secret-a")},
            expected_audience="wilsy-eos-reconciliation",
            provider_name="aws_s3",
        )


def test_maps_canonical_scope_resolution_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scope_resolver = ScopeResolver(error=True)
    gate, _, _ = build(monkeypatch, scope_resolver=scope_resolver)

    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationAuthorizationError,
        match="SERVER_OWNED_RECONCILIATION_SCOPE_UNAVAILABLE",
    ):
        authorize(gate)


def test_rejects_scope_fingerprint_not_derived_from_tenant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scope_resolver = ScopeResolver(
        scope=LegalEvidenceProviderDiscoveryScope(
            tenant_id="tenant-a",
            tenant_scope_fingerprint="f" * 128,
        )
    )
    gate, _, _ = build(monkeypatch, scope_resolver=scope_resolver)

    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationAuthorizationError,
        match="SERVER_OWNED_RECONCILIATION_SCOPE_FINGERPRINT_INVALID",
    ):
        authorize(gate)


def test_requires_caller_owned_active_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gate, assurance, scope_resolver = build(monkeypatch)
    inactive = type("InactiveSession", (), {"in_transaction": False})()

    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationAuthorizationError,
        match="CALLER_OWNED_ACTIVE_TRANSACTION_REQUIRED",
    ):
        authorize(gate, session=inactive)
    assert not assurance.calls
    assert not scope_resolver.calls
