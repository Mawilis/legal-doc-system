"""TITLE: WILSY OS Governed Company Document Reader Grant.
VERSION: v1.1.0-FOUNDER-DISPOSABLE-DEV-INITIALIZATION
AUTHORITY: Existing central IAM, explicit delegation policy and canonical stores.
EPITOME: Assign only the existing read-only company role to an existing member,
using an independently authorized administrator and immutable decision evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/company_document_reader_grant.py
COLLABORATION / OWNERSHIP: Company-document HTTP owner supplies authenticated
actor/tenant/capacity; role and authorization-evidence repositories own storage.
CERTIFICATION / UPDATE DATE: 2026-11-14
CHANGELOG: v1.1.0-FOUNDER-DISPOSABLE-DEV-INITIALIZATION adds an explicit
self-initialization for isolated development databases only, with durable
read-authority evidence, no administrator appointment and no HTTP bypass.
v1.0.0-GOVERNED-COMPANY-READER-GRANT introduces exact-company,
revision-guarded issuance/regrant and historical replay without new IAM stores.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No credentials, profiles, default grants, raw logs,
automatic DDL, transaction ownership or identity-based administrative privilege.
TENANT BOUNDARY: Canonical WILSY tenant only, on every lookup and mutation.
AUTHORITY BOUNDARY: Current tenant_admin eligibility and ENTERPRISE_ADMIN
assignment plus explicit delegation edge are required. Actor differs from target.
Approval/reason references record an independently authorized grantor's decision;
references alone never confer authority. Canonical execution needs operator approval.
TRANSACTION BOUNDARY: Caller owns snapshot transaction, commit, abort and retries.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from __future__ import annotations

from hashlib import sha3_512
import json
import os
from typing import Any

from pymongo.errors import PyMongoError, DuplicateKeyError

from tools.eos.auth.authorization_role_delegation_policy import (
    COMPANY_DOCUMENT_READER_ROLE, VERSION as DELEGATION_VERSION,
    evaluate_authorization_role_grant,
)
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository, PrincipalAuthorityRepositoryError, PrincipalAuthorityNotFoundError
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentRepository, RoleAssignmentRepositoryError, RoleAssignmentNotFoundError,
    RoleAssignmentAlreadyExistsError, RoleAssignmentRevisionConflictError,
)
from tools.eos.auth.tenant_authorization import authorize_tenant_operation
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceRegistry, TenantAuthorizationDecisionEvidenceRegistryError,
    TenantAuthorizationDecisionEvidenceConflictError,
)
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository, TenantBusinessRoleRepositoryError, TenantBusinessRoleNotFoundError
from tools.eos.auth.tenant_business_role_authority import resolve_current_tenant_business_role, BusinessRoleResolution
from tools.eos.auth.tenant_authority_policy import ELIGIBLE, TENANT_ROLES, tenant_role_operation_eligibility
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository, TenantMembershipRepositoryError, TenantMembershipNotFoundError
from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID

VERSION = "v1.1.0-FOUNDER-DISPOSABLE-DEV-INITIALIZATION"
PERMISSION = "tenant:role_assignment:write"
OPERATION = "role_grant"


class CompanyReaderGrantError(RuntimeError):
    """Bounded command failure; no dependency text, secret or speculative success."""

    def __init__(self, code: str, status: int = 503) -> None:
        self.code, self.status = code, status
        super().__init__(code)


class _ScopedReads:
    """Collection binding only; canonical repositories retain lifecycle semantics."""

    def __init__(self, database: Any) -> None:
        self.db = database

    def principal(self, principal_id: str, *, session: Any = None) -> Any:
        return PrincipalAuthorityRepository.resolve(principal_id, self.db["principal_authorities"], session=session)

    def membership(self, principal_id: str, tenant_id: str, *, session: Any = None) -> Any:
        return TenantMembershipRepository.resolve(principal_id, tenant_id, self.db["tenant_memberships"], session=session)

    def resolve(self, principal_id: str, tenant_id: str, role_id: str, *, session: Any = None) -> Any:
        if role_id in TENANT_ROLES:
            return TenantBusinessRoleRepository.resolve_business_role(principal_id, tenant_id, role_id, self.db["tenant_business_roles"], session=session)
        return RoleAssignmentRepository.resolve(principal_id, tenant_id, role_id, self.db["role_assignments"], session=session)

    def resolve_all_business_roles(self, principal_id: str, tenant_id: str, *, session: Any = None) -> Any:
        return TenantBusinessRoleRepository.resolve_all(principal_id, tenant_id, self.db["tenant_business_roles"], session=session)

    def resolve_current_business_role(self, principal_id: str, tenant_id: str, *, session: Any = None) -> Any:
        return TenantBusinessRoleRepository.resolve(principal_id, tenant_id, self.db["tenant_business_roles"], session=session)


class _PrincipalReads:
    def __init__(self, reads: _ScopedReads) -> None:
        self.resolve = reads.principal


class _MembershipReads:
    def __init__(self, reads: _ScopedReads) -> None:
        self.resolve = reads.membership


def _text(value: object, maximum: int) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > maximum:
        raise CompanyReaderGrantError("COMPANY_READER_INPUT_INVALID", 422)
    return value


def _revision(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise CompanyReaderGrantError("COMPANY_READER_REVISION_INVALID", 422)
    return value


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


class CompanyDocumentReaderGrant:
    """Narrow assignment orchestrator; no alternate authentication or IAM ledger.

    Transaction-pending output is historical grant evidence. A receipt never
    proves present access; readers must pass canonical current IAM every time.
    """

    def __init__(self, database: Any) -> None:
        """Bind existing canonical repositories without database I/O or DDL."""
        self.db = database
        self.reads = _ScopedReads(database)
        self.principals = _PrincipalReads(self.reads)
        self.memberships = _MembershipReads(self.reads)
        self.evidence = TenantAuthorizationDecisionEvidenceRegistry(
            database["tenant_authorization_decision_evidence"],
            principal_repository=self.principals, membership_repository=self.memberships,
            role_assignment_repository=self.reads, business_role_repository=self.reads,
        )

    def require_indexes(self) -> None:
        """Read metadata only; reject unsafe/missing uniqueness without creating indexes.

        Metadata reads occur before the caller's business transaction. Existing
        operator-owned index provisioning is not silently run by grant requests.
        """
        required = {
            "role_assignments": [("principal_id", "tenant_id", "role_id")],
            "tenant_authorization_decision_evidence": [("tenant_id", "idempotency_key"), ("authorization_decision_id",)],
        }
        try:
            for collection, keys in required.items():
                indexes = self.db[collection].index_information().values()
                for key in keys:
                    if not any(tuple(name for name, direction in item.get("key", ())) == key
                               and item.get("unique") is True and not item.get("sparse")
                               and not item.get("partialFilterExpression") and "expireAfterSeconds" not in item
                               and item.get("collation", {}).get("locale", "simple") == "simple"
                               for item in indexes):
                        raise CompanyReaderGrantError("COMPANY_READER_INDEX_REQUIRED")
        except PyMongoError as error:
            raise CompanyReaderGrantError("COMPANY_READER_SOURCE_UNAVAILABLE") from error

    def execute_disposable_founder_initialization(
        self, *, authenticated_principal_id: str, tenant_id: str,
        expected_membership_revision: int, expected_capacity_revision: int,
        session: Any,
    ) -> dict[str, Any]:
        """One-time, read-only role admission in an owned disposable development DB.

        This is intentionally NOT an initial IAM grantor appointment. Such an
        appointment requires its own governance contract and evidence authority.
        No HTTP endpoint invokes this method and the regular independently
        authorized grant command remains unchanged. The caller must authenticate
        the person and verify durable session currentness independently; neither
        environment variables nor this method authenticate browser requests.

        The sole success path requires an explicit local disposable replica,
        an exact opted-in database/principal, active tenant-owner authority and
        unchanged revisions. The role's unique natural key prevents a second
        admission even after revocation. Read-authorization evidence is issued
        after role insertion in the same caller-owned transaction; it is NOT
        represented as independently approved administrative grant evidence.
        """
        if session is None or getattr(session, "in_transaction", False) is not True:
            raise CompanyReaderGrantError("FOUNDER_DEV_TRANSACTION_REQUIRED")
        if (
            os.environ.get("WILSY_FOUNDER_DEV_INIT") != "DISPOSABLE_READER_ONLY"
            or os.environ.get("WILSY_EOS_ENV") != "development"
            or os.environ.get("WILSY_FOUNDER_DEV_DB") != getattr(self.db, "name", None)
            or not isinstance(getattr(self.db, "name", None), str)
            or not self.db.name.startswith("wilsy_founder_dev_")
            or os.environ.get("WILSY_FOUNDER_DEV_PRINCIPAL") != authenticated_principal_id
        ):
            raise CompanyReaderGrantError("FOUNDER_DEV_DISABLED", 403)
        try:
            nodes = self.db.client.nodes
            replica_set = self.db.client.options.replica_set_name
        except (AttributeError, TypeError, ValueError) as error:
            raise CompanyReaderGrantError("FOUNDER_DEV_TARGET_UNVERIFIED", 403) from error
        if (
            not nodes or replica_set != "wilsyVendorCertRS"
            or any(host not in {"127.0.0.1", "localhost", "::1"} for host, _ in nodes)
        ):
            raise CompanyReaderGrantError("FOUNDER_DEV_TARGET_UNVERIFIED", 403)
        actor = _text(authenticated_principal_id, 128)
        if tenant_id != WILSY_COMPANY_TENANT_ID:
            raise CompanyReaderGrantError("FOUNDER_DEV_TENANT_DENIED", 403)
        membership_revision = _revision(expected_membership_revision)
        capacity_revision = _revision(expected_capacity_revision)
        try:
            principal = self.principals.resolve(actor, session=session)
            membership = self.memberships.resolve(actor, tenant_id, session=session)
            capacity = TenantBusinessRoleRepository.resolve_business_role(
                actor, tenant_id, "tenant_owner", self.db["tenant_business_roles"], session=session,
            )
            admin = self.reads.resolve(actor, tenant_id, "ENTERPRISE_ADMIN", session=session)
            resolved = resolve_current_tenant_business_role(
                principal_id=actor, tenant_id=tenant_id, repository=self.reads,
                operation="company_operating_document_read",
                selected_business_role="tenant_owner", session=session,
            )
            if (
                principal.status is not PrincipalStatus.ACTIVE
                or membership.status is not TenantMembershipStatus.ACTIVE
                or membership.revision != membership_revision
                or capacity.revision != capacity_revision
                or resolved.resolution is not BusinessRoleResolution.RESOLVED
                or admin.status is not RoleAssignmentStatus.ACTIVE
                or tenant_role_operation_eligibility("tenant_owner", "company_operating_document_read") != ELIGIBLE
            ):
                raise CompanyReaderGrantError("FOUNDER_DEV_AUTHORITY_DENIED", 403)
            try:
                self.reads.resolve(actor, tenant_id, COMPANY_DOCUMENT_READER_ROLE, session=session)
            except RoleAssignmentNotFoundError:
                pass
            else:
                # Even a REVOKED record permanently closes this initialization.
                raise CompanyReaderGrantError("FOUNDER_DEV_ALREADY_CONSUMED", 409)
            value = RoleAssignmentAuthority(
                actor, tenant_id, COMPANY_DOCUMENT_READER_ROLE, RoleAssignmentStatus.ACTIVE, 0,
            )
            RoleAssignmentRepository.insert(value, self.db["role_assignments"], session=session)
            subject = _canonical(dict(
                k="founder_disposable_read_only/v1", p=actor, r=0,
                m=membership_revision, c=capacity_revision,
            ))
            intent_fingerprint = sha3_512(subject.encode("ascii")).hexdigest()
            evidence = self.evidence.issue(
                tenant_id=tenant_id, principal_id=actor,
                operation="company_operating_document_read",
                permission="company_operating_document:read",
                subject_reference=subject,
                subject_evidence_fingerprint=intent_fingerprint,
                idempotency_key="founder-disposable-reader-init:v1", session=session,
            )
            if self.reads.resolve(actor, tenant_id, COMPANY_DOCUMENT_READER_ROLE, session=session) != value:
                raise CompanyReaderGrantError("FOUNDER_DEV_READBACK_FAILED")
            return dict(
                schema="WILSY-FOUNDER-DISPOSABLE-READER-INIT/V1",
                state="TRANSACTION_PENDING", tenant_id=tenant_id,
                principal_id=actor, role_id=COMPANY_DOCUMENT_READER_ROLE,
                authorization_decision_id=evidence.authorization_decision_id,
                evidence_fingerprint=evidence.authorization_evidence_fingerprint,
                administrative_grantor_appointed=False,
                canonical_tenant_changed=False,
            )
        except CompanyReaderGrantError:
            raise
        except (RoleAssignmentAlreadyExistsError, RoleAssignmentRevisionConflictError,
                TenantAuthorizationDecisionEvidenceConflictError) as error:
            raise CompanyReaderGrantError("FOUNDER_DEV_ALREADY_CONSUMED", 409) from error
        except (PrincipalAuthorityNotFoundError, TenantMembershipNotFoundError,
                TenantBusinessRoleNotFoundError, RoleAssignmentNotFoundError) as error:
            raise CompanyReaderGrantError("FOUNDER_DEV_AUTHORITY_DENIED", 403) from error
        except (PrincipalAuthorityRepositoryError, TenantMembershipRepositoryError,
                TenantBusinessRoleRepositoryError, RoleAssignmentRepositoryError,
                TenantAuthorizationDecisionEvidenceRegistryError, PyMongoError) as error:
            raise CompanyReaderGrantError("FOUNDER_DEV_SOURCE_UNAVAILABLE") from error

    def execute(self, *, actor_principal_id: str, tenant_id: str, target_principal_id: str,
                target_business_role: str, expected_membership_revision: int,
                expected_capacity_revision: int, expected_assignment_revision: int | None,
                approval_reference: str, reason_reference: str, idempotency_key: str,
                session: Any, selected_business_role: str | None = None) -> dict[str, Any]:
        """Authorize independently, append grant evidence and insert/CAS atomically.

        Exact replay returns immutable history and never reactivates a revoked
        role. A new regrant requires a new key and the exact revoked revision.
        Current actor IAM is rechecked even for historical replay. Target scope,
        membership/capacity revisions, independent actor and fixed role are bound
        into SHA3-512 intent. Caller must abort on any error and commit before
        responding; an independent durable read must follow a canonical grant.
        """
        if session is None or getattr(session, "in_transaction", False) is not True:
            raise CompanyReaderGrantError("COMPANY_READER_TRANSACTION_REQUIRED")
        actor = _text(actor_principal_id, 128)
        target = _text(target_principal_id, 128)
        if tenant_id != WILSY_COMPANY_TENANT_ID or actor == target:
            raise CompanyReaderGrantError("COMPANY_READER_INDEPENDENT_AUTHORITY_REQUIRED", 403)
        capacity = _text(target_business_role, 128)
        membership_revision = _revision(expected_membership_revision)
        capacity_revision = _revision(expected_capacity_revision)
        if expected_assignment_revision is not None:
            _revision(expected_assignment_revision)
        approval = _text(approval_reference, 48)
        reason = _text(reason_reference, 256)
        key = "company-reader-grant:" + _text(idempotency_key, 200)
        intent = dict(actor=actor, tenant=tenant_id, target=target, role=COMPANY_DOCUMENT_READER_ROLE,
                      capacity=capacity, membership_revision=membership_revision, capacity_revision=capacity_revision,
                      assignment_revision=expected_assignment_revision, approval=approval, reason=reason)
        fingerprint = sha3_512(_canonical(intent).encode("ascii")).hexdigest()
        try:
            decision = authorize_tenant_operation(
                principal_id=actor, tenant_id=tenant_id, permission_id=PERMISSION, operation=OPERATION,
                principal_repository=self.principals, membership_repository=self.memberships,
                role_assignment_repository=self.reads, business_role_repository=self.reads,
                selected_business_role=selected_business_role, session=session,
            )
            if not decision.authorized:
                unavailable = "UNAVAILABLE" in decision.reason.value
                raise CompanyReaderGrantError("COMPANY_READER_AUTHORITY_UNAVAILABLE" if unavailable else "COMPANY_READER_GRANT_DENIED", 503 if unavailable else 403)
            assignment = self.reads.resolve(actor, tenant_id, "ENTERPRISE_ADMIN", session=session)
            if not evaluate_authorization_role_grant(assignment, tenant_id, COMPANY_DOCUMENT_READER_ROLE).allowed:
                raise CompanyReaderGrantError("COMPANY_READER_DELEGATION_DENIED", 403)
            historic = self.evidence.find_by_idempotency(tenant_id=tenant_id, idempotency_key=key, session=session)
            if historic is not None:
                if (historic.subject_evidence_fingerprint != fingerprint or historic.principal_id != actor
                        or historic.operation != OPERATION or historic.permission != PERMISSION):
                    raise CompanyReaderGrantError("COMPANY_READER_IDEMPOTENCY_CONFLICT", 409)
                subject = json.loads(historic.subject_reference)
                revision = 0 if expected_assignment_revision is None else expected_assignment_revision + 1
                if subject.get("k") != "company_reader_grant/v1" or subject.get("p") != target or subject.get("r") != revision:
                    raise CompanyReaderGrantError("COMPANY_READER_EVIDENCE_INVALID")
                return self._result(historic, target, revision, "EXACT_REPLAY")
            principal = self.principals.resolve(target, session=session)
            membership = self.memberships.resolve(target, tenant_id, session=session)
            resolved = resolve_current_tenant_business_role(
                principal_id=target, tenant_id=tenant_id, repository=self.reads,
                operation="company_operating_document_read", selected_business_role=capacity, session=session,
            )
            if resolved.resolution is not BusinessRoleResolution.RESOLVED:
                unavailable = "UNAVAILABLE" in resolved.resolution.value
                raise CompanyReaderGrantError("COMPANY_READER_TARGET_SOURCE_UNAVAILABLE" if unavailable else "COMPANY_READER_TARGET_DENIED", 503 if unavailable else 403)
            target_capacity = TenantBusinessRoleRepository.resolve_business_role(
                target, tenant_id, capacity, self.db["tenant_business_roles"], session=session)
            if (principal.status is not PrincipalStatus.ACTIVE or membership.status is not TenantMembershipStatus.ACTIVE
                    or resolved.resolution is not BusinessRoleResolution.RESOLVED
                    or tenant_role_operation_eligibility(capacity, "company_operating_document_read") != ELIGIBLE):
                raise CompanyReaderGrantError("COMPANY_READER_TARGET_DENIED", 403)
            if membership.revision != membership_revision or target_capacity.revision != capacity_revision:
                raise CompanyReaderGrantError("COMPANY_READER_TARGET_REVISION_CONFLICT", 409)
            try:
                current = self.reads.resolve(target, tenant_id, COMPANY_DOCUMENT_READER_ROLE, session=session)
            except RoleAssignmentNotFoundError:
                current = None
            if (current is None and expected_assignment_revision is not None) or (current is not None and (
                    current.status is not RoleAssignmentStatus.REVOKED or current.revision != expected_assignment_revision)):
                raise CompanyReaderGrantError("COMPANY_READER_ASSIGNMENT_CONFLICT", 409)
            revision = 0 if current is None else current.revision + 1
            subject = _canonical(dict(k="company_reader_grant/v1", p=target, r=revision,
                                      d=DELEGATION_VERSION, a=approval))
            if len(subject) > 256:
                raise CompanyReaderGrantError("COMPANY_READER_REFERENCE_TOO_LONG", 422)
            evidence = self.evidence.issue(tenant_id=tenant_id, principal_id=actor, operation=OPERATION,
                permission=PERMISSION, subject_reference=subject, subject_evidence_fingerprint=fingerprint,
                idempotency_key=key, session=session)
            value = RoleAssignmentAuthority(target, tenant_id, COMPANY_DOCUMENT_READER_ROLE, RoleAssignmentStatus.ACTIVE, revision)
            if current is None:
                RoleAssignmentRepository.insert(value, self.db["role_assignments"], session=session)
            else:
                RoleAssignmentRepository.compare_and_swap(value, current.revision, self.db["role_assignments"], session=session)
            if self.reads.resolve(target, tenant_id, COMPANY_DOCUMENT_READER_ROLE, session=session) != value:
                raise CompanyReaderGrantError("COMPANY_READER_ASSIGNMENT_READBACK_INVALID")
            if self.evidence.find_by_idempotency(tenant_id=tenant_id, idempotency_key=key, session=session) != evidence:
                raise CompanyReaderGrantError("COMPANY_READER_EVIDENCE_READBACK_INVALID")
            return self._result(evidence, target, revision, "NEWLY_GRANTED")
        except CompanyReaderGrantError:
            raise
        except (TenantAuthorizationDecisionEvidenceConflictError, RoleAssignmentAlreadyExistsError,
                RoleAssignmentRevisionConflictError) as error:
            # Ordinary arbitration losses require a fresh transaction. Never
            # treat duplicate evidence/assignment races as source absence.
            raise CompanyReaderGrantError("COMPANY_READER_CONFLICT_RETRY_REQUIRED", 409) from error
        except (PrincipalAuthorityNotFoundError, TenantMembershipNotFoundError,
                TenantBusinessRoleNotFoundError) as error:
            raise CompanyReaderGrantError("COMPANY_READER_TARGET_DENIED", 403) from error
        except (PrincipalAuthorityRepositoryError, TenantMembershipRepositoryError,
                TenantBusinessRoleRepositoryError, RoleAssignmentRepositoryError,
                TenantAuthorizationDecisionEvidenceRegistryError, PyMongoError,
                TypeError, ValueError, KeyError) as error:
            # Preserve the driver's whole-transaction retry contract even when
            # a repository wraps a transient write error. Never retry a fragment.
            cause: BaseException | None = error
            while cause is not None:
                if isinstance(cause, PyMongoError) and cause.has_error_label("TransientTransactionError"):
                    raise cause
                if isinstance(cause, DuplicateKeyError):
                    raise CompanyReaderGrantError("COMPANY_READER_CONFLICT_RETRY_REQUIRED", 409) from error
                cause = cause.__cause__
            raise CompanyReaderGrantError("COMPANY_READER_SOURCE_UNAVAILABLE_OR_INVALID") from error

    @staticmethod
    def _result(evidence: Any, target: str, revision: int, state: str) -> dict[str, Any]:
        return dict(schema="WILSY-COMPANY-READER-GRANT/V1", state=state,
                    tenant_id=evidence.tenant_id, target_principal_id=target,
                    role_id=COMPANY_DOCUMENT_READER_ROLE, assignment_revision=revision,
                    authorization_decision_id=evidence.authorization_decision_id,
                    authorization_evidence_fingerprint=evidence.authorization_evidence_fingerprint,
                    intent_fingerprint=evidence.subject_evidence_fingerprint,
                    authority="HISTORICAL_GRANT_EVIDENCE_ONLY")


# ARTIFACT: company_document_reader_grant.py
# VERSION: v1.1.0-FOUNDER-DISPOSABLE-DEV-INITIALIZATION
# AUTHORITY BOUNDARY: Explicit current IAM and independent fixed-reader delegation only.
# TENANT POSTURE: Canonical company tenant and exact principal/membership/capacity.
# FAIL-CLOSED POSTURE: Revision, evidence, source, replay and authority failures reject.
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
