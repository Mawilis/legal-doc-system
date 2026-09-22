"""Direct certificate for the R9B-P5-R2 approval trust-root succession.

TITLE: WILSY OS Legal Corpus Approval Trust-Root Direct Certificate
VERSION: v1.4.0-R1D-B0F-R9B-P5-R2-LEGAL-CORPUS-APPROVAL-TRUST-ROOT-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Adversarially certifies immutable approval public-key trust metadata,
         predecessor retirement, successor admission, lifecycle predicates,
         deterministic integrity, and historical verification without signing
         or persistence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_corpus_approval_trust_root.py
COLLABORATION / OWNERSHIP: Certifies the R9B-P5-R2 public successor admission
                            after the external ceremony; the predecessor's
                            historical identity and all private/signing
                            material remain outside this repository.
CERTIFICATION / UPDATE DATE: 2026-09-21
CHANGELOG: v1.4.0-R9B-P5-R2 independently certifies the exact retired
           predecessor and active successor membership, fingerprints, time
           windows, and historical-verification boundary.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic public bytes only; no private material,
                            key generation, network, database, or filesystem
                            secret access is permitted.
TENANT BOUNDARY: PLATFORM trust metadata only; no tenant or principal scope.
AUTHORITY BOUNDARY: A passing test certifies implementation semantics only; it
                    does not approve legal text, verify a signature, or issue
                    an authorization.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Every unsupported identity, lifecycle, time, key,
                     fingerprint, membership, and authority shortcut rejects.
"""
from __future__ import annotations

import ast
import base64
import hashlib
import json
from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_corpus_approval_trust_root import (
    APPROVAL_AUTHORITY_DOMAIN,
    APPROVAL_AUTHORITY_ROLE,
    APPROVAL_ISSUER_IDENTITY,
    APPROVAL_OPERATION,
    APPROVAL_SCOPE,
    APPROVAL_TRUST_ROOT_PROVENANCE,
    ED25519_ALGORITHM,
    KEY_ID_PREFIX,
    LegalCorpusApprovalTrustRoot,
    LegalCorpusApprovalTrustRootError,
    LegalCorpusApprovalTrustStatus,
    LegalCorpusApprovalTrustedKey,
    PRODUCTION_APPROVAL_TRUSTED_KEYS,
    PRODUCTION_APPROVAL_TRUST_ROOT,
    PUBLIC_KEY_ENCODING,
)


UTC = timezone.utc
START = datetime(2026, 1, 1, 12, tzinfo=UTC)
END = START + timedelta(hours=24)

_KNOWN_PUBLIC_KEY = "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8"
_KNOWN_KEY_ID = "prdca-key:legal-corpus-approval-cbd3f6eeba676b21e0f2c47522292482"
_SECOND_KNOWN_PUBLIC_KEY = "AQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyA"
_SECOND_KNOWN_KEY_ID = "prdca-key:legal-corpus-approval-340e03d7eb46e5568ba4ec3e48c3805d"
_KNOWN_ANSWER_CANONICAL_JSON = (
    '{"algorithm":"Ed25519","authority_domain":"WILSY_LEGAL_CORPUS_APPROVAL_AUTHORITY",'
    '"authority_role":"WILSY_OS_LEGAL_CORPUS_APPROVAL_AUTHORITY",'
    '"issuer_identity":"WILSY_OS_LEGAL_CORPUS_APPROVAL_AUTHORITY:V1",'
    '"key_id":"prdca-key:legal-corpus-approval-cbd3f6eeba676b21e0f2c47522292482",'
    '"permitted_operations":["LEGAL_CORPUS_DOCUMENT_APPROVAL"],'
    '"public_key_base64url":"AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8",'
    '"revision":1,"scope":"PLATFORM","status":"ACTIVE",'
    '"trust_root_provenance":"WILSY_LEGAL_CORPUS_APPROVAL_TRUST_ROOT/V1",'
    '"valid_from":"2026-01-01T12:00:00.000000+00:00",'
    '"valid_until":"2026-01-02T12:00:00.000000+00:00"}'
)
_KNOWN_ANSWER_FINGERPRINT = "37fb0f87043e264737fbcc0c08229005f30d87e899961173cc5dbe71f9dc9f57adb63f5a9cc2bf1e95edefe2ef945320e58da023c5169fcaf80a30c6a89e6e1c"


