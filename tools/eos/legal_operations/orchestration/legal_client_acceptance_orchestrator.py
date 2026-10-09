"""WILSY OS context-bound legal-client acceptance issuance.

TITLE: WILSY OS Context-Bound Legal Client Acceptance Issuance
VERSION: v1.1.0-L9A3-R1-CONTEXT-BOUND-ACCEPTANCE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Record one immutable LegalClientAcceptance only when an authenticated
         LEGAL_CLIENT explicitly confirms an unexpired, opaque acceptance
         context whose complete matter, party, capacity, instrument, lifecycle,
         approval, visibility and IAM dependencies are current again.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_acceptance_orchestrator.py
COLLABORATION / OWNERSHIP: P2C1 owns context semantics; P2C2 owns context
                            persistence; P2C3 owns context composition; P2D
                            owns the shared dependency revalidation helper;
                            L9A2 owns immutable acceptance persistence; IAM
                            owns authorization evidence. This orchestrator
                            creates no parallel source of truth.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.1.0-L9A3-R1 narrows issuance to authenticated identity, opaque
           context ID, strict confirmation and bounded idempotency intent.
           Tenant, principal, matter, party, subject, scope, source evidence
           and accepted_at are server-derived. Existing current-dependency
           revalidation is repeated at issuance, exact replay is preserved,
           divergent intent is rejected, and the caller retains transaction
           ownership. The former authority-bearing caller signature is removed.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: The request contains no authority-bearing matter
                             or subject fields. Only opaque identifiers and
                             SHA3-512 provenance fingerprints are persisted;
                             candidate values never enter errors.
TENANT BOUNDARY: Tenant and principal derive only from one active
                 SovereignIdentity. Context reads and every revalidation read
                 are exact tenant/principal scoped with no fallback.
AUTHORITY BOUNDARY: Immutable client-acceptance evidence only. This value does
                    not create engagement, retainer, mandate, representation,
                    conflict clearance, Court authority or client acceptance
                    outside the exact context-bound record.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement.
TRANSACTION BOUNDARY: The caller supplies an already-active transaction and
                      owns commit, abort, retry and unknown-commit handling.
                      This module never starts, commits, aborts, retries or
                      reconciles a transaction.
FAIL-CLOSED DECLARATION: Missing/expired/cross-actor contexts, false or
                         malformed confirmation, stale dependencies, denied
                         IAM, persistence divergence and replay conflicts reject
                         without coercion or authority inference.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Callable, Final, NoReturn

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
from tools.eos.legal_operations.domain.legal_client_acceptance_context import (
    LegalClientAcceptanceContext,
)
from tools.eos.legal_operations.registry import (
    legal_client_acceptance_context_registry as context_registry,
)
from tools.eos.legal_operations.registry.legal_client_acceptance_registry import (
    LegalClientAcceptanceRegistry,
    LegalClientAcceptanceRegistryConflictError,
    LegalClientAcceptanceRegistryError,
    LegalClientAcceptanceRegistryNotFoundError,
    LegalClientAcceptanceRegistryPersistenceUnavailableError,
    LegalClientAcceptanceRegistryPersistedRecordInvalidError,
    LegalClientAcceptanceRegistryRetryRequiredError,
)
from tools.eos.legal_operations.service.legal_client_acceptance_content_service import (
    _matter,
    _revalidate_dependencies,
)


VERSION: Final[str] = "v1.1.0-L9A3-R1-CONTEXT-BOUND-ACCEPTANCE"
PERMISSION: Final[str] = "legal_operations:client_acceptance:write"
OPERATION: Final[str] = "legal_client_acceptance_write"
SUBJECT_PREFIX: Final[str] = "legal-client-acceptance-context"
AUTHORIZATION_SUBJECT_PREFIX: Final[str] = "legal-client-acceptance-issuance"
UTC = timezone.utc
Clock = Callable[[], datetime]


class LegalClientAcceptanceOrchestrationError(RuntimeError):
    """Stable fail-closed issuance error containing no supplied values."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded semantic code and retain no request data."""
        self.code = code
        super().__init__(code)


