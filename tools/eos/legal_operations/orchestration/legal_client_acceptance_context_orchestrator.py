"""TITLE: WILSY OS Authorized Legal Client Acceptance Context Composer.
VERSION: v1.0.0-L9A4-P2C3-CLIENT-ACCEPTANCE-CONTEXT-COMPOSER
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations.
EPITOME: Compose and durably persist one server-derived client review context
         only after current IAM, visibility, OPEN matter, exact party/capacity,
         latest instrument, ACTIVE lifecycle and APPROVED decision evidence are
         re-read inside one caller-owned Mongo transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_acceptance_context_orchestrator.py
COLLABORATION / OWNERSHIP: IAM owns current authorization and membership;
                            visibility owns client-to-matter access; CaseMatter,
                            party, acting-capacity, instrument, lifecycle and
                            approval registries own their source truth; P2C2
                            owns context durability. This module composes
                            those authorities and creates no second truth.
CERTIFICATION / UPDATE DATE: 2026-09-26.
CHANGELOG: v1.0.0-L9A4-P2C3 establishes authenticated LEGAL_CLIENT context
           composition, exact server-side party/capacity selection, latest
           effective instrument gating, current ACTIVE/APPROVED checks,
           caller-owned transaction/session propagation, deterministic replay,
           and bounded ten-minute context expiry. It creates no ClientAcceptance,
           Engagement, Representation, Court, delivery, HTTP, or financial
           authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Tenant and principal come only from active
                             SovereignIdentity. Caller fields are opaque
                             identifiers; party, subject, fingerprints, raw
                             content reference, lifecycle and approval evidence
                             are always server-derived. No credentials, JWTs,
                             bearer tokens or raw client PII are accepted.
TENANT BOUNDARY: Every IAM, visibility, lifecycle, party, capacity,
                 instrument, approval, evidence and context operation is bound
                 to the exact identity tenant and the same caller session.
AUTHORITY BOUNDARY: Client review/acceptance-context evidence composition and
                    its issuer authorization evidence only. A context is not
                    acceptance, engagement, representation, Court readiness,
                    content delivery or a financial instruction.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement.
TRANSACTION BOUNDARY: The caller must supply and own an already-active Mongo
                      transaction. This module never starts, commits, aborts,
                      retries, or reconciles a transaction.
FAIL-CLOSED DECLARATION: Missing/inactive IAM, absent visibility, closed or
                         ambiguous source history, stale instrument, terminal
                         lifecycle, missing/rejected/ambiguous approval,
                         divergent replay or persistence uncertainty rejects.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Final, NoReturn, Protocol, cast

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceAuthorizationDeniedError,
    TenantAuthorizationDecisionEvidenceConflictError,
    TenantAuthorizationDecisionEvidencePersistenceError,
    TenantAuthorizationDecisionEvidenceRegistry,
    TenantAuthorizationDecisionEvidenceRegistryError,
    TenantAuthorizationDecisionEvidenceTransactionRequiredError,
)
from tools.eos.legal_operations.domain.legal_client_acceptance_context import (
    LegalClientAcceptanceContext,
    LegalClientAcceptanceContextError,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_approval import (
    LegalClientMatterAcceptanceInstrumentApprovalDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_lifecycle import (
    LegalClientMatterAcceptanceInstrumentLifecycleStatus,
)
from tools.eos.legal_operations.domain.legal_operations_current_projection import (
    resolve_current_lifecycle_snapshot,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.registry import (
    legal_client_acceptance_context_registry as context_registry,
    legal_client_acting_capacity_registry as capacity_registry,
    legal_client_matter_acceptance_instrument_approval_registry as approval_registry,
    legal_client_matter_acceptance_instrument_lifecycle_registry as lifecycle_registry,
    legal_client_matter_acceptance_instrument_registry as instrument_registry,
    legal_client_matter_visibility_registry as visibility_registry,
    legal_matter_party_registry as party_registry,
    legal_operations_lifecycle_registry as matter_registry,
)


VERSION: Final[str] = "v1.0.0-L9A4-P2C3-CLIENT-ACCEPTANCE-CONTEXT-COMPOSER"
PERMISSION: Final[str] = "legal_operations:client_matter:read"
OPERATION: Final[str] = "legal_client_matter_read"
CONTEXT_LIFETIME: Final[timedelta] = timedelta(minutes=10)
AUTHORIZATION_SUBJECT_PREFIX: Final[str] = "legal-client-acceptance-context"
UTC = timezone.utc


class LegalClientAcceptanceContextOrchestrationError(RuntimeError):
    """Stable fail-closed P2C3 error containing no supplied-value payload."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded semantic code; retain technical causes privately."""
        self.code = code
        super().__init__(code)


