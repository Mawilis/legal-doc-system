from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Mapping

import pytest

from tools.eos.auth.privileged_activation import (
    PrivilegedActivation,
)

from tools.eos.auth.privileged_channel_currentness import (
    WorkloadTrustFact,
    WorkloadTrustStatus,
)
from tools.eos.auth.privileged_activation_use_authority import (
    PrivilegedActivationUseAuthority,
    PrivilegedActivationUseError,
)
from tools.eos.auth.privileged_eligibility import (
    PrivilegedTargetClass,
)
from tools.eos.auth.privileged_security_assurance import (
    PrivilegedAssurancePurpose,
)


NOW = datetime(
    2026,
    10,
    15,
    4,
    0,
    tzinfo=timezone.utc,
)


def fp(value: str) -> str:
    return hashlib.sha3_512(
        value.encode("utf-8")
    ).hexdigest()


ELIGIBILITY_FP = fp("p5-eligibility")
ASSURANCE_FP = fp("p5-assurance")


def activation() -> PrivilegedActivation:
    return PrivilegedActivation.issue(
        activation_id="activation-a",
        tenant_id="tenant-a",
        principal_id="principal-a",
        actor_principal_id="principal-a",
        privileged_role_id="ENTERPRISE_ADMIN",
        target_class=PrivilegedTargetClass.TENANT_PRIVILEGED,
        eligibility_evidence_id="eligibility-a",
        eligibility_evidence_fingerprint=ELIGIBILITY_FP,
        assurance_evidence_id="create-assurance-a",
        assurance_evidence_fingerprint=ASSURANCE_FP,
        creation_assurance_purpose=(
            PrivilegedAssurancePurpose
            .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
        ),
        activated_at=NOW,
        effective_until=NOW + timedelta(minutes=15),
        issuance_idempotency_key="issue-a",
    )


@dataclass(frozen=True)
class Eligibility:
    eligibility_evidence_id: str = "eligibility-a"
    eligibility_evidence_fingerprint: str = ELIGIBILITY_FP
    tenant_id: str | None = "tenant-a"
    principal_id: str = "principal-a"
    privileged_role_id: str = "ENTERPRISE_ADMIN"
    target_class: PrivilegedTargetClass = (
        PrivilegedTargetClass.TENANT_PRIVILEGED
    )


@dataclass(frozen=True)
class Decision:
    sufficient: bool = True


@dataclass(frozen=True)
class Evidence:
    assurance_purpose: PrivilegedAssurancePurpose = (
        PrivilegedAssurancePurpose.PRIVILEGED_ACTIVATION_USE
    )
    principal_id: str = "principal-a"


@dataclass(frozen=True)
class AssuranceResult:
    decision: Decision = Decision()
    evidence: Evidence = Evidence()
    workload_fact: WorkloadTrustFact | None = WorkloadTrustFact(
        proof_reference="workload-proof-a",
        principal_id="principal-a",
        credential_or_attestation_reference="workload-credential-a",
        observed_at=NOW,
        status=WorkloadTrustStatus.CURRENT,
    )


class Registry:
    def __init__(
        self,
        item: PrivilegedActivation | None,
    ) -> None:
        self.item = item
        self.calls: list[dict[str, object]] = []

    def resolve_current(
        self,
        *,
        tenant_id: str | None,
        principal_id: str,
        privileged_role_id: str,
        target_class: PrivilegedTargetClass,
        at: datetime,
        session: object | None = None,
    ) -> PrivilegedActivation | None:
        self.calls.append(
            {
                "tenant_id": tenant_id,
                "principal_id": principal_id,
                "privileged_role_id": privileged_role_id,
                "target_class": target_class,
                "at": at,
                "session": session,
            }
        )
        return self.item


class EligibilityResolver:
    def __init__(
        self,
        item: Eligibility | None,
    ) -> None:
        self.item = item
        self.calls: list[dict[str, object]] = []

    def resolve(
        self,
        *,
        eligibility_evidence_id: str,
        at: datetime,
        session: object | None = None,
    ) -> Eligibility | None:
        self.calls.append(
            {
                "eligibility_evidence_id": (
                    eligibility_evidence_id
                ),
                "at": at,
                "session": session,
            }
        )
        return self.item


