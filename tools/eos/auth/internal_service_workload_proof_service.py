"""WILSY OS verified internal-service workload-proof orchestration.

TITLE: Internal-Service Workload Proof Service
VERSION: v1.0.0-P3-R3G-S6-A1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Compose existing HMAC verification with durable credential and principal currentness into one server-issued workload fact.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/internal_service_workload_proof_service.py
COLLABORATION / OWNERSHIP: Internal-service verifier, replay registry, credential registry, PrincipalAuthority, and workload-currentness registry.
CERTIFICATION / UPDATE DATE: 2026-10-14
CHANGELOG: v1.0.0-P3-R3G-S6-A1 establishes the caller-transaction verified-source composition.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Proof references are server-generated; raw HMAC material is never persisted or returned.
TENANT BOUNDARY: Workload proof grants no tenant authority and consumes no caller tenant assertion.
AUTHORITY BOUNDARY: Authentication/currentness evidence only; no role, permission, eligibility, or activation.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller owns one active transaction across replay and both durable authority writes.
"""

from __future__ import annotations

from datetime import datetime, timezone
import secrets
from typing import Any, Callable, Final, Mapping

from tools.eos.auth.internal_service_replay_registry import InternalServiceReplayRegistry
from tools.eos.auth.internal_service_trust import TrustResult, verify_internal_service_request
from tools.eos.auth.internal_service_workload_credential_authority import PLATFORM_INTERNAL_SCOPE
from tools.eos.auth.internal_service_workload_credential_registry import InternalServiceWorkloadCredentialRegistry
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.privileged_channel_currentness import WorkloadTrustFact, WorkloadTrustStatus
from tools.eos.auth.privileged_workload_trust_currentness_registry import PrivilegedWorkloadTrustCurrentnessRegistry

VERSION: Final[str] = "v1.0.0-P3-R3G-S6-A1"
PROOF_REFERENCE_PREFIX: Final[str] = "WILSYWORKLOAD-"


class InternalServiceWorkloadProofError(RuntimeError):
    """Bounded fail-closed composition error with no secret or identity disclosure."""


class InternalServiceWorkloadProofDeniedError(InternalServiceWorkloadProofError):
    """Cryptographic, binding, scope, generation, or principal currentness denied."""


class InternalServiceWorkloadProofPersistenceError(InternalServiceWorkloadProofError):
    """Caller transaction or durable evidence dependency is unavailable."""


def _active_transaction(session: object) -> Any:
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise InternalServiceWorkloadProofPersistenceError("ACTIVE_TRANSACTION_REQUIRED")
    return session


def _proof_reference() -> str:
    """Generate 256 bits of collision-resistant server-owned nonsecret identity."""
    return PROOF_REFERENCE_PREFIX + secrets.token_hex(32)


class InternalServiceWorkloadProofService:
    """Issue workload currentness only from verified server-observed facts.

    The public method intentionally accepts neither principal_id nor a workload
    proof reference. Credential binding determines the principal and this
    service generates the proof reference after all currentness checks.
    """

    def __init__(
        self, *, replay_collection: Any, credential_registry: InternalServiceWorkloadCredentialRegistry,
        principal_collection: Any, workload_registry: PrivilegedWorkloadTrustCurrentnessRegistry,
        clock: Callable[[], datetime] | None = None,
        proof_reference_factory: Callable[[], str] | None = None,
    ) -> None:
        self._replay_collection = replay_collection
        self._credentials = credential_registry
        self._principal_collection = principal_collection
        self._workloads = workload_registry
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._proof_reference_factory = proof_reference_factory or _proof_reference

    def verify_and_record(
        self, *, request: Mapping[str, str], body: bytes, keys: Mapping[str, tuple[str, str]],
        expected_audience: str, session: object,
    ) -> WorkloadTrustFact:
        """Verify HMAC/replay/binding/principal state and persist one workload fact.

        The caller owns commit, abort, and whole-transaction retry. Any failure
        raises so Mongo aborts replay reservation and workload persistence
        together. No tenant, permission, role, or activation decision occurs.
        """
        tx = _active_transaction(session)
        try:
            trust: TrustResult = verify_internal_service_request(
                request=request, body=body, keys=keys,
                replay_store=InternalServiceReplayRegistry(self._replay_collection, session=tx),
            )
            if trust.audience != expected_audience:
                raise InternalServiceWorkloadProofDeniedError("WORKLOAD_SCOPE_DENIED")
            authority = self._credentials.resolve_current(
                service_id=trust.service_id, key_id=trust.key_id, session=tx,
            )
            if authority.credential_scope != PLATFORM_INTERNAL_SCOPE:
                raise InternalServiceWorkloadProofDeniedError("WORKLOAD_SCOPE_DENIED")
            principal = PrincipalAuthorityRepository.get(
                authority.principal_id, self._principal_collection, session=tx,
            )
            if principal.status is not PrincipalStatus.ACTIVE:
                raise InternalServiceWorkloadProofDeniedError("WORKLOAD_PRINCIPAL_NOT_CURRENT")
            observed_at = self._clock().astimezone(timezone.utc)
            reference = self._proof_reference_factory()
            if not isinstance(reference, str) or not reference.startswith(PROOF_REFERENCE_PREFIX) or len(reference) != len(PROOF_REFERENCE_PREFIX) + 64:
                raise InternalServiceWorkloadProofPersistenceError("WORKLOAD_PROOF_REFERENCE_GENERATION_FAILED")
            fact = WorkloadTrustFact(
                proof_reference=reference,
                principal_id=authority.principal_id,
                credential_or_attestation_reference=authority.authority_fingerprint or "",
                observed_at=observed_at,
                status=WorkloadTrustStatus.CURRENT,
            )
            return self._workloads.create_or_replay(fact, recorded_at=observed_at, session=tx)
        except InternalServiceWorkloadProofError:
            raise
        except Exception as error:
            raise InternalServiceWorkloadProofDeniedError("WORKLOAD_PROOF_DENIED") from error


__all__ = [
    "VERSION", "PROOF_REFERENCE_PREFIX", "InternalServiceWorkloadProofError",
    "InternalServiceWorkloadProofDeniedError", "InternalServiceWorkloadProofPersistenceError",
    "InternalServiceWorkloadProofService",
]

# ARTIFACT: internal_service_workload_proof_service.py
# VERSION: v1.0.0-P3-R3G-S6-A1
# AUTHORITY BOUNDARY: Verified workload currentness issuance only; no downstream authorization.
# TENANT POSTURE: No tenant assertion is accepted or created.
# FAIL-CLOSED POSTURE: HMAC, replay, binding, scope, principal, reference, and persistence must all succeed.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
