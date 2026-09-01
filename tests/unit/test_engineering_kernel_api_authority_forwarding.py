"""WILSY OS — dedicated certification for API authority forwarding.

TITLE: Engineering Kernel API Authority Forwarding Certification
VERSION: v1.0.0-WILSY-ENGINEERING-KERNEL-API-AUTHORITY-FORWARDING-CERT
PURPOSE: Prove the reusable API façade forwards explicit execution authority unchanged.
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_engineering_kernel_api_authority_forwarding.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
UPDATED: 2026-08-29
REQUEST AUTHORITY: KernelBootstrapRequest remains caller-owned and per execution.
DEPLOYMENT AUTHORITY: Explicit deployment environment remains caller-supplied per execution.
FAÇADE BOUNDARY: Reusable API state retains only the runner dependency.
RUNNER DELEGATION: The runner result object is passed through unchanged.
SECURITY / PRIVACY: The substitute records references only and performs no external work.
DETERMINISM: Literal requests, environments, results, and exceptions are deterministic.
RUNTIME EXCLUSION: Bootstrap, pipeline, filesystem, telemetry, network, and Mongo are excluded.
IDENTITY OWNERSHIP: Execution and session identity generation remain outside this API certification.
CHANGELOG: v1.0.0 certifies pure API-to-runner authority forwarding.

WILSY OWNS BUSINESS TRUTH. EOS ALL THE WAY.
"""

import inspect

import pytest

from tools.eos.kernel.api import EngineeringKernel
from tools.eos.kernel.domain.kernel_bootstrap_request import KernelBootstrapRequest
from tools.eos.kernel.runner import EngineeringKernelSession


class RunnerSubstitute:
    """Minimal typed runner boundary returning a preconstructed session."""

    def __init__(self, result: EngineeringKernelSession | None = None) -> None:
        self.calls: list[tuple[KernelBootstrapRequest, str]] = []
        self.result = result or EngineeringKernelSession(
            execution_id="KEXEC-ABCDEF123456",
            result={"status": "SUCCESS", "session_id": "kernel-api-session"},
        )

    def run(self, request: KernelBootstrapRequest, deployment_environment: str) -> EngineeringKernelSession:
        """Record exact inputs and return the deterministic runner result."""
        self.calls.append((request, deployment_environment))
        return self.result


def make_request(
    tenant_id: str = "tenant-api-alpha",
    principal_id: str = "principal-api-alpha",
    request_id: str = "request-api-alpha",
    correlation_id: str | None = "corr-api-alpha",
) -> KernelBootstrapRequest:
    """Build a literal authority request for API forwarding tests."""
    return KernelBootstrapRequest(tenant_id, principal_id, request_id, correlation_id)


def make_kernel() -> tuple[EngineeringKernel, RunnerSubstitute]:
    """Install a local runner substitute without invoking runtime behavior."""
    kernel = EngineeringKernel()
    runner = RunnerSubstitute()
    object.__setattr__(kernel, "_runner", runner)
    return kernel, runner


def test_constructor_is_authority_neutral() -> None:
    kernel = EngineeringKernel()
    state = vars(kernel)
    assert tuple(state) == ("_runner",)
    assert all(name not in state for name in ("request", "tenant_id", "principal_id", "request_id", "correlation_id", "deployment_environment", "execution_id", "session_id"))


def test_execute_requires_request_and_environment() -> None:
    signature = inspect.signature(EngineeringKernel.execute)
    assert signature.parameters["request"].default is inspect.Parameter.empty
    assert signature.parameters["deployment_environment"].default is inspect.Parameter.empty
    assert signature.return_annotation == "EngineeringKernelSession"


def test_exact_request_and_environment_are_forwarded() -> None:
    kernel, runner = make_kernel()
    candidate = make_request()
    result = kernel.execute(candidate, "test")
    assert runner.calls == [(candidate, "test")]
    assert runner.calls[0][0] is candidate
    assert result is runner.result


def test_correlation_presence_and_absence_are_preserved() -> None:
    kernel, runner = make_kernel()
    present = make_request()
    absent = make_request("tenant-api-beta", "principal-api-beta", "request-api-beta", None)
    kernel.execute(present, "test")
    kernel.execute(absent, "staging")
    assert runner.calls == [(present, "test"), (absent, "staging")]
    assert runner.calls[0][0].correlation_id == "corr-api-alpha"
    assert runner.calls[1][0].correlation_id is None


def test_request_is_immutable_and_not_reconstructed() -> None:
    kernel, runner = make_kernel()
    candidate = make_request()
    before = candidate.to_dict()
    kernel.execute(candidate, "test")
    assert candidate.to_dict() == before
    assert runner.calls[0][0] is candidate


def test_reusable_facade_isolates_tenant_principal_request_and_environment() -> None:
    kernel, runner = make_kernel()
    first = make_request()
    second = make_request("tenant-api-beta", "principal-api-beta", "request-api-beta", "corr-api-beta")
    kernel.execute(first, "test")
    kernel.execute(second, "staging")
    assert runner.calls == [(first, "test"), (second, "staging")]
    assert runner.calls[0][0] is not runner.calls[1][0]


def test_facade_retains_no_per_execution_authority() -> None:
    kernel, _ = make_kernel()
    kernel.execute(make_request(), "test")
    kernel.execute(make_request("tenant-api-beta", "principal-api-beta", "request-api-beta", None), "staging")
    state = vars(kernel)
    assert tuple(state) == ("_runner",)
    assert all(name not in state for name in ("request", "tenant_id", "principal_id", "request_id", "correlation_id", "deployment_environment", "execution_id", "session_id"))


def test_runner_error_propagates_unchanged() -> None:
    class FailingRunner:
        """Minimal runner that exposes one deterministic authority error."""

        def run(self, request: KernelBootstrapRequest, deployment_environment: str) -> EngineeringKernelSession:
            """Raise the canonical substitute error without rewriting it."""
            raise ValueError("runner authority rejected")

    kernel = EngineeringKernel()
    object.__setattr__(kernel, "_runner", FailingRunner())
    with pytest.raises(ValueError, match="^runner authority rejected$"):
        kernel.execute(make_request(), "test")


def test_api_does_not_generate_or_own_execution_identity() -> None:
    kernel, runner = make_kernel()
    result = kernel.execute(make_request(), "test")
    assert result.execution_id == "KEXEC-ABCDEF123456"
    assert vars(kernel) == {"_runner": runner}


def test_same_request_is_forwarded_again_without_api_identity_semantics() -> None:
    kernel, runner = make_kernel()
    candidate = make_request()
    kernel.execute(candidate, "test")
    kernel.execute(candidate, "staging")
    assert runner.calls == [(candidate, "test"), (candidate, "staging")]
    assert all(call[0] is candidate for call in runner.calls)


# ARTIFACT: test_engineering_kernel_api_authority_forwarding.py
# VERSION: v1.0.0-WILSY-ENGINEERING-KERNEL-API-AUTHORITY-FORWARDING-CERT
# AUTHORITY BOUNDARY: pure API-to-runner authority forwarding certification only.
# TENANT POSTURE: explicit caller tenant remains isolated across façade reuse.
# FAIL-CLOSED POSTURE: authority errors propagate without compatibility defaults.
# FINANCIAL EXECUTION AUTHORITY: none; Kennel financial truth remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
