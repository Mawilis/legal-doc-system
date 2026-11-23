"""TITLE: WILSY Founder Institutional Designation Registry
VERSION: v1.0.2-TYPED-FOUNDER-CURRENTNESS-GUARDS
AUTHORITY: Existing exact WILSY company principal, active membership,
  tenant_owner capacity and ENTERPRISE_ADMIN assignment; verified Owner factor.
EPITOME: Persist and read one explicit non-IAM Founder title with immutable
  decision evidence. Currentness is independently checked at every read.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/founder_institutional_designation.py
COLLABORATION / OWNERSHIP: AuthRegistry owns legacy password and OTP;
  canonical principal, membership, business-role and authorization-role
  repositories own their independent current authorities; workspace bootstrap
  projects non-authorizing title only.
CERTIFICATION / UPDATE DATE: 2026-11-23
CHANGELOG: v1.0.2-TYPED-FOUNDER-CURRENTNESS-GUARDS explicitly
  narrows optional principal, membership, capacity, IAM, Owner, client and
  database sources before access. Missing authorities fail closed with the
  same rejection codes, no casts, blanket type ignores or new grants.
  v1.0.1-ISOLATED-FOUNDER-READBACK verifies existing title
  before canonical Founder-specific source checks, so unrelated users receive
  no title and do not inherit unrelated Founder source failures.
  v1.0.0-EXPLICIT-FOUNDER-DESIGNATION registers user-ratified Founder
  designation against exact already-active principal, never adds IAM grants.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: No password, OTP, email or hashes in audit or output.
TENANT BOUNDARY: WILSYTENANT-4CD2FZ4O only, no tenant aliases.
AUTHORITY BOUNDARY: Title is non-authorizing; tenant_owner remains capacity.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
FAIL-CLOSED DECLARATION: Invalid proof, stale authorities, missing audit,
  anomalous or competing record blocks title; no automatic session grants.
"""
from __future__ import annotations

from datetime import datetime, timezone
import getpass
import hashlib
import json
from typing import Any, Final, TypeVar

from bson import ObjectId
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.kernel import db as kernel_db
from tools.eos.saas.auth.auth_registry import get_auth_registry
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository

VERSION: Final[str] = "v1.0.2-TYPED-FOUNDER-CURRENTNESS-GUARDS"
TENANT: Final[str] = "WILSYTENANT-4CD2FZ4O"
EMAIL: Final[str] = "wilsonkhanyezi@gmail.com"
BUSINESS_ROLE: Final[str] = "tenant_owner"
IAM_ROLE: Final[str] = "ENTERPRISE_ADMIN"
DECISION: Final[str] = "WILSY-INSTITUTIONAL-FOUNDER-DESIGNATION-20261120"
COLLECTION: Final[str] = "institutional_principal_designations"
AUDIT: Final[str] = "institutional_principal_designation_evidence"


class FounderDesignationRejected(RuntimeError):
    """Source-owned fail-closed marker; no credentials or identity data."""


_T = TypeVar("_T")


def _require_present(value: _T | None, code: str) -> _T:
    """Narrow optional source results without weakening an authority denial."""
    if value is None:
        raise FounderDesignationRejected(code)
    return value


def _require(value: bool, code: str) -> None:
    if not value:
        raise FounderDesignationRejected(code)


def _canonical_source(database: Any, principal_id: str, session: Any = None) -> None:
    """Verify exact existing principal and unchanged founder operating role."""
    principal = _require_present(PrincipalAuthorityRepository.get(
        principal_id, database["principal_authorities"], session=session,
    ), "FOUNDER_CURRENT_AUTHORITY_REQUIRED")
    membership = _require_present(TenantMembershipRepository.resolve(
        principal_id, TENANT, database["tenant_memberships"], session=session,
    ), "FOUNDER_CURRENT_AUTHORITY_REQUIRED")
    capacity = _require_present(TenantBusinessRoleRepository.resolve_business_role(
        principal_id, TENANT, BUSINESS_ROLE, database["tenant_business_roles"],
        session=session,
    ), "FOUNDER_CURRENT_AUTHORITY_REQUIRED")
    admin = _require_present(RoleAssignmentRepository.resolve(
        principal_id, TENANT, IAM_ROLE,
        database["role_assignments"], session=session,
    ), "FOUNDER_CURRENT_AUTHORITY_REQUIRED")
    _require(
        principal.principal_id == principal_id
        and principal.status.value == "ACTIVE"
        and membership.principal_id == principal_id
        and membership.tenant_id == TENANT
        and membership.status.value == "ACTIVE"
        and capacity.principal_id == principal_id
        and capacity.tenant_id == TENANT
        and capacity.business_role == BUSINESS_ROLE
        and capacity.status.value == "ACTIVE"
        and admin.principal_id == principal_id
        and admin.tenant_id == TENANT
        and admin.role_id == IAM_ROLE
        and admin.status.value == "ACTIVE",
        "FOUNDER_CURRENT_AUTHORITY_REQUIRED",
    )


