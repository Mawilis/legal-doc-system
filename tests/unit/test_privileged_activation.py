"""TITLE: WILSY OS Privileged Activation Domain Direct Certificate.
VERSION: v1.0.0-P4-R1-DIRECT-CERTIFICATE
AUTHORITY: Direct certification of pure normal-activation semantics only.
EPITOME: Proves exact self-scope, bounded lifetime, temporal currentness,
terminal revocation, evidence lineage, immutable sealing, and authority walls.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_privileged_activation.py
COLLABORATION / OWNERSHIP: P4-R1 domain with canonical P2 target-class and P3
assurance-purpose vocabularies.
CERTIFICATION / UPDATE DATE: 2026-10-14
CHANGELOG: v1.0.0-P4-R1 establishes the complete direct pure-domain certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identifiers and fingerprints only.
TENANT BOUNDARY: Exact tuple matching; wildcard and cross-tenant use deny.
AUTHORITY BOUNDARY: Tests activation facts, not issuance or privileged use.
FINANCIAL AUTHORITY BOUNDARY: No financial execution authority.
"""

from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tools.eos.auth.privileged_activation import (
    ISSUANCE_PERMISSION,
    MAXIMUM_ACTIVATION_LIFETIME,
    PrivilegedActivation,
    PrivilegedActivationError,
    PrivilegedActivationStatus,
)
from tools.eos.auth.privileged_eligibility import PrivilegedTargetClass
from tools.eos.auth.privileged_security_assurance import PrivilegedAssurancePurpose


NOW = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128


def activation(**changes: object) -> PrivilegedActivation:
    values: dict[str, object] = {
        "activation_id": "WILSYACTIVATION-p4-r1",
        "tenant_id": "tenant-a",
        "principal_id": "principal-a",
        "actor_principal_id": "principal-a",
        "privileged_role_id": "ENTERPRISE_ADMIN",
        "target_class": PrivilegedTargetClass.TENANT_PRIVILEGED,
        "eligibility_evidence_id": "eligibility-a",
        "eligibility_evidence_fingerprint": FP_A,
        "assurance_evidence_id": "assurance-a",
        "assurance_evidence_fingerprint": FP_B,
        "creation_assurance_purpose": PrivilegedAssurancePurpose.PRIVILEGED_ELIGIBILITY_TO_ACTIVATION,
        "activated_at": NOW,
        "effective_until": NOW + MAXIMUM_ACTIVATION_LIFETIME,
        "issuance_idempotency_key": "issue-a",
    }
    values.update(changes)
    return PrivilegedActivation.issue(**values)  # type: ignore[arg-type]


def current(value: PrivilegedActivation, **changes: object) -> bool:
    values: dict[str, object] = {
        "at": NOW,
        "tenant_id": "tenant-a",
        "principal_id": "principal-a",
        "privileged_role_id": "ENTERPRISE_ADMIN",
        "target_class": PrivilegedTargetClass.TENANT_PRIVILEGED,
    }
    values.update(changes)
    return value.is_current(**values)  # type: ignore[arg-type]


def test_exact_self_activation_scope_and_creation_purpose() -> None:
    value = activation()
    assert value.actor_principal_id == value.principal_id
    assert value.creation_assurance_purpose is PrivilegedAssurancePurpose.PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
    assert ISSUANCE_PERMISSION == "privileged_activation:issue"
    assert current(value) is True


@pytest.mark.parametrize(
    "changes,code",
    [
        ({"actor_principal_id": "principal-b"}, "SELF_ACTIVATION_REQUIRED"),
        ({"tenant_id": None}, "TENANT_ID_INVALID"),
        ({"tenant_id": "*"}, "TENANT_ID_INVALID"),
        ({"privileged_role_id": "*"}, "PRIVILEGED_ROLE_ID_INVALID"),
        ({"principal_id": "*", "actor_principal_id": "*"}, "PRINCIPAL_ID_INVALID"),
        ({"creation_assurance_purpose": PrivilegedAssurancePurpose.PRIVILEGED_ACTIVATION_USE}, "CREATION_ASSURANCE_PURPOSE_INVALID"),
    ],
)
def test_scope_actor_wildcard_and_wrong_purpose_reject(changes: dict[str, object], code: str) -> None:
    with pytest.raises(PrivilegedActivationError, match=code):
        activation(**changes)


