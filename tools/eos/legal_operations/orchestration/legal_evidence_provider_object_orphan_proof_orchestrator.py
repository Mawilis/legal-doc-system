"""WILSY OS authorized provider-object orphan-proof issuance.

TITLE: WILSY OS Authorized Provider-Object Orphan-Proof Issuance
VERSION: v1.0.1-L10A2R-C4D6D-B3-AUTHORIZED-ORPHAN-PROOF-ISSUANCE
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Authorize one exact already-derived B1 provider-object orphan proof,
         then durably persist/replay it through B2 in the same caller-owned
         transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_evidence_provider_object_orphan_proof_orchestrator.py
COLLABORATION / OWNERSHIP: C4D6D-B1 owns immutable orphan-proof derivation;
                            C4D6D-B2 owns durable exact persistence/replay;
                            IAM owns authorization truth and evidence;
                            C4D6D-B3 owns only their bounded authorized issuance
                            composition.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG: 2026-10-01 v1.0.1-L10A2R-C4D6D-B3-AUTHORIZED-ORPHAN-PROOF-ISSUANCE
           adds the machine-stable orchestration error `code` surface
           required by the certified authorized-issuance precedent;
           preserves the exact B1 -> IAM -> B2 authority, transaction,
           replay, tenant and downstream-authority boundaries.
           v1.0.0 established pure B1 candidate derivation followed by
           exact Legal Evidence IAM authorization and same-transaction
           B2 persistence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque bounded references and deterministic
                             SHA3-512 subject evidence only; stable error codes.
TENANT BOUNDARY: Tenant and principal derive only from one active authenticated
                 SovereignIdentity. B1 prerequisite evidence and B2 persistence
                 independently enforce exact tenant/provider/object scope.
AUTHORITY BOUNDARY: Authorized positive provider-object orphan-proof issuance
                    only. An orphan proof is not cleanup eligibility, retention
                    satisfaction, legal-hold release, deletion authorization,
                    provider deletion, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement.
TRANSACTION BOUNDARY: Caller supplies and owns one already-active transaction.
                      This module never starts, commits, aborts or retries it.
FAIL-CLOSED DECLARATION: Invalid identity/session, invalid B1 prerequisite
                         composition, denied/divergent IAM, malformed
                         authorization correlation, B2 durable divergence, and
                         persistence uncertainty all reject.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from typing import Any, Final, NoReturn

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceAuthorizationDeniedError,
    TenantAuthorizationDecisionEvidenceConflictError,
    TenantAuthorizationDecisionEvidencePersistenceError,
    TenantAuthorizationDecisionEvidenceRegistry,
    TenantAuthorizationDecisionEvidenceRegistryError,
    TenantAuthorizationDecisionEvidenceTransactionRequiredError,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_object_disownership import (
    LegalEvidenceProviderObjectDisownership,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_object_orphan_proof import (
    LegalEvidenceProviderObjectOrphanProof,
    LegalEvidenceProviderObjectOrphanProofError,
    prove_legal_evidence_provider_object_orphan,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_object_orphan_proof_registry import (
    LegalEvidenceProviderObjectOrphanProofConflictError,
    LegalEvidenceProviderObjectOrphanProofPersistedRecordInvalidError,
    LegalEvidenceProviderObjectOrphanProofPersistenceError,
    LegalEvidenceProviderObjectOrphanProofRegistry,
    LegalEvidenceProviderObjectOrphanProofRegistryError,
    LegalEvidenceProviderObjectOrphanProofTransactionRequiredError,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectObservation,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_verification_service import (
    LegalEvidenceProviderCoverageVerification,
    LegalEvidenceProviderCoverageVerificationService,
)


VERSION: Final[str] = (
    "v1.0.1-L10A2R-C4D6D-B3-AUTHORIZED-ORPHAN-PROOF-ISSUANCE"
)
PERMISSION: Final[str] = "legal_operations:evidence:write"
OPERATION: Final[str] = "legal_evidence_write"
BUSINESS_ROLE: Final[str] = "tenant_legal_partner"
AUTHORIZATION_ROLE: Final[str] = "LEGAL_PARTNER"
AUTHORIZATION_SUBJECT_PREFIX: Final[str] = (
    "legal-evidence-provider-object-orphan-proof"
)

_HEX = re.compile(r"[0-9a-f]{128}\Z")


class LegalEvidenceProviderObjectOrphanProofOrchestrationError(
    RuntimeError
):
    """Stable fail-closed issuance error containing one semantic code."""

    def __init__(
        self,
        code: str,
    ) -> None:
        """Retain one bounded machine-stable failure code."""
        self.code = code
        super().__init__(
            code
        )


class LegalEvidenceProviderObjectOrphanProofOrchestrationRetryRequiredError(
    LegalEvidenceProviderObjectOrphanProofOrchestrationError
):
    """Caller must abort and restart the complete transaction."""


def _fail(
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one stable orchestration error without leaking provider details."""
    error = LegalEvidenceProviderObjectOrphanProofOrchestrationError(
        code
    )

    if cause is None:
        raise error

    raise error from cause


