"""WILSY OS direct certificate for credential-security persistence/currentness.

TITLE: Tenant Inbound Provider Credential Security Authority Registry Tests
VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P3-R2
AUTHORITY: Wilsy OS Core Governance
EPITOME: Bounded two-collection proof for immutable facts and explicit current slots.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_inbound_provider_credential_security_authority_registry.py
COLLABORATION / OWNERSHIP: Direct P3 registry certificate; P2 domain and P4 issuance remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3D-P3-R2 certifies race-safe stream identity,
           fact persistence, replay, pointer provenance, and CAS.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque references only; no secret, network, database, or KMS activity.
TENANT BOUNDARY: Every fixture and lookup is explicitly tenant scoped.
AUTHORITY BOUNDARY: Persistence/currentness only; no issuance, binding, checkout, or financial mutation.
FAIL-CLOSED DECLARATION: Corrupt records, divergent replay, and stale CAS expectations reject.
"""

from __future__ import annotations

TITLE = "Tenant Inbound Provider Credential Security Authority Registry Tests"
VERSION = "v1.0.0-M11-R8-R3B-P8-P3D-P3-R2"
AUTHORITY = "Wilsy OS Core Governance"
EPITOME = "Bounded two-collection registry proof for immutable facts and explicit current slots."
ABSOLUTE_CANONICAL_PATH = "/Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_inbound_provider_credential_security_authority_registry.py"
CHANGELOG = "v1.0.0-M11-R8-R3B-P8-P3D-P3-R2 certifies race-safe stream identity, fact persistence, replay, pointer provenance, and CAS."

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import inspect
from typing import Any, cast

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.saas.domain.tenant_inbound_provider_credential_security_authority import (
    TenantInboundProviderCredentialSecurityAuthority,
    TenantInboundProviderCredentialSecurityState,
)
from tools.eos.saas.billing import tenant_inbound_provider_credential_security_authority_registry as registry
from tools.eos.saas.billing.tenant_inbound_provider_credential_security_authority_registry import (
    CURRENT_POINTER_COLLECTION,
    CURRENT_POINTER_INDEX_NAME,
    FACT_COLLECTION,
    FACT_IDENTITY_INDEX_NAME,
    FIRST_SECURITY_REVISION,
    IDEMPOTENCY_INDEX_NAME,
    IDEMPOTENCY_KEY_FIELD,
    REVISION_INDEX_NAME,
    SECURITY_FACT_ID_FIELD,
    TenantInboundProviderCredentialSecurityAuthorityRegistryCASConflictError,
    TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError,
    TenantInboundProviderCredentialSecurityAuthorityRegistryPersistenceCorruptionError,
    TenantInboundProviderCredentialSecurityAuthorityRegistryReplayConflictError,
    TenantInboundProviderCredentialSecurityAuthorityRegistryTransactionError,
    TenantInboundProviderCredentialSecurityCurrent,
    ensure_indexes,
    get_current_fact,
    get_current_pointer,
    get_fact,
    get_fact_by_idempotency_key,
    persist_fact_and_advance_current,
    security_fact_id,
)


NOW = datetime(2026, 9, 10, 10, 0, tzinfo=timezone.utc)
END = NOW + timedelta(hours=1)
CONFIGURATION_FINGERPRINT = "a" * 128
AUTHORIZATION_FINGERPRINT = "b" * 128


class Session:
    in_transaction = True


class Result:
    def __init__(self, matched_count: int) -> None:
        self.matched_count = matched_count


