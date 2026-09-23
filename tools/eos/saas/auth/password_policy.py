"""Canonical prospective-password policy for WILSY OS authentication.

TITLE: WILSY OS Password Policy Contract
VERSION: v1.0.0-R10C1-PASSWORD-POLICY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Defines one deterministic, fail-closed validation contract for a
         prospective password before a caller delegates hashing or durable
         credential mutation to its separate authority. This artifact does not
         own password state, blocklist transport, or authentication lifecycle.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_policy.py
COLLABORATION / OWNERSHIP: Registration, future authenticated-change, and
                           future recovery services may call
                           `validate_password`; each caller retains hashing,
                           persistence, transaction, and credential authority.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10C1-PASSWORD-POLICY establishes Unicode code-point and
           bcrypt-byte boundaries, exact-input semantics, bounded context
           rejection, and an explicit fail-closed blocklist dependency.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 awareness. This
            pure contract does not by itself establish full NIST SP 800-63
            compliance because operational blocklist delivery, rate limiting,
            and authenticator management remain outside this artifact.
SECURITY / PRIVACY POSTURE: Candidate text is never placed in policy state,
                            errors, repr output, logs, or serialized values.
                            The injected checker receives the candidate only
                            for its own bounded decision and is not implemented
                            or contacted here.
TENANT BOUNDARY: No tenant, principal, role, membership, or account identity
                 is resolved or persisted. Optional context terms are
                 caller-supplied comparison values and are not retained.
AUTHORITY BOUNDARY: Validation policy only; no hashing, hash verification,
                    Mongo, JWT, session, refresh, recovery, MFA, delivery,
                    HTTP, or credential-revision authority.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive
                              financial execution and settlement authority.
"""

from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum
from typing import Final, NoReturn, Protocol


VERSION: Final[str] = "v1.0.0-R10C1-PASSWORD-POLICY"
MIN_PASSWORD_CHARACTERS: Final[int] = 15
MAX_PASSWORD_CHARACTERS: Final[int] = 64
BCRYPT_MAX_INPUT_BYTES: Final[int] = 72


class PasswordPolicyCode(StrEnum):
    """Stable, candidate-free classifications for policy rejection.

    The code is safe for caller-facing control flow. It contains no password,
    hash, provider configuration, timestamp, tenant identity, or diagnostic
    detail. The policy itself owns no mutation or transaction lifecycle.
    """

    INVALID_INPUT = "PASSWORD_POLICY_INVALID_INPUT"
    TOO_SHORT = "PASSWORD_POLICY_TOO_SHORT"
    TOO_LONG = "PASSWORD_POLICY_TOO_LONG"
    BCRYPT_BYTE_LIMIT = "PASSWORD_POLICY_BCRYPT_BYTE_LIMIT"
    PROHIBITED_INPUT = "PASSWORD_POLICY_PROHIBITED_INPUT"
    CONTEXT_INVALID = "PASSWORD_POLICY_CONTEXT_INVALID"
    CONTEXT_MATCH = "PASSWORD_POLICY_CONTEXT_MATCH"
    BLOCKLIST_UNAVAILABLE = "PASSWORD_POLICY_BLOCKLIST_UNAVAILABLE"
    BLOCKLIST_FAILURE = "PASSWORD_POLICY_BLOCKLIST_FAILURE"
    BLOCKED = "PASSWORD_POLICY_BLOCKED"


class PasswordPolicyViolation(ValueError):
    """Structured fail-closed policy rejection without secret-bearing detail.

    Authority: this exception represents validation policy only. It never
    hashes, stores, logs, or transforms a candidate and does not own a
    transaction. Callers may inspect ``code`` and decide their own bounded
    response while retaining tenant and financial authority elsewhere.
    """

    def __init__(self, code: PasswordPolicyCode) -> None:
        if not isinstance(code, PasswordPolicyCode):
            raise TypeError("password policy code is invalid")
        self.code = code
        super().__init__(code.value)

    def __str__(self) -> str:
        """Return only the stable rejection code, never candidate material."""

        return self.code.value

    def __repr__(self) -> str:
        """Return a deterministic candidate-free diagnostic representation."""

        return f"PasswordPolicyViolation(code={self.code.value!r})"


class PasswordBlocklistChecker(Protocol):
    """Narrow caller-supplied blocklist capability required by validation.

    The implementation may be local or separately governed, but this policy
    performs no network call and chooses fail-closed behavior when the
    capability is absent, raises, or returns anything other than ``bool``.
    The checker owns no persistence or authentication authority by virtue of
    satisfying this protocol.
    """

    def is_blocked(self, candidate: str) -> bool:
        """Return whether the supplied candidate is prohibited."""

        raise NotImplementedError("blocklist protocol method")


def _reject(code: PasswordPolicyCode) -> NoReturn:
    """Raise the stable policy error without retaining the candidate."""

    raise PasswordPolicyViolation(code)


