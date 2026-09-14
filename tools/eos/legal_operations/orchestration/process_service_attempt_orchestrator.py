"""Caller-transaction-owned P5C handoff from durable attempt authority.

TITLE: Wilsy OS Process-Service Attempt Orchestrator
VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-ORCHESTRATOR
AUTHORITY: Wilsy OS Core Governance
EPITOME: Convert one tenant-scoped durable P5B attempt-authority receipt into
         the initial P1 ``ServiceAttempt`` snapshot and persist that snapshot
         through P2 in the caller's transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/process_service_attempt_orchestrator.py
COLLABORATION / OWNERSHIP: P5C owns composition only. P5B remains the sole
                            durable attempt-authority source; P1 owns attempt
                            lifecycle semantics; P2 owns lifecycle evidence
                            persistence; the caller owns the Mongo session and
                            transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ATTEMPT-ORCHESTRATOR establishes
           the fail-closed P5B-to-P1 initial-attempt handoff using one
           caller-owned Mongo session and transaction.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Reads and forwards opaque tenant and evidence
                             identities only; no network, provider, secret,
                             credential, or PII expansion occurs.
TENANT BOUNDARY: The caller supplies an explicit tenant scope and a durable
                 P5B authority locator. P5B lookup and P2 persistence retain
                 that exact tenant scope; a receipt from another tenant rejects.
AUTHORITY BOUNDARY: Orchestration only. P5B is the sole durable authority read;
                    this module creates only the initial P1 ALLOCATED snapshot
                    and never transitions an attempt or creates service,
                    execution, return, custody, IAM, or transport authority.
FINANCIAL AUTHORITY BOUNDARY: No billing, invoice, payment, execution, or
                              settlement authority exists here. Kennel EOS
                              exclusively owns financial execution and
                              settlement.
TRANSACTION BOUNDARY: An already-active caller-owned Mongo transaction is
                      required. The orchestrator never starts, commits,
                      aborts, retries, or stores a Mongo client.
FAIL-CLOSED DECLARATION: Invalid scope, locator, source receipt, lifecycle
                         construction, persistence, tenant correlation, and
                         transaction inputs reject without fabricating state.
"""
from __future__ import annotations

from typing import Any, Final, NoReturn, cast
import re

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    LegalOperationsLifecycleError,
    ServiceAttempt,
    ServiceAttemptState,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
    LegalOperationsLifecycleRegistryError,
)
from tools.eos.legal_operations.registry.process_service_attempt_authority_registry import (
    ProcessServiceAttemptAuthorityReceipt,
    ProcessServiceAttemptAuthorityRegistry,
    ProcessServiceAttemptAuthorityRegistryError,
)


VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-ATTEMPT-ORCHESTRATOR"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "global_root", "root", "master", "*"})


class ProcessServiceAttemptOrchestratorError(RuntimeError):
    """Stable P5C composition failure.

    This error carries no lifecycle, service, custody, financial, or
    transaction authority. Upstream P5B and P2 governed errors remain intact
    so their durable not-found, corruption, persistence, replay, and
    transaction semantics are not reinterpreted by orchestration.
    """

    default_code: str = "P5C_ORCHESTRATION_ERROR"

    def __init__(self, code: str | None = None) -> None:
        self.code = code or self.default_code
        super().__init__(self.code)


class ProcessServiceAttemptOrchestratorInputError(ProcessServiceAttemptOrchestratorError):
    """Explicit P5C scope, locator, source, or P1 construction failure."""

    default_code: str = "P5C_INPUT_INVALID"


class ProcessServiceAttemptOrchestratorTransactionRequiredError(ProcessServiceAttemptOrchestratorError):
    """Caller did not provide an already-active Mongo transaction session."""

    default_code: str = "P5C_ACTIVE_TRANSACTION_REQUIRED"


