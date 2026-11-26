"""TITLE: MW-T12 exact Atlas temporary source-network admission unit certificate.
VERSION: v1.5.0-HERMETIC-OAUTH-TRANSPORT-CERT
AUTHORITY: WILSY OS Core Governance / AGENTS.md.
EPITOME: Certify Atlas source-IP admission and task-owned rollback fail
         closed on wildcard, ownership drift, concurrency and unauthorized task.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_mw_t12_atlas_access_admission.py
COLLABORATION / OWNERSHIP: tools/eos/ops/mw_t12_atlas_access_admission.py;
         existing exact ECS identity and CloudFormation safety controls.
CERTIFICATION / UPDATE DATE: 2026-11-25.
CHANGELOG: v1.5.0-HERMETIC-OAUTH-TRANSPORT-CERT isolates
           the optional HTTP transport with mock-only modules, avoiding
           external network access or undeclared runtime test dependencies.
CHANGELOG: v1.4.0-OAUTH-SERVICE-ACCOUNT-ISOLATION-CERT covers
           successful OAuth Bearer exchange, denied/invalid responses,
           and restriction to read-only isolated inventory.
CHANGELOG: v1.3.0-ATLAS-API-DENIAL-CLASSIFICATION tests only
           safe HTTP status classifications; no request body or key exposure.
CHANGELOG: v1.2.0-ISOLATION-CLI-FAILCLOSED-CERT verifies the real
           read-only CLI denies wildcard, refuses mutation flag combinations
           before opening network sessions and never issues POST/DELETE.
CHANGELOG: v1.1.0-READONLY-ISOLATION-DENIAL-TEST guards against
           wildcard, broader, duplicate, unattributed and private network
           inventory without making Atlas requests or launching ECS.
CHANGELOG: v1.0.1-PUBLIC-IP-MOCK-FIXTURE-VALIDATION selects a globally routable
           mock-only public IPv4 so strict source-IP checks are exercised;
           no live network activity or Atlas mutation.
CHANGELOG: v1.0.0-OWNED-ROLLBACK-AND-ACCESS-DRIFT-CERTIFICATION
           adds deterministic pure/monkeypatched denial and success tests
           without real AWS, Atlas API, credentials, tasks or network writes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Mock-only global IPv4 fixture and fake API responses;
TENANT BOUNDARY: Synthetic recovery fixture only; no business data.
AUTHORITY BOUNDARY: Test doubles do not grant network or task authority.
FINANCIAL AUTHORITY BOUNDARY: No spending; Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone


import pytest

from tools.eos.ops import mw_t12_atlas_access_admission as admission


TASK_ID = "a" * 32
TASK_ARN = (
    "arn:aws:ecs:af-south-1:121014832643:task/"
    "wilsy-mwt12-nonproduction/" + TASK_ID
)
TEST_SOURCE_IP = "8.8.8.8"  # Mock-only; never sent to Atlas or AWS.


def _entry(*, owner: str | None = None, expiry: str | None = None) -> dict:
    """Build nonlive task source entry with exact task-comment ownership."""
    return {
        "ipAddress": TEST_SOURCE_IP,
        "cidrBlock": TEST_SOURCE_IP + "/32",
        "comment": owner if owner is not None
        else admission.owned_comment(TASK_ARN),
        "deleteAfterDate": expiry or (
            datetime.now(timezone.utc) + timedelta(hours=2)
        ).isoformat(timespec="seconds").replace("+00:00", "Z"),
    }


def test_canonical_network_baseline_is_order_independent() -> None:
    """Fingerprint exact IP networks, never volatile Atlas metadata."""
    first = [{"ipAddress": TEST_SOURCE_IP},
             {"cidrBlock": "0.0.0.0/0"}]
    second = [{"cidrBlock": "0.0.0.0/0", "comment": "changed"},
              {"cidrBlock": TEST_SOURCE_IP + "/32",
               "deleteAfterDate": "later"}]
    assert admission.network_fingerprint(first) == (
        admission.network_fingerprint(second)
    )
    assert admission.network_fingerprint(first) != (
        admission.network_fingerprint([{"ipAddress": TEST_SOURCE_IP}])
    )


def test_temporary_admission_refuses_global_entry(monkeypatch) -> None:
    """An additional /32 never compensates for unrestricted shared access."""
    def forbidden(*args, **kwargs):
        raise AssertionError("MUST_NOT_CALL_ATLAS")

    monkeypatch.setattr(admission, "atlas", forbidden)
    with pytest.raises(admission.NetworkAdmissionError,
                       match="SHARED_ATLAS_GLOBAL_ACCESS"):
        admission.admit(None, [{"cidrBlock": "0.0.0.0/0"}],
                        TEST_SOURCE_IP, TASK_ARN)


def test_temporary_admission_rechecks_access_before_write(monkeypatch) -> None:
    """Another actor changing the access list invalidates the read snapshot."""
    monkeypatch.setattr(
        admission, "inventory",
        lambda unused: [{"cidrBlock": "0.0.0.0/0"}],
    )
    def forbidden(*args, **kwargs):
        raise AssertionError("MUST_NOT_MUTATE_ATLAS")

    monkeypatch.setattr(admission, "atlas", forbidden)
    with pytest.raises(admission.NetworkAdmissionError,
                       match="ATLAS_ACCESS_LIST_CHANGED_DURING_ADMISSION"):
        admission.admit(None, [], TEST_SOURCE_IP, TASK_ARN)


def test_exact_task_receipt_and_ttl_are_read_back(monkeypatch, capsys) -> None:
    """A successful mocked POST is recorded only after matching GET readback."""
    writes = []

    def fake_atlas(client, method, route, *, payload=None, params=None):
        assert method == "POST"
        assert route == "/accessList"
        writes.append(payload)
        return {}

    def fake_inventory(client):
        if not writes:
            return []
        return [{
            "ipAddress": TEST_SOURCE_IP,
            "comment": admission.owned_comment(TASK_ARN),
            "deleteAfterDate": writes[0][0]["deleteAfterDate"],
        }]

    monkeypatch.setattr(admission, "atlas", fake_atlas)
    monkeypatch.setattr(admission, "inventory", fake_inventory)
    admission.admit(None, [], TEST_SOURCE_IP, TASK_ARN)
    assert len(writes) == 1
    assert writes[0][0]["ipAddress"] == TEST_SOURCE_IP
    assert writes[0][0]["comment"] == admission.owned_comment(TASK_ARN)
    expiry = datetime.fromisoformat(
        writes[0][0]["deleteAfterDate"].replace("Z", "+00:00")
    )
    remaining = expiry - datetime.now(timezone.utc)
    assert timedelta(hours=5, minutes=59) < remaining <= timedelta(hours=6)
    assert "MW_T12_ATLAS_TEMPORARY_ACCESS=VERIFIED_READBACK" in capsys.readouterr().out


def test_revoke_refuses_unowned_entry(monkeypatch) -> None:
    """Never DELETE another user's shared rule, even on the same /32."""
    monkeypatch.setattr(
        admission, "atlas",
        lambda *a, **k: pytest.fail("DELETE_MUST_NOT_RUN"),
    )
    with pytest.raises(admission.NetworkAdmissionError,
                       match="OWNED_ATLAS_ENTRY_IDENTITY_MISMATCH"):
        admission.revoke_owned(
            None, [_entry(owner="unrelated consumer")],
            TASK_ARN, TEST_SOURCE_IP,
        )


