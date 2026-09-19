"""Direct certificate for the R8O-P4-R7 legal-corpus operator trust root.

TITLE: WILSY OS Legal Corpus Operator Trust-Root Direct Certificate
VERSION: v1.3.0-R9B-P7-A2-R2-LEGAL-CORPUS-OPERATOR-TRUST-ROOT-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the immutable, two-record PLATFORM-scoped Ed25519 public-key
         trust root: one historical RETIRED record and one human-admitted ACTIVE
         record with a finite 24-hour validity interval.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_corpus_operator_trust_root.py
COLLABORATION / OWNERSHIP: Direct certificate for the R8O-P4-R7 production
                           trust-root artifact; signed authorization and the
                           operator command remain separate boundaries.
CERTIFICATION / UPDATE DATE: 2026-09-19
CHANGELOG: v1.3.0-R9B-P7-A2-R2-LEGAL-CORPUS-OPERATOR-TRUST-ROOT-CERT
           certifies the exact historical RETIRED record and the exact new
           ACTIVE record, independent public-key identity, fingerprints,
           lifecycle boundaries, and 24-hour validity contract.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Deterministic public test material only; no private
                            key, secret, network, Mongo, environment, or file
                            key loading is used.
TENANT BOUNDARY: PLATFORM trust-root scope only; tenant and principal authority
                 are explicitly excluded.
AUTHORITY BOUNDARY: Certificate evidence for retired public trust material
                    only; no signed authorization, R8D evidence, document
                    persistence, approval, acceptance, signing, or execution
                    is created. Historical R8N execution remains unproven.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
FAIL-CLOSED POSTURE: Unknown keys, malformed records, unsupported algorithms,
                     unsupported permissions, drift, mutable-root attempts,
                     and fresh RETIRED-key issuance reject without fallback
                     authority; archival P8 remains historical and P9 remains
                     unproven.
"""
from __future__ import annotations

import ast
from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import fields
from datetime import datetime, timedelta, timezone
import hashlib
import inspect
from pathlib import Path
from typing import Any

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from tools.eos.legal_operations.domain.legal_corpus_operator_trust_root import (
    AUTHORIZED_OPERATION,
    AUTHORITY_DOMAIN,
    ED25519_ALGORITHM,
    PUBLIC_KEY_ENCODING,
    TRUSTED_KEYS,
    TRUST_ROOT_PROVENANCE,
    TRUST_ROOT_SCOPE,
    LegalCorpusOperatorKeyStatus,
    LegalCorpusOperatorTrustRoot,
    LegalCorpusOperatorTrustRootError,
    LegalCorpusOperatorTrustedKey,
    VERSION,
)