class InteractiveService:
    def __init__(
        self,
        result: AssuranceResult | None = None,
    ) -> None:
        self.result = result or AssuranceResult()
        self.calls: list[dict[str, object]] = []

    def compose(
        self,
        *,
        tenant_id: str,
        proof_reference: str,
        assurance_purpose: PrivilegedAssurancePurpose,
        idempotency_key: str,
        session: object,
    ) -> AssuranceResult:
        self.calls.append(
            {
                "tenant_id": tenant_id,
                "proof_reference": proof_reference,
                "assurance_purpose": assurance_purpose,
                "idempotency_key": idempotency_key,
                "session": session,
            }
        )
        return self.result


class NoninteractiveService:
    def __init__(
        self,
        result: AssuranceResult | None = None,
    ) -> None:
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
        self.calls.append(
            {
                "request": request,
                "body": body,
                "keys": keys,
                "expected_audience": expected_audience,
                "assurance_purpose": assurance_purpose,
                "idempotency_key": idempotency_key,
                "session": session,
            }
        )
        return self.result


SESSION = object()


def build(
    *,
    current: PrivilegedActivation | None = None,
    eligibility: Eligibility | None = None,
    interactive_result: AssuranceResult | None = None,
) -> tuple[
    PrivilegedActivationUseAuthority,
    Registry,
    EligibilityResolver,
    InteractiveService,
]:
    registry = Registry(
        activation()
        if current is None
        else current
    )

    resolver = EligibilityResolver(
        Eligibility()
        if eligibility is None
        else eligibility
    )

    interactive = InteractiveService(
        interactive_result
    )

    authority = PrivilegedActivationUseAuthority(
        activation_registry=registry,
        eligibility_resolver=resolver,
        interactive_assurance_service=interactive,
    )

    return (
        authority,
        registry,
        resolver,
        interactive,
    )


def test_interactive_real_contract_shape_green() -> None:
    authority, registry, resolver, interactive = build()

    result = authority.authorize_interactive(
        activation_tenant_id="tenant-a",
        proof_tenant_id="tenant-a",
        principal_id="principal-a",
        privileged_role_id="ENTERPRISE_ADMIN",
        target_class=PrivilegedTargetClass.TENANT_PRIVILEGED,
        at=NOW + timedelta(minutes=1),
        proof_reference="proof-a",
        idempotency_key="use-a",
        session=SESSION,
    )

    assert result.activation_id == "activation-a"

    assert registry.calls[0]["session"] is SESSION

    assert (
        resolver.calls[0]["eligibility_evidence_id"]
        == "eligibility-a"
    )

    assert resolver.calls[0]["session"] is SESSION

    assert (
        interactive.calls[0]["assurance_purpose"]
        == PrivilegedAssurancePurpose.PRIVILEGED_ACTIVATION_USE
    )

    assert interactive.calls[0]["session"] is SESSION


def test_missing_current_p2_denies_before_p3() -> None:
    registry = Registry(
        activation()
    )
    resolver = EligibilityResolver(
        None
    )
    interactive = InteractiveService()

    authority = PrivilegedActivationUseAuthority(
        activation_registry=registry,
        eligibility_resolver=resolver,
        interactive_assurance_service=interactive,
    )

    with pytest.raises(
        PrivilegedActivationUseError,
    ):
        authority.authorize_interactive(
            activation_tenant_id="tenant-a",
            proof_tenant_id="tenant-a",
            principal_id="principal-a",
            privileged_role_id="ENTERPRISE_ADMIN",
            target_class=PrivilegedTargetClass.TENANT_PRIVILEGED,
            at=NOW + timedelta(minutes=1),
            proof_reference="proof-a",
            idempotency_key="use-a",
            session=SESSION,
        )

    assert not interactive.calls


