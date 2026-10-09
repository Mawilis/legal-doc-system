"""WILSY OS authoritative legal conflict-screening orchestration.

TITLE: Legal Conflict Screening Orchestrator
VERSION: v1.0.0-L8-8F-LEGAL-CONFLICT-SCREENING-ORCHESTRATOR
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Compose exact L8-8B source-party and same-subject occurrence evidence
         into one L8-8D screening result and persist it immutably through L8-8E
         under one already-active caller-owned Mongo transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_conflict_screening_orchestrator.py
COLLABORATION / OWNERSHIP: L8-8A owns matter-party semantics; L8-8B owns party
                            persistence and exact subject lookup; L8-8D owns
                            screening semantics; L8-8E owns screening
                            persistence. L8-8F owns composition only. Later IAM,
                            HTTP and human-review domains remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-L8-8F-LEGAL-CONFLICT-SCREENING-ORCHESTRATOR establishes
           source-party lookup by exact tenant/party identity, server-derived
           subject fingerprint, exact same-subject occurrence lookup, mandatory
           exact source occurrence correlation, deterministic L8-8D screening,
           immutable L8-8E persistence, replay, chronology enforcement and
           governed whole-transaction retry propagation. Callers cannot provide
           subject fingerprints, occurrence lists, status, matches, match kind,
           clearance, waiver or resolution authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Caller inputs contain opaque tenant/party/screening
                             identities plus bounded evidence references only.
                             Subject fingerprint and match topology are derived
                             from certified durable party evidence.
TENANT BOUNDARY: Source party and every occurrence are read from L8-8B under
                 exact tenant scope and the same caller transaction.
AUTHORITY BOUNDARY: Screening composition only. NO_MATCH_FOUND is not legal
                    clearance and REVIEW_REQUIRED is not a conflict finding,
                    recusal, waiver, ethical wall, client acceptance,
                    representation authorization or legal advice.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                               execution and settlement authority.
TRANSACTION BOUNDARY: Requires one already-active caller-owned Mongo transaction
                      before any read/write. L8-8F never starts, commits, aborts,
                      retries or closes Mongo sessions/transactions.
FAIL-CLOSED DECLARATION: Missing/divergent/corrupt source party, incomplete or
                         mismatched occurrence lookup, invalid chronology,
                         screening divergence, persistence conflict/outage and
                         governed transaction races reject.
"""
from __future__ import annotations

from datetime import datetime
import re
from typing import Any, Final, NoReturn

from tools.eos.legal_operations.domain.legal_conflict_screening import (
    LegalConflictScreeningError,
    LegalConflictScreeningResult,
    build_legal_conflict_screening,
)
from tools.eos.legal_operations.domain.legal_matter_party import LegalMatterParty
from tools.eos.legal_operations.registry.legal_conflict_screening_registry import (
    LegalConflictScreeningRegistryConflictError,
    LegalConflictScreeningRegistryError,
    LegalConflictScreeningRegistryRetryRequiredError,
    persist_screening,
)
from tools.eos.legal_operations.registry.legal_matter_party_registry import (
    LegalMatterPartyRegistryError,
    LegalMatterPartyRegistryNotFoundError,
    LegalMatterPartyRegistryRetryRequiredError,
    find_subject_occurrences,
    get_party,
)


VERSION: Final[str] = "v1.0.0-L8-8F-LEGAL-CONFLICT-SCREENING-ORCHESTRATOR"
_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_SHA3: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class LegalConflictScreeningOrchestratorError(RuntimeError):
    """Base fail-closed L8-8F composition error with stable code."""

    default_code = "L8_8F_ORCHESTRATION_ERROR"

    def __init__(self, code: str | None = None) -> None:
        self.code = code or self.default_code
        super().__init__(self.code)


class LegalConflictScreeningOrchestratorInputError(
    LegalConflictScreeningOrchestratorError
):
    default_code = "L8_8F_INPUT_INVALID"


