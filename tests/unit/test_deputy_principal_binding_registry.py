"""Direct certificate for immutable deputy-principal binding persistence.

TITLE: WILSY OS Deputy Principal Binding Registry Certificate
VERSION: v1.0.2-L8-6B-DEPUTY-PRINCIPAL-BINDING-REGISTRY-CERT
AUTHORITY: Direct adversarial certificate for L8-6B binding persistence only.
EPITOME: Prove two-way one-to-one uniqueness, exact immutable replay, tenant
         isolation, caller-session propagation, strict hydration/fingerprint
         rejection, exact principal/deputy resolution, and absence of rebind,
         IAM, queue, service, AI, billing, or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_deputy_principal_binding_registry.py
COLLABORATION / OWNERSHIP: Certificate for deputy_principal_binding_registry.py;
                            domain value, P1 Deputy, and IAM remain independent.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.2-L8-6B-DEPUTY-PRINCIPAL-BINDING-REGISTRY-CERT
           makes the fake insert reproduce PyMongo caller-document _id mutation,
           proving production v1.0.3 preserves its canonical comparison payload
           while retaining one-key collision conflict and corruption proofs.
           2026-09-23 v1.0.1-L8-6B-DEPUTY-PRINCIPAL-BINDING-REGISTRY-CERT
           adds pre-index two-key inconsistency rejection and rebinds the
           certificate to production v1.0.2 race/replay hardening.
           2026-09-23 v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-REGISTRY-CERT
           establishes direct persistence, replay, both-key conflict, corruption,
           tenant-isolation, index, session, and public-surface proofs.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque values only.
TENANT BOUNDARY: Every resolution/replay predicate includes exact tenant_id.
AUTHORITY BOUNDARY: Persistence certificate only; no authorization or command.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Conflict, corruption, absence, scope drift, or
                         persistence failure never becomes successful binding.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.deputy_principal_binding import (
    DeputyPrincipalBinding,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import Deputy
from tools.eos.legal_operations.registry.deputy_principal_binding_registry import (
    VERSION as PRODUCTION_VERSION,
    DeputyPrincipalBindingConflictError,
    DeputyPrincipalBindingNotFoundError,
    DeputyPrincipalBindingPersistedRecordInvalidError,
    DeputyPrincipalBindingRegistry,
)


VERSION = "v1.0.2-L8-6B-DEPUTY-PRINCIPAL-BINDING-REGISTRY-CERT"
NOW = datetime(2026, 9, 23, 16, 0, tzinfo=timezone.utc)


class FakeSession:
    """Opaque caller-owned session marker."""


class FakeCollection:
    """Minimal Mongo-compatible collection with two-way uniqueness semantics."""

    def __init__(self) -> None:
        self.docs: list[dict[str, Any]] = []
        self.calls: list[tuple[str, object, object]] = []
        self.indexes: list[tuple[object, bool, str]] = []

    def create_index(
        self,
        keys: object,
        *,
        unique: bool,
        name: str,
    ) -> str:
        self.calls.append(("create_index", None, keys))
        self.indexes.append((keys, unique, name))
        return name

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> dict[str, Any] | None:
        self.calls.append(("find_one", session, deepcopy(query)))
        for document in self.docs:
            if all(document.get(key) == value for key, value in query.items()):
                return deepcopy(document)
        return None

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: object = None,
    ) -> object:
        """Mirror PyMongo's caller-document _id mutation before persistence."""
        self.calls.append(("insert_one", session, deepcopy(document)))
        document.setdefault("_id", f"synthetic-{len(self.docs) + 1}")
        for existing in self.docs:
            if (
                existing["tenant_id"] == document["tenant_id"]
                and (
                    existing["principal_id"] == document["principal_id"]
                    or existing["deputy_id"] == document["deputy_id"]
                    or existing["fingerprint"] == document["fingerprint"]
                )
            ):
                raise DuplicateKeyError("synthetic duplicate")
        self.docs.append(deepcopy(document))
        return SimpleNamespace(inserted_id=document["_id"])


