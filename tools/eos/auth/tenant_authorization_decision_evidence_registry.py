"""TITLE: WILSY OS Tenant Authorization Decision Evidence Registry.
VERSION: v1.1.0-SCOPED-AUTHORIZATION-EVIDENCE-REPLAY-READ
AUTHORITY: Existing Python EOS immutable authorization-decision evidence owner.
EPITOME: Issue or read scoped authorization evidence in caller-owned transactions;
historical evidence is never current permission or a role-assignment authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_authorization_decision_evidence_registry.py
COLLABORATION / OWNERSHIP: Existing IAM grant/revocation command owners and
TenantAuthorizationDecisionEvidence own semantics; this registry owns storage.
CERTIFICATION / UPDATE DATE: 2026-11-14
CHANGELOG: v1.1.0-SCOPED-AUTHORIZATION-EVIDENCE-REPLAY-READ adds an exact
transaction-scoped idempotency lookup with strict hydration and explicit absence.
v1.0.0-TENANT-AUTHORIZATION-DECISION-EVIDENCE-REGISTRY established issuance/replay.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No credential, cookie, token, raw exception logging
or index creation in ordinary reads. Corruption and persistence failure reject.
TENANT BOUNDARY: Exact tenant plus idempotency key; never cross-tenant fallback.
AUTHORITY BOUNDARY: Evidence persistence only; historical rows grant no permission
and never authorize an assignment, publication, settlement or command replay.
TRANSACTION BOUNDARY: Caller owns all sessions, transactions and retries.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations
from datetime import datetime, timezone
import uuid
from typing import Any, Optional
from pymongo import ASCENDING
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from .tenant_authorization_decision_evidence import TenantAuthorizationDecisionEvidence, TenantAuthorizationDecisionEvidenceError
from .tenant_authorization import TenantAuthorizationDecision, authorize_tenant_operation
from . import permission_namespace, roles, tenant_authority_policy
from .tenant_membership_repository import TenantMembershipRepository
from .role_assignment_repository import RoleAssignmentRepository
from .tenant_business_role_repository import TenantBusinessRoleRepository

VERSION = "v1.1.0-SCOPED-AUTHORIZATION-EVIDENCE-REPLAY-READ"
COLLECTION = "tenant_authorization_decision_evidence"

class TenantAuthorizationDecisionEvidenceRegistryError(RuntimeError):
    """Base bounded evidence persistence error."""
class TenantAuthorizationDecisionEvidenceTransactionRequiredError(TenantAuthorizationDecisionEvidenceRegistryError):
    """Caller omitted an active transaction; no persistence is permitted."""
class TenantAuthorizationDecisionEvidenceAuthorizationDeniedError(TenantAuthorizationDecisionEvidenceRegistryError):
    """Current central IAM did not authorize issuance."""
class TenantAuthorizationDecisionEvidenceConflictError(TenantAuthorizationDecisionEvidenceRegistryError):
    """Exact replay diverged or a duplicate requires whole-transaction retry."""
class TenantAuthorizationDecisionEvidencePersistenceError(TenantAuthorizationDecisionEvidenceRegistryError):
    """Persistence or strict evidence hydration could not be verified."""

class TenantAuthorizationDecisionEvidenceRegistry:
    """Durable issuer; never creates or owns sessions or transactions."""
    def __init__(self, collection: Collection, *, principal_repository: Any, membership_repository: Any = TenantMembershipRepository, role_assignment_repository: Any = RoleAssignmentRepository, business_role_repository: Any = TenantBusinessRoleRepository) -> None:
        self._collection = collection
        self._principal_repository = principal_repository
        self._membership_repository = membership_repository
        self._role_assignment_repository = role_assignment_repository
        self._business_role_repository = business_role_repository

    def ensure_indexes(self) -> None:
        """Create durable uniqueness indexes outside issuance transactions."""
        self._collection.create_index([("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)], unique=True, name="tenant_authorization_idempotency_unique")
        self._collection.create_index([("authorization_decision_id", ASCENDING)], unique=True, name="authorization_decision_identity_unique")

    def get(self, *, tenant_id: str, authorization_decision_id: str, session: Optional[ClientSession] = None) -> TenantAuthorizationDecisionEvidence:
        """Read one exact tenant-scoped evidence record and strictly hydrate it."""
        if not isinstance(tenant_id, str) or not tenant_id.strip() or not isinstance(authorization_decision_id, str) or not authorization_decision_id.strip():
            raise TenantAuthorizationDecisionEvidencePersistenceError("EVIDENCE_NOT_FOUND")
        try:
            row = self._collection.find_one({"tenant_id": tenant_id, "authorization_decision_id": authorization_decision_id}, session=session)
            if row is None: raise TenantAuthorizationDecisionEvidencePersistenceError("EVIDENCE_NOT_FOUND")
            body = dict(row); body.pop("_id", None)
            return TenantAuthorizationDecisionEvidence.from_persisted(body)
        except TenantAuthorizationDecisionEvidencePersistenceError: raise
        except (TenantAuthorizationDecisionEvidenceError, PyMongoError, TypeError, ValueError) as error:
            raise TenantAuthorizationDecisionEvidencePersistenceError("EVIDENCE_PERSISTED_RECORD_INVALID") from error

    def find_by_idempotency(self, *, tenant_id: str, idempotency_key: str,
                            session: Optional[ClientSession] = None) -> TenantAuthorizationDecisionEvidence | None:
        """Read immutable evidence by exact tenant/key inside the caller transaction.

        Lawful absence returns None. Corrupt/foreign records and source outages
        raise; this read never issues evidence, creates indexes or authorizes a
        command. The caller must independently revalidate current authority.
        """
        tx = self._require_transaction(session)
        if any(not isinstance(value, str) or not value or value != value.strip()
               for value in (tenant_id, idempotency_key)):
            raise TenantAuthorizationDecisionEvidencePersistenceError("EVIDENCE_SCOPE_INVALID")
        try:
            row = self._collection.find_one({"tenant_id": tenant_id, "idempotency_key": idempotency_key}, session=tx)
            if row is None:
                return None
            body = dict(row); body.pop("_id", None)
            value = TenantAuthorizationDecisionEvidence.from_persisted(body)
            if value.tenant_id != tenant_id or value.idempotency_key != idempotency_key:
                raise TenantAuthorizationDecisionEvidencePersistenceError("EVIDENCE_SCOPE_INVALID")
            return value
        except TenantAuthorizationDecisionEvidencePersistenceError:
            raise
        except (TenantAuthorizationDecisionEvidenceError, PyMongoError, TypeError, ValueError) as error:
            raise TenantAuthorizationDecisionEvidencePersistenceError("EVIDENCE_READ_UNAVAILABLE_OR_INVALID") from error

    @staticmethod
    def _require_transaction(session: Optional[ClientSession]) -> ClientSession:
        if session is None or getattr(session, "in_transaction", False) is not True:
            raise TenantAuthorizationDecisionEvidenceTransactionRequiredError("ACTIVE_TRANSACTION_REQUIRED")
        return session

    @staticmethod
    def _request_material(*, tenant_id: str, principal_id: str, operation: str, permission: str, subject_reference: str, subject_evidence_fingerprint: str, idempotency_key: str) -> tuple[str, ...]:
        return (tenant_id, principal_id, operation, permission, subject_reference, subject_evidence_fingerprint, idempotency_key)

    def issue(self, *, tenant_id: str, principal_id: str, operation: str, permission: str, subject_reference: str, subject_evidence_fingerprint: str, idempotency_key: str, session: Optional[ClientSession] = None) -> TenantAuthorizationDecisionEvidence:
        """Issue or replay evidence; returned evidence is transaction-pending until caller commit."""
        tx = self._require_transaction(session)
        try:
            existing = self._collection.find_one({"tenant_id": tenant_id, "idempotency_key": idempotency_key}, session=tx)
            requested = self._request_material(tenant_id=tenant_id, principal_id=principal_id, operation=operation, permission=permission, subject_reference=subject_reference, subject_evidence_fingerprint=subject_evidence_fingerprint, idempotency_key=idempotency_key)
            if existing is not None:
                persisted = dict(existing); persisted.pop("_id", None)
                historic = TenantAuthorizationDecisionEvidence.from_persisted(persisted)
                historic_material = self._request_material(tenant_id=historic.tenant_id, principal_id=historic.principal_id, operation=historic.operation, permission=historic.permission, subject_reference=historic.subject_reference, subject_evidence_fingerprint=historic.subject_evidence_fingerprint, idempotency_key=historic.idempotency_key)
                if historic_material != requested: raise TenantAuthorizationDecisionEvidenceConflictError("IDEMPOTENCY_CONFLICT")
                return historic
            decision: TenantAuthorizationDecision = authorize_tenant_operation(principal_id=principal_id, tenant_id=tenant_id, permission_id=permission, operation=operation, principal_repository=self._principal_repository, membership_repository=self._membership_repository, role_assignment_repository=self._role_assignment_repository, business_role_repository=self._business_role_repository, session=tx)
            if not decision.authorized or not decision.business_role or not decision.authorization_role:
                raise TenantAuthorizationDecisionEvidenceAuthorizationDeniedError("AUTHORIZATION_DENIED")
            membership = self._membership_repository.resolve(principal_id, tenant_id, session=tx)
            assignment = self._role_assignment_repository.resolve(principal_id, tenant_id, decision.authorization_role, session=tx)
            evidence = TenantAuthorizationDecisionEvidence(tenant_id=tenant_id, authorization_decision_id=uuid.uuid4().hex, principal_id=principal_id, operation=operation, permission=permission, business_role=decision.business_role, authorization_role=decision.authorization_role, membership_revision=membership.revision, role_assignment_revision=assignment.revision, subject_reference=subject_reference, subject_evidence_fingerprint=subject_evidence_fingerprint, permission_namespace_version=permission_namespace.VERSION, authorization_role_policy_version=roles.VERSION, tenant_business_role_policy_version=tenant_authority_policy.VERSION, tenant_authorization_composition_version=__import__("tools.eos.auth.tenant_authorization", fromlist=["VERSION"]).VERSION, idempotency_key=idempotency_key, authorized_at=datetime.now(timezone.utc))
            self._collection.insert_one(evidence.to_persisted(), session=tx)
            return evidence
        except (TenantAuthorizationDecisionEvidenceError, PyMongoError) as error:
            if isinstance(error, TenantAuthorizationDecisionEvidenceError): raise TenantAuthorizationDecisionEvidencePersistenceError("EVIDENCE_INVALID") from error
            if isinstance(error, DuplicateKeyError): raise TenantAuthorizationDecisionEvidenceConflictError("DUPLICATE_RETRY_TRANSACTION") from error
            raise TenantAuthorizationDecisionEvidencePersistenceError("PERSISTENCE_UNAVAILABLE") from error

__all__ = ["VERSION", "COLLECTION", "TenantAuthorizationDecisionEvidenceRegistry", "TenantAuthorizationDecisionEvidenceRegistryError", "TenantAuthorizationDecisionEvidenceTransactionRequiredError", "TenantAuthorizationDecisionEvidenceAuthorizationDeniedError", "TenantAuthorizationDecisionEvidenceConflictError", "TenantAuthorizationDecisionEvidencePersistenceError"]

# ARTIFACT: tenant_authorization_decision_evidence_registry.py
# VERSION: v1.1.0-SCOPED-AUTHORIZATION-EVIDENCE-REPLAY-READ
# AUTHORITY BOUNDARY: durable evidence issuance only; no approval or execution.
# TENANT POSTURE: exact tenant/idempotency scope; no cross-tenant replay.
# FAIL-CLOSED POSTURE: absent transaction, denial, corruption, and conflicts reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