def test_p2_lineage_mismatch_denies() -> None:
    authority, _, _, _ = build(
        eligibility=Eligibility(
            eligibility_evidence_id="eligibility-b",
        )
    )

    with pytest.raises(
        PrivilegedActivationUseError,
    ):
        authority.authorize_interactive(
            activation_tenant_id="tenant-a",
            proof_tenant_id="tenant-a",
            principal_id="principal-a",
            privileged_role_id="ENTERPRISE_ADMIN",
            target_class=PrivilegedTargetClass.TENANT_PRIVILEGED,
            at=NOW + timedelta(minutes=1),
            proof_reference="proof-a",
            idempotency_key="use-a",
            session=SESSION,
        )


def test_wrong_assurance_purpose_denies() -> None:
    bad = AssuranceResult(
        evidence=Evidence(
            assurance_purpose=(
                PrivilegedAssurancePurpose
                .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
            ),
        )
    )

    authority, _, _, _ = build(
        interactive_result=bad,
    )

    with pytest.raises(
        PrivilegedActivationUseError,
    ):
        authority.authorize_interactive(
            activation_tenant_id="tenant-a",
            proof_tenant_id="tenant-a",
            principal_id="principal-a",
            privileged_role_id="ENTERPRISE_ADMIN",
            target_class=PrivilegedTargetClass.TENANT_PRIVILEGED,
            at=NOW + timedelta(minutes=1),
            proof_reference="proof-a",
            idempotency_key="use-a",
            session=SESSION,
        )


def test_insufficient_assurance_denies() -> None:
    bad = AssuranceResult(
        decision=Decision(
            sufficient=False,
        )
    )

    authority, _, _, _ = build(
        interactive_result=bad,
    )

    with pytest.raises(
        PrivilegedActivationUseError,
    ):
        authority.authorize_interactive(
            activation_tenant_id="tenant-a",
            proof_tenant_id="tenant-a",
            principal_id="principal-a",
            privileged_role_id="ENTERPRISE_ADMIN",
            target_class=PrivilegedTargetClass.TENANT_PRIVILEGED,
            at=NOW + timedelta(minutes=1),
            proof_reference="proof-a",
            idempotency_key="use-a",
            session=SESSION,
        )


def test_noninteractive_real_contract_shape_green() -> None:
    registry = Registry(
        activation()
    )
    resolver = EligibilityResolver(
        Eligibility()
    )
    noninteractive = NoninteractiveService()

    authority = PrivilegedActivationUseAuthority(
        activation_registry=registry,
        eligibility_resolver=resolver,
        noninteractive_assurance_service=noninteractive,
    )

    result = authority.authorize_noninteractive(
        activation_tenant_id="tenant-a",
        principal_id="principal-a",
        privileged_role_id="ENTERPRISE_ADMIN",
        target_class=PrivilegedTargetClass.TENANT_PRIVILEGED,
        at=NOW + timedelta(minutes=1),
        request={"authorization": "signature"},
        body=b"{}",
        keys={"key-a": ("secret", "alg")},
        expected_audience="wilsy-eos",
        idempotency_key="use-noninteractive-a",
        session=SESSION,
    )

    assert result.activation_id == "activation-a"

    assert (
        noninteractive.calls[0]["assurance_purpose"]
        == PrivilegedAssurancePurpose.PRIVILEGED_ACTIVATION_USE
    )

    assert (
        noninteractive.calls[0]["session"]
        is SESSION
    )



