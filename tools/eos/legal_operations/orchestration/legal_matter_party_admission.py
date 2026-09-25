"""WILSY OS legal matter-party admission orchestration.

TITLE: Legal Matter Party Admission Orchestrator
VERSION: v1.0.0-L8-8C-LEGAL-MATTER-PARTY-ADMISSION
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Admit one immutable legal matter-party fact only after re-reading the
         complete durable P1 CaseMatter history, resolving one deterministic
         current OPEN matter, constructing L8-8A evidence from that exact
         snapshot, and persisting through L8-8B in one caller transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_matter_party_admission.py
COLLABORATION / OWNERSHIP: P1 owns CaseMatter lifecycle semantics; P2 owns
                            immutable lifecycle persistence; L8-0 owns current
                            projection; L8-8A owns party evidence semantics;
                            L8-8B owns party persistence. L8-8C owns only their
                            fail-closed admission composition. The caller owns
                            Mongo session/transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-L8-8C-LEGAL-MATTER-PARTY-ADMISSION establishes exact durable
           matter revalidation before party admission. The caller supplies only
           tenant/matter identity plus bounded party/source evidence; current
           matter fingerprint/state are server-derived from complete P2 history.
           Closed, missing, ambiguous, corrupt, stale, foreign or persistence-
           unavailable matter authority cannot create party truth. Governed
           whole-transaction retry signals are preserved.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No ID/passport/tax/account number, address, phone,
                             email, biometric or raw KYC material is introduced.
                             Subject identity remains an opaque authority
                             reference plus lowercase SHA3-512 evidence.
TENANT BOUNDARY: Durable CaseMatter history is queried by exact tenant/type/id;
                 resolved matter tenant/id must match inputs before L8-8A/B.
AUTHORITY BOUNDARY: Admission composition only. It does not create CaseMatter
                    lifecycle, subject identity, conflict findings, client
                    acceptance, representation, billing, payment or legal
                    outcome authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                               execution and settlement authority.
TRANSACTION BOUNDARY: Requires one already-active caller-owned Mongo transaction
                      before any durable read/write. L8-8C never starts, commits,
                      aborts, retries or closes a Mongo session/transaction.
FAIL-CLOSED DECLARATION: Missing/closed/forked/corrupt matter history, scope
                         mismatch, invalid chronology, party conflict,
                         persistence outage and governed transaction races reject.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterParty,
    LegalMatterPartyError,
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_current_projection import (
    LegalOperationsCurrentProjectionError,
    resolve_current_lifecycle_snapshot,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.registry.legal_matter_party_registry import (
    LegalMatterPartyRegistryConflictError,
    LegalMatterPartyRegistryError,
    LegalMatterPartyRegistryRetryRequiredError,
    persist_party,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
    LegalOperationsLifecycleRegistryError,
)


VERSION: Final[str] = "v1.0.0-L8-8C-LEGAL-MATTER-PARTY-ADMISSION"
_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class LegalMatterPartyAdmissionError(RuntimeError):
    """Base fail-closed L8-8C admission error with stable code."""

    default_code = "L8_8C_ADMISSION_ERROR"

    def __init__(self, code: str | None = None) -> None:
        self.code = code or self.default_code
        super().__init__(self.code)


class LegalMatterPartyAdmissionInputError(LegalMatterPartyAdmissionError):
    """Caller supplied malformed bounded admission evidence."""

    default_code = "L8_8C_INPUT_INVALID"


class LegalMatterPartyAdmissionTransactionRequiredError(
    LegalMatterPartyAdmissionError
):
    """Caller did not provide one already-active Mongo transaction."""

    default_code = "L8_8C_ACTIVE_TRANSACTION_REQUIRED"


class LegalMatterPartyAdmissionMatterNotFoundError(
    LegalMatterPartyAdmissionError
):
    """No CaseMatter exists for the exact tenant/matter scope."""

    default_code = "L8_8C_CASE_MATTER_NOT_FOUND"


class LegalMatterPartyAdmissionMatterNotOpenError(
    LegalMatterPartyAdmissionError
):
    """The deterministic current CaseMatter is not OPEN."""

    default_code = "L8_8C_CASE_MATTER_NOT_OPEN"


class LegalMatterPartyAdmissionConflictError(
    LegalMatterPartyAdmissionError
):
    """An immutable party identity or matter-subject identity conflicts."""

    default_code = "L8_8C_PARTY_CONFLICT"


class LegalMatterPartyAdmissionRetryRequiredError(
    LegalMatterPartyAdmissionError
):
    """Caller must abort and restart the complete admission transaction."""

    default_code = "L8_8C_WHOLE_TRANSACTION_RETRY_REQUIRED"


class LegalMatterPartyAdmissionAuthorityUnavailableError(
    LegalMatterPartyAdmissionError
):
    """Durable matter/party authority could not be safely established."""

    default_code = "L8_8C_AUTHORITY_UNAVAILABLE"


@dataclass(frozen=True, slots=True)
class LegalMatterPartyAdmissionResult:
    """Exact current matter plus the admitted immutable L8-8A party fact.

    This result is descriptive evidence only. It creates no conflict finding,
    representation mandate, client acceptance, billing, payment, execution or
    settlement authority.
    """

    matter: CaseMatter
    party: LegalMatterParty

    def __post_init__(self) -> None:
        if type(self.matter) is not CaseMatter:
            _raise(
                LegalMatterPartyAdmissionAuthorityUnavailableError,
                "L8_8C_RESULT_MATTER_INVALID",
            )
        if type(self.party) is not LegalMatterParty:
            _raise(
                LegalMatterPartyAdmissionAuthorityUnavailableError,
                "L8_8C_RESULT_PARTY_INVALID",
            )
        if (
            self.matter.state is not CaseMatterState.OPEN
            or self.party.tenant_id != self.matter.tenant_id
            or self.party.case_matter_id != self.matter.case_matter_id
            or self.party.matter_fingerprint != self.matter.fingerprint
        ):
            _raise(
                LegalMatterPartyAdmissionAuthorityUnavailableError,
                "L8_8C_RESULT_CORRELATION_INVALID",
            )

    def to_dict(self) -> dict[str, object]:
        """Serialize exact current matter and immutable admitted party evidence."""
        return {
            "matter": self.matter.to_dict(),
            "party": self.party.to_dict(),
        }


def _raise(
    error_type: type[LegalMatterPartyAdmissionError],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one stable L8-8C error while retaining its technical cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _active_transaction(session: Any) -> Any:
    """Require one already-active caller transaction before any durable read."""
    if session is None:
        _raise(LegalMatterPartyAdmissionTransactionRequiredError)
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError) as error:
        _raise(
            LegalMatterPartyAdmissionTransactionRequiredError,
            cause=error,
        )
    if active is not True:
        _raise(LegalMatterPartyAdmissionTransactionRequiredError)
    return session


def _identity(name: str, value: object) -> str:
    """Require one bounded opaque identifier without inventing defaults."""
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _raise(
            LegalMatterPartyAdmissionInputError,
            f"L8_8C_{name.upper()}_INVALID",
        )
    return value


def _tenant(value: object) -> str:
    """Require an explicit non-global tenant identity."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _raise(
            LegalMatterPartyAdmissionInputError,
            "L8_8C_TENANT_REQUIRED",
        )
    return tenant