def _retry(
    code: str,
    cause: BaseException,
) -> NoReturn:
    """Signal caller-owned whole-transaction retry without performing it."""
    raise (
        LegalEvidenceProviderObjectOrphanProofOrchestrationRetryRequiredError(
            code
        )
    ) from cause


def _active_session(
    session: Any,
) -> Any:
    """Require one already-active caller-owned transaction before authority."""
    if session is None:
        _fail(
            "L10A2R_C4D6D_B3_ACTIVE_TRANSACTION_REQUIRED"
        )

    marker = getattr(
        session,
        "in_transaction",
        None,
    )

    try:
        active = (
            marker()
            if callable(marker)
            else marker
        )
    except (
        AttributeError,
        TypeError,
    ):
        active = False

    if active is not True:
        _fail(
            "L10A2R_C4D6D_B3_ACTIVE_TRANSACTION_REQUIRED"
        )

    return session


def _identity(
    identity: SovereignIdentity,
) -> tuple[str, str]:
    """Derive exact tenant and principal only from active identity."""
    if not isinstance(
        identity,
        SovereignIdentity,
    ):
        _fail(
            "L10A2R_C4D6D_B3_IDENTITY_REQUIRED"
        )

    if identity.status is not PrincipalStatus.ACTIVE:
        _fail(
            "L10A2R_C4D6D_B3_PRINCIPAL_INACTIVE"
        )

    tenant = identity.tenant_id
    principal = identity.identity_id

    if (
        not isinstance(
            tenant,
            str,
        )
        or not tenant
        or tenant != tenant.strip()
        or not isinstance(
            principal,
            str,
        )
        or not principal
        or principal != principal.strip()
    ):
        _fail(
            "L10A2R_C4D6D_B3_IDENTITY_INVALID"
        )

    return (
        tenant,
        principal,
    )


def _text(
    name: str,
    value: object,
    *,
    maximum: int,
) -> str:
    """Require one bounded non-empty opaque string without coercion."""
    if (
        not isinstance(
            value,
            str,
        )
        or not value
        or value != value.strip()
        or len(value) > maximum
        or any(
            ord(character) < 32
            for character in value
        )
    ):
        _fail(
            "L10A2R_C4D6D_B3_"
            + name.upper()
            + "_INVALID"
        )

    return value


def _fingerprint(
    name: str,
    value: object,
) -> str:
    """Require canonical lowercase SHA3-512 hex evidence."""
    if (
        not isinstance(
            value,
            str,
        )
        or _HEX.fullmatch(
            value
        )
        is None
    ):
        _fail(
            "L10A2R_C4D6D_B3_"
            + name.upper()
            + "_INVALID"
        )

    return value


