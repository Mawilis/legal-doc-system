"""TITLE: Accounts Payable Provider Selection Orchestration.
VERSION: v1.0.0-M11-P5-R1B-AP2D-R3.
AUTHORITY: Kennel EOS canonical AP provider-selection transition.
EPITOME: Converts durable AP request, explicit current binding, and exact bound policy into one canonical selection fact.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/orchestration/accounts_payable_provider_selection.py
COLLABORATION / OWNERSHIP: Kennel EOS AP2D orchestration owner; consumes SaaS request and AP policy authorities.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 establishes caller-transaction-owned AP selection with strict provenance and provider-cardinality enforcement.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Exact tenant-scoped opaque identifiers; no provider transport or secrets.
TENANT BOUNDARY: Request, binding, policy, selection, and all conflict checks remain tenant exact.
AUTHORITY BOUNDARY: One AP provider-selection transition only; no policy activation, command issuance, or execution.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS owns later execution and settlement; this transition moves no money.
TRANSACTION BOUNDARY: Caller supplies one already-active Mongo transaction; this module never owns its lifecycle.
FAIL-CLOSED DECLARATION: Missing, cross-tenant, stale, corrupt, ambiguous, or divergent evidence rejects without fallback.
"""
from __future__ import annotations

from typing import Any, NoReturn

from tools.eos.kennel.domain.accounts_payable_provider_policy import AP_POLICY_FAMILY
from tools.eos.kennel.domain.accounts_payable_provider_selection_decision import (
    AccountsPayableProviderSelectionDecision,
)
from tools.eos.kennel.registry.accounts_payable_provider_policy_registry import (
    AccountsPayableProviderPolicyRegistry,
)
from tools.eos.kennel.registry.accounts_payable_provider_policy_runtime_binding_registry import (
    AccountsPayableProviderPolicyRuntimeBindingRegistry,
)
from tools.eos.kennel.registry.accounts_payable_provider_selection_decision_registry import (
    AccountsPayableProviderSelectionDecisionRegistry,
)
from tools.eos.saas.billing.vendor_bill_financial_execution_request_registry import (
    VendorBillFinancialExecutionRequestRegistry,
)


class AccountsPayableProviderSelectionOrchestrationError(RuntimeError):
    """Raised when canonical AP selection evidence cannot be composed safely."""


def _require_active_transaction(session: Any) -> Any:
    """Require an already-active caller transaction before any authority read."""
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise AccountsPayableProviderSelectionOrchestrationError("ACTIVE_TRANSACTION_REQUIRED")
    return session


def _rethrow_registry_error(error: Exception) -> NoReturn:
    """Expose a stable orchestration error code without weakening fail-closed behavior."""
    code = str(error) or "AP_PROVIDER_SELECTION_FAILED"
    raise AccountsPayableProviderSelectionOrchestrationError(code) from error