def _current_case_matter(
    *,
    tenant_id: str,
    case_matter_id: str,
    lifecycle_collection: Any,
    session: Any,
) -> CaseMatter:
    """Read complete P2 history and resolve one exact current CaseMatter."""
    try:
        history = LegalOperationsLifecycleRegistry.get_entity_history(
            tenant_id,
            "CaseMatter",
            case_matter_id,
            lifecycle_collection,
            session=session,
        )
    except LegalOperationsLifecycleRegistryError as error:
        if getattr(error, "code", None) == "M2_RETRY_TRANSACTION_REQUIRED":
            _raise(
                LegalMatterPartyAdmissionRetryRequiredError,
                cause=error,
            )
        _raise(
            LegalMatterPartyAdmissionAuthorityUnavailableError,
            "L8_8C_CASE_MATTER_PERSISTENCE_UNAVAILABLE",
            error,
        )

    if not history:
        _raise(LegalMatterPartyAdmissionMatterNotFoundError)

    try:
        current = resolve_current_lifecycle_snapshot(
            history,
            expected_type=CaseMatter,
        )
    except LegalOperationsCurrentProjectionError as error:
        _raise(
            LegalMatterPartyAdmissionAuthorityUnavailableError,
            "L8_8C_CASE_MATTER_CURRENTNESS_INVALID",
            error,
        )

    if type(current) is not CaseMatter:
        _raise(
            LegalMatterPartyAdmissionAuthorityUnavailableError,
            "L8_8C_CASE_MATTER_TYPE_INVALID",
        )
    matter = cast(CaseMatter, current)
    if (
        matter.tenant_id != tenant_id
        or matter.case_matter_id != case_matter_id
    ):
        _raise(
            LegalMatterPartyAdmissionAuthorityUnavailableError,
            "L8_8C_CASE_MATTER_SCOPE_INVALID",
        )
    if matter.state is not CaseMatterState.OPEN:
        _raise(LegalMatterPartyAdmissionMatterNotOpenError)
    return matter


