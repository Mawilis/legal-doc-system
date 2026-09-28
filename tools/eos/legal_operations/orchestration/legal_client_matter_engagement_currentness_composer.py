"""Read-only composition of Engagement currentness.

TITLE: WILSY OS Legal Client Matter Engagement Currentness Composer
VERSION: v1.0.0-L9C11-P4-ENGAGEMENT-CURRENTNESS-COMPOSER
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Perform one exact tenant/matter/client/subject Engagement-history read
         inside a caller-owned transaction and delegate every currentness rule
         to the certified P3 pure domain projection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_matter_engagement_currentness_composer.py
COLLABORATION / OWNERSHIP: The Engagement registry owns durable immutable
                            history; the P3 currentness domain owns all state,
                            duplicate, future and ambiguity semantics. This
                            adapter owns only validation, one read and
                            delegation.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P4 establishes active caller-transaction enforcement,
           exact five-field history reads, explicit evaluation-time propagation,
           unchanged P3 delegation and bounded registry/projection error
           mapping. It creates no current pointer, lifecycle, IAM,
           Representation, Court, financial, HTTP or client authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only bounded identity inputs and stable error codes
                             cross this boundary; durable payloads and raw
                             persistence errors are not exposed.
TENANT BOUNDARY: Exact tenant, matter, matter fingerprint, client party and
                 subject fingerprint are passed unchanged to the registry.
AUTHORITY BOUNDARY: One read plus pure P3 delegation. No caller-supplied state,
                    decisive record, latest selection, current pointer, IAM,
                    Representation, Court or actor authentication.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement, billing or execution
                              authority; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller supplies and owns an already-active transaction.
                      This module never starts, commits, aborts, retries or
                      reconciles a transaction.
FAIL-CLOSED DECLARATION: Missing/inactive sessions, invalid inputs, registry
                         failures and projection failures reject with bounded
                         composer-specific errors.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final, NoReturn

from tools.eos.legal_operations.domain.legal_client_matter_engagement_currentness import (
    LegalClientMatterEngagementCurrentness,
    project_legal_client_matter_engagement_currentness,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_engagement_registry as engagement_registry,
)


VERSION: Final[str] = "v1.0.0-L9C11-P4-ENGAGEMENT-CURRENTNESS-COMPOSER"
UTC = timezone.utc


class LegalClientMatterEngagementCurrentnessComposerError(RuntimeError):
    """Stable non-sensitive failure at the read-only composition boundary."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded code and never persistence payloads."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one bounded orchestration error while retaining internal cause."""
    error = LegalClientMatterEngagementCurrentnessComposerError(code)
    if cause is None:
        raise error
    raise error from cause


def _text(name: str, value: object) -> str:
    """Require one exact non-empty identity without trimming or coercion."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"L9C11_P4_{name.upper()}_INVALID")
    return value


def _evaluation_time(value: object) -> datetime:
    """Require an explicit aware instant and normalize only through UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail("L9C11_P4_EVALUATED_AT_INVALID")
    return value.astimezone(UTC)


def _active_transaction(session: Any) -> Any:
    """Require an already-active caller transaction without starting one."""
    if session is None:
        _fail("L9C11_P4_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail("L9C11_P4_ACTIVE_TRANSACTION_REQUIRED", error)
    if active is not True:
        _fail("L9C11_P4_ACTIVE_TRANSACTION_REQUIRED")
    return session


class LegalClientMatterEngagementCurrentnessComposer:
    """Compose one exact P3 currentness value from one registry history read.

    The caller supplies exact lineage, an explicit aware evaluation instant,
    and an active transaction. The same session object is forwarded unchanged.
    Registry history is passed to P3 without sorting, filtering, deduplication,
    latest-wins selection or rewriting. This class creates no downstream
    authority and owns no transaction lifecycle.
    """

    def __init__(self, *, engagement_collection: Any) -> None:
        """Bind an explicit registry collection; never resolve or write Mongo."""
        if engagement_collection is None:
            _fail("L9C11_P4_COLLECTION_REQUIRED")
        self._engagement_collection = engagement_collection

    def compose_currentness(
        self,
        tenant_id: str,
        case_matter_id: str,
        matter_fingerprint: str,
        client_party_id: str,
        subject_identity_fingerprint: str,
        evaluated_at: datetime,
        session: Any,
    ) -> LegalClientMatterEngagementCurrentness:
        """Read exact history once and delegate unchanged to P3.

        The caller owns the transaction. P3 exclusively decides future
        exclusion, exact-duplicate normalization, multiplicity ambiguity,
        corruption and the resulting deterministic fingerprint.
        """
        transaction = _active_transaction(session)
        tenant = _text("tenant_id", tenant_id)
        matter = _text("case_matter_id", case_matter_id)
        matter_fp = _text("matter_fingerprint", matter_fingerprint)
        party = _text("client_party_id", client_party_id)
        subject = _text("subject_identity_fingerprint", subject_identity_fingerprint)
        at = _evaluation_time(evaluated_at)
        try:
            history = engagement_registry.list_engagements_for_context(
                tenant,
                matter,
                matter_fp,
                party,
                subject,
                self._engagement_collection,
                session=transaction,
            )
        except engagement_registry.LegalClientMatterEngagementRegistryError as error:
            _fail("L9C11_P4_HISTORY_READ_FAILED", error)
        try:
            return project_legal_client_matter_engagement_currentness(
                tenant_id=tenant,
                case_matter_id=matter,
                matter_fingerprint=matter_fp,
                client_party_id=party,
                subject_identity_fingerprint=subject,
                evaluated_at=at,
                engagements=history,
            )
        except ValueError as error:
            _fail("L9C11_P4_PROJECTION_FAILED", error)


def compose_currentness(
    *,
    tenant_id: str,
    case_matter_id: str,
    matter_fingerprint: str,
    client_party_id: str,
    subject_identity_fingerprint: str,
    evaluated_at: datetime,
    session: Any,
    engagement_collection: Any,
) -> LegalClientMatterEngagementCurrentness:
    """Functional boundary equivalent to the explicit composer class."""
    composer = LegalClientMatterEngagementCurrentnessComposer(
        engagement_collection=engagement_collection,
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
    "LegalClientMatterEngagementCurrentnessComposer",
    "LegalClientMatterEngagementCurrentnessComposerError",
    "compose_currentness",
]


# ARTIFACT: legal_client_matter_engagement_currentness_composer.py
# VERSION: v1.0.0-L9C11-P4-ENGAGEMENT-CURRENTNESS-COMPOSER
# AUTHORITY BOUNDARY: one bounded Engagement-history read plus pure P3 delegation
# TENANT POSTURE: exact tenant/matter/fingerprint/client/subject propagation
# FAIL-CLOSED POSTURE: active transaction and registry/projection failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