class LegalClientAcceptanceOrchestrationRetryRequiredError(
    LegalClientAcceptanceOrchestrationError
):
    """The caller must abort and restart the complete transaction."""


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one bounded error while retaining only an internal cause."""
    error = LegalClientAcceptanceOrchestrationError(code)
    if cause is None:
        raise error
    raise error from cause


def _retry(code: str, cause: BaseException) -> NoReturn:
    """Signal a caller-owned whole-transaction retry without performing one."""
    raise LegalClientAcceptanceOrchestrationRetryRequiredError(code) from cause


def _active_session(session: Any) -> Any:
    """Require an already-active caller-owned transaction before any read."""
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


def _identity(identity: SovereignIdentity) -> tuple[str, str]:
    """Derive exact tenant and principal from the authenticated identity only."""
    if not isinstance(identity, SovereignIdentity):
        _fail("L9A3_IDENTITY_REQUIRED")
    if identity.status is not PrincipalStatus.ACTIVE:
        _fail("L9A3_PRINCIPAL_INACTIVE")
    if (
        not isinstance(identity.tenant_id, str)
        or not identity.tenant_id
        or not isinstance(identity.identity_id, str)
        or not identity.identity_id
    ):
        _fail("L9A3_IDENTITY_INVALID")
    return identity.tenant_id, identity.identity_id


def _text(code: str, value: object, *, maximum: int = 240) -> str:
    """Require one bounded, non-empty, non-coerced opaque request identity."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > maximum
        or any(ord(character) < 32 for character in value)
    ):
        _fail(f"L9A3_{code.upper()}_INVALID")
    return value


def _now(clock: Clock | None) -> datetime:
    """Capture exactly one aware UTC server instant for the issuance attempt."""
    value = datetime.now(UTC) if clock is None else clock()
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail("L9A3_SERVER_CLOCK_INVALID")
    return value.astimezone(UTC)


def _context(
    *, tenant: str, context_id: str, at: datetime, collection: Any, session: Any
) -> LegalClientAcceptanceContext:
    """Load one exact tenant-scoped context inside the caller transaction."""
    try:
        value = context_registry.get_valid_context(
            tenant, context_id, at, collection, session=session
        )
    except Exception as error:
        _fail("L9A3_CONTEXT_UNAVAILABLE", error)
    if value is None:
        _fail("L9A3_CONTEXT_EXPIRED_OR_NOT_FOUND")
    if value.tenant_id != tenant:
        _fail("L9A3_CONTEXT_TENANT_MISMATCH")
    return value