def test_platform_scope_forbids_tenant_and_remains_exact() -> None:
    value = activation(
        tenant_id=None,
        privileged_role_id="SOVEREIGN_ARCHITECT",
        target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT,
    )
    assert value.tenant_id is None
    assert value.is_current(
        at=NOW,
        tenant_id=None,
        principal_id="principal-a",
        privileged_role_id="SOVEREIGN_ARCHITECT",
        target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT,
    )
    with pytest.raises(PrivilegedActivationError, match="PLATFORM_SCOPE_TENANT_FORBIDDEN"):
        activation(target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT)


@pytest.mark.parametrize("delta", [timedelta(0), timedelta(microseconds=-1), timedelta(minutes=15, microseconds=1)])
def test_invalid_activation_lifetimes_reject(delta: timedelta) -> None:
    with pytest.raises(PrivilegedActivationError, match="ACTIVATION_LIFETIME_INVALID"):
        activation(effective_until=NOW + delta)


def test_half_open_interval_and_scope_mismatches_deny() -> None:
    value = activation()
    assert current(value, at=NOW) is True
    assert current(value, at=value.effective_until - timedelta(microseconds=1)) is True
    assert current(value, at=value.effective_until) is False
    assert current(value, principal_id="principal-b") is False
    assert current(value, tenant_id="tenant-b") is False
    assert current(value, privileged_role_id="SOVEREIGN_ARCHITECT") is False
    assert current(value, target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT, tenant_id=None) is False


def test_revocation_is_terminal_chained_and_never_current() -> None:
    first = activation()
    revoked = first.revoke(revoked_at=NOW + timedelta(minutes=1))
    assert first.status is PrivilegedActivationStatus.ACTIVE
    assert revoked.status is PrivilegedActivationStatus.REVOKED
    assert revoked.revision == 2
    assert revoked.previous_activation_fingerprint == first.activation_fingerprint
    assert current(revoked) is False
    with pytest.raises(PrivilegedActivationError, match="ACTIVATION_NOT_ACTIVE"):
        revoked.revoke(revoked_at=NOW + timedelta(minutes=2))


def test_value_is_immutable_and_fingerprint_covers_authority() -> None:
    first = activation()
    second = activation(assurance_evidence_id="assurance-b")
    assert len(first.activation_fingerprint) == 128
    assert first.fingerprint_matches(first.activation_fingerprint)
    assert first.activation_fingerprint != second.activation_fingerprint
    with pytest.raises(FrozenInstanceError):
        first.principal_id = "mutated"  # type: ignore[misc]


def test_no_secret_permission_use_break_glass_or_financial_fields() -> None:
    names = {field.name.lower() for field in fields(PrivilegedActivation)}
    forbidden = {
        "password", "otp", "jwt", "bearer", "private_key", "signature",
        "mfa_secret", "workload_secret", "permission", "payment",
        "settlement", "financial_execution", "break_glass",
        "eligible", "eligibility_current", "assurance_sufficient",
    }
    assert names.isdisjoint(forbidden)


def test_source_is_pure_and_has_sovereign_structure() -> None:
    source = Path("tools/eos/auth/privileged_activation.py").read_text()
    for forbidden in (
        "pymongo", "MongoClient", "FastAPI", "APIRouter", "os.environ",
        "datetime.now", "datetime.utcnow", "uuid4", "secrets.",
        "PRIVILEGED_ACTIVATION_USE)\n        )", "break_glass_registry",
    ):
        assert forbidden not in source
    assert "VERSION: v1.0.0-P4-R1-PRIVILEGED-ACTIVATION-DOMAIN" in source
    assert "END OF WILSY OS SOVEREIGN ARTIFACT" in source


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_privileged_activation.py
# VERSION: v1.0.0-P4-R1-DIRECT-CERTIFICATE
# AUTHORITY BOUNDARY: pure P4 domain certification only; no issuance runtime
# FINANCIAL EXECUTION AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