def _deputy(
    deputy_id: str = "deputy-1",
    *,
    tenant_id: str = "tenant-a",
    sheriff_office_id: str = "office-1",
) -> Deputy:
    return Deputy(
        tenant_id=tenant_id,
        deputy_id=deputy_id,
        sheriff_office_id=sheriff_office_id,
        display_name=f"Deputy {deputy_id}",
        badge_reference=f"badge-{deputy_id}",
        evidence_reference=f"directory-{deputy_id}",
    )


def _binding(
    principal_id: str = "principal-1",
    deputy_id: str = "deputy-1",
    *,
    tenant_id: str = "tenant-a",
) -> DeputyPrincipalBinding:
    return DeputyPrincipalBinding.from_deputy(
        principal_id=principal_id,
        deputy=_deputy(deputy_id, tenant_id=tenant_id),
        bound_at=NOW,
        evidence_reference=f"binding-{principal_id}-{deputy_id}",
    )


def test_indexes_enforce_two_way_one_to_one_tenant_scope() -> None:
    collection = FakeCollection()
    DeputyPrincipalBindingRegistry.ensure_indexes(collection)

    assert collection.indexes == [
        (
            [("tenant_id", 1), ("principal_id", 1)],
            True,
            "legal_operations_tenant_principal_deputy_binding_unique",
        ),
        (
            [("tenant_id", 1), ("deputy_id", 1)],
            True,
            "legal_operations_tenant_deputy_principal_binding_unique",
        ),
        (
            [("tenant_id", 1), ("fingerprint", 1)],
            True,
            "legal_operations_tenant_deputy_binding_fingerprint_unique",
        ),
    ]


def test_create_exact_replay_and_both_resolution_paths_preserve_session() -> None:
    collection = FakeCollection()
    session = FakeSession()
    value = _binding()

    created = DeputyPrincipalBindingRegistry.create(
        value,
        collection,
        session=session,
    )
    replay = DeputyPrincipalBindingRegistry.create(
        value,
        collection,
        session=session,
    )
    by_principal = DeputyPrincipalBindingRegistry.resolve_by_principal(
        "tenant-a",
        "principal-1",
        collection,
        session=session,
    )
    by_deputy = DeputyPrincipalBindingRegistry.resolve_by_deputy(
        "tenant-a",
        "deputy-1",
        collection,
        session=session,
    )

    assert created == value
    assert replay == value
    assert by_principal == value
    assert by_deputy == value
    assert len(collection.docs) == 1
    assert sum(call[0] == "insert_one" for call in collection.calls) == 1
    assert all(
        call[1] is session
        for call in collection.calls
        if call[0] in {"find_one", "insert_one"}
    )


def test_same_principal_different_deputy_conflicts_without_second_write() -> None:
    collection = FakeCollection()
    first = _binding("principal-1", "deputy-1")
    other = _binding("principal-1", "deputy-2")
    DeputyPrincipalBindingRegistry.create(first, collection)

    with pytest.raises(DeputyPrincipalBindingConflictError) as caught:
        DeputyPrincipalBindingRegistry.create(other, collection)

    assert caught.value.code == "L8_6B_BINDING_CONFLICT"
    assert len(collection.docs) == 1


def test_same_deputy_different_principal_conflicts_without_second_write() -> None:
    collection = FakeCollection()
    first = _binding("principal-1", "deputy-1")
    other = _binding("principal-2", "deputy-1")
    DeputyPrincipalBindingRegistry.create(first, collection)

    with pytest.raises(DeputyPrincipalBindingConflictError) as caught:
        DeputyPrincipalBindingRegistry.create(other, collection)

    assert caught.value.code == "L8_6B_BINDING_CONFLICT"
    assert len(collection.docs) == 1


