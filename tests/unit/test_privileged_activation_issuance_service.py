"""P4 privileged-activation issuance orchestration certificate.

The service under test is deliberately a narrow authority composer:

    fresh P3
      AND current P2
      AND current D12 ``privileged_activation:issue``
      AND exact self-activation binding
      -> PrivilegedActivation.issue(...)
      -> PrivilegedActivationRegistry.create_or_replay(...)

It owns no transaction lifecycle, HTTP authority, P5-use authority,
break-glass authority, role-creation authority, or financial authority.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from tools.eos.auth.privileged_activation import (
    ISSUANCE_PERMISSION,
    MAXIMUM_ACTIVATION_LIFETIME,
    PrivilegedActivation,
)
from tools.eos.auth.privileged_eligibility import (
    PrivilegedTargetClass,
)
from tools.eos.auth.privileged_security_assurance import (
    PrivilegedAssuranceChannel,
    PrivilegedAssurancePurpose,
)
from tools.eos.auth.privileged_activation_issuance_service import (
    PrivilegedActivationIssuanceError,
    PrivilegedActivationIssuanceService,
)


SOURCE_TARGET = Path(
    "tools/eos/auth/"
    "privileged_activation_issuance_service.py"
)

NOW = datetime(2026, 10, 15, 1, 30, tzinfo=timezone.utc)

ELIGIBILITY_FINGERPRINT = "a" * 128
ASSURANCE_FINGERPRINT = "b" * 128


class Session:
    in_transaction = True


@dataclass(frozen=True)
class Eligibility:
    eligibility_evidence_id: str = "eligibility-1"
    principal_id: str = "principal-1"
    privileged_role_id: str = "role-1"
    target_class: PrivilegedTargetClass = (
        PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT
    )
    tenant_id: str | None = None
    eligibility_evidence_fingerprint: str = ELIGIBILITY_FINGERPRINT


@dataclass(frozen=True)
class AssuranceEvidence:
    assurance_evidence_id: str = "assurance-1"
    principal_id: str = "principal-1"
    assurance_channel: PrivilegedAssuranceChannel = (
        PrivilegedAssuranceChannel.INTERACTIVE_STRONG_AUTH
    )
    assurance_purpose: PrivilegedAssurancePurpose = (
        PrivilegedAssurancePurpose.PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
    )
    sufficient: bool = True

    @property
    def assurance_evidence_fingerprint(self) -> str:
        return ASSURANCE_FINGERPRINT


@dataclass(frozen=True)
class Decision:
    principal_id: str = "principal-1"
    assurance_channel: PrivilegedAssuranceChannel = (
        PrivilegedAssuranceChannel.INTERACTIVE_STRONG_AUTH
    )
    assurance_purpose: PrivilegedAssurancePurpose = (
        PrivilegedAssurancePurpose.PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
    )
    sufficient: bool = True


@dataclass(frozen=True)
class InteractiveResult:
    decision: Decision
    evidence: AssuranceEvidence


@dataclass(frozen=True)
class WorkloadFact:
    principal_id: str = "principal-1"


@dataclass(frozen=True)
class NoninteractiveResult:
    workload_fact: WorkloadFact
    proof_snapshot: object
    decision: Decision
    evidence: AssuranceEvidence


class D12:
    def __init__(self, allowed: bool = True) -> None:
        self.allowed = allowed
        self.calls: list[dict[str, Any]] = []

    def possesses(
        self,
        *,
        principal_id: str,
        permission_id: str,
        session: object,
    ) -> bool:
        self.calls.append(
            {
                "principal_id": principal_id,
                "permission_id": permission_id,
                "session": session,
            }
        )
        return self.allowed


class P2:
    def __init__(self, value: Eligibility | None = None) -> None:
        self.value: Eligibility | None = (
            value if value is not None else Eligibility()
        )
        self.calls: list[dict[str, Any]] = []

    def resolve(
        self,
        *,
        eligibility_evidence_id: str,
        at: datetime,
        session: object,
    ) -> Eligibility | None:
        self.calls.append(
            {
                "eligibility_evidence_id": eligibility_evidence_id,
                "at": at,
                "session": session,
            }
        )
        return self.value


class InteractiveP3:
    def __init__(
        self,
        result: InteractiveResult | None = None,
    ) -> None:
        self.result = result or InteractiveResult(
            decision=Decision(),
            evidence=AssuranceEvidence(),
        )
        self.calls: list[dict[str, Any]] = []

    def compose(
        self,
        *,
        tenant_id: str,
        proof_reference: str,
        assurance_purpose: PrivilegedAssurancePurpose,
        idempotency_key: str,
        session: object,
    ) -> InteractiveResult:
        self.calls.append(
            {
                "tenant_id": tenant_id,
                "proof_reference": proof_reference,
                "assurance_purpose": assurance_purpose,
                "idempotency_key": idempotency_key,
                "session": session,
            }
        )
        return self.result


class NoninteractiveP3:
    def __init__(
        self,
        result: NoninteractiveResult | None = None,
    ) -> None:
        self.result = result or NoninteractiveResult(
            workload_fact=WorkloadFact(),
            proof_snapshot=object(),
            decision=Decision(
                assurance_channel=(
                    PrivilegedAssuranceChannel
                    .NONINTERACTIVE_WORKLOAD_PROOF
                )
            ),
            evidence=AssuranceEvidence(
                assurance_channel=(
                    PrivilegedAssuranceChannel
                    .NONINTERACTIVE_WORKLOAD_PROOF
                )
            ),
        )
        self.calls: list[dict[str, Any]] = []

    def compose(
        self,
        *,
        request: dict[str, str],
        body: bytes,
        keys: dict[str, tuple[str, str]],
        expected_audience: str,
        assurance_purpose: PrivilegedAssurancePurpose,
        idempotency_key: str,
        session: object,
    ) -> NoninteractiveResult:
        self.calls.append(
            {
                "request": request,
                "body": body,
                "keys": keys,
                "expected_audience": expected_audience,
                "assurance_purpose": assurance_purpose,
                "idempotency_key": idempotency_key,
                "session": session,
            }
        )
        return self.result


class ActivationRegistry:
    def __init__(self) -> None:
        self.persisted: list[PrivilegedActivation] = []
        self.session: object | None = None

    def get_history(
        self,
        activation_id: str,
        *,
        session: object,
    ) -> tuple[PrivilegedActivation, ...]:
        return tuple(
            value
            for value in self.persisted
            if value.activation_id == activation_id
        )

    def create_or_replay(
        self,
        activation: PrivilegedActivation,
        *,
        session: object,
    ) -> PrivilegedActivation:
        self.persisted.append(activation)
        self.session = session
        return activation


def service(
    *,
    d12: D12 | None = None,
    p2: P2 | None = None,
    interactive: InteractiveP3 | None = None,
    noninteractive: NoninteractiveP3 | None = None,
    registry: ActivationRegistry | None = None,
) -> tuple[
    PrivilegedActivationIssuanceService,
    D12,
    P2,
    InteractiveP3,
    NoninteractiveP3,
    ActivationRegistry,
]:
    d12_value = d12 or D12()
    p2_value = p2 or P2()
    interactive_value = interactive or InteractiveP3()
    noninteractive_value = noninteractive or NoninteractiveP3()
    registry_value = registry or ActivationRegistry()

    value = PrivilegedActivationIssuanceService(
        permission_resolver=d12_value,
        eligibility_resolver=p2_value,
        interactive_assurance_service=interactive_value,
        noninteractive_assurance_service=noninteractive_value,
        activation_registry=registry_value,
        activation_id_factory=lambda: "activation-1",
        clock=lambda: NOW,
    )

    return (
        value,
        d12_value,
        p2_value,
        interactive_value,
        noninteractive_value,
        registry_value,
    )


def test_interactive_issuance_composes_exact_four_authorities() -> None:
    value, d12, p2, p3, _, registry = service()
    session = Session()

    activation = value.issue_interactive(
        tenant_id=None,
        eligibility_evidence_id="eligibility-1",
        proof_tenant_id="platform-system",
        proof_reference="proof-1",
        issuance_idempotency_key="issue-1",
        session=session,
    )

    assert activation.activation_id == (
        "WILSYACTIVATION-"
        + hashlib.sha3_512(
            b"WILSY:P4:PRIVILEGED_ACTIVATION:issue-1"
        ).hexdigest()
    )
    assert activation.principal_id == "principal-1"
    assert activation.actor_principal_id == "principal-1"
    assert activation.privileged_role_id == "role-1"
    assert (
        activation.target_class
        is PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT
    )
    assert activation.tenant_id is None
    assert (
        activation.creation_assurance_purpose
        is PrivilegedAssurancePurpose
        .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
    )
    assert activation.activated_at == NOW
    assert (
        activation.effective_until
        == NOW + MAXIMUM_ACTIVATION_LIFETIME
    )
    assert (
        activation.eligibility_evidence_fingerprint
        == ELIGIBILITY_FINGERPRINT
    )
    assert (
        activation.assurance_evidence_fingerprint
        == ASSURANCE_FINGERPRINT
    )
    assert activation.issuance_idempotency_key == "issue-1"

    assert p3.calls[0]["assurance_purpose"] is (
        PrivilegedAssurancePurpose
        .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
    )
    assert p2.calls == [
        {
            "eligibility_evidence_id": "eligibility-1",
            "at": NOW,
            "session": session,
        }
    ]
    assert d12.calls == [
        {
            "principal_id": "principal-1",
            "permission_id": ISSUANCE_PERMISSION,
            "session": session,
        }
    ]
    assert registry.persisted == [activation]
    assert registry.session is session


def test_noninteractive_identity_is_derived_from_fresh_p3() -> None:
    value, d12, _, _, p3, registry = service()
    session = Session()

    activation = value.issue_noninteractive(
        tenant_id=None,
        eligibility_evidence_id="eligibility-1",
        request={"x-wilsy-key": "value"},
        body=b"payload",
        keys={"key-1": ("public", "CURRENT")},
        expected_audience="wilsy-eos",
        issuance_idempotency_key="issue-2",
        session=session,
    )

    assert activation.principal_id == "principal-1"
    assert activation.actor_principal_id == "principal-1"
    assert p3.calls[0]["assurance_purpose"] is (
        PrivilegedAssurancePurpose
        .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
    )
    assert d12.calls[0]["principal_id"] == "principal-1"
    assert registry.persisted == [activation]


@pytest.mark.parametrize(
    ("p2_value", "code"),
    (
        (None, "ELIGIBILITY_NOT_CURRENT"),
    ),
)
def test_current_p2_is_required(
    p2_value: Eligibility | None,
    code: str,
) -> None:
    p2 = P2()
    p2.value = p2_value

    value, _, _, _, _, registry = service(p2=p2)

    with pytest.raises(
        PrivilegedActivationIssuanceError,
        match=code,
    ):
        value.issue_interactive(
            tenant_id=None,
            eligibility_evidence_id="eligibility-1",
            proof_tenant_id="platform-system",
            proof_reference="proof-1",
            issuance_idempotency_key="issue-1",
            session=Session(),
        )

    assert registry.persisted == []


def test_d12_exact_issuance_permission_is_required() -> None:
    value, d12, _, _, _, registry = service(
        d12=D12(False),
    )

    with pytest.raises(
        PrivilegedActivationIssuanceError,
        match="ISSUANCE_PERMISSION_NOT_CURRENT",
    ):
        value.issue_interactive(
            tenant_id=None,
            eligibility_evidence_id="eligibility-1",
            proof_tenant_id="platform-system",
            proof_reference="proof-1",
            issuance_idempotency_key="issue-1",
            session=Session(),
        )

    assert d12.calls[0]["permission_id"] == ISSUANCE_PERMISSION
    assert registry.persisted == []


def test_crossed_p2_principal_is_rejected() -> None:
    crossed = Eligibility(principal_id="other-principal")

    value, _, _, _, _, registry = service(
        p2=P2(crossed),
    )

    with pytest.raises(
        PrivilegedActivationIssuanceError,
        match="ELIGIBILITY_PRINCIPAL_MISMATCH",
    ):
        value.issue_interactive(
            tenant_id=None,
            eligibility_evidence_id="eligibility-1",
            proof_tenant_id="platform-system",
            proof_reference="proof-1",
            issuance_idempotency_key="issue-1",
            session=Session(),
        )

    assert registry.persisted == []


def test_crossed_p3_principal_is_rejected_against_p2() -> None:
    crossed = InteractiveResult(
        decision=Decision(principal_id="other-principal"),
        evidence=AssuranceEvidence(
            principal_id="other-principal",
        ),
    )

    value, _, _, _, _, registry = service(
        interactive=InteractiveP3(crossed),
    )

    with pytest.raises(
        PrivilegedActivationIssuanceError,
        match="ELIGIBILITY_PRINCIPAL_MISMATCH",
    ):
        value.issue_interactive(
            tenant_id=None,
            eligibility_evidence_id="eligibility-1",
            proof_tenant_id="platform-system",
            proof_reference="proof-1",
            issuance_idempotency_key="issue-1",
            session=Session(),
        )

    assert registry.persisted == []


def test_insufficient_p3_is_rejected() -> None:
    insufficient = InteractiveResult(
        decision=Decision(sufficient=False),
        evidence=AssuranceEvidence(sufficient=False),
    )

    value, _, _, _, _, registry = service(
        interactive=InteractiveP3(insufficient),
    )

    with pytest.raises(
        PrivilegedActivationIssuanceError,
        match="ASSURANCE_INSUFFICIENT",
    ):
        value.issue_interactive(
            tenant_id=None,
            eligibility_evidence_id="eligibility-1",
            proof_tenant_id="platform-system",
            proof_reference="proof-1",
            issuance_idempotency_key="issue-1",
            session=Session(),
        )

    assert registry.persisted == []


def test_wrong_creation_purpose_is_rejected() -> None:
    wrong = InteractiveResult(
        decision=Decision(
            assurance_purpose=(
                PrivilegedAssurancePurpose.PRIVILEGED_ACTIVATION_USE
            )
        ),
        evidence=AssuranceEvidence(
            assurance_purpose=(
                PrivilegedAssurancePurpose.PRIVILEGED_ACTIVATION_USE
            )
        ),
    )

    value, _, _, _, _, registry = service(
        interactive=InteractiveP3(wrong),
    )

    with pytest.raises(
        PrivilegedActivationIssuanceError,
        match="ASSURANCE_PURPOSE_INVALID",
    ):
        value.issue_interactive(
            tenant_id=None,
            eligibility_evidence_id="eligibility-1",
            proof_tenant_id="platform-system",
            proof_reference="proof-1",
            issuance_idempotency_key="issue-1",
            session=Session(),
        )

    assert registry.persisted == []


def test_scope_and_role_are_taken_only_from_current_p2() -> None:
    tenant = Eligibility(
        privileged_role_id="tenant-admin-role",
        target_class=PrivilegedTargetClass.TENANT_PRIVILEGED,
        tenant_id="tenant-1",
    )

    value, _, _, _, _, _ = service(
        p2=P2(tenant),
    )

    activation = value.issue_interactive(
        tenant_id="tenant-1",
        eligibility_evidence_id="eligibility-1",
        proof_tenant_id="tenant-1",
        proof_reference="proof-1",
        issuance_idempotency_key="issue-1",
        session=Session(),
    )

    assert activation.tenant_id == "tenant-1"
    assert activation.privileged_role_id == "tenant-admin-role"
    assert (
        activation.target_class
        is PrivilegedTargetClass.TENANT_PRIVILEGED
    )


def test_crossed_requested_tenant_is_rejected() -> None:
    tenant = Eligibility(
        target_class=PrivilegedTargetClass.TENANT_PRIVILEGED,
        tenant_id="tenant-1",
    )

    value, _, _, _, _, registry = service(
        p2=P2(tenant),
    )

    with pytest.raises(
        PrivilegedActivationIssuanceError,
        match="ELIGIBILITY_SCOPE_MISMATCH",
    ):
        value.issue_interactive(
            tenant_id="tenant-2",
            eligibility_evidence_id="eligibility-1",
            proof_tenant_id="tenant-2",
            proof_reference="proof-1",
            issuance_idempotency_key="issue-1",
            session=Session(),
        )

    assert registry.persisted == []


def test_service_owns_no_transaction_lifecycle() -> None:
    text = SOURCE_TARGET.read_text(
        encoding="utf-8",
    )

    for forbidden in (
        "start_transaction(",
        ".commit_transaction(",
        ".abort_transaction(",
        "with_transaction(",
    ):
        assert forbidden not in text


def test_service_contains_no_forbidden_authority() -> None:
    text = SOURCE_TARGET.read_text(
        encoding="utf-8",
    ).lower()

    for forbidden in (
        "payment",
        "settlement",
        "subscription",
        "tenant_plan",
        "break_glass",
        "privileged_activation_use",
        "create_role",
        "delete_role",
    ):
        assert forbidden not in text

# P4-C4-R6 EXACT REPLAY + FRESH AUTHORITY RED CONTRACT


class _ReplayIds:
    def __init__(self) -> None:
        self.values = (
            "activation-replay-first",
            "activation-replay-second",
        )
        self.index = 0

    def __call__(self) -> str:
        value = self.values[self.index]
        self.index += 1
        return value


class _ReplayClock:
    def __init__(self) -> None:
        self.values = (
            NOW,
            NOW + timedelta(seconds=1),
        )
        self.index = 0

    def __call__(self) -> datetime:
        value = self.values[self.index]
        self.index += 1
        return value


class _ExactReplayRegistry:
    """Test double matching sealed exact-replay semantics."""

    def __init__(self) -> None:
        self.original: PrivilegedActivation | None = None
        self.create_calls = 0
        self.history_calls = 0

    def get_history(
        self,
        activation_id: str,
        *,
        session: object,
    ) -> tuple[PrivilegedActivation, ...]:
        self.history_calls += 1

        if (
            self.original is not None
            and self.original.activation_id
            == activation_id
        ):
            return (self.original,)

        return ()

    def create_or_replay(
        self,
        activation: PrivilegedActivation,
        *,
        session: object,
    ) -> PrivilegedActivation:
        self.create_calls += 1

        if self.original is None:
            self.original = activation
            return activation

        if (
            activation.issuance_idempotency_key
            == self.original.issuance_idempotency_key
        ):
            if activation == self.original:
                return self.original

            raise RuntimeError(
                "IDEMPOTENCY_KEY_DIVERGENT_REPLAY"
            )

        raise RuntimeError(
            "UNEXPECTED_SECOND_ACTIVATION"
        )


class _TrackingInteractiveP3(InteractiveP3):
    pass


def _replay_service(
    *,
    p2: P2 | None = None,
    d12: D12 | None = None,
    p3: InteractiveP3 | None = None,
    registry: Any | None = None,
    ids: Any | None = None,
    clock: Any | None = None,
) -> tuple[
    PrivilegedActivationIssuanceService,
    D12,
    P2,
    InteractiveP3,
    Any,
]:
    d12_value = d12 or D12()
    p2_value = p2 or P2()
    p3_value = p3 or _TrackingInteractiveP3()
    registry_value = (
        registry
        if registry is not None
        else _ExactReplayRegistry()
    )

    value = PrivilegedActivationIssuanceService(
        permission_resolver=d12_value,
        eligibility_resolver=p2_value,
        interactive_assurance_service=p3_value,
        noninteractive_assurance_service=NoninteractiveP3(),
        activation_registry=registry_value,
        activation_id_factory=ids or _ReplayIds(),
        clock=clock or _ReplayClock(),
    )

    return (
        value,
        d12_value,
        p2_value,
        p3_value,
        registry_value,
    )


def _issue_replay(
    value: PrivilegedActivationIssuanceService,
    *,
    session: object,
) -> PrivilegedActivation:
    return value.issue_interactive(
        tenant_id=None,
        eligibility_evidence_id="eligibility-1",
        proof_tenant_id="platform-system",
        proof_reference="proof-replay",
        issuance_idempotency_key="issue-replay",
        session=session,
    )


def test_exact_replay_returns_original_without_lifetime_refresh() -> None:
    session = Session()

    value, d12, p2, p3, registry = _replay_service()

    first = _issue_replay(
        value,
        session=session,
    )

    second = _issue_replay(
        value,
        session=session,
    )

    assert second == first
    assert second.activation_id == first.activation_id
    assert second.activated_at == first.activated_at
    assert second.effective_until == first.effective_until

    # Every attempt must still re-establish authority.
    assert len(p3.calls) == 2
    assert len(p2.calls) == 2
    assert len(d12.calls) == 2

    # Replay must be satisfied from the original history rather than
    # constructing and attempting to persist a second activation.
    assert registry.create_calls == 1
    assert registry.history_calls >= 1


def test_interactive_replay_uses_fresh_p3_scope_each_attempt() -> None:
    session = Session()

    registry = ActivationRegistry()

    value, _, _, p3, _ = _replay_service(
        registry=registry,
        ids=lambda: "activation-stable",
        clock=lambda: NOW,
    )

    first = _issue_replay(
        value,
        session=session,
    )

    second = _issue_replay(
        value,
        session=session,
    )

    assert second == first
    assert len(p3.calls) == 2

    first_key = p3.calls[0]["idempotency_key"]
    second_key = p3.calls[1]["idempotency_key"]

    assert first_key != second_key
    assert first_key.startswith(
        "issue-replay:assurance:"
    )
    assert second_key.startswith(
        "issue-replay:assurance:"
    )


class _HistoricRegistry:
    def __init__(
        self,
        history: tuple[PrivilegedActivation, ...],
    ) -> None:
        self.history = history
        self.create_calls = 0
        self.history_calls = 0

    def get_history(
        self,
        activation_id: str,
        *,
        session: object,
    ) -> tuple[PrivilegedActivation, ...]:
        self.history_calls += 1
        return self.history

    def create_or_replay(
        self,
        activation: PrivilegedActivation,
        *,
        session: object,
    ) -> PrivilegedActivation:
        self.create_calls += 1
        return activation


def _historic_activation(
    *,
    effective_until: datetime | None = None,
    eligibility_evidence_id: str = "eligibility-1",
    eligibility_evidence_fingerprint: str = ELIGIBILITY_FINGERPRINT,
) -> PrivilegedActivation:
    digest = hashlib.sha3_512(
        (
            "WILSY:P4:PRIVILEGED_ACTIVATION:"
            "issue-replay"
        ).encode("utf-8")
    ).hexdigest()

    return PrivilegedActivation.issue(
        activation_id=(
            "WILSYACTIVATION-"
            + digest
        ),
        tenant_id=None,
        principal_id="principal-1",
        actor_principal_id="principal-1",
        privileged_role_id="role-1",
        target_class=(
            PrivilegedTargetClass
            .PLATFORM_SYSTEM_ROOT
        ),
        eligibility_evidence_id=
            eligibility_evidence_id,
        eligibility_evidence_fingerprint=
            eligibility_evidence_fingerprint,
        assurance_evidence_id="assurance-original",
        assurance_evidence_fingerprint="c" * 128,
        creation_assurance_purpose=(
            PrivilegedAssurancePurpose
            .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
        ),
        activated_at=NOW - timedelta(minutes=1),
        effective_until=(
            effective_until
            if effective_until is not None
            else NOW + timedelta(minutes=14)
        ),
        issuance_idempotency_key="issue-replay",
    )


def test_expired_original_is_not_resurrected_by_replay() -> None:
    original = _historic_activation(
        effective_until=NOW,
    )

    registry = _HistoricRegistry(
        (original,),
    )

    value, d12, p2, p3, _ = _replay_service(
        registry=registry,
        ids=lambda: original.activation_id,
        clock=lambda: NOW,
    )

    with pytest.raises(
        PrivilegedActivationIssuanceError,
        match="ACTIVATION_REPLAY_NOT_CURRENT",
    ):
        _issue_replay(
            value,
            session=Session(),
        )

    # Authority must still be freshly checked before replay is rejected.
    assert len(p3.calls) == 1
    assert len(p2.calls) == 1
    assert len(d12.calls) == 1

    assert registry.history_calls == 1
    assert registry.create_calls == 0


def test_revoked_original_is_not_resurrected_by_replay() -> None:
    active = _historic_activation()

    revoked = active.revoke(
        revoked_at=NOW,
    )

    registry = _HistoricRegistry(
        (
            active,
            revoked,
        ),
    )

    value, d12, p2, p3, _ = _replay_service(
        registry=registry,
        ids=lambda: active.activation_id,
        clock=lambda: NOW,
    )

    with pytest.raises(
        PrivilegedActivationIssuanceError,
        match="ACTIVATION_REPLAY_NOT_CURRENT",
    ):
        _issue_replay(
            value,
            session=Session(),
        )

    assert len(p3.calls) == 1
    assert len(p2.calls) == 1
    assert len(d12.calls) == 1

    assert registry.history_calls == 1
    assert registry.create_calls == 0


def test_replay_requires_current_p2_lineage_to_match_original() -> None:
    original = _historic_activation()

    crossed = Eligibility(
        eligibility_evidence_id="eligibility-1",
        eligibility_evidence_fingerprint="d" * 128,
    )

    registry = _HistoricRegistry(
        (original,),
    )

    value, d12, p2, p3, _ = _replay_service(
        p2=P2(crossed),
        registry=registry,
        ids=lambda: original.activation_id,
        clock=lambda: NOW,
    )

    with pytest.raises(
        PrivilegedActivationIssuanceError,
        match="ACTIVATION_REPLAY_LINEAGE_MISMATCH",
    ):
        _issue_replay(
            value,
            session=Session(),
        )

    assert len(p3.calls) == 1
    assert len(p2.calls) == 1
    assert len(d12.calls) == 1

    assert registry.history_calls == 1
    assert registry.create_calls == 0