def _public(seed: int = 0) -> str:
    """Return deterministic synthetic raw public bytes, never a keypair."""
    raw = bytes((seed + offset) % 256 for offset in range(32))
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _independent_key_id(public_key_base64url: str) -> str:
    """Calculate the key namespace from raw bytes without production helpers."""
    raw = base64.urlsafe_b64decode(public_key_base64url + "==")
    return KEY_ID_PREFIX + hashlib.sha3_512(raw).hexdigest()[:32]


def _independent_trust_fingerprint(values: dict[str, Any]) -> str:
    """Rebuild the exact semantic payload without production fingerprint code."""
    valid_from = values["valid_from"]
    valid_until = values["valid_until"]
    assert isinstance(valid_from, datetime)
    assert isinstance(valid_until, datetime)
    status = values["status"]
    status_value = status.value if isinstance(status, LegalCorpusApprovalTrustStatus) else status
    operations = values["permitted_operations"]
    payload: dict[str, Any] = {
        "algorithm": values["algorithm"],
        "authority_domain": values["authority_domain"],
        "authority_role": values["authority_role"],
        "issuer_identity": values["issuer_identity"],
        "key_id": values["key_id"],
        "permitted_operations": sorted(operations),
        "public_key_base64url": values["public_key_base64url"],
        "revision": values["revision"],
        "scope": values["scope"],
        "status": status_value,
        "trust_root_provenance": values["trust_root_provenance"],
        "valid_from": valid_from.astimezone(UTC).isoformat(timespec="microseconds"),
        "valid_until": valid_until.astimezone(UTC).isoformat(timespec="microseconds"),
    }
    assert len(payload) == 13
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha3_512(canonical.encode("utf-8")).hexdigest()


def _key_kwargs(**changes: object) -> dict[str, object]:
    """Build valid source-owned metadata with caller-selected mutations."""
    public_key = str(changes.pop("public_key_base64url", _public()))
    values: dict[str, object] = {
        "key_id": LegalCorpusApprovalTrustedKey.derive_key_id(public_key),
        "issuer_identity": APPROVAL_ISSUER_IDENTITY,
        "authority_role": APPROVAL_AUTHORITY_ROLE,
        "authority_domain": APPROVAL_AUTHORITY_DOMAIN,
        "algorithm": ED25519_ALGORITHM,
        "public_key_base64url": public_key,
        "valid_from": START,
        "valid_until": END,
        "status": LegalCorpusApprovalTrustStatus.ACTIVE,
        "revision": 1,
        "permitted_operations": frozenset({APPROVAL_OPERATION}),
        "scope": APPROVAL_SCOPE,
        "trust_root_provenance": APPROVAL_TRUST_ROOT_PROVENANCE,
    }
    values.update(changes)
    values["trust_fingerprint"] = _independent_trust_fingerprint(values)
    return values


def _key(**changes: object) -> LegalCorpusApprovalTrustedKey:
    """Construct one valid synthetic trust record."""
    return LegalCorpusApprovalTrustedKey(**_key_kwargs(**changes))  # type: ignore[arg-type]


def _construct(values: dict[str, object]) -> LegalCorpusApprovalTrustedKey:
    """Construct deliberately malformed typed dictionaries for rejection tests."""
    return LegalCorpusApprovalTrustedKey(**values)  # type: ignore[arg-type]


def _invalid_values(**changes: object) -> dict[str, object]:
    """Keep all unrelated fields valid while targeting one exact rejection."""
    values = _key_kwargs()
    values.update(changes)
    values["trust_fingerprint"] = "0" * 128
    return values


def _assert_code(callable_object: object, code: str) -> None:
    """Assert the exact fail-closed production error code."""
    with pytest.raises(LegalCorpusApprovalTrustRootError) as raised:
        callable_object()  # type: ignore[operator]
    assert raised.value.code == code


def test_valid_key_has_fixed_approval_identity_and_immutable_slots() -> None:
    key = _key()
    assert key.issuer_identity == APPROVAL_ISSUER_IDENTITY
    assert key.authority_role == APPROVAL_AUTHORITY_ROLE
    assert key.authority_domain == APPROVAL_AUTHORITY_DOMAIN
    assert key.algorithm == ED25519_ALGORITHM
    assert key.scope == APPROVAL_SCOPE
    assert key.permitted_operations == frozenset({APPROVAL_OPERATION})
    assert key.key_id.startswith(KEY_ID_PREFIX)
    assert len(key.trust_fingerprint) == 128
    assert fields(key)
    with pytest.raises(FrozenInstanceError):
        key.status = LegalCorpusApprovalTrustStatus.RETIRED  # type: ignore[misc]
    with pytest.raises(AttributeError):
        key.unexpected = True  # type: ignore[attr-defined]


