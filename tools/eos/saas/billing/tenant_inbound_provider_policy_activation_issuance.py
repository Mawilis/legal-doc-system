"""WILSY OS tenant inbound provider-policy activation orchestration.

TITLE: Tenant Inbound Provider Policy Activation Issuance
VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P7-R1
AUTHORITY: Wilsy OS Core Governance; P2/P4/P5/P6 and generic authorization
           remain the canonical upstream authorities.
EPITOME: Compose four explicit provider-policy activation lifecycle authorities
         while preserving replay, currentness, configuration, and CAS boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/tenant_inbound_provider_policy_activation_issuance.py
COLLABORATION / OWNERSHIP: P7 orchestration owner; P2 policy registry, P4 policy
                           authoring, P5 facts, P6 persistence, and auth evidence
                           remain separate owners.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3C-P7-R1 repairs the canonical three-part
           role-assignment currentness lookup and preserves replay-first,
           exact policy/configuration identity, fresh authorization currentness,
           trusted timestamps, and caller-owned transactions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No raw credentials, KMS, secret-manager, binding, or
                             checkout access; administrative activation is Model A.
TENANT BOUNDARY: Every lookup and correlation requires tenant_id and policy scope.
AUTHORITY BOUNDARY: Administrative policy activation only; no credential or
                    financial execution authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
TRANSACTION BOUNDARY: Caller supplies the active session and owns commit, abort,
                      and whole-transaction retry semantics.
FAIL-CLOSED DECLARATION: Missing, stale, divergent, corrupt, or cross-tenant
                          authority rejects before event construction or mutation.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, NoReturn

from pymongo.client_session import ClientSession

from tools.eos.auth import permission_namespace, roles, tenant_authorization, tenant_authority_policy
from tools.eos.auth.tenant_authorization import AssignmentReader
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_authorization_decision_evidence_registry import TenantAuthorizationDecisionEvidenceRegistry
from tools.eos.saas.domain.tenant_inbound_provider_policy import TenantInboundProviderPolicyScope
from tools.eos.saas.domain.tenant_inbound_provider_policy_activation import (
    TenantInboundProviderPolicyActivationEvent,
    TenantInboundProviderPolicyActivationEventKind,
    TenantInboundProviderPolicyReference,
)
from tools.eos.saas.billing.tenant_inbound_provider_policy_activation_registry import (
    ActivationRegistry,
    TenantInboundProviderPolicyActivationRegistry,
)
from tools.eos.saas.billing.tenant_inbound_provider_policy_registry import TenantInboundProviderPolicyRegistry
from tools.eos.saas.billing.tenant_inbound_merchant_configuration_registry import (
    EnablementState,
    TenantInboundMerchantConfigurationRegistry,
)


VERSION = "v1.0.0-M11-R8-R3B-P8-P3C-P7-R1"
CAMPAIGN = "M11-R8-R3B-P8-P3C-P7-R1"
ACTIVATE_OPERATION = "tenant_inbound_provider_policy_activate"
ACTIVATE_PERMISSION = "inbound_provider_policy:activate"
ACTIVATE_AUTH_ROLE = "INBOUND_PROVIDER_POLICY_ACTIVATION_ADMIN"
ACTIVATE_BUSINESS_ROLE = "tenant_inbound_provider_policy_activation_admin"
SUPERSEDE_OPERATION = ACTIVATE_OPERATION
SUPERSEDE_PERMISSION = ACTIVATE_PERMISSION
SUPERSEDE_AUTH_ROLE = ACTIVATE_AUTH_ROLE
SUPERSEDE_BUSINESS_ROLE = ACTIVATE_BUSINESS_ROLE
DEACTIVATE_OPERATION = "tenant_inbound_provider_policy_deactivate"
DEACTIVATE_PERMISSION = "inbound_provider_policy:deactivate"
DEACTIVATE_AUTH_ROLE = ACTIVATE_AUTH_ROLE
DEACTIVATE_BUSINESS_ROLE = ACTIVATE_BUSINESS_ROLE
EMERGENCY_DISABLE_OPERATION = "tenant_inbound_provider_policy_emergency_disable"
EMERGENCY_DISABLE_PERMISSION = "inbound_provider_policy:emergency_disable"
EMERGENCY_DISABLE_AUTH_ROLE = "INBOUND_PROVIDER_SECURITY_ADMIN"
EMERGENCY_DISABLE_BUSINESS_ROLE = "tenant_inbound_provider_security_admin"
ACTIVATION_INTENT_FINGERPRINT_SCHEMA = "WILSY-TENANT-INBOUND-PROVIDER-POLICY-ACTIVATION-INTENT/V1"
ACTIVATION_INTENT_FINGERPRINT_ALGORITHM = "SHA3-512"
_HEX = re.compile(r"^[0-9a-f]{128}$")


class TenantInboundProviderPolicyActivationIssuanceError(RuntimeError):
    """Structured fail-closed orchestration error."""

    def __init__(self, code: str, detail: object | None = None) -> None:
        self.code = code
        suffix = f":{type(detail).__name__}" if detail is not None else ""
        super().__init__(f"{code}{suffix}")


def _fail(code: str, detail: object | None = None) -> NoReturn:
    """Raise an opaque structured error without exposing persisted payloads."""
    raise TenantInboundProviderPolicyActivationIssuanceError(code, detail)


def _text(name: str, value: object) -> str:
    """Require a non-empty, whitespace-stable identity."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"INVALID_{name.upper()}")
    return value


