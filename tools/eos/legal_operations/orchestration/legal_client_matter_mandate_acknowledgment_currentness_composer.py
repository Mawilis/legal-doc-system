"""Compose firm mandate-acknowledgment currentness from append-only history.

TITLE: WILSY OS Legal Client Matter Mandate Acknowledgment Currentness Composer
VERSION: v1.0.0-L9B10-P3-FIRM-MANDATE-ACKNOWLEDGMENT-CURRENTNESS-COMPOSER
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Read one exact client-grant formation and its tenant-scoped firm
         acknowledgment history in a caller-owned transaction, then derive the
         decision at one explicit evaluation instant. This composer selects
         history only; it never authorizes an actor or forms a mandate.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_matter_mandate_acknowledgment_currentness_composer.py
COLLABORATION / OWNERSHIP: The grant registry owns canonical grant lineage;
                            the acknowledgment registry owns append-only
                            decisions; the currentness projection owns state
                            invariants and fingerprinting. This module owns
                            transaction-scoped history selection only.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B10-P3-FIRM-MANDATE-ACKNOWLEDGMENT-CURRENTNESS-COMPOSER
           adds caller-owned active-transaction composition, exact grant and
           acknowledgment correlation, future-effective exclusion, latest
           effective-instant selection, equal-decision preservation and
           fail-closed conflict/corruption handling. No persistence, IAM,
           grant-currentness, mandate or Engagement authority is added.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only opaque IDs and SHA3-512 fingerprints cross
                             the boundary; failures expose stable codes and
                             never echo source evidence or caller secrets.
TENANT BOUNDARY: Formation and acknowledgment reads are exact tenant-scoped
                 registry calls under the same caller session. No fallback,
                 global lookup or cross-tenant inference exists.
AUTHORITY BOUNDARY: Read-only acknowledgment currentness selection. No IAM,
                    grant-currentness, mandate, Engagement, Representation,
                    Court, HTTP, UI or delivery authority.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement, release or execution;
                              Kennel EOS remains exclusive financial authority.
TRANSACTION BOUNDARY: Caller supplies and owns an already-active transaction.
                      This composer never starts, commits, aborts, retries or
                      persists a transaction or currentness projection.
FAIL-CLOSED DECLARATION: Missing transactions, unavailable registries,
                         divergent lineage, malformed evidence and conflicting
                         same-effective decisions never degrade to ACKNOWLEDGED.
"""
from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Final, NoReturn

