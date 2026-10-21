"""Sovereign authenticated practitioner-matter binding HTTP command plane.

TITLE: WILSY OS Practitioner Matter Binding HTTP Router
VERSION: v1.0.0-P9-P12C-R4C-AUTHENTICATED-COMMANDS
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Compose authenticated partner-only grant and revoke commands over
    canonical current IAM, matter, policy and conflict-disposition evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/legal_practitioner_matter_binding_router.py
COLLABORATION / OWNERSHIP: The P9 provisioning service owns binding decisions;
    canonical registries own persisted evidence; HTTP owns only admission,
    repository composition, session lifecycle and bounded responses.
CERTIFICATION / UPDATE DATE: 2026-10-20
CHANGELOG: v1.0.0-P9-P12C-R4C-AUTHENTICATED-COMMANDS introduces strict
    grant/revoke requests and caller-owned transaction composition.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No raw client identities, document contents,
    credentials, conflict narrative or authorization decisions are accepted.
TENANT BOUNDARY: Authenticated tenant context and tenant-scoped evidence
    queries only; no browser-supplied tenant or actor identity.
AUTHORITY BOUNDARY: Relationship evidence only. No matter content admission,
    independent access permission, ethical-wall clearance or waiver.
TRANSACTION BOUNDARY: Exactly one API-owned MongoDB transaction per command;
    commit before receipt, abort on failure, no implied successful retry.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusively responsible
    for financial execution and settlement.
FAIL-CLOSED DECLARATION: Missing IAM, source provenance, binding history,
    tenant scope, transaction integrity or persistence rejects.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Final, TypeVar

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
    get_principal_authority_repository,
    get_tenant_membership_repository,
    get_role_assignment_repository,
)
from tools.eos.auth.authorization import (
    get_role_assignment_repository as get_authorization_role_repository,
)
from tools.eos.kernel.db import get_client, get_database
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
)
from tools.eos.legal_operations.registry.legal_practitioner_matter_access_registry import (
    get_by_id,
)
from tools.eos.legal_operations.registry.legal_practitioner_matter_binding_registry import (
    COLLECTION_NAME as BINDING_COLLECTION,
)
from tools.eos.legal_operations.registry.legal_client_matter_conflict_disposition_registry import (
    COLLECTION as DISPOSITION_COLLECTION,
    get_disposition_by_fingerprint,
)
from tools.eos.legal_operations.service.legal_practitioner_matter_binding_provisioning_service import (
    PERMISSION,
    OPERATION,
    PractitionerBindingProvisioningDenied,
    grant_binding,
    revoke_binding,
)

VERSION: Final[str] = "v1.0.0-P9-P12C-R4C-AUTHENTICATED-COMMANDS"
ACCESS_EVIDENCE_COLLECTION: Final[str] = (
    "legal_practitioner_matter_access_evidence"
)

router = APIRouter(
    prefix="/legal-operations/practitioner-bindings",
    tags=["Legal Practitioner Binding"],
)

_PROVISION = RequireTenantAuthorization(PERMISSION, OPERATION)
_T = TypeVar("_T")


class GrantPractitionerBindingCommand(BaseModel):
    """Opaque grant intent only; no client-selected authority or chronology."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    case_matter_id: str = Field(min_length=1, max_length=200)
    practitioner_principal_id: str = Field(min_length=1, max_length=200)
    binding_id: str = Field(min_length=1, max_length=200)
    access_evidence_id: str = Field(min_length=1, max_length=200)
    expected_access_evidence_fingerprint: str = Field(
        pattern=r"^[0-9a-f]{128}$"
    )