ROOT_PATH = Path("tools/eos/legal_operations/domain/legal_corpus_operator_trust_root.py")
_SEMANTIC_FIELDS = (
    "key_id",
    "algorithm",
    "public_key_base64url",
    "issuer_identity",
    "authority_domain",
    "scope",
    "permitted_operations",
    "valid_from",
    "valid_until",
    "status",
    "revision",
    "trust_root_provenance",
)
_RFC_PUBLIC_KEY = bytes.fromhex(
    "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
)
_ALTERNATE_PUBLIC_KEY = bytes(range(32))
_PRODUCTION_KEY_ID = "prdca-key:legal-corpus-69c7c3e9a67c7e552057d4c0670623be"
_PRODUCTION_PUBLIC_KEY = "jfG0IANHA_tSNyjyurpBtTId98fG2l_LhifnfQJ2cXg"
_PRODUCTION_PUBLIC_KEY_SHA3_512 = "69c7c3e9a67c7e552057d4c0670623be651f22e95dc69ad142e9174d1f811f3bfb74c7faa172a6d12df38abcde2576b8dd4005640c77649c932d13fbc74f72ac"
_PRODUCTION_FINGERPRINT = "1ea7ec1e18355b4181d6b652c05be296deb2bb02cf0d5504e1e2ede82278572ee66178df141a4f98cf280af122fb2f55eebedb44262fa552f215c38a5bec2e38"
_PRODUCTION_SOURCE_BYTES = 22153
_PRODUCTION_SOURCE_SHA3_512 = "6c4e7c8570c7bd938b854e367adbe02fd10f421ade5c395be643a4467b5c31f01680994663b14fadea4acf36aa787f42c7b5b6ede2a79367aacfa1f3d6cba863"
_NEW_KEY_ID = "prdca-key:legal-corpus-159cfa91f279b045407396cd3ec8dca2"
_NEW_PUBLIC_KEY = "vlN3rieZr9YwuvQ6AwW_dD1aN06B2MLGqlFsxacgCpM"
_NEW_PUBLIC_KEY_SHA3_512 = "159cfa91f279b045407396cd3ec8dca291b135e6cf15c1f017fe68cc7f240df792a978670a410375b06bd2a219132bf0ca4395bcc83ede94a1304008818d72f3"
_NEW_TRUST_RECORD_FINGERPRINT = "334af06c789abe47a3c44b93be08a7a68c5ec535a65c45dee02a79d32b33a4c41ecac62e98347740f48eb5e357f8ccf9d63766aae65fcc16315400bfe947345d"
_NEW_VALID_FROM = datetime(2026, 9, 19, 19, 33, 13, 213194, tzinfo=timezone.utc)
_NEW_VALID_UNTIL = datetime(2026, 9, 20, 19, 33, 13, 213194, tzinfo=timezone.utc)
_PRODUCTION_VALID_FROM = datetime(2026, 9, 18, 5, 32, 16, tzinfo=timezone.utc)
_PRODUCTION_VALID_UNTIL = datetime(2026, 9, 19, 5, 32, 16, tzinfo=timezone.utc)


def _production_record() -> LegalCorpusOperatorTrustedKey:
    """Return the historical RETIRED record through the canonical API."""
    assert len(TRUSTED_KEYS) == 2
    return TRUSTED_KEYS[0]


def _active_production_record() -> LegalCorpusOperatorTrustedKey:
    """Return the newly admitted ACTIVE record through the canonical API."""
    assert len(TRUSTED_KEYS) == 2
    return TRUSTED_KEYS[1]


def _encoded_public_key(value: bytes = _RFC_PUBLIC_KEY) -> str:
    """Return deterministic test-only raw Ed25519 public material."""
    return urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _fields(**changes: Any) -> dict[str, Any]:
    """Build actual C1 constructor fields and its matching fingerprint."""
    start = datetime(2026, 9, 18, 8, 0, tzinfo=timezone.utc)
    values: dict[str, Any] = {
        "key_id": "prdca-key:legal-corpus-test",
        "algorithm": ED25519_ALGORITHM,
        "public_key_base64url": _encoded_public_key(),
        "issuer_identity": "issuer:legal-corpus-test",
        "authority_domain": AUTHORITY_DOMAIN,
        "scope": TRUST_ROOT_SCOPE,
        "permitted_operations": frozenset({AUTHORIZED_OPERATION}),
        "valid_from": start,
        "valid_until": start + timedelta(days=1),
        "status": LegalCorpusOperatorKeyStatus.ACTIVE,
        "revision": 1,
        "trust_root_provenance": TRUST_ROOT_PROVENANCE,
    }
    values.update(changes)
    values["fingerprint"] = LegalCorpusOperatorTrustedKey.fingerprint_for(
        **{name: values[name] for name in _SEMANTIC_FIELDS}
    )
    return values


def _record(**changes: Any) -> LegalCorpusOperatorTrustedKey:
    """Construct one test-only trusted-key value through the production API."""
    return LegalCorpusOperatorTrustedKey(**_fields(**changes))


def _error_code(callable_object: object, *args: object, **kwargs: object) -> str:
    """Return the bounded production error code for one failing call."""
    with pytest.raises(LegalCorpusOperatorTrustRootError) as captured:
        callable_object(*args, **kwargs)  # type: ignore[operator]
    return captured.value.code


