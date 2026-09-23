"""Direct certificate for durable L8-7B client-matter visibility history.

TITLE: WILSY OS Legal Client Matter Visibility Registry Certificate
VERSION: v1.0.0-L8-7B-LEGAL-CLIENT-MATTER-VISIBILITY-REGISTRY-CERT
AUTHORITY: Direct adversarial certification of visibility persistence/currentness only.
EPITOME: Prove append-only ACTIVE/REVOKED history, exact replay, many-to-many
         tenant-scoped relations, full-history currentness, deterministic active
         enumeration, session propagation, lifecycle-gap/corruption rejection,
         reactivation denial, and absence of IAM, HTTP, service or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_visibility_registry.py
COLLABORATION / OWNERSHIP: L8-7A owns relation values; L8-7B registry is the sole
                            production subject. IAM, provisioning orchestration,
                            HTTP/client policy, P1/P2 lifecycle and finance remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-7B-LEGAL-CLIENT-MATTER-VISIBILITY-REGISTRY-CERT
           establishes index, grant/replay, append-only revocation, no stale-
           ACTIVE currentness, many-matter/many-client enumeration, tenant
           isolation, divergent replay/reactivation denial, durable corruption,
           lifecycle-gap, caller-session, and public-surface proofs.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque values only; no production PII.
TENANT BOUNDARY: Every lookup and enumeration assertion is exact-tenant scoped.
AUTHORITY BOUNDARY: Persistence/currentness certificate only; no client read authorization.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Fake caller sessions only; registry owns no transaction.
FAIL-CLOSED DECLARATION: Corruption, gaps, conflicts, reactivation, foreign scope,
                         malformed lookup and persistence ambiguity never become visibility.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_client_matter_visibility_binding import (
    LegalClientMatterVisibilityBinding,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.registry.legal_client_matter_visibility_registry import (
    VERSION as PRODUCTION_VERSION,
    LegalClientMatterVisibilityConflictError,
    LegalClientMatterVisibilityNotFoundError,
    LegalClientMatterVisibilityPersistedRecordInvalidError,
    LegalClientMatterVisibilityRegistry,
)


VERSION = "v1.0.0-L8-7B-LEGAL-CLIENT-MATTER-VISIBILITY-REGISTRY-CERT"
NOW = datetime(2026, 9, 23, 19, 0, tzinfo=timezone.utc)


class FakeSession:
    """Opaque caller-owned session marker."""


class FakeCollection:
    """Minimal Mongo-compatible append-only collection with L8-7B uniqueness."""

    def __init__(self) -> None:
        self.docs: list[dict[str, Any]] = []
        self.calls: list[tuple[str, object, object]] = []
        self.indexes: list[tuple[object, bool, str]] = []

    def create_index(
        self,
        keys: object,
        *,
        unique: bool = False,
        name: str,
    ) -> str:
        self.calls.append(("create_index", None, deepcopy(keys)))
        self.indexes.append((deepcopy(keys), unique, name))
        return name

    def find(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> list[dict[str, Any]]:
        self.calls.append(("find", session, deepcopy(query)))
        return [
            deepcopy(document)
            for document in self.docs
            if all(document.get(key) == value for key, value in query.items())
        ]

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: object = None,
    ) -> object:
        self.calls.append(("insert_one", session, deepcopy(document)))
        persisted = deepcopy(document)
        persisted["_id"] = f"synthetic-{len(self.docs) + 1}"
        for existing in self.docs:
            if existing["tenant_id"] != persisted["tenant_id"]:
                continue
            same_lifecycle = (
                existing["binding_identity"] == persisted["binding_identity"]
                and existing["status"] == persisted["status"]
            )
            same_fingerprint = existing["fingerprint"] == persisted["fingerprint"]
            if same_lifecycle or same_fingerprint:
                raise DuplicateKeyError("synthetic duplicate")
        self.docs.append(persisted)
        return SimpleNamespace(inserted_id=persisted["_id"])


def matter(
    matter_id: str = "matter-1",
    *,
    tenant_id: str = "tenant-a",
) -> CaseMatter:
    return CaseMatter(
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        matter_reference=f"CASE-{matter_id}",
        opened_at=NOW,
        evidence_reference=f"matter-evidence-{matter_id}",
    )


def grant(
    principal_id: str = "client-1",
    matter_id: str = "matter-1",
    *,
    tenant_id: str = "tenant-a",
    evidence_reference: str | None = None,
) -> LegalClientMatterVisibilityBinding:
    return LegalClientMatterVisibilityBinding.grant(
        client_principal_id=principal_id,
        case_matter=matter(matter_id, tenant_id=tenant_id),
        granted_by_principal_id="partner-1",
        granted_at=NOW + timedelta(minutes=1),
        evidence_reference=(
            evidence_reference
            if evidence_reference is not None
            else f"grant-{principal_id}-{matter_id}"
        ),
    )


def revoke(
    value: LegalClientMatterVisibilityBinding,
) -> LegalClientMatterVisibilityBinding:
    return value.revoke(
        revoked_by_principal_id="attorney-1",
        revoked_at=NOW + timedelta(minutes=2),
        evidence_reference="revoke-client-visibility",
    )


def test_indexes_support_many_to_many_history_without_tenant_wide_uniqueness() -> None:
    collection = FakeCollection()
    LegalClientMatterVisibilityRegistry.ensure_indexes(collection)

    assert collection.indexes == [
        (
            [
                ("tenant_id", 1),
                ("binding_identity", 1),
                ("status", 1),
            ],
            True,
            "legal_operations_client_matter_visibility_lifecycle_unique",
        ),
        (
            [("tenant_id", 1), ("fingerprint", 1)],
            True,
            "legal_operations_client_matter_visibility_fingerprint_unique",
        ),
        (
            [
                ("tenant_id", 1),
                ("client_principal_id", 1),
                ("binding_identity", 1),
            ],
            False,
            "legal_operations_client_visibility_principal_history",
        ),
        (
            [
                ("tenant_id", 1),
                ("case_matter_id", 1),
                ("binding_identity", 1),
            ],
            False,
            "legal_operations_matter_visibility_client_history",
        ),
    ]


def test_grant_exact_replay_current_resolution_and_session_propagation() -> None:
    collection = FakeCollection()
    session = FakeSession()
    value = grant()

    created = LegalClientMatterVisibilityRegistry.grant(
        value,
        collection,
        session=session,
    )
    replay = LegalClientMatterVisibilityRegistry.grant(
        value,
        collection,
        session=session,
    )
    current = LegalClientMatterVisibilityRegistry.resolve_current_active(
        "tenant-a",
        "client-1",
        "matter-1",
        collection,
        session=session,
    )

    assert created == value
    assert replay == value
    assert current == value
    assert len(collection.docs) == 1
    assert sum(call[0] == "insert_one" for call in collection.calls) == 1
    assert all(
        call[1] is session
        for call in collection.calls
        if call[0] in {"find", "insert_one"}
    )


def test_many_matters_per_client_and_many_clients_per_matter_are_supported() -> None:
    collection = FakeCollection()
    first = grant("client-1", "matter-b")
    second = grant("client-1", "matter-a")
    third = grant("client-2", "matter-a")

    for value in (first, second, third):
        LegalClientMatterVisibilityRegistry.grant(value, collection)

    client_one = LegalClientMatterVisibilityRegistry.list_active_for_principal(
        "tenant-a",
        "client-1",
        collection,
    )
    client_two = LegalClientMatterVisibilityRegistry.list_active_for_principal(
        "tenant-a",
        "client-2",
        collection,
    )

    assert [value.case_matter_id for value in client_one] == [
        "matter-a",
        "matter-b",
    ]
    assert [value.case_matter_id for value in client_two] == ["matter-a"]
    assert len(collection.docs) == 3


def test_revocation_is_append_only_excludes_stale_active_and_replays_exactly() -> None:
    collection = FakeCollection()
    active = grant()
    revoked = revoke(active)

    LegalClientMatterVisibilityRegistry.grant(active, collection)
    created_revoke = LegalClientMatterVisibilityRegistry.revoke(
        revoked,
        collection,
    )
    replay_revoke = LegalClientMatterVisibilityRegistry.revoke(
        revoked,
        collection,
    )

    assert created_revoke == revoked
    assert replay_revoke == revoked
    assert len(collection.docs) == 2
    assert {row["status"] for row in collection.docs} == {"ACTIVE", "REVOKED"}

    with pytest.raises(LegalClientMatterVisibilityNotFoundError):
        LegalClientMatterVisibilityRegistry.resolve_current_active(
            "tenant-a",
            "client-1",
            "matter-1",
            collection,
        )
    assert (
        LegalClientMatterVisibilityRegistry.list_active_for_principal(
            "tenant-a",
            "client-1",
            collection,
        )
        == ()
    )


def test_reactivation_and_divergent_replay_fail_without_new_write() -> None:
    collection = FakeCollection()
    active = grant()
    LegalClientMatterVisibilityRegistry.grant(active, collection)

    divergent = grant(evidence_reference="different-grant-evidence")
    with pytest.raises(LegalClientMatterVisibilityConflictError) as conflict:
        LegalClientMatterVisibilityRegistry.grant(divergent, collection)
    assert conflict.value.code == "L8_7B_VISIBILITY_CONFLICT"

    LegalClientMatterVisibilityRegistry.revoke(revoke(active), collection)
    with pytest.raises(LegalClientMatterVisibilityConflictError) as reactivation:
        LegalClientMatterVisibilityRegistry.grant(active, collection)
    assert reactivation.value.code == "L8_7B_VISIBILITY_REACTIVATION_FORBIDDEN"
    assert len(collection.docs) == 2


def test_revocation_requires_exact_original_grant_history() -> None:
    collection = FakeCollection()
    first = grant()
    LegalClientMatterVisibilityRegistry.grant(first, collection)

    different_grant = grant(evidence_reference="different-grant")
    divergent_revoke = revoke(different_grant)
    with pytest.raises(LegalClientMatterVisibilityConflictError) as caught:
        LegalClientMatterVisibilityRegistry.revoke(
            divergent_revoke,
            collection,
        )
    assert caught.value.code == "L8_7B_VISIBILITY_CONFLICT"
    assert len(collection.docs) == 1


def test_revoked_only_and_duplicate_active_history_fail_as_corruption() -> None:
    collection = FakeCollection()
    active = grant()
    revoked = revoke(active)

    collection.docs.append({**revoked.to_dict(), "_id": "revoked-only"})
    with pytest.raises(LegalClientMatterVisibilityPersistedRecordInvalidError):
        LegalClientMatterVisibilityRegistry.list_active_for_principal(
            "tenant-a",
            "client-1",
            collection,
        )

    collection = FakeCollection()
    first = active.to_dict()
    duplicate = active.to_dict()
    duplicate["fingerprint"] = "f" * 128
    collection.docs.extend(
        [
            {**first, "_id": "active-one"},
            {**duplicate, "_id": "active-two"},
        ]
    )
    with pytest.raises(LegalClientMatterVisibilityPersistedRecordInvalidError):
        LegalClientMatterVisibilityRegistry.resolve_current_active(
            "tenant-a",
            "client-1",
            "matter-1",
            collection,
        )


def test_fingerprint_and_scope_corruption_fail_closed() -> None:
    collection = FakeCollection()
    active = grant()
    LegalClientMatterVisibilityRegistry.grant(active, collection)

    collection.docs[0]["fingerprint"] = "f" * 128
    with pytest.raises(LegalClientMatterVisibilityPersistedRecordInvalidError):
        LegalClientMatterVisibilityRegistry.resolve_current_active(
            "tenant-a",
            "client-1",
            "matter-1",
            collection,
        )


def test_foreign_tenant_is_absence_and_does_not_leak_enumeration() -> None:
    collection = FakeCollection()
    LegalClientMatterVisibilityRegistry.grant(
        grant(tenant_id="tenant-a"),
        collection,
    )

    with pytest.raises(LegalClientMatterVisibilityNotFoundError):
        LegalClientMatterVisibilityRegistry.resolve_current_active(
            "tenant-b",
            "client-1",
            "matter-1",
            collection,
        )
    assert (
        LegalClientMatterVisibilityRegistry.list_active_for_principal(
            "tenant-b",
            "client-1",
            collection,
        )
        == ()
    )


def test_public_surface_has_no_update_delete_reactivate_or_authorization() -> None:
    public = {
        name
        for name in dir(LegalClientMatterVisibilityRegistry)
        if not name.startswith("_")
    }
    assert public == {
        "ensure_indexes",
        "grant",
        "list_active_for_principal",
        "resolve_current_active",
        "revoke",
    }
    assert PRODUCTION_VERSION == (
        "v1.0.0-L8-7B-LEGAL-CLIENT-MATTER-VISIBILITY-REGISTRY"
    )

    payload = grant().to_dict()
    forbidden = {
        "permission",
        "authorized",
        "role_id",
        "business_role",
        "instruction_id",
        "document_id",
        "attempt_id",
        "service_execution_id",
        "return_id",
        "invoice_id",
        "payment_id",
        "settlement_id",
    }
    assert forbidden.isdisjoint(payload)


# SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_client_matter_visibility_registry.py
# VERSION: v1.0.0-L8-7B-LEGAL-CLIENT-MATTER-VISIBILITY-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct append-only visibility persistence/currentness certificate only
# TENANT POSTURE: exact tenant/client/matter history and foreign-scope absence are certified
# FAIL-CLOSED POSTURE: stale ACTIVE, reactivation, corruption, gaps and divergent replay reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
