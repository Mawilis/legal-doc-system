"""
TITLE:
    WILSY OS Privileged Workload Trust Currentness Registry

VERSION:
    v1.0.1-P3-R3G-S4-SOVEREIGN-WORKLOAD-TRUST-CURRENTNESS

AUTHORITY:
    Wilsy OS Sovereign IAM / P3 Security Assurance Currentness

EPITOME:
    Persist and resolve the exact current trust fact for one authoritative
    noninteractive workload proof without minting identity, role, permission,
    eligibility, privileged activation, or financial authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/privileged_workload_trust_currentness_registry.py

COLLABORATION / OWNERSHIP:
    Sovereign IAM owns workload-currentness persistence. Workload proof
    verification is external to this registry. Callers own Mongo
    transaction/session lifecycle. P3 assurance composition consumes this
    registry as durable currentness evidence.

CERTIFICATION / UPDATE DATE:
    2026-10-14

CHANGELOG:
    v1.0.1-P3-R3G-S4-SOVEREIGN-WORKLOAD-TRUST-CURRENTNESS
        Sovereign artifact certification repair only. Adds the mandatory
        institutional header, aligned version/changelog/end seal, and complete
        public API documentation while preserving runtime AST, persisted schema,
        index topology, caller-owned transaction semantics, status transitions,
        collision behavior, and canonical UTC ISO datetime round-trip.

    v1.0.0-P3-R3G-S4-WORKLOAD-TRUST-CURRENTNESS-REGISTRY
        Initial P3 workload-trust currentness registry.

COMPLIANCE:
    WILSY OS Sovereign Code Governance Contract v1.2.0.
    DISCOVER -> MAP -> WIRE -> CLEAN -> CERTIFY lifecycle.
    Persistence remains fail-closed and caller-transaction-bound.

SECURITY / PRIVACY POSTURE:
    Proof and credential references are exact bounded identifiers. The registry
    rejects malformed persisted rows, reference rebinding, duplicate identities,
    divergent replay, invalid initial state, invalid terminal transitions, and
    unavailable persistence. No raw credential secret is stored here.

TENANT BOUNDARY:
    This registry is workload-security currentness, not tenant membership or
    tenant authorization. It does not create or infer tenant scope.

AUTHORITY BOUNDARY:
    WORKLOAD CURRENTNESS != PRINCIPAL AUTHORITY.
    WORKLOAD CURRENTNESS != ROLE OR PERMISSION.
    WORKLOAD CURRENTNESS != PRIVILEGED ELIGIBILITY.
    WORKLOAD CURRENTNESS != PRIVILEGED ACTIVATION.
    Persisted historical/current trust facts do not independently authorize use.

FINANCIAL AUTHORITY BOUNDARY:
    No payment, release, execution, settlement, paid, or settled truth is created.
    Kennel EOS remains the exclusive financial execution authority.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.privileged_channel_currentness import (
    WorkloadTrustFact,
    WorkloadTrustStatus,
)


VERSION = "v1.0.1-P3-R3G-S4-SOVEREIGN-WORKLOAD-TRUST-CURRENTNESS"
COLLECTION = "privileged_workload_trust_currentness"

PROOF_REFERENCE_INDEX = "priv_workload_proof_reference_unique"
CREDENTIAL_REFERENCE_INDEX = "priv_workload_credential_reference_unique"
PRINCIPAL_TIMELINE_INDEX = "priv_workload_principal_observed"


class WorkloadTrustRegistryError(
    RuntimeError
):
    """Base fail-closed error for workload-currentness registry operations.

    This exception communicates invalid caller/domain input at the registry
    boundary. It grants no principal, tenant, role, permission, eligibility,
    activation, or financial authority.
    """
    pass


class WorkloadTrustConflictError(
    WorkloadTrustRegistryError
):
    """Report a deterministic workload-currentness state or replay conflict.

    Conflict includes reference collision, invalid initial/terminal status, or
    concurrent currentness mutation that cannot be reconciled as exact replay.
    The conflict never authorizes fallback or inferred current authority.
    """
    pass


class WorkloadTrustPersistenceError(
    WorkloadTrustRegistryError
):
    """Report fail-closed persistence, hydration, transaction, or index failure.

    Persistence failure never degrades into inferred workload currentness. The
    caller remains responsible for the enclosing Mongo transaction lifecycle.
    """
    pass


def _identifier(
    name: str,
    value: object,
) -> str:
    if not isinstance(value, str):
        raise WorkloadTrustRegistryError(
            f"{name} invalid"
        )

    cleaned = value.strip()

    if not cleaned or len(cleaned) > 1024:
        raise WorkloadTrustRegistryError(
            f"{name} invalid"
        )

    return cleaned


def _active_transaction(
    session: object,
) -> Any:
    if session is None:
        raise WorkloadTrustPersistenceError(
            "TRANSACTION_REQUIRED"
        )

    if not bool(
        getattr(
            session,
            "in_transaction",
            False,
        )
    ):
        raise WorkloadTrustPersistenceError(
            "ACTIVE_TRANSACTION_REQUIRED"
        )

    return session


def _persisted(
    fact: WorkloadTrustFact,
    *,
    recorded_at: datetime,
) -> dict[str, object]:
    return {
        "proof_reference":
            fact.proof_reference,
        "principal_id":
            fact.principal_id,
        "credential_or_attestation_reference":
            fact
            .credential_or_attestation_reference,
        "observed_at":
            fact.observed_at
            .astimezone(timezone.utc)
            .isoformat(),
        "status":
            fact.status.value,
        "recorded_at":
            recorded_at,
    }


def _hydrate(
    row: object,
) -> WorkloadTrustFact:
    if not isinstance(row, dict):
        raise WorkloadTrustPersistenceError(
            "PERSISTED_ROW_INVALID"
        )

    try:
        return WorkloadTrustFact(
            proof_reference=
                row["proof_reference"],
            principal_id=
                row["principal_id"],
            credential_or_attestation_reference=
                row[
                    "credential_or_attestation_reference"
                ],
            observed_at=
                datetime.fromisoformat(
                    row["observed_at"]
                ),
            status=
                WorkloadTrustStatus(
                    row["status"]
                ),
        )
    except (
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        raise WorkloadTrustPersistenceError(
            "PERSISTED_ROW_INVALID"
        ) from error


class PrivilegedWorkloadTrustCurrentnessRegistry:
    """Persist authoritative workload trust currentness without minting authority.

    Persistence:
        Stores one exact workload fact per globally unique proof reference and
        credential/attestation reference. ``observed_at`` is stored as canonical
        UTC ISO text so real-Mongo hydration preserves timezone awareness.

    Transaction ownership:
        Mutating methods require a caller-owned active transaction. Read methods
        accept and propagate an optional caller session.

    Idempotency:
        Exact existing facts replay exactly. Divergent use of either unique
        reference fails closed.

    Lifecycle:
        Creation admits CURRENT only. Termination permits REVOKED or INVALIDATED
        with conditional current-state mutation and exact terminal replay.

    Authority boundary:
        Current workload trust is security evidence only; it is not tenant,
        role, permission, privileged activation, or financial authority.
    """
    def __init__(
        self,
        collection: Any,
    ) -> None:
        self._collection = collection

    def ensure_indexes(
        self,
    ) -> None:
        """Create the fixed workload-currentness index topology.

        Creates unique proof-reference and credential-reference indexes plus the
        non-unique principal/observed-at timeline index. This method creates no
        trust fact and grants no authority. Production callers should invoke it
        from canonical startup/bootstrap ownership, not request execution.
        """
        indexes = (
            (
                [
                    (
                        "proof_reference",
                        ASCENDING,
                    ),
                ],
                True,
                PROOF_REFERENCE_INDEX,
            ),
            (
                [
                    (
                        "credential_or_attestation_reference",
                        ASCENDING,
                    ),
                ],
                True,
                CREDENTIAL_REFERENCE_INDEX,
            ),
            (
                [
                    (
                        "principal_id",
                        ASCENDING,
                    ),
                    (
                        "observed_at",
                        ASCENDING,
                    ),
                ],
                False,
                PRINCIPAL_TIMELINE_INDEX,
            ),
        )

        try:
            for keys, unique, name in indexes:
                self._collection.create_index(
                    keys,
                    unique=unique,
                    name=name,
                )
        except PyMongoError as error:
            raise WorkloadTrustPersistenceError(
                "INDEX_CREATION_FAILED"
            ) from error

    def get_by_proof_reference(
        self,
        *,
        proof_reference: str,
        session: object = None,
    ) -> WorkloadTrustFact | None:
        """Read and verify the fact bound to one exact proof reference.

        ``session`` is propagated when supplied. Absence returns ``None``.
        Persisted corruption, unavailable storage, or proof-reference rebinding
        fails closed rather than returning inferred currentness.
        """
        reference = _identifier(
            "proof_reference",
            proof_reference,
        )

        try:
            row = self._collection.find_one(
                {
                    "proof_reference":
                        reference
                },
                session=session,
            )
        except PyMongoError as error:
            raise WorkloadTrustPersistenceError(
                "PERSISTENCE_UNAVAILABLE"
            ) from error

        if row is None:
            return None

        fact = _hydrate(
            row
        )

        if (
            fact.proof_reference
            != reference
        ):
            raise WorkloadTrustPersistenceError(
                "PROOF_REFERENCE_BINDING_MISMATCH"
            )

        return fact

    def get_by_credential_reference(
        self,
        *,
        credential_or_attestation_reference: str,
        session: object = None,
    ) -> WorkloadTrustFact | None:
        """Read and verify the fact bound to one exact credential reference.

        ``session`` is propagated when supplied. Absence returns ``None``.
        Persisted corruption, unavailable storage, or credential-reference
        rebinding fails closed.
        """
        reference = _identifier(
            "credential_or_attestation_reference",
            credential_or_attestation_reference,
        )

        try:
            row = self._collection.find_one(
                {
                    "credential_or_attestation_reference":
                        reference
                },
                session=session,
            )
        except PyMongoError as error:
            raise WorkloadTrustPersistenceError(
                "PERSISTENCE_UNAVAILABLE"
            ) from error

        if row is None:
            return None

        fact = _hydrate(
            row
        )

        if (
            fact
            .credential_or_attestation_reference
            != reference
        ):
            raise WorkloadTrustPersistenceError(
                "CREDENTIAL_REFERENCE_BINDING_MISMATCH"
            )

        return fact

    def create_or_replay(
        self,
        fact: WorkloadTrustFact,
        *,
        recorded_at: datetime,
        session: object,
    ) -> WorkloadTrustFact:
        """Create CURRENT workload trust or replay the exact existing fact.

        The caller must own an active Mongo transaction. Initial status must be
        CURRENT. Exact proof/credential reference replay returns the existing
        fact; divergent collision fails closed. The persisted ``observed_at`` is
        canonical UTC ISO text and no credential secret is persisted.
        """
        tx = _active_transaction(
            session
        )

        if type(fact) is not WorkloadTrustFact:
            raise WorkloadTrustRegistryError(
                "FACT_REQUIRED"
            )

        if (
            fact.status
            is not WorkloadTrustStatus.CURRENT
        ):
            raise WorkloadTrustConflictError(
                "INITIAL_STATUS_MUST_BE_CURRENT"
            )

        existing = self.get_by_proof_reference(
            proof_reference=
                fact.proof_reference,
            session=tx,
        )

        if existing is not None:
            if existing == fact:
                return existing

            raise WorkloadTrustConflictError(
                "PROOF_REFERENCE_COLLISION"
            )

        by_credential = (
            self.get_by_credential_reference(
                credential_or_attestation_reference=
                    fact
                    .credential_or_attestation_reference,
                session=tx,
            )
        )

        if by_credential is not None:
            if by_credential == fact:
                return by_credential

            raise WorkloadTrustConflictError(
                "CREDENTIAL_REFERENCE_COLLISION"
            )

        try:
            self._collection.insert_one(
                _persisted(
                    fact,
                    recorded_at=recorded_at,
                ),
                session=tx,
            )

        except DuplicateKeyError as error:
            if error.has_error_label(
                "TransientTransactionError"
            ):
                raise

            raise WorkloadTrustConflictError(
                "REFERENCE_COLLISION"
            ) from error

        except PyMongoError as error:
            if error.has_error_label(
                "TransientTransactionError"
            ):
                raise

            raise WorkloadTrustPersistenceError(
                "PERSISTENCE_UNAVAILABLE"
            ) from error

        return fact

    def terminate(
        self,
        *,
        proof_reference: str,
        target_status: WorkloadTrustStatus,
        session: object,
    ) -> WorkloadTrustFact:
        """Transition CURRENT workload trust to REVOKED or INVALIDATED.

        The caller must own an active Mongo transaction. The update condition
        requires CURRENT state, preserving concurrency safety. Exact replay of
        the requested terminal state succeeds; conflicting terminal/currentness
        outcomes fail closed. This method revokes trust evidence only and does
        not itself revoke sessions or grant any authority.
        """
        tx = _active_transaction(
            session
        )

        if target_status not in {
            WorkloadTrustStatus.REVOKED,
            WorkloadTrustStatus.INVALIDATED,
        }:
            raise WorkloadTrustConflictError(
                "TARGET_STATUS_NOT_TERMINAL"
            )

        reference = _identifier(
            "proof_reference",
            proof_reference,
        )

        current = self.get_by_proof_reference(
            proof_reference=
                reference,
            session=tx,
        )

        if current is None:
            raise WorkloadTrustConflictError(
                "TRUST_FACT_NOT_FOUND"
            )

        if (
            current.status
            is not WorkloadTrustStatus.CURRENT
        ):
            if current.status is target_status:
                return current

            raise WorkloadTrustConflictError(
                "TERMINAL_STATUS"
            )

        try:
            result = self._collection.update_one(
                {
                    "proof_reference":
                        reference,
                    "status":
                        WorkloadTrustStatus
                        .CURRENT
                        .value,
                },
                {
                    "$set": {
                        "status":
                            target_status.value
                    }
                },
                session=tx,
            )

        except PyMongoError as error:
            if error.has_error_label(
                "TransientTransactionError"
            ):
                raise

            raise WorkloadTrustPersistenceError(
                "PERSISTENCE_UNAVAILABLE"
            ) from error

        if (
            getattr(
                result,
                "matched_count",
                0,
            )
            != 1
            or getattr(
                result,
                "modified_count",
                0,
            )
            != 1
        ):
            replay = self.get_by_proof_reference(
                proof_reference=
                    reference,
                session=tx,
            )

            if (
                replay is not None
                and replay.status
                is target_status
            ):
                return replay

            raise WorkloadTrustConflictError(
                "CURRENTNESS_CONFLICT"
            )

        updated = self.get_by_proof_reference(
            proof_reference=
                reference,
            session=tx,
        )

        if (
            updated is None
            or updated.status
            is not target_status
        ):
            raise WorkloadTrustPersistenceError(
                "TERMINAL_READBACK_FAILED"
            )

        return updated


__all__ = [
    "VERSION",
    "COLLECTION",
    "PROOF_REFERENCE_INDEX",
    "CREDENTIAL_REFERENCE_INDEX",
    "PRINCIPAL_TIMELINE_INDEX",
    "WorkloadTrustRegistryError",
    "WorkloadTrustConflictError",
    "WorkloadTrustPersistenceError",
    "PrivilegedWorkloadTrustCurrentnessRegistry",
]
# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: privileged_workload_trust_currentness_registry.py
# VERSION: v1.0.1-P3-R3G-S4-SOVEREIGN-WORKLOAD-TRUST-CURRENTNESS
# AUTHORITY BOUNDARY:
#   Workload security currentness only; no principal, tenant, role, permission,
#   privileged eligibility, privileged activation, session, or execution authority.
# TENANT POSTURE:
#   Tenant membership and authorization are neither created nor inferred here.
# FAIL-CLOSED POSTURE:
#   Invalid input, corrupt persisted state, reference collision, invalid lifecycle
#   transition, concurrency conflict, or unavailable persistence rejects operation.
# FINANCIAL EXECUTION AUTHORITY:
#   NONE. Kennel EOS remains the exclusive financial execution authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