def test_production_root_contains_exactly_two_admitted_keys() -> None:
    """The current root contains one historical and one ACTIVE record."""
    assert VERSION == "v1.3.0-R9B-P7-A2-R2-LEGAL-CORPUS-OPERATOR-TRUST-ROOT"
    assert LegalCorpusOperatorTrustRoot.production_key_count() == 2
    assert len(LegalCorpusOperatorTrustRoot.all_keys()) == 2
    assert _production_record().key_id == _PRODUCTION_KEY_ID
    assert _active_production_record().key_id == _NEW_KEY_ID
    assert _error_code(LegalCorpusOperatorTrustRoot.resolve, "prdca-key:absent") == "UNKNOWN_TRUSTED_KEY"


def test_exact_active_production_record_is_fully_bound() -> None:
    """Every field of the new ACTIVE public record is exact and fingerprinted."""
    record = _active_production_record()
    assert record.key_id == _NEW_KEY_ID
    assert record.algorithm == ED25519_ALGORITHM
    assert record.public_key_base64url == _NEW_PUBLIC_KEY
    assert record.issuer_identity == "WILSY_OS_LEGAL_CORPUS_RELEASE_AUTHORITY:V1"
    assert record.authority_domain == "WILSY_LEGAL_CORPUS_OPERATOR_AUTHORITY"
    assert record.scope == "PLATFORM"
    assert record.permitted_operations == frozenset({"LEGAL_CORPUS_DRAFT_ADMISSION"})
    assert record.status is LegalCorpusOperatorKeyStatus.ACTIVE
    assert record.revision == 1
    assert record.valid_from == _NEW_VALID_FROM
    valid_until = record.valid_until
    assert valid_until == _NEW_VALID_UNTIL
    assert valid_until is not None
    assert valid_until - record.valid_from == timedelta(hours=24)
    assert record.trust_root_provenance == "WILSY_LEGAL_CORPUS_OPERATOR_TRUST_ROOT/V1"
    assert record.fingerprint == _NEW_TRUST_RECORD_FINGERPRINT
    assert record.fingerprint == LegalCorpusOperatorTrustedKey.fingerprint_for(
        **{name: getattr(record, name) for name in _SEMANTIC_FIELDS}
    )


def test_exact_production_record_is_fully_bound() -> None:
    """Every authority-bearing field of the admitted production record is exact."""
    record = _production_record()
    assert record.key_id == _PRODUCTION_KEY_ID
    assert record.algorithm == ED25519_ALGORITHM
    assert record.public_key_base64url == _PRODUCTION_PUBLIC_KEY
    assert record.issuer_identity == "WILSY_OS_LEGAL_CORPUS_RELEASE_AUTHORITY:V1"
    assert record.authority_domain == "WILSY_LEGAL_CORPUS_OPERATOR_AUTHORITY"
    assert record.scope == "PLATFORM"
    assert record.permitted_operations == frozenset({"LEGAL_CORPUS_DRAFT_ADMISSION"})
    assert record.status is LegalCorpusOperatorKeyStatus.RETIRED
    assert record.revision == 2
    assert record.valid_from == _PRODUCTION_VALID_FROM
    valid_from = record.valid_from
    valid_until = record.valid_until
    assert valid_until == _PRODUCTION_VALID_UNTIL
    assert valid_until is not None
    assert valid_until - valid_from == timedelta(seconds=86400)
    assert record.trust_root_provenance == "WILSY_LEGAL_CORPUS_OPERATOR_TRUST_ROOT/V1"
    assert record.fingerprint == _PRODUCTION_FINGERPRINT
    assert record.fingerprint == LegalCorpusOperatorTrustedKey.fingerprint_for(
        **{name: getattr(record, name) for name in _SEMANTIC_FIELDS}
    )


def test_public_key_hash_and_derived_key_id_are_independently_certified() -> None:
    """The approved raw public key independently derives the admitted identity."""
    record = _production_record()
    raw = urlsafe_b64decode(record.public_key_base64url + "==")
    assert len(raw) == 32
    assert isinstance(Ed25519PublicKey.from_public_bytes(raw), Ed25519PublicKey)
    digest = hashlib.sha3_512(raw).hexdigest()
    assert digest == _PRODUCTION_PUBLIC_KEY_SHA3_512
    assert f"prdca-key:legal-corpus-{digest[:32]}" == record.key_id


