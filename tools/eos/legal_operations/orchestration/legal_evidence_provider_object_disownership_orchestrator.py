"""WILSY OS authorized provider-object disownership issuance.

TITLE: WILSY OS Authorized Provider-Object Disownership Issuance
VERSION: v1.0.0-L10A2R-C4D6D-A3-AUTHORIZED-DISOWNERSHIP-ISSUANCE
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Issue one positive provider-object disownership fact only after durable,
         tenant-scoped Legal Evidence IAM authorization succeeds in the same
         caller-owned transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_evidence_provider_object_disownership_orchestrator.py
COLLABORATION / OWNERSHIP: C4D6D-A1 owns the immutable disownership fact;
                            C4D6D-A2 owns durable exact persistence/replay;
                            IAM owns authorization truth and evidence;
                            C4D6D-A3 owns only their bounded issuance composition.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG: 2026-10-01 v1.0.0-L10A2R-C4D6D-A3-AUTHORIZED-DISOWNERSHIP-ISSUANCE
           establishes same-transaction Legal Evidence authorization followed by
           exact durable disownership creation/replay. Tenant and principal are
           server-bound to SovereignIdentity; IAM evidence reference, fingerprint
           and authorized_at are copied exactly into the disownership fact.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque bounded references and deterministic SHA3-512
                             subject evidence only; errors contain stable codes.
TENANT BOUNDARY: Tenant and principal derive only from one active authenticated
                 SovereignIdentity and the exact caller-owned transaction.
AUTHORITY BOUNDARY: Positive provider-object disownership issuance only.
                    Disownership is not orphan proof, cleanup eligibility,
                    retention satisfaction, legal-hold release, delete
                    authorization, provider deletion or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement.
TRANSACTION BOUNDARY: Caller supplies and owns one already-active transaction.
                      This module never starts, commits, aborts or retries it.
FAIL-CLOSED DECLARATION: Invalid identity/session, denied or divergent IAM,
                         malformed authorization correlation, domain invalidity,
                         durable divergence and persistence uncertainty reject.
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
    LegalEvidenceProviderObjectDisownershipError,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_object_disownership_registry import (
    LegalEvidenceProviderObjectDisownershipConflictError,
    LegalEvidenceProviderObjectDisownershipPersistedRecordInvalidError,
    LegalEvidenceProviderObjectDisownershipPersistenceError,
    LegalEvidenceProviderObjectDisownershipRegistry,
    LegalEvidenceProviderObjectDisownershipRegistryError,
    LegalEvidenceProviderObjectDisownershipTransactionRequiredError,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4D6D-A3-AUTHORIZED-DISOWNERSHIP-ISSUANCE"
)
PERMISSION: Final[str] = "legal_operations:evidence:write"
OPERATION: Final[str] = "legal_evidence_write"
AUTHORIZATION_SUBJECT_PREFIX: Final[str] = (
    "legal-evidence-provider-object-disownership"
)

_HEX = re.compile(r"[0-9a-f]{128}\Z")


class LegalEvidenceProviderObjectDisownershipOrchestrationError(
    RuntimeError
):
    """Stable fail-closed issuance error containing only one semantic code."""

    def __init__(
        self,
        code: str,
    ) -> None:
        """Retain one bounded machine-stable failure code."""
        self.code = code
        super().__init__(
            code
        )


class LegalEvidenceProviderObjectDisownershipOrchestrationRetryRequiredError(
    LegalEvidenceProviderObjectDisownershipOrchestrationError
):
    """Caller must abort and restart the complete transaction."""


def _fail(
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one bounded fail-closed orchestration error."""
    error = LegalEvidenceProviderObjectDisownershipOrchestrationError(
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
        LegalEvidenceProviderObjectDisownershipOrchestrationRetryRequiredError(
            code
        )
    ) from cause


def _active_session(
    session: Any,
) -> Any:
    """Require one already-active caller-owned transaction before authority work."""
    if session is None:
        _fail(
            "L10A2R_C4D6D_A3_ACTIVE_TRANSACTION_REQUIRED"
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
            "L10A2R_C4D6D_A3_ACTIVE_TRANSACTION_REQUIRED"
        )

    return session


