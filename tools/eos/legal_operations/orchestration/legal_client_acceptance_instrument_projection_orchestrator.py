"""WILSY OS actionable Legal Client acceptance-instrument projection.

TITLE: Legal Client Acceptance Instrument Projection Orchestrator
VERSION: v1.0.0-L9A4-P2E-CLIENT-ACCEPTANCE-INSTRUMENT-PROJECTION
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Revalidate current LEGAL_CLIENT IAM, ACTIVE matter visibility, OPEN
         CaseMatter, exact acting capacity, latest effective instrument chain,
         ACTIVE lifecycle and current APPROVED decision before projecting only
         bounded client-review metadata required to begin acceptance context.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_acceptance_instrument_projection_orchestrator.py
COLLABORATION / OWNERSHIP: Existing IAM, visibility, CaseMatter, party,
                            acting-capacity, instrument, lifecycle and approval
                            authorities remain canonical. This module only
                            composes their current read truth.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.0.0-L9A4-P2E-CLIENT-ACCEPTANCE-INSTRUMENT-PROJECTION
           establishes the bounded server-owned actionable instrument
           projection required for Legal Client browser parity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Emits no content bytes, client PII, approval
                             evidence references, acting-capacity evidence,
                             authorization evidence or financial truth.
TENANT BOUNDARY: Tenant/principal derive only from active SovereignIdentity;
                 every registry read is exact-tenant and exact-matter scoped.
AUTHORITY BOUNDARY: Read-only presentation composition. Projection does not
                    create approval, context, acceptance, engagement,
                    representation, Court, AI, billing, payment or execution.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller owns one already-active transaction. This module
                      never starts, commits, aborts or retries transactions.
FAIL-CLOSED DECLARATION: Missing IAM, visibility, OPEN matter, unique valid
                         capacity, registry integrity, lifecycle or approval
                         evidence rejects rather than inferring authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Final, NoReturn

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_approval import (
    LegalClientMatterAcceptanceInstrumentApprovalDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_lifecycle import (
    LegalClientMatterAcceptanceInstrumentLifecycleStatus,
)
from tools.eos.legal_operations.domain.legal_operations_current_projection import (
    resolve_current_lifecycle_snapshot,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter, CaseMatterState
from tools.eos.legal_operations.registry import (
    legal_client_acting_capacity_registry as capacity_registry,
    legal_client_matter_acceptance_instrument_approval_registry as approval_registry,
    legal_client_matter_acceptance_instrument_lifecycle_registry as lifecycle_registry,
    legal_client_matter_acceptance_instrument_registry as instrument_registry,
    legal_client_matter_visibility_registry as visibility_registry,
    legal_matter_party_registry as party_registry,
    legal_operations_lifecycle_registry as matter_registry,
)

VERSION: Final[str] = "v1.0.0-L9A4-P2E-CLIENT-ACCEPTANCE-INSTRUMENT-PROJECTION"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-ACCEPTANCE-INSTRUMENT-PROJECTION/V1"
VISIBILITY: Final[str] = "LEGAL_CLIENT_ACTIONABLE_ACCEPTANCE_INSTRUMENTS"
PERMISSION: Final[str] = "legal_operations:client_matter:read"
OPERATION: Final[str] = "legal_client_matter_read"
UTC = timezone.utc
Clock = Callable[[], datetime]


class LegalClientAcceptanceInstrumentProjectionError(RuntimeError):
    """Stable fail-closed projection failure containing no supplied-value payload."""

    def __init__(self, code: str) -> None:
        """Expose only one bounded semantic error code."""
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class LegalClientAcceptanceInstrumentProjectionRow:
    """One immutable client-reviewable instrument row with no authorizing effect."""

    instrument_id: str
    version: str
    instrument_kind: str
    title: str
    review_scope: str
    effective_from: datetime
    instrument_fingerprint: str
    content_fingerprint: str

    def to_dict(self) -> dict[str, object]:
        """Return the bounded HTTP-safe row projection."""
        return {
            "instrument_id": self.instrument_id,
            "version": self.version,
            "instrument_kind": self.instrument_kind,
            "title": self.title,
            "review_scope": self.review_scope,
            "effective_from": self.effective_from.isoformat(),
            "instrument_fingerprint": self.instrument_fingerprint,
            "content_fingerprint": self.content_fingerprint,
        }


@dataclass(frozen=True, slots=True)
class LegalClientAcceptanceInstrumentProjection:
    """Immutable server-owned actionable-instrument projection for one matter."""

    tenant_id: str
    case_matter_id: str
    instruments: tuple[LegalClientAcceptanceInstrumentProjectionRow, ...]
    schema: str = SCHEMA
    version: str = VERSION
    visibility: str = VISIBILITY

    def to_dict(self) -> dict[str, object]:
        """Return an exact immutable projection payload for HTTP transport."""
        return {
            "schema": self.schema,
            "version": self.version,
            "tenant_id": self.tenant_id,
            "case_matter_id": self.case_matter_id,
            "visibility": self.visibility,
            "instruments": [row.to_dict() for row in self.instruments],
        }


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalClientAcceptanceInstrumentProjectionError(code)
    if cause is None:
        raise error
    raise error from cause


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"L9A4_P2E_{name.upper()}_INVALID")
    return value


def _active_transaction(session: Any) -> Any:
    if session is None:
        _fail("L9A4_P2E_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _fail("L9A4_P2E_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _identity(identity: SovereignIdentity) -> tuple[str, str]:
    if not isinstance(identity, SovereignIdentity):
        _fail("L9A4_P2E_IDENTITY_REQUIRED")
    if identity.status is not PrincipalStatus.ACTIVE:
        _fail("L9A4_P2E_PRINCIPAL_INACTIVE")
    return _text("tenant_id", identity.tenant_id), _text("principal_id", identity.identity_id)


def _instant(clock: Clock | None) -> datetime:
    value = datetime.now(UTC) if clock is None else clock()
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail("L9A4_P2E_SERVER_CLOCK_INVALID")
    return value.astimezone(UTC)


def _authorize_client(
    *,
    tenant_id: str,
    principal_id: str,
    principal_repository: Any,
    membership_repository: Any,
    business_role_repository: Any,
    role_assignment_repository: Any,
    session: Any,
) -> None:
    try:
        decision = authorize_tenant_operation(
            principal_id=principal_id,
            tenant_id=tenant_id,
            permission_id=PERMISSION,
            operation=OPERATION,
            principal_repository=principal_repository,
            membership_repository=membership_repository,
            business_role_repository=business_role_repository,
            role_assignment_repository=role_assignment_repository,
            session=session,
        )
    except Exception as error:
        _fail("L9A4_P2E_CLIENT_AUTHORIZATION_UNAVAILABLE", error)
    if (
        decision.authorized is not True
        or decision.reason is not TenantAuthorizationReason.AUTHORIZED
        or decision.business_role != "tenant_legal_client"
        or decision.authorization_role != "LEGAL_CLIENT"
    ):
        _fail("L9A4_P2E_LEGAL_CLIENT_AUTHORIZATION_REQUIRED")


def _current_matter(
    *, tenant_id: str, case_matter_id: str, collection: Any, session: Any
) -> CaseMatter:
    try:
        history = matter_registry.LegalOperationsLifecycleRegistry.get_entity_history(
            tenant_id, "CaseMatter", case_matter_id, collection, session=session
        )
        value = resolve_current_lifecycle_snapshot(history, expected_type=CaseMatter)
    except Exception as error:
        _fail("L9A4_P2E_CASE_MATTER_UNAVAILABLE", error)
    if type(value) is not CaseMatter:
        _fail("L9A4_P2E_CASE_MATTER_TYPE_INVALID")
    if value.tenant_id != tenant_id or value.case_matter_id != case_matter_id:
        _fail("L9A4_P2E_CASE_MATTER_SCOPE_MISMATCH")
    if value.state is not CaseMatterState.OPEN:
        _fail("L9A4_P2E_CASE_MATTER_NOT_OPEN")
    return value


def _require_visibility(
    *,
    tenant_id: str,
    principal_id: str,
    case_matter_id: str,
    collection: Any,
    session: Any,
) -> None:
    try:
        value = visibility_registry.LegalClientMatterVisibilityRegistry.resolve_current_active(
            tenant_id, principal_id, case_matter_id, collection, session=session
        )
    except Exception as error:
        _fail("L9A4_P2E_ACTIVE_VISIBILITY_REQUIRED", error)
    if (
        value.tenant_id != tenant_id
        or value.client_principal_id != principal_id
        or value.case_matter_id != case_matter_id
    ):
        _fail("L9A4_P2E_VISIBILITY_SCOPE_MISMATCH")


def _require_unique_capacity(
    *,
    tenant_id: str,
    principal_id: str,
    matter: CaseMatter,
    at: datetime,
    party_collection: Any,
    capacity_collection: Any,
    session: Any,
) -> None:
    try:
        parties = party_registry.list_matter_parties(
            tenant_id, matter.case_matter_id, party_collection, session=session
        )
        capacities = capacity_registry.list_valid_capacities_at(
            tenant_id, matter.case_matter_id, at, capacity_collection, session=session
        )
    except Exception as error:
        _fail("L9A4_P2E_PARTY_OR_CAPACITY_UNAVAILABLE", error)
    by_party = {party.party_id: party for party in parties}
    matches = [
        capacity
        for capacity in capacities
        if capacity.principal_id == principal_id
        and capacity.party_id in by_party
        and by_party[capacity.party_id].subject_reference == capacity.subject_reference
        and by_party[capacity.party_id].subject_identity_fingerprint
        == capacity.subject_identity_fingerprint
        and by_party[capacity.party_id].tenant_id == tenant_id
        and by_party[capacity.party_id].case_matter_id == matter.case_matter_id
        and by_party[capacity.party_id].matter_fingerprint == matter.fingerprint
    ]
    if len(matches) != 1:
        _fail(
            "L9A4_P2E_PARTY_CAPACITY_NOT_FOUND"
            if not matches
            else "L9A4_P2E_PARTY_CAPACITY_AMBIGUOUS"
        )


def project_legal_client_acceptance_instruments(
    *,
    identity: SovereignIdentity,
    case_matter_id: str,
    matter_lifecycle_collection: Any,
    visibility_collection: Any,
    party_collection: Any,
    capacity_collection: Any,
    instrument_collection: Any,
    instrument_lifecycle_collection: Any,
    approval_collection: Any,
    principal_repository: Any,
    membership_repository: Any,
    business_role_repository: Any,
    role_assignment_repository: Any,
    session: Any,
    clock: Clock | None = None,
) -> LegalClientAcceptanceInstrumentProjection:
    """Project actionable review instruments from current canonical authorities.

    The caller owns the active transaction. The function performs no write,
    context issuance, acceptance issuance or financial action. Empty instruments
    is a valid result when the authenticated visible client has no currently
    ACTIVE and APPROVED instrument chain for the matter.
    """
    tx = _active_transaction(session)
    tenant_id, principal_id = _identity(identity)
    matter_id = _text("case_matter_id", case_matter_id)
    if any(
        value is None
        for value in (
            matter_lifecycle_collection,
            visibility_collection,
            party_collection,
            capacity_collection,
            instrument_collection,
            instrument_lifecycle_collection,
            approval_collection,
            principal_repository,
            membership_repository,
            business_role_repository,
            role_assignment_repository,
        )
    ):
        _fail("L9A4_P2E_DEPENDENCY_REQUIRED")
    at = _instant(clock)
    _authorize_client(
        tenant_id=tenant_id,
        principal_id=principal_id,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        business_role_repository=business_role_repository,
        role_assignment_repository=role_assignment_repository,
        session=tx,
    )
    _require_visibility(
        tenant_id=tenant_id,
        principal_id=principal_id,
        case_matter_id=matter_id,
        collection=visibility_collection,
        session=tx,
    )
    matter = _current_matter(
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        collection=matter_lifecycle_collection,
        session=tx,
    )
    _require_unique_capacity(
        tenant_id=tenant_id,
        principal_id=principal_id,
        matter=matter,
        at=at,
        party_collection=party_collection,
        capacity_collection=capacity_collection,
        session=tx,
    )
    try:
        persisted = instrument_registry.list_matter_instruments(
            tenant_id, matter_id, instrument_collection, session=tx
        )
    except Exception as error:
        _fail("L9A4_P2E_INSTRUMENT_REGISTRY_UNAVAILABLE", error)

    rows: list[LegalClientAcceptanceInstrumentProjectionRow] = []
    for instrument_id in sorted({value.instrument_id for value in persisted}):
        try:
            instrument = instrument_registry.get_latest_effective_version(
                tenant_id, matter_id, instrument_id, at, instrument_collection, session=tx
            )
        except Exception as error:
            _fail("L9A4_P2E_INSTRUMENT_CURRENTNESS_UNAVAILABLE", error)
        if instrument is None:
            continue
        try:
            lifecycle = lifecycle_registry.get_current_lifecycle(
                tenant_id,
                matter_id,
                instrument.instrument_id,
                instrument.version,
                instrument_lifecycle_collection,
                session=tx,
            )
        except Exception as error:
            _fail("L9A4_P2E_LIFECYCLE_UNAVAILABLE", error)
        if (
            lifecycle is None
            or lifecycle.status
            is not LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE
            or lifecycle.instrument_fingerprint != instrument.fingerprint
        ):
            continue
        try:
            approval = approval_registry.get_current_approval(
                tenant_id,
                matter_id,
                instrument.instrument_id,
                instrument.version,
                instrument.fingerprint,
                instrument.content_fingerprint,
                approval_collection,
                at=at,
                session=tx,
            )
        except Exception as error:
            _fail("L9A4_P2E_APPROVAL_UNAVAILABLE", error)
        if (
            approval is None
            or approval.decision
            is not LegalClientMatterAcceptanceInstrumentApprovalDecision.APPROVED
        ):
            continue
        rows.append(
            LegalClientAcceptanceInstrumentProjectionRow(
                instrument_id=instrument.instrument_id,
                version=instrument.version,
                instrument_kind=instrument.instrument_kind,
                title=instrument.title,
                review_scope=instrument.review_scope,
                effective_from=instrument.effective_from,
                instrument_fingerprint=instrument.fingerprint,
                content_fingerprint=instrument.content_fingerprint,
            )
        )

    rows.sort(key=lambda item: (item.effective_from, item.instrument_id, item.version), reverse=True)
    return LegalClientAcceptanceInstrumentProjection(
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        instruments=tuple(rows),
    )


__all__ = [
    "OPERATION",
    "PERMISSION",
    "SCHEMA",
    "VERSION",
    "VISIBILITY",
    "LegalClientAcceptanceInstrumentProjection",
    "LegalClientAcceptanceInstrumentProjectionError",
    "LegalClientAcceptanceInstrumentProjectionRow",
    "project_legal_client_acceptance_instruments",
]

# ARTIFACT: legal_client_acceptance_instrument_projection_orchestrator.py
# VERSION: v1.0.0-L9A4-P2E-CLIENT-ACCEPTANCE-INSTRUMENT-PROJECTION
# AUTHORITY BOUNDARY: read-only composition of client-actionable review metadata
# TENANT POSTURE: authenticated identity + exact ACTIVE visibility + exact matter scope
# FAIL-CLOSED POSTURE: IAM/visibility/matter/capacity/registry/currentness failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
