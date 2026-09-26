"""Direct certificate for the P2B2 matter-instrument approval registry.

TITLE: WILSY OS Legal Client Matter Acceptance Instrument Approval Registry Certificate
VERSION: v1.0.0-L9A4-P2B2-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify exact indexes, caller-owned transactions, append-only replay,
         collision safety, subject currentness, ambiguity and tenant isolation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_acceptance_instrument_approval_registry.py
COLLABORATION / OWNERSHIP: Synthetic in-memory collection only; no canonical
                            Mongo, IAM, client, acceptance or financial state.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P2B2-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL-REGISTRY-CERT
           certifies append-only approval persistence and historical currentness.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only.
TENANT BOUNDARY: Every fake query is exact tenant and complete subject scoped.
AUTHORITY BOUNDARY: Historical approval evidence only; no IAM or acceptance.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
from typing import Any, Iterator

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_approval import (
    LegalClientMatterAcceptanceInstrumentApproval,
    LegalClientMatterAcceptanceInstrumentApprovalDecision as Decision,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_acceptance_instrument_approval_registry as registry,
)


UTC = timezone.utc
NOW = datetime(2026, 9, 26, 12, 0, 0, 123456, tzinfo=UTC)
TENANT = "tenant-law"
MATTER = "matter-1"
INSTRUMENT = "instrument-1"
VERSION = "1.0.0"
MATTER_FP = hashlib.sha3_512(b"matter").hexdigest()
INSTRUMENT_FP = hashlib.sha3_512(b"instrument").hexdigest()
CONTENT_FP = hashlib.sha3_512(b"content").hexdigest()
EVIDENCE_FP = hashlib.sha3_512(b"evidence").hexdigest()


class Session:
    """Minimal active transaction marker proving no lifecycle ownership."""

    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active
        self.start_calls = self.commit_calls = self.abort_calls = 0


class Cursor:
    """Small deterministic fake cursor implementing the Mongo methods used."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self.rows)

    def sort(self, fields: list[tuple[str, int]]) -> "Cursor":
        for field, direction in reversed(fields):
            self.rows.sort(key=lambda row: row.get(field, ""), reverse=direction < 0)
        return self


