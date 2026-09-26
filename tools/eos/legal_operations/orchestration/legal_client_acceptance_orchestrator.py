"""TITLE: WILSY OS Authorized Legal Client Acceptance Issuance Orchestrator.
VERSION: v1.0.0-L9A3-LEGAL-CLIENT-ACCEPTANCE-ISSUANCE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations.
EPITOME: Compose one immutable client-acceptance evidence record only after
         exact current CaseMatter and LegalMatterParty reads and durable,
         tenant-scoped LEGAL_CLIENT authorization evidence in the same
         caller-owned transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_acceptance_orchestrator.py
COLLABORATION / OWNERSHIP: L9A owns immutable acceptance semantics; L9A2 owns
                            acceptance persistence; Legal Operations lifecycle
                            and party registries own source facts; IAM owns
                            current authorization evidence. L9A3 composes
                            these authorities without creating a new truth.
CERTIFICATION / UPDATE DATE: 2026-09-26.
CHANGELOG: v1.0.0-L9A3-LEGAL-CLIENT-ACCEPTANCE-ISSUANCE establishes exact
           authenticated-identity binding, current OPEN CaseMatter projection,
           exact matter-party correlation, LEGAL_CLIENT authorization evidence,
           deterministic subject evidence and immutable acceptance persistence.
           It creates no engagement, representation, conflict clearance, Court,
           instruction, billing, payment, execution or settlement authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only opaque identifiers and SHA3-512 evidence
                             fingerprints are admitted; no raw client PII,
                             credentials, tokens or narrative is logged.
TENANT BOUNDARY: Tenant and actor are derived from one authenticated
                 SovereignIdentity and every source/persistence lookup is
                 rechecked against that tenant; no cross-tenant fallback.
AUTHORITY BOUNDARY: Authorized immutable client-acceptance issuance only.
                    Role projections never authorize by themselves; generic
                    durable IAM evidence is required before admission.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller supplies and owns the already-active session and
                      complete transaction lifecycle. This module never starts,
                      commits, aborts, retries, or reconciles transactions.
FAIL-CLOSED DECLARATION: Missing transaction, inactive identity, missing or
                         divergent current sources, denied/conflicting IAM,
                         replay divergence, and persistence failures reject.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Final, NoReturn

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceAuthorizationDeniedError,
    TenantAuthorizationDecisionEvidenceConflictError,
    TenantAuthorizationDecisionEvidencePersistenceError,
    TenantAuthorizationDecisionEvidenceRegistry,
    TenantAuthorizationDecisionEvidenceRegistryError,
    TenantAuthorizationDecisionEvidenceTransactionRequiredError,
)
from tools.eos.legal_operations.domain.legal_client_acceptance import (
    LegalClientAcceptance,
    LegalClientAcceptanceError,
    record_legal_client_acceptance,
)
from tools.eos.legal_operations.domain.legal_operations_current_projection import (
    resolve_current_lifecycle_snapshot,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.registry.legal_client_acceptance_registry import (
    LegalClientAcceptanceRegistry,
    LegalClientAcceptanceRegistryConflictError,
    LegalClientAcceptanceRegistryError,
    LegalClientAcceptanceRegistryPersistenceUnavailableError,
    LegalClientAcceptanceRegistryPersistedRecordInvalidError,
    LegalClientAcceptanceRegistryRetryRequiredError,
)
from tools.eos.legal_operations.registry.legal_matter_party_registry import (
    LegalMatterPartyRegistry,
    LegalMatterPartyRegistryError,
    LegalMatterPartyRegistryNotFoundError,
    LegalMatterPartyRegistryPersistenceUnavailableError,
    LegalMatterPartyRegistryPersistedRecordInvalidError,
    LegalMatterPartyRegistryRetryRequiredError,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
    LegalOperationsLifecycleRegistryError,
)


VERSION: Final[str] = "v1.0.0-L9A3-LEGAL-CLIENT-ACCEPTANCE-ISSUANCE"
PERMISSION: Final[str] = "legal_operations:client_acceptance:write"
OPERATION: Final[str] = "legal_client_acceptance_write"
SUBJECT_PREFIX: Final[str] = "legal-client-acceptance"


class LegalClientAcceptanceOrchestrationError(RuntimeError):
    """Stable fail-closed L9A3 orchestration error without secret payloads."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientAcceptanceOrchestrationRetryRequiredError(
    LegalClientAcceptanceOrchestrationError
):
    """Caller must abort and restart the complete transaction from fresh state."""


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise a stable bounded error while retaining only an internal cause."""
    error = LegalClientAcceptanceOrchestrationError(code)
    if cause is None:
        raise error
    raise error from cause


def _retry(code: str, cause: BaseException) -> NoReturn:
    """Convert a persistence race into caller-owned whole-transaction retry."""
    raise LegalClientAcceptanceOrchestrationRetryRequiredError(code) from cause


def _text(name: str, value: object) -> str:
    """Require one bounded non-empty identity/reference without coercion."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"L9A3_{name.upper()}_INVALID")
    return value