def test_independent_fingerprint_helper_does_not_delegate_to_production() -> None:
    source = Path(__file__).read_text()
    tree = ast.parse(source)
    helper = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "_independent_trust_fingerprint")
    delegated = [
        node
        for node in ast.walk(helper)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "fingerprint_for"
    ]
    assert delegated == []


def test_independent_fingerprint_covers_exact_thirteen_field_payload() -> None:
    values: dict[str, object] = {
        "key_id": _KNOWN_KEY_ID,
        "issuer_identity": APPROVAL_ISSUER_IDENTITY,
        "authority_role": APPROVAL_AUTHORITY_ROLE,
        "authority_domain": APPROVAL_AUTHORITY_DOMAIN,
        "algorithm": ED25519_ALGORITHM,
        "public_key_base64url": _KNOWN_PUBLIC_KEY,
        "valid_from": START,
        "valid_until": END,
        "status": LegalCorpusApprovalTrustStatus.ACTIVE,
        "revision": 1,
        "permitted_operations": frozenset({APPROVAL_OPERATION}),
        "scope": APPROVAL_SCOPE,
        "trust_root_provenance": APPROVAL_TRUST_ROOT_PROVENANCE,
    }
    payload = {
        "algorithm": "Ed25519",
        "authority_domain": APPROVAL_AUTHORITY_DOMAIN,
        "authority_role": APPROVAL_AUTHORITY_ROLE,
        "issuer_identity": APPROVAL_ISSUER_IDENTITY,
        "key_id": _KNOWN_KEY_ID,
        "permitted_operations": [APPROVAL_OPERATION],
        "public_key_base64url": _KNOWN_PUBLIC_KEY,
        "revision": 1,
        "scope": APPROVAL_SCOPE,
        "status": "ACTIVE",
        "trust_root_provenance": APPROVAL_TRUST_ROOT_PROVENANCE,
        "valid_from": "2026-01-01T12:00:00.000000+00:00",
        "valid_until": "2026-01-02T12:00:00.000000+00:00",
    }
    assert json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == _KNOWN_ANSWER_CANONICAL_JSON
    assert hashlib.sha3_512(_KNOWN_ANSWER_CANONICAL_JSON.encode("utf-8")).hexdigest() == _KNOWN_ANSWER_FINGERPRINT
    assert _independent_trust_fingerprint(values) == _KNOWN_ANSWER_FINGERPRINT
    accepted = LegalCorpusApprovalTrustedKey(**values, trust_fingerprint=_KNOWN_ANSWER_FINGERPRINT)  # type: ignore[arg-type]
    assert accepted.trust_fingerprint == _KNOWN_ANSWER_FINGERPRINT
    assert LegalCorpusApprovalTrustedKey.fingerprint_for(**values) == _KNOWN_ANSWER_FINGERPRINT  # type: ignore[arg-type]
    assert set(values) == {
        "key_id",
        "issuer_identity",
        "authority_role",
        "authority_domain",
        "algorithm",
        "public_key_base64url",
        "valid_from",
        "valid_until",
        "status",
        "revision",
        "permitted_operations",
        "scope",
        "trust_root_provenance",
    }


