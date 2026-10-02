"""WILSY OS — Legal Evidence Provider Cleanup Command Domain.

TITLE: Legal Evidence Provider Cleanup Command
VERSION: v1.1.0-L10A2R-C4D6E-A3-P3-P1-CLEANUP-COMMAND-DURABLE-HYDRATION
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Bind one exact certified cleanup-authorization fact to one exact
         successful actor-authorization evidence fact without executing cleanup.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_evidence_provider_cleanup_command.py
COLLABORATION / OWNERSHIP: Legal Operations / Legal Evidence
CERTIFICATION / UPDATE DATE: 2026-10-02
CHANGELOG:
    v1.1.0-L10A2R-C4D6E-A3-P3-P1-CLEANUP-COMMAND-DURABLE-HYDRATION adds strict exact-schema durable serialization and hydration,
    preserves factory-only issuance semantics, verifies SHA3-512 integrity and
    creates no persistence or provider-execution authority.
    v1.0.0 establishes the immutable cleanup command domain. Issuance requires
    one exact LegalEvidenceProviderCleanupAuthorization plus one exact
    TenantAuthorizationDecisionEvidence for legal_evidence_cleanup_authorize /
    legal_operations:evidence_cleanup:authorize, tenant_legal_partner and
    LEGAL_PARTNER. The actor authorization must name the cleanup authorization
    as its subject and bind its exact SHA3-512 fingerprint.
COMPLIANCE:
    POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE:
    Opaque identities only; deterministic canonical serialization; SHA3-512
    integrity; exact tenant/object/actor/evidence correlation; fail closed.
TENANT BOUNDARY:
    Cleanup evidence, actor evidence and resulting command must bind one exact
    tenant. No cross-tenant inference or wildcard tenant is accepted.
AUTHORITY BOUNDARY:
    This artifact is command-intent evidence only. Actor authorization is not
    provider execution. Cleanup authorization is not provider execution. The
    command does not mutate storage, call provider APIs, persist rows, delete
    objects, prove deletion, release preservation constraints, or authorize
    financial execution.
FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains the exclusive financial execution authority.

SEMANTIC CONTRACT:
    CERTIFIED CLEANUP AUTHORIZATION
    + CERTIFIED ACTOR AUTHORIZATION EVIDENCE
    + EXACT SUBJECT / FINGERPRINT BINDING
    = IMMUTABLE CLEANUP COMMAND INTENT

    CLEANUP COMMAND INTENT != PROVIDER DELETE EXECUTION.

FAIL-CLOSED DECLARATION:
    Direct construction, wrong source types, tenant/scope mismatch, wrong IAM
    operation/permission/business-role/authorization-role, subject mismatch,
    fingerprint mismatch, malformed identity, chronology inversion and later
    execution-authority injection reject.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Final, cast

from tools.eos.auth.tenant_authorization_decision_evidence import (
    TenantAuthorizationDecisionEvidence,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_authorization import (
    LegalEvidenceProviderCleanupAuthorization,
)


VERSION: Final[str] = (
    "v1.1.0-L10A2R-C4D6E-A3-P3-P1-CLEANUP-COMMAND-DURABLE-HYDRATION"
)
SCHEMA: Final[str] = "wilsy.legal_evidence.provider_cleanup_command.v1"

CLEANUP_OPERATION: Final[str] = "legal_evidence_cleanup_authorize"
CLEANUP_PERMISSION: Final[str] = (
    "legal_operations:evidence_cleanup:authorize"
)
CLEANUP_BUSINESS_ROLE: Final[str] = "tenant_legal_partner"
CLEANUP_AUTHORIZATION_ROLE: Final[str] = "LEGAL_PARTNER"

_SHA3_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_OPAQUE_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,511}$"
)


class LegalEvidenceProviderCleanupCommandError(ValueError):
    """Stable fail-closed A3-P2 cleanup-command domain error."""


@dataclass(frozen=True, slots=True)
class _ConstructionProof:
    digest: str


def _fail(code: str) -> None:
    raise LegalEvidenceProviderCleanupCommandError(
        f"L10A2R_C4D6E_A3_P2_{code}"
    )


def _text(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or _OPAQUE_RE.fullmatch(value) is None
    ):
        _fail(f"{name.upper()}_INVALID")
    return cast(str, value)


def _sha3(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or _SHA3_RE.fullmatch(value) is None
    ):
        _fail(f"{name.upper()}_INVALID")
    return cast(str, value)


def _utc(name: str, value: object) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(f"{name.upper()}_INVALID")
    return cast(datetime, value).astimezone(timezone.utc)


def _digest(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def cleanup_authorization_subject_reference(
    authorization_id: str,
) -> str:
    """Return the canonical IAM subject reference for one cleanup authorization."""
    identity = _text("authorization_id", authorization_id)
    return (
        "legal-evidence-provider-cleanup-authorization:"
        + identity
    )


_DOCUMENT_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "command_version",
        "command_id",
        "tenant_id",
        "principal_id",
        "provider_name",
        "storage_reference",
        "object_version_reference",
        "cleanup_authorization_id",
        "cleanup_authorization_fingerprint",
        "tenant_authorization_decision_id",
        "tenant_authorization_evidence_fingerprint",
        "issued_at",
        "reason_reference",
        "fingerprint",
    }
)


def _document_str(
    name: str,
    value: object,
) -> str:
    """Require one exact persisted string field."""
    if not isinstance(value, str):
        _fail("DOCUMENT_INVALID")
    return cast(str, value)


def _document_datetime(
    name: str,
    value: object,
) -> datetime:
    """Hydrate one canonical UTC ISO-8601 persisted timestamp."""
    raw = _document_str(name, value)

    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError as error:
        raise LegalEvidenceProviderCleanupCommandError(
            "L10A2R_C4D6E_A3_P3_P1_DOCUMENT_INVALID"
        ) from error

    if (
        parsed.tzinfo is None
        or parsed.utcoffset() is None
        or parsed.astimezone(timezone.utc).isoformat() != raw
    ):
        _fail("DOCUMENT_TIMESTAMP_INVALID")

    return _utc(name, parsed)


def _payload(
    *,
    command_id: str,
    tenant_id: str,
    principal_id: str,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
    cleanup_authorization_id: str,
    cleanup_authorization_fingerprint: str,
    tenant_authorization_decision_id: str,
    tenant_authorization_evidence_fingerprint: str,
    issued_at: datetime,
    reason_reference: str,
) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "command_version": VERSION,
        "command_id": command_id,
        "tenant_id": tenant_id,
        "principal_id": principal_id,
        "provider_name": provider_name,
        "storage_reference": storage_reference,
        "object_version_reference": object_version_reference,
        "cleanup_authorization_id": cleanup_authorization_id,
        "cleanup_authorization_fingerprint":
            cleanup_authorization_fingerprint,
        "tenant_authorization_decision_id":
            tenant_authorization_decision_id,
        "tenant_authorization_evidence_fingerprint":
            tenant_authorization_evidence_fingerprint,
        "issued_at": issued_at.isoformat(),
        "reason_reference": reason_reference,
    }


@dataclass(frozen=True, slots=True)
class LegalEvidenceProviderCleanupCommand:
    """Immutable command intent for one exact provider-object version.

    Construction proves only that certified cleanup authorization and certified
    actor authorization evidence were correlated. This value never performs,
    schedules, retries, observes or proves provider deletion.
    """

    command_id: str
    tenant_id: str
    principal_id: str
    provider_name: str
    storage_reference: str
    object_version_reference: str
    cleanup_authorization_id: str
    cleanup_authorization_fingerprint: str
    tenant_authorization_decision_id: str
    tenant_authorization_evidence_fingerprint: str
    issued_at: datetime
    reason_reference: str
    schema: str = SCHEMA
    command_version: str = VERSION
    _construction_proof: object = field(
        default=None,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        proof = self._construction_proof
        if type(proof) is not _ConstructionProof:
            _fail("FACTORY_REQUIRED")
        construction_proof = cast(_ConstructionProof, proof)

        command_id = _text("command_id", self.command_id)
        tenant_id = _text("tenant_id", self.tenant_id)
        if tenant_id.lower() in {"global", "*", "all"}:
            _fail("TENANT_INVALID")

        principal_id = _text("principal_id", self.principal_id)
        provider_name = _text("provider_name", self.provider_name)
        storage_reference = _text(
            "storage_reference",
            self.storage_reference,
        )
        object_version_reference = _text(
            "object_version_reference",
            self.object_version_reference,
        )
        cleanup_authorization_id = _text(
            "cleanup_authorization_id",
            self.cleanup_authorization_id,
        )
        cleanup_authorization_fingerprint = _sha3(
            "cleanup_authorization_fingerprint",
            self.cleanup_authorization_fingerprint,
        )
        tenant_authorization_decision_id = _text(
            "tenant_authorization_decision_id",
            self.tenant_authorization_decision_id,
        )
        tenant_authorization_evidence_fingerprint = _sha3(
            "tenant_authorization_evidence_fingerprint",
            self.tenant_authorization_evidence_fingerprint,
        )
        issued_at = _utc("issued_at", self.issued_at)
        reason_reference = _text(
            "reason_reference",
            self.reason_reference,
        )

        if self.schema != SCHEMA:
            _fail("SCHEMA_INVALID")
        if self.command_version != VERSION:
            _fail("VERSION_INVALID")

        payload = _payload(
            command_id=command_id,
            tenant_id=tenant_id,
            principal_id=principal_id,
            provider_name=provider_name,
            storage_reference=storage_reference,
            object_version_reference=object_version_reference,
            cleanup_authorization_id=cleanup_authorization_id,
            cleanup_authorization_fingerprint=
                cleanup_authorization_fingerprint,
            tenant_authorization_decision_id=
                tenant_authorization_decision_id,
            tenant_authorization_evidence_fingerprint=
                tenant_authorization_evidence_fingerprint,
            issued_at=issued_at,
            reason_reference=reason_reference,
        )

        if construction_proof.digest != _digest(payload):
            _fail("SOURCE_BINDING_INVALID")

        object.__setattr__(self, "issued_at", issued_at)

    def to_dict(self) -> dict[str, object]:
        """Return the exact canonical command-intent payload."""
        return _payload(
            command_id=self.command_id,
            tenant_id=self.tenant_id,
            principal_id=self.principal_id,
            provider_name=self.provider_name,
            storage_reference=self.storage_reference,
            object_version_reference=self.object_version_reference,
            cleanup_authorization_id=self.cleanup_authorization_id,
            cleanup_authorization_fingerprint=
                self.cleanup_authorization_fingerprint,
            tenant_authorization_decision_id=
                self.tenant_authorization_decision_id,
            tenant_authorization_evidence_fingerprint=
                self.tenant_authorization_evidence_fingerprint,
            issued_at=self.issued_at,
            reason_reference=self.reason_reference,
        )

    @property
    def fingerprint(self) -> str:
        """Return lowercase SHA3-512 over the complete command intent."""
        return _digest(self.to_dict())

    def to_document(self) -> dict[str, object]:
        """Return exact durable command evidence including fingerprint.

        Serialization grants no persistence, replay, provider mutation or
        deletion-execution authority.
        """
        document = self.to_dict()
        document["fingerprint"] = self.fingerprint
        return document

    @classmethod
    def from_dict(
        cls,
        value: dict[str, object],
    ) -> "LegalEvidenceProviderCleanupCommand":
        """Strictly hydrate exact persisted command evidence.

        Hydration validates supplied durable bytes only. It does not authorize
        an actor, rediscover cleanup eligibility, persist a row, call a
        provider or prove deletion execution.
        """
        if not isinstance(value, dict):
            _fail("DOCUMENT_INVALID")

        if set(value) != _DOCUMENT_FIELDS:
            _fail("DOCUMENT_FIELDS_INVALID")

        schema = _document_str(
            "schema",
            value["schema"],
        )
        command_version = _document_str(
            "command_version",
            value["command_version"],
        )

        if schema != SCHEMA:
            _fail("SCHEMA_INVALID")
        if command_version != VERSION:
            _fail("VERSION_INVALID")

        command_id = _text(
            "command_id",
            _document_str(
                "command_id",
                value["command_id"],
            ),
        )
        tenant_id = _text(
            "tenant_id",
            _document_str(
                "tenant_id",
                value["tenant_id"],
            ),
        )
        if tenant_id.lower() in {"global", "*", "all"}:
            _fail("TENANT_INVALID")

        principal_id = _text(
            "principal_id",
            _document_str(
                "principal_id",
                value["principal_id"],
            ),
        )
        provider_name = _text(
            "provider_name",
            _document_str(
                "provider_name",
                value["provider_name"],
            ),
        )
        storage_reference = _text(
            "storage_reference",
            _document_str(
                "storage_reference",
                value["storage_reference"],
            ),
        )
        object_version_reference = _text(
            "object_version_reference",
            _document_str(
                "object_version_reference",
                value["object_version_reference"],
            ),
        )
        cleanup_authorization_id = _text(
            "cleanup_authorization_id",
            _document_str(
                "cleanup_authorization_id",
                value["cleanup_authorization_id"],
            ),
        )
        cleanup_authorization_fingerprint = _sha3(
            "cleanup_authorization_fingerprint",
            _document_str(
                "cleanup_authorization_fingerprint",
                value["cleanup_authorization_fingerprint"],
            ),
        )
        tenant_authorization_decision_id = _text(
            "tenant_authorization_decision_id",
            _document_str(
                "tenant_authorization_decision_id",
                value["tenant_authorization_decision_id"],
            ),
        )
        tenant_authorization_evidence_fingerprint = _sha3(
            "tenant_authorization_evidence_fingerprint",
            _document_str(
                "tenant_authorization_evidence_fingerprint",
                value["tenant_authorization_evidence_fingerprint"],
            ),
        )
        issued_at = _document_datetime(
            "issued_at",
            value["issued_at"],
        )
        reason_reference = _text(
            "reason_reference",
            _document_str(
                "reason_reference",
                value["reason_reference"],
            ),
        )
        persisted_fingerprint = _sha3(
            "fingerprint",
            _document_str(
                "fingerprint",
                value["fingerprint"],
            ),
        )

        payload = _payload(
            command_id=command_id,
            tenant_id=tenant_id,
            principal_id=principal_id,
            provider_name=provider_name,
            storage_reference=storage_reference,
            object_version_reference=object_version_reference,
            cleanup_authorization_id=cleanup_authorization_id,
            cleanup_authorization_fingerprint=
                cleanup_authorization_fingerprint,
            tenant_authorization_decision_id=
                tenant_authorization_decision_id,
            tenant_authorization_evidence_fingerprint=
                tenant_authorization_evidence_fingerprint,
            issued_at=issued_at,
            reason_reference=reason_reference,
        )

        hydrated = cls(
            command_id=command_id,
            tenant_id=tenant_id,
            principal_id=principal_id,
            provider_name=provider_name,
            storage_reference=storage_reference,
            object_version_reference=object_version_reference,
            cleanup_authorization_id=cleanup_authorization_id,
            cleanup_authorization_fingerprint=
                cleanup_authorization_fingerprint,
            tenant_authorization_decision_id=
                tenant_authorization_decision_id,
            tenant_authorization_evidence_fingerprint=
                tenant_authorization_evidence_fingerprint,
            issued_at=issued_at,
            reason_reference=reason_reference,
            schema=schema,
            command_version=command_version,
            _construction_proof=_ConstructionProof(
                digest=_digest(payload)
            ),
        )

        if not hmac.compare_digest(
            persisted_fingerprint,
            hydrated.fingerprint,
        ):
            _fail("FINGERPRINT_MISMATCH")

        return hydrated


def issue_legal_evidence_provider_cleanup_command(
    *,
    cleanup_authorization: LegalEvidenceProviderCleanupAuthorization,
    actor_authorization: TenantAuthorizationDecisionEvidence,
    command_id: str,
    issued_at: datetime,
    reason_reference: str,
) -> LegalEvidenceProviderCleanupCommand:
    """Issue immutable cleanup command intent from two certified evidence facts.

    The function validates evidence correlation only. It does not persist the
    command, call storage/provider APIs, delete objects, retry provider work,
    observe deletion, release legal holds, or establish financial execution.
    """

    if type(cleanup_authorization) is not (
        LegalEvidenceProviderCleanupAuthorization
    ):
        _fail("CLEANUP_AUTHORIZATION_REQUIRED")

    if type(actor_authorization) is not TenantAuthorizationDecisionEvidence:
        _fail("ACTOR_AUTHORIZATION_REQUIRED")

    if actor_authorization.operation != CLEANUP_OPERATION:
        _fail("ACTOR_OPERATION_MISMATCH")
    if actor_authorization.permission != CLEANUP_PERMISSION:
        _fail("ACTOR_PERMISSION_MISMATCH")
    if actor_authorization.business_role != CLEANUP_BUSINESS_ROLE:
        _fail("ACTOR_BUSINESS_ROLE_MISMATCH")
    if (
        actor_authorization.authorization_role
        != CLEANUP_AUTHORIZATION_ROLE
    ):
        _fail("ACTOR_AUTHORIZATION_ROLE_MISMATCH")

    if actor_authorization.tenant_id != cleanup_authorization.tenant_id:
        _fail("TENANT_MISMATCH")

    expected_subject = cleanup_authorization_subject_reference(
        cleanup_authorization.authorization_id
    )
    if actor_authorization.subject_reference != expected_subject:
        _fail("ACTOR_SUBJECT_MISMATCH")

    if actor_authorization.subject_evidence_fingerprint != (
        cleanup_authorization.fingerprint
    ):
        _fail("ACTOR_SUBJECT_FINGERPRINT_MISMATCH")

    issued = _utc("issued_at", issued_at)
    if (
        issued < cleanup_authorization.authorized_at
        or issued < actor_authorization.authorized_at
    ):
        _fail("COMMAND_CHRONOLOGY_INVALID")

    command_identity = _text("command_id", command_id)
    reason = _text("reason_reference", reason_reference)

    cleanup_fingerprint = _sha3(
        "cleanup_authorization_fingerprint",
        cleanup_authorization.fingerprint,
    )
    actor_fingerprint = _sha3(
        "tenant_authorization_evidence_fingerprint",
        actor_authorization.authorization_evidence_fingerprint,
    )

    payload = _payload(
        command_id=command_identity,
        tenant_id=_text(
            "tenant_id",
            cleanup_authorization.tenant_id,
        ),
        principal_id=_text(
            "principal_id",
            actor_authorization.principal_id,
        ),
        provider_name=_text(
            "provider_name",
            cleanup_authorization.provider_name,
        ),
        storage_reference=_text(
            "storage_reference",
            cleanup_authorization.storage_reference,
        ),
        object_version_reference=_text(
            "object_version_reference",
            cleanup_authorization.object_version_reference,
        ),
        cleanup_authorization_id=_text(
            "cleanup_authorization_id",
            cleanup_authorization.authorization_id,
        ),
        cleanup_authorization_fingerprint=cleanup_fingerprint,
        tenant_authorization_decision_id=_text(
            "tenant_authorization_decision_id",
            actor_authorization.authorization_decision_id,
        ),
        tenant_authorization_evidence_fingerprint=actor_fingerprint,
        issued_at=issued,
        reason_reference=reason,
    )

    return LegalEvidenceProviderCleanupCommand(
        command_id=command_identity,
        tenant_id=cleanup_authorization.tenant_id,
        principal_id=actor_authorization.principal_id,
        provider_name=cleanup_authorization.provider_name,
        storage_reference=cleanup_authorization.storage_reference,
        object_version_reference=
            cleanup_authorization.object_version_reference,
        cleanup_authorization_id=
            cleanup_authorization.authorization_id,
        cleanup_authorization_fingerprint=cleanup_fingerprint,
        tenant_authorization_decision_id=
            actor_authorization.authorization_decision_id,
        tenant_authorization_evidence_fingerprint=actor_fingerprint,
        issued_at=issued,
        reason_reference=reason,
        _construction_proof=_ConstructionProof(
            digest=_digest(payload)
        ),
    )


__all__ = [
    "VERSION",
    "SCHEMA",
    "CLEANUP_OPERATION",
    "CLEANUP_PERMISSION",
    "CLEANUP_BUSINESS_ROLE",
    "CLEANUP_AUTHORIZATION_ROLE",
    "LegalEvidenceProviderCleanupCommand",
    "LegalEvidenceProviderCleanupCommandError",
    "cleanup_authorization_subject_reference",
    "issue_legal_evidence_provider_cleanup_command",
]


# ARTIFACT: legal_evidence_provider_cleanup_command.py
# VERSION: v1.1.0-L10A2R-C4D6E-A3-P3-P1-CLEANUP-COMMAND-DURABLE-HYDRATION
# AUTHORITY BOUNDARY: immutable cleanup command intent only; never execution
# TENANT POSTURE: cleanup authorization + actor evidence must bind one tenant
# OBJECT POSTURE: exact provider/storage/object-version inherited from A2 evidence
# IAM POSTURE: exact cleanup operation/permission/business/final-role evidence
# PERSISTENCE POSTURE: strict serialization/hydration only; no registry write
# PROVIDER MUTATION POSTURE: none
# DELETION EXECUTION POSTURE: none
# FAIL-CLOSED POSTURE: malformed, crossed, mismatched or stale evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