def _version(value: object, name: str) -> int:
    """Require one positive non-boolean version."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        _fail(f"INVALID_{name.upper()}")
    return value


def _revision(value: object) -> int | None:
    """Validate an optional caller-observed slot revision."""
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _fail("INVALID_EXPECTED_PRIOR_ACTIVATION_REVISION")
    return value


def _fingerprint(name: str, value: object) -> str:
    """Require a lowercase SHA3-512 fingerprint."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"INVALID_{name.upper()}")
    return value


def _scope(value: object) -> TenantInboundProviderPolicyScope:
    """Require the currently supported inbound-collection scope."""
    if not isinstance(value, TenantInboundProviderPolicyScope) or value is not TenantInboundProviderPolicyScope.INBOUND_COLLECTION:
        _fail("INVALID_POLICY_SCOPE")
    return value


def _active_transaction(session: Any) -> Any:
    """Require caller-owned transaction before any authority read."""
    if session is None or getattr(session, "in_transaction", False) is not True:
        _fail("ACTIVE_TRANSACTION_REQUIRED")
    return session


def _policy_reference(policy: Any) -> TenantInboundProviderPolicyReference:
    """Snapshot exact immutable policy/configuration identity into P5 shape."""
    try:
        return TenantInboundProviderPolicyReference(
            provider_policy_id=policy.provider_policy_id,
            policy_version=policy.policy_version,
            policy_fingerprint=policy.fingerprint,
            provider_id=policy.provider_id,
            merchant_configuration_id=policy.merchant_configuration_id,
            merchant_configuration_version=policy.merchant_configuration_version,
            merchant_configuration_fingerprint=policy.merchant_configuration_fingerprint,
        )
    except (AttributeError, TypeError, ValueError) as error:
        _fail("TARGET_POLICY_INVALID", error)


def _intent_payload(
    *, tenant_id: str, scope: TenantInboundProviderPolicyScope,
    kind: TenantInboundProviderPolicyActivationEventKind,
    expected_revision: int | None,
    prior_policy: TenantInboundProviderPolicyReference | None,
    target_policy: TenantInboundProviderPolicyReference | None,
    reason_reference: str, lifecycle_idempotency_key: str,
) -> dict[str, object]:
    """Build the versioned, deterministic subject-intent payload."""
    return {
        "schema": ACTIVATION_INTENT_FINGERPRINT_SCHEMA,
        "tenant_id": tenant_id,
        "policy_scope": scope.value,
        "event_kind": kind.value,
        "expected_prior_activation_revision": expected_revision,
        "expected_prior_active_policy": None if prior_policy is None else prior_policy.to_dict(),
        "target_active_policy": None if target_policy is None else target_policy.to_dict(),
        "reason_reference": reason_reference,
        "lifecycle_idempotency_key": lifecycle_idempotency_key,
    }


def _subject(payload: Mapping[str, object], operation: str) -> tuple[str, str]:
    """Return opaque subject reference and its SHA3-512 fingerprint."""
    raw = json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha3_512(raw).hexdigest()
    return f"tenant-inbound-provider-policy-activation:{operation}:sha3-512:{digest}", digest


def _evidence_reader(registry: Any, collection: Any, repositories: tuple[Any, ...]) -> Any:
    """Resolve an injected evidence reader without creating persistence authority."""
    if registry is not None:
        return registry
    if collection is None:
        _fail("AUTHORIZATION_EVIDENCE_COLLECTION_REQUIRED")
    principal, membership, assignment, business = repositories
    return TenantAuthorizationDecisionEvidenceRegistry(
        collection,
        principal_repository=principal,
        membership_repository=membership,
        role_assignment_repository=assignment,
        business_role_repository=business,
    )


