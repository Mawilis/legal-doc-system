"""R1D-B0F-B4-R6 legacy principal-authority reconciliation.

TITLE: Exact Legacy PrincipalAuthority Reconciliation
VERSION: v1.1.0-R1D-B0F-B4-R6A
AUTHORITY: Bounded migration evidence and explicit PrincipalAuthority creation.
EPITOME: Validate the known legacy Wilsy account and canonical tenant, then
         report a write-free dry run unless a separately sanctioned status
         authority is supplied.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/migrations/reconcile_legacy_principal_authority.py
COLLABORATION / OWNERSHIP: Auth migration owner; Kernel DB owns connectivity;
                           principal provisioning owns the single create seam.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.1.0-R1D-B0F-B4-R6A consumes deployment-rooted initial-status
           evidence before ACTIVE creation; exact predicates and dry-run safety remain.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No credentials, OTP, email, or role data is emitted.
TENANT BOUNDARY: Exact legacy ObjectId and canonical tenant predicates only.
AUTHORITY BOUNDARY: Missing principal lifecycle authority only; no membership,
                    role, credential, token, or legal-service authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: ``users.status`` and ``SUPER_ADMIN`` never authorize ACTIVE.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional, cast

from bson import ObjectId
from pymongo.errors import PyMongoError

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
)
from tools.eos.auth.principal_authority_provisioning import (
    PrincipalAuthorityProvisioningError,
    provision_principal_authority,
)
from tools.eos.auth.principal_initial_status_authority import (
    PrincipalInitialStatusAuthorityError,
    PrincipalInitialStatusAuthorityDenialCode,
    verify_principal_initial_status_authority,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.kernel import db as kernel_db


VERSION = "v1.1.0-R1D-B0F-B4-R6A"
LEGACY_PRINCIPAL_ID = "695e423c9d355c0675c6835d"
CANONICAL_TENANT_ID = "WILSYTENANT-4CD2FZ4O"
CANONICAL_DATABASE_NAME = "wilsy"
LEGACY_PRINCIPAL_STATUS = "ACTIVE"


class LegacyPrincipalReconciliationError(RuntimeError):
    """Stable, non-sensitive reconciliation refusal."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class LegacyPrincipalReconciliationReport:
    """Bounded report safe for dry-run output."""

    state: str
    principal_id: str
    database_name: Optional[str]
    user_count: int
    canonical_tenant_count: int
    authority_count: int
    target_status: Optional[str]
    target_revision: Optional[int]
    writes_performed: int


def _rows(collection: Any, query: Mapping[str, object], *, session: Any = None) -> list[dict[str, Any]]:
    """Read exact rows while forwarding caller session."""
    finder = getattr(collection, "find", None)
    if not callable(finder):
        raise LegacyPrincipalReconciliationError("COLLECTION_FIND_REQUIRED")
    try:
        result = cast(Iterable[Mapping[str, Any]], finder(dict(query), session=session))
        return [dict(item) for item in result]
    except PyMongoError as error:
        raise LegacyPrincipalReconciliationError("PERSISTENCE_READ_FAILED") from error


def _database_name(database: Any) -> Optional[str]:
    value = getattr(database, "name", None)
    return str(value) if value is not None else None


def _validate_shape(database: Any, *, session: Any = None) -> tuple[Any, Any, Any]:
    if database is None:
        raise LegacyPrincipalReconciliationError("AUTH_DATABASE_UNAVAILABLE")
    if _database_name(database) != CANONICAL_DATABASE_NAME:
        raise LegacyPrincipalReconciliationError("CANONICAL_DATABASE_REQUIRED")
    try:
        users = database["users"]
        tenants = database["tenants"]
        authorities = database["principal_authorities"]
    except Exception as error:
        raise LegacyPrincipalReconciliationError("AUTH_COLLECTIONS_UNAVAILABLE") from error
    try:
        legacy_rows = _rows(users, {"_id": ObjectId(LEGACY_PRINCIPAL_ID)}, session=session)
    except (TypeError, ValueError) as error:
        raise LegacyPrincipalReconciliationError("LEGACY_PRINCIPAL_ID_INVALID") from error
    if len(legacy_rows) != 1:
        raise LegacyPrincipalReconciliationError("LEGACY_PRINCIPAL_NOT_EXACTLY_ONE")
    user = legacy_rows[0]
    if user.get("user_id") is not None:
        raise LegacyPrincipalReconciliationError("LEGACY_PRINCIPAL_IDENTITY_CHANGED")
    if user.get("tenantId") != CANONICAL_TENANT_ID:
        raise LegacyPrincipalReconciliationError("LEGACY_PRINCIPAL_TENANT_MISMATCH")
    if user.get("status") != LEGACY_PRINCIPAL_STATUS:
        raise LegacyPrincipalReconciliationError("LEGACY_PRINCIPAL_NOT_ACTIVE")
    canonical_tenants = _rows(tenants, {"tenant_id": CANONICAL_TENANT_ID}, session=session)
    if len(canonical_tenants) != 1 or canonical_tenants[0].get("status") != "ACTIVE":
        raise LegacyPrincipalReconciliationError("CANONICAL_TENANT_NOT_ACTIVE_EXACTLY_ONCE")
    return users, authorities, user


