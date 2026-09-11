"""TITLE: Accounts Payable Provider Selection Decision Registry.
VERSION: v1.0.1-M11-P5-R1B-AP2D-R2A.
AUTHORITY: Durable AP provider-selection decision persistence.
EPITOME: Strict tenant-scoped hydration and replay protection for AP selections.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/registry/accounts_payable_provider_selection_decision_registry.py
COLLABORATION / OWNERSHIP: Kennel EOS AP2D persistence authority.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.1 adds tenant-scoped execution-request uniqueness and strict request replay adjudication.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped opaque identifiers; no provider transport or secrets.
TENANT BOUNDARY: Every read, replay lookup, and write requires exact tenant scope.
AUTHORITY BOUNDARY: Selection fact persistence only; no request, policy, eligibility, or execution authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS owns later execution and settlement; this registry never moves money.
TRANSACTION BOUNDARY: Caller owns an active transaction and session for every operation.
"""
from __future__ import annotations

from typing import Any
from pymongo.errors import DuplicateKeyError

from ..domain.accounts_payable_provider_selection_decision import (
    AccountsPayableProviderSelectionDecision,
    AccountsPayableProviderSelectionDecisionError,
)


class AccountsPayableProviderSelectionDecisionRegistryError(RuntimeError):
    """Raised when AP selection persistence, replay, or hydration fails."""


