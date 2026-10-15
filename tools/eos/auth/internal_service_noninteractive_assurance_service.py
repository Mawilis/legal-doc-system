"""
TITLE:
    WILSY OS Internal-Service Noninteractive Security Assurance Composition

VERSION:
    v1.0.1-P3-R3G-S6-A2-SOVEREIGN-ARTIFACT-CERTIFIED

AUTHORITY:
    Wilsy OS Sovereign IAM / P3 Security Assurance

EPITOME:
    Compose a cryptographically verified, canonically bound internal-service
    workload proof into current P3 noninteractive security assurance without
    creating tenant, role, privileged-activation, or financial authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/internal_service_noninteractive_assurance_service.py

COLLABORATION / OWNERSHIP:
    Sovereign IAM owns assurance composition. InternalServiceWorkloadProofService
    owns authoritative workload verification and canonical principal/credential
    binding. The caller owns the active Mongo transaction/session. Existing P3
    registries own durable workload currentness, noninteractive proof snapshots,
    and historic security-assurance evidence.

CERTIFICATION / UPDATE DATE:
    2026-10-14

CHANGELOG:
    v1.0.1-P3-R3G-S6-A2-SOVEREIGN-ARTIFACT-CERTIFIED
        Sovereign artifact certification repair only. Adds the mandatory
        institutional header, aligned semantic version/changelog/end seal, and
        complete public API documentation while preserving the previously
        certified runtime AST, transaction ownership, persisted schemas, caller
        surface, authority boundaries, and fail-closed behavior.

    v1.0.0-P3-R3G-S6-A2-ATOMIC-NONINTERACTIVE-ASSURANCE
        Initial atomic noninteractive assurance composition.

COMPLIANCE:
    WILSY OS Sovereign Code Governance Contract v1.2.0.
    DISCOVER -> MAP -> WIRE -> CLEAN -> CERTIFY lifecycle.
    No duplicate canonical workload authority is introduced.

SECURITY / PRIVACY POSTURE:
    Caller-controlled principal identity, proof identity, workload proof
    reference, or assurance evidence identity is not accepted. Authoritative
    workload verification and same-transaction durable rereads determine the
    security facts used by the assurance evaluator. Durable writes require an
    already-active caller-owned Mongo transaction.

TENANT BOUNDARY:
    This service does not create tenant membership, tenant authorization, tenant
    role assignment, or tenant scope. Workload identity and security assurance
    are not tenant authority.

AUTHORITY BOUNDARY:
    WORKLOAD PROOF != TENANT AUTHORITY.
    SECURITY ASSURANCE != PRIVILEGED ACTIVATION.
    ROLE != ASSURANCE.
    HISTORIC ASSURANCE EVIDENCE != CURRENT AUTHORITY.
    This module composes existing canonical security facts only.

FINANCIAL AUTHORITY BOUNDARY:
    No payment, release, execution, settlement, paid, or settled truth is created.
    Kennel EOS remains the exclusive financial execution authority.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

from tools.eos.auth.internal_service_workload_proof_service import (
    InternalServiceWorkloadProofService,
)
from tools.eos.auth.privileged_channel_currentness import (
    WorkloadTrustFact,
    WorkloadTrustStatus,
)
from tools.eos.auth.privileged_workload_trust_currentness_registry import (
    PrivilegedWorkloadTrustCurrentnessRegistry,
)
from tools.eos.auth.privileged_noninteractive_security_proof import (
    PrivilegedNoninteractiveProofStatus,
    PrivilegedNoninteractiveSecurityProof,
)
from tools.eos.auth.privileged_noninteractive_security_proof_registry import (
    PrivilegedNoninteractiveSecurityProofRegistry,
    PrivilegedNoninteractiveSecurityProofSnapshot,
)
from tools.eos.auth.privileged_security_assurance import (
    PrivilegedAssuranceChannel,
    PrivilegedAssurancePurpose,
    PrivilegedSecurityAssuranceDecision,
    evaluate_privileged_security_assurance,
)
from tools.eos.auth.privileged_security_assurance_evidence import (
    PrivilegedSecurityAssuranceEvidence,
)
from tools.eos.auth.privileged_security_assurance_evidence_registry import (
    PrivilegedSecurityAssuranceEvidenceRegistry,
)

VERSION = (
    "v1.0.1-P3-R3G-S6-A2-SOVEREIGN-ARTIFACT-CERTIFIED"
)


class InternalServiceNoninteractiveAssuranceError(
    RuntimeError
):
    """Fail-closed error for sovereign noninteractive assurance composition.

    The exception represents a bounded composition failure only. It does not
    grant, mutate, or imply tenant authority, role authority, privileged
    activation, session authority, or financial execution authority.
    """


@dataclass(
    frozen=True,
    slots=True,
)
class InternalServiceNoninteractiveAssuranceResult:
    """Return the exact facts created by one successful composition.

    The result exposes the authoritative workload fact, current noninteractive
    proof snapshot, pure assurance decision, and immutable historic assurance
    evidence produced inside the caller-owned transaction. The result itself is
    not tenant authorization or privileged activation authority.
    """

    workload_fact: WorkloadTrustFact
    proof_snapshot: (
        PrivilegedNoninteractiveSecurityProofSnapshot
    )
    decision: PrivilegedSecurityAssuranceDecision
    evidence: PrivilegedSecurityAssuranceEvidence


def _active_transaction(
    session: object,
) -> object:
    if (
        session is None
        or getattr(
            session,
            "in_transaction",
            False,
        )
        is not True
    ):
        raise (
            InternalServiceNoninteractiveAssuranceError(
                "ACTIVE_TRANSACTION_REQUIRED"
            )
        )

    return session


def _proof_id() -> str:
    return (
        "WILSY-NONINTERACTIVE-PROOF-"
        f"{uuid.uuid4()}"
    )


def _evidence_id() -> str:
    return (
        "WILSY-ASSURANCE-EVIDENCE-"
        f"{uuid.uuid4()}"
    )


class InternalServiceNoninteractiveAssuranceService:
    """Compose canonical internal-service workload truth into P3 assurance.

    Authority:
        Reuses the existing authoritative workload verifier/currentness
        registries and the pure P3 security-assurance evaluator. It creates no
        role, permission, tenant, privileged-activation, or financial authority.

    Tenant scope:
        No tenant scope is accepted or minted by this service. Tenant
        authorization remains the responsibility of its canonical caller.

    Mutation semantics:
        Persists the existing workload currentness/proof/evidence artifacts only
        through injected canonical registries.

    Transaction ownership:
        The caller must supply an already-active transaction. This service never
        starts, commits, aborts, or replaces that transaction.

    Idempotency:
        The caller supplies one bounded logical idempotency key. Derived proof
        and evidence keys remain purpose-specific within the existing registries.

    Fail-closed posture:
        Any missing/stale workload fact, proof mismatch, insufficient assurance,
        invalid purpose, invalid idempotency material, or persistence failure
        rejects the composition.

    Financial boundary:
        No payment, financial execution, or settlement truth is created.
    """

    def __init__(
        self,
        *,
        workload_source:
            InternalServiceWorkloadProofService,
        workload_registry:
            PrivilegedWorkloadTrustCurrentnessRegistry,
        proof_registry:
            PrivilegedNoninteractiveSecurityProofRegistry,
        evidence_registry:
            PrivilegedSecurityAssuranceEvidenceRegistry,
        clock:
            Callable[[], datetime]
            | None = None,
        proof_id_factory:
            Callable[[], str]
            | None = None,
        evidence_id_factory:
            Callable[[], str]
            | None = None,
    ) -> None:
        self._workload_source = (
            workload_source
        )
        self._workload_registry = (
            workload_registry
        )
        self._proof_registry = (
            proof_registry
        )
        self._evidence_registry = (
            evidence_registry
        )
        self._clock = (
            clock
            or (
                lambda:
                    datetime.now(
                        timezone.utc
                    )
            )
        )
        self._proof_id_factory = (
            proof_id_factory
            or _proof_id
        )
        self._evidence_id_factory = (
            evidence_id_factory
            or _evidence_id
        )

    def compose(
        self,
        *,
        request: Mapping[str, str],
        body: bytes,
        keys: Mapping[
            str,
            tuple[str, str],
        ],
        expected_audience: str,
        assurance_purpose:
            PrivilegedAssurancePurpose,
        idempotency_key: str,
        session: object,
    ) -> (
        InternalServiceNoninteractiveAssuranceResult
    ):
        """Compose one exact current noninteractive assurance.

        Authority:
            Principal identity and workload proof reference are derived only
            from the authoritative workload source; callers cannot assert them.

        Mutation semantics:
            Creates/replays the existing noninteractive proof and immutable
            assurance evidence after same-transaction currentness rereads.

        Transaction ownership:
            ``session`` must already own an active transaction. The caller
            remains responsible for commit/abort of the whole authority chain.

        Idempotency:
            ``idempotency_key`` must be a nonblank trimmed logical key. The
            existing proof/evidence registries retain their certified exact
            replay and divergent-replay behavior.

        Fail-closed behavior:
            Invalid input, stale workload/proof currentness, insufficient
            assurance, or persistence failure raises rather than downgrading.

        Tenant and financial boundaries:
            This method neither grants tenant authority nor privileged
            activation and never creates payment/execution/settlement truth.
        """

        tx = _active_transaction(
            session
        )

        if not isinstance(
            assurance_purpose,
            PrivilegedAssurancePurpose,
        ):
            raise (
                InternalServiceNoninteractiveAssuranceError(
                    "ASSURANCE_PURPOSE_INVALID"
                )
            )

        if (
            not isinstance(
                idempotency_key,
                str,
            )
            or not idempotency_key
            or (
                idempotency_key
                != idempotency_key.strip()
            )
        ):
            raise (
                InternalServiceNoninteractiveAssuranceError(
                    "IDEMPOTENCY_KEY_INVALID"
                )
            )

        workload_fact = (
            self
            ._workload_source
            .verify_and_record(
                request=request,
                body=body,
                keys=keys,
                expected_audience=
                    expected_audience,
                session=tx,
            )
        )

        current_workload = (
            self
            ._workload_registry
            .get_by_proof_reference(
                proof_reference=
                    workload_fact
                    .proof_reference,
                session=tx,
            )
        )

        if (
            current_workload
            is None
            or current_workload
            != workload_fact
            or current_workload.status
            is not
            WorkloadTrustStatus.CURRENT
        ):
            raise (
                InternalServiceNoninteractiveAssuranceError(
                    "WORKLOAD_PROOF_NOT_CURRENT"
                )
            )

        proof = (
            PrivilegedNoninteractiveSecurityProof(
                proof_id=
                    self._proof_id_factory(),
                principal_id=
                    workload_fact
                    .principal_id,
                proof_reference=
                    workload_fact
                    .proof_reference,
                credential_or_attestation_reference=
                    workload_fact
                    .credential_or_attestation_reference,
                observed_at=
                    workload_fact
                    .observed_at,
                proof_status=(
                    PrivilegedNoninteractiveProofStatus
                    .VERIFIED
                ),
            )
        )

        proof_snapshot = (
            self
            ._proof_registry
            .create_or_replay(
                proof,
                status_changed_at=
                    workload_fact
                    .observed_at,
                idempotency_key=(
                    idempotency_key
                    + ":proof"
                ),
                session=tx,
            )
        )

        current_proof = (
            self
            ._proof_registry
            .get_current_by_proof_reference(
                proof_reference=
                    workload_fact
                    .proof_reference,
                session=tx,
            )
        )

        if (
            current_proof is None
            or current_proof
            != proof_snapshot
            or (
                current_proof
                .proof
                .proof_status
                is not
                PrivilegedNoninteractiveProofStatus
                .VERIFIED
            )
            or (
                current_proof
                .proof
                .principal_id
                != workload_fact
                .principal_id
            )
            or (
                current_proof
                .proof
                .credential_or_attestation_reference
                != workload_fact
                .credential_or_attestation_reference
            )
        ):
            raise (
                InternalServiceNoninteractiveAssuranceError(
                    "ASSURANCE_PROOF_NOT_CURRENT"
                )
            )

        # All four common currentness values below are
        # server-derived consequences of successful
        # S6-A1 verification plus same-transaction
        # durable rereads. None are caller inputs.
        principal_current = True
        credential_current = True
        assurance_proof_current = True
        workload_proof_current = True

        decision = (
            evaluate_privileged_security_assurance(
                principal_id=
                    workload_fact.principal_id,
                principal_current=
                    principal_current,
                credential_current=
                    credential_current,
                assurance_channel=(
                    PrivilegedAssuranceChannel
                    .NONINTERACTIVE_WORKLOAD_PROOF
                ),
                assurance_proof_current=
                    assurance_proof_current,
                assurance_purpose=
                    assurance_purpose,
                session_current=None,
                factor_verification_current=
                    None,
                authentication_recency_current=
                    None,
                workload_proof_current=
                    workload_proof_current,
                workload_proof_reference=
                    workload_fact
                    .proof_reference,
            )
        )

        if not decision.sufficient:
            raise (
                InternalServiceNoninteractiveAssuranceError(
                    "NONINTERACTIVE_ASSURANCE_"
                    "INSUFFICIENT:"
                    + decision.reason.value
                )
            )

        evidence = (
            PrivilegedSecurityAssuranceEvidence
            .from_decision(
                assurance_evidence_id=
                    self
                    ._evidence_id_factory(),
                decision=decision,
                principal_current=
                    principal_current,
                credential_current=
                    credential_current,
                assurance_proof_current=
                    assurance_proof_current,
                session_current=None,
                factor_verification_current=
                    None,
                authentication_recency_current=
                    None,
                workload_proof_current=
                    workload_proof_current,
                workload_proof_reference=
                    workload_fact
                    .proof_reference,
                evaluated_at=
                    self._clock(),
                idempotency_key=(
                    idempotency_key
                    + ":evidence"
                ),
            )
        )

        persisted_evidence = (
            self
            ._evidence_registry
            .create_or_replay(
                evidence,
                session=tx,
            )
        )

        return (
            InternalServiceNoninteractiveAssuranceResult(
                workload_fact=
                    workload_fact,
                proof_snapshot=
                    proof_snapshot,
                decision=decision,
                evidence=
                    persisted_evidence,
            )
        )


__all__ = [
    "VERSION",
    "InternalServiceNoninteractiveAssuranceError",
    "InternalServiceNoninteractiveAssuranceResult",
    "InternalServiceNoninteractiveAssuranceService",
]

# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: internal_service_noninteractive_assurance_service.py
# VERSION: v1.0.1-P3-R3G-S6-A2-SOVEREIGN-ARTIFACT-CERTIFIED
# AUTHORITY BOUNDARY:
#   Security assurance only; no tenant role, permission, privileged activation,
#   session issuance, break-glass, or execution authority.
# TENANT POSTURE:
#   No tenant authority is created or inferred by this artifact.
# FAIL-CLOSED POSTURE:
#   Invalid, stale, divergent, or insufficient security facts reject composition.
# FINANCIAL EXECUTION AUTHORITY:
#   NONE. Kennel EOS remains the exclusive financial execution authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
