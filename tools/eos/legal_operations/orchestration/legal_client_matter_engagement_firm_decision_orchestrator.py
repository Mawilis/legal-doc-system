"""WILSY OS authorized Engagement firm-decision issuance orchestration.

TITLE: Engagement Firm-Decision Issuance Orchestrator
VERSION: v1.0.0-L9C8-ENGAGEMENT-FIRM-DECISION-ISSUANCE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Re-read one exact OPEN CaseMatter and client LegalMatterParty,
         issue durable tenant-authorization evidence, and compose one immutable
         firm decision under a caller-owned transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_matter_engagement_firm_decision_orchestrator.py
COLLABORATION / OWNERSHIP: CaseMatter lifecycle and LegalMatterParty registries
                            own source truth; TenantAuthorizationDecisionEvidence
                            owns durable IAM evidence; the firm-decision domain
                            owns immutable value semantics. This module owns
                            only their bounded composition.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C8 establishes authenticated exact matter/client-party
           revalidation, subject-bound durable IAM evidence, actor correlation,
           authorization-derived chronology, deterministic identifiers, and
           caller-owned transaction semantics. It deliberately does not persist
           firm decisions, form Engagements, or read formation prerequisites.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only bounded opaque identifiers, references and
                             lowercase SHA3-512 fingerprints are admitted;
                             no raw PII, credentials, tokens or document body.
TENANT BOUNDARY: Tenant and principal derive only from active SovereignIdentity;
                 every source read and authorization operation is exact tenant
                 scoped and receives the caller's session.
AUTHORITY BOUNDARY: Authorized immutable firm-decision composition only. No
                    firm-decision registry, Engagement, representation, Court,
                    conflict, mandate, acceptance or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive execution and
                              settlement authority.
TRANSACTION BOUNDARY: Caller supplies and owns the active transaction. This
                      module never starts, commits, aborts or retries one.
FAIL-CLOSED DECLARATION: Missing identity/transaction, stale or foreign source,
                         denied or divergent IAM, malformed provenance and
                         persistence uncertainty reject without fallback.
"""
from __future__ import annotations

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
from tools.eos.legal_operations.domain.legal_client_matter_engagement_firm_decision import (
    LegalClientMatterEngagementFirmDecision,
    LegalClientMatterEngagementFirmDecisionError,
    LegalClientMatterEngagementFirmDecisionType,
)
from tools.eos.legal_operations.domain.legal_operations_current_projection import (
    resolve_current_lifecycle_snapshot,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.registry import (
    legal_matter_party_registry as party_registry,
    legal_operations_lifecycle_registry as matter_registry,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterParty,
    LegalMatterPartyRole,
    LegalMatterPartySide,
)


VERSION: Final[str] = "v1.0.0-L9C8-ENGAGEMENT-FIRM-DECISION-ISSUANCE"
OPERATION: Final[str] = "legal_matter_engagement_firm_decision_write"
PERMISSION: Final[str] = "legal_operations:matter_engagement_firm_decision:write"
SUBJECT_PREFIX: Final[str] = "legal-engagement-firm-decision"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_FINGERPRINT = re.compile(r"^[0-9a-f]{128}$")
_MAX_REFERENCE: Final[int] = 512
_MAX_IDEMPOTENCY: Final[int] = 240


class LegalClientMatterEngagementFirmDecisionOrchestrationError(RuntimeError):
    """Stable non-sensitive fail-closed issuer error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientMatterEngagementFirmDecisionOrchestrationRetryRequiredError(
    LegalClientMatterEngagementFirmDecisionOrchestrationError
):
    """The caller must abort and restart the complete transaction."""


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one bounded code while retaining technical cause internally."""
    error = LegalClientMatterEngagementFirmDecisionOrchestrationError(code)
    if cause is None:
        raise error
    raise error from cause


def _retry(code: str, cause: BaseException) -> NoReturn:
    """Require caller-owned whole-transaction retry."""
    raise LegalClientMatterEngagementFirmDecisionOrchestrationRetryRequiredError(
        code
    ) from cause


def _active_session(session: Any) -> Any:
    """Require one already-active caller transaction without owning it."""
    if session is None:
        _fail("L9C8_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError) as error:
        _fail("L9C8_ACTIVE_TRANSACTION_REQUIRED", error)
    if active is not True:
        _fail("L9C8_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _identity(identity: object) -> tuple[str, str]:
    """Derive exact tenant and principal from active authenticated identity."""
    if not isinstance(identity, SovereignIdentity):
        _fail("L9C8_IDENTITY_REQUIRED")
    if identity.status is not PrincipalStatus.ACTIVE:
        _fail("L9C8_PRINCIPAL_INACTIVE")
    tenant = _text("tenant_id", identity.tenant_id, limit=160)
    principal = _text("principal_id", identity.identity_id, limit=160)
    return tenant, principal


def _text(name: str, value: object, *, limit: int = _MAX_REFERENCE) -> str:
    """Require bounded single-line text without coercion or trimming."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(
            ord(character) < 32
            or 0x7F <= ord(character) <= 0x9F
            or 0xD800 <= ord(character) <= 0xDFFF
            for character in value
        )
    ):
        _fail(f"L9C8_{name.upper()}_INVALID")
    return value


def _identity_text(name: str, value: object) -> str:
    """Require one opaque identity in the repository's bounded vocabulary."""
    text = _text(name, value, limit=160)
    if _IDENTITY.fullmatch(text) is None:
        _fail(f"L9C8_{name.upper()}_INVALID")
    return text


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 hexadecimal fingerprint."""
    if not isinstance(value, str) or _FINGERPRINT.fullmatch(value) is None:
        _fail(f"L9C8_{name.upper()}_INVALID")
    return value


def _canonical_digest(payload: dict[str, object]) -> str:
    """Hash canonical issuer intent without retaining a secret or raw payload."""
    return hashlib.sha3_512(
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _subject_reference(tenant: str, matter: str, party: str) -> str:
    """Return an opaque exact tenant/matter/client-party IAM subject."""
    return f"{SUBJECT_PREFIX}:{tenant}:{matter}:{party}"


def _current_case_matter(
    *, tenant: str, matter_id: str, collection: Any, session: Any
) -> CaseMatter:
    """Read and resolve the exact current OPEN CaseMatter snapshot."""
    if collection is None:
        _fail("L9C8_CASE_MATTER_COLLECTION_REQUIRED")
    try:
        history = matter_registry.LegalOperationsLifecycleRegistry.get_entity_history(
            tenant,
            "CaseMatter",
            matter_id,
            collection,
            session=session,
        )
        value = resolve_current_lifecycle_snapshot(history, expected_type=CaseMatter)
    except Exception as error:
        _fail("L9C8_CASE_MATTER_UNAVAILABLE", error)
    if type(value) is not CaseMatter:
        _fail("L9C8_CASE_MATTER_TYPE_INVALID")
    if value.tenant_id != tenant or value.case_matter_id != matter_id:
        _fail("L9C8_CASE_MATTER_SCOPE_MISMATCH")
    if value.state is not CaseMatterState.OPEN:
        _fail("L9C8_CASE_MATTER_NOT_OPEN")
    return value


def _client_party(
    *, tenant: str, party_id: str, matter: CaseMatter, collection: Any, session: Any
) -> LegalMatterParty:
    """Read and correlate one exact client-side LegalMatterParty."""
    if collection is None:
        _fail("L9C8_PARTY_COLLECTION_REQUIRED")
    try:
        value = party_registry.LegalMatterPartyRegistry.get_party(
            tenant, party_id, collection, session=session
        )
    except party_registry.LegalMatterPartyRegistryNotFoundError as error:
        _fail("L9C8_CLIENT_PARTY_NOT_FOUND", error)
    except party_registry.LegalMatterPartyRegistryRetryRequiredError as error:
        _retry("L9C8_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    except party_registry.LegalMatterPartyRegistryError as error:
        _fail("L9C8_CLIENT_PARTY_UNAVAILABLE", error)
    if type(value) is not LegalMatterParty:
        _fail("L9C8_CLIENT_PARTY_TYPE_INVALID")
    if (
        value.tenant_id != tenant
        or value.party_id != party_id
        or value.case_matter_id != matter.case_matter_id
        or value.matter_fingerprint != matter.fingerprint
        or value.party_side is not LegalMatterPartySide.CLIENT_SIDE
        or value.matter_role is not LegalMatterPartyRole.CLIENT
    ):
        _fail("L9C8_CLIENT_PARTY_SCOPE_MISMATCH")
    return value


def issue_legal_client_matter_engagement_firm_decision(
    *,
    identity: SovereignIdentity,
    case_matter_id: str,
    client_party_id: str,
    decision: LegalClientMatterEngagementFirmDecisionType | str,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
    idempotency_key: str,
    matter_lifecycle_collection: Any,
    party_collection: Any,
    authorization_evidence_registry: TenantAuthorizationDecisionEvidenceRegistry,
    session: Any,
) -> LegalClientMatterEngagementFirmDecision:
    """Authorize and compose one immutable firm decision.

    Tenant, principal, matter fingerprint, subject fields, decision ID,
    authorization provenance and chronology are server-derived. The exact
    CaseMatter and client party are read with ``session`` before IAM evidence
    is issued. The existing authorization-evidence registry performs canonical
    IAM evaluation and durable insertion in the same caller-owned transaction.
    This function does not persist the firm decision and never starts, commits,
    aborts or retries a transaction.
    """
    tx = _active_session(session)
    tenant, principal = _identity(identity)
    matter_id = _identity_text("case_matter_id", case_matter_id)
    party_id = _identity_text("client_party_id", client_party_id)
    source_reference = _text("source_evidence_reference", source_evidence_reference)
    source_fingerprint = _fingerprint(
        "source_evidence_fingerprint", source_evidence_fingerprint
    )
    idempotency = _text("idempotency_key", idempotency_key, limit=_MAX_IDEMPOTENCY)
    try:
        decision_value = LegalClientMatterEngagementFirmDecisionType(decision)
    except (TypeError, ValueError) as error:
        _fail("L9C8_DECISION_INVALID", error)
    if not isinstance(
        authorization_evidence_registry,
        TenantAuthorizationDecisionEvidenceRegistry,
    ):
        _fail("L9C8_AUTHORIZATION_EVIDENCE_REGISTRY_REQUIRED")

    matter = _current_case_matter(
        tenant=tenant,
        matter_id=matter_id,
        collection=matter_lifecycle_collection,
        session=tx,
    )
    party = _client_party(
        tenant=tenant,
        party_id=party_id,
        matter=matter,
        collection=party_collection,
        session=tx,
    )
    subject = _subject_reference(tenant, matter.case_matter_id, party.party_id)
    subject_fingerprint = _canonical_digest(
        {
            "tenant_id": tenant,
            "principal_id": principal,
            "case_matter_id": matter.case_matter_id,
            "matter_fingerprint": matter.fingerprint,
            "client_party_id": party.party_id,
            "subject_reference": party.subject_reference,
            "subject_identity_fingerprint": party.subject_identity_fingerprint,
            "decision": decision_value.value,
            "source_evidence_reference": source_reference,
            "source_evidence_fingerprint": source_fingerprint,
            "idempotency_key": idempotency,
        }
    )
    authorization_idempotency = (
        f"{SUBJECT_PREFIX}:iam:{_canonical_digest({'tenant_id': tenant, 'idempotency_key': idempotency})}"
    )
    decision_id = (
        f"{SUBJECT_PREFIX}:{_canonical_digest({'tenant_id': tenant, 'case_matter_id': matter.case_matter_id, 'client_party_id': party.party_id, 'idempotency_key': idempotency})}"
    )
    try:
        authorization = authorization_evidence_registry.issue(
            tenant_id=tenant,
            principal_id=principal,
            operation=OPERATION,
            permission=PERMISSION,
            subject_reference=subject,
            subject_evidence_fingerprint=subject_fingerprint,
            idempotency_key=authorization_idempotency,
            session=tx,
        )
    except TenantAuthorizationDecisionEvidenceAuthorizationDeniedError as error:
        _fail("L9C8_FIRM_DECISION_AUTHORIZATION_REQUIRED", error)
    except TenantAuthorizationDecisionEvidenceTransactionRequiredError as error:
        _fail("L9C8_ACTIVE_TRANSACTION_REQUIRED", error)
    except TenantAuthorizationDecisionEvidenceConflictError as error:
        _retry("L9C8_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    except (
        TenantAuthorizationDecisionEvidencePersistenceError,
        TenantAuthorizationDecisionEvidenceRegistryError,
    ) as error:
        _fail("L9C8_AUTHORIZATION_EVIDENCE_UNAVAILABLE", error)

    if (
        authorization.tenant_id != tenant
        or authorization.principal_id != principal
        or authorization.operation != OPERATION
        or authorization.permission != PERMISSION
        or authorization.subject_reference != subject
        or authorization.subject_evidence_fingerprint != subject_fingerprint
    ):
        _fail("L9C8_AUTHORIZATION_EVIDENCE_CORRELATION_INVALID")
    authorized_at = authorization.authorized_at
    try:
        return LegalClientMatterEngagementFirmDecision.from_canonical(
            decision_id=decision_id,
            case_matter=matter,
            party=party,
            decision=decision_value,
            decision_actor_principal_id=authorization.principal_id,
            authorization_evidence_reference=(
                authorization.authorization_evidence_reference
            ),
            authorization_evidence_fingerprint=(
                authorization.authorization_evidence_fingerprint
            ),
            source_evidence_reference=source_reference,
            source_evidence_fingerprint=source_fingerprint,
            occurred_at=authorized_at,
            effective_from=authorized_at,
            idempotency_key=idempotency,
        )
    except LegalClientMatterEngagementFirmDecisionError as error:
        _fail("L9C8_FIRM_DECISION_INVALID", error)


__all__ = [
    "OPERATION",
    "PERMISSION",
    "SUBJECT_PREFIX",
    "VERSION",
    "LegalClientMatterEngagementFirmDecisionOrchestrationError",
    "LegalClientMatterEngagementFirmDecisionOrchestrationRetryRequiredError",
    "issue_legal_client_matter_engagement_firm_decision",
]


# ARTIFACT: legal_client_matter_engagement_firm_decision_orchestrator.py
# VERSION: v1.0.0-L9C8-ENGAGEMENT-FIRM-DECISION-ISSUANCE
# AUTHORITY BOUNDARY: authorized immutable firm-decision composition only; no persistence or formation
# TENANT POSTURE: exact authenticated tenant/matter/client-party scope and caller session
# FAIL-CLOSED POSTURE: stale, denied, divergent, corrupt and persistence-uncertain requests reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
