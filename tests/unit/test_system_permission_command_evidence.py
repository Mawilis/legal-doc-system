"""TITLE: D12 system permission command evidence certificate.
VERSION: v1.0.0-D12-COMMAND-EVIDENCE-CERT
AUTHORITY: Direct immutable binding and SHA3-512 proof.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_system_permission_command_evidence.py
CERTIFICATION DATE: 2026-10-14
CHANGELOG: v1.0.0 certifies all command evidence operations.
BOUNDARY: Evidence only; no transaction, tenant, or finance authority.
"""
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
import pytest
from tools.eos.auth.system_permission_command_evidence import *

NOW = datetime(2026, 10, 14, 13, 0, tzinfo=timezone.utc)


def _value(operation: SystemPermissionCommandOperation = SystemPermissionCommandOperation.ASSIGN) -> SystemPermissionCommandEvidence:
    extras = {}
    if operation is SystemPermissionCommandOperation.BOOTSTRAP_SEED:
        extras = {"bootstrap_id": "bootstrap-1", "bootstrap_purpose": "SEED_SYSTEM_PERMISSION_ASSIGNMENT_COMMAND_AUTHORITY"}
    if operation is SystemPermissionCommandOperation.REVOKE:
        extras = {"assignment_id": "assignment-1"}
    return SystemPermissionCommandEvidence(operation, "actor-1", "target-1", "privileged_activation:issue", "evidence-1", NOW, "idem-1", **extras)


@pytest.mark.parametrize("operation", list(SystemPermissionCommandOperation))
def test_exact_construction_deterministic_fingerprint_and_operation_bindings(operation: SystemPermissionCommandOperation) -> None:
    first = _value(operation)
    second = _value(operation)
    assert first == second and len(first.evidence_fingerprint) == 128
    assert first.to_payload()["operation"] == operation.value
    if operation is not SystemPermissionCommandOperation.REVOKE:
        assert first.derived_assignment_id().startswith("WILSYSYSPERM-")


@pytest.mark.parametrize("field", ["actor_principal_id", "target_principal_id", "permission_id", "evidence_reference", "idempotency_key"])
def test_every_core_binding_changes_fingerprint(field: str) -> None:
    value = _value()
    assert replace(value, **{field: "different"}).evidence_fingerprint != value.evidence_fingerprint


@pytest.mark.parametrize("invalid", ["", "*", " value", "value "])
def test_invalid_identifiers_rejected(invalid: str) -> None:
    with pytest.raises(SystemPermissionCommandEvidenceError):
        replace(_value(), actor_principal_id=invalid)


def test_utc_required_bootstrap_binding_required_and_immutable() -> None:
    with pytest.raises(SystemPermissionCommandEvidenceError, match="OCCURRED_AT_INVALID"):
        replace(_value(), occurred_at=NOW.replace(tzinfo=None))
    with pytest.raises(SystemPermissionCommandEvidenceError, match="BOOTSTRAP_ID_INVALID"):
        SystemPermissionCommandEvidence(SystemPermissionCommandOperation.BOOTSTRAP_SEED, "a", "a", "p", "e", NOW, "i")
    with pytest.raises(FrozenInstanceError):
        _value().permission_id = "other"  # type: ignore[misc]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_system_permission_command_evidence.py
# VERSION: v1.0.0-D12-COMMAND-EVIDENCE-CERT
# AUTHORITY BOUNDARY: IMMUTABLE EVIDENCE CERTIFICATE ONLY
# END OF WILSY OS SOVEREIGN ARTIFACT