def _identity(
    identity: SovereignIdentity,
) -> tuple[str, str]:
    """Derive exact tenant and principal only from active authenticated identity."""
    if not isinstance(
        identity,
        SovereignIdentity,
    ):
        _fail(
            "L10A2R_C4D6D_A3_IDENTITY_REQUIRED"
        )

    if identity.status is not PrincipalStatus.ACTIVE:
        _fail(
            "L10A2R_C4D6D_A3_PRINCIPAL_INACTIVE"
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
            "L10A2R_C4D6D_A3_IDENTITY_INVALID"
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
            "L10A2R_C4D6D_A3_"
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
            "L10A2R_C4D6D_A3_"
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


def _subject_material(
    *,
    tenant_id: str,
    principal_id: str,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
    disownership_reference: str,
    reason_reference: str,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
) -> dict[str, object]:
    """Bind authorization to the exact proposed positive disownership decision."""
    return {
        "tenant_id":
            tenant_id,
        "actor_principal_id":
            principal_id,
        "provider_name":
            provider_name,
        "storage_reference":
            storage_reference,
        "object_version_reference":
            object_version_reference,
        "disownership_reference":
            disownership_reference,
        "reason_reference":
            reason_reference,
        "source_evidence_reference":
            source_evidence_reference,
        "source_evidence_fingerprint":
            source_evidence_fingerprint,
    }


def _authorization_subject_reference(
    *,
    tenant_id: str,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
    disownership_reference: str,
) -> str:
    """Create one stable IAM subject identity for this proposed disownership."""
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
            "disownership_reference":
                disownership_reference,
        }
    )

    return (
        f"{AUTHORIZATION_SUBJECT_PREFIX}:"
        f"{identity_digest}"
    )