def test_revoke_refuses_wildcard_and_wrong_task(monkeypatch) -> None:
    """Task identity or IPv4 scope mismatch cannot revoke a network entry."""
    monkeypatch.setattr(
        admission, "atlas",
        lambda *a, **k: pytest.fail("DELETE_MUST_NOT_RUN"),
    )
    with pytest.raises(admission.NetworkAdmissionError,
                       match="REVOKE_SOURCE_IPV4_INVALID"):
        admission.revoke_owned(
            None, [{"cidrBlock": "0.0.0.0/0"}], TASK_ARN, "0.0.0.0",
        )
    wrong_task = TASK_ARN[:-32] + "b" * 32
    with pytest.raises(admission.NetworkAdmissionError,
                       match="OWNED_ATLAS_ENTRY_IDENTITY_MISMATCH"):
        admission.revoke_owned(None, [_entry()], wrong_task, TEST_SOURCE_IP)


def test_revoke_refuses_modified_entry_between_reads(monkeypatch) -> None:
    """A concurrent CIDR change prevents any DELETE before it is attempted."""
    monkeypatch.setattr(
        admission, "inventory",
        lambda unused: [{"cidrBlock": "203.0.113.12/32"}],
    )
    monkeypatch.setattr(
        admission, "atlas",
        lambda *a, **k: pytest.fail("DELETE_MUST_NOT_RUN"),
    )
    with pytest.raises(admission.NetworkAdmissionError,
                       match="ATLAS_ACCESS_LIST_CHANGED_DURING_REVOKE"):
        admission.revoke_owned(None, [_entry()], TASK_ARN, TEST_SOURCE_IP)


