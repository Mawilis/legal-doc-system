"""WILSY OS HR Document Commit-Uncertainty Domain.

TITLE: HR Document Commit Uncertainty
VERSION: v1.0.0-P0-C12F6C-HR-DOCUMENT-COMMIT-UNCERTAINTY
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Represent one exact HR document provider completion for which durable
provider-object evidence is proven but the corresponding immutable
HrDocument Mongo control-plane commit is not yet proven durable.

EPITOME:
EXACT HR BINARY WRITE INTENT
+ VERIFIED PROVIDER OBJECT EVIDENCE
+ DOCUMENT-CLASS / PROVENANCE INPUTS
+ COMMIT OUTCOME NOT PROVEN
-> IMMUTABLE HR DOCUMENT COMMIT UNCERTAINTY

COMMIT UNCERTAINTY:
- is durable evidence for later reconciliation;
- is not proof Mongo committed or failed;
- is not proof an object is orphaned;
- is not provider-delete authority;
- is not retention-disposal authority;
- is not IAM or HTTP authority;
- is not billing, payment, settlement or financial authority.

AUTHORITY BOUNDARY:
Immutable HR provider-complete / Mongo-unproven evidence only.
This artifact grants no Mongo persistence or transaction authority,
provider deletion or cleanup authority, retention/disposal authority,
IAM or HTTP authority, billing, payment, settlement or financial authority.

RECONSTRUCTION:
The value contains only immutable metadata needed to reconstruct the
exact intended HrDocument after restart. Raw document bytes are never
stored here. Provider coordinates are derived from certified provider
evidence and never accepted independently as caller authority.

CONSISTENCY BOUNDARY:
S3/provider completion occurs outside MongoDB transactions. This domain
does not claim atomicity between provider bytes and Mongo metadata.

ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/hr_document_commit_uncertainty.py

CERTIFICATION / UPDATE DATE: 2026-10-05

CHANGELOG:
2026-10-05 v1.0.0-P0-C12F6C-HR-DOCUMENT-COMMIT-UNCERTAINTY
establishes immutable HR provider-complete / Mongo-unproven evidence.

FAIL-CLOSED DECLARATION:
Wrong types, malformed identities, pseudo tenants, schema/version drift,
provider/write-intent scope divergence, digest corruption, impossible
timestamps, self-supersession and fingerprint tampering reject.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Any, Final, cast

from tools.eos.saas.domain.hr_document import (
    HrDocument,
    HrDocumentClass,
    HrDocumentDomainError,
)
from tools.eos.saas.hr.hr_document_storage import (
    HrDocumentBinaryObjectEvidence,
    HrDocumentBinaryStoragePortError,
    HrDocumentBinaryWriteIntent,
    validate_object_evidence_for_intent,
)


VERSION: Final[str] = (
    "v1.0.0-P0-C12F6C-"
    "HR-DOCUMENT-COMMIT-UNCERTAINTY"
)

SCHEMA: Final[str] = (
    "WILSY-HR-DOCUMENT-COMMIT-UNCERTAINTY/V1"
)

_UNCERTAINTY_PREFIX: Final[str] = (
    "hr-document-commit-uncertainty:"
)

_IDENTITY_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:@/-]{0,511}$"
)

_SHA3_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9a-f]{128}$"
)

_PSEUDO_TENANTS: Final[frozenset[str]] = frozenset(
    {
        "*",
        "default",
        "global",
        "global_root",
        "master",
        "root",
    }
)

_FIELDS: Final[tuple[str, ...]] = (
    "uncertainty_id",
    "tenant_id",
    "employee_id",
    "document_id",
    "document_version_id",
    "ingestion_reference",
    "media_type",
    "original_filename",
    "admitted_max_content_length",
    "document_class",
    "created_at",
    "created_by_principal_id",
    "retention_until",
    "legal_hold",
    "supersedes_version_id",
    "provider_name",
    "storage_reference",
    "object_version_reference",
    "provider_integrity_reference",
    "write_intent_fingerprint",
    "content_length",
    "content_fingerprint",
    "detected_at",
    "schema",
    "uncertainty_version",
    "fingerprint",
)


class HrDocumentCommitUncertaintyError(
    ValueError
):
    """Stable fail-closed HR commit-uncertainty domain error."""


def _fail(
    code: str,
) -> None:
    raise HrDocumentCommitUncertaintyError(
        code
    )


def _identity(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or value != value.strip()
        or _IDENTITY_RE.fullmatch(
            value
        ) is None
    ):
        _fail(
            f"P0_C12F6C_{name.upper()}_INVALID"
        )

    return cast(
        str,
        value,
    )


def _tenant(
    value: object,
) -> str:
    tenant = _identity(
        "tenant_id",
        value,
    )

    if (
        tenant.casefold()
        in _PSEUDO_TENANTS
    ):
        _fail(
            "P0_C12F6C_TENANT_REQUIRED"
        )

    return tenant


def _text(
    name: str,
    value: object,
    *,
    limit: int = 2048,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value
        or value != value.strip()
        or len(
            value
        ) > limit
        or any(
            ord(character) < 32
            for character in value
        )
    ):
        _fail(
            f"P0_C12F6C_{name.upper()}_INVALID"
        )

    return cast(
        str,
        value,
    )


def _positive_int(
    name: str,
    value: object,
) -> int:
    if (
        isinstance(
            value,
            bool,
        )
        or not isinstance(
            value,
            int,
        )
        or value <= 0
    ):
        _fail(
            f"P0_C12F6C_{name.upper()}_INVALID"
        )

    return cast(
        int,
        value,
    )


def _sha3(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or _SHA3_RE.fullmatch(
            value
        ) is None
    ):
        _fail(
            f"P0_C12F6C_{name.upper()}_INVALID"
        )

    return cast(
        str,
        value,
    )


def _utc(
    name: str,
    value: object,
) -> datetime:
    if isinstance(
        value,
        str,
    ):
        try:
            value = datetime.fromisoformat(
                value.replace(
                    "Z",
                    "+00:00",
                )
            )
        except ValueError:
            _fail(
                f"P0_C12F6C_{name.upper()}_INVALID"
            )

    if (
        not isinstance(
            value,
            datetime,
        )
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(
            f"P0_C12F6C_{name.upper()}_UTC_REQUIRED"
        )

    return cast(
        datetime,
        value,
    ).astimezone(
        timezone.utc
    )


def _timestamp(
    value: datetime,
) -> str:
    return (
        value.astimezone(
            timezone.utc
        )
        .isoformat()
    )


def _serialize_value(
    value: object,
) -> object:
    if isinstance(
        value,
        datetime,
    ):
        return _timestamp(
            value
        )

    if isinstance(
        value,
        HrDocumentClass,
    ):
        return value.value

    return value


def _uncertainty_identity(
    *,
    tenant_id: str,
    employee_id: str,
    document_id: str,
    document_version_id: str,
    ingestion_reference: str,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
    write_intent_fingerprint: str,
    content_length: int,
    content_fingerprint: str,
) -> str:
    payload = {
        "tenant_id":
            tenant_id,
        "employee_id":
            employee_id,
        "document_id":
            document_id,
        "document_version_id":
            document_version_id,
        "ingestion_reference":
            ingestion_reference,
        "provider_name":
            provider_name,
        "storage_reference":
            storage_reference,
        "object_version_reference":
            object_version_reference,
        "write_intent_fingerprint":
            write_intent_fingerprint,
        "content_length":
            content_length,
        "content_fingerprint":
            content_fingerprint,
    }

    raw = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    ).encode(
        "utf-8"
    )

    return (
        _UNCERTAINTY_PREFIX
        + hashlib.sha3_512(
            raw
        ).hexdigest()
    )


def _fingerprint(
    payload: Mapping[
        str,
        object,
    ],
) -> str:
    raw = json.dumps(
        dict(
            payload
        ),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    ).encode(
        "utf-8"
    )

    return hashlib.sha3_512(
        raw
    ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
)
class HrDocumentCommitUncertainty:
    """Immutable provider-complete / Mongo-unproven HR evidence."""

    uncertainty_id: str

    tenant_id: str
    employee_id: str
    document_id: str
    document_version_id: str
    ingestion_reference: str

    media_type: str
    original_filename: str
    admitted_max_content_length: int

    document_class: HrDocumentClass
    created_at: datetime
    created_by_principal_id: str
    retention_until: datetime | None
    legal_hold: bool
    supersedes_version_id: str | None

    provider_name: str
    storage_reference: str
    object_version_reference: str
    provider_integrity_reference: str
    write_intent_fingerprint: str
    content_length: int
    content_fingerprint: str

    detected_at: datetime

    schema: str = SCHEMA
    uncertainty_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(
        self,
    ) -> None:
        tenant = _tenant(
            self.tenant_id
        )

        employee = _identity(
            "employee_id",
            self.employee_id,
        )

        document = _identity(
            "document_id",
            self.document_id,
        )

        document_version = _identity(
            "document_version_id",
            self.document_version_id,
        )

        ingestion = _identity(
            "ingestion_reference",
            self.ingestion_reference,
        )

        media_type = _text(
            "media_type",
            self.media_type,
            limit=128,
        ).lower()

        original_filename = _text(
            "original_filename",
            self.original_filename,
            limit=255,
        )

        admitted = _positive_int(
            "admitted_max_content_length",
            self.admitted_max_content_length,
        )

        if (
            type(
                self.document_class
            )
            is not HrDocumentClass
        ):
            _fail(
                "P0_C12F6C_DOCUMENT_CLASS_INVALID"
            )

        created = _utc(
            "created_at",
            self.created_at,
        )

        principal = _identity(
            "created_by_principal_id",
            self.created_by_principal_id,
        )

        retention = (
            None
            if self.retention_until is None
            else _utc(
                "retention_until",
                self.retention_until,
            )
        )

        if (
            retention is not None
            and retention < created
        ):
            _fail(
                "P0_C12F6C_RETENTION_PRECEDES_CREATION"
            )

        if type(
            self.legal_hold
        ) is not bool:
            _fail(
                "P0_C12F6C_LEGAL_HOLD_INVALID"
            )

        supersedes = (
            None
            if self.supersedes_version_id is None
            else _identity(
                "supersedes_version_id",
                self.supersedes_version_id,
            )
        )

        if (
            supersedes
            == document_version
        ):
            _fail(
                "P0_C12F6C_SELF_SUPERSESSION"
            )

        provider = _identity(
            "provider_name",
            self.provider_name,
        )

        storage_reference = _text(
            "storage_reference",
            self.storage_reference,
        )

        object_version = _text(
            "object_version_reference",
            self.object_version_reference,
        )

        provider_integrity = _text(
            "provider_integrity_reference",
            self.provider_integrity_reference,
        )

        intent_fingerprint = _sha3(
            "write_intent_fingerprint",
            self.write_intent_fingerprint,
        )

        content_length = _positive_int(
            "content_length",
            self.content_length,
        )

        content_fingerprint = _sha3(
            "content_fingerprint",
            self.content_fingerprint,
        )

        detected = _utc(
            "detected_at",
            self.detected_at,
        )

        if detected < created:
            _fail(
                "P0_C12F6C_DETECTED_AT_PRECEDES_CREATION"
            )

        if content_length > admitted:
            _fail(
                "P0_C12F6C_CONTENT_LENGTH_EXCEEDED"
            )

        if (
            self.schema != SCHEMA
            or self.uncertainty_version
            != VERSION
        ):
            _fail(
                "P0_C12F6C_SCHEMA_INVALID"
            )

        expected_id = _uncertainty_identity(
            tenant_id=tenant,
            employee_id=employee,
            document_id=document,
            document_version_id=(
                document_version
            ),
            ingestion_reference=ingestion,
            provider_name=provider,
            storage_reference=(
                storage_reference
            ),
            object_version_reference=(
                object_version
            ),
            write_intent_fingerprint=(
                intent_fingerprint
            ),
            content_length=(
                content_length
            ),
            content_fingerprint=(
                content_fingerprint
            ),
        )

        if (
            not isinstance(
                self.uncertainty_id,
                str,
            )
            or not hmac.compare_digest(
                self.uncertainty_id,
                expected_id,
            )
        ):
            _fail(
                "P0_C12F6C_UNCERTAINTY_ID_MISMATCH"
            )

        object.__setattr__(
            self,
            "tenant_id",
            tenant,
        )
        object.__setattr__(
            self,
            "employee_id",
            employee,
        )
        object.__setattr__(
            self,
            "document_id",
            document,
        )
        object.__setattr__(
            self,
            "document_version_id",
            document_version,
        )
        object.__setattr__(
            self,
            "ingestion_reference",
            ingestion,
        )
        object.__setattr__(
            self,
            "media_type",
            media_type,
        )
        object.__setattr__(
            self,
            "original_filename",
            original_filename,
        )
        object.__setattr__(
            self,
            "admitted_max_content_length",
            admitted,
        )
        object.__setattr__(
            self,
            "created_at",
            created,
        )
        object.__setattr__(
            self,
            "created_by_principal_id",
            principal,
        )
        object.__setattr__(
            self,
            "retention_until",
            retention,
        )
        object.__setattr__(
            self,
            "supersedes_version_id",
            supersedes,
        )
        object.__setattr__(
            self,
            "provider_name",
            provider,
        )
        object.__setattr__(
            self,
            "storage_reference",
            storage_reference,
        )
        object.__setattr__(
            self,
            "object_version_reference",
            object_version,
        )
        object.__setattr__(
            self,
            "provider_integrity_reference",
            provider_integrity,
        )
        object.__setattr__(
            self,
            "write_intent_fingerprint",
            intent_fingerprint,
        )
        object.__setattr__(
            self,
            "content_length",
            content_length,
        )
        object.__setattr__(
            self,
            "content_fingerprint",
            content_fingerprint,
        )
        object.__setattr__(
            self,
            "detected_at",
            detected,
        )

        payload = {
            field: _serialize_value(
                getattr(
                    self,
                    field,
                )
            )
            for field in _FIELDS[:-1]
        }

        digest = _fingerprint(
            payload
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
                    "P0_C12F6C_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    def to_dict(
        self,
    ) -> dict[str, object]:
        """Serialize exact immutable uncertainty evidence."""

        return {
            field: _serialize_value(
                getattr(
                    self,
                    field,
                )
            )
            for field in _FIELDS
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[
            str,
            object,
        ],
    ) -> "HrDocumentCommitUncertainty":
        """Strictly hydrate exact immutable uncertainty evidence."""

        if (
            not isinstance(
                payload,
                Mapping,
            )
            or set(
                payload
            ) != set(
                _FIELDS
            )
        ):
            _fail(
                "P0_C12F6C_SCHEMA_INVALID"
            )

        values = dict(
            payload
        )

        stored_fingerprint = values.pop(
            "fingerprint"
        )

        try:
            values[
                "document_class"
            ] = HrDocumentClass(
                cast(
                    str,
                    values[
                        "document_class"
                    ],
                )
            )

            values[
                "created_at"
            ] = _utc(
                "created_at",
                values[
                    "created_at"
                ],
            )

            if (
                values[
                    "retention_until"
                ]
                is not None
            ):
                values[
                    "retention_until"
                ] = _utc(
                    "retention_until",
                    values[
                        "retention_until"
                    ],
                )

            values[
                "detected_at"
            ] = _utc(
                "detected_at",
                values[
                    "detected_at"
                ],
            )

            values[
                "fingerprint"
            ] = stored_fingerprint

            return cls(
                **cast(
                    Any,
                    values,
                )
            )

        except HrDocumentCommitUncertaintyError:
            raise

        except (
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            raise HrDocumentCommitUncertaintyError(
                "P0_C12F6C_HYDRATION_INVALID"
            ) from error

    def _write_intent(
        self,
    ) -> HrDocumentBinaryWriteIntent:
        try:
            return HrDocumentBinaryWriteIntent(
                tenant_id=self.tenant_id,
                employee_id=self.employee_id,
                document_id=self.document_id,
                document_version_id=(
                    self.document_version_id
                ),
                ingestion_reference=(
                    self.ingestion_reference
                ),
                media_type=self.media_type,
                original_filename=(
                    self.original_filename
                ),
                admitted_max_content_length=(
                    self.admitted_max_content_length
                ),
                fingerprint=(
                    self.write_intent_fingerprint
                ),
            )

        except HrDocumentBinaryStoragePortError as error:
            raise HrDocumentCommitUncertaintyError(
                "P0_C12F6C_WRITE_INTENT_RECONSTRUCTION_INVALID"
            ) from error

    def _object_evidence(
        self,
    ) -> HrDocumentBinaryObjectEvidence:
        try:
            return HrDocumentBinaryObjectEvidence(
                provider_name=self.provider_name,
                storage_reference=(
                    self.storage_reference
                ),
                object_version_reference=(
                    self.object_version_reference
                ),
                provider_integrity_reference=(
                    self.provider_integrity_reference
                ),
                write_intent_fingerprint=(
                    self.write_intent_fingerprint
                ),
                content_length=(
                    self.content_length
                ),
                content_fingerprint=(
                    self.content_fingerprint
                ),
            )

        except HrDocumentBinaryStoragePortError as error:
            raise HrDocumentCommitUncertaintyError(
                "P0_C12F6C_OBJECT_EVIDENCE_RECONSTRUCTION_INVALID"
            ) from error

    def to_hr_document(
        self,
    ) -> HrDocument:
        """Reconstruct the exact intended immutable HrDocument."""

        intent = self._write_intent()
        evidence = self._object_evidence()

        try:
            return HrDocument.from_binary_evidence(
                intent=intent,
                evidence=evidence,
                document_class=(
                    self.document_class
                ),
                created_at=self.created_at,
                created_by_principal_id=(
                    self.created_by_principal_id
                ),
                retention_until=(
                    self.retention_until
                ),
                legal_hold=self.legal_hold,
                supersedes_version_id=(
                    self.supersedes_version_id
                ),
            )

        except HrDocumentDomainError as error:
            raise HrDocumentCommitUncertaintyError(
                "P0_C12F6C_HR_DOCUMENT_RECONSTRUCTION_INVALID"
            ) from error


def open_hr_document_commit_uncertainty(
    *,
    intent: HrDocumentBinaryWriteIntent,
    object_evidence: HrDocumentBinaryObjectEvidence,
    document_class: HrDocumentClass,
    created_at: datetime,
    created_by_principal_id: str,
    retention_until: datetime | None = None,
    legal_hold: bool = False,
    supersedes_version_id: str | None = None,
    detected_at: datetime,
) -> HrDocumentCommitUncertainty:
    """Create uncertainty only from exact verified provider completion."""

    if (
        type(
            intent
        )
        is not HrDocumentBinaryWriteIntent
    ):
        _fail(
            "P0_C12F6C_WRITE_INTENT_REQUIRED"
        )

    if (
        type(
            object_evidence
        )
        is not HrDocumentBinaryObjectEvidence
    ):
        _fail(
            "P0_C12F6C_OBJECT_EVIDENCE_REQUIRED"
        )

    try:
        validate_object_evidence_for_intent(
            intent=intent,
            evidence=object_evidence,
        )

    except HrDocumentBinaryStoragePortError as error:
        raise HrDocumentCommitUncertaintyError(
            "P0_C12F6C_OBJECT_SCOPE_MISMATCH"
        ) from error

    if not object_evidence.proves_stream(
        observed_length=(
            object_evidence.content_length
        ),
        observed_fingerprint=(
            object_evidence.content_fingerprint
        ),
    ):
        _fail(
            "P0_C12F6C_OBJECT_CONTENT_MISMATCH"
        )

    if (
        object_evidence.content_length
        > intent.admitted_max_content_length
    ):
        _fail(
            "P0_C12F6C_CONTENT_LENGTH_EXCEEDED"
        )

    created = _utc(
        "created_at",
        created_at,
    )

    detected = _utc(
        "detected_at",
        detected_at,
    )

    if detected < created:
        _fail(
            "P0_C12F6C_DETECTED_AT_PRECEDES_CREATION"
        )

    retention = (
        None
        if retention_until is None
        else _utc(
            "retention_until",
            retention_until,
        )
    )

    if (
        retention is not None
        and retention < created
    ):
        _fail(
            "P0_C12F6C_RETENTION_PRECEDES_CREATION"
        )

    if (
        supersedes_version_id
        == intent.document_version_id
    ):
        _fail(
            "P0_C12F6C_SELF_SUPERSESSION"
        )

    uncertainty_id = _uncertainty_identity(
        tenant_id=intent.tenant_id,
        employee_id=intent.employee_id,
        document_id=intent.document_id,
        document_version_id=(
            intent.document_version_id
        ),
        ingestion_reference=(
            intent.ingestion_reference
        ),
        provider_name=(
            object_evidence.provider_name
        ),
        storage_reference=(
            object_evidence.storage_reference
        ),
        object_version_reference=(
            object_evidence.object_version_reference
        ),
        write_intent_fingerprint=(
            object_evidence.write_intent_fingerprint
        ),
        content_length=(
            object_evidence.content_length
        ),
        content_fingerprint=(
            object_evidence.content_fingerprint
        ),
    )

    return HrDocumentCommitUncertainty(
        uncertainty_id=uncertainty_id,
        tenant_id=intent.tenant_id,
        employee_id=intent.employee_id,
        document_id=intent.document_id,
        document_version_id=(
            intent.document_version_id
        ),
        ingestion_reference=(
            intent.ingestion_reference
        ),
        media_type=intent.media_type,
        original_filename=(
            intent.original_filename
        ),
        admitted_max_content_length=(
            intent.admitted_max_content_length
        ),
        document_class=document_class,
        created_at=created,
        created_by_principal_id=(
            created_by_principal_id
        ),
        retention_until=retention,
        legal_hold=legal_hold,
        supersedes_version_id=(
            supersedes_version_id
        ),
        provider_name=(
            object_evidence.provider_name
        ),
        storage_reference=(
            object_evidence.storage_reference
        ),
        object_version_reference=(
            object_evidence.object_version_reference
        ),
        provider_integrity_reference=(
            object_evidence.provider_integrity_reference
        ),
        write_intent_fingerprint=(
            object_evidence.write_intent_fingerprint
        ),
        content_length=(
            object_evidence.content_length
        ),
        content_fingerprint=(
            object_evidence.content_fingerprint
        ),
        detected_at=detected,
    )


__all__ = [
    "VERSION",
    "SCHEMA",
    "HrDocumentCommitUncertainty",
    "HrDocumentCommitUncertaintyError",
    "open_hr_document_commit_uncertainty",
]


# ARTIFACT: tools/eos/saas/domain/hr_document_commit_uncertainty.py
# VERSION: v1.0.0-P0-C12F6C-HR-DOCUMENT-COMMIT-UNCERTAINTY
# AUTHORITY: immutable HR provider-complete / Mongo-unproven evidence only
# RAW BYTES: forbidden
# PROVIDER DELETE AUTHORITY: none
# IAM AUTHORITY: none
# HTTP AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
