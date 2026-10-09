"""WILSY OS Legal Evidence provider-delete execution uncertainty.

TITLE: Legal Evidence Provider Delete Execution Uncertainty
VERSION: v1.0.1-L10A2R-A3-P4-P6A-PROVIDER-DELETE-EXECUTION-UNCERTAINTY-GOVERNANCE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME:
    Immutable tenant-scoped uncertainty evidence recording that a provider
    delete response exists but durable execution recording cannot yet be
    certified, without authorizing provider retry or inferring physical absence.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_evidence_provider_delete_execution_uncertainty.py
COLLABORATION / OWNERSHIP:
    Python EOS Legal Operations owns uncertainty semantics. Provider adapters
    supply bounded execution evidence only; registries own persistence mechanics.
CERTIFICATION OR UPDATE DATE: 2026-10-03
CHANGELOG:
    v1.0.1-L10A2R-A3-P4-P6A-PROVIDER-DELETE-EXECUTION-UNCERTAINTY-GOVERNANCE repairs sovereign source governance metadata and the
    mandatory end seal only. Durable executable VERSION remains
    v1.0.0-L10A2R-A3-P4-P6A-PROVIDER-DELETE-EXECUTION-UNCERTAINTY; SCHEMA, serialized representation, fingerprint inputs,
    hydration compatibility and runtime control flow remain unchanged.
    v1.0.0-L10A2R-A3-P4-P6A-PROVIDER-DELETE-EXECUTION-UNCERTAINTY establishes immutable provider-delete execution uncertainty.
COMPLIANCE:
    WILSY OS sovereign Legal Operations governance; exact tenant isolation;
    SHA3-512 integrity; fail-closed durable uncertainty evidence.
SECURITY / PRIVACY POSTURE:
    Opaque tenant/provider/object identities and cryptographic evidence only;
    no raw credential, IAM, billing, payment, settlement, retry or physical-
    absence authority is introduced.
TENANT BOUNDARY:
    Every uncertainty record binds one exact tenant, command, cleanup
    authorization, execution evidence and provider object/version.
AUTHORITY BOUNDARY:
    Immutable unresolved post-provider persistence uncertainty only. It does not
    prove physical absence, authorize provider retry, reconcile execution truth,
    mutate lifecycle truth, or confer IAM, billing, payment or settlement authority.
FINANCIAL AUTHORITY BOUNDARY:
    None. Provider-delete uncertainty is not financial execution or settlement;
    Kennel EOS remains the exclusive financial execution authority.

DURABLE RUNTIME VERSION:
    v1.0.0-L10A2R-A3-P4-P6A-PROVIDER-DELETE-EXECUTION-UNCERTAINTY

SEMANTIC BOUNDARY:
    UNCERTAINTY RECORDED
    != PROVIDER RETRY AUTHORIZED
    != PROVIDER OBJECT ABSENT
    != EXECUTION RECONCILED
    != PAYMENT EXECUTED
    != SETTLED
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_512
import hmac
import json
import re
from typing import Final, Mapping, NoReturn

from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_command import (
    LegalEvidenceProviderCleanupCommand,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_delete_execution_evidence import (
    LegalEvidenceProviderDeleteExecutionEvidence,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-A3-P4-P6A-"
    "PROVIDER-DELETE-EXECUTION-UNCERTAINTY"
)
SCHEMA: Final[str] = (
    "WILSY-LEGAL-EVIDENCE-PROVIDER-DELETE-EXECUTION-UNCERTAINTY/V1"
)

_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$")
_SHA3_512 = re.compile(r"^[0-9a-f]{128}$")


class LegalEvidenceProviderDeleteExecutionUncertaintyError(ValueError):
    """Stable pure-domain uncertainty validation failure."""


def _fail(code: str) -> NoReturn:
    raise LegalEvidenceProviderDeleteExecutionUncertaintyError(
        f"L10A2R_A3_P4_P6A_{code}"
    )


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or _IDENTITY.fullmatch(value) is None:
        _fail(f"{name.upper()}_INVALID")
    return value


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.lower() in {"global", "*", "all"}:
        _fail("TENANT_REQUIRED")
    return tenant


def _text(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > 2048
        or any(ord(character) < 32 for character in value)
    ):
        _fail(f"{name.upper()}_INVALID")
    return value


def _sha3(name: str, value: object) -> str:
    if not isinstance(value, str) or _SHA3_512.fullmatch(value) is None:
        _fail(f"{name.upper()}_INVALID")
    return value


def _utc(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        _fail(f"{name.upper()}_INVALID")
    offset = value.utcoffset()
    if offset is None:
        _fail(f"{name.upper()}_INVALID")
    return value.astimezone(timezone.utc)


def _payload(
    *,
    uncertainty_id: str,
    tenant_id: str,
    execution_evidence_id: str,
    command_id: str,
    cleanup_authorization_id: str,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
    command_fingerprint: str,
    cleanup_authorization_fingerprint: str,
    execution_evidence_fingerprint: str,
    delete_marker: bool | None,
    delete_marker_version_reference: str | None,
    executed_at: datetime,
    uncertainty_recorded_at: datetime,
) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "uncertainty_id": uncertainty_id,
        "tenant_id": tenant_id,
        "execution_evidence_id": execution_evidence_id,
        "command_id": command_id,
        "cleanup_authorization_id": cleanup_authorization_id,
        "provider_name": provider_name,
        "storage_reference": storage_reference,
        "object_version_reference": object_version_reference,
        "command_fingerprint": command_fingerprint,
        "cleanup_authorization_fingerprint":
            cleanup_authorization_fingerprint,
        "execution_evidence_fingerprint": execution_evidence_fingerprint,
        "delete_marker": delete_marker,
        "delete_marker_version_reference":
            delete_marker_version_reference,
        "executed_at": executed_at.isoformat(),
        "uncertainty_recorded_at": uncertainty_recorded_at.isoformat(),
    }


def _fingerprint(payload: Mapping[str, object]) -> str:
    raw = json.dumps(
        dict(payload),
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha3_512(raw).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalEvidenceProviderDeleteExecutionUncertainty:
    """Immutable unresolved provider-delete execution persistence evidence."""

    uncertainty_id: str
    tenant_id: str
    execution_evidence_id: str
    command_id: str
    cleanup_authorization_id: str
    provider_name: str
    storage_reference: str
    object_version_reference: str
    command_fingerprint: str
    cleanup_authorization_fingerprint: str
    execution_evidence_fingerprint: str
    delete_marker: bool | None
    delete_marker_version_reference: str | None
    executed_at: datetime
    uncertainty_recorded_at: datetime
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        uncertainty_id = _identity("uncertainty_id", self.uncertainty_id)
        tenant_id = _tenant(self.tenant_id)
        execution_evidence_id = _identity(
            "execution_evidence_id",
            self.execution_evidence_id,
        )
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
        execution_evidence_fingerprint = _sha3(
            "execution_evidence_fingerprint",
            self.execution_evidence_fingerprint,
        )

        if (
            self.delete_marker is not None
            and not isinstance(self.delete_marker, bool)
        ):
            _fail("DELETE_MARKER_INVALID")

        marker_reference = (
            None
            if self.delete_marker_version_reference is None
            else _text(
                "delete_marker_version_reference",
                self.delete_marker_version_reference,
            )
        )
        if self.delete_marker is not True and marker_reference is not None:
            _fail("DELETE_MARKER_EVIDENCE_INVALID")

        executed_at = _utc("executed_at", self.executed_at)
        uncertainty_recorded_at = _utc(
            "uncertainty_recorded_at",
            self.uncertainty_recorded_at,
        )
        if uncertainty_recorded_at < executed_at:
            _fail("CHRONOLOGY_INVALID")

        if self.schema != SCHEMA:
            _fail("SCHEMA_INVALID")
        if self.version != VERSION:
            _fail("VERSION_INVALID")

        payload = _payload(
            uncertainty_id=uncertainty_id,
            tenant_id=tenant_id,
            execution_evidence_id=execution_evidence_id,
            command_id=command_id,
            cleanup_authorization_id=cleanup_authorization_id,
            provider_name=provider_name,
            storage_reference=storage_reference,
            object_version_reference=object_version_reference,
            command_fingerprint=command_fingerprint,
            cleanup_authorization_fingerprint=
                cleanup_authorization_fingerprint,
            execution_evidence_fingerprint=
                execution_evidence_fingerprint,
            delete_marker=self.delete_marker,
            delete_marker_version_reference=marker_reference,
            executed_at=executed_at,
            uncertainty_recorded_at=uncertainty_recorded_at,
        )
        digest = _fingerprint(payload)

        if self.fingerprint:
            supplied = _sha3("fingerprint", self.fingerprint)
            if not hmac.compare_digest(supplied, digest):
                _fail("FINGERPRINT_MISMATCH")

        object.__setattr__(self, "uncertainty_id", uncertainty_id)
        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(
            self,
            "execution_evidence_id",
            execution_evidence_id,
        )
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
            "execution_evidence_fingerprint",
            execution_evidence_fingerprint,
        )
        object.__setattr__(
            self,
            "delete_marker_version_reference",
            marker_reference,
        )
        object.__setattr__(self, "executed_at", executed_at)
        object.__setattr__(
            self,
            "uncertainty_recorded_at",
            uncertainty_recorded_at,
        )
        object.__setattr__(self, "fingerprint", digest)

    def to_document(self) -> dict[str, object]:
        """Return exact durable representation."""
        return {
            **_payload(
                uncertainty_id=self.uncertainty_id,
                tenant_id=self.tenant_id,
                execution_evidence_id=self.execution_evidence_id,
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
                execution_evidence_fingerprint=
                    self.execution_evidence_fingerprint,
                delete_marker=self.delete_marker,
                delete_marker_version_reference=
                    self.delete_marker_version_reference,
                executed_at=self.executed_at,
                uncertainty_recorded_at=
                    self.uncertainty_recorded_at,
            ),
            "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_document(
        cls,
        document: Mapping[str, object],
    ) -> "LegalEvidenceProviderDeleteExecutionUncertainty":
        """Hydrate and cryptographically revalidate exact durable bytes."""
        if not isinstance(document, Mapping):
            _fail("DOCUMENT_INVALID")

        expected = {
            "schema",
            "version",
            "uncertainty_id",
            "tenant_id",
            "execution_evidence_id",
            "command_id",
            "cleanup_authorization_id",
            "provider_name",
            "storage_reference",
            "object_version_reference",
            "command_fingerprint",
            "cleanup_authorization_fingerprint",
            "execution_evidence_fingerprint",
            "delete_marker",
            "delete_marker_version_reference",
            "executed_at",
            "uncertainty_recorded_at",
            "fingerprint",
        }
        if set(document) != expected:
            _fail("DOCUMENT_SCHEMA_INVALID")

        executed_raw = document["executed_at"]
        recorded_raw = document["uncertainty_recorded_at"]
        if not isinstance(executed_raw, str):
            _fail("EXECUTED_AT_INVALID")
        if not isinstance(recorded_raw, str):
            _fail("UNCERTAINTY_RECORDED_AT_INVALID")

        try:
            executed_at = datetime.fromisoformat(executed_raw)
            recorded_at = datetime.fromisoformat(recorded_raw)
        except ValueError as error:
            raise LegalEvidenceProviderDeleteExecutionUncertaintyError(
                "L10A2R_A3_P4_P6A_DATETIME_INVALID"
            ) from error

        return cls(
            uncertainty_id=document["uncertainty_id"],  # type: ignore[arg-type]
            tenant_id=document["tenant_id"],  # type: ignore[arg-type]
            execution_evidence_id=document["execution_evidence_id"],  # type: ignore[arg-type]
            command_id=document["command_id"],  # type: ignore[arg-type]
            cleanup_authorization_id=document["cleanup_authorization_id"],  # type: ignore[arg-type]
            provider_name=document["provider_name"],  # type: ignore[arg-type]
            storage_reference=document["storage_reference"],  # type: ignore[arg-type]
            object_version_reference=document["object_version_reference"],  # type: ignore[arg-type]
            command_fingerprint=document["command_fingerprint"],  # type: ignore[arg-type]
            cleanup_authorization_fingerprint=document["cleanup_authorization_fingerprint"],  # type: ignore[arg-type]
            execution_evidence_fingerprint=document["execution_evidence_fingerprint"],  # type: ignore[arg-type]
            delete_marker=document["delete_marker"],  # type: ignore[arg-type]
            delete_marker_version_reference=document[
                "delete_marker_version_reference"
            ],  # type: ignore[arg-type]
            executed_at=executed_at,
            uncertainty_recorded_at=recorded_at,
            schema=document["schema"],  # type: ignore[arg-type]
            version=document["version"],  # type: ignore[arg-type]
            fingerprint=document["fingerprint"],  # type: ignore[arg-type]
        )


def open_legal_evidence_provider_delete_execution_uncertainty(
    *,
    uncertainty_id: str,
    command: LegalEvidenceProviderCleanupCommand,
    execution_evidence: LegalEvidenceProviderDeleteExecutionEvidence,
    uncertainty_recorded_at: datetime,
) -> LegalEvidenceProviderDeleteExecutionUncertainty:
    """Bind one successful provider response to unresolved durable recording."""
    if type(command) is not LegalEvidenceProviderCleanupCommand:
        _fail("COMMAND_REQUIRED")
    if (
        type(execution_evidence)
        is not LegalEvidenceProviderDeleteExecutionEvidence
    ):
        _fail("EXECUTION_EVIDENCE_REQUIRED")

    exact_pairs = (
        ("tenant_id", command.tenant_id, execution_evidence.tenant_id),
        ("command_id", command.command_id, execution_evidence.command_id),
        (
            "cleanup_authorization_id",
            command.cleanup_authorization_id,
            execution_evidence.cleanup_authorization_id,
        ),
        (
            "provider_name",
            command.provider_name,
            execution_evidence.provider_name,
        ),
        (
            "storage_reference",
            command.storage_reference,
            execution_evidence.storage_reference,
        ),
        (
            "object_version_reference",
            command.object_version_reference,
            execution_evidence.object_version_reference,
        ),
        (
            "command_fingerprint",
            command.fingerprint,
            execution_evidence.command_fingerprint,
        ),
        (
            "cleanup_authorization_fingerprint",
            command.cleanup_authorization_fingerprint,
            execution_evidence.cleanup_authorization_fingerprint,
        ),
    )
    for name, left, right in exact_pairs:
        if left != right:
            _fail(f"{name.upper()}_MISMATCH")

    if execution_evidence.executed_at < command.issued_at:
        _fail("EXECUTION_CHRONOLOGY_INVALID")

    return LegalEvidenceProviderDeleteExecutionUncertainty(
        uncertainty_id=_identity("uncertainty_id", uncertainty_id),
        tenant_id=execution_evidence.tenant_id,
        execution_evidence_id=execution_evidence.execution_evidence_id,
        command_id=execution_evidence.command_id,
        cleanup_authorization_id=
            execution_evidence.cleanup_authorization_id,
        provider_name=execution_evidence.provider_name,
        storage_reference=execution_evidence.storage_reference,
        object_version_reference=
            execution_evidence.object_version_reference,
        command_fingerprint=execution_evidence.command_fingerprint,
        cleanup_authorization_fingerprint=
            execution_evidence.cleanup_authorization_fingerprint,
        execution_evidence_fingerprint=execution_evidence.fingerprint,
        delete_marker=execution_evidence.delete_marker,
        delete_marker_version_reference=
            execution_evidence.delete_marker_version_reference,
        executed_at=execution_evidence.executed_at,
        uncertainty_recorded_at=uncertainty_recorded_at,
    )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalEvidenceProviderDeleteExecutionUncertainty",
    "LegalEvidenceProviderDeleteExecutionUncertaintyError",
    "open_legal_evidence_provider_delete_execution_uncertainty",
]

# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_evidence_provider_delete_execution_uncertainty.py
# VERSION: v1.0.1-L10A2R-A3-P4-P6A-PROVIDER-DELETE-EXECUTION-UNCERTAINTY-GOVERNANCE
# AUTHORITY BOUNDARY: immutable post-provider execution uncertainty evidence only; no retry, reconciliation, physical-absence, IAM, billing, payment or settlement authority
# TENANT POSTURE: exact tenant/command/authorization/execution-evidence/provider-object identity remains immutable
# FAIL-CLOSED POSTURE: malformed, divergent, corrupt, foreign-tenant, schema-incompatible or version-incompatible evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# DURABLE RUNTIME VERSION: v1.0.0-L10A2R-A3-P4-P6A-PROVIDER-DELETE-EXECUTION-UNCERTAINTY
# END OF WILSY OS SOVEREIGN ARTIFACT
