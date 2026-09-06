"""WILSY OS M10 POS execution-authorization issuance owner.

TITLE: POS Financial Execution Authorization Issuance
VERSION: v1.0.0-M10
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Issue durable directional POS execution authorization from canonical evidence.
EPITOME: Policy binding of M9 commercial intent and existing authority evidence.
ABSOLUTE CANONICAL PATH: tools/eos/saas/billing/pos_financial_execution_authorization_issuance.py
COLLABORATION / OWNERSHIP: Python EOS SaaS POS authorization orchestration owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M10 establishes governed collection/refund issuance.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No provider calls or payment credentials.
TENANT BOUNDARY: Existing authority evidence and M9 source must share tenant/location.
AUTHORITY BOUNDARY: Binds existing authority; creates no role.
FINANCIAL AUTHORITY BOUNDARY: No execution, settlement, or paid truth.
TRANSACTION BOUNDARY: Caller supplies collection/session; no lifecycle ownership.
FAIL-CLOSED DECLARATION: Missing or mismatched canonical evidence rejects.
"""
from datetime import datetime, timezone
from tools.eos.auth.tenant_authorization_decision_evidence import TenantAuthorizationDecisionEvidence
from ..domain.pos_commercial import POSSale, POSTenderIntent, POSRefundIntent
from ..domain.pos_financial_execution_authorization import POSFinancialExecutionAuthorization
from .pos_financial_execution_authorization_registry import POSFinancialExecutionAuthorizationRegistry

def _issue(sale, source, authority, collection, *, authorization_id, idempotency_key, authorized_at=None, session=None):
 if not isinstance(sale,POSSale) or not isinstance(source,(POSTenderIntent,POSRefundIntent)) or not isinstance(authority,TenantAuthorizationDecisionEvidence): raise ValueError('M10_AUTH_CANONICAL_INPUT_REQUIRED')
 value=POSFinancialExecutionAuthorization.issue(sale,source,authority,authorization_id=authorization_id,idempotency_key=idempotency_key,authorized_at=authorized_at or datetime.now(timezone.utc))
 return POSFinancialExecutionAuthorizationRegistry.create(value,collection,session=session)
def issue_pos_collection_execution_authorization(sale, tender, authority, collection, *, authorization_id, idempotency_key, authorized_at=None, session=None):
 return _issue(sale,tender,authority,collection,authorization_id=authorization_id,idempotency_key=idempotency_key,authorized_at=authorized_at,session=session)
def issue_pos_refund_execution_authorization(sale, refund, authority, collection, *, authorization_id, idempotency_key, authorized_at=None, session=None):
 return _issue(sale,refund,authority,collection,authorization_id=authorization_id,idempotency_key=idempotency_key,authorized_at=authorized_at,session=session)
# ARTIFACT: pos_financial_execution_authorization_issuance.py
# VERSION: v1.0.0-M10
# AUTHORITY BOUNDARY: Existing authority evidence is required; no role grant.
# TENANT POSTURE: Exact M9 provenance and tenant scope.
# FAIL-CLOSED POSTURE: Invalid context and unsupported tenders reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
