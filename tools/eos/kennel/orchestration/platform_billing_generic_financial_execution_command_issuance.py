"""TITLE: Platform Billing Generic Financial Execution Command Issuance.
VERSION: v1.0.0-M11E2D5C2G-P5-R2C-R2.
AUTHORITY: Wilsy OS Core Governance / Kennel EOS.
EPITOME: Compose one canonical Platform request and pre-existing P4 decision into generic command authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/orchestration/platform_billing_generic_financial_execution_command_issuance.py
COLLABORATION / OWNERSHIP: Kennel EOS Platform generic-command composition owner.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v1.0.0-M11E2D5C2G-P5-R2C-R2 establishes request-first command precedence, frozen P4 provenance composition, and canonical generic persistence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque tenant-scoped references only; no credentials, provider payloads, or transport secrets.
TENANT BOUNDARY: Every request, P4 decision, command lookup, correlation, and persistence operation is exact tenant scoped.
AUTHORITY BOUNDARY: Platform generic command composition only; P4 remains the provider-routing authority.
FINANCIAL AUTHORITY BOUNDARY: No attempt, provider execution, execution truth, settlement, paid state, or receivable mutation.
TRANSACTION BOUNDARY: Caller supplies one active session; this bridge never starts, commits, aborts, or retries transactions.
FAIL-CLOSED DECLARATION: Missing, corrupt, divergent, stale, cross-tenant, or mismatched authority rejects without rerouting or reconstruction.
"""
from __future__ import annotations

import hashlib
import json
from typing import NoReturn

from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from tools.eos.kennel.domain.financial_execution_command import (
    FinancialExecutionCommand,
    FinancialExecutionCommandFamily,
    PlatformBillingCommandSource,
)
from tools.eos.kennel.domain.platform_billing_provider_routing_decision import (
    PlatformBillingProviderRoutingDecision,
)
from tools.eos.kennel.registry.financial_execution_command_registry import (
    FinancialExecutionCommandRegistry,
)
from tools.eos.kennel.registry.platform_billing_provider_routing_decision_registry import (
    PlatformBillingProviderRoutingDecisionRegistry,
)
from tools.eos.saas.billing.platform_billing_financial_execution_request_registry import (
    PlatformBillingFinancialExecutionRequestRegistry,
)
from tools.eos.saas.domain.platform_billing_financial_execution_request import (
    PlatformBillingFinancialExecutionRequest,
)

VERSION = "v1.0.0-M11E2D5C2G-P5-R2C-R2"


class PlatformBillingGenericFinancialExecutionCommandIssuanceError(RuntimeError):
    """Raised when Platform generic-command authority cannot be composed safely."""


def _require_active_transaction(session: ClientSession | None) -> ClientSession:
    """Require an already-active caller transaction before any authority read."""
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise PlatformBillingGenericFinancialExecutionCommandIssuanceError(
            "ACTIVE_TRANSACTION_REQUIRED"
        )
    return session


def _rethrow(error: Exception) -> NoReturn:
    """Expose a stable bridge error while preserving fail-closed rejection."""
    code = str(error) or "PLATFORM_GENERIC_FINANCIAL_EXECUTION_COMMAND_FAILED"
    raise PlatformBillingGenericFinancialExecutionCommandIssuanceError(code) from error


def _derive_command_id(tenant_id: str, execution_request_id: str) -> str:
    """Derive the generic Platform command identity from tenant, family, and request."""
    payload = {
        "execution_request_id": execution_request_id,
        "source_authority_kind": FinancialExecutionCommandFamily.PLATFORM_BILLING.value,
        "tenant_id": tenant_id,
    }
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _correlate_existing(
    command: FinancialExecutionCommand,
    request: PlatformBillingFinancialExecutionRequest,
) -> None:
    """Require exact existing-command correlation to the canonical Platform request."""
    source = command.source_authority
    if type(source) is not PlatformBillingCommandSource:
        raise PlatformBillingGenericFinancialExecutionCommandIssuanceError(
            "EXISTING_COMMAND_REQUEST_CORRELATION_INVALID"
        )
    if (
        command.source_authority_kind is not FinancialExecutionCommandFamily.PLATFORM_BILLING
        or command.tenant_id != request.tenant_id
        or command.execution_command_id
        != _derive_command_id(request.tenant_id, request.execution_request_id)
        or source.execution_request_id != request.execution_request_id
        or source.execution_request_fingerprint != request.fingerprint
        or source.platform_invoice_id != request.platform_invoice_id
        or source.release_authorization_id != request.release_authorization_id
        or source.release_authorization_fingerprint
        != request.release_authorization_fingerprint
        or command.amount_minor != request.amount_minor
        or command.currency != request.currency
        or command.payment_destination_reference != request.payment_destination_reference
        or command.idempotency_key != request.idempotency_key
        or command.created_at != request.requested_at
    ):
        raise PlatformBillingGenericFinancialExecutionCommandIssuanceError(
            "EXISTING_COMMAND_REQUEST_CORRELATION_INVALID"
        )


