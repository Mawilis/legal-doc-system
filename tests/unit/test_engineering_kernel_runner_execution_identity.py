"""WILSY OS — dedicated certification for runner execution identity.

TITLE: Engineering Kernel Runner Execution Identity Certification
VERSION: v1.0.0-WILSY-KERNEL-RUNNER-EXECUTION-IDENTITY-CERT
PURPOSE: Prove runner-owned execution identities remain distinct from session and caller identities.
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_engineering_kernel_runner_execution_identity.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
UPDATED: 2026-08-29
EXECUTION IDENTITY: Runner-owned lifecycle identity generated once per run.
SESSION DISTINCTION: Bootstrap session identity remains provider-owned and unchanged.
REQUEST / CORRELATION: Caller identities are forwarded but never reused as execution identity.
SECURITY / PRIVACY: Deterministic substitutes retain references only and perform no external work.
DETERMINISM: UUID generation is narrowly patched with fixed literals in test scope.
RUNTIME EXCLUSION: Real bootstrap, filesystem, network, Mongo, and runtime pipelines are excluded.
FAILURE BOUNDARY: Failed sessions are certified only when the current result contract exposes them.
FINANCIAL BOUNDARY: Execution identity carries no financial or idempotency semantics.
CHANGELOG: v1.0.0 certifies distinct runner execution identity semantics.

WILSY OWNS BUSINESS TRUTH. EOS ALL THE WAY.
"""

import re
import uuid

import pytest

import tools.eos.kernel.runner as runner_module
from tools.eos.kernel.domain.kernel_bootstrap_request import KernelBootstrapRequest
from tools.eos.kernel.runner import EngineeringKernelRunner, EngineeringKernelSession


class PipelineSubstitute:
    """Minimal pipeline seam returning deterministic provider session material."""

    def __init__(self, status: str = "SUCCESS") -> None:
        self.status = status
        self.calls: list[tuple[KernelBootstrapRequest, str]] = []

    def execute(self, request: KernelBootstrapRequest, deployment_environment: str) -> EngineeringKernelSession:
        """Record authority and return the provider-owned session identity."""
        self.calls.append((request, deployment_environment))
        return EngineeringKernelSession(
            execution_id="kernel-cert-session-001",
            result={"status": self.status, "session_id": "kernel-cert-session-001"},
        )


def request() -> KernelBootstrapRequest:
    """Build one immutable request with distinct identity dimensions."""
    return KernelBootstrapRequest("tenant-cert-001", "principal-cert-001", "request-cert-001", "correlation-cert-001")


@pytest.fixture
def controlled_runner(monkeypatch: pytest.MonkeyPatch) -> tuple[EngineeringKernelRunner, PipelineSubstitute]:
    """Install a side-effect-free pipeline seam for one deterministic test."""
    pipeline = PipelineSubstitute()
    runner = EngineeringKernelRunner()
    monkeypatch.setattr(runner, "_pipeline", pipeline)
    return runner, pipeline


def test_execution_identity_exists_and_has_canonical_format(
    monkeypatch: pytest.MonkeyPatch, controlled_runner: tuple[EngineeringKernelRunner, PipelineSubstitute]
) -> None:
    runner, _ = controlled_runner
    monkeypatch.setattr(runner_module.uuid, "uuid4", lambda: uuid.UUID("00112233-4455-6677-8899-aabbccddeeff"))
    result = runner.run(request(), "test")
    assert isinstance(result.execution_id, str)
    assert re.fullmatch(r"KEXEC-[0-9A-F]{12}", result.execution_id)
    assert result.execution_id == "KEXEC-001122334455"


