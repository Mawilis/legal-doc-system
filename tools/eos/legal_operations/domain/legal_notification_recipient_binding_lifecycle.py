"""WILSY OS immutable Legal recipient-binding lifecycle evidence.

TITLE: Legal Notification Recipient Binding Lifecycle
VERSION: v1.1.0-L8-8H-RECIPIENT-BINDING-LIFECYCLE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Records append-only revocation or exact successor supersession of one
         immutable Legal notification recipient binding.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_notification_recipient_binding_lifecycle.py
COLLABORATION / OWNERSHIP: Binding domain owns selections; lifecycle registry
                            persists these events; resolver derives currentness.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.1.0 canonicalizes lifecycle UTC instants to BSON
           millisecond precision before deterministic fingerprint formation,
           preserving exact durable replay without weakening chronology,
           lineage, tenant, or fingerprint verification.
           v1.0.0 establishes immutable revocation and supersession evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; SHA3-512.
SECURITY / PRIVACY POSTURE: Opaque identifiers and fingerprints only.
TENANT BOUNDARY: Event and target/successor must share exact tenant scope.
AUTHORITY BOUNDARY: Terminates/supersedes recipient binding only; no dispatch.
TRANSACTION BOUNDARY: Pure domain artifact; owns no transaction.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Invalid lineage, chronology, schema or digest rejects.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Final, Mapping, NoReturn, cast

from tools.eos.legal_operations.domain.legal_notification_recipient_binding import LegalNotificationEvent, LegalNotificationRecipientBinding

SCHEMA: Final[str] = "WILSY-LEGAL-NOTIFICATION-RECIPIENT-BINDING-LIFECYCLE/V1"
VERSION: Final[str] = "v1.1.0-L8-8H-RECIPIENT-BINDING-LIFECYCLE"
_ID: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_FP: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN: Final[frozenset[str]] = frozenset({"default", "global", "global_root", "root", "master", "*"})
_FIELDS: Final[tuple[str, ...]] = ("schema", "lifecycle_version", "lifecycle_event_id", "tenant_id", "case_matter_id", "event", "action", "target_binding_id", "target_binding_fingerprint", "successor_binding_id", "successor_binding_fingerprint", "effective_at", "created_by_principal_id", "created_at", "fingerprint")


class LegalNotificationRecipientBindingLifecycleError(ValueError):
    """Stable code-only lifecycle evidence failure."""
    def __init__(self, code: str) -> None: self.code = code; super().__init__(code)


class LegalNotificationRecipientBindingLifecycleAction(StrEnum):
    """Closed immutable termination vocabulary."""
    REVOKED = "REVOKED"
    SUPERSEDED = "SUPERSEDED"


def _fail(code: str) -> NoReturn: raise LegalNotificationRecipientBindingLifecycleError(code)


def _id(name: str, value: object, tenant: bool = False) -> str:
    if not isinstance(value, str) or value != value.strip() or _ID.fullmatch(value) is None or (tenant and value.casefold() in _FORBIDDEN): _fail(f"L8_8H_LIFECYCLE_{name.upper()}_INVALID")
    return value


def _fp(name: str, value: object) -> str:
    if not isinstance(value, str) or _FP.fullmatch(value) is None: _fail(f"L8_8H_LIFECYCLE_{name.upper()}_INVALID")
    return value


def _utc(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None: _fail(f"L8_8H_LIFECYCLE_{name.upper()}_INVALID")
    result = value.astimezone(timezone.utc)
    if result != value or result.tzinfo != timezone.utc:
        _fail(f"L8_8H_LIFECYCLE_{name.upper()}_INVALID")
    return result.replace(
        microsecond=(result.microsecond // 1000) * 1000
    )


def _time(value: datetime) -> str: return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


@dataclass(frozen=True, slots=True)
class LegalNotificationRecipientBindingLifecycle:
    """Immutable termination evidence naming an exact target and optional successor."""
    lifecycle_event_id: str
    tenant_id: str
    case_matter_id: str
    event: LegalNotificationEvent | str
    action: LegalNotificationRecipientBindingLifecycleAction | str
    target_binding_id: str
    target_binding_fingerprint: str
    successor_binding_id: str | None
    successor_binding_fingerprint: str | None
    effective_at: datetime
    created_by_principal_id: str
    created_at: datetime
    schema: str = SCHEMA
    lifecycle_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate exact lineage, chronology and deterministic integrity."""
        event_id = _id("lifecycle_event_id", self.lifecycle_event_id); tenant = _id("tenant_id", self.tenant_id, True); matter = _id("case_matter_id", self.case_matter_id)
        target = _id("target_binding_id", self.target_binding_id); target_fp = _fp("target_binding_fingerprint", self.target_binding_fingerprint); creator = _id("created_by_principal_id", self.created_by_principal_id)
        try: event = LegalNotificationEvent(self.event); action = LegalNotificationRecipientBindingLifecycleAction(self.action)
        except (TypeError, ValueError) as error: raise LegalNotificationRecipientBindingLifecycleError("L8_8H_LIFECYCLE_ENUM_INVALID") from error
        effective = _utc("effective_at", self.effective_at); created = _utc("created_at", self.created_at)
        if created > effective: _fail("L8_8H_LIFECYCLE_CHRONOLOGY_INVALID")
        successor = self.successor_binding_id; successor_fp = self.successor_binding_fingerprint
        if action is LegalNotificationRecipientBindingLifecycleAction.REVOKED:
            if successor is not None or successor_fp is not None: _fail("L8_8H_LIFECYCLE_SUCCESSOR_FORBIDDEN")
        else:
            successor = _id("successor_binding_id", successor); successor_fp = _fp("successor_binding_fingerprint", successor_fp)
            if successor == target: _fail("L8_8H_LIFECYCLE_SUCCESSOR_INVALID")
        if self.schema != SCHEMA or self.lifecycle_version != VERSION: _fail("L8_8H_LIFECYCLE_SCHEMA_INVALID")
        for name, value in (("lifecycle_event_id", event_id), ("tenant_id", tenant), ("case_matter_id", matter), ("event", event), ("action", action), ("target_binding_id", target), ("target_binding_fingerprint", target_fp), ("successor_binding_id", successor), ("successor_binding_fingerprint", successor_fp), ("effective_at", effective), ("created_by_principal_id", creator), ("created_at", created)): object.__setattr__(self, name, value)
        digest = hashlib.sha3_512(json.dumps(self._payload(), sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
        if self.fingerprint and (not isinstance(self.fingerprint, str) or not hmac.compare_digest(self.fingerprint, digest)): _fail("L8_8H_LIFECYCLE_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def _payload(self) -> dict[str, object]:
        return {"schema": self.schema, "lifecycle_version": self.lifecycle_version, "lifecycle_event_id": self.lifecycle_event_id, "tenant_id": self.tenant_id, "case_matter_id": self.case_matter_id, "event": LegalNotificationEvent(self.event).value, "action": LegalNotificationRecipientBindingLifecycleAction(self.action).value, "target_binding_id": self.target_binding_id, "target_binding_fingerprint": self.target_binding_fingerprint, "successor_binding_id": self.successor_binding_id, "successor_binding_fingerprint": self.successor_binding_fingerprint, "effective_at": _time(self.effective_at), "created_by_principal_id": self.created_by_principal_id, "created_at": _time(self.created_at)}

    def to_dict(self) -> dict[str, object]:
        """Serialize exact durable evidence without contact data."""
        return {**self._payload(), "fingerprint": self.fingerprint}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LegalNotificationRecipientBindingLifecycle":
        """Hydrate only the exact lifecycle schema and reverify integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS): _fail("L8_8H_LIFECYCLE_SCHEMA_INVALID")
        values = dict(payload)
        for name in ("effective_at", "created_at"):
            if not isinstance(values[name], datetime):
                try: values[name] = datetime.fromisoformat(cast(str, values[name]).replace("Z", "+00:00"))
                except (TypeError, ValueError) as error: raise LegalNotificationRecipientBindingLifecycleError(f"L8_8H_LIFECYCLE_{name.upper()}_INVALID") from error
        return cls(**cast(dict, values))


def revoke_binding(*, lifecycle_event_id: str, target: LegalNotificationRecipientBinding, effective_at: datetime, created_by_principal_id: str, created_at: datetime) -> LegalNotificationRecipientBindingLifecycle:
    """Create exact revocation evidence after the target becomes effective."""
    if type(target) is not LegalNotificationRecipientBinding or effective_at <= target.effective_from: _fail("L8_8H_LIFECYCLE_TARGET_CHRONOLOGY_INVALID")
    return LegalNotificationRecipientBindingLifecycle(lifecycle_event_id, target.tenant_id, target.case_matter_id, target.event, LegalNotificationRecipientBindingLifecycleAction.REVOKED, target.binding_id, target.fingerprint, None, None, effective_at, created_by_principal_id, created_at)


def supersede_binding(*, lifecycle_event_id: str, target: LegalNotificationRecipientBinding, successor: LegalNotificationRecipientBinding, created_by_principal_id: str, created_at: datetime) -> LegalNotificationRecipientBindingLifecycle:
    """Create exact successor evidence with a contiguous effective boundary."""
    if type(target) is not LegalNotificationRecipientBinding or type(successor) is not LegalNotificationRecipientBinding: _fail("L8_8H_LIFECYCLE_BINDING_REQUIRED")
    if (target.tenant_id, target.case_matter_id, target.event) != (successor.tenant_id, successor.case_matter_id, successor.event) or successor.effective_from <= target.effective_from or (target.effective_until is not None and successor.effective_from > target.effective_until): _fail("L8_8H_LIFECYCLE_SUCCESSOR_SCOPE_INVALID")
    return LegalNotificationRecipientBindingLifecycle(lifecycle_event_id, target.tenant_id, target.case_matter_id, target.event, LegalNotificationRecipientBindingLifecycleAction.SUPERSEDED, target.binding_id, target.fingerprint, successor.binding_id, successor.fingerprint, successor.effective_from, created_by_principal_id, created_at)


__all__ = ["SCHEMA", "VERSION", "LegalNotificationRecipientBindingLifecycle", "LegalNotificationRecipientBindingLifecycleAction", "LegalNotificationRecipientBindingLifecycleError", "revoke_binding", "supersede_binding"]

# ARTIFACT: legal_notification_recipient_binding_lifecycle.py
# VERSION: v1.1.0-L8-8H-RECIPIENT-BINDING-LIFECYCLE
# AUTHORITY BOUNDARY: immutable binding revocation/supersession evidence only
# TENANT POSTURE: target and successor remain exact same tenant/matter/event scope
# FAIL-CLOSED POSTURE: lineage, chronology, scope, schema and digest divergence reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
