"""TITLE: WILSY OS HR Document Pure Domain.
VERSION: v1.0.0-P0-C12F3-HR-DOCUMENT-DOMAIN
AUTHORITY: Immutable personnel-document/version domain truth.
EPITOME: Binds certified HR binary evidence to exact tenant, employee,
document and immutable document-version identity with governed class,
sensitivity, UTC provenance, retention/legal-hold state and SHA3-512
domain fingerprinting.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/hr_document.py
CERTIFICATION/UPDATE DATE: 2026-10-04.
CHANGELOG:
2026-10-04 v1.0.0-P0-C12F3-HR-DOCUMENT-DOMAIN
establishes the first sovereign HR document/version domain.
AUTHORITY BOUNDARY: Domain truth only. No IAM, registry, provider,
HTTP, deletion execution, payroll, billing or financial authority.
STORAGE BOUNDARY: Consumes the frozen HR binary-storage intent and
completed-object evidence but performs no provider operation itself.
RETENTION BOUNDARY: Models retention and legal-hold blocking state;
it does not grant deletion or disposal authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import hmac
import json
import re
from typing import Final

from tools.eos.saas.hr.hr_document_storage import (
    HrDocumentBinaryObjectEvidence,
    HrDocumentBinaryStoragePortError,
    HrDocumentBinaryWriteIntent,
    validate_object_evidence_for_intent,
)


VERSION: Final[str] = (
    "v1.0.0-P0-C12F3-HR-DOCUMENT-DOMAIN"
)

HR_DOCUMENT_SCHEMA: Final[str] = (
    "WILSY-HR-DOCUMENT/V1"
)

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$"
)

_HEX: Final[frozenset[str]] = frozenset(
    "0123456789abcdef"
)


class HrDocumentDomainError(ValueError):
    """Stable fail-closed HR document domain error."""


class HrDocumentClass(str, Enum):
    EMPLOYMENT_CONTRACT = "EMPLOYMENT_CONTRACT"
    APPOINTMENT_LETTER = "APPOINTMENT_LETTER"
    OFFER_LETTER = "OFFER_LETTER"
    WARNING = "WARNING"
    FINAL_WARNING = "FINAL_WARNING"
    DISCIPLINARY_NOTICE = "DISCIPLINARY_NOTICE"
    DISCIPLINARY_OUTCOME = "DISCIPLINARY_OUTCOME"
    GRIEVANCE_RECORD = "GRIEVANCE_RECORD"
    PERFORMANCE_RECORD = "PERFORMANCE_RECORD"
    PERFORMANCE_IMPROVEMENT_PLAN = "PERFORMANCE_IMPROVEMENT_PLAN"
    POLICY_ACKNOWLEDGEMENT = "POLICY_ACKNOWLEDGEMENT"
    TRAINING_CERTIFICATE = "TRAINING_CERTIFICATE"
    LEAVE_SUPPORTING_DOCUMENT = "LEAVE_SUPPORTING_DOCUMENT"
    MEDICAL_SUPPORTING_DOCUMENT = "MEDICAL_SUPPORTING_DOCUMENT"
    IDENTITY_SUPPORTING_DOCUMENT = "IDENTITY_SUPPORTING_DOCUMENT"
    QUALIFICATION_DOCUMENT = "QUALIFICATION_DOCUMENT"
    TERMINATION_LETTER = "TERMINATION_LETTER"
    RESIGNATION_LETTER = "RESIGNATION_LETTER"
    EXIT_DOCUMENT = "EXIT_DOCUMENT"
    GENERAL_EMPLOYEE_ARTIFACT = "GENERAL_EMPLOYEE_ARTIFACT"


HR_DOCUMENT_CLASSES: Final[frozenset[HrDocumentClass]] = frozenset(
    HrDocumentClass
)


class HrDocumentSensitivity(str, Enum):
    STANDARD_EMPLOYMENT = "STANDARD_EMPLOYMENT"
    EMPLOYEE_RELATIONS_RESTRICTED = "EMPLOYEE_RELATIONS_RESTRICTED"
    PERFORMANCE_RESTRICTED = "PERFORMANCE_RESTRICTED"
    HIGHLY_SENSITIVE_HEALTH = "HIGHLY_SENSITIVE_HEALTH"
    HIGHLY_SENSITIVE_IDENTITY = "HIGHLY_SENSITIVE_IDENTITY"
    SEPARATION_RESTRICTED = "SEPARATION_RESTRICTED"
    GENERAL = "GENERAL"


_SENSITIVITY: Final[
    dict[
        HrDocumentClass,
        HrDocumentSensitivity,
    ]
] = {
    HrDocumentClass.EMPLOYMENT_CONTRACT:
        HrDocumentSensitivity.STANDARD_EMPLOYMENT,
    HrDocumentClass.APPOINTMENT_LETTER:
        HrDocumentSensitivity.STANDARD_EMPLOYMENT,
    HrDocumentClass.OFFER_LETTER:
        HrDocumentSensitivity.STANDARD_EMPLOYMENT,
    HrDocumentClass.POLICY_ACKNOWLEDGEMENT:
        HrDocumentSensitivity.STANDARD_EMPLOYMENT,
    HrDocumentClass.TRAINING_CERTIFICATE:
        HrDocumentSensitivity.STANDARD_EMPLOYMENT,
    HrDocumentClass.QUALIFICATION_DOCUMENT:
        HrDocumentSensitivity.STANDARD_EMPLOYMENT,
    HrDocumentClass.WARNING:
        HrDocumentSensitivity.EMPLOYEE_RELATIONS_RESTRICTED,
    HrDocumentClass.FINAL_WARNING:
        HrDocumentSensitivity.EMPLOYEE_RELATIONS_RESTRICTED,
    HrDocumentClass.DISCIPLINARY_NOTICE:
        HrDocumentSensitivity.EMPLOYEE_RELATIONS_RESTRICTED,
    HrDocumentClass.DISCIPLINARY_OUTCOME:
        HrDocumentSensitivity.EMPLOYEE_RELATIONS_RESTRICTED,
    HrDocumentClass.GRIEVANCE_RECORD:
        HrDocumentSensitivity.EMPLOYEE_RELATIONS_RESTRICTED,
    HrDocumentClass.PERFORMANCE_IMPROVEMENT_PLAN:
        HrDocumentSensitivity.EMPLOYEE_RELATIONS_RESTRICTED,
    HrDocumentClass.PERFORMANCE_RECORD:
        HrDocumentSensitivity.PERFORMANCE_RESTRICTED,
    HrDocumentClass.LEAVE_SUPPORTING_DOCUMENT:
        HrDocumentSensitivity.STANDARD_EMPLOYMENT,
    HrDocumentClass.MEDICAL_SUPPORTING_DOCUMENT:
        HrDocumentSensitivity.HIGHLY_SENSITIVE_HEALTH,
    HrDocumentClass.IDENTITY_SUPPORTING_DOCUMENT:
        HrDocumentSensitivity.HIGHLY_SENSITIVE_IDENTITY,
    HrDocumentClass.TERMINATION_LETTER:
        HrDocumentSensitivity.SEPARATION_RESTRICTED,
    HrDocumentClass.RESIGNATION_LETTER:
        HrDocumentSensitivity.SEPARATION_RESTRICTED,
    HrDocumentClass.EXIT_DOCUMENT:
        HrDocumentSensitivity.SEPARATION_RESTRICTED,
    HrDocumentClass.GENERAL_EMPLOYEE_ARTIFACT:
        HrDocumentSensitivity.GENERAL,
}


def sensitivity_for_document_class(
    value: HrDocumentClass,
) -> HrDocumentSensitivity:

    if type(value) is not HrDocumentClass:
        raise HrDocumentDomainError(
            "P0_C12F3_DOCUMENT_CLASS_INVALID"
        )

    try:
        return _SENSITIVITY[value]

    except KeyError as exc:
        raise HrDocumentDomainError(
            "P0_C12F3_DOCUMENT_CLASS_UNMAPPED"
        ) from exc


def _identity(
    name: str,
    value: object,
) -> str:

    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        raise HrDocumentDomainError(
            f"P0_C12F3_{name.upper()}_INVALID"
        )

    return value


def _text(
    name: str,
    value: object,
    *,
    limit: int,
) -> str:

    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(
            ord(character) < 32
            for character in value
        )
    ):
        raise HrDocumentDomainError(
            f"P0_C12F3_{name.upper()}_INVALID"
        )

    return value


def _digest(
    value: object,
) -> str:

    if (
        not isinstance(value, str)
        or len(value) != 128
        or any(
            character not in _HEX
            for character in value
        )
    ):
        raise HrDocumentDomainError(
            "P0_C12F3_CONTENT_DIGEST_INVALID"
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
        raise HrDocumentDomainError(
            f"P0_C12F3_{name.upper()}_UTC_REQUIRED"
        )

    return value.astimezone(
        timezone.utc
    )


def _fingerprint(
    *,
    tenant_id: str,
    employee_id: str,
    document_id: str,
    document_version_id: str,
    document_class: HrDocumentClass,
    sensitivity: HrDocumentSensitivity,
    original_filename: str,
    media_type: str,
    byte_length: int,
    content_digest_sha3_512: str,
    storage_provider_id: str,
    storage_object_reference: str,
    object_version_reference: str,
    provider_integrity_reference: str,
    created_at: datetime,
    created_by_principal_id: str,
    retention_until: datetime | None,
    legal_hold: bool,
    supersedes_version_id: str | None,
) -> str:

    payload = {
        "schema": HR_DOCUMENT_SCHEMA,
        "tenant_id": tenant_id,
        "employee_id": employee_id,
        "document_id": document_id,
        "document_version_id": document_version_id,
        "document_class": document_class.value,
        "sensitivity": sensitivity.value,
        "original_filename": original_filename,
        "media_type": media_type,
        "byte_length": byte_length,
        "content_digest_sha3_512": content_digest_sha3_512,
        "storage_provider_id": storage_provider_id,
        "storage_object_reference": storage_object_reference,
        "object_version_reference": object_version_reference,
        "provider_integrity_reference": provider_integrity_reference,
        "created_at": created_at.isoformat(),
        "created_by_principal_id": created_by_principal_id,
        "retention_until": (
            retention_until.isoformat()
            if retention_until is not None
            else None
        ),
        "legal_hold": legal_hold,
        "supersedes_version_id": supersedes_version_id,
    }

    raw = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
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
class HrDocument:
    """One immutable HR document version and its binary evidence."""

    tenant_id: str
    employee_id: str
    document_id: str
    document_version_id: str
    document_class: HrDocumentClass
    sensitivity: HrDocumentSensitivity
    original_filename: str
    media_type: str
    byte_length: int
    content_digest_sha3_512: str
    storage_provider_id: str
    storage_object_reference: str
    object_version_reference: str
    provider_integrity_reference: str
    created_at: datetime
    created_by_principal_id: str
    retention_until: datetime | None
    legal_hold: bool
    supersedes_version_id: str | None
    schema: str = HR_DOCUMENT_SCHEMA
    fingerprint: str = ""

    @classmethod
    def from_binary_evidence(
        cls,
        *,
        intent: HrDocumentBinaryWriteIntent,
        evidence: HrDocumentBinaryObjectEvidence,
        document_class: HrDocumentClass,
        created_at: datetime,
        created_by_principal_id: str,
        retention_until: datetime | None = None,
        legal_hold: bool = False,
        supersedes_version_id: str | None = None,
    ) -> "HrDocument":

        if (
            type(intent)
            is not HrDocumentBinaryWriteIntent
            or type(evidence)
            is not HrDocumentBinaryObjectEvidence
        ):
            raise HrDocumentDomainError(
                "P0_C12F3_BINARY_EVIDENCE_INVALID"
            )

        try:
            validate_object_evidence_for_intent(
                intent=intent,
                evidence=evidence,
            )

        except HrDocumentBinaryStoragePortError as exc:
            raise HrDocumentDomainError(
                "P0_C12F3_BINARY_SCOPE_MISMATCH"
            ) from exc

        if (
            evidence.content_length
            > intent.admitted_max_content_length
        ):
            raise HrDocumentDomainError(
                "P0_C12F3_CONTENT_LENGTH_EXCEEDED"
            )

        if type(document_class) is not HrDocumentClass:
            raise HrDocumentDomainError(
                "P0_C12F3_DOCUMENT_CLASS_INVALID"
            )

        created = _utc(
            "created_at",
            created_at,
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
            raise HrDocumentDomainError(
                "P0_C12F3_RETENTION_PRECEDES_CREATION"
            )

        if type(legal_hold) is not bool:
            raise HrDocumentDomainError(
                "P0_C12F3_LEGAL_HOLD_INVALID"
            )

        supersedes = (
            None
            if supersedes_version_id is None
            else _identity(
                "supersedes_version_id",
                supersedes_version_id,
            )
        )

        if (
            supersedes
            == intent.document_version_id
        ):
            raise HrDocumentDomainError(
                "P0_C12F3_SELF_SUPERSESSION"
            )

        sensitivity = sensitivity_for_document_class(
            document_class
        )

        return cls(
            tenant_id=intent.tenant_id,
            employee_id=intent.employee_id,
            document_id=intent.document_id,
            document_version_id=intent.document_version_id,
            document_class=document_class,
            sensitivity=sensitivity,
            original_filename=intent.original_filename,
            media_type=intent.media_type,
            byte_length=evidence.content_length,
            content_digest_sha3_512=evidence.content_fingerprint,
            storage_provider_id=evidence.provider_name,
            storage_object_reference=evidence.storage_reference,
            object_version_reference=evidence.object_version_reference,
            provider_integrity_reference=evidence.provider_integrity_reference,
            created_at=created,
            created_by_principal_id=created_by_principal_id,
            retention_until=retention,
            legal_hold=legal_hold,
            supersedes_version_id=supersedes,
        )

    def __post_init__(
        self,
    ) -> None:

        if self.schema != HR_DOCUMENT_SCHEMA:
            raise HrDocumentDomainError(
                "P0_C12F3_SCHEMA_INVALID"
            )

        tenant = _identity(
            "tenant_id",
            self.tenant_id,
        )

        employee = _identity(
            "employee_id",
            self.employee_id,
        )

        document = _identity(
            "document_id",
            self.document_id,
        )

        version = _identity(
            "document_version_id",
            self.document_version_id,
        )

        if type(self.document_class) is not HrDocumentClass:
            raise HrDocumentDomainError(
                "P0_C12F3_DOCUMENT_CLASS_INVALID"
            )

        expected_sensitivity = sensitivity_for_document_class(
            self.document_class
        )

        if self.sensitivity is not expected_sensitivity:
            raise HrDocumentDomainError(
                "P0_C12F3_SENSITIVITY_MISMATCH"
            )

        filename = _text(
            "original_filename",
            self.original_filename,
            limit=255,
        )

        media = _text(
            "media_type",
            self.media_type,
            limit=128,
        ).lower()

        if (
            isinstance(self.byte_length, bool)
            or not isinstance(self.byte_length, int)
            or self.byte_length <= 0
        ):
            raise HrDocumentDomainError(
                "P0_C12F3_BYTE_LENGTH_INVALID"
            )

        digest = _digest(
            self.content_digest_sha3_512
        )

        provider = _identity(
            "storage_provider_id",
            self.storage_provider_id,
        )

        storage_ref = _text(
            "storage_object_reference",
            self.storage_object_reference,
            limit=2048,
        )

        object_version = _text(
            "object_version_reference",
            self.object_version_reference,
            limit=2048,
        )

        integrity = _text(
            "provider_integrity_reference",
            self.provider_integrity_reference,
            limit=2048,
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
            raise HrDocumentDomainError(
                "P0_C12F3_RETENTION_PRECEDES_CREATION"
            )

        if type(self.legal_hold) is not bool:
            raise HrDocumentDomainError(
                "P0_C12F3_LEGAL_HOLD_INVALID"
            )

        supersedes = (
            None
            if self.supersedes_version_id is None
            else _identity(
                "supersedes_version_id",
                self.supersedes_version_id,
            )
        )

        if supersedes == version:
            raise HrDocumentDomainError(
                "P0_C12F3_SELF_SUPERSESSION"
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
            version,
        )

        object.__setattr__(
            self,
            "original_filename",
            filename,
        )

        object.__setattr__(
            self,
            "media_type",
            media,
        )

        object.__setattr__(
            self,
            "content_digest_sha3_512",
            digest,
        )

        object.__setattr__(
            self,
            "storage_provider_id",
            provider,
        )

        object.__setattr__(
            self,
            "storage_object_reference",
            storage_ref,
        )

        object.__setattr__(
            self,
            "object_version_reference",
            object_version,
        )

        object.__setattr__(
            self,
            "provider_integrity_reference",
            integrity,
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

        digest_value = _fingerprint(
            tenant_id=tenant,
            employee_id=employee,
            document_id=document,
            document_version_id=version,
            document_class=self.document_class,
            sensitivity=self.sensitivity,
            original_filename=filename,
            media_type=media,
            byte_length=self.byte_length,
            content_digest_sha3_512=digest,
            storage_provider_id=provider,
            storage_object_reference=storage_ref,
            object_version_reference=object_version,
            provider_integrity_reference=integrity,
            created_at=created,
            created_by_principal_id=principal,
            retention_until=retention,
            legal_hold=self.legal_hold,
            supersedes_version_id=supersedes,
        )

        if (
            self.fingerprint
            and (
                not isinstance(
                    self.fingerprint,
                    str,
                )
                or not hmac.compare_digest(
                    self.fingerprint,
                    digest_value,
                )
            )
        ):
            raise HrDocumentDomainError(
                "P0_C12F3_FINGERPRINT_MISMATCH"
            )

        object.__setattr__(
            self,
            "fingerprint",
            digest_value,
        )

    def retention_blocks_disposal(
        self,
        *,
        at: datetime,
    ) -> bool:

        current = _utc(
            "at",
            at,
        )

        return (
            self.retention_until is not None
            and current < self.retention_until
        )

    def disposal_blocked(
        self,
        *,
        at: datetime,
    ) -> bool:

        return (
            self.legal_hold
            or self.retention_blocks_disposal(
                at=at
            )
        )


__all__ = [
    "VERSION",
    "HR_DOCUMENT_SCHEMA",
    "HR_DOCUMENT_CLASSES",
    "HrDocumentDomainError",
    "HrDocumentClass",
    "HrDocumentSensitivity",
    "sensitivity_for_document_class",
    "HrDocument",
]


# ARTIFACT: tools/eos/saas/domain/hr_document.py
# VERSION: v1.0.0-P0-C12F3-HR-DOCUMENT-DOMAIN
# AUTHORITY BOUNDARY: immutable HR document/version domain truth only
# STORAGE BOUNDARY: consumes certified HR binary evidence; performs no provider operation
# RETENTION BOUNDARY: models retention/legal-hold blocking only; no deletion authorization
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
