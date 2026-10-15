"""TITLE: WILSY OS Legal Operating Role Scope Binding
VERSION: v1.1.1-CX27-R3-R3-LEGAL-OPERATING-ROLE-SCOPE-BINDING
ARTIFACT: tools/eos/legal_operations/domain/legal_operating_role_scope_binding.py
AUTHORITY: Organizational operating-role scope description only; no record-access authority.
EPITOME: Bind an operating-role revision to explicit office, practice, business-unit, or jurisdiction references.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_operating_role_scope_binding.py
COLLABORATION / OWNERSHIP: CX27-C owns immutable descriptive scope-association semantics; role, IAM, matter, workflow, entitlement, and execution authorities remain external.
CLASSIFICATION: EMERGING CANONICAL
TENANT BOUNDARY: Exact explicit non-pseudo tenant identity only.
AUTHORITY BOUNDARY: Descriptive office, practice, business-unit, and jurisdiction references only; never record, client, matter, route, workflow, assignment, or supervision authority.
SECURITY / PRIVACY: Opaque identifiers and deterministic SHA3-512 fingerprints; fail closed on malformed input.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
IDEMPOTENCY: Pure immutable value object; persistence/replay authority NONE.
TRANSACTION OWNERSHIP: NONE.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.1.1 completes sovereign ownership, authority, and compliance metadata and corrects changelog rendering without changing scope semantics.

"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Final, Mapping, NoReturn, cast

VERSION: Final[str] = "v1.1.1-CX27-R3-R3-LEGAL-OPERATING-ROLE-SCOPE-BINDING"
SCHEMA: Final[str] = "WILSY-LEGAL-OPERATING-ROLE-SCOPE-BINDING/V1"
_HEX_128 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "root", "*"})


class LegalOperatingRoleScopeBindingError(ValueError):
    """Stable fail-closed scope-binding validation error."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _fail(code: str) -> NoReturn:
    raise LegalOperatingRoleScopeBindingError(code)


def _text(name: str, value: object, limit: int = 240) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(ord(ch) < 32 for ch in value)
    ):
        _fail(f"CX27_R2_{name.upper()}_INVALID")
    return value


def _tenant(value: object) -> str:
    tenant = _text("tenant_id", value, 160)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("CX27_R2_TENANT_ID_INVALID")
    return tenant


def _revision(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        _fail("CX27_R2_OPERATING_ROLE_REVISION_INVALID")
    return value


def _when(value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail("CX27_R2_EFFECTIVE_FROM_INVALID")
    return value.astimezone(timezone.utc)


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or not _HEX_128.fullmatch(value):
        _fail(f"CX27_R2_{name.upper()}_INVALID")
    return value


def _references(name: str, value: object) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)):
        _fail(f"CX27_R2_{name.upper()}_INVALID")
    normalized = tuple(_text(name, raw) for raw in value)
    if len(set(normalized)) != len(normalized):
        _fail(f"CX27_R2_{name.upper()}_DUPLICATE")
    return tuple(sorted(normalized))


