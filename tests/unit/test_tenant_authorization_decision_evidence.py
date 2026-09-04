"""WILSY OS tenant authorization decision evidence direct certificate.
VERSION: v1.0.0-TENANT-AUTHORIZATION-DECISION-EVIDENCE-CERT
AUTHORITY: direct value-contract certification only; no authority grant.
"""
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, cast
import pytest

from tools.eos.auth.tenant_authorization_decision_evidence import (
    SCHEMA, VERSION, TenantAuthorizationDecisionEvidence,
    TenantAuthorizationDecisionEvidenceError,
)

STAMP = datetime(2026, 9, 4, 12, 0, tzinfo=timezone.utc)
HEX = "a" * 128


def make(**changes):
    data = dict(tenant_id="tenant-1", authorization_decision_id="decision-1", principal_id="principal-1", operation="profile_update", permission="tenant:profile:write", business_role="tenant_owner", authorization_role="TENANT_OWNER", membership_revision=0, role_assignment_revision=0, subject_reference="tenant-profile:tenant-1", subject_evidence_fingerprint=HEX, permission_namespace_version="v1", authorization_role_policy_version="v1", tenant_business_role_policy_version="v1", tenant_authorization_composition_version="v1.1.0", idempotency_key="idem-1", authorized_at=STAMP)
    data.update(changes)
    return TenantAuthorizationDecisionEvidence(**cast(dict[str, Any], data))


def test_schema_and_explicit_fields():
    value = make()
    assert SCHEMA == "WILSY-TENANT-AUTHORIZATION-DECISION-EVIDENCE/V1"
    assert set(value.__dataclass_fields__) == {"tenant_id", "authorization_decision_id", "principal_id", "operation", "permission", "business_role", "authorization_role", "membership_revision", "role_assignment_revision", "subject_reference", "subject_evidence_fingerprint", "permission_namespace_version", "authorization_role_policy_version", "tenant_business_role_policy_version", "tenant_authorization_composition_version", "idempotency_key", "authorized_at"}
    assert value.authorized_by_principal_id == "principal-1"
    assert value.authorization_evidence_reference == "tenant-authorization-decision:decision-1"


def test_immutable_and_no_denied_state():
    value = make()
    with pytest.raises((AttributeError, TypeError)): setattr(cast(Any, value), "tenant_id", "other")
    with pytest.raises((AttributeError, TypeError)): setattr(value, "authorized", False)
    assert not hasattr(value, "authorized")


@pytest.mark.parametrize("field", ["tenant_id", "authorization_decision_id", "principal_id", "operation", "permission", "business_role", "authorization_role", "subject_reference", "permission_namespace_version", "authorization_role_policy_version", "tenant_business_role_policy_version", "tenant_authorization_composition_version", "idempotency_key"])
def test_required_text_fail_closed(field):
    for bad in (None, "", "   ", 7):
        with pytest.raises(TenantAuthorizationDecisionEvidenceError): make(**{field: bad})


def test_text_preserved_and_generic():
    value = make(operation=" profile_update ", permission="unknown:permission", subject_reference="  subject  ")
    assert value.operation == " profile_update "
    assert value.subject_reference == "  subject  "


@pytest.mark.parametrize("field", ["membership_revision", "role_assignment_revision"])
def test_revisions_nonnegative_int(field):
    for bad in (-1, True, "0"):
        with pytest.raises(TenantAuthorizationDecisionEvidenceError): make(**{field: bad})


def test_subject_fingerprint_lowercase_sha3():
    with pytest.raises(TenantAuthorizationDecisionEvidenceError): make(subject_evidence_fingerprint="A" * 128)
    with pytest.raises(TenantAuthorizationDecisionEvidenceError): make(subject_evidence_fingerprint="a" * 127)


def test_timestamp_is_aware_and_supplied():
    make(authorized_at=datetime(2026, 9, 4, tzinfo=timezone.utc))
    with pytest.raises(TenantAuthorizationDecisionEvidenceError): make(authorized_at=datetime(2026, 9, 4))
    data = make().to_persisted(); data.pop("authorized_at")
    with pytest.raises(TenantAuthorizationDecisionEvidenceError): TenantAuthorizationDecisionEvidence.from_persisted(data)


@pytest.mark.parametrize("bad", ["abc:def", "abc\ndef", "abc\rdef", "abc\tdef", "abc\x00def", "abc\x1fdef", "abc\x7fdef", "abc\x85def", " decision-1"])
def test_decision_reference_atom_rejects_injection(bad):
    with pytest.raises(TenantAuthorizationDecisionEvidenceError): make(authorization_decision_id=bad)