def test_revoke_owner_only_and_post_delete_absence(monkeypatch, capsys) -> None:
    """One exact task-owned entry is removed; unrelated shared entry survives."""
    owned = _entry()
    shared = {"cidrBlock": "198.51.100.7/32", "comment": "legacy consumer"}
    calls = []
    deleted = False

    def fake_atlas(client, method, route, *, payload=None, params=None):
        nonlocal deleted
        assert method == "DELETE"
        assert route == "/accessList/" + TEST_SOURCE_IP
        calls.append(route)
        deleted = True
        return {}

    def fake_inventory(client):
        return [shared] if deleted else [owned, shared]

    monkeypatch.setattr(admission, "atlas", fake_atlas)
    monkeypatch.setattr(admission, "inventory", fake_inventory)
    admission.revoke_owned(None, [owned, shared], TASK_ARN, TEST_SOURCE_IP)
    assert calls == ["/accessList/" + TEST_SOURCE_IP]
    assert "MW_T12_OWNED_ATLAS_ENTRY_REVOKED=VERIFIED" in capsys.readouterr().out


def test_invalid_task_arn_fails_without_aws_or_atlas(monkeypatch) -> None:
    """Unrelated ARN fails before consulting live ECS or network endpoints."""
    monkeypatch.setattr(
        admission.ecs, "aws",
        lambda *a, **k: pytest.fail("AWS_MUST_NOT_RUN"),
    )
    with pytest.raises(admission.NetworkAdmissionError,
                       match="EXACT_NONPRODUCTION_TASK_ARN_REQUIRED"):
        admission.public_source_ip("wilsy-legal-cert", "other-task")


@pytest.mark.parametrize("entries,denial", [
    ([{"cidrBlock": "0.0.0.0/0", "comment": "test"}],
     "ATLAS_PUBLIC_NETWORK_WILDCARD_PRESENT"),
    ([{"cidrBlock": "8.8.8.0/24", "comment": "test"}],
     "ATLAS_NONEXACT_OR_NONGLOBAL_NETWORK"),
    ([{"cidrBlock": "10.0.0.1/32", "comment": "test"}],
     "ATLAS_NONEXACT_OR_NONGLOBAL_NETWORK"),
    ([{"cidrBlock": "8.8.8.8/32", "comment": ""}],
     "ATLAS_NETWORK_CONSUMER_UNATTRIBUTED"),
    ([{"cidrBlock": "8.8.8.8/32", "comment": "owner"},
      {"ipAddress": "8.8.8.8", "comment": "other"}],
     "ATLAS_DUPLICATE_NETWORKS_UNATTRIBUTED"),
])
def test_readonly_network_cert_rejects_unsafe_shared_sources(
    entries, denial,
) -> None:
    """Read-only admission cannot mistake global or unknown sources for safe."""
    with pytest.raises(admission.NetworkAdmissionError, match=denial):
        admission.certify_isolated_network(entries)


def test_readonly_network_cert_proves_only_ip_inventory(capsys) -> None:
    """A valid source inventory still cannot certify actual ECS recovery."""
    admission.certify_isolated_network([{
        "cidrBlock": "8.8.8.8/32", "comment": "verified synthetic consumer",
    }])
    output = capsys.readouterr().out
    assert "MW_T12_ATLAS_SOURCE_NETWORK_INVENTORY=ISOLATION_ELIGIBLE" in output
    assert "MW_T12_ATLAS_ECS_CONNECTIVITY_CERTIFIED=FALSE" in output
    assert "MW_T12_ATLAS_BACKUP_RESTORE_CERTIFIED=FALSE" in output


