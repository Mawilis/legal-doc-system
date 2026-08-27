"""WILSY OS — VENDOR BILL RELEASE-AUTHORIZATION ORCHESTRATOR

VERSION: v1.0.1-VENDOR-BILL-RELEASE-ORCHESTRATOR-EXACT-REPLAY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Caller-owned transaction orchestration that creates immutable release
evidence only; Kennel EOS exclusively executes financial transactions.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/vendor_bill_release_orchestrator.py
ARCHITECTURE: APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
CHANGELOG: v1.0.1 adds fail-closed exact replay comparison across all
caller-controlled authorization command semantics.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Optional

from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import OperationFailure

from ...kernel.db import get_database
from ..domain.vendor_bill_release_authorization import VendorBillReleaseAuthorization
from ..domain.vendor_bill_release_policy import evaluate_vendor_bill_release_eligibility, fingerprint_financial_approval_effective_result
from .vendor_bill_registry import VendorBillRegistry
from .vendor_bill_release_authorization_registry import VendorBillReleaseAuthorizationRegistry, VendorBillReleaseAuthorizationNotFoundError
from .financial_approval_effective_result_registry import FinancialApprovalEffectiveResultRegistry

_MAX_TRANSACTION_ATTEMPTS = 3


def _authorization_matches_command(
    authorization: VendorBillReleaseAuthorization,
    command: VendorBillReleaseCommand,
) -> bool:
    """Compare every caller-controlled field represented by durable evidence."""
    return (
        authorization.tenant_id == command.tenant_id
        and authorization.payable_id == command.payable_id
        and authorization.release_authorization_id == command.release_authorization_id
        and authorization.authorized_amount_minor == command.requested_amount_minor
        and authorization.currency == command.currency
        and authorization.authorized_by_actor_id == command.authorized_by_actor_id
        and authorization.authorization_basis_reference == command.authorization_basis_reference
        and authorization.authorized_at == command.authorized_at
    )


class VendorBillReleaseOrchestrationError(RuntimeError):
    """Stable orchestration boundary error; no execution authority is granted."""


class VendorBillReleaseOrchestrationIdempotencyError(VendorBillReleaseOrchestrationError):
    """Raised when an idempotency key conflicts with immutable evidence."""


class VendorBillReleaseTransactionRetryExhaustedError(VendorBillReleaseOrchestrationError):
    """Raised only after bounded transient transaction retries are exhausted."""


class VendorBillReleaseOrchestrationOutcome(StrEnum):
    AUTHORIZED = "AUTHORIZED"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"


@dataclass(frozen=True)
class VendorBillReleaseCommand:
    """Immutable release request containing no payment or execution fields."""
    tenant_id: str
    payable_id: str
    release_authorization_id: str
    requested_amount_minor: int
    currency: str
    authorized_by_actor_id: str
    authorization_basis_reference: str
    authorized_at: datetime
    idempotency_key: str


@dataclass(frozen=True)
class VendorBillReleaseResult:
    """Immutable result that distinguishes authorization from replay."""
    outcome: VendorBillReleaseOrchestrationOutcome
    authorization: VendorBillReleaseAuthorization


class VendorBillReleaseOrchestrator:
    """Own release-authorization transaction ordering; never executes money."""

    @staticmethod
    def authorize(command: VendorBillReleaseCommand, database=None, *, max_attempts: int = 3) -> VendorBillReleaseResult:
        """Run bounded whole-transaction attempts with fresh caller-owned sessions."""
        if not isinstance(command, VendorBillReleaseCommand):
            raise VendorBillReleaseOrchestrationError("invalid release command")
        db = database or get_database()
        if db is None:
            raise VendorBillReleaseOrchestrationError("VENDOR_BILL_PERSISTENCE_UNAVAILABLE")
        bills = db["vendor_bills"]
        results = db["financial_approval_effective_results"]
        authorizations = db["vendor_bill_release_authorizations"]
        attempts = min(max(1, max_attempts), _MAX_TRANSACTION_ATTEMPTS)
        for attempt in range(attempts):
            with db.client.start_session() as session:
                session.start_transaction()
                try:
                    try:
                        existing = VendorBillReleaseAuthorizationRegistry.get_by_idempotency_key(command.tenant_id, command.payable_id, command.idempotency_key, authorizations, session=session)
                    except VendorBillReleaseAuthorizationNotFoundError:
                        existing = None
                    if existing is not None:
                        if not _authorization_matches_command(existing, command):
                            raise VendorBillReleaseOrchestrationIdempotencyError("VENDOR_BILL_RELEASE_AUTHORIZATION_IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_COMMAND")
                        session.commit_transaction()
                        return VendorBillReleaseResult(VendorBillReleaseOrchestrationOutcome.IDEMPOTENT_REPLAY, existing)
                    bill = VendorBillRegistry.get(command.tenant_id, command.payable_id, bills, session=session)
                    result = FinancialApprovalEffectiveResultRegistry.get(command.tenant_id, bill.approval_effective_result_id or "", results, session=session)
                    reserved = VendorBillReleaseAuthorizationRegistry.sum_authorized_amount_minor(command.tenant_id, command.payable_id, authorizations, session=session)
                    decision = evaluate_vendor_bill_release_eligibility(bill, result, command.requested_amount_minor, command.currency, bill.approval_projection_revision, reserved)
                    if not decision.eligible:
                        raise VendorBillReleaseOrchestrationError(decision.reason.value)
                    guarded = VendorBillRegistry.acquire_release_authority_guard(command.tenant_id, command.payable_id, bill.revision, bill.approval_projection_revision, result.result_id, bill.release_authority_guard_revision, bills, session=session)
                    authorization = VendorBillReleaseAuthorization(tenant_id=command.tenant_id, release_authorization_id=command.release_authorization_id, payable_id=command.payable_id, vendor_bill_revision=guarded.revision, approval_effective_result_id=result.result_id, approval_effective_result_fingerprint=fingerprint_financial_approval_effective_result(result), authorized_amount_minor=command.requested_amount_minor, currency=command.currency, authorized_by_actor_id=command.authorized_by_actor_id, authorization_basis_reference=command.authorization_basis_reference, authorized_at=command.authorized_at, created_at=command.authorized_at)
                    VendorBillReleaseAuthorizationRegistry.create(authorization, command.idempotency_key, authorizations, session=session)
                    session.commit_transaction()
                    return VendorBillReleaseResult(VendorBillReleaseOrchestrationOutcome.AUTHORIZED, authorization)
                except OperationFailure as error:
                    if session.in_transaction:
                        session.abort_transaction()
                    if error.has_error_label("UnknownTransactionCommitResult"):
                        raise VendorBillReleaseOrchestrationError("VENDOR_BILL_RELEASE_TRANSACTION_COMMIT_UNCERTAIN") from error
                    if error.has_error_label("TransientTransactionError") or error.code == 112:
                        if attempt + 1 < attempts:
                            continue
                        raise VendorBillReleaseTransactionRetryExhaustedError("VENDOR_BILL_RELEASE_TRANSACTION_RETRY_EXHAUSTED") from error
                    raise
                except Exception:
                    if session.in_transaction:
                        session.abort_transaction()
                    raise
        raise VendorBillReleaseTransactionRetryExhaustedError("VENDOR_BILL_RELEASE_TRANSACTION_RETRY_EXHAUSTED")


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: vendor_bill_release_orchestrator.py
# VERSION: v1.0.1-VENDOR-BILL-RELEASE-ORCHESTRATOR-EXACT-REPLAY
# AUTHORITY BOUNDARY: release evidence orchestration only; no execution or settlement
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