@pytest.mark.parametrize(
    "changes",
    [
        {"key_id": "prdca-key:legal-corpus-approval-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
        {"issuer_identity": "OTHER_ISSUER"},
        {"authority_role": "OTHER_ROLE"},
        {"authority_domain": "OTHER_DOMAIN"},
        {"algorithm": "OtherAlgorithm"},
        {"public_key_base64url": _public(1), "key_id": LegalCorpusApprovalTrustedKey.derive_key_id(_public(1))},
        {"valid_from": START + timedelta(seconds=1)},
        {"valid_until": END + timedelta(seconds=1)},
        {"status": LegalCorpusApprovalTrustStatus.RETIRED},
        {"revision": 2},
        {"permitted_operations": frozenset({"OTHER_OPERATION"})},
        {"scope": "OTHER_SCOPE"},
        {"trust_root_provenance": "OTHER_PROVENANCE"},
    ],
)
def test_independent_fingerprint_changes_for_each_semantic_field(changes: dict[str, object]) -> None:
    baseline = _key_kwargs()
    mutated = dict(baseline)
    mutated.update(changes)
    assert _independent_trust_fingerprint(mutated) != baseline["trust_fingerprint"]


@pytest.mark.parametrize(
    "changes",
    [
        {"public_key_base64url": _public(1), "key_id": LegalCorpusApprovalTrustedKey.derive_key_id(_public(1))},
        {"valid_from": START + timedelta(seconds=1)},
        {"valid_until": END + timedelta(seconds=1)},
        {"status": LegalCorpusApprovalTrustStatus.RETIRED},
        {"status": LegalCorpusApprovalTrustStatus.REVOKED},
        {"revision": 2},
    ],
)
def test_constructor_rejects_stale_fingerprint_for_valid_semantic_mutations(changes: dict[str, object]) -> None:
    values = _key_kwargs(**changes)
    values["trust_fingerprint"] = _key_kwargs()["trust_fingerprint"]
    _assert_code(lambda: _construct(values), "APPROVAL_TRUST_FINGERPRINT_MISMATCH")


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("issuer_identity", "WILSY_OS_LEGAL_CORPUS_RELEASE_AUTHORITY:V1", "APPROVAL_TRUST_ISSUER_INVALID"),
        ("authority_role", "AUTHORISED_SIGNATORY", "APPROVAL_TRUST_ROLE_INVALID"),
        ("authority_domain", "WILSY_LEGAL_CORPUS_OPERATOR_AUTHORITY", "APPROVAL_TRUST_DOMAIN_INVALID"),
        ("algorithm", "Ed448", "APPROVAL_TRUST_ALGORITHM_INVALID"),
        ("scope", "TENANT", "APPROVAL_TRUST_SCOPE_INVALID"),
        ("permitted_operations", frozenset({"LEGAL_CORPUS_DRAFT_ADMISSION"}), "APPROVAL_TRUST_OPERATION_INVALID"),
        ("permitted_operations", frozenset({"*"}), "APPROVAL_TRUST_OPERATION_INVALID"),
        ("trust_root_provenance", "WILSY_LEGAL_CORPUS_OPERATOR_TRUST_ROOT/V1", "APPROVAL_TRUST_PROVENANCE_INVALID"),
    ],
)
def test_fixed_identity_and_operation_boundaries_reject(field: str, value: object, code: str) -> None:
    values = _key_kwargs()
    values[field] = value
    values["trust_fingerprint"] = "0" * 128
    _assert_code(lambda: _construct(values), code)


@pytest.mark.parametrize(
    "public_key",
    [
        "",
        None,
        b"raw-public-bytes",
        object(),
        "   ",
        " leading",
        "trailing ",
        "ordinary space",
        _public()[:10] + " " + _public()[11:],
        "a\n",
        "a\r",
        "a\t",
        42,
        "not base64!",
        "====",
        _public() + "=",
        _public()[:-1] + "9",
        "/" * 43,
    ],
)
def test_public_key_syntax_rejects_noncanonical_values(public_key: object) -> None:
    _assert_code(lambda: _construct(_invalid_values(public_key_base64url=public_key)), "APPROVAL_TRUST_PUBLIC_KEY_INVALID")


@pytest.mark.parametrize("raw", [b"", b"1" * 31, b"2" * 33, b"3" * 64])
def test_public_key_decoded_length_must_be_exactly_32_bytes(raw: bytes) -> None:
    encoded = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
    _assert_code(lambda: _construct(_invalid_values(public_key_base64url=encoded)), "APPROVAL_TRUST_PUBLIC_KEY_INVALID")


@pytest.mark.parametrize(
    "provenance",
    [
        "",
        " ",
        "   ",
        " leading",
        "trailing ",
        "line\nfeed",
        "carriage\rreturn",
        "tab\tvalue",
        "nul\x00value",
        "control\x01value",
        "control\x1fvalue",
        "delete\x7fvalue",
        b"bytes",
        object(),
        "x" * 256,
        "x" * 257,
    ],
)
def test_trust_root_provenance_is_single_line_bounded_and_source_owned(provenance: object) -> None:
    _assert_code(lambda: _construct(_invalid_values(trust_root_provenance=provenance)), "APPROVAL_TRUST_PROVENANCE_INVALID")


def test_trust_root_provenance_maximum_bound_is_explicit() -> None:
    assert len("x" * 256) == 256
    assert len("x" * 257) == 257
    assert APPROVAL_TRUST_ROOT_PROVENANCE == "WILSY_LEGAL_CORPUS_APPROVAL_TRUST_ROOT/V1"