def _read_evidence(reader: Any, tenant_id: str, decision_id: str, session: Any) -> Any:
    """Read strict durable evidence; caller assertions are never trusted."""
    getter = getattr(reader, "get", None)
    if not callable(getter):
        _fail("AUTHORIZATION_EVIDENCE_REGISTRY_API_INVALID")
    try:
        return getter(tenant_id=tenant_id, authorization_decision_id=decision_id, session=session)
    except Exception as error:
        _fail("AUTHORIZATION_EVIDENCE_NOT_FOUND_OR_INVALID", error)


def _currentness(
    evidence: Any, *, tenant_id: str, operation: str, permission: str,
    authorization_role: str, business_role: str, session: Any,
    principal_repository: Any, membership_repository: Any,
    role_assignment_repository: AssignmentReader, business_role_repository: AssignmentReader,
) -> None:
    """Reprove current principal, membership, role, policy, and composition."""
    principal_id = getattr(evidence, "principal_id", None)
    if not isinstance(principal_id, str) or not principal_id.strip():
        _fail("AUTHORIZATION_PRINCIPAL_INVALID")
    evidence_role_id = getattr(evidence, "authorization_role", None)
    evidence_business_role = getattr(evidence, "business_role", None)
    if (
        not isinstance(evidence_role_id, str)
        or not isinstance(evidence_business_role, str)
        or evidence_role_id != authorization_role
        or evidence_business_role != business_role
    ):
        _fail("CURRENT_AUTHORIZATION_ROLE_CORRELATION_INVALID")
    try:
        decision = tenant_authorization.authorize_tenant_operation(
            principal_id=principal_id, tenant_id=tenant_id, permission_id=permission,
            operation=operation, principal_repository=principal_repository,
            membership_repository=membership_repository, role_assignment_repository=role_assignment_repository,
            business_role_repository=business_role_repository, session=session,
        )
    except Exception as error:
        _fail("CURRENT_PRIVILEGE_READ_FAILED", error)
    if not getattr(decision, "authorized", False):
        _fail("CURRENT_PRIVILEGE_REQUIRED")
    if getattr(decision, "authorization_role", None) != authorization_role or getattr(decision, "business_role", None) != business_role:
        _fail("CURRENT_AUTHORIZATION_ROLE_CORRELATION_INVALID")
    if tenant_authority_policy.tenant_role_operation_eligibility(business_role, operation) != tenant_authority_policy.ELIGIBLE:
        _fail("BUSINESS_ROLE_INELIGIBLE")
    principal = _resolve(principal_repository, (principal_id,), session)
    membership = _resolve(membership_repository, (principal_id, tenant_id), session)
    assignment = _resolve(role_assignment_repository, (principal_id, tenant_id, evidence_role_id), session)
    business = _resolve(business_role_repository, (principal_id, tenant_id, evidence_business_role), session)
    if _value(getattr(principal, "status", None)) != PrincipalStatus.ACTIVE.value:
        _fail("CURRENT_PRINCIPAL_INACTIVE")
    if _value(getattr(membership, "status", None)) != TenantMembershipStatus.ACTIVE.value:
        _fail("CURRENT_MEMBERSHIP_INACTIVE")
    if getattr(membership, "revision", None) != getattr(evidence, "membership_revision", None):
        _fail("MEMBERSHIP_REVISION_MISMATCH")
    if _value(getattr(assignment, "status", None)) != RoleAssignmentStatus.ACTIVE.value:
        _fail("CURRENT_ROLE_ASSIGNMENT_INACTIVE")
    if getattr(assignment, "revision", None) != getattr(evidence, "role_assignment_revision", None):
        _fail("ROLE_ASSIGNMENT_REVISION_MISMATCH")
    _require_role_assignment_identity(
        assignment,
        principal_id=principal_id,
        tenant_id=tenant_id,
        role_id=evidence_role_id,
        mismatch_code="CURRENT_ROLE_ASSIGNMENT_IDENTITY_MISMATCH",
    )
    if business is None:
        _fail("CURRENT_BUSINESS_ROLE_UNAVAILABLE")
    _require_role_assignment_identity(
        business,
        principal_id=principal_id,
        tenant_id=tenant_id,
        role_id=evidence_business_role,
        mismatch_code="CURRENT_BUSINESS_ROLE_MISMATCH",
    )
    if (
        getattr(evidence, "permission_namespace_version", None) != permission_namespace.VERSION
        or getattr(evidence, "authorization_role_policy_version", None) != roles.VERSION
        or getattr(evidence, "tenant_business_role_policy_version", None) != tenant_authority_policy.VERSION
        or getattr(evidence, "tenant_authorization_composition_version", None) != tenant_authorization.VERSION
    ):
        _fail("AUTHORIZATION_POLICY_VERSION_MISMATCH")