def _canonical_digest(
    payload: dict[str, object],
) -> str:
    """Return deterministic SHA3-512 over one canonical JSON payload."""
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode(
        "utf-8"
    )

    return hashlib.sha3_512(
        encoded
    ).hexdigest()


def _datetime_text(
    name: str,
    value: object,
) -> str:
    """Require aware datetime and return one canonical UTC-capable text value."""
    if (
        not isinstance(
            value,
            datetime,
        )
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(
            "L10A2R_C4D6D_B3_"
            + name.upper()
            + "_INVALID"
        )

    return value.isoformat(
        timespec="microseconds"
    )


def _authorization_subject_reference(
    *,
    tenant_id: str,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
    orphan_proof_reference: str,
) -> str:
    """Create stable IAM subject identity for one provider-object proof."""
    identity_digest = _canonical_digest(
        {
            "tenant_id":
                tenant_id,
            "provider_name":
                provider_name,
            "storage_reference":
                storage_reference,
            "object_version_reference":
                object_version_reference,
            "orphan_proof_reference":
                orphan_proof_reference,
        }
    )

    return (
        f"{AUTHORIZATION_SUBJECT_PREFIX}:"
        f"{identity_digest}"
    )


def _subject_material(
    *,
    tenant_id: str,
    principal_id: str,
    value: LegalEvidenceProviderObjectOrphanProof,
) -> dict[str, object]:
    """Bind IAM to the exact immutable B1 orphan-proof candidate."""
    return {
        "tenant_id":
            tenant_id,
        "actor_principal_id":
            principal_id,
        "provider_name":
            value.provider_name,
        "storage_reference":
            value.storage_reference,
        "object_version_reference":
            value.object_version_reference,
        "orphan_proof_reference":
            value.orphan_proof_reference,
        "orphan_proof_fingerprint":
            value.fingerprint,
        "coverage_verification_fingerprint":
            value.coverage_verification_fingerprint,
        "completed_observation_membership_fingerprint":
            value.completed_observation_membership_fingerprint,
        "disownership_reference":
            value.disownership_reference,
        "disownership_fingerprint":
            value.disownership_fingerprint,
        "provider_observed_at":
            _datetime_text(
                "provider_observed_at",
                value.provider_observed_at,
            ),
        "disownership_decided_at":
            _datetime_text(
                "disownership_decided_at",
                value.disownership_decided_at,
            ),
        "proved_at":
            _datetime_text(
                "proved_at",
                value.proved_at,
            ),
    }


def issue_legal_evidence_provider_object_orphan_proof(
    *,
    identity: SovereignIdentity,
    coverage_service: LegalEvidenceProviderCoverageVerificationService,
    verification: LegalEvidenceProviderCoverageVerification,
    observation: LegalEvidenceCompletedObjectObservation,
    disownership: LegalEvidenceProviderObjectDisownership,
    orphan_proof_reference: str,
    proved_at: datetime,
    authorization_evidence_registry: TenantAuthorizationDecisionEvidenceRegistry,
    orphan_proof_registry: LegalEvidenceProviderObjectOrphanProofRegistry,
    session: Any,
) -> LegalEvidenceProviderObjectOrphanProof:
    """Authorize and persist/replay one exact positive orphan-proof fact.

    Tenant and principal come only from ``identity``. B1 first derives one
    immutable candidate purely in memory so IAM can authorize its exact
    fingerprint. No durable orphan-proof issuance occurs before IAM succeeds.
    The same caller-owned active transaction is then forwarded into IAM and B2.

    IAM uses the already-certified ``legal_evidence_write`` operation and
    ``legal_operations:evidence:write`` permission. The returned authorization
    must correlate exactly to the server-bound tenant/principal, Partner role,
    candidate subject identity, candidate fingerprint, and idempotency key.

    This function does not satisfy retention, release legal hold, authorize
    cleanup/deletion, mutate provider storage, start/commit/abort/retry a
    transaction, or create financial execution or settlement authority.
    """
    tx = _active_session(
        session
    )

    tenant, principal = _identity(
        identity
    )

    proof_reference = _text(
        "orphan_proof_reference",
        orphan_proof_reference,
        maximum=240,
    )

    if not callable(
        getattr(
            authorization_evidence_registry,
            "issue",
            None,
        )
    ):
        _fail(
            "L10A2R_C4D6D_B3_AUTHORIZATION_EVIDENCE_REGISTRY_REQUIRED"
        )

    if not callable(
        getattr(
            orphan_proof_registry,
            "create_or_replay",
            None,
        )
    ):
        _fail(
            "L10A2R_C4D6D_B3_ORPHAN_PROOF_REGISTRY_REQUIRED"
        )

    try:
        value = prove_legal_evidence_provider_object_orphan(
            coverage_service=coverage_service,
            verification=verification,
            observation=observation,
            disownership=disownership,
            orphan_proof_reference=proof_reference,
            proved_at=proved_at,
        )
    except (
        LegalEvidenceProviderObjectOrphanProofError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as error:
        _fail(
            "L10A2R_C4D6D_B3_ORPHAN_PROOF_INVALID",
            error,
        )

    if value.tenant_id != tenant:
        _fail(
            "L10A2R_C4D6D_B3_TENANT_SCOPE_MISMATCH"
        )

    proof_fingerprint = _fingerprint(
        "orphan_proof_fingerprint",
        value.fingerprint,
    )

    subject_reference = _authorization_subject_reference(
        tenant_id=tenant,
        provider_name=value.provider_name,
        storage_reference=value.storage_reference,
        object_version_reference=value.object_version_reference,
        orphan_proof_reference=value.orphan_proof_reference,
    )

    subject_fingerprint = _canonical_digest(
        _subject_material(
            tenant_id=tenant,
            principal_id=principal,
            value=value,
        )
    )

    try:
        authorization = authorization_evidence_registry.issue(
            tenant_id=tenant,
            principal_id=principal,
            operation=OPERATION,
            permission=PERMISSION,
            subject_reference=subject_reference,
            subject_evidence_fingerprint=subject_fingerprint,
            idempotency_key=subject_reference,
            session=tx,
        )
    except (
        TenantAuthorizationDecisionEvidenceAuthorizationDeniedError
    ) as error:
        _fail(
            "L10A2R_C4D6D_B3_AUTHORIZATION_REQUIRED",
            error,
        )
    except (
        TenantAuthorizationDecisionEvidenceTransactionRequiredError
    ) as error:
        _fail(
            "L10A2R_C4D6D_B3_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )
    except TenantAuthorizationDecisionEvidenceConflictError as error:
        if str(
            error
        ) == "DUPLICATE_RETRY_TRANSACTION":
            _retry(
                "L10A2R_C4D6D_B3_WHOLE_TRANSACTION_RETRY_REQUIRED",
                error,
            )

        _fail(
            "L10A2R_C4D6D_B3_AUTHORIZATION_REPLAY_CONFLICT",
            error,
        )
    except (
        TenantAuthorizationDecisionEvidencePersistenceError,
        TenantAuthorizationDecisionEvidenceRegistryError,
    ) as error:
        _fail(
            "L10A2R_C4D6D_B3_AUTHORIZATION_EVIDENCE_UNAVAILABLE",
            error,
        )
    except Exception as error:
        _fail(
            "L10A2R_C4D6D_B3_AUTHORIZATION_EVIDENCE_UNAVAILABLE",
            error,
        )

    if (
        getattr(
            authorization,
            "tenant_id",
            None,
        )
        != tenant
        or getattr(
            authorization,
            "principal_id",
            None,
        )
        != principal
        or getattr(
            authorization,
            "operation",
            None,
        )
        != OPERATION
        or getattr(
            authorization,
            "permission",
            None,
        )
        != PERMISSION
        or getattr(
            authorization,
            "business_role",
            None,
        )
        != BUSINESS_ROLE
        or getattr(
            authorization,
            "authorization_role",
            None,
        )
        != AUTHORIZATION_ROLE
        or getattr(
            authorization,
            "subject_reference",
            None,
        )
        != subject_reference
        or getattr(
            authorization,
            "subject_evidence_fingerprint",
            None,
        )
        != subject_fingerprint
        or getattr(
            authorization,
            "idempotency_key",
            None,
        )
        != subject_reference
    ):
        _fail(
            "L10A2R_C4D6D_B3_AUTHORIZATION_CORRELATION_INVALID"
        )

    authorized_at = getattr(
        authorization,
        "authorized_at",
        None,
    )

    if (
        not isinstance(
            authorized_at,
            datetime,
        )
        or authorized_at.tzinfo is None
        or authorized_at.utcoffset() is None
    ):
        _fail(
            "L10A2R_C4D6D_B3_AUTHORIZATION_TIMESTAMP_INVALID"
        )

    if not proof_fingerprint:
        _fail(
            "L10A2R_C4D6D_B3_ORPHAN_PROOF_FINGERPRINT_INVALID"
        )

    try:
        persisted = orphan_proof_registry.create_or_replay(
            value,
            session=tx,
        )
    except (
        LegalEvidenceProviderObjectOrphanProofTransactionRequiredError
    ) as error:
        _fail(
            "L10A2R_C4D6D_B3_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )
    except (
        LegalEvidenceProviderObjectOrphanProofConflictError
    ) as error:
        if str(
            error
        ) == (
            "L10A2R_C4D6D_B2_WHOLE_TRANSACTION_RETRY_REQUIRED"
        ):
            _retry(
                "L10A2R_C4D6D_B3_WHOLE_TRANSACTION_RETRY_REQUIRED",
                error,
            )

        _fail(
            "L10A2R_C4D6D_B3_ORPHAN_PROOF_REPLAY_CONFLICT",
            error,
        )
    except (
        LegalEvidenceProviderObjectOrphanProofPersistedRecordInvalidError,
        LegalEvidenceProviderObjectOrphanProofPersistenceError,
        LegalEvidenceProviderObjectOrphanProofRegistryError,
    ) as error:
        _fail(
            "L10A2R_C4D6D_B3_ORPHAN_PROOF_PERSISTENCE_UNAVAILABLE",
            error,
        )
    except Exception as error:
        _fail(
            "L10A2R_C4D6D_B3_ORPHAN_PROOF_PERSISTENCE_UNAVAILABLE",
            error,
        )

    if persisted != value:
        _fail(
            "L10A2R_C4D6D_B3_POST_WRITE_CORRELATION_INVALID"
        )

    return persisted


__all__ = [
    "VERSION",
    "PERMISSION",
    "OPERATION",
    "BUSINESS_ROLE",
    "AUTHORIZATION_ROLE",
    "LegalEvidenceProviderObjectOrphanProofOrchestrationError",
    "LegalEvidenceProviderObjectOrphanProofOrchestrationRetryRequiredError",
    "issue_legal_evidence_provider_object_orphan_proof",
]

# ARTIFACT: legal_evidence_provider_object_orphan_proof_orchestrator.py
# VERSION: v1.0.1-L10A2R-C4D6D-B3-AUTHORIZED-ORPHAN-PROOF-ISSUANCE
# AUTHORITY BOUNDARY: authorized positive provider-object orphan-proof issuance only
# TENANT POSTURE: active authenticated identity and exact tenant-scoped B1/B2/IAM correlation
# TRANSACTION POSTURE: caller owns one already-active transaction and all retry lifecycle
# REPLAY POSTURE: IAM/B2 exact replay only; duplicate races require whole-transaction retry
# PRESERVATION POSTURE: no retention satisfaction or legal-hold release authority
# DELETION POSTURE: no cleanup eligibility, delete authorization or provider mutation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# FAIL-CLOSED POSTURE: invalid identity/session, prerequisite evidence, IAM correlation, replay divergence or persistence uncertainty rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