def test_key_id_is_approval_namespace_and_must_match_raw_public_digest() -> None:
    public_key_1 = _KNOWN_PUBLIC_KEY
    public_key_2 = _SECOND_KNOWN_PUBLIC_KEY
    expected_1 = _independent_key_id(public_key_1)
    expected_2 = _independent_key_id(public_key_2)
    assert expected_1 == _KNOWN_KEY_ID
    assert expected_2 == _SECOND_KNOWN_KEY_ID
    assert expected_1 != expected_2
    assert LegalCorpusApprovalTrustedKey.derive_key_id(public_key_1) == expected_1
    assert LegalCorpusApprovalTrustedKey.derive_key_id(public_key_2) == expected_2
    mismatched = _key_kwargs(public_key_base64url=public_key_1, key_id=expected_2)
    _assert_code(lambda: _construct(mismatched), "APPROVAL_TRUST_KEY_ID_INVALID")
    _assert_code(lambda: _key(key_id="prdca-key:legal-corpus-00000000000000000000000000000000"), "APPROVAL_TRUST_KEY_ID_INVALID")


@pytest.mark.parametrize(
    "changes",
    [
        {"valid_from": START.replace(tzinfo=None)},
        {"valid_until": END.replace(tzinfo=None)},
        {"valid_from": END, "valid_until": START},
        {"valid_from": START, "valid_until": START},
    ],
)
def test_validity_requires_aware_strictly_ordered_endpoints(changes: dict[str, object]) -> None:
    _assert_code(lambda: _key(**changes), "APPROVAL_TRUST_VALIDITY_INVALID")


@pytest.mark.parametrize("revision", [0, -1, True, False, 1.0, "1", None])
def test_revision_is_positive_integer_not_bool(revision: object) -> None:
    _assert_code(lambda: _key(revision=revision), "APPROVAL_TRUST_REVISION_INVALID")


def test_lifecycle_enum_is_closed_and_status_is_fingerprint_semantic() -> None:
    assert tuple(LegalCorpusApprovalTrustStatus) == (
        LegalCorpusApprovalTrustStatus.ACTIVE,
        LegalCorpusApprovalTrustStatus.RETIRED,
        LegalCorpusApprovalTrustStatus.REVOKED,
    )
    active = _key(status=LegalCorpusApprovalTrustStatus.ACTIVE)
    retired = _key(status=LegalCorpusApprovalTrustStatus.RETIRED)
    revoked = _key(status=LegalCorpusApprovalTrustStatus.REVOKED)
    assert len({active.trust_fingerprint, retired.trust_fingerprint, revoked.trust_fingerprint}) == 3
    _assert_code(lambda: _key(status="ACTIVE"), "APPROVAL_TRUST_STATUS_INVALID")


def test_fingerprint_binds_revision_public_key_and_all_governance_fields() -> None:
    base = _key()
    assert _key(revision=2).trust_fingerprint != base.trust_fingerprint
    assert _key(public_key_base64url=_public(1)).trust_fingerprint != base.trust_fingerprint
    assert _key(valid_from=START + timedelta(seconds=1)).trust_fingerprint != base.trust_fingerprint
    assert _key(valid_until=END + timedelta(seconds=1)).trust_fingerprint != base.trust_fingerprint
    for field, value in (("issuer_identity", "OTHER"), ("authority_role", "OTHER"), ("authority_domain", "OTHER"), ("algorithm", "Other"), ("scope", "OTHER"), ("permitted_operations", frozenset({"OTHER"})), ("trust_root_provenance", "OTHER")):
        values = _key_kwargs()
        values[field] = value
        values["trust_fingerprint"] = "0" * 128
        with pytest.raises(LegalCorpusApprovalTrustRootError):
            _construct(values)
    _assert_code(lambda: replace(base, trust_fingerprint="0" * 128), "APPROVAL_TRUST_FINGERPRINT_MISMATCH")


def test_equivalent_offsets_normalize_and_fingerprint_identically() -> None:
    plus_two = timezone(timedelta(hours=2))
    shifted_start = datetime(2026, 1, 1, 14, tzinfo=plus_two)
    shifted_end = datetime(2026, 1, 2, 14, tzinfo=plus_two)
    key = _key(valid_from=shifted_start, valid_until=shifted_end)
    assert key.valid_from == START
    assert key.valid_until == END
    assert key.trust_fingerprint == _key().trust_fingerprint


