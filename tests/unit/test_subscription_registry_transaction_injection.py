"""Direct certificate for bounded SubscriptionRegistry transaction injection.

TITLE: SubscriptionRegistry Transaction Injection Direct Certificate
VERSION: v1.0.0-D22B3-P34-SUBSCRIPTION-TRANSACTION-INJECTION-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove exact optional collection/session forwarding while preserving
         legacy defaults, lifecycle delegation and caller transaction ownership.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_subscription_registry_transaction_injection.py
COLLABORATION / OWNERSHIP: SubscriptionRegistry owns subscription persistence;
                            callers retain Mongo transaction lifecycle authority.
CERTIFICATION / UPDATE DATE: 2026-10-09
CHANGELOG: v1.0.0-D22B3-P34-SUBSCRIPTION-TRANSACTION-INJECTION-CERT adds direct
           evidence for create, duplicate replay, mutation CAS and lifecycle
           collection/session propagation without authority-semantic changes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identifiers only; no credentials or PII.
TENANT BOUNDARY: Every asserted read/write retains exact tenant scope.
AUTHORITY BOUNDARY: Dependency-injection certificate only.
TRANSACTION BOUNDARY: Fakes expose no transaction lifecycle methods.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

import inspect
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.saas.billing import subscription_registry as registry
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.domain.subscription import (
    BillingFrequency,
    PlanTiers,
    SubscriptionStatus,
)


class Result:
    """Minimal acknowledged replacement result."""

    matched_count = 1


class Collection:
    """Record exact Mongo method arguments without transaction ownership."""

    def __init__(self) -> None:
        self.find_results: list[dict[str, Any] | None] = []
        self.find_calls: list[tuple[dict[str, Any], object]] = []
        self.insert_calls: list[tuple[dict[str, Any], object]] = []
        self.replace_calls: list[tuple[dict[str, Any], dict[str, Any], object]] = []
        self.insert_error: BaseException | None = None

    def find_one(self, query: dict[str, Any], *, session: object = None) -> dict[str, Any] | None:
        self.find_calls.append((query, session))
        return self.find_results.pop(0) if self.find_results else None

    def insert_one(self, document: dict[str, Any], *, session: object = None) -> object:
        self.insert_calls.append((document, session))
        if self.insert_error is not None:
            raise self.insert_error
        return object()

    def replace_one(
        self, query: dict[str, Any], replacement: dict[str, Any], *, session: object = None,
    ) -> Result:
        self.replace_calls.append((query, replacement, session))
        return Result()


def _plan() -> SimpleNamespace:
    """Return the minimum canonical catalogue projection used by create."""
    return SimpleNamespace(
        plan_id="plan-p34",
        plan_type=SimpleNamespace(value=PlanTiers.PROFESSIONAL.value),
        billing_frequency=SimpleNamespace(value=BillingFrequency.MONTHLY.value),
        name="P34 Plan",
        features=("legal.core",),
        catalogue_version=1,
        price=100.0,
        currency="ZAR",
    )


def _payload(*, key: str = "p34-key", status: str = "active") -> dict[str, Any]:
    """Return one valid legacy-compatible creation command."""
    return {
        "tenantId": "tenant-p34",
        "planId": "plan-p34",
        "startDate": "2026-10-09T12:00:00+00:00",
        "idempotencyKey": key,
        "billingMode": "PLATFORM",
        "status": status,
    }


def _prepare_create(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep catalogue authority deterministic while testing persistence routing."""
    monkeypatch.setattr(SubscriptionRegistry, "_resolve_catalogue_plan", classmethod(lambda cls, *_: _plan()))
    monkeypatch.setattr(registry, "_ensure_indexes", lambda collection=None: None)


