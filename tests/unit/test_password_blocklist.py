"""Direct unit certificate for the WILSY OS password-blocklist adapter.

TITLE: WILSY OS Pwned Password Blocklist Adapter Direct Certificate
VERSION: v1.0.0-R10C1B-PASSWORD-BLOCKLIST-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the exact fixed-provider k-anonymity adapter through
         deterministic fake transports. This certificate is offline,
         Mongo-free, secret-free, and independent of live HIBP availability.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_blocklist.py
COLLABORATION / OWNERSHIP: Tests only
                            `tools/eos/saas/auth/password_blocklist.py` and
                            its already-certified password-policy boundary;
                            no AuthRegistry, reset service, router, client,
                            database, or credential authority is changed.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10C1B-PASSWORD-BLOCKLIST-CERT certifies fixed provider
           identity, exact local SHA-1 range derivation, request privacy,
           response parsing, bounded failures, no retry/cache behavior,
           policy-protocol compatibility, and authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 awareness. This
            certificate makes no live-provider SLA or full NIST claim.
SECURITY / PRIVACY POSTURE: Only synthetic candidates and synthetic response
                            rows are used. Assertions prohibit plaintext,
                            full digest, suffix, credential, tenant, and
                            provider-secret leakage.
TENANT BOUNDARY: No tenant, principal, account, role, membership, email, or
                 username authority exists at this adapter boundary.
AUTHORITY BOUNDARY: External blocklist capability only; no hashing,
                    credential mutation, revision, JWT, session, refresh,
                    recovery, MFA, delivery, route, Mongo, or financial
                    authority is exercised.
EXTERNAL CAPABILITY BOUNDARY: Tests observe the server-constructed fixed
                              HTTPS HIBP range request through a fake seam;
                              no caller-controlled host or path is accepted.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive
                              financial execution and settlement authority.
FAIL-CLOSED POSTURE: Every untrusted provider status, transport failure,
                     malformed row, encoding failure, and oversized response
                     remains a structured rejection rather than an allow.
"""
from __future__ import annotations

import ast
import hashlib
import inspect
import ssl
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import pytest

from tools.eos.saas.auth.password_blocklist import (
    MAX_RESPONSE_BYTES,
    PREFIX_HEX_CHARACTERS,
    PROVIDER_HOST,
    PROVIDER_SCHEME,
    RANGE_PATH_PREFIX,
    SHA1_SUFFIX_HEX_CHARACTERS,
    USER_AGENT,
    VERSION,
    PwnedPasswordBlocklistChecker,
    PasswordBlocklistProviderCode,
    PasswordBlocklistProviderError,
)
from tools.eos.saas.auth.password_policy import PasswordPolicyCode, PasswordPolicyViolation, validate_password


_ADAPTER_PATH = Path(__file__).resolve().parents[2] / "tools/eos/saas/auth/password_blocklist.py"
_EXPECTED_VERSION = "v1.0.0-R10C1B-PASSWORD-BLOCKLIST-CERT"
_POLICY_CANDIDATE = "synthetic policy candidate"


class RecordingTransport:
    """Deterministic transport double recording the actual request seam."""

    def __init__(
        self,
        *,
        status: Any = 200,
        body: Any = b"A" * SHA1_SUFFIX_HEX_CHARACTERS + b":0\n",
        failure: BaseException | None = None,
        result_override: Any = None,
    ) -> None:
        self.status = status
        self.body = body
        self.failure = failure
        self.result_override = result_override
        self.calls: list[dict[str, Any]] = []

    def get(self, **kwargs: Any) -> Any:
        self.calls.append(dict(kwargs))
        if self.failure is not None:
            raise self.failure
        if self.result_override is not None:
            return self.result_override
        return self.status, self.body


def _sha1_parts(candidate: str) -> tuple[str, str, str]:
    """Calculate the independently expected exact UTF-8 SHA-1 range parts."""

    digest = hashlib.sha1(candidate.encode("utf-8")).hexdigest().upper()
    return digest, digest[:PREFIX_HEX_CHARACTERS], digest[PREFIX_HEX_CHARACTERS:]


def _range_body(*rows: tuple[str, int], ending: str = "\n") -> bytes:
    """Build synthetic provider rows without implementing adapter parsing."""

    return ("".join(f"{suffix}:{count}\n" for suffix, count in rows).rstrip("\n") + ending).encode("ascii")


def _checker(candidate: str, transport: RecordingTransport) -> bool:
    """Invoke the actual concrete adapter with only its production seam."""

    return PwnedPasswordBlocklistChecker(transport=transport).is_blocked(candidate)