def issue_legal_evidence_provider_object_disownership(
    *,
    identity: SovereignIdentity,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
    disownership_reference: str,
    reason_reference: str,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
    authorization_evidence_registry: TenantAuthorizationDecisionEvidenceRegistry,
    disownership_registry: LegalEvidenceProviderObjectDisownershipRegistry,
    session: Any,
) -> LegalEvidenceProviderObjectDisownership:
    """Authorize and persist/replay one positive provider-object disownership.

    Tenant and principal come only from ``identity``. The exact caller-owned
    active transaction is forwarded into IAM and A2. IAM alone creates the
    authorization evidence reference, authorization evidence fingerprint and
    authorization timestamp. Those values are copied into A1 unchanged.

    This function does not prove orphan status, satisfy retention, release
    legal hold, authorize deletion, mutate provider storage, or create
    financial execution or settlement authority.
    """
    tx = _active_session(
        session
    )

    tenant, principal = _identity(
        identity
    )

    provider = _text(
        "provider_name",
        provider_name,
        maximum=240,
    )
    storage = _text(
        "storage_reference",
        storage_reference,
        maximum=2048,
    )
    object_version = _text(
        "object_version_reference",
        object_version_reference,
        maximum=1024,
    )
    disownership = _text(
        "disownership_reference",
        disownership_reference,
        maximum=240,
    )
    reason = _text(
        "reason_reference",
        reason_reference,
        maximum=240,
    )
    source_reference = _text(
        "source_evidence_reference",
        source_evidence_reference,
        maximum=1024,
    )
    source_fingerprint = _fingerprint(
        "source_evidence_fingerprint",
        source_evidence_fingerprint,
    )

    if not callable(
        getattr(
            authorization_evidence_registry,
            "issue",
            None,
        )
    ):
        _fail(
            "L10A2R_C4D6D_A3_AUTHORIZATION_EVIDENCE_REGISTRY_REQUIRED"
        )

    if not callable(
        getattr(
            disownership_registry,
            "create_or_replay",
            None,
        )
    ):
        _fail(
            "L10A2R_C4D6D_A3_DISOWNERSHIP_REGISTRY_REQUIRED"
        )

    subject_reference = _authorization_subject_reference(
        tenant_id=tenant,
        provider_name=provider,
        storage_reference=storage,
        object_version_reference=object_version,
        disownership_reference=disownership,
    )

    subject_fingerprint = _canonical_digest(
        _subject_material(
            tenant_id=tenant,
            principal_id=principal,
            provider_name=provider,
            storage_reference=storage,
            object_version_reference=object_version,
            disownership_reference=disownership,
            reason_reference=reason,
            source_evidence_reference=source_reference,
            source_evidence_fingerprint=source_fingerprint,
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
            "L10A2R_C4D6D_A3_AUTHORIZATION_REQUIRED",
            error,
        )
    except (
        TenantAuthorizationDecisionEvidenceTransactionRequiredError
    ) as error:
        _fail(
            "L10A2R_C4D6D_A3_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )
    except TenantAuthorizationDecisionEvidenceConflictError as error:
        if str(
            error
        ) == "DUPLICATE_RETRY_TRANSACTION":
            _retry(
                "L10A2R_C4D6D_A3_WHOLE_TRANSACTION_RETRY_REQUIRED",
                error,
            )

        _fail(
            "L10A2R_C4D6D_A3_AUTHORIZATION_REPLAY_CONFLICT",
            error,
        )
    except (
        TenantAuthorizationDecisionEvidencePersistenceError,
        TenantAuthorizationDecisionEvidenceRegistryError,
    ) as error:
        _fail(
            "L10A2R_C4D6D_A3_AUTHORIZATION_EVIDENCE_UNAVAILABLE",
            error,
        )
    except Exception as error:
        _fail(
            "L10A2R_C4D6D_A3_AUTHORIZATION_EVIDENCE_UNAVAILABLE",
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
    ):
        _fail(
            "L10A2R_C4D6D_A3_AUTHORIZATION_CORRELATION_INVALID"
        )

    authorization_reference = _text(
        "authorization_evidence_reference",
        getattr(
            authorization,
            "authorization_evidence_reference",
            None,
        ),
        maximum=1024,
    )

    authorization_fingerprint = _fingerprint(
        "authorization_evidence_fingerprint",
        getattr(
            authorization,
            "authorization_evidence_fingerprint",
            None,
        ),
    )

    decided_at = getattr(
        authorization,
        "authorized_at",
        None,
    )

    if (
        not isinstance(
            decided_at,
            datetime,
        )
        or decided_at.tzinfo is None
        or decided_at.utcoffset() is None
    ):
        _fail(
            "L10A2R_C4D6D_A3_AUTHORIZATION_TIMESTAMP_INVALID"
        )

    try:
        value = LegalEvidenceProviderObjectDisownership(
            tenant_id=tenant,
            provider_name=provider,
            storage_reference=storage,
            object_version_reference=object_version,
            disownership_reference=disownership,
            reason_reference=reason,
            source_evidence_reference=source_reference,
            source_evidence_fingerprint=source_fingerprint,
            authorization_evidence_reference=authorization_reference,
            authorization_evidence_fingerprint=authorization_fingerprint,
            decided_at=decided_at,
        )
    except (
        LegalEvidenceProviderObjectDisownershipError,
        TypeError,
        ValueError,
    ) as error:
        _fail(
            "L10A2R_C4D6D_A3_DISOWNERSHIP_INVALID",
            error,
        )

    try:
        persisted = disownership_registry.create_or_replay(
            value,
            session=tx,
        )
    except (
        LegalEvidenceProviderObjectDisownershipTransactionRequiredError
    ) as error:
        _fail(
            "L10A2R_C4D6D_A3_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )
    except (
        LegalEvidenceProviderObjectDisownershipConflictError
    ) as error:
        if str(
            error
        ) == (
            "L10A2R_C4D6D_A2_WHOLE_TRANSACTION_RETRY_REQUIRED"
        ):
            _retry(
                "L10A2R_C4D6D_A3_WHOLE_TRANSACTION_RETRY_REQUIRED",
                error,
            )

        _fail(
            "L10A2R_C4D6D_A3_DISOWNERSHIP_REPLAY_CONFLICT",
            error,
        )
    except (
        LegalEvidenceProviderObjectDisownershipPersistedRecordInvalidError,
        LegalEvidenceProviderObjectDisownershipPersistenceError,
        LegalEvidenceProviderObjectDisownershipRegistryError,
    ) as error:
        _fail(
            "L10A2R_C4D6D_A3_DISOWNERSHIP_PERSISTENCE_UNAVAILABLE",
            error,
        )
    except Exception as error:
        _fail(
            "L10A2R_C4D6D_A3_DISOWNERSHIP_PERSISTENCE_UNAVAILABLE",
            error,
        )

    if persisted != value:
        _fail(
            "L10A2R_C4D6D_A3_POST_WRITE_CORRELATION_INVALID"
        )

    return persisted


__all__ = [
    "AUTHORIZATION_SUBJECT_PREFIX",
    "OPERATION",
    "PERMISSION",
    "VERSION",
    "LegalEvidenceProviderObjectDisownershipOrchestrationError",
    "LegalEvidenceProviderObjectDisownershipOrchestrationRetryRequiredError",
    "issue_legal_evidence_provider_object_disownership",
]


# ARTIFACT: legal_evidence_provider_object_disownership_orchestrator.py
# VERSION: v1.0.0-L10A2R-C4D6D-A3-AUTHORIZED-DISOWNERSHIP-ISSUANCE
# AUTHORITY BOUNDARY: authorized positive provider-object disownership issuance only
# TENANT POSTURE: tenant and principal derive only from active SovereignIdentity
# TRANSACTION POSTURE: caller owns one already-active transaction and all retry lifecycle
# REPLAY POSTURE: IAM and A2 exact replay only; divergence fails closed
# ORPHAN POSTURE: disownership issuance is not orphan proof
# PRESERVATION POSTURE: no retention satisfaction or legal-hold release authority
# DELETION POSTURE: no cleanup eligibility, delete authorization or provider mutation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
