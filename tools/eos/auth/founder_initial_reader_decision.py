"""
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS remains exclusive.
TITLE: WILSY OS Production Founder Initial Company-Reader Decision.
VERSION: v1.1.0-PRODUCTION-INITIAL-READER-CONSUMPTION
AUTHORITY: WILSY EOS Core Governance; independently verified issuer authority
           remains external and is never selected by this artifact.
EPITOME: Verify and atomically consume one independently governed, exact-scope
         production decision for the existing WILSY Founder reader assignment.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/founder_initial_reader_decision.py
COLLABORATION / OWNERSHIP: External institutional authority owns issuer,
    representation mandate, key custody and decision revocation truth. AuthRegistry
    owns session currentness. Canonical IAM repositories own all local state.
CERTIFICATION / UPDATE DATE: 2026-11-15
CHANGELOG:
    v1.1.0-PRODUCTION-INITIAL-READER-CONSUMPTION adds the operator-only,
    caller-transaction-bound consumer. It reuses the canonical role assignment
    and tenant authorization-decision evidence registry as the one immutable
    consumption record; it adds no HTTP route, login/startup hook, authority
    store, trust-root registry, role authority, or development bypass.
    v1.0.0-PRODUCTION-INITIAL-READER-DECISION introduced pure exact-scope
    Ed25519 decision verification without command wiring or persistence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque references and SHA3-512 fingerprints only.
    No private key, corporate document, bearer, session reference, signature,
    identity attribute or driver exception is persisted or logged here.
TENANT BOUNDARY: Consumption is confined to the exact canonical WILSY tenant
    and its existing Founder principal; every repository operation is scoped.
AUTHORITY BOUNDARY: A fresh independent authority verification is mandatory.
    Founder declarations, G64 integrity hashes, existing IAM, browser sessions,
    and environment values are never substitutes for issuer/mandate authority.
TRANSACTION BOUNDARY: The caller owns the full snapshot/majority+journal
    transaction and retries. This file never opens, commits, aborts or retries.
FINANCIAL AUTHORITY BOUNDARY: No financial authority; Kennel EOS exclusively.
FAIL-CLOSED POSTURE: Authority/key/revocation uncertainty, invalid signature or
    scope, stale session/revision, replay, existing assignment, missing indexes,
    and any persistence uncertainty deny without a partial durable mutation.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import json
import re
from typing import Any, Final, Protocol, cast

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.company_document_reader_grant import CompanyDocumentReaderGrant
from tools.eos.auth.jwt_provider import TokenPurpose, verify_access_token
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentAlreadyExistsError, RoleAssignmentNotFoundError,
    RoleAssignmentRepository, RoleAssignmentRepositoryError,
)
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceConflictError,
    TenantAuthorizationDecisionEvidenceRegistryError,
)
from tools.eos.auth.tenant_authority_policy import ELIGIBLE, tenant_role_operation_eligibility
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleRepository, TenantBusinessRoleRepositoryError,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepositoryError
from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID
from tools.eos.saas.auth.auth_registry import AuthRegistry
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry

VERSION: Final[str] = "v1.1.0-PRODUCTION-INITIAL-READER-CONSUMPTION"
DECISION_REFERENCE: Final[str] = "WILSY-IAM-INITIAL-GRANTOR-20261114"
FOUNDER_PRINCIPAL: Final[str] = "695e423c9d355c0675c6835d"
PURPOSE: Final[str] = "INITIAL_IAM_READER_ADMISSION"
ROLE: Final[str] = "COMPANY_DOCUMENT_READER"
PERMISSION: Final[str] = "company_operating_document:read"
OPERATION: Final[str] = "company_operating_document_read"
SCHEMA: Final[str] = "WILSY-PRODUCTION-INITIAL-READER-ADMISSION/V1"
_DOMAIN: Final[bytes] = b"WILSY:EOS:INITIAL-COMPANY-READER:PRODUCTION:v1\x00"
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,255}\Z")
_HASH = re.compile(r"[0-9a-f]{128}\Z")


class InitialReaderDecisionDenied(RuntimeError):
    """Stable content-free decision/admission denial; never mutates by itself."""
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class InitialReaderVerdict(StrEnum):
    """Closed verifier result; no partial successful decision exists."""
    VERIFIED = "VERIFIED"


def _identity(value: object) -> str:
    """Validate one bounded opaque identifier without normalization or repair."""
    if type(value) is not str or _ID.fullmatch(value) is None:
        raise InitialReaderDecisionDenied("INITIAL_READER_DECISION_IDENTIFIER_INVALID")
    return value


def _fingerprint(value: object) -> str:
    """Require a complete lower-case SHA3-512 fingerprint."""
    if type(value) is not str or _HASH.fullmatch(value) is None:
        raise InitialReaderDecisionDenied("INITIAL_READER_DECISION_FINGERPRINT_INVALID")
    return value


def _utc(value: object) -> datetime:
    """Require an aware instant; host-local time is never accepted as authority."""
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise InitialReaderDecisionDenied("INITIAL_READER_DECISION_TIME_INVALID")
    return value.astimezone(timezone.utc)


def _revision(value: object) -> int:
    """Require one non-negative canonical source revision without coercion."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_REVISION_INVALID")
    return value