class FakeCollection:
    """Small deterministic collection double recording sessions and indexes."""

    def __init__(self) -> None:
        self.docs: list[dict[str, object]] = []
        self.indexes: list[dict[str, object]] = []
        self.last_sessions: list[object] = []
        self.last_queries: list[dict[str, object]] = []
        self.insert_calls = 0
        self.update_calls = 0
        self.force_update_miss = False

    @staticmethod
    def _same(document: dict[str, object], query: dict[str, object]) -> bool:
        return all(document.get(key) == value for key, value in query.items())

    def create_index(
        self,
        fields: list[tuple[str, int]],
        *,
        unique: bool = False,
        name: str = "",
        **_: object,
    ) -> str:
        self.indexes.append({"fields": fields, "unique": unique, "name": name})
        return name

    def find_one(self, query: dict[str, object], **kwargs: object) -> dict[str, object] | None:
        self.last_queries.append(dict(query))
        self.last_sessions.append(kwargs.get("session"))
        for document in self.docs:
            if self._same(document, query):
                return dict(document)
        return None

    def find(self, query: dict[str, object], **kwargs: object) -> list[dict[str, object]]:
        self.last_queries.append(dict(query))
        self.last_sessions.append(kwargs.get("session"))
        return [dict(document) for document in self.docs if self._same(document, query)]

    def insert_one(self, document: dict[str, object], **kwargs: object) -> object:
        self.insert_calls += 1
        self.last_sessions.append(kwargs.get("session"))
        for index in self.indexes:
            if not bool(index["unique"]):
                continue
            fields = cast(list[tuple[str, int]], index["fields"])
            if any(
                all(old.get(field) == document.get(field) for field, _ in fields)
                for old in self.docs
            ):
                raise DuplicateKeyError("duplicate key")
        self.docs.append(dict(document))
        return object()

    def update_one(
        self,
        query: dict[str, object],
        update: dict[str, object],
        **kwargs: object,
    ) -> Result:
        self.update_calls += 1
        self.last_sessions.append(kwargs.get("session"))
        if self.force_update_miss:
            return Result(0)
        for index, document in enumerate(self.docs):
            if self._same(document, query):
                replacement = dict(document)
                replacement.update(cast(dict[str, object], update.get("$set", {})))
                self.docs[index] = replacement
                return Result(1)
        return Result(0)


def _fact(**changes: object) -> TenantInboundProviderCredentialSecurityAuthority:
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "provider_id": "provider-a",
        "merchant_configuration_id": "merchant-config-a",
        "merchant_configuration_version": 1,
        "merchant_configuration_fingerprint": CONFIGURATION_FINGERPRINT,
        "credential_reference": "secret-ref://tenant-a/config-a/v1",
        "credential_version": "v1",
        "security_state": TenantInboundProviderCredentialSecurityState.ELIGIBLE,
        "security_revision": 0,
        "valid_from": NOW,
        "valid_until": END,
        "evaluated_at": NOW,
        "authorization_decision_id": "credential-security-auth-a",
        "authorization_evidence_fingerprint": AUTHORIZATION_FINGERPRINT,
    }
    values.update(changes)
    return TenantInboundProviderCredentialSecurityAuthority(
        **cast(dict[str, Any], values)
    )


def _collections() -> tuple[FakeCollection, FakeCollection]:
    facts, pointers = FakeCollection(), FakeCollection()
    ensure_indexes(facts, pointers)
    return facts, pointers


def _seed() -> tuple[FakeCollection, FakeCollection, TenantInboundProviderCredentialSecurityAuthority]:
    facts, pointers = _collections()
    value = _fact()
    persist_fact_and_advance_current(
        value,
        "credential-idem-a",
        None,
        None,
        None,
        fact_collection=facts,
        pointer_collection=pointers,
        session=Session(),
    )
    return facts, pointers, value


@pytest.mark.parametrize(
    ("name", "fields"),
    [
        (FACT_IDENTITY_INDEX_NAME, [("tenant_id", 1), (SECURITY_FACT_ID_FIELD, 1)]),
        (
            IDEMPOTENCY_INDEX_NAME,
            [("tenant_id", 1), ("provider_id", 1), ("merchant_configuration_id", 1), ("merchant_configuration_version", 1), (IDEMPOTENCY_KEY_FIELD, 1)],
        ),
        (
            REVISION_INDEX_NAME,
            [("tenant_id", 1), ("provider_id", 1), ("merchant_configuration_id", 1), ("merchant_configuration_version", 1), ("security_revision", 1)],
        ),
        (
            CURRENT_POINTER_INDEX_NAME,
            [("tenant_id", 1), ("provider_id", 1), ("merchant_configuration_id", 1), ("merchant_configuration_version", 1)],
        ),
    ],
)
def test_indexes_are_exact_and_unique(name: str, fields: list[tuple[str, int]]) -> None:
    facts, pointers = _collections()
    rows = facts.indexes + pointers.indexes
    row = next(row for row in rows if row["name"] == name)
    assert row["fields"] == fields
    assert row["unique"] is True


def test_collection_topology_is_two_explicit_collections() -> None:
    assert FACT_COLLECTION != CURRENT_POINTER_COLLECTION
    facts, pointers = _collections()
    assert len(facts.indexes) == 3
    assert len(pointers.indexes) == 1
    assert all("$" not in str(index) for index in facts.indexes + pointers.indexes)


