"""Independent adversarial certificate for approval-registry preflight.

TITLE: WILSY OS Approval Registry Preflight Independent Certificate
VERSION: v1.1.0-R1D-B0F-R9B-P4-R3-R7-LEGAL-CORPUS-APPROVAL-REGISTRY-PREFLIGHT-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Independently certifies complete five-selector reconciliation without
         importing registry selector/state/collision oracles.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_corpus_approval_registry_preflight.py
COLLABORATION / OWNERSHIP: Certifies only the frozen approval registry seam;
                            service, Mongo, transaction, and promotion layers
                            remain outside this certificate.
CERTIFICATION / UPDATE DATE: 2026-09-19
CHANGELOG: v1.1.0-R1D-B0F-R9B-P4-R3-R7-LEGAL-CORPUS-APPROVAL-REGISTRY-PREFLIGHT-CERT
           replaces self-matching raw forbidden-oracle scans with one generic
           structural AST dependency audit and covers name, attribute, import,
           string, and assertion-message representations.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic signing material is memory-only and no
                            secret, network, or persistence authority is used.
TENANT BOUNDARY: PLATFORM approval only; no tenant or principal authority.
AUTHORITY BOUNDARY: Proofs are produced only by the governed verifier; this
                    certificate proves registry observation, not approval.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Corruption, read failures, partial identity, divergence,
                     and split rows are never converted to optimistic states.
"""
from __future__ import annotations

import ast
import base64
from copy import deepcopy
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, cast

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pymongo.errors import PyMongoError

from tools.eos.legal_operations import production_legal_corpus as corpus
from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAgreementType,
    LegalDocumentStatus,
    LegalDocumentVersion,
    canonical_document_digest,
)
from tools.eos.legal_operations.domain.legal_corpus_approval_authority import (
    APPROVAL_AUTHORITY_MECHANISM_VERSION,
    APPROVAL_SIGNING_MECHANISM_VERSION,
    LegalCorpusApprovalAuthorityEvidence,
    LegalCorpusApprovalAuthorityMechanism,
    LegalCorpusApprovalAuthorityScope,
    LegalCorpusApprovalAuthoritySource,
    LegalCorpusApprovalDecision,
    LegalCorpusApprovalOperation,
    LegalCorpusApprovalSigningMechanism,
)
from tools.eos.legal_operations.domain.legal_corpus_approval_authorization import (
    SCHEMA,
    LegalCorpusApprovalAuthorization,
    LegalCorpusApprovalAuthorizationOperation,
    LegalCorpusApprovalAuthorizationScope,
    VerifiedLegalCorpusApprovalAuthorization,
    canonical_signed_payload,
    verify_legal_corpus_approval_authorization,
)
from tools.eos.legal_operations.domain.legal_corpus_approval_trust_root import (
    APPROVAL_AUTHORITY_DOMAIN,
    APPROVAL_AUTHORITY_ROLE,
    APPROVAL_ISSUER_IDENTITY,
    APPROVAL_OPERATION,
    APPROVAL_SCOPE,
    APPROVAL_TRUST_ROOT_PROVENANCE,
    ED25519_ALGORITHM,
    LegalCorpusApprovalTrustRoot,
    LegalCorpusApprovalTrustStatus,
    LegalCorpusApprovalTrustedKey,
)
from tools.eos.legal_operations.registry import legal_corpus_approval_registry as registry


UTC = timezone.utc
NOW = datetime(2026, 9, 19, 12, 0, 0, 123456, tzinfo=UTC)
SOURCE = corpus.get_institutional_charter_draft()
EXPECTED_SELECTORS = (
    "evidence_id",
    "authorization_id",
    "authorization_idempotency",
    "evidence_idempotency",
    "target_version",
)
EXPECTED_STATES = {"ABSENT", "EXACT", "DIVERGENT", "SPLIT_IDENTITY"}
EXPECTED_CODES = {
    "evidence_id": "LEGAL_CORPUS_APPROVAL_EVIDENCE_ID_COLLISION",
    "authorization_id": "LEGAL_CORPUS_APPROVAL_AUTHORIZATION_ID_COLLISION",
    "authorization_idempotency": "LEGAL_CORPUS_APPROVAL_IDEMPOTENCY_CONFLICT",
    "evidence_idempotency": "LEGAL_CORPUS_APPROVAL_IDEMPOTENCY_CONFLICT",
    "target_version": "LEGAL_CORPUS_APPROVAL_IMMUTABILITY_CONFLICT",
}