def test_new_public_key_hash_and_derived_key_id_are_independently_certified() -> None:
    """The new frozen public material independently derives its exact ID."""
    record = _active_production_record()
    raw = urlsafe_b64decode(record.public_key_base64url + "==")
    assert len(raw) == 32
    assert isinstance(Ed25519PublicKey.from_public_bytes(raw), Ed25519PublicKey)
    digest = hashlib.sha3_512(raw).hexdigest()
    assert digest == _NEW_PUBLIC_KEY_SHA3_512
    assert f"prdca-key:legal-corpus-{digest[:32]}" == _NEW_KEY_ID == record.key_id


@pytest.mark.parametrize("key_id", ["", "not-a-key", "prdca-key:missing"])
def test_unknown_and_malformed_keys_fail_closed(key_id: str) -> None:
    """Absent and malformed identifiers never authenticate an issuer."""
    assert _error_code(LegalCorpusOperatorTrustRoot.resolve, key_id) in {
        "KEY_ID_INVALID",
        "UNKNOWN_TRUSTED_KEY",
    }


def test_production_registry_exposure_is_immutable() -> None:
    """Returned production collections cannot be changed by a caller."""
    exposed = LegalCorpusOperatorTrustRoot.all_keys()
    assert isinstance(exposed, tuple)
    with pytest.raises(AttributeError):
        exposed.append(_record())  # type: ignore[attr-defined]
    assert LegalCorpusOperatorTrustRoot.production_key_count() == 2
    assert LegalCorpusOperatorTrustRoot.all_keys() == TRUSTED_KEYS
    assert LegalCorpusOperatorTrustRoot.resolve(_PRODUCTION_KEY_ID) is _production_record()
    assert LegalCorpusOperatorTrustRoot.resolve(_NEW_KEY_ID) is _active_production_record()


def test_valid_test_record_binds_actual_c1_contract() -> None:
    """A test-only public record validates every implemented trust field."""
    value = _record()
    assert value.key_id == "prdca-key:legal-corpus-test"
    assert value.algorithm == ED25519_ALGORITHM
    assert value.public_key() is not None
    assert value.issuer_identity == "issuer:legal-corpus-test"
    assert value.scope == TRUST_ROOT_SCOPE == "PLATFORM"
    assert value.permitted_operations == frozenset({AUTHORIZED_OPERATION})
    assert value.valid_from.tzinfo is not None
    assert value.valid_until is not None
    assert value.status is LegalCorpusOperatorKeyStatus.ACTIVE
    assert value.revision == 1
    assert value.trust_root_provenance == TRUST_ROOT_PROVENANCE
    assert len(value.fingerprint) == 128
    assert value.fingerprint == value.fingerprint.lower()
    assert isinstance(value.public_key(), Ed25519PublicKey)


def test_test_record_does_not_enter_production_root() -> None:
    """Constructing a test value never changes source-owned production trust."""
    value = _record()
    assert value.key_id not in {item.key_id for item in LegalCorpusOperatorTrustRoot.all_keys()}
    assert LegalCorpusOperatorTrustRoot.production_key_count() == 2
    assert _error_code(LegalCorpusOperatorTrustRoot.resolve, value.key_id) == "UNKNOWN_TRUSTED_KEY"
    assert LegalCorpusOperatorTrustRoot.resolve(_PRODUCTION_KEY_ID) is not value


