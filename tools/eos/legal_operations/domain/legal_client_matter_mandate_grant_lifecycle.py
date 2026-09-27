"""Immutable lifecycle evidence for one exact client mandate grant.

TITLE: WILSY OS Legal Client Matter Mandate Grant Lifecycle
VERSION: v1.0.0-L9B6-CLIENT-MANDATE-GRANT-LIFECYCLE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Record a bounded REVOKED or SUPERSEDED event for one immutable client
         mandate grant. This value is historical evidence only; it does not
         compute currentness, mutate a mandate, terminate Engagement, or grant
         IAM, Representation, Court, or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_mandate_grant_lifecycle.py
COLLABORATION / OWNERSHIP: LegalClientMatterMandateGrant owns the canonical
                            grant snapshot. This artifact owns only event
                            lineage and chronology. A future registry owns
                            durable history and currentness composition.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B6-CLIENT-MANDATE-GRANT-LIFECYCLE establishes the closed
           REVOKED/SUPERSEDED vocabulary, exact grant and successor binding,
           currentness-key evidence, actor/evidence provenance, UTC chronology,
           idempotency, deterministic SHA3-512 integrity, and strict hydration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers, bounded evidence references
                             and lowercase SHA3-512 fingerprints only; no raw
                             PII, credentials, tokens, or evidence bodies.
TENANT BOUNDARY: Exact tenant, matter, client party, subject, breadth, scope,
                 and capability identity is copied from the primary grant;
                 successor events require exact currentness-key equality.
AUTHORITY BOUNDARY: Immutable lifecycle evidence only. No persistence, IAM,
                    currentness, mandate, acknowledgment, Engagement,
                    Representation, Court, or delivery authority.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement, release, or execution;
                              Kennel EOS remains exclusive financial authority.
TRANSACTION BOUNDARY: Pure immutable construction, serialization, and strict
                      hydration; no database, HTTP, registry, retry, or network.
FAIL-CLOSED DECLARATION: Invalid scope, chronology, event invariants,
                         fingerprints, or schema reject without coercion.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Any, Final, NoReturn, cast
import unicodedata

from tools.eos.legal_operations.domain.legal_client_matter_mandate import (
    LegalClientMatterMandateBreadth,
    LegalClientMatterMandateCapability,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant import (
    LegalClientMatterMandateGrant,
)


VERSION: Final[str] = "v1.0.0-L9B6-CLIENT-MANDATE-GRANT-LIFECYCLE"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-MANDATE-GRANT-LIFECYCLE/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FIELDS: Final[tuple[str, ...]] = (
    "schema", "lifecycle_version", "lifecycle_event_id", "event",
    "tenant_id", "case_matter_id", "matter_fingerprint", "client_party_id",
    "subject_identity_fingerprint", "breadth", "scope_fingerprint",
    "capabilities", "client_grant_id", "client_grant_fingerprint",
    "successor_client_grant_id", "successor_client_grant_fingerprint",
    "decision_actor_principal_id", "acting_capacity_id",
    "acting_capacity_fingerprint", "authorization_evidence_reference",
    "authorization_evidence_fingerprint", "source_evidence_reference",
    "source_evidence_fingerprint", "reason", "occurred_at", "effective_from",
    "idempotency_key", "fingerprint",
)
LIFECYCLE_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientMatterMandateGrantLifecycleEvent(StrEnum):
    """Closed lifecycle events; expiration is derived, not an event."""

    REVOKED = "REVOKED"
    SUPERSEDED = "SUPERSEDED"


class LegalClientMatterMandateGrantLifecycleReason(StrEnum):
    """Bounded reasons for an explicit client-grant lifecycle decision."""

    CLIENT_WITHDRAWAL = "CLIENT_WITHDRAWAL"
    AUTHORITY_REPLACED = "AUTHORITY_REPLACED"
    SCOPE_CHANGED = "SCOPE_CHANGED"
    ERROR_CORRECTION = "ERROR_CORRECTION"


class LegalClientMatterMandateGrantLifecycleError(ValueError):
    """Stable non-sensitive lifecycle validation failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalClientMatterMandateGrantLifecycleError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"L9B6_{name.upper()}_INVALID")
    return cast(str, value)


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9B6_{name.upper()}_INVALID")
    return value


