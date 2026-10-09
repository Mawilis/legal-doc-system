"""WILSY OS Legal Evidence provider-delete pre-execution claim.

TITLE: Legal Evidence Provider Delete Execution Claim
VERSION: v1.0.1-L10A2R-A3-P4-P6D2-PROVIDER-DELETE-EXECUTION-CLAIM-GOVERNANCE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME:
    Immutable tenant-scoped pre-provider claim evidence establishing the
    durable execution fence without asserting provider execution, success,
    physical absence, reconciliation, or retry authority.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_evidence_provider_delete_execution_claim.py
COLLABORATION / OWNERSHIP:
    Python EOS Legal Operations owns claim semantics and durable evidence
    meaning. Provider adapters own external capability only; registries own
    persistence mechanics only.
CERTIFICATION OR UPDATE DATE: 2026-10-02
CHANGELOG:
    v1.0.1-L10A2R-A3-P4-P6D2-PROVIDER-DELETE-EXECUTION-CLAIM-GOVERNANCE repairs sovereign source governance metadata and the
    mandatory end seal only. Durable executable VERSION remains
    v1.0.0-L10A2R-A3-P4-P6D2-PROVIDER-DELETE-EXECUTION-CLAIM; SCHEMA, serialized representation, fingerprint inputs,
    hydration compatibility and runtime control flow remain unchanged.
    v1.0.0-L10A2R-A3-P4-P6D2-PROVIDER-DELETE-EXECUTION-CLAIM establishes the immutable pre-provider execution claim.
COMPLIANCE:
    WILSY OS sovereign Legal Operations governance; exact tenant isolation;
    immutable SHA3-512 evidence; fail-closed durable replay semantics.
SECURITY / PRIVACY POSTURE:
    Opaque tenant/provider/object identities and cryptographic fingerprints
    only within this domain contract; no raw secret, IAM, payment, settlement
    or physical-absence authority is introduced.
TENANT BOUNDARY:
    Every claim is bound to the exact tenant inherited from the certified
    cleanup command. Cross-tenant substitution is invalid.
AUTHORITY BOUNDARY:
    Pure immutable evidence only. No provider execution, Mongo persistence,
    retry, reconciliation, cleanup authorization, physical-absence, lifecycle,
    IAM, billing, payment or financial authority.
FINANCIAL AUTHORITY BOUNDARY:
    None. Provider-delete evidence is not payment execution or settlement;
    Kennel EOS remains the exclusive financial execution authority.

DURABLE RUNTIME VERSION:
    v1.0.0-L10A2R-A3-P4-P6D2-PROVIDER-DELETE-EXECUTION-CLAIM

SEMANTIC BOUNDARY:
    CLAIM PRESENT
    != PROVIDER CALL DEFINITELY OCCURRED
    != PROVIDER DELETE SUCCEEDED
    != PROVIDER OBJECT ABSENT
    != EXECUTION EVIDENCE DURABLE
    != RETRY AUTHORIZED

CONCURRENCY BOUNDARY:
    A committed claim must exist before provider execution begins. Presence of
    an unresolved claim blocks automatic competing or repeated provider calls.

CRASH BOUNDARY:
    A claim surviving process failure may represent:
      - crash after claim commit but before provider call;
      - crash during provider call;
      - provider response lost before durable execution evidence;
      - later execution evidence persisted separately.
    This domain does not decide which occurred.
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


VERSION: Final[str] = (
    "v1.0.0-L10A2R-A3-P4-P6D2-"
    "PROVIDER-DELETE-EXECUTION-CLAIM"
)
SCHEMA: Final[str] = (
    "WILSY-LEGAL-EVIDENCE-PROVIDER-DELETE-EXECUTION-CLAIM/V1"
)

_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$")
_SHA3_512 = re.compile(r"^[0-9a-f]{128}$")


class LegalEvidenceProviderDeleteExecutionClaimError(ValueError):
    """Stable pure-domain execution-claim validation failure."""


def _fail(code: str) -> NoReturn:
    raise LegalEvidenceProviderDeleteExecutionClaimError(
        f"L10A2R_A3_P4_P6D2_{code}"
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
    if value.utcoffset() is None:
        _fail(f"{name.upper()}_INVALID")
    return value.astimezone(timezone.utc)


def _payload(
    *,
    claim_id: str,
    tenant_id: str,
    command_id: str,
    cleanup_authorization_id: str,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
    command_fingerprint: str,
    cleanup_authorization_fingerprint: str,
    claimed_at: datetime,
) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "claim_id": claim_id,
        "tenant_id": tenant_id,
        "command_id": command_id,
        "cleanup_authorization_id": cleanup_authorization_id,
        "provider_name": provider_name,
        "storage_reference": storage_reference,
        "object_version_reference": object_version_reference,
        "command_fingerprint": command_fingerprint,
        "cleanup_authorization_fingerprint":
            cleanup_authorization_fingerprint,
        "claimed_at": claimed_at.isoformat(),
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
class LegalEvidenceProviderDeleteExecutionClaim:
    """Immutable pre-provider execution claim."""

    claim_id: str
    tenant_id: str
    command_id: str
    cleanup_authorization_id: str
    provider_name: str
    storage_reference: str
    object_version_reference: str
    command_fingerprint: str
    cleanup_authorization_fingerprint: str
    claimed_at: datetime
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        claim_id = _identity("claim_id", self.claim_id)
        tenant_id = _tenant(self.tenant_id)
        command_id = _identity("command_id", self.command_id)
        cleanup_authorization_id = _identity(
            "cleanup_authorization_id",
            self.cleanup_authorization_id,
        )
        provider_name = _identity(
            "provider_name",
            self.provider_name,
        )
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
        claimed_at = _utc("claimed_at", self.claimed_at)

        if self.schema != SCHEMA:
            _fail("SCHEMA_INVALID")
        if self.version != VERSION:
            _fail("VERSION_INVALID")

        payload = _payload(
            claim_id=claim_id,
            tenant_id=tenant_id,
            command_id=command_id,
            cleanup_authorization_id=cleanup_authorization_id,
            provider_name=provider_name,
            storage_reference=storage_reference,
            object_version_reference=object_version_reference,
            command_fingerprint=command_fingerprint,
            cleanup_authorization_fingerprint=
                cleanup_authorization_fingerprint,
            claimed_at=claimed_at,
        )
        digest = _fingerprint(payload)

        if self.fingerprint:
            supplied = _sha3("fingerprint", self.fingerprint)
            if not hmac.compare_digest(supplied, digest):
                _fail("FINGERPRINT_MISMATCH")

        object.__setattr__(self, "claim_id", claim_id)
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
        object.__setattr__(self, "claimed_at", claimed_at)
        object.__setattr__(self, "fingerprint", digest)

    def to_document(self) -> dict[str, object]:
        """Return exact immutable durable representation."""
        return {
            **_payload(
                claim_id=self.claim_id,
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
                claimed_at=self.claimed_at,
            ),
            "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_document(
        cls,
        document: Mapping[str, object],
    ) -> "LegalEvidenceProviderDeleteExecutionClaim":
        """Hydrate and cryptographically revalidate exact durable bytes."""
        if not isinstance(document, Mapping):
            _fail("DOCUMENT_INVALID")

        expected = {
            "schema",
            "version",
            "claim_id",
            "tenant_id",
            "command_id",
            "cleanup_authorization_id",
            "provider_name",
            "storage_reference",
            "object_version_reference",
            "command_fingerprint",
            "cleanup_authorization_fingerprint",
            "claimed_at",
            "fingerprint",
        }
        if set(document) != expected:
            _fail("DOCUMENT_SCHEMA_INVALID")

        claimed_raw = document["claimed_at"]
        if not isinstance(claimed_raw, str):
            _fail("CLAIMED_AT_INVALID")

        try:
            claimed_at = datetime.fromisoformat(claimed_raw)
        except ValueError as error:
            raise LegalEvidenceProviderDeleteExecutionClaimError(
                "L10A2R_A3_P4_P6D2_CLAIMED_AT_INVALID"
            ) from error

        return cls(
            claim_id=document["claim_id"],  # type: ignore[arg-type]
            tenant_id=document["tenant_id"],  # type: ignore[arg-type]
            command_id=document["command_id"],  # type: ignore[arg-type]
            cleanup_authorization_id=document[
                "cleanup_authorization_id"
            ],  # type: ignore[arg-type]
            provider_name=document["provider_name"],  # type: ignore[arg-type]
            storage_reference=document[
                "storage_reference"
            ],  # type: ignore[arg-type]
            object_version_reference=document[
                "object_version_reference"
            ],  # type: ignore[arg-type]
            command_fingerprint=document[
                "command_fingerprint"
            ],  # type: ignore[arg-type]
            cleanup_authorization_fingerprint=document[
                "cleanup_authorization_fingerprint"
            ],  # type: ignore[arg-type]
            claimed_at=claimed_at,
            schema=document["schema"],  # type: ignore[arg-type]
            version=document["version"],  # type: ignore[arg-type]
            fingerprint=document["fingerprint"],  # type: ignore[arg-type]
        )


def open_legal_evidence_provider_delete_execution_claim(
    *,
    claim_id: str,
    command: LegalEvidenceProviderCleanupCommand,
    claimed_at: datetime,
) -> LegalEvidenceProviderDeleteExecutionClaim:
    """Bind one exact cleanup command before any provider execution begins."""
    if type(command) is not LegalEvidenceProviderCleanupCommand:
        _fail("COMMAND_REQUIRED")

    claimed = _utc("claimed_at", claimed_at)
    if claimed < command.issued_at:
        _fail("CHRONOLOGY_INVALID")

    return LegalEvidenceProviderDeleteExecutionClaim(
        claim_id=_identity("claim_id", claim_id),
        tenant_id=command.tenant_id,
        command_id=command.command_id,
        cleanup_authorization_id=
            command.cleanup_authorization_id,
        provider_name=command.provider_name,
        storage_reference=command.storage_reference,
        object_version_reference=
            command.object_version_reference,
        command_fingerprint=command.fingerprint,
        cleanup_authorization_fingerprint=
            command.cleanup_authorization_fingerprint,
        claimed_at=claimed,
    )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalEvidenceProviderDeleteExecutionClaim",
    "LegalEvidenceProviderDeleteExecutionClaimError",
    "open_legal_evidence_provider_delete_execution_claim",
]

# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_evidence_provider_delete_execution_claim.py
# VERSION: v1.0.1-L10A2R-A3-P4-P6D2-PROVIDER-DELETE-EXECUTION-CLAIM-GOVERNANCE
# AUTHORITY BOUNDARY: immutable pre-provider execution-claim evidence only; no provider execution, retry, reconciliation, physical-absence, IAM, billing, payment or settlement authority
# TENANT POSTURE: exact tenant identity is inherited from the certified cleanup command and remains immutable
# FAIL-CLOSED POSTURE: malformed, divergent, corrupt, foreign-tenant or version-incompatible evidence rejects; an unresolved claim never authorizes provider retry
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# DURABLE RUNTIME VERSION: v1.0.0-L10A2R-A3-P4-P6D2-PROVIDER-DELETE-EXECUTION-CLAIM
# END OF WILSY OS SOVEREIGN ARTIFACT
