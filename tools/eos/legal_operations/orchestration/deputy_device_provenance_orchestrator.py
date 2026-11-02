"""Canonical orchestration for Deputy browser-device proof-of-possession.

TITLE: WILSY OS Deputy Device Provenance Orchestrator
VERSION: v1.0.0-L8-6H-DEPUTY-DEVICE-PROVENANCE-ORCHESTRATION
AUTHORITY: L8-6H composition boundary for short-lived Deputy browser-key proof.
EPITOME: Require one caller-owned active transaction, revalidate the canonical
         L8-6B principal/Deputy binding and its five current authorities, issue
         a short-lived L8-6G P-256 challenge, and delegate exact-session proof
         verification plus single-use atomic consumption to the L8-6H registry.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/deputy_device_provenance_orchestrator.py
COLLABORATION / OWNERSHIP: IAM repositories own principal, membership, business
                            role and authorization-role truth; P1/L8-5 own
                            canonical Deputy truth; L8-6B owns principal/Deputy
                            binding; L8-6G owns cryptographic proof semantics;
                            L8-6H owns challenge persistence, session checks and
                            single-use consumption; this module composes them.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG: v1.0.0-L8-6H-DEPUTY-DEVICE-PROVENANCE-ORCHESTRATION establishes
           caller-transaction enforcement, current five-
           authority revalidation, challenge issuance, exact caller/session
           scope checks, and delegation of proof verification and atomic
           challenge consumption. It grants no device, hardware, OS, service,
           Return of Service, or financial authority.
COMPLIANCE: Privacy-by-design engineering controls; no legal-compliance
            certification or regulatory finding is made by this module.
SECURITY / PRIVACY POSTURE: Accepts a public P-256 SPKI key and a P1363
                             signature; never accepts or stores private keys,
                             bearer tokens, location, permission, biometric or
                             hardware-attestation claims.
TENANT BOUNDARY: Tenant, principal, Deputy and office are sourced from the
                 canonical L8-6B binding; challenge lookups and registry writes
                 retain the explicit tenant and same caller transaction.
AUTHORITY BOUNDARY: Proves browser-held P-256 key possession for one challenge
                    only. It does not authenticate a user, confer device trust,
                    prove hardware/OS integrity, grant IAM/role/membership, or
                    authorize service or Return of Service operations.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial
                              execution authority; no payment or settlement
                              truth is created or inferred here.
TRANSACTION BOUNDARY: Caller supplies one already-active transaction. This
                      module never starts, commits, aborts, or retries it.
FAIL-CLOSED DECLARATION: Missing/stale authority, inactive transaction, binding
                         drift, invalid challenge/proof, cross-scope session,
                         replay, corrupt persistence or storage failure rejects.
"""
from __future__ import annotations

from datetime import datetime, timezone
import secrets
import uuid
from typing import Any, Final, NoReturn

from tools.eos.legal_operations.domain.deputy_device_provenance_authority import (
    MAX_CHALLENGE_LIFETIME,
    DeputyDeviceProvenance,
    DeputyDeviceProvenanceAuthorityError,
    DeputyDeviceProvenanceChallenge,
)
from tools.eos.legal_operations.orchestration.deputy_principal_binding_orchestrator import (
    DeputyPrincipalBindingOrchestrationError,
    bind_deputy_principal_identity,
)
from tools.eos.legal_operations.registry.deputy_device_provenance_registry import (
    DeputyDeviceProvenanceRegistry,
    DeputyDeviceProvenanceRegistryConflictError,
    DeputyDeviceProvenanceRegistryError,
    DeputyDeviceProvenanceRegistryPersistedRecordInvalidError,
    DeputyDeviceProvenanceRegistryPersistenceError,
    DeputyDeviceProvenanceRegistryRetryTransactionError,
)
from tools.eos.legal_operations.registry.deputy_principal_binding_registry import (
    DeputyPrincipalBindingRegistry,
    DeputyPrincipalBindingRegistryError,
)

VERSION: Final[str] = (
    "v1.0.0-L8-6H-DEPUTY-DEVICE-PROVENANCE-ORCHESTRATION"
)


