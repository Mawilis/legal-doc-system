"""WILSY OS JWT purpose and credential-revision provider certificate.

TITLE: WILSY OS JWT Purpose/Credential Revision Direct Certificate
VERSION: v1.2.0-R10C2F9B-JWT-PROVIDER-CERT-DURABLE-COMPARISON-RECONCILIATION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the additive provider contract for ACCESS/PRE_AUTH purpose
         and bounded credential-revision claims without activating persistence
         comparison or changing any issuer caller.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_jwt_provider_credential_revision.py
COLLABORATION / OWNERSHIP: Test-only evidence; jwt_provider is the sole
                           production artifact exercised by this certificate.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.2.0-R10C2F9B-JWT-PROVIDER-CERT-DURABLE-COMPARISON-RECONCILIATION — Preserves
    the original F5 provider-claim tests while reconciling the later F8R/F9
    topology: the provider remains structural-only, authentication owns fresh
    durable revision comparison, and the router remains explicit PRE_AUTH.
  v1.0.0-R10C2F5-JWT-PURPOSE-CREDENTIAL-REVISION-CERT — Adds direct coverage
    for purpose values, revision boundaries, legacy compatibility, adversarial
    signed claims, signature/expiry behavior, privacy, and authority limits.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic in-memory secrets and claims only; test
                            diagnostics never print bearer or signing values.
TENANT BOUNDARY: Synthetic tenant claims are structural projections only.
AUTHORITY BOUNDARY: JWT signing and structural verification only; no durable
                    identity, revision, session, recovery, or route authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusively financial.
"""

from __future__ import annotations

import ast
import base64
import hashlib
import hmac
import inspect
import json
import os
import pathlib
import time
from typing import Any

import pytest

from tools.eos.auth import jwt_provider


SECRET = "r10c2f5-synthetic-signing-secret"
IDENTITY = "R10C2F5-identity"
TENANT = "R10C2F5-tenant"
BASE = {"identity_id": IDENTITY, "tenant_id": TENANT, "roles": [], "permissions": []}


@pytest.fixture(autouse=True)
def _signing_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WILSY_JWT_SECRET", SECRET)


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _signed_payload(payload: dict[str, Any]) -> str:
    """Create adversarial HS256 input without using the production issuer."""
    header = _encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":"), sort_keys=True).encode())
    body = _encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode())
    signing_input = f"{header}.{body}"
    signature = _encode(hmac.new(SECRET.encode(), signing_input.encode(), hashlib.sha256).digest())
    return f"{signing_input}.{signature}"


def _payload_without(**changes: Any) -> dict[str, Any]:
    now = int(time.time())
    payload = {**BASE, "iat": now, "exp": now + 60}
    payload.update(changes)
    return payload


def test_certificate_identity_and_api_are_frozen() -> None:
    assert jwt_provider.VERSION == "v1.3.0-R10C2F4-JWT-PURPOSE-CREDENTIAL-REVISION-CONTRACT"
    assert tuple(p.name for p in jwt_provider.TokenPurpose) == ("ACCESS", "PRE_AUTH")
    assert {p.value for p in jwt_provider.TokenPurpose} == {"ACCESS", "PRE_AUTH"}
    signature = inspect.signature(jwt_provider.create_access_token)
    assert str(signature) == "(identity_data: Dict[str, Any], expires_in_seconds: int = 86400, *, token_purpose: tools.eos.auth.jwt_provider.TokenPurpose | str | None = None, credential_revision: int | None = None) -> str"
    assert str(inspect.signature(jwt_provider.verify_access_token)) == "(token: str) -> Dict[str, Any] | None"


def test_legacy_issuance_and_verification_remain_compatible() -> None:
    token = jwt_provider.create_access_token(BASE)
    payload = jwt_provider.verify_access_token(token)
    assert payload is not None
    assert "token_purpose" not in payload
    assert "credential_revision" not in payload


@pytest.mark.parametrize("revision", [0, 17, jwt_provider.CREDENTIAL_REVISION_MAX])
def test_access_revision_shapes_round_trip_exactly(revision: int) -> None:
    token = jwt_provider.create_access_token(
        BASE,
        token_purpose=jwt_provider.TokenPurpose.ACCESS,
        credential_revision=revision,
    )
    payload = jwt_provider.verify_access_token(token)
    assert payload is not None
    assert payload["token_purpose"] == "ACCESS"
    assert payload["credential_revision"] == revision
    assert isinstance(payload["credential_revision"], int)


def test_pre_auth_without_revision_is_supported() -> None:
    token = jwt_provider.create_access_token(BASE, token_purpose=jwt_provider.TokenPurpose.PRE_AUTH)
    payload = jwt_provider.verify_access_token(token)
    assert payload is not None
    assert payload["token_purpose"] == "PRE_AUTH"
    assert "credential_revision" not in payload


@pytest.mark.parametrize("purpose", ["UNKNOWN", "", True, 1, object()])
def test_invalid_explicit_purpose_is_rejected(purpose: Any) -> None:
    with pytest.raises((TypeError, ValueError)):
        jwt_provider.create_access_token(BASE, token_purpose=purpose)


@pytest.mark.parametrize(
    "revision",
    [True, False, -1, 1.5, "0", "wrong", [], {}, jwt_provider.CREDENTIAL_REVISION_MAX + 1],
)
def test_invalid_explicit_revision_is_rejected(revision: Any) -> None:
    with pytest.raises((TypeError, ValueError)):
        jwt_provider.create_access_token(BASE, credential_revision=revision)


@pytest.mark.parametrize("purpose", ["UNKNOWN", "", True, 1, [], {}])
def test_malformed_present_signed_purpose_is_rejected(purpose: Any) -> None:
    assert jwt_provider.verify_access_token(_signed_payload(_payload_without(token_purpose=purpose))) is None