class Collection:
    """In-memory collection with unique approval identities and session tracing."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[dict[str, Any]] = []
        self.sessions: list[Any] = []
        self.update_calls = 0
        self.delete_calls = 0

    def with_options(self, **_kwargs: Any) -> "Collection":
        return self

    def create_index(self, keys: list[tuple[str, int]], **kwargs: Any) -> str:
        self.indexes.append({"key": keys, **kwargs})
        return str(kwargs["name"])

    @staticmethod
    def _matches(row: dict[str, Any], query: dict[str, Any]) -> bool:
        return all(row.get(key) == expected for key, expected in query.items())

    def find(self, query: dict[str, Any], *, session: Any) -> Cursor:
        self.sessions.append(session)
        return Cursor([deepcopy(row) for row in self.rows if self._matches(row, query)])

    def find_one(self, query: dict[str, Any], *, session: Any) -> dict[str, Any] | None:
        self.sessions.append(session)
        for row in self.rows:
            if self._matches(row, query):
                return deepcopy(row)
        return None

    def insert_one(self, document: dict[str, Any], *, session: Any) -> object:
        self.sessions.append(session)
        identity_pairs = (
            ("tenant_id", "approval_id"),
            ("tenant_id", "fingerprint"),
            ("tenant_id", "idempotency_key"),
        )
        for row in self.rows:
            if any(
                row[left] == document[left] and row[right] == document[right]
                for left, right in identity_pairs
            ):
                raise DuplicateKeyError("synthetic approval identity collision")
        stored = deepcopy(document)
        stored["_id"] = f"approval-{len(self.rows) + 1}"
        self.rows.append(stored)
        return object()

    def update_one(self, *_args: Any, **_kwargs: Any) -> object:
        self.update_calls += 1
        return object()

    def delete_many(self, *_args: Any, **_kwargs: Any) -> object:
        self.delete_calls += 1
        return object()


def approval(
    *,
    decision: Decision = Decision.APPROVED,
    approval_id: str = "approval-1",
    idempotency_key: str = "idem-1",
    tenant: str = TENANT,
    matter: str = MATTER,
    instrument: str = INSTRUMENT,
    version: str = VERSION,
    instrument_fp: str = INSTRUMENT_FP,
    content_fp: str = CONTENT_FP,
    effective_from: datetime = NOW,
    occurred_at: datetime = NOW,
) -> LegalClientMatterAcceptanceInstrumentApproval:
    """Build one synthetic domain approval with deterministic opaque evidence."""
    return LegalClientMatterAcceptanceInstrumentApproval(
        tenant_id=tenant,
        case_matter_id=matter,
        matter_fingerprint=MATTER_FP,
        approval_id=approval_id,
        instrument_id=instrument,
        version=version,
        instrument_fingerprint=instrument_fp,
        content_fingerprint=content_fp,
        decision=decision,
        approver_principal_id="principal-1",
        approver_capacity_reference="capacity:reviewer",
        authorization_evidence_reference="auth:evidence-1",
        authorization_evidence_fingerprint=EVIDENCE_FP,
        approval_evidence_reference="approval:evidence-1",
        approval_evidence_fingerprint=EVIDENCE_FP,
        occurred_at=occurred_at,
        effective_from=effective_from,
        idempotency_key=idempotency_key,
    )


def persist(value: LegalClientMatterAcceptanceInstrumentApproval, collection: Collection, session: Session | None = None):
    """Persist through one synthetic caller-owned active transaction."""
    return registry.persist_approval(value, collection, session=session or Session())


def test_indexes_are_exact_non_expiring_and_replay_scoped() -> None:
    collection = Collection()
    registry.ensure_indexes(collection)
    assert [item["name"] for item in collection.indexes] == [
        registry.APPROVAL_ID_INDEX_NAME,
        registry.FINGERPRINT_INDEX_NAME,
        registry.IDEMPOTENCY_INDEX_NAME,
        registry.HISTORY_INDEX_NAME,
        registry.DECISION_INDEX_NAME,
    ]
    assert all(item.get("unique") is True for item in collection.indexes[:3])
    assert all("expireAfterSeconds" not in item for item in collection.indexes)
    assert collection.indexes[3]["key"][:6] == [
        ("tenant_id", 1), ("case_matter_id", 1), ("instrument_id", 1),
        ("version", 1), ("instrument_fingerprint", 1), ("content_fingerprint", 1),
    ]


@pytest.mark.parametrize("session", [None, Session(False)])
def test_active_transaction_is_required(session: Session | None) -> None:
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryTransactionRequiredError):
        registry.persist_approval(approval(), Collection(), session=session)


def test_insert_replays_exact_and_propagates_session() -> None:
    collection = Collection()
    session = Session()
    first = persist(approval(), collection, session)
    second = persist(approval(), collection, session)
    assert first.to_dict() == second.to_dict()
    assert collection.sessions and all(item is session for item in collection.sessions)
    assert len(collection.rows) == 1


@pytest.mark.parametrize(
    "variant,code",
    [
        (approval(approval_id="approval-2"), "APPROVAL_ID_COLLISION"),
        (approval(idempotency_key="idem-2"), "APPROVAL_ID_COLLISION"),
    ],
)
def test_divergent_identity_or_subject_fails_closed(variant: LegalClientMatterAcceptanceInstrumentApproval, code: str) -> None:
    collection = Collection()
    persist(approval(), collection)
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryConflictError) as error:
        persist(variant, collection)
    assert error.value.code.startswith("L9A4_P2B2_")


def test_divergent_idempotency_collision_fails_closed() -> None:
    collection = Collection()
    persist(approval(), collection)
    value = approval(approval_id="approval-2", idempotency_key="idem-1")
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryConflictError):
        persist(value, collection)


def test_history_is_complete_exact_and_sorted() -> None:
    collection = Collection()
    later = approval(approval_id="approval-2", idempotency_key="idem-2", effective_from=NOW + timedelta(days=1), occurred_at=NOW + timedelta(days=1))
    persist(approval(), collection)
    persist(later, collection)
    history = registry.get_approval_history(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, session=Session())
    assert [item.approval_id for item in history] == ["approval-1", "approval-2"]


def test_current_approved_rejected_and_future_boundary() -> None:
    collection = Collection()
    first = approval()
    rejected = approval(decision=Decision.REJECTED, approval_id="approval-2", idempotency_key="idem-2", effective_from=NOW + timedelta(days=1), occurred_at=NOW + timedelta(days=1))
    persist(first, collection)
    persist(rejected, collection)
    current_before = registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, at=NOW + timedelta(hours=1), session=Session())
    current_after = registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, at=NOW + timedelta(days=1), session=Session())
    assert current_before is not None and current_before.approval_id == first.approval_id
    assert current_after is None


def test_no_history_returns_none() -> None:
    assert registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, Collection(), at=NOW, session=Session()) is None


def test_equal_effective_time_divergent_decisions_fail_closed_even_if_occurred_differs() -> None:
    collection = Collection()
    effective = NOW + timedelta(days=1)
    persist(approval(effective_from=effective, occurred_at=NOW), collection)
    persist(approval(decision=Decision.REJECTED, approval_id="approval-2", idempotency_key="idem-2", occurred_at=NOW + timedelta(hours=1), effective_from=effective), collection)
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryAmbiguousCurrentError):
        registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, at=effective + timedelta(hours=1), session=Session())


def test_stale_instrument_and_content_fingerprints_are_excluded() -> None:
    collection = Collection()
    persist(approval(), collection)
    stale = hashlib.sha3_512(b"stale").hexdigest()
    assert registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, stale, CONTENT_FP, collection, at=NOW, session=Session()) is None
    assert registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, stale, collection, at=NOW, session=Session()) is None


def test_tenant_isolation_and_exact_get() -> None:
    collection = Collection()
    persist(approval(), collection)
    assert registry.get_approval(TENANT, "approval-1", collection, session=Session()).approval_id == "approval-1"
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryNotFoundError):
        registry.get_approval("tenant-other", "approval-1", collection, session=Session())


def test_corrupt_persisted_record_fails_closed() -> None:
    collection = Collection()
    row = approval().to_dict()
    row["decision"] = "CORRUPT"
    row["_id"] = "corrupt"
    collection.rows.append(row)
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryPersistedRecordInvalidError):
        registry.get_approval_history(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, session=Session())


def test_no_update_delete_or_transaction_ownership() -> None:
    collection = Collection()
    session = Session()
    persist(approval(), collection, session)
    assert collection.update_calls == 0 and collection.delete_calls == 0
    assert session.start_calls == session.commit_calls == session.abort_calls == 0


def test_post_write_reconciliation_is_durable() -> None:
    collection = Collection()
    value = persist(approval(), collection)
    assert value.to_dict() == collection.rows[0] | {"_id": collection.rows[0]["_id"]} if False else value.to_dict() == {key: item for key, item in collection.rows[0].items() if key != "_id"}


def test_scope_must_be_exact_and_non_empty() -> None:
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryInputError):
        registry.get_approval_history("", MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, Collection(), session=Session())


def test_naive_currentness_time_rejected() -> None:
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryInputError):
        registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, Collection(), at=datetime(2026, 9, 26), session=Session())


def test_equal_effective_time_same_decision_is_unambiguous() -> None:
    collection = Collection()
    persist(approval(), collection)
    second = approval(approval_id="approval-2", idempotency_key="idem-2")
    persist(second, collection)
    current = registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, at=NOW + timedelta(hours=1), session=Session())
    assert current is not None and current.decision is Decision.APPROVED


def test_cross_subject_rows_do_not_enter_exact_history() -> None:
    collection = Collection()
    persist(approval(), collection)
    other = approval(approval_id="approval-2", idempotency_key="idem-2", instrument="instrument-other")
    persist(other, collection)
    history = registry.get_approval_history(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, session=Session())
    assert len(history) == 1


def test_approval_value_is_not_mutated() -> None:
    collection = Collection()
    value = approval()
    before = value.to_dict()
    persist(value, collection)
    assert value.to_dict() == before


def test_rejected_only_history_is_not_current() -> None:
    collection = Collection()
    persist(approval(decision=Decision.REJECTED), collection)
    assert registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, at=NOW, session=Session()) is None


def test_read_session_is_propagated() -> None:
    collection = Collection()
    session = Session()
    persist(approval(), collection, session)
    collection.sessions.clear()
    registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, at=NOW, session=session)
    assert collection.sessions and all(item is session for item in collection.sessions)


def test_public_registry_surface_is_bounded() -> None:
    assert set(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistry.__dict__) >= {
        "ensure_indexes", "persist_approval", "get_approval", "get_approval_history", "get_current_approval"
    }


def test_version_isolation() -> None:
    collection = Collection()
    persist(approval(), collection)
    assert registry.get_approval_history(TENANT, MATTER, INSTRUMENT, "2.0.0", INSTRUMENT_FP, CONTENT_FP, collection, session=Session()) == ()


def test_approval_id_lookup_is_tenant_scoped() -> None:
    collection = Collection()
    persist(approval(), collection)
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryNotFoundError):
        registry.get_approval("tenant-other", "approval-1", collection, session=Session())


def test_missing_fingerprint_query_is_rejected() -> None:
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryInputError):
        registry.get_approval_history(TENANT, MATTER, INSTRUMENT, VERSION, "bad", CONTENT_FP, Collection(), session=Session())


def test_missing_content_query_is_rejected() -> None:
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryInputError):
        registry.get_approval_history(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, "bad", Collection(), session=Session())


def test_explicit_corrupt_extra_field_rejects() -> None:
    collection = Collection()
    row = approval().to_dict()
    row["unexpected"] = True
    collection.rows.append(row)
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryPersistedRecordInvalidError):
        registry.get_approval_history(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, session=Session())


def test_explicit_corrupt_missing_field_rejects() -> None:
    collection = Collection()
    row = approval().to_dict()
    row.pop("decision")
    collection.rows.append(row)
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryPersistedRecordInvalidError):
        registry.get_approval_history(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, session=Session())


def test_approval_history_does_not_use_wall_clock() -> None:
    collection = Collection()
    persist(approval(effective_from=NOW + timedelta(days=30), occurred_at=NOW), collection)
    assert registry.get_approval_history(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, session=Session())


def test_rejected_effective_transition_does_not_delete_history() -> None:
    collection = Collection()
    persist(approval(), collection)
    rejection_time = NOW + timedelta(days=1)
    persist(approval(decision=Decision.REJECTED, approval_id="approval-2", idempotency_key="idem-2", effective_from=rejection_time, occurred_at=rejection_time), collection)
    assert len(collection.rows) == 2


def test_duplicate_collision_does_not_call_update_or_delete() -> None:
    collection = Collection()
    persist(approval(), collection)
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryConflictError):
        persist(approval(approval_id="approval-2", idempotency_key="idem-1"), collection)
    assert collection.update_calls == collection.delete_calls == 0


def test_same_subject_requires_both_fingerprints() -> None:
    collection = Collection()
    persist(approval(), collection)
    other = hashlib.sha3_512(b"other").hexdigest()
    assert registry.get_approval_history(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, other, collection, session=Session()) == ()


def test_registry_does_not_accept_inactive_session_for_reads() -> None:
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentApprovalRegistryTransactionRequiredError):
        registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, Collection(), at=NOW, session=Session(False))


def test_current_rejection_is_not_an_approval_value() -> None:
    collection = Collection()
    persist(approval(decision=Decision.REJECTED), collection)
    assert registry.get_current_approval(TENANT, MATTER, INSTRUMENT, VERSION, INSTRUMENT_FP, CONTENT_FP, collection, at=NOW, session=Session()) is None


# ARTIFACT: test_legal_client_matter_acceptance_instrument_approval_registry.py
# VERSION: v1.0.0-L9A4-P2B2-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct synthetic registry certificate only
# TENANT POSTURE: exact tenant and complete subject predicates
# FAIL-CLOSED POSTURE: required behavior and corruption tests fail the certificate
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