def _reference(name: str, value: object, *, limit: int = 512) -> str:
    if (
        not isinstance(value, str) or not value or value != value.strip() or len(value) > limit
        or any(ord(c) < 32 or 0x7F <= ord(c) <= 0x9F or 0xD800 <= ord(c) <= 0xDFFF for c in value)
    ):
        _fail(f"L9B6_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if normalized != value:
        _fail(f"L9B6_{name.upper()}_INVALID")
    return normalized


def _timestamp(name: str, value: object) -> datetime:
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9B6_{name.upper()}_INVALID", error)
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(f"L9B6_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc)


def _capabilities(value: object) -> tuple[LegalClientMatterMandateCapability, ...]:
    if not isinstance(value, (tuple, list, set, frozenset)) or isinstance(value, str):
        _fail("L9B6_CAPABILITIES_INVALID")
    try:
        result = tuple(LegalClientMatterMandateCapability(item) for item in cast(Any, value))
    except (TypeError, ValueError) as error:
        _fail("L9B6_CAPABILITY_UNKNOWN", error)
    if not result:
        _fail("L9B6_CAPABILITIES_EMPTY")
    if len(set(result)) != len(result):
        _fail("L9B6_CAPABILITY_DUPLICATE")
    return tuple(sorted(result, key=lambda item: item.value))


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    return value


def _digest(instance: "LegalClientMatterMandateGrantLifecycle") -> str:
    payload = {field: _json_value(getattr(instance, field)) for field in _FIELDS[:-1]}
    return hashlib.sha3_512(json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=False, separators=(",", ":")).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalClientMatterMandateGrantLifecycle:
    """One immutable REVOKED or SUPERSEDED event for one exact grant.

    This class owns no transaction or persistence. A registry must preserve
    every event and separately derive whether a grant is currently usable.
    """

    lifecycle_event_id: str
    event: LegalClientMatterMandateGrantLifecycleEvent | str
    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    client_party_id: str
    subject_identity_fingerprint: str
    breadth: LegalClientMatterMandateBreadth | str
    scope_fingerprint: str
    capabilities: tuple[LegalClientMatterMandateCapability, ...] | list[str]
    client_grant_id: str
    client_grant_fingerprint: str
    successor_client_grant_id: str | None
    successor_client_grant_fingerprint: str | None
    decision_actor_principal_id: str
    acting_capacity_id: str | None
    acting_capacity_fingerprint: str | None
    authorization_evidence_reference: str
    authorization_evidence_fingerprint: str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    reason: LegalClientMatterMandateGrantLifecycleReason | str | None
    occurred_at: datetime
    effective_from: datetime
    idempotency_key: str
    schema: str = SCHEMA
    lifecycle_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        event = self.event if isinstance(self.event, LegalClientMatterMandateGrantLifecycleEvent) else _event(self.event)
        reason = None if self.reason is None else _reason(self.reason)
        breadth = _breadth(self.breadth)
        occurred = _timestamp("occurred_at", self.occurred_at)
        effective = _timestamp("effective_from", self.effective_from)
        if self.schema != SCHEMA or self.lifecycle_version != VERSION:
            _fail("L9B6_IDENTITY_INVALID")
        if effective < occurred:
            _fail("L9B6_EFFECTIVE_FROM_BEFORE_OCCURRED")
        _identity("lifecycle_event_id", self.lifecycle_event_id)
        _identity("tenant_id", self.tenant_id)
        _identity("case_matter_id", self.case_matter_id)
        _fingerprint("matter_fingerprint", self.matter_fingerprint)
        _identity("client_party_id", self.client_party_id)
        _fingerprint("subject_identity_fingerprint", self.subject_identity_fingerprint)
        _fingerprint("scope_fingerprint", self.scope_fingerprint)
        capabilities = _capabilities(self.capabilities)
        _identity("client_grant_id", self.client_grant_id)
        _fingerprint("client_grant_fingerprint", self.client_grant_fingerprint)
        _identity("decision_actor_principal_id", self.decision_actor_principal_id)
        auth_ref = _reference("authorization_evidence_reference", self.authorization_evidence_reference)
        auth_fp = _fingerprint("authorization_evidence_fingerprint", self.authorization_evidence_fingerprint)
        source_ref = _reference("source_evidence_reference", self.source_evidence_reference)
        source_fp = _fingerprint("source_evidence_fingerprint", self.source_evidence_fingerprint)
        idem = _reference("idempotency_key", self.idempotency_key, limit=240)
        successor_id = self.successor_client_grant_id
        successor_fp = self.successor_client_grant_fingerprint
        cap_id = self.acting_capacity_id
        cap_fp = self.acting_capacity_fingerprint
        if (cap_id is None) != (cap_fp is None):
            _fail("L9B6_ACTING_CAPACITY_PAIR_REQUIRED")
        if cap_id is not None:
            _identity("acting_capacity_id", cap_id)
            _fingerprint("acting_capacity_fingerprint", cap_fp)
        if event is LegalClientMatterMandateGrantLifecycleEvent.REVOKED:
            if reason is None:
                _fail("L9B6_REVOKED_REASON_REQUIRED")
            if successor_id is not None or successor_fp is not None:
                _fail("L9B6_REVOKED_SUCCESSOR_FORBIDDEN")
        else:
            if reason is not None:
                _fail("L9B6_SUPERSEDED_REASON_FORBIDDEN")
            if successor_id is None or successor_fp is None:
                _fail("L9B6_SUPERSEDED_SUCCESSOR_REQUIRED")
            _identity("successor_client_grant_id", successor_id)
            _fingerprint("successor_client_grant_fingerprint", successor_fp)
            if successor_id == self.client_grant_id or successor_fp == self.client_grant_fingerprint:
                _fail("L9B6_SELF_SUPERSESSION")
            if cap_id is not None:
                _fail("L9B6_SUPERSESSION_CAPACITY_FORBIDDEN")
        object.__setattr__(self, "event", event)
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "breadth", breadth)
        object.__setattr__(self, "occurred_at", occurred)
        object.__setattr__(self, "effective_from", effective)
        object.__setattr__(self, "capabilities", capabilities)
        object.__setattr__(self, "authorization_evidence_reference", auth_ref)
        object.__setattr__(self, "authorization_evidence_fingerprint", auth_fp)
        object.__setattr__(self, "source_evidence_reference", source_ref)
        object.__setattr__(self, "source_evidence_fingerprint", source_fp)
        object.__setattr__(self, "idempotency_key", idem)
        digest = _digest(self)
        if self.fingerprint and (not isinstance(self.fingerprint, str) or not hmac.compare_digest(self.fingerprint, digest)):
            _fail("L9B6_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize this exact event without mutable status fields."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_client_grant(cls, **values: object) -> "LegalClientMatterMandateGrantLifecycle":
        """Construct through the canonical exact-grant factory.

        The classmethod is a convenience boundary only; it delegates all
        scope, chronology, successor, and provenance checks to the module
        factory and performs no persistence or transaction work.
        """
        return record_legal_client_matter_mandate_grant_lifecycle(**cast(Any, values))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LegalClientMatterMandateGrantLifecycle":
        """Hydrate the exact schema and verify its deterministic fingerprint."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9B6_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, result.fingerprint):
            _fail("L9B6_FINGERPRINT_MISMATCH")
        return result


def _event(value: object) -> LegalClientMatterMandateGrantLifecycleEvent:
    try:
        return LegalClientMatterMandateGrantLifecycleEvent(value)
    except (TypeError, ValueError) as error:
        _fail("L9B6_EVENT_INVALID", error)


def _reason(value: object) -> LegalClientMatterMandateGrantLifecycleReason:
    try:
        return LegalClientMatterMandateGrantLifecycleReason(value)
    except (TypeError, ValueError) as error:
        _fail("L9B6_REASON_INVALID", error)


def _breadth(value: object) -> LegalClientMatterMandateBreadth:
    try:
        return LegalClientMatterMandateBreadth(value)
    except (TypeError, ValueError) as error:
        _fail("L9B6_BREADTH_INVALID", error)


def record_legal_client_matter_mandate_grant_lifecycle(
    *,
    client_grant: LegalClientMatterMandateGrant,
    lifecycle_event_id: str,
    event: LegalClientMatterMandateGrantLifecycleEvent | str,
    decision_actor_principal_id: str,
    authorization_evidence_reference: str,
    authorization_evidence_fingerprint: str,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
    occurred_at: datetime,
    effective_from: datetime,
    idempotency_key: str,
    reason: LegalClientMatterMandateGrantLifecycleReason | str | None = None,
    acting_capacity_id: str | None = None,
    acting_capacity_fingerprint: str | None = None,
    successor_grant: LegalClientMatterMandateGrant | None = None,
    lifecycle_version: str = VERSION,
) -> LegalClientMatterMandateGrantLifecycle:
    """Construct one exact grant-bound lifecycle event without persistence."""
    if type(client_grant) is not LegalClientMatterMandateGrant:
        _fail("L9B6_PRIMARY_GRANT_REQUIRED")
    selected = _event(event)
    if lifecycle_version != VERSION:
        _fail("L9B6_IDENTITY_INVALID")
    occurred = _timestamp("occurred_at", occurred_at)
    effective = _timestamp("effective_from", effective_from)
    if effective < occurred:
        _fail("L9B6_EFFECTIVE_FROM_BEFORE_OCCURRED")
    if client_grant.effective_from > effective:
        _fail("L9B6_GRANT_NOT_EFFECTIVE_AT_EVENT")
    successor_id: str | None = None
    successor_fp: str | None = None
    if selected is LegalClientMatterMandateGrantLifecycleEvent.REVOKED:
        if successor_grant is not None:
            _fail("L9B6_REVOKED_SUCCESSOR_FORBIDDEN")
    else:
        if type(successor_grant) is not LegalClientMatterMandateGrant:
            _fail("L9B6_SUPERSEDED_SUCCESSOR_REQUIRED")
        assert successor_grant is not None
        same_key = (
            successor_grant.tenant_id == client_grant.tenant_id
            and successor_grant.case_matter_id == client_grant.case_matter_id
            and successor_grant.matter_fingerprint == client_grant.matter_fingerprint
            and successor_grant.client_party_id == client_grant.client_party_id
            and successor_grant.subject_identity_fingerprint == client_grant.subject_identity_fingerprint
            and successor_grant.breadth is client_grant.breadth
            and successor_grant.scope_fingerprint == client_grant.scope_fingerprint
            and successor_grant.capabilities == client_grant.capabilities
        )
        if not same_key:
            _fail("L9B6_CURRENTNESS_KEY_MISMATCH")
        successor_id, successor_fp = successor_grant.client_grant_id, successor_grant.fingerprint
        if successor_grant.effective_from > effective:
            _fail("L9B6_GRANT_NOT_EFFECTIVE_AT_EVENT")
        if successor_grant.effective_until is not None and effective >= successor_grant.effective_until:
            _fail("L9B6_SUCCESSOR_EXPIRED_AT_EVENT")
    return LegalClientMatterMandateGrantLifecycle(
        lifecycle_event_id=lifecycle_event_id,
        event=selected,
        tenant_id=client_grant.tenant_id,
        case_matter_id=client_grant.case_matter_id,
        matter_fingerprint=client_grant.matter_fingerprint,
        client_party_id=client_grant.client_party_id,
        subject_identity_fingerprint=client_grant.subject_identity_fingerprint,
        breadth=client_grant.breadth,
        scope_fingerprint=client_grant.scope_fingerprint,
        capabilities=client_grant.capabilities,
        client_grant_id=client_grant.client_grant_id,
        client_grant_fingerprint=client_grant.fingerprint,
        successor_client_grant_id=successor_id,
        successor_client_grant_fingerprint=successor_fp,
        decision_actor_principal_id=decision_actor_principal_id,
        acting_capacity_id=acting_capacity_id,
        acting_capacity_fingerprint=acting_capacity_fingerprint,
        authorization_evidence_reference=authorization_evidence_reference,
        authorization_evidence_fingerprint=authorization_evidence_fingerprint,
        source_evidence_reference=source_evidence_reference,
        source_evidence_fingerprint=source_evidence_fingerprint,
        reason=reason,
        occurred_at=occurred,
        effective_from=effective,
        idempotency_key=idempotency_key,
        lifecycle_version=lifecycle_version,
    )


__all__ = [
    "LIFECYCLE_FIELDS", "SCHEMA", "VERSION",
    "LegalClientMatterMandateGrantLifecycle",
    "LegalClientMatterMandateGrantLifecycleError",
    "LegalClientMatterMandateGrantLifecycleEvent",
    "LegalClientMatterMandateGrantLifecycleReason",
    "record_legal_client_matter_mandate_grant_lifecycle",
]


# ARTIFACT: legal_client_matter_mandate_grant_lifecycle.py
# VERSION: v1.0.0-L9B6-CLIENT-MANDATE-GRANT-LIFECYCLE
# AUTHORITY BOUNDARY: immutable client-mandate lifecycle evidence only
# TENANT POSTURE: exact grant and currentness-key binding; no fallback
# FAIL-CLOSED POSTURE: strict event, chronology, scope and fingerprint validation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
