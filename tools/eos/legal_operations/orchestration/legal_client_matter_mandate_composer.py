"""Compose and persist one immutable client-matter mandate.

TITLE: WILSY OS Legal Client Matter Mandate Formation Composer
VERSION: v1.0.0-L9B11-P1-CLIENT-MATTER-MANDATE-COMPOSER
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Derive one immutable mandate formation artifact from an exact
         persisted client grant, grant currentness, and acknowledged firm
         decision under one caller-owned transaction. This module creates no
         currentness, lifecycle, Engagement, Representation, Court, IAM or
         financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_matter_mandate_composer.py
COLLABORATION / OWNERSHIP: Grant and acknowledgment registries own durable
                            evidence; their currentness composers own state
                            selection; LegalClientMatterMandate owns immutable
                            serialization; its registry owns append-only
                            persistence. This composer owns only orchestration.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B11-P1 establishes caller-session validation, authoritative
           acknowledgment-time evaluation, exact grant/acknowledgment lineage,
           deterministic mandate identity, domain construction and exact
           registry persistence. No real-Mongo certificate is included.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Caller supplies only tenant, grant identity and a
                             bounded idempotency key. Scope, capabilities,
                             chronology, fingerprints and authority state are
                             read from canonical evidence; errors expose codes.
TENANT BOUNDARY: Every read and the single allowed write are exact-tenant and
                 exact-grant scoped under the identical caller session.
AUTHORITY BOUNDARY: Mandate formation evidence only. No separate IAM,
                    CaseMatter, acting-capacity currentness, conflict,
                    ClientAcceptance or downstream authority is consulted.
FINANCIAL AUTHORITY BOUNDARY: No payment, release, settlement or execution;
                              Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller supplies and owns the active transaction. This
                      composer never starts, commits, aborts or retries it.
FAIL-CLOSED DECLARATION: Missing/corrupt/non-current/divergent evidence,
                         ambiguous decisions and persistence uncertainty reject
                         without fallback, overwrite or downstream mutation.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
import re
from typing import Any, Final, NoReturn

from tools.eos.legal_operations.domain.legal_client_matter_mandate import (
    LegalClientMatterMandate,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment import (
    LegalClientMatterMandateAcknowledgment,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment_currentness import (
    LegalClientMatterMandateAcknowledgmentCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant import (
    LegalClientMatterMandateGrant,
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
    legal_client_matter_mandate_registry as mandate_registry,
)


VERSION: Final[str] = "v1.0.0-L9B11-P1-CLIENT-MATTER-MANDATE-COMPOSER"
MANDATE_ID_PREFIX: Final[str] = "legal-client-matter-mandate"
_IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_MAX_IDEMPOTENCY: Final[int] = 240


class LegalClientMatterMandateComposerError(RuntimeError):
    """Stable, non-sensitive fail-closed formation error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalClientMatterMandateComposerError(code)
    if cause is None:
        raise error
    raise error from cause


def _active_transaction(session: Any) -> Any:
    """Require an active caller-owned transaction before any read."""
    if session is None:
        _fail("L9B11_P1_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _fail("L9B11_P1_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or _IDENTITY.fullmatch(value) is None:
        _fail(f"L9B11_P1_{name.upper()}_INVALID")
    return value


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in {"default", "global", "global_root", "root", "master", "*"}:
        _fail("L9B11_P1_TENANT_INVALID")
    return tenant


def _idempotency(value: object) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > _MAX_IDEMPOTENCY
        or any(ord(char) < 32 or 0x7F <= ord(char) <= 0x9F or 0xD800 <= ord(char) <= 0xDFFF for char in value)
    ):
        _fail("L9B11_P1_IDEMPOTENCY_KEY_INVALID")
    return value


def _formation_id(tenant_id: str, grant_fingerprint: str, acknowledgment_fingerprint: str, idempotency_key: str) -> str:
    payload = {
        "tenant_id": tenant_id,
        "client_grant_fingerprint": grant_fingerprint,
        "firm_acknowledgment_fingerprint": acknowledgment_fingerprint,
        "idempotency_key": idempotency_key,
    }
    digest = hashlib.sha3_512(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:48]
    return f"{MANDATE_ID_PREFIX}:{digest}"


def _state_label(state: object) -> str:
    """Return a bounded state label without assuming an enum implementation."""
    return str(getattr(state, "value", state))


def _correlates(grant: LegalClientMatterMandateGrant, acknowledgment: LegalClientMatterMandateAcknowledgment) -> bool:
    return (
        acknowledgment.tenant_id == grant.tenant_id
        and acknowledgment.client_grant_id == grant.client_grant_id
        and acknowledgment.client_grant_fingerprint == grant.fingerprint
        and acknowledgment.case_matter_id == grant.case_matter_id
        and acknowledgment.matter_fingerprint == grant.matter_fingerprint
        and acknowledgment.client_party_id == grant.client_party_id
        and acknowledgment.subject_identity_fingerprint == grant.subject_identity_fingerprint
    )


