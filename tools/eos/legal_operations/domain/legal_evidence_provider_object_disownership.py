"""WILSY OS — explicit Legal Evidence provider-object disownership fact.

TITLE: Legal Evidence Provider Object Disownership
VERSION: v1.0.0-L10A2R-C4D6D-PROVIDER-OBJECT-DISOWNERSHIP
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Represent one explicit, immutable, positively evidenced decision that
         WILSY disowns one exact tenant-scoped provider object version.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_evidence_provider_object_disownership.py
COLLABORATION / OWNERSHIP:
    C4D6C-B owns trusted exhaustive provider coverage verification.
    C4D6D owns only the explicit provider-object disownership fact.
    Later gates own durable persistence, authorized issuance, orphan proof,
    preservation/retention/legal-hold composition, deletion authorization and
    provider deletion execution.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG:
    v1.0.0-L10A2R-C4D6D establishes one immutable positive disownership fact
    over exact tenant/provider/storage/version identity, explicit source and
    authorization evidence, UTC decision time and deterministic SHA3-512
    fingerprint.

AUTHORITY BOUNDARY
------------------
This value records an explicit positive disownership decision only.

It does NOT:
- infer disownership from missing metadata, missing write intent, ABSENT,
  NOT_OBSERVED, cleanup classification or provider coverage;
- prove orphan status;
- prove retention expiry or legal-hold release;
- authorize abort or deletion;
- perform provider mutation;
- establish financial authority.

Construction alone is not authorized issuance. A later separately-certified
issuer/orchestrator must prove actor permission and authorization evidence
before this value may become durable authority.

Financial execution authority remains exclusively with Kennel EOS.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Final, NoReturn


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4D6D-PROVIDER-OBJECT-DISOWNERSHIP"
)

SCHEMA: Final[str] = (
    "wilsy.legal-evidence.provider-object-disownership.v1"
)

_IDENTITY_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$"
)

_SHA3_512_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9a-f]{128}$"
)


class LegalEvidenceProviderObjectDisownershipError(
    ValueError
):
    """Raised when explicit provider-object disownership evidence is invalid."""


def _fail(code: str) -> NoReturn:
    raise LegalEvidenceProviderObjectDisownershipError(
        code
    )


def _identity(
    name: str,
    value: str,
) -> str:
    if (
        not isinstance(value, str)
        or _IDENTITY_RE.fullmatch(value) is None
    ):
        _fail(
            f"L10A2R_C4D6D_{name.upper()}_INVALID"
        )

    return value


def _text(
    name: str,
    value: str,
    *,
    limit: int = 512,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
    ):
        _fail(
            f"L10A2R_C4D6D_{name.upper()}_INVALID"
        )

    return value


def _sha3(
    name: str,
    value: str,
) -> str:
    if (
        not isinstance(value, str)
        or _SHA3_512_RE.fullmatch(value) is None
    ):
        _fail(
            f"L10A2R_C4D6D_{name.upper()}_INVALID"
        )

    return value


def _utc(
    name: str,
    value: datetime,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(
            f"L10A2R_C4D6D_{name.upper()}_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


def _document_str(
    name: str,
    value: object,
) -> str:
    """Narrow one persisted field to exact string type before hydration."""

    if not isinstance(
        value,
        str,
    ):
        _fail(
            f"L10A2R_C4D6D_DOCUMENT_{name.upper()}_TYPE_INVALID"
        )

    return value


def _document_datetime(
    name: str,
    value: object,
) -> datetime:
    """Narrow one persisted field to datetime before semantic validation."""

    if not isinstance(
        value,
        datetime,
    ):
        _fail(
            f"L10A2R_C4D6D_DOCUMENT_{name.upper()}_TYPE_INVALID"
        )

    return value


def _fingerprint(
    *,
    tenant_id: str,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
    disownership_reference: str,
    reason_reference: str,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
    authorization_evidence_reference: str,
    authorization_evidence_fingerprint: str,
    decided_at: datetime,
) -> str:
    payload = {
        "authorization_evidence_fingerprint":
            authorization_evidence_fingerprint,
        "authorization_evidence_reference":
            authorization_evidence_reference,
        "decided_at":
            decided_at.isoformat(),
        "disownership_reference":
            disownership_reference,
        "object_version_reference":
            object_version_reference,
        "provider_name":
            provider_name,
        "reason_reference":
            reason_reference,
        "schema":
            SCHEMA,
        "source_evidence_fingerprint":
            source_evidence_fingerprint,
        "source_evidence_reference":
            source_evidence_reference,
        "storage_reference":
            storage_reference,
        "tenant_id":
            tenant_id,
        "version":
            VERSION,
    }

    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode(
        "utf-8"
    )

    return hashlib.sha3_512(
        encoded
    ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
)
class LegalEvidenceProviderObjectDisownership:
    """One explicit positive disownership fact for one provider object version."""

    tenant_id: str
    provider_name: str
    storage_reference: str
    object_version_reference: str
    disownership_reference: str
    reason_reference: str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    authorization_evidence_reference: str
    authorization_evidence_fingerprint: str
    decided_at: datetime
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = ""

    def __post_init__(
        self,
    ) -> None:
        tenant = _identity(
            "tenant_id",
            self.tenant_id,
        )
        provider = _identity(
            "provider_name",
            self.provider_name,
        )
        storage = _text(
            "storage_reference",
            self.storage_reference,
            limit=2048,
        )
        object_version = _text(
            "object_version_reference",
            self.object_version_reference,
            limit=1024,
        )
        disownership_reference = _identity(
            "disownership_reference",
            self.disownership_reference,
        )
        reason_reference = _text(
            "reason_reference",
            self.reason_reference,
        )
        source_reference = _text(
            "source_evidence_reference",
            self.source_evidence_reference,
            limit=1024,
        )
        source_fingerprint = _sha3(
            "source_evidence_fingerprint",
            self.source_evidence_fingerprint,
        )
        authorization_reference = _text(
            "authorization_evidence_reference",
            self.authorization_evidence_reference,
            limit=1024,
        )
        authorization_fingerprint = _sha3(
            "authorization_evidence_fingerprint",
            self.authorization_evidence_fingerprint,
        )
        decided = _utc(
            "decided_at",
            self.decided_at,
        )

        if self.schema != SCHEMA:
            _fail(
                "L10A2R_C4D6D_SCHEMA_INVALID"
            )

        if self.version != VERSION:
            _fail(
                "L10A2R_C4D6D_VERSION_INVALID"
            )

        digest = _fingerprint(
            tenant_id=tenant,
            provider_name=provider,
            storage_reference=storage,
            object_version_reference=object_version,
            disownership_reference=disownership_reference,
            reason_reference=reason_reference,
            source_evidence_reference=source_reference,
            source_evidence_fingerprint=source_fingerprint,
            authorization_evidence_reference=authorization_reference,
            authorization_evidence_fingerprint=authorization_fingerprint,
            decided_at=decided,
        )

        if self.fingerprint:
            if (
                not isinstance(
                    self.fingerprint,
                    str,
                )
                or not hmac.compare_digest(
                    self.fingerprint,
                    digest,
                )
            ):
                _fail(
                    "L10A2R_C4D6D_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "tenant_id",
            tenant,
        )
        object.__setattr__(
            self,
            "provider_name",
            provider,
        )
        object.__setattr__(
            self,
            "storage_reference",
            storage,
        )
        object.__setattr__(
            self,
            "object_version_reference",
            object_version,
        )
        object.__setattr__(
            self,
            "disownership_reference",
            disownership_reference,
        )
        object.__setattr__(
            self,
            "reason_reference",
            reason_reference,
        )
        object.__setattr__(
            self,
            "source_evidence_reference",
            source_reference,
        )
        object.__setattr__(
            self,
            "source_evidence_fingerprint",
            source_fingerprint,
        )
        object.__setattr__(
            self,
            "authorization_evidence_reference",
            authorization_reference,
        )
        object.__setattr__(
            self,
            "authorization_evidence_fingerprint",
            authorization_fingerprint,
        )
        object.__setattr__(
            self,
            "decided_at",
            decided,
        )
        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    def to_dict(
        self,
    ) -> dict[str, object]:
        """Serialize the exact immutable disownership schema."""

        return {
            "tenant_id":
                self.tenant_id,
            "provider_name":
                self.provider_name,
            "storage_reference":
                self.storage_reference,
            "object_version_reference":
                self.object_version_reference,
            "disownership_reference":
                self.disownership_reference,
            "reason_reference":
                self.reason_reference,
            "source_evidence_reference":
                self.source_evidence_reference,
            "source_evidence_fingerprint":
                self.source_evidence_fingerprint,
            "authorization_evidence_reference":
                self.authorization_evidence_reference,
            "authorization_evidence_fingerprint":
                self.authorization_evidence_fingerprint,
            "decided_at":
                self.decided_at,
            "schema":
                self.schema,
            "version":
                self.version,
            "fingerprint":
                self.fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        value: dict[str, object],
    ) -> "LegalEvidenceProviderObjectDisownership":
        """Strictly hydrate an exact persisted schema and verify fingerprint."""

        if not isinstance(
            value,
            dict,
        ):
            _fail(
                "L10A2R_C4D6D_DOCUMENT_INVALID"
            )

        expected = {
            "tenant_id",
            "provider_name",
            "storage_reference",
            "object_version_reference",
            "disownership_reference",
            "reason_reference",
            "source_evidence_reference",
            "source_evidence_fingerprint",
            "authorization_evidence_reference",
            "authorization_evidence_fingerprint",
            "decided_at",
            "schema",
            "version",
            "fingerprint",
        }

        if set(value) != expected:
            _fail(
                "L10A2R_C4D6D_DOCUMENT_FIELDS_INVALID"
            )

        tenant_id = _document_str(
            "tenant_id",
            value["tenant_id"],
        )
        provider_name = _document_str(
            "provider_name",
            value["provider_name"],
        )
        storage_reference = _document_str(
            "storage_reference",
            value["storage_reference"],
        )
        object_version_reference = _document_str(
            "object_version_reference",
            value["object_version_reference"],
        )
        disownership_reference = _document_str(
            "disownership_reference",
            value["disownership_reference"],
        )
        reason_reference = _document_str(
            "reason_reference",
            value["reason_reference"],
        )
        source_evidence_reference = _document_str(
            "source_evidence_reference",
            value["source_evidence_reference"],
        )
        source_evidence_fingerprint = _document_str(
            "source_evidence_fingerprint",
            value["source_evidence_fingerprint"],
        )
        authorization_evidence_reference = _document_str(
            "authorization_evidence_reference",
            value["authorization_evidence_reference"],
        )
        authorization_evidence_fingerprint = _document_str(
            "authorization_evidence_fingerprint",
            value["authorization_evidence_fingerprint"],
        )
        decided_at = _document_datetime(
            "decided_at",
            value["decided_at"],
        )
        schema = _document_str(
            "schema",
            value["schema"],
        )
        version = _document_str(
            "version",
            value["version"],
        )
        fingerprint = _document_str(
            "fingerprint",
            value["fingerprint"],
        )

        try:
            return cls(
                tenant_id=tenant_id,
                provider_name=provider_name,
                storage_reference=storage_reference,
                object_version_reference=object_version_reference,
                disownership_reference=disownership_reference,
                reason_reference=reason_reference,
                source_evidence_reference=source_evidence_reference,
                source_evidence_fingerprint=source_evidence_fingerprint,
                authorization_evidence_reference=authorization_evidence_reference,
                authorization_evidence_fingerprint=authorization_evidence_fingerprint,
                decided_at=decided_at,
                schema=schema,
                version=version,
                fingerprint=fingerprint,
            )
        except LegalEvidenceProviderObjectDisownershipError:
            raise
        except (
            TypeError,
            ValueError,
        ) as error:
            raise LegalEvidenceProviderObjectDisownershipError(
                "L10A2R_C4D6D_DOCUMENT_INVALID"
            ) from error



__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalEvidenceProviderObjectDisownership",
    "LegalEvidenceProviderObjectDisownershipError",
]


# ARTIFACT: legal_evidence_provider_object_disownership.py
# VERSION: v1.0.0-L10A2R-C4D6D-PROVIDER-OBJECT-DISOWNERSHIP
# AUTHORITY BOUNDARY: explicit positive provider-object disownership fact only
# IDENTITY POSTURE: exact tenant/provider/storage/object-version identity
# EVIDENCE POSTURE: explicit source and authorization evidence are mandatory
# INFERENCE POSTURE: absence, coverage and cleanup classification grant no disownership
# ORPHAN POSTURE: disownership alone is not orphan proof
# RETENTION / HOLD POSTURE: no retention or legal-hold authority
# DELETION POSTURE: no abort, authorization or provider mutation authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
