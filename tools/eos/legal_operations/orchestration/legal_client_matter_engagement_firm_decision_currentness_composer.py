"""Read-only composition of Engagement firm-decision currentness.

TITLE: WILSY OS Legal Client Matter Engagement Firm Decision Currentness Composer
VERSION: v1.0.0-L9C9-P4-ENGAGEMENT-FIRM-DECISION-CURRENTNESS-COMPOSER
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Perform one exact tenant-scoped firm-decision history read in a
         caller-owned transaction and delegate all currentness semantics to
         the certified pure P3 projection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_matter_engagement_firm_decision_currentness_composer.py
COLLABORATION / OWNERSHIP: The P1 registry owns durable history and the P3
                            domain owns effective-time currentness. This
                            adapter owns only validation, one read and
                            delegation.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C9-P4-ENGAGEMENT-FIRM-DECISION-CURRENTNESS-COMPOSER
           establishes exact history composition, explicit evaluation-time
           propagation, caller-session propagation and fail-closed errors.
           It performs no writes, transaction lifecycle, IAM, Engagement,
           Representation, Court or financial work.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only bounded opaque scope values and stable error
                             codes cross this boundary. Durable payloads and
                             persistence errors are never exposed.
TENANT BOUNDARY: The exact tenant, matter, matter fingerprint, client party
                 and subject fingerprint are passed unchanged to the registry.
AUTHORITY BOUNDARY: One read plus pure P3 delegation. No caller state,
                    latest selection, sorting, deduplication or future
                    filtering is authoritative here.
FINANCIAL AUTHORITY BOUNDARY: No financial execution, settlement or payment;
                              Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller supplies and owns an already-active Mongo
                      transaction. This module never starts, commits, aborts,
                      retries or reconciles a transaction.
FAIL-CLOSED DECLARATION: Missing/inactive sessions, invalid scope, registry
                         failures and projection failures reject with stable
                         non-sensitive codes.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final, NoReturn

from tools.eos.legal_operations.domain.legal_client_matter_engagement_firm_decision_currentness import (
    LegalClientMatterEngagementFirmDecisionCurrentness,
    project_legal_client_matter_engagement_firm_decision_currentness,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_engagement_firm_decision_registry as decision_registry,
)


VERSION: Final[str] = "v1.0.0-L9C9-P4-ENGAGEMENT-FIRM-DECISION-CURRENTNESS-COMPOSER"
UTC = timezone.utc


class LegalClientMatterEngagementFirmDecisionCurrentnessComposerError(RuntimeError):
    """Stable non-sensitive failure at the read-only composition boundary."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded code; never include evidence or PII."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one bounded orchestration error while retaining an internal cause."""
    error = LegalClientMatterEngagementFirmDecisionCurrentnessComposerError(code)
    if cause is None:
        raise error
    raise error from cause


def _text(name: str, value: object) -> str:
    """Require one exact non-empty opaque identity without coercion."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"L9C9_P4_{name.upper()}_INVALID")
    return value


def _evaluation_time(value: object) -> datetime:
    """Require explicit aware time and normalize only to UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail("L9C9_P4_EVALUATED_AT_INVALID")
    return value.astimezone(UTC)


def _active_transaction(session: Any) -> Any:
    """Require an already-active caller transaction without starting one."""
    if session is None:
        _fail("L9C9_P4_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail("L9C9_P4_ACTIVE_TRANSACTION_REQUIRED", error)
    if active is not True:
        _fail("L9C9_P4_ACTIVE_TRANSACTION_REQUIRED")
    return session


class LegalClientMatterEngagementFirmDecisionCurrentnessComposer:
    """Compose one exact-scope P3 projection from one registry history read.

    The caller supplies all five lineage values, an explicit aware evaluation
    instant and an active transaction. The exact same session is forwarded to
    the registry. The returned value is the immutable P3 projection; this
    class creates no Engagement or other downstream authority.
    """

    def __init__(self, *, decision_collection: Any) -> None:
        """Bind an explicit registry collection; never resolve or write Mongo."""
        if decision_collection is None:
            _fail("L9C9_P4_COLLECTION_REQUIRED")
        self._decision_collection = decision_collection

    def compose_currentness(
        self,
        tenant_id: str,
        case_matter_id: str,
        matter_fingerprint: str,
        client_party_id: str,
        subject_identity_fingerprint: str,
        evaluated_at: datetime,
        session: Any,
    ) -> LegalClientMatterEngagementFirmDecisionCurrentness:
        """Read exact history once and delegate unchanged to P3.

        Registry history is not sorted, filtered, deduplicated or interpreted
        here. P3 exclusively decides future exclusion, effective-time
        precedence, ambiguity, corruption and the resulting fingerprint.
        Transaction lifecycle remains entirely caller-owned.
        """
        transaction = _active_transaction(session)
        tenant = _text("tenant_id", tenant_id)
        matter = _text("case_matter_id", case_matter_id)
        matter_fp = _text("matter_fingerprint", matter_fingerprint)
        party = _text("client_party_id", client_party_id)
        subject = _text("subject_identity_fingerprint", subject_identity_fingerprint)
        at = _evaluation_time(evaluated_at)
        try:
            history = decision_registry.list_firm_decisions_for_context(
                tenant,
                matter,
                matter_fp,
                party,
                subject,
                self._decision_collection,
                session=transaction,
            )
        except decision_registry.LegalClientMatterEngagementFirmDecisionRegistryError as error:
            _fail("L9C9_P4_HISTORY_READ_FAILED", error)
        try:
            return project_legal_client_matter_engagement_firm_decision_currentness(
                tenant_id=tenant,
                case_matter_id=matter,
                matter_fingerprint=matter_fp,
                client_party_id=party,
                subject_identity_fingerprint=subject,
                evaluated_at=at,
                decisions=history,
            )
        except ValueError as error:
            _fail("L9C9_P4_PROJECTION_FAILED", error)


def compose_currentness(
    *,
    tenant_id: str,
    case_matter_id: str,
    matter_fingerprint: str,
    client_party_id: str,
    subject_identity_fingerprint: str,
    evaluated_at: datetime,
    session: Any,
    decision_collection: Any,
) -> LegalClientMatterEngagementFirmDecisionCurrentness:
    """Functional boundary equivalent to the explicit composer class."""
    composer = LegalClientMatterEngagementFirmDecisionCurrentnessComposer(
        decision_collection=decision_collection,
    )
    return composer.compose_currentness(
        tenant_id,
        case_matter_id,
        matter_fingerprint,
        client_party_id,
        subject_identity_fingerprint,
        evaluated_at,
        session,
    )


__all__ = [
    "VERSION",
    "LegalClientMatterEngagementFirmDecisionCurrentnessComposer",
    "LegalClientMatterEngagementFirmDecisionCurrentnessComposerError",
    "compose_currentness",
]


# ARTIFACT: legal_client_matter_engagement_firm_decision_currentness_composer.py
# VERSION: v1.0.0-L9C9-P4-ENGAGEMENT-FIRM-DECISION-CURRENTNESS-COMPOSER
# AUTHORITY BOUNDARY: one bounded registry read plus pure P3 delegation only
# TENANT POSTURE: exact tenant/matter/fingerprint/client/subject propagation
# FAIL-CLOSED POSTURE: active transaction and registry/projection failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
