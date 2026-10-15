"""TITLE: D11-R5 signed bootstrap creation authorization certificate.
VERSION: v1.0.0-P4-R4-D11-R5-AUTHORIZATION-CERTIFICATE
AUTHORITY: Direct Ed25519 integrity, currentness, and closed-purpose proof.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_system_permission_bootstrap_creation_authorization.py
CERTIFICATION DATE: 2026-10-14
CHANGELOG: v1.0.0 proves signature-before-semantic-claim ordering.
BOUNDARY: No assignment, activation, break-glass, or finance.
"""
from __future__ import annotations

import base64
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.eos.auth.system_permission_bootstrap_creation_authorization import (
    SystemPermissionBootstrapCreationAuthorization,
    SystemPermissionBootstrapCreationAuthorizationError,
    VerifiedSystemPermissionBootstrapCreationAuthorization,
    verify_system_permission_bootstrap_creation_authorization,
)
from tools.eos.auth.system_permission_bootstrap_creation_trust import (
    OPERATION,
    SCOPE,
    SystemPermissionBootstrapCreationTrustedKey,
    SystemPermissionBootstrapCreationTrustRoot,
    SystemPermissionBootstrapCreationTrustStatus,
)

NOW = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc)
ASSIGN_PURPOSE = "SEED_SYSTEM_PERMISSION_ASSIGNMENT_COMMAND_AUTHORITY"
REVOKE_PURPOSE = "SEED_SYSTEM_PERMISSION_REVOCATION_COMMAND_AUTHORITY"


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _fixture(
    *,
    purpose: str = ASSIGN_PURPOSE,
    status: SystemPermissionBootstrapCreationTrustStatus = SystemPermissionBootstrapCreationTrustStatus.ACTIVE,
    issued_at: datetime = NOW - timedelta(minutes=1),
    expires_at: datetime = NOW + timedelta(minutes=10),
) -> tuple[SystemPermissionBootstrapCreationAuthorization, SystemPermissionBootstrapCreationTrustRoot]:
    private = Ed25519PrivateKey.generate()
    public = _b64(
        private.public_key().public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw,
        )
    )
    key = SystemPermissionBootstrapCreationTrustedKey.create(
        creator_principal_id="principal-creator",
        public_key_base64url=public,
        valid_from=NOW - timedelta(hours=1),
        valid_until=NOW + timedelta(hours=1),
        status=status,
        revision=1,
        provenance="installation-ceremony:evidence-1",
    )
    unsigned = SystemPermissionBootstrapCreationAuthorization(
        operation=OPERATION,
        scope=SCOPE,
        creator_principal_id="principal-creator",
        target_principal_id="principal-target",
        bootstrap_id="bootstrap-1",
        bootstrap_purpose=purpose,
        evidence_reference="evidence:create-1",
        key_id=key.key_id,
        trust_fingerprint=key.trust_fingerprint,
        issued_at=issued_at,
        expires_at=expires_at,
        nonce="nonce-1",
        idempotency_key="idem-1",
        signature_base64url=_b64(bytes(64)),
    )
    signed = replace(unsigned, signature_base64url=_b64(private.sign(unsigned.signed_payload())))
    return signed, SystemPermissionBootstrapCreationTrustRoot((key,))


@pytest.mark.parametrize("purpose", [ASSIGN_PURPOSE, REVOKE_PURPOSE])
def test_exact_valid_signature_and_both_closed_purposes(purpose: str) -> None:
    authorization, root = _fixture(purpose=purpose)
    verified = verify_system_permission_bootstrap_creation_authorization(
        authorization, root, now=NOW
    )
    assert isinstance(verified, VerifiedSystemPermissionBootstrapCreationAuthorization)
    assert verified.authorization.bootstrap_purpose == purpose


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("creator_principal_id", "different-creator"),
        ("target_principal_id", "different-target"),
        ("bootstrap_id", "bootstrap-2"),
        ("evidence_reference", "evidence:tampered"),
        ("bootstrap_purpose", REVOKE_PURPOSE),
    ],
)
def test_signed_binding_tamper_is_rejected_cryptographically(field: str, value: str) -> None:
    authorization, root = _fixture()
    with pytest.raises(SystemPermissionBootstrapCreationAuthorizationError, match="BOOTSTRAP_CREATION_SIGNATURE_INVALID"):
        verify_system_permission_bootstrap_creation_authorization(
            replace(authorization, **{field: value}), root, now=NOW
        )


