"""Direct certificate for the Legal Storefront public-intent registry.

TITLE: Legal Storefront Public Intent Registry Direct Certificate
VERSION: v1.0.0-L8-9B-LEGAL-STOREFRONT-PUBLIC-INTENT-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Adversarially certify pre-tenant append-only durability, exact replay,
         strict corruption rejection, active caller-transaction enforcement,
         deterministic unique indexes, duplicate-race signaling and the absence
         of tenant, contact-search, retention or downstream authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_storefront_public_intent_registry.py
COLLABORATION / OWNERSHIP: Certifies only L8-9B registry behavior. L8-9A owns
                            immutable intent semantics; Mongo integration,
                            public HTTP, identity verification, tenant genesis,
                            retention/deletion and downstream admission remain
                            separately certified boundaries.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-9B-LEGAL-STOREFRONT-PUBLIC-INTENT-REGISTRY-CERT
           establishes the direct adversarial registry certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic public-intent metadata only; no live
                             credentials, tenants, customer records or providers.
TENANT BOUNDARY: Explicitly pre-tenant. The registry must neither store nor
                 accept tenant identity and exposes no tenant lookup.
AUTHORITY BOUNDARY: Test evidence only; creates no production authority.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import inspect
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_storefront_public_intent import (
    LegalStorefrontPublicIntent,
    create_legal_storefront_public_intent,
)
from tools.eos.legal_operations.registry.legal_storefront_public_intent_registry import (
    COLLECTION,
    INDEX_FINGERPRINT,
    INDEX_INTENT_ID,
    LegalStorefrontPublicIntentRegistry,
    LegalStorefrontPublicIntentRegistryConflictError,
    LegalStorefrontPublicIntentRegistryError,
    LegalStorefrontPublicIntentRegistryPersistenceError,
    LegalStorefrontPublicIntentRegistryRetryTransactionError,
    LegalStorefrontPublicIntentRegistryTransactionRequiredError,
    ensure_indexes,
)


NOW = datetime(2026, 10, 12, 9, 21, 0, 123456, tzinfo=timezone.utc)


class _Session:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class _Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[
            tuple[list[tuple[str, int]], str, bool]
        ] = []
        self.fail_read = False
        self.fail_insert = False
        self.duplicate_insert = False

    def create_index(
        self,
        keys: list[tuple[str, int]],
        *,
        name: str,
        unique: bool = False,
    ) -> str:
        self.indexes.append((keys, name, unique))
        return name

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object,
    ) -> dict[str, object] | None:
        assert session is not None
        if self.fail_read:
            raise PyMongoError("synthetic-read-failure")
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return deepcopy(row)
        return None

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: object,
    ) -> object:
        assert session is not None
        if self.duplicate_insert:
            raise DuplicateKeyError("synthetic-duplicate")
        if self.fail_insert:
            raise PyMongoError("synthetic-insert-failure")
        self.rows.append(deepcopy(document))
        return object()


def _intent(
    *,
    intent_id: str = "legal-storefront-intent:01",
    organization_name: str = "Khanyezi Legal",
    contact_email: str = "intake@example.org",
) -> LegalStorefrontPublicIntent:
    return create_legal_storefront_public_intent(
        intent_id=intent_id,
        organization_name=organization_name,
        contact_email=contact_email,
        industry="Legal Services",
        region="ZA",
        submitted_at=NOW,
    )


def test_collection_name_is_exact_and_pretenant() -> None:
    assert COLLECTION == "legal_storefront_public_intents"
    assert "tenant" not in COLLECTION


def test_indexes_are_exact_unique_and_have_no_ttl() -> None:
    collection = _Collection()

    ensure_indexes(collection)

    assert collection.indexes == [
        ([("intent_id", 1)], INDEX_INTENT_ID, True),
        ([("fingerprint", 1)], INDEX_FINGERPRINT, True),
    ]
    assert all(
        "expire" not in repr(index).lower()
        and "ttl" not in repr(index).lower()
        for index in collection.indexes
    )


def test_create_persists_exact_domain_payload() -> None:
    collection = _Collection()
    registry = LegalStorefrontPublicIntentRegistry(collection)
    intent = _intent()

    result = registry.create_or_replay(intent, session=_Session())

    assert result == intent
    assert collection.rows == [intent.to_dict()]
    assert "tenant_id" not in collection.rows[0]


def test_exact_intent_identity_replay_performs_zero_second_write() -> None:
    collection = _Collection()
    registry = LegalStorefrontPublicIntentRegistry(collection)
    intent = _intent()
    collection.rows.append(intent.to_dict())

    result = registry.create_or_replay(intent, session=_Session())

    assert result == intent
    assert collection.rows == [intent.to_dict()]


def test_exact_fingerprint_replay_is_allowed() -> None:
    collection = _Collection()
    registry = LegalStorefrontPublicIntentRegistry(collection)
    intent = _intent()
    collection.rows.append(intent.to_dict())

    result = registry.create_or_replay(intent, session=_Session())

    assert result.fingerprint == intent.fingerprint
    assert len(collection.rows) == 1


def test_same_intent_id_with_divergent_evidence_fails_closed() -> None:
    collection = _Collection()
    registry = LegalStorefrontPublicIntentRegistry(collection)
    original = _intent()
    divergent = _intent(organization_name="Different Legal")
    row = divergent.to_dict()
    row["intent_id"] = original.intent_id
    collection.rows.append(row)

    with pytest.raises(
        LegalStorefrontPublicIntentRegistryError,
    ):
        registry.create_or_replay(original, session=_Session())


def test_divergent_fingerprint_collision_fails_closed() -> None:
    collection = _Collection()
    registry = LegalStorefrontPublicIntentRegistry(collection)
    original = _intent()
    other = _intent(
        intent_id="legal-storefront-intent:02",
        organization_name="Other Legal",
    )
    row = other.to_dict()
    row["fingerprint"] = original.fingerprint
    collection.rows.append(row)

    with pytest.raises(
        LegalStorefrontPublicIntentRegistryError,
    ):
        registry.create_or_replay(original, session=_Session())


def test_missing_transaction_rejects_before_write() -> None:
    collection = _Collection()
    registry = LegalStorefrontPublicIntentRegistry(collection)

    with pytest.raises(
        LegalStorefrontPublicIntentRegistryTransactionRequiredError,
        match="L8_9B_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(_intent(), session=None)

    assert collection.rows == []


def test_inactive_transaction_rejects_before_write() -> None:
    collection = _Collection()
    registry = LegalStorefrontPublicIntentRegistry(collection)

    with pytest.raises(
        LegalStorefrontPublicIntentRegistryTransactionRequiredError,
        match="L8_9B_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(_intent(), session=_Session(False))

    assert collection.rows == []


def test_wrong_domain_type_rejects() -> None:
    registry = LegalStorefrontPublicIntentRegistry(_Collection())

    with pytest.raises(
        LegalStorefrontPublicIntentRegistryError,
        match="L8_9B_INTENT_REQUIRED",
    ):
        registry.create_or_replay(object(), session=_Session())  # type: ignore[arg-type]


def test_duplicate_write_race_requires_fresh_transaction() -> None:
    collection = _Collection()
    collection.duplicate_insert = True
    registry = LegalStorefrontPublicIntentRegistry(collection)

    with pytest.raises(
        LegalStorefrontPublicIntentRegistryRetryTransactionError,
        match="L8_9B_RETRY_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(_intent(), session=_Session())


def test_mongo_read_failure_is_non_sensitive_persistence_error() -> None:
    collection = _Collection()
    collection.fail_read = True
    registry = LegalStorefrontPublicIntentRegistry(collection)

    with pytest.raises(
        LegalStorefrontPublicIntentRegistryPersistenceError,
        match="L8_9B_PERSISTENCE_UNAVAILABLE",
    ):
        registry.get_by_intent_id(
            intent_id="legal-storefront-intent:01",
            session=_Session(),
        )


def test_mongo_insert_failure_is_non_sensitive_persistence_error() -> None:
    collection = _Collection()
    collection.fail_insert = True
    registry = LegalStorefrontPublicIntentRegistry(collection)

    with pytest.raises(
        LegalStorefrontPublicIntentRegistryPersistenceError,
        match="L8_9B_PERSISTENCE_UNAVAILABLE",
    ):
        registry.create_or_replay(_intent(), session=_Session())


def test_exact_intent_lookup_round_trips() -> None:
    collection = _Collection()
    intent = _intent()
    collection.rows.append(intent.to_dict())
    registry = LegalStorefrontPublicIntentRegistry(collection)

    result = registry.get_by_intent_id(
        intent_id=intent.intent_id,
        session=_Session(),
    )

    assert result == intent


def test_missing_intent_is_canonical_absence() -> None:
    registry = LegalStorefrontPublicIntentRegistry(_Collection())

    result = registry.get_by_intent_id(
        intent_id="legal-storefront-intent:missing",
        session=_Session(),
    )

    assert result is None


@pytest.mark.parametrize(
    "corruption",
    [
        {"tenant_id": "forbidden-tenant"},
        {"plan": "ENTERPRISE"},
        {"password": "forbidden"},
        {"subscription_id": "forbidden"},
        {"entitlement_id": "forbidden"},
        {"case_matter_id": "forbidden"},
        {"payment_id": "forbidden"},
    ],
)
def test_persisted_authority_field_injection_is_corruption(
    corruption: dict[str, str],
) -> None:
    collection = _Collection()
    row = _intent().to_dict()
    row.update(corruption)
    collection.rows.append(row)
    registry = LegalStorefrontPublicIntentRegistry(collection)

    with pytest.raises(
        LegalStorefrontPublicIntentRegistryError,
        match="L8_9B_CORRUPT_INTENT",
    ):
        registry.get_by_intent_id(
            intent_id="legal-storefront-intent:01",
            session=_Session(),
        )


def test_persisted_fingerprint_corruption_rejects() -> None:
    collection = _Collection()
    row = _intent().to_dict()
    row["fingerprint"] = "0" * 128
    collection.rows.append(row)
    registry = LegalStorefrontPublicIntentRegistry(collection)

    with pytest.raises(
        LegalStorefrontPublicIntentRegistryError,
        match="L8_9B_CORRUPT_INTENT",
    ):
        registry.get_by_intent_id(
            intent_id="legal-storefront-intent:01",
            session=_Session(),
        )


def test_persisted_missing_field_rejects() -> None:
    collection = _Collection()
    row = _intent().to_dict()
    row.pop("industry")
    collection.rows.append(row)
    registry = LegalStorefrontPublicIntentRegistry(collection)

    with pytest.raises(
        LegalStorefrontPublicIntentRegistryError,
        match="L8_9B_CORRUPT_INTENT",
    ):
        registry.get_by_intent_id(
            intent_id="legal-storefront-intent:01",
            session=_Session(),
        )


def test_lookup_surface_is_opaque_identity_only() -> None:
    public_methods = {
        name
        for name, member in inspect.getmembers(
            LegalStorefrontPublicIntentRegistry,
            predicate=inspect.isfunction,
        )
        if not name.startswith("_")
    }

    assert public_methods == {
        "create_or_replay",
        "ensure_indexes",
        "get_by_intent_id",
    }


def test_registry_exposes_no_contact_or_tenant_query_parameters() -> None:
    forbidden = {
        "tenant_id",
        "contact_email",
        "organization_name",
        "industry",
        "region",
    }

    for name in ("create_or_replay", "get_by_intent_id"):
        parameters = set(
            inspect.signature(
                getattr(LegalStorefrontPublicIntentRegistry, name)
            ).parameters
        )
        assert forbidden.isdisjoint(parameters)


def test_no_delete_purge_or_expiry_api_exists() -> None:
    names = {
        name.lower()
        for name in dir(LegalStorefrontPublicIntentRegistry)
    }

    assert all(
        forbidden not in names
        for forbidden in {
            "delete",
            "purge",
            "expire",
            "remove",
        }
    )


# ARTIFACT: test_legal_storefront_public_intent_registry.py
# VERSION: v1.0.0-L8-9B-LEGAL-STOREFRONT-PUBLIC-INTENT-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct registry certificate only; no production authority
# TENANT POSTURE: synthetic pre-tenant evidence only; tenant identity is neither stored nor queried
# TRANSACTION POSTURE: active caller-owned transaction is mandatory for operational reads/writes
# RETENTION POSTURE: certificate proves no delete, purge, expiry or TTL authority
# FAIL-CLOSED POSTURE: malformed, corrupt, divergent, racy and Mongo-failure paths reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
