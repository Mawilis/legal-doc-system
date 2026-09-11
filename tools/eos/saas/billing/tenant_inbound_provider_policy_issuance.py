"""Wilsy OS tenant inbound provider-policy authoring issuance.

TITLE: Tenant Inbound Provider Policy Authorized Authoring Issuance
VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P4
AUTHORITY: Wilsy OS Core Governance; durable generic tenant authorization is
           the sole authoring authority and the P2 registry owns persistence.
EPITOME: Issue immutable tenant inbound provider-policy facts for initial
         creation and later revision without activation or provider execution.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/tenant_inbound_provider_policy_issuance.py
COLLABORATION / OWNERSHIP: SaaS provider-policy authoring owner; P1 domain,
                           P2 registry, and generic authorization remain
                           separate authorities.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3C-P4 establishes replay-first CREATE and
           REVISE issuance with durable authorization/currentness correlation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque references and fingerprints only; no raw
                             credential, KMS, secret-manager, or provider transport.
TENANT BOUNDARY: Every identity, evidence, currentness, and persistence call
                 is scoped to the supplied tenant and caller session.
AUTHORITY BOUNDARY: Immutable policy authoring only; no activation, binding,
                    credential eligibility, checkout, payment, or settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
TRANSACTION BOUNDARY: Caller owns session, transaction, commit, abort,
                      DuplicateKey recovery, and whole-transaction retry.
FAIL-CLOSED DECLARATION: Missing, stale, corrupt, divergent, cross-tenant, or
                          caller-asserted authority rejects before persistence.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, NoReturn, Protocol, cast

from pymongo.client_session import ClientSession

from tools.eos.auth import permission_namespace, roles, tenant_authorization, tenant_authority_policy
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.saas.domain.tenant_inbound_merchant_configuration import (
    InboundMerchantProviderId,
)
from tools.eos.saas.domain.tenant_inbound_provider_policy import (
    POLICY_FINGERPRINT_VERSION,
    TenantInboundProviderPolicy,
    TenantInboundProviderPolicyScope,
)
from tools.eos.saas.billing.tenant_inbound_provider_policy_registry import (
    TenantInboundProviderPolicyNotFoundError,
    TenantInboundProviderPolicyRegistry,
)


VERSION = "v1.0.0-M11-R8-R3B-P8-P3C-P4"
CAMPAIGN = "M11-R8-R3B-P8-P3C-P4"
CREATE_OPERATION = "tenant_inbound_provider_policy_create"
REVISE_OPERATION = "tenant_inbound_provider_policy_revise"
AUTHOR_PERMISSION = "inbound_provider_policy:author"
AUTHORIZATION_ROLE = "INBOUND_PROVIDER_POLICY_ADMIN"
BUSINESS_ROLE = "tenant_inbound_provider_policy_admin"
CREATE_SUBJECT_PREFIX = "tenant-inbound-provider-policy:create"
REVISE_SUBJECT_PREFIX = "tenant-inbound-provider-policy:revise"
AUTHORING_INTENT_SCHEMA = "WILSY-TENANT-INBOUND-PROVIDER-POLICY-AUTHORING-INTENT/V1"
AUTHORING_INTENT_FIELDS = (
    "tenant_id",
    "provider_policy_id",
    "policy_version",
    "policy_scope",
    "provider_id",
    "merchant_configuration_id",
    "merchant_configuration_version",
    "merchant_configuration_fingerprint",
    "policy_fingerprint_version",
)
_HEX = re.compile(r"^[0-9a-f]{128}$")


class TenantInboundProviderPolicyIssuanceError(RuntimeError):
    """Structured fail-closed error for policy authoring boundaries."""

    def __init__(self, code: str, message: str | None = None) -> None:
        self.code = code
        super().__init__(message or code)


def _fail(code: str, detail: object | None = None) -> NoReturn:
    """Raise a stable error without exposing persisted payloads or secrets."""
    suffix = f":{type(detail).__name__}" if detail is not None else ""
    raise TenantInboundProviderPolicyIssuanceError(f"{code}{suffix}")


def _text(name: str, value: object) -> str:
    """Require one exact non-blank identity component."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"INVALID_{name.upper()}")
    return value