@pytest.mark.parametrize(
    "revision",
    [None, True, False, -1, 1.5, "0", "wrong", [], {}, jwt_provider.CREDENTIAL_REVISION_MAX + 1],
)
def test_malformed_present_signed_revision_is_rejected(revision: Any) -> None:
    assert jwt_provider.verify_access_token(_signed_payload(_payload_without(credential_revision=revision))) is None


@pytest.mark.parametrize("claim", ["identity_id", "tenant_id", "iat", "exp"])
def test_base_required_claims_remain_required(claim: str) -> None:
    payload = _payload_without()
    payload.pop(claim)
    assert jwt_provider.verify_access_token(_signed_payload(payload)) is None


def test_expiry_and_signature_contract_remain_hs256() -> None:
    expired = _payload_without(exp=int(time.time()) - 1)
    assert jwt_provider.verify_access_token(_signed_payload(expired)) is None
    fresh = jwt_provider.create_access_token(BASE)
    assert jwt_provider.verify_access_token(fresh) is not None
    assert jwt_provider.verify_access_token(fresh[:-1] + ("A" if fresh[-1] != "A" else "B")) is None
    header = json.loads(base64.urlsafe_b64decode(fresh.split(".")[0] + "=="))
    assert header == {"alg": "HS256", "typ": "JWT"}


def test_default_lifetime_and_relationship_compatibility() -> None:
    before = int(time.time())
    payload = jwt_provider.verify_access_token(jwt_provider.create_access_token(BASE))
    assert payload is not None
    assert 86400 <= payload["exp"] - payload["iat"] <= 86400
    assert payload["iat"] >= before
    access_without_revision = jwt_provider.create_access_token(BASE, token_purpose="ACCESS")
    assert jwt_provider.verify_access_token(access_without_revision) is not None
    pre_auth_with_revision = jwt_provider.create_access_token(
        BASE, token_purpose="PRE_AUTH", credential_revision=0
    )
    assert jwt_provider.verify_access_token(pre_auth_with_revision) is not None


def test_no_purpose_inference_and_privacy_safe_failures() -> None:
    for roles, permissions in [(["ACCESS"], []), ([], ["ACCESS"]), (["PRE_AUTH"], ["ACCESS"])]:
        token = jwt_provider.create_access_token({**BASE, "roles": roles, "permissions": permissions})
        payload = jwt_provider.verify_access_token(token)
        assert payload is not None
        assert "token_purpose" not in payload

    sentinel_token = "SYNTHETIC-BEARER-SENTINEL"
    assert jwt_provider.verify_access_token(sentinel_token) is None
    assert sentinel_token not in repr(jwt_provider.verify_access_token(sentinel_token))
    with pytest.raises(RuntimeError) as error:
        os.environ.pop("WILSY_JWT_SECRET", None)
        jwt_provider.create_access_token(BASE)
    assert SECRET not in str(error.value)


def test_provider_has_no_persistence_or_adjacent_authority() -> None:
    path = pathlib.Path(jwt_provider.__file__)
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        node.names[0].name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import) and node.names
    }
    imported.update(
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    )
    forbidden = {"pymongo", "motor", "AuthRegistry", "PrincipalAuthority", "fastapi", "httpx"}
    assert not imported.intersection(forbidden)
    for forbidden_text in ("MongoClient", "get_current_identity", "PrincipalAuthorityRepository", "start_transaction", "commit_transaction"):
        assert forbidden_text not in source
    assert "credential_revision" in source
    assert "token_purpose" in source


def test_provider_remains_structural_while_authentication_enforces_durable_revision() -> None:
    registry_source = pathlib.Path("tools/eos/saas/auth/auth_registry.py").read_text(encoding="utf-8")
    router_source = pathlib.Path("tools/eos/api/auth_router.py").read_text(encoding="utf-8")
    authentication_source = pathlib.Path("tools/eos/auth/authentication.py").read_text(encoding="utf-8")
    provider_source = pathlib.Path(jwt_provider.__file__).read_text(encoding="utf-8")
    router_tree = ast.parse(router_source)
    router_call_sites = [
        node.func.attr
        for node in ast.walk(router_tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {
            "generate_jwt",
            "generate_pre_auth_jwt",
            "generate_access_jwt",
        }
    ]
    assert "create_access_token" in registry_source
    assert router_call_sites.count("generate_jwt") == 0
    assert router_call_sites.count("generate_pre_auth_jwt") == 3
    assert router_call_sites.count("generate_access_jwt") == 0
    assert "get_credential_revision" not in provider_source
    assert "get_credential_revision" in authentication_source
    assert "credential_revision" in authentication_source
    assert "token_revision != durable_revision" in authentication_source


def test_certificate_self_identity() -> None:
    path = pathlib.Path(__file__)
    source = path.read_text(encoding="utf-8")
    version = "v1.2.0-R10C2F9B-JWT-PROVIDER-CERT-DURABLE-COMPARISON-RECONCILIATION"
    assert source.count(version) == 4
    assert "ABSOLUTE CANONICAL PATH" in source
    assert "CHANGELOG:" in source
    assert "END OF WILSY OS SOVEREIGN ARTIFACT" in source
    assert hashlib.sha3_512(path.read_bytes()).hexdigest()


# ARTIFACT: test_jwt_provider_credential_revision.py
# VERSION: v1.2.0-R10C2F9B-JWT-PROVIDER-CERT-DURABLE-COMPARISON-RECONCILIATION
# AUTHORITY BOUNDARY: direct provider contract evidence only.
# TENANT POSTURE: synthetic claims; no durable tenant authority.
# FAIL-CLOSED POSTURE: malformed signed claims and invalid inputs are rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
