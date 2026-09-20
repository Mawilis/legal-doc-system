"""R1D-B0F-B3A canonical tenant identity reconciliation utility.

TITLE: WILSY OS Legacy Super-Administrator Tenant Reconciliation
VERSION: v1.0.0-R1D-B0F-B3A-TENANT-RECONCILIATION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prepare and, only with explicit confirmation, atomically move one
         proven legacy principal from ``wilsy-sovereign-root`` to the existing
         canonical ``WILSYTENANT-4CD2FZ4O`` tenant without changing identity,
         credentials, permissions, MFA, covenant state, or OTP material.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/migrations/reconcile_legacy_super_admin_tenant.py
COLLABORATION / OWNERSHIP: Auth persistence owner with Kernel DB lifecycle owner.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG:
  v1.0.0-R1D-B0F-B3A-TENANT-RECONCILIATION - Adds dry-run-first, exact
    ObjectId-anchored tenant migration with transaction, idempotency, explicit
    confirmation, principal-scoped session/token revocation, and fail-closed
    preconditions. Records the B3B tenant source-of-truth hardening roadmap.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Reports contain only bounded metadata. Passwords,
    JWTs, refresh tokens, OTP secrets, and PII are never emitted.
TENANT BOUNDARY: The exact principal ObjectId and exact old tenant are required;
    no email, role, or broad tenant query can select a mutation target.
AUTHORITY BOUNDARY: Identity tenant-field reconciliation and revocation of
    sessions/refresh tokens for that principal only; no authorization grant.
FINANCIAL AUTHORITY BOUNDARY: No financial execution or settlement authority.
TRANSACTION BOUNDARY: Execution requires a caller/client-owned Mongo session
    transaction; unsupported transaction seams fail before any write.
ROADMAP: R1D-B0F-B3B - production tenant source-of-truth hardening remains a
         separately gated follow-on and is not performed by this utility.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, NoReturn

from bson import ObjectId
from pymongo.errors import PyMongoError

from tools.eos.kernel import db as kernel_db


VERSION = "v1.0.0-R1D-B0F-B3A-TENANT-RECONCILIATION"
LEGACY_TENANT_ID = "wilsy-sovereign-root"
CANONICAL_TENANT_ID = "WILSYTENANT-4CD2FZ4O"
CANONICAL_TENANT_ALIAS = "wilsy"
CANONICAL_TENANT_STATUS = "ACTIVE"
CANONICAL_TENANT_VERIFIED = True
NEXT_GATED_WORK = "R1D-B0F-B3B - production tenant source-of-truth hardening"


class TenantIdentityMigrationError(RuntimeError):
    """Stable, fail-closed migration refusal without sensitive details."""

    def __init__(self, code: str, message: str | None = None) -> None:
        self.code = code
        super().__init__(message or code)


@dataclass(frozen=True, slots=True)
class MigrationReport:
    """Redacted migration evidence safe for operator output and audit storage."""

    state: str
    database_name: str | None
    principal_id: str
    old_tenant_id: str
    new_tenant_id: str
    role: str | None
    mfa_registered: bool | None
    session_count: int
    refresh_token_count: int
    user_tenant_field_changed_only: bool
    stale_sessions_revoked: bool
    stale_refresh_tokens_revoked: bool
    dry_run: bool
    def to_dict(self) -> dict[str, object]:
        """Return only non-secret migration metadata."""
        return asdict(self)


def _fail(code: str, message: str | None = None) -> NoReturn:
    raise TenantIdentityMigrationError(code, message)


def _object_id(principal_id: str) -> ObjectId:
    if not isinstance(principal_id, str) or not ObjectId.is_valid(principal_id):
        _fail("INVALID_PRINCIPAL_OBJECT_ID")
    try:
        return ObjectId(principal_id)
    except (TypeError, ValueError) as error:
        _fail("INVALID_PRINCIPAL_OBJECT_ID", str(error))


def _find(collection: Any, query: Mapping[str, object], *, session: Any = None) -> list[dict[str, Any]]:
    """Read rows with mandatory session propagation on transaction paths."""
    if collection is None or not callable(getattr(collection, "find", None)):
        _fail("COLLECTION_FIND_REQUIRED")
    rows: Iterable[Mapping[str, Any]] = collection.find(dict(query), session=session)
    return [dict(row) for row in rows]


def _find_one(collection: Any, query: Mapping[str, object], *, session: Any = None) -> dict[str, Any] | None:
    rows = _find(collection, query, session=session)
    return rows[0] if rows else None


def _database_name(database: Any) -> str | None:
    value = getattr(database, "name", None)
    return str(value) if value is not None else None


def _collections(database: Any) -> tuple[Any, Any, Any, Any]:
    if database is None:
        _fail("AUTH_DATABASE_UNAVAILABLE")
    try:
        return (database["users"], database["sessions"], database["refresh_tokens"], database["tenants"])
    except Exception as error:
        _fail("AUTH_COLLECTIONS_UNAVAILABLE", str(error))


def _validate_tenants(tenants: Any, *, session: Any = None) -> None:
    canonical = _find(tenants, {"tenant_id": CANONICAL_TENANT_ID}, session=session)
    if len(canonical) != 1:
        _fail("CANONICAL_TENANT_NOT_EXACTLY_ONE")
    target = canonical[0]
    if target.get("alias") != CANONICAL_TENANT_ALIAS:
        _fail("CANONICAL_TENANT_ALIAS_MISMATCH")
    if target.get("status") != CANONICAL_TENANT_STATUS:
        _fail("CANONICAL_TENANT_STATUS_MISMATCH")
    if target.get("verified") is not CANONICAL_TENANT_VERIFIED:
        _fail("CANONICAL_TENANT_VERIFIED_MISMATCH")
    if _find(tenants, {"tenant_id": LEGACY_TENANT_ID}, session=session):
        _fail("LEGACY_PSEUDO_TENANT_EXISTS")


def _principal_rows(users: Any, principal: ObjectId, tenant_id: str, *, session: Any = None) -> list[dict[str, Any]]:
    return _find(users, {"_id": principal, "tenantId": tenant_id}, session=session)


def _counts(sessions: Any, refresh_tokens: Any, principal_id: str, *, session: Any = None) -> tuple[int, int]:
    return (
        len(_find(sessions, {"user_id": principal_id}, session=session)),
        len(_find(refresh_tokens, {"user_id": principal_id}, session=session)),
    )


def _report(*, database: Any, principal_id: str, state: str, user: Mapping[str, Any] | None,
            session_count: int, refresh_token_count: int, dry_run: bool,
            revoked_sessions: bool = False, revoked_refresh_tokens: bool = False,
            changed_only: bool = False) -> MigrationReport:
    return MigrationReport(
        state=state,
        database_name=_database_name(database),
        principal_id=principal_id,
        old_tenant_id=LEGACY_TENANT_ID,
        new_tenant_id=CANONICAL_TENANT_ID,
        role=str(user.get("role")) if user and user.get("role") is not None else None,
        mfa_registered=bool(user["mfaRegistered"]) if user and "mfaRegistered" in user else None,
        session_count=session_count,
        refresh_token_count=refresh_token_count,
        user_tenant_field_changed_only=changed_only,
        stale_sessions_revoked=revoked_sessions,
        stale_refresh_tokens_revoked=revoked_refresh_tokens,
        dry_run=dry_run,
    )


def _preflight(database: Any, principal_id: str, *, session: Any = None) -> tuple[Any, Any, Any, Any, ObjectId, dict[str, Any] | None, str, int, int]:
    users, sessions, refresh_tokens, tenants = _collections(database)
    principal = _object_id(principal_id)
    _validate_tenants(tenants, session=session)
    legacy = _principal_rows(users, principal, LEGACY_TENANT_ID, session=session)
    canonical = _principal_rows(users, principal, CANONICAL_TENANT_ID, session=session)
    if len(legacy) > 1 or len(canonical) > 1 or (legacy and canonical):
        _fail("PRINCIPAL_IDENTITY_NOT_EXACT")
    if canonical:
        session_count, refresh_count = _counts(sessions, refresh_tokens, principal_id, session=session)
        if session_count or refresh_count:
            _fail("PARTIAL_RECONCILIATION_REQUIRES_REVIEW")
        return users, sessions, refresh_tokens, tenants, principal, canonical[0], "already_reconciled", 0, 0
    if len(legacy) != 1:
        _fail("LEGACY_PRINCIPAL_NOT_EXACTLY_ONE")
    session_count, refresh_count = _counts(sessions, refresh_tokens, principal_id, session=session)
    return users, sessions, refresh_tokens, tenants, principal, legacy[0], "pending", session_count, refresh_count


def run_migration(*, principal_id: str, dry_run: bool = True, database: Any | None = None,
                  client: Any | None = None, confirm_old_tenant: str | None = None,
                  confirm_new_tenant: str | None = None) -> MigrationReport:
    """Validate or execute one exact tenant reconciliation.

    Dry-run performs reads only. Execution requires exact confirmations and a
    caller-owned Mongo transaction; no fallback partial-write path exists.
    """
    if database is None:
        database = kernel_db.get_database()
    if not dry_run and (confirm_old_tenant != LEGACY_TENANT_ID or confirm_new_tenant != CANONICAL_TENANT_ID):
        _fail("EXPLICIT_TENANT_CONFIRMATION_REQUIRED")
    if dry_run:
        try:
            _, _, _, _, _, user, state, sessions, refresh = _preflight(database, principal_id)
            return _report(database=database, principal_id=principal_id, state="dry_run_" + state,
                           user=user, session_count=sessions, refresh_token_count=refresh,
                           dry_run=True, changed_only=False)
        except TenantIdentityMigrationError:
            raise
        except PyMongoError as error:
            raise TenantIdentityMigrationError("PERSISTENCE_READ_FAILED") from error
    if client is None:
        client = kernel_db.get_client()
    if client is None or not callable(getattr(client, "start_session", None)):
        _fail("TRANSACTION_CLIENT_REQUIRED")
    try:
        with client.start_session() as mongo_session:
            def callback(current_session: Any) -> MigrationReport:
                users, sessions_collection, refresh_collection, _, principal, user, state, before_sessions, before_refresh = _preflight(database, principal_id, session=current_session)
                if state == "already_reconciled":
                    return _report(database=database, principal_id=principal_id, state="already_reconciled", user=user,
                                   session_count=0, refresh_token_count=0, dry_run=False)
                update = users.update_one({"_id": principal, "tenantId": LEGACY_TENANT_ID},
                                          {"$set": {"tenantId": CANONICAL_TENANT_ID}}, session=current_session)
                if getattr(update, "matched_count", 0) != 1 or getattr(update, "modified_count", 0) != 1:
                    _fail("PRINCIPAL_TENANT_UPDATE_NOT_EXACT")
                deleted_sessions = sessions_collection.delete_many({"user_id": principal_id}, session=current_session)
                deleted_refresh = refresh_collection.delete_many({"user_id": principal_id}, session=current_session)
                if getattr(deleted_sessions, "deleted_count", 0) != before_sessions or getattr(deleted_refresh, "deleted_count", 0) != before_refresh:
                    _fail("PRINCIPAL_SESSION_REVOCATION_NOT_EXACT")
                return _report(database=database, principal_id=principal_id, state="migrated", user=user,
                               session_count=before_sessions, refresh_token_count=before_refresh,
                               dry_run=False, revoked_sessions=True, revoked_refresh_tokens=True,
                               changed_only=True)
            with_transaction = getattr(mongo_session, "with_transaction", None)
            if not callable(with_transaction):
                _fail("TRANSACTION_CALLBACK_REQUIRED")
            result = with_transaction(callback)
            if not isinstance(result, MigrationReport):
                _fail("TRANSACTION_OUTCOME_UNKNOWN")
            return result
    except TenantIdentityMigrationError:
        raise
    except PyMongoError as error:
        raise TenantIdentityMigrationError("TRANSACTION_FAILED") from error
    except Exception as error:
        raise TenantIdentityMigrationError("TRANSACTION_OUTCOME_UNKNOWN") from error


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reconcile one legacy auth principal tenant identity.")
    parser.add_argument("--principal-id", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--confirm-old-tenant")
    parser.add_argument("--confirm-new-tenant")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the explicit CLI and emit only redacted JSON evidence."""
    args = _parser().parse_args(argv)
    connected, _ = kernel_db.connect_db()
    if not connected:
        print("AUTH_DATABASE_UNAVAILABLE")
        return 2
    try:
        database = kernel_db.get_database()
        client = kernel_db.get_client()
        if database is None or client is None:
            print("AUTH_DATABASE_UNAVAILABLE")
            return 2
        report = run_migration(
            principal_id=args.principal_id,
            dry_run=args.dry_run,
            database=database,
            client=client,
            confirm_old_tenant=args.confirm_old_tenant,
            confirm_new_tenant=args.confirm_new_tenant,
        )
        print(json.dumps(report.to_dict(), sort_keys=True, separators=(",", ":")))
        return 0
    except TenantIdentityMigrationError as error:
        print(error.code)
        return 2
    finally:
        kernel_db.disconnect_db()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except TenantIdentityMigrationError as error:
        raise SystemExit(error.code)


# ARTIFACT: reconcile_legacy_super_admin_tenant.py
# VERSION: v1.0.0-R1D-B0F-B3A-TENANT-RECONCILIATION
# AUTHORITY BOUNDARY: exact legacy-principal tenant reconciliation only
# TENANT POSTURE: explicit ObjectId and old/new tenant predicates; no email scope
# FAIL-CLOSED POSTURE: every identity, target, transaction, and revocation mismatch denies
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
