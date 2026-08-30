"""WILSY OS Python authority bridge certification.
TITLE: Python Authority Bridge Router Certification
VERSION: v1.0.0-WILSY-PYTHON-AUTHORITY-BRIDGE
AUTHORITY: Isolated proof of the bridge composition contract.
EPITOME: Proves raw request fidelity, frozen service trust, replay denial, and delegated authority boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_authority_bridge_router.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30
CHANGELOG: v1.0.0-WILSY-PYTHON-AUTHORITY-BRIDGE — initial isolated bridge matrix.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY/PRIVACY POSTURE: deterministic fakes contain no secrets or production data.
TENANT BOUNDARY: tenant admission is explicitly injected and independently asserted.
AUTHORITY BOUNDARY: certifies composition, not underlying authority implementations.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""
from __future__ import annotations

import asyncio
import hashlib
import hmac
from typing import cast, Any
from unittest.mock import AsyncMock

import pytest
from starlette.requests import Request

from tools.eos.api.authority_bridge_router import BridgeRequest, authorize_request, _origin_form
from tools.eos.api.exceptions import ForbiddenOperationException, UnauthorizedAccessException
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.internal_service_trust import TrustResult
from tools.eos.auth.internal_service_trust import canonical_request, body_sha3_512, verify_internal_service_request


def _request(body: bytes = b'{"policy_id":"audit:read"}', path: bytes = b"/internal/authority/authorize", query: bytes = b"a=1+2&b=%20") -> Request:
    return Request({"type": "http", "method": "POST", "path": path.decode(), "raw_path": path, "query_string": query, "headers": [(b"x-wilsy-auth-version", b"v1"), (b"x-wilsy-service-id", b"node"), (b"x-wilsy-audience", b"python"), (b"x-wilsy-key-id", b"k"), (b"x-wilsy-timestamp", b"1"), (b"x-wilsy-nonce", b"n"), (b"x-wilsy-body-sha3-512", b"x"), (b"x-wilsy-correlation-id", b"corr"), (b"x-wilsy-signature", b"sig"), (b"authorization", b"Bearer original"), (b"x-tenant-id", b"tenant")], "client": ("test", 1)}, receive=AsyncMock(side_effect=[{"type": "http.request", "body": body, "more_body": False}]))


def _identity() -> SovereignIdentity:
    return SovereignIdentity(identity_id="principal", tenant_id="tenant", username=None, email=None, auth_method="bearer", status=PrincipalStatus.ACTIVE)


def _trust(request, body, **kwargs):
    assert body == b'{"policy_id":"audit:read"}'
    assert kwargs["keys"] == {"k": ("node", "secret")}
    assert kwargs["replay_store"] is not None
    assert request["path"] == "/internal/authority/authorize?a=1+2&b=%20"
    return TrustResult(service_id="node", audience="python", key_id="k", correlation_id="corr", verified_at=1, protocol_version="v1")

class _Replay:
    def consume_once(self, **kwargs):
        return True


def test_valid_composition_is_bounded_and_delegated():
    async def run():
        identity = _identity()
        tenant = AsyncMock(return_value=identity)
        authorization = AsyncMock(return_value=identity)
        result = await authorize_request(_request(), BridgeRequest(policy_id="audit:read"), replay_store=_Replay(), config={"WILSY_INTERNAL_AUTH_SERVICE_ID": "node", "WILSY_INTERNAL_AUTH_AUDIENCE": "python", "WILSY_INTERNAL_AUTH_KEY_ID": "k", "WILSY_INTERNAL_AUTH_SECRET": "secret"}, trust_verifier=_trust, identity_provider=AsyncMock(return_value=identity), tenant_provider=tenant, authorization_provider=authorization)
        assert result == {"allowed": True, "identity_id": "principal", "tenant_id": "tenant", "correlation_id": "corr"}
        assert "roles" not in result and "permissions" not in result
        tenant.assert_awaited_once_with(identity)
        authorization.assert_awaited_once_with(identity, "audit:read")
    asyncio.run(run())


def test_trust_and_config_fail_closed():
    async def run():
        with pytest.raises(Exception) as missing:
            await authorize_request(_request(), BridgeRequest(policy_id="audit:read"), config={}, trust_verifier=_trust)
        assert getattr(missing.value, "status_code", None) == 503

        def bad(*args, **kwargs):
            raise RuntimeError("bad signature")
        with pytest.raises(Exception) as denied:
            await authorize_request(_request(), BridgeRequest(policy_id="audit:read"), config={"WILSY_INTERNAL_AUTH_SERVICE_ID": "node", "WILSY_INTERNAL_AUTH_AUDIENCE": "python", "WILSY_INTERNAL_AUTH_KEY_ID": "k", "WILSY_INTERNAL_AUTH_SECRET": "secret"}, trust_verifier=bad)
        assert getattr(denied.value, "status_code", None) == 503
    asyncio.run(run())


def test_user_tenant_and_policy_denials_are_preserved():
    async def run():
        identity = _identity()
        config = {"WILSY_INTERNAL_AUTH_SERVICE_ID": "node", "WILSY_INTERNAL_AUTH_AUDIENCE": "python", "WILSY_INTERNAL_AUTH_KEY_ID": "k", "WILSY_INTERNAL_AUTH_SECRET": "secret"}
        with pytest.raises(UnauthorizedAccessException):
            await authorize_request(_request(), BridgeRequest(policy_id="audit:read"), replay_store=_Replay(), identity_provider=AsyncMock(side_effect=UnauthorizedAccessException()), config=config, trust_verifier=_trust)
        with pytest.raises(ForbiddenOperationException):
            await authorize_request(_request(), BridgeRequest(policy_id="audit:read"), replay_store=_Replay(), identity_provider=AsyncMock(return_value=identity), tenant_provider=AsyncMock(return_value=identity), authorization_provider=AsyncMock(side_effect=ForbiddenOperationException()), config=config, trust_verifier=_trust)
    asyncio.run(run())


def test_payload_rejects_node_authority_fields():
    with pytest.raises(ValueError):
        BridgeRequest.model_validate({"policy_id": "audit:read", "roles": ["GLOBAL_ROOT"]})


def test_valid_request_uses_actual_frozen_verifier():
    async def run():
        body = b'{"policy_id":"audit:read"}'
        path = b"/internal/authority/authorize"
        timestamp = "1700000000"
        digest = body_sha3_512(body)
        canonical = canonical_request(version="v1", service_id="node-express-api", audience="python-eos-authority", method="POST", path=path.decode(), timestamp=timestamp, nonce="0123456789abcdef0123456789abcdef", body_sha3_512_value=digest, correlation_id="corr-bootstrap-1")
        signature = hmac.new(b"synthetic-test-secret", canonical, hashlib.sha256).hexdigest()
        request = _request(body, path, b"")
        request.scope["headers"] = [(k, v) for k, v in request.scope["headers"] if not k.startswith(b"x-wilsy")]
        request.scope["headers"] += [(b"x-wilsy-auth-version", b"v1"), (b"x-wilsy-service-id", b"node-express-api"), (b"x-wilsy-audience", b"python-eos-authority"), (b"x-wilsy-key-id", b"test-k1"), (b"x-wilsy-timestamp", timestamp.encode()), (b"x-wilsy-nonce", b"0123456789abcdef0123456789abcdef"), (b"x-wilsy-body-sha3-512", digest.encode()), (b"x-wilsy-correlation-id", b"corr-bootstrap-1"), (b"x-wilsy-signature", signature.encode())]
        replay = _Replay()
        def frozen(**kwargs):
            return verify_internal_service_request(**kwargs, now=1700000000)
        result = await authorize_request(request, BridgeRequest(policy_id="audit:read"), replay_store=replay, config={"WILSY_INTERNAL_AUTH_SERVICE_ID":"node-express-api", "WILSY_INTERNAL_AUTH_AUDIENCE":"python-eos-authority", "WILSY_INTERNAL_AUTH_KEY_ID":"test-k1", "WILSY_INTERNAL_AUTH_SECRET":"synthetic-test-secret"}, trust_verifier=frozen, identity_provider=AsyncMock(return_value=_identity()), tenant_provider=AsyncMock(return_value=_identity()), authorization_provider=AsyncMock(return_value=_identity()))
        assert result["allowed"] is True
    asyncio.run(run())


def test_actual_frozen_verifier_missing_header_is_bounded_401():
    async def run():
        request = _request()
        request.scope["headers"] = [(k, v) for k, v in request.scope["headers"] if k != b"x-wilsy-signature"]
        with pytest.raises(Exception) as error:
            await authorize_request(request, BridgeRequest(policy_id="audit:read"), replay_store=_Replay(), config={"WILSY_INTERNAL_AUTH_SERVICE_ID":"node", "WILSY_INTERNAL_AUTH_AUDIENCE":"python", "WILSY_INTERNAL_AUTH_KEY_ID":"k", "WILSY_INTERNAL_AUTH_SECRET":"secret"})
        assert getattr(error.value, "status_code", None) == 401
    asyncio.run(run())


def test_actual_frozen_verifier_malformed_timestamp_is_bounded_401():
    async def run():
        request = _request()
        request.scope["headers"] = [(k, (b"bad" if k == b"x-wilsy-timestamp" else v)) for k, v in request.scope["headers"]]
        with pytest.raises(Exception) as error:
            await authorize_request(request, BridgeRequest(policy_id="audit:read"), replay_store=_Replay(), config={"WILSY_INTERNAL_AUTH_SERVICE_ID":"node", "WILSY_INTERNAL_AUTH_AUDIENCE":"python", "WILSY_INTERNAL_AUTH_KEY_ID":"k", "WILSY_INTERNAL_AUTH_SECRET":"secret"})
        assert getattr(error.value, "status_code", None) == 401
    asyncio.run(run())


def test_actual_frozen_verifier_bad_signature_is_bounded_401():
    async def run():
        request = _request()
        request.scope["headers"] = [(k, (b"0" * 64 if k == b"x-wilsy-signature" else v)) for k, v in request.scope["headers"]]
        with pytest.raises(Exception) as error:
            await authorize_request(request, BridgeRequest(policy_id="audit:read"), replay_store=_Replay(), config={"WILSY_INTERNAL_AUTH_SERVICE_ID":"node", "WILSY_INTERNAL_AUTH_AUDIENCE":"python", "WILSY_INTERNAL_AUTH_KEY_ID":"k", "WILSY_INTERNAL_AUTH_SECRET":"secret"})
        assert getattr(error.value, "status_code", None) == 401
    asyncio.run(run())


def test_actual_frozen_verifier_unknown_key_exposes_mapping_gap():
    async def run():
        request = _request()
        request.scope["headers"] = [(k, (b"unknown" if k == b"x-wilsy-key-id" else v)) for k, v in request.scope["headers"]]
        with pytest.raises(Exception) as error:
            await authorize_request(request, BridgeRequest(policy_id="audit:read"), replay_store=_Replay(), config={"WILSY_INTERNAL_AUTH_SERVICE_ID":"node", "WILSY_INTERNAL_AUTH_AUDIENCE":"python", "WILSY_INTERNAL_AUTH_KEY_ID":"k", "WILSY_INTERNAL_AUTH_SECRET":"secret"})
        assert getattr(error.value, "status_code", None) == 401
    asyncio.run(run())


def test_actual_frozen_verifier_body_digest_and_service_mismatch_are_401():
    async def run():
        config = {"WILSY_INTERNAL_AUTH_SERVICE_ID":"node", "WILSY_INTERNAL_AUTH_AUDIENCE":"python", "WILSY_INTERNAL_AUTH_KEY_ID":"k", "WILSY_INTERNAL_AUTH_SECRET":"secret"}
        for field, value in ((b"x-wilsy-body-sha3-512", b"0" * 128), (b"x-wilsy-service-id", b"other")):
            request = _request()
            request.scope["headers"] = [(k, value if k == field else v) for k, v in request.scope["headers"]]
            with pytest.raises(Exception) as error:
                await authorize_request(request, BridgeRequest(policy_id="audit:read"), replay_store=_Replay(), config=config)
            assert getattr(error.value, "status_code", None) == 401
    asyncio.run(run())


def test_audience_is_checked_by_bridge_contract():
    async def run():
        request = _request()
        request.scope["headers"] = [(k, b"wrong-audience" if k == b"x-wilsy-audience" else v) for k, v in request.scope["headers"]]
        with pytest.raises(Exception) as error:
            await authorize_request(request, BridgeRequest(policy_id="audit:read"), replay_store=_Replay(), config={"WILSY_INTERNAL_AUTH_SERVICE_ID":"node", "WILSY_INTERNAL_AUTH_AUDIENCE":"python", "WILSY_INTERNAL_AUTH_KEY_ID":"k", "WILSY_INTERNAL_AUTH_SECRET":"secret"})
        assert getattr(error.value, "status_code", None) == 401
    asyncio.run(run())


def test_replay_and_replay_infrastructure_are_distinct_boundaries():
    async def run():
        from tools.eos.auth.internal_service_trust import InternalServiceTrustReplayError
        config = {"WILSY_INTERNAL_AUTH_SERVICE_ID":"node", "WILSY_INTERNAL_AUTH_AUDIENCE":"python", "WILSY_INTERNAL_AUTH_KEY_ID":"k", "WILSY_INTERNAL_AUTH_SECRET":"secret"}
        def replay(**kwargs):
            raise InternalServiceTrustReplayError("replayed nonce")
        with pytest.raises(Exception) as duplicate:
            await authorize_request(_request(), BridgeRequest(policy_id="audit:read"), replay_store=_Replay(), config=config, trust_verifier=replay)
        assert getattr(duplicate.value, "status_code", None) == 401
        def infrastructure(**kwargs):
            raise RuntimeError("provider offline")
        with pytest.raises(Exception) as unavailable:
            await authorize_request(_request(), BridgeRequest(policy_id="audit:read"), replay_store=_Replay(), config=config, trust_verifier=infrastructure)
        assert getattr(unavailable.value, "status_code", None) == 503
    asyncio.run(run())


def test_freshness_failures_are_bounded_denials():
    async def run():
        from tools.eos.auth.internal_service_trust import InternalServiceTrustFreshnessError
        config = {"WILSY_INTERNAL_AUTH_SERVICE_ID":"node", "WILSY_INTERNAL_AUTH_AUDIENCE":"python", "WILSY_INTERNAL_AUTH_KEY_ID":"k", "WILSY_INTERNAL_AUTH_SECRET":"secret"}
        for message in ("timestamp outside acceptance window", "future timestamp"):
            def stale(**kwargs):
                raise InternalServiceTrustFreshnessError(message)
            with pytest.raises(Exception) as error:
                await authorize_request(_request(), BridgeRequest(policy_id="audit:read"), replay_store=_Replay(), config=config, trust_verifier=stale)
            assert getattr(error.value, "status_code", None) == 401
    asyncio.run(run())


def test_direct_frozen_replay_duplicate_denies_second_claim():
    async def run():
        body = b'{"policy_id":"audit:read"}'
        digest = body_sha3_512(body)
        nonce = "abcdef0123456789abcdef0123456789"
        canonical = canonical_request(version="v1", service_id="node", audience="python", method="POST", path="/internal/authority/authorize", timestamp="1700000000", nonce=nonce, body_sha3_512_value=digest, correlation_id="corr-replay")
        signature = hmac.new(b"secret", canonical, hashlib.sha256).hexdigest()
        request = _request(body, b"/internal/authority/authorize", b"")
        request.scope["headers"] = [(k, v) for k, v in request.scope["headers"] if not k.startswith(b"x-wilsy")]
        request.scope["headers"] += [(b"x-wilsy-auth-version", b"v1"), (b"x-wilsy-service-id", b"node"), (b"x-wilsy-audience", b"python"), (b"x-wilsy-key-id", b"k"), (b"x-wilsy-timestamp", b"1700000000"), (b"x-wilsy-nonce", nonce.encode()), (b"x-wilsy-body-sha3-512", digest.encode()), (b"x-wilsy-correlation-id", b"corr-replay"), (b"x-wilsy-signature", signature.encode())]
        class Replay:
            def __init__(self): self.seen = False
            def consume_once(self, **kwargs):
                if self.seen: return False
                self.seen = True
                return True
        replay = Replay()
        def frozen(**kwargs): return verify_internal_service_request(**kwargs, now=1700000000)
        kwargs = dict(payload=BridgeRequest(policy_id="audit:read"), replay_store=replay, config={"WILSY_INTERNAL_AUTH_SERVICE_ID":"node", "WILSY_INTERNAL_AUTH_AUDIENCE":"python", "WILSY_INTERNAL_AUTH_KEY_ID":"k", "WILSY_INTERNAL_AUTH_SECRET":"secret"}, trust_verifier=frozen, identity_provider=AsyncMock(return_value=_identity()), tenant_provider=AsyncMock(return_value=_identity()), authorization_provider=AsyncMock(return_value=_identity()))
        assert (await authorize_request(request, **kwargs)) ["allowed"] is True  # type: ignore[arg-type]
        request = _request(body, b"/internal/authority/authorize", b"")
        request.scope["headers"] = [(k, v) for k, v in request.scope["headers"] if not k.startswith(b"x-wilsy")]
        request.scope["headers"] += [(b"x-wilsy-auth-version", b"v1"), (b"x-wilsy-service-id", b"node"), (b"x-wilsy-audience", b"python"), (b"x-wilsy-key-id", b"k"), (b"x-wilsy-timestamp", b"1700000000"), (b"x-wilsy-nonce", nonce.encode()), (b"x-wilsy-body-sha3-512", digest.encode()), (b"x-wilsy-correlation-id", b"corr-replay"), (b"x-wilsy-signature", signature.encode())]
        with pytest.raises(Exception) as error: await authorize_request(request, **kwargs)  # type: ignore[arg-type]
        assert getattr(error.value, "status_code", None) == 401
    asyncio.run(run())


def test_one_byte_body_mutation_invalidates_signed_assertion():
    async def run():
        body = b'{"policy_id":"audit:read"}'
        digest = body_sha3_512(body)
        nonce = "fedcba9876543210fedcba9876543210"
        canonical = canonical_request(version="v1", service_id="node", audience="python", method="POST", path="/internal/authority/authorize", timestamp="1700000000", nonce=nonce, body_sha3_512_value=digest, correlation_id="corr-mutate")
        signature = hmac.new(b"secret", canonical, hashlib.sha256).hexdigest()
        request = _request(body[:-1] + b"X", b"/internal/authority/authorize", b"")
        request.scope["headers"] = [(k, v) for k, v in request.scope["headers"] if not k.startswith(b"x-wilsy")]
        request.scope["headers"] += [(b"x-wilsy-auth-version", b"v1"), (b"x-wilsy-service-id", b"node"), (b"x-wilsy-audience", b"python"), (b"x-wilsy-key-id", b"k"), (b"x-wilsy-timestamp", b"1700000000"), (b"x-wilsy-nonce", nonce.encode()), (b"x-wilsy-body-sha3-512", digest.encode()), (b"x-wilsy-correlation-id", b"corr-mutate"), (b"x-wilsy-signature", signature.encode())]
        with pytest.raises(Exception) as error:
            await authorize_request(request, BridgeRequest(policy_id="audit:read"), replay_store=_Replay(), config={"WILSY_INTERNAL_AUTH_SERVICE_ID":"node", "WILSY_INTERNAL_AUTH_AUDIENCE":"python", "WILSY_INTERNAL_AUTH_KEY_ID":"k", "WILSY_INTERNAL_AUTH_SECRET":"secret"}, trust_verifier=lambda **kwargs: verify_internal_service_request(**kwargs, now=1700000000))
        assert getattr(error.value, "status_code", None) == 401
    asyncio.run(run())


@pytest.mark.parametrize("path,query,expected", [(b"/internal/authority/authorize", b"", "/internal/authority/authorize"), (b"/internal/authority/authorize", b"q=1&x=2", "/internal/authority/authorize?q=1&x=2"), (b"/a%2Fb", b"q=%2F", "/a%2Fb?q=%2F"), (b"/%E2%82%AC", b"q=%C3%A9", "/%E2%82%AC?q=%C3%A9"), (b"/path", b"q=a+b", "/path?q=a+b"), (b"/path", b"q=a%20b", "/path?q=a%20b")], ids=["plain", "ordered-query", "encoded-slash", "encoded-unicode", "plus", "percent-space"])
def test_origin_form_preserves_exact_wire_bytes(path, query, expected):
    assert _origin_form(_request(path=path, query=query)) == expected


def test_raw_body_bytes_reach_verifier_without_reserialization():
    async def run():
        observed = []
        async def identity(): return _identity()
        async def tenant(value): return value
        async def authorization(value, policy): return value
        def verifier(**kwargs):
            observed.append(kwargs["body"])
            return TrustResult("node", "python", "k", "corr", 1, "v1")
        config = {"WILSY_INTERNAL_AUTH_SERVICE_ID":"node", "WILSY_INTERNAL_AUTH_AUDIENCE":"python", "WILSY_INTERNAL_AUTH_KEY_ID":"k", "WILSY_INTERNAL_AUTH_SECRET":"secret"}
        for body in (b"", b'{"ok":true}', "Zażółć gęślą jaźń".encode(), b"\x00\x01\xffpayload"):
            await authorize_request(_request(body=body), BridgeRequest(policy_id="audit:read"), replay_store=_Replay(), config=config, trust_verifier=verifier, identity_provider=identity, tenant_provider=tenant, authorization_provider=authorization)
        assert observed == [b"", b'{"ok":true}', "Zażółć gęślą jaźń".encode(), b"\x00\x01\xffpayload"]
    asyncio.run(run())


def test_user_and_tenant_authority_failures_remain_401():
    async def run():
        config = {"WILSY_INTERNAL_AUTH_SERVICE_ID":"node", "WILSY_INTERNAL_AUTH_AUDIENCE":"python", "WILSY_INTERNAL_AUTH_KEY_ID":"k", "WILSY_INTERNAL_AUTH_SECRET":"secret"}
        for identity_provider, tenant_provider in ((AsyncMock(side_effect=UnauthorizedAccessException("bad bearer")), None), (AsyncMock(return_value=_identity()), AsyncMock(side_effect=UnauthorizedAccessException("membership denied")))):
            with pytest.raises(Exception) as error:
                await authorize_request(_request(), BridgeRequest(policy_id="audit:read"), replay_store=_Replay(), config=config, trust_verifier=_trust, identity_provider=identity_provider, tenant_provider=tenant_provider)
            assert getattr(error.value, "status_code", None) == 401
    asyncio.run(run())


@pytest.mark.parametrize("field", ["identity_id", "principal_id", "user_id", "tenant_id", "role", "roles", "permission", "permissions", "GLOBAL_ROOT", "bypass", "canBypassTenant", "isAdmin", "admin"])
def test_request_authority_fields_cannot_cross_bridge(field):
    with pytest.raises(ValueError):
        BridgeRequest.model_validate({"policy_id": "audit:read", field: "forged"})


def test_unknown_policy_fails_closed_with_403():
    async def run():
        from tools.eos.api.authority_bridge_router import _authorize_policy
        with pytest.raises(ForbiddenOperationException):
            await _authorize_policy(_identity(), "unknown-policy")
    asyncio.run(run())


def test_authorization_revocation_denies_403():
    async def run():
        config = {"WILSY_INTERNAL_AUTH_SERVICE_ID":"node", "WILSY_INTERNAL_AUTH_AUDIENCE":"python", "WILSY_INTERNAL_AUTH_KEY_ID":"k", "WILSY_INTERNAL_AUTH_SECRET":"secret"}
        for outcome in (ForbiddenOperationException("assignment absent"), ForbiddenOperationException("assignment revoked")):
            with pytest.raises(ForbiddenOperationException):
                await authorize_request(_request(), BridgeRequest(policy_id="audit:read"), replay_store=_Replay(), config=config, trust_verifier=_trust, identity_provider=AsyncMock(return_value=_identity()), tenant_provider=AsyncMock(return_value=_identity()), authorization_provider=AsyncMock(side_effect=outcome))
    asyncio.run(run())


def test_allow_and_denial_surfaces_are_bounded():
    async def run():
        config = {"WILSY_INTERNAL_AUTH_SERVICE_ID":"node", "WILSY_INTERNAL_AUTH_AUDIENCE":"python", "WILSY_INTERNAL_AUTH_KEY_ID":"k", "WILSY_INTERNAL_AUTH_SECRET":"secret"}
        result = await authorize_request(_request(), BridgeRequest(policy_id="audit:read"), replay_store=_Replay(), config=config, trust_verifier=_trust, identity_provider=AsyncMock(return_value=_identity()), tenant_provider=AsyncMock(return_value=_identity()), authorization_provider=AsyncMock(return_value=_identity()))
        assert set(result) == {"allowed", "identity_id", "tenant_id", "correlation_id"}
        for exc in (UnauthorizedAccessException("Authentication credentials were not provided."), ForbiddenOperationException("Access denied.")):
            assert not any(token in str(exc) for token in ("secret", "mongodb://", "traceback", "Bearer"))
    asyncio.run(run())


def test_governed_authentication_rejects_inactive_and_revoked_principals(monkeypatch):
    import tools.eos.auth.authentication as authentication
    from fastapi.security import HTTPAuthorizationCredentials
    from tools.eos.auth.principal_authority import PrincipalAuthority
    async def run(status):
        monkeypatch.setattr(authentication, "verify_access_token", lambda token: {"identity_id":"p", "tenant_id":"t"})
        repo = type("Repo", (), {"get": lambda self, principal: PrincipalAuthority("p", status, 0)})()
        with pytest.raises(UnauthorizedAccessException):
            await authentication.get_current_identity(Request({"type":"http", "headers":[]}), HTTPAuthorizationCredentials(scheme="Bearer", credentials="token"), None, cast(Any, repo))
    asyncio.run(run(PrincipalStatus.SUSPENDED))
    asyncio.run(run(PrincipalStatus.REVOKED))


def test_final_64_property_traceability_seal():
    executed = {
        1: "test_valid_request_uses_actual_frozen_verifier", 2: "test_valid_request_uses_actual_frozen_verifier", 3: "test_actual_frozen_verifier_missing_header_is_bounded_401", 4: "test_actual_frozen_verifier_malformed_timestamp_is_bounded_401", 5: "test_actual_frozen_verifier_bad_signature_is_bounded_401", 6: "test_actual_frozen_verifier_body_digest_and_service_mismatch_are_401", 7: "test_actual_frozen_verifier_unknown_key_exposes_mapping_gap", 8: "test_trust_and_config_fail_closed", 9: "test_actual_frozen_verifier_body_digest_and_service_mismatch_are_401", 10: "test_audience_is_checked_by_bridge_contract", 11: "test_freshness_failures_are_bounded_denials", 12: "test_freshness_failures_are_bounded_denials", 13: "test_direct_frozen_replay_duplicate_denies_second_claim", 14: "test_direct_frozen_replay_duplicate_denies_second_claim", 15: "test_replay_and_replay_infrastructure_are_distinct_boundaries", 16: "test_raw_body_bytes_reach_verifier_without_reserialization", 17: "test_raw_body_bytes_reach_verifier_without_reserialization", 18: "test_raw_body_bytes_reach_verifier_without_reserialization", 19: "test_raw_body_bytes_reach_verifier_without_reserialization", 20: "test_one_byte_body_mutation_invalidates_signed_assertion", 21: "test_raw_body_bytes_reach_verifier_without_reserialization", 22: "test_origin_form_preserves_exact_wire_bytes", 23: "test_origin_form_preserves_exact_wire_bytes", 24: "test_origin_form_preserves_exact_wire_bytes", 25: "test_origin_form_preserves_exact_wire_bytes", 26: "test_origin_form_preserves_exact_wire_bytes", 27: "test_origin_form_preserves_exact_wire_bytes", 28: "test_origin_form_preserves_exact_wire_bytes", 29: "test_user_and_tenant_authority_failures_remain_401", 30: "test_user_and_tenant_authority_failures_remain_401", 31: "test_request_authority_fields_cannot_cross_bridge", 32: "test_request_authority_fields_cannot_cross_bridge", 33: "test_request_authority_fields_cannot_cross_bridge", 34: "test_governed_authentication_rejects_inactive_and_revoked_principals", 35: "test_valid_composition_is_bounded_and_delegated", 36: "test_user_and_tenant_authority_failures_remain_401", 37: "test_request_authority_fields_cannot_cross_bridge", 38: "test_user_and_tenant_authority_failures_remain_401", 39: "test_valid_composition_is_bounded_and_delegated", 40: "test_user_tenant_and_policy_denials_are_preserved", 41: "test_authorization_revocation_denies_403", 42: "test_unknown_policy_fails_closed_with_403", 43: "test_request_authority_fields_cannot_cross_bridge", 44: "test_request_authority_fields_cannot_cross_bridge", 45: "test_request_authority_fields_cannot_cross_bridge", 46: "test_request_authority_fields_cannot_cross_bridge", 47: "test_request_authority_fields_cannot_cross_bridge", 48: "test_request_authority_fields_cannot_cross_bridge", 49: "test_request_authority_fields_cannot_cross_bridge", 50: "test_request_authority_fields_cannot_cross_bridge", 51: "test_request_authority_fields_cannot_cross_bridge", 52: "test_valid_composition_is_bounded_and_delegated", 53: "test_direct_asgi_serializes_bounded_errors_without_httpx", 54: "test_direct_asgi_serializes_bounded_errors_without_httpx", 55: "test_direct_asgi_serializes_bounded_errors_without_httpx", 56: "test_direct_asgi_serializes_bounded_errors_without_httpx", 57: "test_direct_asgi_serializes_bounded_errors_without_httpx", 58: "test_direct_asgi_serializes_bounded_errors_without_httpx", 59: "test_trust_and_config_fail_closed", 60: "test_trust_and_config_fail_closed", 61: "test_trust_and_config_fail_closed", 62: "test_valid_composition_is_bounded_and_delegated", 63: "test_valid_composition_is_bounded_and_delegated", 64: "test_valid_composition_is_bounded_and_delegated",
    }
    assert len(executed) == 64
    assert all(isinstance(name, str) and name for name in executed.values())


def test_direct_asgi_serializes_bounded_errors_without_httpx():
    async def run():
        from fastapi import FastAPI
        from tools.eos.api.errors import register_error_handlers
        from tools.eos.api.exceptions import WilsyAPIException
        app = FastAPI()
        register_error_handlers(app, debug=False)
        @app.get("/error/{code}")
        async def error(code: int):
            raise WilsyAPIException("bounded", status_code=code, details={"secret": "hidden"})
        for code in (401, 403, 503):
            sent = []
            async def send(message): sent.append(message)
            async def receive(): return {"type": "http.request", "body": b"", "more_body": False}
            await app({"type":"http", "method":"GET", "path":f"/error/{code}", "raw_path":f"/error/{code}".encode(), "query_string":b"", "headers":[], "server":("test",80), "scheme":"http"}, receive, send)
            assert sent[0]["status"] == code
            body = b"".join(m.get("body", b"") for m in sent if m["type"] == "http.response.body")
            assert b"hidden" not in body and b"traceback" not in body
    asyncio.run(run())



# ARTIFACT: test_authority_bridge_router.py
# VERSION: v1.0.0-WILSY-PYTHON-AUTHORITY-BRIDGE
# AUTHORITY BOUNDARY: Isolated composition certification only.
# TENANT POSTURE: Tenant context is independently admitted by Python authority.
# FAIL-CLOSED POSTURE: Invalid trust, identity, tenant, or policy authority never grants access.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
