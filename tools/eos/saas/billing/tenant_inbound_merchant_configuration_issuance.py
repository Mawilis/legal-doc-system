"""Wilsy OS authorized tenant inbound merchant-configuration lifecycle orchestration.

TITLE: Tenant Inbound Merchant Configuration Issuance
VERSION: v1.1.0-M11-R8-R3B-P8-P3B-I2-I1-AUTHORIZED-MERCHANT-CONFIGURATION-LIFECYCLE
AUTHORITY: Wilsy OS Core Governance; generic tenant authorization remains the
           authority source and the P8-P2 registry remains the persistence owner.
EPITOME: Compose registration and caller-authorized lifecycle, compromise, and
         remediation transitions with strict replay and CAS semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/tenant_inbound_merchant_configuration_issuance.py
COLLABORATION / OWNERSHIP: SaaS registration orchestration owner; auth evidence,
                           P8-P2 domain, and P8-P2 registry remain separate owners.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.1.0-M11-R8-R3B-P8-P3B-I2-I1-AUTHORIZED-MERCHANT-CONFIGURATION-LIFECYCLE adds ordinary lifecycle, compromise, and remediation orchestration; registration semantics remain frozen.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque identifiers, stable secret references, and
                            non-secret options only; no raw credentials or KMS.
TENANT BOUNDARY: Every configuration and authorization-evidence lookup binds
                 the caller tenant and uses the caller session.
AUTHORITY BOUNDARY: Registration and administrative lifecycle composition only;
                    no generic authorization issuance, provider policy, binding, or checkout.
FINANCIAL AUTHORITY BOUNDARY: No payment, execution, settlement, invoice, or
                              receivable authority; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller supplies an active session and owns commit, abort,
                      DuplicateKey recovery, and whole-transaction retry.
FAIL-CLOSED DECLARATION: Missing, divergent, stale, corrupt, cross-tenant,
                          legacy, or unavailable authority rejects without inference.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, NoReturn, cast

from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from tools.eos.auth import permission_namespace, roles, tenant_authorization, tenant_authority_policy
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.tenant_business_role_authority import BusinessRoleResolution
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.saas.domain.tenant_inbound_merchant_configuration import (
    InboundMerchantProviderId,
    TenantInboundMerchantConfiguration,
)
from tools.eos.saas.billing.tenant_inbound_merchant_configuration_registry import (
    EnablementState,
    TenantInboundMerchantConfigurationRecord,
    TenantInboundMerchantConfigurationRegistry,
)


VERSION = "v1.1.0-M11-R8-R3B-P8-P3B-I2-I1-AUTHORIZED-MERCHANT-CONFIGURATION-LIFECYCLE"
CAMPAIGN = "M11-R8-R3B-P8-P3B-I2-I1"
REGISTER_OPERATION = "tenant_inbound_merchant_configuration_register"
REGISTER_PERMISSION = "inbound_merchant_configuration:register"
REGISTER_AUTHORIZATION_ROLE = "INBOUND_MERCHANT_CONFIGURATION_ADMIN"
REGISTER_BUSINESS_ROLE = "tenant_inbound_merchant_configuration_admin"
REGISTER_SUBJECT_PREFIX = "tenant-inbound-merchant-configuration:register"
REGISTER_INTENT_FIELDS = (
    "tenant_id",
    "provider_id",
    "merchant_account_id",
    "merchant_configuration_id",
    "merchant_configuration_version",
    "non_secret_provider_options",
    "credential_secret_reference",
    "register_idempotency_key",
)
_HEX = re.compile(r"^[0-9a-f]{128}$")
_SECRET_KEY = re.compile(
    r"(?:secret|password|passphrase|token|credential|api[_-]?key|private[_-]?key)",
    re.IGNORECASE,
)
_OPTION_KEYS = frozenset({"mode", "merchant_name", "return_url", "cancel_url", "notify_url", "currency"})


class TenantInboundMerchantConfigurationIssuanceError(RuntimeError):
    """Structured fail-closed error for registration composition boundaries."""

    def __init__(self, code: str, message: str | None = None) -> None:
        self.code = code
        super().__init__(message or code)


def _fail(code: str, detail: object | None = None) -> NoReturn:
    """Raise a stable error without exposing secrets or persisted payloads."""
    suffix = f":{type(detail).__name__}" if detail is not None else ""
    raise TenantInboundMerchantConfigurationIssuanceError(f"{code}{suffix}")


def _text(name: str, value: object) -> str:
    """Require one non-empty, whitespace-stable request identity."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"INVALID_{name.upper()}")
    return value


def _provider(value: object) -> InboundMerchantProviderId:
    """Accept only the frozen typed provider enum; never normalize arbitrary strings."""
    if isinstance(value, InboundMerchantProviderId):
        return value
    if isinstance(value, str):
        try:
            return InboundMerchantProviderId(value)
        except ValueError as error:
            _ = error
    _fail("INVALID_PROVIDER_ID")


