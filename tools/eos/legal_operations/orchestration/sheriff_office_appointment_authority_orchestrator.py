"""TITLE: WILSY OS Sheriff Office Appointment Evidence Orchestrator
VERSION: v1.0.0-L8-SHERIFF-OFFICE-APPOINTMENT-EVIDENCE-ORCHESTRATION
ARTIFACT: tools/eos/legal_operations/orchestration/sheriff_office_appointment_authority_orchestrator.py
AUTHORITY: Current IAM, canonical P1 office/jurisdiction and verified external instrument evidence composition before immutable appointment evidence persistence.
EPITOME: Record one independently verified Ministerial Sheriff appointment, exact office scope, jurisdiction-matched Board Fidelity Fund Certificate, and professional indemnity insurance for one active tenant Sheriff principal.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/sheriff_office_appointment_authority_orchestrator.py
COLLABORATION / OWNERSHIP: IAM repositories own current principal/membership/business-role/authorization-role facts; P1/L8-0 own District and SheriffOffice truth; this orchestrator owns same-transaction composition; appointment registry owns append-only persistence/currentness; external Minister and South African Board for Sheriffs remain issuing authorities.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG: v1.0.0 establishes independently verified, tenant-scoped Sheriff appointment evidence admission with exact replay and optimistic revision control.
COMPLIANCE: Sheriffs Act 90 of 1986, sections 2, 3, 5 and 30-34; POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque principal/office identifiers, source references, and SHA3-512 fingerprints only; no source document bytes or credentials.
TENANT BOUNDARY: All IAM, canonical directory, and appointment registry reads use one exact tenant and one caller-owned active transaction.
AUTHORITY BOUNDARY: Verifier attestation records a human's inspection of external Ministerial appointment, office-scope, Board FFC and professional-indemnity evidence. It does not issue an appointment, independently authenticate external documents, grant IAM, or itself authorize a read.
DUAL CONTROL: Target Sheriff principal must differ from the active tenant-admin verifier.
TRANSACTION OWNERSHIP: Caller-owned active transaction required; this module never starts, commits, aborts, or retries it.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
FAIL-CLOSED DECLARATION: Missing/inactive/wrong IAM, self-verification, absent/corrupt P1 office/district, jurisdiction mismatch, stale revision, divergent replay, invalid evidence, or persistence failure rejects.
"""

from __future__ import annotations

from datetime import datetime
import hmac
from typing import Any, Final, NoReturn, cast

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepository,
    RoleAssignmentRepositoryError,
)
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
    TenantBusinessRoleRepositoryError,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipNotFoundError,
    TenantMembershipRepository,
    TenantMembershipRepositoryError,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    District,
    SheriffOffice,
)
from tools.eos.legal_operations.domain.legal_operations_read_model import (
    LegalOperationsReadModelError,
    get_entity_read_model,
)
from tools.eos.legal_operations.domain.sheriff_office_appointment_authority import (
    SheriffOfficeAppointmentAuthority,
    SheriffOfficeAppointmentAuthorityError,
)
from tools.eos.legal_operations.registry.sheriff_office_appointment_authority_registry import (
    SheriffOfficeAppointmentAuthorityRegistry,
    SheriffOfficeAppointmentConflictError,
    SheriffOfficeAppointmentRegistryError,
)


VERSION: Final[str] = "v1.0.0-L8-SHERIFF-OFFICE-APPOINTMENT-EVIDENCE-ORCHESTRATION"


