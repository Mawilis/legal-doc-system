"""WILSY OS — dedicated certification for runner authority forwarding.

TITLE: Engineering Kernel Runner Authority Forwarding Certification
VERSION: v1.0.1-WILSY-KERNEL-RUNNER-AUTHORITY-FORWARDING-CERT
PURPOSE: Prove per-execution request and deployment authority reaches bootstrap unchanged.
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_engineering_kernel_runner_authority_forwarding.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
UPDATED: 2026-08-29
TENANT / REQUEST BOUNDARY: Certified KernelBootstrapRequest remains the exact forwarded object.
DEPLOYMENT BOUNDARY: Explicit deployment environment is forwarded without fallback.
RUNNER / PIPELINE BOUNDARY: Reusable orchestration retains no per-execution authority.
SECURITY / PRIVACY: The substitute records references only and performs no external work.
DETERMINISM: Literal requests, environments, and provider results make forwarding repeatable.
RUNTIME EXCLUSION: Real kernel execution, event publication, and provider work are excluded.
SESSION / EXECUTION LIMIT: Existing session/execution alias semantics are not certified here.
CHANGELOG: v1.0.1 removes the obsolete session/execution alias expectation; v1.0.0 certifies runner-to-bootstrap forwarding.

WILSY OWNS BUSINESS TRUTH. EOS ALL THE WAY.
"""

import inspect

import pytest

import tools.eos.kernel.runner as runner_module
from tools.eos.kernel.domain.kernel_bootstrap_request import KernelBootstrapRequest
from tools.eos.kernel.runner import EngineeringKernelPipeline, EngineeringKernelRunner


class BootstrapSubstitute:
    """Minimal deterministic boundary substitute that records forwarded inputs."""

    calls: list[tuple[KernelBootstrapRequest, str]] = []

    def __init__(self, request: KernelBootstrapRequest, deployment_environment: str) -> None:
        self.session_id = "kernel-forwarded-session"
        BootstrapSubstitute.calls.append((request, deployment_environment))

    async def boot_and_execute(self) -> dict[str, object]:
        """Return only the fields required by the existing runner adapter."""
        return {"status": "SUCCESS", "session_id": self.session_id}


@pytest.fixture(autouse=True)
def isolated_substitute(monkeypatch: pytest.MonkeyPatch) -> None:
    """Install the narrow bootstrap boundary and reset deterministic observations."""
    BootstrapSubstitute.calls = []
    monkeypatch.setattr(runner_module, "WilsyKernelBootstrap", BootstrapSubstitute)


def make_request(
    tenant_id: str = "tenant-runner-alpha",
    principal_id: str = "principal-runner-alpha",
    request_id: str = "request-runner-alpha",
    correlation_id: str | None = "corr-runner-alpha",
) -> KernelBootstrapRequest:
    """Build a literal request for forwarding certification."""
    return KernelBootstrapRequest(tenant_id, principal_id, request_id, correlation_id)


def test_runner_and_pipeline_require_explicit_authority() -> None:
    runner_signature = inspect.signature(EngineeringKernelRunner.run)
    pipeline_signature = inspect.signature(EngineeringKernelPipeline.execute)
    for signature in (runner_signature, pipeline_signature):
        assert signature.parameters["request"].default is inspect.Parameter.empty
        assert signature.parameters["deployment_environment"].default is inspect.Parameter.empty


def test_runner_forwards_exact_request_and_environment() -> None:
    request = make_request()
    result = EngineeringKernelRunner().run(request, "test")
    assert result.success is True
    assert BootstrapSubstitute.calls == [(request, "test")]
    assert BootstrapSubstitute.calls[0][0] is request


def test_pipeline_forwards_exact_request_and_environment() -> None:
    request = make_request()
    EngineeringKernelPipeline().execute(request, "test")
    assert BootstrapSubstitute.calls == [(request, "test")]
    assert BootstrapSubstitute.calls[0][0] is request


def test_absent_correlation_remains_absent_at_bootstrap_boundary() -> None:
    request = make_request(correlation_id=None)
    EngineeringKernelRunner().run(request, "test")
    forwarded = BootstrapSubstitute.calls[0][0]
    assert forwarded is request
    assert forwarded.correlation_id is None


def test_reusable_runner_keeps_two_tenants_isolated() -> None:
    first = make_request()
    second = make_request("tenant-runner-beta", "principal-runner-beta", "request-runner-beta", None)
    runner = EngineeringKernelRunner()
    runner.run(first, "test")
    runner.run(second, "staging")
    assert BootstrapSubstitute.calls == [(first, "test"), (second, "staging")]
    assert BootstrapSubstitute.calls[0][0] is not BootstrapSubstitute.calls[1][0]


def test_runner_and_pipeline_retain_no_per_execution_authority() -> None:
    runner = EngineeringKernelRunner()
    pipeline = EngineeringKernelPipeline()
    runner.run(make_request(), "test")
    pipeline.execute(make_request("tenant-runner-beta", "principal-runner-beta", "request-runner-beta"), "staging")
    runner_state = vars(runner)
    pipeline_state = vars(pipeline)
    for state in (runner_state, pipeline_state):
        assert all(name not in state for name in ("request", "tenant_id", "principal_id", "request_id", "correlation_id", "deployment_environment"))


def test_request_material_is_unchanged_after_forwarding() -> None:
    request = make_request()
    before = request.to_dict()
    EngineeringKernelRunner().run(request, "test")
    assert request.to_dict() == before
    assert BootstrapSubstitute.calls[0][0] is request


def test_forwarding_does_not_rebuild_authority_or_add_session_fields() -> None:
    request = make_request()
    EngineeringKernelPipeline().execute(request, "test")
    forwarded = BootstrapSubstitute.calls[0][0]
    assert forwarded is request
    assert tuple(forwarded.to_dict()) == ("tenant_id", "principal_id", "request_id", "correlation_id")
    assert "session_id" not in forwarded.to_dict()
    assert "execution_id" not in forwarded.to_dict()


def test_forwarding_preserves_each_identity_dimension() -> None:
    request = make_request()
    EngineeringKernelRunner().run(request, "test")
    forwarded = BootstrapSubstitute.calls[0][0]
    assert forwarded.tenant_id == "tenant-runner-alpha"
    assert forwarded.principal_id == "principal-runner-alpha"
    assert forwarded.request_id == "request-runner-alpha"
    assert forwarded.correlation_id == "corr-runner-alpha"


def test_provider_owned_session_result_is_not_claimed_as_request_identity() -> None:
    request = make_request()
    result = EngineeringKernelRunner().run(request, "test")
    assert result.execution_id != request.request_id
    assert result.execution_id != request.correlation_id


# ARTIFACT: test_engineering_kernel_runner_authority_forwarding.py
# VERSION: v1.0.1-WILSY-KERNEL-RUNNER-AUTHORITY-FORWARDING-CERT
# AUTHORITY BOUNDARY: pure per-execution forwarding certification only.
# TENANT POSTURE: explicit request authority remains isolated across calls.
# FAIL-CLOSED POSTURE: request and deployment environment are required parameters.
# FINANCIAL EXECUTION AUTHORITY: none; Kennel financial truth remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