def _correlate_p4(
    request: PlatformBillingFinancialExecutionRequest,
    decision: PlatformBillingProviderRoutingDecision,
) -> None:
    """Require exact immutable P4/request provenance before command composition."""
    if (
        decision.tenant_id != request.tenant_id
        or decision.source_execution_request_id != request.execution_request_id
        or decision.source_execution_request_fingerprint != request.fingerprint
        or decision.source_provider_policy_id != request.provider_policy_id
        or decision.source_provider_policy_revision != request.provider_policy_revision
        or decision.source_provider_policy_fingerprint
        != request.provider_policy_fingerprint
    ):
        raise PlatformBillingGenericFinancialExecutionCommandIssuanceError(
            "P4_REQUEST_CORRELATION_INVALID"
        )


def issue_platform_billing_generic_financial_execution_command(
    tenant_id: str,
    execution_request_id: str,
    *,
    request_collection: Collection,
    routing_collection: Collection,
    command_collection: Collection,
    session: ClientSession,
) -> FinancialExecutionCommand:
    """Compose one durable generic Platform command from request and pre-existing P4.

    The caller supplies only tenant/request identity, dependency collections, and
    an active transaction session. Existing generic command authority is read and
    strictly correlated first. Only when absent is the canonical request-level P4
    decision read; no P4 routing transition, provider policy lookup, routing-ID
    generation, platform-specific command, or caller override is accepted.

    :raises PlatformBillingGenericFinancialExecutionCommandIssuanceError: when
        authority is missing, inactive, divergent, corrupt, or mismatched.
    :returns: the newly persisted or exact-replayed generic Platform command.
    """
    tx = _require_active_transaction(session)

    try:
        request = PlatformBillingFinancialExecutionRequestRegistry.get(
            tenant_id,
            execution_request_id,
            request_collection,
            session=tx,
        )
    except Exception as error:
        _rethrow(error)
    if (
        request.tenant_id != tenant_id
        or request.execution_request_id != execution_request_id
    ):
        raise PlatformBillingGenericFinancialExecutionCommandIssuanceError(
            "REQUEST_CORRELATION_INVALID"
        )

    try:
        existing = FinancialExecutionCommandRegistry.get_by_source_request(
            tenant_id,
            FinancialExecutionCommandFamily.PLATFORM_BILLING,
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
        decision = PlatformBillingProviderRoutingDecisionRegistry.get_by_request(
            tenant_id,
            execution_request_id,
            routing_collection,
            session=tx,
        )
    except Exception as error:
        _rethrow(error)
    if decision is None:
        raise PlatformBillingGenericFinancialExecutionCommandIssuanceError(
            "P4_ROUTING_DECISION_REQUIRED"
        )
    _correlate_p4(request, decision)

    source = PlatformBillingCommandSource(
        execution_request_id=request.execution_request_id,
        execution_request_fingerprint=request.fingerprint,
        routing_decision_id=decision.routing_decision_id,
        routing_decision_fingerprint=decision.routing_decision_fingerprint,
        platform_invoice_id=request.platform_invoice_id,
        release_authorization_id=request.release_authorization_id,
        release_authorization_fingerprint=request.release_authorization_fingerprint,
        authorized_provider_name=decision.selected_provider,
    )
    command = FinancialExecutionCommand(
        tenant_id=request.tenant_id,
        execution_command_id=_derive_command_id(
            request.tenant_id, request.execution_request_id
        ),
        idempotency_key=request.idempotency_key,
        amount_minor=request.amount_minor,
        currency=request.currency,
        payment_destination_reference=request.payment_destination_reference,
        source_authority=source,
        provider_name=decision.selected_provider,
        created_at=request.requested_at,
        provider_metadata_reference=None,
    )
    try:
        result = FinancialExecutionCommandRegistry.create(
            command, command_collection, session=tx
        )
    except Exception as error:
        _rethrow(error)
    return result.command


# ARTIFACT: platform_billing_generic_financial_execution_command_issuance.py
# VERSION: v1.0.0-M11E2D5C2G-P5-R2C-R2
# AUTHORITY BOUNDARY: canonical Platform generic-command composition only; no provider execution or settlement.
# TENANT POSTURE: exact tenant-scoped request, P4, and generic-command provenance.
# FAIL-CLOSED POSTURE: missing, corrupt, divergent, and mismatched authority rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