class AccountsPayableProviderSelectionDecisionRegistry:
    """Persist immutable AP selection facts without resolving external authority."""

    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        """Declare both immutable selection-slot and one-request uniqueness identities."""
        collection.create_index(
            [("tenant_id", 1), ("selection_decision_id", 1)],
            unique=True,
            name="accounts_payable_provider_selection_decision_unique",
        )
        collection.create_index(
            [("tenant_id", 1), ("execution_request_id", 1)],
            unique=True,
            name="accounts_payable_provider_selection_request_unique",
        )

    @staticmethod
    def _require_active_transaction(session: Any) -> Any:
        """Require the caller-owned session to be inside an active transaction."""
        if session is None or getattr(session, "in_transaction", False) is not True:
            raise AccountsPayableProviderSelectionDecisionRegistryError("ACTIVE_TRANSACTION_REQUIRED")
        return session

    @staticmethod
    def _hydrate(row: Any) -> AccountsPayableProviderSelectionDecision:
        """Hydrate through the domain constructor and preserve strict corruption failures."""
        try:
            body = dict(row)
            body.pop("_id", None)
            return AccountsPayableProviderSelectionDecision.from_persisted(body)
        except (KeyError, TypeError, ValueError, AccountsPayableProviderSelectionDecisionError) as error:
            raise AccountsPayableProviderSelectionDecisionRegistryError(
                "SELECTION_DECISION_PERSISTED_RECORD_INVALID"
            ) from error

    @staticmethod
    def get_by_request(
        tenant_id: str,
        execution_request_id: str,
        collection: Any,
        *,
        session: Any = None,
    ) -> AccountsPayableProviderSelectionDecision | None:
        """Read the single canonical selection for an exact tenant/request pair.

        The request identity is intentionally exact and unsorted.  Zero rows
        means no canonical selection; more than one row is durable corruption,
        never an invitation to choose a first/latest/highest row.
        """
        tx = AccountsPayableProviderSelectionDecisionRegistry._require_active_transaction(session)
        try:
            cursor = collection.find(
                {"tenant_id": tenant_id, "execution_request_id": execution_request_id},
                session=tx,
            )
            limited = cursor.limit(2) if hasattr(cursor, "limit") else cursor
            rows = list(limited)[:2]
            if len(rows) > 1:
                raise AccountsPayableProviderSelectionDecisionRegistryError(
                    "MULTIPLE_REQUEST_SELECTION_ROWS"
                )
            if not rows:
                return None
            current = AccountsPayableProviderSelectionDecisionRegistry._hydrate(rows[0])
            if current.tenant_id != tenant_id or current.execution_request_id != execution_request_id:
                raise AccountsPayableProviderSelectionDecisionRegistryError(
                    "SELECTION_DECISION_PERSISTED_RECORD_INVALID"
                )
            return current
        except AccountsPayableProviderSelectionDecisionRegistryError:
            raise
        except Exception as error:
            raise AccountsPayableProviderSelectionDecisionRegistryError(
                "SELECTION_DECISION_REQUEST_LOOKUP_FAILED"
            ) from error

    @staticmethod
    def create(
        value: AccountsPayableProviderSelectionDecision,
        collection: Any,
        *,
        session: Any = None,
    ) -> tuple[AccountsPayableProviderSelectionDecision, bool]:
        """Persist one immutable fact, return exact replay, or reject divergence.

        The lookup identity is tenant plus deterministic selection decision ID.
        A selected-provider change therefore collides with the same authority
        slot and is rejected as divergent replay; no row is overwritten.
        """
        tx = AccountsPayableProviderSelectionDecisionRegistry._require_active_transaction(session)
        if not isinstance(value, AccountsPayableProviderSelectionDecision):
            raise AccountsPayableProviderSelectionDecisionRegistryError("SELECTION_DECISION_INVALID")
        query = {"tenant_id": value.tenant_id, "selection_decision_id": value.selection_decision_id}
        try:
            existing = collection.find_one(query, session=tx)
            if existing is not None:
                current = AccountsPayableProviderSelectionDecisionRegistry._hydrate(existing)
                if current.selection_decision_fingerprint == value.selection_decision_fingerprint:
                    return current, True
                raise AccountsPayableProviderSelectionDecisionRegistryError("SELECTION_DECISION_REPLAY_CONFLICT")
            request_current = AccountsPayableProviderSelectionDecisionRegistry.get_by_request(
                value.tenant_id,
                value.execution_request_id,
                collection,
                session=tx,
            )
            if request_current is not None:
                if request_current.selection_decision_id == value.selection_decision_id:
                    if request_current.selection_decision_fingerprint == value.selection_decision_fingerprint:
                        return request_current, True
                    raise AccountsPayableProviderSelectionDecisionRegistryError(
                        "SELECTION_DECISION_REPLAY_CONFLICT"
                    )
                raise AccountsPayableProviderSelectionDecisionRegistryError(
                    "REQUEST_ALREADY_HAS_CANONICAL_SELECTION"
                )
            try:
                collection.insert_one(value.to_persisted(), session=tx)
            except DuplicateKeyError:
                winner = AccountsPayableProviderSelectionDecisionRegistry.get_by_request(
                    value.tenant_id,
                    value.execution_request_id,
                    collection,
                    session=tx,
                )
                if winner is None:
                    raise AccountsPayableProviderSelectionDecisionRegistryError(
                        "SELECTION_DECISION_PERSISTENCE_FAILED"
                    )
                if winner.selection_decision_id == value.selection_decision_id:
                    if winner.selection_decision_fingerprint == value.selection_decision_fingerprint:
                        return winner, True
                    raise AccountsPayableProviderSelectionDecisionRegistryError(
                        "SELECTION_DECISION_REPLAY_CONFLICT"
                    )
                raise AccountsPayableProviderSelectionDecisionRegistryError(
                    "REQUEST_ALREADY_HAS_CANONICAL_SELECTION"
                )
            return value, False
        except AccountsPayableProviderSelectionDecisionRegistryError:
            raise
        except Exception as error:
            raise AccountsPayableProviderSelectionDecisionRegistryError("SELECTION_DECISION_PERSISTENCE_FAILED") from error

    @staticmethod
    def get(
        tenant_id: str,
        selection_decision_id: str,
        collection: Any,
        *,
        session: Any = None,
    ) -> AccountsPayableProviderSelectionDecision | None:
        """Read and strictly hydrate one tenant-scoped immutable selection fact."""
        tx = AccountsPayableProviderSelectionDecisionRegistry._require_active_transaction(session)
        try:
            row = collection.find_one(
                {"tenant_id": tenant_id, "selection_decision_id": selection_decision_id},
                session=tx,
            )
            return None if row is None else AccountsPayableProviderSelectionDecisionRegistry._hydrate(row)
        except AccountsPayableProviderSelectionDecisionRegistryError:
            raise
        except Exception as error:
            raise AccountsPayableProviderSelectionDecisionRegistryError("SELECTION_DECISION_LOOKUP_FAILED") from error


# ARTIFACT: accounts_payable_provider_selection_decision_registry.py
# VERSION: v1.0.1-M11-P5-R1B-AP2D-R2A
# AUTHORITY BOUNDARY: durable AP selection persistence only; no external resolution or execution
# TENANT POSTURE: exact tenant plus deterministic selection identity
# FAIL-CLOSED POSTURE: missing transaction, corruption, and divergent replay reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