def select_accounts_payable_provider(
    tenant_id: str,
    execution_request_id: str,
    *,
    request_collection: Any,
    binding_collection: Any,
    policy_collection: Any,
    selection_collection: Any,
    session: Any = None,
) -> tuple[AccountsPayableProviderSelectionDecision, bool]:
    """Select and durably record the sole eligible provider for one AP request.

    The caller supplies only the tenant/request lookup identity and persistence
    collections.  The durable request supplies request provenance, the explicit
    current runtime binding supplies policy provenance, and that exact historical
    policy supplies provider eligibility.  An existing canonical selection is
    returned before current binding or policy lookup, so later currentness changes
    cannot create a second selection authority.  The caller-owned transaction is
    propagated to every read and the canonical registry write; this function never
    starts, commits, aborts, or retries a transaction and never executes a provider.

    :raises AccountsPayableProviderSelectionOrchestrationError: if any authority
        is missing, cross-tenant, corrupt, ambiguous, divergent, or not active.
    :returns: the canonical selection and the registry replay flag.
    """
    tx = _require_active_transaction(session)

    try:
        request = VendorBillFinancialExecutionRequestRegistry.get(
            tenant_id,
            execution_request_id,
            request_collection,
            session=tx,
        )
    except Exception as error:
        _rethrow_registry_error(error)

    try:
        existing = AccountsPayableProviderSelectionDecisionRegistry.get_by_request(
            tenant_id,
            execution_request_id,
            selection_collection,
            session=tx,
        )
    except Exception as error:
        _rethrow_registry_error(error)

    if existing is not None:
        if (
            existing.tenant_id != request.tenant_id
            or existing.execution_request_id != request.execution_command_id
            or existing.execution_request_fingerprint != request.fingerprint
        ):
            raise AccountsPayableProviderSelectionOrchestrationError(
                "SELECTION_REQUEST_CORRELATION_INVALID"
            )
        return existing, True

    try:
        binding = AccountsPayableProviderPolicyRuntimeBindingRegistry.current(
            tenant_id,
            binding_collection,
            session=tx,
        )
    except Exception as error:
        _rethrow_registry_error(error)
    if binding is None:
        raise AccountsPayableProviderSelectionOrchestrationError("CURRENT_BINDING_REQUIRED")
    if binding.tenant_id != request.tenant_id or binding.family != AP_POLICY_FAMILY:
        raise AccountsPayableProviderSelectionOrchestrationError("BINDING_REQUEST_CORRELATION_INVALID")

    try:
        policy = AccountsPayableProviderPolicyRegistry.get(
            binding.tenant_id,
            binding.provider_policy_id,
            policy_collection,
            revision=binding.provider_policy_revision,
            session=tx,
        )
    except Exception as error:
        _rethrow_registry_error(error)
    if policy.tenant_id != binding.tenant_id:
        raise AccountsPayableProviderSelectionOrchestrationError("POLICY_BINDING_CORRELATION_INVALID")
    if policy.policy_id != binding.provider_policy_id or policy.policy_revision != binding.provider_policy_revision:
        raise AccountsPayableProviderSelectionOrchestrationError("POLICY_BINDING_CORRELATION_INVALID")
    if policy.policy_fingerprint != binding.provider_policy_fingerprint:
        raise AccountsPayableProviderSelectionOrchestrationError("POLICY_BINDING_CORRELATION_INVALID")

    eligible = policy.eligible_provider_names
    if len(eligible) == 0:
        raise AccountsPayableProviderSelectionOrchestrationError("NO_ELIGIBLE_PROVIDERS")
    if len(eligible) != 1:
        raise AccountsPayableProviderSelectionOrchestrationError("MULTIPLE_ELIGIBLE_PROVIDERS")

    value = AccountsPayableProviderSelectionDecision(
        tenant_id=request.tenant_id,
        execution_request_id=request.execution_command_id,
        execution_request_fingerprint=request.fingerprint,
        runtime_binding_id=binding.binding_id,
        runtime_binding_revision=binding.binding_revision,
        runtime_binding_fingerprint=binding.binding_fingerprint,
        provider_policy_id=policy.policy_id,
        provider_policy_revision=policy.policy_revision,
        provider_policy_fingerprint=policy.policy_fingerprint,
        selected_provider=eligible[0],
    )
    try:
        return AccountsPayableProviderSelectionDecisionRegistry.create(
            value,
            selection_collection,
            session=tx,
        )
    except Exception as error:
        _rethrow_registry_error(error)


# ARTIFACT: accounts_payable_provider_selection.py
# VERSION: v1.0.0-M11-P5-R1B-AP2D-R3
# AUTHORITY BOUNDARY: canonical AP provider selection only; no command or execution
# TENANT POSTURE: exact tenant-scoped request, binding, policy, and selection provenance
# FAIL-CLOSED POSTURE: missing, corrupt, ambiguous, cross-tenant, and divergent evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
