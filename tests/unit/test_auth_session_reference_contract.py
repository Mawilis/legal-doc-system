"""
TITLE: Canonical Authentication Session Reference Contract Certificate
VERSION: v1.0.0-P3-R3G-S5-A2-SESSION-REFERENCE-CONTRACT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies that the canonical authentication Session model preserves the
         durable session reference already generated and persisted by AuthRegistry,
         while retaining backward compatibility for generic legacy Session construction.
CERTIFICATION / UPDATE DATE: 2026-10-18
SECURITY / PRIVACY POSTURE: Session reference is opaque correlation identity only;
                            no bearer secret, credential, role, or privilege is created.
TENANT BOUNDARY: No tenant authority is created by this model field.
AUTHORITY BOUNDARY: Session identity representation only; AuthRegistry remains the
                    creation/persistence authority and factor currentness remains separate.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive financial execution authority.
"""

from __future__ import annotations

from datetime import datetime, timezone

from tools.eos.saas.domain.auth import Session


def _base(**changes: object) -> Session:
    values: dict[str, object] = {
        "userId": "principal-session-cert",
        "token": "opaque-test-token",
        "expiresAt": datetime.now(timezone.utc),
        "tenantId": "tenant-session-cert",
        "role": "ATTORNEY",
        "permissions": ["legal_operations:matter_deadline:read"],
    }
    values.update(changes)
    return Session(**values)  # type: ignore[arg-type]


def test_session_preserves_canonical_session_reference() -> None:
    value = _base(
        sessionReference="WILSYSESSION-session-contract-cert"
    )

    assert (
        value.sessionReference
        == "WILSYSESSION-session-contract-cert"
    )

    dumped = value.model_dump()

    assert (
        dumped["sessionReference"]
        == "WILSYSESSION-session-contract-cert"
    )


def test_legacy_session_construction_remains_compatible() -> None:
    value = _base()

    assert value.sessionReference is None

    dumped = value.model_dump()

    assert "sessionReference" in dumped
    assert dumped["sessionReference"] is None


def test_session_reference_does_not_create_authority() -> None:
    value = _base(
        sessionReference="WILSYSESSION-authority-boundary"
    )

    assert value.role == "ATTORNEY"
    assert value.permissions == [
        "legal_operations:matter_deadline:read"
    ]
    session_reference = value.sessionReference

    assert isinstance(session_reference, str)
    assert session_reference.startswith(
        "WILSYSESSION-"
    )


# ARTIFACT: test_auth_session_reference_contract.py
# VERSION: v1.0.0-P3-R3G-S5-A2-SESSION-REFERENCE-CONTRACT
# AUTHORITY BOUNDARY: Representation/correlation only; no IAM authority issuance.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