def _approved(version: str = "1.0.0-APPROVED") -> LegalDocumentVersion:
    reference = f"wilsy-os://legal/institutional-charter/{version.casefold()}"
    return LegalDocumentVersion(
        document_id=SOURCE.document_id,
        agreement_type=LegalAgreementType.INSTITUTIONAL_CHARTER,
        version=version,
        title=SOURCE.title,
        jurisdiction=SOURCE.jurisdiction,
        locale=SOURCE.locale,
        effective_from=datetime(2026, 10, 1, tzinfo=UTC),
        status=LegalDocumentStatus.APPROVED,
        content_reference=reference,
        content=SOURCE.content,
        sha3_512=canonical_document_digest(SOURCE.content, reference),
        created_at=datetime(2026, 9, 19, 11, 0, 0, 654321, tzinfo=UTC),
        supersedes_document_id=SOURCE.document_id,
    )


def _key_root(private: Ed25519PrivateKey) -> LegalCorpusApprovalTrustRoot:
    raw = private.public_key().public_bytes_raw()
    encoded = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
    key_id = LegalCorpusApprovalTrustedKey.derive_key_id(encoded)
    valid_from = datetime(2026, 9, 19, tzinfo=UTC)
    valid_until = datetime(2026, 9, 20, tzinfo=UTC)
    values: dict[str, Any] = {
        "key_id": key_id,
        "issuer_identity": APPROVAL_ISSUER_IDENTITY,
        "authority_role": APPROVAL_AUTHORITY_ROLE,
        "authority_domain": APPROVAL_AUTHORITY_DOMAIN,
        "algorithm": ED25519_ALGORITHM,
        "public_key_base64url": encoded,
        "valid_from": valid_from,
        "valid_until": valid_until,
        "status": LegalCorpusApprovalTrustStatus.ACTIVE,
        "revision": 1,
        "permitted_operations": frozenset({APPROVAL_OPERATION}),
        "scope": APPROVAL_SCOPE,
        "trust_root_provenance": APPROVAL_TRUST_ROOT_PROVENANCE,
    }
    values["trust_fingerprint"] = LegalCorpusApprovalTrustedKey.fingerprint_for(**values)
    return LegalCorpusApprovalTrustRoot((LegalCorpusApprovalTrustedKey(**values),))


