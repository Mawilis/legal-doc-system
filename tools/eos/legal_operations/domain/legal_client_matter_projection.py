"""Bounded current-matter projection for explicitly visible Legal clients.

TITLE: WILSY OS Legal Client Matter Projection
VERSION: v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION
AUTHORITY: Current LEGAL_CLIENT IAM + ACTIVE visibility + canonical current CaseMatter composition.
EPITOME: Under one caller-owned active snapshot transaction, require the exact
         D4 client-matter authorization, resolve only ACTIVE L8-7B visibility
         relations for that authenticated principal, hydrate each exact current
         P1 CaseMatter through L8-5, and emit a deliberately minimal immutable
         dashboard projection containing matter identity/reference/opened time/
         current OPEN-or-CLOSED state only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_projection.py
COLLABORATION / OWNERSHIP: Tenant authorization owns current client IAM; L8-7B
                            owns current visibility; P1/P2/L8-5 own CaseMatter
                            truth/currentness; this module owns only sanitized
                            projection composition. HTTP transport and browser
                            rendering remain later gates.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION establishes
           active-snapshot enforcement, exact D4 authorization, ACTIVE
           principal-specific visibility enumeration, strict current CaseMatter
           resolution, deterministic ordering, whole-projection failure on
           bound-matter corruption/absence, session propagation, and an exact
           client-safe field whitelist. Grant-time source fingerprints remain
           provenance for the visibility relation and do not pin a stale matter
           snapshot; legitimate current P1 transitions are projected.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Emits only explicit matter identifiers/references,
                             current state and opened timestamp. Internal evidence
                             references/fingerprints/history, instruction/document
                             identifiers, deputy/attempt/service/return evidence,
                             billing, payment, AI and settlement data are excluded.
TENANT BOUNDARY: Authorization, visibility and every bound matter resolve inside
                 one explicit tenant and the same caller-owned active transaction.
                 Foreign rows are absence and never become projection data.
AUTHORITY BOUNDARY: Read projection only. IAM authorization does not create
                    visibility; visibility does not create IAM; neither mutates
                    lifecycle/service/return/billing/financial truth.
FINANCIAL AUTHORITY BOUNDARY: No financial fields or execution authority;
                              Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller must supply one already-active transaction/session.
                      This module never starts, commits, aborts or retries it.
FAIL-CLOSED DECLARATION: Inactive transaction, denied/current-IAM failure,
                         visibility corruption/outage, missing/corrupt bound
                         matter, tenant/identity drift or malformed projection
                         rejects the whole result without partial or broad fallback.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any, Final, NoReturn, Protocol, cast

from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.domain.legal_operations_read_model import (
    LegalOperationsReadModelError,
    get_entity_read_model,
)
from tools.eos.legal_operations.registry.legal_client_matter_visibility_registry import (
    LegalClientMatterVisibilityPersistedRecordInvalidError,
    LegalClientMatterVisibilityRegistry,
    LegalClientMatterVisibilityRegistryError,
)


VERSION: Final[str] = "v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-PROJECTION/V1"
PERMISSION: Final[str] = "legal_operations:client_matter:read"
OPERATION: Final[str] = "legal_client_matter_read"
VISIBILITY: Final[str] = "LEGAL_CLIENT_EXPLICIT_MATTERS"
_IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class LegalClientMatterProjectionError(RuntimeError):
    """Stable fail-closed D5 projection-composition failure."""

    def __init__(self, code: str) -> None:
        """Create one bounded projection failure code."""
        self.code = code
        super().__init__(code)


class LegalClientMatterProjectionTransactionRequiredError(
    LegalClientMatterProjectionError
):
    """Caller failed to provide one already-active snapshot transaction."""


class PrincipalReader(Protocol):
    """Read current principal authority without mutation."""

    def resolve(
        self,
        principal_id: str,
        *,
        session: Any = None,
    ) -> object: ...


class MembershipReader(Protocol):
    """Read current principal/tenant membership without mutation."""

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> object: ...


class AssignmentReader(Protocol):
    """Read current business/final role authority without mutation."""

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> object: ...


def _fail(
    code: str,
    cause: BaseException | None = None,
    *,
    error_type: type[LegalClientMatterProjectionError] = (
        LegalClientMatterProjectionError
    ),
) -> NoReturn:
    """Raise one stable projection error while retaining the root cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    """Require one trimmed opaque projection identity."""
    if (
        not isinstance(value, str)
        or _IDENTITY.fullmatch(value) is None
        or value != value.strip()
    ):
        _fail(f"L8_7D5_{name.upper()}_INVALID")
    return cast(str, value)