def _value(value: object) -> object:
    """Read enum values without normalizing business identifiers."""
    return getattr(value, "value", value)


def _require_role_assignment_identity(
    value: Any, *, principal_id: str, tenant_id: str, role_id: str, mismatch_code: str,
) -> None:
    """Require the resolved authority to match the exact canonical natural key."""
    if (
        getattr(value, "principal_id", None) != principal_id
        or getattr(value, "tenant_id", None) != tenant_id
        or getattr(value, "role_id", None) != role_id
    ):
        _fail(mismatch_code)


def _resolve(repository: Any, key: tuple[str, ...], session: Any) -> Any:
    """Resolve a current authority using repository-native signatures."""
    resolver = getattr(repository, "resolve", None)
    if not callable(resolver):
        _fail("CURRENT_AUTHORITY_REPOSITORY_API_INVALID")
    try:
        if len(key) == 1:
            return resolver(key[0], session=session)
        if len(key) == 2:
            return resolver(key[0], key[1], session=session)
        return resolver(key[0], key[1], key[2], session=session)
    except Exception as error:
        _fail("CURRENT_AUTHORITY_UNAVAILABLE", error)


def _correlate(evidence: Any, *, tenant_id: str, decision_id: str, operation: str,
               permission: str, subject_reference: str, subject_fingerprint: str) -> str:
    """Require exact durable authorization correlation and return its fingerprint."""
    if (
        getattr(evidence, "tenant_id", None) != tenant_id
        or getattr(evidence, "authorization_decision_id", None) != decision_id
        or getattr(evidence, "operation", None) != operation
        or getattr(evidence, "permission", None) != permission
        or getattr(evidence, "subject_reference", None) != subject_reference
        or getattr(evidence, "subject_evidence_fingerprint", None) != subject_fingerprint
    ):
        _fail("GENERIC_AUTHORIZATION_EVIDENCE_CORRELATION_INVALID")
    return _fingerprint("authorization_evidence_fingerprint", getattr(evidence, "authorization_evidence_fingerprint", None))


def _event_matches(event: Any, *, tenant_id: str, scope: TenantInboundProviderPolicyScope,
                   kind: TenantInboundProviderPolicyActivationEventKind,
                   expected_revision: int | None, prior: TenantInboundProviderPolicyReference | None,
                   target: TenantInboundProviderPolicyReference | None, reason: str,
                   key: str, auth_reference: str, auth_fingerprint: str) -> bool:
    """Compare every replay-bearing intent field without rewriting durable state."""
    return (
        event.tenant_id == tenant_id and event.policy_scope is scope and event.event_kind is kind
        and event.activation_revision == (0 if expected_revision is None else expected_revision + 1)
        and event.prior_active_policy == prior and event.target_active_policy == target
        and event.reason_reference == reason and event.lifecycle_idempotency_key == key
        and event.authorization_reference == auth_reference
        and event.authorization_evidence_fingerprint == auth_fingerprint
    )


