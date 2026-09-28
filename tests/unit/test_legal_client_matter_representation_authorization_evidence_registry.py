"""Direct certificate for the L9C11-P18 authorization-evidence registry.

TITLE: WILSY OS L9C11-P18 Client Representation Authorization Evidence Registry Certificate
VERSION: v1.0.0-L9C11-P18-CLIENT-REPRESENTATION-AUTHORIZATION-EVIDENCE-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove immutable tenant-scoped P17 evidence persistence, replay,
         strict BSON hydration, bounded lineage history and caller-owned
         transaction behavior without live Mongo or authority evaluation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_representation_authorization_evidence_registry.py
COLLABORATION / OWNERSHIP: P17 owns the evidence value; P18 owns only its
                            durable registry certificate. P1, IAM, currentness,
                            orchestration, Representation formation, Court and
                            finance remain separate gates.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0 covers explicit collection/transaction boundaries,
           tenant-scoped identities, BSON capability normalization, exact
           replay/collision/race handling, deterministic history and authority
           exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only.
TENANT BOUNDARY: Every fixture and query is explicitly tenant-scoped.
AUTHORITY BOUNDARY: P17 evidence persistence/read only; no live authority.
FINANCIAL AUTHORITY BOUNDARY: No financial execution or settlement authority.
"""
from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, TypedDict, cast

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    LegalClientActingCapacityType,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_authorization_evidence import (
    LegalClientMatterRepresentationAuthorizationEvidence,
)
from tools.eos.legal_operations.registry.legal_client_matter_representation_authorization_evidence_registry import (
    AUTHORIZATION_EVIDENCE_ID_INDEX_NAME,
    COLLECTION,
    EVIDENCE_ID_INDEX_NAME,
    FINGERPRINT_INDEX_NAME,
    HISTORY_INDEX_FIELDS,
    HISTORY_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    VERSION,
    LegalClientMatterRepresentationAuthorizationEvidenceRegistryConflictError,
    LegalClientMatterRepresentationAuthorizationEvidenceRegistryInputError,
    LegalClientMatterRepresentationAuthorizationEvidenceRegistryNotFoundError,
    LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError,
    LegalClientMatterRepresentationAuthorizationEvidenceRegistryRetryRequiredError,
    LegalClientMatterRepresentationAuthorizationEvidenceRegistryTransactionRequiredError,
    ensure_indexes,
    get_authorization_evidence,
    get_authorization_evidence_by_fingerprint,
    get_authorization_evidence_by_idempotency_key,
    list_authorization_evidence_for_context,
    persist_authorization_evidence,
)


BASE = datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc)
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128


class Session:
    """Minimal active caller-owned transaction marker."""

    in_transaction = True


class InactiveSession:
    """Minimal inactive transaction marker."""

    in_transaction = False


class Cursor:
    """Small Mongo-like cursor supporting deterministic sort and limit."""

    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def sort(self, keys: list[tuple[str, int]]) -> "Cursor":
        for key, direction in reversed(keys):
            self.rows.sort(
                key=lambda row: cast(Any, row.get(key)),
                reverse=direction < 0,
            )
        return self

    def limit(self, count: int) -> "Cursor":
        self.rows = self.rows[:count]
        return self

    def __iter__(self):
        return iter(self.rows)