def _proof(
    *,
    evidence_changes: dict[str, object] | None = None,
    authorization_changes: dict[str, object] | None = None,
    approved_document: LegalDocumentVersion | None = None,
) -> VerifiedLegalCorpusApprovalAuthorization:
    private = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    approved = approved_document or _approved()
    evidence_values: dict[str, Any] = {
        "approval_evidence_id": "approval-evidence-001",
        "schema_version": "v1.0.0",
        "scope": LegalCorpusApprovalAuthorityScope.PLATFORM,
        "operation": LegalCorpusApprovalOperation.DOCUMENT_APPROVAL,
        "approval_decision": LegalCorpusApprovalDecision.APPROVE,
        "approval_authority_source": LegalCorpusApprovalAuthoritySource.HUMAN_GOVERNED,
        "approval_authority_mechanism": LegalCorpusApprovalAuthorityMechanism.HUMAN_APPROVAL_RECORD,
        "approval_authority_mechanism_version": APPROVAL_AUTHORITY_MECHANISM_VERSION,
        "human_authority_representation": "independent-governance-record",
        "approval_signing_mechanism": LegalCorpusApprovalSigningMechanism.EXTERNAL_GOVERNED_SIGNER,
        "approval_signing_mechanism_version": APPROVAL_SIGNING_MECHANISM_VERSION,
        "approval_signing_key_id": "independent-approval-key",
        "approval_signature_reference": "independent-signature-reference",
        "source_document": SOURCE,
        "approved_document": approved,
        "approved_at": datetime(2026, 9, 19, 11, 30, 0, 123456, tzinfo=UTC),
        "effective_from": approved.effective_from,
        "idempotency_key": "evidence-idempotency-001",
        "provenance_reference": "independent-governance-record",
    }
    evidence_values.update(evidence_changes or {})
    evidence_values["evidence_fingerprint"] = LegalCorpusApprovalAuthorityEvidence.fingerprint_for(**evidence_values)
    evidence = LegalCorpusApprovalAuthorityEvidence(**evidence_values)
    key = _key_root(private).all_keys()[0]
    authorization_values: dict[str, Any] = {
        "authorization_id": "123e4567-e89b-42d3-a456-426614174000",
        "issuer_identity": APPROVAL_ISSUER_IDENTITY,
        "authority_role": APPROVAL_AUTHORITY_ROLE,
        "authority_domain": APPROVAL_AUTHORITY_DOMAIN,
        "algorithm": ED25519_ALGORITHM,
        "key_id": key.key_id,
        "trust_fingerprint": key.trust_fingerprint,
        "operation": LegalCorpusApprovalAuthorizationOperation.DOCUMENT_APPROVAL,
        "scope": LegalCorpusApprovalAuthorizationScope.PLATFORM,
        "approval_evidence": evidence,
        "issued_at": NOW,
        "expires_at": NOW + timedelta(minutes=30),
        "nonce": base64.urlsafe_b64encode(b"n" * 32).rstrip(b"=").decode("ascii"),
        "idempotency_key": "223e4567-e89b-42d3-a456-426614174001",
        "signature_base64url": base64.urlsafe_b64encode(b"s" * 64).rstrip(b"=").decode("ascii"),
        "schema": SCHEMA,
    }
    authorization_values.update(authorization_changes or {})
    unsigned = LegalCorpusApprovalAuthorization(**authorization_values)
    signature = base64.urlsafe_b64encode(private.sign(canonical_signed_payload(unsigned))).rstrip(b"=").decode("ascii")
    signed = LegalCorpusApprovalAuthorization(**{**authorization_values, "signature_base64url": signature})
    return verify_legal_corpus_approval_authorization(
        signed,
        _key_root(private),
        now=NOW,
        source_document=SOURCE,
        approved_document=approved,
    )


def _stored(proof: VerifiedLegalCorpusApprovalAuthorization) -> dict[str, Any]:
    payload = deepcopy(proof.authorization.to_document())
    payload["approval_evidence_fingerprint"] = proof.approval_evidence.evidence_fingerprint
    return payload


def _path(row: dict[str, Any], path: str) -> Any:
    value: Any = row
    for part in path.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


class IndependentCollection:
    """Independent Mongo-shaped fake with exact query and mutation telemetry."""

    def __init__(self, documents: list[dict[str, Any]] | None = None) -> None:
        self.documents = deepcopy(documents or [])
        self.find_calls: list[tuple[dict[str, Any], Any]] = []
        self.insert_calls: list[tuple[dict[str, Any], Any]] = []
        self.update_calls = 0
        self.replace_calls = 0
        self.delete_calls = 0
        self.index_calls = 0
        self.index_definitions: list[tuple[Any, dict[str, Any]]] = []
        self.fail_at: int | None = None
        self.read_count = 0

    def find_one(self, query: dict[str, Any], *, session: Any = None) -> dict[str, Any] | None:
        self.read_count += 1
        self.find_calls.append((deepcopy(query), session))
        if self.fail_at == self.read_count:
            raise PyMongoError(f"read-{self.read_count}")
        for document in self.documents:
            if all(_path(document, key) == value for key, value in query.items()):
                return deepcopy(document)
        return None

    def insert_one(self, document: dict[str, Any], *, session: Any = None) -> object:
        self.insert_calls.append((deepcopy(document), session))
        self.documents.append(deepcopy(document))
        return object()

    def create_index(self, *args: Any, **kwargs: Any) -> str:
        self.index_calls += 1
        self.index_definitions.append((args[0] if args else None, dict(kwargs)))
        return str(kwargs.get("name", "index"))