def _fail_input(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable P5C input error while retaining technical context."""
    error = ProcessServiceAttemptOrchestratorInputError(code)
    if cause is None:
        raise error
    raise error from cause


def _tenant(value: object) -> str:
    """Require explicit non-pseudo tenant scope without inventing defaults."""
    if not isinstance(value, str) or _IDENTITY.fullmatch(value) is None:
        _fail_input("P5C_TENANT_INVALID")
    tenant = cast(str, value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail_input("P5C_TENANT_INVALID")
    return tenant


def _authority_locator(value: object) -> str:
    """Require the canonical P5B authority identity used only as a locator."""
    if not isinstance(value, str) or _IDENTITY.fullmatch(value) is None:
        _fail_input("P5C_ATTEMPT_AUTHORITY_ID_INVALID")
    return cast(str, value)


def _active_transaction(session: object) -> object:
    """Require an active caller transaction without taking ownership of it."""
    if session is None:
        raise ProcessServiceAttemptOrchestratorTransactionRequiredError()
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        raise ProcessServiceAttemptOrchestratorTransactionRequiredError() from error
    if active is not True:
        raise ProcessServiceAttemptOrchestratorTransactionRequiredError()
    return session


def _validated_receipt(
    value: object,
) -> ProcessServiceAttemptAuthorityReceipt:
    """Require the exact P5B receipt type and replay its own validation."""
    if type(value) is not ProcessServiceAttemptAuthorityReceipt:
        _fail_input("P5C_P5B_RECEIPT_INVALID")
    receipt = cast(ProcessServiceAttemptAuthorityReceipt, value)
    try:
        receipt.__post_init__()
    except ProcessServiceAttemptAuthorityRegistryError as error:
        _fail_input("P5C_P5B_RECEIPT_INVALID", error)
    except Exception as error:
        _fail_input("P5C_P5B_RECEIPT_INVALID", error)
    return receipt


def _initial_attempt(receipt: ProcessServiceAttemptAuthorityReceipt) -> ServiceAttempt:
    """Derive only the canonical initial P1 ALLOCATED attempt from P5B."""
    try:
        attempt = ServiceAttempt(
            tenant_id=receipt.tenant_id,
            attempt_id=receipt.attempt_id,
            instruction_id=receipt.instruction_id,
            document_id=receipt.document_id,
            deputy_id=receipt.deputy_id,
            allocated_at=receipt.allocated_at,
            allocation_evidence_reference=receipt.allocation_evidence_reference,
            state=ServiceAttemptState.ALLOCATED,
            transition_history=(),
        )
    except LegalOperationsLifecycleError as error:
        _fail_input("P5C_P1_ATTEMPT_INVALID", error)
    except Exception as error:
        _fail_input("P5C_P1_ATTEMPT_INVALID", error)
    return attempt


def orchestrate_process_service_attempt(
    *,
    tenant_id: str,
    attempt_authority_id: str,
    attempt_authority_collection: Any,
    lifecycle_collection: Any,
    session: object,
) -> ServiceAttempt:
    """Handoff one durable P5B receipt into an initial persisted P1 attempt.

    ``tenant_id`` is an explicit lookup scope and ``attempt_authority_id`` is
    only a locator. All authority-bearing attempt identities, allocation
    provenance, and timestamps are derived from the strictly hydrated P5B
    receipt. The same already-active caller session is passed to the P5B read
    and P2 ``create`` call. This function never manages transaction lifecycle,
    retries, or persistence outside the supplied transaction, and it never
    creates an attempt state beyond ``ALLOCATED``.

    P5B registry errors and P2 registry errors are deliberately propagated
    unchanged. P5C wraps only malformed orchestration inputs or invalid
    derived P1 construction in stable P5C input errors.
    """
    tx = _active_transaction(session)
    tenant = _tenant(tenant_id)
    authority_id = _authority_locator(attempt_authority_id)

    try:
        durable_receipt = ProcessServiceAttemptAuthorityRegistry.get_by_attempt_authority_id(
            tenant,
            authority_id,
            attempt_authority_collection,
            session=tx,
        )
    except ProcessServiceAttemptAuthorityRegistryError:
        raise
    receipt = _validated_receipt(durable_receipt)
    if receipt.tenant_id != tenant or receipt.attempt_authority_id != authority_id:
        _fail_input("P5C_P5B_SCOPE_MISMATCH")

    attempt = _initial_attempt(receipt)
    try:
        persisted = LegalOperationsLifecycleRegistry.create(
            attempt,
            lifecycle_collection,
            session=tx,
        )
    except LegalOperationsLifecycleRegistryError:
        raise
    if type(persisted) is not ServiceAttempt:
        _fail_input("P5C_P2_ATTEMPT_INVALID")
    persisted_attempt = cast(ServiceAttempt, persisted)
    if persisted_attempt.to_dict() != attempt.to_dict() or persisted_attempt.fingerprint != attempt.fingerprint:
        _fail_input("P5C_P2_REPLAY_DIVERGENCE")
    return persisted_attempt


__all__ = [
    "VERSION",
    "ProcessServiceAttemptOrchestratorError",
    "ProcessServiceAttemptOrchestratorInputError",
    "ProcessServiceAttemptOrchestratorTransactionRequiredError",
    "orchestrate_process_service_attempt",
]


# ARTIFACT: process_service_attempt_orchestrator.py
# VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-ORCHESTRATOR
# AUTHORITY BOUNDARY: P5C composition of one durable P5B receipt into an initial
#                      P1 ALLOCATED attempt persisted by P2 only.
# TENANT POSTURE: explicit tenant scope is preserved through P5B read and P2 write.
# FAIL-CLOSED POSTURE: malformed, mismatched, corrupt, unavailable, and divergent
#                      evidence rejects without fabricated lifecycle state.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
