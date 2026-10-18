"""Unit certificate for P3-R3G-S6-A1 internal workload credential authority.

TITLE: Internal-Service Workload Credential Authority Unit Certificate
VERSION: v1.0.0-P3-R3G-S6-A1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Pure contract proof for binding, lifecycle, secret exclusion, and caller-input boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_internal_service_workload_credential_authority.py
COLLABORATION / OWNERSHIP: EOS IAM authority certification.
CERTIFICATION / UPDATE DATE: 2026-10-14
CHANGELOG: v1.0.0-P3-R3G-S6-A1 establishes the bounded unit certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Uses synthetic identifiers and no production secrets.
TENANT BOUNDARY: Proves no tenant authority surface.
AUTHORITY BOUNDARY: Tests credential binding/currentness only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from datetime import datetime, timezone
import inspect

import pytest

from tools.eos.auth.internal_service_workload_credential_authority import (
    PLATFORM_INTERNAL_SCOPE,
    InternalServiceWorkloadCredentialAuthority,
    InternalServiceWorkloadCredentialAuthorityError,
    WorkloadCredentialLifecycleStatus,
)
from tools.eos.auth.internal_service_workload_proof_service import InternalServiceWorkloadProofService

NOW = datetime(2026, 10, 14, tzinfo=timezone.utc)


def _authority(**changes: object) -> InternalServiceWorkloadCredentialAuthority:
    values: dict[str, object] = {
        "service_id": "node-authority-bridge", "key_id": "key-2026-10", "principal_id": "principal-service-1",
        "credential_scope": PLATFORM_INTERNAL_SCOPE, "credential_revision": 1, "lifecycle_revision": 1,
        "lifecycle_status": WorkloadCredentialLifecycleStatus.CURRENT, "status_changed_at": NOW,
    }
    values.update(changes)
    return InternalServiceWorkloadCredentialAuthority(**values)  # type: ignore[arg-type]


def test_current_binding_is_exact_secret_free_and_fingerprint_stable() -> None:
    authority = _authority()
    assert authority.service_id == "node-authority-bridge"
    assert authority.key_id == "key-2026-10"
    assert authority.principal_id == "principal-service-1"
    assert authority.credential_revision > 0
    assert authority.lifecycle_status is WorkloadCredentialLifecycleStatus.CURRENT
    assert authority == InternalServiceWorkloadCredentialAuthority.from_persisted(authority.to_persisted())
    persisted = authority.to_persisted()
    forbidden = {"secret", "hmac", "signature", "token", "tenant_id", "permission", "role", "privileged_activation"}
    assert forbidden.isdisjoint(persisted)


@pytest.mark.parametrize("status", [
    WorkloadCredentialLifecycleStatus.REVOKED,
    WorkloadCredentialLifecycleStatus.ROTATED,
    WorkloadCredentialLifecycleStatus.INVALIDATED,
])
def test_terminal_states_require_chained_lifecycle(status: WorkloadCredentialLifecycleStatus) -> None:
    current = _authority()
    terminal = _authority(
        lifecycle_revision=2, lifecycle_status=status, previous_fingerprint=current.authority_fingerprint,
    )
    assert terminal.lifecycle_status is status
    assert terminal.authority_fingerprint != current.authority_fingerprint


def test_scope_revision_and_corruption_fail_closed() -> None:
    with pytest.raises(InternalServiceWorkloadCredentialAuthorityError):
        _authority(credential_scope="TENANT")
    with pytest.raises(InternalServiceWorkloadCredentialAuthorityError):
        _authority(credential_revision=0)
    row = _authority().to_persisted()
    row["principal_id"] = "different-principal"
    with pytest.raises(InternalServiceWorkloadCredentialAuthorityError):
        InternalServiceWorkloadCredentialAuthority.from_persisted(row)


def test_public_workload_issuer_accepts_neither_principal_nor_proof_reference() -> None:
    parameters = inspect.signature(InternalServiceWorkloadProofService.verify_and_record).parameters
    assert "principal_id" not in parameters
    assert "proof_reference" not in parameters
    assert "tenant_id" not in parameters
    assert "permission" not in parameters
    assert "privileged_activation" not in parameters


# ARTIFACT: test_internal_service_workload_credential_authority.py
# VERSION: v1.0.0-P3-R3G-S6-A1
# AUTHORITY BOUNDARY: Unit certification only; creates no runtime authority.
# TENANT POSTURE: No tenant authority.
# FAIL-CLOSED POSTURE: Any contract drift fails the certificate.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
