"""WILSY OS — M11E2D1 authenticated observation ingestion certificate.

TITLE: Authenticated Provider Observation Ingestion Unit Certificate
VERSION: v1.1.0-M11-P5-R2E-R5
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Certify the provider-evidence boundary without manufacturing execution truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_authenticated_provider_observation_ingestion.py
COLLABORATION / OWNERSHIP: Kennel EOS ingestion owner; direct M11-P5-R2E-R5 certificate.
CERTIFICATION / UPDATE DATE: 2026-09-08
CHANGELOG: v1.1.0-M11-P5-R2E-R5 certifies terminal-only runtime composition and explicit collection/session binding; v1.0.0-M11E2D1 certifies typed validation and authority separation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: deterministic opaque references; no provider payloads.
TENANT BOUNDARY: tenant and attempt identity correlation is fail-closed.
AUTHORITY BOUNDARY: test supplies external capability evidence only.
FINANCIAL AUTHORITY BOUNDARY: no execution truth, settlement, or paid state.
TRANSACTION BOUNDARY: production boundary requires caller-owned active session.
FAIL-CLOSED DECLARATION: invalid evidence never reaches the applicator.
"""
from datetime import datetime, timezone
from typing import Any, cast
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from tools.eos.kennel.domain.financial_execution_execution_time_evidence import (
    ExecutionTimeAuthorityKind,
    FinancialExecutionTimeEvidence,
)
from tools.eos.kennel.domain.financial_execution_lifecycle import FinancialExecutionAttemptState
from tools.eos.kennel.domain.financial_execution_provider_observation import (
    EvidenceStrength,
    ObservationStatus,
    TransportDisposition,
)
from tools.eos.kennel.orchestration.authenticated_provider_observation_ingestion import (
    AuthenticatedProviderObservationIngestionError,
    AuthenticatedProviderTransportEvidence,
    ingest_authenticated_provider_observation,
)
from tools.eos.kennel.orchestration.financial_execution_observation_applicator import (
    ObservationApplicationOutcome,
    ObservationApplicationResult,
)


def _evidence(**overrides):
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    values = dict(
        observation_id="obs-1", tenant_id="tenant-1", execution_attempt_id="attempt-1",
        provider_name="provider-1", observation_status=ObservationStatus.EXECUTED,
        observed_at=now, evidence_strength=EvidenceStrength.AUTHENTICATED,
        transport_disposition=TransportDisposition.RESPONSE_RECEIVED,
        provider_execution_reference="exec-1", provider_evidence_reference="evidence-1",
        execution_time_evidence=FinancialExecutionTimeEvidence(
            "tenant-1", "attempt-1", "provider-1", "exec-1", "evidence-1", now,
            ExecutionTimeAuthorityKind.PROVIDER_EXECUTION_CONFIRMATION,
            EvidenceStrength.AUTHENTICATED,
        ),
    )
    values.update(overrides)
    return AuthenticatedProviderTransportEvidence(**cast(Any, values))


def _collections() -> dict[str, Mock]:
    return {
        "observation_collection": Mock(name="observation"),
        "attempt_collection": Mock(name="attempt"),
        "command_collection": Mock(name="command"),
        "fact_collection": Mock(name="fact"),
        "ap_truth_collection": Mock(name="ap_truth"),
        "platform_truth_collection": Mock(name="platform_truth"),
    }


def test_authenticated_evidence_constructs_observation_and_delegates_without_truth():
    session = Mock(spec=[])  # a typed stand-in; property is supplied explicitly
    session.in_transaction = True
    collections = _collections()
    expected = Mock()
    with patch("tools.eos.kennel.orchestration.authenticated_provider_observation_ingestion.ClientSession", object), patch(
        "tools.eos.kennel.orchestration.authenticated_provider_observation_ingestion.FinancialExecutionObservationApplicator.apply",
        return_value=expected,
    ) as apply:
        assert ingest_authenticated_provider_observation("tenant-1", _evidence(), session=session, **collections) is expected
    observation = apply.call_args.args[1]
    assert observation.observation_status is ObservationStatus.EXECUTED
    assert observation.provider_execution_reference == "exec-1"


@pytest.mark.parametrize("bad", [
    {"evidence_strength": EvidenceStrength.UNAUTHENTICATED},
    {"transport_disposition": TransportDisposition.AMBIGUOUS},
    {"tenant_id": "other"},
    {"execution_time_evidence": None},
])
def test_invalid_authority_evidence_fails_closed(bad):
    session = Mock(spec=[]); session.in_transaction = True
    collections = _collections()
    with patch("tools.eos.kennel.orchestration.authenticated_provider_observation_ingestion.ClientSession", object), pytest.raises(AuthenticatedProviderObservationIngestionError):
        ingest_authenticated_provider_observation("tenant-1", _evidence(**bad), session=session, **collections)


def test_terminal_confirming_application_composes_runtime_once_with_all_bindings():
    session = Mock(spec=[])
    session.in_transaction = True
    collections = _collections()
    attempt = SimpleNamespace(
        state=FinancialExecutionAttemptState.CONFIRMED_EXECUTED,
        execution_attempt_id="attempt-1",
    )
    application = ObservationApplicationResult(
        ObservationApplicationOutcome.ATTEMPT_ADVANCED, cast(Any, attempt), Mock()
    )
    runtime_result = Mock(name="runtime_result")
    with (
        patch("tools.eos.kennel.orchestration.authenticated_provider_observation_ingestion.ClientSession", object),
        patch(
            "tools.eos.kennel.orchestration.authenticated_provider_observation_ingestion.FinancialExecutionObservationApplicator.apply",
            return_value=application,
        ) as apply,
        patch(
            "tools.eos.kennel.orchestration.authenticated_provider_observation_ingestion.orchestrate_terminal_execution_fact_and_projection",
            return_value=runtime_result,
        ) as runtime,
    ):
        result = ingest_authenticated_provider_observation(
            "tenant-1", _evidence(), session=session, **collections
        )
    assert result is runtime_result
    apply.assert_called_once()
    runtime.assert_called_once_with(
        "tenant-1",
        "attempt-1",
        command_collection=collections["command_collection"],
        attempt_collection=collections["attempt_collection"],
        observation_collection=collections["observation_collection"],
        fact_collection=collections["fact_collection"],
        ap_truth_collection=collections["ap_truth_collection"],
        platform_truth_collection=collections["platform_truth_collection"],
        execution_time_evidence=_evidence().execution_time_evidence,
        session=session,
    )


def test_nonterminal_application_does_not_compose_runtime():
    session = Mock(spec=[])
    session.in_transaction = True
    collections = _collections()
    application = ObservationApplicationResult(
        ObservationApplicationOutcome.ATTEMPT_ADVANCED,
        cast(
            Any,
            SimpleNamespace(
                state=FinancialExecutionAttemptState.PENDING,
                execution_attempt_id="attempt-1",
            ),
        ),
        Mock(),
    )
    with (
        patch("tools.eos.kennel.orchestration.authenticated_provider_observation_ingestion.ClientSession", object),
        patch(
            "tools.eos.kennel.orchestration.authenticated_provider_observation_ingestion.FinancialExecutionObservationApplicator.apply",
            return_value=application,
        ),
        patch(
            "tools.eos.kennel.orchestration.authenticated_provider_observation_ingestion.orchestrate_terminal_execution_fact_and_projection",
        ) as runtime,
    ):
        assert ingest_authenticated_provider_observation(
            "tenant-1", _evidence(), session=session, **collections
        ) is application
    runtime.assert_not_called()


def test_terminal_runtime_failure_propagates_to_caller_transaction_owner():
    session = Mock(spec=[])
    session.in_transaction = True
    collections = _collections()
    application = ObservationApplicationResult(
        ObservationApplicationOutcome.ATTEMPT_ADVANCED,
        cast(
            Any,
            SimpleNamespace(
                state=FinancialExecutionAttemptState.CONFIRMED_EXECUTED,
                execution_attempt_id="attempt-1",
            ),
        ),
        Mock(),
    )
    with (
        patch("tools.eos.kennel.orchestration.authenticated_provider_observation_ingestion.ClientSession", object),
        patch(
            "tools.eos.kennel.orchestration.authenticated_provider_observation_ingestion.FinancialExecutionObservationApplicator.apply",
            return_value=application,
        ),
        patch(
            "tools.eos.kennel.orchestration.authenticated_provider_observation_ingestion.orchestrate_terminal_execution_fact_and_projection",
            side_effect=RuntimeError("child failure"),
        ),
        pytest.raises(RuntimeError, match="child failure"),
    ):
        ingest_authenticated_provider_observation(
            "tenant-1", _evidence(), session=session, **collections
        )


# ARTIFACT: test_authenticated_provider_observation_ingestion.py
# VERSION: v1.1.0-M11-P5-R2E-R5
# AUTHORITY BOUNDARY: certificate only; no financial authority.
# TENANT POSTURE: synthetic external evidence is passed through production validation.
# FAIL-CLOSED POSTURE: invalid provenance is rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
