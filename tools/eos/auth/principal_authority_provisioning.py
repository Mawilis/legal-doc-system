"""WILSY OS durable principal-authority provisioning owner.

TITLE: Durable PrincipalAuthority Provisioning Owner
VERSION: v1.1.0-R1D-B0F-B4-R6A
AUTHORITY: The sole orchestration seam for initial PrincipalAuthority creation.
EPITOME: Create one immutable revision-zero principal snapshot from an explicit
         admission or activation decision, never from a role, tenant, JWT, or
         protected read.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/principal_authority_provisioning.py
COLLABORATION / OWNERSHIP: Account-admission and activation callers invoke this
                           seam; the repository remains persistence-only.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.1.0-R1D-B0F-B4-R6A requires immutable initial-status authority
           evidence, while retaining idempotent creation and caller-owned sessions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Only opaque principal identity and lifecycle state
                            cross this boundary; no credentials or tenant data.
TENANT BOUNDARY: PrincipalAuthority is tenant-neutral; membership is separate.
AUTHORITY BOUNDARY: Initial principal lifecycle snapshot only; no role grant,
                    authentication, membership, or token issuance.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: The caller owns any Mongo session and transaction.
FAIL-CLOSED POSTURE: Missing authority evidence, malformed input, absence, and
                     conflicting durable state are explicit denials.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from pymongo.collection import Collection

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityAlreadyExistsError,
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_initial_status_authority import (
    AUTHORITY_SOURCE_ID,
    PRINCIPAL_INITIAL_STATUS_OPERATION,
    PrincipalInitialStatusAuthorityEvidence,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.kernel import db as kernel_db


VERSION = "v1.1.0-R1D-B0F-B4-R6A"
ADMISSION_STATUS_AUTHORITY = "ACCOUNT_ADMISSION_EXPLICIT"
ACTIVATION_STATUS_AUTHORITY = "PRINCIPAL_ACTIVATION_EXPLICIT"


class PrincipalAuthorityProvisioningError(RuntimeError):
    """Stable fail-closed provisioning refusal."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class PrincipalAuthorityProvisioningResult:
    """Redacted outcome of one initial-authority command."""

    authority: PrincipalAuthority
    created: bool


def _collection(collection: Optional[Collection]) -> Collection:
    """Use an injected collection or the sole live Kernel database."""
    if collection is not None:
        return collection
    database = kernel_db.get_database()
    if database is None:
        raise PrincipalAuthorityProvisioningError("PRINCIPAL_AUTHORITY_PERSISTENCE_UNAVAILABLE")
    try:
        return database["principal_authorities"]
    except Exception as error:
        raise PrincipalAuthorityProvisioningError("PRINCIPAL_AUTHORITY_COLLECTION_UNAVAILABLE") from error


def provision_principal_authority(
    *,
    principal_id: str,
    initial_status: PrincipalStatus | None = None,
    status: PrincipalStatus | None = None,
    authority_evidence: PrincipalInitialStatusAuthorityEvidence | None = None,
    collection: Optional[Collection] = None,
    session: Any = None,
) -> PrincipalAuthorityProvisioningResult:
    """Create or replay one explicit revision-zero principal authority.

    ``authority_evidence`` is mandatory immutable evidence supplied by the
    sanctioned admission/activation owner. ``users.status``, ``SUPER_ADMIN``,
    tenant membership, browser state, JWT claims, and a bare status marker are
    never accepted as evidence. ``initial_status`` is the canonical request
    field; ``status`` remains a non-authoritative compatibility alias. The
    caller owns transaction/session lifecycle and whole-transaction retry.
    """
    if not isinstance(principal_id, str) or not principal_id.strip():
        raise PrincipalAuthorityProvisioningError("PRINCIPAL_ID_REQUIRED")
    if not isinstance(authority_evidence, PrincipalInitialStatusAuthorityEvidence):
        raise PrincipalAuthorityProvisioningError("PRINCIPAL_INITIAL_STATUS_AUTHORITY_EVIDENCE_REQUIRED")
    if authority_evidence.subject_principal_id != principal_id.strip():
        raise PrincipalAuthorityProvisioningError("PRINCIPAL_INITIAL_STATUS_AUTHORITY_SUBJECT_MISMATCH")
    if authority_evidence.operation != PRINCIPAL_INITIAL_STATUS_OPERATION:
        raise PrincipalAuthorityProvisioningError("PRINCIPAL_INITIAL_STATUS_AUTHORITY_OPERATION_MISMATCH")
    if authority_evidence.authority_source != AUTHORITY_SOURCE_ID:
        raise PrincipalAuthorityProvisioningError("PRINCIPAL_INITIAL_STATUS_AUTHORITY_SOURCE_MISMATCH")
    requested_status = initial_status if initial_status is not None else status
    if initial_status is not None and status is not None and initial_status is not status:
        raise PrincipalAuthorityProvisioningError("PRINCIPAL_INITIAL_STATUS_AUTHORITY_STATUS_MISMATCH")
    if requested_status is not None and requested_status is not authority_evidence.target_status:
        raise PrincipalAuthorityProvisioningError("PRINCIPAL_INITIAL_STATUS_AUTHORITY_STATUS_MISMATCH")
    status = authority_evidence.target_status

    target = PrincipalAuthority(principal_id.strip(), status, 0)
    target_collection = _collection(collection)
    try:
        existing = PrincipalAuthorityRepository.get(
            target.principal_id, target_collection, session=session
        )
    except PrincipalAuthorityNotFoundError:
        try:
            created = PrincipalAuthorityRepository.create(
                target, target_collection, session=session
            )
        except PrincipalAuthorityAlreadyExistsError as error:
            # A concurrent creator won; re-read and classify exact replay or
            # divergence instead of overwriting the durable row.
            try:
                existing = PrincipalAuthorityRepository.get(
                    target.principal_id, target_collection, session=session
                )
            except PrincipalAuthorityRepositoryError as reread_error:
                raise PrincipalAuthorityProvisioningError(
                    "PRINCIPAL_AUTHORITY_RECONCILIATION_UNAVAILABLE"
                ) from reread_error
            if existing != target:
                raise PrincipalAuthorityProvisioningError(
                    "PRINCIPAL_AUTHORITY_CONFLICT"
                ) from error
            return PrincipalAuthorityProvisioningResult(existing, False)
        except PrincipalAuthorityRepositoryError as error:
            raise PrincipalAuthorityProvisioningError(
                "PRINCIPAL_AUTHORITY_CREATE_FAILED"
            ) from error
        return PrincipalAuthorityProvisioningResult(created, True)
    except PrincipalAuthorityRepositoryError as error:
        raise PrincipalAuthorityProvisioningError(
            "PRINCIPAL_AUTHORITY_READ_FAILED"
        ) from error

    if existing != target:
        raise PrincipalAuthorityProvisioningError("PRINCIPAL_AUTHORITY_CONFLICT")
    return PrincipalAuthorityProvisioningResult(existing, False)


__all__ = [
    "ACTIVATION_STATUS_AUTHORITY",
    "ADMISSION_STATUS_AUTHORITY",
    "PrincipalAuthorityProvisioningError",
    "PrincipalAuthorityProvisioningResult",
    "VERSION",
    "provision_principal_authority",
]

# ARTIFACT: principal_authority_provisioning.py
# VERSION: v1.1.0-R1D-B0F-B4-R6A
# AUTHORITY BOUNDARY: explicit initial PrincipalAuthority snapshot only
# TENANT POSTURE: tenant-neutral; membership and roles remain separate
# FAIL-CLOSED POSTURE: no status inference, upsert, overwrite, or hidden transaction
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
