"""Have I Been Pwned k-anonymity password blocklist adapter.

TITLE: WILSY OS Pwned Password Blocklist Adapter
VERSION: v1.0.0-R10C1B-PASSWORD-BLOCKLIST-ADAPTER
AUTHORITY: Wilsy OS Core Governance
EPITOME: Provides one fixed, privacy-preserving external capability for
         checking a complete prospective password against the Have I Been
         Pwned Pwned Passwords range service. It reports only a boolean
         blocklist result and never owns password policy, credentials, or
         lifecycle state.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_blocklist.py
COLLABORATION / OWNERSHIP: `password_policy.py` remains the canonical policy
                           decision authority. A future registration/change/
                           recovery caller may inject this adapter as its
                           `PasswordBlocklistChecker`; this module owns only
                           the provider capability and transport boundary.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10C1B-PASSWORD-BLOCKLIST-ADAPTER establishes fixed HTTPS
           HIBP range requests, local SHA-1 interoperability hashing,
           five-character k-anonymity transmission, bounded parsing, and
           deterministic fail-closed provider errors.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 awareness. The
            adapter is an external capability and does not by itself establish
            full NIST SP 800-63 compliance or password-management compliance.
SECURITY / PRIVACY POSTURE: The complete password remains in process. Only
                            the first five uppercase SHA-1 hexadecimal
                            characters are transmitted. The suffix, full
                            digest, password, account identity, tenant data,
                            response corpus, and provider errors are never
                            logged, persisted, or returned.
TENANT BOUNDARY: No tenant, principal, account, email, username, role, or
                 membership input is accepted or resolved.
AUTHORITY BOUNDARY: External blocklist capability only. No password hashing,
                    credential mutation, credential revision, JWT, session,
                    refresh, recovery, MFA, delivery, router, database, or
                    financial authority is owned here.
EXTERNAL CAPABILITY BOUNDARY: HTTPS access is fixed to
                              `api.pwnedpasswords.com/range/{prefix}`;
                              callers cannot provide a base URL or redirect
                              destination. Provider failure fails closed.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive
                              financial execution and settlement authority.
FAIL-CLOSED POSTURE: Missing transport trust, network failure, non-200 status,
                     oversized or malformed response, invalid encoding, and
                     invalid response rows raise a bounded provider error;
                     only a valid response with no positive matching suffix
                     returns False.
"""
from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
import hashlib
from typing import Final, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from tools.eos.saas.auth.password_policy import PasswordBlocklistChecker


VERSION: Final[str] = "v1.0.0-R10C1B-PASSWORD-BLOCKLIST-ADAPTER"
PROVIDER_HOST: Final[str] = "api.pwnedpasswords.com"
PROVIDER_SCHEME: Final[str] = "https"
RANGE_PATH_PREFIX: Final[str] = "/range/"
USER_AGENT: Final[str] = "Wilsy-OS-Password-Blocklist/1.0.0-R10C1B"
DEFAULT_TIMEOUT_SECONDS: Final[float] = 5.0
MAX_TIMEOUT_SECONDS: Final[float] = 30.0
MAX_RESPONSE_BYTES: Final[int] = 131_072
PREFIX_HEX_CHARACTERS: Final[int] = 5
SHA1_HEX_CHARACTERS: Final[int] = 40
SHA1_SUFFIX_HEX_CHARACTERS: Final[int] = 35


class PasswordBlocklistProviderCode(StrEnum):
    """Candidate-free classifications for external-provider failures."""

    INVALID_INPUT = "PASSWORD_BLOCKLIST_INVALID_INPUT"
    INVALID_CONFIGURATION = "PASSWORD_BLOCKLIST_INVALID_CONFIGURATION"
    TRANSPORT_FAILURE = "PASSWORD_BLOCKLIST_TRANSPORT_FAILURE"
    NETWORK_FAILURE = "PASSWORD_BLOCKLIST_NETWORK_FAILURE"
    NON_200_RESPONSE = "PASSWORD_BLOCKLIST_NON_200_RESPONSE"
    RESPONSE_TOO_LARGE = "PASSWORD_BLOCKLIST_RESPONSE_TOO_LARGE"
    RESPONSE_ENCODING_FAILURE = "PASSWORD_BLOCKLIST_RESPONSE_ENCODING_FAILURE"
    MALFORMED_RESPONSE = "PASSWORD_BLOCKLIST_MALFORMED_RESPONSE"


