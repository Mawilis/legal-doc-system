"""TITLE: WILSY OS Legal Operating Role Capability Binding
VERSION: v1.1.1-CX27-R3-R3-LEGAL-OPERATING-ROLE-CAPABILITY-BINDING
ARTIFACT: tools/eos/legal_operations/domain/legal_operating_role_capability_binding.py
AUTHORITY: Operating-role to Legal operating-capability association only; never permission possession.
EPITOME: Bind one exact operating-role revision to known Legal operating catalogue items.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_operating_role_capability_binding.py
COLLABORATION / OWNERSHIP: CX27-B owns immutable capability association semantics; catalogue, role definition, persistence, IAM, and workflow layers retain their own authority.
CLASSIFICATION: EMERGING CANONICAL
TENANT BOUNDARY: Exact explicit non-pseudo tenant identity only.
SECURITY / PRIVACY: Opaque identifiers and deterministic SHA3-512 fingerprints; fail closed on malformed input.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
IDEMPOTENCY: Pure immutable value object; persistence/replay authority NONE.
TRANSACTION OWNERSHIP: NONE.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.1.1 completes sovereign ownership/compliance metadata and corrects changelog rendering without changing capability semantics.

"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Final, Mapping, NoReturn, cast

from tools.eos.legal_operations.domain.legal_operating_catalogue import (
    get_legal_operating_item,
)

VERSION: Final[str] = "v1.1.1-CX27-R3-R3-LEGAL-OPERATING-ROLE-CAPABILITY-BINDING"
SCHEMA: Final[str] = "WILSY-LEGAL-OPERATING-ROLE-CAPABILITY-BINDING/V1"
_HEX_128 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "root", "*"})


class LegalOperatingRoleCapabilityBindingError(ValueError):
    """Stable fail-closed capability-binding validation error."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _fail(code: str) -> NoReturn:
    raise LegalOperatingRoleCapabilityBindingError(code)


def _text(name: str, value: object, limit: int = 200) -> str:
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


def _capabilities(value: object) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)) or not value:
        _fail("CX27_R2_CAPABILITY_IDS_INVALID")
    values: list[str] = []
    for raw in value:
        item_id = _text("capability_id", raw)
        try:
            item = get_legal_operating_item(item_id)
        except Exception as exc:
            raise LegalOperatingRoleCapabilityBindingError(
                "CX27_R2_CAPABILITY_UNKNOWN"
            ) from exc
        if item is None:
            _fail("CX27_R2_CAPABILITY_UNKNOWN")
        values.append(item_id)
    if len(set(values)) != len(values):
        _fail("CX27_R2_CAPABILITY_DUPLICATE")
    return tuple(sorted(values))


@dataclass(frozen=True, slots=True)
class LegalOperatingRoleCapabilityBinding:
    """Immutable capability association for one exact operating-role revision.

    The association is configuration only and grants no IAM permission,
    authorization role, matter access, principal authority, assignment,
    supervision, entitlement, or financial authority.
    """

    tenant_id: str
    capability_binding_id: str
    operating_role_id: str
    operating_role_revision: int
    capability_binding_revision: int
    capability_ids: tuple[str, ...]
    effective_from: datetime
    supersedes_fingerprint: str | None = None
    schema: str = SCHEMA
    capability_binding_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        tenant = _tenant(self.tenant_id)
        binding_id = _text("capability_binding_id", self.capability_binding_id)
        role_id = _text("operating_role_id", self.operating_role_id)
        role_revision = _revision(self.operating_role_revision)
        binding_revision = _revision(self.capability_binding_revision)
        capabilities = _capabilities(self.capability_ids)
        effective = _when(self.effective_from)
        predecessor = (
            None
            if self.supersedes_fingerprint is None
            else _fingerprint("supersedes_fingerprint", self.supersedes_fingerprint)
        )
        if binding_revision == 1 and predecessor is not None:
            _fail("CX27_R3_FIRST_BINDING_REVISION_SUPERSEDES_FORBIDDEN")
        if binding_revision > 1 and predecessor is None:
            _fail("CX27_R3_LATER_BINDING_REVISION_SUPERSEDES_REQUIRED")
        if self.schema != SCHEMA or self.capability_binding_version != VERSION:
            _fail("CX27_R2_SCHEMA_VERSION_INVALID")

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "capability_binding_id", binding_id)
        object.__setattr__(self, "operating_role_id", role_id)
        object.__setattr__(
            self,
            "operating_role_revision",
            role_revision,
        )
        object.__setattr__(
            self,
            "capability_binding_revision",
            binding_revision,
        )
        object.__setattr__(self, "capability_ids", capabilities)
        object.__setattr__(self, "effective_from", effective)
        object.__setattr__(self, "supersedes_fingerprint", predecessor)

        computed = self._compute_fingerprint()
        if self.fingerprint:
            supplied = _fingerprint("fingerprint", self.fingerprint)
            if not hmac.compare_digest(supplied, computed):
                _fail("CX27_R2_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", computed)

    def semantic_dict(self) -> dict[str, object]:
        """Return exact deterministic semantic payload."""
        return {
            "schema": self.schema,
            "capability_binding_version": self.capability_binding_version,
            "tenant_id": self.tenant_id,
            "capability_binding_id": self.capability_binding_id,
            "operating_role_id": self.operating_role_id,
            "operating_role_revision": self.operating_role_revision,
            "capability_binding_revision": self.capability_binding_revision,
            "capability_ids": list(self.capability_ids),
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
        """Serialize exact immutable binding truth."""
        return {**self.semantic_dict(), "fingerprint": self.fingerprint}

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalOperatingRoleCapabilityBinding":
        """Strictly hydrate exact capability-binding truth."""
        expected = {
            "schema", "capability_binding_version", "tenant_id",
            "capability_binding_id", "operating_role_id",
            "operating_role_revision", "capability_binding_revision",
            "capability_ids", "effective_from",
            "supersedes_fingerprint", "fingerprint",
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
        raw_capabilities = payload["capability_ids"]
        if not isinstance(raw_capabilities, list):
            _fail("CX27_R2_CAPABILITY_IDS_INVALID")
        return cls(
            schema=cast(str, payload["schema"]),
            capability_binding_version=cast(str, payload["capability_binding_version"]),
            tenant_id=cast(str, payload["tenant_id"]),
            capability_binding_id=cast(str, payload["capability_binding_id"]),
            operating_role_id=cast(str, payload["operating_role_id"]),
            operating_role_revision=cast(
                int,
                payload["operating_role_revision"],
            ),
            capability_binding_revision=cast(
                int,
                payload["capability_binding_revision"],
            ),
            capability_ids=tuple(cast(list[str], raw_capabilities)),
            effective_from=effective,
            supersedes_fingerprint=cast(str | None, payload["supersedes_fingerprint"]),
            fingerprint=cast(str, payload["fingerprint"]),
        )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalOperatingRoleCapabilityBinding",
    "LegalOperatingRoleCapabilityBindingError",
]

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: tools/eos/legal_operations/domain/legal_operating_role_capability_binding.py
# VERSION: v1.1.1-CX27-R3-R3-LEGAL-OPERATING-ROLE-CAPABILITY-BINDING
# POSTURE: FAIL-CLOSED
# AUTHORITY BOUNDARY: operating capability association only; no permission, IAM, assignment, supervision, or financial authority
# TENANT POSTURE: exact explicit non-pseudo tenant identity only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