def reconcile_legacy_principal_authority(
    *,
    database: Any | None = None,
    client: Any | None = None,
    dry_run: bool = True,
) -> LegacyPrincipalReconciliationReport:
    """Reconcile exactly one legacy principal; dry-run is the default.

    ACTIVE creation is permitted only when the deployment configuration is
    verified by the principal-initial-status authority seam. The legacy
    The deployment verifier is the only source of initial-status authority.
    """
    database = database if database is not None else kernel_db.get_database()
    users, authorities, user = _validate_shape(database)
    existing_rows = _rows(authorities, {"principal_id": LEGACY_PRINCIPAL_ID})
    if len(existing_rows) > 1:
        raise LegacyPrincipalReconciliationError("PRINCIPAL_AUTHORITY_CONFLICT")
    existing: PrincipalAuthority | None = None
    if existing_rows:
        try:
            existing = PrincipalAuthorityRepository.get(LEGACY_PRINCIPAL_ID, authorities)
        except Exception as error:
            raise LegacyPrincipalReconciliationError("PRINCIPAL_AUTHORITY_CORRUPT") from error
        if existing.status is not PrincipalStatus.ACTIVE or existing.revision != 0:
            raise LegacyPrincipalReconciliationError("PRINCIPAL_AUTHORITY_CONFLICT")
        return LegacyPrincipalReconciliationReport(
            "already_reconciled", LEGACY_PRINCIPAL_ID, _database_name(database), 1, 1, 1,
            existing.status.value, existing.revision, 0
        )

    # Deliberately do not treat users.status or role as lifecycle authority.
    try:
        activation_evidence = verify_principal_initial_status_authority(
            principal_id=LEGACY_PRINCIPAL_ID,
            target_status=PrincipalStatus.ACTIVE,
        )
    except PrincipalInitialStatusAuthorityError as error:
        if error.code is PrincipalInitialStatusAuthorityDenialCode.MISSING_AUTHORITY:
            return LegacyPrincipalReconciliationReport(
                "dry_run_pending_status_authority" if dry_run else "blocked_status_authority",
                LEGACY_PRINCIPAL_ID, _database_name(database), 1, 1, 0,
                None, None, 0
            )
        raise LegacyPrincipalReconciliationError(error.code.value) from error
    if activation_evidence.target_status is not PrincipalStatus.ACTIVE:
        raise LegacyPrincipalReconciliationError("PRINCIPAL_INITIAL_STATUS_INVALID")
    if dry_run:
        return LegacyPrincipalReconciliationReport(
            "dry_run_pending", LEGACY_PRINCIPAL_ID, _database_name(database), 1, 1, 0,
            activation_evidence.target_status.value, 0, 0
        )
    if client is None or not callable(getattr(client, "start_session", None)):
        raise LegacyPrincipalReconciliationError("TRANSACTION_CLIENT_REQUIRED")
    try:
        with client.start_session() as session:
            holder: dict[str, Any] = {}

            def callback(current_session: Any) -> None:
                _validate_shape(database, session=current_session)
                result = provision_principal_authority(
                    principal_id=LEGACY_PRINCIPAL_ID,
                    authority_evidence=activation_evidence,
                    collection=authorities,
                    session=current_session,
                )
                holder["result"] = result

            session.with_transaction(callback)
        result = holder.get("result")
        if result is None:
            raise LegacyPrincipalReconciliationError("TRANSACTION_OUTCOME_UNKNOWN")
        return LegacyPrincipalReconciliationReport(
            "reconciled" if result.created else "already_reconciled",
            LEGACY_PRINCIPAL_ID, _database_name(database), 1, 1, 1,
            result.authority.status.value, result.authority.revision, 1 if result.created else 0
        )
    except LegacyPrincipalReconciliationError:
        raise
    except PrincipalAuthorityProvisioningError as error:
        raise LegacyPrincipalReconciliationError(error.code) from error
    except Exception as error:
        raise LegacyPrincipalReconciliationError("TRANSACTION_FAILED") from error


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reconcile the exact legacy principal authority.")
    parser.add_argument("--execute", action="store_true", help="Require explicit activation authority.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run a Kernel-bound dry run; execution remains explicitly gated."""
    args = _parser().parse_args(argv)
    database = kernel_db.get_database()
    try:
        report = reconcile_legacy_principal_authority(database=database, dry_run=not args.execute)
    except LegacyPrincipalReconciliationError as error:
        print(error.code)
        return 2
    print(report.state)
    return 0


__all__ = [
    "CANONICAL_DATABASE_NAME",
    "CANONICAL_TENANT_ID",
    "LEGACY_PRINCIPAL_ID",
    "LegacyPrincipalReconciliationError",
    "LegacyPrincipalReconciliationReport",
    "VERSION",
    "main",
    "reconcile_legacy_principal_authority",
]

# ARTIFACT: reconcile_legacy_principal_authority.py
# VERSION: v1.1.0-R1D-B0F-B4-R6A
# AUTHORITY BOUNDARY: exact legacy PrincipalAuthority reconciliation only
# TENANT POSTURE: exact ObjectId and canonical tenant predicates
# FAIL-CLOSED POSTURE: dry-run default; no status inference, overwrite, or private client
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