class PasswordBlocklistProviderError(RuntimeError):
    """Structured provider failure that never exposes password-derived data.

    Authority: this exception represents only an unavailable or untrustworthy
    external blocklist capability. It does not grant or revoke credentials,
    persist state, own a transaction, or classify tenant or financial truth.
    The stable ``code`` is safe for bounded caller handling; provider bodies,
    URLs, hashes, prefixes, suffixes, and underlying exception text are
    intentionally discarded.
    """

    def __init__(self, code: PasswordBlocklistProviderCode) -> None:
        if not isinstance(code, PasswordBlocklistProviderCode):
            raise TypeError("password blocklist provider code is invalid")
        self.code = code
        super().__init__(code.value)

    def __str__(self) -> str:
        """Return only the stable, non-secret failure code."""

        return self.code.value

    def __repr__(self) -> str:
        """Return a deterministic diagnostic without provider details."""

        return f"PasswordBlocklistProviderError(code={self.code.value!r})"


class PasswordBlocklistTransport(Protocol):
    """Narrow testable transport seam for the fixed provider request.

    Implementations receive a server-constructed fixed HTTPS URL and bounded
    request metadata. They must return one HTTP status and raw response bytes;
    they do not receive tenant, account, password, digest, or suffix values.
    The production implementation is the private standard-library transport.
    """

    def get(
        self,
        *,
        url: str,
        headers: Mapping[str, str],
        timeout_seconds: float,
        max_response_bytes: int,
    ) -> tuple[int, bytes]:
        """Perform one bounded GET without redirecting to another authority."""

        raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.INVALID_CONFIGURATION)


class _NoRedirectHandler(HTTPRedirectHandler):
    """Disable urllib redirect following so provider identity cannot drift."""

    def redirect_request(self, *args: object, **kwargs: object) -> Request | None:
        return None


class _UrllibPasswordBlocklistTransport:
    """Production HTTPS transport with one request, no retry, and bounded read."""

    __slots__ = ("_opener",)

    def __init__(self) -> None:
        self._opener = build_opener(_NoRedirectHandler())

    def get(
        self,
        *,
        url: str,
        headers: Mapping[str, str],
        timeout_seconds: float,
        max_response_bytes: int,
    ) -> tuple[int, bytes]:
        """Fetch the fixed URL once and reject non-200 or oversized responses."""

        request = Request(url=url, method="GET", headers=dict(headers))
        try:
            with self._opener.open(request, timeout=timeout_seconds) as response:
                status = getattr(response, "status", None)
                body = response.read(max_response_bytes + 1)
        except HTTPError as error:
            raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.NON_200_RESPONSE) from None
        except (TimeoutError, URLError, OSError):
            raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.NETWORK_FAILURE) from None
        except Exception:
            raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.TRANSPORT_FAILURE) from None
        if isinstance(status, bool) or not isinstance(status, int):
            raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.TRANSPORT_FAILURE)
        if status != 200:
            raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.NON_200_RESPONSE)
        if not isinstance(body, bytes):
            raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.TRANSPORT_FAILURE)
        if len(body) > max_response_bytes:
            raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.RESPONSE_TOO_LARGE)
        return status, body


def _bounded_timeout(timeout_seconds: float) -> float:
    """Require a finite caller timeout within the server safety bound."""

    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)):
        raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.INVALID_CONFIGURATION)
    timeout = float(timeout_seconds)
    if timeout <= 0 or timeout > MAX_TIMEOUT_SECONDS:
        raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.INVALID_CONFIGURATION)
    return timeout


def _hash_candidate(candidate: str) -> tuple[str, str]:
    """Return uppercase prefix/suffix from exact UTF-8 candidate bytes locally."""

    if not isinstance(candidate, str) or not candidate:
        raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.INVALID_INPUT)
    try:
        digest = hashlib.sha1(candidate.encode("utf-8")).hexdigest().upper()
    except (UnicodeEncodeError, ValueError):
        raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.INVALID_INPUT) from None
    if len(digest) != SHA1_HEX_CHARACTERS:
        raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.INVALID_INPUT)
    return digest[:PREFIX_HEX_CHARACTERS], digest[PREFIX_HEX_CHARACTERS:]


def _parse_response(body: bytes, expected_suffix: str) -> bool:
    """Parse one valid HIBP range body and return positive-count match status."""

    try:
        text = body.decode("ascii")
    except UnicodeDecodeError:
        raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.RESPONSE_ENCODING_FAILURE) from None
    lines = text.replace("\r\n", "\n").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if not lines:
        raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.MALFORMED_RESPONSE)
    blocked = False
    for line in lines:
        if not line:
            raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.MALFORMED_RESPONSE)
        fields = line.split(":")
        if len(fields) != 2:
            raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.MALFORMED_RESPONSE)
        suffix, count_text = fields
        if len(suffix) != SHA1_SUFFIX_HEX_CHARACTERS or any(
            character not in "0123456789ABCDEFabcdef" for character in suffix
        ):
            raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.MALFORMED_RESPONSE)
        if not count_text.isdigit():
            raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.MALFORMED_RESPONSE)
        count = int(count_text)
        if suffix.upper() == expected_suffix and count > 0:
            blocked = True
    return blocked


