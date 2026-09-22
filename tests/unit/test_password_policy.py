"""Direct unit certificate for the WILSY OS password-policy contract.

TITLE: WILSY OS Password Policy Direct Certificate
VERSION: v1.0.0-R10C1-PASSWORD-POLICY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Independently certifies the pure prospective-password policy against
         deterministic synthetic blocklist capabilities without hashing,
         persistence, network access, authentication mutation, or recovery
         authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_policy.py
COLLABORATION / OWNERSHIP: Tests only
                            `tools/eos/saas/auth/password_policy.py`;
                            registration, reset, JWT, session, Mongo, and
                            financial authorities remain outside this file.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10C1-PASSWORD-POLICY-CERT certifies exact length and
           bcrypt-byte boundaries, Unicode/control semantics, no-composition
           behavior, fail-closed blocklist handling, context rejection,
           secret hygiene, and authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 awareness. This
            certificate does not claim full NIST SP 800-63 compliance.
SECURITY / PRIVACY POSTURE: Every candidate is synthetic test data. Assertions
                            require policy errors and representations to omit
                            candidate material; no secrets, hashes, tokens, or
                            provider credentials are used.
TENANT BOUNDARY: No tenant or principal is resolved. Context terms are
                 ephemeral exact values supplied only to the policy call.
AUTHORITY BOUNDARY: Unit evidence for validation policy only; no password
                    hashing, credential mutation, Mongo, JWT, session,
                    refresh, recovery, MFA, delivery, HTTP, or financial
                    authority is exercised.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive
                              financial execution and settlement authority.
FAIL-CLOSED POSTURE: Missing, raising, malformed, or blocked checker results
                     must reject deterministically without secret-bearing
                     diagnostics.
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import Any

import pytest

from tools.eos.saas.auth.password_policy import (
    BCRYPT_MAX_INPUT_BYTES,
    MAX_PASSWORD_CHARACTERS,
    MIN_PASSWORD_CHARACTERS,
    PasswordPolicyCode,
    PasswordPolicyViolation,
    VERSION,
    validate_password,
)


_POLICY_PATH = Path(__file__).resolve().parents[2] / "tools/eos/saas/auth/password_policy.py"
_EXPECTED_POLICY_VERSION = "v1.0.0-R10C1-PASSWORD-POLICY"


class RecordingChecker:
    """Synthetic checker that records exact candidate forwarding only."""

    def __init__(self, result: Any = False) -> None:
        self.result = result
        self.candidates: list[str] = []

    def is_blocked(self, candidate: str) -> Any:
        self.candidates.append(candidate)
        return self.result


class RaisingChecker:
    """Synthetic provider failure whose message contains no candidate."""

    def __init__(self) -> None:
        self.candidates: list[str] = []

    def is_blocked(self, candidate: str) -> bool:
        self.candidates.append(candidate)
        raise RuntimeError("synthetic blocklist provider failure")


def _assert_rejected(
    candidate: Any,
    expected: PasswordPolicyCode,
    *,
    checker: Any = None,
    context_terms: Any = None,
) -> PasswordPolicyViolation:
    """Assert one candidate-free structured policy rejection."""

    with pytest.raises(PasswordPolicyViolation) as captured:
        validate_password(candidate, checker=checker, context_terms=context_terms)
    error = captured.value
    assert error.code is expected
    assert candidate is None or not isinstance(candidate, str) or not candidate or candidate not in str(error)
    assert candidate is None or not isinstance(candidate, str) or not candidate or candidate not in repr(error)
    return error


def test_policy_version_and_public_signature_are_frozen() -> None:
    """The certificate targets the exact R10C1 public contract."""

    assert VERSION == _EXPECTED_POLICY_VERSION
    assert MIN_PASSWORD_CHARACTERS == 15
    assert MAX_PASSWORD_CHARACTERS == 64
    assert BCRYPT_MAX_INPUT_BYTES == 72
    signature = inspect.signature(validate_password)
    assert list(signature.parameters) == ["candidate", "checker", "context_terms"]
    assert signature.parameters["checker"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["context_terms"].kind is inspect.Parameter.KEYWORD_ONLY


def test_code_point_length_boundaries_fail_closed() -> None:
    """Fourteen and sixty-five code points reject; fifteen and sixty-four pass."""

    checker = RecordingChecker(False)
    _assert_rejected("a" * 14, PasswordPolicyCode.TOO_SHORT, checker=checker)
    _assert_rejected("", PasswordPolicyCode.TOO_SHORT, checker=checker)
    assert validate_password("a" * 15, checker=checker) is None
    assert validate_password("a" * 64, checker=checker) is None
    _assert_rejected("a" * 65, PasswordPolicyCode.TOO_LONG, checker=checker)


def test_non_string_candidate_fails_with_invalid_input_category() -> None:
    """The policy does not coerce arbitrary objects into password text."""

    _assert_rejected(object(), PasswordPolicyCode.INVALID_INPUT, checker=RecordingChecker(False))


def test_bcrypt_utf8_byte_boundary_is_separate_from_code_point_length() -> None:
    """UTF-8 bytes are checked without truncation or pre-hashing."""

    exact_72 = "é" * 36
    assert len(exact_72) == 36
    assert len(exact_72.encode("utf-8")) == BCRYPT_MAX_INPUT_BYTES
    checker = RecordingChecker(False)
    assert validate_password(exact_72, checker=checker) is None
    assert checker.candidates == [exact_72]

    seventy_three = ("é" * 36) + "a"
    assert len(seventy_three.encode("utf-8")) == 73
    _assert_rejected(seventy_three, PasswordPolicyCode.BCRYPT_BYTE_LIMIT, checker=checker)

    within_code_point_limit_but_too_many_bytes = "é" * 37
    assert len(within_code_point_limit_but_too_many_bytes) < MAX_PASSWORD_CHARACTERS
    assert len(within_code_point_limit_but_too_many_bytes.encode("utf-8")) > 72
    _assert_rejected(
        within_code_point_limit_but_too_many_bytes,
        PasswordPolicyCode.BCRYPT_BYTE_LIMIT,
        checker=checker,
    )


def test_no_character_composition_rule_is_introduced() -> None:
    """Long otherwise-valid passwords need no case, digit, or symbol mixture."""

    checker = RecordingChecker(False)
    assert validate_password("lowercase letters only", checker=checker) is None
    assert validate_password("letterswithoutdigits", checker=checker) is None
    assert validate_password("embedded spaces in a long phrase", checker=checker) is None
    assert len(checker.candidates) == 3


def test_spaces_are_significant_and_not_silently_stripped_or_collapsed() -> None:
    """The checker receives leading, trailing, and internal spaces exactly."""

    candidate = "  leading and trailing  "
    checker = RecordingChecker(False)
    assert validate_password(candidate, checker=checker) is None
    assert checker.candidates == [candidate]
    assert checker.candidates[0] != candidate.strip()
    assert "  " in checker.candidates[0]


def test_legitimate_unicode_passes_without_normalization() -> None:
    """Ordinary Unicode is accepted and reaches the checker byte-for-byte."""

    candidate = "éclair café 東京!"
    assert len(candidate) >= MIN_PASSWORD_CHARACTERS
    checker = RecordingChecker(False)
    assert validate_password(candidate, checker=checker) is None
    assert checker.candidates == [candidate]


@pytest.mark.parametrize(
    "candidate",
    [
        "valid-prefix-\x00-suffix",
        "valid-prefix-\x1f-suffix",
        "valid-prefix-\x7f-suffix",
        "valid-prefix-\x9f-suffix",
        "valid-prefix-\ud800-suffix",
        "valid-prefix-\udfff-suffix",
    ],
)
def test_controls_and_lone_surrogates_are_prohibited(candidate: str) -> None:
    """Representative C0, C1, and surrogate states fail before blocklist use."""

    checker = RecordingChecker(False)
    _assert_rejected(candidate, PasswordPolicyCode.PROHIBITED_INPUT, checker=checker)
    assert checker.candidates == []


def test_blocklist_false_is_required_and_allows_otherwise_valid_input() -> None:
    """A trustworthy literal False checker decision permits the candidate."""

    checker = RecordingChecker(False)
    candidate = "synthetic allowed passphrase"
    assert validate_password(candidate, checker=checker) is None
    assert checker.candidates == [candidate]


def test_blocklist_true_rejects_with_stable_category() -> None:
    """A literal True checker decision is a blocked-password rejection."""

    candidate = "synthetic blocked passphrase"
    _assert_rejected(candidate, PasswordPolicyCode.BLOCKED, checker=RecordingChecker(True))


def test_missing_checker_fails_closed_when_runtime_boundary_allows_none() -> None:
    """The optional runtime annotation cannot weaken the mandatory capability."""

    _assert_rejected(
        "synthetic missing checker",
        PasswordPolicyCode.BLOCKLIST_UNAVAILABLE,
        checker=None,
    )


def test_raising_checker_fails_closed_without_provider_exception_or_secret() -> None:
    """Provider failures become bounded errors and never expose candidate text."""

    candidate = "synthetic raising checker secret"
    checker = RaisingChecker()
    error = _assert_rejected(candidate, PasswordPolicyCode.BLOCKLIST_FAILURE, checker=checker)
    assert checker.candidates == [candidate]
    assert candidate not in str(error)
    assert candidate not in repr(error)


@pytest.mark.parametrize("result", [None, 1, "false"])
def test_invalid_checker_results_fail_closed(result: Any) -> None:
    """Non-boolean provider output is not treated as an allow decision."""

    _assert_rejected(
        "synthetic invalid checker result",
        PasswordPolicyCode.BLOCKLIST_FAILURE,
        checker=RecordingChecker(result),
    )


def test_context_terms_are_exact_ephemeral_rejections() -> None:
    """Exact service/account terms reject without persistence or fuzzy scoring."""

    candidate = "wilsy os service account"
    checker = RecordingChecker(False)
    _assert_rejected(
        candidate,
        PasswordPolicyCode.CONTEXT_MATCH,
        checker=checker,
        context_terms=("other term", candidate),
    )
    assert checker.candidates == []
    assert validate_password(candidate, checker=RecordingChecker(False), context_terms=("other",)) is None
    _assert_rejected(
        candidate,
        PasswordPolicyCode.CONTEXT_INVALID,
        checker=RecordingChecker(False),
        context_terms=("valid", 7),
    )


def test_policy_error_has_no_candidate_state_or_secret_bearing_diagnostics() -> None:
    """The structured exception stores only its stable policy code."""

    candidate = "synthetic secret candidate for diagnostics"
    error = _assert_rejected(candidate, PasswordPolicyCode.BLOCKED, checker=RecordingChecker(True))
    assert vars(error) == {"code": PasswordPolicyCode.BLOCKED}
    assert candidate not in str(error)
    assert candidate not in repr(error)


def test_production_module_has_no_external_authority_imports_or_persistence_calls() -> None:
    """Static boundary evidence excludes hashing, storage, transport, and JWT."""

    source = _POLICY_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(_POLICY_PATH))
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
        "smtplib",
        "pyotp",
        "tools.eos.saas.auth.password_recovery_registry",
    }
    assert forbidden_modules.isdisjoint(imported_modules)
    call_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert {"MongoClient", "hashpw", "checkpw", "encode", "decode"}.isdisjoint(call_names)
    assert "password_policy.py" in source
    assert "END OF WILSY OS SOVEREIGN ARTIFACT" in source


# ARTIFACT: test_password_policy.py
# VERSION: v1.0.0-R10C1-PASSWORD-POLICY-CERT
# AUTHORITY BOUNDARY: direct unit evidence for pure prospective-password policy only
# TENANT POSTURE: no tenant, principal, membership, or account authority
# FAIL-CLOSED POSTURE: every mandatory policy dependency and invalid input path is rejected deterministically
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