def _preflight(proof: object, collection: IndependentCollection, session: Any = None) -> Any:
    return registry.LegalCorpusApprovalRegistry.preflight_verified_approval(cast(Any, proof), collection, session=session)


def _error(call: Callable[[], Any]) -> registry.LegalCorpusApprovalRegistryError:
    with pytest.raises(registry.LegalCorpusApprovalRegistryError) as captured:
        call()
    return captured.value


def _one_selector_row(selector: str, target: VerifiedLegalCorpusApprovalAuthorization) -> dict[str, Any]:
    """Create a valid row whose independent query model matches one selector."""
    altered: dict[str, object] = {
        "authorization_id": "323e4567-e89b-42d3-a456-426614174010",
        "idempotency_key": "323e4567-e89b-42d3-a456-426614174011",
    }
    evidence_changes: dict[str, object] = {
        "approval_evidence_id": "approval-evidence-altered",
        "idempotency_key": "evidence-idempotency-altered",
    }
    approved = _approved("1.0.0-OTHER")
    if selector == "evidence_id":
        evidence_changes["approval_evidence_id"] = target.approval_evidence.approval_evidence_id
    elif selector == "authorization_id":
        altered["authorization_id"] = target.authorization.authorization_id
    elif selector == "authorization_idempotency":
        altered["idempotency_key"] = target.authorization.idempotency_key
    elif selector == "evidence_idempotency":
        evidence_changes["idempotency_key"] = target.approval_evidence.idempotency_key
    elif selector == "target_version":
        approved = _approved()
    else:
        raise AssertionError("unknown independent selector")
    return _stored(_proof(evidence_changes=evidence_changes, authorization_changes=altered, approved_document=approved))


def test_independent_contract_oracles_are_literal_and_complete() -> None:
    assert EXPECTED_SELECTORS == (
        "evidence_id", "authorization_id", "authorization_idempotency",
        "evidence_idempotency", "target_version",
    )
    assert EXPECTED_STATES == {"ABSENT", "EXACT", "DIVERGENT", "SPLIT_IDENTITY"}
    assert tuple(EXPECTED_CODES) == EXPECTED_SELECTORS


@pytest.mark.parametrize("bad", [None, {}, object(), False, "proof"])
def test_verified_proof_only_boundary(bad: object) -> None:
    error = _error(lambda: _preflight(bad, IndependentCollection()))
    assert error.code == "LEGAL_CORPUS_APPROVAL_AUTHORITY_INPUT_INVALID"


def test_all_five_absent_is_absent_and_nonmutating() -> None:
    collection = IndependentCollection()
    result = _preflight(_proof(), collection, session=None)
    assert result.state.value == "ABSENT"
    assert len(collection.find_calls) == 5
    assert collection.insert_calls == []
    assert collection.update_calls == collection.replace_calls == collection.delete_calls == 0
    assert collection.index_calls == 0


@pytest.mark.parametrize("selector", EXPECTED_SELECTORS)
def test_each_single_selector_match_never_manufactures_absent(selector: str) -> None:
    target = _proof()
    row = _one_selector_row(selector, target)
    result = _preflight(target, IndependentCollection([row]))
    assert result.state.value != "ABSENT"
    assert result.state.value == "DIVERGENT"
    assert result.collision_code == EXPECTED_CODES[selector]


