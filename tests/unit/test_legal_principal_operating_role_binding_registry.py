"""TITLE: CX27-D principal occupancy registry unit certificate.

VERSION: v1.0.0-CX27-D-PRINCIPAL-OCCUPANCY-REGISTRY-UNIT-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certifies append-only tenant occupancy history and window projection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_principal_operating_role_binding_registry.py
COLLABORATION / OWNERSHIP: CX27-D in-memory registry certificate only.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.0 establishes direct occupancy-registry unit certification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers; no PII or credentials.
TENANT BOUNDARY: Exact tenant-scoped history, replay, currentness, and windows.
AUTHORITY BOUNDARY: Persistence evidence only; no authentication, IAM, access, workforce, matter, workflow, or financial authority.
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

from tools.eos.legal_operations.domain.legal_principal_operating_role_binding import (
    LegalPrincipalOperatingRoleBinding,
)
from tools.eos.legal_operations.registry.legal_principal_operating_role_binding_registry import (
    LegalPrincipalOperatingRoleBindingRegistry,
    RegistryConflictError,
)


FP = "a" * 128


def make_value(
    *,
    revision: int = 1,
    when: datetime = NOW,
    until: datetime | None = None,
    predecessor: str | None = None,
) -> LegalPrincipalOperatingRoleBinding:
    return LegalPrincipalOperatingRoleBinding(
        tenant_id="tenant-a",
        principal_operating_role_binding_id=(
            "principal-binding-1"
        ),
        binding_revision=revision,
        principal_id="principal-1",
        operating_role_id="role-1",
        operating_role_revision=4,
        effective_from=when,
        effective_until=until,
        source_reference=(
            f"evidence:{revision}"
        ),
        source_evidence_fingerprint=FP,
        supersedes_fingerprint=predecessor,
    )


def test_principal_currentness_and_window() -> None:
    collection = Collection()
    registry = (
        LegalPrincipalOperatingRoleBindingRegistry(
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

    assert (
        registry.list_current_for_principal(
            "tenant-a",
            "principal-1",
            NOW,
            session=tx,
        )


        == (first,)
    )

    closed = make_value(
        revision=2,
        when=NOW,
        until=NOW + timedelta(days=1),
        predecessor=first.fingerprint,
    )

    registry.persist_revision(
        closed,
        session=tx,
    )

    assert (
        registry.resolve_current(
            "tenant-a",
            "principal-binding-1",
            NOW + timedelta(days=2),
            session=tx,
        )
        is None
    )


def test_principal_gap_rejects() -> None:
    collection = Collection()
    registry = (
        LegalPrincipalOperatingRoleBindingRegistry(
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
                predecessor=first.fingerprint,
            ),
            session=tx,
        )


# ARTIFACT: test_legal_principal_operating_role_binding_registry.py
# VERSION: v1.0.0-CX27-D-PRINCIPAL-OCCUPANCY-REGISTRY-UNIT-CERT
# AUTHORITY BOUNDARY: tenant-scoped immutable occupancy registry unit certificate only
# TENANT POSTURE: exact tenant isolation and non-disclosure
# FAIL-CLOSED POSTURE: transaction absence, conflict, lineage, corruption, overlap, and ambiguity reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
