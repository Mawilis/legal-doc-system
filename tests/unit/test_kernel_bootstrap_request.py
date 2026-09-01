"""WILSY OS — dedicated certification for kernel bootstrap authority.

TITLE: KernelBootstrapRequest Domain Certification
VERSION: v1.0.0-WILSY-KERNEL-BOOTSTRAP-REQUEST-CERT
PURPOSE: Prove the immutable, tenant-scoped bootstrap authority contract.
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_kernel_bootstrap_request.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
UPDATED: 2026-08-29
SCOPE: Deterministic unit certification only; no provider or runtime execution.
SECURITY / PRIVACY: Tests references only; no credentials, claims, or secrets.
TENANT AUTHORITY: Explicit tenant reference is required and validated fail-closed.
CERTIFICATION BOUNDARY: Domain construction, identity separation, and serialization.
DETERMINISM: Literal fixtures, stable assertions, and repeatable value semantics.
PROVIDER / RUNTIME AUTHORITY: None; live handles and generated execution IDs are absent.
CHANGELOG: v1.0.0 certifies the initial KernelBootstrapRequest contract.

WILSY OWNS BUSINESS TRUTH. EOS ALL THE WAY.
"""

from dataclasses import fields

import pytest

from tools.eos.kernel.domain.kernel_bootstrap_request import (
    KernelBootstrapRequest,
    KernelBootstrapRequestError,
)


def request(
    tenant_id: str = "tenant-certification",
    principal_id: str = "principal-certification",
    request_id: str = "request-certification",
    correlation_id: str | None = None,
) -> KernelBootstrapRequest:
    """Construct a deterministic tenant-scoped certification fixture."""
    return KernelBootstrapRequest(tenant_id, principal_id, request_id, correlation_id)


def test_valid_authority_is_normalized_and_correlation_is_absent() -> None:
    value = request(tenant_id=" tenant-certification ", principal_id=" principal-certification ")
    assert value.tenant_id == "tenant-certification"
    assert value.principal_id == "principal-certification"
    assert value.request_id == "request-certification"
    assert value.correlation_id is None


def test_explicit_correlation_remains_distinct() -> None:
    value = request(correlation_id="correlation-certification")
    assert value.correlation_id == "correlation-certification"
    assert value.correlation_id != value.request_id


@pytest.mark.parametrize("field", ["tenant_id", "principal_id", "request_id"])
@pytest.mark.parametrize("invalid", ["", "   ", "unknown", "none", "null"])
def test_required_authority_rejects_empty_and_sentinel_values(field: str, invalid: str) -> None:
    with pytest.raises(KernelBootstrapRequestError, match=f"{field} is invalid"):
        if field == "tenant_id":
            request(tenant_id=invalid)
        elif field == "principal_id":
            request(principal_id=invalid)
        else:
            request(request_id=invalid)


def test_correlation_rejects_empty_and_sentinel_values() -> None:
    for invalid in ("", "   ", "unknown", "none", "null"):
        with pytest.raises(KernelBootstrapRequestError, match="correlation_id is invalid"):
            request(correlation_id=invalid)


def test_immutability_and_slots_are_enforced() -> None:
    value = request()
    with pytest.raises(AttributeError):
        setattr(value, "tenant_id", "other-tenant")
    with pytest.raises((AttributeError, TypeError)):
        setattr(value, "extra", "forbidden")


def test_field_surface_preserves_authority_boundaries() -> None:
    names = tuple(item.name for item in fields(KernelBootstrapRequest))
    assert names == ("tenant_id", "principal_id", "request_id", "correlation_id")
    lowered = {name.casefold() for name in names}
    assert not lowered.intersection({"session_id", "execution_id", "provider", "client"})
    assert not any(word in name for name in lowered for word in ("token", "password", "secret", "credential", "api_key"))
    assert not lowered.intersection({"repository", "sentinel", "knowledge_graph", "payload", "metadata"})


def test_serialization_is_deterministic_and_does_not_generate_data() -> None:
    value = request(correlation_id="correlation-certification")
    first = value.to_dict()
    second = value.to_dict()
    assert first == second
    assert tuple(first) == ("tenant_id", "principal_id", "request_id", "correlation_id")
    assert first == {
        "tenant_id": "tenant-certification",
        "principal_id": "principal-certification",
        "request_id": "request-certification",
        "correlation_id": "correlation-certification",
    }


def test_value_equality_distinguishes_each_material_identity() -> None:
    baseline = request(correlation_id="correlation-certification")
    assert baseline == request(correlation_id="correlation-certification")
    assert baseline != request(tenant_id="other-tenant", correlation_id="correlation-certification")
    assert baseline != request(principal_id="other-principal", correlation_id="correlation-certification")
    assert baseline != request(request_id="other-request", correlation_id="correlation-certification")
    assert baseline != request(correlation_id="other-correlation")


def test_contract_has_no_system_mode_or_generated_execution_authority() -> None:
    names = {item.name for item in fields(KernelBootstrapRequest)}
    assert "system_mode" not in names
    assert "session_id" not in names
    assert "execution_id" not in names


# ARTIFACT: test_kernel_bootstrap_request.py
# VERSION: v1.0.0-WILSY-KERNEL-BOOTSTRAP-REQUEST-CERT
# AUTHORITY BOUNDARY: deterministic unit certification of domain authority only.
# TENANT POSTURE: explicit tenant reference; missing, blank, and sentinels fail closed.
# FAIL-CLOSED POSTURE: invalid authority references raise KernelBootstrapRequestError.
# FINANCIAL EXECUTION AUTHORITY: none; Kennel financial truth remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
