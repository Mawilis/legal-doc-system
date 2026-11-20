"""TITLE: WILSY Founder Legacy-to-Global Credential Migration Command
VERSION: v1.0.0-OWNER-FACTOR-VERIFIED-EXACT-PRINCIPAL-MIGRATION
AUTHORITY: Existing Owner password, existing OTP, exact ACTIVE principal and
  membership, source-owned PrincipalCredentialRepository, audit-only receipt.
EPITOME: Migrate one already-established legacy Founder identity to its current
  Global Principal credential without creating a principal, MFA factor or grant.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/founder_legacy_credential_migration.py
COLLABORATION / OWNERSHIP: AuthRegistry owns Owner bcrypt and OTP verification;
  read-only migration assessment owns identity/source checks; canonical credential
  repository owns issuance; global MFA KMS service owns subsequent factor migration.
CERTIFICATION / UPDATE DATE: 2026-11-20
CHANGELOG: v1.0.0-OWNER-FACTOR-VERIFIED-EXACT-PRINCIPAL-MIGRATION
  adds explicit current Owner password plus enrolled legacy OTP proof, one
  source-matched canonical credential insertion and atomic immutable receipt.
COMPLIANCE: POPIA s19; GDPR Article 32; SOC2 CC7.2; ISO27001.
SECURITY / PRIVACY POSTURE: Passwords, OTP secrets and hashes are never logged
  or included in audit. Verification occurs locally against canonical EOS truth.
TENANT BOUNDARY: Only WILSYTENANT-4CD2FZ4O and one fixed Founder email.
AUTHORITY BOUNDARY: Cannot create/modify principal, membership, role, MFA,
  owner user, entitlement or commercial subscription. No authentication bypass.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusive.
TRANSACTION BOUNDARY: Source checks, canonical credential insert and receipt
  use one caller-owned Mongo transaction with majority write concern.
FAIL-CLOSED DECLARATION: Wrong password/OTP, source mutation, ambiguous user,
  competing credential or authority, and missing audit prevent issuance.
"""
from __future__ import annotations

from datetime import datetime, timezone
import getpass
import hashlib
import re
from typing import Any, Final

from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from pymongo.write_concern import WriteConcern

from tools.eos.kernel import db as kernel_db
from tools.eos.saas.auth.auth_registry import get_auth_registry
from tools.eos.auth.principal_credential_migration_assessment import (
    assess_legacy_user_credential,
)
from tools.eos.auth.principal_credential_repository import (
    PrincipalCredentialRepository,
    PrincipalCredentialNotFoundError,
)

VERSION: Final[str] = "v1.0.0-OWNER-FACTOR-VERIFIED-EXACT-PRINCIPAL-MIGRATION"
FOUNDER_EMAIL: Final[str] = "wilsonkhanyezi@gmail.com"
FOUNDER_TENANT_ID: Final[str] = "WILSYTENANT-4CD2FZ4O"
_AUDIT_COLLECTION: Final[str] = "global_principal_credential_migration_evidence"
_OTP_CODE: Final[re.Pattern[str]] = re.compile(r"^\d{6}$")


class FounderCredentialMigrationRejected(RuntimeError):
    """Bounded operator-facing rejection; no sensitive credentials."""


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise FounderCredentialMigrationRejected(code)


def _get_unique_user(database: Any, *, session: Any = None) -> dict[str, Any]:
    rows = list(database["users"].find(
        {"email": FOUNDER_EMAIL}, session=session,
    ).limit(2))
    _require(len(rows) == 1, "FOUNDER_LEGACY_EMAIL_NOT_UNIQUE")
    source = rows[0]
    _require(
        source.get("tenantId") == FOUNDER_TENANT_ID
        and source.get("user_id") is None
        and isinstance(source.get("_id"), ObjectId),
        "FOUNDER_LEGACY_IDENTITY_NOT_ELIGIBLE",
    )
    opaque_id = str(source["_id"])
    competing = list(database["users"].find(
        {"user_id": opaque_id}, projection={"_id": 1},
        session=session,
    ).limit(2))
    _require(
        not competing or (
            len(competing) == 1 and competing[0]["_id"] == source["_id"]
        ),
        "FOUNDER_LEGACY_IDENTITY_COLLISION",
    )
    return source