def _reference(value: object) -> str:
    """Require one bounded client-facing matter reference."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > 512
        or any(ord(character) < 32 for character in value)
    ):
        _fail("L8_7D5_MATTER_REFERENCE_INVALID")
    return cast(str, value)


def _timestamp(value: object) -> datetime:
    """Require one timezone-aware projection timestamp."""
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail("L8_7D5_OPENED_AT_INVALID")
    return value


def _active_transaction(session: object) -> object:
    """Require an already-active caller-owned snapshot transaction."""
    if session is None:
        _fail(
            "L8_7D5_ACTIVE_TRANSACTION_REQUIRED",
            error_type=LegalClientMatterProjectionTransactionRequiredError,
        )
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail(
            "L8_7D5_ACTIVE_TRANSACTION_REQUIRED",
            error,
            error_type=LegalClientMatterProjectionTransactionRequiredError,
        )
    if active is not True:
        _fail(
            "L8_7D5_ACTIVE_TRANSACTION_REQUIRED",
            error_type=LegalClientMatterProjectionTransactionRequiredError,
        )
    return session


@dataclass(frozen=True, slots=True)
class LegalClientMatterProjection:
    """One exact client-safe current CaseMatter projection.

    The value is immutable and contains no lifecycle evidence references,
    transition history, instruction/document/deputy/service/return fields,
    billing/financial state or AI output. Construction validates only the
    projection surface; canonical CaseMatter truth remains owned by P1.
    """

    case_matter_id: str
    matter_reference: str
    opened_at: datetime
    state: CaseMatterState

    def __post_init__(self) -> None:
        """Fail closed on malformed public construction."""
        _identity("case_matter_id", self.case_matter_id)
        _reference(self.matter_reference)
        _timestamp(self.opened_at)
        if not isinstance(self.state, CaseMatterState):
            _fail("L8_7D5_CASE_MATTER_STATE_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Return the exact client-safe wire-neutral field whitelist."""
        return {
            "case_matter_id": self.case_matter_id,
            "matter_reference": self.matter_reference,
            "opened_at": self.opened_at.isoformat(),
            "state": self.state.value,
        }


@dataclass(frozen=True, slots=True)
class LegalClientMatterProjectionSet:
    """Deterministic own-tenant collection of explicitly visible matters.

    The authenticated client principal is intentionally not echoed into the
    serialized payload. The aggregate exposes only tenant scope, projection
    classification and sanitized matter cards. An empty tuple is a valid
    authorized result when no ACTIVE visibility relations exist.
    """

    tenant_id: str
    matters: tuple[LegalClientMatterProjection, ...]

    def __post_init__(self) -> None:
        """Validate exact tenant scope, immutable tuple shape and uniqueness."""
        _identity("tenant_id", self.tenant_id)
        if type(self.matters) is not tuple:
            _fail("L8_7D5_MATTERS_INVALID")
        identities: set[str] = set()
        prior_key: tuple[str, str] | None = None
        for matter in self.matters:
            if type(matter) is not LegalClientMatterProjection:
                _fail("L8_7D5_MATTER_PROJECTION_INVALID")
            if matter.case_matter_id in identities:
                _fail("L8_7D5_DUPLICATE_MATTER_INVALID")
            identities.add(matter.case_matter_id)
            current_key = (matter.case_matter_id, matter.matter_reference)
            if prior_key is not None and current_key < prior_key:
                _fail("L8_7D5_MATTER_ORDER_INVALID")
            prior_key = current_key

    def to_dict(self) -> dict[str, object]:
        """Return the exact dashboard-safe aggregate payload."""
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "tenant_id": self.tenant_id,
            "visibility": VISIBILITY,
            "matters": [matter.to_dict() for matter in self.matters],
        }


def _authorize_client(
    *,
    tenant_id: str,
    principal_id: str,
    principal_repository: PrincipalReader,
    membership_repository: MembershipReader,
    business_role_repository: AssignmentReader,
    role_assignment_repository: AssignmentReader,
    session: Any,
) -> None:
    """Require exact D4 current LEGAL_CLIENT read authorization."""
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
    if (
        decision.authorized is not True
        or decision.reason is not TenantAuthorizationReason.AUTHORIZED
        or decision.business_role != "tenant_legal_client"
        or decision.authorization_role != "LEGAL_CLIENT"
    ):
        _fail(
            "L8_7D5_CLIENT_AUTHORIZATION_DENIED_"
            + decision.reason.value
        )