def test_exact_requires_all_five_same_row_and_is_immutable() -> None:
    proof = _proof()
    row = _stored(proof)
    row["_id"] = "physical-exact-row"
    result = _preflight(proof, IndependentCollection([row]))
    assert result.state.value == "EXACT"
    assert result.matched_identities == ("mongo:physical-exact-row",)
    assert tuple(name for name, _ in result.selector_to_row_identity) == EXPECTED_SELECTORS
    with pytest.raises(FrozenInstanceError):
        result.state = result.state  # type: ignore[misc]


def test_four_same_row_one_absent_is_not_exact() -> None:
    proof = _proof()
    row = _stored(_proof(approved_document=_approved("1.0.0-OTHER")))
    result = _preflight(proof, IndependentCollection([row]))
    assert result.state.value == "DIVERGENT"
    assert result.state.value != "EXACT"


def test_same_selectors_with_semantic_signed_field_difference_is_divergent() -> None:
    proof = _proof()
    row = _stored(proof)
    row["signature_base64url"] = base64.urlsafe_b64encode(b"d" * 64).rstrip(b"=").decode("ascii")
    result = _preflight(proof, IndependentCollection([row]))
    assert result.state.value == "DIVERGENT"
    assert result.collision_code == EXPECTED_CODES["evidence_id"]


def test_id_metadata_does_not_change_semantic_exactness() -> None:
    proof = _proof()
    with_id = _preflight(proof, IndependentCollection([{**_stored(proof), "_id": "with-id"}]))
    without_id = _preflight(proof, IndependentCollection([_stored(proof)]))
    assert with_id.state.value == without_id.state.value == "EXACT"
    assert with_id.matched_identities == ("mongo:with-id",)
    assert without_id.matched_identities[0].startswith("semantic:")


def test_two_three_and_maximum_practical_splits_are_explicit() -> None:
    proof = _proof()
    rows = [{**_one_selector_row(selector, proof), "_id": f"split-{index}"} for index, selector in enumerate(EXPECTED_SELECTORS)]
    two_rows = rows[:2]
    three_rows = rows[:3]
    maximum_rows = rows
    expected_two_selectors = {"evidence_id", "authorization_id"}
    expected_three_selectors = {"evidence_id", "authorization_id", "authorization_idempotency"}
    expected_maximum_selectors = {
        "evidence_id",
        "authorization_id",
        "authorization_idempotency",
        "evidence_idempotency",
        "target_version",
    }
    assert len(two_rows) == len(expected_two_selectors) == 2
    assert len(three_rows) == len(expected_three_selectors) == 3
    assert len(maximum_rows) == len(expected_maximum_selectors) == 5
    assert len(EXPECTED_SELECTORS) == 5
    assert len({row["_id"] for row in two_rows}) == len(two_rows)
    assert len({row["_id"] for row in three_rows}) == len(three_rows)
    assert len({row["_id"] for row in maximum_rows}) == len(maximum_rows)
    assert all(
        row["approval_evidence_fingerprint"] == row["approval_evidence"]["evidence_fingerprint"]
        for row in maximum_rows
    )
    assert all(
        registry.LegalCorpusApprovalRegistry.get_by_approval_evidence_id(
            row["approval_evidence"]["approval_evidence_id"], IndependentCollection([row])
        ) is not None
        for row in maximum_rows
    )
    three = _preflight(proof, IndependentCollection(three_rows))
    two = _preflight(proof, IndependentCollection(two_rows))
    maximum = _preflight(proof, IndependentCollection(maximum_rows))
    for result, expected_selectors, expected_rows in (
        (two, expected_two_selectors, two_rows),
        (three, expected_three_selectors, three_rows),
        (maximum, expected_maximum_selectors, maximum_rows),
    ):
        assert result.state.value == "SPLIT_IDENTITY"
        assert {selector for selector, _ in result.selector_to_row_identity} == expected_selectors
        assert len(result.selector_to_row_identity) == len(expected_selectors)
        assert len(result.matched_identities) == len(expected_rows)
        assert len({identity for _, identity in result.selector_to_row_identity}) == len(expected_rows)