class LegalConflictScreeningOrchestratorTransactionRequiredError(
    LegalConflictScreeningOrchestratorError
):
    default_code = "L8_8F_ACTIVE_TRANSACTION_REQUIRED"


class LegalConflictScreeningOrchestratorSourcePartyNotFoundError(
    LegalConflictScreeningOrchestratorError
):
    default_code = "L8_8F_SOURCE_PARTY_NOT_FOUND"


class LegalConflictScreeningOrchestratorConflictError(
    LegalConflictScreeningOrchestratorError
):
    default_code = "L8_8F_SCREENING_CONFLICT"


class LegalConflictScreeningOrchestratorRetryRequiredError(
    LegalConflictScreeningOrchestratorError
):
    default_code = "L8_8F_WHOLE_TRANSACTION_RETRY_REQUIRED"


class LegalConflictScreeningOrchestratorAuthorityUnavailableError(
    LegalConflictScreeningOrchestratorError
):
    default_code = "L8_8F_AUTHORITY_UNAVAILABLE"


def _raise(
    error_type: type[LegalConflictScreeningOrchestratorError],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _active_transaction(session: Any) -> Any:
    if session is None:
        _raise(LegalConflictScreeningOrchestratorTransactionRequiredError)
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError) as error:
        _raise(
            LegalConflictScreeningOrchestratorTransactionRequiredError,
            cause=error,
        )
    if active is not True:
        _raise(LegalConflictScreeningOrchestratorTransactionRequiredError)
    return session


def _identity(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _raise(
            LegalConflictScreeningOrchestratorInputError,
            f"L8_8F_{name.upper()}_INVALID",
        )
    return value


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _raise(
            LegalConflictScreeningOrchestratorInputError,
            "L8_8F_TENANT_REQUIRED",
        )
    return tenant


def _evidence_reference(value: object) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > 512
        or any(ord(character) < 32 for character in value)
    ):
        _raise(
            LegalConflictScreeningOrchestratorInputError,
            "L8_8F_SOURCE_EVIDENCE_REFERENCE_INVALID",
        )
    return value


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _raise(
            LegalConflictScreeningOrchestratorInputError,
            f"L8_8F_{name.upper()}_INVALID",
        )
    return value


