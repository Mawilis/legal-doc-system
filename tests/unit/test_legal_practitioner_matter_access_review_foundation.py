"""R65 non-authorizing matter-access review foundation certificate.

Only the immutable domain and transaction-bound registry are imported.
No operational access, approval, HTTP or issuer authority is certified.
"""
from copy import deepcopy
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_practitioner_matter_access_review import (
    LegalPractitionerMatterAccessReview as Review,
    MatterAccessReviewBlocker as Blocker,
    MatterAccessReviewDecision as Decision,
    MatterAccessReviewError,
)
from tools.eos.legal_operations.registry.legal_practitioner_matter_access_review_codec import (create_review, serialize, verify_integrity)
from tools.eos.legal_operations.registry import (
    legal_practitioner_matter_access_review_registry as registry,
)

NOW = datetime(2026, 10, 22, 4, 0, tzinfo=timezone.utc)


def make_review(**changes):
    values = {
        "review_request_id": "request-1",
        "tenant_id": "tenant-1",
        "case_matter_id": "matter-1",
        "practitioner_principal_id": "practitioner-1",
        "requested_by_principal_id": "partner-1",
        "decision": Decision.PENDING_REVIEW,
        "blockers": (
            Blocker.REGULATOR_ISSUER_TRUST_UNRATIFIED,
            Blocker.ETHICAL_WALL_CLEARANCE_NOT_ESTABLISHED,
        ),
        "reason_reference": "reason-1",
        "idempotency_key": "key-1",
        "recorded_at": NOW,
    }
    values.update(changes)
    return create_review(**values)


class Session:
    in_transaction = True


class Collection:
    def __init__(self):
        self.rows = []
        self.indexes = []
        self.duplicate = False

    def create_index(self, keys, **options):
        self.indexes.append((tuple(keys), dict(options)))
        return options["name"]

    def find_one(self, predicate, *, session):
        clauses = predicate.get("$or", [predicate])
        for row in self.rows:
            if any(all(row.get(k) == v for k, v in part.items()) for part in clauses):
                return deepcopy(row)
        return None

    def insert_one(self, document, *, session):
        if self.duplicate:
            raise DuplicateKeyError("duplicate")
        self.rows.append(deepcopy(document))
        return SimpleNamespace(inserted_id="r65")


def test_domain_denies_positive_authority_and_preserves_integrity():
    value = make_review()
    assert set(Decision) == {Decision.PENDING_REVIEW, Decision.DENIED}
    assert value.permits_operational_access is False
    assert verify_integrity(value)
    assert len(value.fingerprint) == 128
    assert serialize(value)["fingerprint"] == value.fingerprint


@pytest.mark.parametrize("tenant", ["default", "root", "*", "global"])
def test_pseudo_tenant_is_forbidden(tenant):
    with pytest.raises(MatterAccessReviewError):
        make_review(tenant_id=tenant)


def test_domain_rejects_duplicate_blocker_and_noncanonical_time():
    with pytest.raises(MatterAccessReviewError):
        make_review(blockers=(Blocker.REGULATOR_ISSUER_TRUST_UNRATIFIED,) * 2)
    with pytest.raises(MatterAccessReviewError):
        make_review(recorded_at=NOW.replace(microsecond=10))


def test_domain_fingerprint_binds_request_scope():
    original = make_review()
    changed = make_review(case_matter_id="matter-2")
    assert original.fingerprint != changed.fingerprint
    assert original != changed


def test_indexes_are_tenant_scoped_unique_and_no_ttl():
    collection = Collection()
    registry.ensure_indexes(collection)
    names = {options["name"] for _, options in collection.indexes}
    assert names == {
        registry.IDENTITY_INDEX,
        registry.IDEMPOTENCY_INDEX,
        registry.SCOPE_INDEX,
    }
    for keys, options in collection.indexes:
        assert keys[0][0] == "tenant_id"
        assert "expireAfterSeconds" not in options
        assert options.get("unique", False) == (
            options["name"] in {registry.IDENTITY_INDEX, registry.IDEMPOTENCY_INDEX}
        )


def test_registry_requires_active_transaction():
    collection = Collection()
    value = make_review()
    with pytest.raises(registry.MatterAccessReviewTransactionRequired):
        registry.append_review(review=value, collection=collection, session=None)
    with pytest.raises(registry.MatterAccessReviewTransactionRequired):
        registry.get_review(
            tenant_id=value.tenant_id,
            review_request_id=value.review_request_id,
            collection=collection,
            session=None,
        )


def test_registry_exact_replay_and_divergence():
    collection = Collection()
    value = make_review()
    assert registry.append_review(
        review=value, collection=collection, session=Session()
    ) == value
    assert registry.append_review(
        review=value, collection=collection, session=Session()
    ) == value
    assert len(collection.rows) == 1
    with pytest.raises(registry.MatterAccessReviewConflict):
        registry.append_review(
            review=make_review(review_request_id="request-2"),
            collection=collection,
            session=Session(),
        )


def test_registry_exact_tenant_read_and_tampering_rejection():
    collection = Collection()
    value = make_review()
    registry.append_review(review=value, collection=collection, session=Session())
    assert registry.get_review(
        tenant_id="foreign-tenant",
        review_request_id=value.review_request_id,
        collection=collection,
        session=Session(),
    ) is None
    collection.rows[0]["reason_reference"] = "tampered"
    with pytest.raises(registry.MatterAccessReviewPersistedInvalid):
        registry.get_review(
            tenant_id=value.tenant_id,
            review_request_id=value.review_request_id,
            collection=collection,
            session=Session(),
        )


def test_duplicate_insert_requires_whole_transaction_retry():
    collection = Collection()
    collection.duplicate = True
    with pytest.raises(registry.MatterAccessReviewRetryTransaction):
        registry.append_review(
            review=make_review(), collection=collection, session=Session()
        )