def _intent_fingerprint(
    *, context: LegalClientAcceptanceContext, idempotency_key: str, confirmed: bool
) -> str:
    """Bind context replay identity and explicit confirmation without storing the key."""
    payload = {
        "acceptance_context_id": context.acceptance_context_id,
        "context_fingerprint": context.fingerprint,
        "context_replay_key": context.replay_key,
        "idempotency_key": idempotency_key,
        "confirmed": confirmed,
    }
    return hashlib.sha3_512(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _acceptance_id(context_id: str) -> str:
    """Derive one stable acceptance identity from the opaque context identity."""
    return f"LEGAL-CLIENT-ACCEPT:{context_id}"


def _source_reference(
    *, context: LegalClientAcceptanceContext, intent_fingerprint: str
) -> str:
    """Create bounded source provenance without persisting a raw content locator."""
    return (
        f"{SUBJECT_PREFIX}:{context.acceptance_context_id}:"
        f"instrument:{context.instrument_id}:{context.instrument_version}:"
        f"content:{context.content_fingerprint}:intent:{intent_fingerprint[:32]}"
    )


def _authorization_fingerprint(
    *, context: LegalClientAcceptanceContext, intent_fingerprint: str
) -> str:
    """Bind IAM evidence to the exact context and acceptance intent."""
    payload = {
        "context_fingerprint": context.fingerprint,
        "intent_fingerprint": intent_fingerprint,
        "acceptance_context_id": context.acceptance_context_id,
    }
    return hashlib.sha3_512(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _revalidate(
    *,
    context: LegalClientAcceptanceContext,
    tenant: str,
    principal: str,
    collections: tuple[Any, Any, Any, Any, Any, Any, Any],
    repositories: tuple[Any, Any, Any, Any],
    session: Any,
    at: datetime,
) -> None:
    """Run the certified P2D complete dependency revalidation unchanged."""
    try:
        _revalidate_dependencies(
            context=context,
            tenant=tenant,
            principal=principal,
            matter_collection=collections[0],
            visibility_collection=collections[1],
            party_collection=collections[2],
            capacity_collection=collections[3],
            instrument_collection=collections[4],
            lifecycle_collection=collections[5],
            approval_collection=collections[6],
            session=session,
            at=at,
            principal_repository=repositories[0],
            membership_repository=repositories[1],
            business_role_repository=repositories[2],
            role_assignment_repository=repositories[3],
        )
    except LegalClientAcceptanceOrchestrationError:
        raise
    except Exception as error:
        code = getattr(error, "code", None)
        if isinstance(code, str) and code.startswith("L9A4_"):
            _fail(code, error)
        _fail("L9A3_DEPENDENCY_REVALIDATION_FAILED", error)


def issue_legal_client_acceptance(
    *,
    identity: SovereignIdentity,
    acceptance_context_id: str,
    confirmed: bool,
    idempotency_key: str,
    context_collection: Any,
    matter_lifecycle_collection: Any,
    visibility_collection: Any,
    party_collection: Any,
    capacity_collection: Any,
    instrument_collection: Any,
    instrument_lifecycle_collection: Any,
    approval_collection: Any,
    acceptance_collection: Any,
    authorization_evidence_registry: TenantAuthorizationDecisionEvidenceRegistry,
    principal_repository: Any,
    membership_repository: Any,
    business_role_repository: Any,
    role_assignment_repository: Any,
    session: Any,
    clock: Clock | None = None,
) -> LegalClientAcceptance:
    """Issue or exactly replay one context-bound client acceptance.

    Only ``identity``, an opaque ``acceptance_context_id``, strict
    ``confirmed=True``, a bounded ``idempotency_key`` and the caller-owned
    active session are request authority. Tenant, principal, matter, party,
    subject, acting capacity, scope, source provenance and accepted time are
    loaded or derived from the persisted context and current authorities. The
    exact session is forwarded to every read/write. This function owns no
    transaction lifecycle and creates no engagement, representation, Court or
    financial authority.
    """
    tx = _active_session(session)
    tenant, principal = _identity(identity)
    context_id = _text("acceptance_context_id", acceptance_context_id)
    intent = _text("idempotency_key", idempotency_key)
    if type(confirmed) is not bool or confirmed is not True:
        _fail("L9A3_EXPLICIT_CONFIRMATION_REQUIRED")
    collections = (
        matter_lifecycle_collection,
        visibility_collection,
        party_collection,
        capacity_collection,
        instrument_collection,
        instrument_lifecycle_collection,
        approval_collection,
    )
    if context_collection is None or acceptance_collection is None or any(
        value is None for value in collections
    ):
        _fail("L9A3_COLLECTION_REQUIRED")
    if not callable(getattr(authorization_evidence_registry, "issue", None)):
        _fail("L9A3_AUTHORIZATION_EVIDENCE_REGISTRY_REQUIRED")

    at = _now(clock)
    context = _context(
        tenant=tenant, context_id=context_id, at=at,
        collection=context_collection, session=tx,
    )
    if context.actor_principal_id != principal:
        _fail("L9A3_CONTEXT_ACTOR_MISMATCH")
    _revalidate(
        context=context,
        tenant=tenant,
        principal=principal,
        collections=collections,
        repositories=(
            principal_repository,
            membership_repository,
            business_role_repository,
            role_assignment_repository,
        ),
        session=tx,
        at=at,
    )
    try:
        matter = _matter(
            tenant=tenant,
            matter_id=context.case_matter_id,
            collection=matter_lifecycle_collection,
            session=tx,
        )
    except Exception as error:
        code = getattr(error, "code", None)
        _fail(
            code
            if isinstance(code, str) and code.startswith("L9A4_")
            else "L9A3_CASE_MATTER_UNAVAILABLE",
            error,
        )

    acceptance_identity = _acceptance_id(context.acceptance_context_id)
    intent_fingerprint = _intent_fingerprint(
        context=context, idempotency_key=intent, confirmed=confirmed
    )
    source_reference = _source_reference(
        context=context, intent_fingerprint=intent_fingerprint
    )
    authorization_subject = (
        f"{AUTHORIZATION_SUBJECT_PREFIX}:{context.acceptance_context_id}"
    )
    authorization_fingerprint = _authorization_fingerprint(
        context=context, intent_fingerprint=intent_fingerprint
    )
    try:
        authorization = authorization_evidence_registry.issue(
            tenant_id=tenant,
            principal_id=principal,
            operation=OPERATION,
            permission=PERMISSION,
            subject_reference=authorization_subject,
            subject_evidence_fingerprint=authorization_fingerprint,
            idempotency_key=authorization_subject,
            session=tx,
        )
    except TenantAuthorizationDecisionEvidenceAuthorizationDeniedError as error:
        _fail("L9A3_CLIENT_AUTHORIZATION_REQUIRED", error)
    except TenantAuthorizationDecisionEvidenceTransactionRequiredError as error:
        _fail("L9A3_ACTIVE_TRANSACTION_REQUIRED", error)
    except TenantAuthorizationDecisionEvidenceConflictError as error:
        _fail("L9A3_AUTHORIZATION_REPLAY_CONFLICT", error)
    except (
        TenantAuthorizationDecisionEvidencePersistenceError,
        TenantAuthorizationDecisionEvidenceRegistryError,
    ) as error:
        _fail("L9A3_AUTHORIZATION_EVIDENCE_UNAVAILABLE", error)
    except Exception as error:
        _fail("L9A3_AUTHORIZATION_EVIDENCE_UNAVAILABLE", error)
    if (
        getattr(authorization, "tenant_id", None) != tenant
        or getattr(authorization, "principal_id", None) != principal
        or getattr(authorization, "operation", None) != OPERATION
        or getattr(authorization, "permission", None) != PERMISSION
        or getattr(authorization, "subject_reference", None) != authorization_subject
        or getattr(authorization, "subject_evidence_fingerprint", None)
        != authorization_fingerprint
    ):
        _fail("L9A3_AUTHORIZATION_CORRELATION_INVALID")

    accepted_at = at
    try:
        existing = LegalClientAcceptanceRegistry.get_acceptance(
            tenant, acceptance_identity, acceptance_collection, session=tx
        )
    except LegalClientAcceptanceRegistryNotFoundError:
        existing = None
    except LegalClientAcceptanceRegistryError as error:
        _fail("L9A3_ACCEPTANCE_READ_UNAVAILABLE", error)
    if existing is not None:
        accepted_at = existing.accepted_at
    try:
        value = record_legal_client_acceptance(
            case_matter=matter,
            acceptance_id=acceptance_identity,
            party_id=context.party_id,
            subject_reference=context.subject_reference,
            subject_identity_fingerprint=context.subject_identity_fingerprint,
            acceptance_scope=context.acceptance_scope,
            actor_principal_id=principal,
            accepted_at=accepted_at,
            source_evidence_reference=source_reference,
            source_evidence_fingerprint=context.content_fingerprint,
        )
    except (LegalClientAcceptanceError, TypeError, ValueError) as error:
        _fail("L9A3_ACCEPTANCE_INVALID", error)
    try:
        persisted = LegalClientAcceptanceRegistry.persist_acceptance(
            value, acceptance_collection, session=tx
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
    if persisted.to_dict() != value.to_dict():
        _fail("L9A3_POST_WRITE_CORRELATION_INVALID")
    return persisted


__all__ = [
    "OPERATION",
    "PERMISSION",
    "AUTHORIZATION_SUBJECT_PREFIX",
    "SUBJECT_PREFIX",
    "VERSION",
    "LegalClientAcceptanceOrchestrationError",
    "LegalClientAcceptanceOrchestrationRetryRequiredError",
    "issue_legal_client_acceptance",
]


# ARTIFACT: legal_client_acceptance_orchestrator.py
# VERSION: v1.1.0-L9A3-R1-CONTEXT-BOUND-ACCEPTANCE
# AUTHORITY BOUNDARY: context-bound immutable client-acceptance issuance only
# TENANT POSTURE: exact authenticated identity + tenant-scoped context and current dependencies
# FAIL-CLOSED POSTURE: false confirmation, stale authority, divergence and persistence uncertainty reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
