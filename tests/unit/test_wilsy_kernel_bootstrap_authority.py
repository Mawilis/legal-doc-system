"""WILSY OS — dedicated certification for bootstrap authority normalization.

TITLE: Wilsy Kernel Bootstrap Authority Certification
VERSION: v1.0.0-WILSY-KERNEL-BOOTSTRAP-AUTHORITY-CERT
PURPOSE: Prove that certified request authority enters the kernel provider context unchanged.
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_kernel_bootstrap_authority.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
UPDATED: 2026-08-29
SCOPE: Deterministic constructor normalization only; kernel execution is excluded.
SECURITY / PRIVACY: Tests authority references and never carry sensitive authentication material.
TENANT BOUNDARY: Explicit request tenant is preserved without fallback or substitution.
PRINCIPAL BOUNDARY: Explicit authenticated principal reference is preserved unchanged.
REQUEST / CORRELATION: Request and correlation identities remain distinct and explicit.
DEPLOYMENT AUTHORITY: Environment is supplied explicitly by the provider harness.
SESSION OWNERSHIP: Deterministic session override remains provider-owned and independent.
DETERMINISM: Literal values and explicit session/environment inputs produce stable assertions.
CHANGELOG: v1.0.0 certifies the corrected bootstrap normalization boundary.

WILSY OWNS BUSINESS TRUTH. EOS ALL THE WAY.
"""

import inspect

from tools.eos.kernel import ExecutionContext, WilsyKernelBootstrap
from tools.eos.kernel.domain.kernel_bootstrap_request import KernelBootstrapRequest


def make_request(
    tenant_id: str = "tenant-cert-alpha",
    principal_id: str = "principal-cert-alpha",
    request_id: str = "request-cert-alpha",
    correlation_id: str | None = None,
) -> KernelBootstrapRequest:
    """Build a deterministic certified request."""
    return KernelBootstrapRequest(tenant_id, principal_id, request_id, correlation_id)


def make_bootstrap(request: KernelBootstrapRequest) -> WilsyKernelBootstrap:
    """Construct the provider with explicit deployment and lifecycle authority."""
    return WilsyKernelBootstrap(request, "test", "kernel-cert-session-001")


def test_explicit_authority_is_normalized_once() -> None:
    request = make_request()
    before = request.to_dict()
    bootstrap = make_bootstrap(request)
    context = bootstrap.context
    assert context.tenant_id == request.tenant_id
    assert context.principal_id == request.principal_id
    assert context.request_id == request.request_id
    assert context.correlation_id is None
    assert request.to_dict() == before


def test_correlation_is_preserved_and_not_aliased() -> None:
    request = make_request(correlation_id="corr-cert-alpha")
    context = make_bootstrap(request).context
    assert context.correlation_id == "corr-cert-alpha"
    assert context.correlation_id != context.request_id


def test_session_override_is_provider_owned_and_independent() -> None:
    request = make_request(correlation_id="corr-cert-alpha")
    context = make_bootstrap(request).context
    assert context.session_id == "kernel-cert-session-001"
    assert context.session_id not in {
        context.tenant_id,
        context.principal_id,
        context.request_id,
        context.correlation_id,
    }


def test_environment_is_explicit_provider_authority() -> None:
    request = make_request()
    context = make_bootstrap(request).context
    assert context.environment == "test"
    assert "environment" not in request.to_dict()


def test_cross_tenant_principal_and_request_values_do_not_bleed() -> None:
    first = make_bootstrap(make_request()).context
    second = make_bootstrap(
        make_request(
            tenant_id="tenant-cert-beta",
            principal_id="principal-cert-beta",
            request_id="request-cert-beta",
            correlation_id="corr-cert-beta",
        )
    ).context
    assert first.tenant_id == "tenant-cert-alpha"
    assert first.principal_id == "principal-cert-alpha"
    assert first.request_id == "request-cert-alpha"
    assert first.correlation_id is None
    assert second.tenant_id == "tenant-cert-beta"
    assert second.principal_id == "principal-cert-beta"
    assert second.request_id == "request-cert-beta"
    assert second.correlation_id == "corr-cert-beta"


def test_context_has_explicit_authority_surface_without_runtime_or_claim_fields() -> None:
    names = set(ExecutionContext.model_fields)
    assert names == {
        "session_id",
        "tenant_id",
        "principal_id",
        "request_id",
        "correlation_id",
        "environment",
        "booted_at",
    }
    forbidden = {
        "token",
        "password",
        "secret",
        "credential",
        "api_key",
        "roles",
        "permissions",
        "claims",
        "execution_id",
    }
    assert names.isdisjoint(forbidden)


def test_provider_requires_request_environment_and_optional_session() -> None:
    signature = inspect.signature(WilsyKernelBootstrap)
    assert signature.parameters["request"].default is inspect.Parameter.empty
    assert signature.parameters["deployment_environment"].default is inspect.Parameter.empty
    assert signature.parameters["session_id"].default is None


def test_missing_deployment_environment_fails_closed() -> None:
    request = make_request()
    try:
        WilsyKernelBootstrap(request, "")
    except ValueError as error:
        assert str(error) == "deployment_environment is invalid"
    else:
        raise AssertionError("empty deployment environment must fail")


def test_normalization_is_deterministic_for_identical_inputs() -> None:
    first = make_bootstrap(make_request(correlation_id="corr-cert-alpha")).context
    second = make_bootstrap(make_request(correlation_id="corr-cert-alpha")).context
    assert first.session_id == second.session_id
    assert first.tenant_id == second.tenant_id
    assert first.principal_id == second.principal_id
    assert first.request_id == second.request_id
    assert first.correlation_id == second.correlation_id
    assert first.environment == second.environment


# ARTIFACT: test_wilsy_kernel_bootstrap_authority.py
# VERSION: v1.0.0-WILSY-KERNEL-BOOTSTRAP-AUTHORITY-CERT
# AUTHORITY BOUNDARY: constructor normalization certification only.
# TENANT POSTURE: explicit request authority remains tenant-scoped and unchanged.
# FAIL-CLOSED POSTURE: deployment authority is required; no fallback is accepted.
# FINANCIAL EXECUTION AUTHORITY: none; Kennel financial truth remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