def test_readonly_isolation_cli_fails_closed_without_mutation(
    monkeypatch, capsys,
) -> None:
    """The operator flag must deny a wildcard without changing Atlas."""
    class FakeClient:
        def close(self):
            pass
    monkeypatch.setattr(admission, "atlas_session", lambda *args: FakeClient())
    monkeypatch.setattr(admission, "inventory",
                        lambda client: [{"cidrBlock": "0.0.0.0/0"}])
    monkeypatch.setattr(admission, "atlas", lambda *a, **k:
                        pytest.fail("MUST_NOT_MUTATE_ATLAS"))
    result = admission.main(["--certify-isolation"])
    assert result == 2
    output = capsys.readouterr().out
    assert "MW_T12_ERROR=ATLAS_PUBLIC_NETWORK_WILDCARD_PRESENT" in output
    assert "MW_T12_ATLAS_ACCESS_ADMISSION=FAIL_CLOSED" in output


def test_isolation_flag_never_combines_with_network_write(monkeypatch) -> None:
    """Reject disallowed combinations before any API credential prompt."""
    monkeypatch.setattr(admission, "atlas_session", lambda:
                        pytest.fail("MUST_NOT_OPEN_ATLAS_SESSION"))
    result = admission.main([
        "--certify-isolation", "--admit-six-hours",
        "--task-arn", TASK_ARN,
    ])
    assert result == 2


@pytest.mark.parametrize("status,code", [
    (401, "ATLAS_ADMIN_API_AUTHENTICATION_DENIED_401"),
    (403, "ATLAS_ADMIN_API_ACCESS_DENIED_403"),
    (429, "ATLAS_ADMIN_API_RATE_LIMITED_429"),
    (404, "ATLAS_API_REQUEST_DENIED"),
])
def test_atlas_admin_api_denials_are_status_only(
    status, code,
) -> None:
    """Never print or process a denied response body containing secrets."""
    class Denial:
        status_code = status
        content = b"PRIVATE-ERROR-BODY-MUST-NOT-BE-READ"
        def json(self):
            pytest.fail("DENIAL_BODY_MUST_NOT_BE_PARSED")
    class Client:
        def request(self, method, url, **kwargs):
            assert method == "GET"
            return Denial()
    with pytest.raises(admission.NetworkAdmissionError,
                       match="^" + code + "$") as denied:
        admission.atlas(Client(), "GET", "/accessList")
    assert "PRIVATE-ERROR-BODY-MUST-NOT-BE-READ" not in str(denied.value)


def _mock_requests(monkeypatch, session_class) -> None:
    """Inject a hermetic requests transport; no pip or actual networking."""
    import sys
    from types import ModuleType

    request_module = ModuleType("requests")
    auth_module = ModuleType("requests.auth")

    class Basic:
        def __init__(self, username, password):
            self.username = username
            self.password = password

    request_module.Session = session_class
    auth_module.HTTPBasicAuth = Basic
    auth_module.HTTPDigestAuth = Basic
    request_module.auth = auth_module
    monkeypatch.setitem(sys.modules, "requests", request_module)
    monkeypatch.setitem(sys.modules, "requests.auth", auth_module)


def test_oauth_service_account_token_uses_ephemeral_bearer(monkeypatch) -> None:
    """Client credentials only enter TLS Basic auth, not CLI, logs or files."""
    prompts = iter(("mdb_sa_id_synthetic", "mdb_sa_sk_synthetic"))
    monkeypatch.setattr(admission, "getpass", lambda prompt: next(prompts))
    calls = []

    class Reply:
        status_code = 200
        content = b'{"access_token":"synthetic-access-token"}'
        def json(self):
            return {
                "access_token": "synthetic-access-token",
                "token_type": "Bearer",
                "expires_in": 3600,
            }

    class Session:
        def __init__(self):
            self.headers = {}
            self.closed = False
            self.auth = None
        def post(self, url, **kwargs):
            calls.append((url, kwargs))
            return Reply()
        def close(self):
            self.closed = True

    _mock_requests(monkeypatch, Session)
    client = admission.atlas_session("service-account")
    assert len(calls) == 1
    url, options = calls[0]
    assert url == admission.OAUTH_TOKEN_URL
    assert options["data"] == {"grant_type": "client_credentials"}
    assert options["auth"].username == "mdb_sa_id_synthetic"
    assert options["auth"].password == "mdb_sa_sk_synthetic"
    assert options["allow_redirects"] is False
    assert client.auth is None
    assert client.headers["Authorization"] == "Bearer synthetic-access-token"
    assert client.headers["Accept"] == admission.ATLAS_MEDIA_TYPE
    client.close()
    assert client.closed


