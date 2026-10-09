"""WILSY OS — Legal Evidence Provider Cleanup Authorization.

TITLE: Legal Evidence Provider Cleanup Authorization
VERSION: v1.1.0-L10A2R-C4D6E-A1-PROVIDER-CLEANUP-AUTHORIZATION
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Derive and strictly hydrate one immutable provider-object cleanup-authorization fact only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_evidence_provider_cleanup_authorization.py
COLLABORATION / OWNERSHIP: Legal Operations / Legal Evidence
CERTIFICATION / UPDATE DATE: 2026-10-02
CHANGELOG:
    v1.1.0 adds strict exact-schema persisted-document hydration and canonical
    document serialization, preserves factory-only issuance, and closes the
    sovereign header/end-seal structural contract.
    v1.0.0 introduced pure immutable cleanup-authorization evidence derived
    from exact orphan-proof and preservation evidence.
COMPLIANCE:
    Fail-closed tenant/object correlation; deterministic canonical evidence;
    SHA3-512 integrity; no inferred provider execution or settlement truth.
SECURITY / PRIVACY POSTURE:
    Opaque tenant/provider/object references and evidence fingerprints only.
    Persisted hydration rejects malformed fields, non-canonical timestamps,
    schema/version drift and fingerprint corruption.
TENANT BOUNDARY:
    Exact tenant + provider + storage reference + object-version correlation.
AUTHORITY BOUNDARY:
    This artifact creates cleanup-authorization evidence only. It does not
    mutate providers, delete objects, perform IAM authorization, persist rows,
    execute billing/payment activity or assert execution/settlement truth.
FINANCIAL AUTHORITY BOUNDARY:
    No financial execution authority. Kennel EOS remains exclusive financial
    execution authority.

SEMANTIC CONTRACT:
    ORPHAN PROOF
    + NO PRESERVATION BLOCK DEMONSTRATED
    + EXACT OBJECT SCOPE
    != PROVIDER DELETE EXECUTION.

FAIL-CLOSED DECLARATION:
    Direct construction, malformed persisted documents, unexpected persisted
    fields, non-canonical timestamps, schema/version drift, source-scope drift,
    later-authority injection and fingerprint mismatch reject.
"""

from __future__ import annotations

import hmac

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re
from typing import Final, cast

from tools.eos.legal_operations.domain.legal_evidence_preservation_assessment import (
    LegalEvidencePreservationState,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_object_orphan_proof import (
    LegalEvidenceProviderObjectOrphanProof,
)
from tools.eos.legal_operations.orchestration.legal_evidence_preservation_composer import (
    LegalEvidencePreservationComposition,
)


VERSION: Final[str] = (
    "v1.1.0-L10A2R-C4D6E-A1-PROVIDER-CLEANUP-AUTHORIZATION"
)
SCHEMA: Final[str] = "wilsy.legal_evidence.provider_cleanup_authorization.v1"

_SHA3_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_OPAQUE_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,511}$"
)


class LegalEvidenceProviderCleanupAuthorizationError(ValueError):
    """Stable fail-closed C4D6E-A1 cleanup-authorization error."""


@dataclass(frozen=True, slots=True)
class _ConstructionProof:
    digest: str


def _fail(code: str) -> None:
    raise LegalEvidenceProviderCleanupAuthorizationError(
        f"L10A2R_C4D6E_A1_{code}"
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


def _enum_value(value: object) -> str:
    raw = getattr(value, "value", value)
    if not isinstance(raw, str) or not raw:
        _fail("SOURCE_ENUM_INVALID")
    return cast(str, raw)


def _preservation_fingerprint(
    value: LegalEvidencePreservationComposition,
) -> str:
    retention = value.retention
    retention_constraint = retention.constraint
    hold = value.legal_hold_currentness

    payload: dict[str, object] = {
        "tenant_id": retention_constraint.tenant_id,
        "provider_name": retention_constraint.provider_name,
        "storage_reference": retention_constraint.storage_reference,
        "object_version_reference":
            retention_constraint.object_version_reference,
        "retention_constraint_fingerprint":
            retention_constraint.fingerprint,
        "retention_assessed_at":
            retention.assessed_at.astimezone(timezone.utc).isoformat(),
        "retention_state": _enum_value(retention.state),
        "retention_elapsed": retention.retention_elapsed,
        "legal_hold_currentness_fingerprint": hold.fingerprint,
        "legal_hold_evaluated_at":
            hold.evaluated_at.astimezone(timezone.utc).isoformat(),
        "legal_hold_state": _enum_value(hold.state),
        "preservation_assessed_at":
            value.assessed_at.astimezone(timezone.utc).isoformat(),
        "preservation_state": _enum_value(value.state),
        "preservation_required": value.preservation_required,
    }
    return _digest(payload)


def _payload(
    *,
    authorization_id: str,
    tenant_id: str,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
    orphan_proof_fingerprint: str,
    disownership_fingerprint: str,
    preservation_fingerprint: str,
    preservation_assessed_at: datetime,
    authorized_at: datetime,
    reason_reference: str,
) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "authorization_version": VERSION,
        "authorization_id": authorization_id,
        "tenant_id": tenant_id,
        "provider_name": provider_name,
        "storage_reference": storage_reference,
        "object_version_reference": object_version_reference,
        "orphan_proof_fingerprint": orphan_proof_fingerprint,
        "disownership_fingerprint": disownership_fingerprint,
        "preservation_fingerprint": preservation_fingerprint,
        "preservation_assessed_at": preservation_assessed_at.isoformat(),
        "authorized_at": authorized_at.isoformat(),
        "reason_reference": reason_reference,
    }