class SheriffOfficeAppointmentOrchestrationError(RuntimeError):
    """Stable fail-closed appointment composition failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class SheriffOfficeAppointmentTransactionRequiredError(
    SheriffOfficeAppointmentOrchestrationError
):
    """Caller did not provide one already-active transaction."""


def _fail(
    code: str,
    cause: BaseException | None = None,
    *,
    error_type: type[SheriffOfficeAppointmentOrchestrationError] = (
        SheriffOfficeAppointmentOrchestrationError
    ),
) -> NoReturn:
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _active_transaction(session: object) -> object:
    if session is None:
        _fail(
            "L8_SOA_ACTIVE_TRANSACTION_REQUIRED",
            error_type=SheriffOfficeAppointmentTransactionRequiredError,
        )
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail(
            "L8_SOA_ACTIVE_TRANSACTION_REQUIRED",
            error,
            error_type=SheriffOfficeAppointmentTransactionRequiredError,
        )
    if active is not True:
        _fail(
            "L8_SOA_ACTIVE_TRANSACTION_REQUIRED",
            error_type=SheriffOfficeAppointmentTransactionRequiredError,
        )
    return session


def _principal(
    principal_id: str,
    collection: Any,
    *,
    session: Any,
) -> PrincipalAuthority:
    try:
        value = PrincipalAuthorityRepository.get(
            principal_id,
            collection,
            session=session,
        )
    except PrincipalAuthorityNotFoundError as error:
        _fail("L8_SOA_PRINCIPAL_NOT_FOUND", error)
    except PrincipalAuthorityRepositoryError as error:
        _fail("L8_SOA_PRINCIPAL_AUTHORITY_UNAVAILABLE", error)
    if value.status is not PrincipalStatus.ACTIVE:
        _fail("L8_SOA_PRINCIPAL_INACTIVE")
    return value


def _membership(
    principal_id: str,
    tenant_id: str,
    collection: Any,
    *,
    session: Any,
) -> TenantMembershipAuthority:
    try:
        value = TenantMembershipRepository.resolve(
            principal_id,
            tenant_id,
            collection,
            session=session,
        )
    except TenantMembershipNotFoundError as error:
        _fail("L8_SOA_MEMBERSHIP_NOT_FOUND", error)
    except TenantMembershipRepositoryError as error:
        _fail("L8_SOA_MEMBERSHIP_AUTHORITY_UNAVAILABLE", error)
    if value.status is not TenantMembershipStatus.ACTIVE:
        _fail("L8_SOA_MEMBERSHIP_INACTIVE")
    return value


def _business_role(
    principal_id: str,
    tenant_id: str,
    expected_role: str,
    collection: Any,
    *,
    session: Any,
) -> TenantBusinessRoleAuthority:
    try:
        value = TenantBusinessRoleRepository.resolve(
            principal_id,
            tenant_id,
            collection,
            session=session,
        )
    except TenantBusinessRoleNotFoundError as error:
        _fail("L8_SOA_BUSINESS_ROLE_NOT_FOUND", error)
    except TenantBusinessRoleRepositoryError as error:
        _fail("L8_SOA_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE", error)
    if (
        value.status is not TenantBusinessRoleStatus.ACTIVE
        or value.business_role != expected_role
    ):
        _fail("L8_SOA_BUSINESS_ROLE_REQUIRED")
    return value


def _authorization_role(
    principal_id: str,
    tenant_id: str,
    expected_role: str,
    collection: Any,
    *,
    session: Any,
) -> RoleAssignmentAuthority:
    try:
        value = RoleAssignmentRepository.resolve(
            principal_id,
            tenant_id,
            expected_role,
            collection,
            session=session,
        )
    except RoleAssignmentNotFoundError as error:
        _fail("L8_SOA_AUTHORIZATION_ROLE_NOT_FOUND", error)
    except RoleAssignmentRepositoryError as error:
        _fail("L8_SOA_AUTHORIZATION_ROLE_UNAVAILABLE", error)
    if value.status is not RoleAssignmentStatus.ACTIVE:
        _fail("L8_SOA_AUTHORIZATION_ROLE_REQUIRED")
    return value


def _district(
    tenant_id: str,
    district_id: str,
    collection: Any,
    *,
    session: Any,
) -> District:
    try:
        model = get_entity_read_model(
            tenant_id=tenant_id,
            entity_type="District",
            entity_identity=district_id,
            lifecycle_collection=collection,
            session=session,
        )
    except LegalOperationsReadModelError as error:
        if error.code == "L8_5_ENTITY_NOT_FOUND":
            _fail("L8_SOA_DISTRICT_NOT_FOUND", error)
        _fail("L8_SOA_DISTRICT_EVIDENCE_UNAVAILABLE", error)
    if (
        model.tenant_id != tenant_id
        or model.entity_type != "District"
        or model.entity_identity != district_id
        or type(model.current) is not District
    ):
        _fail("L8_SOA_DISTRICT_EVIDENCE_INVALID")
    return cast(District, model.current)


def _office(
    tenant_id: str,
    sheriff_office_id: str,
    collection: Any,
    *,
    session: Any,
) -> SheriffOffice:
    try:
        model = get_entity_read_model(
            tenant_id=tenant_id,
            entity_type="SheriffOffice",
            entity_identity=sheriff_office_id,
            lifecycle_collection=collection,
            session=session,
        )
    except LegalOperationsReadModelError as error:
        if error.code == "L8_5_ENTITY_NOT_FOUND":
            _fail("L8_SOA_OFFICE_NOT_FOUND", error)
        _fail("L8_SOA_OFFICE_EVIDENCE_UNAVAILABLE", error)
    if (
        model.tenant_id != tenant_id
        or model.entity_type != "SheriffOffice"
        or model.entity_identity != sheriff_office_id
        or type(model.current) is not SheriffOffice
    ):
        _fail("L8_SOA_OFFICE_EVIDENCE_INVALID")
    return cast(SheriffOffice, model.current)


def _same_command(
    value: SheriffOfficeAppointmentAuthority,
    *,
    principal_id: str,
    sheriff_office_id: str,
    district_id: str,
    appointment_kind: str,
    appointment_instrument_reference: str,
    appointment_instrument_fingerprint: str,
    office_scope_instrument_reference: str,
    office_scope_instrument_fingerprint: str,
    fidelity_fund_certificate_reference: str,
    fidelity_fund_certificate_fingerprint: str,
    certificate_jurisdiction_reference: str,
    professional_indemnity_insurance_reference: str,
    professional_indemnity_insurance_fingerprint: str,
    appointment_effective_from: datetime,
    appointment_effective_until: datetime | None,
    certificate_valid_from: datetime,
    certificate_valid_until: datetime,
    professional_indemnity_insurance_valid_from: datetime,
    professional_indemnity_insurance_valid_until: datetime,
    verifier_principal_id: str,
) -> bool:
    expected = (
        principal_id,
        sheriff_office_id,
        district_id,
        appointment_kind,
        appointment_instrument_reference,
        appointment_instrument_fingerprint,
        office_scope_instrument_reference,
        office_scope_instrument_fingerprint,
        fidelity_fund_certificate_reference,
        fidelity_fund_certificate_fingerprint,
        certificate_jurisdiction_reference,
        professional_indemnity_insurance_reference,
        professional_indemnity_insurance_fingerprint,
        appointment_effective_from,
        appointment_effective_until,
        certificate_valid_from,
        certificate_valid_until,
        professional_indemnity_insurance_valid_from,
        professional_indemnity_insurance_valid_until,
        verifier_principal_id,
    )
    actual = (
        value.principal_id,
        value.sheriff_office_id,
        value.district_id,
        value.appointment_kind,
        value.appointment_instrument_reference,
        value.appointment_instrument_fingerprint,
        value.office_scope_instrument_reference,
        value.office_scope_instrument_fingerprint,
        value.fidelity_fund_certificate_reference,
        value.fidelity_fund_certificate_fingerprint,
        value.certificate_jurisdiction_reference,
        value.professional_indemnity_insurance_reference,
        value.professional_indemnity_insurance_fingerprint,
        value.appointment_effective_from,
        value.appointment_effective_until,
        value.certificate_valid_from,
        value.certificate_valid_until,
        value.professional_indemnity_insurance_valid_from,
        value.professional_indemnity_insurance_valid_until,
        value.verified_by_principal_id,
    )
    return hmac.compare_digest(
        repr(expected).encode("utf-8"),
        repr(actual).encode("utf-8"),
    )


def record_sheriff_office_appointment_authority(
    *,
    tenant_id: str,
    appointment_id: str,
    expected_revision: int,
    expected_predecessor_fingerprint: str | None,
    principal_id: str,
    sheriff_office_id: str,
    appointment_kind: str,
    appointment_instrument_reference: str,
    appointment_instrument_fingerprint: str,
    office_scope_instrument_reference: str,
    office_scope_instrument_fingerprint: str,
    fidelity_fund_certificate_reference: str,
    fidelity_fund_certificate_fingerprint: str,
    professional_indemnity_insurance_reference: str,
    professional_indemnity_insurance_fingerprint: str,
    appointment_effective_from: datetime,
    appointment_effective_until: datetime | None,
    certificate_valid_from: datetime,
    certificate_valid_until: datetime,
    professional_indemnity_insurance_valid_from: datetime,
    professional_indemnity_insurance_valid_until: datetime,
    verifier_principal_id: str,
    verified_at: datetime,
    lifecycle_collection: Any,
    appointment_collection: Any,
    principal_collection: Any,
    membership_collection: Any,
    business_role_collection: Any,
    role_assignment_collection: Any,
    session: Any,
) -> SheriffOfficeAppointmentAuthority:
    """Record or exactly replay one independently verified Sheriff appointment.

    The verifier must be an active own-tenant administrator; the target must be
    an active own-tenant Sheriff principal. The office and District are resolved
    from canonical P1 current truth. The certificate jurisdiction is derived
    from District.jurisdiction_code and cannot be supplied by the caller.

    expected_revision and expected_predecessor_fingerprint are optimistic
    concurrency tokens, not authority. An exact retry returns the existing
    immutable revision only when every source fact, effective window, target,
    office and verifier matches.
    """
    active_session = _active_transaction(session)
    if verifier_principal_id == principal_id:
        _fail("L8_SOA_SELF_VERIFICATION_FORBIDDEN")

    _principal(principal_id, principal_collection, session=active_session)
    _membership(
        principal_id,
        tenant_id,
        membership_collection,
        session=active_session,
    )
    _business_role(
        principal_id,
        tenant_id,
        "tenant_sheriff",
        business_role_collection,
        session=active_session,
    )
    _authorization_role(
        principal_id,
        tenant_id,
        "SHERIFF",
        role_assignment_collection,
        session=active_session,
    )

    _principal(verifier_principal_id, principal_collection, session=active_session)
    _membership(
        verifier_principal_id,
        tenant_id,
        membership_collection,
        session=active_session,
    )
    _business_role(
        verifier_principal_id,
        tenant_id,
        "tenant_admin",
        business_role_collection,
        session=active_session,
    )
    _authorization_role(
        verifier_principal_id,
        tenant_id,
        "ENTERPRISE_ADMIN",
        role_assignment_collection,
        session=active_session,
    )

    office = _office(
        tenant_id,
        sheriff_office_id,
        lifecycle_collection,
        session=active_session,
    )
    district = _district(
        tenant_id,
        office.district_id,
        lifecycle_collection,
        session=active_session,
    )
    if (
        office.tenant_id != tenant_id
        or district.tenant_id != tenant_id
        or office.district_id != district.district_id
    ):
        _fail("L8_SOA_CANONICAL_OFFICE_DISTRICT_LINEAGE_INVALID")

    registry = SheriffOfficeAppointmentAuthorityRegistry(appointment_collection)
    try:
        history = registry.get_history_if_any(
            tenant_id,
            appointment_id,
            session=active_session,
        )
    except SheriffOfficeAppointmentRegistryError as error:
        _fail("L8_SOA_APPOINTMENT_HISTORY_UNAVAILABLE", error)

    if expected_revision < 0:
        _fail("L8_SOA_EXPECTED_REVISION_INVALID")
    if len(history) == expected_revision + 1:
        existing = history[-1]
        if (
            existing.revision == expected_revision + 1
            and (
                expected_predecessor_fingerprint
                == existing.supersedes_fingerprint
            )
            and _same_command(
                existing,
                principal_id=principal_id,
                sheriff_office_id=sheriff_office_id,
                district_id=district.district_id,
                appointment_kind=appointment_kind,
                appointment_instrument_reference=appointment_instrument_reference,
                appointment_instrument_fingerprint=appointment_instrument_fingerprint,
                office_scope_instrument_reference=office_scope_instrument_reference,
                office_scope_instrument_fingerprint=office_scope_instrument_fingerprint,
                fidelity_fund_certificate_reference=fidelity_fund_certificate_reference,
                fidelity_fund_certificate_fingerprint=fidelity_fund_certificate_fingerprint,
                certificate_jurisdiction_reference=district.jurisdiction_code,
                professional_indemnity_insurance_reference=professional_indemnity_insurance_reference,
                professional_indemnity_insurance_fingerprint=professional_indemnity_insurance_fingerprint,
                appointment_effective_from=appointment_effective_from,
                appointment_effective_until=appointment_effective_until,
                certificate_valid_from=certificate_valid_from,
                certificate_valid_until=certificate_valid_until,
                professional_indemnity_insurance_valid_from=professional_indemnity_insurance_valid_from,
                professional_indemnity_insurance_valid_until=professional_indemnity_insurance_valid_until,
                verifier_principal_id=verifier_principal_id,
            )
        ):
            return existing
        _fail("L8_SOA_DIVERGENT_REPLAY")

    if len(history) != expected_revision:
        _fail("L8_SOA_STALE_APPOINTMENT_REVISION")
    predecessor = history[-1].fingerprint if history else None
    if expected_predecessor_fingerprint != predecessor:
        _fail("L8_SOA_PREDECESSOR_MISMATCH")

    try:
        value = SheriffOfficeAppointmentAuthority(
            tenant_id=tenant_id,
            appointment_id=appointment_id,
            revision=expected_revision + 1,
            principal_id=principal_id,
            sheriff_office_id=sheriff_office_id,
            district_id=district.district_id,
            appointment_kind=appointment_kind,
            appointment_instrument_reference=appointment_instrument_reference,
            appointment_instrument_fingerprint=appointment_instrument_fingerprint,
            office_scope_instrument_reference=office_scope_instrument_reference,
            office_scope_instrument_fingerprint=office_scope_instrument_fingerprint,
            fidelity_fund_certificate_reference=fidelity_fund_certificate_reference,
            fidelity_fund_certificate_fingerprint=fidelity_fund_certificate_fingerprint,
            certificate_jurisdiction_reference=district.jurisdiction_code,
            professional_indemnity_insurance_reference=professional_indemnity_insurance_reference,
            professional_indemnity_insurance_fingerprint=professional_indemnity_insurance_fingerprint,
            professional_indemnity_insurance_valid_from=professional_indemnity_insurance_valid_from,
            professional_indemnity_insurance_valid_until=professional_indemnity_insurance_valid_until,
            appointment_effective_from=appointment_effective_from,
            appointment_effective_until=appointment_effective_until,
            certificate_valid_from=certificate_valid_from,
            certificate_valid_until=certificate_valid_until,
            verified_by_principal_id=verifier_principal_id,
            verified_at=verified_at,
            supersedes_fingerprint=predecessor,
        )
    except SheriffOfficeAppointmentAuthorityError as error:
        _fail("L8_SOA_APPOINTMENT_VALUE_INVALID", error)

    try:
        return registry.create_or_replay(value, session=active_session)
    except SheriffOfficeAppointmentConflictError as error:
        _fail("L8_SOA_APPOINTMENT_CONFLICT", error)
    except SheriffOfficeAppointmentRegistryError as error:
        _fail("L8_SOA_APPOINTMENT_PERSISTENCE_UNAVAILABLE", error)


__all__ = [
    "VERSION",
    "SheriffOfficeAppointmentOrchestrationError",
    "SheriffOfficeAppointmentTransactionRequiredError",
    "record_sheriff_office_appointment_authority",
]


# ARTIFACT: sheriff_office_appointment_authority_orchestrator.py
# VERSION: v1.0.0-L8-SHERIFF-OFFICE-APPOINTMENT-EVIDENCE-ORCHESTRATION
# AUTHORITY BOUNDARY: current Sheriff/admin IAM + canonical P1 + external evidence attestation before immutable persistence
# TENANT POSTURE: exact tenant and caller-owned session across every authority and evidence read/write
# FAIL-CLOSED POSTURE: self-verification, inactive/wrong role, canonical mismatch, stale revision, replay divergence, and persistence failure reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