def _active_transaction(session: Any) -> None:
    """Require the caller-owned active Mongo transaction before any source read."""
    marker = getattr(session, "in_transaction", None) if session is not None else None
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError) as error:
        raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_TRANSACTION_REQUIRED") from error
    if active is not True:
        raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_TRANSACTION_REQUIRED")


def _validate_decision_fields(value: object) -> None:
    """Revalidate every signed field at use time, including hostile post-init mutation."""
    if type(value) is not InitialReaderDecision:
        raise InitialReaderDecisionDenied("INITIAL_READER_DECISION_REQUIRED")
    for name in ("reference", "tenant_id", "recipient_principal_id", "issuer_id",
                 "issuer_appointment_reference", "trust_root_reference", "key_id",
                 "legal_entity_reference", "mandate_evidence_reference", "revocation_reference"):
        _identity(getattr(value, name))
    for name in ("issuer_appointment_fingerprint", "trust_root_fingerprint",
                 "mandate_evidence_fingerprint", "decision_evidence_fingerprint"):
        _fingerprint(getattr(value, name))
    if type(value.key_revision) is not int or value.key_revision < 1:
        raise InitialReaderDecisionDenied("INITIAL_READER_DECISION_KEY_REVISION_INVALID")
    if (value.operation, value.role, value.permission) != (PURPOSE, ROLE, PERMISSION):
        raise InitialReaderDecisionDenied("INITIAL_READER_DECISION_SCOPE_INVALID")
    if _utc(value.issued_at) > _utc(value.effective_until) or _utc(value.effective_from) >= _utc(value.effective_until):
        raise InitialReaderDecisionDenied("INITIAL_READER_DECISION_INTERVAL_INVALID")


@dataclass(frozen=True, slots=True)
class InitialReaderDecision:
    """Signed exact-scope claims, never independently verified authority by construction."""
    reference: str
    tenant_id: str
    recipient_principal_id: str
    issuer_id: str
    issuer_appointment_reference: str
    issuer_appointment_fingerprint: str
    trust_root_reference: str
    trust_root_fingerprint: str
    key_id: str
    key_revision: int
    legal_entity_reference: str
    mandate_evidence_reference: str
    mandate_evidence_fingerprint: str
    decision_evidence_fingerprint: str
    issued_at: datetime
    effective_from: datetime
    effective_until: datetime
    revocation_reference: str
    operation: str = PURPOSE
    role: str = ROLE
    permission: str = PERMISSION

    def __post_init__(self) -> None:
        """Fail closed before canonical signing bytes or authority lookups exist."""
        _validate_decision_fields(self)