def run_legal_conflict_screening(
    *,
    tenant_id: str,
    source_party_id: str,
    screening_id: str,
    screened_at: datetime,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
    party_collection: Any,
    screening_collection: Any,
    session: Any,
) -> LegalConflictScreeningResult:
    """Compose and persist one exact-subject screening from durable party truth.

    The public API intentionally exposes no subject fingerprint, occurrence
    list, status, match kind, match list, conflict flag, clearance, waiver,
    resolution or representation authority. Those values are either derived
    from L8-8B/L8-8D or do not belong to screening authority at all.
    """
    tx = _active_transaction(session)
    tenant = _tenant(tenant_id)
    party_id = _identity("source_party_id", source_party_id)
    screening_identity = _identity("screening_id", screening_id)
    evidence_reference = _evidence_reference(source_evidence_reference)
    evidence_fingerprint = _fingerprint(
        "source_evidence_fingerprint",
        source_evidence_fingerprint,
    )
    if (
        not isinstance(screened_at, datetime)
        or screened_at.tzinfo is None
        or screened_at.utcoffset() is None
    ):
        _raise(
            LegalConflictScreeningOrchestratorInputError,
            "L8_8F_SCREENED_AT_INVALID",
        )

    try:
        source = get_party(
            tenant,
            party_id,
            party_collection,
            session=tx,
        )
    except LegalMatterPartyRegistryNotFoundError as error:
        _raise(
            LegalConflictScreeningOrchestratorSourcePartyNotFoundError,
            cause=error,
        )
    except LegalMatterPartyRegistryRetryRequiredError as error:
        _raise(
            LegalConflictScreeningOrchestratorRetryRequiredError,
            cause=error,
        )
    except LegalMatterPartyRegistryError as error:
        _raise(
            LegalConflictScreeningOrchestratorAuthorityUnavailableError,
            "L8_8F_SOURCE_PARTY_AUTHORITY_UNAVAILABLE",
            error,
        )

    if type(source) is not LegalMatterParty:
        _raise(
            LegalConflictScreeningOrchestratorAuthorityUnavailableError,
            "L8_8F_SOURCE_PARTY_TYPE_INVALID",
        )
    if source.tenant_id != tenant or source.party_id != party_id:
        _raise(
            LegalConflictScreeningOrchestratorAuthorityUnavailableError,
            "L8_8F_SOURCE_PARTY_SCOPE_INVALID",
        )
    if screened_at < source.registered_at:
        _raise(
            LegalConflictScreeningOrchestratorInputError,
            "L8_8F_SCREENED_AT_INVALID",
        )

    try:
        occurrences = find_subject_occurrences(
            tenant,
            source.subject_identity_fingerprint,
            party_collection,
            session=tx,
        )
    except LegalMatterPartyRegistryRetryRequiredError as error:
        _raise(
            LegalConflictScreeningOrchestratorRetryRequiredError,
            cause=error,
        )
    except LegalMatterPartyRegistryError as error:
        _raise(
            LegalConflictScreeningOrchestratorAuthorityUnavailableError,
            "L8_8F_SUBJECT_OCCURRENCE_AUTHORITY_UNAVAILABLE",
            error,
        )

    exact_source = tuple(
        occurrence
        for occurrence in occurrences
        if occurrence.party_id == source.party_id
    )
    if len(exact_source) != 1 or exact_source[0].to_dict() != source.to_dict():
        _raise(
            LegalConflictScreeningOrchestratorAuthorityUnavailableError,
            "L8_8F_SOURCE_OCCURRENCE_CORRELATION_INVALID",
        )

    try:
        screening = build_legal_conflict_screening(
            source_party=source,
            occurrences=occurrences,
            screening_id=screening_identity,
            screened_at=screened_at,
            source_evidence_reference=evidence_reference,
            source_evidence_fingerprint=evidence_fingerprint,
        )
    except LegalConflictScreeningError as error:
        _raise(
            LegalConflictScreeningOrchestratorAuthorityUnavailableError,
            "L8_8F_SCREENING_COMPOSITION_INVALID",
            error,
        )

    try:
        return persist_screening(
            screening,
            screening_collection,
            session=tx,
        )
    except LegalConflictScreeningRegistryRetryRequiredError as error:
        _raise(
            LegalConflictScreeningOrchestratorRetryRequiredError,
            cause=error,
        )
    except LegalConflictScreeningRegistryConflictError as error:
        _raise(
            LegalConflictScreeningOrchestratorConflictError,
            getattr(error, "code", None) or None,
            error,
        )
    except LegalConflictScreeningRegistryError as error:
        _raise(
            LegalConflictScreeningOrchestratorAuthorityUnavailableError,
            "L8_8F_SCREENING_PERSISTENCE_UNAVAILABLE",
            error,
        )


__all__ = [
    "VERSION",
    "LegalConflictScreeningOrchestratorAuthorityUnavailableError",
    "LegalConflictScreeningOrchestratorConflictError",
    "LegalConflictScreeningOrchestratorError",
    "LegalConflictScreeningOrchestratorInputError",
    "LegalConflictScreeningOrchestratorRetryRequiredError",
    "LegalConflictScreeningOrchestratorSourcePartyNotFoundError",
    "LegalConflictScreeningOrchestratorTransactionRequiredError",
    "run_legal_conflict_screening",
]


# ARTIFACT: legal_conflict_screening_orchestrator.py
# VERSION: v1.0.0-L8-8F-LEGAL-CONFLICT-SCREENING-ORCHESTRATOR
# AUTHORITY BOUNDARY: exact durable party lookup -> screening composition -> immutable persistence only
# TENANT POSTURE: source and occurrences are registry-derived under one exact tenant transaction
# FAIL-CLOSED POSTURE: missing/divergent/corrupt/incomplete/conflicting/raced evidence rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