def test_unknown_key_and_wrong_fingerprint_fail_before_signature() -> None:
    authorization, root = _fixture()
    with pytest.raises(SystemPermissionBootstrapCreationAuthorizationError, match="BOOTSTRAP_CREATION_KEY_UNKNOWN"):
        verify_system_permission_bootstrap_creation_authorization(
            replace(authorization, key_id="unknown-key"), root, now=NOW
        )
    with pytest.raises(SystemPermissionBootstrapCreationAuthorizationError, match="BOOTSTRAP_CREATION_TRUST_FINGERPRINT_INVALID"):
        verify_system_permission_bootstrap_creation_authorization(
            replace(authorization, trust_fingerprint="0" * 128), root, now=NOW
        )


@pytest.mark.parametrize(
    ("issued_at", "expires_at", "expected"),
    [
        (NOW - timedelta(minutes=20), NOW - timedelta(seconds=1), "BOOTSTRAP_CREATION_AUTHORIZATION_NOT_CURRENT"),
        (NOW + timedelta(seconds=1), NOW + timedelta(minutes=10), "BOOTSTRAP_CREATION_AUTHORIZATION_NOT_CURRENT"),
    ],
)
def test_authorization_time_window_fails_closed(
    issued_at: datetime,
    expires_at: datetime,
    expected: str,
) -> None:
    authorization, root = _fixture(issued_at=issued_at, expires_at=expires_at)
    with pytest.raises(SystemPermissionBootstrapCreationAuthorizationError, match=expected):
        verify_system_permission_bootstrap_creation_authorization(authorization, root, now=NOW)


@pytest.mark.parametrize(
    "status",
    [SystemPermissionBootstrapCreationTrustStatus.RETIRED, SystemPermissionBootstrapCreationTrustStatus.REVOKED],
)
def test_retired_and_revoked_trust_fail_after_signature(
    status: SystemPermissionBootstrapCreationTrustStatus,
) -> None:
    authorization, root = _fixture(status=status)
    with pytest.raises(SystemPermissionBootstrapCreationAuthorizationError, match="BOOTSTRAP_CREATION_TRUST_NOT_CURRENT_AT_ISSUANCE"):
        verify_system_permission_bootstrap_creation_authorization(authorization, root, now=NOW)


@pytest.mark.parametrize("purpose", ["privileged_activation:issue", "arbitrary_system_permission", "BREAK_GLASS", "financial:execute"])
def test_non_bootstrap_purposes_are_rejected(purpose: str) -> None:
    with pytest.raises(SystemPermissionBootstrapCreationAuthorizationError, match="BOOTSTRAP_PURPOSE_NOT_ALLOWED"):
        _fixture(purpose=purpose)


def test_lifetime_over_thirty_minutes_is_rejected() -> None:
    with pytest.raises(SystemPermissionBootstrapCreationAuthorizationError, match="BOOTSTRAP_CREATION_LIFETIME_INVALID"):
        _fixture(issued_at=NOW, expires_at=NOW + timedelta(minutes=30, microseconds=1))


def test_verified_wrapper_cannot_be_forged() -> None:
    authorization, root = _fixture()
    with pytest.raises(TypeError, match="requires verifier"):
        VerifiedSystemPermissionBootstrapCreationAuthorization(
            authorization, root.trusted_keys[0], NOW
        )


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_system_permission_bootstrap_creation_authorization.py
# VERSION: v1.0.0-P4-R4-D11-R5-AUTHORIZATION-CERTIFICATE
# POSTURE: COMPLETE PAYLOAD AUTHENTICATED BEFORE CLAIM AUTHORIZATION
# END OF WILSY OS SOVEREIGN ARTIFACT