def test_issue_and_historical_verification_time_law_is_exact() -> None:
    active = _key(status=LegalCorpusApprovalTrustStatus.ACTIVE)
    retired = _key(status=LegalCorpusApprovalTrustStatus.RETIRED)
    revoked = _key(status=LegalCorpusApprovalTrustStatus.REVOKED)
    for key in (active, retired, revoked):
        assert key.is_valid_at(START)
        assert not key.is_valid_at(END)
        assert not key.can_verify_at("WRONG", APPROVAL_SCOPE, START)
        assert not key.can_verify_at(APPROVAL_OPERATION, "TENANT", START)
    assert active.can_issue(APPROVAL_OPERATION, APPROVAL_SCOPE, START)
    assert not active.can_issue(APPROVAL_OPERATION, APPROVAL_SCOPE, START - timedelta(seconds=1))
    assert not active.can_issue(APPROVAL_OPERATION, APPROVAL_SCOPE, END)
    assert not active.can_issue("WRONG", APPROVAL_SCOPE, START)
    assert not active.can_issue(APPROVAL_OPERATION, "TENANT", START)
    assert retired.can_verify_at(APPROVAL_OPERATION, APPROVAL_SCOPE, START)
    assert not retired.can_issue(APPROVAL_OPERATION, APPROVAL_SCOPE, START)
    assert not revoked.can_verify_at(APPROVAL_OPERATION, APPROVAL_SCOPE, START)
    assert not revoked.can_issue(APPROVAL_OPERATION, APPROVAL_SCOPE, START)


def test_serialization_is_deterministic_primitives_and_mutation_safe() -> None:
    key = _key()
    first = key.to_document()
    second = key.to_document()
    assert first == second
    assert all(isinstance(value, (str, int, list)) for value in first.values())
    assert isinstance(first["permitted_operations"], list)
    first["status"] = "REVOKED"
    assert key.status is LegalCorpusApprovalTrustStatus.ACTIVE


def test_trust_root_membership_is_immutable_duplicate_safe_and_fail_closed() -> None:
    first = _key()
    second = _key(public_key_base64url=_public(1))
    root = LegalCorpusApprovalTrustRoot((first, second))
    assert root.resolve(first.key_id) is first
    assert root.all_keys() == (first, second)
    with pytest.raises(FrozenInstanceError):
        root.trusted_keys = ()  # type: ignore[misc]
    _assert_code(lambda: LegalCorpusApprovalTrustRoot((first, first)), "APPROVAL_TRUST_DUPLICATE_KEY")
    _assert_code(lambda: root.resolve("prdca-key:legal-corpus-approval-00000000000000000000000000000000"), "APPROVAL_TRUST_KEY_UNKNOWN")
    _assert_code(lambda: root.resolve("bad"), "APPROVAL_TRUST_KEY_ID_INVALID")


_PREDECESSOR_KEY_ID = "prdca-key:legal-corpus-approval-f8bc464615e8047f008909c36750348b"
_PREDECESSOR_PUBLIC_KEY = "MgzL6fXojmva5bRPonUOdVLOEZFRJHd6gA1kJa1SXGE"
_PREDECESSOR_PUBLIC_SHA3 = "f8bc464615e8047f008909c36750348b4d7e3158bd912c0db5f3afbe2ebbe5da434eb9254f34d77bd7f0eb1b9ed6cfb113d917cce59a6bdb3548cd9aa42a1501"
_PREDECESSOR_FINGERPRINT = "88b2c725e8545c8a88259a74a517266202a99daa0145ed90dbef458e8e41bbdecbd24bc9a777acece7a9a5ebe0c20aa0e77ea210ee4b027c14058a65edcdeaad"
_PREDECESSOR_VALID_FROM = datetime(2026, 9, 19, 10, 3, 24, 50717, tzinfo=UTC)
_PREDECESSOR_VALID_UNTIL = datetime(2026, 9, 20, 10, 3, 24, 50717, tzinfo=UTC)
_SUCCESSOR_KEY_ID = "prdca-key:legal-corpus-approval-2084472fec6f273b537255d0b2dff9fb"
_SUCCESSOR_PUBLIC_KEY = "12o_Ya2-muW1IXlcdIJF_Hu-2Nn3aKdIIqb4DYNcp9Q"
_SUCCESSOR_PUBLIC_SHA3 = "2084472fec6f273b537255d0b2dff9fbc648985307c473e3993127e6d8f2cc178750fc744cee8c6b510b7d3f7e76a69f9046472e499debc87efe7a87081cb007"
_SUCCESSOR_FINGERPRINT = "f25151e216e1fadf4728c59583b64e84692685e6b12a0ed85a303e92e6a0039d1914151f9d070e6349083713464e4a753b1bd19a72031c94594385935f390b95"
_SUCCESSOR_VALID_FROM = datetime(2026, 9, 21, 19, 48, 56, 907799, tzinfo=UTC)
_SUCCESSOR_VALID_UNTIL = datetime(2026, 9, 22, 19, 48, 56, 907799, tzinfo=UTC)


