"""Unit certification for append-only Issue #300 ownership evidence storage."""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth.tenant_ownership_evidence_registry import (
    TenantOwnershipEvidencePersistenceError,
    TenantOwnershipEvidenceRegistry,
    TenantOwnershipEvidenceTransactionRequiredError,
)
from tools.eos.auth.tenant_ownership_verifier import (
    TenantOwnershipVerificationError,
    VerifiedTenantOwnershipEvidence,
)


class _Session:
    def __init__(self, active: bool = True) -> None:
        self._active = active

    def in_transaction(self) -> bool:
        return self._active


class _Collection:
    def __init__(self) -> None:
        self.indexes: list[tuple[Any, ...]] = []
        self.reads = 0
        self.writes = 0

    def create_index(self, keys: Any, **kwargs: Any) -> None:
        self.indexes.append((keys, kwargs))

    def find_one(self, query: Any, **kwargs: Any) -> None:
        self.reads += 1
        return None

    def insert_one(self, document: Any, **kwargs: Any) -> None:
        self.writes += 1


def _registry() -> tuple[TenantOwnershipEvidenceRegistry, _Collection, _Collection]:
    history = _Collection()
    current = _Collection()
    return TenantOwnershipEvidenceRegistry(history, current), history, current


def test_registry_requires_both_explicit_collections() -> None:
    with pytest.raises(TenantOwnershipEvidencePersistenceError) as raised:
        TenantOwnershipEvidenceRegistry(None, object())
    assert str(raised.value) == "COLLECTION_REQUIRED"


def test_registry_indexes_are_tenant_first_and_never_ttl() -> None:
    registry, history, current = _registry()
    registry.ensure_indexes()

    assert [entry[1]["name"] for entry in history.indexes] == [
        "tenant_ownership_tenant_evidence_unique",
        "tenant_ownership_tenant_command_unique",
        "tenant_ownership_tenant_revision_unique",
    ]
    assert [entry[0][0][0] for entry in history.indexes] == [
        "tenant_id", "tenant_id", "tenant_id"
    ]
    assert current.indexes[0][0] == [("tenant_id", 1)]
    assert all("expireAfterSeconds" not in entry[1] for entry in history.indexes)


@pytest.mark.parametrize("active", [False, None])
def test_reads_require_an_already_active_caller_transaction(active: bool | None) -> None:
    registry, history, current = _registry()
    with pytest.raises(TenantOwnershipEvidenceTransactionRequiredError) as raised:
        registry.current(tenant_id="tenant-a", session=_Session(active is True if active is not None else False))
    assert str(raised.value) == "ACTIVE_TRANSACTION_REQUIRED"
    assert history.reads == current.reads == 0


def test_cross_tenant_pseudo_scope_is_rejected_before_database_read() -> None:
    registry, history, current = _registry()
    with pytest.raises(TenantOwnershipEvidencePersistenceError) as raised:
        registry.current(tenant_id="global", session=_Session())
    assert str(raised.value) == "TENANT_ID_INVALID"
    assert history.reads == current.reads == 0


def test_caller_shaped_evidence_cannot_be_appended() -> None:
    registry, history, current = _registry()
    untrusted = SimpleNamespace(request=SimpleNamespace(tenant_id="tenant-a"))

    with pytest.raises(TenantOwnershipEvidencePersistenceError) as raised:
        registry.append(
            evidence=untrusted,  # type: ignore[arg-type]
            command_id="cmd-1",
            expected_revision=0,
            session=_Session(),
        )

    assert str(raised.value) == "VERIFIED_OWNERSHIP_EVIDENCE_REQUIRED"
    assert history.reads == history.writes == current.reads == current.writes == 0


def test_public_positive_evidence_constructor_remains_unavailable() -> None:
    with pytest.raises(TenantOwnershipVerificationError) as raised:
        VerifiedTenantOwnershipEvidence()
    assert raised.value.code == "OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE"


def test_missing_transaction_is_rejected_before_untrusted_evidence_inspection() -> None:
    registry, history, current = _registry()
    with pytest.raises(TenantOwnershipEvidenceTransactionRequiredError):
        registry.append(
            evidence=object(),  # type: ignore[arg-type]
            command_id="cmd-1",
            expected_revision=0,
            session=None,
        )
    assert history.reads == history.writes == current.reads == current.writes == 0
