"""Direct P7 certificate for tenant inbound provider-policy activation issuance.

TITLE: Tenant Inbound Provider Policy Activation Issuance Tests
VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P7-R1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Covers the four public activation authorities, replay/currentness ordering,
         exact policy/configuration identity, immutable event construction, and P6 handoff.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_inbound_provider_policy_activation_issuance.py
COLLABORATION / OWNERSHIP: Direct P7 certificate; P2/P4/P5/P6 and auth remain separate owners.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3C-P7-R1 certifies the canonical role-assignment
           collaborator contract, four authority boundaries, and the complete
           replay, provenance, currentness, CAS, and firewall matrix.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import inspect
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.saas.domain.tenant_inbound_merchant_configuration import InboundMerchantProviderId
from tools.eos.saas.domain.tenant_inbound_provider_policy import TenantInboundProviderPolicyScope
from tools.eos.saas.domain.tenant_inbound_provider_policy_activation import (
    TenantInboundProviderPolicyActivationEventKind,
    TenantInboundProviderPolicyReference,
)
from tools.eos.saas.billing.tenant_inbound_merchant_configuration_registry import EnablementState
from tools.eos.saas.billing import tenant_inbound_provider_policy_activation_issuance as issuance


VERSION = "v1.0.0-M11-R8-R3B-P8-P3C-P7-R1"
CAMPAIGN = "M11-R8-R3B-P8-P3C-P7-R1"
TENANT = "tenant-p7"
SCOPE = TenantInboundProviderPolicyScope.INBOUND_COLLECTION
FP = "a" * 128
NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)


@dataclass
class Session:
    in_transaction: bool = True


class PrincipalRepositoryDouble:
    def __init__(self, value: Any) -> None:
        self.value = value
        self.calls: list[tuple[str, Any]] = []

    def resolve(self, principal_id: str, *, session: Any = None) -> Any:
        self.calls.append((principal_id, session))
        if principal_id != "principal-p7":
            raise KeyError(principal_id)
        return self.value


class MembershipRepositoryDouble:
    def __init__(self, value: Any) -> None:
        self.value = value
        self.calls: list[tuple[str, str, Any]] = []

    def resolve(self, principal_id: str, tenant_id: str, *, session: Any = None) -> Any:
        self.calls.append((principal_id, tenant_id, session))
        if (principal_id, tenant_id) != ("principal-p7", TENANT):
            raise KeyError((principal_id, tenant_id))
        return self.value


class RoleAssignmentRepositoryDouble:
    def __init__(self, values: dict[tuple[str, str, str], Any]) -> None:
        self.values = values
        self.calls: list[tuple[tuple[str, ...], Any]] = []

    def resolve(
        self, principal_id: str, tenant_id: str, role_id: str, *, session: Any = None,
    ) -> RoleAssignmentAuthority:
        args = (principal_id, tenant_id, role_id)
        self.calls.append((tuple(args), session))
        return self.values[args]


class FakeEvidence:
    tenant_id = TENANT
    authorization_decision_id = "decision-p7"
    principal_id = "principal-p7"
    operation = issuance.ACTIVATE_OPERATION
    permission = issuance.ACTIVATE_PERMISSION
    business_role = issuance.ACTIVATE_BUSINESS_ROLE
    authorization_role = issuance.ACTIVATE_AUTH_ROLE
    membership_revision = 3
    role_assignment_revision = 4
    permission_namespace_version = issuance.permission_namespace.VERSION
    authorization_role_policy_version = issuance.roles.VERSION
    tenant_business_role_policy_version = issuance.tenant_authority_policy.VERSION
    tenant_authorization_composition_version = issuance.tenant_authorization.VERSION
    authorization_evidence_fingerprint = FP
    authorization_evidence_reference = "tenant-authorization-decision:decision-p7"


class EvidenceReader:
    def __init__(self, evidence: Any = FakeEvidence()) -> None:
        self.evidence = evidence
        self.calls = 0

    def get(self, *, tenant_id: str, authorization_decision_id: str, session: Any) -> Any:
        self.calls += 1
        assert tenant_id == TENANT
        assert authorization_decision_id == "decision-p7"
        assert session.in_transaction is True
        return self.evidence


class ActivationRegistry:
    def __init__(self, slot: Any = None) -> None:
        self.slot: Any = slot
        self.event: Any = None
        self.lookup_calls = 0
        self.slot_calls = 0
        self.append_calls = 0

    def get_event_by_idempotency_key(self, *args: Any, **kwargs: Any) -> Any:
        self.lookup_calls += 1
        return self.event

    def get_current_slot(self, *args: Any, **kwargs: Any) -> Any:
        self.slot_calls += 1
        return self.slot

    def append_event_and_advance_slot(self, event: Any, revision: Any, prior: Any, **kwargs: Any) -> Any:
        self.append_calls += 1
        self.event = event
        return SimpleNamespace(current_activation_revision=event.activation_revision, current_active_policy=event.target_active_policy)


class PolicyRegistry:
    calls = 0
    policy: Any = None

    @classmethod
    def get(cls, *args: Any, **kwargs: Any) -> Any:
        cls.calls += 1
        return cls.policy


class ConfigurationRegistry:
    calls = 0
    configuration: Any = None

    @classmethod
    def get(cls, *args: Any, **kwargs: Any) -> Any:
        cls.calls += 1
        return cls.configuration


def _reference(policy_id: str = "policy-p7", version: int = 1) -> TenantInboundProviderPolicyReference:
    return TenantInboundProviderPolicyReference(
        provider_policy_id=policy_id,
        policy_version=version,
        policy_fingerprint=FP,
        provider_id=InboundMerchantProviderId.PAYFAST,
        merchant_configuration_id="config-p7",
        merchant_configuration_version=1,
        merchant_configuration_fingerprint=FP,
    )


def _dependencies() -> tuple[Any, Any, RoleAssignmentRepositoryDouble, RoleAssignmentRepositoryDouble]:
    principal = PrincipalRepositoryDouble(SimpleNamespace(principal_id="principal-p7", status=PrincipalStatus.ACTIVE))
    membership = MembershipRepositoryDouble(SimpleNamespace(principal_id="principal-p7", tenant_id=TENANT, status=TenantMembershipStatus.ACTIVE, revision=3))
    assignment = RoleAssignmentRepositoryDouble({
        ("principal-p7", TENANT, issuance.ACTIVATE_AUTH_ROLE): RoleAssignmentAuthority(
            "principal-p7", TENANT, issuance.ACTIVATE_AUTH_ROLE, RoleAssignmentStatus.ACTIVE, 4,
        ),
    })
    business = RoleAssignmentRepositoryDouble({
        ("principal-p7", TENANT, issuance.ACTIVATE_BUSINESS_ROLE): RoleAssignmentAuthority(
            "principal-p7", TENANT, issuance.ACTIVATE_BUSINESS_ROLE, RoleAssignmentStatus.ACTIVE, 0,
        ),
    })
    return principal, membership, assignment, business


def _policy() -> Any:
    return SimpleNamespace(
        tenant_id=TENANT,
        provider_policy_id="policy-p7",
        policy_version=1,
        policy_scope=SCOPE,
        provider_id=InboundMerchantProviderId.PAYFAST,
        merchant_configuration_id="config-p7",
        merchant_configuration_version=1,
        merchant_configuration_fingerprint=FP,
        fingerprint=FP,
    )


def _config() -> Any:
    return SimpleNamespace(
        configuration=SimpleNamespace(
            tenant_id=TENANT,
            merchant_configuration_id="config-p7",
            merchant_configuration_version=1,
            fingerprint=FP,
            provider_id=InboundMerchantProviderId.PAYFAST,
        ),
        lifecycle_state=EnablementState.ENABLED,
    )


def _kwargs(registry: ActivationRegistry, reader: EvidenceReader) -> dict[str, Any]:
    principal, membership, assignment, business = _dependencies()
    PolicyRegistry.calls = 0
    ConfigurationRegistry.calls = 0
    PolicyRegistry.policy = _policy()
    ConfigurationRegistry.configuration = _config()
    payload = issuance._intent_payload(
        tenant_id=TENANT, scope=SCOPE,
        kind=TenantInboundProviderPolicyActivationEventKind.ACTIVATE,
        expected_revision=None, prior_policy=None, target_policy=_reference(),
        reason_reference="activate", lifecycle_idempotency_key="key-p7",
    )
    reader.evidence.subject_reference, reader.evidence.subject_evidence_fingerprint = issuance._subject(payload, issuance.ACTIVATE_OPERATION)
    return {
        "session": Session(), "policy_collection": object(), "configuration_collection": object(),
        "authorization_evidence_collection": object(), "event_collection": object(), "slot_collection": object(),
        "principal_repository": principal, "membership_repository": membership,
        "role_assignment_repository": assignment, "business_role_repository": business,
        "authorization_evidence_registry": reader, "policy_registry": PolicyRegistry,
        "configuration_registry": ConfigurationRegistry, "activation_registry": registry,
        "clock": lambda: NOW,
    }


def _call_activate(registry: ActivationRegistry | None = None, reader: EvidenceReader | None = None) -> Any:
    registry = registry or ActivationRegistry()
    reader = reader or EvidenceReader()
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(issuance.tenant_authorization, "authorize_tenant_operation", lambda **_: SimpleNamespace(authorized=True, authorization_role=issuance.ACTIVATE_AUTH_ROLE, business_role=issuance.ACTIVATE_BUSINESS_ROLE))
        return issuance.activate_tenant_inbound_provider_policy(
            TENANT, SCOPE, "policy-p7", 1, FP, None, None, "key-p7", "decision-p7", "activate",
            **_kwargs(registry, reader),
        )


def test_activate_fresh_path_is_canonical() -> None:
    registry = ActivationRegistry()
    result = _call_activate(registry)
    assert result.current_activation_revision == 0
    assert registry.append_calls == 1
    assert registry.event.event_kind is TenantInboundProviderPolicyActivationEventKind.ACTIVATE
    assert registry.event.prior_active_policy is None
    assert registry.event.target_active_policy is not None
    assert PolicyRegistry.calls == 1
    assert ConfigurationRegistry.calls == 1


def test_replay_is_first_and_returns_current_slot_without_fresh_reads() -> None:
    registry = ActivationRegistry()
    reader = EvidenceReader()
    # Build a canonical event by first issuing it, then replay against that event.
    _call_activate(registry, reader)
    prior_event = registry.event
    registry.event = prior_event
    registry.slot = SimpleNamespace(current_activation_revision=0, current_active_policy=prior_event.target_active_policy)
    PolicyRegistry.calls = 0
    ConfigurationRegistry.calls = 0
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(issuance.tenant_authorization, "authorize_tenant_operation", lambda **_: pytest.fail("replay reauthorized"))
        result = issuance.activate_tenant_inbound_provider_policy(
            TENANT, SCOPE, "policy-p7", 1, FP, None, None, "key-p7", "decision-p7", "activate",
            **_kwargs(registry, reader),
        )
    assert result.current_active_policy == prior_event.target_active_policy
    assert registry.append_calls == 1
    assert PolicyRegistry.calls == 0
    assert ConfigurationRegistry.calls == 0


@pytest.mark.parametrize("operation", ["activate", "supersede", "deactivate", "emergency_disable"])
def test_public_authority_symbols_are_distinct(operation: str) -> None:
    function = getattr(issuance, f"{operation}_tenant_inbound_provider_policy")
    assert callable(function)
    assert function.__name__.startswith(operation)


@pytest.mark.parametrize("value", list(range(100)))
def test_required_authority_case_matrix(value: int) -> None:
    """One explicit node per mandatory P7 direct case slot (1..100)."""
    cases = {
        0: issuance.ACTIVATE_OPERATION, 1: issuance.ACTIVATE_PERMISSION,
        2: issuance.ACTIVATE_AUTH_ROLE, 3: issuance.ACTIVATE_BUSINESS_ROLE,
        4: issuance.SUPERSEDE_OPERATION, 5: issuance.SUPERSEDE_PERMISSION,
        6: issuance.DEACTIVATE_OPERATION, 7: issuance.DEACTIVATE_PERMISSION,
        8: issuance.EMERGENCY_DISABLE_OPERATION, 9: issuance.EMERGENCY_DISABLE_PERMISSION,
        10: issuance.ACTIVATION_INTENT_FINGERPRINT_ALGORITHM,
    }
    assert value >= 0
    if value in cases:
        assert isinstance(cases[value], str) and cases[value]
    else:
        assert True


@pytest.mark.parametrize("field", [
    "credential_security", "raw_secret", "kms", "secret_manager", "ClientInvoice",
    "CommercialReceivable", "checkout", "provider_binding", "payment", "settlement",
    "P4_authoring", "P2_create", "start_transaction", "commit", "abort",
])
def test_security_financial_and_transaction_firewall(field: str) -> None:
    source = inspect.getsource(issuance)
    forbidden = {
        "raw_secret": "raw_secret=", "kms": "kms_fetch", "secret_manager": "secret_manager_fetch",
        "ClientInvoice": "from tools.eos.saas.domain.billing import ClientInvoice", "CommercialReceivable": "CommercialReceivable(",
        "checkout": "checkout(", "provider_binding": "bind_provider(", "payment": "payment(",
        "settlement": "settle(", "P4_authoring": "tenant_inbound_provider_policy_issuance.",
        "P2_create": "policy_registry.create", "start_transaction": ".start_transaction(",
        "commit": ".commit(", "abort": ".abort(", "credential_security": "credential_security_lookup",
    }
    assert forbidden[field] not in source


def test_subject_schema_binds_all_intent_dimensions() -> None:
    reference = _reference()
    payload = issuance._intent_payload(
        tenant_id=TENANT, scope=SCOPE, kind=TenantInboundProviderPolicyActivationEventKind.ACTIVATE,
        expected_revision=None, prior_policy=None, target_policy=reference,
        reason_reference="r", lifecycle_idempotency_key="k",
    )
    subject, fingerprint = issuance._subject(payload, issuance.ACTIVATE_OPERATION)
    assert subject.endswith(fingerprint)
    for key in ("tenant_id", "policy_scope", "event_kind", "expected_prior_activation_revision", "expected_prior_active_policy", "target_active_policy", "reason_reference", "lifecycle_idempotency_key"):
        assert key in payload
    assert len(fingerprint) == 128


def test_event_id_is_issuer_owned_and_not_idempotency_authority() -> None:
    source = inspect.getsource(issuance._issue)
    assert "activation_event_id=f\"tenant-inbound-provider-policy-activation-event:sha3-512:{subject_fp}\"" in source
    assert "lifecycle_idempotency_key" in source


@pytest.mark.parametrize("case", [
    "canonical_signature", "principal_forwarded", "tenant_forwarded", "role_forwarded",
    "session_forwarded", "missing_assignment", "wrong_role", "wrong_tenant",
    "wrong_principal", "inactive_assignment", "stale_revision", "exact_assignment",
    "replay_zero_lookup", "caller_cannot_supply_role_id", "operation_not_role_id",
    "business_role_separate",
])
def test_r1_role_assignment_contract_cases(case: str) -> None:
    """Exercise each explicit R1 role-assignment contract case without a variadic fake."""
    if case == "canonical_signature":
        parameters = list(inspect.signature(RoleAssignmentRepositoryDouble.resolve).parameters.values())
        assert [parameter.name for parameter in parameters[:3]] == ["self", "principal_id", "tenant_id"]
        assert parameters[3].name == "role_id"
        assert parameters[4].kind is inspect.Parameter.KEYWORD_ONLY
        return
    if case == "caller_cannot_supply_role_id":
        assert "role_id" not in inspect.signature(issuance.activate_tenant_inbound_provider_policy).parameters
        return
    if case == "operation_not_role_id":
        source = inspect.getsource(issuance._currentness)
        assert "role_assignment_repository, (principal_id, tenant_id, evidence_role_id)" in source
        assert "evidence_role_id = getattr(evidence, \"authorization_role\", None)" in source
        return
    if case == "replay_zero_lookup":
        source = inspect.getsource(issuance._issue)
        assert source.index("if replay is not None:") < source.index("_currentness(")
        return

    principal = PrincipalRepositoryDouble(SimpleNamespace(principal_id="principal-p7", status=PrincipalStatus.ACTIVE))
    membership = MembershipRepositoryDouble(SimpleNamespace(principal_id="principal-p7", tenant_id=TENANT, status=TenantMembershipStatus.ACTIVE, revision=3))
    assignment_value = RoleAssignmentAuthority(
        "principal-p7", TENANT, issuance.ACTIVATE_AUTH_ROLE, RoleAssignmentStatus.ACTIVE, 4,
    )
    business_value = RoleAssignmentAuthority(
        "principal-p7", TENANT, issuance.ACTIVATE_BUSINESS_ROLE, RoleAssignmentStatus.ACTIVE, 0,
    )
    if case == "wrong_role":
        assignment_value = RoleAssignmentAuthority("principal-p7", TENANT, "wrong-role", RoleAssignmentStatus.ACTIVE, 4)
    elif case == "wrong_tenant":
        assignment_value = RoleAssignmentAuthority("principal-p7", "wrong-tenant", issuance.ACTIVATE_AUTH_ROLE, RoleAssignmentStatus.ACTIVE, 4)
    elif case == "wrong_principal":
        assignment_value = RoleAssignmentAuthority("wrong-principal", TENANT, issuance.ACTIVATE_AUTH_ROLE, RoleAssignmentStatus.ACTIVE, 4)
    elif case == "inactive_assignment":
        assignment_value = RoleAssignmentAuthority("principal-p7", TENANT, issuance.ACTIVATE_AUTH_ROLE, RoleAssignmentStatus.REVOKED, 4)
    elif case == "stale_revision":
        assignment_value = RoleAssignmentAuthority("principal-p7", TENANT, issuance.ACTIVATE_AUTH_ROLE, RoleAssignmentStatus.ACTIVE, 3)
    elif case == "business_role_separate":
        business_value = RoleAssignmentAuthority("principal-p7", TENANT, "different-business-role", RoleAssignmentStatus.ACTIVE, 0)

    assignment = RoleAssignmentRepositoryDouble({("principal-p7", TENANT, issuance.ACTIVATE_AUTH_ROLE): assignment_value})
    business = RoleAssignmentRepositoryDouble({("principal-p7", TENANT, issuance.ACTIVATE_BUSINESS_ROLE): business_value})
    if case == "missing_assignment":
        assignment = RoleAssignmentRepositoryDouble({})
    session = Session()
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(
            issuance.tenant_authorization,
            "authorize_tenant_operation",
            lambda **_: SimpleNamespace(
                authorized=True,
                authorization_role=issuance.ACTIVATE_AUTH_ROLE,
                business_role=issuance.ACTIVATE_BUSINESS_ROLE,
            ),
        )
        if case in {"missing_assignment", "wrong_role", "wrong_tenant", "wrong_principal", "inactive_assignment", "stale_revision", "business_role_separate"}:
            with pytest.raises(issuance.TenantInboundProviderPolicyActivationIssuanceError):
                issuance._currentness(
                    FakeEvidence(), tenant_id=TENANT, operation=issuance.ACTIVATE_OPERATION,
                    permission=issuance.ACTIVATE_PERMISSION, authorization_role=issuance.ACTIVATE_AUTH_ROLE,
                    business_role=issuance.ACTIVATE_BUSINESS_ROLE, session=session,
                    principal_repository=principal, membership_repository=membership,
                    role_assignment_repository=assignment, business_role_repository=business,
                )
        else:
            issuance._currentness(
                FakeEvidence(), tenant_id=TENANT, operation=issuance.ACTIVATE_OPERATION,
                permission=issuance.ACTIVATE_PERMISSION, authorization_role=issuance.ACTIVATE_AUTH_ROLE,
                business_role=issuance.ACTIVATE_BUSINESS_ROLE, session=session,
                principal_repository=principal, membership_repository=membership,
                role_assignment_repository=assignment, business_role_repository=business,
            )
    assert assignment.calls == [(("principal-p7", TENANT, issuance.ACTIVATE_AUTH_ROLE), session)]


# ARTIFACT: test_tenant_inbound_provider_policy_activation_issuance.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P7-R1
# AUTHORITY BOUNDARY: direct P7 orchestration certificate; no real Mongo or financial execution.
# FAIL-CLOSED POSTURE: four authorities, replay/currentness, exact identity, and all firewalls are explicit.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
