"""Read-only composition of firm Representation decision currentness.

TITLE: WILSY OS Legal Client Matter Representation Firm Decision Currentness Composer
VERSION: v1.0.0-L9C11-P22-FIRM-REPRESENTATION-DECISION-CURRENTNESS-COMPOSER
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Perform exactly one bounded P9 history read for one exact P2
         decision lineage and delegate all semantics to the pure P22 domain.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_matter_representation_firm_decision_currentness_composer.py
COLLABORATION / OWNERSHIP: P2 owns immutable decision evidence; P9 owns the
                            durable history query; P22 domain owns projection
                            semantics. This adapter owns only validation,
                            one read and delegation.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P22 establishes exact P1/representative/role lineage,
           explicit evaluation-time propagation, same-session forwarding and
           zero-write composition. It starts no transaction and performs no
           IAM, Representation, Court or financial work.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only bounded opaque identifiers and stable error
                             codes cross this boundary; persistence payloads
                             and technical errors remain internal.
TENANT BOUNDARY: Exact tenant, matter, client, subject, P1 authority,
                 representative principal and role are propagated unchanged.
AUTHORITY BOUNDARY: One P9 read plus pure P22 delegation only. No sorting,
                    latest-wins, precedence, lifecycle, IAM or downstream
                    Representation authority is introduced.
FINANCIAL AUTHORITY BOUNDARY: No financial execution or settlement; Kennel EOS
                               remains exclusive.
TRANSACTION BOUNDARY: Caller supplies an active transaction. This module never
                      starts, commits, aborts, retries or owns its lifecycle.
FAIL-CLOSED DECLARATION: Missing/inactive sessions, invalid scope, registry
                         failures and projection failures reject with stable
                         non-sensitive composer codes.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final, NoReturn

from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision_currentness import (
    LegalClientMatterRepresentationFirmDecisionCurrentness,
    project_legal_client_matter_representation_firm_decision_currentness,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_representation_firm_decision_registry as decision_registry,
)


VERSION: Final[str] = "v1.0.0-L9C11-P22-FIRM-REPRESENTATION-DECISION-CURRENTNESS-COMPOSER"
UTC = timezone.utc


class LegalClientMatterRepresentationFirmDecisionCurrentnessComposerError(RuntimeError):
    """Stable non-sensitive failure at the read-only composition boundary."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalClientMatterRepresentationFirmDecisionCurrentnessComposerError(code)
    if cause is None:
        raise error
    raise error from cause


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"L9C11_P22_COMPOSER_{name.upper()}_INVALID")
    return value


def _evaluation_time(value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail("L9C11_P22_COMPOSER_EVALUATED_AT_INVALID")
    return value.astimezone(UTC)


def _active_transaction(session: Any) -> Any:
    if session is None:
        _fail("L9C11_P22_COMPOSER_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail("L9C11_P22_COMPOSER_ACTIVE_TRANSACTION_REQUIRED", error)
    if active is not True:
        _fail("L9C11_P22_COMPOSER_ACTIVE_TRANSACTION_REQUIRED")
    return session


class LegalClientMatterRepresentationFirmDecisionCurrentnessComposer:
    """Compose one P22 projection from one exact P9 history read.

    The same caller-owned session is forwarded to P9. P22 exclusively decides
    duplicate normalization, future exclusion, ambiguity and corruption.
    """

    def __init__(self, *, decision_collection: Any) -> None:
        if decision_collection is None:
            _fail("L9C11_P22_COMPOSER_COLLECTION_REQUIRED")
        self._decision_collection = decision_collection

    def compose_currentness(
        self,
        tenant_id: str,
        case_matter_id: str,
        matter_fingerprint: str,
        client_party_id: str,
        subject_identity_fingerprint: str,
        representation_authority_id: str,
        representation_authority_fingerprint: str,
        representative_principal_id: str,
        representative_role: str,
        evaluated_at: datetime,
        session: Any,
    ) -> LegalClientMatterRepresentationFirmDecisionCurrentness:
        """Read P9 once and delegate unchanged to pure P22."""
        transaction = _active_transaction(session)
        tenant = _text("tenant_id", tenant_id)
        matter = _text("case_matter_id", case_matter_id)
        matter_fp = _text("matter_fingerprint", matter_fingerprint)
        party = _text("client_party_id", client_party_id)
        subject = _text("subject_identity_fingerprint", subject_identity_fingerprint)
        authority_id = _text("representation_authority_id", representation_authority_id)
        authority_fp = _text("representation_authority_fingerprint", representation_authority_fingerprint)
        representative = _text("representative_principal_id", representative_principal_id)
        role = _text("representative_role", representative_role)
        at = _evaluation_time(evaluated_at)
        try:
            history = decision_registry.list_firm_decisions_for_context(
                tenant,
                matter,
                matter_fp,
                party,
                subject,
                authority_id,
                authority_fp,
                representative,
                self._decision_collection,
                session=transaction,
            )
        except decision_registry.LegalClientMatterRepresentationFirmDecisionRegistryError as error:
            _fail("L9C11_P22_COMPOSER_HISTORY_READ_FAILED", error)
        try:
            return project_legal_client_matter_representation_firm_decision_currentness(
                tenant_id=tenant,
                case_matter_id=matter,
                matter_fingerprint=matter_fp,
                client_party_id=party,
                subject_identity_fingerprint=subject,
                representation_authority_id=authority_id,
                representation_authority_fingerprint=authority_fp,
                representative_principal_id=representative,
                representative_role=role,
                evaluated_at=at,
                decisions=history,
            )
        except ValueError as error:
            _fail("L9C11_P22_COMPOSER_PROJECTION_FAILED", error)


def compose_currentness(
    *,
    tenant_id: str,
    case_matter_id: str,
    matter_fingerprint: str,
    client_party_id: str,
    subject_identity_fingerprint: str,
    representation_authority_id: str,
    representation_authority_fingerprint: str,
    representative_principal_id: str,
    representative_role: str,
    evaluated_at: datetime,
    session: Any,
    decision_collection: Any,
) -> LegalClientMatterRepresentationFirmDecisionCurrentness:
    """Functional boundary equivalent to the explicit composer class."""
    return LegalClientMatterRepresentationFirmDecisionCurrentnessComposer(
        decision_collection=decision_collection,
    ).compose_currentness(
        tenant_id,
        case_matter_id,
        matter_fingerprint,
        client_party_id,
        subject_identity_fingerprint,
        representation_authority_id,
        representation_authority_fingerprint,
        representative_principal_id,
        representative_role,
        evaluated_at,
        session,
    )


__all__ = [
    "VERSION",
    "LegalClientMatterRepresentationFirmDecisionCurrentnessComposer",
    "LegalClientMatterRepresentationFirmDecisionCurrentnessComposerError",
    "compose_currentness",
]


# ARTIFACT: legal_client_matter_representation_firm_decision_currentness_composer.py
# VERSION: v1.0.0-L9C11-P22-FIRM-REPRESENTATION-DECISION-CURRENTNESS-COMPOSER
# AUTHORITY BOUNDARY: one bounded P9 read plus pure P22 delegation only
# TENANT POSTURE: exact P1 and representative lineage propagation
# FAIL-CLOSED POSTURE: active transaction and registry/projection failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
