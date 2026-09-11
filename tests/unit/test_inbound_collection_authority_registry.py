"""WILSY OS M11 R8-R4 authorization-provenance inbound collection authority registry certificate.
TITLE: Inbound Collection Authority Registry Certificate
VERSION: v1.1.0-M11-R8-R3B-P3-AUTHORIZATION-PROVENANCE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies tenant-scoped uniqueness, exact-one cardinality, strict hydration, replay, and race boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_inbound_collection_authority_registry.py
COLLABORATION / OWNERSHIP: SaaS persistence-registry certificate owner.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.1.0-M11-R8-R3B-P3-AUTHORIZATION-PROVENANCE certifies exact authorization-evidence fingerprint persistence, strict hydration, and divergent replay; v1.0.0-M11-R8-R3 certified the durable authority registry without host-database claims.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic records and tenant-scoped predicates only.
TENANT BOUNDARY: Every read, uniqueness assertion, and replay fixture includes tenant_id.
AUTHORITY BOUNDARY: Persistence/replay certificate only; no issuance or external transport authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive for outbound financial execution truth.
TRANSACTION BOUNDARY: Fake collection only; caller owns session and transaction lifecycle.
FAIL-CLOSED DECLARATION: Missing, mixed, corrupt, conflicting, divergent, and authorization-provenance-invalid durable material rejects.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import dataclasses
import hashlib
import inspect
from pathlib import Path
from typing import Any, cast

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.saas.domain.commercial_receivable import ReceivableFamily
from tools.eos.saas.domain.inbound_collection_authority import (
    ClientCollectionSource,
    InboundCollectionAuthority,
    InboundCollectionAuthorityError,
    PlatformCollectionSource,
)
from tools.eos.saas.billing.inbound_collection_authority_registry import (
    COLLECTION,
    InboundCollectionAuthorityPersistedRecordInvalidError,
    InboundCollectionAuthorityPersistenceCorruptionError,
    InboundCollectionAuthorityRegistry,
    InboundCollectionAuthorityRegistryError,
    InboundCollectionAuthorityReplayConflictError,
)


FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128
STAMP = datetime(2026, 9, 9, 8, 30, tzinfo=timezone.utc)


class ActiveSession:
    in_transaction = True


ACTIVE_SESSION = ActiveSession()


def client_authority(
    *, tenant_id: str = "tenant-a", authority_id: str = "authority-a", source_id: str = "receivable-a", key: str = "key-a", amount: int = 12500, currency: str = "ZAR", authorization_evidence_fingerprint: str = FP_C
) -> InboundCollectionAuthority:
    source = ClientCollectionSource(tenant_id, f"client-invoice-{source_id}", source_id, FP_A, FP_B, "customer-a")
    return InboundCollectionAuthority(authority_id, tenant_id, ReceivableFamily.CLIENT, source, amount, currency, key, "actor-a", "authorization-a", authorization_evidence_fingerprint, STAMP, STAMP)


def platform_authority(
    *, tenant_id: str = "tenant-a", authority_id: str = "authority-platform", source_id: str = "receivable-platform", key: str = "key-platform"
) -> InboundCollectionAuthority:
    source = PlatformCollectionSource(tenant_id, f"platform-invoice-{source_id}", source_id, FP_A, FP_B)
    return InboundCollectionAuthority(authority_id, tenant_id, ReceivableFamily.PLATFORM, source, 12500, "ZAR", key, "actor-a", "authorization-a", FP_C, STAMP, STAMP)


def _value_at(document: dict[str, Any], path: str) -> object:
    value: object = document
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


class FakeCursor:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def limit(self, amount: int) -> "FakeCursor":
        return FakeCursor(self.rows[:amount])

    def __iter__(self):
        return iter(self.rows)


class FakeCollection:
    """Small deterministic collection double; no mocking dependency or transaction ownership."""

    def __init__(self, documents: list[dict[str, Any]] | None = None) -> None:
        self.documents = documents or []
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, Any]]] = []
        self.operations: list[tuple[str, Any, Any]] = []
        self.duplicate_on_insert = False
        self.duplicate_document: dict[str, Any] | None = None

    def create_index(self, keys: list[tuple[str, int]], **options: Any) -> str:
        self.indexes.append((keys, options))
        return str(options.get("name", len(self.indexes)))

    def find(self, query: dict[str, object], *, session: object = None) -> FakeCursor:
        self.operations.append(("find", deepcopy(query), session))
        return FakeCursor([deepcopy(row) for row in self.documents if all(_value_at(row, key) == expected for key, expected in query.items())])

    def insert_one(self, document: dict[str, Any], *, session: object = None) -> object:
        self.operations.append(("insert_one", deepcopy(document), session))
        if self.duplicate_on_insert:
            if self.duplicate_document is not None:
                self.documents.append(deepcopy(self.duplicate_document))
            raise DuplicateKeyError("duplicate authority identity")
        self.documents.append(deepcopy(document))
        return object()


def test_collection_and_exact_three_tenant_scoped_unique_indexes() -> None:
    collection = FakeCollection()
    InboundCollectionAuthorityRegistry.ensure_indexes(collection)  # type: ignore[arg-type]
    assert COLLECTION == "inbound_collection_authorities"
    assert len(collection.indexes) == 3
    assert [keys for keys, _ in collection.indexes] == [
        [("tenant_id", 1), ("collection_authority_id", 1)],
        [("tenant_id", 1), ("source_authority_kind", 1), ("source_authority.commercial_receivable_id", 1)],
        [("tenant_id", 1), ("idempotency_key", 1)],
    ]
    assert all(options.get("unique") is True for _, options in collection.indexes)
    assert not any("amount" in key or "customer" in key or "provider" in key for keys, _ in collection.indexes for key, _ in keys)


def test_fresh_client_and_platform_create_and_exact_replays() -> None:
    collection = FakeCollection()
    client = client_authority()
    platform = platform_authority()
    assert InboundCollectionAuthorityRegistry.create(client, collection, session=ACTIVE_SESSION) == client  # type: ignore[arg-type]
    assert InboundCollectionAuthorityRegistry.create(platform, collection, session=ACTIVE_SESSION) == platform  # type: ignore[arg-type]
    assert len(collection.documents) == 2
    assert InboundCollectionAuthorityRegistry.create(client, collection, session=ACTIVE_SESSION) == client  # type: ignore[arg-type]
    assert InboundCollectionAuthorityRegistry.get_by_source_receivable("tenant-a", ReceivableFamily.CLIENT, "receivable-a", collection, session=ACTIVE_SESSION) == client  # type: ignore[arg-type]
    assert InboundCollectionAuthorityRegistry.get_by_idempotency_key("tenant-a", "key-a", collection, session=ACTIVE_SESSION) == client  # type: ignore[arg-type]
    assert collection.documents[0]["authorization_evidence_fingerprint"] == FP_C
    assert InboundCollectionAuthorityRegistry._hydrate(collection.documents[0]).authorization_evidence_fingerprint == FP_C  # type: ignore[arg-type]
    assert InboundCollectionAuthorityRegistry._hydrate(collection.documents[1]).authorization_evidence_fingerprint == FP_C  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "candidate",
    [
        client_authority(authority_id="authority-new"),
        client_authority(key="key-new"),
        client_authority(amount=12501),
        client_authority(currency="EUR"),
        client_authority(authorization_evidence_fingerprint="d" * 128),
        client_authority(authority_id="authority-new", source_id="receivable-new"),
    ],
)
def test_divergent_id_source_idempotency_amount_and_currency_reject(candidate: InboundCollectionAuthority) -> None:
    collection = FakeCollection()
    InboundCollectionAuthorityRegistry.create(client_authority(), collection, session=ACTIVE_SESSION)  # type: ignore[arg-type]
    with pytest.raises(InboundCollectionAuthorityReplayConflictError):
        InboundCollectionAuthorityRegistry.create(candidate, collection, session=ACTIVE_SESSION)  # type: ignore[arg-type]


def test_same_id_source_and_idempotency_with_changed_authorization_evidence_rejects() -> None:
    collection = FakeCollection()
    original = client_authority()
    InboundCollectionAuthorityRegistry.create(original, collection, session=ACTIVE_SESSION)  # type: ignore[arg-type]
    divergent = client_authority(authorization_evidence_fingerprint="d" * 128)
    with pytest.raises(InboundCollectionAuthorityReplayConflictError):
        InboundCollectionAuthorityRegistry.create(divergent, collection, session=ACTIVE_SESSION)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "candidate",
    [
        client_authority(authority_id="authority-new", authorization_evidence_fingerprint="d" * 128),
        client_authority(source_id="receivable-new", key="key-a", authorization_evidence_fingerprint="d" * 128),
    ],
)
def test_source_or_idempotency_replay_with_changed_authorization_evidence_rejects(candidate: InboundCollectionAuthority) -> None:
    collection = FakeCollection()
    InboundCollectionAuthorityRegistry.create(client_authority(), collection, session=ACTIVE_SESSION)  # type: ignore[arg-type]
    with pytest.raises(InboundCollectionAuthorityReplayConflictError):
        InboundCollectionAuthorityRegistry.create(candidate, collection, session=ACTIVE_SESSION)  # type: ignore[arg-type]


def test_same_idempotency_different_source_and_id_reject() -> None:
    collection = FakeCollection()
    InboundCollectionAuthorityRegistry.create(client_authority(), collection, session=ACTIVE_SESSION)  # type: ignore[arg-type]
    candidate = client_authority(authority_id="authority-new", source_id="receivable-new", key="key-a")
    with pytest.raises(InboundCollectionAuthorityReplayConflictError):
        InboundCollectionAuthorityRegistry.create(candidate, collection, session=ACTIVE_SESSION)  # type: ignore[arg-type]


def test_disagreeing_id_source_and_idempotency_facts_fail_closed() -> None:
    candidate = client_authority()
    row_for_id = client_authority(authority_id="authority-a", source_id="receivable-id", key="key-id")
    row_for_source = client_authority(authority_id="authority-source", source_id="receivable-a", key="key-source")
    row_for_key = client_authority(authority_id="authority-key", source_id="receivable-key", key="key-a")
    collection = FakeCollection([row_for_id.to_dict(), row_for_source.to_dict(), row_for_key.to_dict()])
    with pytest.raises(InboundCollectionAuthorityPersistenceCorruptionError):
        InboundCollectionAuthorityRegistry.create(candidate, collection, session=ACTIVE_SESSION)  # type: ignore[arg-type]


def test_tenant_scoped_getters_isolate_identical_textual_values() -> None:
    first = client_authority(tenant_id="tenant-a")
    second_source = ClientCollectionSource("tenant-b", "client-invoice", "receivable", FP_A, FP_B, "customer")
    second = InboundCollectionAuthority("authority-b", "tenant-b", ReceivableFamily.CLIENT, second_source, 12500, "ZAR", "same-key", "actor", "auth", FP_C, STAMP, STAMP)
    collection = FakeCollection([first.to_dict(), second.to_dict()])
    assert InboundCollectionAuthorityRegistry.get("tenant-a", "authority-a", collection, session=ACTIVE_SESSION) == first  # type: ignore[arg-type]
    assert InboundCollectionAuthorityRegistry.get("tenant-b", "authority-a", collection, session=ACTIVE_SESSION) is None  # type: ignore[arg-type]
    assert InboundCollectionAuthorityRegistry.get_by_source_receivable("tenant-b", ReceivableFamily.CLIENT, "receivable", collection, session=ACTIVE_SESSION) == second  # type: ignore[arg-type]
    assert InboundCollectionAuthorityRegistry.get_by_idempotency_key("tenant-a", "same-key", collection, session=ACTIVE_SESSION) is None  # type: ignore[arg-type]
    assert InboundCollectionAuthorityRegistry.get_by_idempotency_key("tenant-b", "same-key", collection, session=ACTIVE_SESSION) == second  # type: ignore[arg-type]


def test_getters_require_tenant_and_closed_family_and_have_no_tenantless_api() -> None:
    collection = FakeCollection()
    for call in (
        lambda: InboundCollectionAuthorityRegistry.get("", "authority", collection, session=ACTIVE_SESSION),  # type: ignore[arg-type]
        lambda: InboundCollectionAuthorityRegistry.get_by_source_receivable("tenant-a", "CLIENT", "receivable", collection, session=ACTIVE_SESSION),  # type: ignore[arg-type]
        lambda: InboundCollectionAuthorityRegistry.get_by_idempotency_key("tenant-a", " ", collection, session=ACTIVE_SESSION),  # type: ignore[arg-type]
    ):
        with pytest.raises(InboundCollectionAuthorityRegistryError):
            call()
    for name in ("get", "get_by_source_receivable", "get_by_idempotency_key"):
        assert "tenant_id" in inspect.signature(getattr(InboundCollectionAuthorityRegistry, name)).parameters


@pytest.mark.parametrize("mutator", [
    lambda payload: payload.pop("tenant_id"),
    lambda payload: payload.update({"unknown": True}),
    lambda payload: payload.update({"source_authority_kind": "UNKNOWN"}),
    lambda payload: payload["source_authority"].update({"platform_invoice_id": "mixed"}),
    lambda payload: payload["source_authority"].pop("client_invoice_fingerprint"),
    lambda payload: payload.update({"expected_amount_minor": 0}),
    lambda payload: payload.update({"currency": "bad"}),
    lambda payload: payload.update({"created_at": datetime(2026, 9, 9).isoformat()}),
    lambda payload: payload.update({"fingerprint": "c" * 128}),
])
def test_strict_hydration_rejects_corruption(mutator) -> None:
    payload = deepcopy(client_authority().to_dict())
    mutator(payload)
    with pytest.raises(InboundCollectionAuthorityPersistedRecordInvalidError):
        InboundCollectionAuthorityRegistry._hydrate(payload)  # type: ignore[arg-type]


@pytest.mark.parametrize("mutator", [
    lambda payload: payload.pop("authorization_evidence_fingerprint"),
    lambda payload: payload.update({"authorization_evidence_fingerprint": "A" * 128}),
    lambda payload: payload.update({"authorization_evidence_fingerprint": "bad"}),
])
def test_authorization_evidence_fingerprint_hydration_is_required_and_strict(mutator) -> None:
    payload = deepcopy(client_authority().to_dict())
    mutator(payload)
    with pytest.raises(InboundCollectionAuthorityPersistedRecordInvalidError):
        InboundCollectionAuthorityRegistry._hydrate(payload)  # type: ignore[arg-type]


def test_stored_authorization_evidence_change_breaks_authority_fingerprint() -> None:
    payload = deepcopy(client_authority().to_dict())
    payload["authorization_evidence_fingerprint"] = "d" * 128
    with pytest.raises(InboundCollectionAuthorityPersistedRecordInvalidError):
        InboundCollectionAuthorityRegistry._hydrate(payload)  # type: ignore[arg-type]


def test_registry_never_derives_or_defaults_authorization_evidence_fingerprint() -> None:
    payload = deepcopy(client_authority().to_dict())
    payload.pop("authorization_evidence_fingerprint")
    with pytest.raises(InboundCollectionAuthorityPersistedRecordInvalidError):
        InboundCollectionAuthorityRegistry._hydrate(payload)  # type: ignore[arg-type]


def test_strict_client_and_platform_round_trip_and_duplicate_rows_fail_closed() -> None:
    client, platform = client_authority(), platform_authority()
    assert InboundCollectionAuthorityRegistry._hydrate(client.to_dict()) == client  # type: ignore[arg-type]
    assert InboundCollectionAuthorityRegistry._hydrate(platform.to_dict()) == platform  # type: ignore[arg-type]
    collection = FakeCollection([client.to_dict(), client.to_dict()])
    with pytest.raises(InboundCollectionAuthorityPersistenceCorruptionError):
        InboundCollectionAuthorityRegistry.get("tenant-a", "authority-a", collection, session=ACTIVE_SESSION)  # type: ignore[arg-type]


def test_session_is_forwarded_and_registry_does_not_own_transaction_lifecycle() -> None:
    class Session:
        in_transaction = True

        def start_transaction(self):
            raise AssertionError("registry must not start transactions")

        def commit_transaction(self):
            raise AssertionError("registry must not commit transactions")

        def abort_transaction(self):
            raise AssertionError("registry must not abort transactions")

    session = Session()
    collection = FakeCollection()
    value = client_authority()
    InboundCollectionAuthorityRegistry.create(value, collection, session=session)  # type: ignore[arg-type]
    assert all(operation[2] is session for operation in collection.operations)


def test_preinsert_canonical_existing_precedence_precedes_insert() -> None:
    collection = FakeCollection()
    InboundCollectionAuthorityRegistry.create(client_authority(), collection, session=ACTIVE_SESSION)  # type: ignore[arg-type]
    collection.operations.clear()
    InboundCollectionAuthorityRegistry.create(client_authority(), collection, session=ACTIVE_SESSION)  # type: ignore[arg-type]
    assert [operation[0] for operation in collection.operations] == ["find", "find", "find"]


def test_duplicate_key_propagates_without_post_abort_lookup() -> None:
    value = client_authority()
    collection = FakeCollection()
    collection.duplicate_on_insert = True
    with pytest.raises(DuplicateKeyError):
        InboundCollectionAuthorityRegistry.create(value, collection, session=ACTIVE_SESSION)  # type: ignore[arg-type]
    assert [operation[0] for operation in collection.operations] == ["find", "find", "find", "insert_one"]


def test_whole_transaction_retry_resolves_identical_winner_and_rejects_divergent_winner() -> None:
    value = client_authority()
    collection = FakeCollection()
    collection.duplicate_on_insert = True
    collection.duplicate_document = value.to_dict()
    with pytest.raises(DuplicateKeyError):
        InboundCollectionAuthorityRegistry.create(value, collection, session=ACTIVE_SESSION)  # type: ignore[arg-type]
    collection.duplicate_on_insert = False
    assert InboundCollectionAuthorityRegistry.create(value, collection, session=ACTIVE_SESSION) == value  # type: ignore[arg-type]

    divergent = client_authority(amount=12501)
    with pytest.raises(InboundCollectionAuthorityReplayConflictError):
        InboundCollectionAuthorityRegistry.create(divergent, collection, session=ACTIVE_SESSION)  # type: ignore[arg-type]


def test_registry_does_not_generate_or_mutate_authority_fields() -> None:
    value = client_authority()
    before = value.to_dict()
    collection = FakeCollection()
    result = InboundCollectionAuthorityRegistry.create(value, collection, session=ACTIVE_SESSION)  # type: ignore[arg-type]
    assert result is value
    assert value.to_dict() == before
    assert collection.documents[0] == before
    assert "fingerprint" in collection.documents[0]
    assert set(collection.documents[0]) == set(before)


def test_registry_source_has_no_external_or_outbound_dependencies_and_domain_hash_is_frozen() -> None:
    registry_path = Path(__file__).parents[2] / "tools/eos/saas/billing/inbound_collection_authority_registry.py"
    registry_source = registry_path.read_text(encoding="utf-8").lower()
    for forbidden in (
        "payfast", "payshap", "m_payment_id", "pf_payment_id", "merchant_id",
        "financialexecutioncommand", "financialexecutionattempt", "vendorbill", "paymentdestination",
        "from tools.eos.kennel", "import tools.eos.kennel", "import requests", "import http",
    ):
        assert forbidden not in registry_source
    domain_path = Path(__file__).parents[2] / "tools/eos/saas/domain/inbound_collection_authority.py"
    domain_bytes = domain_path.read_bytes()
    assert len(domain_bytes) == 15337
    assert hashlib.sha3_512(domain_bytes).hexdigest() == "893ec6b47466beecc3c1bfeae5ebac827f0fb5dbd2813d00d688fa21e8ae52a58115c7c2fa80532482ce34e2d9d5886c2d21bdf3dd7a514d62b57590ef27a421"


def test_registry_persists_no_lifecycle_or_external_identity_fields() -> None:
    document = client_authority().to_dict()
    forbidden = {"status", "paid", "settled", "settlement", "provider", "merchant_id", "m_payment_id", "pf_payment_id"}
    assert not forbidden.intersection(document)
    assert not forbidden.intersection(cast(dict[str, object], document["source_authority"]))
    assert not dataclasses.is_dataclass(InboundCollectionAuthorityRegistry)


# ARTIFACT: test_inbound_collection_authority_registry.py
# VERSION: v1.1.0-M11-R8-R3B-P3-AUTHORIZATION-PROVENANCE
# AUTHORITY BOUNDARY: Durable authority persistence and replay certificate only.
# TENANT POSTURE: Explicit tenant-scoped fake records and predicates.
# FAIL-CLOSED POSTURE: Corruption, authorization-provenance disagreement, and duplicate races reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