@pytest.mark.parametrize("status,code", [
    (401, "ATLAS_OAUTH_CLIENT_AUTH_DENIED_401"),
    (403, "ATLAS_OAUTH_CLIENT_ACCESS_DENIED_403"),
    (429, "ATLAS_OAUTH_RATE_LIMITED_429"),
    (503, "ATLAS_OAUTH_TOKEN_UNAVAILABLE"),
])
def test_oauth_denials_do_not_parse_or_log_sensitive_body(
    monkeypatch, status, code,
) -> None:
    """Denied OAuth token responses never disclose bodies or retry."""
    prompts = iter(("mdb_sa_id_mock", "mdb_sa_sk_mock"))
    monkeypatch.setattr(admission, "getpass", lambda prompt: next(prompts))

    class Reply:
        status_code = status
        content = b"SENSITIVE_RESPONSE"
        def json(self):
            pytest.fail("MUST_NOT_PARSE_DENIED_OAUTH_RESPONSE")

    class Session:
        def __init__(self):
            self.headers = {}
            self.closed = False
        def post(self, *args, **kwargs):
            return Reply()
        def close(self):
            self.closed = True

    _mock_requests(monkeypatch, Session)
    with pytest.raises(admission.NetworkAdmissionError,
                       match="^" + code + "$") as denied:
        admission.atlas_session("service-account")
    assert "SENSITIVE_RESPONSE" not in str(denied.value)


@pytest.mark.parametrize("payload", [
    {"access_token": "", "token_type": "Bearer", "expires_in": 3600},
    {"access_token": "token", "token_type": "Basic", "expires_in": 3600},
    {"access_token": "token", "token_type": "Bearer", "expires_in": 7200},
    {"access_token": "token", "token_type": "Bearer", "expires_in": True},
])
def test_oauth_invalid_token_contract_denies(monkeypatch, payload) -> None:
    """Malformed token fields cannot become Authorization Bearer."""
    prompts = iter(("mdb_sa_id_mock", "mdb_sa_sk_mock"))
    monkeypatch.setattr(admission, "getpass", lambda prompt: next(prompts))

    class Reply:
        status_code = 200
        content = b"{}"
        def json(self):
            return payload

    class Session:
        def __init__(self):
            self.headers = {}
        def post(self, *args, **kwargs):
            return Reply()
        def close(self):
            pass

    _mock_requests(monkeypatch, Session)
    with pytest.raises(admission.NetworkAdmissionError,
                       match="^ATLAS_OAUTH_TOKEN_INVALID$"):
        admission.atlas_session("service-account")


def test_oauth_service_account_isolation_only_refuses_mutations(
    monkeypatch,
) -> None:
    """No service account CLI mode can invoke POST, DELETE or task admission."""
    monkeypatch.setattr(admission, "atlas_session", lambda *args:
                        pytest.fail("SHOULD_NOT_OPEN_ATLAS_SESSION"))
    for args in (
        ["--auth-mode", "service-account"],
        ["--auth-mode", "service-account", "--revoke-owned",
         "--task-arn", TASK_ARN, "--owned-source-ip", TEST_SOURCE_IP],
        ["--auth-mode", "service-account", "--admit-six-hours",
         "--task-arn", TASK_ARN],
    ):
        assert admission.main(args) == 2


# ARTIFACT: tests/unit/test_mw_t12_atlas_access_admission.py
# VERSION: v1.5.0-HERMETIC-OAUTH-TRANSPORT-CERT
# AUTHORITY BOUNDARY: Mocked Atlas /32 admission only; no cloud mutation.
# TENANT POSTURE: No real tenant, MongoDB or credential access.
# FAIL-CLOSED POSTURE: Wildcard, shared ownership and changed state denied.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