def _version(value: object) -> int:
    """Require the caller-selected positive configuration revision."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        _fail("INVALID_MERCHANT_CONFIGURATION_VERSION")
    return value


def _options(value: object) -> dict[str, str]:
    """Canonicalize flat non-secret options without accepting secret-shaped data."""
    if not isinstance(value, Mapping):
        _fail("INVALID_NON_SECRET_PROVIDER_OPTIONS")
    result: dict[str, str] = {}
    for key, raw in value.items():
        if (
            not isinstance(key, str)
            or not key
            or key != key.strip()
            or key not in _OPTION_KEYS
            or _SECRET_KEY.search(key)
            or not isinstance(raw, str)
            or not raw
            or raw != raw.strip()
        ):
            _fail("RAW_SECRET_OR_INVALID_PROVIDER_OPTION")
        result[key] = raw
    return result


def _active_session(session: ClientSession | None) -> ClientSession:
    """Require the caller-owned active transaction before any authority read."""
    if session is None or getattr(session, "in_transaction", False) is not True:
        _fail("ACTIVE_TRANSACTION_REQUIRED")
    return session


def _intent_payload(
    *,
    tenant_id: str,
    provider_id: InboundMerchantProviderId,
    merchant_account_id: str,
    merchant_configuration_id: str,
    merchant_configuration_version: int,
    non_secret_provider_options: Mapping[str, str],
    credential_secret_reference: str,
    register_idempotency_key: str,
) -> dict[str, object]:
    """Return the exact immutable registration intent envelope.

    This payload deliberately excludes created_at, the generated configuration
    fingerprint, lifecycle state, raw secrets, and current secret versions.
    """
    return {
        "tenant_id": tenant_id,
        "provider_id": provider_id.value,
        "merchant_account_id": merchant_account_id,
        "merchant_configuration_id": merchant_configuration_id,
        "merchant_configuration_version": merchant_configuration_version,
        "non_secret_provider_options": dict(non_secret_provider_options),
        "credential_secret_reference": credential_secret_reference,
        "register_idempotency_key": register_idempotency_key,
    }


def canonical_registration_intent_fingerprint(
    *,
    tenant_id: str,
    provider_id: InboundMerchantProviderId,
    merchant_account_id: str,
    merchant_configuration_id: str,
    merchant_configuration_version: int,
    non_secret_provider_options: Mapping[str, str],
    credential_secret_reference: str,
    register_idempotency_key: str,
) -> str:
    """Hash the canonical registration intent using the generic subject-evidence law."""
    encoded = json.dumps(
        _intent_payload(
            tenant_id=tenant_id,
            provider_id=provider_id,
            merchant_account_id=merchant_account_id,
            merchant_configuration_id=merchant_configuration_id,
            merchant_configuration_version=merchant_configuration_version,
            non_secret_provider_options=non_secret_provider_options,
            credential_secret_reference=credential_secret_reference,
            register_idempotency_key=register_idempotency_key,
        ),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def registration_subject_reference(intent_fingerprint: str) -> str:
    """Build an opaque subject reference; the generic engine never parses it."""
    if not isinstance(intent_fingerprint, str) or _HEX.fullmatch(intent_fingerprint) is None:
        _fail("INVALID_REGISTRATION_INTENT_FINGERPRINT")
    return f"{REGISTER_SUBJECT_PREFIX}:sha3-512:{intent_fingerprint}"


def _enum_value(value: object) -> object:
    """Read an enum value without weakening status validation."""
    return getattr(value, "value", value)


def _fingerprint(name: str, value: object) -> str:
    """Require an existing lowercase SHA3-512 evidence fingerprint."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"INVALID_{name.upper()}")
    return value


class _RepositoryAdapter:
    """Adapt canonical resolve/get repositories while recording session-bound reads."""

    def __init__(self, repository: Any, collection: Any = None) -> None:
        self.repository = repository
        self.collection = collection
        self.observed: dict[tuple[object, ...], object] = {}

    def resolve(self, *args: object, session: Any = None) -> object:
        """Resolve through the existing repository API and preserve the exact session."""
        method = getattr(self.repository, "resolve", None)
        if method is None:
            method = getattr(self.repository, "get", None)
        if not callable(method):
            _fail("CURRENTNESS_REPOSITORY_API_INVALID")
        if self.collection is None:
            value = method(*args, session=session)
        else:
            value = method(*args, self.collection, session=session)
        self.observed[tuple(args)] = value
        return value


def _default_dependencies(
    principal_repository: Any,
    membership_repository: Any,
    role_assignment_repository: Any,
    business_role_repository: Any,
) -> tuple[Any, Any, Any, Any]:
    """Load canonical repositories lazily after replay precedence has been decided."""
    if principal_repository is None:
        from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository

        principal_repository = PrincipalAuthorityRepository
    if membership_repository is None:
        from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository

        membership_repository = TenantMembershipRepository
    if role_assignment_repository is None:
        from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository

        role_assignment_repository = RoleAssignmentRepository
    if business_role_repository is None:
        business_role_repository = role_assignment_repository
    return principal_repository, membership_repository, role_assignment_repository, business_role_repository


def _evidence_registry(
    registry: Any,
    collection: Collection,
    principal_repository: Any,
    membership_repository: Any,
    role_assignment_repository: Any,
    business_role_repository: Any,
) -> Any:
    """Resolve an injected evidence reader or construct the canonical read registry."""
    if registry is not None:
        return registry
    return TenantAuthorizationDecisionEvidenceRegistry(
        collection,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        role_assignment_repository=role_assignment_repository,
        business_role_repository=business_role_repository,
    )


