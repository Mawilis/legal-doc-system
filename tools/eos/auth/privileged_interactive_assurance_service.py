"""
TITLE:
    WILSY OS Privileged Interactive Security Assurance Orchestration Service

VERSION:
    v1.0.1-P3-R3G-INTERACTIVE-ASSURANCE-HISTORIC-REPLAY

AUTHORITY:
    Wilsy OS Sovereign IAM

EPITOME:
    Derive current interactive privileged-security assurance exclusively from
    canonical principal, credential, session, factor-verification, interactive
    proof, and assurance-evidence authorities.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/privileged_interactive_assurance_service.py

COLLABORATION / OWNERSHIP:
    This service composes existing sovereign P3 authorities. It does not own
    principal provisioning, credentials, sessions, factors, role assignment,
    tenant authority, privileged activation, transaction lifecycle, or finance.

CERTIFICATION / UPDATE DATE:
    2026-10-14

CHANGELOG:
    v1.0.1-P3-R3G-INTERACTIVE-ASSURANCE-HISTORIC-REPLAY
        Adds exact scoped historic idempotent replay precedence. Once sealed
        assurance evidence exists for principal/channel/purpose/replay scope,
        that historic security decision is returned unchanged before present
        currentness, clock, or new evidence identity is evaluated. New issuance
        retains the existing fresh-currentness path and caller-owned transaction.
    v1.0.0-P3-R3G-INTERACTIVE-ASSURANCE-ORCHESTRATION
        Initial interactive current-assurance orchestration service. Principal
        identity and all currentness facts are derived from existing canonical
        authorities; callers cannot assert assurance truth.

COMPLIANCE:
    WILSY OS Sovereign Code Governance Contract v1.2.0.

SECURITY / PRIVACY POSTURE:
    Raw bearer tokens, OTP secrets, OTP codes, credential secrets, and workload
    secrets are neither accepted nor returned. Only non-secret canonical
    references and currentness facts participate in assurance evaluation.

TENANT BOUNDARY:
    tenant_id scopes credential and session currentness only. This service does
    not create tenant membership, tenant role, or tenant authorization.

AUTHORITY BOUNDARY:
    Security assurance is evidence of current security posture. It is not role,
    permission, privileged eligibility, privileged activation, or execution
    authority.

FINANCIAL AUTHORITY BOUNDARY:
    NONE. Kennel EOS remains the exclusive financial execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Protocol, cast
from uuid import uuid4

from pymongo.errors import PyMongoError

from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.privileged_channel_currentness import (
    InteractiveCurrentness,
    derive_interactive_currentness,
)
from tools.eos.auth.privileged_factor_verification_currentness_registry import (
    PrivilegedFactorVerificationCurrentnessRegistry,
)
from tools.eos.auth.privileged_interactive_security_proof import (
    PrivilegedInteractiveProofStatus,
)
from tools.eos.auth.privileged_interactive_security_proof_registry import (
    PrivilegedInteractiveSecurityProofRegistry,
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
    "v1.0.0-P3-R3G-"
    "INTERACTIVE-ASSURANCE-ORCHESTRATION"
)


class PrivilegedInteractiveAssuranceError(
    RuntimeError
):
    """Fail-closed interactive-assurance orchestration failure.

    This classification exposes no secret material and grants no authority.
    Transaction lifecycle remains exclusively with the caller.
    """


class InteractiveAuthCurrentnessReader(
    Protocol
):
    """Read canonical credential and session currentness for one principal.

    Implementations are read-only transaction participants. They do not create
    sessions, mutate credentials, grant tenant authority, or own transaction
    lifecycle.
    """

    def get_credential_revision(
        self,
        tenant_id: str,
        user_id: str,
        *,
        session: Any = None,
    ) -> int:
        """Return the canonical current credential revision."""
        ...

    def is_session_current(
        self,
        tenant_id: str,
        user_id: str,
        session_reference: str,
        *,
        at: datetime | None = None,
        session: Any = None,
    ) -> bool:
        """Return fail-closed currentness for one non-secret session reference."""
        ...


@dataclass(
    frozen=True,
    slots=True,
)
class PrivilegedInteractiveAssuranceResult:
    """Immutable result of one persisted interactive P3 assurance evaluation.

    The decision and evidence contain security-assurance truth only. They grant
    no role, tenant, activation, break-glass, or financial authority.
    """

    decision: PrivilegedSecurityAssuranceDecision
    evidence: PrivilegedSecurityAssuranceEvidence


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
    ):
        raise PrivilegedInteractiveAssuranceError(
            name + "_INVALID"
        )

    return value.strip()


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
        raise PrivilegedInteractiveAssuranceError(
            "ACTIVE_TRANSACTION_REQUIRED"
        )

    return session


def _utc(
    value: datetime,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise PrivilegedInteractiveAssuranceError(
            "EVALUATED_AT_INVALID"
        )

    return value.astimezone(timezone.utc)


class PrivilegedInteractiveAssuranceService:
    """Compose one authoritative interactive P3 security-assurance decision.

    Authority:
        The current interactive proof determines principal identity. Principal
        currentness comes from PrincipalAuthorityRepository. Credential and
        session currentness come from the injected canonical authentication
        registry reader. Factor and authentication-recency currentness are
        derived from the canonical factor event. The shared P3 evaluator makes
        the assurance decision and the assurance-evidence registry persists it.

    Caller contract:
        Callers may provide only tenant_id, proof_reference, assurance_purpose,
        idempotency_key, and one already-active transaction. They cannot assert
        principal identity, any currentness fact, or an assurance decision.

    Transaction contract:
        The caller owns begin/commit/abort/retry. This service never starts,
        commits, aborts, or retries a transaction.

    Idempotency:
        Durable evidence replay remains governed by the canonical evidence
        registry's principal + channel + purpose + idempotency contract.

    Fail-closed posture:
        Missing proof, invalid transaction, malformed identifiers, unavailable
        authoritative reads, or malformed evidence fail closed.

    Boundaries:
        No role, permission, tenant membership, eligibility, activation,
        break-glass, token issuance, session creation, or financial execution
        authority is created here.
    """

    def __init__(
        self,
        *,
        auth_registry: InteractiveAuthCurrentnessReader,
        principal_collection: Any,
        factor_registry:
            PrivilegedFactorVerificationCurrentnessRegistry,
        proof_registry:
            PrivilegedInteractiveSecurityProofRegistry,
        evidence_registry:
            PrivilegedSecurityAssuranceEvidenceRegistry,
        maximum_age_seconds: int,
        clock: Callable[[], datetime] | None = None,
        evidence_id_factory: Callable[[], str] | None = None,
    ) -> None:
        """Bind existing authoritative P3 dependencies without creating authority."""

        if auth_registry is None:
            raise PrivilegedInteractiveAssuranceError(
                "AUTH_REGISTRY_REQUIRED"
            )

        if principal_collection is None:
            raise PrivilegedInteractiveAssuranceError(
                "PRINCIPAL_COLLECTION_REQUIRED"
            )

        if not isinstance(
            factor_registry,
            PrivilegedFactorVerificationCurrentnessRegistry,
        ):
            raise PrivilegedInteractiveAssuranceError(
                "FACTOR_REGISTRY_REQUIRED"
            )

        if not isinstance(
            proof_registry,
            PrivilegedInteractiveSecurityProofRegistry,
        ):
            raise PrivilegedInteractiveAssuranceError(
                "PROOF_REGISTRY_REQUIRED"
            )

        if not isinstance(
            evidence_registry,
            PrivilegedSecurityAssuranceEvidenceRegistry,
        ):
            raise PrivilegedInteractiveAssuranceError(
                "EVIDENCE_REGISTRY_REQUIRED"
            )

        if (
            not isinstance(maximum_age_seconds, int)
            or isinstance(maximum_age_seconds, bool)
            or maximum_age_seconds <= 0
        ):
            raise PrivilegedInteractiveAssuranceError(
                "MAXIMUM_AGE_SECONDS_INVALID"
            )

        self._auth_registry = auth_registry
        self._principal_collection = principal_collection
        self._factor_registry = factor_registry
        self._proof_registry = proof_registry
        self._evidence_registry = evidence_registry
        self._maximum_age_seconds = maximum_age_seconds
        self._clock = (
            clock
            if clock is not None
            else lambda: datetime.now(
                timezone.utc
            )
        )
        self._evidence_id_factory = (
            evidence_id_factory
            if evidence_id_factory is not None
            else lambda: (
                "WILSYASSURANCE-"
                + str(uuid4())
            )
        )

    def compose(
        self,
        *,
        tenant_id: str,
        proof_reference: str,
        assurance_purpose:
            PrivilegedAssurancePurpose,
        idempotency_key: str,
        session: object,
    ) -> PrivilegedInteractiveAssuranceResult:
        """Derive, evaluate, and persist one interactive assurance observation.

        The current proof is resolved first and is the sole principal-identity
        source. If sealed evidence already exists for the exact principal,
        interactive channel, purpose, and idempotency scope, that historic
        decision is returned unchanged before present currentness is reevaluated.
        For a new scope, every currentness fact is freshly read or derived inside
        the caller's active transaction and the shared evaluator is invoked with
        INTERACTIVE_STRONG_AUTH and no workload material.

        Both sufficient and insufficient authoritative decisions may be
        persisted as immutable historic evidence. This method owns no
        transaction lifecycle, privileged activation, or financial execution.
        """

        tx = _active_transaction(
            session
        )

        tenant = _text(
            "TENANT_ID",
            tenant_id,
        )

        reference = _text(
            "PROOF_REFERENCE",
            proof_reference,
        )

        replay_key = _text(
            "IDEMPOTENCY_KEY",
            idempotency_key,
        )

        if not isinstance(
            assurance_purpose,
            PrivilegedAssurancePurpose,
        ):
            raise PrivilegedInteractiveAssuranceError(
                "ASSURANCE_PURPOSE_INVALID"
            )

        snapshot = (
            self._proof_registry
            .get_current_by_proof_reference(
                proof_reference=reference,
                session=tx,
            )
        )

        if snapshot is None:
            raise PrivilegedInteractiveAssuranceError(
                "INTERACTIVE_PROOF_NOT_FOUND"
            )

        proof = snapshot.proof

        if proof.proof_reference != reference:
            raise PrivilegedInteractiveAssuranceError(
                "INTERACTIVE_PROOF_REFERENCE_MISMATCH"
            )

        principal_id = _text(
            "PRINCIPAL_ID",
            proof.principal_id,
        )

        try:
            historic = (
                self._evidence_registry
                .get_by_scope_idempotency(
                    principal_id=
                        principal_id,
                    assurance_channel=(
                        PrivilegedAssuranceChannel
                        .INTERACTIVE_STRONG_AUTH
                        .value
                    ),
                    assurance_purpose=
                        assurance_purpose.value,
                    idempotency_key=
                        replay_key,
                    session=tx,
                )
            )

        except Exception as error:
            cause = error.__cause__

            if (
                isinstance(
                    cause,
                    PyMongoError,
                )
                and cause.has_error_label(
                    "TransientTransactionError"
                )
            ):
                raise cause

            raise PrivilegedInteractiveAssuranceError(
                "ASSURANCE_EVIDENCE_PERSISTENCE_FAILED"
            ) from error

        if historic is not None:
            historic_decision = (
                PrivilegedSecurityAssuranceDecision(
                    principal_id=
                        historic.principal_id,
                    assurance_channel=
                        historic.assurance_channel,
                    assurance_purpose=
                        historic.assurance_purpose,
                    sufficient=
                        historic.sufficient,
                    reason=
                        historic.reason,
                )
            )

            return PrivilegedInteractiveAssuranceResult(
                decision=
                    historic_decision,
                evidence=
                    historic,
            )

        evaluated_at = _utc(
            self._clock()
        )

        assurance_proof_current = (
            proof.proof_status
            is PrivilegedInteractiveProofStatus.VERIFIED
        )

        try:
            authority = (
                PrincipalAuthorityRepository
                .get(
                    principal_id,
                    self._principal_collection,
                    session=cast(
                        Any,
                        tx,
                    ),
                )
            )

            principal_current = (
                authority.status
                is PrincipalStatus.ACTIVE
            )

        except PrincipalAuthorityNotFoundError:
            principal_current = False

        except PrincipalAuthorityRepositoryError as error:
            raise PrivilegedInteractiveAssuranceError(
                "PRINCIPAL_AUTHORITY_UNAVAILABLE"
            ) from error

        try:
            credential_revision = (
                self._auth_registry
                .get_credential_revision(
                    tenant,
                    principal_id,
                    session=tx,
                )
            )

            credential_current = (
                credential_revision
                == proof.credential_revision
            )

            session_current = (
                self._auth_registry
                .is_session_current(
                    tenant,
                    principal_id,
                    proof.session_reference,
                    at=evaluated_at,
                    session=tx,
                )
            )

        except Exception as error:
            raise PrivilegedInteractiveAssuranceError(
                "AUTH_CURRENTNESS_UNAVAILABLE"
            ) from error

        try:
            factor = (
                self._factor_registry
                .get(
                    factor_verification_reference=
                        proof.factor_verification_reference,
                    session=tx,
                )
            )

        except Exception as error:
            raise PrivilegedInteractiveAssuranceError(
                "FACTOR_CURRENTNESS_UNAVAILABLE"
            ) from error

        if factor is None:
            currentness = (
                InteractiveCurrentness(
                    factor_verification_current=False,
                    authentication_recency_current=False,
                )
            )
        else:
            try:
                currentness = (
                    derive_interactive_currentness(
                        factor,
                        principal_id=principal_id,
                        session_reference=
                            proof.session_reference,
                        credential_revision=
                            credential_revision,
                        session_current=
                            session_current,
                        evaluated_at=
                            evaluated_at,
                        maximum_age_seconds=
                            self._maximum_age_seconds,
                    )
                )

            except Exception as error:
                raise PrivilegedInteractiveAssuranceError(
                    "INTERACTIVE_CURRENTNESS_INVALID"
                ) from error

        decision = (
            evaluate_privileged_security_assurance(
                principal_id=principal_id,
                principal_current=
                    principal_current,
                credential_current=
                    credential_current,
                assurance_channel=(
                    PrivilegedAssuranceChannel
                    .INTERACTIVE_STRONG_AUTH
                ),
                assurance_proof_current=
                    assurance_proof_current,
                assurance_purpose=
                    assurance_purpose,
                session_current=
                    session_current,
                factor_verification_current=(
                    currentness
                    .factor_verification_current
                ),
                authentication_recency_current=(
                    currentness
                    .authentication_recency_current
                ),
                workload_proof_current=None,
                workload_proof_reference=None,
            )
        )

        evidence = (
            PrivilegedSecurityAssuranceEvidence
            .from_decision(
                assurance_evidence_id=
                    _text(
                        "ASSURANCE_EVIDENCE_ID",
                        self._evidence_id_factory(),
                    ),
                decision=decision,
                principal_current=
                    principal_current,
                credential_current=
                    credential_current,
                assurance_proof_current=
                    assurance_proof_current,
                session_current=
                    session_current,
                factor_verification_current=(
                    currentness
                    .factor_verification_current
                ),
                authentication_recency_current=(
                    currentness
                    .authentication_recency_current
                ),
                workload_proof_current=None,
                workload_proof_reference=None,
                evaluated_at=
                    evaluated_at,
                idempotency_key=
                    replay_key,
            )
        )

        try:
            persisted = (
                self._evidence_registry
                .create_or_replay(
                    evidence,
                    session=tx,
                )
            )

        except PyMongoError as error:
            if error.has_error_label(
                "TransientTransactionError"
            ):
                raise

            raise PrivilegedInteractiveAssuranceError(
                "ASSURANCE_EVIDENCE_PERSISTENCE_FAILED"
            ) from error

        except Exception as error:
            raise PrivilegedInteractiveAssuranceError(
                "ASSURANCE_EVIDENCE_PERSISTENCE_FAILED"
            ) from error

        return PrivilegedInteractiveAssuranceResult(
            decision=decision,
            evidence=persisted,
        )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: privileged_interactive_assurance_service.py
# VERSION: v1.0.1-P3-R3G-INTERACTIVE-ASSURANCE-HISTORIC-REPLAY
# AUTHORITY BOUNDARY:
#   Derives and records P3 security assurance only. No role, permission,
#   eligibility, privileged activation, break-glass, or execution authority.
# TENANT POSTURE:
#   tenant_id scopes canonical credential/session currentness; no tenant
#   membership or tenant authorization is created.
# FAIL-CLOSED POSTURE:
#   Missing proof, stale/absent currentness, unavailable authority, malformed
#   input, inactive transaction, or persistence failure cannot create sufficiency.
# FINANCIAL EXECUTION AUTHORITY:
#   NONE. Kennel EOS remains the exclusive financial execution authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
