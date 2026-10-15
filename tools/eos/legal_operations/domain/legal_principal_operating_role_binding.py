"""TITLE: WILSY OS Legal Principal Operating Role Binding
VERSION: v1.0.1-CX27-R2-LEGAL-PRINCIPAL-OPERATING-ROLE-BINDING
ARTIFACT: tools/eos/legal_operations/domain/legal_principal_operating_role_binding.py
AUTHORITY: Principal organizational operating-role occupancy only; never IAM or workforce authority.
EPITOME: Record one immutable effective-dated principal occupancy of a tenant-defined Legal operating role.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_principal_operating_role_binding.py
COLLABORATION / OWNERSHIP: CX27-D owns immutable effective-dated occupancy evidence; identity, IAM, workforce, matter, workflow, entitlement, and execution authorities remain external.
CLASSIFICATION: EMERGING CANONICAL
TENANT BOUNDARY: Exact explicit non-pseudo tenant identity only.
AUTHORITY BOUNDARY: Principal-to-operating-role occupancy metadata only; never authentication, IAM membership, access, assignment, supervision, professional status, or execution authority.
SECURITY / PRIVACY: Opaque identifiers and deterministic SHA3-512 fingerprints; fail closed on malformed input.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
IDEMPOTENCY: Pure immutable value object; persistence/replay authority NONE.
TRANSACTION OWNERSHIP: NONE.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.1 completes sovereign ownership, authority, compliance, and tenant metadata without changing occupancy semantics.

"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Final, Mapping, NoReturn, cast

VERSION: Final[str] = "v1.0.1-CX27-R2-LEGAL-PRINCIPAL-OPERATING-ROLE-BINDING"
SCHEMA: Final[str] = "WILSY-LEGAL-PRINCIPAL-OPERATING-ROLE-BINDING/V1"
_HEX_128 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "root", "*"})


class LegalPrincipalOperatingRoleBindingError(ValueError):
    """Stable fail-closed principal operating-role binding validation error."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _fail(code: str) -> NoReturn:
    raise LegalPrincipalOperatingRoleBindingError(code)


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


