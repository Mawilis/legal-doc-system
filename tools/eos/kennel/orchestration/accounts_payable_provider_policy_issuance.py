"""TITLE: Accounts Payable Provider Policy Issuance.
VERSION: v1.0.0-M11E2C2.
AUTHORITY: Kennel EOS; exact tenant authorization evidence required.
EPITOME: Creates immutable AP provider eligibility revisions.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/orchestration/accounts_payable_provider_policy_issuance.py
COLLABORATION / OWNERSHIP: Kennel EOS AP authority orchestration.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 establishes authorization-gated AP policy creation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Authorization and policy tenant must match.
AUTHORITY BOUNDARY: Eligibility issuance only; no runtime binding or selection.
"""
from datetime import datetime
from typing import Any
from ..domain.accounts_payable_provider_policy import AccountsPayableProviderPolicy, AP_POLICY_FAMILY
from ..registry.accounts_payable_provider_policy_registry import AccountsPayableProviderPolicyRegistry

class AccountsPayableProviderPolicyIssuanceError(RuntimeError):
    """Raised when exact AP administration evidence is absent or mismatched."""

def issue_accounts_payable_provider_policy(*, authorization_evidence: Any, tenant_id: str, policy_id: str, policy_revision: int, provider_names: tuple[str, ...], predecessor_fingerprint: str | None, collection: Any, effective_at: datetime, created_at: datetime, session: Any = None) -> AccountsPayableProviderPolicy:
    """Issue one immutable revision from exact durable AP admin evidence."""
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise AccountsPayableProviderPolicyIssuanceError("ACTIVE_TRANSACTION_REQUIRED")
    evidence = authorization_evidence
    if evidence is None or getattr(evidence, 'tenant_id', None) != tenant_id or getattr(evidence, 'permission', None) != 'accounts_payable:provider_policy:admin' or getattr(evidence, 'operation', None) not in {'accounts_payable_provider_policy_create', 'accounts_payable_provider_policy_revise'}:
        raise AccountsPayableProviderPolicyIssuanceError('ADMIN_AUTHORIZATION_EVIDENCE_INVALID')
    if evidence.operation == 'accounts_payable_provider_policy_revise' and policy_revision <= 1:
        raise AccountsPayableProviderPolicyIssuanceError('REVISE_PREDECESSOR_REQUIRED')
    if evidence.operation == 'accounts_payable_provider_policy_create' and policy_revision != 1:
        raise AccountsPayableProviderPolicyIssuanceError('CREATE_INITIAL_REVISION_REQUIRED')
    if getattr(evidence, 'subject_reference', None) != f'accounts-payable-provider-policy:{tenant_id}:{policy_id}:{policy_revision}':
        raise AccountsPayableProviderPolicyIssuanceError('SUBJECT_EVIDENCE_INVALID')
    if policy_revision > 1:
        if not predecessor_fingerprint:
            raise AccountsPayableProviderPolicyIssuanceError('PREDECESSOR_REQUIRED')
        predecessor = AccountsPayableProviderPolicyRegistry.get(tenant_id, policy_id, collection, revision=policy_revision - 1, session=session)
        if predecessor.policy_fingerprint != predecessor_fingerprint:
            raise AccountsPayableProviderPolicyIssuanceError('PREDECESSOR_INVALID')
    policy = AccountsPayableProviderPolicy(policy_id=policy_id, tenant_id=tenant_id, policy_revision=policy_revision, eligible_provider_names=tuple(sorted(set(provider_names))), authorization_decision_id=evidence.authorization_decision_id, authorization_decision_fingerprint=evidence.subject_evidence_fingerprint, created_at=created_at)
    return AccountsPayableProviderPolicyRegistry.create(policy, collection, session=session)

# ARTIFACT: accounts_payable_provider_policy_issuance.py
# VERSION: v1.0.0-M11E2C2
# AUTHORITY BOUNDARY: exact AP authorization-evidence-gated issuance
# TENANT POSTURE: tenant continuity is mandatory
# FAIL-CLOSED POSTURE: bad evidence and predecessor drift reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