from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment import (
    LegalClientMatterMandateAcknowledgment,
    LegalClientMatterMandateAcknowledgmentDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment_currentness import (
    LegalClientMatterMandateAcknowledgmentCurrentness,
    LegalClientMatterMandateAcknowledgmentCurrentnessReason,
    LegalClientMatterMandateAcknowledgmentCurrentnessState,
    project_legal_client_matter_mandate_acknowledgment_currentness,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant import (
    LegalClientMatterMandateGrant,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_mandate_acknowledgment_registry as acknowledgment_registry,
    legal_client_matter_mandate_grant_registry as grant_registry,
)


VERSION: Final[str] = (
    "v1.0.0-L9B10-P3-FIRM-MANDATE-ACKNOWLEDGMENT-CURRENTNESS-COMPOSER"
)
UTC: Final[timezone] = timezone.utc
_IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")


class LegalClientMatterMandateAcknowledgmentCurrentnessComposerError(RuntimeError):
    """Stable, non-sensitive fail-closed composition error.

    The composer is a read-only authority. The caller owns the transaction,
    while this error reports only a bounded code and never supplied evidence,
    identifiers, tokens or personal data.
    """

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable code without exposing the failed input."""
    error = LegalClientMatterMandateAcknowledgmentCurrentnessComposerError(code)
    if cause is None:
        raise error
    raise error from cause


def _text(name: str, value: object) -> str:
    """Require one bounded caller identity without trimming or coercion."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"L9B10_P3_{name.upper()}_INVALID")
    if _IDENTITY.fullmatch(value) is None:
        _fail(f"L9B10_P3_{name.upper()}_INVALID")
    return value


def _active_transaction(session: Any) -> Any:
    """Require the caller's already-active transaction before any registry read."""
    if session is None:
        _fail("L9B10_P3_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _fail("L9B10_P3_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _evaluation_time(value: object) -> datetime:
    """Require explicit aware UTC evaluation time without reading the clock."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail("L9B10_P3_EVALUATION_TIME_INVALID")
    return value.astimezone(UTC).replace(microsecond=value.microsecond)


def _projection_id(tenant_id: str, grant_id: str, evaluation_time: datetime) -> str:
    """Derive a deterministic in-memory projection identity without persistence."""
    payload = {
        "tenant_id": tenant_id,
        "client_grant_id": grant_id,
        "evaluation_time": evaluation_time.isoformat(timespec="microseconds"),
    }
    digest = hashlib.sha3_512(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:48]
    return f"currentness-{digest}"


def _ordered(
    history: Iterable[LegalClientMatterMandateAcknowledgment],
) -> tuple[LegalClientMatterMandateAcknowledgment, ...]:
    """Order evidence for deterministic output only, never authority precedence."""
    return tuple(
        sorted(
            history,
            key=lambda value: (
                value.effective_from,
                value.occurred_at,
                value.fingerprint,
                value.acknowledgment_id,
            ),
        )
    )


def _correlates(
    acknowledgment: object,
    grant: LegalClientMatterMandateGrant,
) -> bool:
    """Require every historical row to match the complete authoritative grant key."""
    return (
        type(acknowledgment) is LegalClientMatterMandateAcknowledgment
        and acknowledgment.tenant_id == grant.tenant_id
        and acknowledgment.client_grant_id == grant.client_grant_id
        and acknowledgment.client_grant_fingerprint == grant.fingerprint
        and acknowledgment.case_matter_id == grant.case_matter_id
        and acknowledgment.matter_fingerprint == grant.matter_fingerprint
        and acknowledgment.client_party_id == grant.client_party_id
        and acknowledgment.subject_identity_fingerprint
        == grant.subject_identity_fingerprint
    )


def _decision_value(value: LegalClientMatterMandateAcknowledgmentDecision | str) -> str:
    """Return the canonical decision string after strict domain hydration."""
    if isinstance(value, LegalClientMatterMandateAcknowledgmentDecision):
        return value.value
    if isinstance(value, str):
        return value
    _fail("L9B10_P3_DECISION_INVALID")


def _known_corruption_fingerprints(
    history: Iterable[object],
) -> tuple[str, ...]:
    """Retain only already-valid opaque fingerprints as corruption evidence."""
    fingerprints: list[str] = []
    for value in history:
        fingerprint = getattr(value, "fingerprint", None)
        if (
            isinstance(fingerprint, str)
            and len(fingerprint) == 128
            and all(character in "0123456789abcdef" for character in fingerprint)
            and fingerprint not in fingerprints
        ):
            fingerprints.append(fingerprint)
    return tuple(fingerprints)


def _corrupt_projection(
    *,
    grant: LegalClientMatterMandateGrant,
    evaluation_time: datetime,
    history: Iterable[object],
) -> LegalClientMatterMandateAcknowledgmentCurrentness:
    """Return CORRUPT_BLOCKED when safe lineage and corruption evidence exist."""
    corruption = _known_corruption_fingerprints(history)
    if not corruption:
        _fail("L9B10_P3_CORRUPT_HISTORY")
    return project_legal_client_matter_mandate_acknowledgment_currentness(
        currentness_id=_projection_id(grant.tenant_id, grant.client_grant_id, evaluation_time),
        tenant_id=grant.tenant_id,
        client_grant_id=grant.client_grant_id,
        client_grant_fingerprint=grant.fingerprint,
        case_matter_id=grant.case_matter_id,
        matter_fingerprint=grant.matter_fingerprint,
        client_party_id=grant.client_party_id,
        subject_identity_fingerprint=grant.subject_identity_fingerprint,
        evaluation_time=evaluation_time,
        state=LegalClientMatterMandateAcknowledgmentCurrentnessState.CORRUPT_BLOCKED,
        reason=LegalClientMatterMandateAcknowledgmentCurrentnessReason.CORRUPT_EVIDENCE,
        acknowledgment_evidence_fingerprints=(),
        decisive_acknowledgment_ids=(),
        decisive_acknowledgment_fingerprints=(),
        decisive_decisions=(),
        corruption_evidence_fingerprints=corruption,
    )


def _decision_projection(
    *,
    grant: LegalClientMatterMandateGrant,
    evaluation_time: datetime,
    applicable: tuple[LegalClientMatterMandateAcknowledgment, ...],
) -> LegalClientMatterMandateAcknowledgmentCurrentness:
    """Select the latest effective instant and construct the published value."""
    ordered = _ordered(applicable)
    latest_effective = max(value.effective_from for value in ordered)
    decisive = tuple(value for value in ordered if value.effective_from == latest_effective)
    decisions = {_decision_value(value.decision) for value in decisive}
    evidence = tuple(value.fingerprint for value in ordered)
    decisive_ids = tuple(value.acknowledgment_id for value in decisive)
    decisive_fingerprints = tuple(value.fingerprint for value in decisive)
    decisive_decisions = tuple(_decision_value(value.decision) for value in decisive)
    if len(decisions) > 1:
        state = LegalClientMatterMandateAcknowledgmentCurrentnessState.AMBIGUOUS
        reason = LegalClientMatterMandateAcknowledgmentCurrentnessReason.AMBIGUOUS_DECISIONS
    else:
        decision = next(iter(decisions))
        state = LegalClientMatterMandateAcknowledgmentCurrentnessState(decision)
        reason = LegalClientMatterMandateAcknowledgmentCurrentnessReason(decision)
    return project_legal_client_matter_mandate_acknowledgment_currentness(
        currentness_id=_projection_id(grant.tenant_id, grant.client_grant_id, evaluation_time),
        tenant_id=grant.tenant_id,
        client_grant_id=grant.client_grant_id,
        client_grant_fingerprint=grant.fingerprint,
        case_matter_id=grant.case_matter_id,
        matter_fingerprint=grant.matter_fingerprint,
        client_party_id=grant.client_party_id,
        subject_identity_fingerprint=grant.subject_identity_fingerprint,
        evaluation_time=evaluation_time,
        state=state,
        reason=reason,
        acknowledgment_evidence_fingerprints=evidence,
        decisive_acknowledgment_ids=decisive_ids,
        decisive_acknowledgment_fingerprints=decisive_fingerprints,
        decisive_decisions=decisive_decisions,
    )


class LegalClientMatterMandateAcknowledgmentCurrentnessComposer:
    """Compose one read-only acknowledgment currentness projection.

    The constructor receives explicit grant and acknowledgment collection
    handles. ``compose_currentness`` accepts only tenant, grant, evaluation
    time and an active caller session. Formation lineage is read from the
    canonical grant registry; decision state and history are read from the
    acknowledgment registry. No caller-supplied decision or evidence is
    trusted, and the caller owns transaction lifecycle completely.
    """

    def __init__(self, *, grant_collection: Any, acknowledgment_collection: Any) -> None:
        """Bind explicit read-only collection handles; never resolve a database."""
        if grant_collection is None or acknowledgment_collection is None:
            _fail("L9B10_P3_COLLECTION_REQUIRED")
        self._grant_collection = grant_collection
        self._acknowledgment_collection = acknowledgment_collection

    def compose_currentness(
        self,
        tenant_id: str,
        client_grant_id: str,
        evaluation_time: datetime,
        session: Any,
    ) -> LegalClientMatterMandateAcknowledgmentCurrentness:
        """Read exact formation/history and return currentness at explicit T.

        Both registry reads receive the identical active session. Future
        effective decisions are excluded. The latest effective instant, not
        insertion order, ``occurred_at`` or fingerprint order, determines the
        decision; incompatible decisions at that instant are ambiguous.
        """
        transaction = _active_transaction(session)
        tenant = _text("tenant_id", tenant_id)
        grant_id = _text("client_grant_id", client_grant_id)
        at = _evaluation_time(evaluation_time)
        try:
            grant = grant_registry.get_grant(
                tenant,
                grant_id,
                self._grant_collection,
                session=transaction,
            )
        except grant_registry.LegalClientMatterMandateGrantRegistryError as error:
            _fail("L9B10_P3_GRANT_READ_FAILED", error)
        if type(grant) is not LegalClientMatterMandateGrant or not (
            grant.tenant_id == tenant and grant.client_grant_id == grant_id
        ):
            _fail("L9B10_P3_GRANT_CORRELATION_INVALID")
        try:
            history = acknowledgment_registry.list_acknowledgments_for_grant(
                tenant,
                grant_id,
                self._acknowledgment_collection,
                session=transaction,
            )
        except acknowledgment_registry.LegalClientMatterMandateAcknowledgmentRegistryError as error:
            _fail("L9B10_P3_ACKNOWLEDGMENT_HISTORY_READ_FAILED", error)
        if any(not _correlates(value, grant) for value in history):
            return _corrupt_projection(
                grant=grant,
                evaluation_time=at,
                history=history,
            )
        applicable = tuple(value for value in history if value.effective_from <= at)
        if not applicable:
            return project_legal_client_matter_mandate_acknowledgment_currentness(
                currentness_id=_projection_id(tenant, grant_id, at),
                tenant_id=grant.tenant_id,
                client_grant_id=grant.client_grant_id,
                client_grant_fingerprint=grant.fingerprint,
                case_matter_id=grant.case_matter_id,
                matter_fingerprint=grant.matter_fingerprint,
                client_party_id=grant.client_party_id,
                subject_identity_fingerprint=grant.subject_identity_fingerprint,
                evaluation_time=at,
                state=LegalClientMatterMandateAcknowledgmentCurrentnessState.NO_DECISION,
                reason=LegalClientMatterMandateAcknowledgmentCurrentnessReason.NO_DECISION,
                acknowledgment_evidence_fingerprints=(),
                decisive_acknowledgment_ids=(),
                decisive_acknowledgment_fingerprints=(),
                decisive_decisions=(),
            )
        return _decision_projection(
            grant=grant,
            evaluation_time=at,
            applicable=applicable,
        )


def compose_currentness(
    *,
    tenant_id: str,
    client_grant_id: str,
    evaluation_time: datetime,
    session: Any,
    grant_collection: Any,
    acknowledgment_collection: Any,
) -> LegalClientMatterMandateAcknowledgmentCurrentness:
    """Compose through a one-shot functional boundary with the same contract."""
    composer = LegalClientMatterMandateAcknowledgmentCurrentnessComposer(
        grant_collection=grant_collection,
        acknowledgment_collection=acknowledgment_collection,
    )
    return composer.compose_currentness(tenant_id, client_grant_id, evaluation_time, session)


__all__ = [
    "VERSION",
    "LegalClientMatterMandateAcknowledgmentCurrentnessComposer",
    "LegalClientMatterMandateAcknowledgmentCurrentnessComposerError",
    "compose_currentness",
]


# ARTIFACT: legal_client_matter_mandate_acknowledgment_currentness_composer.py
# VERSION: v1.0.0-L9B10-P3-FIRM-MANDATE-ACKNOWLEDGMENT-CURRENTNESS-COMPOSER
# AUTHORITY BOUNDARY: read-only acknowledgment currentness composition only
# TENANT POSTURE: exact grant lineage and tenant-scoped registry reads
# FAIL-CLOSED POSTURE: active transaction, correlation, chronology and conflict validation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