def migrate_founder_credential(
    *, password: str, otp_code: str,
) -> dict[str, str]:
    """Require existing two-factor Owner proof before canonical migration.

    Credentials, audit and readback never confer any business operation.
    A second invocation is read-only only when the existing credential and
    receipt exactly match the already verified legacy source.
    """
    _require(isinstance(password, str) and bool(password),
             "FOUNDER_LEGACY_PASSWORD_REQUIRED")
    _require(
        isinstance(otp_code, str) and _OTP_CODE.fullmatch(otp_code) is not None,
        "FOUNDER_LEGACY_FACTOR_CODE_INVALID",
    )
    client, database = kernel_db.get_client(), kernel_db.get_database()
    _require(client is not None and database is not None
             and database.name == "wilsy",
             "FOUNDER_CANONICAL_DATABASE_REQUIRED")
    source = _get_unique_user(database)
    principal_id = str(source["_id"])
    registry = get_auth_registry(None)
    authenticated = registry.authenticate(FOUNDER_EMAIL, password)
    _require(
        authenticated is not None
        and authenticated.id == principal_id
        and authenticated.tenantId == FOUNDER_TENANT_ID
        and authenticated.mfaRegistered is True,
        "FOUNDER_LEGACY_OWNER_PASSWORD_NOT_VERIFIED",
    )
    _require(
        registry.verify_otp(principal_id, otp_code) is True,
        "FOUNDER_LEGACY_OWNER_MFA_NOT_VERIFIED",
    )
    credentials = database["principal_credentials"].with_options(
        write_concern=WriteConcern(w="majority", j=True),
    )
    audit = database[_AUDIT_COLLECTION].with_options(
        write_concern=WriteConcern(w="majority", j=True),
    )
    PrincipalCredentialRepository.ensure_indexes(credentials)
    audit.create_index(
        [("principal_id", 1)], unique=True,
        name="credential_migration_one_receipt_per_principal",
    )

    def current_source(session: Any) -> Any:
        fresh = _get_unique_user(database, session=session)
        _require(fresh["_id"] == source["_id"]
                 and fresh.get("passwordHash") == source.get("passwordHash")
                 and fresh.get("credential_revision") == source.get("credential_revision")
                 and fresh.get("mfaRegistered") == source.get("mfaRegistered"),
                 "FOUNDER_LEGACY_SOURCE_CHANGED")
        assessment = assess_legacy_user_credential(
            document=fresh, matching_email_record_count=1, session=session,
        )
        _require(assessment.disposition == "ELIGIBLE_FOR_GOVERNED_MIGRATION"
                 and assessment.credential is not None
                 and assessment.credential.principal_id == principal_id
                 and assessment.tenant_id == FOUNDER_TENANT_ID
                 and assessment.credential.mfa_enabled is True,
                 "FOUNDER_LEGACY_SOURCE_QUARANTINED_" + assessment.reason_code)
        return assessment.credential

    with client.start_session() as session:
        with session.start_transaction():
            credential = current_source(session)
            existing_rows = list(credentials.find({
                "$or": [
                    {"normalized_email": credential.normalized_email},
                    {"principal_id": principal_id},
                ]
            }, session=session).limit(2))
            if existing_rows:
                _require(
                    len(existing_rows) == 1
                    and existing_rows[0].get("principal_id") == principal_id
                    and existing_rows[0].get("normalized_email") == credential.normalized_email
                    and existing_rows[0].get("password_hash") == credential.password_hash
                    and existing_rows[0].get("credential_revision") == credential.credential_revision,
                    "FOUNDER_GLOBAL_CREDENTIAL_CONFLICT",
                )
                _require(
                    audit.count_documents({"principal_id": principal_id},
                                          limit=2, session=session) == 1,
                    "FOUNDER_GLOBAL_CREDENTIAL_AUDIT_MISSING",
                )
                status = "ALREADY_ISSUED"
            else:
                _require(
                    audit.count_documents({"principal_id": principal_id},
                                          limit=2, session=session) == 0,
                    "FOUNDER_GLOBAL_CREDENTIAL_AUDIT_CONFLICT",
                )
                PrincipalCredentialRepository.insert(
                    credential, credentials, session=session,
                )
                audit.insert_one({
                    "principal_id": principal_id,
                    "tenant_id": FOUNDER_TENANT_ID,
                    "event": "LEGACY_FOUNDER_OWNER_FACTOR_VERIFIED_CREDENTIAL_MIGRATION",
                    "source": "EXISTING_USERS_OBJECTID_AND_ACTIVE_PRINCIPAL",
                    "email_fingerprint": hashlib.sha3_256(
                        FOUNDER_EMAIL.encode("utf-8")
                    ).hexdigest(),
                    "credential_revision": credential.credential_revision,
                    "legacy_password_verified": True,
                    "legacy_mfa_verified": True,
                    "occurred_at": datetime.now(timezone.utc),
                }, session=session)
                status = "ISSUED"
    with client.start_session() as session:
        readback = PrincipalCredentialRepository.get_by_email(
            FOUNDER_EMAIL, credentials, session=session,
        )
        evidence = audit.find_one(
            {"principal_id": principal_id}, session=session,
        )
        _require(
            readback.principal_id == principal_id
            and readback.normalized_email == FOUNDER_EMAIL
            and readback.credential_revision == credential.credential_revision
            and readback.mfa_enabled is True
            and isinstance(evidence, dict)
            and evidence.get("tenant_id") == FOUNDER_TENANT_ID
            and evidence.get("credential_revision") == credential.credential_revision,
            "FOUNDER_GLOBAL_CREDENTIAL_READBACK_FAILED",
        )
    return {
        "credential_state": status,
        "canonical_principal": "EXISTING_ACTIVE_LINK",
        "source_tenant": "VERIFIED",
        "migration_audit": "PERSISTED",
        "next_gate": "GLOBAL_MFA_KMS_FACTOR_MIGRATION",
    }


def main() -> int:
    """Interactive, no shell-argument credentials and no secret output."""
    print("=== FOUNDER EXISTING CREDENTIAL GOVERNED MIGRATION ===")
    connected, _ = kernel_db.connect_db()
    if not connected:
        print("MIGRATION=DATABASE_UNAVAILABLE")
        return 2
    password = getpass.getpass("Existing Owner password (hidden): ")
    otp_code = getpass.getpass("Existing Owner authenticator code (hidden): ")
    try:
        result = migrate_founder_credential(password=password, otp_code=otp_code)
        for field, value in result.items():
            print(field.upper() + "=" + value)
        print("MIGRATION=PASS")
        return 0
    except FounderCredentialMigrationRejected as error:
        print("MIGRATION=DENIED")
        print("ERROR_CODE=" + str(error))
        return 2
    except (DuplicateKeyError, Exception) as error:
        print("MIGRATION=UNAVAILABLE")
        print("FAILURE_CLASS=" + type(error).__name__)
        return 2
    finally:
        password = ""
        otp_code = ""
        client = kernel_db.get_client()
        if client is not None:
            client.close()


if __name__ == "__main__":
    raise SystemExit(main())

# ARTIFACT: founder_legacy_credential_migration.py
# VERSION: v1.0.0-OWNER-FACTOR-VERIFIED-EXACT-PRINCIPAL-MIGRATION
# AUTHORITY BOUNDARY: password+MFA and existing source; canonical repository only
# TENANT POSTURE: fixed Founder tenant; no identity generation or role grants
# FAIL-CLOSED POSTURE: source drift, missing audit or conflicting credential denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
