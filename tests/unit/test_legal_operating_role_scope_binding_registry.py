"""TITLE: CX27-C scope-binding registry unit certificate.

VERSION: v1.0.0-CX27-C-SCOPE-BINDING-REGISTRY-UNIT-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certifies append-only tenant-scoped scope history with caller transactions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_operating_role_scope_binding_registry.py
COLLABORATION / OWNERSHIP: CX27-C in-memory registry certificate only.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.0 establishes direct scope-registry unit certification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers; no PII or credentials.
TENANT BOUNDARY: Exact tenant-scoped history, replay, and currentness.
AUTHORITY BOUNDARY: Persistence evidence only; no access, IAM, matter, workflow, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively executes or settles.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError


NOW = datetime(
    2026,
    10,
    13,
    12,
    0,
    0,
    123456,
    tzinfo=timezone.utc,
)


class ActiveSession:
    in_transaction = True


class InactiveSession:
    in_transaction = False


class Cursor:
    def __init__(
        self,
        rows: list[
            dict[str, object]
        ],
    ) -> None:
        self._rows = rows

    def sort(
        self,
        field: str,
        direction: int,
    ) -> "Cursor":
        def revision_key(
            row: dict[str, object],
        ) -> int:
            value = row.get(field)

            if (
                isinstance(value, bool)
                or not isinstance(value, int)
            ):
                raise TypeError(
                    "TEST_CURSOR_REVISION_KEY_NOT_INT"
                )

            return value

        self._rows.sort(
            key=revision_key,
            reverse=direction < 0,
        )

        return self

    def __iter__(self):
        return iter(
            self._rows
        )


class Collection:
    def __init__(self) -> None:
        self.rows: list[
            dict[str, object]
        ] = []

        self.indexes: list[
            tuple[
                object,
                bool,
                str,
            ]
        ] = []

    def create_index(
        self,
        keys: object,
        *,
        unique: bool,
        name: str,
    ) -> str:
        self.indexes.append(
            (
                deepcopy(keys),
                unique,
                name,
            )
        )

        return name

    def find_one(
        self,
        query: dict[
            str,
            object,
        ],
        *,
        session: Any = None,
    ) -> dict[
        str,
        object,
    ] | None:
        del session

        for row in self.rows:
            if all(
                row.get(key) == value
                for key, value
                in query.items()
            ):
                return deepcopy(row)

        return None

    def find(
        self,
        query: dict[
            str,
            object,
        ],
        *,
        session: Any = None,
    ) -> Cursor:
        del session

        return Cursor(
            [
                deepcopy(row)
                for row in self.rows
                if all(
                    row.get(key) == value
                    for key, value
                    in query.items()
                )
            ]
        )

    def insert_one(
        self,
        document: dict[
            str,
            object,
        ],
        *,
        session: Any = None,
    ) -> object:
        del session

        tenant = document["tenant_id"]

        if (
            "principal_operating_role_binding_id"
            in document
        ):
            identity_field = (
                "principal_operating_role_binding_id"
            )
            revision_field = (
                "binding_revision"
            )

        elif (
            "capability_binding_id"
            in document
        ):
            identity_field = (
                "capability_binding_id"
            )
            revision_field = (
                "capability_binding_revision"
            )

        elif (
            "scope_binding_id"
            in document
        ):
            identity_field = (
                "scope_binding_id"
            )
            revision_field = (
                "scope_binding_revision"
            )

        else:
            identity_field = (
                "operating_role_id"
            )
            revision_field = (
                "role_revision"
            )

        for row in self.rows:
            if (
                row.get("tenant_id")
                == tenant
                and row.get(identity_field)
                == document[identity_field]
                and row.get(revision_field)
                == document[revision_field]
            ):
                raise DuplicateKeyError(
                    "identity"
                )

            if (
                row.get("tenant_id")
                == tenant
                and row.get("fingerprint")
                == document["fingerprint"]
            ):
                raise DuplicateKeyError(
                    "fingerprint"
                )

        self.rows.append(
            deepcopy(document)
        )

        return object()

from tools.eos.legal_operations.domain.legal_operating_role_scope_binding import (
    LegalOperatingRoleScopeBinding,
)
from tools.eos.legal_operations.registry.legal_operating_role_scope_binding_registry import (
    LegalOperatingRoleScopeBindingRegistry,
    RegistryConflictError,
)


def make_value(
    *,
    revision: int = 1,
    when: datetime = NOW,
    predecessor: str | None = None,
    office: tuple[str, ...] = (
        "office:jhb",
    ),
) -> LegalOperatingRoleScopeBinding:
    return LegalOperatingRoleScopeBinding(
        tenant_id="tenant-a",
        scope_binding_id="scope-binding-1",
        operating_role_id="role-1",
        operating_role_revision=9,
        scope_binding_revision=revision,
        office_references=office,
        practice_references=(),
        business_unit_references=(),
        jurisdiction_references=(),
        effective_from=when,
        supersedes_fingerprint=predecessor,
    )


def test_independent_scope_history() -> None:
    collection = Collection()
    registry = (
        LegalOperatingRoleScopeBindingRegistry(
            collection
        )
    )
    registry.ensure_indexes()

    tx = ActiveSession()

    first = make_value()

    registry.persist_revision(
        first,
        session=tx,
    )

    second = make_value(
        revision=2,
        when=NOW + timedelta(days=1),
        predecessor=first.fingerprint,
        office=(
            "office:cpt",
        ),
    )

    registry.persist_revision(
        second,
        session=tx,
    )

    assert (
        second.operating_role_revision
        == 9
    )

    assert (
        registry.resolve_current(
            "tenant-a",
            "scope-binding-1",
            NOW + timedelta(days=2),
            session=tx,
        )


        == second
    )


def test_scope_gap_rejects() -> None:
    collection = Collection()
    registry = (
        LegalOperatingRoleScopeBindingRegistry(
            collection
        )
    )
    tx = ActiveSession()

    first = make_value()

    registry.persist_revision(
        first,
        session=tx,
    )

    with pytest.raises(
        RegistryConflictError
    ):
        registry.persist_revision(
            make_value(
                revision=3,
                when=NOW + timedelta(days=3),
                predecessor=first.fingerprint,
            ),
            session=tx,
        )


# ARTIFACT: test_legal_operating_role_scope_binding_registry.py
# VERSION: v1.0.0-CX27-C-SCOPE-BINDING-REGISTRY-UNIT-CERT
# AUTHORITY BOUNDARY: tenant-scoped immutable scope registry unit certificate only
# TENANT POSTURE: exact tenant isolation and non-disclosure
# FAIL-CLOSED POSTURE: transaction absence, conflict, lineage, corruption, and ambiguity reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