def _read_evidence(
    registry: Any,
    tenant_id: str,
    authorization_decision_id: str,
    session: ClientSession,
) -> Any:
    """Read one strict durable evidence record; never accept a caller evidence object."""
    getter = getattr(registry, "get", None)
    if not callable(getter):
        _fail("AUTHORIZATION_EVIDENCE_REGISTRY_API_INVALID")
    try:
        return getter(tenant_id=tenant_id, authorization_decision_id=authorization_decision_id, session=session)
    except Exception as error:
        _fail("AUTHORIZATION_EVIDENCE_NOT_FOUND_OR_INVALID", error)


def _currentness(
    *,
    evidence: Any,
    tenant_id: str,
    principal_adapter: _RepositoryAdapter,
    membership_adapter: _RepositoryAdapter,
    role_adapter: _RepositoryAdapter,
    business_adapter: _RepositoryAdapter,
    session: ClientSession,
    operation: str = REGISTER_OPERATION,
    permission: str = REGISTER_PERMISSION,
    authorization_role: str = REGISTER_AUTHORIZATION_ROLE,
    business_role: str = REGISTER_BUSINESS_ROLE,
) -> None:
    """Prove fresh current privilege and every evidence revision on the same session."""
    principal_id = getattr(evidence, "principal_id", None)
    if not isinstance(principal_id, str) or not principal_id.strip():
        _fail("AUTHORIZATION_PRINCIPAL_INVALID")
    try:
        decision = tenant_authorization.authorize_tenant_operation(
            principal_id=principal_id,
            tenant_id=tenant_id,
            permission_id=permission,
            operation=operation,
            principal_repository=principal_adapter,
            membership_repository=membership_adapter,
            role_assignment_repository=role_adapter,
            business_role_repository=business_adapter,
            session=session,
        )
    except TenantInboundMerchantConfigurationIssuanceError:
        raise
    except Exception as error:
        _fail("CURRENT_PRIVILEGE_READ_FAILED", error)
    if not decision.authorized:
        _fail("CURRENT_PRIVILEGE_REQUIRED")
    if decision.business_role != getattr(evidence, "business_role", None) or decision.authorization_role != getattr(evidence, "authorization_role", None):
        _fail("CURRENT_AUTHORIZATION_ROLE_CORRELATION_INVALID")
    if decision.business_role != business_role or decision.authorization_role != authorization_role:
        _fail("REGISTER_AUTHORITY_ROLE_INVALID")
    if getattr(principal_adapter.observed.get((principal_id,)), "status", None) not in (PrincipalStatus.ACTIVE, PrincipalStatus.ACTIVE.value):
        _fail("CURRENT_PRINCIPAL_INACTIVE")
    membership = membership_adapter.observed.get((principal_id, tenant_id))
    if _enum_value(getattr(membership, "status", None)) != TenantMembershipStatus.ACTIVE.value:
        _fail("CURRENT_MEMBERSHIP_INACTIVE")
    if getattr(membership, "revision", None) != getattr(evidence, "membership_revision", None):
        _fail("MEMBERSHIP_REVISION_MISMATCH")
    assignment = role_adapter.observed.get((principal_id, tenant_id, authorization_role))
    if _enum_value(getattr(assignment, "status", None)) != RoleAssignmentStatus.ACTIVE.value:
        _fail("CURRENT_ROLE_ASSIGNMENT_INACTIVE")
    if getattr(assignment, "revision", None) != getattr(evidence, "role_assignment_revision", None):
        _fail("ROLE_ASSIGNMENT_REVISION_MISMATCH")
    role_result = business_adapter.observed.get((principal_id, tenant_id, business_role))
    if role_result is None:
        _fail("CURRENT_BUSINESS_ROLE_UNAVAILABLE")
    if getattr(role_result, "status", None) is None and getattr(role_result, "value", None) is None:
        _fail("CURRENT_BUSINESS_ROLE_UNAVAILABLE")
    if tenant_authority_policy.tenant_role_operation_eligibility(business_role, operation) != tenant_authority_policy.ELIGIBLE:
        _fail("BUSINESS_ROLE_INELIGIBLE")
    if (
        getattr(evidence, "permission_namespace_version", None) != permission_namespace.VERSION
        or getattr(evidence, "authorization_role_policy_version", None) != roles.VERSION
        or getattr(evidence, "tenant_business_role_policy_version", None) != tenant_authority_policy.VERSION
        or getattr(evidence, "tenant_authorization_composition_version", None) != tenant_authorization.VERSION
    ):
        _fail("AUTHORIZATION_POLICY_VERSION_MISMATCH")


def _correlate_existing(
    existing: TenantInboundMerchantConfigurationRecord,
    *,
    tenant_id: str,
    provider_id: InboundMerchantProviderId,
    merchant_account_id: str,
    merchant_configuration_id: str,
    merchant_configuration_version: int,
    non_secret_provider_options: Mapping[str, str],
    credential_secret_reference: str,
    register_idempotency_key: str,
    authorization_decision_id: str,
    evidence: Any,
) -> None:
    """Require exact immutable intent and original provenance for replay."""
    configuration = existing.configuration
    if (
        configuration.tenant_id != tenant_id
        or configuration.provider_id is not provider_id
        or configuration.merchant_account_id != merchant_account_id
        or configuration.merchant_configuration_id != merchant_configuration_id
        or configuration.merchant_configuration_version != merchant_configuration_version
        or dict(configuration.non_secret_provider_options) != dict(non_secret_provider_options)
        or configuration.credential_secret_reference != credential_secret_reference
        or existing.create_idempotency_key != register_idempotency_key
    ):
        _fail("DIVERGENT_REGISTER_REPLAY")
    stored_reference = getattr(existing, "create_authorization_reference", None)
    stored_fingerprint = getattr(existing, "create_authorization_evidence_fingerprint", None)
    expected_reference = f"tenant-authorization-decision:{authorization_decision_id}"
    accepted_references = {authorization_decision_id, expected_reference}
    if stored_reference not in accepted_references or stored_fingerprint != getattr(evidence, "authorization_evidence_fingerprint", None):
        _fail("REGISTER_REPLAY_PROVENANCE_INVALID")