@pytest.mark.parametrize("state", list(TenantInboundProviderCredentialSecurityState))
def test_each_security_state_can_be_current(state: TenantInboundProviderCredentialSecurityState) -> None:
    facts, pointers = _collections()
    value = _fact(security_state=state)
    persist_fact_and_advance_current(value, f"idem-{state.value}", None, None, None, fact_collection=facts, pointer_collection=pointers, session=Session())
    current = get_current_fact("tenant-a", "provider-a", "merchant-config-a", 1, CONFIGURATION_FINGERPRINT, fact_collection=facts, pointer_collection=pointers, session=Session())
    assert current == value


def test_fresh_revision_zero_fact_and_pointer_persist() -> None:
    facts, pointers, value = _seed()
    assert len(facts.docs) == 1
    assert len(pointers.docs) == 1
    assert facts.docs[0]["security_revision"] == FIRST_SECURITY_REVISION
    assert facts.docs[0][SECURITY_FACT_ID_FIELD] == security_fact_id(value)
    assert facts.docs[0][IDEMPOTENCY_KEY_FIELD] == "credential-idem-a"


def test_fact_and_pointer_use_same_caller_session() -> None:
    facts, pointers, _ = _seed()
    assert facts.last_sessions[-1] is pointers.last_sessions[-1]
    assert facts.last_sessions[-1] is not None


def test_fact_lookup_is_tenant_scoped_and_strictly_hydrated() -> None:
    facts, _, value = _seed()
    assert get_fact("tenant-a", security_fact_id(value), facts, session=Session()) == value
    assert get_fact("tenant-b", security_fact_id(value), facts, session=Session()) is None
    facts.docs[0]["unknown"] = True
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError):
        get_fact("tenant-a", security_fact_id(value), facts, session=Session())


def test_idempotency_lookup_is_tenant_scoped() -> None:
    facts, _, value = _seed()
    assert get_fact_by_idempotency_key("tenant-a", "provider-a", "merchant-config-a", 1, "credential-idem-a", facts, session=Session()) == value
    assert get_fact_by_idempotency_key("tenant-b", "provider-a", "merchant-config-a", 1, "credential-idem-a", facts, session=Session()) is None


def test_exact_replay_returns_original_without_writes_or_pointer_advance() -> None:
    facts, pointers, value = _seed()
    inserts, updates = facts.insert_calls, pointers.update_calls
    replay = persist_fact_and_advance_current(value, "credential-idem-a", None, None, None, fact_collection=facts, pointer_collection=pointers, session=Session())
    assert replay == value
    assert facts.insert_calls == inserts
    assert pointers.update_calls == updates


def test_same_fingerprint_duplicate_initial_insert_fails_closed() -> None:
    facts, pointers, value = _seed()
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityRegistryReplayConflictError):
        persist_fact_and_advance_current(
            value,
            "credential-idem-new",
            None,
            None,
            None,
            fact_collection=facts,
            pointer_collection=pointers,
            session=Session(),
        )
    assert len(facts.docs) == 1 and len(pointers.docs) == 1


def test_divergent_same_key_fails_closed_before_write() -> None:
    facts, pointers, _ = _seed()
    divergent = _fact(security_state=TenantInboundProviderCredentialSecurityState.COMPROMISED, security_revision=1)
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityRegistryReplayConflictError):
        persist_fact_and_advance_current(divergent, "credential-idem-a", None, None, None, fact_collection=facts, pointer_collection=pointers, session=Session())
    assert len(facts.docs) == 1 and len(pointers.docs) == 1


def test_same_configuration_version_different_fingerprint_fails_closed() -> None:
    facts, pointers, _ = _seed()
    divergent = _fact(
        merchant_configuration_fingerprint="c" * 128,
        credential_reference="secret-ref://tenant-a/config-a/v2",
        credential_version="v2",
        security_state=TenantInboundProviderCredentialSecurityState.COMPROMISED,
        security_revision=1,
    )
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityRegistryCASConflictError):
        persist_fact_and_advance_current(divergent, "credential-idem-b", 0, "x" * 128, "y" * 128, fact_collection=facts, pointer_collection=pointers, session=Session())
    assert len(facts.docs) == 1


def test_current_lookup_uses_four_field_stream_then_checks_fingerprint() -> None:
    facts, pointers, _ = _seed()
    current = get_current_fact(
        "tenant-a",
        "provider-a",
        "merchant-config-a",
        1,
        CONFIGURATION_FINGERPRINT,
        fact_collection=facts,
        pointer_collection=pointers,
        session=Session(),
    )
    assert current is not None
    assert "merchant_configuration_fingerprint" not in pointers.last_queries[-1]
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityRegistryCASConflictError):
        get_current_fact(
            "tenant-a",
            "provider-a",
            "merchant-config-a",
            1,
            "c" * 128,
            fact_collection=facts,
            pointer_collection=pointers,
            session=Session(),
        )


