"""TITLE: Platform Billing Provider Routing Orchestration.
VERSION: v1.1.0-M11E2D5C2G-P5-R2C.
AUTHORITY: Kennel EOS / Wilsy OS Core Governance.
EPITOME: Select exactly one provider from request-bound historical policy with request-level replay precedence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/orchestration/platform_billing_provider_routing.py
COLLABORATION / OWNERSHIP: Kennel EOS P4 routing transition owner; consumes durable Platform request and policy.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v1.1.0-M11E2D5C2G-P5-R2C adds canonical request-level decision precedence while preserving issuance-time policy routing.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Exact tenant-scoped opaque references; no provider transport or secrets.
TENANT BOUNDARY: Platform request, policy, decision, and replay checks are exact tenant scoped.
AUTHORITY BOUNDARY: Provider routing only; no generic command, execution, attempt, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS owns later financial execution and settlement.
TRANSACTION BOUNDARY: Caller supplies one active transaction; every registry operation receives that session.
FAIL-CLOSED DECLARATION: Missing, divergent, corrupt, ambiguous, or conflicting routing evidence rejects.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from tools.eos.saas.billing.platform_billing_financial_execution_request_registry import PlatformBillingFinancialExecutionRequestRegistry
from tools.eos.kennel.registry.platform_billing_provider_policy_registry import PlatformBillingProviderPolicyRegistry
from tools.eos.kennel.domain.platform_billing_provider_routing_decision import PlatformBillingProviderRoutingDecision
from tools.eos.kennel.registry.platform_billing_provider_routing_decision_registry import PlatformBillingProviderRoutingDecisionRegistry


def route_platform_billing_request(
    tenant_id: str,
    execution_request_id: str,
    routing_decision_id: str,
    database: Any,
    *,
    session: Any,
) -> tuple[PlatformBillingProviderRoutingDecision, bool]:
    """Return the exact request-level P4 decision or create its first routing fact.

    The caller-provided routing decision ID remains first-issuance identity only.
    Once a tenant/request decision exists, it is strictly correlated and returned
    before policy lookup; a different caller ID cannot create a second decision.
    The request's issuance-time policy provenance remains the sole provider
    authority. This transition never creates a generic command or executes funds.
    """
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise RuntimeError("ACTIVE_TRANSACTION_REQUIRED")
    request_collection = database["platform_billing_financial_execution_requests"]
    decision_collection = database["platform_billing_provider_routing_decisions"]
    request = PlatformBillingFinancialExecutionRequestRegistry.get(
        tenant_id,
        execution_request_id,
        request_collection,
        session=session,
    )
    existing = PlatformBillingProviderRoutingDecisionRegistry.get_by_request(
        tenant_id,
        execution_request_id,
        decision_collection,
        session=session,
    )
    if existing is not None:
        if (
            existing.tenant_id != request.tenant_id
            or existing.source_execution_request_id != request.execution_request_id
            or existing.source_execution_request_fingerprint != request.fingerprint
            or existing.source_provider_policy_id != request.provider_policy_id
            or existing.source_provider_policy_revision != request.provider_policy_revision
            or existing.source_provider_policy_fingerprint != request.provider_policy_fingerprint
        ):
            raise RuntimeError("ROUTING_DECISION_REQUEST_CORRELATION_INVALID")
        return existing, True

    policy = PlatformBillingProviderPolicyRegistry.get(
        tenant_id,
        request.provider_policy_id,
        database["platform_billing_provider_policies"],
        revision=request.provider_policy_revision,
        session=session,
    )
    if policy is None or policy.policy_fingerprint != request.provider_policy_fingerprint:
        raise RuntimeError("ROUTING_BOUND_POLICY_INVALID")
    if len(policy.authorized_provider_names) != 1:
        raise RuntimeError("ROUTING_PROVIDER_AMBIGUOUS")
    value = PlatformBillingProviderRoutingDecision(
        tenant_id,
        routing_decision_id,
        request.execution_request_id,
        request.fingerprint,
        policy.policy_id,
        policy.policy_revision,
        policy.policy_fingerprint,
        policy.authorized_provider_names[0],
        datetime.now(timezone.utc),
    )
    return PlatformBillingProviderRoutingDecisionRegistry.create(
        value,
        decision_collection,
        session=session,
    )


# ARTIFACT: platform_billing_provider_routing.py
# VERSION: v1.1.0-M11E2D5C2G-P5-R2C
# AUTHORITY BOUNDARY: request-level P4 routing only; no generic command or execution.
# TENANT POSTURE: exact tenant/source-request scope.
# FAIL-CLOSED POSTURE: ambiguity, corruption, divergence, and duplicate requests reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