def _trusted_instant(clock: Callable[[], datetime] | None) -> datetime:
    """Capture exactly one service-owned aware UTC instant on a fresh path."""
    value = datetime.now(timezone.utc) if clock is None else clock()
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail("TRUSTED_CLOCK_INVALID")
    return value.astimezone(timezone.utc)


def register_tenant_inbound_merchant_configuration(
    tenant_id: str,
    provider_id: InboundMerchantProviderId | str,
    merchant_account_id: str,
    merchant_configuration_id: str,
    merchant_configuration_version: int,
    non_secret_provider_options: Mapping[str, str],
    credential_secret_reference: str,
    register_idempotency_key: str,
    authorization_decision_id: str,
    *,
    session: ClientSession,
    configuration_collection: Collection,
    authorization_evidence_collection: Collection,
    principal_repository: Any = None,
    membership_repository: Any = None,
    role_assignment_repository: Any = None,
    business_role_repository: Any = None,
    principal_collection: Collection | None = None,
    membership_collection: Collection | None = None,
    role_assignment_collection: Collection | None = None,
    business_role_collection: Collection | None = None,
    authorization_evidence_registry: Any = None,
    configuration_registry: Any = TenantInboundMerchantConfigurationRegistry,
    clock: Callable[[], datetime] | None = None,
) -> TenantInboundMerchantConfigurationRecord:
    """Register or exactly replay one tenant inbound merchant configuration.

    The caller supplies registration intent and an authorization decision ID,
    never a principal, timestamp, fingerprint, lifecycle state, evidence object,
    raw secret, or secret version. The first operation after normalization is the
    tenant-scoped P8-P2 idempotency lookup. A hit performs only strict historical
    evidence-integrity reading and exact replay correlation. A miss reads durable
    generic evidence, proves current privilege and stored revisions, captures one
    UTC instant, constructs the immutable domain value, and calls P8-P2 create once.

    The caller must own an active transaction and retry the whole transaction on
    DuplicateKeyError or commit uncertainty; this issuer never commits, aborts,
    starts, nests, or recovers a failed transaction.
    """
    tenant = _text("tenant_id", tenant_id)
    provider = _provider(provider_id)
    account = _text("merchant_account_id", merchant_account_id)
    configuration_id = _text("merchant_configuration_id", merchant_configuration_id)
    version = _version(merchant_configuration_version)
    options = _options(non_secret_provider_options)
    secret_reference = _text("credential_secret_reference", credential_secret_reference)
    register_key = _text("register_idempotency_key", register_idempotency_key)
    decision_id = _text("authorization_decision_id", authorization_decision_id)
    tx = _active_session(session)
    if configuration_collection is None or authorization_evidence_collection is None:
        _fail("REQUIRED_COLLECTION_MISSING")

    intent_fingerprint = canonical_registration_intent_fingerprint(
        tenant_id=tenant,
        provider_id=provider,
        merchant_account_id=account,
        merchant_configuration_id=configuration_id,
        merchant_configuration_version=version,
        non_secret_provider_options=options,
        credential_secret_reference=secret_reference,
        register_idempotency_key=register_key,
    )
    subject_reference = registration_subject_reference(intent_fingerprint)
    existing = configuration_registry.get_by_idempotency_key(
        tenant,
        register_key,
        configuration_collection,
        session=tx,
    )
    if existing is not None:
        replay_registry = _evidence_registry(
            authorization_evidence_registry,
            authorization_evidence_collection,
            principal_repository or object(),
            membership_repository,
            role_assignment_repository,
            business_role_repository,
        )
        evidence = _read_evidence(replay_registry, tenant, decision_id, tx)
        evidence_fingerprint = _correlate_evidence(
            evidence,
            tenant_id=tenant,
            authorization_decision_id=decision_id,
            subject_reference=subject_reference,
            subject_fingerprint=intent_fingerprint,
        )
        if evidence_fingerprint != getattr(existing, "create_authorization_evidence_fingerprint", None):
            _fail("REGISTER_REPLAY_PROVENANCE_INVALID")
        _correlate_existing(
            existing,
            tenant_id=tenant,
            provider_id=provider,
            merchant_account_id=account,
            merchant_configuration_id=configuration_id,
            merchant_configuration_version=version,
            non_secret_provider_options=options,
            credential_secret_reference=secret_reference,
            register_idempotency_key=register_key,
            authorization_decision_id=decision_id,
            evidence=evidence,
        )
        return existing

    principal_repository, membership_repository, role_assignment_repository, business_role_repository = _default_dependencies(
        principal_repository,
        membership_repository,
        role_assignment_repository,
        business_role_repository,
    )
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
        subject_reference=subject_reference,
        subject_fingerprint=intent_fingerprint,
    )
    principal_adapter = _RepositoryAdapter(principal_repository, principal_collection)
    membership_adapter = _RepositoryAdapter(membership_repository, membership_collection)
    role_adapter = _RepositoryAdapter(role_assignment_repository, role_assignment_collection)
    business_adapter = _RepositoryAdapter(business_role_repository, business_role_collection)
    _currentness(
        evidence=evidence,
        tenant_id=tenant,
        principal_adapter=principal_adapter,
        membership_adapter=membership_adapter,
        role_adapter=role_adapter,
        business_adapter=business_adapter,
        session=tx,
    )
    created_at = _trusted_instant(clock)
    configuration = TenantInboundMerchantConfiguration(
        merchant_configuration_id=configuration_id,
        tenant_id=tenant,
        provider_id=provider,
        merchant_account_id=account,
        merchant_configuration_version=version,
        non_secret_provider_options=options,
        credential_secret_reference=secret_reference,
        created_at=created_at,
    )
    return configuration_registry.create(
        configuration,
        configuration_collection,
        idempotency_key=register_key,
        authorization_reference=f"tenant-authorization-decision:{decision_id}",
        authorization_evidence_fingerprint=evidence_fingerprint,
        session=tx,
    )


