"""Direct certificate for immutable authorization-role revocation evidence.

TITLE: Authorization Role Revocation Evidence Direct Certificate
VERSION: v1.0.0-P1-R3B-E1-AUTHORIZATION-ROLE-REVOCATION-EVIDENCE-CERT
AUTHORITY: Wilsy OS Core Governance / Sovereign IAM Design
EPITOME: Prove strict transition, provenance, serialization, fingerprint, and authority boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_authorization_role_revocation_evidence.py
COLLABORATION / OWNERSHIP: Certifies only authorization_role_revocation_evidence.py.
CERTIFICATION / UPDATE DATE: 2026-10-13
CHANGELOG: v1.0.0-P1-R3B-E1 establishes direct value-object and dependency-boundary proof.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identities; no credentials or PII.
TENANT BOUNDARY: Exact non-pseudo tenant evidence only; no inference.
AUTHORITY BOUNDARY: Test-only verification; no authority, mutation, persistence, or transaction ownership.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tools.eos.auth.authorization_role_revocation_evidence import (
    OPERATION,
    PRIOR_STATUS,
    RESULT_STATUS,
    SCHEMA,
    AuthorizationRoleRevocationEvidence,
    AuthorizationRoleRevocationEvidenceError,
)

VERSION = "v1.0.0-P1-R3B-E1-AUTHORIZATION-ROLE-REVOCATION-EVIDENCE-CERT"
PRODUCTION = Path("tools/eos/auth/authorization_role_revocation_evidence.py")
DIGEST_A = "a" * 128


def evidence(**changes: object) -> AuthorizationRoleRevocationEvidence:
    """Construct canonical revision-zero-to-one evidence with explicit overrides."""
    values: dict[str, object] = {
        "revocation_id": "revoke-001",
        "tenant_id": "tenant-a",
        "actor_principal_id": "principal-admin",
        "target_principal_id": "principal-target",
        "target_role_id": "AUDITOR",
        "target_assignment_prior_revision": 0,
        "target_assignment_result_revision": 1,
        "operation": "role_revoke",
        "reason_reference": "ticket:ACCESS-42",
        "authorization_evidence_reference": "tenant-authorization-decision:auth-001",
        "authorization_evidence_fingerprint": DIGEST_A,
        "idempotency_key": "idem-001",
        "revoked_at": datetime(2026, 10, 13, 8, 30, tzinfo=timezone.utc),
    }
    values.update(changes)
    return AuthorizationRoleRevocationEvidence(**values)  # type: ignore[arg-type]


def test_valid_construction_is_immutable_and_binds_transition() -> None:
    """Valid evidence is immutable and encodes only ACTIVE-to-REVOKED."""
    value = evidence()
    assert value.operation == OPERATION
    assert value.target_assignment_prior_revision == 0
    assert value.target_assignment_result_revision == 1
    assert value.evidence_payload()["prior_status"] == PRIOR_STATUS
    assert value.evidence_payload()["result_status"] == RESULT_STATUS
    with pytest.raises(FrozenInstanceError):
        value.tenant_id = "tenant-b"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "bad"),
    [
        ("revocation_id", ""),
        ("revocation_id", " revoke "),
        ("revocation_id", 1),
        ("tenant_id", ""),
        ("tenant_id", "GLOBAL_ROOT"),
        ("tenant_id", "tenant\ninvalid"),
        ("actor_principal_id", ""),
        ("actor_principal_id", " actor "),
        ("target_principal_id", None),
        ("target_principal_id", "target\tinvalid"),
        ("target_role_id", ""),
        ("target_role_id", " AUDITOR"),
        ("reason_reference", ""),
        ("reason_reference", " reason "),
        ("authorization_evidence_reference", ""),
        ("authorization_evidence_reference", "auth\nreference"),
        ("idempotency_key", ""),
        ("idempotency_key", " idem "),
    ],
)
def test_malformed_identifiers_reject(field: str, bad: object) -> None:
    """Every identity, reason, provenance reference, and idempotency key is strict."""
    with pytest.raises(AuthorizationRoleRevocationEvidenceError):
        evidence(**{field: bad})


def test_unknown_operation_rejects() -> None:
    """The evidence schema recognizes only exact role_revoke."""
    with pytest.raises(AuthorizationRoleRevocationEvidenceError):
        evidence(operation="role_grant")


@pytest.mark.parametrize(
    "bad",
    ["", "a" * 127, "a" * 129, "A" * 128, "g" * 128, 7, None],
)
def test_malformed_authorization_fingerprint_rejects(bad: object) -> None:
    """Authorization provenance requires exact lowercase SHA3-512 hex."""
    with pytest.raises(AuthorizationRoleRevocationEvidenceError):
        evidence(authorization_evidence_fingerprint=bad)


@pytest.mark.parametrize(
    ("prior", "result"),
    [
        (True, 2),
        (0, True),
        (-1, 0),
        (0, -1),
        ("0", 1),
        (0, 1.0),
        (0, 2),
        (3, 3),
    ],
)
def test_invalid_revision_contract_rejects(prior: object, result: object) -> None:
    """Revisions must be non-boolean integers and exactly contiguous."""
    with pytest.raises(AuthorizationRoleRevocationEvidenceError):
        evidence(
            target_assignment_prior_revision=prior,
            target_assignment_result_revision=result,
        )


def test_revision_zero_to_one_is_accepted() -> None:
    """The initial assignment transition 0 to 1 is valid evidence."""
    assert evidence().target_assignment_result_revision == 1


@pytest.mark.parametrize("bad", [datetime(2026, 10, 13), "2026-10-13T00:00:00Z", None])
def test_invalid_timestamp_rejects(bad: object) -> None:
    """Naive and non-datetime timestamp values reject."""
    with pytest.raises(AuthorizationRoleRevocationEvidenceError):
        evidence(revoked_at=bad)


def test_aware_timestamp_is_canonicalized_to_utc() -> None:
    """One aware offset is normalized exactly once to UTC."""
    local = datetime(2026, 10, 13, 10, 30, tzinfo=timezone(timedelta(hours=2)))
    value = evidence(revoked_at=local)
    assert value.revoked_at == datetime(2026, 10, 13, 8, 30, tzinfo=timezone.utc)
    assert value.to_persisted()["revoked_at"] == "2026-10-13T08:30:00.000000+00:00"


def test_fingerprint_is_deterministic_lowercase_sha3_512() -> None:
    """Identical semantic evidence yields one stable lowercase digest."""
    first = evidence().revocation_evidence_fingerprint
    second = evidence().revocation_evidence_fingerprint
    assert first == second
    assert len(first) == 128 and first == first.lower()
    int(first, 16)


@pytest.mark.parametrize(
    ("field", "changed"),
    [
        ("actor_principal_id", "principal-other-admin"),
        ("target_principal_id", "principal-other-target"),
        ("target_role_id", "SERVICE_WORKER"),
        ("target_assignment_prior_revision", 4),
        ("reason_reference", "ticket:ACCESS-43"),
        ("authorization_evidence_reference", "tenant-authorization-decision:auth-002"),
        ("authorization_evidence_fingerprint", "b" * 128),
        ("idempotency_key", "idem-002"),
        ("revoked_at", datetime(2026, 10, 13, 8, 31, tzinfo=timezone.utc)),
    ],
)
def test_every_material_fact_changes_fingerprint(field: str, changed: object) -> None:
    """Every identity, provenance, idempotency, revision, and time fact is bound."""
    overrides = {field: changed}
    if field == "target_assignment_prior_revision":
        overrides["target_assignment_result_revision"] = 5
    assert evidence(**overrides).revocation_evidence_fingerprint != evidence().revocation_evidence_fingerprint


def test_persisted_shape_schema_and_roundtrip_are_exact() -> None:
    """Strict persisted evidence includes schema, transition, digest, and roundtrips."""
    value = evidence()
    persisted = value.to_persisted()
    assert persisted["schema"] == SCHEMA
    assert persisted["prior_status"] == "ACTIVE"
    assert persisted["result_status"] == "REVOKED"
    assert set(persisted) == {
        "schema", "revocation_id", "tenant_id", "actor_principal_id",
        "target_principal_id", "target_role_id",
        "target_assignment_prior_revision", "target_assignment_result_revision",
        "prior_status", "result_status", "operation", "reason_reference",
        "authorization_evidence_reference", "authorization_evidence_fingerprint",
        "idempotency_key", "revoked_at", "revocation_evidence_fingerprint",
    }
    assert AuthorizationRoleRevocationEvidence.from_persisted(persisted) == value


@pytest.mark.parametrize("mutation", ["unknown", "missing", "schema", "fingerprint", "timestamp", "transition"])
def test_persisted_corruption_rejects(mutation: str) -> None:
    """Shape, schema, transition, time, and digest corruption fail closed."""
    persisted = evidence().to_persisted()
    if mutation == "unknown":
        persisted["unknown"] = "value"
    elif mutation == "missing":
        persisted.pop("reason_reference")
    elif mutation == "schema":
        persisted["schema"] = "WILSY-AUTHORIZATION-ROLE-REVOCATION-EVIDENCE/V2"
    elif mutation == "fingerprint":
        persisted["revocation_evidence_fingerprint"] = "f" * 128
    elif mutation == "timestamp":
        persisted["revoked_at"] = "not-a-time"
    else:
        persisted["prior_status"] = "REVOKED"
    with pytest.raises(AuthorizationRoleRevocationEvidenceError):
        AuthorizationRoleRevocationEvidence.from_persisted(persisted)


def test_construction_grants_no_authority_or_mutation() -> None:
    """Evidence construction records history and exposes no authority result."""
    value = evidence()
    assert not hasattr(value, "authorized")
    assert not hasattr(value, "allowed")
    assert not hasattr(value, "mutate")
    assert not hasattr(value, "revoke")


def test_production_dependency_and_authority_boundaries() -> None:
    """Certify pure evidence without Mongo, repositories, sessions, Legal, finance, or root workflows."""
    source = PRODUCTION.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert all(not name.startswith(("pymongo", "fastapi", "tools.eos.legal_operations")) for name in imports)
    assert "role_assignment_repository" not in source.lower()
    forbidden_calls = {
        "insert_one", "update_one", "delete_one", "create_index",
        "compare_and_swap", "start_session", "start_transaction",
    }
    called = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))
    }
    assert called.isdisjoint(forbidden_calls)
    assert "collection_name" not in source.lower()
    assert "financial execution authority: none" in source.lower()
    function_names = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert function_names.isdisjoint({"authorize", "evaluate_policy", "rotate_root", "break_glass", "activate_privilege"})


# ARTIFACT: test_authorization_role_revocation_evidence.py
# VERSION: v1.0.0-P1-R3B-E1-AUTHORIZATION-ROLE-REVOCATION-EVIDENCE-CERT
# AUTHORITY BOUNDARY: direct immutable-evidence verification only; no authority, mutation, persistence, transaction, root lifecycle, activation, or break glass
# TENANT POSTURE: exact tenant/actor/target/role binding and no inference certified
# FAIL-CLOSED POSTURE: malformed facts, schema/transition/time drift, and fingerprint corruption reject
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