def test_corrupt_parallel_pointers_fail_closed_without_selection_or_repair() -> None:
    facts, pointers, _ = _seed()
    corrupt = dict(pointers.docs[0])
    corrupt["merchant_configuration_fingerprint"] = "c" * 128
    pointers.docs.append(corrupt)
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityRegistryPersistenceCorruptionError):
        get_current_fact(
            "tenant-a",
            "provider-a",
            "merchant-config-a",
            1,
            CONFIGURATION_FINGERPRINT,
            fact_collection=facts,
            pointer_collection=pointers,
            session=Session(),
        )
    assert len(pointers.docs) == 2


def test_cas_requires_prior_configuration_fingerprint_correlation() -> None:
    facts, pointers, first = _seed()
    pointer = get_current_pointer(first, pointers, session=Session())
    assert pointer is not None
    second = _fact(security_state=TenantInboundProviderCredentialSecurityState.COMPROMISED, security_revision=1)
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityRegistryCASConflictError):
        persist_fact_and_advance_current(
            second,
            "credential-idem-b",
            0,
            pointer.security_fact_id,
            pointer.security_fingerprint,
            expected_prior_configuration_fingerprint="c" * 128,
            fact_collection=facts,
            pointer_collection=pointers,
            session=Session(),
        )
    assert len(facts.docs) == 1


def test_revision_unique_index_excludes_configuration_fingerprint() -> None:
    facts, _, first = _seed()
    divergent = _fact(merchant_configuration_fingerprint="c" * 128)
    with pytest.raises(DuplicateKeyError):
        facts.insert_one(
            registry._fact_document(divergent, security_fact_id(divergent), "credential-idem-c")
        )


def test_same_key_different_tenant_is_independent() -> None:
    facts, pointers, _ = _seed()
    other = _fact(tenant_id="tenant-b")
    persist_fact_and_advance_current(other, "credential-idem-a", None, None, None, fact_collection=facts, pointer_collection=pointers, session=Session())
    assert len(facts.docs) == 2 and len(pointers.docs) == 2
    assert get_current_fact("tenant-a", "provider-a", "merchant-config-a", 1, CONFIGURATION_FINGERPRINT, fact_collection=facts, pointer_collection=pointers, session=Session()) is not None
    assert get_current_fact("tenant-b", "provider-a", "merchant-config-a", 1, CONFIGURATION_FINGERPRINT, fact_collection=facts, pointer_collection=pointers, session=Session()) == other


def test_subsequent_n_plus_one_transition_succeeds() -> None:
    facts, pointers, first = _seed()
    pointer = get_current_pointer(first, pointers, session=Session())
    assert pointer is not None
    second = _fact(security_state=TenantInboundProviderCredentialSecurityState.COMPROMISED, security_revision=1)
    persist_fact_and_advance_current(second, "credential-idem-b", pointer.security_revision, pointer.security_fact_id, pointer.security_fingerprint, expected_prior_configuration_fingerprint=CONFIGURATION_FINGERPRINT, fact_collection=facts, pointer_collection=pointers, session=Session())
    current = get_current_fact("tenant-a", "provider-a", "merchant-config-a", 1, CONFIGURATION_FINGERPRINT, fact_collection=facts, pointer_collection=pointers, session=Session())
    assert current == second
    assert len(facts.docs) == 2


@pytest.mark.parametrize("case", ["gap", "stale", "wrong_fact", "wrong_fingerprint"])
def test_revision_and_complete_prior_pointer_cas_reject(case: str) -> None:
    facts, pointers, first = _seed()
    pointer = get_current_pointer(first, pointers, session=Session())
    assert pointer is not None
    second = _fact(security_state=TenantInboundProviderCredentialSecurityState.COMPROMISED, security_revision=1)
    revision = pointer.security_revision + (2 if case == "gap" else 1)
    prior_revision = pointer.security_revision if case != "stale" else 9
    prior_fact = pointer.security_fact_id if case != "wrong_fact" else "f" * 128
    prior_fp = pointer.security_fingerprint if case != "wrong_fingerprint" else "f" * 128
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityRegistryCASConflictError):
        candidate = second if revision == 1 else _fact(security_state=TenantInboundProviderCredentialSecurityState.COMPROMISED, security_revision=revision)
        persist_fact_and_advance_current(candidate, "credential-idem-b", prior_revision, prior_fact, prior_fp, expected_prior_configuration_fingerprint=CONFIGURATION_FINGERPRINT, fact_collection=facts, pointer_collection=pointers, session=Session())
    assert len(facts.docs) == 1
    assert pointers.docs[0]["security_revision"] == 0