# Lifecycle authorities deliberately live beside the frozen I1 registration issuer.
# They compose authorization and currentness; the P8-P2 registry remains the only
# owner of persisted state, append-only facts, and CAS semantics.
LIFECYCLE_OPERATION = "tenant_inbound_merchant_configuration_lifecycle_transition"
LIFECYCLE_PERMISSION = "inbound_merchant_configuration:lifecycle"
LIFECYCLE_AUTHORIZATION_ROLE = "INBOUND_MERCHANT_CONFIGURATION_ADMIN"
LIFECYCLE_BUSINESS_ROLE = "tenant_inbound_merchant_configuration_admin"
COMPROMISE_OPERATION = "tenant_inbound_merchant_configuration_compromise"
COMPROMISE_PERMISSION = "inbound_merchant_configuration:security"
COMPROMISE_AUTHORIZATION_ROLE = "INBOUND_PROVIDER_SECURITY_ADMIN"
COMPROMISE_BUSINESS_ROLE = "tenant_inbound_provider_security_admin"
REMEDIATION_OPERATION = "tenant_inbound_merchant_configuration_remediate"
REMEDIATION_PERMISSION = "inbound_merchant_configuration:remediate"
REMEDIATION_AUTHORIZATION_ROLE = "INBOUND_PROVIDER_SECURITY_ADMIN"
REMEDIATION_BUSINESS_ROLE = "tenant_inbound_provider_security_admin"


def _state(value: object, name: str = "state") -> EnablementState:
    """Accept one exact lifecycle enum value; never normalize unknown states."""
    if isinstance(value, EnablementState):
        return value
    if isinstance(value, str):
        try:
            return EnablementState(value)
        except ValueError:
            pass
    _fail(f"INVALID_{name.upper()}")


def _lifecycle_payload(
    *, tenant_id: str, merchant_configuration_id: str,
    merchant_configuration_version: int, configuration_fingerprint: str,
    expected_prior_lifecycle_revision: int, expected_prior_state: EnablementState,
    target_state: EnablementState, reason_reference: str,
    lifecycle_idempotency_key: str,
) -> dict[str, object]:
    """Return the deterministic, non-secret lifecycle intent envelope."""
    return {
        "tenant_id": tenant_id,
        "merchant_configuration_id": merchant_configuration_id,
        "merchant_configuration_version": merchant_configuration_version,
        "configuration_fingerprint": configuration_fingerprint,
        "expected_prior_lifecycle_revision": expected_prior_lifecycle_revision,
        "expected_prior_state": expected_prior_state.value,
        "target_state": target_state.value,
        "reason_reference": reason_reference,
        "lifecycle_idempotency_key": lifecycle_idempotency_key,
    }