def test_platform_activation_scope_and_proof_tenant_are_distinct() -> None:
    platform = PrivilegedActivation.issue(
        activation_id="activation-platform-a",
        tenant_id=None,
        principal_id="principal-a",
        actor_principal_id="principal-a",
        privileged_role_id="SOVEREIGN_ARCHITECT",
        target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT,
        eligibility_evidence_id="eligibility-a",
        eligibility_evidence_fingerprint=ELIGIBILITY_FP,
        assurance_evidence_id="create-assurance-a",
        assurance_evidence_fingerprint=ASSURANCE_FP,
        creation_assurance_purpose=(
            PrivilegedAssurancePurpose
            .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
        ),
        activated_at=NOW,
        effective_until=NOW + timedelta(minutes=15),
        issuance_idempotency_key="issue-platform-a",
    )

    platform_eligibility = Eligibility(
        tenant_id=None,
        privileged_role_id="SOVEREIGN_ARCHITECT",
        target_class=(
            PrivilegedTargetClass
            .PLATFORM_SYSTEM_ROOT
        ),
    )

    registry = Registry(
        platform
    )

    resolver = EligibilityResolver(
        platform_eligibility
    )

    interactive = InteractiveService()

    authority = PrivilegedActivationUseAuthority(
        activation_registry=registry,
        eligibility_resolver=resolver,
        interactive_assurance_service=interactive,
    )

    result = authority.authorize_interactive(
        activation_tenant_id=None,
        proof_tenant_id="tenant-proof-a",
        principal_id="principal-a",
        privileged_role_id="SOVEREIGN_ARCHITECT",
        target_class=(
            PrivilegedTargetClass
            .PLATFORM_SYSTEM_ROOT
        ),
        at=NOW + timedelta(minutes=1),
        proof_reference="proof-platform-a",
        idempotency_key="use-platform-a",
        session=SESSION,
    )

    assert (
        result.activation_id
        == "activation-platform-a"
    )

    assert (
        registry.calls[0]["tenant_id"]
        is None
    )

    assert (
        interactive.calls[0]["tenant_id"]
        == "tenant-proof-a"
    )



def test_noninteractive_workload_path_derives_principal_once_and_checks_platform_scope() -> None:
    platform = PrivilegedActivation.issue(
        activation_id="activation-platform-workload-a",
        tenant_id=None,
        principal_id="principal-a",
        actor_principal_id="principal-a",
        privileged_role_id="SOVEREIGN_ARCHITECT",
        target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT,
        eligibility_evidence_id="eligibility-a",
        eligibility_evidence_fingerprint=ELIGIBILITY_FP,
        assurance_evidence_id="create-assurance-platform-a",
        assurance_evidence_fingerprint=ASSURANCE_FP,
        creation_assurance_purpose=PrivilegedAssurancePurpose.PRIVILEGED_ELIGIBILITY_TO_ACTIVATION,
        activated_at=NOW,
        effective_until=NOW + timedelta(minutes=15),
        issuance_idempotency_key="issue-platform-workload-a",
    )
    platform_eligibility = Eligibility(
        tenant_id=None,
        privileged_role_id="SOVEREIGN_ARCHITECT",
        target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT,
    )
    registry = Registry(platform)
    resolver = EligibilityResolver(platform_eligibility)
    noninteractive = NoninteractiveService()
    authority = PrivilegedActivationUseAuthority(
        activation_registry=registry,
        eligibility_resolver=resolver,
        noninteractive_assurance_service=noninteractive,
    )

    result = authority.authorize_noninteractive_workload(
        activation_tenant_id=None,
        privileged_role_id="SOVEREIGN_ARCHITECT",
        target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT,
        at=NOW + timedelta(minutes=1),
        request={"service_id": "trusted"},
        body=b"{}",
        keys={"key-a": ("secret", "algorithm")},
        expected_audience="wilsy-eos-reconciliation",
        idempotency_key="use-platform-workload-a",
        session=SESSION,
    )

    assert result.activation.activation_id == "activation-platform-workload-a"
    assert result.principal_id == "principal-a"
    assert len(noninteractive.calls) == 1
    assert noninteractive.calls[0]["session"] is SESSION
    assert registry.calls[0]["principal_id"] == "principal-a"
    assert registry.calls[0]["tenant_id"] is None
    assert registry.calls[0]["target_class"] is PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT


def test_noninteractive_workload_path_rejects_missing_verified_workload_fact() -> None:
    registry = Registry(None)
    resolver = EligibilityResolver(None)
    noninteractive = NoninteractiveService(
        AssuranceResult(workload_fact=None)
    )
    authority = PrivilegedActivationUseAuthority(
        activation_registry=registry,
        eligibility_resolver=resolver,
        noninteractive_assurance_service=noninteractive,
    )

    with pytest.raises(
        PrivilegedActivationUseError,
        match="VERIFIED_WORKLOAD_FACT_REQUIRED",
    ):
        authority.authorize_noninteractive_workload(
            activation_tenant_id=None,
            privileged_role_id="SOVEREIGN_ARCHITECT",
            target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT,
            at=NOW + timedelta(minutes=1),
            request={"service_id": "untrusted"},
            body=b"{}",
            keys={"key-a": ("secret", "algorithm")},
            expected_audience="wilsy-eos-reconciliation",
            idempotency_key="use-platform-workload-missing-fact",
            session=SESSION,
        )

    assert not registry.calls
    assert len(noninteractive.calls) == 1


def test_noninteractive_workload_path_rejects_assurance_principal_mismatch() -> None:
    wrong_fact = WorkloadTrustFact(
        proof_reference="workload-proof-a",
        principal_id="principal-a",
        credential_or_attestation_reference="workload-credential-a",
        observed_at=NOW,
        status=WorkloadTrustStatus.CURRENT,
    )
    wrong_result = AssuranceResult(
        evidence=Evidence(principal_id="principal-b"),
        workload_fact=wrong_fact,
    )
    authority, registry, resolver, _ = build()
    noninteractive = NoninteractiveService(wrong_result)
    authority = PrivilegedActivationUseAuthority(
        activation_registry=registry,
        eligibility_resolver=resolver,
        noninteractive_assurance_service=noninteractive,
    )

    with pytest.raises(
        PrivilegedActivationUseError,
        match="PRIVILEGED_USE_ASSURANCE_PRINCIPAL_MISMATCH",
    ):
        authority.authorize_noninteractive_workload(
            activation_tenant_id="tenant-a",
            privileged_role_id="ENTERPRISE_ADMIN",
            target_class=PrivilegedTargetClass.TENANT_PRIVILEGED,
            at=NOW + timedelta(minutes=1),
            request={"service_id": "trusted"},
            body=b"{}",
            keys={"key-a": ("secret", "algorithm")},
            expected_audience="wilsy-eos",
            idempotency_key="use-principal-mismatch",
            session=SESSION,
        )

    assert len(noninteractive.calls) == 1
    assert not registry.calls
    assert not resolver.calls



def test_noninteractive_workload_path_rejects_stale_workload_fact_before_p4_lookup() -> None:
    stale_fact = WorkloadTrustFact(
        proof_reference="workload-proof-stale",
        principal_id="principal-a",
        credential_or_attestation_reference="workload-credential-a",
        observed_at=NOW,
        status=WorkloadTrustStatus.REVOKED,
    )
    registry = Registry(activation())
    resolver = EligibilityResolver(Eligibility())
    noninteractive = NoninteractiveService(
        AssuranceResult(workload_fact=stale_fact)
    )
    authority = PrivilegedActivationUseAuthority(
        activation_registry=registry,
        eligibility_resolver=resolver,
        noninteractive_assurance_service=noninteractive,
    )

    with pytest.raises(
        PrivilegedActivationUseError,
        match="WORKLOAD_PROOF_NOT_CURRENT",
    ):
        authority.authorize_noninteractive_workload(
            activation_tenant_id="tenant-a",
            privileged_role_id="ENTERPRISE_ADMIN",
            target_class=PrivilegedTargetClass.TENANT_PRIVILEGED,
            at=NOW + timedelta(minutes=1),
            request={"service_id": "trusted"},
            body=b"{}",
            keys={"key-a": ("secret", "algorithm")},
            expected_audience="wilsy-eos",
            idempotency_key="use-stale-workload-a",
            session=SESSION,
        )

    assert len(noninteractive.calls) == 1
    assert not registry.calls
    assert not resolver.calls

def test_no_privileged_use_permission_or_break_glass_surface() -> None:
    source = Path(
        "tools/eos/auth/privileged_activation_use_authority.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "privileged_activation:use" not in source
    assert "privileged_activation:break_glass" not in source
    assert "issue_activation" not in source
    assert "create_permission" not in source
    assert "assign_role" not in source
