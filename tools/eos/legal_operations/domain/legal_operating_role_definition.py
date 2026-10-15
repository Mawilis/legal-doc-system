"""TITLE: WILSY OS Legal Operating Role Definition
VERSION: v1.0.0-CX27-R2-LEGAL-OPERATING-ROLE-DEFINITION
ARTIFACT: tools/eos/legal_operations/domain/legal_operating_role_definition.py
AUTHORITY: Tenant-defined organizational operating-role definition only; no IAM or execution authority.
EPITOME: Represent one immutable revision of one tenant-defined Legal operating role.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_operating_role_definition.py
CLASSIFICATION: EMERGING CANONICAL
TENANT BOUNDARY: Exact explicit non-pseudo tenant identity only.
SECURITY / PRIVACY: Opaque identifiers and deterministic SHA3-512 fingerprints; fail closed on malformed input.
IDEMPOTENCY: Pure immutable value object; persistence/replay authority NONE.
TRANSACTION OWNERSHIP: NONE.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
CERTIFICATION / UPDATE DATE: 2026-10-13
CHANGELOG: v1.0.0-CX27-R2-LEGAL-OPERATING-ROLE-DEFINITION establishes the CX27 tenant-defined Legal operating-role pure-domain contract.

"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Final, Mapping, NoReturn, cast

VERSION: Final[str] = "v1.0.0-CX27-R2-LEGAL-OPERATING-ROLE-DEFINITION"
SCHEMA: Final[str] = "WILSY-LEGAL-OPERATING-ROLE-DEFINITION/V1"

_HEX_128 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "root", "*"})


class LegalOperatingRoleDefinitionError(ValueError):
    """Stable fail-closed validation error for operating-role definitions."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _fail(code: str) -> NoReturn:
    raise LegalOperatingRoleDefinitionError(code)


def _text(name: str, value: object, limit: int) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(ord(ch) < 32 for ch in value)
    ):
        _fail(f"CX27_R2_{name.upper()}_INVALID")
    return value


def _optional_text(name: str, value: object, limit: int) -> str | None:
    if value is None:
        return None
    return _text(name, value, limit)


def _tenant(value: object) -> str:
    tenant = _text("tenant_id", value, 160)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("CX27_R2_TENANT_ID_INVALID")
    return tenant


def _revision(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        _fail("CX27_R2_ROLE_REVISION_INVALID")
    return value


def _when(name: str, value: object) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(f"CX27_R2_{name.upper()}_INVALID")
    return value.astimezone(timezone.utc)


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or not _HEX_128.fullmatch(value):
        _fail(f"CX27_R2_{name.upper()}_INVALID")
    return value


def _optional_fingerprint(name: str, value: object) -> str | None:
    if value is None:
        return None
    return _fingerprint(name, value)


@dataclass(frozen=True, slots=True)
class LegalOperatingRoleDefinition:
    """One immutable tenant-defined operating-role revision.

    This value owns organizational role-definition truth only. It does not grant
    an IAM role, permission, business role, matter role, professional capacity,
    work assignment, supervision, entitlement, billing authority, or financial
    execution authority.
    """

    tenant_id: str
    operating_role_id: str
    role_revision: int
    display_name: str
    description: str | None
    effective_from: datetime
    supersedes_fingerprint: str | None = None
    schema: str = SCHEMA
    role_definition_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        tenant = _tenant(self.tenant_id)
        role_id = _text("operating_role_id", self.operating_role_id, 200)
        revision = _revision(self.role_revision)
        display = _text("display_name", self.display_name, 200)
        description = _optional_text("description", self.description, 2000)
        effective = _when("effective_from", self.effective_from)
        predecessor = _optional_fingerprint(
            "supersedes_fingerprint",
            self.supersedes_fingerprint,
        )

        if revision == 1 and predecessor is not None:
            _fail("CX27_R2_FIRST_REVISION_SUPERSEDES_FORBIDDEN")
        if revision > 1 and predecessor is None:
            _fail("CX27_R2_LATER_REVISION_SUPERSEDES_REQUIRED")
        if self.schema != SCHEMA or self.role_definition_version != VERSION:
            _fail("CX27_R2_SCHEMA_VERSION_INVALID")

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "operating_role_id", role_id)
        object.__setattr__(self, "role_revision", revision)
        object.__setattr__(self, "display_name", display)
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "effective_from", effective)
        object.__setattr__(self, "supersedes_fingerprint", predecessor)

        computed = self._compute_fingerprint()
        if self.fingerprint:
            supplied = _fingerprint("fingerprint", self.fingerprint)
            if not hmac.compare_digest(supplied, computed):
                _fail("CX27_R2_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", computed)

    def semantic_dict(self) -> dict[str, object]:
        """Return the exact deterministic semantic fingerprint payload."""
        return {
            "schema": self.schema,
            "role_definition_version": self.role_definition_version,
            "tenant_id": self.tenant_id,
            "operating_role_id": self.operating_role_id,
            "role_revision": self.role_revision,
            "display_name": self.display_name,
            "description": self.description,
            "effective_from": self.effective_from.isoformat(),
            "supersedes_fingerprint": self.supersedes_fingerprint,
        }

    def _compute_fingerprint(self) -> str:
        payload = json.dumps(
            self.semantic_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha3_512(payload).hexdigest()

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact immutable snapshot including its fingerprint."""
        return {**self.semantic_dict(), "fingerprint": self.fingerprint}

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalOperatingRoleDefinition":
        """Strictly hydrate one exact immutable snapshot and verify fingerprint."""
        expected = {
            "schema", "role_definition_version", "tenant_id",
            "operating_role_id", "role_revision", "display_name",
            "description", "effective_from", "supersedes_fingerprint",
            "fingerprint",
        }
        if set(payload) != expected:
            _fail("CX27_R2_PAYLOAD_SCHEMA_INVALID")

        raw_time = payload["effective_from"]
        if not isinstance(raw_time, str):
            _fail("CX27_R2_EFFECTIVE_FROM_INVALID")
        try:
            effective = datetime.fromisoformat(raw_time)
        except ValueError:
            _fail("CX27_R2_EFFECTIVE_FROM_INVALID")

        return cls(
            schema=cast(str, payload["schema"]),
            role_definition_version=cast(str, payload["role_definition_version"]),
            tenant_id=cast(str, payload["tenant_id"]),
            operating_role_id=cast(str, payload["operating_role_id"]),
            role_revision=cast(int, payload["role_revision"]),
            display_name=cast(str, payload["display_name"]),
            description=cast(str | None, payload["description"]),
            effective_from=effective,
            supersedes_fingerprint=cast(str | None, payload["supersedes_fingerprint"]),
            fingerprint=cast(str, payload["fingerprint"]),
        )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalOperatingRoleDefinition",
    "LegalOperatingRoleDefinitionError",
]

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: tools/eos/legal_operations/domain/legal_operating_role_definition.py
# VERSION: v1.0.0-CX27-R2-LEGAL-OPERATING-ROLE-DEFINITION
# POSTURE: FAIL-CLOSED
# AUTHORITY BOUNDARY: tenant-defined operating-role definition only; no IAM, assignment, supervision, or financial authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