def _has_prohibited_code_point(candidate: str) -> bool:
    """Detect C0/C1 controls and lone UTF-16 surrogate code points."""

    return any(
        ord(character) <= 0x1F
        or 0x7F <= ord(character) <= 0x9F
        or 0xD800 <= ord(character) <= 0xDFFF
        for character in candidate
    )


def _matches_context(candidate: str, context_terms: Iterable[str] | None) -> bool:
    """Apply exact, non-persistent context comparisons supplied by a caller."""

    if context_terms is None:
        return False
    try:
        for term in context_terms:
            if not isinstance(term, str):
                _reject(PasswordPolicyCode.CONTEXT_INVALID)
            if candidate == term:
                return True
    except PasswordPolicyViolation:
        raise
    except Exception:
        _reject(PasswordPolicyCode.CONTEXT_INVALID)
    return False


def _check_blocklist(
    candidate: str,
    checker: PasswordBlocklistChecker | None,
) -> None:
    """Require a trustworthy checker decision without exposing checker errors."""

    if checker is None:
        _reject(PasswordPolicyCode.BLOCKLIST_UNAVAILABLE)
    check = getattr(checker, "is_blocked", None)
    if not callable(check):
        _reject(PasswordPolicyCode.BLOCKLIST_UNAVAILABLE)
    try:
        blocked = check(candidate)
    except Exception:
        _reject(PasswordPolicyCode.BLOCKLIST_FAILURE)
    if not isinstance(blocked, bool):
        _reject(PasswordPolicyCode.BLOCKLIST_FAILURE)
    if blocked:
        _reject(PasswordPolicyCode.BLOCKED)


def validate_password(
    candidate: str,
    *,
    checker: PasswordBlocklistChecker | None,
    context_terms: Iterable[str] | None = None,
) -> None:
    """Validate one exact prospective password and return no transformed value.

    Authority: pure policy validation. The caller supplies the mandatory
    blocklist capability and optional exact context terms, then remains solely
    responsible for hashing, persistence, transaction/session ownership,
    tenant/principal resolution, credential revision, and any user response.
    The candidate is not stored on this function or a long-lived object.

    Mutation semantics: none. Mongo, JWT, session, refresh, recovery, MFA,
    delivery, HTTP, and financial authorities are intentionally absent.

    Failure semantics: raises ``PasswordPolicyViolation`` with a stable
    ``PasswordPolicyCode`` and no candidate-derived detail. Missing, invalid,
    blocked, or failing blocklist capability fails closed.

    Secret handling: the candidate is compared and encoded exactly as supplied;
    it is not stripped, case-transformed, normalized, truncated, hashed, or
    returned. Spaces and ordinary Unicode remain significant.

    Tenant and financial boundaries: context terms are ephemeral exact
    comparisons only; no tenant or financial authority is inferred.

    :param candidate: Complete prospective password text.
    :param checker: Required object implementing ``is_blocked(str) -> bool``.
    :param context_terms: Optional exact service/account terms to reject.
    :raises PasswordPolicyViolation: when any policy boundary is not met.
    """

    if not isinstance(candidate, str):
        _reject(PasswordPolicyCode.INVALID_INPUT)
    if len(candidate) < MIN_PASSWORD_CHARACTERS:
        _reject(PasswordPolicyCode.TOO_SHORT)
    if len(candidate) > MAX_PASSWORD_CHARACTERS:
        _reject(PasswordPolicyCode.TOO_LONG)
    if _has_prohibited_code_point(candidate):
        _reject(PasswordPolicyCode.PROHIBITED_INPUT)
    try:
        encoded = candidate.encode("utf-8")
    except UnicodeEncodeError:
        _reject(PasswordPolicyCode.PROHIBITED_INPUT)
    if len(encoded) > BCRYPT_MAX_INPUT_BYTES:
        _reject(PasswordPolicyCode.BCRYPT_BYTE_LIMIT)
    if _matches_context(candidate, context_terms):
        _reject(PasswordPolicyCode.CONTEXT_MATCH)
    _check_blocklist(candidate, checker)


__all__ = [
    "BCRYPT_MAX_INPUT_BYTES",
    "MAX_PASSWORD_CHARACTERS",
    "MIN_PASSWORD_CHARACTERS",
    "PasswordBlocklistChecker",
    "PasswordPolicyCode",
    "PasswordPolicyViolation",
    "VERSION",
    "validate_password",
]


# ARTIFACT: password_policy.py
# VERSION: v1.0.0-R10C1-PASSWORD-POLICY
# AUTHORITY BOUNDARY: pure prospective-password validation; no credential, persistence, or delivery authority
# TENANT POSTURE: no tenant or principal resolution; context terms are ephemeral exact comparisons
# FAIL-CLOSED POSTURE: absent, invalid, blocked, or failing blocklist capability rejects deterministically
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
