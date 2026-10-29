"""Direct certificate for S6-A2 noninteractive assurance composition."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from pathlib import Path
import inspect

import pytest

from tools.eos.auth.internal_service_noninteractive_assurance_service import (
    InternalServiceNoninteractiveAssuranceError,
    InternalServiceNoninteractiveAssuranceService,
)
from tools.eos.auth.privileged_channel_currentness import (
    WorkloadTrustFact,
    WorkloadTrustStatus,
)
from tools.eos.auth.privileged_noninteractive_security_proof import (
    PrivilegedNoninteractiveProofStatus,
)
from tools.eos.auth.privileged_security_assurance import (
    PrivilegedAssuranceChannel,
    PrivilegedAssurancePurpose,
)

NOW = datetime(
    2026,
    10,
    14,
    tzinfo=timezone.utc,
)


class Session:
    in_transaction = True


class Source:
    def verify_and_record(
        self,
        **_: object,
    ) -> WorkloadTrustFact:
        return WorkloadTrustFact(
            proof_reference=
                "WILSYWORKLOAD-unit",
            principal_id=
                "principal-service",
            credential_or_attestation_reference=
                "service:key:revision:1",
            observed_at=NOW,
            status=
                WorkloadTrustStatus.CURRENT,
        )


class Workloads:
    def get_by_proof_reference(
        self,
        *,
        proof_reference: str,
        session: object,
    ) -> WorkloadTrustFact:
        assert (
            proof_reference
            == "WILSYWORKLOAD-unit"
        )
        assert session is not None
        return (
            Source()
            .verify_and_record()
        )


class ExactProofRegistry:
    def __init__(self) -> None:
        self.snapshot = None

    def create_or_replay(
        self,
        proof,
        *,
        status_changed_at,
        idempotency_key,
        session,
    ):
        assert (
            proof.proof_status
            is PrivilegedNoninteractiveProofStatus
            .VERIFIED
        )

        self.snapshot = SimpleNamespace(
            proof=proof,
            revision=1,
            status_changed_at=
                status_changed_at,
            idempotency_key=
                idempotency_key,
        )

        return self.snapshot

    def get_current_by_proof_reference(
        self,
        *,
        proof_reference,
        session,
    ):
        assert self.snapshot is not None
        assert (
            self.snapshot
            .proof
            .proof_reference
            == proof_reference
        )
        return self.snapshot


class EvidenceRegistry:
    def create_or_replay(
        self,
        value,
        *,
        session,
    ):
        assert session is not None
        return value


def service() -> (
    InternalServiceNoninteractiveAssuranceService
):
    return (
        InternalServiceNoninteractiveAssuranceService(
            workload_source=
                Source(),  # type: ignore[arg-type]
            workload_registry=
                Workloads(),  # type: ignore[arg-type]
            proof_registry=
                ExactProofRegistry(),  # type: ignore[arg-type]
            evidence_registry=
                EvidenceRegistry(),  # type: ignore[arg-type]
            clock=lambda: NOW,
            proof_id_factory=(
                lambda:
                    "WILSY-NONINTERACTIVE-PROOF-unit"
            ),
            evidence_id_factory=(
                lambda:
                    "WILSY-ASSURANCE-EVIDENCE-unit"
            ),
        )
    )


def test_authoritative_fact_composes_sufficient_noninteractive_assurance():
    result = service().compose(
        request={},
        body=b"{}",
        keys={},
        expected_audience=
            "internal",
        assurance_purpose=(
            PrivilegedAssurancePurpose
            .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
        ),
        idempotency_key=
            "unit",
        session=Session(),
    )

    assert (
        result
        .workload_fact
        .principal_id
        == "principal-service"
    )

    assert (
        result.decision.sufficient
        is True
    )

    assert (
        result
        .decision
        .assurance_channel
        is PrivilegedAssuranceChannel
        .NONINTERACTIVE_WORKLOAD_PROOF
    )

    assert (
        result
        .evidence
        .workload_proof_reference
        == result
        .workload_fact
        .proof_reference
    )

    assert (
        result
        .evidence
        .workload_proof_current
        is True
    )


def test_stable_idempotency_key_replays_identical_p3_assurance_material():
    selected = InternalServiceNoninteractiveAssuranceService(
        workload_source=Source(),  # type: ignore[arg-type]
        workload_registry=Workloads(),  # type: ignore[arg-type]
        proof_registry=ExactProofRegistry(),  # type: ignore[arg-type]
        evidence_registry=EvidenceRegistry(),  # type: ignore[arg-type]
    )
    arguments = {
        "request": {},
        "body": b"{}",
        "keys": {},
        "expected_audience": "internal",
        "assurance_purpose": PrivilegedAssurancePurpose.PRIVILEGED_ELIGIBILITY_TO_ACTIVATION,
        "idempotency_key": "stable-credential-generation-key",
    }
    first = selected.compose(**arguments, session=Session())
    second = selected.compose(**arguments, session=Session())

    assert first.proof_snapshot.proof.proof_id == second.proof_snapshot.proof.proof_id
    assert first.evidence.assurance_evidence_id == second.evidence.assurance_evidence_id
    assert first.evidence.evaluated_at == second.evidence.evaluated_at
    assert first.proof_snapshot.idempotency_key == second.proof_snapshot.idempotency_key


def test_missing_active_transaction_fails_before_source_use():
    with pytest.raises(
        InternalServiceNoninteractiveAssuranceError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        service().compose(
            request={},
            body=b"{}",
            keys={},
            expected_audience=
                "internal",
            assurance_purpose=(
                PrivilegedAssurancePurpose
                .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
            ),
            idempotency_key=
                "unit",
            session=object(),
        )


def test_caller_surface_has_no_principal_or_proof_reference_parameters():
    parameters = set(
        inspect.signature(
            InternalServiceNoninteractiveAssuranceService
            .compose
        ).parameters
    )

    for forbidden in (
        "principal_id",
        "proof_reference",
        "workload_proof_reference",
        "proof_id",
        "assurance_evidence_id",
    ):
        assert forbidden not in parameters


def test_source_contains_no_activation_tenant_or_financial_authority():
    source = Path(
        "tools/eos/auth/"
        "internal_service_noninteractive_assurance_service.py"
    ).read_text(
        encoding="utf-8"
    ).lower()

    for forbidden in (
        "activate_privilege(",
        "role_assignment_repository",
        "tenant_membership_repository",
        "business_role_repository",
        "payment_execution",
        "financial_settlement",
        "break_glass",
    ):
        assert forbidden not in source