def test_production_resolver_positive_and_unknown_paths_are_exact() -> None:
    """The resolver returns both source keys and has no fallback path."""
    assert LegalCorpusOperatorTrustRoot.resolve(_PRODUCTION_KEY_ID) is _production_record()
    assert LegalCorpusOperatorTrustRoot.resolve(_NEW_KEY_ID) is _active_production_record()
    assert _error_code(
        LegalCorpusOperatorTrustRoot.resolve,
        "prdca-key:legal-corpus-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    ) == "UNKNOWN_TRUSTED_KEY"


def test_production_validity_boundaries_are_deterministic() -> None:
    """Validity is certified at fixed boundaries rather than wall-clock state."""
    record = _production_record()
    valid_until = record.valid_until
    assert valid_until is not None
    assert not record.can_verify_at(AUTHORIZED_OPERATION, _PRODUCTION_VALID_FROM - timedelta(microseconds=1))
    assert record.can_verify_at(AUTHORIZED_OPERATION, _PRODUCTION_VALID_FROM)
    assert record.can_verify_at(AUTHORIZED_OPERATION, _PRODUCTION_VALID_FROM + timedelta(hours=12))
    assert not record.can_verify_at(AUTHORIZED_OPERATION, valid_until)
    assert not record.can_verify_at(AUTHORIZED_OPERATION, valid_until + timedelta(microseconds=1))
    assert not record.can_issue(AUTHORIZED_OPERATION, _PRODUCTION_VALID_FROM + timedelta(hours=12))


def test_new_active_production_validity_boundaries_are_deterministic() -> None:
    """The ACTIVE key issues only inside its exact finite 24-hour interval."""
    record = _active_production_record()
    assert not record.can_issue(AUTHORIZED_OPERATION, _NEW_VALID_FROM - timedelta(microseconds=1))
    assert record.can_issue(AUTHORIZED_OPERATION, _NEW_VALID_FROM)
    assert record.can_verify_at(AUTHORIZED_OPERATION, _NEW_VALID_FROM + timedelta(hours=12))
    assert not record.can_issue(AUTHORIZED_OPERATION, _NEW_VALID_UNTIL)
    assert not record.can_verify_at(AUTHORIZED_OPERATION, _NEW_VALID_UNTIL + timedelta(microseconds=1))


def test_production_source_identity_is_exact() -> None:
    """The certificate freezes the final governed source bytes and digest."""
    source = ROOT_PATH.read_bytes()
    assert len(source) == _PRODUCTION_SOURCE_BYTES
    assert hashlib.sha3_512(source).hexdigest() == _PRODUCTION_SOURCE_SHA3_512


def test_trusted_key_is_frozen() -> None:
    """Lifecycle and authority-bearing fields cannot be mutated in memory."""
    value = _record()
    with pytest.raises((AttributeError, TypeError)):
        value.status = LegalCorpusOperatorKeyStatus.RETIRED  # type: ignore[misc]
    with pytest.raises((AttributeError, TypeError)):
        value.issuer_identity = "issuer:changed"  # type: ignore[misc]


@pytest.mark.parametrize("algorithm", ["RSA", "Ed25519ph", ""])
def test_only_ed25519_is_supported(algorithm: str) -> None:
    """Algorithm substitution cannot create a valid trusted record."""
    assert _error_code(_record, algorithm=algorithm) == "ED25519_ALGORITHM_REQUIRED"


@pytest.mark.parametrize("permission", [frozenset(), frozenset({"PLATFORM_ADMIN"}), frozenset({"LEGAL_APPROVAL"}), frozenset({"LEGAL_CORPUS_DRAFT_ADMISSION", "PAYMENT"})])
def test_permission_is_exactly_least_privilege(permission: frozenset[str]) -> None:
    """Generic administrator, approval, payment, and empty permissions reject."""
    assert _error_code(_record, permitted_operations=permission) == "PERMITTED_OPERATION_INVALID"


@pytest.mark.parametrize("encoded", ["not-base64", "AAAA", _encoded_public_key() + "=", b"bytes", _encoded_public_key(b"x" * 33)])
def test_public_key_encoding_is_canonical_raw_32_byte_base64url(encoded: object) -> None:
    """Malformed, padded, wrong-sized, and wrong-typed key material rejects."""
    assert PUBLIC_KEY_ENCODING == "base64url_without_padding_raw_32_bytes"
    assert _error_code(_record, public_key_base64url=encoded) in {
        "PUBLIC_KEY_ENCODING_INVALID",
        "TRUSTED_KEY_FINGERPRINT_INVALID",
    }


def test_issuer_identity_is_required_and_fingerprinted() -> None:
    """Issuer identity is mandatory and changes integrity identity."""
    assert _error_code(_record, issuer_identity="") == "ISSUER_IDENTITY_REQUIRED"
    original = _record()
    changed = _record(issuer_identity="issuer:other")
    assert changed.fingerprint != original.fingerprint
    assert changed.to_document()["issuer_identity"] == "issuer:other"


def test_platform_scope_and_no_tenant_or_principal_fields() -> None:
    """Trust records are platform-only and expose no tenant identity surface."""
    value = _record()
    assert value.scope == "PLATFORM"
    assert {field.name for field in fields(value)}.isdisjoint({"tenant_id", "principal_id"})
    assert not hasattr(value, "tenant_id")
    assert not hasattr(value, "principal_id")


def test_statuses_are_distinct_immutable_trust_states() -> None:
    """ACTIVE, RETIRED, and REVOKED remain distinct and fingerprinted."""
    active = _record(status=LegalCorpusOperatorKeyStatus.ACTIVE)
    retired = _record(status=LegalCorpusOperatorKeyStatus.RETIRED)
    revoked = _record(status=LegalCorpusOperatorKeyStatus.REVOKED)
    assert {active.status.value, retired.status.value, revoked.status.value} == {"ACTIVE", "RETIRED", "REVOKED"}
    assert len({active.fingerprint, retired.fingerprint, revoked.fingerprint}) == 3
    at = active.valid_from + timedelta(hours=1)
    assert active.can_issue(AUTHORIZED_OPERATION, at)
    assert not retired.can_issue(AUTHORIZED_OPERATION, at)
    assert retired.can_verify_at(AUTHORIZED_OPERATION, at)
    assert not revoked.can_verify_at(AUTHORIZED_OPERATION, at)


def test_validity_requires_aware_ordered_timestamps() -> None:
    """Naive times and reversed intervals fail closed."""
    assert _error_code(_record, valid_from=datetime(2026, 9, 18)) == "VALID_FROM_INVALID"
    start = datetime(2026, 9, 18, tzinfo=timezone.utc)
    assert _error_code(_record, valid_from=start, valid_until=start - timedelta(seconds=1)) == "KEY_VALIDITY_INTERVAL_INVALID"
    value = _record()
    with pytest.raises(LegalCorpusOperatorTrustRootError, match="EVALUATION_TIMESTAMP_INVALID"):
        value.is_valid_at(datetime(2026, 9, 18))
    assert _record(valid_from=start + timedelta(hours=1)).fingerprint != value.fingerprint


def test_revision_and_provenance_are_required_and_fingerprinted() -> None:
    """Revision and fixed source provenance cannot be omitted or invented."""
    original = _record()
    assert _record(revision=2).fingerprint != original.fingerprint
    assert _error_code(_record, revision=0) == "KEY_REVISION_INVALID"
    assert _error_code(_record, revision=True) == "KEY_REVISION_INVALID"
    assert _error_code(_record, trust_root_provenance="caller:trust") == "TRUST_ROOT_PROVENANCE_INVALID"


def test_fingerprint_is_sha3_512_deterministic_and_nonrecursive() -> None:
    """Equivalent construction and serialization produce one stable digest."""
    first = _record()
    second = _record()
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 128
    assert first.fingerprint == first.fingerprint.lower()
    assert first.to_document() == second.to_document()
    assert "fingerprint" in first.to_document()
    assert first.fingerprint == LegalCorpusOperatorTrustedKey.fingerprint_for(
        **{name: getattr(first, name) for name in _SEMANTIC_FIELDS}
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("key_id", "prdca-key:legal-corpus-other"),
        ("public_key_base64url", _encoded_public_key(_ALTERNATE_PUBLIC_KEY)),
        ("issuer_identity", "issuer:other"),
        ("valid_until", datetime(2026, 9, 19, tzinfo=timezone.utc)),
        ("status", LegalCorpusOperatorKeyStatus.RETIRED),
        ("revision", 2),
    ],
)
def test_authority_bearing_field_changes_fingerprint(field: str, value: object) -> None:
    """Valid changes to each mutable trust fact change its fingerprint."""
    original = _record()
    changed = _record(**{field: value})
    assert changed.fingerprint != original.fingerprint