def _issue(
    *, tenant_id: str, policy_scope: TenantInboundProviderPolicyScope,
    provider_policy_id: str, policy_version: int, target_policy_fingerprint: str | None,
    expected_prior_activation_revision: int | None,
    expected_prior_active_policy: TenantInboundProviderPolicyReference | None,
    lifecycle_idempotency_key: str, authorization_decision_id: str, reason_reference: str,
    event_kind: TenantInboundProviderPolicyActivationEventKind,
    operation: str, permission: str, authorization_role: str, business_role: str,
    session: ClientSession, policy_collection: Any, configuration_collection: Any,
    authorization_evidence_collection: Any, event_collection: Any, slot_collection: Any,
    principal_repository: Any, membership_repository: Any, role_assignment_repository: Any,
    business_role_repository: Any, authorization_evidence_registry: Any,
    policy_registry: Any, configuration_registry: Any, activation_registry: Any,
    clock: Callable[[], datetime] | None,
) -> Any:
    """Shared replay-first implementation for the four public authorities."""
    tenant = _text("tenant_id", tenant_id)
    scope = _scope(policy_scope)
    policy_id = _text("provider_policy_id", provider_policy_id)
    version = _version(policy_version, "policy_version")
    expected_revision = _revision(expected_prior_activation_revision)
    key = _text("lifecycle_idempotency_key", lifecycle_idempotency_key)
    decision_id = _text("authorization_decision_id", authorization_decision_id)
    reason = _text("reason_reference", reason_reference)
    if event_kind in (TenantInboundProviderPolicyActivationEventKind.ACTIVATE, TenantInboundProviderPolicyActivationEventKind.SUPERSEDE):
        if target_policy_fingerprint is None:
            _fail("TARGET_POLICY_FINGERPRINT_REQUIRED")
        target_fp = _fingerprint("target_policy_fingerprint", target_policy_fingerprint)
    else:
        target_fp = None
    tx = _active_transaction(session)
    if event_collection is None or slot_collection is None:
        _fail("REQUIRED_COLLECTION_MISSING")
    replay = activation_registry.get_event_by_idempotency_key(tenant, scope, key, event_collection, session=tx)
    if replay is not None:
        replay_target = replay.target_active_policy
        payload = _intent_payload(tenant_id=tenant, scope=scope, kind=event_kind, expected_revision=expected_revision, prior_policy=expected_prior_active_policy, target_policy=replay_target, reason_reference=reason, lifecycle_idempotency_key=key)
        reader = _evidence_reader(authorization_evidence_registry, authorization_evidence_collection, (principal_repository, membership_repository, role_assignment_repository, business_role_repository))
        evidence = _read_evidence(reader, tenant, decision_id, tx)
        auth_ref = getattr(evidence, "authorization_evidence_reference", f"tenant-authorization-decision:{decision_id}")
        subject_ref, subject_fp = _subject(payload, operation)
        auth_fp = _correlate(evidence, tenant_id=tenant, decision_id=decision_id, operation=operation, permission=permission, subject_reference=subject_ref, subject_fingerprint=subject_fp)
        target = replay_target
        if target_fp is not None and (target is None or target.policy_fingerprint != target_fp):
            _fail("DIVERGENT_ACTIVATION_REPLAY")
        if not _event_matches(replay, tenant_id=tenant, scope=scope, kind=event_kind, expected_revision=expected_revision, prior=expected_prior_active_policy, target=target, reason=reason, key=key, auth_reference=auth_ref, auth_fingerprint=auth_fp):
            _fail("DIVERGENT_ACTIVATION_REPLAY")
        current = activation_registry.get_current_slot(tenant, scope, slot_collection, event_collection, session=tx)
        if current is None:
            _fail("CURRENT_SLOT_UNAVAILABLE")
        return current
    current = activation_registry.get_current_slot(tenant, scope, slot_collection, event_collection, session=tx)
    if event_kind is TenantInboundProviderPolicyActivationEventKind.ACTIVATE:
        if current is not None and current.current_active_policy is not None:
            _fail("ACTIVATE_POLICY_ALREADY_ACTIVE")
        if current is None and expected_revision is not None:
            _fail("ACTIVATE_INITIAL_REVISION_MUST_BE_NONE")
        if current is not None and (expected_revision != current.current_activation_revision or expected_prior_active_policy is not None or current.current_active_policy is not None):
            _fail("ACTIVATE_EMPTY_SLOT_EXPECTATION_INVALID")
    else:
        if current is None or current.current_active_policy is None:
            _fail("ACTIVE_POLICY_REQUIRED")
        if expected_revision != current.current_activation_revision or expected_prior_active_policy != current.current_active_policy:
            _fail("EXPECTED_PRIOR_SLOT_MISMATCH")
        if event_kind is TenantInboundProviderPolicyActivationEventKind.SUPERSEDE and target_policy_fingerprint == current.current_active_policy.policy_fingerprint:
            _fail("SUPERSEDE_TARGET_MUST_DIFFER")
    target_policy = None
    if target_fp is not None:
        if policy_collection is None or configuration_collection is None:
            _fail("REQUIRED_COLLECTION_MISSING")
        policy = policy_registry.get(tenant, policy_id, version, policy_collection, session=tx)
        target_policy = _policy_reference(policy)
        if target_policy.policy_fingerprint != target_fp:
            _fail("TARGET_POLICY_FINGERPRINT_MISMATCH")
        if getattr(policy, "tenant_id", None) != tenant or getattr(policy, "policy_scope", None) is not scope:
            _fail("TARGET_POLICY_IDENTITY_MISMATCH")
        config = configuration_registry.get(tenant, target_policy.merchant_configuration_id, target_policy.merchant_configuration_version, configuration_collection, session=tx)
        if config is None or config.configuration.tenant_id != tenant or config.configuration.merchant_configuration_id != target_policy.merchant_configuration_id or config.configuration.merchant_configuration_version != target_policy.merchant_configuration_version or config.configuration.fingerprint != target_policy.merchant_configuration_fingerprint or config.configuration.provider_id is not target_policy.provider_id:
            _fail("REFERENCED_CONFIGURATION_IDENTITY_MISMATCH")
        if config.lifecycle_state is not EnablementState.ENABLED:
            _fail("REFERENCED_CONFIGURATION_NOT_ENABLED")
    reader = _evidence_reader(authorization_evidence_registry, authorization_evidence_collection, (principal_repository, membership_repository, role_assignment_repository, business_role_repository))
    payload = _intent_payload(tenant_id=tenant, scope=scope, kind=event_kind, expected_revision=expected_revision, prior_policy=expected_prior_active_policy, target_policy=target_policy, reason_reference=reason, lifecycle_idempotency_key=key)
    subject_ref, subject_fp = _subject(payload, operation)
    evidence = _read_evidence(reader, tenant, decision_id, tx)
    auth_fp = _correlate(evidence, tenant_id=tenant, decision_id=decision_id, operation=operation, permission=permission, subject_reference=subject_ref, subject_fingerprint=subject_fp)
    _currentness(evidence, tenant_id=tenant, operation=operation, permission=permission, authorization_role=authorization_role, business_role=business_role, session=tx, principal_repository=principal_repository, membership_repository=membership_repository, role_assignment_repository=role_assignment_repository, business_role_repository=business_role_repository)
    instant = datetime.now(timezone.utc) if clock is None else clock()
    if not isinstance(instant, datetime) or instant.tzinfo is None or instant.utcoffset() is None:
        _fail("TRUSTED_CLOCK_INVALID")
    instant = instant.astimezone(timezone.utc)
    revision = 0 if current is None else current.current_activation_revision + 1
    auth_ref = getattr(evidence, "authorization_evidence_reference", f"tenant-authorization-decision:{decision_id}")
    event = TenantInboundProviderPolicyActivationEvent(
        tenant_id=tenant, policy_scope=scope,
        activation_event_id=f"tenant-inbound-provider-policy-activation-event:sha3-512:{subject_fp}",
        activation_revision=revision, event_kind=event_kind,
        lifecycle_idempotency_key=key,
        prior_active_policy=None if current is None else current.current_active_policy,
        target_active_policy=target_policy,
        authorization_reference=auth_ref,
        authorization_evidence_fingerprint=auth_fp,
        reason_reference=reason, occurred_at=instant,
    )
    return activation_registry.append_event_and_advance_slot(event, None if current is None else current.current_activation_revision, None if current is None else current.current_active_policy, event_collection=event_collection, slot_collection=slot_collection, session=tx)


