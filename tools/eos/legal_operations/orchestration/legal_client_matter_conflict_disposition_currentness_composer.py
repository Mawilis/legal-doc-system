"""Read-only composition of conflict-disposition currentness.

TITLE: WILSY OS Legal Client Matter Conflict Disposition Currentness Composer
VERSION: v1.0.0-L9C5-CONFLICT-DISPOSITION-CURRENTNESS-COMPOSER
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Read one exact tenant/matter/client/subject disposition history under
         a caller-owned active transaction and delegate all currentness
         semantics to the certified pure projection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_matter_conflict_disposition_currentness_composer.py
COLLABORATION / OWNERSHIP: The L9C3 disposition registry owns durable
                            append-only history; the L9C5 domain projection
                            owns effective-time and ambiguity semantics. This
                            composer owns only one bounded read and delegation.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9C5-CONFLICT-DISPOSITION-CURRENTNESS-COMPOSER adds exact
           context history composition, caller-session propagation, explicit
           evaluation-time propagation and fail-closed registry error mapping.
           It performs no writes, transaction lifecycle, currentness
           persistence, screening/review rereads, IAM or Engagement work.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only bounded opaque scope values and stable error
                             codes cross this boundary. Registry failures are
                             mapped without exposing durable payloads.
TENANT BOUNDARY: The exact tenant, matter, matter fingerprint, client party
                 and subject fingerprint are passed unchanged to the registry.
AUTHORITY BOUNDARY: Read-only currentness composition. No caller-supplied
                    state, decisive record, clock, IAM, ClientAcceptance,
                    mandate, Engagement, Representation or Court authority.
FINANCIAL AUTHORITY BOUNDARY: No financial execution, settlement or payment;
                              Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller supplies and owns an already-active Mongo
                      transaction. This module never starts, commits, aborts,
                      retries or reconciles a transaction.
FAIL-CLOSED DECLARATION: Missing/inactive sessions, invalid inputs, registry
                         corruption/unavailability and projection failures
                         reject with stable non-sensitive codes.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final, NoReturn

from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition_currentness import (
    LegalClientMatterConflictDispositionCurrentness,
    project_legal_client_matter_conflict_disposition_currentness,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_conflict_disposition_registry as disposition_registry,
)


VERSION: Final[str] = "v1.0.0-L9C5-CONFLICT-DISPOSITION-CURRENTNESS-COMPOSER"
UTC = timezone.utc


class LegalClientMatterConflictDispositionCurrentnessComposerError(RuntimeError):
    """Stable non-sensitive failure at the read-only composition boundary."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalClientMatterConflictDispositionCurrentnessComposerError(code)
    if cause is None:
        raise error
    raise error from cause


def _text(name: str, value: object) -> str:
    """Require an exact non-empty identity without trimming or coercion."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"L9C5_P2_{name.upper()}_INVALID")
    return value


def _evaluation_time(value: object) -> datetime:
    """Require explicit aware time and canonicalize only through UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail("L9C5_P2_EVALUATION_TIME_INVALID")
    return value.astimezone(UTC).replace(microsecond=value.microsecond)


def _active_transaction(session: Any) -> Any:
    """Require an already-active caller transaction without starting one."""
    if session is None:
        _fail("L9C5_P2_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail("L9C5_P2_ACTIVE_TRANSACTION_REQUIRED", error)
    if active is not True:
        _fail("L9C5_P2_ACTIVE_TRANSACTION_REQUIRED")
    return session


class LegalClientMatterConflictDispositionCurrentnessComposer:
    """Compose one exact-scope currentness value from durable history.

    The explicit collection is read through the published registry exactly
    once. The identical caller session is forwarded unchanged. Empty history
    is valid and becomes ``NO_DISPOSITION`` through the pure projection. This
    class owns no transaction lifecycle and creates no downstream authority.
    """

    def __init__(self, *, disposition_collection: Any) -> None:
        """Bind an explicit registry collection; never resolve or write Mongo."""
        if disposition_collection is None:
            _fail("L9C5_P2_COLLECTION_REQUIRED")
        self._disposition_collection = disposition_collection

    def compose_currentness(
        self,
        tenant_id: str,
        case_matter_id: str,
        matter_fingerprint: str,
        client_party_id: str,
        subject_identity_fingerprint: str,
        evaluation_time: datetime,
        session: Any,
    ) -> LegalClientMatterConflictDispositionCurrentness:
        """Read exact history and delegate all semantics to the projection.

        The caller owns the active transaction. The registry receives every
        scope field and the same session object. This method never selects a
        latest record, compares states, constructs a fingerprint, reads a
        clock, persists currentness, or rereads screening/review authority.
        """
        transaction = _active_transaction(session)
        tenant = _text("tenant_id", tenant_id)
        matter = _text("case_matter_id", case_matter_id)
        matter_fp = _text("matter_fingerprint", matter_fingerprint)
        party = _text("client_party_id", client_party_id)
        subject = _text("subject_identity_fingerprint", subject_identity_fingerprint)
        at = _evaluation_time(evaluation_time)
        try:
            history = disposition_registry.list_dispositions_for_context(
                tenant,
                matter,
                matter_fp,
                party,
                subject,
                self._disposition_collection,
                session=transaction,
            )
        except disposition_registry.LegalClientMatterConflictDispositionRegistryError as error:
            _fail("L9C5_P2_HISTORY_READ_FAILED", error)
        try:
            return project_legal_client_matter_conflict_disposition_currentness(
                tenant_id=tenant,
                case_matter_id=matter,
                matter_fingerprint=matter_fp,
                client_party_id=party,
                subject_identity_fingerprint=subject,
                evaluation_time=at,
                dispositions=history,
            )
        except ValueError as error:
            _fail("L9C5_P2_PROJECTION_FAILED", error)


def compose_currentness(
    *,
    tenant_id: str,
    case_matter_id: str,
    matter_fingerprint: str,
    client_party_id: str,
    subject_identity_fingerprint: str,
    evaluation_time: datetime,
    session: Any,
    disposition_collection: Any,
) -> LegalClientMatterConflictDispositionCurrentness:
    """Compose through a one-shot functional boundary with identical rules."""
    composer = LegalClientMatterConflictDispositionCurrentnessComposer(
        disposition_collection=disposition_collection,
    )
    return composer.compose_currentness(
        tenant_id,
        case_matter_id,
        matter_fingerprint,
        client_party_id,
        subject_identity_fingerprint,
        evaluation_time,
        session,
    )


__all__ = [
    "VERSION",
    "LegalClientMatterConflictDispositionCurrentnessComposer",
    "LegalClientMatterConflictDispositionCurrentnessComposerError",
    "compose_currentness",
]


# ARTIFACT: legal_client_matter_conflict_disposition_currentness_composer.py
# VERSION: v1.0.0-L9C5-CONFLICT-DISPOSITION-CURRENTNESS-COMPOSER
# AUTHORITY BOUNDARY: one bounded read plus pure currentness delegation only
# TENANT POSTURE: exact tenant/matter/fingerprint/client/subject propagation
# FAIL-CLOSED POSTURE: active transaction and registry/projection failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
