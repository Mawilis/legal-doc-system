"""TITLE: Authorized Provider-Object Disownership Issuance Certification.
VERSION: v1.0.0-L10A2R-C4D6D-A3-AUTHORIZED-DISOWNERSHIP-ISSUANCE-CERT
AUTHORITY: Direct certification of the bounded C4D6D-A3 issuance composition.
EPITOME: Proves server-bound identity, same-transaction IAM, exact evidence
         correlation, A1 construction, A2 replay and whole-transaction retry.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_evidence_provider_object_disownership_orchestrator.py
COLLABORATION / OWNERSHIP: WILSY OS Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-10-01.
CHANGELOG: 2026-10-01 v1.0.0-L10A2R-C4D6D-A3-AUTHORIZED-DISOWNERSHIP-ISSUANCE-CERT
certifies the exact Legal Evidence IAM authorization -> positive disownership
fact -> durable A2 create/replay chain without orphan, preservation, deletion,
provider-mutation or financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Stable codes only; opaque references and SHA3-512.
TENANT BOUNDARY: Authenticated tenant/principal only; exact session propagation.
AUTHORITY BOUNDARY: Positive disownership fact issuance only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, cast

import pytest

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceAuthorizationDeniedError,
    TenantAuthorizationDecisionEvidenceConflictError,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_object_disownership import (
    LegalEvidenceProviderObjectDisownership,
)
from tools.eos.legal_operations.orchestration import (
    legal_evidence_provider_object_disownership_orchestrator as issuer,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_object_disownership_registry import (
    LegalEvidenceProviderObjectDisownershipConflictError,
)


TENANT = "tenant-a3"
PRINCIPAL = "principal-a3"

SOURCE_FP = hashlib.sha3_512(
    b"c4d6d-a3-source"
).hexdigest()

AUTH_FP = hashlib.sha3_512(
    b"c4d6d-a3-authorization"
).hexdigest()

AUTHORIZED_AT = datetime(
    2026,
    10,
    1,
    6,
    30,
    tzinfo=timezone.utc,
)


class _Session:
    in_transaction = True


def _identity(
    *,
    active: bool = True,
) -> SovereignIdentity:
    value = object.__new__(
        SovereignIdentity
    )

    object.__setattr__(
        value,
        "identity_id",
        PRINCIPAL,
    )
    object.__setattr__(
        value,
        "tenant_id",
        TENANT,
    )
    object.__setattr__(
        value,
        "status",
        (
            PrincipalStatus.ACTIVE
            if active
            else object()
        ),
    )

    return value


class _AuthorizationRegistry:
    def __init__(
        self,
        *,
        error: BaseException | None = None,
        mutate: dict[str, Any] | None = None,
    ) -> None:
        self.error = error
        self.mutate = mutate or {}
        self.calls: list[dict[str, Any]] = []

    def issue(
        self,
        **kwargs: Any,
    ) -> object:
        self.calls.append(
            kwargs
        )

        if self.error is not None:
            raise self.error

        body: dict[str, Any] = {
            "tenant_id":
                TENANT,
            "principal_id":
                PRINCIPAL,
            "operation":
                issuer.OPERATION,
            "permission":
                issuer.PERMISSION,
            "subject_reference":
                kwargs["subject_reference"],
            "subject_evidence_fingerprint":
                kwargs["subject_evidence_fingerprint"],
            "authorization_evidence_reference":
                "tenant-authorization-decision:a3",
            "authorization_evidence_fingerprint":
                AUTH_FP,
            "authorized_at":
                AUTHORIZED_AT,
        }

        body.update(
            self.mutate
        )

        return SimpleNamespace(
            **body
        )


class _DisownershipRegistry:
    def __init__(
        self,
        *,
        error: BaseException | None = None,
        divergent: bool = False,
    ) -> None:
        self.error = error
        self.divergent = divergent
        self.calls: list[
            tuple[
                LegalEvidenceProviderObjectDisownership,
                object,
            ]
        ] = []

    def create_or_replay(
        self,
        value: LegalEvidenceProviderObjectDisownership,
        *,
        session: object,
    ) -> LegalEvidenceProviderObjectDisownership:
        self.calls.append(
            (
                value,
                session,
            )
        )

        if self.error is not None:
            raise self.error

        if self.divergent:
            return LegalEvidenceProviderObjectDisownership(
                tenant_id=value.tenant_id,
                provider_name=value.provider_name,
                storage_reference=value.storage_reference,
                object_version_reference=value.object_version_reference,
                disownership_reference=value.disownership_reference,
                reason_reference="reason:divergent",
                source_evidence_reference=value.source_evidence_reference,
                source_evidence_fingerprint=value.source_evidence_fingerprint,
                authorization_evidence_reference=(
                    value.authorization_evidence_reference
                ),
                authorization_evidence_fingerprint=(
                    value.authorization_evidence_fingerprint
                ),
                decided_at=value.decided_at,
            )

        return value


def _issue(
    *,
    authorization_registry: Any | None = None,
    disownership_registry: Any | None = None,
    session: Any | None = None,
    identity: Any | None = None,
    reason_reference: str = "reason:a3",
) -> LegalEvidenceProviderObjectDisownership:
    return issuer.issue_legal_evidence_provider_object_disownership(
        identity=(
            _identity()
            if identity is None
            else identity
        ),
        provider_name="s3",
        storage_reference="bucket/object",
        object_version_reference="version-1",
        disownership_reference="disownership-a3",
        reason_reference=reason_reference,
        source_evidence_reference="source:a3",
        source_evidence_fingerprint=SOURCE_FP,
        authorization_evidence_registry=cast(
            Any,
            (
                _AuthorizationRegistry()
                if authorization_registry is None
                else authorization_registry
            ),
        ),
        disownership_registry=cast(
            Any,
            (
                _DisownershipRegistry()
                if disownership_registry is None
                else disownership_registry
            ),
        ),
        session=(
            _Session()
            if session is None
            else session
        ),
    )


def test_constants_are_exact_and_nonfinancial() -> None:
    assert (
        issuer.PERMISSION
        == "legal_operations:evidence:write"
    )
    assert (
        issuer.OPERATION
        == "legal_evidence_write"
    )
    assert (
        issuer.AUTHORIZATION_SUBJECT_PREFIX
        == "legal-evidence-provider-object-disownership"
    )


def test_success_copies_iam_evidence_and_same_session_exactly() -> None:
    auth = _AuthorizationRegistry()
    registry = _DisownershipRegistry()
    session = _Session()

    value = _issue(
        authorization_registry=auth,
        disownership_registry=registry,
        session=session,
    )

    assert len(
        auth.calls
    ) == 1

    call = auth.calls[0]

    assert call["tenant_id"] == TENANT
    assert call["principal_id"] == PRINCIPAL
    assert call["operation"] == issuer.OPERATION
    assert call["permission"] == issuer.PERMISSION
    assert call["session"] is session

    assert (
        call["idempotency_key"]
        == call["subject_reference"]
    )

    assert call[
        "subject_reference"
    ].startswith(
        issuer.AUTHORIZATION_SUBJECT_PREFIX
        + ":"
    )

    expected_subject_fingerprint = hashlib.sha3_512(
        json.dumps(
            {
                "tenant_id":
                    TENANT,
                "actor_principal_id":
                    PRINCIPAL,
                "provider_name":
                    "s3",
                "storage_reference":
                    "bucket/object",
                "object_version_reference":
                    "version-1",
                "disownership_reference":
                    "disownership-a3",
                "reason_reference":
                    "reason:a3",
                "source_evidence_reference":
                    "source:a3",
                "source_evidence_fingerprint":
                    SOURCE_FP,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode(
            "utf-8"
        )
    ).hexdigest()

    assert (
        call["subject_evidence_fingerprint"]
        == expected_subject_fingerprint
    )

    assert value.tenant_id == TENANT
    assert value.provider_name == "s3"
    assert value.storage_reference == "bucket/object"
    assert value.object_version_reference == "version-1"
    assert value.disownership_reference == "disownership-a3"
    assert value.reason_reference == "reason:a3"
    assert value.source_evidence_reference == "source:a3"
    assert value.source_evidence_fingerprint == SOURCE_FP

    assert (
        value.authorization_evidence_reference
        == "tenant-authorization-decision:a3"
    )

    assert (
        value.authorization_evidence_fingerprint
        == AUTH_FP
    )

    assert value.decided_at == AUTHORIZED_AT
    assert len(value.fingerprint) == 128

    assert len(
        registry.calls
    ) == 1

    persisted_value, persisted_session = registry.calls[0]

    assert persisted_value == value
    assert persisted_session is session


def test_inactive_transaction_fails_before_authority() -> None:
    auth = _AuthorizationRegistry()
    registry = _DisownershipRegistry()

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectDisownershipOrchestrationError
    ) as captured:
        _issue(
            authorization_registry=auth,
            disownership_registry=registry,
            session=SimpleNamespace(
                in_transaction=False
            ),
        )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_A3_ACTIVE_TRANSACTION_REQUIRED"
    )

    assert auth.calls == []
    assert registry.calls == []


def test_inactive_identity_fails_before_authority() -> None:
    auth = _AuthorizationRegistry()
    registry = _DisownershipRegistry()

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectDisownershipOrchestrationError
    ) as captured:
        _issue(
            authorization_registry=auth,
            disownership_registry=registry,
            identity=_identity(
                active=False
            ),
        )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_A3_PRINCIPAL_INACTIVE"
    )

    assert auth.calls == []
    assert registry.calls == []


def test_iam_denial_fails_before_disownership_persistence() -> None:
    auth = _AuthorizationRegistry(
        error=TenantAuthorizationDecisionEvidenceAuthorizationDeniedError(
            "AUTHORIZATION_DENIED"
        )
    )
    registry = _DisownershipRegistry()

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectDisownershipOrchestrationError
    ) as captured:
        _issue(
            authorization_registry=auth,
            disownership_registry=registry,
        )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_A3_AUTHORIZATION_REQUIRED"
    )

    assert registry.calls == []


def test_iam_duplicate_race_requires_whole_transaction_retry() -> None:
    auth = _AuthorizationRegistry(
        error=TenantAuthorizationDecisionEvidenceConflictError(
            "DUPLICATE_RETRY_TRANSACTION"
        )
    )

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectDisownershipOrchestrationRetryRequiredError
    ) as captured:
        _issue(
            authorization_registry=auth,
        )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_A3_WHOLE_TRANSACTION_RETRY_REQUIRED"
    )


def test_iam_idempotency_divergence_fails_closed_without_retry() -> None:
    auth = _AuthorizationRegistry(
        error=TenantAuthorizationDecisionEvidenceConflictError(
            "IDEMPOTENCY_CONFLICT"
        )
    )

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectDisownershipOrchestrationError
    ) as captured:
        _issue(
            authorization_registry=auth,
        )

    assert not isinstance(
        captured.value,
        issuer.LegalEvidenceProviderObjectDisownershipOrchestrationRetryRequiredError,
    )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_A3_AUTHORIZATION_REPLAY_CONFLICT"
    )


def test_authorization_correlation_mismatch_rejects_before_a2() -> None:
    auth = _AuthorizationRegistry(
        mutate={
            "principal_id":
                "other-principal",
        }
    )
    registry = _DisownershipRegistry()

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectDisownershipOrchestrationError
    ) as captured:
        _issue(
            authorization_registry=auth,
            disownership_registry=registry,
        )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_A3_AUTHORIZATION_CORRELATION_INVALID"
    )

    assert registry.calls == []


def test_a2_duplicate_race_requires_whole_transaction_retry() -> None:
    registry = _DisownershipRegistry(
        error=LegalEvidenceProviderObjectDisownershipConflictError(
            "L10A2R_C4D6D_A2_WHOLE_TRANSACTION_RETRY_REQUIRED"
        )
    )

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectDisownershipOrchestrationRetryRequiredError
    ) as captured:
        _issue(
            disownership_registry=registry,
        )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_A3_WHOLE_TRANSACTION_RETRY_REQUIRED"
    )


def test_a2_divergence_fails_closed_without_retry() -> None:
    registry = _DisownershipRegistry(
        error=LegalEvidenceProviderObjectDisownershipConflictError(
            "L10A2R_C4D6D_A2_IMMUTABLE_REPLAY_DIVERGENCE"
        )
    )

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectDisownershipOrchestrationError
    ) as captured:
        _issue(
            disownership_registry=registry,
        )

    assert not isinstance(
        captured.value,
        issuer.LegalEvidenceProviderObjectDisownershipOrchestrationRetryRequiredError,
    )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_A3_DISOWNERSHIP_REPLAY_CONFLICT"
    )


def test_post_write_correlation_mismatch_fails_closed() -> None:
    with pytest.raises(
        issuer.LegalEvidenceProviderObjectDisownershipOrchestrationError
    ) as captured:
        _issue(
            disownership_registry=_DisownershipRegistry(
                divergent=True
            ),
        )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_A3_POST_WRITE_CORRELATION_INVALID"
    )


def test_subject_identity_stable_but_decision_fingerprint_sensitive() -> None:
    first = _AuthorizationRegistry()
    second = _AuthorizationRegistry()

    _issue(
        authorization_registry=first,
        reason_reference="reason:a3",
    )

    _issue(
        authorization_registry=second,
        reason_reference="reason:a3-changed",
    )

    first_call = first.calls[0]
    second_call = second.calls[0]

    assert (
        first_call["subject_reference"]
        == second_call["subject_reference"]
    )

    assert (
        first_call["subject_evidence_fingerprint"]
        != second_call["subject_evidence_fingerprint"]
    )


# ARTIFACT: test_legal_evidence_provider_object_disownership_orchestrator.py
# VERSION: v1.0.0-L10A2R-C4D6D-A3-AUTHORIZED-DISOWNERSHIP-ISSUANCE-CERT
# AUTHORITY BOUNDARY: direct certification of authorized positive disownership issuance only
# TENANT POSTURE: active authenticated identity and exact same-transaction propagation
# REPLAY POSTURE: IAM/A2 exact replay only; duplicate races require whole-transaction retry
# ORPHAN POSTURE: no orphan proof
# PRESERVATION POSTURE: no retention satisfaction or legal-hold release
# DELETION POSTURE: no cleanup eligibility, delete authorization or provider mutation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