class PwnedPasswordBlocklistChecker(PasswordBlocklistChecker):
    """Check complete passwords through HIBP's fixed k-anonymity range API.

    Authority: external compromised-password capability only. SHA-1 is used
    solely for provider interoperability; it is never a credential hash.
    Mutation semantics: none. This class does not hash with bcrypt, persist,
    cache, log, issue tokens, revoke sessions, or change any user state.
    Transaction semantics: none; one bounded HTTPS request is made per call.
    Failure semantics: provider or parser uncertainty raises
    ``PasswordBlocklistProviderError``. ``False`` means only that a valid
    response contained no positive-count matching suffix.
    Tenant and financial boundaries: no identity or tenant inputs are accepted;
    Kennel EOS remains the exclusive financial execution authority.

    The optional transport exists only as a narrow deterministic test seam. It
    cannot change the server-constructed provider host, scheme, path shape, or
    transmitted headers.
    """

    __slots__ = ("_timeout_seconds", "_transport")

    def __init__(
        self,
        *,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        transport: PasswordBlocklistTransport | None = None,
    ) -> None:
        """Construct a fixed-provider checker with finite timeout and no cache."""

        self._timeout_seconds = _bounded_timeout(timeout_seconds)
        self._transport = transport if transport is not None else _UrllibPasswordBlocklistTransport()
        if not callable(getattr(self._transport, "get", None)):
            raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.INVALID_CONFIGURATION)

    def __repr__(self) -> str:
        """Expose only fixed operational identity, never candidate material."""

        return f"PwnedPasswordBlocklistChecker(timeout_seconds={self._timeout_seconds!r})"

    def is_blocked(self, candidate: str) -> bool:
        """Return HIBP's positive-count result for one complete candidate.

        The plaintext candidate, full SHA-1 digest, and suffix never leave this
        process. Only the five-character uppercase prefix is placed in the
        fixed provider URL. No incremental or browser-side lookup is exposed.
        """

        prefix, suffix = _hash_candidate(candidate)
        url = f"{PROVIDER_SCHEME}://{PROVIDER_HOST}{RANGE_PATH_PREFIX}{prefix}"
        headers = {
            "Add-Padding": "true",
            "User-Agent": USER_AGENT,
            "Accept": "text/plain",
        }
        try:
            response = self._transport.get(
                url=url,
                headers=headers,
                timeout_seconds=self._timeout_seconds,
                max_response_bytes=MAX_RESPONSE_BYTES,
            )
        except PasswordBlocklistProviderError:
            raise
        except Exception:
            raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.NETWORK_FAILURE) from None
        if not isinstance(response, tuple) or len(response) != 2:
            raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.TRANSPORT_FAILURE)
        status, body = response
        if isinstance(status, bool) or not isinstance(status, int):
            raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.TRANSPORT_FAILURE)
        if status != 200:
            raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.NON_200_RESPONSE)
        if isinstance(body, bytearray):
            body = bytes(body)
        if not isinstance(body, bytes):
            raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.TRANSPORT_FAILURE)
        if len(body) > MAX_RESPONSE_BYTES:
            raise PasswordBlocklistProviderError(PasswordBlocklistProviderCode.RESPONSE_TOO_LARGE)
        return _parse_response(body, suffix)


__all__ = [
    "DEFAULT_TIMEOUT_SECONDS",
    "MAX_RESPONSE_BYTES",
    "MAX_TIMEOUT_SECONDS",
    "PREFIX_HEX_CHARACTERS",
    "PROVIDER_HOST",
    "PROVIDER_SCHEME",
    "PwnedPasswordBlocklistChecker",
    "PasswordBlocklistProviderCode",
    "PasswordBlocklistProviderError",
    "PasswordBlocklistTransport",
    "RANGE_PATH_PREFIX",
    "SHA1_SUFFIX_HEX_CHARACTERS",
    "USER_AGENT",
    "VERSION",
]


# ARTIFACT: password_blocklist.py
# VERSION: v1.0.0-R10C1B-PASSWORD-BLOCKLIST-ADAPTER
# AUTHORITY BOUNDARY: external HIBP compromised-password capability only; canonical policy remains password_policy.py
# EXTERNAL CAPABILITY BOUNDARY: fixed HTTPS api.pwnedpasswords.com range endpoint; five-character prefix only
# TENANT POSTURE: no tenant, principal, account, role, membership, or identity authority
# FAIL-CLOSED POSTURE: unavailable, malformed, oversized, redirected, or non-200 provider evidence rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
