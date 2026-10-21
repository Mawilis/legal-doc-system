"""TITLE: WILSY OS Ethical Wall Policy Domain Certificate.
VERSION: v1.0.0-G76-ETHICAL-WALL-POLICY-CERT
AUTHORITY: Pure deterministic policy-evidence verification only.
EPITOME: Freezes deny-first matter-wall semantics without operational grants.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_work_ethical_wall_policy.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-21.
CHANGELOG: 2026-10-21 v1.0.0 establishes the G76 policy-domain certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque identifiers and hashes; no matter content.
TENANT BOUNDARY: Exact tenant and matter scope.
AUTHORITY BOUNDARY: Recorded policy evidence is not institutional approval.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from tools.eos.legal_operations.domain.legal_work_ethical_wall_policy import (
    EthicalWallAccessState,
    EthicalWallPolicyError,
    EthicalWallPolicyRevision,
    EthicalWallPolicyStatus,
    InstitutionalRatificationState,
    evaluate_ethical_wall_access,
)

NOW = datetime(2026, 10, 21, 10, 0, tzinfo=UTC)


def policy(**changes: object) -> EthicalWallPolicyRevision:
    values: dict[str, object] = {
        "policy_id": "wall-1", "revision": 1, "predecessor_fingerprint": None,
        "tenant_id": "tenant-a", "case_matter_id": "matter-a",
        "protected_subject_fingerprints": ("a" * 128,),
        "restricted_principal_ids": ("principal-denied",),
        "permitted_principal_ids": ("principal-allowed",),
        "status": EthicalWallPolicyStatus.ACTIVE,
        "effective_from": NOW, "effective_until": NOW + timedelta(days=30),
        "source_evidence_reference": "source-1",
        "source_evidence_fingerprint": "b" * 128,
        "administrator_principal_id": "admin-1",
        "administrator_authorization_reference": "admin-auth-1",
        "administrator_authorization_fingerprint": "c" * 128,
        "ratification_state": InstitutionalRatificationState.PENDING,
        "ratification_reference": None, "ratification_fingerprint": None,
    }
    values.update(changes)
    return EthicalWallPolicyRevision(**values)  # type: ignore[arg-type]


def evaluate(principal: str, *history: EthicalWallPolicyRevision,
             at: datetime = NOW) -> EthicalWallAccessState:
    return evaluate_ethical_wall_access(
        tenant_id="tenant-a", case_matter_id="matter-a",
        practitioner_principal_id=principal, evaluation_time=at,
        revisions=history,
    ).state


def test_exact_policy_is_frozen_deterministic_and_non_authorizing() -> None:
    left = policy()
    assert left == policy()
    assert len(left.fingerprint) == 128
    assert left.permits_operational_access is False


def test_deny_by_absence_and_explicit_deny_precedence() -> None:
    value = policy(permitted_principal_ids=("principal-allowed", "principal-denied"))
    assert evaluate("principal-unknown", value) is EthicalWallAccessState.DENIED_ABSENT
    assert evaluate("principal-denied", value) is EthicalWallAccessState.DENIED_RESTRICTED


def test_recorded_allow_remains_unverified_even_with_recorded_ratification() -> None:
    pending = policy()
    approved = policy(
        ratification_state=InstitutionalRatificationState.APPROVED,
        ratification_reference="ratification-1",
        ratification_fingerprint="d" * 128,
    )
    assert evaluate("principal-allowed", pending) is EthicalWallAccessState.DENIED_UNRATIFIED
    result = evaluate_ethical_wall_access(
        tenant_id="tenant-a", case_matter_id="matter-a",
        practitioner_principal_id="principal-allowed", evaluation_time=NOW,
        revisions=(approved,),
    )
    assert result.state is EthicalWallAccessState.ALLOW_RECORDED_UNVERIFIED
    assert result.permits_operational_access is False


def test_ratification_evidence_pair_is_strict() -> None:
    with pytest.raises(EthicalWallPolicyError, match="RATIFICATION_EVIDENCE_REQUIRED"):
        policy(ratification_state=InstitutionalRatificationState.APPROVED)
    with pytest.raises(EthicalWallPolicyError, match="RATIFICATION_EVIDENCE_FORBIDDEN"):
        policy(ratification_reference="ratification-1",
               ratification_fingerprint="d" * 128)


def test_pseudo_tenant_rejects() -> None:
    with pytest.raises(EthicalWallPolicyError, match="TENANT_ID_INVALID"):
        policy(tenant_id="global")


def test_revocation_and_expiry_deny() -> None:
    root = policy(ratification_state=InstitutionalRatificationState.APPROVED,
                  ratification_reference="ratification-1",
                  ratification_fingerprint="d" * 128)
    revoked = policy(
        revision=2, predecessor_fingerprint=root.fingerprint,
        status=EthicalWallPolicyStatus.REVOKED,
        effective_from=NOW + timedelta(days=1),
        effective_until=NOW + timedelta(days=30),
        ratification_state=InstitutionalRatificationState.REVOKED,
        ratification_reference="ratification-2",
        ratification_fingerprint="e" * 128,
    )
    assert evaluate("principal-allowed", root, revoked,
                    at=NOW + timedelta(days=2)) is EthicalWallAccessState.DENIED_REVOKED
    assert evaluate("principal-allowed", root,
                    at=NOW + timedelta(days=31)) is EthicalWallAccessState.DENIED_EXPIRED


def test_lineage_scope_fork_and_tampering_corrupt_block() -> None:
    root = policy()
    successor = policy(revision=2, predecessor_fingerprint=root.fingerprint,
                       effective_from=NOW + timedelta(days=1))
    fork = replace(successor, source_evidence_reference="source-2")
    foreign = policy(tenant_id="tenant-b")
    tampered = object.__new__(EthicalWallPolicyRevision)
    for name in root.__dataclass_fields__:
        object.__setattr__(tampered, name, getattr(root, name))
    object.__setattr__(tampered, "fingerprint", "f" * 128)
    for history in ((root, successor, fork), (root, foreign), (tampered,)):
        assert evaluate("principal-allowed", *history) is EthicalWallAccessState.DENIED_CORRUPT


# ARTIFACT: test_legal_work_ethical_wall_policy.py
# VERSION: v1.0.0-G76-ETHICAL-WALL-POLICY-CERT
# AUTHORITY BOUNDARY: non-authorizing immutable policy evidence only
# TENANT POSTURE: exact tenant and matter; drift corrupt-blocked
# FAIL-CLOSED POSTURE: absence, restriction, pending, revocation and corruption deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