@dataclass(frozen=True, slots=True)
class InitialReaderDecisionEnvelope:
    """Transport signature envelope; signature validity is not authority approval."""
    decision: InitialReaderDecision
    algorithm: str
    signature_hex: str


@dataclass(frozen=True, slots=True)
class InitialReaderVerificationRequest:
    """Verified caller coordinates; caller scope is never corporate evidence."""
    tenant_id: str
    recipient_principal_id: str
    evaluated_at: datetime

    def __post_init__(self) -> None:
        """Reject malformed scope before an institutional source is invoked."""
        _identity(self.tenant_id)
        _identity(self.recipient_principal_id)
        _utc(self.evaluated_at)


class InitialReaderInstitutionalAuthority(Protocol):
    """Read-only external authority for issuer, mandate, key, and revocation.

    A concrete production adapter remains a separately ratified dependency. The
    Issue #300 root registry is deliberately ownership-scoped, so this protocol
    must not be satisfied by reusing it without a separately approved scope.
    """
    def verify_current_issuer_and_mandate(self, decision: InitialReaderDecision, evaluated_at: datetime) -> bool:
        """Return true only for independently verified, fresh, exact-scope authority."""
        ...
    def verify_current_key(self, decision: InitialReaderDecision, evaluated_at: datetime) -> Ed25519PublicKey:
        """Return only an approved current public key of exact purpose/revision."""
        ...
    def is_decision_revoked(self, decision: InitialReaderDecision, evaluated_at: datetime) -> bool:
        """Return current revocation truth; uncertainty/outage raises and denies."""
        ...