def activate_tenant_inbound_provider_policy(
    tenant_id: str, policy_scope: TenantInboundProviderPolicyScope, provider_policy_id: str,
    policy_version: int, target_policy_fingerprint: str, expected_prior_activation_revision: int | None,
    expected_prior_active_policy: TenantInboundProviderPolicyReference | None,
    lifecycle_idempotency_key: str, authorization_decision_id: str, reason_reference: str,
    *, session: ClientSession, policy_collection: Any, configuration_collection: Any,
    authorization_evidence_collection: Any, event_collection: Any, slot_collection: Any,
    principal_repository: Any, membership_repository: Any, role_assignment_repository: Any,
    business_role_repository: Any, authorization_evidence_registry: Any = None,
    policy_registry: Any = TenantInboundProviderPolicyRegistry,
    configuration_registry: Any = TenantInboundMerchantConfigurationRegistry,
    activation_registry: Any = ActivationRegistry, clock: Callable[[], datetime] | None = None,
) -> Any:
    """Activate an exact enabled policy from no-slot or empty-slot state."""
    return _issue(tenant_id=tenant_id, policy_scope=policy_scope, provider_policy_id=provider_policy_id, policy_version=policy_version, target_policy_fingerprint=target_policy_fingerprint, expected_prior_activation_revision=expected_prior_activation_revision, expected_prior_active_policy=expected_prior_active_policy, lifecycle_idempotency_key=lifecycle_idempotency_key, authorization_decision_id=authorization_decision_id, reason_reference=reason_reference, event_kind=TenantInboundProviderPolicyActivationEventKind.ACTIVATE, operation=ACTIVATE_OPERATION, permission=ACTIVATE_PERMISSION, authorization_role=ACTIVATE_AUTH_ROLE, business_role=ACTIVATE_BUSINESS_ROLE, session=session, policy_collection=policy_collection, configuration_collection=configuration_collection, authorization_evidence_collection=authorization_evidence_collection, event_collection=event_collection, slot_collection=slot_collection, principal_repository=principal_repository, membership_repository=membership_repository, role_assignment_repository=role_assignment_repository, business_role_repository=business_role_repository, authorization_evidence_registry=authorization_evidence_registry, policy_registry=policy_registry, configuration_registry=configuration_registry, activation_registry=activation_registry, clock=clock)