def _lifecycle_fingerprint(payload: Mapping[str, object]) -> str:
    """Hash canonical lifecycle intent with SHA3-512."""
    return hashlib.sha3_512(json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _lifecycle_subject(prefix: str, fingerprint: str) -> str:
    """Build an opaque subject reference; authorization never parses it."""
    _fingerprint("lifecycle_intent_fingerprint", fingerprint)
    return f"tenant-inbound-merchant-configuration:{prefix}:sha3-512:{fingerprint}"


def _transition_common(
    *, tenant_id: str, merchant_configuration_id: str,
    merchant_configuration_version: int, expected_configuration_fingerprint: str,
    expected_lifecycle_revision: int, expected_prior_state: EnablementState,
    target_state: EnablementState, reason_reference: str,
    lifecycle_idempotency_key: str, authorization_decision_id: str,
    session: ClientSession, configuration_collection: Collection,
    authorization_evidence_collection: Collection, principal_repository: Any = None,
    membership_repository: Any = None, role_assignment_repository: Any = None,
    business_role_repository: Any = None, principal_collection: Collection | None = None,
    membership_collection: Collection | None = None,
    role_assignment_collection: Collection | None = None,
    business_role_collection: Collection | None = None,
    authorization_evidence_registry: Any = None,
    configuration_registry: Any = TenantInboundMerchantConfigurationRegistry,
    clock: Callable[[], datetime] | None = None, operation: str,
    permission: str, authorization_role: str, business_role: str,
    allowed_edges: frozenset[tuple[EnablementState, EnablementState]],
) -> TenantInboundMerchantConfigurationRecord:
    """Shared replay-first implementation for all three administrative authorities."""
    tenant = _text("tenant_id", tenant_id)
    configuration_id = _text("merchant_configuration_id", merchant_configuration_id)
    version = _version(merchant_configuration_version)
    expected_fp = _fingerprint("expected_configuration_fingerprint", expected_configuration_fingerprint)
    if isinstance(expected_lifecycle_revision, bool) or not isinstance(expected_lifecycle_revision, int) or expected_lifecycle_revision < 0:
        _fail("INVALID_EXPECTED_LIFECYCLE_REVISION")
    prior = _state(expected_prior_state, "expected_prior_state")
    target = _state(target_state, "target_state")
    reason = _text("reason_reference", reason_reference)
    lifecycle_key = _text("lifecycle_idempotency_key", lifecycle_idempotency_key)
    decision_id = _text("authorization_decision_id", authorization_decision_id)
    tx = _active_session(session)
    if configuration_collection is None or authorization_evidence_collection is None:
        _fail("REQUIRED_COLLECTION_MISSING")
    payload = _lifecycle_payload(
        tenant_id=tenant, merchant_configuration_id=configuration_id,
        merchant_configuration_version=version, configuration_fingerprint=expected_fp,
        expected_prior_lifecycle_revision=expected_lifecycle_revision,
        expected_prior_state=prior, target_state=target, reason_reference=reason,
        lifecycle_idempotency_key=lifecycle_key,
    )
    subject_prefix = {
        LIFECYCLE_OPERATION: "lifecycle-transition",
        COMPROMISE_OPERATION: "compromise",
        REMEDIATION_OPERATION: "remediate",
    }.get(operation)
    if subject_prefix is None:
        _fail("UNKNOWN_LIFECYCLE_OPERATION")
    subject_fingerprint = _lifecycle_fingerprint(payload)
    subject = _lifecycle_subject(subject_prefix, subject_fingerprint)
    auth_ref = f"tenant-authorization-decision:{decision_id}"

    replay = configuration_registry.get_lifecycle_event_by_idempotency_key(tenant, lifecycle_key, configuration_collection, session=tx)
    if replay is not None:
        current, event = replay
        evidence_reader = _evidence_registry(authorization_evidence_registry, authorization_evidence_collection, principal_repository or object(), membership_repository, role_assignment_repository, business_role_repository)
        evidence = _read_evidence(evidence_reader, tenant, decision_id, tx)
        evidence_fp = _correlate_evidence(evidence, tenant_id=tenant, authorization_decision_id=decision_id, subject_reference=subject, subject_fingerprint=subject_fingerprint, operation=operation, permission=permission)
        if (
            event.tenant_id != tenant or event.merchant_configuration_id != configuration_id
            or event.merchant_configuration_version != version or event.configuration_fingerprint != expected_fp
            or event.prior_revision != expected_lifecycle_revision or event.prior_state is not prior
            or event.new_state is not target or event.reason_reference != reason
            or event.authorization_reference != auth_ref
            or event.authorization_evidence_fingerprint != evidence_fp
            or event.lifecycle_idempotency_key != lifecycle_key
        ):
            _fail("DIVERGENT_LIFECYCLE_REPLAY")
        return current

    principal_repository, membership_repository, role_assignment_repository, business_role_repository = _default_dependencies(principal_repository, membership_repository, role_assignment_repository, business_role_repository)
    evidence_reader = _evidence_registry(authorization_evidence_registry, authorization_evidence_collection, principal_repository, membership_repository, role_assignment_repository, business_role_repository)
    evidence = _read_evidence(evidence_reader, tenant, decision_id, tx)
    evidence_fp = _correlate_evidence(evidence, tenant_id=tenant, authorization_decision_id=decision_id, subject_reference=subject, subject_fingerprint=subject_fingerprint, operation=operation, permission=permission)
    principal_adapter = _RepositoryAdapter(principal_repository, principal_collection)
    membership_adapter = _RepositoryAdapter(membership_repository, membership_collection)
    role_adapter = _RepositoryAdapter(role_assignment_repository, role_assignment_collection)
    business_adapter = _RepositoryAdapter(business_role_repository, business_role_collection)
    _currentness(evidence=evidence, tenant_id=tenant, principal_adapter=principal_adapter, membership_adapter=membership_adapter, role_adapter=role_adapter, business_adapter=business_adapter, session=tx, operation=operation, permission=permission, authorization_role=authorization_role, business_role=business_role)
    current = configuration_registry.get(tenant, configuration_id, version, configuration_collection, session=tx)
    if current is None or current.configuration.fingerprint != expected_fp or current.lifecycle_revision != expected_lifecycle_revision or current.lifecycle_state is not prior:
        _fail("CURRENT_CONFIGURATION_CONFLICT")
    if (prior, target) not in allowed_edges:
        _fail("LIFECYCLE_EDGE_FORBIDDEN")
    instant = _trusted_instant(clock)
    transition = getattr(configuration_registry, "transition_enablement", None)
    if not callable(transition):
        transition = getattr(configuration_registry, "transition", None)
    if not callable(transition):
        _fail("REGISTRY_TRANSITION_API_INVALID")
    invoke = cast(Callable[..., TenantInboundMerchantConfigurationRecord], transition)
    return invoke(tenant, configuration_id, version, expected_lifecycle_revision, prior, target, instant, instant, reason, auth_ref, evidence_fp, lifecycle_key, configuration_collection, session=tx)


def _correlate_evidence(
    evidence: Any, *, tenant_id: str, authorization_decision_id: str,
    subject_reference: str, subject_fingerprint: str, operation: str = REGISTER_OPERATION,
    permission: str = REGISTER_PERMISSION,
) -> str:
    """Require exact correlation for one operation's durable authorization evidence."""
    if (
        getattr(evidence, "tenant_id", None) != tenant_id
        or getattr(evidence, "authorization_decision_id", None) != authorization_decision_id
        or getattr(evidence, "operation", None) != operation
        or getattr(evidence, "permission", None) != permission
        or getattr(evidence, "subject_reference", None) != subject_reference
        or getattr(evidence, "subject_evidence_fingerprint", None) != subject_fingerprint
    ):
        _fail("GENERIC_AUTHORIZATION_EVIDENCE_CORRELATION_INVALID")
    return _fingerprint("authorization_evidence_fingerprint", getattr(evidence, "authorization_evidence_fingerprint", None))


def transition_tenant_inbound_merchant_configuration(
    tenant_id: str, merchant_configuration_id: str, merchant_configuration_version: int,
    expected_configuration_fingerprint: str, expected_lifecycle_revision: int,
    expected_prior_state: EnablementState, target_state: EnablementState,
    reason_reference: str, lifecycle_idempotency_key: str, authorization_decision_id: str,
    *, session: ClientSession, configuration_collection: Collection,
    authorization_evidence_collection: Collection, principal_repository: Any = None,
    membership_repository: Any = None, role_assignment_repository: Any = None,
    business_role_repository: Any = None, principal_collection: Collection | None = None,
    membership_collection: Collection | None = None, role_assignment_collection: Collection | None = None,
    business_role_collection: Collection | None = None, authorization_evidence_registry: Any = None,
    configuration_registry: Any = TenantInboundMerchantConfigurationRegistry,
    clock: Callable[[], datetime] | None = None,
) -> TenantInboundMerchantConfigurationRecord:
    """Apply one ordinary administrative lifecycle edge, or return its exact replay."""
    allowed = frozenset({
        (EnablementState.DISABLED, EnablementState.ENABLED), (EnablementState.DISABLED, EnablementState.SUSPENDED),
        (EnablementState.DISABLED, EnablementState.RETIRED), (EnablementState.ENABLED, EnablementState.DISABLED),
        (EnablementState.ENABLED, EnablementState.SUSPENDED), (EnablementState.ENABLED, EnablementState.RETIRED),
        (EnablementState.SUSPENDED, EnablementState.ENABLED), (EnablementState.SUSPENDED, EnablementState.DISABLED),
        (EnablementState.SUSPENDED, EnablementState.RETIRED),
    })
    return _transition_common(tenant_id=tenant_id, merchant_configuration_id=merchant_configuration_id, merchant_configuration_version=merchant_configuration_version, expected_configuration_fingerprint=expected_configuration_fingerprint, expected_lifecycle_revision=expected_lifecycle_revision, expected_prior_state=expected_prior_state, target_state=target_state, reason_reference=reason_reference, lifecycle_idempotency_key=lifecycle_idempotency_key, authorization_decision_id=authorization_decision_id, session=session, configuration_collection=configuration_collection, authorization_evidence_collection=authorization_evidence_collection, principal_repository=principal_repository, membership_repository=membership_repository, role_assignment_repository=role_assignment_repository, business_role_repository=business_role_repository, principal_collection=principal_collection, membership_collection=membership_collection, role_assignment_collection=role_assignment_collection, business_role_collection=business_role_collection, authorization_evidence_registry=authorization_evidence_registry, configuration_registry=configuration_registry, clock=clock, operation=LIFECYCLE_OPERATION, permission=LIFECYCLE_PERMISSION, authorization_role=LIFECYCLE_AUTHORIZATION_ROLE, business_role=LIFECYCLE_BUSINESS_ROLE, allowed_edges=allowed)


def compromise_tenant_inbound_merchant_configuration(
    tenant_id: str, merchant_configuration_id: str, merchant_configuration_version: int,
    expected_configuration_fingerprint: str, expected_lifecycle_revision: int,
    expected_prior_state: EnablementState, reason_reference: str,
    security_event_idempotency_key: str, authorization_decision_id: str,
    *, session: ClientSession, configuration_collection: Collection,
    authorization_evidence_collection: Collection, principal_repository: Any = None,
    membership_repository: Any = None, role_assignment_repository: Any = None,
    business_role_repository: Any = None, principal_collection: Collection | None = None,
    membership_collection: Collection | None = None, role_assignment_collection: Collection | None = None,
    business_role_collection: Collection | None = None, authorization_evidence_registry: Any = None,
    configuration_registry: Any = TenantInboundMerchantConfigurationRegistry,
    clock: Callable[[], datetime] | None = None,
) -> TenantInboundMerchantConfigurationRecord:
    """Record a security compromise from an active state; target is always COMPROMISED."""
    allowed = frozenset({
        (EnablementState.DISABLED, EnablementState.COMPROMISED),
        (EnablementState.ENABLED, EnablementState.COMPROMISED),
        (EnablementState.SUSPENDED, EnablementState.COMPROMISED),
    })
    return _transition_common(tenant_id=tenant_id, merchant_configuration_id=merchant_configuration_id, merchant_configuration_version=merchant_configuration_version, expected_configuration_fingerprint=expected_configuration_fingerprint, expected_lifecycle_revision=expected_lifecycle_revision, expected_prior_state=expected_prior_state, target_state=EnablementState.COMPROMISED, reason_reference=reason_reference, lifecycle_idempotency_key=security_event_idempotency_key, authorization_decision_id=authorization_decision_id, session=session, configuration_collection=configuration_collection, authorization_evidence_collection=authorization_evidence_collection, principal_repository=principal_repository, membership_repository=membership_repository, role_assignment_repository=role_assignment_repository, business_role_repository=business_role_repository, principal_collection=principal_collection, membership_collection=membership_collection, role_assignment_collection=role_assignment_collection, business_role_collection=business_role_collection, authorization_evidence_registry=authorization_evidence_registry, configuration_registry=configuration_registry, clock=clock, operation=COMPROMISE_OPERATION, permission=COMPROMISE_PERMISSION, authorization_role=COMPROMISE_AUTHORIZATION_ROLE, business_role=COMPROMISE_BUSINESS_ROLE, allowed_edges=allowed)


def remediate_tenant_inbound_merchant_configuration(
    tenant_id: str, merchant_configuration_id: str, merchant_configuration_version: int,
    expected_configuration_fingerprint: str, expected_lifecycle_revision: int,
    expected_prior_state: EnablementState, reason_reference: str,
    lifecycle_idempotency_key: str, authorization_decision_id: str,
    *, session: ClientSession, configuration_collection: Collection,
    authorization_evidence_collection: Collection, principal_repository: Any = None,
    membership_repository: Any = None, role_assignment_repository: Any = None,
    business_role_repository: Any = None, principal_collection: Collection | None = None,
    membership_collection: Collection | None = None, role_assignment_collection: Collection | None = None,
    business_role_collection: Collection | None = None, authorization_evidence_registry: Any = None,
    configuration_registry: Any = TenantInboundMerchantConfigurationRegistry,
    clock: Callable[[], datetime] | None = None,
) -> TenantInboundMerchantConfigurationRecord:
    """Remediate exactly COMPROMISED to DISABLED; no enablement or secret claim occurs."""
    allowed = frozenset({(EnablementState.COMPROMISED, EnablementState.DISABLED)})
    return _transition_common(tenant_id=tenant_id, merchant_configuration_id=merchant_configuration_id, merchant_configuration_version=merchant_configuration_version, expected_configuration_fingerprint=expected_configuration_fingerprint, expected_lifecycle_revision=expected_lifecycle_revision, expected_prior_state=expected_prior_state, target_state=EnablementState.DISABLED, reason_reference=reason_reference, lifecycle_idempotency_key=lifecycle_idempotency_key, authorization_decision_id=authorization_decision_id, session=session, configuration_collection=configuration_collection, authorization_evidence_collection=authorization_evidence_collection, principal_repository=principal_repository, membership_repository=membership_repository, role_assignment_repository=role_assignment_repository, business_role_repository=business_role_repository, principal_collection=principal_collection, membership_collection=membership_collection, role_assignment_collection=role_assignment_collection, business_role_collection=business_role_collection, authorization_evidence_registry=authorization_evidence_registry, configuration_registry=configuration_registry, clock=clock, operation=REMEDIATION_OPERATION, permission=REMEDIATION_PERMISSION, authorization_role=REMEDIATION_AUTHORIZATION_ROLE, business_role=REMEDIATION_BUSINESS_ROLE, allowed_edges=allowed)


__all__ = [
    "CAMPAIGN",
    "REGISTER_AUTHORIZATION_ROLE",
    "REGISTER_BUSINESS_ROLE",
    "REGISTER_INTENT_FIELDS",
    "REGISTER_OPERATION",
    "REGISTER_PERMISSION",
    "REGISTER_SUBJECT_PREFIX",
    "LIFECYCLE_OPERATION",
    "LIFECYCLE_PERMISSION",
    "COMPROMISE_OPERATION",
    "COMPROMISE_PERMISSION",
    "REMEDIATION_OPERATION",
    "REMEDIATION_PERMISSION",
    "TenantInboundMerchantConfigurationIssuanceError",
    "VERSION",
    "canonical_registration_intent_fingerprint",
    "register_tenant_inbound_merchant_configuration",
    "transition_tenant_inbound_merchant_configuration",
    "compromise_tenant_inbound_merchant_configuration",
    "remediate_tenant_inbound_merchant_configuration",
    "registration_subject_reference",
]


# ARTIFACT: tenant_inbound_merchant_configuration_issuance.py
# VERSION: v1.1.0-M11-R8-R3B-P8-P3B-I2-I1-AUTHORIZED-MERCHANT-CONFIGURATION-LIFECYCLE
# AUTHORITY BOUNDARY: registration and administrative lifecycle composition only.
# TENANT POSTURE: exact tenant-scoped replay, evidence, currentness, and P8-P2 create.
# FAIL-CLOSED POSTURE: replay-first, strict provenance, current privilege, one UTC instant, and caller-owned transactions.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