class LegalClientMatterMandateComposer:
    """Form and persist one exact mandate inside a caller transaction.

    Public input is limited to tenant identity, persisted client-grant ID and
    idempotency key. Grant and acknowledgment fingerprints, scope, capability,
    chronology, mandate ID and currentness are never caller assertions. All
    registry and currentness calls receive the exact supplied session; this
    class never owns transaction lifecycle and performs one mandate-registry
    write at most. No IAM, conflict, ClientAcceptance, Engagement,
    Representation, Court or financial authority is created.
    """

    def __init__(
        self,
        *,
        grant_collection: Any,
        grant_lifecycle_collection: Any,
        matter_lifecycle_collection: Any,
        acknowledgment_collection: Any,
        mandate_collection: Any,
    ) -> None:
        """Bind explicit canonical collection handles without resolving a DB."""
        if any(value is None for value in (
            grant_collection,
            grant_lifecycle_collection,
            matter_lifecycle_collection,
            acknowledgment_collection,
            mandate_collection,
        )):
            _fail("L9B11_P1_COLLECTION_REQUIRED")
        self._grant_collection = grant_collection
        self._grant_lifecycle_collection = grant_lifecycle_collection
        self._matter_lifecycle_collection = matter_lifecycle_collection
        self._acknowledgment_collection = acknowledgment_collection
        self._mandate_collection = mandate_collection

    def compose_mandate(
        self,
        *,
        tenant_id: str,
        client_grant_id: str,
        idempotency_key: str,
        session: Any,
    ) -> LegalClientMatterMandate:
        """Derive/replay one immutable mandate from canonical evidence.

        The latest persisted acknowledgment effective instant is the explicit
        formation evaluation instant. Both currentness composers evaluate at
        that same instant and the decisive ACKNOWLEDGED row supplies mandate
        chronology. The caller owns commit, abort and whole-transaction retry.
        """
        transaction = _active_transaction(session)
        tenant = _tenant(tenant_id)
        grant_id = _identity("client_grant_id", client_grant_id)
        idempotency = _idempotency(idempotency_key)
        try:
            grant = grant_registry.get_grant(tenant, grant_id, self._grant_collection, session=transaction)
        except grant_registry.LegalClientMatterMandateGrantRegistryNotFoundError as error:
            _fail("L9B11_P1_GRANT_ABSENT", error)
        except grant_registry.LegalClientMatterMandateGrantRegistryError as error:
            _fail("L9B11_P1_GRANT_READ_FAILED", error)
        if type(grant) is not LegalClientMatterMandateGrant or grant.tenant_id != tenant or grant.client_grant_id != grant_id:
            _fail("L9B11_P1_GRANT_CORRELATION_INVALID")
        try:
            acknowledgment_history = acknowledgment_registry.list_acknowledgments_for_grant(
                tenant, grant_id, self._acknowledgment_collection, session=transaction
            )
        except acknowledgment_registry.LegalClientMatterMandateAcknowledgmentRegistryError as error:
            _fail("L9B11_P1_ACKNOWLEDGMENT_READ_FAILED", error)
        if not acknowledgment_history:
            _fail("L9B11_P1_ACKNOWLEDGMENT_ABSENT")
        if any(type(value) is not LegalClientMatterMandateAcknowledgment or not _correlates(grant, value) for value in acknowledgment_history):
            _fail("L9B11_P1_ACKNOWLEDGMENT_LINEAGE_INVALID")
        evaluation_time = max(value.effective_from for value in acknowledgment_history)
        try:
            grant_currentness = LegalClientMatterMandateGrantCurrentnessComposer(
                grant_collection=self._grant_collection,
                lifecycle_collection=self._grant_lifecycle_collection,
                matter_lifecycle_collection=self._matter_lifecycle_collection,
            ).compose_currentness(tenant, grant_id, evaluation_time, transaction)
        except LegalClientMatterMandateGrantCurrentnessComposerError as error:
            _fail("L9B11_P1_GRANT_CURRENTNESS_FAILED", error)
        if grant_currentness.state is not LegalClientMatterMandateGrantCurrentnessState.CURRENT or not grant_currentness.is_current:
            _fail(f"L9B11_P1_GRANT_NOT_CURRENT_{_state_label(grant_currentness.state)}")
        if (
            grant_currentness.tenant_id != grant.tenant_id
            or grant_currentness.client_grant_id != grant.client_grant_id
            or grant_currentness.client_grant_fingerprint != grant.fingerprint
            or grant_currentness.case_matter_id != grant.case_matter_id
            or grant_currentness.client_party_id != grant.client_party_id
            or grant_currentness.subject_identity_fingerprint != grant.subject_identity_fingerprint
        ):
            _fail("L9B11_P1_GRANT_CURRENTNESS_LINEAGE_INVALID")
        try:
            acknowledgment_currentness = LegalClientMatterMandateAcknowledgmentCurrentnessComposer(
                grant_collection=self._grant_collection,
                acknowledgment_collection=self._acknowledgment_collection,
            ).compose_currentness(tenant, grant_id, evaluation_time, transaction)
        except LegalClientMatterMandateAcknowledgmentCurrentnessComposerError as error:
            _fail("L9B11_P1_ACKNOWLEDGMENT_CURRENTNESS_FAILED", error)
        if acknowledgment_currentness.state is not LegalClientMatterMandateAcknowledgmentCurrentnessState.ACKNOWLEDGED or not acknowledgment_currentness.is_acknowledged:
            _fail(f"L9B11_P1_ACKNOWLEDGMENT_NOT_ACKNOWLEDGED_{_state_label(acknowledgment_currentness.state)}")
        if len(acknowledgment_currentness.decisive_acknowledgment_ids) != 1 or len(acknowledgment_currentness.decisive_acknowledgment_fingerprints) != 1:
            _fail("L9B11_P1_ACKNOWLEDGMENT_DECISION_AMBIGUOUS")
        acknowledgment_id = acknowledgment_currentness.decisive_acknowledgment_ids[0]
        acknowledgment_fingerprint = acknowledgment_currentness.decisive_acknowledgment_fingerprints[0]
        decisive = tuple(
            value for value in acknowledgment_history
            if value.acknowledgment_id == acknowledgment_id and value.fingerprint == acknowledgment_fingerprint
        )
        if len(decisive) != 1 or decisive[0].effective_from != evaluation_time:
            _fail("L9B11_P1_ACKNOWLEDGMENT_DECISIVE_EVIDENCE_INVALID")
        acknowledgment = decisive[0]
        mandate_id = _formation_id(tenant, grant.fingerprint, acknowledgment.fingerprint, idempotency)
        try:
            mandate = LegalClientMatterMandate(
                mandate_id=mandate_id,
                tenant_id=grant.tenant_id,
                case_matter_id=grant.case_matter_id,
                matter_fingerprint=grant.matter_fingerprint,
                client_party_id=grant.client_party_id,
                subject_identity_fingerprint=grant.subject_identity_fingerprint,
                grant_actor_principal_id=grant.grant_actor_principal_id,
                acting_capacity_id=grant.acting_capacity_id,
                acting_capacity_fingerprint=grant.acting_capacity_fingerprint,
                breadth=grant.breadth,
                scope_reference=grant.scope_reference,
                scope_fingerprint=grant.scope_fingerprint,
                capabilities=grant.capabilities,
                source_evidence_reference=grant.source_evidence_reference,
                source_evidence_fingerprint=grant.source_evidence_fingerprint,
                client_grant_reference=grant.client_grant_id,
                client_grant_fingerprint=grant.fingerprint,
                firm_acknowledgment_reference=acknowledgment.acknowledgment_id,
                firm_acknowledgment_fingerprint=acknowledgment.fingerprint,
                occurred_at=evaluation_time,
                effective_from=evaluation_time,
                effective_until=grant.effective_until,
                idempotency_key=idempotency,
            )
        except (TypeError, ValueError) as error:
            _fail("L9B11_P1_MANDATE_CONSTRUCTION_FAILED", error)
        try:
            return mandate_registry.persist_mandate(mandate, self._mandate_collection, session=transaction)
        except mandate_registry.LegalClientMatterMandateRegistryConflictError as error:
            _fail("L9B11_P1_MANDATE_DIVERGENT_REPLAY", error)
        except mandate_registry.LegalClientMatterMandateRegistryRetryRequiredError as error:
            _fail("L9B11_P1_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
        except mandate_registry.LegalClientMatterMandateRegistryError as error:
            _fail("L9B11_P1_MANDATE_PERSISTENCE_FAILED", error)


def compose_mandate(
    *,
    tenant_id: str,
    client_grant_id: str,
    idempotency_key: str,
    session: Any,
    grant_collection: Any,
    grant_lifecycle_collection: Any,
    matter_lifecycle_collection: Any,
    acknowledgment_collection: Any,
    mandate_collection: Any,
) -> LegalClientMatterMandate:
    """Functional one-shot boundary equivalent to the class composer."""
    return LegalClientMatterMandateComposer(
        grant_collection=grant_collection,
        grant_lifecycle_collection=grant_lifecycle_collection,
        matter_lifecycle_collection=matter_lifecycle_collection,
        acknowledgment_collection=acknowledgment_collection,
        mandate_collection=mandate_collection,
    ).compose_mandate(
        tenant_id=tenant_id,
        client_grant_id=client_grant_id,
        idempotency_key=idempotency_key,
        session=session,
    )


__all__ = [
    "VERSION",
    "LegalClientMatterMandateComposer",
    "LegalClientMatterMandateComposerError",
    "compose_mandate",
]


# ARTIFACT: legal_client_matter_mandate_composer.py
# VERSION: v1.0.0-L9B11-P1-CLIENT-MATTER-MANDATE-COMPOSER
# AUTHORITY BOUNDARY: immutable mandate formation orchestration only
# TENANT POSTURE: exact tenant/grant/acknowledgment lineage under one session
# FAIL-CLOSED POSTURE: no degraded currentness, chronology, replay or authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