class RevokePractitionerBindingCommand(BaseModel):
    """Opaque revocation command without client-supplied actor or timestamp."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    binding_id: str = Field(min_length=1, max_length=200)
    evidence_reference: str = Field(min_length=1, max_length=512)


def _collection(database: Any, name: str) -> Any:
    """Resolve only a named canonical collection; never install indexes."""
    if database is None:
        raise HTTPException(503, "P9_BINDING_PERSISTENCE_UNAVAILABLE")
    try:
        return database.get_collection(name)
    except Exception as exc:
        raise HTTPException(
            503, "P9_BINDING_PERSISTENCE_UNAVAILABLE"
        ) from exc


def _translate(error: Exception) -> HTTPException:
    """Collapse sensitive service/registry failures to bounded HTTP outcomes."""
    if isinstance(error, PractitionerBindingProvisioningDenied):
        code = str(error)
        if (
            "DENIED" in code
            or "INACTIVE" in code
            or "INELIGIBLE" in code
            or "MISMATCH" in code
        ):
            return HTTPException(403, "P9_BINDING_AUTHORIZATION_DENIED")
        if (
            "NOT_CURRENT" in code
            or "CONFLICT" in code
            or "CORRUPT" in code
        ):
            return HTTPException(409, "P9_BINDING_CURRENTNESS_CONFLICT")
        if "INPUT_INVALID" in code:
            return HTTPException(422, "P9_BINDING_COMMAND_INVALID")
    return HTTPException(503, "P9_BINDING_AUTHORITY_UNAVAILABLE")


def _transaction(callback: Callable[[Any, Any], _T]) -> _T:
    """Commit one API-owned transaction before returning a command result."""
    client, database = get_client(), get_database()
    if client is None or database is None:
        raise HTTPException(503, "P9_BINDING_PERSISTENCE_UNAVAILABLE")
    try:
        with client.start_session() as session:
            session.start_transaction()
            try:
                result = callback(session, database)
                session.commit_transaction()
                return result
            except Exception:
                if bool(getattr(session, "in_transaction", False)):
                    session.abort_transaction()
                raise
    except HTTPException:
        raise
    except Exception as error:
        raise _translate(error) from error


@router.post("", status_code=status.HTTP_201_CREATED)
def grant_practitioner_binding(
    command: GrantPractitionerBindingCommand,
    context: TenantAuthorizationContext = Depends(_PROVISION),
    principal_repository: Any = Depends(get_principal_authority_repository),
    membership_repository: Any = Depends(get_tenant_membership_repository),
    business_role_repository: Any = Depends(get_role_assignment_repository),
    role_assignment_repository: Any = Depends(
        get_authorization_role_repository
    ),
) -> dict[str, object]:
    """Grant relationship evidence after canonical transactional provenance."""
    def run(session: Any, database: Any) -> dict[str, object]:
        access = _collection(database, ACCESS_EVIDENCE_COLLECTION)
        dispositions = _collection(database, DISPOSITION_COLLECTION)

        evidence = get_by_id(
            tenant_id=context.tenant_id,
            access_evidence_id=command.access_evidence_id,
            collection=access,
            session=session,
        )
        if (
            evidence is None
            or evidence.case_matter_id != command.case_matter_id
            or evidence.practitioner_principal_id
            != command.practitioner_principal_id
            or evidence.fingerprint
            != command.expected_access_evidence_fingerprint
        ):
            raise HTTPException(403, "P9_BINDING_EVIDENCE_DENIED")

        disposition = get_disposition_by_fingerprint(
            context.tenant_id,
            evidence.source_evidence_fingerprint,
            dispositions,
            session=session,
        )
        if (
            disposition.tenant_id != context.tenant_id
            or disposition.case_matter_id != command.case_matter_id
            or disposition.fingerprint
            != evidence.source_evidence_fingerprint
        ):
            raise HTTPException(403, "P9_BINDING_PROVENANCE_DENIED")

        result = grant_binding(
            authenticated_principal_id=context.identity.identity_id,
            tenant_id=context.tenant_id,
            case_matter_id=command.case_matter_id,
            practitioner_principal_id=command.practitioner_principal_id,
            binding_id=command.binding_id,
            access_evidence_id=command.access_evidence_id,
            expected_access_evidence_fingerprint=(
                command.expected_access_evidence_fingerprint
            ),
            granted_at=datetime.now(timezone.utc),
            client_party_id=disposition.client_party_id,
            subject_identity_fingerprint=(
                disposition.subject_identity_fingerprint
            ),
            principal_repository=principal_repository,
            membership_repository=membership_repository,
            business_role_repository=business_role_repository,
            role_assignment_repository=role_assignment_repository,
            lifecycle_collection=_collection(database, LIFECYCLE_COLLECTION),
            access_evidence_collection=access,
            disposition_collection=dispositions,
            binding_collection=_collection(database, BINDING_COLLECTION),
            session=session,
        )
        return result.to_dict()

    return _transaction(run)


@router.post("/revocations", status_code=status.HTTP_201_CREATED)
def revoke_practitioner_binding(
    command: RevokePractitionerBindingCommand,
    context: TenantAuthorizationContext = Depends(_PROVISION),
    principal_repository: Any = Depends(get_principal_authority_repository),
    membership_repository: Any = Depends(get_tenant_membership_repository),
    business_role_repository: Any = Depends(get_role_assignment_repository),
    role_assignment_repository: Any = Depends(
        get_authorization_role_repository
    ),
) -> dict[str, object]:
    """Revoke only a current own-tenant binding within one transaction."""
    def run(session: Any, database: Any) -> dict[str, object]:
        result = revoke_binding(
            authenticated_principal_id=context.identity.identity_id,
            tenant_id=context.tenant_id,
            binding_id=command.binding_id,
            evidence_reference=command.evidence_reference,
            revoked_at=datetime.now(timezone.utc),
            principal_repository=principal_repository,
            membership_repository=membership_repository,
            business_role_repository=business_role_repository,
            role_assignment_repository=role_assignment_repository,
            binding_collection=_collection(database, BINDING_COLLECTION),
            session=session,
        )
        return result.to_dict()

    return _transaction(run)


# ARTIFACT: legal_practitioner_matter_binding_router.py
# VERSION: v1.0.0-P9-P12C-R4C-AUTHENTICATED-COMMANDS
# AUTHORITY BOUNDARY: authenticated transport only; no access admission
# TENANT POSTURE: canonical tenant context and exact tenant-scoped reads
# FAIL-CLOSED POSTURE: denied, corrupt, absent and unavailable authority rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