def _digest(record: dict[str, object]) -> str:
    return hashlib.sha3_512(json.dumps(
        record, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _principal_from_source(database: Any, session: Any = None) -> str:
    documents = list(database["users"].find(
        {"email": EMAIL, "tenantId": TENANT},
        {"_id": 1, "user_id": 1}, session=session,
    ).limit(2))
    _require(len(documents) == 1, "FOUNDER_OWNER_IDENTITY_NOT_UNIQUE")
    row = documents[0]
    if row.get("user_id") is None:
        _require(isinstance(row.get("_id"), ObjectId),
                 "FOUNDER_OWNER_OBJECTID_REQUIRED")
        principal_id = str(row["_id"])
    else:
        principal_id = row["user_id"]
        _require(isinstance(principal_id, str) and bool(principal_id.strip())
                 and principal_id == principal_id.strip(),
                 "FOUNDER_OWNER_CANONICAL_ID_REQUIRED")
    _canonical_source(database, principal_id, session=session)
    return principal_id


def read_founder_designation(
    *, principal_id: str, tenant_id: str,
    database: Any = None, session: Any = None,
) -> dict[str, str] | None:
    """Fail closed if an explicitly ratified persisted title is not current.

    A missing registration is not a Founder claim. A corrupted registration is
    an unavailable source, not a permit to show a privileged label.
    """
    if tenant_id != TENANT or not isinstance(principal_id, str) or not principal_id:
        return None
    db = database if database is not None else kernel_db.get_database()
    _require(db is not None, "FOUNDER_DESIGNATION_DATABASE_UNAVAILABLE")
    rows = list(db[COLLECTION].find(
        {"tenant_id": TENANT, "principal_id": principal_id},
        {"_id": 0}, session=session,
    ).limit(2))
    if not rows:
        return None
    source = _principal_from_source(db, session=session)
    _require(source == principal_id, "FOUNDER_DESIGNATION_PRINCIPAL_MISMATCH")
    _require(len(rows) == 1, "FOUNDER_DESIGNATION_AMBIGUOUS")
    record = rows[0]
    seal = record.pop("proof_sha3_512", None)
    _require(
        isinstance(seal, str) and seal == _digest(record)
        and record.get("decision") == DECISION
        and record.get("designation") == "Founder"
        and record.get("business_role") == BUSINESS_ROLE
        and record.get("state") == "ACTIVE",
        "FOUNDER_DESIGNATION_EVIDENCE_INVALID",
    )
    evidence = list(db[AUDIT].find(
        {"tenant_id": TENANT, "principal_id": principal_id, "decision": DECISION},
        {"_id": 0}, session=session,
    ).limit(2))
    _require(
        len(evidence) == 1
        and evidence[0].get("proof_sha3_512") == seal
        and evidence[0].get("event") == "FOUNDER_TITLE_RATIFIED",
        "FOUNDER_DESIGNATION_AUDIT_INVALID",
    )
    return {
        "title": "Founder",
        "state": "ACTIVE",
        "authority": "INSTITUTIONAL_DESIGNATION",
        "operating_capacity": BUSINESS_ROLE,
    }


def issue_founder_designation(*, password: str, otp_code: str) -> dict[str, str]:
    """Owner password+existing TOTP proof; issue a non-IAM title once."""
    _require(isinstance(password, str) and bool(password),
             "FOUNDER_PASSWORD_REQUIRED")
    _require(isinstance(otp_code, str) and len(otp_code) == 6
             and otp_code.isdigit(), "FOUNDER_OTP_FORMAT_INVALID")
    client = _require_present(kernel_db.get_client(),
                              "FOUNDER_EXACT_DATABASE_REQUIRED")
    db = _require_present(kernel_db.get_database(),
                          "FOUNDER_EXACT_DATABASE_REQUIRED")
    _require(db.name == "wilsy", "FOUNDER_EXACT_DATABASE_REQUIRED")
    principal_id = _principal_from_source(db)
    registry = get_auth_registry(None)
    user = _require_present(registry.authenticate(EMAIL, password),
                            "FOUNDER_OWNER_PASSWORD_PROOF_DENIED")
    _require(user.id == principal_id
             and user.tenantId == TENANT and user.mfaRegistered is True,
             "FOUNDER_OWNER_PASSWORD_PROOF_DENIED")
    _require(registry.verify_otp(principal_id, otp_code) is True,
             "FOUNDER_OWNER_MFA_PROOF_DENIED")
    credential = db["principal_credentials"].find_one(
        {"principal_id": principal_id, "normalized_email": EMAIL},
        {"_id": 1},
    )
    factor = db["global_principal_mfa_factors"].find_one(
        {"principal_id": principal_id, "status": "ACTIVE"},
        {"_id": 1},
    )
    _require(credential is not None and factor is not None,
             "FOUNDER_GLOBAL_CREDENTIAL_AND_MFA_REQUIRED")
    db[COLLECTION].create_index(
        [("tenant_id", 1), ("principal_id", 1)], unique=True,
        name="institutional_founder_one_principal",
    )
    db[AUDIT].create_index(
        [("tenant_id", 1), ("principal_id", 1), ("decision", 1)],
        unique=True, name="institutional_founder_one_ratification",
    )
    with client.start_session() as session:
        with session.start_transaction():
            _require(_principal_from_source(db, session=session) == principal_id,
                     "FOUNDER_IDENTITY_CHANGED")
            _require(db["principal_credentials"].count_documents(
                {"principal_id": principal_id, "normalized_email": EMAIL},
                limit=2, session=session,
            ) == 1, "FOUNDER_GLOBAL_CREDENTIAL_REQUIRED")
            _require(db["global_principal_mfa_factors"].count_documents(
                {"principal_id": principal_id, "status": "ACTIVE"},
                limit=2, session=session,
            ) == 1, "FOUNDER_GLOBAL_MFA_REQUIRED")
            current = read_founder_designation(
                principal_id=principal_id, tenant_id=TENANT,
                database=db, session=session,
            )
            if current is not None:
                return {"designation": "Founder", "status": "ALREADY_ACTIVE"}
            now = datetime.now(timezone.utc).isoformat()
            value: dict[str, object] = {
                "tenant_id": TENANT,
                "principal_id": principal_id,
                "decision": DECISION,
                "designation": "Founder",
                "business_role": BUSINESS_ROLE,
                "state": "ACTIVE",
                "ratified_at": now,
                "authority_basis": "EXPLICIT_FOUNDER_OPERATOR_DIRECTION_20261120",
                "grants_permissions": False,
            }
            proof = _digest(value)
            db[COLLECTION].insert_one({
                **value, "proof_sha3_512": proof,
            }, session=session)
            db[AUDIT].insert_one({
                "tenant_id": TENANT,
                "principal_id": principal_id,
                "decision": DECISION,
                "proof_sha3_512": proof,
                "event": "FOUNDER_TITLE_RATIFIED",
                "occurred_at": now,
                "grants_permissions": False,
            }, session=session)
    verified = read_founder_designation(
        principal_id=principal_id, tenant_id=TENANT, database=db,
    )
    _require(verified is not None, "FOUNDER_DESIGNATION_READBACK_FAILED")
    return {"designation": "Founder", "status": "ACTIVE"}


def main() -> int:
    print("=== WILSY INSTITUTIONAL FOUNDER DESIGNATION ===")
    connected, _ = kernel_db.connect_db()
    if not connected:
        print("FOUNDER_DESIGNATION=DATABASE_UNAVAILABLE")
        return 2
    password = getpass.getpass("Existing Owner password (hidden): ")
    otp = getpass.getpass("Existing Owner authenticator code (hidden): ")
    try:
        result = issue_founder_designation(password=password, otp_code=otp)
        print("FOUNDER_DESIGNATION=" + result["designation"])
        print("DESIGNATION_STATE=" + result["status"])
        print("OPERATING_CAPACITY=tenant_owner")
        print("IAM_PERMISSIONS=UNCHANGED")
        return 0
    except FounderDesignationRejected as error:
        print("FOUNDER_DESIGNATION=DENIED")
        print("ERROR_CODE=" + str(error))
        return 2
    except Exception as error:
        print("FOUNDER_DESIGNATION=UNAVAILABLE")
        print("FAILURE_CLASS=" + type(error).__name__)
        return 2
    finally:
        password = ""
        otp = ""
        client = kernel_db.get_client()
        if client is not None:
            client.close()


if __name__ == "__main__":
    raise SystemExit(main())

# ARTIFACT: founder_institutional_designation.py
# VERSION: v1.0.2-TYPED-FOUNDER-CURRENTNESS-GUARDS
# AUTHORITY BOUNDARY: non-IAM Founder identity title; no grant
# TENANT POSTURE: exact principal and WILSY tenant with live role checks
# FAIL-CLOSED POSTURE: absent proof, missing factor or authority denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
