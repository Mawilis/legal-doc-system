"""WILSY OS worker-result DTO direct certification.

TITLE: WILSY Runtime Worker Result Certificate
VERSION: v1.0.0-WILSY-WORKER-RESULT-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Direct deterministic certificate for execution-result evidence shape and status semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_worker_result.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-01
CHANGELOG: v1.0.0 certifies canonical statuses, fail-closed defaults, task identity, finite duration, output/error evidence, and shallow frozen posture without authority behavior.
COMPLIANCE: In-memory unit certification; POPIA section 19, GDPR Article 32, SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No external services, persistence, or synthetic authority.
TENANT BOUNDARY: task_id is execution correlation evidence only, never tenant identity or authorization.
AUTHORITY BOUNDARY: WorkerResultDTO evidence shape only; no authentication, tenant authorization, principal, or KEXEC authority.
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS remains exclusive.
"""

from typing import Any

import pytest
from pydantic import ValidationError

from tools.eos.runtime.worker_result import (
    VERSION,
    EngineWorkerResultDTO,
    WorkerExecutionResult,
    WorkerExecutionStatusEnum,
    WorkerResultDTO,
)


def make_result(**overrides: Any) -> WorkerResultDTO:
    values: dict[str, Any] = {"task_id": "task-001", "execution_duration_ms": 1.25}
    values.update(overrides)
    return WorkerResultDTO(**values)


def test_version_enum_and_alias_contract() -> None:
    assert VERSION == "v1.0.0-WILSY-RUNTIME-WORKER-RESULT"
    assert WorkerExecutionStatusEnum.SUCCESS.value == "SUCCESS"
    assert WorkerExecutionStatusEnum.FAILED.value == "FAILED"
    assert WorkerExecutionStatusEnum.CANCELLED.value == "CANCELLED"
    assert WorkerExecutionStatusEnum.FAILURE is WorkerExecutionStatusEnum.FAILED
    assert list(WorkerExecutionStatusEnum) == [WorkerExecutionStatusEnum.SUCCESS, WorkerExecutionStatusEnum.FAILED, WorkerExecutionStatusEnum.CANCELLED]
    assert EngineWorkerResultDTO is WorkerResultDTO
    assert WorkerExecutionResult is WorkerResultDTO


@pytest.mark.parametrize("status", [WorkerExecutionStatusEnum.SUCCESS, WorkerExecutionStatusEnum.FAILED, WorkerExecutionStatusEnum.CANCELLED])
def test_explicit_terminal_statuses_preserve_evidence(status: WorkerExecutionStatusEnum) -> None:
    value = make_result(status=status, output={"nested": {"v": 1}}, error_details="evidence")
    assert isinstance(value, WorkerResultDTO)
    assert value.task_id == "task-001"
    assert value.status is status
    assert value.execution_duration_ms == 1.25
    assert value.output == {"nested": {"v": 1}}
    assert value.error_details == "evidence"


def test_omitted_status_fails_closed_and_defaults_are_fresh() -> None:
    first = make_result()
    second = make_result()
    assert first.status is WorkerExecutionStatusEnum.FAILED
    assert first.output == {}
    assert first.error_details is None
    first.output["x"] = 1
    assert second.output == {}


@pytest.mark.parametrize("task_id", ["", " ", "   "])
def test_blank_task_ids_rejected(task_id: str) -> None:
    with pytest.raises(ValidationError, match="TASK_ID_REQUIRED"):
        make_result(task_id=task_id)


def test_task_id_is_preserved_and_not_tenant_policy() -> None:
    for task_id in (" exact ", "unknown", "none", "null", "tenant-default"):
        assert make_result(task_id=task_id).task_id == task_id
    with pytest.raises(ValidationError):
        make_result(task_id=7)


@pytest.mark.parametrize("duration", [0.0, 2.5])
def test_finite_nonnegative_duration_accepted(duration: float) -> None:
    assert make_result(execution_duration_ms=duration).execution_duration_ms == duration


@pytest.mark.parametrize("duration", [-1.0, float("nan"), float("inf"), float("-inf")])
def test_negative_and_nonfinite_duration_rejected(duration: float) -> None:
    with pytest.raises(ValidationError):
        make_result(execution_duration_ms=duration)


def test_output_and_error_contract() -> None:
    value = make_result(output={"artifact": [1, 2]}, error_details=None)
    assert value.output == {"artifact": [1, 2]}
    with pytest.raises(ValidationError):
        make_result(output=[])
    with pytest.raises(ValidationError):
        make_result(error_details=7)


def test_status_does_not_rewrite_valid_content() -> None:
    success = make_result(status=WorkerExecutionStatusEnum.SUCCESS, error_details="warning")
    failed = make_result(status=WorkerExecutionStatusEnum.FAILED, output={"diagnostic": True})
    cancelled = make_result(status=WorkerExecutionStatusEnum.CANCELLED, output={"checkpoint": 1}, error_details="cancelled")
    assert success.error_details == "warning"
    assert failed.output == {"diagnostic": True}
    assert cancelled.output == {"checkpoint": 1}
    assert cancelled.error_details == "cancelled"


def test_field_reassignment_is_frozen_but_nested_output_is_mutable() -> None:
    value = make_result(output={"nested": {"value": 1}})
    value.output["nested"]["value"] = 2
    assert value.output["nested"]["value"] == 2
    with pytest.raises(ValidationError):
        setattr(value, "task_id", "other")


# ARTIFACT: test_worker_result.py
# VERSION: v1.0.0-WILSY-WORKER-RESULT-CERT
# AUTHORITY BOUNDARY: execution-result evidence shape only.
# TENANT POSTURE: task_id is correlation evidence, never tenant authority.
# FAIL-CLOSED POSTURE: omitted status fails closed; invalid identity/duration rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