def supersede_tenant_inbound_provider_policy(
    tenant_id: str, policy_scope: TenantInboundProviderPolicyScope, provider_policy_id: str,
    policy_version: int, target_policy_fingerprint: str, expected_prior_activation_revision: int,
    expected_prior_active_policy: TenantInboundProviderPolicyReference,
    lifecycle_idempotency_key: str, authorization_decision_id: str, reason_reference: str,
    *, session: ClientSession, policy_collection: Any, configuration_collection: Any,
    authorization_evidence_collection: Any, event_collection: Any, slot_collection: Any,
    principal_repository: Any, membership_repository: Any, role_assignment_repository: Any,
    business_role_repository: Any, authorization_evidence_registry: Any = None,
    policy_registry: Any = TenantInboundProviderPolicyRegistry,
    configuration_registry: Any = TenantInboundMerchantConfigurationRegistry,
    activation_registry: Any = ActivationRegistry, clock: Callable[[], datetime] | None = None,
) -> Any:
    """Supersede an active exact policy with a different exact enabled policy."""
    return _issue(tenant_id=tenant_id, policy_scope=policy_scope, provider_policy_id=provider_policy_id, policy_version=policy_version, target_policy_fingerprint=target_policy_fingerprint, expected_prior_activation_revision=expected_prior_activation_revision, expected_prior_active_policy=expected_prior_active_policy, lifecycle_idempotency_key=lifecycle_idempotency_key, authorization_decision_id=authorization_decision_id, reason_reference=reason_reference, event_kind=TenantInboundProviderPolicyActivationEventKind.SUPERSEDE, operation=SUPERSEDE_OPERATION, permission=SUPERSEDE_PERMISSION, authorization_role=SUPERSEDE_AUTH_ROLE, business_role=SUPERSEDE_BUSINESS_ROLE, session=session, policy_collection=policy_collection, configuration_collection=configuration_collection, authorization_evidence_collection=authorization_evidence_collection, event_collection=event_collection, slot_collection=slot_collection, principal_repository=principal_repository, membership_repository=membership_repository, role_assignment_repository=role_assignment_repository, business_role_repository=business_role_repository, authorization_evidence_registry=authorization_evidence_registry, policy_registry=policy_registry, configuration_registry=configuration_registry, activation_registry=activation_registry, clock=clock)


def deactivate_tenant_inbound_provider_policy(
    tenant_id: str, policy_scope: TenantInboundProviderPolicyScope, provider_policy_id: str,
    policy_version: int, expected_prior_activation_revision: int,
    expected_prior_active_policy: TenantInboundProviderPolicyReference,
    lifecycle_idempotency_key: str, authorization_decision_id: str, reason_reference: str,
    *, session: ClientSession, policy_collection: Any, configuration_collection: Any,
    authorization_evidence_collection: Any, event_collection: Any, slot_collection: Any,
    principal_repository: Any, membership_repository: Any, role_assignment_repository: Any,
    business_role_repository: Any, authorization_evidence_registry: Any = None,
    policy_registry: Any = TenantInboundProviderPolicyRegistry,
    configuration_registry: Any = TenantInboundMerchantConfigurationRegistry,
    activation_registry: Any = ActivationRegistry, clock: Callable[[], datetime] | None = None,
) -> Any:
    """Deactivate the currently active policy without rereading configuration."""
    return _issue(tenant_id=tenant_id, policy_scope=policy_scope, provider_policy_id=provider_policy_id, policy_version=policy_version, target_policy_fingerprint=None, expected_prior_activation_revision=expected_prior_activation_revision, expected_prior_active_policy=expected_prior_active_policy, lifecycle_idempotency_key=lifecycle_idempotency_key, authorization_decision_id=authorization_decision_id, reason_reference=reason_reference, event_kind=TenantInboundProviderPolicyActivationEventKind.DEACTIVATE, operation=DEACTIVATE_OPERATION, permission=DEACTIVATE_PERMISSION, authorization_role=DEACTIVATE_AUTH_ROLE, business_role=DEACTIVATE_BUSINESS_ROLE, session=session, policy_collection=policy_collection, configuration_collection=configuration_collection, authorization_evidence_collection=authorization_evidence_collection, event_collection=event_collection, slot_collection=slot_collection, principal_repository=principal_repository, membership_repository=membership_repository, role_assignment_repository=role_assignment_repository, business_role_repository=business_role_repository, authorization_evidence_registry=authorization_evidence_registry, policy_registry=policy_registry, configuration_registry=configuration_registry, activation_registry=activation_registry, clock=clock)


