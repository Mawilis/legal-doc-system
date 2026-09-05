"""WILSY OS — PRE-TENANT BOOTSTRAP AUTHORITY CERTIFICATE

TITLE: Direct certificate for deployment-rooted provisioner verification
VERSION: v1.0.0-WILSY-PRETENANT-BOOTSTRAP-AUTHORITY
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify the bounded, reusable pre-tenant authority contract.
EPITOME: Executable evidence that only an authenticated, configured principal
may enter tenant-owner bootstrap; this certificate grants no authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_pretenant_bootstrap_authority.py
COLLABORATION / OWNERSHIP: Auth-domain certificate consumed by architecture review.
SECURITY / PRIVACY POSTURE: Synthetic identities only; no configuration leakage.
TENANT BOUNDARY: Tenant projection is ignored for this non-tenant authority.
AUTHORITY BOUNDARY: Verification evidence only; no tenant creation or administration.
FINANCIAL BOUNDARY: No financial or Kennel authority.
TRANSACTION BOUNDARY: Pure in-memory tests; no database or transaction.
CERTIFICATION / UPDATE DATE: 2026-09-05
CHANGELOG: v1.0.0-WILSY-PRETENANT-BOOTSTRAP-AUTHORITY — initial direct certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
import inspect
import json
from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.pretenant_bootstrap_authority import (
    AUTHORITY_SOURCE_ID,
    TENANT_OWNER_BOOTSTRAP_OPERATION,
    PretenantBootstrapAuthorityDenialCode,
    PretenantBootstrapAuthorityError,
    PretenantBootstrapAuthorityEvidence,
    VERSION,
    verify_pretenant_bootstrap_authority,
)

CONFIG = "WILSY_PRETENANT_TENANT_PROVISIONER_PRINCIPAL_IDS"


def identity(principal: str = "synthetic-provisioner", *, roles: list[str] | None = None, permissions: list[str] | None = None, tenant_id: str = "ignored") -> SovereignIdentity:
    return SovereignIdentity(identity_id=principal, tenant_id=tenant_id, username=None, email=None, auth_method="test", status=PrincipalStatus.ACTIVE, roles=roles or [], permissions=permissions or [])


def denied(monkeypatch: pytest.MonkeyPatch, raw: object, expected: PretenantBootstrapAuthorityDenialCode) -> None:
    if raw is None:
        monkeypatch.delenv(CONFIG, raising=False)
    else:
        monkeypatch.setenv(CONFIG, raw if isinstance(raw, str) else str(raw))
    with pytest.raises(PretenantBootstrapAuthorityError) as exc:
        verify_pretenant_bootstrap_authority(identity())
    assert exc.value.code is expected
    assert "synthetic-provisioner" not in str(exc.value)


def test_root_01_valid_and_evidence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(CONFIG, json.dumps(["synthetic-provisioner"]))
    result = verify_pretenant_bootstrap_authority(identity())
    assert result == PretenantBootstrapAuthorityEvidence("synthetic-provisioner", TENANT_OWNER_BOOTSTRAP_OPERATION, AUTHORITY_SOURCE_ID)


def test_root_02_non_provisioner(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(CONFIG, '["other"]')
    with pytest.raises(PretenantBootstrapAuthorityError) as exc: verify_pretenant_bootstrap_authority(identity())
    assert exc.value.code is PretenantBootstrapAuthorityDenialCode.PRINCIPAL_NOT_PROVISIONER


@pytest.mark.parametrize("raw", [None, "", "   ", "[]"])
def test_root_03_missing_or_empty(monkeypatch: pytest.MonkeyPatch, raw: object) -> None:
    denied(monkeypatch, raw, PretenantBootstrapAuthorityDenialCode.MISSING_TRUSTED_AUTHORITY)


@pytest.mark.parametrize("raw", ["{", "{}", "1", "null", '[1]', '[" "]', '["*"]', '["a", "a"]', '["a", " a "]', '["a\\n"]'])
def test_root_04_malformed_config(monkeypatch: pytest.MonkeyPatch, raw: str) -> None:
    denied(monkeypatch, raw, PretenantBootstrapAuthorityDenialCode.MALFORMED_TRUST_CONFIG)


def test_root_05_whitespace_case_and_reuse(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(CONFIG, '[" synthetic-provisioner "]')
    assert verify_pretenant_bootstrap_authority(identity()).principal_id == "synthetic-provisioner"
    assert verify_pretenant_bootstrap_authority(identity(roles=["administrator"], permissions=["root"], tenant_id="forged")).principal_id == "synthetic-provisioner"
    monkeypatch.setenv(CONFIG, '["SYNTHETIC-PROVISIONER"]')
    with pytest.raises(PretenantBootstrapAuthorityError): verify_pretenant_bootstrap_authority(identity())


def test_root_06_immutability_and_public_signature() -> None:
    evidence = PretenantBootstrapAuthorityEvidence("p", TENANT_OWNER_BOOTSTRAP_OPERATION, AUTHORITY_SOURCE_ID)
    with pytest.raises(FrozenInstanceError): setattr(evidence, "principal_id", "x")
    assert list(inspect.signature(verify_pretenant_bootstrap_authority).parameters) == ["identity"]
    assert VERSION == "v1.0.0-WILSY-PRETENANT-BOOTSTRAP-AUTHORITY"
    assert CONFIG == "WILSY_PRETENANT_TENANT_PROVISIONER_PRINCIPAL_IDS"


def test_root_07_identity_and_scope_boundaries(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(CONFIG, '["synthetic-provisioner"]')
    malformed: Any = {"identity_id": "synthetic-provisioner"}
    with pytest.raises(PretenantBootstrapAuthorityError) as exc: verify_pretenant_bootstrap_authority(malformed)
    assert exc.value.code is PretenantBootstrapAuthorityDenialCode.MALFORMED_IDENTITY
    assert "Mongo" not in inspect.getsource(verify_pretenant_bootstrap_authority)


# ARTIFACT: test_pretenant_bootstrap_authority.py
# VERSION: v1.0.0-WILSY-PRETENANT-BOOTSTRAP-AUTHORITY
# AUTHORITY BOUNDARY: Direct verification certificate only; no authority grant.
# TENANT POSTURE: Tenant projection cannot authorize pre-tenant bootstrap.
# FAIL-CLOSED POSTURE: Invalid identity/configuration denies deterministically.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
