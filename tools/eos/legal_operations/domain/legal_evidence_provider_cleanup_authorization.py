"""WILSY OS Legal Evidence provider-cleanup authorization domain.

TITLE: Legal Evidence Provider Cleanup Authorization
VERSION: v1.0.0-L10A2R-C4D6E-A1-PROVIDER-CLEANUP-AUTHORIZATION
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Derive one immutable provider-object cleanup-authorization fact only
         from an exact positive orphan proof and an exact preservation
         composition demonstrating no active preservation block.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_evidence_provider_cleanup_authorization.py

COLLABORATION / OWNERSHIP:
    C4D6D-B owns positive provider-object orphan proof.
    C4D4C owns preservation composition over retention and legal-hold truth.
    C4D6E-A1 owns only the immutable correlation fact that those exact sources
    permit a later separately-authorized cleanup workflow to proceed.

AUTHORITY BOUNDARY:
    Immutable cleanup-authorization evidence only. This module performs no
    provider mutation, object deletion, multipart abort, persistence, IAM
    decision, HTTP/API routing, reconciliation, billing, payment, execution or
    settlement.

SEMANTIC CONTRACT:
    positive orphan proof
    + exact same tenant/provider/storage/object-version preservation composition
    + retention elapsed
    + legal-hold currentness non-blocking
    + NO_PRESERVATION_BLOCK_DEMONSTRATED
    -> immutable cleanup-authorization evidence

    cleanup authorization evidence
    != provider deletion execution
    != proof that deletion occurred

FAIL-CLOSED DECLARATION:
    Wrong source types, cross-scope evidence, active preservation requirements,
    ambiguous/corrupt legal-hold blocking, non-elapsed retention, malformed
    identities/fingerprints, temporal inversion and source-binding drift reject.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
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
    "v1.0.0-L10A2R-C4D6E-A1-PROVIDER-CLEANUP-AUTHORIZATION"
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
    "VERSION",
    "LegalEvidenceProviderCleanupAuthorization",
    "LegalEvidenceProviderCleanupAuthorizationError",
    "authorize_legal_evidence_provider_cleanup",
]


# ARTIFACT: legal_evidence_provider_cleanup_authorization.py
# VERSION: v1.0.0-L10A2R-C4D6E-A1-PROVIDER-CLEANUP-AUTHORIZATION
# AUTHORITY BOUNDARY: immutable provider cleanup-authorization evidence only
# TENANT POSTURE: exact tenant/provider/storage/object-version correlation
# PRESERVATION POSTURE: explicit no-block composition required
# ORPHAN POSTURE: exact positive C4D6D-B orphan proof required
# IAM POSTURE: none; later separately certified gate owns actor authorization
# PERSISTENCE POSTURE: none
# PROVIDER MUTATION POSTURE: none
# DELETION EXECUTION POSTURE: none
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
