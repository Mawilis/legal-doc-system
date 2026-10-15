"""TITLE: D11-R5 bootstrap creation trust direct certificate.
VERSION: v1.0.0-P4-R4-D11-R5-TRUST-CERTIFICATE
AUTHORITY: Direct certification of source-owned Ed25519 bootstrap creation trust.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_system_permission_bootstrap_creation_trust.py
CERTIFICATION DATE: 2026-10-14
CHANGELOG: v1.0.0 establishes the frozen trust matrix.
BOUNDARY: No private keys, tenant roles, activation, break-glass, or finance.
"""
from __future__ import annotations

import base64
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.eos.auth.system_permission_bootstrap_creation_trust import (
    ALGORITHM,
    OPERATION,
    SCOPE,
    SystemPermissionBootstrapCreationTrustedKey,
    SystemPermissionBootstrapCreationTrustError,
    SystemPermissionBootstrapCreationTrustRoot,
    SystemPermissionBootstrapCreationTrustStatus,
)

NOW = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc)


def _encoded_public_key() -> str:
    raw = Ed25519PrivateKey.generate().public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _key(
    status: SystemPermissionBootstrapCreationTrustStatus = SystemPermissionBootstrapCreationTrustStatus.ACTIVE,
) -> SystemPermissionBootstrapCreationTrustedKey:
    return SystemPermissionBootstrapCreationTrustedKey.create(
        creator_principal_id="principal-creator",
        public_key_base64url=_encoded_public_key(),
        valid_from=NOW - timedelta(minutes=5),
        valid_until=NOW + timedelta(hours=1),
        status=status,
        revision=1,
        provenance="installation-ceremony:evidence-1",
    )


def test_exact_key_identity_fingerprint_and_resolution_are_deterministic() -> None:
    key = _key()
    assert key.key_id == SystemPermissionBootstrapCreationTrustedKey.derive_key_id(
        key.public_key_base64url
    )
    assert len(key.trust_fingerprint) == 128
    assert SystemPermissionBootstrapCreationTrustRoot((key,)).resolve(key.key_id) == key
    assert key.algorithm == ALGORITHM
    assert key.scope == SCOPE
    assert key.operation == OPERATION


def test_unknown_key_fails_closed() -> None:
    with pytest.raises(SystemPermissionBootstrapCreationTrustError, match="BOOTSTRAP_CREATION_KEY_UNKNOWN"):
        SystemPermissionBootstrapCreationTrustRoot((_key(),)).resolve("unknown-key")


@pytest.mark.parametrize(
    "status",
    [
        SystemPermissionBootstrapCreationTrustStatus.RETIRED,
        SystemPermissionBootstrapCreationTrustStatus.REVOKED,
    ],
)
def test_nonactive_key_cannot_issue(status: SystemPermissionBootstrapCreationTrustStatus) -> None:
    key = _key(status)
    assert not key.can_issue(
        creator_principal_id=key.creator_principal_id,
        operation=OPERATION,
        scope=SCOPE,
        at=NOW,
    )


def test_validity_window_is_start_inclusive_and_end_exclusive() -> None:
    key = _key()
    assert key.can_issue(
        creator_principal_id=key.creator_principal_id,
        operation=OPERATION,
        scope=SCOPE,
        at=key.valid_from,
    )
    assert not key.can_issue(
        creator_principal_id=key.creator_principal_id,
        operation=OPERATION,
        scope=SCOPE,
        at=key.valid_until,
    )


@pytest.mark.parametrize(
    ("creator", "operation", "scope"),
    [
        ("different-creator", OPERATION, SCOPE),
        ("principal-creator", "CREATE_OTHER_AUTHORITY", SCOPE),
        ("principal-creator", OPERATION, "TENANT"),
    ],
)
def test_creator_operation_and_scope_are_exact(
    creator: str,
    operation: str,
    scope: str,
) -> None:
    key = _key()
    assert not key.can_issue(
        creator_principal_id=creator,
        operation=operation,
        scope=scope,
        at=NOW,
    )


def test_fingerprint_tamper_and_wildcards_fail_closed() -> None:
    key = _key()
    with pytest.raises(SystemPermissionBootstrapCreationTrustError, match="TRUST_FINGERPRINT_INVALID"):
        replace(key, trust_fingerprint="0" * 128)
    with pytest.raises(SystemPermissionBootstrapCreationTrustError, match="CREATOR_PRINCIPAL_ID_INVALID"):
        SystemPermissionBootstrapCreationTrustedKey.create(
            creator_principal_id="*",
            public_key_base64url=_encoded_public_key(),
            valid_from=NOW,
            valid_until=NOW + timedelta(minutes=1),
            status=SystemPermissionBootstrapCreationTrustStatus.ACTIVE,
            revision=1,
            provenance="ceremony",
        )


def test_public_contract_exposes_no_private_or_broad_authority_surface() -> None:
    names = set(dir(SystemPermissionBootstrapCreationTrustedKey))
    assert not {"private_key", "sign", "assign", "activate", "break_glass", "execute_payment"} & names


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_system_permission_bootstrap_creation_trust.py
# VERSION: v1.0.0-P4-R4-D11-R5-TRUST-CERTIFICATE
# POSTURE: DIRECT TRUST MATRIX; NO PRIVATE OR BROAD AUTHORITY
# END OF WILSY OS SOVEREIGN ARTIFACT