def get_legal_client_matter_projection(
    *,
    tenant_id: str,
    principal_id: str,
    visibility_collection: Any,
    lifecycle_collection: Any,
    principal_repository: PrincipalReader,
    membership_repository: MembershipReader,
    business_role_repository: AssignmentReader,
    role_assignment_repository: AssignmentReader,
    session: Any,
) -> LegalClientMatterProjectionSet:
    """Return the authenticated client's exact current visible matters.

    Order of proof is security-significant:

    1. require one caller-owned active transaction;
    2. authorize the exact D4 client-matter read against current IAM;
    3. enumerate only current ACTIVE L8-7B bindings for that tenant/principal;
    4. resolve each bound identity through the canonical L8-5 current read model;
    5. project only the four whitelisted CaseMatter fields.

    An authorized client with zero ACTIVE relations receives an empty immutable
    projection. Any corrupt visibility evidence or missing/corrupt bound matter
    rejects the whole projection; the function never broadens to tenant-wide
    CaseMatter enumeration. The same caller session is forwarded unchanged to
    every authority/visibility/lifecycle read. No mutation or transaction
    ownership occurs here.
    """
    tenant = _identity("tenant_id", tenant_id)
    principal = _identity("principal_id", principal_id)
    active_session = _active_transaction(session)

    _authorize_client(
        tenant_id=tenant,
        principal_id=principal,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        business_role_repository=business_role_repository,
        role_assignment_repository=role_assignment_repository,
        session=active_session,
    )

    try:
        bindings = LegalClientMatterVisibilityRegistry.list_active_for_principal(
            tenant,
            principal,
            visibility_collection,
            session=active_session,
        )
    except LegalClientMatterVisibilityPersistedRecordInvalidError as error:
        _fail("L8_7D5_VISIBILITY_EVIDENCE_INVALID", error)
    except LegalClientMatterVisibilityRegistryError as error:
        _fail("L8_7D5_VISIBILITY_EVIDENCE_UNAVAILABLE", error)

    projected: list[LegalClientMatterProjection] = []
    seen: set[str] = set()
    for binding in bindings:
        if (
            binding.tenant_id != tenant
            or binding.client_principal_id != principal
            or binding.case_matter_id in seen
        ):
            _fail("L8_7D5_VISIBILITY_SCOPE_INVALID")
        seen.add(binding.case_matter_id)

        try:
            model = get_entity_read_model(
                tenant_id=tenant,
                entity_type="CaseMatter",
                entity_identity=binding.case_matter_id,
                lifecycle_collection=lifecycle_collection,
                session=active_session,
            )
        except LegalOperationsReadModelError as error:
            if error.code == "L8_5_ENTITY_NOT_FOUND":
                _fail("L8_7D5_BOUND_MATTER_NOT_FOUND", error)
            _fail("L8_7D5_BOUND_MATTER_EVIDENCE_UNAVAILABLE", error)

        if (
            model.tenant_id != tenant
            or model.entity_type != "CaseMatter"
            or model.entity_identity != binding.case_matter_id
            or type(model.current) is not CaseMatter
        ):
            _fail("L8_7D5_BOUND_MATTER_INVALID")

        current = cast(CaseMatter, model.current)
        if (
            current.tenant_id != tenant
            or current.case_matter_id != binding.case_matter_id
        ):
            _fail("L8_7D5_BOUND_MATTER_SCOPE_INVALID")

        projected.append(
            LegalClientMatterProjection(
                case_matter_id=current.case_matter_id,
                matter_reference=current.matter_reference,
                opened_at=current.opened_at,
                state=current.state,
            )
        )

    matters = tuple(
        sorted(
            projected,
            key=lambda value: (
                value.case_matter_id,
                value.matter_reference,
            ),
        )
    )
    return LegalClientMatterProjectionSet(
        tenant_id=tenant,
        matters=matters,
    )


__all__ = [
    "OPERATION",
    "PERMISSION",
    "SCHEMA",
    "VERSION",
    "VISIBILITY",
    "LegalClientMatterProjection",
    "LegalClientMatterProjectionError",
    "LegalClientMatterProjectionSet",
    "LegalClientMatterProjectionTransactionRequiredError",
    "get_legal_client_matter_projection",
]


# ARTIFACT: legal_client_matter_projection.py
# VERSION: v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION
# AUTHORITY BOUNDARY: current D4 LEGAL_CLIENT IAM + ACTIVE L8-7B visibility + current P1 CaseMatter sanitized projection only
# TENANT POSTURE: one exact tenant/principal and caller-owned active session span IAM, visibility and every bound matter read
# FAIL-CLOSED POSTURE: denied IAM, corrupt/unavailable visibility, missing/corrupt bound matter, scope drift or inactive transaction rejects whole projection
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