@dataclass(frozen=True, slots=True)
class LegalOperatingRoleScopeBinding:
    """Immutable organizational scope descriptor for an operating-role revision.

    Scope configuration does not itself authorize access to any record, matter,
    operation, permission, work item, or financial function.
    """

    tenant_id: str
    scope_binding_id: str
    operating_role_id: str
    operating_role_revision: int
    scope_binding_revision: int
    office_references: tuple[str, ...]
    practice_references: tuple[str, ...]
    business_unit_references: tuple[str, ...]
    jurisdiction_references: tuple[str, ...]
    effective_from: datetime
    supersedes_fingerprint: str | None = None
    schema: str = SCHEMA
    scope_binding_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        tenant = _tenant(self.tenant_id)
        binding_id = _text("scope_binding_id", self.scope_binding_id)
        role_id = _text("operating_role_id", self.operating_role_id)
        role_revision = _revision(self.operating_role_revision)
        binding_revision = _revision(self.scope_binding_revision)
        offices = _references("office_reference", self.office_references)
        practices = _references("practice_reference", self.practice_references)
        units = _references("business_unit_reference", self.business_unit_references)
        jurisdictions = _references("jurisdiction_reference", self.jurisdiction_references)
        effective = _when(self.effective_from)
        predecessor = (
            None
            if self.supersedes_fingerprint is None
            else _fingerprint("supersedes_fingerprint", self.supersedes_fingerprint)
        )

        if not any((offices, practices, units, jurisdictions)):
            _fail("CX27_R2_SCOPE_EMPTY")
        if binding_revision == 1 and predecessor is not None:
            _fail("CX27_R3_FIRST_BINDING_REVISION_SUPERSEDES_FORBIDDEN")
        if binding_revision > 1 and predecessor is None:
            _fail("CX27_R3_LATER_BINDING_REVISION_SUPERSEDES_REQUIRED")
        if self.schema != SCHEMA or self.scope_binding_version != VERSION:
            _fail("CX27_R2_SCHEMA_VERSION_INVALID")

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "scope_binding_id", binding_id)
        object.__setattr__(self, "operating_role_id", role_id)
        object.__setattr__(
            self,
            "operating_role_revision",
            role_revision,
        )
        object.__setattr__(
            self,
            "scope_binding_revision",
            binding_revision,
        )
        object.__setattr__(self, "office_references", offices)
        object.__setattr__(self, "practice_references", practices)
        object.__setattr__(self, "business_unit_references", units)
        object.__setattr__(self, "jurisdiction_references", jurisdictions)
        object.__setattr__(self, "effective_from", effective)
        object.__setattr__(self, "supersedes_fingerprint", predecessor)

        computed = self._compute_fingerprint()
        if self.fingerprint:
            supplied = _fingerprint("fingerprint", self.fingerprint)
            if not hmac.compare_digest(supplied, computed):
                _fail("CX27_R2_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", computed)

    def semantic_dict(self) -> dict[str, object]:
        """Return exact deterministic semantic scope payload."""
        return {
            "schema": self.schema,
            "scope_binding_version": self.scope_binding_version,
            "tenant_id": self.tenant_id,
            "scope_binding_id": self.scope_binding_id,
            "operating_role_id": self.operating_role_id,
            "operating_role_revision": self.operating_role_revision,
            "scope_binding_revision": self.scope_binding_revision,
            "office_references": list(self.office_references),
            "practice_references": list(self.practice_references),
            "business_unit_references": list(self.business_unit_references),
            "jurisdiction_references": list(self.jurisdiction_references),
            "effective_from": self.effective_from.isoformat(),
            "supersedes_fingerprint": self.supersedes_fingerprint,
        }

    def _compute_fingerprint(self) -> str:
        raw = json.dumps(
            self.semantic_dict(),
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        return hashlib.sha3_512(raw).hexdigest()

    def to_dict(self) -> dict[str, object]:
        """Serialize exact immutable scope truth."""
        return {**self.semantic_dict(), "fingerprint": self.fingerprint}

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalOperatingRoleScopeBinding":
        """Strictly hydrate exact organizational scope truth."""
        expected = {
            "schema", "scope_binding_version", "tenant_id",
            "scope_binding_id", "operating_role_id",
            "operating_role_revision", "scope_binding_revision",
            "office_references", "practice_references",
            "business_unit_references", "jurisdiction_references",
            "effective_from", "supersedes_fingerprint", "fingerprint",
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
        for field in (
            "office_references", "practice_references",
            "business_unit_references", "jurisdiction_references",
        ):
            if not isinstance(payload[field], list):
                _fail(f"CX27_R2_{field.upper()}_INVALID")
        return cls(
            schema=cast(str, payload["schema"]),
            scope_binding_version=cast(str, payload["scope_binding_version"]),
            tenant_id=cast(str, payload["tenant_id"]),
            scope_binding_id=cast(str, payload["scope_binding_id"]),
            operating_role_id=cast(str, payload["operating_role_id"]),
            operating_role_revision=cast(
                int,
                payload["operating_role_revision"],
            ),
            scope_binding_revision=cast(
                int,
                payload["scope_binding_revision"],
            ),
            office_references=tuple(
                cast(list[str], payload["office_references"])
            ),
            practice_references=tuple(cast(list[str], payload["practice_references"])),
            business_unit_references=tuple(cast(list[str], payload["business_unit_references"])),
            jurisdiction_references=tuple(cast(list[str], payload["jurisdiction_references"])),
            effective_from=effective,
            supersedes_fingerprint=cast(str | None, payload["supersedes_fingerprint"]),
            fingerprint=cast(str, payload["fingerprint"]),
        )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalOperatingRoleScopeBinding",
    "LegalOperatingRoleScopeBindingError",
]

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: tools/eos/legal_operations/domain/legal_operating_role_scope_binding.py
# VERSION: v1.1.1-CX27-R3-R3-LEGAL-OPERATING-ROLE-SCOPE-BINDING
# POSTURE: FAIL-CLOSED
# AUTHORITY BOUNDARY: organizational scope configuration only; no record access, IAM, assignment, supervision, or financial authority
# TENANT POSTURE: exact explicit non-pseudo tenant identity only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
