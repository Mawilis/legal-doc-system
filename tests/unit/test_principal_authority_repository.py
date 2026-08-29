# -*- coding: utf-8 -*-
"""Bounded certification for PrincipalAuthorityRepository semantics.

VERSION: v1.0.0-WILSY-PRINCIPAL-AUTHORITY-REPOSITORY-CERT
CHANGELOG: v1.0.0 certifies strict serialization, absence, duplicate, and CAS behavior.
"""
from dataclasses import dataclass
from typing import Any

import pytest

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityAlreadyExistsError,
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
    PrincipalAuthorityRevisionConflictError,
)
from tools.eos.auth.principal_status import PrincipalStatus


@dataclass
class Result:
    matched_count: int = 0


class FakeCollection:
    def __init__(self) -> None:
        self.rows: dict[str, dict[str, object]] = {}

    def create_index(self, *_args: Any, **_kwargs: Any) -> str:
        return "principal_identity_unique"

    def insert_one(self, document: dict[str, object], *, session: Any = None) -> None:
        if document["principal_id"] in self.rows:
            from pymongo.errors import DuplicateKeyError

            raise DuplicateKeyError("duplicate")
        self.rows[str(document["principal_id"])] = dict(document)

    def find_one(self, query: dict[str, object], *, session: Any = None) -> dict[str, object] | None:
        row = self.rows.get(str(query["principal_id"]))
        return dict(row) if row is not None else None

    def replace_one(self, query: dict[str, object], document: dict[str, object], *, upsert: bool, session: Any = None) -> Result:
        key = str(query["principal_id"])
        row = self.rows.get(key)
        if row is None or row.get("revision") != query["revision"]:
            return Result()
        self.rows[key] = dict(document)
        return Result(1)


def authority(status: PrincipalStatus = PrincipalStatus.ACTIVE, revision: int = 0) -> PrincipalAuthority:
    return PrincipalAuthority("principal-1", status, revision)


def typed(collection: FakeCollection) -> Any:
    """Cast the in-memory double to the injected collection boundary."""
    return collection


def test_create_get_absence_duplicate_and_exact_shape() -> None:
    collection = FakeCollection()
    PrincipalAuthorityRepository.ensure_indexes(typed(collection))
    item = authority()
    assert PrincipalAuthorityRepository.create(item, typed(collection)) == item
    assert PrincipalAuthorityRepository.get("principal-1", typed(collection)) == item
    assert set(collection.rows["principal-1"]) == {"principal_id", "status", "revision"}
    with pytest.raises(PrincipalAuthorityAlreadyExistsError):
        PrincipalAuthorityRepository.create(item, typed(collection))
    with pytest.raises(PrincipalAuthorityNotFoundError):
        PrincipalAuthorityRepository.get("missing", typed(collection))


def test_compare_and_swap_advances_exactly_and_rejects_stale() -> None:
    collection = FakeCollection()
    PrincipalAuthorityRepository.create(authority(), typed(collection))
    updated = authority(PrincipalStatus.SUSPENDED, 1)
    assert PrincipalAuthorityRepository.compare_and_swap(updated, 0, typed(collection)) == updated
    with pytest.raises(PrincipalAuthorityRevisionConflictError):
        PrincipalAuthorityRepository.compare_and_swap(authority(PrincipalStatus.ACTIVE, 1), 0, typed(collection))


def test_revoked_snapshot_survives_stale_active_and_suspended_writes() -> None:
    collection = FakeCollection()
    PrincipalAuthorityRepository.create(authority(), typed(collection))
    revoked = authority(PrincipalStatus.REVOKED, 1)
    PrincipalAuthorityRepository.compare_and_swap(revoked, 0, typed(collection))
    for stale in (authority(PrincipalStatus.ACTIVE, 1), authority(PrincipalStatus.SUSPENDED, 1)):
        with pytest.raises(PrincipalAuthorityRevisionConflictError):
            PrincipalAuthorityRepository.compare_and_swap(stale, 0, typed(collection))
    assert PrincipalAuthorityRepository.get("principal-1", typed(collection)) == revoked


def test_repository_does_not_own_transition_policy_or_extra_authority() -> None:
    assert not any(name in PrincipalAuthorityRepository.__dict__ for name in ("start_transaction", "commit", "abort", "transition"))
    assert not {"tenant_id", "roles", "permissions", "credential_id", "kind"}.intersection(PrincipalAuthority.__dataclass_fields__)


# ARTIFACT: test_principal_authority_repository.py
# VERSION: v1.0.0-WILSY-PRINCIPAL-AUTHORITY-REPOSITORY-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
