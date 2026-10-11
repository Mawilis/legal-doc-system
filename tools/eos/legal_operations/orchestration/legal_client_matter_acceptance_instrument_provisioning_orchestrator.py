"""Atomic provisioning of client matter acceptance instruments.

TITLE: Legal Client Matter Acceptance Instrument Provisioning Orchestrator
VERSION: v1.0.0-CLIENT-ACCEPTANCE-INSTRUMENT-PROVISIONING
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Authorize and atomically compose dedicated bytes, immutable instrument
         metadata and the mandatory initial ACTIVE lifecycle fact.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_matter_acceptance_instrument_provisioning_orchestrator.py
COLLABORATION / OWNERSHIP: CaseMatter and IAM are upstream authorities; dedicated
                            content, instrument and lifecycle registries own writes.
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0 establishes exact Partner/Attorney-authorized,
           caller-transaction-owned three-write provisioning and exact replay.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Tenant/principal and chronology are server-derived;
                             callers cannot select storage locators or lifecycle.
TENANT BOUNDARY: Every read, authorization and write uses identity tenant scope.
AUTHORITY BOUNDARY: Provisioning only; no approval, context, acceptance,
                    engagement, representation, Court or AI authority.
TRANSACTION BOUNDARY: Caller owns active transaction, commit, abort and retry.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Inactive identity, closed matter, denied IAM,
                         divergence, corruption or persistence uncertainty reject.
"""
from __future__ import annotations

from dataclasses import dataclass
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
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument import (
    LegalClientMatterAcceptanceInstrument,
    LegalClientMatterAcceptanceInstrumentError,
    record_legal_client_matter_acceptance_instrument,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_content import (
    LegalClientMatterAcceptanceInstrumentContent,
    LegalClientMatterAcceptanceInstrumentContentError,
    content_fingerprint,
    register_legal_client_matter_acceptance_instrument_content,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_lifecycle import (
    LegalClientMatterAcceptanceInstrumentLifecycle,
    LegalClientMatterAcceptanceInstrumentLifecycleError,
    LegalClientMatterAcceptanceInstrumentLifecycleStatus,
    record_legal_client_matter_acceptance_instrument_lifecycle,
)
from tools.eos.legal_operations.domain.legal_operations_current_projection import resolve_current_lifecycle_snapshot
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter, CaseMatterState
from tools.eos.legal_operations.registry import (
    legal_client_matter_acceptance_instrument_content_registry as content_registry,
    legal_client_matter_acceptance_instrument_lifecycle_registry as lifecycle_registry,
    legal_client_matter_acceptance_instrument_registry as instrument_registry,
    legal_operations_lifecycle_registry as matter_registry,
)


VERSION: Final[str] = "v1.0.0-CLIENT-ACCEPTANCE-INSTRUMENT-PROVISIONING"
PERMISSION: Final[str] = "legal_operations:matter_acceptance_instrument:write"
OPERATION: Final[str] = "legal_matter_acceptance_instrument_write"
SUBJECT_PREFIX: Final[str] = "legal-client-acceptance-instrument-provisioning"
_ACCEPTANCE_SCOPE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)


class LegalClientMatterAcceptanceInstrumentProvisioningError(RuntimeError):
    """Stable bounded provisioning failure."""
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientMatterAcceptanceInstrumentProvisioningRetryRequiredError(LegalClientMatterAcceptanceInstrumentProvisioningError):
    """Caller must abort and retry the whole transaction."""


@dataclass(frozen=True, slots=True)
class LegalClientMatterAcceptanceInstrumentProvisioningResult:
    """Correlated durable result from the atomic three-write composition."""
    content: LegalClientMatterAcceptanceInstrumentContent
    instrument: LegalClientMatterAcceptanceInstrument
    lifecycle: LegalClientMatterAcceptanceInstrumentLifecycle


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalClientMatterAcceptanceInstrumentProvisioningError(code)
    if cause is None:
        raise error
    raise error from cause


def _retry(code: str, cause: BaseException) -> NoReturn:
    raise LegalClientMatterAcceptanceInstrumentProvisioningRetryRequiredError(code) from cause


def _active(session: Any) -> Any:
    marker = getattr(session, "in_transaction", None) if session is not None else None
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _identity(identity: SovereignIdentity) -> tuple[str, str]:
    if not isinstance(identity, SovereignIdentity):
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_IDENTITY_REQUIRED")
    if identity.status is not PrincipalStatus.ACTIVE:
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_PRINCIPAL_INACTIVE")
    if not identity.tenant_id or not identity.identity_id:
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_IDENTITY_INVALID")
    return identity.tenant_id, identity.identity_id


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"CLIENT_ACCEPTANCE_PROVISIONING_{name.upper()}_INVALID")
    return value