def test_equivalent_instants_are_canonical_and_different_instant_changes():
    a = make(authorized_at=datetime.fromisoformat("2026-09-04T08:00:00+00:00"))
    b = make(authorized_at=datetime.fromisoformat("2026-09-04T10:00:00+02:00"))
    assert a.authorized_at == b.authorized_at
    assert a.evidence_payload() == b.evidence_payload()
    assert a.authorization_basis_reference == b.authorization_basis_reference
    assert a.authorization_evidence_fingerprint == b.authorization_evidence_fingerprint
    assert make(authorized_at=datetime.fromisoformat("2026-09-04T08:00:01+00:00")).authorization_evidence_fingerprint != a.authorization_evidence_fingerprint


def test_basis_is_structured_and_excludes_subject_identity():
    value = make()
    basis = value.authorization_basis_payload()
    assert basis["schema"] == "WILSY-TENANT-AUTHORIZATION-BASIS/V1"
    assert "subject_reference" not in basis and "authorization_decision_id" not in basis
    assert value.authorization_basis_reference.startswith("tenant-authorization-basis:sha3-512:")
    assert len(value.authorization_basis_reference.rsplit(":", 1)[1]) == 128


def test_deterministic_payload_and_fingerprint():
    assert make().evidence_payload() == make().evidence_payload()
    assert make().authorization_evidence_fingerprint == make().authorization_evidence_fingerprint
    assert make(authorization_decision_id="decision-2").authorization_evidence_fingerprint != make().authorization_evidence_fingerprint


def test_persisted_round_trip_and_strict_shape():
    value = make(); persisted = value.to_persisted()
    assert TenantAuthorizationDecisionEvidence.from_persisted(persisted) == value
    with pytest.raises(TenantAuthorizationDecisionEvidenceError): TenantAuthorizationDecisionEvidence.from_persisted({**persisted, "extra": 1})
    with pytest.raises(TenantAuthorizationDecisionEvidenceError): TenantAuthorizationDecisionEvidence.from_persisted({**persisted, "schema": "bad"})
    with pytest.raises(TenantAuthorizationDecisionEvidenceError): TenantAuthorizationDecisionEvidence.from_persisted({**persisted, "authorization_evidence_fingerprint": "b" * 128})
    with pytest.raises(TenantAuthorizationDecisionEvidenceError): TenantAuthorizationDecisionEvidence.from_persisted({**persisted, "authorized_at": "2026-09-04T10:00:00+02:00"})
    with pytest.raises(TenantAuthorizationDecisionEvidenceError): TenantAuthorizationDecisionEvidence.from_persisted({**persisted, "authorized_at": STAMP})
    with pytest.raises(TenantAuthorizationDecisionEvidenceError): TenantAuthorizationDecisionEvidence.from_persisted({**persisted, "authorized_at": "2026-09-04T12:00:00+00:00"})
    with pytest.raises(TenantAuthorizationDecisionEvidenceError): TenantAuthorizationDecisionEvidence.from_persisted({**persisted, "authorized_at": "2026-09-04T12:00:00Z"})
    with pytest.raises(TenantAuthorizationDecisionEvidenceError): TenantAuthorizationDecisionEvidence.from_persisted({**persisted, "authorized_at": "2026-09-04T12:00:00"})
    with pytest.raises(TenantAuthorizationDecisionEvidenceError): TenantAuthorizationDecisionEvidence.from_persisted({**persisted, "_id": "mongo"})


def test_subject_policy_and_idempotency_sensitivity():
    base = make()
    subject = make(subject_reference="tenant-profile:tenant-2", subject_evidence_fingerprint="b" * 128)
    assert subject.authorization_basis_reference == base.authorization_basis_reference
    assert subject.authorization_evidence_fingerprint != base.authorization_evidence_fingerprint
    for field in ("permission_namespace_version", "authorization_role_policy_version", "tenant_business_role_policy_version", "tenant_authorization_composition_version"):
        changed = make(**{field: "v2"})
        assert changed.authorization_basis_reference != base.authorization_basis_reference
        assert changed.authorization_evidence_fingerprint != base.authorization_evidence_fingerprint
    idem = make(idempotency_key="idem-2")
    assert idem.authorization_basis_reference == base.authorization_basis_reference
    assert idem.authorization_evidence_fingerprint != base.authorization_evidence_fingerprint


def test_r3c1_provenance_values_and_no_authority_imports():
    value = make()
    assert value.authorization_evidence_reference
    assert value.authorization_evidence_fingerprint == hashlib.sha3_512(json.dumps(value.evidence_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()
    assert "billing" not in __import__("tools.eos.auth.tenant_authorization_decision_evidence", fromlist=["x"]).__file__
    assert not hasattr(value, "execute") and not hasattr(value, "authorize")


# ARTIFACT: test_tenant_authorization_decision_evidence.py
# VERSION: v1.0.0-TENANT-AUTHORIZATION-DECISION-EVIDENCE-CERT
# AUTHORITY BOUNDARY: direct evidence-shape certification only; no authority grant.
# TENANT POSTURE: explicit tenant-scoped inputs; no cross-tenant inference.
# EVIDENCE POSTURE: provenance is supplied and deterministically fingerprinted.
# FAIL-CLOSED POSTURE: malformed and corrupted evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