@dataclass(frozen=True, slots=True, init=False)
class VerifiedInitialReaderDecision:
    """Read-only verification receipt; it is never an IAM-grant capability."""
    reference: str
    tenant_id: str
    recipient_principal_id: str
    signed_payload_fingerprint: str
    verified_at: datetime
    decision_expires_at: datetime
    verdict: InitialReaderVerdict

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Prevent caller-supplied fabrication of a positive verification receipt."""
        del args, kwargs
        raise InitialReaderDecisionDenied("INITIAL_READER_RECEIPT_CONSTRUCTOR_DISABLED")


def canonical_initial_reader_message(decision: InitialReaderDecision) -> bytes:
    """Return domain-separated deterministic bytes covering every decision field."""
    _validate_decision_fields(decision)
    body = {name: (getattr(decision, name).astimezone(timezone.utc).isoformat()
                   if name in {"issued_at", "effective_from", "effective_until"}
                   else getattr(decision, name)) for name in decision.__dataclass_fields__}
    return _DOMAIN + json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def verify_initial_reader_decision(request: InitialReaderVerificationRequest, envelope: InitialReaderDecisionEnvelope,
                                   institutional_authority: InitialReaderInstitutionalAuthority) -> VerifiedInitialReaderDecision:
    """Verify one current independent decision without IAM, consumption, or persistence writes."""
    if type(request) is not InitialReaderVerificationRequest:
        raise InitialReaderDecisionDenied("INITIAL_READER_VERIFICATION_REQUEST_REQUIRED")
    if type(envelope) is not InitialReaderDecisionEnvelope or type(envelope.decision) is not InitialReaderDecision:
        raise InitialReaderDecisionDenied("INITIAL_READER_DECISION_ENVELOPE_REQUIRED")
    if institutional_authority is None:
        raise InitialReaderDecisionDenied("INITIAL_READER_INSTITUTIONAL_AUTHORITY_UNAVAILABLE")
    decision, instant = envelope.decision, _utc(request.evaluated_at)
    _validate_decision_fields(decision)
    if (request.tenant_id, request.recipient_principal_id) != (decision.tenant_id, decision.recipient_principal_id):
        raise InitialReaderDecisionDenied("INITIAL_READER_DECISION_SCOPE_MISMATCH")
    if not (_utc(decision.issued_at) <= instant and _utc(decision.effective_from) <= instant < _utc(decision.effective_until)):
        raise InitialReaderDecisionDenied("INITIAL_READER_DECISION_NOT_CURRENT")
    if envelope.algorithm != "Ed25519":
        raise InitialReaderDecisionDenied("INITIAL_READER_SIGNATURE_ALGORITHM_UNSUPPORTED")
    try:
        signature = bytes.fromhex(envelope.signature_hex)
    except (TypeError, ValueError) as error:
        raise InitialReaderDecisionDenied("INITIAL_READER_SIGNATURE_INVALID") from error
    if len(signature) != 64:
        raise InitialReaderDecisionDenied("INITIAL_READER_SIGNATURE_INVALID")
    try:
        authorized = institutional_authority.verify_current_issuer_and_mandate(decision, instant)
        public_key = institutional_authority.verify_current_key(decision, instant)
        revoked = institutional_authority.is_decision_revoked(decision, instant)
    except InitialReaderDecisionDenied:
        raise
    except Exception as error:
        raise InitialReaderDecisionDenied("INITIAL_READER_INSTITUTIONAL_AUTHORITY_UNAVAILABLE") from error
    if authorized is not True or not isinstance(public_key, Ed25519PublicKey) or type(revoked) is not bool:
        raise InitialReaderDecisionDenied("INITIAL_READER_INSTITUTIONAL_AUTHORITY_UNVERIFIED")
    if revoked:
        raise InitialReaderDecisionDenied("INITIAL_READER_DECISION_REVOKED")
    message = canonical_initial_reader_message(decision)
    try:
        public_key.verify(signature, message)
    except InvalidSignature as error:
        raise InitialReaderDecisionDenied("INITIAL_READER_SIGNATURE_INVALID") from error
    value = object.__new__(VerifiedInitialReaderDecision)
    for name, item in {"reference": decision.reference, "tenant_id": decision.tenant_id,
                       "recipient_principal_id": decision.recipient_principal_id,
                       "signed_payload_fingerprint": sha3_512(message + signature).hexdigest(),
                       "verified_at": instant, "decision_expires_at": _utc(decision.effective_until),
                       "verdict": InitialReaderVerdict.VERIFIED}.items():
        object.__setattr__(value, name, item)
    return value


class _TenantReads:
    """Bind the existing AuthRegistry to the caller's canonical database/session."""
    def __init__(self, database: Any, session: Any) -> None:
        self.database, self.session = database, session
    def resolve_canonical_tenant(self, reference: str, **kwargs: Any) -> Any:
        """Resolve one exact tenant without opening a connection or transaction."""
        return TenantRegistry.resolve_canonical_tenant(reference, collection=self.database["tenants"],
            session=self.session, allow_alias=kwargs.get("allow_alias", False))


class _AdmissionAuthRegistry(AuthRegistry):
    """Use canonical AuthRegistry currentness against the caller-owned Mongo view."""
    def __init__(self, database: Any, session: Any) -> None:
        super().__init__(tenant_registry=cast(Any, _TenantReads(database, session)))
        self.database = database
    def _collection(self, collection_name: str) -> Any:
        """Return a canonical auth collection; no second store or DDL exists."""
        return self.database[collection_name]