class Collection:
    """Recording fake proving filters, sessions, indexes and writes."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[dict[str, object]] = []
        self.calls: list[tuple[str, object, dict[str, object] | None]] = []

    def with_options(self, **_: object) -> "Collection":
        return self

    def create_index(
        self,
        keys: list[tuple[str, int]],
        *,
        unique: bool,
        name: str,
    ) -> str:
        self.indexes.append({"keys": keys, "unique": unique, "name": name})
        return name

    def find(self, query: dict[str, object], *, session: object) -> Cursor:
        self.calls.append(("find", session, dict(query)))
        return Cursor(
            [
                dict(row)
                for row in self.rows
                if all(row.get(key) == value for key, value in query.items())
            ]
        )

    def insert_one(self, document: dict[str, object], *, session: object) -> object:
        self.calls.append(("insert_one", session, None))
        self.rows.append(dict(document))
        return object()


class DuplicateRaceCollection(Collection):
    """Fake where a concurrent insert wins between preflight and insert."""

    def __init__(self, winning: dict[str, object]) -> None:
        super().__init__()
        self.winning = dict(winning)
        self.hidden = True

    def find(self, query: dict[str, object], *, session: object) -> Cursor:
        if self.hidden:
            return Cursor([])
        return super().find(query, session=session)

    def insert_one(self, document: dict[str, object], *, session: object) -> object:
        self.hidden = False
        self.rows.append(dict(self.winning))
        raise DuplicateKeyError("synthetic duplicate race")


def evidence(
    *,
    tenant_id: str = "tenant-p18-a",
    idempotency_key: str = "idempotency:p18-1",
    representative_principal_id: str = "principal-attorney-p18",
    representative_role: str = "LEGAL_ATTORNEY",
    effective_offset: int = 0,
) -> LegalClientMatterRepresentationAuthorizationEvidence:
    """Build valid synthetic P17 evidence without live reads."""
    occurred = BASE + timedelta(minutes=effective_offset)
    return LegalClientMatterRepresentationAuthorizationEvidence(
        tenant_id=tenant_id,
        case_matter_id="matter-p18",
        matter_fingerprint=HEX_A,
        client_party_id="party-p18",
        subject_reference="client:subject-p18",
        subject_identity_fingerprint=HEX_B,
        client_subject_principal_id="principal-client-p18",
        appointing_principal_id="principal-client-p18",
        appointing_principal_status=PrincipalStatus.ACTIVE,
        appointing_membership_status=TenantMembershipStatus.ACTIVE,
        appointing_membership_revision=4,
        appointing_role="LEGAL_CLIENT",
        appointing_role_assignment_revision=7,
        client_visibility_reference="visibility:p18",
        client_visibility_fingerprint=HEX_C,
        client_visibility_status="ACTIVE",
        acting_capacity_id="capacity-p18",
        acting_capacity_fingerprint=HEX_B,
        acting_capacity_type=LegalClientActingCapacityType.SELF,
        engagement_id="engagement-p18",
        engagement_fingerprint=HEX_C,
        mandate_id="mandate-p18",
        mandate_fingerprint=HEX_A,
        mandate_scope_reference="scope:p18",
        mandate_scope_fingerprint=HEX_B,
        mandate_capabilities=["ADVISORY", "NEGOTIATION"],
        representative_principal_id=representative_principal_id,
        representative_principal_status=PrincipalStatus.ACTIVE,
        representative_membership_status=TenantMembershipStatus.ACTIVE,
        representative_membership_revision=3,
        representative_role_assignment_revision=8,
        representative_role=representative_role,
        representative_eligibility_policy_version="roles:v1.29.0",
        representation_scope_capabilities=["ADVISORY"],
        decision="AUTHORIZED",
        source_evidence_reference="evidence:p18-1",
        source_evidence_fingerprint=HEX_A,
        occurred_at=occurred,
        effective_from=occurred + timedelta(minutes=1),
        idempotency_key=idempotency_key,
    )


class _HistoryKwargs(TypedDict):
    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    client_party_id: str
    subject_identity_fingerprint: str
    appointing_principal_id: str
    acting_capacity_id: str
    acting_capacity_fingerprint: str
    engagement_id: str
    engagement_fingerprint: str
    mandate_id: str
    mandate_fingerprint: str
    representative_principal_id: str
    representative_role: str


def _history_kwargs(value: LegalClientMatterRepresentationAuthorizationEvidence) -> _HistoryKwargs:
    return {
        "tenant_id": value.tenant_id,
        "case_matter_id": value.case_matter_id,
        "matter_fingerprint": value.matter_fingerprint,
        "client_party_id": value.client_party_id,
        "subject_identity_fingerprint": value.subject_identity_fingerprint,
        "appointing_principal_id": value.appointing_principal_id,
        "acting_capacity_id": value.acting_capacity_id,
        "acting_capacity_fingerprint": value.acting_capacity_fingerprint,
        "engagement_id": value.engagement_id,
        "engagement_fingerprint": value.engagement_fingerprint,
        "mandate_id": value.mandate_id,
        "mandate_fingerprint": value.mandate_fingerprint,
        "representative_principal_id": value.representative_principal_id,
        "representative_role": value.representative_role,
    }


def test_registry_identity_version_collection_and_indexes() -> None:
    collection = Collection()
    ensure_indexes(collection)
    assert VERSION == "v1.0.0-L9C11-P18-CLIENT-REPRESENTATION-AUTHORIZATION-EVIDENCE-REGISTRY"
    assert COLLECTION == "legal_client_matter_representation_authorization_evidence"
    assert EVIDENCE_ID_INDEX_NAME == AUTHORIZATION_EVIDENCE_ID_INDEX_NAME
    assert {cast(str, item["name"]) for item in collection.indexes} == {
        EVIDENCE_ID_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        IDEMPOTENCY_INDEX_NAME,
        HISTORY_INDEX_NAME,
    }
    assert sum(bool(item["unique"]) for item in collection.indexes) == 3
    assert all("expireAfterSeconds" not in item for item in collection.indexes)
    history = next(item for item in collection.indexes if item["name"] == HISTORY_INDEX_NAME)
    assert [key for key, _direction in cast(list[tuple[str, int]], history["keys"])] == list(HISTORY_INDEX_FIELDS)
    assert "current" not in HISTORY_INDEX_NAME.lower()


def test_explicit_collection_and_exact_domain_are_required() -> None:
    value = evidence()
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceRegistryInputError):
        ensure_indexes(None)
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceRegistryInputError):
        persist_authorization_evidence(value, None, session=Session())
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceRegistryInputError):
        persist_authorization_evidence(cast(Any, value.to_dict()), Collection(), session=Session())


def test_missing_and_inactive_transactions_are_rejected() -> None:
    value = evidence()
    collection = Collection()
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceRegistryTransactionRequiredError):
        persist_authorization_evidence(value, collection, session=None)
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceRegistryTransactionRequiredError):
        get_authorization_evidence(value.tenant_id, value.evidence_id, collection, session=InactiveSession())


def test_active_transaction_is_propagated_and_registry_owns_no_lifecycle() -> None:
    collection = Collection()
    value = evidence()
    result = persist_authorization_evidence(value, collection, session=Session())
    assert result == value
    assert collection.rows == [value.to_dict()]
    assert all(call[1].__class__ is Session for call in collection.calls)
    call_names = [call[0] for call in collection.calls]
    assert "start_transaction" not in call_names
    assert "commit_transaction" not in call_names
    assert "abort_transaction" not in call_names


def test_canonical_payload_and_bson_capability_round_trip_are_exact() -> None:
    collection = Collection()
    value = evidence()
    persisted = persist_authorization_evidence(value, collection, session=Session())
    assert persisted.to_dict() == value.to_dict()
    assert isinstance(collection.rows[0]["mandate_capabilities"], list)
    assert isinstance(collection.rows[0]["representation_scope_capabilities"], list)
    assert get_authorization_evidence(value.tenant_id, value.evidence_id, collection, session=Session()) == value


def test_malformed_bson_container_or_schema_fails_closed() -> None:
    value = evidence()
    scalar = Collection()
    scalar.rows.append({**value.to_dict(), "mandate_capabilities": "ADVISORY"})
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError):
        get_authorization_evidence(value.tenant_id, value.evidence_id, scalar, session=Session())
    unknown = Collection()
    unknown.rows.append({**value.to_dict(), "unexpected": True})
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError):
        get_authorization_evidence(value.tenant_id, value.evidence_id, unknown, session=Session())
    missing = Collection()
    row = value.to_dict()
    del row["source_evidence_fingerprint"]
    missing.rows.append(row)
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError):
        get_authorization_evidence(value.tenant_id, value.evidence_id, missing, session=Session())


@pytest.mark.parametrize(
    "field",
    ["evidence_id", "fingerprint", "decision", "acting_capacity_type", "representative_role"],
)
def test_corrupted_p17_semantics_and_integrity_are_rejected(field: str) -> None:
    value = evidence()
    row = value.to_dict()
    row[field] = {
        "evidence_id": "client-representation-authorization:corrupt",
        "fingerprint": "0" * 128,
        "decision": "REVIEW",
        "acting_capacity_type": "REPRESENTATIVE",
        "representative_role": "LEGAL_PARALEGAL",
    }[field]
    collection = Collection()
    collection.rows.append(row)
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError):
        get_authorization_evidence(
            value.tenant_id,
            str(row["evidence_id"] if field == "evidence_id" else value.evidence_id),
            collection,
            session=Session(),
        )


def test_exact_replay_is_one_row_and_all_identity_reads_are_tenant_scoped() -> None:
    collection = Collection()
    value = evidence()
    other = evidence(tenant_id="tenant-p18-b")
    assert persist_authorization_evidence(value, collection, session=Session()) == value
    assert persist_authorization_evidence(value, collection, session=Session()) == value
    assert persist_authorization_evidence(other, collection, session=Session()) == other
    assert len(collection.rows) == 2
    assert get_authorization_evidence_by_fingerprint(other.tenant_id, other.fingerprint, collection, session=Session()) == other
    assert get_authorization_evidence_by_idempotency_key(value.tenant_id, value.idempotency_key, collection, session=Session()) == value
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceRegistryNotFoundError):
        get_authorization_evidence("tenant-p18-missing", value.evidence_id, collection, session=Session())
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceRegistryNotFoundError):
        get_authorization_evidence_by_fingerprint("tenant-p18-missing", value.fingerprint, collection, session=Session())
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceRegistryNotFoundError):
        get_authorization_evidence_by_idempotency_key("tenant-p18-missing", value.idempotency_key, collection, session=Session())
    queries = [call[2] for call in collection.calls if call[0] == "find"]
    assert queries and all(query is not None and query.get("tenant_id") for query in queries)


def test_divergent_idempotency_evidence_id_and_fingerprint_collisions_fail_closed() -> None:
    collection = Collection()
    value = evidence()
    persist_authorization_evidence(value, collection, session=Session())
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceRegistryConflictError):
        persist_authorization_evidence(evidence(representative_principal_id="principal-partner-p18", idempotency_key=value.idempotency_key), collection, session=Session())
    divergent_id = evidence(representative_principal_id="principal-partner-p18", idempotency_key="idempotency:p18-id")
    object.__setattr__(divergent_id, "evidence_id", value.evidence_id)
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceRegistryConflictError):
        persist_authorization_evidence(divergent_id, collection, session=Session())
    divergent_fingerprint = evidence(representative_principal_id="principal-partner-p18", idempotency_key="idempotency:p18-fp")
    object.__setattr__(divergent_fingerprint, "fingerprint", value.fingerprint)
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceRegistryConflictError):
        persist_authorization_evidence(divergent_fingerprint, collection, session=Session())


def test_duplicate_key_race_reconciles_exact_and_rejects_divergence_or_unknown() -> None:
    value = evidence()
    exact = DuplicateRaceCollection(value.to_dict())
    assert persist_authorization_evidence(value, exact, session=Session()) == value
    divergent = evidence(representative_principal_id="principal-partner-p18")
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceRegistryConflictError):
        persist_authorization_evidence(divergent, DuplicateRaceCollection(value.to_dict()), session=Session())
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceRegistryRetryRequiredError):
        persist_authorization_evidence(value, DuplicateRaceCollection({}), session=Session())


def test_history_is_exactly_filtered_deterministic_bounded_and_immutable() -> None:
    collection = Collection()
    first = evidence(effective_offset=0)
    second = evidence(effective_offset=5, idempotency_key="idempotency:p18-2")
    persist_authorization_evidence(first, collection, session=Session())
    persist_authorization_evidence(second, collection, session=Session())
    values = list_authorization_evidence_for_context(
        **_history_kwargs(first), evidence_collection=collection, session=Session(), limit=2
    )
    assert values == (first, second)
    assert isinstance(values, tuple)
    history_query = next(
        call[2]
        for call in collection.calls
        if call[0] == "find" and call[2] is not None and "representative_role" in call[2]
    )
    assert list(history_query) == list(HISTORY_INDEX_FIELDS[: len(HISTORY_INDEX_FIELDS) - 4])
    assert all(call[1].__class__ is Session for call in collection.calls)
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError):
        list_authorization_evidence_for_context(
            **_history_kwargs(first), evidence_collection=collection, session=Session(), limit=1
        )


def test_empty_history_is_immutable_tuple_and_wrong_context_is_absent() -> None:
    collection = Collection()
    value = evidence()
    empty = list_authorization_evidence_for_context(
        **_history_kwargs(value), evidence_collection=collection, session=Session()
    )
    assert empty == ()
    assert isinstance(empty, tuple)
    with pytest.raises(LegalClientMatterRepresentationAuthorizationEvidenceRegistryNotFoundError):
        get_authorization_evidence(value.tenant_id, value.evidence_id, collection, session=Session())


def test_history_tenant_isolation_and_scope_corruption_fail_closed() -> None:
    collection = Collection()
    value = evidence()
    other = evidence(tenant_id="tenant-p18-b")
    persist_authorization_evidence(value, collection, session=Session())
    persist_authorization_evidence(other, collection, session=Session())
    assert list_authorization_evidence_for_context(
        **_history_kwargs(value), evidence_collection=collection, session=Session()
    ) == (value,)
    assert list_authorization_evidence_for_context(
        **{**_history_kwargs(value), "tenant_id": "tenant-p18-missing"},
        evidence_collection=collection,
        session=Session(),
    ) == ()


def test_no_currentness_consumption_p1_iam_court_finance_or_transport_authority() -> None:
    source = Path(
        "tools/eos/legal_operations/registry/legal_client_matter_representation_authorization_evidence_registry.py"
    ).read_text()
    imports = " ".join(
        ast.unparse(node).lower()
        for node in ast.walk(ast.parse(source))
        if isinstance(node, (ast.Import, ast.ImportFrom))
    )
    assert "currentness" not in imports
    assert "tenant_authorization" not in imports
    assert "principal_status" not in imports
    assert "tenant_membership" not in imports
    assert "legal_client_matter_representation_authority" not in imports
    assert "http" not in imports
    assert "node" not in imports
    assert "CURRENT_POINTER" not in source
    assert "consumption_state" not in source.lower()
    assert "LegalClientMatterRepresentationAuthority" not in source
    assert "pymongo" in source


# ARTIFACT: test_legal_client_matter_representation_authorization_evidence_registry.py
# VERSION: v1.0.0-L9C11-P18-CLIENT-REPRESENTATION-AUTHORIZATION-EVIDENCE-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct pure-registry certificate only
# TENANT POSTURE: synthetic exact tenant and appointment-lineage fixtures
# FAIL-CLOSED POSTURE: malformed, divergent, cross-tenant and transactionless access rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
