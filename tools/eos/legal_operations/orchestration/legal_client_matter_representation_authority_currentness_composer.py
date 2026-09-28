"""Read-only composition of client Representation-authority currentness.

TITLE: WILSY OS Legal Client Matter Representation Authority Currentness Composer
VERSION: v1.0.0-L9C11-P21A-CLIENT-REPRESENTATION-AUTHORITY-CURRENTNESS-COMPOSER
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Perform exactly one exact representative-specific P7 history read in
         a caller-owned transaction and delegate every currentness rule to
         the certified pure P21A projection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_matter_representation_authority_currentness_composer.py
COLLABORATION / OWNERSHIP: P1 owns immutable authority values; P7 owns
                            durable history and exact lineage reads; the P21A
                            domain owns all state, duplicate, future,
                            corruption and ambiguity semantics. This adapter
                            owns only validation, one read and delegation.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P21A establishes explicit evaluated-time propagation,
           exact six-field P7 lineage, active caller-session enforcement,
           one-read composition and fail-closed registry/projection mapping.
           It performs no writes, transaction lifecycle, IAM, firm decision,
           Representation, Court or financial work.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only bounded opaque identities and stable error
                             codes cross this boundary; source payloads and
                             persistence errors are not exposed.
TENANT BOUNDARY: Exact tenant, matter, matter fingerprint, client party,
                 subject fingerprint and representative principal are passed
                 unchanged to P7.
AUTHORITY BOUNDARY: One P7 read plus pure P21A delegation. No latest-wins,
                    sorting, deduplication, lifecycle, IAM, firm decision,
                    Representation, Court or actor authentication.
FINANCIAL AUTHORITY BOUNDARY: No financial execution, settlement or payment;
                              Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller supplies and owns an already-active Mongo
                      transaction. This module never starts, commits, aborts,
                      retries or reconciles a transaction.
FAIL-CLOSED DECLARATION: Missing/inactive sessions, invalid scope, registry
                         failures and projection failures reject with stable
                         non-sensitive composer codes.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final, NoReturn

from tools.eos.legal_operations.domain.legal_client_matter_representation_authority_currentness import (
    LegalClientMatterRepresentationAuthorityCurrentness,
    project_legal_client_matter_representation_authority_currentness,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_representation_authority_registry as authority_registry,
)


VERSION: Final[str] = "v1.0.0-L9C11-P21A-CLIENT-REPRESENTATION-AUTHORITY-CURRENTNESS-COMPOSER"
UTC = timezone.utc


class LegalClientMatterRepresentationAuthorityCurrentnessComposerError(RuntimeError):
    """Stable non-sensitive failure at the read-only composition boundary."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded code and never persistence payloads."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalClientMatterRepresentationAuthorityCurrentnessComposerError(code)
    if cause is None:
        raise error
    raise error from cause


def _text(name: str, value: object) -> str:
    """Require one exact non-empty opaque identity without coercion."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"L9C11_P21A_COMPOSER_{name.upper()}_INVALID")
    return value


def _evaluation_time(value: object) -> datetime:
    """Require explicit aware time and normalize only to UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail("L9C11_P21A_COMPOSER_EVALUATED_AT_INVALID")
    return value.astimezone(UTC)


def _active_transaction(session: Any) -> Any:
    """Require an already-active caller transaction without starting one."""
    if session is None:
        _fail("L9C11_P21A_COMPOSER_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail("L9C11_P21A_COMPOSER_ACTIVE_TRANSACTION_REQUIRED", error)
    if active is not True:
        _fail("L9C11_P21A_COMPOSER_ACTIVE_TRANSACTION_REQUIRED")
    return session


class LegalClientMatterRepresentationAuthorityCurrentnessComposer:
    """Compose one exact P21A projection from one P7 history read.

    The caller supplies all six P7 lineage values, an explicit aware
    evaluation instant and an active transaction. The identical session is
    forwarded unchanged. P21A alone decides future exclusion, exact
    duplicate normalization, multiplicity ambiguity and corruption.
    """

    def __init__(self, *, authority_collection: Any) -> None:
        """Bind an explicit P7 collection; never resolve or write Mongo."""
        if authority_collection is None:
            _fail("L9C11_P21A_COMPOSER_COLLECTION_REQUIRED")
        self._authority_collection = authority_collection

    def compose_currentness(
        self,
        tenant_id: str,
        case_matter_id: str,
        matter_fingerprint: str,
        client_party_id: str,
        subject_identity_fingerprint: str,
        representative_principal_id: str,
        evaluated_at: datetime,
        session: Any,
    ) -> LegalClientMatterRepresentationAuthorityCurrentness:
        """Read exact P7 history once and delegate unchanged to P21A.

        The caller owns transaction lifecycle. This method never starts,
        commits or aborts a transaction and never writes a currentness row.
        """
        transaction = _active_transaction(session)
        tenant = _text("tenant_id", tenant_id)
        matter = _text("case_matter_id", case_matter_id)
        matter_fp = _text("matter_fingerprint", matter_fingerprint)
        party = _text("client_party_id", client_party_id)
        subject = _text("subject_identity_fingerprint", subject_identity_fingerprint)
        representative = _text("representative_principal_id", representative_principal_id)
        at = _evaluation_time(evaluated_at)
        try:
            history = authority_registry.list_representation_authorities_for_context(
                tenant,
                matter,
                matter_fp,
                party,
                subject,
                representative,
                self._authority_collection,
                session=transaction,
            )
        except authority_registry.LegalClientMatterRepresentationAuthorityRegistryError as error:
            _fail("L9C11_P21A_COMPOSER_HISTORY_READ_FAILED", error)
        try:
            return project_legal_client_matter_representation_authority_currentness(
                tenant_id=tenant,
                case_matter_id=matter,
                matter_fingerprint=matter_fp,
                client_party_id=party,
                subject_identity_fingerprint=subject,
                representative_principal_id=representative,
                evaluated_at=at,
                authorities=history,
            )
        except ValueError as error:
            _fail("L9C11_P21A_COMPOSER_PROJECTION_FAILED", error)


def compose_currentness(
    *,
    tenant_id: str,
    case_matter_id: str,
    matter_fingerprint: str,
    client_party_id: str,
    subject_identity_fingerprint: str,
    representative_principal_id: str,
    evaluated_at: datetime,
    session: Any,
    authority_collection: Any,
) -> LegalClientMatterRepresentationAuthorityCurrentness:
    """Functional boundary equivalent to the explicit composer class."""
    composer = LegalClientMatterRepresentationAuthorityCurrentnessComposer(
        authority_collection=authority_collection,
    )
    return composer.compose_currentness(
        tenant_id,
        case_matter_id,
        matter_fingerprint,
        client_party_id,
        subject_identity_fingerprint,
        representative_principal_id,
        evaluated_at,
        session,
    )


__all__ = [
    "VERSION",
    "LegalClientMatterRepresentationAuthorityCurrentnessComposer",
    "LegalClientMatterRepresentationAuthorityCurrentnessComposerError",
    "compose_currentness",
]


# ARTIFACT: legal_client_matter_representation_authority_currentness_composer.py
# VERSION: v1.0.0-L9C11-P21A-CLIENT-REPRESENTATION-AUTHORITY-CURRENTNESS-COMPOSER
# AUTHORITY BOUNDARY: one bounded P7 history read plus pure P21A delegation
# TENANT POSTURE: exact tenant/matter/fingerprint/client/subject/representative propagation
# FAIL-CLOSED POSTURE: active transaction and registry/projection failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