def _matter(*, tenant: str, matter_id: str, collection: Any, session: Any) -> CaseMatter:
    try:
        history = matter_registry.LegalOperationsLifecycleRegistry.get_entity_history(tenant, "CaseMatter", matter_id, collection, session=session)
        value = resolve_current_lifecycle_snapshot(history, expected_type=CaseMatter)
    except Exception as error:
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_MATTER_UNAVAILABLE", error)
    if type(value) is not CaseMatter or value.tenant_id != tenant or value.case_matter_id != matter_id:
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_MATTER_SCOPE_INVALID")
    if value.state is not CaseMatterState.OPEN:
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_MATTER_NOT_OPEN")
    return value


def _subject_fingerprint(*, tenant: str, principal: str, matter: CaseMatter, instrument_id: str, version: str, instrument_kind: str, title: str, review_scope: str, content_digest: str, media_type: str, effective_from: object, source_reference: str, source_fingerprint: str, supersedes_version_id: str | None, idempotency_key: str) -> str:
    payload = {"tenant_id": tenant, "principal_id": principal, "matter_fingerprint": matter.fingerprint, "instrument_id": instrument_id, "version": version, "instrument_kind": instrument_kind, "title": title, "review_scope": review_scope, "content_fingerprint": content_digest, "media_type": media_type, "effective_from": str(effective_from), "approval_evidence_reference": source_reference, "approval_evidence_fingerprint": source_fingerprint, "supersedes_version_id": supersedes_version_id, "idempotency_key": idempotency_key}
    return hashlib.sha3_512(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def provision_legal_client_matter_acceptance_instrument(*, identity: SovereignIdentity, case_matter_id: str, instrument_id: str, version: str, instrument_kind: str, title: str, review_scope: str, content: bytes, media_type: str, effective_from: datetime, approval_evidence_reference: str, approval_evidence_fingerprint: str, idempotency_key: str, matter_lifecycle_collection: Any, content_collection: Any, instrument_collection: Any, instrument_lifecycle_collection: Any, authorization_evidence_registry: TenantAuthorizationDecisionEvidenceRegistry, session: Any, supersedes_version_id: str | None = None) -> LegalClientMatterAcceptanceInstrumentProvisioningResult:
    """Authorize and persist/replay content, instrument and ACTIVE lifecycle.

    Source ``approval_evidence_*`` values are pre-instrument authoring provenance,
    not the distinct downstream firm approval record. All writes share the exact
    active caller session; this function never commits, aborts or retries.
    """
    tx = _active(session)
    tenant, principal = _identity(identity)
    matter_id = _text("case_matter_id", case_matter_id)
    instrument_identity = _text("instrument_id", instrument_id)
    version_identity = _text("version", version)
    kind = _text("instrument_kind", instrument_kind)
    bounded_title = _text("title", title)
    scope = _text("review_scope", review_scope)
    if _ACCEPTANCE_SCOPE.fullmatch(scope) is None:
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_REVIEW_SCOPE_INVALID")
    idempotency = _text("idempotency_key", idempotency_key)
    source_reference = _text("approval_evidence_reference", approval_evidence_reference)
    source_fingerprint = _text("approval_evidence_fingerprint", approval_evidence_fingerprint)
    if not isinstance(authorization_evidence_registry, TenantAuthorizationDecisionEvidenceRegistry):
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_AUTHORIZATION_REGISTRY_REQUIRED")
    if any(item is None for item in (matter_lifecycle_collection, content_collection, instrument_collection, instrument_lifecycle_collection)):
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_COLLECTION_REQUIRED")
    matter = _matter(tenant=tenant, matter_id=matter_id, collection=matter_lifecycle_collection, session=tx)
    try:
        digest = content_fingerprint(content)
        if media_type not in {"text/plain", "text/markdown"}:
            _fail("CLIENT_ACCEPTANCE_PROVISIONING_CONTENT_INVALID")
    except LegalClientMatterAcceptanceInstrumentContentError as error:
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_CONTENT_INVALID", error)
    subject_reference = f"{SUBJECT_PREFIX}:{matter.case_matter_id}:{instrument_identity}:{version_identity}"
    subject_fingerprint = _subject_fingerprint(tenant=tenant, principal=principal, matter=matter, instrument_id=instrument_identity, version=version_identity, instrument_kind=kind, title=bounded_title, review_scope=scope, content_digest=digest, media_type=media_type, effective_from=effective_from, source_reference=source_reference, source_fingerprint=source_fingerprint, supersedes_version_id=supersedes_version_id, idempotency_key=idempotency)
    try:
        authorization = authorization_evidence_registry.issue(tenant_id=tenant, principal_id=principal, operation=OPERATION, permission=PERMISSION, subject_reference=subject_reference, subject_evidence_fingerprint=subject_fingerprint, idempotency_key=idempotency, session=tx)
    except TenantAuthorizationDecisionEvidenceAuthorizationDeniedError as error:
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_AUTHORIZATION_REQUIRED", error)
    except TenantAuthorizationDecisionEvidenceTransactionRequiredError as error:
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_ACTIVE_TRANSACTION_REQUIRED", error)
    except TenantAuthorizationDecisionEvidenceConflictError as error:
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_AUTHORIZATION_REPLAY_CONFLICT", error)
    except (TenantAuthorizationDecisionEvidencePersistenceError, TenantAuthorizationDecisionEvidenceRegistryError) as error:
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_AUTHORIZATION_UNAVAILABLE", error)
    if authorization.tenant_id != tenant or authorization.principal_id != principal or authorization.operation != OPERATION or authorization.permission != PERMISSION or authorization.subject_reference != subject_reference or authorization.subject_evidence_fingerprint != subject_fingerprint:
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_AUTHORIZATION_CORRELATION_INVALID")
    try:
        canonical_content = register_legal_client_matter_acceptance_instrument_content(tenant_id=tenant, case_matter_id=matter.case_matter_id, instrument_id=instrument_identity, instrument_version=version_identity, content=content, media_type=media_type, registered_at=authorization.authorized_at)
        persisted_content = content_registry.persist_content(canonical_content, content, content_collection, session=tx)
        instrument = record_legal_client_matter_acceptance_instrument(case_matter=matter, instrument_id=instrument_identity, version=version_identity, instrument_kind=kind, title=bounded_title, review_scope=scope, content_reference=persisted_content.content_reference, content_fingerprint=persisted_content.content_fingerprint, created_at=authorization.authorized_at, effective_from=effective_from, approval_evidence_reference=source_reference, approval_evidence_fingerprint=source_fingerprint, supersedes_version_id=supersedes_version_id)
        persisted_instrument = instrument_registry.persist_instrument(instrument, instrument_collection, session=tx)
        lifecycle_reference = f"{SUBJECT_PREFIX}:active:{authorization.authorization_evidence_reference}"
        lifecycle_fingerprint = hashlib.sha3_512(json.dumps({"authorization": authorization.authorization_evidence_fingerprint, "instrument": persisted_instrument.fingerprint, "status": "ACTIVE"}, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        lifecycle = record_legal_client_matter_acceptance_instrument_lifecycle(tenant_id=tenant, case_matter_id=matter.case_matter_id, matter_fingerprint=matter.fingerprint, instrument_id=instrument_identity, version=version_identity, instrument_fingerprint=persisted_instrument.fingerprint, status=LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE, occurred_at=authorization.authorized_at, lifecycle_evidence_reference=lifecycle_reference, lifecycle_evidence_fingerprint=lifecycle_fingerprint)
        persisted_lifecycle = lifecycle_registry.persist_lifecycle(lifecycle, instrument_lifecycle_collection, instrument_collection=instrument_collection, session=tx)
    except (content_registry.LegalClientMatterAcceptanceInstrumentContentRegistryRetryRequiredError, instrument_registry.LegalClientMatterAcceptanceInstrumentRegistryRetryRequiredError, lifecycle_registry.LegalClientMatterAcceptanceInstrumentLifecycleRegistryRetryRequiredError) as error:
        _retry("CLIENT_ACCEPTANCE_PROVISIONING_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    except (LegalClientMatterAcceptanceInstrumentContentError, LegalClientMatterAcceptanceInstrumentError, LegalClientMatterAcceptanceInstrumentLifecycleError) as error:
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_COMPOSITION_INVALID", error)
    except (content_registry.LegalClientMatterAcceptanceInstrumentContentRegistryConflictError, instrument_registry.LegalClientMatterAcceptanceInstrumentRegistryConflictError, lifecycle_registry.LegalClientMatterAcceptanceInstrumentLifecycleRegistryConflictError) as error:
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_REPLAY_CONFLICT", error)
    except (content_registry.LegalClientMatterAcceptanceInstrumentContentRegistryError, instrument_registry.LegalClientMatterAcceptanceInstrumentRegistryError, lifecycle_registry.LegalClientMatterAcceptanceInstrumentLifecycleRegistryError) as error:
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_PERSISTENCE_UNAVAILABLE", error)
    if persisted_content.tenant_id != tenant or persisted_instrument.content_reference != persisted_content.content_reference or persisted_instrument.content_fingerprint != persisted_content.content_fingerprint or persisted_lifecycle.instrument_fingerprint != persisted_instrument.fingerprint or persisted_lifecycle.status is not LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE:
        _fail("CLIENT_ACCEPTANCE_PROVISIONING_POST_WRITE_CORRELATION_INVALID")
    return LegalClientMatterAcceptanceInstrumentProvisioningResult(persisted_content, persisted_instrument, persisted_lifecycle)


__all__ = ["OPERATION", "PERMISSION", "SUBJECT_PREFIX", "VERSION", "LegalClientMatterAcceptanceInstrumentProvisioningError", "LegalClientMatterAcceptanceInstrumentProvisioningResult", "LegalClientMatterAcceptanceInstrumentProvisioningRetryRequiredError", "provision_legal_client_matter_acceptance_instrument"]

# ARTIFACT: legal_client_matter_acceptance_instrument_provisioning_orchestrator.py
# VERSION: v1.0.0-CLIENT-ACCEPTANCE-INSTRUMENT-PROVISIONING
# AUTHORITY BOUNDARY: authorized atomic content/instrument/ACTIVE provisioning only
# TENANT POSTURE: exact authenticated tenant and OPEN matter scope
# FAIL-CLOSED POSTURE: denied, divergent, corrupt and uncertain operations reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
