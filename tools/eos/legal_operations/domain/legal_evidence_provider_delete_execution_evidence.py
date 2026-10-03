"""WILSY OS Legal Evidence provider-delete execution evidence.

TITLE: Legal Evidence Provider Delete Execution Evidence
VERSION: v1.0.1-L10A2R-A3-P4-P5A-PROVIDER-DELETE-EXECUTION-EVIDENCE-GOVERNANCE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME:
    Immutable tenant-scoped evidence describing one observed provider-delete
    execution result without asserting physical absence, retry authority,
    payment execution, settlement, or broader lifecycle truth.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_evidence_provider_delete_execution_evidence.py
COLLABORATION / OWNERSHIP:
    Python EOS Legal Operations owns evidence semantics. Provider adapters
    supply bounded external execution evidence only; registries own durable
    persistence mechanics only.
CERTIFICATION OR UPDATE DATE: 2026-10-03
CHANGELOG:
    v1.0.1-L10A2R-A3-P4-P5A-PROVIDER-DELETE-EXECUTION-EVIDENCE-GOVERNANCE repairs sovereign source governance metadata and the
    mandatory end seal only. Executable module VERSION remains
    v1.0.0-L10A2R-A3-P4-P5A-PROVIDER-DELETE-EXECUTION-EVIDENCE; SCHEMA, serialized representation, fingerprint inputs,
    hydration compatibility and runtime control flow remain unchanged.
    The executable VERSION is source identity metadata and is intentionally not
    persisted in the execution-evidence document or fingerprint payload.
    v1.0.0-L10A2R-A3-P4-P5A-PROVIDER-DELETE-EXECUTION-EVIDENCE establishes immutable provider-delete execution evidence.
COMPLIANCE:
    WILSY OS sovereign Legal Operations governance; exact tenant isolation;
    immutable SHA3-512 evidence; fail-closed persisted-document validation.
SECURITY / PRIVACY POSTURE:
    Opaque tenant/provider/object identities and bounded provider response
    evidence only; no raw credentials, IAM, payment, settlement or physical-
    absence authority is introduced.
TENANT BOUNDARY:
    Every execution-evidence record is bound to one exact tenant, command,
    cleanup authorization, provider object/version and immutable fingerprints.
AUTHORITY BOUNDARY:
    Immutable provider-delete execution evidence only. No cleanup authorization,
    retry, reconciliation, physical-absence proof, lifecycle, IAM, billing,
    payment or settlement authority.
FINANCIAL AUTHORITY BOUNDARY:
    None. Provider execution evidence is not financial execution or settlement;
    Kennel EOS remains the exclusive financial execution authority.

EXECUTABLE MODULE VERSION:
    v1.0.0-L10A2R-A3-P4-P5A-PROVIDER-DELETE-EXECUTION-EVIDENCE

DURABLE DOCUMENT DISCRIMINATOR:
    SCHEMA only. Executable VERSION is not serialized or fingerprinted.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_512
import hmac
import json
import re
from typing import Final, Mapping


VERSION: Final[str] = (
    "v1.0.0-L10A2R-A3-P4-P5A-"
    "PROVIDER-DELETE-EXECUTION-EVIDENCE"
)
SCHEMA: Final[str] = (
    "WILSY-LEGAL-EVIDENCE-PROVIDER-DELETE-EXECUTION-EVIDENCE/V1"
)

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$"
)
_HEX: Final[frozenset[str]] = frozenset("0123456789abcdef")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class LegalEvidenceProviderDeleteExecutionEvidenceError(ValueError):
    """Stable fail-closed execution-evidence domain failure."""


def _text(name: str, value: object, *, limit: int = 2048) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(ord(character) < 32 for character in value)
    ):
        raise LegalEvidenceProviderDeleteExecutionEvidenceError(
            f"L10A2R_A3_P4_P5A_{name.upper()}_INVALID"
        )
    return value


def _identity(name: str, value: object) -> str:
    normalized = _text(name, value, limit=256)
    if _IDENTITY.fullmatch(normalized) is None:
        raise LegalEvidenceProviderDeleteExecutionEvidenceError(
            f"L10A2R_A3_P4_P5A_{name.upper()}_INVALID"
        )
    return normalized


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        raise LegalEvidenceProviderDeleteExecutionEvidenceError(
            "L10A2R_A3_P4_P5A_TENANT_REQUIRED"
        )
    return tenant


def _sha3(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 128
        or any(character not in _HEX for character in value)
    ):
        raise LegalEvidenceProviderDeleteExecutionEvidenceError(
            f"L10A2R_A3_P4_P5A_{name.upper()}_INVALID"
        )
    return value


def _utc(name: str, value: object) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceProviderDeleteExecutionEvidenceError(
            f"L10A2R_A3_P4_P5A_{name.upper()}_INVALID"
        )
    return value.astimezone(timezone.utc)


def _fingerprint_payload(
    *,
    execution_evidence_id: str,
    tenant_id: str,
    command_id: str,
    cleanup_authorization_id: str,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
    command_fingerprint: str,
    cleanup_authorization_fingerprint: str,
    delete_marker: bool | None,
    delete_marker_version_reference: str | None,
    executed_at: datetime,
) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "execution_evidence_id": execution_evidence_id,
        "tenant_id": tenant_id,
        "command_id": command_id,
        "cleanup_authorization_id": cleanup_authorization_id,
        "provider_name": provider_name,
        "storage_reference": storage_reference,
        "object_version_reference": object_version_reference,
        "command_fingerprint": command_fingerprint,
        "cleanup_authorization_fingerprint":
            cleanup_authorization_fingerprint,
        "delete_marker": delete_marker,
        "delete_marker_version_reference":
            delete_marker_version_reference,
        "executed_at": executed_at.isoformat(),
    }


def _fingerprint(**payload: object) -> str:
    raw = json.dumps(
        payload,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha3_512(raw).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalEvidenceProviderDeleteExecutionEvidence:
    """Immutable successful provider-delete execution evidence."""

    execution_evidence_id: str
    tenant_id: str
    command_id: str
    cleanup_authorization_id: str
    provider_name: str
    storage_reference: str
    object_version_reference: str
    command_fingerprint: str
    cleanup_authorization_fingerprint: str
    delete_marker: bool | None
    delete_marker_version_reference: str | None
    executed_at: datetime
    schema: str = SCHEMA
    fingerprint: str = ""

    def __post_init__(self) -> None:
        execution_evidence_id = _identity(
            "execution_evidence_id",
            self.execution_evidence_id,
        )
        tenant_id = _tenant(self.tenant_id)
        command_id = _identity("command_id", self.command_id)
        cleanup_authorization_id = _identity(
            "cleanup_authorization_id",
            self.cleanup_authorization_id,
        )
        provider_name = _identity("provider_name", self.provider_name)
        storage_reference = _text(
            "storage_reference",
            self.storage_reference,
        )
        object_version_reference = _text(
            "object_version_reference",
            self.object_version_reference,
        )
        command_fingerprint = _sha3(
            "command_fingerprint",
            self.command_fingerprint,
        )
        cleanup_authorization_fingerprint = _sha3(
            "cleanup_authorization_fingerprint",
            self.cleanup_authorization_fingerprint,
        )

        if (
            self.delete_marker is not None
            and not isinstance(self.delete_marker, bool)
        ):
            raise LegalEvidenceProviderDeleteExecutionEvidenceError(
                "L10A2R_A3_P4_P5A_DELETE_MARKER_INVALID"
            )

        delete_marker_version_reference = (
            None
            if self.delete_marker_version_reference is None
            else _text(
                "delete_marker_version_reference",
                self.delete_marker_version_reference,
            )
        )

        if (
            self.delete_marker is not True
            and delete_marker_version_reference is not None
        ):
            raise LegalEvidenceProviderDeleteExecutionEvidenceError(
                "L10A2R_A3_P4_P5A_DELETE_MARKER_EVIDENCE_INVALID"
            )

        executed_at = _utc("executed_at", self.executed_at)

        if self.schema != SCHEMA:
            raise LegalEvidenceProviderDeleteExecutionEvidenceError(
                "L10A2R_A3_P4_P5A_SCHEMA_INVALID"
            )

        payload = _fingerprint_payload(
            execution_evidence_id=execution_evidence_id,
            tenant_id=tenant_id,
            command_id=command_id,
            cleanup_authorization_id=cleanup_authorization_id,
            provider_name=provider_name,
            storage_reference=storage_reference,
            object_version_reference=object_version_reference,
            command_fingerprint=command_fingerprint,
            cleanup_authorization_fingerprint=
                cleanup_authorization_fingerprint,
            delete_marker=self.delete_marker,
            delete_marker_version_reference=
                delete_marker_version_reference,
            executed_at=executed_at,
        )
        digest = _fingerprint(**payload)

        if self.fingerprint:
            supplied = _sha3("fingerprint", self.fingerprint)
            if not hmac.compare_digest(supplied, digest):
                raise LegalEvidenceProviderDeleteExecutionEvidenceError(
                    "L10A2R_A3_P4_P5A_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "execution_evidence_id",
            execution_evidence_id,
        )
        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "command_id", command_id)
        object.__setattr__(
            self,
            "cleanup_authorization_id",
            cleanup_authorization_id,
        )
        object.__setattr__(self, "provider_name", provider_name)
        object.__setattr__(
            self,
            "storage_reference",
            storage_reference,
        )
        object.__setattr__(
            self,
            "object_version_reference",
            object_version_reference,
        )
        object.__setattr__(
            self,
            "command_fingerprint",
            command_fingerprint,
        )
        object.__setattr__(
            self,
            "cleanup_authorization_fingerprint",
            cleanup_authorization_fingerprint,
        )
        object.__setattr__(
            self,
            "delete_marker_version_reference",
            delete_marker_version_reference,
        )
        object.__setattr__(self, "executed_at", executed_at)
        object.__setattr__(self, "fingerprint", digest)

    def to_document(self) -> dict[str, object]:
        """Return exact durable-document representation."""
        return {
            **_fingerprint_payload(
                execution_evidence_id=self.execution_evidence_id,
                tenant_id=self.tenant_id,
                command_id=self.command_id,
                cleanup_authorization_id=
                    self.cleanup_authorization_id,
                provider_name=self.provider_name,
                storage_reference=self.storage_reference,
                object_version_reference=
                    self.object_version_reference,
                command_fingerprint=self.command_fingerprint,
                cleanup_authorization_fingerprint=
                    self.cleanup_authorization_fingerprint,
                delete_marker=self.delete_marker,
                delete_marker_version_reference=
                    self.delete_marker_version_reference,
                executed_at=self.executed_at,
            ),
            "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_document(
        cls,
        document: Mapping[str, object],
    ) -> "LegalEvidenceProviderDeleteExecutionEvidence":
        """Hydrate and cryptographically revalidate one durable document."""
        if not isinstance(document, Mapping):
            raise LegalEvidenceProviderDeleteExecutionEvidenceError(
                "L10A2R_A3_P4_P5A_DOCUMENT_INVALID"
            )

        expected = {
            "schema",
            "execution_evidence_id",
            "tenant_id",
            "command_id",
            "cleanup_authorization_id",
            "provider_name",
            "storage_reference",
            "object_version_reference",
            "command_fingerprint",
            "cleanup_authorization_fingerprint",
            "delete_marker",
            "delete_marker_version_reference",
            "executed_at",
            "fingerprint",
        }

        if set(document) != expected:
            raise LegalEvidenceProviderDeleteExecutionEvidenceError(
                "L10A2R_A3_P4_P5A_DOCUMENT_SCHEMA_INVALID"
            )

        executed_at_raw = document["executed_at"]
        if not isinstance(executed_at_raw, str):
            raise LegalEvidenceProviderDeleteExecutionEvidenceError(
                "L10A2R_A3_P4_P5A_EXECUTED_AT_INVALID"
            )

        try:
            executed_at = datetime.fromisoformat(executed_at_raw)
        except ValueError as error:
            raise LegalEvidenceProviderDeleteExecutionEvidenceError(
                "L10A2R_A3_P4_P5A_EXECUTED_AT_INVALID"
            ) from error

        return cls(
            execution_evidence_id=document["execution_evidence_id"],  # type: ignore[arg-type]
            tenant_id=document["tenant_id"],  # type: ignore[arg-type]
            command_id=document["command_id"],  # type: ignore[arg-type]
            cleanup_authorization_id=document["cleanup_authorization_id"],  # type: ignore[arg-type]
            provider_name=document["provider_name"],  # type: ignore[arg-type]
            storage_reference=document["storage_reference"],  # type: ignore[arg-type]
            object_version_reference=document["object_version_reference"],  # type: ignore[arg-type]
            command_fingerprint=document["command_fingerprint"],  # type: ignore[arg-type]
            cleanup_authorization_fingerprint=document["cleanup_authorization_fingerprint"],  # type: ignore[arg-type]
            delete_marker=document["delete_marker"],  # type: ignore[arg-type]
            delete_marker_version_reference=document[
                "delete_marker_version_reference"
            ],  # type: ignore[arg-type]
            executed_at=executed_at,
            schema=document["schema"],  # type: ignore[arg-type]
            fingerprint=document["fingerprint"],  # type: ignore[arg-type]
        )

# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_evidence_provider_delete_execution_evidence.py
# VERSION: v1.0.1-L10A2R-A3-P4-P5A-PROVIDER-DELETE-EXECUTION-EVIDENCE-GOVERNANCE
# AUTHORITY BOUNDARY: immutable provider-delete execution evidence only; no cleanup authorization, retry, reconciliation, physical-absence, IAM, billing, payment or settlement authority
# TENANT POSTURE: exact tenant/command/authorization/provider-object identity remains immutable
# FAIL-CLOSED POSTURE: malformed, divergent, corrupt, foreign-tenant or schema-incompatible evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# EXECUTABLE MODULE VERSION: v1.0.0-L10A2R-A3-P4-P5A-PROVIDER-DELETE-EXECUTION-EVIDENCE
# DURABLE DOCUMENT DISCRIMINATOR: SCHEMA only; executable VERSION is not serialized or fingerprinted
# END OF WILSY OS SOVEREIGN ARTIFACT
