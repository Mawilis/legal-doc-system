"""TITLE: WILSY Explicit Canonical-Development Founder Reader Admission.
VERSION: v1.0.0
AUTHORITY: WILSY-IAM-INITIAL-GRANTOR-20261114; direct user-ratified development exception.
EPITOME: Consume one exact development initial admission, without appointing an
administrator, asserting an independent approver, or changing ordinary IAM law.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/founder_development_admission.py
COLLABORATION / OWNERSHIP: Explicit local operator; canonical JWT/AuthRegistry,
tenant, principal, membership, capacity, role and read-decision source owners.
CERTIFICATION / UPDATE DATE: 2026-11-14
CHANGELOG: v1.0.0 introduces a separate operator-only, snapshot-atomic, permanently
consumed development admission; existing disposable and independent grants unchanged.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No endpoint/startup hook, token construction, credential
file/logging, silent repair, session borrowing, wildcard or private key persistence.
TENANT BOUNDARY: Exact WILSYTENANT-4CD2FZ4O and 695e423c9d355c0675c6835d only.
AUTHORITY BOUNDARY: Explicit development initial-admission exception only; evidence
truthfully records no independent approver and no administrator appointment.
TRANSACTION BOUNDARY: Command requires caller-owned snapshot transaction; CLI owns
whole-transaction retries and commit. Currentness is snapshot-bound, not serializable.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from getpass import getpass
from hashlib import sha3_512
import hmac
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

from pymongo import MongoClient, ReadPreference
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.auth.company_document_reader_grant import CompanyDocumentReaderGrant
from tools.eos.auth.jwt_provider import TokenPurpose, verify_access_token
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository, RoleAssignmentNotFoundError
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_authorization_decision_evidence_registry import TenantAuthorizationDecisionEvidenceRegistryError
from tools.eos.kernel.db import resolve_mongo_uri
from tools.eos.saas.auth.auth_registry import AuthRegistry
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry

VERSION = "v1.0.0"
TENANT = "WILSYTENANT-4CD2FZ4O"
PRINCIPAL = "695e423c9d355c0675c6835d"
DECISION = "WILSY-IAM-INITIAL-GRANTOR-20261114"
ROLE = "COMPANY_DOCUMENT_READER"
PERMISSION = "company_operating_document:read"
COLLECTION = "founder_development_admission_evidence"
SCHEMA = "WILSY-CANONICAL-DEVELOPMENT-FOUNDER-ADMISSION/V1"
GOVERNANCE_PATH = Path(__file__).resolve().parents[3] / "docs/governance/founder-canonical-development-admission-2026-11-14.md"
_ENV_KEYS = ("ENV", "WILSY_ENV", "WILSY_EOS_ENV", "NODE_ENV", "APP_ENV", "ENVIRONMENT", "VERCEL_ENV")


class FounderAdmissionError(RuntimeError):
    """Structured, content-free denial; caller must abort its transaction."""

    def __init__(self, code: str) -> None:
        """Retain only stable code/message; never credentials or driver detail."""
        self.code = code
        self.message = "Founder development admission was denied or could not be verified."
        super().__init__(code)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(value: Any) -> str:
    return sha3_512(_canonical(value).encode("ascii")).hexdigest()


def _revision(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise FounderAdmissionError("FOUNDER_ADMISSION_REVISION_INVALID")
    return value


def _controls() -> None:
    if (any(os.getenv(key, "").strip().lower() in {"production", "prod"} for key in _ENV_KEYS)
            or any(os.getenv(key) != "development" for key in ("ENV", "WILSY_ENV", "WILSY_EOS_ENV"))
            or os.getenv("WILSY_FOUNDER_CANONICAL_ADMISSION") != DECISION):
        raise FounderAdmissionError("FOUNDER_ADMISSION_DEVELOPMENT_CONTROLS_REQUIRED")


def source_digest() -> str:
    """Fingerprint exact operator source bytes; no signing or authority is implied."""
    return sha3_512(Path(__file__).read_bytes()).hexdigest()


def governance_digest() -> str:
    """Fingerprint the exact ratified development decision record, never an approver."""
    return sha3_512(GOVERNANCE_PATH.read_bytes()).hexdigest()


def database_target(database: Any) -> str:
    """Read non-secret replica topology and fingerprint exact database/member scope.

    Platform metadata is explicitly operator-scoped. No credentials, writes,
    transaction ownership, inferred development classification or IAM are created.
    """
    hello = database.client.admin.command("hello")
    if not hello.get("isWritablePrimary") or not hello.get("setName") or not hello.get("hosts"):
        raise FounderAdmissionError("FOUNDER_ADMISSION_REPLICA_PRIMARY_REQUIRED")
    return _digest({"database": database.name, "replica": hello["setName"], "hosts": sorted(hello["hosts"])})


class _TenantReads:
    def __init__(self, database: Any, session: Any) -> None:
        self.database, self.session = database, session

    def resolve_canonical_tenant(self, reference: str, **kwargs: Any) -> Any:
        # Bind even legacy internal calls that omit an optional session to this
        # command's caller-owned transaction. Source hydration remains unchanged.
        return TenantRegistry.resolve_canonical_tenant(reference, collection=self.database["tenants"],
            session=self.session, allow_alias=kwargs.get("allow_alias", False))


class _AuthenticationReads(AuthRegistry):
    def __init__(self, database: Any, session: Any) -> None:
        super().__init__(tenant_registry=_TenantReads(database, session))  # type: ignore[arg-type]
        self.database = database

    def _collection(self, collection_name: str) -> Any:
        return self.database[collection_name]


class FounderDevelopmentAdmission:
    """One explicit operator contract over canonical authorities and one consumption record.

    No ordinary IAM grant is impersonated. Only the fixed singleton reader role
    is inserted. There is no route, login hook, automatic provisioning or regrant.
    Every raised error requires transaction abort; no partial command is retryable.
    """

    def __init__(self, database: Any, *, target_fingerprint: str, decision: str,
                 approval_fingerprint: str) -> None:
        """Bind explicit operator decision and exact development database preflight.

        Configuration is request admission only, never Founder authentication.
        Replica metadata is read before the business transaction; binding expires
        after sixty seconds. No data, index or transaction is created here.
        """
        _controls()
        if decision != DECISION or not hmac.compare_digest(approval_fingerprint, governance_digest()):
            raise FounderAdmissionError("FOUNDER_ADMISSION_DECISION_BINDING_INVALID")
        if not hmac.compare_digest(target_fingerprint, database_target(database)):
            raise FounderAdmissionError("FOUNDER_ADMISSION_TARGET_MISMATCH")
        if ROLE_PERMISSIONS_MAP.get(ROLE) != [PERMISSION]:
            raise FounderAdmissionError("FOUNDER_ADMISSION_ROLE_PERMISSION_DRIFT")
        self.db, self.target = database, target_fingerprint
        self.approval, self.source = approval_fingerprint, source_digest()
        self.preflight_at = time.monotonic()
        self.command = CompanyDocumentReaderGrant(database)

    def _guard(self, session: Any = None) -> None:
        _controls()
        if not 0 <= time.monotonic() - self.preflight_at <= 60:
            raise FounderAdmissionError("FOUNDER_ADMISSION_PREFLIGHT_EXPIRED")
        if session is not None and (getattr(session, "in_transaction", False) is not True
                                    or getattr(session, "client", None) is not self.db.client):
            raise FounderAdmissionError("FOUNDER_ADMISSION_CALLER_TRANSACTION_REQUIRED")
        if ROLE_PERMISSIONS_MAP.get(ROLE) != [PERMISSION]:
            raise FounderAdmissionError("FOUNDER_ADMISSION_ROLE_PERMISSION_DRIFT")

    def provision_evidence_indexes(self) -> None:
        """Explicit operator DDL for the new consumption evidence only, before transaction.

        Existing role/decision indexes are validated, never changed. Canonical
        CLI invokes this only after isolated certification and fresh authentication.
        No login, API or startup path calls it.
        """
        self._guard()
        self.command.require_indexes()
        self.db[COLLECTION].create_index([("tenant_id", 1), ("decision_id", 1)], unique=True,
                                         name="founder_development_decision_once")
        self.db[COLLECTION].create_index([("tenant_id", 1), ("idempotency_key", 1)], unique=True,
                                         name="founder_development_command_once")

    def _indexes(self) -> None:
        self.command.require_indexes()
        indexes = list(self.db[COLLECTION].index_information().values())
        for fields in (("tenant_id", "decision_id"), ("tenant_id", "idempotency_key")):
            if not any(tuple(key for key, _ in item.get("key", ())) == fields and item.get("unique") is True
                       and not item.get("sparse") and not item.get("partialFilterExpression")
                       and "expireAfterSeconds" not in item
                       and item.get("collation", {}).get("locale", "simple") == "simple" for item in indexes):
                raise FounderAdmissionError("FOUNDER_ADMISSION_INDEX_REQUIRED")

    def authenticate(self, access_token: str, *, session: Any, expected_principal_revision: int,
                     expected_membership_revision: int, expected_capacity_revision: int,
                     expected_admin_revision: int) -> dict[str, Any]:
        """Freshly validate the existing signed ACCESS session and durable authority.

        Canonical JWT verification and AuthRegistry retain authentication truth;
        this operator contract adds exact scope and revision restrictions. Every
        persistence read uses this caller transaction. No credential is issued,
        stored, logged or treated as an administrative approval.
        """
        self._guard(session)
        if session is None:
            raise FounderAdmissionError("FOUNDER_ADMISSION_CALLER_TRANSACTION_REQUIRED")
        claims = verify_access_token(access_token)
        if (not claims or claims.get("token_purpose") != TokenPurpose.ACCESS.value
                or claims.get("identity_id") != PRINCIPAL or claims.get("tenant_id") != TENANT
                or claims.get("principal_scope") not in (None, "TENANT")
                or not isinstance(claims.get("session_reference"), str)
                or not claims["session_reference"].startswith("WILSYSESSION-")):
            raise FounderAdmissionError("FOUNDER_ADMISSION_CURRENT_ACCESS_SESSION_REQUIRED")
        token_revision = _revision(claims.get("credential_revision"))
        auth = _AuthenticationReads(self.db, session)
        if (auth.get_credential_revision(TENANT, PRINCIPAL, session=session) != token_revision
                or not auth.is_session_current(TENANT, PRINCIPAL, claims["session_reference"], session=session)):
            raise FounderAdmissionError("FOUNDER_ADMISSION_SESSION_NOT_CURRENT")
        principal = self.command.principals.resolve(PRINCIPAL, session=session)
        membership = self.command.memberships.resolve(PRINCIPAL, TENANT, session=session)
        capacity = TenantBusinessRoleRepository.resolve_business_role(PRINCIPAL, TENANT, "tenant_owner",
                    self.db["tenant_business_roles"], session=session)
        admin = self.command.reads.resolve(PRINCIPAL, TENANT, "ENTERPRISE_ADMIN", session=session)
        for value, expected in ((principal, expected_principal_revision), (membership, expected_membership_revision),
                                (capacity, expected_capacity_revision), (admin, expected_admin_revision)):
            if value.status.value != "ACTIVE" or value.revision != _revision(expected):
                raise FounderAdmissionError("FOUNDER_ADMISSION_AUTHORITY_REVISION_DENIED")
        return {"session_fingerprint": sha3_512(claims["session_reference"].encode()).hexdigest(),
                "credential_revision": token_revision, "access_expires_at": claims["exp"]}

    def execute(self, *, access_token: str, tenant_id: str, principal_id: str, idempotency_key: str,
                expected_principal_revision: int, expected_membership_revision: int,
                expected_capacity_revision: int, expected_admin_revision: int, session: Any) -> dict[str, Any]:
        """Consume the exact development decision and persist reader/evidence atomically.

        Same-command repeat denies ALREADY_CONSUMED; divergent repeat denies
        IDEMPOTENCY_CONFLICT. A revoked/deleted assignment never makes the decision
        reusable. Caller must abort on error and owns whole-transaction retry/commit.
        This is explicitly a ratified development initial-admission exception,
        not an independently approved tenant-admin role grant or financial authority.
        """
        self._guard(session)
        if tenant_id != TENANT or principal_id != PRINCIPAL:
            raise FounderAdmissionError("FOUNDER_ADMISSION_EXACT_SCOPE_REQUIRED")
        if (not isinstance(idempotency_key, str) or not idempotency_key or len(idempotency_key) > 128
                or idempotency_key != idempotency_key.strip()):
            raise FounderAdmissionError("FOUNDER_ADMISSION_IDEMPOTENCY_INVALID")
        self._indexes()
        revisions = {"principal": _revision(expected_principal_revision), "membership": _revision(expected_membership_revision),
                     "capacity": _revision(expected_capacity_revision), "existing_admin": _revision(expected_admin_revision)}
        observed = self.authenticate(access_token, session=session,
            expected_principal_revision=expected_principal_revision, expected_membership_revision=expected_membership_revision,
            expected_capacity_revision=expected_capacity_revision, expected_admin_revision=expected_admin_revision)
        intent = {"decision_id": DECISION, "tenant_id": TENANT, "principal_id": PRINCIPAL, "role_id": ROLE,
                  "permissions": [PERMISSION], "idempotency_key": idempotency_key, "expected_revisions": revisions,
                  "target_fingerprint": self.target, "approval_fingerprint": self.approval, "source_fingerprint": self.source}
        command_fingerprint = _digest(intent)
        try:
            prior = self.db[COLLECTION].find_one({"tenant_id": TENANT, "decision_id": DECISION}, session=session)
            if prior is not None:
                prior = self._hydrate(prior)
                raise FounderAdmissionError("FOUNDER_ADMISSION_ALREADY_CONSUMED" if
                    prior["command_fingerprint"] == command_fingerprint else "FOUNDER_ADMISSION_IDEMPOTENCY_CONFLICT")
            try:
                self.command.reads.resolve(PRINCIPAL, TENANT, ROLE, session=session)
            except RoleAssignmentNotFoundError:
                pass
            else:
                raise FounderAdmissionError("FOUNDER_ADMISSION_ASSIGNMENT_ALREADY_EXISTS")
            assignment = RoleAssignmentAuthority(PRINCIPAL, TENANT, ROLE, RoleAssignmentStatus.ACTIVE, 0)
            RoleAssignmentRepository.insert(assignment, self.db["role_assignments"], session=session)
            read_evidence = self.command.evidence.issue(tenant_id=TENANT, principal_id=PRINCIPAL,
                operation="company_operating_document_read", permission=PERMISSION,
                subject_reference="canonical-development-founder-admission:" + DECISION,
                subject_evidence_fingerprint=command_fingerprint,
                idempotency_key="founder-canonical-development:" + idempotency_key, session=session)
            record = {"schema": SCHEMA, "contract_version": VERSION, **intent,
                "command_fingerprint": command_fingerprint,
                "authority_basis": "EXPLICIT_OPERATOR_RATIFIED_DEVELOPMENT_INITIAL_ADMISSION",
                "independent_approver": None, "ordinary_independent_grant": False,
                "administrative_grantor_appointed": False, "assignment_revision": 0,
                "authenticated_session_fingerprint": observed["session_fingerprint"],
                "credential_revision": observed["credential_revision"],
                "read_decision_id": read_evidence.authorization_decision_id,
                "read_decision_fingerprint": read_evidence.authorization_evidence_fingerprint,
                "consumed_at": datetime.now(timezone.utc).isoformat(), "consumed": True}
            record["evidence_fingerprint"] = _digest(record)
            self.db[COLLECTION].insert_one(record, session=session)
            if time.time() >= observed["access_expires_at"]:
                raise FounderAdmissionError("FOUNDER_ADMISSION_ACCESS_EXPIRED")
            return self.readback(session=session)
        except FounderAdmissionError:
            raise
        except (PyMongoError, RuntimeError, ValueError, TypeError) as error:
            cause: BaseException | None = error
            while cause is not None:
                if isinstance(cause, PyMongoError) and cause.has_error_label("TransientTransactionError"):
                    raise cause
                if isinstance(cause, DuplicateKeyError):
                    raise FounderAdmissionError("FOUNDER_ADMISSION_CONCURRENT_CONSUMPTION_DENIED") from error
                cause = cause.__cause__
            raise FounderAdmissionError("FOUNDER_ADMISSION_PERSISTENCE_OR_EVIDENCE_FAILURE") from error

    @staticmethod
    def _hydrate(document: dict[str, Any]) -> dict[str, Any]:
        body = dict(document)
        body.pop("_id", None)
        fingerprint = body.pop("evidence_fingerprint", None)
        if (not isinstance(fingerprint, str) or not hmac.compare_digest(fingerprint, _digest(body))
                or body.get("schema") != SCHEMA or body.get("tenant_id") != TENANT
                or body.get("principal_id") != PRINCIPAL or body.get("decision_id") != DECISION
                or body.get("role_id") != ROLE or body.get("permissions") != [PERMISSION]
                or body.get("independent_approver") is not None or body.get("ordinary_independent_grant") is not False
                or body.get("administrative_grantor_appointed") is not False or body.get("consumed") is not True):
            raise FounderAdmissionError("FOUNDER_ADMISSION_EVIDENCE_INVALID")
        return {**body, "evidence_fingerprint": fingerprint}

    def readback(self, *, session: Any = None) -> dict[str, Any]:
        """Strictly verify immutable governance and canonical read-decision correlation.

        Independently bind a fresh database/client for post-commit inspection.
        Assignment status is reported as current observation, not inferred from
        historical evidence. This method grants nothing and performs no writes.
        """
        record = self.db[COLLECTION].find_one({"tenant_id": TENANT, "decision_id": DECISION}, session=session)
        if record is None:
            raise FounderAdmissionError("FOUNDER_ADMISSION_EVIDENCE_ABSENT")
        record = self._hydrate(record)
        read_evidence = self.command.evidence.get(tenant_id=TENANT,
            authorization_decision_id=record["read_decision_id"], session=session)
        if (read_evidence.authorization_evidence_fingerprint != record["read_decision_fingerprint"]
                or read_evidence.subject_evidence_fingerprint != record["command_fingerprint"]
                or read_evidence.principal_id != PRINCIPAL or read_evidence.permission != PERMISSION
                or read_evidence.authorization_role != ROLE):
            raise FounderAdmissionError("FOUNDER_ADMISSION_EVIDENCE_CORRELATION_INVALID")
        try:
            assignment = self.command.reads.resolve(PRINCIPAL, TENANT, ROLE, session=session)
            status, revision = assignment.status.value, assignment.revision
        except RoleAssignmentNotFoundError:
            status, revision = "ABSENT", None
        return {"schema": SCHEMA, "tenant_id": TENANT, "principal_id": PRINCIPAL,
                "decision_id": DECISION, "role_id": ROLE, "permission": PERMISSION,
                "assignment_status": status, "assignment_revision": revision,
                "evidence_fingerprint": record["evidence_fingerprint"],
                "read_decision_id": record["read_decision_id"],
                "read_decision_fingerprint": record["read_decision_fingerprint"],
                "independent_approver": None, "ordinary_independent_grant": False,
                "administrative_grantor_appointed": False, "consumed": True}


def _main() -> int:
    parser = argparse.ArgumentParser(description="Explicit once-off canonical-development Founder reader admission")
    parser.add_argument("--execute-development-decision", required=True, choices=[DECISION])
    parser.add_argument("--target-fingerprint", required=True)
    parser.add_argument("--approval-fingerprint", required=True)
    parser.add_argument("--certification-evidence", required=True)
    parser.add_argument("--certification-fingerprint", required=True)
    parser.add_argument("--idempotency-key", required=True)
    for name in ("principal", "membership", "capacity", "admin"):
        parser.add_argument("--expected-" + name + "-revision", required=True, type=int)
    parser.add_argument("--token-stdin", action="store_true")
    args = parser.parse_args()
    try:
        _controls()
        raw = Path(args.certification_evidence).read_bytes()
        certificate = json.loads(raw)
        if (not hmac.compare_digest(sha3_512(raw).hexdigest(), args.certification_fingerprint)
                or certificate.get("schema") != "WILSY-FOUNDER-ADMISSION-ISOLATED-CERTIFICATE/V1"
                or certificate.get("status") != "PASSED" or certificate.get("failures") != 0
                or certificate.get("skipped") != 0 or certificate.get("source_fingerprint") != source_digest()
                or certificate.get("governance_fingerprint") != governance_digest()
                or certificate.get("isolated_replica_set") != "wilsyFounderAdmissionCertRS"):
            raise FounderAdmissionError("FOUNDER_ADMISSION_ISOLATED_CERTIFICATION_REQUIRED")
        token = sys.stdin.readline(8193).strip() if args.token_stdin else getpass("Existing Founder ACCESS bearer: ").strip()
        if not token or len(token) > 8192:
            raise FounderAdmissionError("FOUNDER_ADMISSION_CURRENT_ACCESS_SESSION_REQUIRED")
        uri = resolve_mongo_uri()
        if not uri:
            raise FounderAdmissionError("FOUNDER_ADMISSION_CANONICAL_DATABASE_UNAVAILABLE")
        with MongoClient(uri, tz_aware=True, serverSelectionTimeoutMS=8000) as client:
            database = client.get_default_database()
            command = FounderDevelopmentAdmission(database, target_fingerprint=args.target_fingerprint,
                decision=args.execute_development_decision, approval_fingerprint=args.approval_fingerprint)
            revisions = {"expected_" + name + "_revision": getattr(args, "expected_" + name + "_revision")
                         for name in ("principal", "membership", "capacity", "admin")}
            def authenticate(session: Any) -> Any:
                return command.authenticate(token, session=session, **revisions)
            with client.start_session() as session:
                session.with_transaction(authenticate, read_concern=ReadConcern("snapshot"),
                    read_preference=ReadPreference.PRIMARY, write_concern=WriteConcern(w="majority", j=True))
            command.provision_evidence_indexes()
            command._indexes()
            def execute(session: Any) -> Any:
                return command.execute(access_token=token, tenant_id=TENANT, principal_id=PRINCIPAL,
                    idempotency_key=args.idempotency_key, session=session, **revisions)
            with client.start_session() as session:
                result = session.with_transaction(execute, read_concern=ReadConcern("snapshot"),
                    read_preference=ReadPreference.PRIMARY, write_concern=WriteConcern(w="majority", j=True))
            print(json.dumps({"status": "COMMITTED", **result}))
        return 0
    except (FounderAdmissionError, PyMongoError, RuntimeError, ValueError, OSError) as error:
        code = error.code if isinstance(error, FounderAdmissionError) else "FOUNDER_ADMISSION_SOURCE_UNAVAILABLE"
        print(json.dumps({"error": code, "message": "Founder development admission did not report a verified commit."}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(_main())

# ARTIFACT: founder_development_admission.py
# VERSION: v1.0.0
# AUTHORITY BOUNDARY: Exact operator-ratified development initial admission; no independent approver asserted
# TENANT POSTURE: One existing WILSY tenant and principal; no identity or administrator creation
# FAIL-CLOSED POSTURE: Production, absent controls, scope/revision/session/evidence failures and all re-execution deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