def _provider_error(candidate: str, transport: RecordingTransport) -> PasswordBlocklistProviderError:
    """Capture one structured failure and assert candidate-free diagnostics."""

    digest, _, suffix = _sha1_parts(candidate)
    with pytest.raises(PasswordBlocklistProviderError) as captured:
        _checker(candidate, transport)
    error = captured.value
    assert candidate not in str(error)
    assert candidate not in repr(error)
    assert digest not in str(error)
    assert suffix not in str(error)
    assert transport.calls == [transport.calls[0]]
    return error


def test_version_and_public_api_are_exact() -> None:
    """The certificate targets the frozen adapter identity and callable seam."""

    assert VERSION == "v1.0.0-R10C1B-PASSWORD-BLOCKLIST-ADAPTER"
    assert PROVIDER_SCHEME == "https"
    assert PROVIDER_HOST == "api.pwnedpasswords.com"
    assert RANGE_PATH_PREFIX == "/range/"
    assert PREFIX_HEX_CHARACTERS == 5
    assert SHA1_SUFFIX_HEX_CHARACTERS == 35
    assert MAX_RESPONSE_BYTES > 0
    assert USER_AGENT.startswith("Wilsy-OS-Password-Blocklist/")
    assert list(inspect.signature(PwnedPasswordBlocklistChecker.is_blocked).parameters) == ["self", "candidate"]


@pytest.mark.parametrize(
    "candidate",
    [
        "  leading synthetic space",
        "trailing synthetic space  ",
        "internal  synthetic spaces",
        "Unicode café 東京 candidate",
        "MiXeD CaSe synthetic candidate",
    ],
)
def test_exact_utf8_sha1_prefix_and_fixed_request_identity(candidate: str) -> None:
    """Exact candidate bytes determine only the five-character URL prefix."""

    digest, prefix, suffix = _sha1_parts(candidate)
    transport = RecordingTransport(body=_range_body(("0" * 35, 0)))
    assert _checker(candidate, transport) is False
    assert len(transport.calls) == 1
    request = transport.calls[0]
    assert set(request) == {"url", "headers", "timeout_seconds", "max_response_bytes"}
    parsed = urlsplit(request["url"])
    assert parsed.scheme == PROVIDER_SCHEME
    assert parsed.netloc == PROVIDER_HOST
    assert parsed.path == f"{RANGE_PATH_PREFIX}{prefix}"
    assert len(parsed.path.rsplit("/", 1)[-1]) == PREFIX_HEX_CHARACTERS
    assert all(character in "0123456789ABCDEF" for character in prefix)
    assert parsed.query == ""
    assert parsed.fragment == ""
    assert request["headers"]["Add-Padding"] == "true"
    assert request["headers"]["User-Agent"] == USER_AGENT
    assert request["max_response_bytes"] == MAX_RESPONSE_BYTES
    assert request["timeout_seconds"] > 0
    for secret in (candidate, digest, suffix):
        assert secret not in request["url"]
        assert secret not in repr(request["headers"])


def test_request_contains_no_body_query_or_identity_secrets() -> None:
    """The GET seam exposes only fixed URL, headers, timeout, and response bound."""

    candidate = "sentinel email user tenant principal jwt refresh token"
    _, prefix, suffix = _sha1_parts(candidate)
    transport = RecordingTransport(body=_range_body(("F" * 35, 0)))
    assert _checker(candidate, transport) is False
    request = transport.calls[0]
    assert "body" not in request
    assert urlsplit(request["url"]).query == ""
    assert urlsplit(request["url"]).fragment == ""
    for secret in (candidate, suffix, "bcrypt", "Authorization", "Bearer"):
        assert secret not in repr(request)
    assert request["url"].endswith(prefix)


@pytest.mark.parametrize("count", [1, 7, 2_000_000])
def test_positive_matching_suffix_blocks(count: int) -> None:
    """Any positive matching exposure count is a blocked result."""

    candidate = "synthetic positive match candidate"
    _, _, suffix = _sha1_parts(candidate)
    transport = RecordingTransport(body=_range_body((suffix, count)))
    assert _checker(candidate, transport) is True
    assert len(transport.calls) == 1


def test_absent_match_is_false_only_for_a_valid_response() -> None:
    """A valid body without the candidate suffix is the only absent result."""

    candidate = "synthetic absent match candidate"
    _, _, suffix = _sha1_parts(candidate)
    unrelated = "0" * 35 if suffix != "0" * 35 else "1" * 35
    transport = RecordingTransport(body=_range_body((unrelated, 4)))
    assert _checker(candidate, transport) is False
    assert len(transport.calls) == 1


def test_zero_count_padding_does_not_block_and_unrelated_padding_is_ignored() -> None:
    """Matching and unrelated zero-count padded rows both remain allowed."""

    candidate = "synthetic zero padding candidate"
    _, _, suffix = _sha1_parts(candidate)
    unrelated = "A" * 35 if suffix != "A" * 35 else "B" * 35
    transport = RecordingTransport(body=_range_body((unrelated, 0), (suffix.lower(), 0)))
    assert _checker(candidate, transport) is False


@pytest.mark.parametrize("ending", ["\n", "", "\r\n"])
def test_legitimate_line_endings_are_parsed(ending: str) -> None:
    """Provider suffix casing and documented line-ending variants are accepted."""

    candidate = "synthetic line ending candidate"
    _, _, suffix = _sha1_parts(candidate)
    transport = RecordingTransport(body=_range_body((suffix.lower(), 1), ending=ending))
    assert _checker(candidate, transport) is True


def test_duplicate_suffix_behavior_is_deterministic_positive_wins() -> None:
    """The current parser deterministically treats any positive duplicate as blocked."""

    candidate = "synthetic duplicate candidate"
    _, _, suffix = _sha1_parts(candidate)
    transport = RecordingTransport(body=_range_body((suffix, 0), (suffix, 2)))
    assert _checker(candidate, transport) is True


@pytest.mark.parametrize(
    "body",
    [
        b"A" * 34 + b":1\n",
        b"A" * 36 + b":1\n",
        b"G" * 35 + b":1\n",
        b"A" * 35,
        b"A" * 35 + b":1:2\n",
        b"A" * 35 + b":\n",
        b"A" * 35 + b":not-a-count\n",
        b"A" * 35 + b":-1\n",
        b"A" * 35 + b":1.5\n",
        b"A" * 35 + b": 1\n",
        b"A" * 35 + b":1\n\nA" * 1,
        b"\xff\n",
    ],
)
def test_malformed_response_matrix_fails_closed(body: bytes) -> None:
    """Every substantive malformed row raises instead of becoming allow."""

    candidate = "synthetic malformed response candidate"
    transport = RecordingTransport(body=body)
    error = _provider_error(candidate, transport)
    assert error.code in {
        PasswordBlocklistProviderCode.MALFORMED_RESPONSE,
        PasswordBlocklistProviderCode.RESPONSE_ENCODING_FAILURE,
    }
    assert len(transport.calls) == 1


@pytest.mark.parametrize("status", [301, 302, 400, 401, 403, 404, 429, 500, 503])
def test_all_non_200_statuses_fail_closed_without_retry(status: int) -> None:
    """Redirects and provider errors never become an allow or a retry loop."""

    candidate = "synthetic status candidate"
    transport = RecordingTransport(status=status, body=b"provider body is not exposed")
    error = _provider_error(candidate, transport)
    assert error.code is PasswordBlocklistProviderCode.NON_200_RESPONSE
    assert len(transport.calls) == 1


@pytest.mark.parametrize(
    "failure",
    [TimeoutError("synthetic timeout"), OSError("synthetic dns failure"), ConnectionError("synthetic refused"), ssl.SSLError("synthetic tls"), ConnectionResetError("synthetic reset"), RuntimeError("synthetic transport failure")],
)
def test_transport_failures_fail_closed_without_retry(failure: BaseException) -> None:
    """Timeout, DNS-like, TLS, reset, and generic failures remain bounded."""

    candidate = "synthetic network candidate"
    transport = RecordingTransport(failure=failure)
    error = _provider_error(candidate, transport)
    assert error.code is PasswordBlocklistProviderCode.NETWORK_FAILURE
    assert len(transport.calls) == 1


def test_response_size_boundary_is_bounded_and_not_truncated_to_allow() -> None:
    """An in-bound valid body is authoritative; an over-bound body rejects."""

    candidate = "synthetic response size candidate"
    _, _, suffix = _sha1_parts(candidate)
    valid_body = _range_body((suffix, 1))
    assert len(valid_body) <= MAX_RESPONSE_BYTES
    assert _checker(candidate, RecordingTransport(body=valid_body)) is True
    oversized = RecordingTransport(body=b"A" * (MAX_RESPONSE_BYTES + 1))
    error = _provider_error(candidate, oversized)
    assert error.code is PasswordBlocklistProviderCode.RESPONSE_TOO_LARGE
    assert len(oversized.calls) == 1