_DOCUMENT_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "authorization_version",
        "authorization_id",
        "tenant_id",
        "provider_name",
        "storage_reference",
        "object_version_reference",
        "orphan_proof_fingerprint",
        "disownership_fingerprint",
        "preservation_fingerprint",
        "preservation_assessed_at",
        "authorized_at",
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
        raise LegalEvidenceProviderCleanupAuthorizationError(
            "L10A2R_C4D6E_A1_DOCUMENT_INVALID"
        ) from error

    if (
        parsed.tzinfo is None
        or parsed.utcoffset() is None
        or parsed.utcoffset() != timedelta(0)
        or parsed.isoformat() != raw
    ):
        _fail("DOCUMENT_TIMESTAMP_INVALID")

    return _utc(name, parsed)


@dataclass(frozen=True, slots=True)
class LegalEvidenceProviderCleanupAuthorization:
    """Immutable authorization evidence for one exact provider object version."""

    authorization_id: str
    tenant_id: str
    provider_name: str
    storage_reference: str
    object_version_reference: str
    orphan_proof_fingerprint: str
    disownership_fingerprint: str
    preservation_fingerprint: str
    preservation_assessed_at: datetime
    authorized_at: datetime
    reason_reference: str
    schema: str = SCHEMA
    authorization_version: str = VERSION
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

        authorization_id = _text(
            "authorization_id",
            self.authorization_id,
        )
        tenant_id = _text("tenant_id", self.tenant_id)
        if tenant_id.lower() in {"global", "*", "all"}:
            _fail("TENANT_INVALID")

        provider_name = _text(
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
        orphan_fingerprint = _sha3(
            "orphan_proof_fingerprint",
            self.orphan_proof_fingerprint,
        )
        disownership_fingerprint = _sha3(
            "disownership_fingerprint",
            self.disownership_fingerprint,
        )
        preservation_fingerprint = _sha3(
            "preservation_fingerprint",
            self.preservation_fingerprint,
        )
        preservation_at = _utc(
            "preservation_assessed_at",
            self.preservation_assessed_at,
        )
        authorized_at = _utc(
            "authorized_at",
            self.authorized_at,
        )
        if authorized_at < preservation_at:
            _fail("AUTHORIZATION_CHRONOLOGY_INVALID")

        reason_reference = _text(
            "reason_reference",
            self.reason_reference,
        )

        if self.schema != SCHEMA:
            _fail("SCHEMA_INVALID")
        if self.authorization_version != VERSION:
            _fail("VERSION_INVALID")

        payload = _payload(
            authorization_id=authorization_id,
            tenant_id=tenant_id,
            provider_name=provider_name,
            storage_reference=storage_reference,
            object_version_reference=object_version_reference,
            orphan_proof_fingerprint=orphan_fingerprint,
            disownership_fingerprint=disownership_fingerprint,
            preservation_fingerprint=preservation_fingerprint,
            preservation_assessed_at=preservation_at,
            authorized_at=authorized_at,
            reason_reference=reason_reference,
        )

        if construction_proof.digest != _digest(payload):
            _fail("SOURCE_BINDING_INVALID")

        object.__setattr__(
            self,
            "preservation_assessed_at",
            preservation_at,
        )
        object.__setattr__(
            self,
            "authorized_at",
            authorized_at,
        )

    def to_dict(self) -> dict[str, object]:
        """Return exact canonical cleanup-authorization evidence."""
        return _payload(
            authorization_id=self.authorization_id,
            tenant_id=self.tenant_id,
            provider_name=self.provider_name,
            storage_reference=self.storage_reference,
            object_version_reference=self.object_version_reference,
            orphan_proof_fingerprint=self.orphan_proof_fingerprint,
            disownership_fingerprint=self.disownership_fingerprint,
            preservation_fingerprint=self.preservation_fingerprint,
            preservation_assessed_at=self.preservation_assessed_at,
            authorized_at=self.authorized_at,
            reason_reference=self.reason_reference,
        )

    @property
    def fingerprint(self) -> str:
        """Return lowercase SHA3-512 over the complete canonical fact."""
        return _digest(self.to_dict())

    def to_document(self) -> dict[str, object]:
        """Return the exact durable document including integrity fingerprint.

        Serialization creates no persistence authority and performs no write.
        The resulting document is suitable only for a separately certified
        registry or equivalent durable boundary.
        """
        document = self.to_dict()
        document["fingerprint"] = self.fingerprint
        return document

    @classmethod
    def from_dict(
        cls,
        value: dict[str, object],
    ) -> "LegalEvidenceProviderCleanupAuthorization":
        """Strictly hydrate exact persisted evidence and verify integrity.

        Hydration validates supplied persisted bytes only. It does not
        rediscover orphan status, reevaluate preservation, grant IAM authority,
        persist data or execute provider deletion.
        """
        if not isinstance(value, dict):
            _fail("DOCUMENT_INVALID")

        if set(value) != _DOCUMENT_FIELDS:
            _fail("DOCUMENT_FIELDS_INVALID")

        schema = _document_str(
            "schema",
            value["schema"],
        )
        authorization_version = _document_str(
            "authorization_version",
            value["authorization_version"],
        )

        if schema != SCHEMA:
            _fail("SCHEMA_INVALID")
        if authorization_version != VERSION:
            _fail("VERSION_INVALID")

        authorization_id = _text(
            "authorization_id",
            _document_str(
                "authorization_id",
                value["authorization_id"],
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
        orphan_proof_fingerprint = _sha3(
            "orphan_proof_fingerprint",
            _document_str(
                "orphan_proof_fingerprint",
                value["orphan_proof_fingerprint"],
            ),
        )
        disownership_fingerprint = _sha3(
            "disownership_fingerprint",
            _document_str(
                "disownership_fingerprint",
                value["disownership_fingerprint"],
            ),
        )
        preservation_fingerprint = _sha3(
            "preservation_fingerprint",
            _document_str(
                "preservation_fingerprint",
                value["preservation_fingerprint"],
            ),
        )
        preservation_assessed_at = _document_datetime(
            "preservation_assessed_at",
            value["preservation_assessed_at"],
        )
        authorized_at = _document_datetime(
            "authorized_at",
            value["authorized_at"],
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
            authorization_id=authorization_id,
            tenant_id=tenant_id,
            provider_name=provider_name,
            storage_reference=storage_reference,
            object_version_reference=object_version_reference,
            orphan_proof_fingerprint=orphan_proof_fingerprint,
            disownership_fingerprint=disownership_fingerprint,
            preservation_fingerprint=preservation_fingerprint,
            preservation_assessed_at=preservation_assessed_at,
            authorized_at=authorized_at,
            reason_reference=reason_reference,
        )

        hydrated = cls(
            authorization_id=authorization_id,
            tenant_id=tenant_id,
            provider_name=provider_name,
            storage_reference=storage_reference,
            object_version_reference=object_version_reference,
            orphan_proof_fingerprint=orphan_proof_fingerprint,
            disownership_fingerprint=disownership_fingerprint,
            preservation_fingerprint=preservation_fingerprint,
            preservation_assessed_at=preservation_assessed_at,
            authorized_at=authorized_at,
            reason_reference=reason_reference,
            schema=schema,
            authorization_version=authorization_version,
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


def authorize_legal_evidence_provider_cleanup(
    *,
    orphan_proof: LegalEvidenceProviderObjectOrphanProof,
    preservation: LegalEvidencePreservationComposition,
    authorization_id: str,
    authorized_at: datetime,
    reason_reference: str,
) -> LegalEvidenceProviderCleanupAuthorization:
    """Derive immutable cleanup authorization from exact certified evidence.

    This function authorizes only the evidence fact. It does not mutate the
    provider, delete an object, persist data, perform IAM authorization or
    assert that cleanup execution occurred.
    """

    if type(orphan_proof) is not LegalEvidenceProviderObjectOrphanProof:
        _fail("ORPHAN_PROOF_REQUIRED")

    if type(preservation) is not LegalEvidencePreservationComposition:
        _fail("PRESERVATION_REQUIRED")

    retention = preservation.retention
    constraint = retention.constraint
    hold = preservation.legal_hold_currentness

    source_scope = (
        orphan_proof.tenant_id,
        orphan_proof.provider_name,
        orphan_proof.storage_reference,
        orphan_proof.object_version_reference,
    )
    preservation_scope = (
        constraint.tenant_id,
        constraint.provider_name,
        constraint.storage_reference,
        constraint.object_version_reference,
    )
    hold_scope = (
        hold.tenant_id,
        hold.provider_name,
        hold.storage_reference,
        hold.object_version_reference,
    )

    if (
        source_scope != preservation_scope
        or source_scope != hold_scope
    ):
        _fail("SOURCE_SCOPE_MISMATCH")

    if (
        preservation.state
        is not LegalEvidencePreservationState
        .NO_PRESERVATION_BLOCK_DEMONSTRATED
        or preservation.preservation_required is not False
        or retention.retention_elapsed is not True
        or hold.preservation_blocking is not False
    ):
        _fail("PRESERVATION_CLEARANCE_REQUIRED")

    if (
        preservation.orphan_proven is not False
        or preservation.deletion_authorized is not False
        or preservation.provider_delete_authorized is not False
        or retention.orphan_proven is not False
        or retention.provider_delete_authorized is not False
    ):
        _fail("SOURCE_LATER_AUTHORITY_FORBIDDEN")

    authorization_identity = _text(
        "authorization_id",
        authorization_id,
    )
    reason = _text(
        "reason_reference",
        reason_reference,
    )
    authorized = _utc(
        "authorized_at",
        authorized_at,
    )
    preservation_at = _utc(
        "preservation_assessed_at",
        preservation.assessed_at,
    )

    if authorized < preservation_at:
        _fail("AUTHORIZATION_CHRONOLOGY_INVALID")

    orphan_fingerprint = _sha3(
        "orphan_proof_fingerprint",
        orphan_proof.fingerprint,
    )
    disownership_fingerprint = _sha3(
        "disownership_fingerprint",
        orphan_proof.disownership_fingerprint,
    )
    preservation_fingerprint = _preservation_fingerprint(
        preservation
    )

    payload = _payload(
        authorization_id=authorization_identity,
        tenant_id=_text("tenant_id", orphan_proof.tenant_id),
        provider_name=_text(
            "provider_name",
            orphan_proof.provider_name,
        ),
        storage_reference=_text(
            "storage_reference",
            orphan_proof.storage_reference,
        ),
        object_version_reference=_text(
            "object_version_reference",
            orphan_proof.object_version_reference,
        ),
        orphan_proof_fingerprint=orphan_fingerprint,
        disownership_fingerprint=disownership_fingerprint,
        preservation_fingerprint=preservation_fingerprint,
        preservation_assessed_at=preservation_at,
        authorized_at=authorized,
        reason_reference=reason,
    )

    return LegalEvidenceProviderCleanupAuthorization(
        authorization_id=authorization_identity,
        tenant_id=orphan_proof.tenant_id,
        provider_name=orphan_proof.provider_name,
        storage_reference=orphan_proof.storage_reference,
        object_version_reference=orphan_proof.object_version_reference,
        orphan_proof_fingerprint=orphan_fingerprint,
        disownership_fingerprint=disownership_fingerprint,
        preservation_fingerprint=preservation_fingerprint,
        preservation_assessed_at=preservation_at,
        authorized_at=authorized,
        reason_reference=reason,
        _construction_proof=_ConstructionProof(
            digest=_digest(payload)
        ),
    )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalEvidenceProviderCleanupAuthorization",
    "LegalEvidenceProviderCleanupAuthorizationError",
    "authorize_legal_evidence_provider_cleanup",
]


# ARTIFACT: legal_evidence_provider_cleanup_authorization.py
# VERSION: v1.1.0-L10A2R-C4D6E-A1-PROVIDER-CLEANUP-AUTHORIZATION
# AUTHORITY BOUNDARY: immutable provider cleanup-authorization evidence only
# TENANT POSTURE: exact tenant/provider/storage/object-version correlation
# PRESERVATION POSTURE: explicit no-block composition required
# ORPHAN POSTURE: exact positive C4D6D-B orphan proof required
# IAM POSTURE: none; later separately certified gate owns actor authorization
# PERSISTENCE POSTURE: strict hydration/serialization only; no registry write
# PROVIDER MUTATION POSTURE: none
# DELETION EXECUTION POSTURE: none
# FAIL-CLOSED POSTURE: malformed/corrupt persisted evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
