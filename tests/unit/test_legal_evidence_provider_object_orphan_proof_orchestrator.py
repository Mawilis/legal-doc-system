"""Direct certificate for authorized provider-object orphan-proof issuance.

TITLE: Authorized Provider-Object Orphan-Proof Issuance Certification
VERSION: v1.0.0-L10A2R-C4D6D-B3-AUTHORIZED-ORPHAN-PROOF-ISSUANCE-CERT
AUTHORITY: Direct certification of bounded C4D6D-B3 issuance composition.
EPITOME: Certifies server-bound identity, pure B1 candidate derivation, exact
         same-transaction IAM authorization, B2 persistence/replay, fail-closed
         divergence and whole-transaction retry without downstream authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_evidence_provider_object_orphan_proof_orchestrator.py
COLLABORATION / OWNERSHIP: WILSY OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG: 2026-10-01 v1.0.0-L10A2R-C4D6D-B3-AUTHORIZED-ORPHAN-PROOF-ISSUANCE-CERT
           establishes direct behavioral certification of B3 against the frozen
           B1, B2 and Legal Evidence IAM contracts.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque references and deterministic SHA3-512 only.
TENANT BOUNDARY: Tenant/principal derive only from authenticated identity and
                 exact B1/B2 evidence remains tenant scoped.
AUTHORITY BOUNDARY: Positive orphan-proof issuance only; no retention, legal
                    hold, cleanup, deletion or provider mutation authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
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
from tools.eos.legal_operations.domain.legal_evidence_provider_object_orphan_proof import (
    LegalEvidenceProviderObjectOrphanProof,
)
from tools.eos.legal_operations.orchestration import (
    legal_evidence_provider_object_orphan_proof_orchestrator as issuer,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_object_orphan_proof_registry import (
    LegalEvidenceProviderObjectOrphanProofConflictError,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectIntentMetadataState,
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceProviderDiscoveryScope,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_enumeration_port import (
    LegalEvidenceProviderCoverageEnumerationPort,
    LegalEvidenceProviderEnumerationKind,
    LegalEvidenceProviderEnumerationPage,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_verification_service import (
    LegalEvidenceProviderCoverageVerification,
    LegalEvidenceProviderCoverageVerificationService,
)


TENANT = "tenant-b1-cert"
PRINCIPAL = "principal-b3-cert"

AT = datetime(
    2026,
    10,
    1,
    10,
    0,
    tzinfo=timezone.utc,
)

AUTHORIZED_AT = datetime(
    2026,
    10,
    1,
    10,
    30,
    tzinfo=timezone.utc,
)

SHA_A = "a" * 128
SHA_B = "b" * 128


class _Session:
    in_transaction = True


class _InactiveSession:
    in_transaction = False


def _identity(
    *,
    active: bool = True,
    tenant_id: str = TENANT,
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
        tenant_id,
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


def _scope(
    *,
    tenant_id: str = TENANT,
) -> LegalEvidenceProviderDiscoveryScope:
    return LegalEvidenceProviderDiscoveryScope(
        tenant_id=tenant_id,
        tenant_scope_fingerprint=SHA_A,
    )


def _completed(
    *,
    tenant_id: str = TENANT,
    provider_name: str = "aws_s3",
    storage_reference: str = "opaque/storage/b3-cert",
    object_version_reference: str = "version-b3-cert",
    observed_at: datetime = AT,
) -> LegalEvidenceCompletedObjectObservation:
    return LegalEvidenceCompletedObjectObservation(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        provider_integrity_reference='"etag-b3-cert"',
        content_length=17,
        last_modified_at=observed_at,
        observed_at=observed_at,
        write_intent_metadata_state=(
            LegalEvidenceCompletedObjectIntentMetadataState.ABSENT
        ),
        write_intent_fingerprint=None,
    )


def _page(
    *,
    scope: LegalEvidenceProviderDiscoveryScope,
    kind: LegalEvidenceProviderEnumerationKind,
    observations: tuple[Any, ...] = (),
) -> LegalEvidenceProviderEnumerationPage:
    return LegalEvidenceProviderEnumerationPage(
        tenant_id=scope.tenant_id,
        tenant_scope_fingerprint=scope.tenant_scope_fingerprint,
        provider_name="aws_s3",
        enumeration_kind=kind,
        observed_at=AT,
        observations=observations,
        next_page_reference=None,
    )


class _Provider:
    def __init__(
        self,
        *,
        scope: LegalEvidenceProviderDiscoveryScope,
        completed: tuple[
            LegalEvidenceCompletedObjectObservation,
            ...,
        ] = (),
    ) -> None:
        self.scope = scope
        self.completed = completed

    def list_incomplete_write_session_page(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: datetime,
        page_reference: str | None,
    ) -> LegalEvidenceProviderEnumerationPage:
        assert scope == self.scope
        assert observed_at == AT
        assert page_reference is None

        return _page(
            scope=scope,
            kind=(
                LegalEvidenceProviderEnumerationKind
                .INCOMPLETE_WRITE_SESSIONS
            ),
        )

    def list_completed_object_version_page(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: datetime,
        page_reference: str | None,
    ) -> LegalEvidenceProviderEnumerationPage:
        assert scope == self.scope
        assert observed_at == AT
        assert page_reference is None

        return _page(
            scope=scope,
            kind=(
                LegalEvidenceProviderEnumerationKind
                .COMPLETED_OBJECT_VERSIONS
            ),
            observations=cast(
                tuple[Any, ...],
                self.completed,
            ),
        )


def _service(
    *,
    scope: LegalEvidenceProviderDiscoveryScope,
    completed: tuple[
        LegalEvidenceCompletedObjectObservation,
        ...,
    ] = (),
) -> LegalEvidenceProviderCoverageVerificationService:
    provider = _Provider(
        scope=scope,
        completed=completed,
    )

    assert isinstance(
        provider,
        LegalEvidenceProviderCoverageEnumerationPort,
    )

    return LegalEvidenceProviderCoverageVerificationService(
        provider=provider,
    )


def _disownership(
    *,
    tenant_id: str = TENANT,
    provider_name: str = "aws_s3",
    storage_reference: str = "opaque/storage/b3-cert",
    object_version_reference: str = "version-b3-cert",
) -> LegalEvidenceProviderObjectDisownership:
    return LegalEvidenceProviderObjectDisownership(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        disownership_reference="disownership-b3-cert",
        reason_reference="reason-b3-cert",
        source_evidence_reference="source-b3-cert",
        source_evidence_fingerprint=SHA_A,
        authorization_evidence_reference="authorization-b3-cert",
        authorization_evidence_fingerprint=SHA_B,
        decided_at=AT - timedelta(minutes=5),
    )


def _prerequisites() -> tuple[
    LegalEvidenceProviderCoverageVerificationService,
    LegalEvidenceProviderCoverageVerification,
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceProviderObjectDisownership,
]:
    scope = _scope()
    observation = _completed()

    service = _service(
        scope=scope,
        completed=(observation,),
    )

    verification = service.verify_coverage(
        scope=scope,
        provider_name="aws_s3",
        observed_at=AT,
    )

    return (
        service,
        verification,
        observation,
        _disownership(),
    )


class _AuthorizationRegistry:
    def __init__(
        self,
        *,
        error: BaseException | None = None,
        mutate: dict[str, Any] | None = None,
        events: list[str] | None = None,
    ) -> None:
        self.error = error
        self.mutate = mutate or {}
        self.events = events
        self.calls: list[dict[str, Any]] = []

    def issue(
        self,
        **kwargs: Any,
    ) -> object:
        self.calls.append(
            kwargs
        )

        if self.events is not None:
            self.events.append(
                "iam"
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
            "business_role":
                issuer.BUSINESS_ROLE,
            "authorization_role":
                issuer.AUTHORIZATION_ROLE,
            "subject_reference":
                kwargs["subject_reference"],
            "subject_evidence_fingerprint":
                kwargs["subject_evidence_fingerprint"],
            "idempotency_key":
                kwargs["idempotency_key"],
            "authorization_evidence_reference":
                "tenant-authorization-decision:b3",
            "authorization_evidence_fingerprint":
                SHA_B,
            "authorized_at":
                AUTHORIZED_AT,
        }

        body.update(
            self.mutate
        )

        return SimpleNamespace(
            **body
        )


class _OrphanProofRegistry:
    def __init__(
        self,
        *,
        error: BaseException | None = None,
        divergent: bool = False,
        events: list[str] | None = None,
    ) -> None:
        self.error = error
        self.divergent = divergent
        self.events = events
        self.calls: list[
            tuple[
                LegalEvidenceProviderObjectOrphanProof,
                object,
            ]
        ] = []

    def create_or_replay(
        self,
        value: LegalEvidenceProviderObjectOrphanProof,
        *,
        session: object,
    ) -> LegalEvidenceProviderObjectOrphanProof:
        self.calls.append(
            (
                value,
                session,
            )
        )

        if self.events is not None:
            self.events.append(
                "b2"
            )

        if self.error is not None:
            raise self.error

        if self.divergent:
            return cast(
                LegalEvidenceProviderObjectOrphanProof,
                object(),
            )

        return value


def _issue(
    *,
    identity: Any | None = None,
    session: Any | None = None,
    authorization_registry: Any | None = None,
    orphan_proof_registry: Any | None = None,
    orphan_proof_reference: str = "orphan-proof-b3-cert",
    proved_at: datetime = AT + timedelta(minutes=1),
    disownership: Any | None = None,
) -> LegalEvidenceProviderObjectOrphanProof:
    (
        service,
        verification,
        observation,
        canonical_disownership,
    ) = _prerequisites()

    return issuer.issue_legal_evidence_provider_object_orphan_proof(
        identity=(
            _identity()
            if identity is None
            else identity
        ),
        coverage_service=service,
        verification=verification,
        observation=observation,
        disownership=(
            canonical_disownership
            if disownership is None
            else disownership
        ),
        orphan_proof_reference=orphan_proof_reference,
        proved_at=proved_at,
        authorization_evidence_registry=cast(
            Any,
            (
                _AuthorizationRegistry()
                if authorization_registry is None
                else authorization_registry
            ),
        ),
        orphan_proof_registry=cast(
            Any,
            (
                _OrphanProofRegistry()
                if orphan_proof_registry is None
                else orphan_proof_registry
            ),
        ),
        session=(
            _Session()
            if session is None
            else session
        ),
    )


def test_constants_are_exact_and_authority_is_bounded() -> None:
    assert (
        issuer.VERSION
        == "v1.0.1-L10A2R-C4D6D-B3-AUTHORIZED-ORPHAN-PROOF-ISSUANCE"
    )
    assert issuer.PERMISSION == "legal_operations:evidence:write"
    assert issuer.OPERATION == "legal_evidence_write"
    assert issuer.BUSINESS_ROLE == "tenant_legal_partner"
    assert issuer.AUTHORIZATION_ROLE == "LEGAL_PARTNER"
    assert (
        issuer.AUTHORIZATION_SUBJECT_PREFIX
        == "legal-evidence-provider-object-orphan-proof"
    )


def test_success_uses_same_session_and_orders_iam_before_b2() -> None:
    events: list[str] = []
    auth = _AuthorizationRegistry(
        events=events,
    )
    registry = _OrphanProofRegistry(
        events=events,
    )
    session = _Session()

    value = _issue(
        authorization_registry=auth,
        orphan_proof_registry=registry,
        session=session,
    )

    assert events == [
        "iam",
        "b2",
    ]

    assert len(auth.calls) == 1
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

    assert len(
        call["subject_evidence_fingerprint"]
    ) == 128

    assert len(registry.calls) == 1

    persisted, persisted_session = registry.calls[0]

    assert persisted == value
    assert persisted_session is session
    assert value.tenant_id == TENANT


def test_inactive_transaction_fails_before_b1_iam_and_b2(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    auth = _AuthorizationRegistry()
    registry = _OrphanProofRegistry()
    b1_calls: list[str] = []

    def forbidden_b1(
        **_: Any,
    ) -> Any:
        b1_calls.append(
            "called"
        )
        raise AssertionError(
            "B1 must not run"
        )

    monkeypatch.setattr(
        issuer,
        "prove_legal_evidence_provider_object_orphan",
        forbidden_b1,
    )

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectOrphanProofOrchestrationError
    ) as captured:
        _issue(
            session=_InactiveSession(),
            authorization_registry=auth,
            orphan_proof_registry=registry,
        )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_B3_ACTIVE_TRANSACTION_REQUIRED"
    )
    assert b1_calls == []
    assert auth.calls == []
    assert registry.calls == []


def test_inactive_identity_fails_before_b1_iam_and_b2(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    auth = _AuthorizationRegistry()
    registry = _OrphanProofRegistry()
    b1_calls: list[str] = []

    def forbidden_b1(
        **_: Any,
    ) -> Any:
        b1_calls.append(
            "called"
        )
        raise AssertionError(
            "B1 must not run"
        )

    monkeypatch.setattr(
        issuer,
        "prove_legal_evidence_provider_object_orphan",
        forbidden_b1,
    )

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectOrphanProofOrchestrationError
    ) as captured:
        _issue(
            identity=_identity(
                active=False,
            ),
            authorization_registry=auth,
            orphan_proof_registry=registry,
        )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_B3_PRINCIPAL_INACTIVE"
    )
    assert b1_calls == []
    assert auth.calls == []
    assert registry.calls == []


def test_b1_tenant_mismatch_fails_before_iam_and_b2() -> None:
    auth = _AuthorizationRegistry()
    registry = _OrphanProofRegistry()

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectOrphanProofOrchestrationError
    ) as captured:
        _issue(
            identity=_identity(
                tenant_id="tenant-other",
            ),
            authorization_registry=auth,
            orphan_proof_registry=registry,
        )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_B3_TENANT_SCOPE_MISMATCH"
    )
    assert auth.calls == []
    assert registry.calls == []


def test_invalid_b1_prerequisite_fails_before_iam_and_b2() -> None:
    auth = _AuthorizationRegistry()
    registry = _OrphanProofRegistry()

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectOrphanProofOrchestrationError
    ) as captured:
        _issue(
            disownership=object(),
            authorization_registry=auth,
            orphan_proof_registry=registry,
        )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_B3_ORPHAN_PROOF_INVALID"
    )
    assert auth.calls == []
    assert registry.calls == []


def test_iam_denial_fails_before_b2() -> None:
    auth = _AuthorizationRegistry(
        error=TenantAuthorizationDecisionEvidenceAuthorizationDeniedError(
            "AUTHORIZATION_DENIED"
        )
    )
    registry = _OrphanProofRegistry()

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectOrphanProofOrchestrationError
    ) as captured:
        _issue(
            authorization_registry=auth,
            orphan_proof_registry=registry,
        )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_B3_AUTHORIZATION_REQUIRED"
    )
    assert registry.calls == []


def test_iam_duplicate_race_requires_whole_transaction_retry() -> None:
    auth = _AuthorizationRegistry(
        error=TenantAuthorizationDecisionEvidenceConflictError(
            "DUPLICATE_RETRY_TRANSACTION"
        )
    )
    registry = _OrphanProofRegistry()

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectOrphanProofOrchestrationRetryRequiredError
    ) as captured:
        _issue(
            authorization_registry=auth,
            orphan_proof_registry=registry,
        )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_B3_WHOLE_TRANSACTION_RETRY_REQUIRED"
    )
    assert registry.calls == []


def test_iam_replay_divergence_fails_closed_without_retry() -> None:
    auth = _AuthorizationRegistry(
        error=TenantAuthorizationDecisionEvidenceConflictError(
            "IAM_REPLAY_DIVERGENCE"
        )
    )
    registry = _OrphanProofRegistry()

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectOrphanProofOrchestrationError
    ) as captured:
        _issue(
            authorization_registry=auth,
            orphan_proof_registry=registry,
        )

    assert not isinstance(
        captured.value,
        issuer.LegalEvidenceProviderObjectOrphanProofOrchestrationRetryRequiredError,
    )
    assert (
        captured.value.code
        == "L10A2R_C4D6D_B3_AUTHORIZATION_REPLAY_CONFLICT"
    )
    assert registry.calls == []


def test_iam_correlation_mismatch_fails_before_b2() -> None:
    auth = _AuthorizationRegistry(
        mutate={
            "principal_id":
                "principal-other",
        }
    )
    registry = _OrphanProofRegistry()

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectOrphanProofOrchestrationError
    ) as captured:
        _issue(
            authorization_registry=auth,
            orphan_proof_registry=registry,
        )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_B3_AUTHORIZATION_CORRELATION_INVALID"
    )
    assert registry.calls == []


def test_b2_duplicate_race_requires_whole_transaction_retry() -> None:
    auth = _AuthorizationRegistry()
    registry = _OrphanProofRegistry(
        error=LegalEvidenceProviderObjectOrphanProofConflictError(
            "L10A2R_C4D6D_B2_WHOLE_TRANSACTION_RETRY_REQUIRED"
        )
    )

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectOrphanProofOrchestrationRetryRequiredError
    ) as captured:
        _issue(
            authorization_registry=auth,
            orphan_proof_registry=registry,
        )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_B3_WHOLE_TRANSACTION_RETRY_REQUIRED"
    )


def test_b2_divergence_fails_closed_without_retry() -> None:
    auth = _AuthorizationRegistry()
    registry = _OrphanProofRegistry(
        error=LegalEvidenceProviderObjectOrphanProofConflictError(
            "B2_REPLAY_DIVERGENCE"
        )
    )

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectOrphanProofOrchestrationError
    ) as captured:
        _issue(
            authorization_registry=auth,
            orphan_proof_registry=registry,
        )

    assert not isinstance(
        captured.value,
        issuer.LegalEvidenceProviderObjectOrphanProofOrchestrationRetryRequiredError,
    )
    assert (
        captured.value.code
        == "L10A2R_C4D6D_B3_ORPHAN_PROOF_REPLAY_CONFLICT"
    )


def test_post_write_correlation_mismatch_fails_closed() -> None:
    auth = _AuthorizationRegistry()
    registry = _OrphanProofRegistry(
        divergent=True,
    )

    with pytest.raises(
        issuer.LegalEvidenceProviderObjectOrphanProofOrchestrationError
    ) as captured:
        _issue(
            authorization_registry=auth,
            orphan_proof_registry=registry,
        )

    assert (
        captured.value.code
        == "L10A2R_C4D6D_B3_POST_WRITE_CORRELATION_INVALID"
    )


def test_subject_identity_stable_but_proof_fingerprint_sensitive() -> None:
    first = _AuthorizationRegistry()
    second = _AuthorizationRegistry()

    _issue(
        authorization_registry=first,
        proved_at=AT + timedelta(minutes=1),
    )

    _issue(
        authorization_registry=second,
        proved_at=AT + timedelta(minutes=2),
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


def test_orchestrator_grants_no_later_or_financial_authority() -> None:
    forbidden = {
        "retention_satisfied",
        "retention_expired",
        "legal_hold_released",
        "hold_released",
        "cleanup_authorized",
        "delete_authorized",
        "deletion_authorized",
        "provider_delete_authorized",
        "delete_object",
        "delete_objects",
        "billing_authorized",
        "payment_authorized",
        "settlement_authorized",
    }

    public_surface = {
        name
        for name in dir(
            issuer
        )
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(
        public_surface
    )

    value = _issue()

    public_value_surface = {
        name
        for name in dir(
            value
        )
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(
        public_value_surface
    )


# ARTIFACT: test_legal_evidence_provider_object_orphan_proof_orchestrator.py
# VERSION: v1.0.0-L10A2R-C4D6D-B3-AUTHORIZED-ORPHAN-PROOF-ISSUANCE-CERT
# AUTHORITY BOUNDARY: direct B3 issuance certification only
# TENANT POSTURE: exact authenticated tenant/principal and B1/B2 scope
# FAIL-CLOSED POSTURE: denial, divergence, invalid evidence and retry races reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