def test_execution_identity_is_distinct_from_provider_session_and_callers(
    monkeypatch: pytest.MonkeyPatch, controlled_runner: tuple[EngineeringKernelRunner, PipelineSubstitute]
) -> None:
    runner, _ = controlled_runner
    monkeypatch.setattr(runner_module.uuid, "uuid4", lambda: uuid.UUID("00112233-4455-6677-8899-aabbccddeeff"))
    candidate = request()
    result = runner.run(candidate, "test")
    assert result.execution_id != "kernel-cert-session-001"
    assert result.execution_id not in {candidate.request_id, candidate.correlation_id, candidate.tenant_id, candidate.principal_id}


def test_two_runs_receive_distinct_ids_without_runner_retention(
    monkeypatch: pytest.MonkeyPatch, controlled_runner: tuple[EngineeringKernelRunner, PipelineSubstitute]
) -> None:
    runner, _ = controlled_runner
    values = iter((uuid.UUID("00112233-4455-6677-8899-aabbccddeeff"), uuid.UUID("ffeeddcc-bbaa-9988-7766-554433221100")))
    monkeypatch.setattr(runner_module.uuid, "uuid4", lambda: next(values))
    first = runner.run(request(), "test")
    second = runner.run(request(), "test")
    assert first.execution_id != second.execution_id
    assert "execution_id" not in vars(runner)


def test_same_request_can_produce_distinct_execution_identities(
    monkeypatch: pytest.MonkeyPatch, controlled_runner: tuple[EngineeringKernelRunner, PipelineSubstitute]
) -> None:
    runner, _ = controlled_runner
    values = iter((uuid.UUID("00112233-4455-6677-8899-aabbccddeeff"), uuid.UUID("ffeeddcc-bbaa-9988-7766-554433221100")))
    monkeypatch.setattr(runner_module.uuid, "uuid4", lambda: next(values))
    candidate = request()
    first = runner.run(candidate, "test")
    second = runner.run(candidate, "test")
    assert first.execution_id != second.execution_id
    assert candidate.to_dict() == request().to_dict()


def test_session_material_and_authority_forwarding_remain_unchanged(
    monkeypatch: pytest.MonkeyPatch, controlled_runner: tuple[EngineeringKernelRunner, PipelineSubstitute]
) -> None:
    runner, pipeline = controlled_runner
    monkeypatch.setattr(runner_module.uuid, "uuid4", lambda: uuid.UUID("00112233-4455-6677-8899-aabbccddeeff"))
    candidate = request()
    before = candidate.to_dict()
    result = runner.run(candidate, "staging")
    assert pipeline.calls == [(candidate, "staging")]
    assert result.result["session_id"] == "kernel-cert-session-001"
    assert candidate.to_dict() == before


def test_success_semantics_remain_unchanged(
    monkeypatch: pytest.MonkeyPatch, controlled_runner: tuple[EngineeringKernelRunner, PipelineSubstitute]
) -> None:
    runner, _ = controlled_runner
    monkeypatch.setattr(runner_module.uuid, "uuid4", lambda: uuid.UUID("00112233-4455-6677-8899-aabbccddeeff"))
    assert runner.run(request(), "test").success is True


def test_failed_session_retains_distinct_execution_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = EngineeringKernelRunner()
    pipeline = PipelineSubstitute(status="FAILED")
    monkeypatch.setattr(runner, "_pipeline", pipeline)
    monkeypatch.setattr(runner_module.uuid, "uuid4", lambda: uuid.UUID("00112233-4455-6677-8899-aabbccddeeff"))
    result = runner.run(request(), "test")
    assert result.success is False
    assert result.execution_id == "KEXEC-001122334455"
    assert result.execution_id != result.result["session_id"]


# ARTIFACT: test_engineering_kernel_runner_execution_identity.py
# VERSION: v1.0.0-WILSY-KERNEL-RUNNER-EXECUTION-IDENTITY-CERT
# AUTHORITY BOUNDARY: pure runner execution-identity certification only.
# TENANT POSTURE: caller authority remains explicit and isolated.
# FAIL-CLOSED POSTURE: no synthetic authority or uncontrolled runtime is used.
# FINANCIAL EXECUTION AUTHORITY: none; Kennel financial truth remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