def test_fingerprint_tampering_is_rejected_at_constructor_boundary() -> None:
    """A supplied stale fingerprint cannot hydrate as a trusted record."""
    values = _fields()
    values["fingerprint"] = "0" * 128
    with pytest.raises(LegalCorpusOperatorTrustRootError, match="TRUSTED_KEY_FINGERPRINT_MISMATCH"):
        LegalCorpusOperatorTrustedKey(**values)


def test_resolver_has_no_caller_supplied_trust_map() -> None:
    """The canonical resolver accepts only a key ID and owns its root."""
    signature = inspect.signature(LegalCorpusOperatorTrustRoot.resolve)
    assert tuple(signature.parameters) == ("key_id",)
    with pytest.raises(TypeError):
        LegalCorpusOperatorTrustRoot.resolve("prdca-key:missing", {"key": "value"})  # type: ignore[call-arg]


def test_private_key_surface_and_dependency_boundary_are_absent() -> None:
    """The value/API expose public material only and no runtime authority imports."""
    public_names = set(vars(LegalCorpusOperatorTrustedKey))
    assert not any("private" in name.lower() or "secret" in name.lower() or name == "sign" for name in public_names)
    source = ROOT_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    modules = {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert not any(module.startswith(("pymongo", "fastapi", "requests", "httpx", "tools.eos.kernel")) for module in modules)
    assert "tools.eos.legal_operations.service.legal_corpus_provisioning_service" not in modules
    assert not any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"open", "urlopen"} for node in ast.walk(tree))
    assert "os.getenv" not in source
    assert "MongoClient" not in source