def test_provider_errors_do_not_expose_password_digest_or_suffix() -> None:
    """Failure diagnostics contain only stable provider error codes."""

    candidate = "distinctive secret sentinel candidate"
    digest, _, suffix = _sha1_parts(candidate)
    for transport in (
        RecordingTransport(status=503, body=b"secret provider response"),
        RecordingTransport(failure=TimeoutError("secret timeout")),
        RecordingTransport(body=b"malformed secret response"),
        RecordingTransport(body=b"A" * (MAX_RESPONSE_BYTES + 1)),
    ):
        error = _provider_error(candidate, transport)
        assert candidate not in repr(error)
        assert digest not in repr(error)
        assert suffix not in repr(error)


def test_repeated_lookup_is_repeated_transport_not_cache() -> None:
    """No password-derived response cache suppresses the second request."""

    candidate = "synthetic repeated lookup candidate"
    transport = RecordingTransport(body=_range_body(("0" * 35, 0)))
    checker = PwnedPasswordBlocklistChecker(transport=transport)
    assert checker.is_blocked(candidate) is False
    assert checker.is_blocked(candidate) is False
    assert len(transport.calls) == 2


def test_transport_injection_cannot_change_fixed_endpoint() -> None:
    """The fake observes production-built identity rather than selecting it."""

    candidate = "synthetic fixed endpoint candidate"
    _, prefix, _ = _sha1_parts(candidate)
    transport = RecordingTransport(body=_range_body(("0" * 35, 0)))
    assert _checker(candidate, transport) is False
    request = transport.calls[0]
    assert request["url"] == f"https://{PROVIDER_HOST}{RANGE_PATH_PREFIX}{prefix}"
    assert "base_url" not in request
    assert "host" not in request
    assert "path" not in request


def test_policy_protocol_integration_is_exact_and_fail_closed() -> None:
    """The concrete adapter can be passed to the certified policy unchanged."""

    allowed_transport = RecordingTransport(body=_range_body(("0" * 35, 0)))
    allowed = PwnedPasswordBlocklistChecker(transport=allowed_transport)
    assert callable(allowed.is_blocked)
    assert validate_password(_POLICY_CANDIDATE, checker=allowed) is None

    blocked_candidate = "synthetic policy blocked candidate"
    _, _, blocked_suffix = _sha1_parts(blocked_candidate)
    blocked = PwnedPasswordBlocklistChecker(transport=RecordingTransport(body=_range_body((blocked_suffix, 1))))
    with pytest.raises(PasswordPolicyViolation) as blocked_error:
        validate_password(blocked_candidate, checker=blocked)
    assert blocked_error.value.code is PasswordPolicyCode.BLOCKED

    failing = PwnedPasswordBlocklistChecker(transport=RecordingTransport(failure=TimeoutError()))
    with pytest.raises(PasswordPolicyViolation) as provider_error:
        validate_password(_POLICY_CANDIDATE, checker=failing)
    assert provider_error.value.code is PasswordPolicyCode.BLOCKLIST_FAILURE


def test_authority_boundary_excludes_auth_database_and_financial_modules() -> None:
    """Static imports and calls confirm this adapter owns external capability only."""

    source = _ADAPTER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(_ADAPTER_PATH))
    imported_modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)
    forbidden_modules = {
        "bcrypt",
        "pymongo",
        "jwt",
        "requests",
        "httpx",
        "fastapi",
        "pyotp",
        "smtplib",
        "tools.eos.saas.auth.auth_registry",
        "tools.eos.saas.auth.password_recovery_registry",
        "tools.eos.kernel.db",
    }
    assert forbidden_modules.isdisjoint(imported_modules)
    call_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert {"MongoClient", "hashpw", "checkpw", "urlopen", "sleep"}.isdisjoint(call_names)
    assert "client.post" not in source


# ARTIFACT: test_password_blocklist.py
# VERSION: v1.0.0-R10C1B-PASSWORD-BLOCKLIST-CERT
# AUTHORITY BOUNDARY: direct offline evidence for external blocklist capability only
# EXTERNAL CAPABILITY BOUNDARY: fixed HIBP HTTPS range request observed through deterministic fake transport
# TENANT POSTURE: no tenant, principal, account, membership, or financial authority
# FAIL-CLOSED POSTURE: provider uncertainty, malformed evidence, and privacy-boundary violations fail certification
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