def _version(name: str, value: object) -> int:
    """Require a positive, non-boolean integer version."""
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        _fail(f"INVALID_{name.upper()}")
    return value


def _fingerprint(name: str, value: object) -> str:
    """Require a lowercase SHA3-512 hexadecimal digest."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"INVALID_{name.upper()}")
    return value


def _provider(value: object) -> InboundMerchantProviderId:
    """Resolve the closed typed provider without normalizing unknown input."""
    if isinstance(value, InboundMerchantProviderId):
        return value
    if isinstance(value, str):
        try:
            return InboundMerchantProviderId(value)
        except ValueError:
            pass
    _fail("INVALID_PROVIDER_ID")


def _scope(value: object) -> TenantInboundProviderPolicyScope:
    """Resolve the closed typed policy scope."""
    if isinstance(value, TenantInboundProviderPolicyScope):
        return value
    if isinstance(value, str):
        try:
            return TenantInboundProviderPolicyScope(value)
        except ValueError:
            pass
    _fail("INVALID_POLICY_SCOPE")


def _active_session(session: ClientSession | None) -> ClientSession:
    """Require a caller-owned active transaction before any authority read."""
    if session is None or getattr(session, "in_transaction", False) is not True:
        _fail("ACTIVE_TRANSACTION_REQUIRED")
    return session


def _intent_payload(
    *,
    tenant_id: str,
    provider_policy_id: str,
    policy_version: int,
    policy_scope: TenantInboundProviderPolicyScope,
    provider_id: InboundMerchantProviderId,
    merchant_configuration_id: str,
    merchant_configuration_version: int,
    merchant_configuration_fingerprint: str,
    policy_fingerprint_version: str,
) -> dict[str, object]:
    """Build the pre-authorization intent, excluding issuer-owned provenance."""
    return {
        "schema": AUTHORING_INTENT_SCHEMA,
        "tenant_id": tenant_id,
        "provider_policy_id": provider_policy_id,
        "policy_version": policy_version,
        "policy_scope": policy_scope.value,
        "provider_id": provider_id.value,
        "merchant_configuration_id": merchant_configuration_id,
        "merchant_configuration_version": merchant_configuration_version,
        "merchant_configuration_fingerprint": merchant_configuration_fingerprint,
        "policy_fingerprint_version": policy_fingerprint_version,
    }


def _intent_fingerprint(**values: object) -> str:
    """Hash canonical UTF-8 JSON for one immutable authoring intent."""
    payload = _intent_payload(**cast(dict[str, Any], values))
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _subject(prefix: str, fingerprint: str) -> str:
    """Build the opaque generic-authorization subject reference."""
    _fingerprint("authoring_intent_fingerprint", fingerprint)
    return f"{prefix}:sha3-512:{fingerprint}"


class _RepositoryAdapter:
    """Adapt canonical repositories while retaining session-bound observations."""

    def __init__(self, repository: Any, collection: Any = None) -> None:
        self.repository = repository
        self.collection = collection
        self.observed: dict[tuple[object, ...], object] = {}

    def resolve(self, *args: object, session: Any = None) -> object:
        """Resolve through the existing repository API with exact session scope."""
        method = getattr(self.repository, "resolve", None)
        if not callable(method):
            method = getattr(self.repository, "get", None)
        if not callable(method):
            _fail("CURRENTNESS_REPOSITORY_API_INVALID")
        if self.collection is None:
            value = method(*args, session=session)
        else:
            value = method(*args, self.collection, session=session)
        self.observed[tuple(args)] = value
        return value


def _defaults(principal: Any, membership: Any, assignment: Any, business: Any) -> tuple[Any, Any, Any, Any]:
    """Load canonical currentness repositories lazily after replay precedence."""
    if principal is None:
        from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository

        principal = PrincipalAuthorityRepository
    if membership is None:
        from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository

        membership = TenantMembershipRepository
    if assignment is None:
        from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository

        assignment = RoleAssignmentRepository
    if business is None:
        business = assignment
    return principal, membership, assignment, business


def _evidence_registry(
    supplied: Any,
    collection: Any,
    principal: Any,
    membership: Any,
    assignment: Any,
    business: Any,
) -> Any:
    """Use an injected evidence reader or the canonical durable read registry."""
    if supplied is not None:
        return supplied
    if collection is None:
        _fail("AUTHORIZATION_EVIDENCE_COLLECTION_REQUIRED")
    return TenantAuthorizationDecisionEvidenceRegistry(
        collection,
        principal_repository=principal,
        membership_repository=membership,
        role_assignment_repository=assignment,
        business_role_repository=business,
    )


def _read_evidence(registry: Any, tenant_id: str, decision_id: str, session: ClientSession) -> Any:
    """Read strict durable authorization evidence; caller evidence is never trusted."""
    getter = getattr(registry, "get", None)
    if not callable(getter):
        _fail("AUTHORIZATION_EVIDENCE_REGISTRY_API_INVALID")
    try:
        return getter(tenant_id=tenant_id, authorization_decision_id=decision_id, session=session)
    except Exception as error:
        _fail("AUTHORIZATION_EVIDENCE_NOT_FOUND_OR_INVALID", error)


def _correlate_evidence(
    evidence: Any,
    *,
    tenant_id: str,
    authorization_decision_id: str,
    subject_reference: str,
    subject_fingerprint: str,
    operation: str,
) -> str:
    """Require exact tenant, operation, permission, subject, and decision identity."""
    if (
        getattr(evidence, "tenant_id", None) != tenant_id
        or getattr(evidence, "authorization_decision_id", None) != authorization_decision_id
        or getattr(evidence, "operation", None) != operation
        or getattr(evidence, "permission", None) != AUTHOR_PERMISSION
        or getattr(evidence, "subject_reference", None) != subject_reference
        or getattr(evidence, "subject_evidence_fingerprint", None) != subject_fingerprint
    ):
        _fail("GENERIC_AUTHORIZATION_EVIDENCE_CORRELATION_INVALID")
    return _fingerprint(
        "authorization_evidence_fingerprint",
        getattr(evidence, "authorization_evidence_fingerprint", None),
    )


def _authorization_reference(evidence: Any) -> str:
    """Derive the immutable policy reference from durable evidence only."""
    reference = getattr(evidence, "authorization_evidence_reference", None)
    if not isinstance(reference, str) or not reference:
        decision_id = getattr(evidence, "authorization_decision_id", None)
        reference = f"tenant-authorization-decision:{decision_id}"
    return _text("authoring_authorization_reference", reference)


def _currentness(
    *,
    evidence: Any,
    tenant_id: str,
    principal: _RepositoryAdapter,
    membership: _RepositoryAdapter,
    assignment: _RepositoryAdapter,
    business: _RepositoryAdapter,
    session: ClientSession,
    operation: str,
) -> None:
    """Reprove every current authorization conjunct and persisted revision."""
    principal_id = getattr(evidence, "principal_id", None)
    if not isinstance(principal_id, str) or not principal_id.strip():
        _fail("AUTHORIZATION_PRINCIPAL_INVALID")
    try:
        decision = tenant_authorization.authorize_tenant_operation(
            principal_id=principal_id,
            tenant_id=tenant_id,
            permission_id=AUTHOR_PERMISSION,
            operation=operation,
            principal_repository=principal,
            membership_repository=membership,
            role_assignment_repository=assignment,
            business_role_repository=business,
            session=session,
        )
    except Exception as error:
        _fail("CURRENT_PRIVILEGE_READ_FAILED", error)
    if not decision.authorized:
        _fail("CURRENT_PRIVILEGE_REQUIRED")
    if decision.business_role != getattr(evidence, "business_role", None) or decision.authorization_role != getattr(evidence, "authorization_role", None):
        _fail("CURRENT_AUTHORIZATION_ROLE_CORRELATION_INVALID")
    if decision.business_role != BUSINESS_ROLE or decision.authorization_role != AUTHORIZATION_ROLE:
        _fail("AUTHORING_AUTHORITY_ROLE_INVALID")
    current_principal = principal.observed.get((principal_id,))
    if getattr(current_principal, "status", None) not in (PrincipalStatus.ACTIVE, PrincipalStatus.ACTIVE.value):
        _fail("CURRENT_PRINCIPAL_INACTIVE")
    current_membership = membership.observed.get((principal_id, tenant_id))
    if getattr(getattr(current_membership, "status", None), "value", getattr(current_membership, "status", None)) != TenantMembershipStatus.ACTIVE.value:
        _fail("CURRENT_MEMBERSHIP_INACTIVE")
    if getattr(current_membership, "revision", None) != getattr(evidence, "membership_revision", None):
        _fail("MEMBERSHIP_REVISION_MISMATCH")
    current_assignment = assignment.observed.get((principal_id, tenant_id, AUTHORIZATION_ROLE))
    if getattr(getattr(current_assignment, "status", None), "value", getattr(current_assignment, "status", None)) != RoleAssignmentStatus.ACTIVE.value:
        _fail("CURRENT_ROLE_ASSIGNMENT_INACTIVE")
    if getattr(current_assignment, "revision", None) != getattr(evidence, "role_assignment_revision", None):
        _fail("ROLE_ASSIGNMENT_REVISION_MISMATCH")
    current_business = business.observed.get((principal_id, tenant_id, BUSINESS_ROLE))
    if current_business is None:
        _fail("CURRENT_BUSINESS_ROLE_UNAVAILABLE")
    if tenant_authority_policy.tenant_role_operation_eligibility(BUSINESS_ROLE, operation) != tenant_authority_policy.ELIGIBLE:
        _fail("BUSINESS_ROLE_INELIGIBLE")
    if (
        getattr(evidence, "permission_namespace_version", None) != permission_namespace.VERSION
        or getattr(evidence, "authorization_role_policy_version", None) != roles.VERSION
        or getattr(evidence, "tenant_business_role_policy_version", None) != tenant_authority_policy.VERSION
        or getattr(evidence, "tenant_authorization_composition_version", None) != tenant_authorization.VERSION
    ):
        _fail("AUTHORIZATION_POLICY_VERSION_MISMATCH")


def _trusted_instant(clock: Callable[[], datetime] | None) -> datetime:
    """Capture one aware UTC issuance instant on a fresh path only."""
    value = datetime.now(timezone.utc) if clock is None else clock()
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail("TRUSTED_CLOCK_INVALID")
    return value.astimezone(timezone.utc)


def _existing(
    registry: Any,
    tenant_id: str,
    provider_policy_id: str,
    policy_version: int,
    collection: Any,
    session: ClientSession,
) -> TenantInboundProviderPolicy | None:
    """Perform the exact P2 identity read used to establish replay precedence."""
    try:
        value = registry.get(tenant_id, provider_policy_id, policy_version, collection, session=session)
    except TenantInboundProviderPolicyNotFoundError:
        return None
    except Exception as error:
        if getattr(error, "code", None) == "M11R8_PROVIDER_POLICY_NOT_FOUND":
            return None
        raise
    if value is None:
        return None
    if not isinstance(value, TenantInboundProviderPolicy):
        _fail("PERSISTED_POLICY_INVALID")
    return value


def _replay_or_none(
    existing: TenantInboundProviderPolicy,
    *,
    tenant_id: str,
    provider_policy_id: str,
    policy_version: int,
    policy_scope: TenantInboundProviderPolicyScope,
    provider_id: InboundMerchantProviderId,
    merchant_configuration_id: str,
    merchant_configuration_version: int,
    merchant_configuration_fingerprint: str,
    policy_fingerprint_version: str,
    authorization_decision_id: str,
    operation: str,
    evidence_registry: Any,
    session: ClientSession,
) -> TenantInboundProviderPolicy:
    """Validate historical replay integrity without currentness, clock, or writes."""
    intent = _intent_fingerprint(
        tenant_id=tenant_id,
        provider_policy_id=provider_policy_id,
        policy_version=policy_version,
        policy_scope=policy_scope,
        provider_id=provider_id,
        merchant_configuration_id=merchant_configuration_id,
        merchant_configuration_version=merchant_configuration_version,
        merchant_configuration_fingerprint=merchant_configuration_fingerprint,
        policy_fingerprint_version=policy_fingerprint_version,
    )
    subject = _subject(CREATE_SUBJECT_PREFIX if operation == CREATE_OPERATION else REVISE_SUBJECT_PREFIX, intent)
    evidence = _read_evidence(evidence_registry, tenant_id, authorization_decision_id, session)
    evidence_fingerprint = _correlate_evidence(
        evidence,
        tenant_id=tenant_id,
        authorization_decision_id=authorization_decision_id,
        subject_reference=subject,
        subject_fingerprint=intent,
        operation=operation,
    )
    expected_reference = _authorization_reference(evidence)
    if (
        existing.tenant_id != tenant_id
        or existing.provider_policy_id != provider_policy_id
        or existing.policy_version != policy_version
        or existing.policy_scope is not policy_scope
        or existing.provider_id is not provider_id
        or existing.merchant_configuration_id != merchant_configuration_id
        or existing.merchant_configuration_version != merchant_configuration_version
        or existing.merchant_configuration_fingerprint != merchant_configuration_fingerprint
        or existing.policy_fingerprint_version != policy_fingerprint_version
        or existing.authoring_authorization_reference != expected_reference
        or existing.authoring_authorization_evidence_fingerprint != evidence_fingerprint
    ):
        _fail("DIVERGENT_PROVIDER_POLICY_REPLAY")
    if not existing.verify_fingerprint():
        _fail("PERSISTED_POLICY_INVALID")
    return existing


def _issue(
    *,
    tenant_id: str,
    provider_policy_id: str,
    policy_version: int,
    policy_scope: TenantInboundProviderPolicyScope | str,
    provider_id: InboundMerchantProviderId | str,
    merchant_configuration_id: str,
    merchant_configuration_version: int,
    merchant_configuration_fingerprint: str,
    authorization_decision_id: str,
    operation: str,
    subject_prefix: str,
    session: ClientSession,
    collection: Any,
    authorization_evidence_collection: Any,
    principal_repository: Any,
    membership_repository: Any,
    role_assignment_repository: Any,
    business_role_repository: Any,
    principal_collection: Any,
    membership_collection: Any,
    role_assignment_collection: Any,
    business_role_collection: Any,
    authorization_evidence_registry: Any,
    policy_registry: Any,
    clock: Callable[[], datetime] | None,
    policy_fingerprint_version: str,
    revision: bool,
) -> TenantInboundProviderPolicy:
    """Shared CREATE/REVISE implementation; callers own all transaction control."""
    tenant = _text("tenant_id", tenant_id)
    policy_id = _text("provider_policy_id", provider_policy_id)
    version = _version("policy_version", policy_version)
    scope = _scope(policy_scope)
    provider = _provider(provider_id)
    configuration_id = _text("merchant_configuration_id", merchant_configuration_id)
    configuration_version = _version("merchant_configuration_version", merchant_configuration_version)
    configuration_fingerprint = _fingerprint("merchant_configuration_fingerprint", merchant_configuration_fingerprint)
    decision_id = _text("authorization_decision_id", authorization_decision_id)
    if policy_fingerprint_version != POLICY_FINGERPRINT_VERSION:
        _fail("INVALID_POLICY_FINGERPRINT_VERSION")
    tx = _active_session(session)
    if collection is None:
        _fail("POLICY_COLLECTION_REQUIRED")
    registry = policy_registry

    # Replay identity is the first authority read.  Dependencies are loaded only
    # after this lookup misses, preserving exact historical replay semantics.
    existing = _existing(registry, tenant, policy_id, version, collection, tx)
    if existing is not None:
        evidence_reader = _evidence_registry(
            authorization_evidence_registry,
            authorization_evidence_collection,
            object(),
            None,
            None,
            None,
        )
        if revision and version <= 1:
            _fail("REVISION_VERSION_MUST_EXCEED_ONE")
        if not revision and version != 1:
            _fail("CREATE_VERSION_MUST_EQUAL_ONE")
        return _replay_or_none(
            existing,
            tenant_id=tenant,
            provider_policy_id=policy_id,
            policy_version=version,
            policy_scope=scope,
            provider_id=provider,
            merchant_configuration_id=configuration_id,
            merchant_configuration_version=configuration_version,
            merchant_configuration_fingerprint=configuration_fingerprint,
            policy_fingerprint_version=policy_fingerprint_version,
            authorization_decision_id=decision_id,
            operation=operation,
            evidence_registry=evidence_reader,
            session=tx,
        )

    if revision:
        if version <= 1:
            _fail("REVISION_VERSION_MUST_EXCEED_ONE")
        predecessor = registry.get_predecessor_policy(
            tenant,
            policy_id,
            version,
            collection,
            session=tx,
        )
        if predecessor is None:
            _fail("PREDECESSOR_REQUIRED")
    else:
        if version != 1:
            _fail("CREATE_VERSION_MUST_EQUAL_ONE")

    principal_repository, membership_repository, role_assignment_repository, business_role_repository = _defaults(
        principal_repository,
        membership_repository,
        role_assignment_repository,
        business_role_repository,
    )
    intent = _intent_fingerprint(
        tenant_id=tenant,
        provider_policy_id=policy_id,
        policy_version=version,
        policy_scope=scope,
        provider_id=provider,
        merchant_configuration_id=configuration_id,
        merchant_configuration_version=configuration_version,
        merchant_configuration_fingerprint=configuration_fingerprint,
        policy_fingerprint_version=policy_fingerprint_version,
    )
    subject = _subject(subject_prefix, intent)
    evidence_reader = _evidence_registry(
        authorization_evidence_registry,
        authorization_evidence_collection,
        principal_repository,
        membership_repository,
        role_assignment_repository,
        business_role_repository,
    )
    evidence = _read_evidence(evidence_reader, tenant, decision_id, tx)
    evidence_fingerprint = _correlate_evidence(
        evidence,
        tenant_id=tenant,
        authorization_decision_id=decision_id,
        subject_reference=subject,
        subject_fingerprint=intent,
        operation=operation,
    )
    _currentness(
        evidence=evidence,
        tenant_id=tenant,
        principal=_RepositoryAdapter(principal_repository, principal_collection),
        membership=_RepositoryAdapter(membership_repository, membership_collection),
        assignment=_RepositoryAdapter(role_assignment_repository, role_assignment_collection),
        business=_RepositoryAdapter(business_role_repository, business_role_collection),
        session=tx,
        operation=operation,
    )
    created_at = _trusted_instant(clock)
    policy = TenantInboundProviderPolicy(
        tenant_id=tenant,
        provider_policy_id=policy_id,
        policy_version=version,
        policy_scope=scope,
        provider_id=provider,
        merchant_configuration_id=configuration_id,
        merchant_configuration_version=configuration_version,
        merchant_configuration_fingerprint=configuration_fingerprint,
        authoring_authorization_reference=_authorization_reference(evidence),
        authoring_authorization_evidence_fingerprint=evidence_fingerprint,
        created_at=created_at,
        policy_fingerprint_version=policy_fingerprint_version,
    )
    return registry.create(policy, collection, session=tx)


def issue_tenant_inbound_provider_policy(
    tenant_id: str,
    provider_policy_id: str,
    policy_version: int,
    policy_scope: TenantInboundProviderPolicyScope | str,
    provider_id: InboundMerchantProviderId | str,
    merchant_configuration_id: str,
    merchant_configuration_version: int,
    merchant_configuration_fingerprint: str,
    authorization_decision_id: str,
    *,
    session: ClientSession,
    collection: Any,
    authorization_evidence_collection: Any = None,
    principal_repository: Any = None,
    membership_repository: Any = None,
    role_assignment_repository: Any = None,
    business_role_repository: Any = None,
    principal_collection: Any = None,
    membership_collection: Any = None,
    role_assignment_collection: Any = None,
    business_role_collection: Any = None,
    authorization_evidence_registry: Any = None,
    policy_registry: Any = TenantInboundProviderPolicyRegistry,
    clock: Callable[[], datetime] | None = None,
    policy_fingerprint_version: str = POLICY_FINGERPRINT_VERSION,
) -> TenantInboundProviderPolicy:
    """Create policy version one from matching durable current authorization."""
    return _issue(
        tenant_id=tenant_id,
        provider_policy_id=provider_policy_id,
        policy_version=policy_version,
        policy_scope=policy_scope,
        provider_id=provider_id,
        merchant_configuration_id=merchant_configuration_id,
        merchant_configuration_version=merchant_configuration_version,
        merchant_configuration_fingerprint=merchant_configuration_fingerprint,
        authorization_decision_id=authorization_decision_id,
        operation=CREATE_OPERATION,
        subject_prefix=CREATE_SUBJECT_PREFIX,
        session=session,
        collection=collection,
        authorization_evidence_collection=authorization_evidence_collection,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        role_assignment_repository=role_assignment_repository,
        business_role_repository=business_role_repository,
        principal_collection=principal_collection,
        membership_collection=membership_collection,
        role_assignment_collection=role_assignment_collection,
        business_role_collection=business_role_collection,
        authorization_evidence_registry=authorization_evidence_registry,
        policy_registry=policy_registry,
        clock=clock,
        policy_fingerprint_version=policy_fingerprint_version,
        revision=False,
    )


def revise_tenant_inbound_provider_policy(
    tenant_id: str,
    provider_policy_id: str,
    policy_version: int,
    policy_scope: TenantInboundProviderPolicyScope | str,
    provider_id: InboundMerchantProviderId | str,
    merchant_configuration_id: str,
    merchant_configuration_version: int,
    merchant_configuration_fingerprint: str,
    authorization_decision_id: str,
    *,
    session: ClientSession,
    collection: Any,
    authorization_evidence_collection: Any = None,
    principal_repository: Any = None,
    membership_repository: Any = None,
    role_assignment_repository: Any = None,
    business_role_repository: Any = None,
    principal_collection: Any = None,
    membership_collection: Any = None,
    role_assignment_collection: Any = None,
    business_role_collection: Any = None,
    authorization_evidence_registry: Any = None,
    policy_registry: Any = TenantInboundProviderPolicyRegistry,
    clock: Callable[[], datetime] | None = None,
    policy_fingerprint_version: str = POLICY_FINGERPRINT_VERSION,
) -> TenantInboundProviderPolicy:
    """Create an immutable revision above one existing lower policy version."""
    return _issue(
        tenant_id=tenant_id,
        provider_policy_id=provider_policy_id,
        policy_version=policy_version,
        policy_scope=policy_scope,
        provider_id=provider_id,
        merchant_configuration_id=merchant_configuration_id,
        merchant_configuration_version=merchant_configuration_version,
        merchant_configuration_fingerprint=merchant_configuration_fingerprint,
        authorization_decision_id=authorization_decision_id,
        operation=REVISE_OPERATION,
        subject_prefix=REVISE_SUBJECT_PREFIX,
        session=session,
        collection=collection,
        authorization_evidence_collection=authorization_evidence_collection,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        role_assignment_repository=role_assignment_repository,
        business_role_repository=business_role_repository,
        principal_collection=principal_collection,
        membership_collection=membership_collection,
        role_assignment_collection=role_assignment_collection,
        business_role_collection=business_role_collection,
        authorization_evidence_registry=authorization_evidence_registry,
        policy_registry=policy_registry,
        clock=clock,
        policy_fingerprint_version=policy_fingerprint_version,
        revision=True,
    )


__all__ = [
    "VERSION",
    "CAMPAIGN",
    "CREATE_OPERATION",
    "REVISE_OPERATION",
    "AUTHOR_PERMISSION",
    "AUTHORIZATION_ROLE",
    "BUSINESS_ROLE",
    "AUTHORING_INTENT_SCHEMA",
    "AUTHORING_INTENT_FIELDS",
    "TenantInboundProviderPolicyIssuanceError",
    "issue_tenant_inbound_provider_policy",
    "revise_tenant_inbound_provider_policy",
]


# ARTIFACT: tenant_inbound_provider_policy_issuance.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P4
# AUTHORITY BOUNDARY: immutable policy CREATE/REVISE authoring only; no activation or binding.
# TENANT POSTURE: exact tenant-scoped identity, authorization, currentness, and persistence.
# FAIL-CLOSED POSTURE: replay, predecessor, provenance, currentness, and transaction invariants reject closed.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
