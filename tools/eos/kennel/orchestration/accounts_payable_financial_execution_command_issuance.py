"""TITLE: Accounts Payable Financial Execution Command Issuance.
VERSION: v1.0.0-M11-P5-R2B-R2.
AUTHORITY: Wilsy OS Core Governance / Kennel EOS.
EPITOME: Canonical AP request and frozen R3 selection bridge into one generic command.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/orchestration/accounts_payable_financial_execution_command_issuance.py
COLLABORATION / OWNERSHIP: Kennel EOS AP command-composition owner; consumes AP request, R3 selection, and generic command registry.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v1.0.0-M11-P5-R2B-R2 establishes caller-transaction composition, existing-command precedence, deterministic AP command identity, and typed source provenance.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque tenant-scoped references only; no provider credentials or transport payloads.
TENANT BOUNDARY: Every request, command, selection, and persistence operation is exact tenant scoped.
AUTHORITY BOUNDARY: AP command composition only; provider policy and selection authority remain in frozen R3.
FINANCIAL AUTHORITY BOUNDARY: No attempt, provider execution, execution truth, settlement, paid state, or receivable closure.
TRANSACTION BOUNDARY: Caller supplies one active session; this bridge never owns its lifecycle.
FAIL-CLOSED DECLARATION: Missing, cross-tenant, divergent, stale, corrupt, or mismatched authority rejects without fallback.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, NoReturn

from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from tools.eos.kennel.domain.financial_execution_command import (
    AccountsPayableCommandSource,
    FinancialExecutionCommand,
    FinancialExecutionCommandFamily,
)
from tools.eos.kennel.domain.accounts_payable_provider_selection_decision import (
    AccountsPayableProviderSelectionDecision,
)
from tools.eos.kennel.orchestration.accounts_payable_provider_selection import (
    select_accounts_payable_provider,
)
from tools.eos.kennel.registry.financial_execution_command_registry import (
    FinancialExecutionCommandRegistry,
)
from tools.eos.saas.billing.vendor_bill_financial_execution_request_registry import (
    VendorBillFinancialExecutionRequestRegistry,
)
from tools.eos.saas.domain.vendor_bill_financial_execution_request import (
    VendorBillFinancialExecutionRequest,
)

VERSION = "v1.0.0-M11-P5-R2B-R2"


class AccountsPayableFinancialExecutionCommandIssuanceError(RuntimeError):
    """Raised when the canonical AP command transition cannot be composed safely."""


def _require_active_transaction(session: ClientSession | None) -> ClientSession:
    """Require an already-active caller transaction before any authority read."""
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise AccountsPayableFinancialExecutionCommandIssuanceError("ACTIVE_TRANSACTION_REQUIRED")
    return session


def _rethrow(error: Exception) -> NoReturn:
    """Expose a stable bridge error while preserving fail-closed rejection."""
    code = str(error) or "AP_FINANCIAL_EXECUTION_COMMAND_FAILED"
    raise AccountsPayableFinancialExecutionCommandIssuanceError(code) from error


def _derive_command_id(tenant_id: str, execution_request_id: str) -> str:
    """Derive the deterministic AP command identity from its exact identity tuple."""
    payload = {
        "execution_request_id": execution_request_id,
        "source_authority_kind": FinancialExecutionCommandFamily.ACCOUNTS_PAYABLE.value,
        "tenant_id": tenant_id,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _correlate_existing(
    command: FinancialExecutionCommand,
    request: VendorBillFinancialExecutionRequest,
) -> None:
    """Require exact durable command/request correlation before returning replay."""
    source = command.source_authority
    if type(source) is not AccountsPayableCommandSource:
        raise AccountsPayableFinancialExecutionCommandIssuanceError(
            "EXISTING_COMMAND_REQUEST_CORRELATION_INVALID"
        )
    if (
        command.source_authority_kind is not FinancialExecutionCommandFamily.ACCOUNTS_PAYABLE
        or command.tenant_id != request.tenant_id
        or command.execution_command_id != _derive_command_id(request.tenant_id, request.execution_command_id)
        or source.execution_request_id != request.execution_command_id
        or source.execution_request_fingerprint != request.fingerprint
        or source.payable_id != request.payable_id
        or source.release_authorization_id != request.release_authorization_id
        or command.amount_minor != request.amount_minor
        or command.currency != request.currency
        or command.payment_destination_reference != request.payment_destination_reference
        or command.idempotency_key != request.idempotency_key
        or command.created_at != request.requested_at
    ):
        raise AccountsPayableFinancialExecutionCommandIssuanceError(
            "EXISTING_COMMAND_REQUEST_CORRELATION_INVALID"
        )


def _correlate_selection(
    selection: AccountsPayableProviderSelectionDecision,
    request: VendorBillFinancialExecutionRequest,
) -> None:
    """Require the frozen R3 selection to belong to the canonical AP request."""
    if (
        selection.tenant_id != request.tenant_id
        or selection.execution_request_id != request.execution_command_id
        or selection.execution_request_fingerprint != request.fingerprint
    ):
        raise AccountsPayableFinancialExecutionCommandIssuanceError(
            "SELECTION_REQUEST_CORRELATION_INVALID"
        )


def issue_accounts_payable_financial_execution_command(
    tenant_id: str,
    execution_request_id: str,
    *,
    request_collection: Collection,
    binding_collection: Collection,
    policy_collection: Collection,
    selection_collection: Collection,
    command_collection: Collection,
    session: ClientSession,
) -> FinancialExecutionCommand:
    """Compose one canonical AP request and frozen R3 selection into a command.

    The bridge accepts only tenant/request identity, dependency collections, and
    an active caller session. It first returns an existing strictly correlated
    command; only absent commands invoke R3. All command material is copied from
    canonical request/selection facts, and persistence is delegated to the
    family-aware generic registry.

    :raises AccountsPayableFinancialExecutionCommandIssuanceError: when any
        authority is missing, inactive, divergent, corrupt, or mismatched.
    :returns: the created or exact-replayed durable generic command.
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
        _rethrow(error)
    if request.tenant_id != tenant_id or request.execution_command_id != execution_request_id:
        raise AccountsPayableFinancialExecutionCommandIssuanceError("REQUEST_CORRELATION_INVALID")

    try:
        existing = FinancialExecutionCommandRegistry.get_by_source_request(
            tenant_id,
            FinancialExecutionCommandFamily.ACCOUNTS_PAYABLE,
            execution_request_id,
            command_collection,
            session=tx,
        )
    except Exception as error:
        _rethrow(error)
    if existing is not None:
        _correlate_existing(existing, request)
        return existing

    try:
        selection, _ = select_accounts_payable_provider(
            tenant_id,
            execution_request_id,
            request_collection=request_collection,
            binding_collection=binding_collection,
            policy_collection=policy_collection,
            selection_collection=selection_collection,
            session=tx,
        )
    except Exception as error:
        _rethrow(error)
    _correlate_selection(selection, request)

    source = AccountsPayableCommandSource(
        execution_request_id=request.execution_command_id,
        execution_request_fingerprint=request.fingerprint,
        selection_decision_id=selection.selection_decision_id,
        selection_decision_fingerprint=selection.selection_decision_fingerprint,
        payable_id=request.payable_id,
        release_authorization_id=request.release_authorization_id,
        authorized_provider_name=selection.selected_provider,
    )
    command = FinancialExecutionCommand(
        tenant_id=request.tenant_id,
        execution_command_id=_derive_command_id(request.tenant_id, request.execution_command_id),
        idempotency_key=request.idempotency_key,
        amount_minor=request.amount_minor,
        currency=request.currency,
        payment_destination_reference=request.payment_destination_reference,
        source_authority=source,
        provider_name=selection.selected_provider,
        created_at=request.requested_at,
        provider_metadata_reference=None,
    )
    try:
        result = FinancialExecutionCommandRegistry.create(command, command_collection, session=tx)
    except Exception as error:
        _rethrow(error)
    return result.command


# ARTIFACT: accounts_payable_financial_execution_command_issuance.py
# VERSION: v1.0.0-M11-P5-R2B-R2
# AUTHORITY BOUNDARY: canonical AP command composition only; no provider execution or settlement.
# TENANT POSTURE: exact tenant-scoped request, selection, and command provenance.
# FAIL-CLOSED POSTURE: missing, corrupt, divergent, and mismatched evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