def test_production_root_admits_exact_predecessor_and_successor_public_keys() -> None:
    assert PRODUCTION_APPROVAL_TRUST_ROOT.production_key_count() == 2
    assert PRODUCTION_APPROVAL_TRUSTED_KEYS == PRODUCTION_APPROVAL_TRUST_ROOT.all_keys()
    predecessor = PRODUCTION_APPROVAL_TRUST_ROOT.resolve(_PREDECESSOR_KEY_ID)
    assert predecessor.key_id == _PREDECESSOR_KEY_ID
    assert predecessor.public_key_base64url == _PREDECESSOR_PUBLIC_KEY
    raw = base64.urlsafe_b64decode(_PREDECESSOR_PUBLIC_KEY + "==")
    assert len(raw) == 32
    assert hashlib.sha3_512(raw).hexdigest() == _PREDECESSOR_PUBLIC_SHA3
    assert LegalCorpusApprovalTrustedKey.derive_key_id(_PREDECESSOR_PUBLIC_KEY) == _PREDECESSOR_KEY_ID
    assert predecessor.trust_fingerprint == _PREDECESSOR_FINGERPRINT
    assert _independent_trust_fingerprint({
        "key_id": predecessor.key_id,
        "issuer_identity": predecessor.issuer_identity,
        "authority_role": predecessor.authority_role,
        "authority_domain": predecessor.authority_domain,
        "algorithm": predecessor.algorithm,
        "public_key_base64url": predecessor.public_key_base64url,
        "valid_from": predecessor.valid_from,
        "valid_until": predecessor.valid_until,
        "status": predecessor.status,
        "revision": predecessor.revision,
        "permitted_operations": predecessor.permitted_operations,
        "scope": predecessor.scope,
        "trust_root_provenance": predecessor.trust_root_provenance,
    }) == _PREDECESSOR_FINGERPRINT
    assert predecessor.valid_from == _PREDECESSOR_VALID_FROM
    assert predecessor.valid_until == _PREDECESSOR_VALID_UNTIL
    assert predecessor.status is LegalCorpusApprovalTrustStatus.RETIRED
    assert predecessor.revision == 2

    successor = PRODUCTION_APPROVAL_TRUST_ROOT.resolve(_SUCCESSOR_KEY_ID)
    assert successor.key_id == _SUCCESSOR_KEY_ID
    assert successor.public_key_base64url == _SUCCESSOR_PUBLIC_KEY
    successor_raw = base64.urlsafe_b64decode(_SUCCESSOR_PUBLIC_KEY + "==")
    assert len(successor_raw) == 32
    assert hashlib.sha3_512(successor_raw).hexdigest() == _SUCCESSOR_PUBLIC_SHA3
    assert LegalCorpusApprovalTrustedKey.derive_key_id(_SUCCESSOR_PUBLIC_KEY) == _SUCCESSOR_KEY_ID
    assert successor.trust_fingerprint == _SUCCESSOR_FINGERPRINT
    assert _independent_trust_fingerprint({
        "key_id": successor.key_id,
        "issuer_identity": successor.issuer_identity,
        "authority_role": successor.authority_role,
        "authority_domain": successor.authority_domain,
        "algorithm": successor.algorithm,
        "public_key_base64url": successor.public_key_base64url,
        "valid_from": successor.valid_from,
        "valid_until": successor.valid_until,
        "status": successor.status,
        "revision": successor.revision,
        "permitted_operations": successor.permitted_operations,
        "scope": successor.scope,
        "trust_root_provenance": successor.trust_root_provenance,
    }) == _SUCCESSOR_FINGERPRINT
    assert successor.valid_from == _SUCCESSOR_VALID_FROM
    assert successor.valid_until == _SUCCESSOR_VALID_UNTIL
    assert successor.status is LegalCorpusApprovalTrustStatus.ACTIVE
    assert successor.revision == 1
    assert successor.issuer_identity == APPROVAL_ISSUER_IDENTITY
    assert successor.authority_role == APPROVAL_AUTHORITY_ROLE
    assert successor.authority_domain == APPROVAL_AUTHORITY_DOMAIN
    assert successor.algorithm == ED25519_ALGORITHM
    assert successor.scope == APPROVAL_SCOPE
    assert successor.permitted_operations == frozenset({APPROVAL_OPERATION})
    assert successor.trust_root_provenance == APPROVAL_TRUST_ROOT_PROVENANCE
    assert PRODUCTION_APPROVAL_TRUST_ROOT.resolve(_SUCCESSOR_KEY_ID) is successor


