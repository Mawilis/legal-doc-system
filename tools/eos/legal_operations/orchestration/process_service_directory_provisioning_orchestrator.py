"""Canonical provisioning orchestration for the Process Service directory.

TITLE: WILSY OS Process Service Directory Provisioning Orchestrator
VERSION: v1.0.1-L8-1-PROCESS-SERVICE-DIRECTORY-PROVISIONING
AUTHORITY: Wilsy OS Legal Operations directory composition over canonical P1/P2 truth.
EPITOME: Create or exactly replay tenant-scoped District, SheriffOffice, and
         Deputy directory facts inside one caller-owned active transaction,
         while validating District -> SheriffOffice -> Deputy lineage and
         rejecting divergent durable identities before any additional write.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/process_service_directory_provisioning_orchestrator.py
COLLABORATION / OWNERSHIP: P1 owns immutable directory value semantics; P2 owns
                            immutable persistence and strict hydration; L8-0
                            owns deterministic immutable-current validation;
                            this orchestrator owns only governed provisioning
                            composition. HTTP/IAM admission remains separate.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.1-L8-1-PROCESS-SERVICE-DIRECTORY-PROVISIONING
           replaces the generic variadic P1 constructor helper with exact
           typed District, SheriffOffice, and Deputy constructors so static
           analysis proves the same fail-closed runtime contract without casts
           or weakened validation.
           2026-09-23 v1.0.0-L8-1-PROCESS-SERVICE-DIRECTORY-PROVISIONING
           established transaction-required create/exact-replay provisioning
           for District, SheriffOffice, and Deputy with canonical parent
           resolution, lineage validation, divergence rejection, and no
           lifecycle allocation/service/financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Accepts only explicit tenant-scoped directory
                             attributes and evidence references. It accepts no
                             credentials, JWT claims, provider secrets, payment
                             data, browser authority, or cross-tenant fallback.
TENANT BOUNDARY: Every history lookup and write binds the exact tenant_id.
                 Parent District/SheriffOffice values must resolve under that
                 same tenant and cross-tenant absence remains indistinguishable
                 from ordinary exact-scope absence.
AUTHORITY BOUNDARY: Directory provisioning only. It cannot accept instructions,
                    receive documents, allocate work, authorize attempts,
                    establish service, generate returns, issue invoices, grant
                    IAM roles, execute funds, or establish settlement truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; directory facts carry no payment
                              or settlement semantics.
TRANSACTION BOUNDARY: The caller must supply one already-active transaction
                      session. This module never starts, commits, aborts, or
                      retries a transaction. P2 receives the same session for
                      every exact-history read and write.
FAIL-CLOSED DECLARATION: Missing transaction, malformed P1 values, absent
                         parents, parent lineage mismatch, corrupt/divergent
                         durable history, and same-identity/different-fact
                         provisioning all reject without healing or overwrite.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Final, NoReturn, TypeVar, cast

from tools.eos.legal_operations.domain.legal_operations_current_projection import (
    LegalOperationsCurrentProjectionError,
    resolve_current_lifecycle_snapshot,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    Deputy,
    District,
    LegalOperationsLifecycleError,
    SheriffOffice,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)


VERSION: Final[str] = "v1.0.1-L8-1-PROCESS-SERVICE-DIRECTORY-PROVISIONING"

_DirectoryValue = District | SheriffOffice | Deputy
_TDirectory = TypeVar("_TDirectory", District, SheriffOffice, Deputy)


class ProcessServiceDirectoryProvisioningDisposition(StrEnum):
    """Durable outcome classification without adding lifecycle authority."""

    CREATED = "CREATED"
    REPLAYED = "REPLAYED"


class ProcessServiceDirectoryProvisioningError(RuntimeError):
    """Stable fail-closed L8-1 directory provisioning failure.

    The exception represents no persistence mutation by itself and grants no
    tenant, IAM, legal-lifecycle, service, billing, payment, financial-execution,
    or settlement authority.
    """

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class ProcessServiceDirectoryTransactionRequiredError(
    ProcessServiceDirectoryProvisioningError
):
    """Caller did not provide an already-active transaction session."""


@dataclass(frozen=True, slots=True)
class ProcessServiceDirectoryProvisioningResult:
    """Immutable result for one directory create or exact replay.

    The value is the exact canonical P1 directory value returned by P2.
    The disposition reports whether this orchestration observed no prior exact
    identity before persistence or replayed an already-identical immutable
    value. The result carries no allocation, service, IAM, invoice, payment,
    execution, or settlement authority.
    """

    value: _DirectoryValue
    disposition: ProcessServiceDirectoryProvisioningDisposition

    def __post_init__(self) -> None:
        """Reject malformed result composition rather than invent success."""
        if type(self.value) not in {District, SheriffOffice, Deputy}:
            _fail("L8_1_DIRECTORY_RESULT_VALUE_INVALID")
        if not isinstance(
            self.disposition,
            ProcessServiceDirectoryProvisioningDisposition,
        ):
            _fail("L8_1_DIRECTORY_RESULT_DISPOSITION_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Serialize bounded result evidence without adding authority."""
        return {
            "disposition": self.disposition.value,
            "value": self.value.to_dict(),
        }


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable provisioning failure while retaining technical cause."""
    error = ProcessServiceDirectoryProvisioningError(code)
    if cause is None:
        raise error
    raise error from cause


def _active_transaction(session: object) -> object:
    """Require one already-active caller-owned transaction before any read."""
    if session is None:
        raise ProcessServiceDirectoryTransactionRequiredError(
            "L8_1_ACTIVE_TRANSACTION_REQUIRED"
        )
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        raise ProcessServiceDirectoryTransactionRequiredError(
            "L8_1_ACTIVE_TRANSACTION_REQUIRED"
        ) from error
    if active is not True:
        raise ProcessServiceDirectoryTransactionRequiredError(
            "L8_1_ACTIVE_TRANSACTION_REQUIRED"
        )
    return session


def _construct_district(
    tenant_id: str,
    district_id: str,
    name: str,
    jurisdiction_code: str,
    evidence_reference: str,
) -> District:
    """Construct one exact District and normalize P1 validation failures."""
    try:
        return District(
            tenant_id,
            district_id,
            name,
            jurisdiction_code,
            evidence_reference,
        )
    except LegalOperationsLifecycleError as error:
        _fail("L8_1_DIRECTORY_VALUE_INVALID", error)


def _construct_sheriff_office(
    tenant_id: str,
    sheriff_office_id: str,
    district_id: str,
    name: str,
    evidence_reference: str,
) -> SheriffOffice:
    """Construct one exact SheriffOffice and normalize P1 validation failures."""
    try:
        return SheriffOffice(
            tenant_id,
            sheriff_office_id,
            district_id,
            name,
            evidence_reference,
        )
    except LegalOperationsLifecycleError as error:
        _fail("L8_1_DIRECTORY_VALUE_INVALID", error)


def _construct_deputy(
    tenant_id: str,
    deputy_id: str,
    sheriff_office_id: str,
    display_name: str,
    badge_reference: str,
    evidence_reference: str,
) -> Deputy:
    """Construct one exact Deputy and normalize P1 validation failures."""
    try:
        return Deputy(
            tenant_id,
            deputy_id,
            sheriff_office_id,
            display_name,
            badge_reference,
            evidence_reference,
        )
    except LegalOperationsLifecycleError as error:
        _fail("L8_1_DIRECTORY_VALUE_INVALID", error)


def _history_current(
    *,
    tenant_id: str,
    entity_type: type[_TDirectory],
    entity_identity: str,
    collection: Any,
    session: object,
) -> _TDirectory | None:
    """Resolve one exact immutable directory identity or bounded absence.

    P2 enumerates the complete exact tenant/type/entity history. L8-0 then
    rejects divergent immutable durable facts. Empty exact history returns None;
    no cross-tenant lookup or fallback occurs.
    """
    history = LegalOperationsLifecycleRegistry.get_entity_history(
        tenant_id,
        entity_type.__name__,
        entity_identity,
        collection,
        session=session,
    )
    if not history:
        return None
    try:
        value = resolve_current_lifecycle_snapshot(
            history,
            expected_type=entity_type,
        )
    except LegalOperationsCurrentProjectionError as error:
        _fail("L8_1_DIRECTORY_HISTORY_DIVERGENT", error)
    if type(value) is not entity_type:
        _fail("L8_1_DIRECTORY_HISTORY_TYPE_INVALID")
    return cast(_TDirectory, value)


def _persist_or_replay(
    proposed: _TDirectory,
    *,
    collection: Any,
    session: object,
) -> ProcessServiceDirectoryProvisioningResult:
    """Persist one new immutable identity or return exact replay.

    The complete current history is checked before P2 creation. Existing same
    identity with a different fingerprint rejects before another row is
    inserted, preventing directory divergence from being introduced through
    this orchestrator. Exact existing fingerprint is replayed without write.
    """
    entity_type = type(proposed)
    identity_field = {
        District: "district_id",
        SheriffOffice: "sheriff_office_id",
        Deputy: "deputy_id",
    }.get(entity_type)
    if identity_field is None:
        _fail("L8_1_DIRECTORY_VALUE_INVALID")
    entity_identity = getattr(proposed, identity_field, None)
    if not isinstance(entity_identity, str):
        _fail("L8_1_DIRECTORY_VALUE_INVALID")

    existing = _history_current(
        tenant_id=proposed.tenant_id,
        entity_type=cast(type[_TDirectory], entity_type),
        entity_identity=entity_identity,
        collection=collection,
        session=session,
    )
    if existing is not None:
        if existing.fingerprint != proposed.fingerprint:
            _fail("L8_1_DIRECTORY_IDENTITY_DIVERGENCE")
        return ProcessServiceDirectoryProvisioningResult(
            value=existing,
            disposition=ProcessServiceDirectoryProvisioningDisposition.REPLAYED,
        )

    persisted = LegalOperationsLifecycleRegistry.create(
        proposed,
        collection,
        session=session,
    )
    if type(persisted) is not entity_type:
        _fail("L8_1_DIRECTORY_PERSISTED_TYPE_INVALID")
    if persisted.fingerprint != proposed.fingerprint:
        _fail("L8_1_DIRECTORY_PERSISTED_DIVERGENCE")
    return ProcessServiceDirectoryProvisioningResult(
        value=cast(_DirectoryValue, persisted),
        disposition=ProcessServiceDirectoryProvisioningDisposition.CREATED,
    )


def provision_district(
    *,
    tenant_id: str,
    district_id: str,
    name: str,
    jurisdiction_code: str,
    evidence_reference: str,
    lifecycle_collection: Any,
    session: object,
) -> ProcessServiceDirectoryProvisioningResult:
    """Create or exactly replay one tenant-scoped District.

    The caller must already own an active transaction and must separately prove
    IAM authority at the transport boundary. This function validates P1 domain
    shape and exact durable identity before persistence. It does not infer a
    jurisdiction from external providers or create allocation/service authority.
    """
    active_session = _active_transaction(session)
    value = _construct_district(
        tenant_id,
        district_id,
        name,
        jurisdiction_code,
        evidence_reference,
    )
    return _persist_or_replay(
        value,
        collection=lifecycle_collection,
        session=active_session,
    )


def provision_sheriff_office(
    *,
    tenant_id: str,
    sheriff_office_id: str,
    district_id: str,
    name: str,
    evidence_reference: str,
    lifecycle_collection: Any,
    session: object,
) -> ProcessServiceDirectoryProvisioningResult:
    """Create or exactly replay one SheriffOffice under a canonical District.

    The exact tenant-scoped District must already exist as non-divergent
    immutable P2/L8-0 truth. The function does not create a missing District,
    cross tenant boundaries, or infer district lineage from caller claims.
    """
    active_session = _active_transaction(session)
    district = _history_current(
        tenant_id=tenant_id,
        entity_type=District,
        entity_identity=district_id,
        collection=lifecycle_collection,
        session=active_session,
    )
    if district is None:
        _fail("L8_1_DISTRICT_NOT_FOUND")

    value = _construct_sheriff_office(
        tenant_id,
        sheriff_office_id,
        district_id,
        name,
        evidence_reference,
    )
    if value.district_id != district.district_id:
        _fail("L8_1_DISTRICT_OFFICE_LINEAGE_MISMATCH")
    return _persist_or_replay(
        value,
        collection=lifecycle_collection,
        session=active_session,
    )


def provision_deputy(
    *,
    tenant_id: str,
    deputy_id: str,
    sheriff_office_id: str,
    display_name: str,
    badge_reference: str,
    evidence_reference: str,
    lifecycle_collection: Any,
    session: object,
) -> ProcessServiceDirectoryProvisioningResult:
    """Create or exactly replay one Deputy under canonical office lineage.

    The exact tenant-scoped SheriffOffice and its referenced District must both
    already resolve as non-divergent immutable truth. The function creates no
    IAM role, service authority, custody possession, or financial authority.
    """
    active_session = _active_transaction(session)
    office = _history_current(
        tenant_id=tenant_id,
        entity_type=SheriffOffice,
        entity_identity=sheriff_office_id,
        collection=lifecycle_collection,
        session=active_session,
    )
    if office is None:
        _fail("L8_1_SHERIFF_OFFICE_NOT_FOUND")

    district = _history_current(
        tenant_id=tenant_id,
        entity_type=District,
        entity_identity=office.district_id,
        collection=lifecycle_collection,
        session=active_session,
    )
    if district is None:
        _fail("L8_1_OFFICE_DISTRICT_NOT_FOUND")
    if office.district_id != district.district_id:
        _fail("L8_1_DISTRICT_OFFICE_LINEAGE_MISMATCH")

    value = _construct_deputy(
        tenant_id,
        deputy_id,
        sheriff_office_id,
        display_name,
        badge_reference,
        evidence_reference,
    )
    if value.sheriff_office_id != office.sheriff_office_id:
        _fail("L8_1_OFFICE_DEPUTY_LINEAGE_MISMATCH")
    return _persist_or_replay(
        value,
        collection=lifecycle_collection,
        session=active_session,
    )


__all__ = [
    "VERSION",
    "ProcessServiceDirectoryProvisioningDisposition",
    "ProcessServiceDirectoryProvisioningError",
    "ProcessServiceDirectoryProvisioningResult",
    "ProcessServiceDirectoryTransactionRequiredError",
    "provision_deputy",
    "provision_district",
    "provision_sheriff_office",
]


# ARTIFACT: process_service_directory_provisioning_orchestrator.py
# VERSION: v1.0.1-L8-1-PROCESS-SERVICE-DIRECTORY-PROVISIONING
# AUTHORITY BOUNDARY: transaction-scoped District/SheriffOffice/Deputy provisioning composition only
# TENANT POSTURE: exact tenant history and writes; canonical parent lineage required
# FAIL-CLOSED POSTURE: inactive transaction, absence, corruption, divergence, and lineage mismatch reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT