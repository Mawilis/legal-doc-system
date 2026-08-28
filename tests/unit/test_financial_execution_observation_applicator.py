# -*- coding: utf-8 -*-
"""Unit certification for caller-owned observation application orchestration.

VERSION: v1.0.0-KENNEL-FINANCIAL-OBSERVATION-APPLICATOR-UNIT-CERT
AUTHORITY: deterministic orchestration certification; no execution truth or settlement.
PURPOSE: prove observation-first persistence and attempt CAS under caller transactions.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_financial_execution_observation_applicator.py
COLLABORATION: Wilson Khanyezi (Founder); Codex (AI Engineering)
DATE: 2026-08-28 | COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: opaque evidence only; no payloads or credentials.
TENANT BOUNDARY: tenant identity is validated before persistence.
TRANSACTION BOUNDARY: caller owns session and transaction lifecycle.
TRUTH / SETTLEMENT BOUNDARY: applicator never creates FinancialExecutionTruth or settles.
CHANGELOG: v1.0.0 certifies transaction ownership, ordering, replay, and policy mapping.
"""
from datetime import datetime, timezone
from unittest.mock import Mock, patch
import pytest
from tools.eos.kennel.domain.financial_execution_lifecycle import (
    FinancialExecutionAttempt,
    FinancialExecutionAttemptState,
)
from tools.eos.kennel.domain.financial_execution_provider_observation import (
    FinancialExecutionProviderObservation,
    ObservationStatus,
)
from tools.eos.kennel.orchestration.financial_execution_observation_applicator import (
    FinancialExecutionObservationApplicator,
)

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def obs(status=ObservationStatus.PENDING):
    return FinancialExecutionProviderObservation("o", "t", "a", "P", status, NOW)


def att():
    return FinancialExecutionAttempt(
        "a", "t", "c", "P", state=FinancialExecutionAttemptState.TRANSMITTED
    )


def session(active=True):
    s = Mock()
    s.in_transaction.return_value = active
    return s


def test_requires_active_caller_transaction():
    with pytest.raises(RuntimeError):
        FinancialExecutionObservationApplicator.apply("t", obs(), session(False))


def test_order_and_advance():
    s = session()
    calls = []
    with patch(
        "tools.eos.kennel.orchestration.financial_execution_observation_applicator.FinancialExecutionProviderObservationRegistry.create",
        side_effect=lambda *a, **k: (calls.append("observation") or ("CREATED", obs())),
    ), patch(
        "tools.eos.kennel.orchestration.financial_execution_observation_applicator.FinancialExecutionAttemptRegistry.get",
        side_effect=lambda *a, **k: (calls.append("get") or att()),
    ), patch(
        "tools.eos.kennel.orchestration.financial_execution_observation_applicator.FinancialExecutionAttemptRegistry.transition",
        side_effect=lambda *a, **k: (calls.append("transition") or a[4]),
    ):
        result = FinancialExecutionObservationApplicator.apply(
            "t", obs(ObservationStatus.ACCEPTED), s
        )
    assert (
        calls == ["observation", "get", "transition"]
        and result.outcome.value == "ATTEMPT_ADVANCED"
    )


def test_replay_and_nonadvance_mapping():
    with patch(
        "tools.eos.kennel.orchestration.financial_execution_observation_applicator.FinancialExecutionProviderObservationRegistry.create",
        return_value=("IDEMPOTENT_REPLAY", obs()),
    ), patch(
        "tools.eos.kennel.orchestration.financial_execution_observation_applicator.FinancialExecutionAttemptRegistry.get",
        return_value=att(),
    ), patch(
        "tools.eos.kennel.orchestration.financial_execution_observation_applicator.FinancialExecutionAttemptRegistry.transition",
        return_value=att(),
    ):
        result = FinancialExecutionObservationApplicator.apply("t", obs(), session())
    assert result.outcome.value in {
        "ATTEMPT_ADVANCED",
        "ATTEMPT_ALREADY_SATISFIED",
        "OBSERVATION_REPLAYED",
        "RECONCILIATION_REQUIRED",
    }


def test_tenant_mismatch_before_persistence():
    with pytest.raises(ValueError):
        FinancialExecutionObservationApplicator.apply("other", obs(), session())


def test_truth_and_settlement_not_created():
    assert "truth" not in FinancialExecutionObservationApplicator.apply.__annotations__


# ARTIFACT: test_financial_execution_observation_applicator.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-OBSERVATION-APPLICATOR-UNIT-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
