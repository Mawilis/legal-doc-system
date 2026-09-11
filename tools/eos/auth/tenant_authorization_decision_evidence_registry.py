"""WILSY OS durable tenant authorization decision evidence registry.

VERSION: v1.0.0-TENANT-AUTHORIZATION-DECISION-EVIDENCE-REGISTRY
AUTHORITY: Python EOS durable authorization-decision evidence owner.
EPITOME: Issues immutable evidence inside a caller-owned active transaction.
TENANT BOUNDARY: All identity and idempotency lookups are tenant scoped.
FINANCIAL AUTHORITY: Kennel EOS exclusively executes financial operations.
TRANSACTION BOUNDARY: Caller owns ClientSession and transaction lifecycle.
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

VERSION = "v1.0.0-TENANT-AUTHORIZATION-DECISION-EVIDENCE-REGISTRY"
COLLECTION = "tenant_authorization_decision_evidence"

class TenantAuthorizationDecisionEvidenceRegistryError(RuntimeError): pass
class TenantAuthorizationDecisionEvidenceTransactionRequiredError(TenantAuthorizationDecisionEvidenceRegistryError): pass
class TenantAuthorizationDecisionEvidenceAuthorizationDeniedError(TenantAuthorizationDecisionEvidenceRegistryError): pass
class TenantAuthorizationDecisionEvidenceConflictError(TenantAuthorizationDecisionEvidenceRegistryError): pass
class TenantAuthorizationDecisionEvidencePersistenceError(TenantAuthorizationDecisionEvidenceRegistryError): pass

class TenantAuthorizationDecisionEvidenceRegistry:
    """Durable issuer; never creates or owns sessions or transactions."""
    def __init__(self, collection: Collection, *, principal_repository: Any, membership_repository: Any = TenantMembershipRepository, role_assignment_repository: Any = RoleAssignmentRepository, business_role_repository: Any = RoleAssignmentRepository) -> None:
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
# VERSION: v1.0.0-TENANT-AUTHORIZATION-DECISION-EVIDENCE-REGISTRY
# AUTHORITY BOUNDARY: durable evidence issuance only; no approval or execution.
# TENANT POSTURE: exact tenant/idempotency scope; no cross-tenant replay.
# FAIL-CLOSED POSTURE: absent transaction, denial, corruption, and conflicts reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