class LegalClientAcceptanceContextOrchestrationRetryRequiredError(
    LegalClientAcceptanceContextOrchestrationError
):
    """Caller must abort and restart the complete transaction from fresh state."""


class AuthorizationEvidenceIssuer(Protocol):
    """Minimal durable issuer seam; transaction lifecycle remains caller-owned."""

    def issue(self, **kwargs: object) -> object:
        """Issue or exactly replay authorization evidence in the caller session."""


Clock = Callable[[], datetime]


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise a bounded orchestration code while retaining only an internal cause."""
    error = LegalClientAcceptanceContextOrchestrationError(code)
    if cause is None:
        raise error
    raise error from cause


def _retry(code: str, cause: BaseException) -> NoReturn:
    """Convert a registry race into caller-owned whole-transaction retry."""
    raise LegalClientAcceptanceContextOrchestrationRetryRequiredError(code) from cause


def _text(name: str, value: object) -> str:
    """Require one bounded opaque identity without coercion or trimming."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"L9A4_P2C3_{name.upper()}_INVALID")
    return value


def _active_transaction(session: Any) -> Any:
    """Require one already-active caller-owned transaction before any read."""
    if session is None:
        _fail("L9A4_P2C3_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _fail("L9A4_P2C3_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _identity(identity: SovereignIdentity) -> tuple[str, str]:
    """Derive exact tenant/principal only from an active authenticated identity."""
    if not isinstance(identity, SovereignIdentity):
        _fail("L9A4_P2C3_IDENTITY_REQUIRED")
    if identity.status is not PrincipalStatus.ACTIVE:
        _fail("L9A4_P2C3_PRINCIPAL_INACTIVE")
    return _text("tenant_id", identity.tenant_id), _text("principal_id", identity.identity_id)


def _utc_now(clock: Clock | None) -> datetime:
    """Read one server clock instant and reject naive or invalid clock output."""
    value = datetime.now(UTC) if clock is None else clock()
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail("L9A4_P2C3_SERVER_CLOCK_INVALID")
    return value.astimezone(UTC)


def _current_case_matter(
    *, tenant_id: str, case_matter_id: str, collection: Any, session: Any
) -> CaseMatter:
    """Resolve exact current CaseMatter and require OPEN state."""
    try:
        history = matter_registry.LegalOperationsLifecycleRegistry.get_entity_history(
            tenant_id, "CaseMatter", case_matter_id, collection, session=session
        )
        value = resolve_current_lifecycle_snapshot(history, expected_type=CaseMatter)
    except Exception as error:
        _fail("L9A4_P2C3_CASE_MATTER_UNAVAILABLE", error)
    if type(value) is not CaseMatter:
        _fail("L9A4_P2C3_CASE_MATTER_TYPE_INVALID")
    if value.tenant_id != tenant_id or value.case_matter_id != case_matter_id:
        _fail("L9A4_P2C3_CASE_MATTER_SCOPE_MISMATCH")
    if value.state is not CaseMatterState.OPEN:
        _fail("L9A4_P2C3_CASE_MATTER_NOT_OPEN")
    return value


def _authorize_client(
    *,
    tenant_id: str,
    principal_id: str,
    principal_repository: Any,
    membership_repository: Any,
    business_role_repository: Any,
    role_assignment_repository: Any,
    session: Any,
) -> None:
    """Require the certified exact LEGAL_CLIENT matter-read IAM conjunction."""
    try:
        decision = authorize_tenant_operation(
            principal_id=principal_id,
            tenant_id=tenant_id,
            permission_id=PERMISSION,
            operation=OPERATION,
            principal_repository=principal_repository,
            membership_repository=membership_repository,
            business_role_repository=business_role_repository,
            role_assignment_repository=role_assignment_repository,
            session=session,
        )
    except Exception as error:
        _fail("L9A4_P2C3_CLIENT_AUTHORIZATION_UNAVAILABLE", error)
    if (
        decision.authorized is not True
        or decision.reason is not TenantAuthorizationReason.AUTHORIZED
        or decision.business_role != "tenant_legal_client"
        or decision.authorization_role != "LEGAL_CLIENT"
    ):
        _fail("L9A4_P2C3_LEGAL_CLIENT_AUTHORIZATION_REQUIRED")


def _require_visibility(
    *, tenant_id: str, principal_id: str, case_matter_id: str, collection: Any, session: Any
) -> None:
    """Require the exact current ACTIVE client-to-matter visibility relation."""
    try:
        value = visibility_registry.LegalClientMatterVisibilityRegistry.resolve_current_active(
            tenant_id, principal_id, case_matter_id, collection, session=session
        )
    except visibility_registry.LegalClientMatterVisibilityNotFoundError as error:
        _fail("L9A4_P2C3_ACTIVE_VISIBILITY_REQUIRED", error)
    except visibility_registry.LegalClientMatterVisibilityRegistryError as error:
        _fail("L9A4_P2C3_VISIBILITY_UNAVAILABLE", error)
    if (
        value.tenant_id != tenant_id
        or value.client_principal_id != principal_id
        or value.case_matter_id != case_matter_id
    ):
        _fail("L9A4_P2C3_VISIBILITY_SCOPE_MISMATCH")


def _resolve_party_and_capacity(
    *, tenant_id: str, principal_id: str, case_matter: CaseMatter, party_collection: Any,
    capacity_collection: Any, issued_at: datetime, session: Any,
) -> tuple[Any, Any]:
    """Correlate exactly one valid actor capacity to exactly one matter party."""
    try:
        parties = party_registry.list_matter_parties(
            tenant_id, case_matter.case_matter_id, party_collection, session=session
        )
        capacities = capacity_registry.list_valid_capacities_at(
            tenant_id, case_matter.case_matter_id, issued_at, capacity_collection, session=session
        )
    except Exception as error:
        _fail("L9A4_P2C3_PARTY_OR_CAPACITY_UNAVAILABLE", error)
    by_party = {party.party_id: party for party in parties}
    matches = [
        (by_party[capacity.party_id], capacity)
        for capacity in capacities
        if capacity.principal_id == principal_id
        and capacity.party_id in by_party
        and by_party[capacity.party_id].subject_reference == capacity.subject_reference
        and by_party[capacity.party_id].subject_identity_fingerprint
        == capacity.subject_identity_fingerprint
        and by_party[capacity.party_id].tenant_id == tenant_id
        and by_party[capacity.party_id].case_matter_id == case_matter.case_matter_id
        and by_party[capacity.party_id].matter_fingerprint == case_matter.fingerprint
    ]
    if not matches:
        _fail("L9A4_P2C3_PARTY_CAPACITY_NOT_FOUND")
    if len(matches) != 1:
        _fail("L9A4_P2C3_PARTY_CAPACITY_AMBIGUOUS")
    return matches[0]


def _select_instrument(
    *, tenant_id: str, case_matter: CaseMatter, instrument_id: str, collection: Any,
    issued_at: datetime, session: Any,
) -> Any:
    """Select only the latest effective unsuperseded version of caller's chain."""
    try:
        value = instrument_registry.get_latest_effective_version(
            tenant_id, case_matter.case_matter_id, instrument_id, issued_at, collection, session=session
        )
    except Exception as error:
        _fail("L9A4_P2C3_INSTRUMENT_UNAVAILABLE", error)
    if value is None:
        _fail("L9A4_P2C3_LATEST_INSTRUMENT_REQUIRED")
    if (
        value.tenant_id != tenant_id
        or value.case_matter_id != case_matter.case_matter_id
        or value.matter_fingerprint != case_matter.fingerprint
        or value.effective_from > issued_at
    ):
        _fail("L9A4_P2C3_INSTRUMENT_SCOPE_MISMATCH")
    return value


def _current_lifecycle(
    *, tenant_id: str, case_matter: CaseMatter, instrument: Any, collection: Any, session: Any
) -> Any:
    """Require exact current ACTIVE lifecycle for the selected instrument."""
    try:
        value = lifecycle_registry.get_current_lifecycle(
            tenant_id, case_matter.case_matter_id, instrument.instrument_id,
            instrument.version, collection, session=session
        )
    except Exception as error:
        _fail("L9A4_P2C3_LIFECYCLE_UNAVAILABLE", error)
    if value is None or value.status is not LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE:
        _fail("L9A4_P2C3_INSTRUMENT_NOT_ACTIVE")
    if (
        value.tenant_id != tenant_id
        or value.case_matter_id != case_matter.case_matter_id
        or value.instrument_fingerprint != instrument.fingerprint
        or value.matter_fingerprint != case_matter.fingerprint
    ):
        _fail("L9A4_P2C3_LIFECYCLE_SCOPE_MISMATCH")
    return value


def _current_approval(
    *, tenant_id: str, case_matter: CaseMatter, instrument: Any, collection: Any,
    issued_at: datetime, session: Any,
) -> Any:
    """Require the exact latest effective APPROVED decision at issuance time."""
    try:
        value = approval_registry.get_current_approval(
            tenant_id, case_matter.case_matter_id, instrument.instrument_id,
            instrument.version, instrument.fingerprint, instrument.content_fingerprint,
            collection, at=issued_at, session=session,
        )
    except Exception as error:
        _fail("L9A4_P2C3_APPROVAL_UNAVAILABLE", error)
    if value is None:
        _fail("L9A4_P2C3_CURRENT_APPROVAL_REQUIRED")
    if (
        value.tenant_id != tenant_id
        or value.case_matter_id != case_matter.case_matter_id
        or value.instrument_id != instrument.instrument_id
        or value.version != instrument.version
        or value.instrument_fingerprint != instrument.fingerprint
        or value.content_fingerprint != instrument.content_fingerprint
        or value.decision is not LegalClientMatterAcceptanceInstrumentApprovalDecision.APPROVED
        or value.effective_from > issued_at
    ):
        _fail("L9A4_P2C3_APPROVAL_SCOPE_MISMATCH")
    return value


def _issuer_fingerprint(
    *, tenant_id: str, principal_id: str, context_id: str, replay_key: str,
    case_matter: CaseMatter, party: Any, capacity: Any, instrument: Any,
    lifecycle: Any, approval: Any,
) -> str:
    """Fingerprint every server-derived source and the caller replay identity."""
    payload = {
        "tenant_id": tenant_id,
        "principal_id": principal_id,
        "context_id": context_id,
        "replay_key": replay_key,
        "case_matter_id": case_matter.case_matter_id,
        "matter_fingerprint": case_matter.fingerprint,
        "party_id": party.party_id,
        "party_fingerprint": party.fingerprint,
        "capacity_id": capacity.capacity_id,
        "capacity_fingerprint": capacity.fingerprint,
        "instrument_id": instrument.instrument_id,
        "instrument_version": instrument.version,
        "instrument_fingerprint": instrument.fingerprint,
        "content_fingerprint": instrument.content_fingerprint,
        "lifecycle_fingerprint": lifecycle.fingerprint,
        "approval_id": approval.approval_id,
        "approval_fingerprint": approval.fingerprint,
    }
    return hashlib.sha3_512(
        json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _find_replay(
    *, tenant_id: str, principal_id: str, context_id: str, replay_key: str,
    case_matter_id: str, instrument_id: str, collection: Any, session: Any,
) -> LegalClientAcceptanceContext | None:
    """Find one actor-scoped replay and reject divergent identity reuse."""
    try:
        values = context_registry.list_contexts_for_actor(
            tenant_id, principal_id, collection, session=session,
        )
    except context_registry.LegalClientAcceptanceContextRegistryNotFoundError:
        return None
    except context_registry.LegalClientAcceptanceContextRegistryError as error:
        _fail("L9A4_P2C3_CONTEXT_REPLAY_READ_UNAVAILABLE", error)
    matches = tuple(value for value in values if value.replay_key == replay_key)
    if len(matches) > 1:
        _fail("L9A4_P2C3_CONTEXT_REPLAY_AMBIGUOUS")
    if not matches:
        return None
    value = matches[0]
    if (
        value.acceptance_context_id != context_id
        or value.case_matter_id != case_matter_id
        or value.instrument_id != instrument_id
        or value.tenant_id != tenant_id
        or value.actor_principal_id != principal_id
    ):
        _fail("L9A4_P2C3_CONTEXT_REPLAY_CONFLICT")
    return value


def _issue_authorization(
    *, tenant_id: str, principal_id: str, context_id: str, replay_key: str,
    subject_fingerprint: str, issuer: AuthorizationEvidenceIssuer, session: Any,
) -> object:
    """Persist or exactly replay the issuer authorization evidence."""
    try:
        return issuer.issue(
            tenant_id=tenant_id,
            principal_id=principal_id,
            operation=OPERATION,
            permission=PERMISSION,
            subject_reference=f"{AUTHORIZATION_SUBJECT_PREFIX}:{context_id}",
            subject_evidence_fingerprint=subject_fingerprint,
            idempotency_key=f"{AUTHORIZATION_SUBJECT_PREFIX}:{replay_key}",
            session=session,
        )
    except TenantAuthorizationDecisionEvidenceAuthorizationDeniedError as error:
        _fail("L9A4_P2C3_LEGAL_CLIENT_AUTHORIZATION_REQUIRED", error)
    except TenantAuthorizationDecisionEvidenceTransactionRequiredError as error:
        _fail("L9A4_P2C3_ACTIVE_TRANSACTION_REQUIRED", error)
    except TenantAuthorizationDecisionEvidenceConflictError as error:
        _fail("L9A4_P2C3_ISSUER_REPLAY_CONFLICT", error)
    except (
        TenantAuthorizationDecisionEvidencePersistenceError,
        TenantAuthorizationDecisionEvidenceRegistryError,
        AttributeError,
    ) as error:
        _fail("L9A4_P2C3_ISSUER_EVIDENCE_UNAVAILABLE", error)


def compose_legal_client_acceptance_context(
    *,
    identity: SovereignIdentity,
    case_matter_id: str,
    acceptance_context_id: str,
    replay_key: str,
    instrument_id: str,
    matter_lifecycle_collection: Any,
    visibility_collection: Any,
    party_collection: Any,
    capacity_collection: Any,
    instrument_collection: Any,
    instrument_lifecycle_collection: Any,
    approval_collection: Any,
    context_collection: Any,
    authorization_evidence_registry: AuthorizationEvidenceIssuer,
    principal_repository: Any,
    membership_repository: Any,
    business_role_repository: Any,
    role_assignment_repository: Any,
    session: Any,
    clock: Clock | None = None,
) -> LegalClientAcceptanceContext:
    """Compose or exactly replay one authorized durable acceptance context.

    ``identity`` supplies only authenticated tenant/principal identity. The
    caller supplies opaque matter/context/replay/instrument identifiers; all
    party, capacity, subject, instrument version, lifecycle, approval,
    fingerprints, content reference and chronology are server-derived. Every
    read, issuer-evidence write and context write receives the exact active
    ``session``. The caller owns commit, abort, retry and unknown-commit
    reconciliation. This method never records ClientAcceptance and has no
    Engagement, Representation, Court, HTTP, delivery or financial authority.
    """
    tx = _active_transaction(session)
    tenant, principal = _identity(identity)
    matter_id = _text("case_matter_id", case_matter_id)
    context_id = _text("acceptance_context_id", acceptance_context_id)
    replay = _text("replay_key", replay_key)
    instrument_identity = _text("instrument_id", instrument_id)
    collections = (
        matter_lifecycle_collection, visibility_collection, party_collection,
        capacity_collection, instrument_collection, instrument_lifecycle_collection,
        approval_collection, context_collection,
    )
    if any(value is None for value in collections):
        _fail("L9A4_P2C3_COLLECTION_REQUIRED")

    _authorize_client(
        tenant_id=tenant, principal_id=principal,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        business_role_repository=business_role_repository,
        role_assignment_repository=role_assignment_repository,
        session=tx,
    )
    _require_visibility(
        tenant_id=tenant, principal_id=principal, case_matter_id=matter_id,
        collection=visibility_collection, session=tx,
    )

    replayed = _find_replay(
        tenant_id=tenant, principal_id=principal, context_id=context_id,
        replay_key=replay, case_matter_id=matter_id, instrument_id=instrument_identity,
        collection=context_collection, session=tx,
    )
    issued_at = replayed.issued_at if replayed is not None else _utc_now(clock)
    expires_at = replayed.expires_at if replayed is not None else issued_at + CONTEXT_LIFETIME
    matter = _current_case_matter(
        tenant_id=tenant, case_matter_id=matter_id,
        collection=matter_lifecycle_collection, session=tx,
    )
    party, capacity = _resolve_party_and_capacity(
        tenant_id=tenant, principal_id=principal, case_matter=matter,
        party_collection=party_collection, capacity_collection=capacity_collection,
        issued_at=issued_at, session=tx,
    )
    instrument = _select_instrument(
        tenant_id=tenant, case_matter=matter, instrument_id=instrument_identity,
        collection=instrument_collection, issued_at=issued_at, session=tx,
    )
    lifecycle = _current_lifecycle(
        tenant_id=tenant, case_matter=matter, instrument=instrument,
        collection=instrument_lifecycle_collection, session=tx,
    )
    approval = _current_approval(
        tenant_id=tenant, case_matter=matter, instrument=instrument,
        collection=approval_collection, issued_at=issued_at, session=tx,
    )
    subject_fingerprint = _issuer_fingerprint(
        tenant_id=tenant, principal_id=principal, context_id=context_id,
        replay_key=replay, case_matter=matter, party=party, capacity=capacity,
        instrument=instrument, lifecycle=lifecycle, approval=approval,
    )
    authorization = _issue_authorization(
        tenant_id=tenant, principal_id=principal, context_id=context_id,
        replay_key=replay, subject_fingerprint=subject_fingerprint,
        issuer=authorization_evidence_registry, session=tx,
    )
    authorization_tenant = getattr(authorization, "tenant_id", None)
    authorization_principal = getattr(authorization, "principal_id", None)
    evidence_reference = getattr(authorization, "authorization_evidence_reference", None)
    evidence_fingerprint = getattr(authorization, "authorization_evidence_fingerprint", None)
    if (
        authorization_tenant != tenant
        or authorization_principal != principal
        or getattr(authorization, "operation", None) != OPERATION
        or getattr(authorization, "permission", None) != PERMISSION
        or evidence_reference is None
        or evidence_fingerprint is None
    ):
        _fail("L9A4_P2C3_ISSUER_CORRELATION_INVALID")
    try:
        value = LegalClientAcceptanceContext.from_canonical(
            acceptance_context_id=context_id,
            actor_principal_id=principal,
            case_matter=matter,
            party=party,
            acting_capacity=capacity,
            instrument=instrument,
            lifecycle=lifecycle,
            approval=approval,
            issued_at=issued_at,
            expires_at=expires_at,
            replay_key=replay,
            issuer_evidence_reference=cast(str, evidence_reference),
            issuer_evidence_fingerprint=cast(str, evidence_fingerprint),
        )
    except (LegalClientAcceptanceContextError, TypeError, ValueError) as error:
        _fail("L9A4_P2C3_CONTEXT_INVALID", error)
    if replayed is not None and value.to_dict() != replayed.to_dict():
        _fail("L9A4_P2C3_CONTEXT_REPLAY_CONFLICT")
    try:
        persisted = context_registry.persist_context(value, context_collection, session=tx)
    except context_registry.LegalClientAcceptanceContextRegistryRetryRequiredError as error:
        _retry("L9A4_P2C3_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    except context_registry.LegalClientAcceptanceContextRegistryConflictError as error:
        _fail("L9A4_P2C3_CONTEXT_REPLAY_CONFLICT", error)
    except context_registry.LegalClientAcceptanceContextRegistryError as error:
        _fail("L9A4_P2C3_CONTEXT_PERSISTENCE_UNAVAILABLE", error)
    if persisted.to_dict() != value.to_dict():
        _fail("L9A4_P2C3_POST_WRITE_CORRELATION_INVALID")
    return persisted


__all__ = [
    "AUTHORIZATION_SUBJECT_PREFIX",
    "CONTEXT_LIFETIME",
    "OPERATION",
    "PERMISSION",
    "VERSION",
    "LegalClientAcceptanceContextOrchestrationError",
    "LegalClientAcceptanceContextOrchestrationRetryRequiredError",
    "compose_legal_client_acceptance_context",
]


# ARTIFACT: legal_client_acceptance_context_orchestrator.py
# VERSION: v1.0.0-L9A4-P2C3-CLIENT-ACCEPTANCE-CONTEXT-COMPOSER
# AUTHORITY BOUNDARY: authenticated client review-context composition only
# TENANT POSTURE: exact identity tenant + principal + active visibility + source correlations
# FAIL-CLOSED POSTURE: inactive/ambiguous/stale/terminal/denied/divergent/uncertain requests reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