class DeputyDeviceProvenanceOrchestrationError(RuntimeError):
    """Stable fail-closed composition error.

    ``code`` is a non-secret institutional failure code. The error conveys no
    authority itself. Tenant scope is supplied by the rejected operation; no
    cross-tenant record details are included. Mutations are limited to challenge
    issuance or challenge consumption inside the caller's transaction. The
    caller owns commit/rollback and any whole-transaction retry. No financial,
    service, or Return of Service authority is represented.
    """

    def __init__(self, code: str) -> None:
        """Create one stable orchestration failure without exposing record data."""
        self.code = code
        super().__init__(code)


def _fail(
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise a stable orchestration error while preserving its technical cause."""
    error = DeputyDeviceProvenanceOrchestrationError(code)
    if cause is None:
        raise error
    raise error from cause


def _active_transaction(session: Any) -> Any:
    """Require one already-active caller transaction before authority reads."""
    if session is None:
        _fail("L8_6H_ACTIVE_TRANSACTION_REQUIRED")
    try:
        marker = getattr(session, "in_transaction", None)
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail("L8_6H_ACTIVE_TRANSACTION_REQUIRED", error)
    if active is not True:
        _fail("L8_6H_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _canonical_binding(
    *,
    tenant_id: str,
    principal_id: str,
    deputy_id: str,
    lifecycle_collection: Any,
    binding_collection: Any,
    principal_collection: Any,
    membership_collection: Any,
    business_role_collection: Any,
    role_assignment_collection: Any,
    session: Any,
) -> Any:
    """Revalidate the exact stored binding and all five current authorities.

    The binding registry lookup is tenant/principal scoped. The existing L8-6B
    orchestrator then independently rechecks ACTIVE principal, ACTIVE tenant
    membership, ACTIVE ``tenant_deputy`` business role, ACTIVE ``DEPUTY`` role
    assignment, and canonical same-tenant Deputy evidence in this transaction.
    Replaying the binding through L8-6B must reproduce the exact stored value.
    """
    try:
        stored = DeputyPrincipalBindingRegistry.resolve_by_principal(
            tenant_id,
            principal_id,
            binding_collection,
            session=session,
        )
    except DeputyPrincipalBindingRegistryError as error:
        _fail("L8_6H_CANONICAL_BINDING_REQUIRED", error)

    if (
        stored.tenant_id != tenant_id
        or stored.principal_id != principal_id
        or stored.deputy_id != deputy_id
    ):
        _fail("L8_6H_CANONICAL_BINDING_SCOPE_MISMATCH")

    try:
        current = bind_deputy_principal_identity(
            tenant_id=tenant_id,
            principal_id=principal_id,
            deputy_id=deputy_id,
            bound_at=stored.bound_at,
            evidence_reference=stored.evidence_reference,
            lifecycle_collection=lifecycle_collection,
            binding_collection=binding_collection,
            principal_collection=principal_collection,
            membership_collection=membership_collection,
            business_role_collection=business_role_collection,
            role_assignment_collection=role_assignment_collection,
            session=session,
        )
    except DeputyPrincipalBindingOrchestrationError as error:
        _fail("L8_6H_CURRENT_DEPUTY_AUTHORITY_REJECTED", error)

    if current.to_dict() != stored.to_dict():
        _fail("L8_6H_CANONICAL_BINDING_CHANGED")
    return current


def _registry(
    challenge_collection: Any,
    auth_registry: Any,
    binding_collection: Any,
) -> DeputyDeviceProvenanceRegistry:
    """Construct the registry boundary without creating indexes or a session."""
    try:
        return DeputyDeviceProvenanceRegistry(
            challenge_collection,
            auth_registry=auth_registry,
            binding_collection=binding_collection,
        )
    except DeputyDeviceProvenanceRegistryError as error:
        _fail("L8_6H_REGISTRY_UNAVAILABLE", error)


def _persist_challenge(
    registry: DeputyDeviceProvenanceRegistry,
    challenge: DeputyDeviceProvenanceChallenge,
    *,
    session: Any,
) -> DeputyDeviceProvenanceChallenge:
    """Persist the challenge and map registry outcomes to stable API errors."""
    try:
        return registry.create(challenge, session=session)
    except DeputyDeviceProvenanceRegistryRetryTransactionError as error:
        _fail("L8_6H_CHALLENGE_PERSISTENCE_RETRY_REQUIRED", error)
    except DeputyDeviceProvenanceRegistryConflictError as error:
        _fail("L8_6H_CHALLENGE_PERSISTENCE_CONFLICT", error)
    except DeputyDeviceProvenanceRegistryPersistedRecordInvalidError as error:
        _fail("L8_6H_CHALLENGE_PERSISTED_RECORD_INVALID", error)
    except DeputyDeviceProvenanceRegistryPersistenceError as error:
        _fail("L8_6H_CHALLENGE_PERSISTENCE_UNAVAILABLE", error)
    except DeputyDeviceProvenanceRegistryError as error:
        _fail("L8_6H_CHALLENGE_PERSISTENCE_REJECTED", error)


def issue_deputy_device_challenge(
    *,
    tenant_id: str,
    principal_id: str,
    deputy_id: str,
    session_reference: str,
    public_key_spki_der: bytes,
    lifecycle_collection: Any,
    binding_collection: Any,
    principal_collection: Any,
    membership_collection: Any,
    business_role_collection: Any,
    role_assignment_collection: Any,
    challenge_collection: Any,
    auth_registry: Any,
    session: Any,
    issued_at: datetime | None = None,
    challenge_id: str | None = None,
    nonce: bytes | None = None,
) -> DeputyDeviceProvenanceChallenge:
    """Revalidate current Deputy authorities and persist one fresh challenge.

    A caller-owned active transaction is mandatory and is propagated unchanged
    to every authority read and registry write. The registry independently
    confirms that ``session_reference`` is current for this tenant/principal.
    The challenge is short-lived and bound to the exact canonical Deputy binding
    and public key. Optional time/identity/nonce inputs support deterministic
    tests; production callers should omit them. The function never commits or
    retries the transaction and creates no device-trust or financial authority.
    """
    tx = _active_transaction(session)
    binding = _canonical_binding(
        tenant_id=tenant_id,
        principal_id=principal_id,
        deputy_id=deputy_id,
        lifecycle_collection=lifecycle_collection,
        binding_collection=binding_collection,
        principal_collection=principal_collection,
        membership_collection=membership_collection,
        business_role_collection=business_role_collection,
        role_assignment_collection=role_assignment_collection,
        session=tx,
    )
    now = datetime.now(timezone.utc) if issued_at is None else issued_at
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        _fail("L8_6H_ISSUED_AT_INVALID")

    try:
        challenge = DeputyDeviceProvenanceChallenge.issue(
            binding=binding,
            session_reference=session_reference,
            challenge_id=uuid.uuid4().hex if challenge_id is None else challenge_id,
            public_key_spki_der=public_key_spki_der,
            nonce=secrets.token_bytes(32) if nonce is None else nonce,
            issued_at=now,
            expires_at=now + MAX_CHALLENGE_LIFETIME,
        )
    except DeputyDeviceProvenanceAuthorityError as error:
        _fail("L8_6H_CHALLENGE_ISSUANCE_REJECTED", error)

    registry = _registry(
        challenge_collection,
        auth_registry,
        binding_collection,
    )
    return _persist_challenge(registry, challenge, session=tx)


def _load_challenge(
    registry: DeputyDeviceProvenanceRegistry,
    *,
    tenant_id: str,
    challenge_id: str,
    session: Any,
) -> DeputyDeviceProvenanceChallenge:
    """Load only the exact tenant/challenge and preserve integrity distinctions."""
    try:
        return registry.get(tenant_id, challenge_id, session=session)
    except DeputyDeviceProvenanceRegistryConflictError as error:
        # Same bounded response for absent and foreign-tenant challenge IDs.
        _fail("L8_6H_CHALLENGE_NOT_AVAILABLE", error)
    except DeputyDeviceProvenanceRegistryPersistedRecordInvalidError as error:
        _fail("L8_6H_CHALLENGE_INTEGRITY_REJECTED", error)
    except DeputyDeviceProvenanceRegistryPersistenceError as error:
        _fail("L8_6H_CHALLENGE_LOOKUP_UNAVAILABLE", error)
    except DeputyDeviceProvenanceRegistryError as error:
        _fail("L8_6H_CHALLENGE_LOOKUP_REJECTED", error)


def verify_and_consume_deputy_device_challenge(
    *,
    tenant_id: str,
    principal_id: str,
    deputy_id: str,
    session_reference: str,
    challenge_id: str,
    signature_p1363: bytes,
    lifecycle_collection: Any,
    binding_collection: Any,
    principal_collection: Any,
    membership_collection: Any,
    business_role_collection: Any,
    role_assignment_collection: Any,
    challenge_collection: Any,
    auth_registry: Any,
    session: Any,
    verified_at: datetime | None = None,
) -> DeputyDeviceProvenance:
    """Revalidate current authorities and atomically consume one exact proof.

    The challenge must match the current canonical binding and the exact caller
    session reference. L8-6H independently revalidates AuthRegistry session
    currentness at verification time, verifies the P-256 P1363 signature, and
    compare-and-sets ``consumed_at`` with immutable provenance in one document
    update. The caller owns commit/rollback; no transaction lifecycle or retry
    is performed here. The result proves one browser-key possession event only.
    """
    tx = _active_transaction(session)
    binding = _canonical_binding(
        tenant_id=tenant_id,
        principal_id=principal_id,
        deputy_id=deputy_id,
        lifecycle_collection=lifecycle_collection,
        binding_collection=binding_collection,
        principal_collection=principal_collection,
        membership_collection=membership_collection,
        business_role_collection=business_role_collection,
        role_assignment_collection=role_assignment_collection,
        session=tx,
    )
    registry = _registry(
        challenge_collection,
        auth_registry,
        binding_collection,
    )
    challenge = _load_challenge(
        registry,
        tenant_id=tenant_id,
        challenge_id=challenge_id,
        session=tx,
    )
    if (
        challenge.tenant_id != binding.tenant_id
        or challenge.principal_id != binding.principal_id
        or challenge.deputy_id != binding.deputy_id
        or challenge.sheriff_office_id != binding.sheriff_office_id
        or challenge.session_reference != session_reference
    ):
        _fail("L8_6H_CHALLENGE_CALLER_SCOPE_MISMATCH")

    now = datetime.now(timezone.utc) if verified_at is None else verified_at
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        _fail("L8_6H_VERIFIED_AT_INVALID")
    try:
        return registry.verify_and_consume(
            tenant_id=tenant_id,
            challenge_id=challenge_id,
            signature_p1363=signature_p1363,
            verified_at=now,
            session=tx,
        )
    except DeputyDeviceProvenanceRegistryConflictError as error:
        _fail("L8_6H_PROOF_CONSUMPTION_CONFLICT", error)
    except DeputyDeviceProvenanceRegistryPersistedRecordInvalidError as error:
        _fail("L8_6H_PROOF_PERSISTED_RECORD_INVALID", error)
    except DeputyDeviceProvenanceRegistryPersistenceError as error:
        _fail("L8_6H_PROOF_CONSUMPTION_UNAVAILABLE", error)
    except DeputyDeviceProvenanceRegistryError as error:
        _fail("L8_6H_PROOF_CONSUMPTION_REJECTED", error)


__all__ = [
    "VERSION",
    "DeputyDeviceProvenanceOrchestrationError",
    "issue_deputy_device_challenge",
    "verify_and_consume_deputy_device_challenge",
]


# ARTIFACT: deputy_device_provenance_orchestrator.py
# VERSION: v1.0.0-L8-6H-DEPUTY-DEVICE-PROVENANCE-ORCHESTRATION
# AUTHORITY BOUNDARY: Browser-held P-256 proof-of-possession for one challenge only; no device trust, hardware attestation, OS permission, IAM, service, or Return of Service authority.
# TENANT POSTURE: Exact canonical tenant/principal/Deputy/office binding and exact caller-owned transaction/session across participating authorities.
# FAIL-CLOSED POSTURE: Stale/missing authority, transaction failure, binding drift, challenge mismatch, invalid proof, replay, corrupt persistence, or storage failure rejects.
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT