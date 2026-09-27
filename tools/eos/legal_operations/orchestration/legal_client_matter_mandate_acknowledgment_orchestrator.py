"""Issue one authorized firm acknowledgment for an exact client grant.

TITLE: WILSY OS Firm Mandate Acknowledgment Issuance Orchestrator
VERSION: v1.0.0-L9B10-P7-FIRM-MANDATE-ACKNOWLEDGMENT-ISSUANCE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Derive authenticated tenant/principal authority, issue durable IAM
         evidence, require current grant and acknowledgment history, and append
         one immutable acknowledgment in the caller's transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_matter_mandate_acknowledgment_orchestrator.py
COLLABORATION / OWNERSHIP: SovereignIdentity supplies authenticated identity;
                            IAM evidence owns authorization; grant and
                            acknowledgment registries own durable evidence;
                            currentness composers own read-only state selection.
                            This module owns only their bounded composition.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B10-P7 establishes caller-owned transactional issuance,
           exact IAM subject intent, current grant/history gating, deterministic
           replay identity, immutable factory construction and post-write
           reconciliation. No mandate, Engagement, Representation, Court,
           HTTP, UI, Node or financial authority is created.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only bounded opaque references and SHA3-512
                             fingerprints cross the boundary; errors expose
                             stable codes and never echo caller values.
TENANT BOUNDARY: Tenant and principal come only from active SovereignIdentity;
                 every canonical read, IAM evidence and append is exact tenant
                 and grant scoped under one caller session.
AUTHORITY BOUNDARY: Authorized immutable acknowledgment issuance only. The
                    acknowledgment is not a mandate, engagement, representation,
                    court authority, client acceptance or financial approval.
FINANCIAL AUTHORITY BOUNDARY: No payment, release, settlement or execution;
                              Kennel EOS remains exclusive financial authority.
TRANSACTION BOUNDARY: Caller supplies and owns the active transaction. This
                      orchestrator never starts, commits, aborts, retries or
                      reconciles a whole transaction.
FAIL-CLOSED DECLARATION: Missing authority, stale/corrupt evidence, divergent
                         replay, malformed provenance and persistence uncertainty
                         reject without cross-tenant disclosure or fallback.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
import re
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
from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment import (
    LegalClientMatterMandateAcknowledgment,
    LegalClientMatterMandateAcknowledgmentDecision,
    LegalClientMatterMandateAcknowledgmentError,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment_currentness import (
    LegalClientMatterMandateAcknowledgmentCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_currentness import (
    LegalClientMatterMandateGrantCurrentnessState,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_mandate_acknowledgment_currentness_composer import (
    LegalClientMatterMandateAcknowledgmentCurrentnessComposer,
    LegalClientMatterMandateAcknowledgmentCurrentnessComposerError,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_mandate_grant_currentness_composer import (
    LegalClientMatterMandateGrantCurrentnessComposer,
    LegalClientMatterMandateGrantCurrentnessComposerError,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_mandate_acknowledgment_registry as acknowledgment_registry,
    legal_client_matter_mandate_grant_registry as grant_registry,
)


VERSION: Final[str] = "v1.0.0-L9B10-P7-FIRM-MANDATE-ACKNOWLEDGMENT-ISSUANCE"
OPERATION: Final[str] = "legal_matter_mandate_acknowledgment_write"
PERMISSION: Final[str] = "legal_operations:matter_mandate_acknowledgment:write"
SUBJECT_PREFIX: Final[str] = "legal-matter-mandate-acknowledgment"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_FINGERPRINT = re.compile(r"^[0-9a-f]{128}$")
_MAX_REFERENCE: Final[int] = 512
_MAX_IDEMPOTENCY: Final[int] = 240


class LegalClientMatterMandateAcknowledgmentOrchestrationError(RuntimeError):
    """Stable non-sensitive fail-closed issuer error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientMatterMandateAcknowledgmentOrchestrationRetryRequiredError(
    LegalClientMatterMandateAcknowledgmentOrchestrationError
):
    """The caller must abort and restart the complete transaction."""


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalClientMatterMandateAcknowledgmentOrchestrationError(code)
    if cause is None:
        raise error
    raise error from cause


def _retry(code: str, cause: BaseException) -> NoReturn:
    raise LegalClientMatterMandateAcknowledgmentOrchestrationRetryRequiredError(code) from cause


def _active_transaction(session: Any) -> Any:
    if session is None:
        _fail("L9B10_P7_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _fail("L9B10_P7_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _identity(identity: object) -> tuple[str, str]:
    if not isinstance(identity, SovereignIdentity):
        _fail("L9B10_P7_IDENTITY_REQUIRED")
    if identity.status is not PrincipalStatus.ACTIVE:
        _fail("L9B10_P7_PRINCIPAL_INACTIVE")
    tenant = identity.tenant_id
    principal = identity.identity_id
    if not isinstance(tenant, str) or _IDENTITY.fullmatch(tenant) is None:
        _fail("L9B10_P7_TENANT_INVALID")
    if not isinstance(principal, str) or _IDENTITY.fullmatch(principal) is None:
        _fail("L9B10_P7_PRINCIPAL_INVALID")
    return tenant, principal


def _opaque(name: str, value: object, *, limit: int = _MAX_REFERENCE) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(ord(char) < 32 or 0x7F <= ord(char) <= 0x9F or 0xD800 <= ord(char) <= 0xDFFF for char in value)
    ):
        _fail(f"L9B10_P7_{name.upper()}_INVALID")
    return value


def _grant_identity(value: object) -> str:
    if not isinstance(value, str) or _IDENTITY.fullmatch(value) is None:
        _fail("L9B10_P7_CLIENT_GRANT_ID_INVALID")
    return value


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _FINGERPRINT.fullmatch(value) is None:
        _fail(f"L9B10_P7_{name.upper()}_INVALID")
    return value


def _decision(value: object) -> str:
    try:
        return LegalClientMatterMandateAcknowledgmentDecision(value).value
    except (TypeError, ValueError) as error:
        _fail("L9B10_P7_DECISION_INVALID", error)


def _subject_reference(grant_id: str) -> str:
    return f"{SUBJECT_PREFIX}:grant:{grant_id}"


def _intent_fingerprint(
    *, tenant: str, principal: str, grant_id: str, decision: str,
    source_reference: str, source_fingerprint: str, idempotency: str,
) -> str:
    payload = {
        "tenant_id": tenant,
        "principal_id": principal,
        "client_grant_id": grant_id,
        "decision": decision,
        "source_evidence_reference": source_reference,
        "source_evidence_fingerprint": source_fingerprint,
        "idempotency_key": idempotency,
    }
    return hashlib.sha3_512(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _iam_idempotency(idempotency: str) -> str:
    raw = json.dumps(
        {"namespace": SUBJECT_PREFIX, "idempotency_key": idempotency},
        sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    return f"{SUBJECT_PREFIX}:iam:{hashlib.sha3_512(raw).hexdigest()}"


def _acknowledgment_id(tenant: str, grant_id: str, idempotency: str) -> str:
    raw = json.dumps(
        {"tenant_id": tenant, "client_grant_id": grant_id, "idempotency_key": idempotency},
        sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    return f"{SUBJECT_PREFIX}:ack:{hashlib.sha3_512(raw).hexdigest()[:48]}"


class LegalClientMatterMandateAcknowledgmentOrchestrator:
    """Issue one exact firm acknowledgment inside a caller-owned transaction.

    Collection handles are dependency injection only; this class never resolves
    a database. ``issue_acknowledgment`` derives tenant/principal from the
    authenticated identity, authorizes before grant disclosure, revalidates
    grant and acknowledgment currentness at durable IAM time, then appends one
    immutable value. The caller owns commit, abort and whole-transaction retry.
    No method creates mandate, Engagement, Representation, Court or financial
    authority.
    """

    def __init__(
        self,
        *,
        grant_collection: Any,
        grant_lifecycle_collection: Any,
        matter_lifecycle_collection: Any,
        acknowledgment_collection: Any,
    ) -> None:
        if any(value is None for value in (grant_collection, grant_lifecycle_collection, matter_lifecycle_collection, acknowledgment_collection)):
            _fail("L9B10_P7_COLLECTION_REQUIRED")
        self._grant_collection = grant_collection
        self._grant_lifecycle_collection = grant_lifecycle_collection
        self._matter_lifecycle_collection = matter_lifecycle_collection
        self._acknowledgment_collection = acknowledgment_collection

    def issue_acknowledgment(
        self,
        *,
        identity: SovereignIdentity,
        client_grant_id: str,
        decision: LegalClientMatterMandateAcknowledgmentDecision | str,
        idempotency_key: str,
        source_evidence_reference: str,
        source_evidence_fingerprint: str,
        authorization_evidence_registry: TenantAuthorizationDecisionEvidenceRegistry,
        session: Any,
    ) -> LegalClientMatterMandateAcknowledgment:
        """Issue or exactly replay one authorized immutable acknowledgment.

        The public caller supplies only grant identity, closed decision,
        bounded source provenance, replay identity and authenticated identity.
        All reads and both durable writes receive the exact active session;
        transaction lifecycle remains caller-owned. Errors expose stable codes,
        never grant existence or supplied evidence.
        """
        tx = _active_transaction(session)
        tenant, principal = _identity(identity)
        grant_id = _grant_identity(client_grant_id)
        decision_value = _decision(decision)
        idempotency = _opaque("idempotency_key", idempotency_key, limit=_MAX_IDEMPOTENCY)
        source_reference = _opaque("source_evidence_reference", source_evidence_reference)
        source_fingerprint = _fingerprint("source_evidence_fingerprint", source_evidence_fingerprint)
        if authorization_evidence_registry is None or not callable(getattr(authorization_evidence_registry, "issue", None)):
            _fail("L9B10_P7_AUTHORIZATION_EVIDENCE_REGISTRY_REQUIRED")

        subject = _subject_reference(grant_id)
        subject_fingerprint = _intent_fingerprint(
            tenant=tenant, principal=principal, grant_id=grant_id,
            decision=decision_value, source_reference=source_reference,
            source_fingerprint=source_fingerprint, idempotency=idempotency,
        )
        try:
            authorization = authorization_evidence_registry.issue(
                tenant_id=tenant,
                principal_id=principal,
                operation=OPERATION,
                permission=PERMISSION,
                subject_reference=subject,
                subject_evidence_fingerprint=subject_fingerprint,
                idempotency_key=_iam_idempotency(idempotency),
                session=tx,
            )
        except TenantAuthorizationDecisionEvidenceAuthorizationDeniedError as error:
            _fail("L9B10_P7_AUTHORIZATION_DENIED", error)
        except TenantAuthorizationDecisionEvidenceTransactionRequiredError as error:
            _fail("L9B10_P7_ACTIVE_TRANSACTION_REQUIRED", error)
        except TenantAuthorizationDecisionEvidenceConflictError as error:
            _fail("L9B10_P7_IAM_REPLAY_CONFLICT", error)
        except (TenantAuthorizationDecisionEvidencePersistenceError, TenantAuthorizationDecisionEvidenceRegistryError) as error:
            _fail("L9B10_P7_IAM_EVIDENCE_UNAVAILABLE", error)

        if (
            getattr(authorization, "tenant_id", None) != tenant
            or getattr(authorization, "principal_id", None) != principal
            or getattr(authorization, "operation", None) != OPERATION
            or getattr(authorization, "permission", None) != PERMISSION
            or getattr(authorization, "subject_reference", None) != subject
            or getattr(authorization, "subject_evidence_fingerprint", None) != subject_fingerprint
            or not isinstance(getattr(authorization, "authorized_at", None), datetime)
            or authorization.authorized_at.tzinfo is None
            or authorization.authorized_at.utcoffset() is None
        ):
            _fail("L9B10_P7_IAM_EVIDENCE_CORRELATION_INVALID")
        authorized_at = authorization.authorized_at

        try:
            current_grant = LegalClientMatterMandateGrantCurrentnessComposer(
                grant_collection=self._grant_collection,
                lifecycle_collection=self._grant_lifecycle_collection,
                matter_lifecycle_collection=self._matter_lifecycle_collection,
            ).compose_currentness(tenant, grant_id, authorized_at, tx)
        except LegalClientMatterMandateGrantCurrentnessComposerError as error:
            _fail("L9B10_P7_GRANT_CURRENTNESS_UNAVAILABLE", error)
        if current_grant.state is not LegalClientMatterMandateGrantCurrentnessState.CURRENT:
            _fail("L9B10_P7_GRANT_NOT_CURRENT")
        try:
            grant = grant_registry.get_grant(tenant, grant_id, self._grant_collection, session=tx)
        except grant_registry.LegalClientMatterMandateGrantRegistryError as error:
            _fail("L9B10_P7_GRANT_READ_FAILED", error)
        if grant.tenant_id != tenant or grant.client_grant_id != grant_id or grant.fingerprint != current_grant.client_grant_fingerprint:
            _fail("L9B10_P7_GRANT_CORRELATION_INVALID")

        try:
            current_acknowledgment = LegalClientMatterMandateAcknowledgmentCurrentnessComposer(
                grant_collection=self._grant_collection,
                acknowledgment_collection=self._acknowledgment_collection,
            ).compose_currentness(tenant, grant_id, authorized_at, tx)
        except LegalClientMatterMandateAcknowledgmentCurrentnessComposerError as error:
            _fail("L9B10_P7_ACKNOWLEDGMENT_HISTORY_UNAVAILABLE", error)
        if current_acknowledgment.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.CORRUPT_BLOCKED:
            _fail("L9B10_P7_ACKNOWLEDGMENT_HISTORY_CORRUPT")
        if current_acknowledgment.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.AMBIGUOUS:
            try:
                history = acknowledgment_registry.list_acknowledgments_for_grant(
                    tenant, grant_id, self._acknowledgment_collection, session=tx
                )
            except acknowledgment_registry.LegalClientMatterMandateAcknowledgmentRegistryError as error:
                _fail("L9B10_P7_ACKNOWLEDGMENT_HISTORY_UNAVAILABLE", error)
            if not history or authorized_at <= max(value.effective_from for value in history):
                _fail("L9B10_P7_ACKNOWLEDGMENT_AMBIGUITY_NOT_REPAIRABLE")

        acknowledgment_id = _acknowledgment_id(tenant, grant_id, idempotency)
        try:
            value = LegalClientMatterMandateAcknowledgment.from_client_grant(
                client_grant=grant,
                acknowledgment_id=acknowledgment_id,
                decision=decision_value,
                decision_actor_principal_id=principal,
                authorization_evidence_reference=authorization.authorization_evidence_reference,
                authorization_evidence_fingerprint=authorization.authorization_evidence_fingerprint,
                source_evidence_reference=source_reference,
                source_evidence_fingerprint=source_fingerprint,
                occurred_at=authorized_at,
                effective_from=authorized_at,
                idempotency_key=idempotency,
            )
        except (LegalClientMatterMandateAcknowledgmentError, TypeError, ValueError) as error:
            _fail("L9B10_P7_ACKNOWLEDGMENT_INVALID", error)
        try:
            persisted = acknowledgment_registry.persist_acknowledgment(
                value, self._acknowledgment_collection, session=tx
            )
        except acknowledgment_registry.LegalClientMatterMandateAcknowledgmentRegistryRetryRequiredError as error:
            _retry("L9B10_P7_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
        except acknowledgment_registry.LegalClientMatterMandateAcknowledgmentRegistryConflictError as error:
            _fail("L9B10_P7_ACKNOWLEDGMENT_REPLAY_CONFLICT", error)
        except acknowledgment_registry.LegalClientMatterMandateAcknowledgmentRegistryError as error:
            _fail("L9B10_P7_ACKNOWLEDGMENT_PERSISTENCE_UNAVAILABLE", error)
        if persisted.to_dict() != value.to_dict() or persisted.tenant_id != tenant or persisted.decision_actor_principal_id != principal:
            _fail("L9B10_P7_POST_WRITE_CORRELATION_INVALID")
        return persisted


def issue_legal_client_matter_mandate_acknowledgment(
    *,
    identity: SovereignIdentity,
    client_grant_id: str,
    decision: LegalClientMatterMandateAcknowledgmentDecision | str,
    idempotency_key: str,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
    grant_collection: Any,
    grant_lifecycle_collection: Any,
    matter_lifecycle_collection: Any,
    acknowledgment_collection: Any,
    authorization_evidence_registry: TenantAuthorizationDecisionEvidenceRegistry,
    session: Any,
) -> LegalClientMatterMandateAcknowledgment:
    """Functional issuer boundary using the same caller-owned contract."""
    return LegalClientMatterMandateAcknowledgmentOrchestrator(
        grant_collection=grant_collection,
        grant_lifecycle_collection=grant_lifecycle_collection,
        matter_lifecycle_collection=matter_lifecycle_collection,
        acknowledgment_collection=acknowledgment_collection,
    ).issue_acknowledgment(
        identity=identity,
        client_grant_id=client_grant_id,
        decision=decision,
        idempotency_key=idempotency_key,
        source_evidence_reference=source_evidence_reference,
        source_evidence_fingerprint=source_evidence_fingerprint,
        authorization_evidence_registry=authorization_evidence_registry,
        session=session,
    )


__all__ = [
    "OPERATION",
    "PERMISSION",
    "SUBJECT_PREFIX",
    "VERSION",
    "LegalClientMatterMandateAcknowledgmentOrchestrationError",
    "LegalClientMatterMandateAcknowledgmentOrchestrationRetryRequiredError",
    "LegalClientMatterMandateAcknowledgmentOrchestrator",
    "issue_legal_client_matter_mandate_acknowledgment",
]


# ARTIFACT: legal_client_matter_mandate_acknowledgment_orchestrator.py
# VERSION: v1.0.0-L9B10-P7-FIRM-MANDATE-ACKNOWLEDGMENT-ISSUANCE
# AUTHORITY BOUNDARY: authorized immutable firm acknowledgment issuance only
# TENANT POSTURE: exact authenticated tenant plus canonical grant lineage
# FAIL-CLOSED POSTURE: denied, stale, corrupt, divergent and uncertain requests reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