def test_pointer_and_fact_are_atomic_on_update_miss() -> None:
    facts, pointers, first = _seed()
    pointer = get_current_pointer(first, pointers, session=Session())
    assert pointer is not None
    pointers.force_update_miss = True
    second = _fact(security_state=TenantInboundProviderCredentialSecurityState.COMPROMISED, security_revision=1)
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityRegistryCASConflictError):
        persist_fact_and_advance_current(second, "credential-idem-b", 0, pointer.security_fact_id, pointer.security_fingerprint, expected_prior_configuration_fingerprint=CONFIGURATION_FINGERPRINT, fact_collection=facts, pointer_collection=pointers, session=Session())
    assert pointers.docs[0]["security_revision"] == 0


@pytest.mark.parametrize("missing", ["tenant_id", "security_state", "security_fingerprint"])
def test_missing_fact_fields_fail_closed(missing: str) -> None:
    facts, _, value = _seed()
    facts.docs[0].pop(missing, None)
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError):
        registry._hydrate_fact(facts.docs[0])


def test_fact_fingerprint_mismatch_fails_closed() -> None:
    facts, _, value = _seed()
    facts.docs[0]["security_fingerprint"] = "f" * 128
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError):
        get_fact("tenant-a", security_fact_id(value), facts, session=Session())


def test_pointer_round_trip_is_strict_and_frozen() -> None:
    _, pointers, value = _seed()
    pointer = get_current_pointer(value, pointers, session=Session())
    assert pointer is not None
    assert set(pointer.to_dict()) == set(TenantInboundProviderCredentialSecurityCurrent._FIELDS)
    with pytest.raises(FrozenInstanceError):
        pointer.security_revision = 9  # type: ignore[misc]
    pointers.docs[0]["latest"] = True
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError):
        get_current_pointer(value, pointers, session=Session())


@pytest.mark.parametrize("field", ["security_fact_id", "tenant_id", "provider_id", "merchant_configuration_id", "merchant_configuration_version", "merchant_configuration_fingerprint", "security_revision", "credential_version", "security_fingerprint"])
def test_pointer_fact_provenance_mismatch_fails_closed(field: str) -> None:
    facts, pointers, value = _seed()
    if field in {"security_fact_id", "security_fingerprint"}:
        pointers.docs[0][field] = "f" * 128
    elif field == "security_revision":
        pointers.docs[0][field] = 2
    elif field == "merchant_configuration_version":
        pointers.docs[0][field] = 2
    else:
        pointers.docs[0][field] = "other"
    if field in {"tenant_id", "provider_id", "merchant_configuration_id", "merchant_configuration_version"}:
        assert get_current_fact(
            "tenant-a",
            "provider-a",
            "merchant-config-a",
            1,
            CONFIGURATION_FINGERPRINT,
            fact_collection=facts,
            pointer_collection=pointers,
            session=Session(),
        ) is None
    elif field == "merchant_configuration_fingerprint":
        with pytest.raises((TenantInboundProviderCredentialSecurityAuthorityRegistryCASConflictError, TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError)):
            get_current_fact(
                "tenant-a",
                "provider-a",
                "merchant-config-a",
                1,
                CONFIGURATION_FINGERPRINT,
                fact_collection=facts,
                pointer_collection=pointers,
                session=Session(),
            )
    else:
        lookup = {
            "tenant_id": pointers.docs[0].get("tenant_id", "tenant-a"),
            "provider_id": pointers.docs[0].get("provider_id", "provider-a"),
            "merchant_configuration_id": pointers.docs[0].get("merchant_configuration_id", "merchant-config-a"),
            "merchant_configuration_version": pointers.docs[0].get("merchant_configuration_version", 1),
            "merchant_configuration_fingerprint": pointers.docs[0].get("merchant_configuration_fingerprint", CONFIGURATION_FINGERPRINT),
        }
        with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError):
            get_current_fact("tenant-a", "provider-a", "merchant-config-a", 1, CONFIGURATION_FINGERPRINT, fact_collection=facts, pointer_collection=pointers, session=Session())