def admit_legal_matter_party(
    *,
    tenant_id: str,
    case_matter_id: str,
    party_id: str,
    party_kind: LegalMatterPartyKind | str,
    party_side: LegalMatterPartySide | str,
    matter_role: LegalMatterPartyRole | str,
    subject_reference: str,
    subject_identity_fingerprint: str,
    display_name: str,
    registered_at: datetime,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
    lifecycle_collection: Any,
    party_collection: Any,
    session: Any,
) -> LegalMatterPartyAdmissionResult:
    """Admit one immutable party only against current durable OPEN matter truth.

    The caller owns the already-active transaction. Current matter state and
    fingerprint are never caller inputs: they are re-derived from complete P2
    history through L8-0 under the same transaction. Exact replay is delegated
    to L8-8B; divergent immutable identity fails closed.
    """
    tx = _active_transaction(session)
    tenant = _tenant(tenant_id)
    matter_id = _identity("case_matter_id", case_matter_id)

    matter = _current_case_matter(
        tenant_id=tenant,
        case_matter_id=matter_id,
        lifecycle_collection=lifecycle_collection,
        session=tx,
    )

    if (
        not isinstance(registered_at, datetime)
        or registered_at.tzinfo is None
        or registered_at.utcoffset() is None
        or registered_at < matter.opened_at
    ):
        _raise(
            LegalMatterPartyAdmissionInputError,
            "L8_8C_REGISTERED_AT_INVALID",
        )

    try:
        candidate = register_legal_matter_party(
            matter=matter,
            party_id=party_id,
            party_kind=party_kind,
            party_side=party_side,
            matter_role=matter_role,
            subject_reference=subject_reference,
            subject_identity_fingerprint=subject_identity_fingerprint,
            display_name=display_name,
            registered_at=registered_at,
            source_evidence_reference=source_evidence_reference,
            source_evidence_fingerprint=source_evidence_fingerprint,
        )
    except LegalMatterPartyError as error:
        _raise(
            LegalMatterPartyAdmissionInputError,
            f"L8_8C_PARTY_INPUT_INVALID:{error.code}",
            error,
        )

    try:
        persisted = persist_party(
            candidate,
            party_collection,
            session=tx,
        )
    except LegalMatterPartyRegistryRetryRequiredError as error:
        _raise(
            LegalMatterPartyAdmissionRetryRequiredError,
            cause=error,
        )
    except LegalMatterPartyRegistryConflictError as error:
        _raise(
            LegalMatterPartyAdmissionConflictError,
            getattr(error, "code", None) or None,
            error,
        )
    except LegalMatterPartyRegistryError as error:
        _raise(
            LegalMatterPartyAdmissionAuthorityUnavailableError,
            "L8_8C_PARTY_PERSISTENCE_UNAVAILABLE",
            error,
        )

    return LegalMatterPartyAdmissionResult(
        matter=matter,
        party=persisted,
    )


__all__ = [
    "VERSION",
    "LegalMatterPartyAdmissionAuthorityUnavailableError",
    "LegalMatterPartyAdmissionConflictError",
    "LegalMatterPartyAdmissionError",
    "LegalMatterPartyAdmissionInputError",
    "LegalMatterPartyAdmissionMatterNotFoundError",
    "LegalMatterPartyAdmissionMatterNotOpenError",
    "LegalMatterPartyAdmissionResult",
    "LegalMatterPartyAdmissionRetryRequiredError",
    "LegalMatterPartyAdmissionTransactionRequiredError",
    "admit_legal_matter_party",
]


# ARTIFACT: legal_matter_party_admission.py
# VERSION: v1.0.0-L8-8C-LEGAL-MATTER-PARTY-ADMISSION
# AUTHORITY BOUNDARY: durable-current CaseMatter-to-party admission composition only
# TENANT POSTURE: exact tenant/type/matter history re-read in caller transaction before persistence
# FAIL-CLOSED POSTURE: missing/closed/ambiguous/corrupt/foreign/conflicting/raced evidence rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
