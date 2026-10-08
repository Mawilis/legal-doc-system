"""
TITLE: WILSY OS Shared Record Scope Authority Domain
VERSION: v1.0.0-RECORD-SCOPE-AUTHORITY
AUTHORITY:
    Immutable source-bound relationship-scope evidence only.
EPITOME:
    Establishes the shared WILSY OS record relationship-scope primitive used
    by CRM, HR, Legal Operations and future governed record domains.

    The domain answers only what relationship scope has already been proven
    for one principal and one record inside one exact tenant. It does not
    authenticate, authorize, grant permissions, assign business roles,
    establish tenant membership, establish entitlement, bypass sensitivity,
    mutate records, execute workflow commands or persist evidence.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/record_scope_authority.py

RESEARCH BASIS:
    - Apollo record ownership, assignment and record-operation boundaries.
    - Salesforce ownership, hierarchy, team, territory and sharing patterns.
    - HubSpot own/team/all visibility patterns.
    - WILSY Legal immutable principal-to-record visibility evidence.
    - WILSY tenant authorization exact principal/tenant authority composition.
    - WILSY HR restricted sensitivity categories remain independent.

RELATIONSHIP SCOPE:
    SELF
    OWN
    ASSIGNED
    SHARED
    TEAM
    REPORTING_LINE
    DEPARTMENT
    TERRITORY
    BUSINESS_UNIT
    TENANT

SENSITIVITY BOUNDARY:
    RESTRICTED is deliberately not a relationship scope. Existing HR
    EMPLOYEE_RELATIONS_RESTRICTED, PERFORMANCE_RESTRICTED and
    SEPARATION_RESTRICTED classifications remain independent authorization
    conjuncts. Broad relationship scope never pierces sensitive data by itself.

TENANT BOUNDARY:
    Evidence can exist only when principal tenant and record tenant are exact,
    explicit, non-pseudo and identical. Cross-tenant scope is impossible.

AUTHORITY BOUNDARY:
    Scope evidence is not authorization. Effective access still requires
    authentication, ACTIVE membership, eligible business role, canonical
    permission, tenant entitlement where applicable, sensitivity clearance,
    operation preconditions and any additional domain-specific authority.

AI BOUNDARY:
    Scores, intent, inference, recommendations and generated content cannot
    create or widen record-scope evidence.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.

MUTATION BOUNDARY:
    Pure immutable value domain. No persistence, HTTP, transaction, workflow,
    sharing, assignment or lifecycle mutation authority.

CHANGELOG:
    2026-10-06 v1.0.0 establishes the researched shared record-scope contract.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import hmac
import json
import unicodedata
from typing import Any, Final, cast


RECORD_SCOPE_AUTHORITY_VERSION: Final[str] = (
    "v1.0.0-RECORD-SCOPE-AUTHORITY"
)

RECORD_SCOPE_AUTHORITY_SCHEMA: Final[str] = (
    "WILSY-RECORD-SCOPE-AUTHORITY/V1"
)

_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {
        "default",
        "global",
        "root",
        "*",
        "master",
        "global_root",
        "sovereign_root",
        "wilsy-sovereign-root",
    }
)

_LOWER_HEX: Final[frozenset[str]] = frozenset(
    "0123456789abcdef"
)


class RecordScopeEvidenceError(ValueError):
    """Raised when record-scope evidence fails closed."""


class RecordScope(str, Enum):
    """Closed shared WILSY OS relationship-scope vocabulary."""

    SELF = "SELF"
    OWN = "OWN"
    ASSIGNED = "ASSIGNED"
    SHARED = "SHARED"
    TEAM = "TEAM"
    REPORTING_LINE = "REPORTING_LINE"
    DEPARTMENT = "DEPARTMENT"
    TERRITORY = "TERRITORY"
    BUSINESS_UNIT = "BUSINESS_UNIT"
    TENANT = "TENANT"


class RecordAccessBasis(str, Enum):
    """Closed source basis corresponding exactly to one relationship scope."""

    SUBJECT_SELF = "SUBJECT_SELF"
    RECORD_OWNER = "RECORD_OWNER"
    EXPLICIT_ASSIGNMENT = "EXPLICIT_ASSIGNMENT"
    EXPLICIT_SHARE = "EXPLICIT_SHARE"
    TEAM_MEMBERSHIP = "TEAM_MEMBERSHIP"
    REPORTING_HIERARCHY = "REPORTING_HIERARCHY"
    DEPARTMENT_MEMBERSHIP = "DEPARTMENT_MEMBERSHIP"
    TERRITORY_ASSIGNMENT = "TERRITORY_ASSIGNMENT"
    BUSINESS_UNIT_MEMBERSHIP = "BUSINESS_UNIT_MEMBERSHIP"
    TENANT_ELEVATED_AUTHORITY = "TENANT_ELEVATED_AUTHORITY"


_BASIS_SCOPE: Final[
    dict[RecordAccessBasis, RecordScope]
] = {
    RecordAccessBasis.SUBJECT_SELF:
        RecordScope.SELF,
    RecordAccessBasis.RECORD_OWNER:
        RecordScope.OWN,
    RecordAccessBasis.EXPLICIT_ASSIGNMENT:
        RecordScope.ASSIGNED,
    RecordAccessBasis.EXPLICIT_SHARE:
        RecordScope.SHARED,
    RecordAccessBasis.TEAM_MEMBERSHIP:
        RecordScope.TEAM,
    RecordAccessBasis.REPORTING_HIERARCHY:
        RecordScope.REPORTING_LINE,
    RecordAccessBasis.DEPARTMENT_MEMBERSHIP:
        RecordScope.DEPARTMENT,
    RecordAccessBasis.TERRITORY_ASSIGNMENT:
        RecordScope.TERRITORY,
    RecordAccessBasis.BUSINESS_UNIT_MEMBERSHIP:
        RecordScope.BUSINESS_UNIT,
    RecordAccessBasis.TENANT_ELEVATED_AUTHORITY:
        RecordScope.TENANT,
}

_DURABLE_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "version",
    "tenant_id",
    "principal_id",
    "resource_type",
    "resource_id",
    "scope",
    "basis",
    "source_reference",
    "source_revision",
    "source_fingerprint",
    "issued_at",
    "fingerprint",
)


def _exact_text(
    name: str,
    value: object,
) -> str:
    """Require exact non-empty NFC text with no trimming inference."""

    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        raise RecordScopeEvidenceError(
            f"RECORD_SCOPE_{name.upper()}_INVALID"
        )

    normalized = unicodedata.normalize(
        "NFC",
        value,
    )

    if (
        normalized != value
        or not normalized
        or any(
            ord(character) < 32
            for character in normalized
        )
    ):
        raise RecordScopeEvidenceError(
            f"RECORD_SCOPE_{name.upper()}_INVALID"
        )

    return normalized


def _tenant(value: object) -> str:
    """Require one explicit non-pseudo tenant identity."""

    tenant = _exact_text(
        "tenant_id",
        value,
    )

    if tenant.casefold() in _FORBIDDEN_TENANTS:
        raise RecordScopeEvidenceError(
            "RECORD_SCOPE_TENANT_ID_INVALID"
        )

    return tenant


def _source_revision(value: object) -> int:
    """Require a non-negative source revision; booleans are invalid."""

    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
    ):
        raise RecordScopeEvidenceError(
            "RECORD_SCOPE_SOURCE_REVISION_INVALID"
        )

    return value


def _digest(
    name: str,
    value: object,
) -> str:
    """Require canonical lowercase SHA3-512 hexadecimal shape."""

    if (
        not isinstance(value, str)
        or len(value) != 128
        or any(
            character not in _LOWER_HEX
            for character in value
        )
    ):
        raise RecordScopeEvidenceError(
            f"RECORD_SCOPE_{name.upper()}_INVALID"
        )

    return value


def _issued_at(value: object) -> datetime:
    """Require an aware datetime and normalize it exactly to UTC."""

    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise RecordScopeEvidenceError(
            "RECORD_SCOPE_ISSUED_AT_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


def _scope(value: object) -> RecordScope:
    """Hydrate one exact closed relationship scope."""

    try:
        return RecordScope(value)
    except (TypeError, ValueError) as error:
        raise RecordScopeEvidenceError(
            "RECORD_SCOPE_SCOPE_INVALID"
        ) from error


def _basis(value: object) -> RecordAccessBasis:
    """Hydrate one exact closed access basis."""

    try:
        return RecordAccessBasis(value)
    except (TypeError, ValueError) as error:
        raise RecordScopeEvidenceError(
            "RECORD_SCOPE_BASIS_INVALID"
        ) from error


def _utc_text(value: datetime) -> str:
    """Serialize one UTC datetime without losing microseconds."""

    return (
        value.astimezone(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _fingerprint_payload(
    *,
    tenant_id: str,
    principal_id: str,
    resource_type: str,
    resource_id: str,
    scope: RecordScope,
    basis: RecordAccessBasis,
    source_reference: str,
    source_revision: int,
    source_fingerprint: str,
    issued_at: datetime,
) -> dict[str, object]:
    """Build the exact semantic payload used for SHA3-512 evidence identity."""

    return {
        "schema": RECORD_SCOPE_AUTHORITY_SCHEMA,
        "version": RECORD_SCOPE_AUTHORITY_VERSION,
        "tenant_id": tenant_id,
        "principal_id": principal_id,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "scope": scope.value,
        "basis": basis.value,
        "source_reference": source_reference,
        "source_revision": source_revision,
        "source_fingerprint": source_fingerprint,
        "issued_at": _utc_text(issued_at),
    }


def _fingerprint(
    *,
    tenant_id: str,
    principal_id: str,
    resource_type: str,
    resource_id: str,
    scope: RecordScope,
    basis: RecordAccessBasis,
    source_reference: str,
    source_revision: int,
    source_fingerprint: str,
    issued_at: datetime,
) -> str:
    """Return deterministic SHA3-512 over canonical semantic coordinates."""

    payload = _fingerprint_payload(
        tenant_id=tenant_id,
        principal_id=principal_id,
        resource_type=resource_type,
        resource_id=resource_id,
        scope=scope,
        basis=basis,
        source_reference=source_reference,
        source_revision=source_revision,
        source_fingerprint=source_fingerprint,
        issued_at=issued_at,
    )

    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha3_512(
        encoded
    ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
)
class RecordScopeEvidence:
    """Immutable exact-tenant relationship-scope evidence.

    Authority:
        Represents already-proven relationship scope only.

    Tenant scope:
        Exactly one explicit tenant shared by the principal and record.

    Mutation semantics:
        Immutable. New upstream relationship evidence must issue a new value.

    Security:
        Contains no permission, role, membership, entitlement, sensitivity,
        workflow, AI, persistence or financial execution authority.
    """

    tenant_id: str
    principal_id: str
    resource_type: str
    resource_id: str
    scope: RecordScope
    basis: RecordAccessBasis
    source_reference: str
    source_revision: int
    source_fingerprint: str
    issued_at: datetime
    fingerprint: str

    @classmethod
    def issue(
        cls,
        *,
        principal_tenant_id: str,
        record_tenant_id: str,
        principal_id: str,
        resource_type: str,
        resource_id: str,
        scope: RecordScope | str,
        basis: RecordAccessBasis | str,
        source_reference: str,
        source_revision: int,
        source_fingerprint: str,
        issued_at: datetime,
    ) -> "RecordScopeEvidence":
        """Issue one immutable scope-evidence value from explicit source facts.

        This factory does not discover ownership, membership, hierarchy,
        assignment, team, territory or tenant authority. The caller must
        provide source-bound evidence coordinates already established by
        their sovereign domain.
        """

        principal_tenant = _tenant(
            principal_tenant_id
        )

        record_tenant = _tenant(
            record_tenant_id
        )

        if principal_tenant != record_tenant:
            raise RecordScopeEvidenceError(
                "RECORD_SCOPE_CROSS_TENANT_FORBIDDEN"
            )

        canonical_principal = _exact_text(
            "principal_id",
            principal_id,
        )

        canonical_resource_type = _exact_text(
            "resource_type",
            resource_type,
        )

        canonical_resource_id = _exact_text(
            "resource_id",
            resource_id,
        )

        canonical_scope = _scope(
            scope
        )

        canonical_basis = _basis(
            basis
        )

        if (
            _BASIS_SCOPE[canonical_basis]
            is not canonical_scope
        ):
            raise RecordScopeEvidenceError(
                "RECORD_SCOPE_BASIS_SCOPE_MISMATCH"
            )

        canonical_reference = _exact_text(
            "source_reference",
            source_reference,
        )

        canonical_revision = _source_revision(
            source_revision
        )

        canonical_source_fingerprint = _digest(
            "source_fingerprint",
            source_fingerprint,
        )

        canonical_issued_at = _issued_at(
            issued_at
        )

        digest = _fingerprint(
            tenant_id=principal_tenant,
            principal_id=canonical_principal,
            resource_type=canonical_resource_type,
            resource_id=canonical_resource_id,
            scope=canonical_scope,
            basis=canonical_basis,
            source_reference=canonical_reference,
            source_revision=canonical_revision,
            source_fingerprint=canonical_source_fingerprint,
            issued_at=canonical_issued_at,
        )

        return cls(
            tenant_id=principal_tenant,
            principal_id=canonical_principal,
            resource_type=canonical_resource_type,
            resource_id=canonical_resource_id,
            scope=canonical_scope,
            basis=canonical_basis,
            source_reference=canonical_reference,
            source_revision=canonical_revision,
            source_fingerprint=canonical_source_fingerprint,
            issued_at=canonical_issued_at,
            fingerprint=digest,
        )

    def to_dict(
        self,
    ) -> dict[str, object]:
        """Serialize the exact durable scope-evidence representation."""

        return {
            "schema":
                RECORD_SCOPE_AUTHORITY_SCHEMA,
            "version":
                RECORD_SCOPE_AUTHORITY_VERSION,
            "tenant_id":
                self.tenant_id,
            "principal_id":
                self.principal_id,
            "resource_type":
                self.resource_type,
            "resource_id":
                self.resource_id,
            "scope":
                self.scope.value,
            "basis":
                self.basis.value,
            "source_reference":
                self.source_reference,
            "source_revision":
                self.source_revision,
            "source_fingerprint":
                self.source_fingerprint,
            "issued_at":
                _utc_text(self.issued_at),
            "fingerprint":
                self.fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "RecordScopeEvidence":
        """Hydrate one strict durable scope-evidence representation.

        Missing fields, additional fields, malformed coordinates, semantic
        basis/scope mismatch and fingerprint drift all fail closed.
        """

        if not isinstance(payload, Mapping):
            raise RecordScopeEvidenceError(
                "RECORD_SCOPE_DOCUMENT_INVALID"
            )

        if set(payload) != set(_DURABLE_FIELDS):
            raise RecordScopeEvidenceError(
                "RECORD_SCOPE_DOCUMENT_SCHEMA_INVALID"
            )

        if (
            payload["schema"]
            != RECORD_SCOPE_AUTHORITY_SCHEMA
            or payload["version"]
            != RECORD_SCOPE_AUTHORITY_VERSION
        ):
            raise RecordScopeEvidenceError(
                "RECORD_SCOPE_DOCUMENT_IDENTITY_INVALID"
            )

        raw_issued_at = payload[
            "issued_at"
        ]

        if not isinstance(
            raw_issued_at,
            str,
        ):
            raise RecordScopeEvidenceError(
                "RECORD_SCOPE_ISSUED_AT_INVALID"
            )

        try:
            parsed_issued_at = datetime.fromisoformat(
                raw_issued_at.replace(
                    "Z",
                    "+00:00",
                )
            )
        except ValueError as error:
            raise RecordScopeEvidenceError(
                "RECORD_SCOPE_ISSUED_AT_INVALID"
            ) from error

        item = cls.issue(
            principal_tenant_id=cast(
                str,
                payload["tenant_id"],
            ),
            record_tenant_id=cast(
                str,
                payload["tenant_id"],
            ),
            principal_id=cast(
                str,
                payload["principal_id"],
            ),
            resource_type=cast(
                str,
                payload["resource_type"],
            ),
            resource_id=cast(
                str,
                payload["resource_id"],
            ),
            scope=cast(
                str,
                payload["scope"],
            ),
            basis=cast(
                str,
                payload["basis"],
            ),
            source_reference=cast(
                str,
                payload["source_reference"],
            ),
            source_revision=cast(
                int,
                payload["source_revision"],
            ),
            source_fingerprint=cast(
                str,
                payload["source_fingerprint"],
            ),
            issued_at=parsed_issued_at,
        )

        stored_fingerprint = _digest(
            "fingerprint",
            payload["fingerprint"],
        )

        if not hmac.compare_digest(
            stored_fingerprint,
            item.fingerprint,
        ):
            raise RecordScopeEvidenceError(
                "RECORD_SCOPE_FINGERPRINT_MISMATCH"
            )

        return item


__all__ = [
    "RECORD_SCOPE_AUTHORITY_SCHEMA",
    "RECORD_SCOPE_AUTHORITY_VERSION",
    "RecordAccessBasis",
    "RecordScope",
    "RecordScopeEvidence",
    "RecordScopeEvidenceError",
]

# ARTIFACT: record_scope_authority.py
# VERSION: v1.0.0-RECORD-SCOPE-AUTHORITY
# AUTHORITY BOUNDARY: immutable relationship-scope evidence only
# TENANT POSTURE: principal and record tenants must be exact and identical
# SENSITIVITY POSTURE: sensitivity remains an independent authorization conjunct
# AI AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