def test_current_lookup_uses_pointer_not_latest_fact() -> None:
    facts, pointers, first = _seed()
    pointer = get_current_pointer(first, pointers, session=Session())
    assert pointer is not None
    second = _fact(security_state=TenantInboundProviderCredentialSecurityState.COMPROMISED, security_revision=1)
    persist_fact_and_advance_current(second, "credential-idem-b", 0, pointer.security_fact_id, pointer.security_fingerprint, expected_prior_configuration_fingerprint=CONFIGURATION_FINGERPRINT, fact_collection=facts, pointer_collection=pointers, session=Session())
    assert get_current_fact("tenant-a", "provider-a", "merchant-config-a", 1, CONFIGURATION_FINGERPRINT, fact_collection=facts, pointer_collection=pointers, session=Session()) == second


def test_time_expired_fact_can_remain_current_without_mutation() -> None:
    facts, pointers = _collections()
    expired = _fact(valid_from=NOW - timedelta(hours=2), valid_until=NOW - timedelta(hours=1), evaluated_at=NOW - timedelta(hours=2))
    persist_fact_and_advance_current(expired, "expired-key", None, None, None, fact_collection=facts, pointer_collection=pointers, session=Session())
    assert get_current_fact("tenant-a", "provider-a", "merchant-config-a", 1, CONFIGURATION_FINGERPRINT, fact_collection=facts, pointer_collection=pointers, session=Session()) == expired
    assert len(facts.docs) == 1


def test_raw_document_never_returned_and_corrupt_pointer_fails() -> None:
    facts, pointers, value = _seed()
    current = get_current_fact("tenant-a", "provider-a", "merchant-config-a", 1, CONFIGURATION_FINGERPRINT, fact_collection=facts, pointer_collection=pointers, session=Session())
    assert isinstance(current, TenantInboundProviderCredentialSecurityAuthority)
    pointers.docs[0]["security_fact_id"] = "missing"
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError):
        get_current_fact("tenant-a", "provider-a", "merchant-config-a", 1, CONFIGURATION_FINGERPRINT, fact_collection=facts, pointer_collection=pointers, session=Session())


def test_transaction_and_authority_firewalls() -> None:
    facts, pointers = _collections()
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityRegistryTransactionError):
        persist_fact_and_advance_current(_fact(), "key", None, None, None, fact_collection=facts, pointer_collection=pointers, session=None)
    source = inspect.getsource(registry)
    assert ".start_transaction(" not in source
    assert ".commit_transaction(" not in source
    assert ".abort_transaction(" not in source
    assert "MongoClient" not in source
    assert "resolve_secret" not in source
    assert "ClientInvoice" not in source
    assert "KMSClient" not in source


def test_registry_import_has_no_index_bootstrap_or_network_side_effect() -> None:
    source = inspect.getsource(registry)
    assert "ensure_indexes(" not in source.split("def ensure_indexes", 1)[0]
    assert "socket" not in source
    assert "requests" not in source
    assert "os.environ" not in source


def test_security_fact_id_is_deterministic_and_distinct_from_domain_fingerprint() -> None:
    first, second = _fact(), _fact()
    assert security_fact_id(first) == security_fact_id(second)
    assert security_fact_id(first) != first.fingerprint
    assert security_fact_id(replace(first, security_fingerprint=None, credential_version="v2")) != security_fact_id(first)


def test_no_multikey_or_null_sentinel_idempotency_scheme() -> None:
    source = inspect.getsource(registry)
    assert "lifecycle_history" not in source
    assert "partialFilterExpression" not in source
    assert "idempotency_keys" not in source
    assert IDEMPOTENCY_KEY_FIELD in source


def test_registry_does_not_evaluate_security_or_create_authority() -> None:
    source = inspect.getsource(registry)
    assert "TenantInboundProviderCredentialSecurityAuthority(" not in source
    assert "authorize" not in source.lower()
    assert "current_privilege" not in source
    assert "credential_safe" not in source
    assert "def authorize" not in source
    assert "def create_session" not in source


# REQUIRED_DIRECT_CASE_COUNT=50; parameterized cases provide explicit proof for
# state, index, strictness, tenant isolation, replay, CAS, provenance, and firewalls.
# ARTIFACT: test_tenant_inbound_provider_credential_security_authority_registry.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P3-R2
# AUTHORITY BOUNDARY: persistence/currentness only; no issuance or provider binding.
# TENANT POSTURE: all reads, writes, replay predicates, and pointers are tenant-scoped.
# FAIL-CLOSED POSTURE: corrupt records and stale/divergent identities reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