def test_same_identifiers_different_binding_evidence_conflicts() -> None:
    collection = FakeCollection()
    first = _binding()
    changed = DeputyPrincipalBinding.from_deputy(
        principal_id="principal-1",
        deputy=_deputy(),
        bound_at=NOW,
        evidence_reference="different-binding-evidence",
    )
    DeputyPrincipalBindingRegistry.create(first, collection)

    with pytest.raises(DeputyPrincipalBindingConflictError) as caught:
        DeputyPrincipalBindingRegistry.create(changed, collection)

    assert caught.value.code == "L8_6B_BINDING_CONFLICT"
    assert len(collection.docs) == 1


def test_preindex_inconsistent_natural_keys_reject_instead_of_exact_replay() -> None:
    """Legacy duplicate-key drift cannot short-circuit through one exact side."""
    collection = FakeCollection()
    exact = _binding("principal-1", "deputy-1")
    conflicting = _binding("principal-2", "deputy-1")
    collection.docs = [
        deepcopy(conflicting.to_dict()),
        deepcopy(exact.to_dict()),
    ]

    with pytest.raises(DeputyPrincipalBindingConflictError) as caught:
        DeputyPrincipalBindingRegistry.create(exact, collection)

    assert caught.value.code == "L8_6B_BINDING_CONFLICT"
    assert len(collection.docs) == 2


def test_foreign_tenant_is_absence_and_never_cross_resolves() -> None:
    collection = FakeCollection()
    DeputyPrincipalBindingRegistry.create(_binding(), collection)

    with pytest.raises(DeputyPrincipalBindingNotFoundError):
        DeputyPrincipalBindingRegistry.resolve_by_principal(
            "tenant-b",
            "principal-1",
            collection,
        )
    with pytest.raises(DeputyPrincipalBindingNotFoundError):
        DeputyPrincipalBindingRegistry.resolve_by_deputy(
            "tenant-b",
            "deputy-1",
            collection,
        )


def test_corrupt_persisted_fingerprint_and_shape_fail_closed() -> None:
    collection = FakeCollection()
    DeputyPrincipalBindingRegistry.create(_binding(), collection)

    collection.docs[0]["fingerprint"] = "f" * 128
    with pytest.raises(DeputyPrincipalBindingPersistedRecordInvalidError):
        DeputyPrincipalBindingRegistry.resolve_by_principal(
            "tenant-a",
            "principal-1",
            collection,
        )

    collection = FakeCollection()
    DeputyPrincipalBindingRegistry.create(_binding(), collection)
    collection.docs[0]["unexpected"] = "drift"
    with pytest.raises(DeputyPrincipalBindingPersistedRecordInvalidError):
        DeputyPrincipalBindingRegistry.resolve_by_deputy(
            "tenant-a",
            "deputy-1",
            collection,
        )


def test_registry_exposes_no_update_delete_rebind_or_financial_surface() -> None:
    assert not hasattr(DeputyPrincipalBindingRegistry, "update")
    assert not hasattr(DeputyPrincipalBindingRegistry, "delete")
    assert not hasattr(DeputyPrincipalBindingRegistry, "rebind")
    assert not hasattr(DeputyPrincipalBindingRegistry, "compare_and_swap")

    keys = set(_binding().to_dict())
    for forbidden in {
        "permission",
        "role_id",
        "queue",
        "invoice",
        "payment",
        "settlement",
        "bank_execution",
        "provider_execution",
    }:
        assert forbidden not in keys

    assert PRODUCTION_VERSION == (
        "v1.0.3-L8-6B-DEPUTY-PRINCIPAL-BINDING-REGISTRY"
    )
    assert VERSION == (
        "v1.0.2-L8-6B-DEPUTY-PRINCIPAL-BINDING-REGISTRY-CERT"
    )


# ARTIFACT: test_deputy_principal_binding_registry.py
# VERSION: v1.0.2-L8-6B-DEPUTY-PRINCIPAL-BINDING-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct immutable binding persistence/resolution certificate only
# TENANT POSTURE: exact tenant/principal and tenant/deputy scope only
# FAIL-CLOSED POSTURE: conflict, corruption, absence, and scope drift reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