class ProductionInitialReaderAdmission:
    """Operator-only atomic consumer for the one exact Founder reader decision.

    This path is independent of the development-only admission and normal IAM
    delegation. It deliberately has no router, CLI, startup registration, login
    hook, or environment bypass. The caller must inject the separate authority
    adapter and own the transaction enclosing ``execute``.
    """
    def __init__(self, database: Any, institutional_authority: InitialReaderInstitutionalAuthority) -> None:
        """Bind existing IAM/evidence source owners and the external verifier without I/O."""
        if database is None or institutional_authority is None:
            raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_DEPENDENCIES_REQUIRED")
        self.database, self.authority = database, institutional_authority
        self.reader = CompanyDocumentReaderGrant(database)

    def require_indexes(self) -> None:
        """Inspect existing role/evidence arbitration indexes; runtime never provisions DDL."""
        try:
            self.reader.require_indexes()
        except Exception as error:
            raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_INDEX_REQUIRED") from error

    @staticmethod
    def _consumption_key(reference: str) -> str:
        """Return a bounded deterministic key that consumes one opaque decision reference."""
        return "production-initial-reader:" + sha3_512(reference.encode("utf-8")).hexdigest()

    @staticmethod
    def _subject(fingerprint: str) -> str:
        """Bind consumption evidence to the verified signed payload, without raw documents."""
        return "production-initial-reader:v1:" + _fingerprint(fingerprint)

    def _authenticate(self, access_token: str, request: InitialReaderVerificationRequest,
                      expected_principal_revision: int, expected_membership_revision: int,
                      expected_capacity_revision: int, expected_admin_revision: int, session: Any) -> str:
        """Recheck ACCESS/session and immutable IAM prerequisites in the active transaction."""
        if not isinstance(access_token, str) or not access_token or len(access_token) > 8192:
            raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_CURRENT_ACCESS_REQUIRED")
        claims = verify_access_token(access_token)
        if (not claims or claims.get("token_purpose") != TokenPurpose.ACCESS.value
                or claims.get("identity_id") != request.recipient_principal_id
                or claims.get("tenant_id") != request.tenant_id
                or claims.get("principal_scope") not in (None, "TENANT", "GLOBAL")
                or not isinstance(claims.get("session_reference"), str)
                or not claims["session_reference"].startswith("WILSYSESSION-")):
            raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_CURRENT_ACCESS_REQUIRED")
        try:
            auth = _AdmissionAuthRegistry(self.database, session)
            if (auth.get_credential_revision(request.tenant_id, request.recipient_principal_id, session=session) != _revision(claims.get("credential_revision"))
                    or auth.is_session_current(request.tenant_id, request.recipient_principal_id, claims["session_reference"], session=session) is not True):
                raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_SESSION_NOT_CURRENT")
            principal = self.reader.principals.resolve(request.recipient_principal_id, session=session)
            membership = self.reader.memberships.resolve(request.recipient_principal_id, request.tenant_id, session=session)
            capacity = TenantBusinessRoleRepository.resolve_business_role(request.recipient_principal_id, request.tenant_id,
                "tenant_owner", self.database["tenant_business_roles"], session=session)
            admin = self.reader.reads.resolve(request.recipient_principal_id, request.tenant_id, "ENTERPRISE_ADMIN", session=session)
        except InitialReaderDecisionDenied:
            raise
        except Exception as error:
            raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_CURRENTNESS_UNAVAILABLE") from error
        checks = ((principal, expected_principal_revision), (membership, expected_membership_revision),
                  (capacity, expected_capacity_revision), (admin, expected_admin_revision))
        if any(getattr(value, "revision", None) != _revision(revision) for value, revision in checks):
            raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_REVISION_DENIED")
        if (principal.status is not PrincipalStatus.ACTIVE or membership.status is not TenantMembershipStatus.ACTIVE
                or getattr(capacity.status, "value", None) != "ACTIVE" or admin.status is not RoleAssignmentStatus.ACTIVE
                or tenant_role_operation_eligibility("tenant_owner", OPERATION) != ELIGIBLE):
            raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_IAM_PREREQUISITE_DENIED")
        return sha3_512(claims["session_reference"].encode("utf-8")).hexdigest()

    def execute(self, *, request: InitialReaderVerificationRequest, envelope: InitialReaderDecisionEnvelope,
                access_token: str, expected_principal_revision: int, expected_membership_revision: int,
                expected_capacity_revision: int, expected_admin_revision: int, session: Any) -> dict[str, Any]:
        """Atomically consume exactly one verified decision and insert only the reader role.

        The external authority is deliberately read again at the mutation boundary.
        Existing tenant authorization evidence supplies the sole consumption record:
        its tenant-scoped unique idempotency key binds the decision reference and
        its SHA3-512 subject binds the signed decision. Any failure rolls back both
        the role insertion and evidence issuance under the caller's transaction.
        """
        _active_transaction(session)
        if type(request) is not InitialReaderVerificationRequest:
            raise InitialReaderDecisionDenied("INITIAL_READER_VERIFICATION_REQUEST_REQUIRED")
        if request.tenant_id != WILSY_COMPANY_TENANT_ID or request.recipient_principal_id != FOUNDER_PRINCIPAL:
            raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_CANONICAL_SCOPE_REQUIRED")
        if ROLE_PERMISSIONS_MAP.get(ROLE) != [PERMISSION]:
            raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_ROLE_PERMISSION_DRIFT")
        self.require_indexes()
        verified = verify_initial_reader_decision(request, envelope, self.authority)
        if (verified.verdict is not InitialReaderVerdict.VERIFIED or verified.reference != DECISION_REFERENCE
                or verified.tenant_id != WILSY_COMPANY_TENANT_ID or verified.recipient_principal_id != FOUNDER_PRINCIPAL):
            raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_DECISION_SCOPE_DENIED")
        if datetime.now(timezone.utc) >= verified.decision_expires_at:
            raise InitialReaderDecisionDenied("INITIAL_READER_DECISION_NOT_CURRENT")
        session_fingerprint = self._authenticate(access_token, request, expected_principal_revision,
            expected_membership_revision, expected_capacity_revision, expected_admin_revision, session)
        key, subject = self._consumption_key(verified.reference), self._subject(verified.signed_payload_fingerprint)
        try:
            historic = self.reader.evidence.find_by_idempotency(tenant_id=request.tenant_id, idempotency_key=key, session=session)
            if historic is not None:
                if (historic.principal_id != request.recipient_principal_id or historic.operation != OPERATION
                        or historic.permission != PERMISSION or historic.subject_reference != subject
                        or historic.subject_evidence_fingerprint != verified.signed_payload_fingerprint):
                    raise InitialReaderDecisionDenied("INITIAL_READER_DECISION_REPLAY_CONFLICT")
                raise InitialReaderDecisionDenied("INITIAL_READER_DECISION_ALREADY_CONSUMED")
            try:
                self.reader.reads.resolve(request.recipient_principal_id, request.tenant_id, ROLE, session=session)
            except RoleAssignmentNotFoundError:
                pass
            else:
                raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_ASSIGNMENT_ALREADY_EXISTS")
            assignment = RoleAssignmentAuthority(request.recipient_principal_id, request.tenant_id, ROLE, RoleAssignmentStatus.ACTIVE, 0)
            RoleAssignmentRepository.insert(assignment, self.database["role_assignments"], session=session)
            evidence = self.reader.evidence.issue(tenant_id=request.tenant_id, principal_id=request.recipient_principal_id,
                operation=OPERATION, permission=PERMISSION, subject_reference=subject,
                subject_evidence_fingerprint=verified.signed_payload_fingerprint, idempotency_key=key, session=session)
            if self.reader.reads.resolve(request.recipient_principal_id, request.tenant_id, ROLE, session=session) != assignment:
                raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_ASSIGNMENT_READBACK_INVALID")
            if self.reader.evidence.find_by_idempotency(tenant_id=request.tenant_id, idempotency_key=key, session=session) != evidence:
                raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_CONSUMPTION_READBACK_INVALID")
            return {"schema": SCHEMA, "state": "TRANSACTION_PENDING", "tenant_id": request.tenant_id,
                    "principal_id": request.recipient_principal_id, "role_id": ROLE, "permission": PERMISSION,
                    "decision_reference": verified.reference, "decision_fingerprint": verified.signed_payload_fingerprint,
                    "authorization_decision_id": evidence.authorization_decision_id,
                    "authorization_evidence_fingerprint": evidence.authorization_evidence_fingerprint,
                    "authenticated_session_fingerprint": session_fingerprint, "additional_permissions_granted": False}
        except InitialReaderDecisionDenied:
            raise
        except (RoleAssignmentAlreadyExistsError, TenantAuthorizationDecisionEvidenceConflictError, DuplicateKeyError) as error:
            raise InitialReaderDecisionDenied("INITIAL_READER_DECISION_CONCURRENT_CONSUMPTION_DENIED") from error
        except (RoleAssignmentRepositoryError, TenantAuthorizationDecisionEvidenceRegistryError,
                TenantMembershipRepositoryError, TenantBusinessRoleRepositoryError, PyMongoError, TypeError, ValueError) as error:
            raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_PERSISTENCE_OR_EVIDENCE_FAILURE") from error

    def readback(self, result: dict[str, Any]) -> dict[str, Any]:
        """Verify committed consumption/assignment correlation; it never grants access."""
        if not isinstance(result, dict) or result.get("schema") != SCHEMA:
            raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_RESULT_INVALID")
        if (result.get("tenant_id"), result.get("principal_id"), result.get("role_id"), result.get("permission"), result.get("decision_reference")) != (WILSY_COMPANY_TENANT_ID, FOUNDER_PRINCIPAL, ROLE, PERMISSION, DECISION_REFERENCE):
            raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_RESULT_SCOPE_INVALID")
        decision_id, fingerprint = result.get("authorization_decision_id"), result.get("decision_fingerprint")
        if type(decision_id) is not str or type(fingerprint) is not str:
            raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_RESULT_INVALID")
        try:
            evidence = self.reader.evidence.get(tenant_id=WILSY_COMPANY_TENANT_ID, authorization_decision_id=decision_id)
            assignment = self.reader.reads.resolve(FOUNDER_PRINCIPAL, WILSY_COMPANY_TENANT_ID, ROLE)
        except Exception as error:
            raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_READBACK_UNAVAILABLE") from error
        if (evidence.principal_id != FOUNDER_PRINCIPAL or evidence.operation != OPERATION or evidence.permission != PERMISSION
                or evidence.subject_reference != self._subject(fingerprint) or evidence.subject_evidence_fingerprint != fingerprint
                or assignment.tenant_id != WILSY_COMPANY_TENANT_ID or assignment.principal_id != FOUNDER_PRINCIPAL or assignment.role_id != ROLE):
            raise InitialReaderDecisionDenied("INITIAL_READER_ADMISSION_READBACK_INVALID")
        return {"schema": SCHEMA, "tenant_id": WILSY_COMPANY_TENANT_ID, "principal_id": FOUNDER_PRINCIPAL,
                "role_id": ROLE, "permission": PERMISSION, "assignment_status": assignment.status.value,
                "assignment_revision": assignment.revision, "decision_reference": DECISION_REFERENCE,
                "decision_fingerprint": fingerprint, "authorization_decision_id": evidence.authorization_decision_id,
                "authorization_evidence_fingerprint": evidence.authorization_evidence_fingerprint,
                "additional_permissions_granted": False}


__all__ = ["VERSION", "DECISION_REFERENCE", "FOUNDER_PRINCIPAL", "PURPOSE", "ROLE", "PERMISSION", "OPERATION", "SCHEMA", "InitialReaderDecisionDenied", "InitialReaderVerdict", "InitialReaderDecision", "InitialReaderDecisionEnvelope", "InitialReaderVerificationRequest", "InitialReaderInstitutionalAuthority", "VerifiedInitialReaderDecision", "ProductionInitialReaderAdmission", "canonical_initial_reader_message", "verify_initial_reader_decision"]

# ARTIFACT: founder_initial_reader_decision.py
# VERSION: v1.1.0-PRODUCTION-INITIAL-READER-CONSUMPTION
# AUTHORITY BOUNDARY: independent exact reader decision only; no issuer, trust root, administrator or owner is created
# TENANT POSTURE: exact canonical WILSY tenant and Founder principal; no cross-scope consumption
# FAIL-CLOSED POSTURE: authority, signature, currentness, replay, index and persistence failures deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
