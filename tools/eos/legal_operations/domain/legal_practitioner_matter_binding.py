"""Immutable documentary practitioner-to-matter binding.

P9-R105-P4G-P6-R7B-P1. A binding is not a current IAM,
conflict, ethical-wall, document, or operational read authorization.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import json
import re
from typing import Any, Final

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)

VERSION: Final[str] = "v1.0.0-P9-R105-P4G-P6-R7B-P1"
SCHEMA: Final[str] = "WILSY-LEGAL-PRACTITIONER-MATTER-BINDING/V1"


class PractitionerMatterBindingError(ValueError):
    pass


class PractitionerMatterBindingStatus(StrEnum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


def _identity(value: object) -> str:
    if (
        type(value) is not str or not value or value != value.strip()
        or len(value) > 200 or any(c.isspace() for c in value)
    ):
        raise PractitionerMatterBindingError("BINDING_IDENTITY_INVALID")
    return value


def _reference(value: object) -> str:
    if (
        type(value) is not str or not value or value != value.strip()
        or len(value) > 512
    ):
        raise PractitionerMatterBindingError("BINDING_REFERENCE_INVALID")
    return value


def _moment(value: object) -> datetime:
    if (
        type(value) is not datetime or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise PractitionerMatterBindingError("BINDING_TIMESTAMP_INVALID")
    return value.astimezone(timezone.utc)


def _fingerprint(value: object) -> str:
    if type(value) is not str or re.fullmatch("[0-9a-f]{128}", value) is None:
        raise PractitionerMatterBindingError("BINDING_FINGERPRINT_INVALID")
    return value


@dataclass(frozen=True, slots=True, init=False)
class LegalPractitionerMatterBinding:
    binding_id: str
    tenant_id: str
    case_matter_id: str
    practitioner_principal_id: str
    source_case_matter_fingerprint: str
    granted_by_principal_id: str
    granted_at: datetime
    grant_evidence_reference: str
    status: PractitionerMatterBindingStatus
    revoked_by_principal_id: str | None
    revoked_at: datetime | None
    revocation_evidence_reference: str | None
    schema: str
    binding_version: str
    fingerprint: str

    def __init__(self, *args: object, **kwargs: object) -> None:
        raise PractitionerMatterBindingError("BINDING_FACTORY_REQUIRED")

    def _payload(self) -> dict[str, Any]:
        return {
            "binding_id": self.binding_id,
            "tenant_id": self.tenant_id,
            "case_matter_id": self.case_matter_id,
            "practitioner_principal_id": self.practitioner_principal_id,
            "source_case_matter_fingerprint": self.source_case_matter_fingerprint,
            "granted_by_principal_id": self.granted_by_principal_id,
            "granted_at": self.granted_at.isoformat(),
            "grant_evidence_reference": self.grant_evidence_reference,
            "status": self.status.value,
            "revoked_by_principal_id": self.revoked_by_principal_id,
            "revoked_at": (
                self.revoked_at.isoformat()
                if self.revoked_at is not None else None
            ),
            "revocation_evidence_reference": self.revocation_evidence_reference,
            "schema": self.schema,
            "binding_version": self.binding_version,
        }

    def _validate(self) -> None:
        for value in (
            self.binding_id, self.tenant_id, self.case_matter_id,
            self.practitioner_principal_id, self.granted_by_principal_id,
        ):
            _identity(value)
        _fingerprint(self.source_case_matter_fingerprint)
        _reference(self.grant_evidence_reference)
        _moment(self.granted_at)
        if self.schema != SCHEMA or self.binding_version != VERSION:
            raise PractitionerMatterBindingError("BINDING_SCHEMA_INVALID")
        if type(self.status) is not PractitionerMatterBindingStatus:
            raise PractitionerMatterBindingError("BINDING_STATUS_INVALID")
        if self.status is PractitionerMatterBindingStatus.ACTIVE:
            if any(value is not None for value in (
                self.revoked_by_principal_id, self.revoked_at,
                self.revocation_evidence_reference,
            )):
                raise PractitionerMatterBindingError("BINDING_ACTIVE_REVOCATION_INVALID")
        else:
            _identity(self.revoked_by_principal_id)
            _reference(self.revocation_evidence_reference)
            revoked = _moment(self.revoked_at)
            if revoked < _moment(self.granted_at):
                raise PractitionerMatterBindingError("BINDING_CHRONOLOGY_INVALID")
        _fingerprint(self.fingerprint)
        raw = json.dumps(
            self._payload(), sort_keys=True, separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        if self.fingerprint != sha3_512(raw).hexdigest():
            raise PractitionerMatterBindingError("BINDING_INTEGRITY_INVALID")

    @classmethod
    def _build(cls, fields: dict[str, Any]) -> LegalPractitionerMatterBinding:
        value = object.__new__(cls)
        for name, item in fields.items():
            object.__setattr__(value, name, item)
        object.__setattr__(value, "schema", SCHEMA)
        object.__setattr__(value, "binding_version", VERSION)
        raw = json.dumps(
            value._payload(), sort_keys=True, separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        object.__setattr__(value, "fingerprint", sha3_512(raw).hexdigest())
        value._validate()
        return value

    @classmethod
    def grant(
        cls, *, binding_id: str, case_matter: CaseMatter,
        practitioner_principal_id: str, granted_by_principal_id: str,
        granted_at: datetime, evidence_reference: str,
    ) -> LegalPractitionerMatterBinding:
        if type(case_matter) is not CaseMatter:
            raise PractitionerMatterBindingError("BINDING_MATTER_REQUIRED")
        try:
            case_matter.__post_init__()
        except Exception as exc:
            raise PractitionerMatterBindingError("BINDING_MATTER_INVALID") from exc
        if case_matter.state is not CaseMatterState.OPEN:
            raise PractitionerMatterBindingError("BINDING_MATTER_NOT_OPEN")
        at = _moment(granted_at)
        if at < _moment(case_matter.opened_at):
            raise PractitionerMatterBindingError("BINDING_BEFORE_MATTER_OPEN")
        return cls._build({
            "binding_id": _identity(binding_id),
            "tenant_id": _identity(case_matter.tenant_id),
            "case_matter_id": _identity(case_matter.case_matter_id),
            "practitioner_principal_id": _identity(practitioner_principal_id),
            "source_case_matter_fingerprint": _fingerprint(
                case_matter.fingerprint
            ),
            "granted_by_principal_id": _identity(granted_by_principal_id),
            "granted_at": at,
            "grant_evidence_reference": _reference(evidence_reference),
            "status": PractitionerMatterBindingStatus.ACTIVE,
            "revoked_by_principal_id": None,
            "revoked_at": None,
            "revocation_evidence_reference": None,
        })

    def revoke(
        self, *, revoked_by_principal_id: str,
        revoked_at: datetime, evidence_reference: str,
    ) -> LegalPractitionerMatterBinding:
        self._validate()
        if self.status is not PractitionerMatterBindingStatus.ACTIVE:
            raise PractitionerMatterBindingError("BINDING_ALREADY_REVOKED")
        at = _moment(revoked_at)
        if at < self.granted_at:
            raise PractitionerMatterBindingError("BINDING_CHRONOLOGY_INVALID")
        fields = {
            name: getattr(self, name)
            for name in (
                "binding_id", "tenant_id", "case_matter_id",
                "practitioner_principal_id",
                "source_case_matter_fingerprint",
                "granted_by_principal_id", "granted_at",
                "grant_evidence_reference",
            )
        }
        fields.update({
            "status": PractitionerMatterBindingStatus.REVOKED,
            "revoked_by_principal_id": _identity(revoked_by_principal_id),
            "revoked_at": at,
            "revocation_evidence_reference": _reference(evidence_reference),
        })
        return type(self)._build(fields)

    def to_dict(self) -> dict[str, Any]:
        self._validate()
        return {**self._payload(), "fingerprint": self.fingerprint}

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> LegalPractitionerMatterBinding:
        if type(raw) is not dict:
            raise PractitionerMatterBindingError("BINDING_RECORD_INVALID")
        required = set(cls.__dataclass_fields__)
        if set(raw) != required:
            raise PractitionerMatterBindingError("BINDING_RECORD_FIELDS_INVALID")
        try:
            values = dict(raw)
            expected = values.pop("fingerprint")
            if values.pop("schema") != SCHEMA:
                raise ValueError("SCHEMA")
            if values.pop("binding_version") != VERSION:
                raise ValueError("VERSION")
            values["granted_at"] = _moment(
                datetime.fromisoformat(values["granted_at"])
            )
            if values["revoked_at"] is not None:
                values["revoked_at"] = _moment(
                    datetime.fromisoformat(values["revoked_at"])
                )
            values["status"] = PractitionerMatterBindingStatus(
                values["status"]
            )
            result = cls._build(values)
            if result.fingerprint != _fingerprint(expected):
                raise ValueError("FINGERPRINT")
            return result
        except Exception as exc:
            raise PractitionerMatterBindingError("BINDING_RECORD_INVALID") from exc

    @property
    def authorizes_matter_access(self) -> bool:
        return False


__all__ = (
    "VERSION", "SCHEMA", "PractitionerMatterBindingError",
    "PractitionerMatterBindingStatus", "LegalPractitionerMatterBinding",
)

# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.0-P9-R105-P4G-P6-R7B-P1
# DOMAIN RELATION EVIDENCE ONLY; NO OPERATIONAL ACCESS GRANT
# END OF WILSY OS SOVEREIGN ARTIFACT