@pytest.mark.parametrize("mutation", [
    lambda row: row.pop("authorization_id"),
    lambda row: row.__setitem__("extra", True),
    lambda row: row["approval_evidence"].pop("evidence_fingerprint"),
    lambda row: row["approval_evidence"].__setitem__("extra", True),
    lambda row: row.__setitem__("approval_evidence_fingerprint", "0" * 128),
    lambda row: row.__setitem__("signature_base64url", "not-base64"),
    lambda row: row.__setitem__("issued_at", "2026-09-19T12:00:00+00:00"),
    lambda row: row["approval_evidence"].__setitem__("source_content", "changed"),
])
def test_reachable_corrupt_rows_are_persisted_invalid(mutation: Callable[[dict[str, Any]], object]) -> None:
    proof = _proof()
    row = _stored(proof)
    mutation(row)
    assert _path(row, "approval_evidence.approval_evidence_id") == proof.approval_evidence.approval_evidence_id
    error = _error(lambda: _preflight(proof, IndependentCollection([row])))
    assert error.code == "LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID"


@pytest.mark.parametrize("position", [1, 2, 3, 4, 5])
def test_each_selector_read_failure_is_bounded_and_causal(position: int) -> None:
    lower = PyMongoError(f"read-{position}")
    collection = IndependentCollection()
    collection.fail_at = position
    error = _error(lambda: _preflight(_proof(), collection, session=object()))
    assert error.code == "LEGAL_CORPUS_APPROVAL_READ_FAILED"
    assert error.__cause__ is lower or isinstance(error.__cause__, PyMongoError)
    assert collection.insert_calls == []


def test_all_five_reads_forward_exact_session_identity() -> None:
    session = object()
    collection = IndependentCollection()
    _preflight(_proof(), collection, session=session)
    assert len(collection.find_calls) == 5
    assert all(observed is session for _, observed in collection.find_calls)


def test_admission_regression_and_get_by_evidence_remain_fail_closed() -> None:
    proof = _proof()
    absent = IndependentCollection()
    created = registry.LegalCorpusApprovalRegistry.admit_verified_approval(proof, absent)
    assert created.state.value == "CREATED"
    exact = IndependentCollection([_stored(proof)])
    replay = registry.LegalCorpusApprovalRegistry.admit_verified_approval(proof, exact)
    assert replay.state.value == "EXACT_REPLAY"
    split = IndependentCollection([
        {**_one_selector_row("evidence_id", proof), "_id": "evidence-row"},
        {**_one_selector_row("authorization_id", proof), "_id": "authorization-row"},
    ])
    assert _error(lambda: registry.LegalCorpusApprovalRegistry.admit_verified_approval(proof, split)).code == "LEGAL_CORPUS_APPROVAL_IMMUTABILITY_CONFLICT"
    found = registry.LegalCorpusApprovalRegistry.get_by_approval_evidence_id(proof.approval_evidence.approval_evidence_id, exact, session="s")
    assert found is not None
    assert exact.find_calls[-1][1] == "s"
    assert exact.insert_calls == []


FORBIDDEN_ORACLE_SYMBOLS = frozenset(
    {
        "_identity_queries",
        "_collision_code",
        "LegalCorpusApprovalPreflightState",
    }
)


def _structural_forbidden_oracle_references(source: str, forbidden: set[str]) -> set[str]:
    """Return executable forbidden dependencies without inspecting literals."""
    tree = ast.parse(source)
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in forbidden:
            found.add(node.id)
        elif isinstance(node, ast.Attribute) and node.attr in forbidden:
            found.add(node.attr)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                imported_name = alias.name.rsplit(".", 1)[-1]
                bound_name = alias.asname
                if imported_name in forbidden:
                    found.add(imported_name)
                if bound_name in forbidden:
                    found.add(bound_name)
    return found