def _revision(name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        _fail(f"CX27_R2_{name.upper()}_INVALID")
    return value


def _when(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail(f"CX27_R2_{name.upper()}_INVALID")
    return value.astimezone(timezone.utc)


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or not _HEX_128.fullmatch(value):
        _fail(f"CX27_R2_{name.upper()}_INVALID")
    return value


@dataclass(frozen=True, slots=True)
class LegalPrincipalOperatingRoleBinding:
    """Immutable organizational occupancy of a tenant-defined operating role.

    Occupancy does not grant IAM permission, business role, authorization role,
    workforce currentness, matter access, professional qualification,
    regulatory appointment, work assignment, supervision, entitlement, billing,
    payment, execution, or settlement authority.
    """

    tenant_id: str
    principal_operating_role_binding_id: str
    binding_revision: int
    principal_id: str
    operating_role_id: str
    operating_role_revision: int
    effective_from: datetime
    effective_until: datetime | None
    source_reference: str
    source_evidence_fingerprint: str
    supersedes_fingerprint: str | None = None
    schema: str = SCHEMA
    principal_binding_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        tenant = _tenant(self.tenant_id)
        binding_id = _text(
            "principal_operating_role_binding_id",
            self.principal_operating_role_binding_id,
        )
        binding_revision = _revision("binding_revision", self.binding_revision)
        principal = _text("principal_id", self.principal_id)
        role_id = _text("operating_role_id", self.operating_role_id)
        role_revision = _revision(
            "operating_role_revision",
            self.operating_role_revision,
        )
        effective = _when("effective_from", self.effective_from)
        until = (
            None
            if self.effective_until is None
            else _when("effective_until", self.effective_until)
        )
        if until is not None and until <= effective:
            _fail("CX27_R2_EFFECTIVE_UNTIL_INVALID")

        source_reference = _text("source_reference", self.source_reference, 500)
        source_fingerprint = _fingerprint(
            "source_evidence_fingerprint",
            self.source_evidence_fingerprint,
        )
        predecessor = (
            None
            if self.supersedes_fingerprint is None
            else _fingerprint("supersedes_fingerprint", self.supersedes_fingerprint)
        )
        if binding_revision == 1 and predecessor is not None:
            _fail("CX27_R2_FIRST_REVISION_SUPERSEDES_FORBIDDEN")
        if binding_revision > 1 and predecessor is None:
            _fail("CX27_R2_LATER_REVISION_SUPERSEDES_REQUIRED")
        if self.schema != SCHEMA or self.principal_binding_version != VERSION:
            _fail("CX27_R2_SCHEMA_VERSION_INVALID")

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "principal_operating_role_binding_id", binding_id)
        object.__setattr__(self, "binding_revision", binding_revision)
        object.__setattr__(self, "principal_id", principal)
        object.__setattr__(self, "operating_role_id", role_id)
        object.__setattr__(self, "operating_role_revision", role_revision)
        object.__setattr__(self, "effective_from", effective)
        object.__setattr__(self, "effective_until", until)
        object.__setattr__(self, "source_reference", source_reference)
        object.__setattr__(self, "source_evidence_fingerprint", source_fingerprint)
        object.__setattr__(self, "supersedes_fingerprint", predecessor)

        computed = self._compute_fingerprint()
        if self.fingerprint:
            supplied = _fingerprint("fingerprint", self.fingerprint)
            if not hmac.compare_digest(supplied, computed):
                _fail("CX27_R2_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", computed)

    def semantic_dict(self) -> dict[str, object]:
        """Return exact deterministic semantic occupancy payload."""
        return {
            "schema": self.schema,
            "principal_binding_version": self.principal_binding_version,
            "tenant_id": self.tenant_id,
            "principal_operating_role_binding_id":
                self.principal_operating_role_binding_id,
            "binding_revision": self.binding_revision,
            "principal_id": self.principal_id,
            "operating_role_id": self.operating_role_id,
            "operating_role_revision": self.operating_role_revision,
            "effective_from": self.effective_from.isoformat(),
            "effective_until": (
                self.effective_until.isoformat()
                if self.effective_until is not None
                else None
            ),
            "source_reference": self.source_reference,
            "source_evidence_fingerprint": self.source_evidence_fingerprint,
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
        """Serialize exact immutable organizational occupancy truth."""
        return {**self.semantic_dict(), "fingerprint": self.fingerprint}

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalPrincipalOperatingRoleBinding":
        """Strictly hydrate exact organizational occupancy truth."""
        expected = {
            "schema", "principal_binding_version", "tenant_id",
            "principal_operating_role_binding_id", "binding_revision",
            "principal_id", "operating_role_id", "operating_role_revision",
            "effective_from", "effective_until", "source_reference",
            "source_evidence_fingerprint", "supersedes_fingerprint",
            "fingerprint",
        }
        if set(payload) != expected:
            _fail("CX27_R2_PAYLOAD_SCHEMA_INVALID")
        raw_from = payload["effective_from"]
        raw_until = payload["effective_until"]
        if not isinstance(raw_from, str):
            _fail("CX27_R2_EFFECTIVE_FROM_INVALID")
        if raw_until is not None and not isinstance(raw_until, str):
            _fail("CX27_R2_EFFECTIVE_UNTIL_INVALID")
        try:
            effective_from = datetime.fromisoformat(raw_from)
            effective_until = (
                None if raw_until is None else datetime.fromisoformat(raw_until)
            )
        except ValueError:
            _fail("CX27_R2_EFFECTIVE_TIME_INVALID")
        return cls(
            schema=cast(str, payload["schema"]),
            principal_binding_version=cast(str, payload["principal_binding_version"]),
            tenant_id=cast(str, payload["tenant_id"]),
            principal_operating_role_binding_id=cast(
                str, payload["principal_operating_role_binding_id"]
            ),
            binding_revision=cast(int, payload["binding_revision"]),
            principal_id=cast(str, payload["principal_id"]),
            operating_role_id=cast(str, payload["operating_role_id"]),
            operating_role_revision=cast(int, payload["operating_role_revision"]),
            effective_from=effective_from,
            effective_until=effective_until,
            source_reference=cast(str, payload["source_reference"]),
            source_evidence_fingerprint=cast(
                str, payload["source_evidence_fingerprint"]
            ),
            supersedes_fingerprint=cast(str | None, payload["supersedes_fingerprint"]),
            fingerprint=cast(str, payload["fingerprint"]),
        )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalPrincipalOperatingRoleBinding",
    "LegalPrincipalOperatingRoleBindingError",
]

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: tools/eos/legal_operations/domain/legal_principal_operating_role_binding.py
# VERSION: v1.0.1-CX27-R2-LEGAL-PRINCIPAL-OPERATING-ROLE-BINDING
# POSTURE: FAIL-CLOSED
# AUTHORITY BOUNDARY: organizational principal-role occupancy only; no IAM, workforce, matter, assignment, supervision, or financial authority
# TENANT POSTURE: exact explicit non-pseudo tenant identity only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