def emergency_disable_tenant_inbound_provider_policy(
    tenant_id: str, policy_scope: TenantInboundProviderPolicyScope, provider_policy_id: str,
    policy_version: int, expected_prior_activation_revision: int,
    expected_prior_active_policy: TenantInboundProviderPolicyReference,
    lifecycle_idempotency_key: str, authorization_decision_id: str, reason_reference: str,
    *, session: ClientSession, policy_collection: Any, configuration_collection: Any,
    authorization_evidence_collection: Any, event_collection: Any, slot_collection: Any,
    principal_repository: Any, membership_repository: Any, role_assignment_repository: Any,
    business_role_repository: Any, authorization_evidence_registry: Any = None,
    policy_registry: Any = TenantInboundProviderPolicyRegistry,
    configuration_registry: Any = TenantInboundMerchantConfigurationRegistry,
    activation_registry: Any = ActivationRegistry, clock: Callable[[], datetime] | None = None,
) -> Any:
    """Emergency-disable the active policy under the distinct security authority."""
    return _issue(tenant_id=tenant_id, policy_scope=policy_scope, provider_policy_id=provider_policy_id, policy_version=policy_version, target_policy_fingerprint=None, expected_prior_activation_revision=expected_prior_activation_revision, expected_prior_active_policy=expected_prior_active_policy, lifecycle_idempotency_key=lifecycle_idempotency_key, authorization_decision_id=authorization_decision_id, reason_reference=reason_reference, event_kind=TenantInboundProviderPolicyActivationEventKind.EMERGENCY_DISABLE, operation=EMERGENCY_DISABLE_OPERATION, permission=EMERGENCY_DISABLE_PERMISSION, authorization_role=EMERGENCY_DISABLE_AUTH_ROLE, business_role=EMERGENCY_DISABLE_BUSINESS_ROLE, session=session, policy_collection=policy_collection, configuration_collection=configuration_collection, authorization_evidence_collection=authorization_evidence_collection, event_collection=event_collection, slot_collection=slot_collection, principal_repository=principal_repository, membership_repository=membership_repository, role_assignment_repository=role_assignment_repository, business_role_repository=business_role_repository, authorization_evidence_registry=authorization_evidence_registry, policy_registry=policy_registry, configuration_registry=configuration_registry, activation_registry=activation_registry, clock=clock)


__all__ = [
    "ACTIVATE_AUTH_ROLE", "ACTIVATE_BUSINESS_ROLE", "ACTIVATE_OPERATION", "ACTIVATE_PERMISSION",
    "ACTIVATION_INTENT_FINGERPRINT_ALGORITHM", "ACTIVATION_INTENT_FINGERPRINT_SCHEMA", "CAMPAIGN",
    "DEACTIVATE_AUTH_ROLE", "DEACTIVATE_BUSINESS_ROLE", "DEACTIVATE_OPERATION", "DEACTIVATE_PERMISSION",
    "EMERGENCY_DISABLE_AUTH_ROLE", "EMERGENCY_DISABLE_BUSINESS_ROLE", "EMERGENCY_DISABLE_OPERATION", "EMERGENCY_DISABLE_PERMISSION",
    "SUPERSEDE_AUTH_ROLE", "SUPERSEDE_BUSINESS_ROLE", "SUPERSEDE_OPERATION", "SUPERSEDE_PERMISSION",
    "TenantInboundProviderPolicyActivationIssuanceError", "VERSION",
    "activate_tenant_inbound_provider_policy", "supersede_tenant_inbound_provider_policy",
    "deactivate_tenant_inbound_provider_policy", "emergency_disable_tenant_inbound_provider_policy",
]


# ARTIFACT: tenant_inbound_provider_policy_activation_issuance.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P7-R1
# AUTHORITY BOUNDARY: administrative provider-policy activation orchestration only.
# TENANT POSTURE: exact tenant/scope replay, policy, configuration, and authorization correlation.
# FAIL-CLOSED POSTURE: replay-first, currentness, one-clock, immutable-event, and P6 CAS handoff.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