def test_source_and_certificate_defend_against_oracle_masking_and_lifecycle() -> None:
    source = Path(registry.__file__).read_text(encoding="utf-8")
    certificate = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    attrs = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert "MongoClient" not in names
    assert not attrs.intersection({"start_session", "start_transaction", "commit_transaction", "abort_transaction", "with_transaction"})
    broad_pytest = ("pytest.raises(" + "Exception)", "pytest.raises(" + "BaseException)")
    broad_except = ("except " + "Exception", "except " + "BaseException")
    contains_forbidden = lambda sample: any(token in sample for token in broad_pytest + broad_except)
    assert not contains_forbidden(certificate)
    assert contains_forbidden("with pytest.raises(" + "Exception): pass")
    assert not contains_forbidden("with pytest.raises(ValueError): pass")

    assert _structural_forbidden_oracle_references(certificate, set(FORBIDDEN_ORACLE_SYMBOLS)) == set()

    for symbol in FORBIDDEN_ORACLE_SYMBOLS:
        assert _structural_forbidden_oracle_references(f'value = "{symbol}"\n', {symbol}) == set()
        assert _structural_forbidden_oracle_references(f'assert True, "{symbol}"\n', {symbol}) == set()
        assert _structural_forbidden_oracle_references(f"{symbol}()\n", {symbol}) == {symbol}
        assert _structural_forbidden_oracle_references(f"obj.{symbol}\n", {symbol}) == {symbol}
        assert _structural_forbidden_oracle_references(f"import {symbol}\n", {symbol}) == {symbol}
        assert _structural_forbidden_oracle_references(f"from module import {symbol}\n", {symbol}) == {symbol}
        assert _structural_forbidden_oracle_references(f"from module import {symbol} as bound\n", {symbol}) == {symbol}


def test_duplicatekey_regression_cases_remain_present_for_next_recertification() -> None:
    direct_certificate = Path("tests/unit/test_legal_corpus_approval_registry.py").read_text(encoding="utf-8")
    assert "def test_duplicate_race_exact_reconciles_with_causal_duplicate" in direct_certificate
    assert "def test_duplicate_race_divergent_readback_fails_closed" in direct_certificate
    assert "def test_duplicate_race_split_identity_readback_fails_closed" in direct_certificate


def test_durable_schema_and_index_contract_remain_unchanged() -> None:
    assert registry.COLLECTION == "legal_corpus_approval_evidence"
    stored = _stored(_proof())
    assert len(stored) == 17
    assert len(stored["approval_evidence"]) == 44
    assert "tenant_id" not in stored
    assert "tenant_id" not in stored["approval_evidence"]
    collection = IndependentCollection()
    registry.LegalCorpusApprovalRegistry.ensure_indexes(collection)
    assert collection.index_calls == 7
    assert [definition[0] for definition in collection.index_definitions] == [
        [("approval_evidence.approval_evidence_id", 1)],
        [("authorization_id", 1)],
        [("scope", 1), ("operation", 1), ("idempotency_key", 1)],
        [("scope", 1), ("operation", 1), ("approval_evidence.idempotency_key", 1)],
        [("scope", 1), ("operation", 1), ("approval_evidence.approved_document_id", 1), ("approval_evidence.approved_version", 1)],
        [("approval_evidence.evidence_fingerprint", 1)],
        [("approval_evidence.source_document_id", 1), ("approval_evidence.source_version", 1)],
    ]


# ARTIFACT: test_legal_corpus_approval_registry_preflight.py
# VERSION: v1.1.0-R1D-B0F-R9B-P4-R3-R7-LEGAL-CORPUS-APPROVAL-REGISTRY-PREFLIGHT-CERT
# AUTHORITY BOUNDARY: independent observation-only certification of five-selector preflight
# TENANT POSTURE: PLATFORM-only; no tenant/principal authority
# FAIL-CLOSED POSTURE: no optimistic absence, exactness, or split-row selection
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