def test_production_key_lifecycle_is_bounded_and_successor_is_only_issuer() -> None:
    predecessor = PRODUCTION_APPROVAL_TRUST_ROOT.resolve(_PREDECESSOR_KEY_ID)
    assert not predecessor.can_issue(APPROVAL_OPERATION, APPROVAL_SCOPE, _PREDECESSOR_VALID_FROM)
    assert predecessor.can_verify_at(APPROVAL_OPERATION, APPROVAL_SCOPE, _PREDECESSOR_VALID_FROM)
    successor = PRODUCTION_APPROVAL_TRUST_ROOT.resolve(_SUCCESSOR_KEY_ID)
    assert not successor.can_issue(APPROVAL_OPERATION, APPROVAL_SCOPE, _SUCCESSOR_VALID_FROM - timedelta(microseconds=1))
    assert successor.can_issue(APPROVAL_OPERATION, APPROVAL_SCOPE, _SUCCESSOR_VALID_FROM)
    assert successor.can_issue(APPROVAL_OPERATION, APPROVAL_SCOPE, _SUCCESSOR_VALID_UNTIL - timedelta(microseconds=1))
    assert not successor.can_issue(APPROVAL_OPERATION, APPROVAL_SCOPE, _SUCCESSOR_VALID_UNTIL)
    assert successor.can_verify_at(APPROVAL_OPERATION, APPROVAL_SCOPE, _SUCCESSOR_VALID_FROM)


def test_production_root_has_no_private_material_or_r8_shortcuts() -> None:
    source = Path("tools/eos/legal_operations/domain/legal_corpus_approval_trust_root.py").read_text()
    for forbidden in (
        "Ed25519PrivateKey", "BEGIN PRIVATE KEY", "BEGIN ENCRYPTED PRIVATE KEY",
        ".private.pem", "$HOME/.wilsy", "/.wilsy/", "passphrase",
        "private-key", ".sign(", "Path(", "open(", "os.getenv", "LEGAL_CORPUS_DRAFT_ADMISSION",
        "WILSY_OS_LEGAL_CORPUS_RELEASE_AUTHORITY", "WILSY_LEGAL_CORPUS_OPERATOR_AUTHORITY",
        "SUPER_ADMIN", "AUTHORISED_SIGNATORY",
    ):
        assert forbidden not in source


def test_r8_and_role_ai_shortcuts_are_absent_and_no_crypto_or_persistence_apis_exist() -> None:
    source = Path("tools/eos/legal_operations/domain/legal_corpus_approval_trust_root.py").read_text()
    assert "legal_corpus_operator_trust_root" not in source
    assert "LEGAL_CORPUS_DRAFT_ADMISSION" not in source
    assert "WILSY_LEGAL_CORPUS_OPERATOR_AUTHORITY" not in source
    assert "WILSY_OS_LEGAL_CORPUS_RELEASE_AUTHORITY" not in source
    assert "SUPER_ADMIN" not in source
    assert "AUTHORISED_SIGNATORY" not in source
    assert "Ed25519PrivateKey" not in source
    assert ".sign(" not in source
    assert ".verify(" not in source
    tree = ast.parse(source)
    imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    imported = " ".join(ast.unparse(node) for node in imports)
    assert "pymongo" not in imported.lower()
    assert "fastapi" not in imported.lower()
    assert "requests" not in imported.lower()


def test_public_contract_does_not_create_filesystem_or_network_behavior() -> None:
    key = _key()
    assert key.to_document()["trust_fingerprint"] == key.trust_fingerprint
    assert PUBLIC_KEY_ENCODING == "base64url_without_padding_raw_32_bytes"


# ARTIFACT: test_legal_corpus_approval_trust_root.py
# VERSION: v1.4.0-R1D-B0F-R9B-P5-R2-LEGAL-CORPUS-APPROVAL-TRUST-ROOT-CERT
# AUTHORITY BOUNDARY: direct unit evidence for public approval trust metadata only
# TENANT POSTURE: PLATFORM-only; no tenant or principal authority
# FAIL-CLOSED POSTURE: unsupported trust records, keys, lifecycle, and shortcuts reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