def test_legacy_defaults_and_public_positional_compatibility(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Omitted dependencies retain global collection and legacy positional APIs."""
    collection = Collection()
    monkeypatch.setattr(registry, "subscriptions_collection", collection)
    assert registry._find_document("subscription-a", "tenant-p34") is None
    assert collection.find_calls == [(
        {"tenant_id": "tenant-p34", "subscription_id": "subscription-a"}, None
    )]
    assert list(inspect.signature(SubscriptionRegistry.create).parameters)[:3] == [
        "payload", "tenant_id_header", "collection"
    ]


def test_create_uses_exact_injected_collection_and_session_for_find_and_insert(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fresh create routes initial replay lookup and insert through one dependency pair."""
    _prepare_create(monkeypatch)
    collection, session = Collection(), object()
    result = SubscriptionRegistry.create(
        _payload(), "tenant-p34", collection=collection, session=session
    )
    assert result["success"] is True and result["replayed"] is False
    assert collection.find_calls == [(
        {"tenant_id": "tenant-p34", "idempotency_key": "p34-key"}, session
    )]
    assert len(collection.insert_calls) == 1
    assert collection.insert_calls[0][1] is session


def test_duplicate_key_replay_uses_same_collection_and_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Idempotency duplicate recovery cannot switch persistence or lose session."""
    _prepare_create(monkeypatch)
    first = Collection()
    created = SubscriptionRegistry.create(
        _payload(), "tenant-p34", collection=first, session=object()
    )
    document = first.insert_calls[0][0]
    collection, session = Collection(), object()
    collection.find_results = [None, document]
    collection.insert_error = DuplicateKeyError(
        "tenant_idempotency_unique",
        details={"keyPattern": {"tenant_id": 1, "idempotency_key": 1}},
    )
    replay = SubscriptionRegistry.create(
        _payload(), "tenant-p34", collection=collection, session=session
    )
    assert created["success"] is True
    assert replay["success"] is True and replay["replayed"] is True
    assert len(collection.find_calls) == 2
    assert all(call[1] is session for call in collection.find_calls)
    assert collection.insert_calls[0][1] is session


def test_mutation_read_and_replace_receive_exact_collection_and_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The mutation seam forwards one dependency pair into read and CAS write."""
    collection, session = object(), object()
    calls: list[tuple[str, object, object]] = []
    entity = SimpleNamespace(tenant_id="tenant-p34", subscription_id="sub-p34")
    monkeypatch.setattr(
        registry,
        "_find_document",
        lambda *_args, collection=None, session=None: calls.append(("find", collection, session)) or {"row": True},
    )
    monkeypatch.setattr(registry, "_hydrate", lambda _document: entity)
    monkeypatch.setattr(
        registry,
        "_replace_document",
        lambda _previous, replacement, *, collection=None, session=None: calls.append(("replace", collection, session)) or replacement,
    )
    result = SubscriptionRegistry._mutate(
        "sub-p34", "tenant-p34", lambda current: current,
        collection=collection, session=session,
    )
    assert result["success"] is True
    assert calls == [("find", collection, session), ("replace", collection, session)]


def test_replace_preserves_exact_revision_cas_and_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Injected persistence retains tenant, identity and prior-revision predicate."""
    collection, session = Collection(), object()
    previous = {
        "tenant_id": "tenant-p34",
        "subscription_id": "sub-p34",
        "_registry_revision": 7,
    }
    entity = SimpleNamespace(tenant_id="tenant-p34", subscription_id="sub-p34")
    monkeypatch.setattr(registry, "_validate_create_evidence", lambda _row: ("material", "f" * 128))
    monkeypatch.setattr(
        registry,
        "_document_for",
        lambda value, **kwargs: {"entity": value, "revision": kwargs["revision"]},
    )
    monkeypatch.setattr(registry, "_hydrate", lambda row: row)
    persisted: Any = registry._replace_document(
        previous, entity, collection=collection, session=session  # type: ignore[arg-type]
    )
    assert persisted["revision"] == 8
    assert collection.replace_calls == [(
        {
            "tenant_id": "tenant-p34",
            "subscription_id": "sub-p34",
            "_registry_revision": 7,
        },
        persisted,
        session,
    )]


@pytest.mark.parametrize("method_name", ["resume", "reactivate"])
def test_lifecycle_methods_forward_exact_dependencies(
    monkeypatch: pytest.MonkeyPatch, method_name: str,
) -> None:
    """Resume and reactivate delegate the exact collection/session through mutation."""
    collection, session = object(), object()
    captured: dict[str, object] = {}

    def mutate(cls: object, *args: object, **kwargs: object) -> dict[str, Any]:
        captured.update(kwargs)
        return {"success": True}

    monkeypatch.setattr(SubscriptionRegistry, "_mutate", classmethod(mutate))
    method = getattr(SubscriptionRegistry, method_name)
    result = method(
        "sub-p34", "tenant-p34", collection=collection, session=session
    )
    assert result["success"] is True
    assert captured == {"collection": collection, "session": session}


def test_source_contains_no_transaction_lifecycle_ownership() -> None:
    """Registry remains transaction-stateless by structural evidence."""
    source = Path(registry.__file__).read_text(encoding="utf-8")
    for token in (
        "start_session(", "start_transaction(", "commit_transaction(",
        "abort_transaction(", "with_transaction(",
    ):
        assert token not in source


def test_lifecycle_transition_laws_remain_exact() -> None:
    """The bounded source still guards only PAUSED and CANCELLED activation paths."""
    source = Path(registry.__file__).read_text(encoding="utf-8")
    assert "sub.status != SubscriptionStatus.PAUSED" in source
    assert "sub.status != SubscriptionStatus.CANCELLED" in source
    assert source.count('"status": SubscriptionStatus.ACTIVE.value') >= 2

# ARTIFACT: test_subscription_registry_transaction_injection.py
# VERSION: v1.0.0-D22B3-P34-SUBSCRIPTION-TRANSACTION-INJECTION-CERT
# AUTHORITY BOUNDARY: direct dependency-injection certification only
# TENANT POSTURE: exact tenant-filter and dependency-forwarding assertions
# FAIL-CLOSED POSTURE: session loss, collection drift and CAS drift fail tests
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