def _active_session(session: Any) -> Any:
    """Require an already-active caller-owned transaction session."""
    if session is None:
        _fail("L9A3_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _fail("L9A3_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _subject_reference(acceptance_id: str) -> str:
    """Derive the opaque authorization subject identity from acceptance ID."""
    return f"{SUBJECT_PREFIX}:{acceptance_id}"


def _authorization_idempotency_key(acceptance_id: str) -> str:
    """Derive stable tenant-scoped IAM idempotency from acceptance identity."""
    return f"legal-client-acceptance:{acceptance_id}"


def _subject_fingerprint(
    *,
    tenant_id: str,
    case_matter: CaseMatter,
    acceptance_id: str,
    party_id: str,
    subject_reference: str,
    subject_identity_fingerprint: str,
    acceptance_scope: str,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
    actor_principal_id: str,
) -> str:
    """Fingerprint all caller material plus server-bound matter and actor data."""
    payload = {
        "tenant_id": tenant_id,
        "case_matter_id": case_matter.case_matter_id,
        "matter_fingerprint": case_matter.fingerprint,
        "acceptance_id": acceptance_id,
        "party_id": party_id,
        "subject_reference": subject_reference,
        "subject_identity_fingerprint": subject_identity_fingerprint,
        "acceptance_scope": acceptance_scope,
        "source_evidence_reference": source_evidence_reference,
        "source_evidence_fingerprint": source_evidence_fingerprint,
        "actor_principal_id": actor_principal_id,
    }
    return hashlib.sha3_512(
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _identity(identity: SovereignIdentity) -> tuple[str, str]:
    """Extract only active server-authenticated principal and tenant identity."""
    if not isinstance(identity, SovereignIdentity):
        _fail("L9A3_IDENTITY_REQUIRED")
    if identity.status is not PrincipalStatus.ACTIVE:
        _fail("L9A3_PRINCIPAL_INACTIVE")
    return _text("tenant_id", identity.tenant_id), _text("principal_id", identity.identity_id)


def _current_case_matter(
    *, tenant_id: str, case_matter_id: str, collection: Any, session: Any
) -> CaseMatter:
    """Read complete exact lifecycle history and select its current snapshot."""
    try:
        history = LegalOperationsLifecycleRegistry.get_entity_history(
            tenant_id,
            "CaseMatter",
            case_matter_id,
            collection,
            session=session,
        )
        value = resolve_current_lifecycle_snapshot(history, expected_type=CaseMatter)
    except (LegalOperationsLifecycleRegistryError, ValueError, TypeError) as error:
        _fail("L9A3_CASE_MATTER_UNAVAILABLE", error)
    if not isinstance(value, CaseMatter):
        _fail("L9A3_CASE_MATTER_TYPE_INVALID")
    if value.tenant_id != tenant_id or value.case_matter_id != case_matter_id:
        _fail("L9A3_CASE_MATTER_SCOPE_MISMATCH")
    if value.state is not CaseMatterState.OPEN:
        _fail("L9A3_CASE_MATTER_NOT_OPEN")
    return value


def issue_legal_client_acceptance(
    *,
    identity: SovereignIdentity,
    case_matter_id: str,
    acceptance_id: str,
    party_id: str,
    subject_reference: str,
    subject_identity_fingerprint: str,
    acceptance_scope: str,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
    lifecycle_collection: Any,
    party_collection: Any,
    acceptance_collection: Any,
    authorization_evidence_registry: TenantAuthorizationDecisionEvidenceRegistry,
    session: Any,
) -> LegalClientAcceptance:
    """Issue one authorized immutable acceptance and return its durable replay.

    Tenant and actor are derived from the authenticated identity; the current
    OPEN CaseMatter and exact party are re-read under the supplied session.
    Authorization evidence and acceptance persistence use the same active
    caller transaction. This function owns neither transaction lifecycle nor
    HTTP authentication and creates no engagement, representation, Court or
    financial authority.
    """
    tx = _active_session(session)
    tenant, principal = _identity(identity)
    matter_id = _text("case_matter_id", case_matter_id)
    acceptance_identity = _text("acceptance_id", acceptance_id)
    party_identity = _text("party_id", party_id)
    subject = _text("subject_reference", subject_reference)
    subject_fingerprint = _text(
        "subject_identity_fingerprint", subject_identity_fingerprint
    )
    scope = _text("acceptance_scope", acceptance_scope)
    source_reference = _text("source_evidence_reference", source_evidence_reference)
    source_fingerprint = _text(
        "source_evidence_fingerprint", source_evidence_fingerprint
    )
    if not isinstance(
        authorization_evidence_registry,
        TenantAuthorizationDecisionEvidenceRegistry,
    ):
        _fail("L9A3_AUTHORIZATION_EVIDENCE_REGISTRY_REQUIRED")
    if lifecycle_collection is None or party_collection is None or acceptance_collection is None:
        _fail("L9A3_COLLECTION_REQUIRED")

    matter = _current_case_matter(
        tenant_id=tenant,
        case_matter_id=matter_id,
        collection=lifecycle_collection,
        session=tx,
    )
    try:
        party = LegalMatterPartyRegistry.get_party(
            tenant,
            party_identity,
            party_collection,
            session=tx,
        )
    except LegalMatterPartyRegistryNotFoundError as error:
        _fail("L9A3_PARTY_NOT_FOUND", error)
    except LegalMatterPartyRegistryRetryRequiredError as error:
        _retry("L9A3_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    except (
        LegalMatterPartyRegistryPersistedRecordInvalidError,
        LegalMatterPartyRegistryPersistenceUnavailableError,
        LegalMatterPartyRegistryError,
    ) as error:
        _fail("L9A3_PARTY_UNAVAILABLE", error)
    if (
        party.tenant_id != tenant
        or party.case_matter_id != matter.case_matter_id
        or party.matter_fingerprint != matter.fingerprint
        or party.party_id != party_identity
        or party.subject_reference != subject
        or party.subject_identity_fingerprint != subject_fingerprint
    ):
        _fail("L9A3_PARTY_SCOPE_MISMATCH")

    subject_reference_value = _subject_reference(acceptance_identity)
    evidence_fingerprint = _subject_fingerprint(
        tenant_id=tenant,
        case_matter=matter,
        acceptance_id=acceptance_identity,
        party_id=party_identity,
        subject_reference=subject,
        subject_identity_fingerprint=subject_fingerprint,
        acceptance_scope=scope,
        source_evidence_reference=source_reference,
        source_evidence_fingerprint=source_fingerprint,
        actor_principal_id=principal,
    )
    try:
        authorization = authorization_evidence_registry.issue(
            tenant_id=tenant,
            principal_id=principal,
            operation=OPERATION,
            permission=PERMISSION,
            subject_reference=subject_reference_value,
            subject_evidence_fingerprint=evidence_fingerprint,
            idempotency_key=_authorization_idempotency_key(acceptance_identity),
            session=tx,
        )
    except TenantAuthorizationDecisionEvidenceAuthorizationDeniedError as error:
        _fail("L9A3_CLIENT_AUTHORIZATION_REQUIRED", error)
    except TenantAuthorizationDecisionEvidenceTransactionRequiredError as error:
        _fail("L9A3_ACTIVE_TRANSACTION_REQUIRED", error)
    except TenantAuthorizationDecisionEvidenceConflictError as error:
        _fail("L9A3_AUTHORIZATION_REPLAY_CONFLICT", error)
    except TenantAuthorizationDecisionEvidencePersistenceError as error:
        _fail("L9A3_AUTHORIZATION_EVIDENCE_UNAVAILABLE", error)
    except TenantAuthorizationDecisionEvidenceRegistryError as error:
        _fail("L9A3_AUTHORIZATION_EVIDENCE_UNAVAILABLE", error)
    if (
        authorization.tenant_id != tenant
        or authorization.principal_id != principal
        or authorization.operation != OPERATION
        or authorization.permission != PERMISSION
        or authorization.subject_reference != subject_reference_value
        or authorization.subject_evidence_fingerprint != evidence_fingerprint
    ):
        _fail("L9A3_AUTHORIZATION_CORRELATION_INVALID")

    try:
        value = record_legal_client_acceptance(
            case_matter=matter,
            acceptance_id=acceptance_identity,
            party_id=party_identity,
            subject_reference=subject,
            subject_identity_fingerprint=subject_fingerprint,
            acceptance_scope=scope,
            actor_principal_id=principal,
            accepted_at=authorization.authorized_at,
            source_evidence_reference=source_reference,
            source_evidence_fingerprint=source_fingerprint,
        )
    except LegalClientAcceptanceError as error:
        _fail("L9A3_ACCEPTANCE_INVALID", error)
    try:
        persisted = LegalClientAcceptanceRegistry.persist_acceptance(
            value,
            acceptance_collection,
            session=tx,
        )
    except LegalClientAcceptanceRegistryRetryRequiredError as error:
        _retry("L9A3_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    except LegalClientAcceptanceRegistryConflictError as error:
        _fail("L9A3_ACCEPTANCE_REPLAY_CONFLICT", error)
    except (
        LegalClientAcceptanceRegistryPersistedRecordInvalidError,
        LegalClientAcceptanceRegistryPersistenceUnavailableError,
        LegalClientAcceptanceRegistryError,
    ) as error:
        _fail("L9A3_ACCEPTANCE_PERSISTENCE_UNAVAILABLE", error)
    if (
        persisted.to_dict() != value.to_dict()
        or persisted.tenant_id != tenant
        or persisted.case_matter_id != matter.case_matter_id
        or persisted.actor_principal_id != principal
        or persisted.accepted_at != authorization.authorized_at
    ):
        _fail("L9A3_POST_WRITE_CORRELATION_INVALID")
    return persisted


__all__ = [
    "OPERATION",
    "PERMISSION",
    "SUBJECT_PREFIX",
    "VERSION",
    "LegalClientAcceptanceOrchestrationError",
    "LegalClientAcceptanceOrchestrationRetryRequiredError",
    "issue_legal_client_acceptance",
]


# ARTIFACT: legal_client_acceptance_orchestrator.py
# VERSION: v1.0.0-L9A3-LEGAL-CLIENT-ACCEPTANCE-ISSUANCE
# AUTHORITY BOUNDARY: authorized immutable client-acceptance issuance only
# TENANT POSTURE: authenticated exact tenant + current OPEN matter + exact party + durable IAM evidence
# FAIL-CLOSED POSTURE: transaction/source/authorization/persistence divergence rejects; retry remains caller-owned
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