def test_source_bootstrap_is_static_two_key_and_side_effect_free() -> None:
    """Reloading preserves both source records without external effects."""
    import importlib

    module = importlib.import_module("tools.eos.legal_operations.domain.legal_corpus_operator_trust_root")
    reloaded = importlib.reload(module)
    assert reloaded.LegalCorpusOperatorTrustRoot.production_key_count() == 2
    assert len(reloaded.LegalCorpusOperatorTrustRoot.all_keys()) == 2
    assert reloaded.TRUSTED_KEYS[0].key_id == _PRODUCTION_KEY_ID
    assert reloaded.TRUSTED_KEYS[0].status is reloaded.LegalCorpusOperatorKeyStatus.RETIRED
    assert reloaded.TRUSTED_KEYS[0].revision == 2
    assert reloaded.TRUSTED_KEYS[1].key_id == _NEW_KEY_ID
    assert reloaded.TRUSTED_KEYS[1].status is reloaded.LegalCorpusOperatorKeyStatus.ACTIVE
    assert reloaded.TRUSTED_KEYS[1].revision == 1


def test_d1_uses_the_unchanged_canonical_resolver_contract() -> None:
    """D1 imports and calls the canonical resolver without issuing authority."""
    import importlib

    source = Path("tools/eos/legal_operations/domain/legal_corpus_operator_authorization.py").read_text(encoding="utf-8")
    assert "legal_corpus_operator_trust_root import" in source
    assert "LegalCorpusOperatorTrustRoot.resolve(self.key_id)" in source
    current_root = importlib.import_module("tools.eos.legal_operations.domain.legal_corpus_operator_trust_root")
    assert current_root.LegalCorpusOperatorTrustRoot.resolve(_PRODUCTION_KEY_ID) is current_root.TRUSTED_KEYS[0]


# ARTIFACT: test_legal_corpus_operator_trust_root.py
# VERSION: v1.3.0-R9B-P7-A2-R2-LEGAL-CORPUS-OPERATOR-TRUST-ROOT-CERT
# AUTHORITY BOUNDARY: direct evidence for public trust-root semantics only
# TENANT POSTURE: PLATFORM trust only; no tenant or principal authority
# FAIL-CLOSED POSTURE: exact two-key root, lifecycle boundaries, unknown keys, and invalid trust values reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
