"""WILSY OS immutable client mandate-grant evidence domain.

TITLE: WILSY OS Legal Client Matter Mandate Grant
VERSION: v1.0.0-L9B4-CLIENT-MATTER-MANDATE-GRANT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Record immutable evidence that one exact client-side matter party,
         through one exact actor/capacity provenance, explicitly granted one
         bounded mandate scope for one exact CaseMatter. This artifact is
         grant evidence only; it does not establish firm acknowledgment,
         mandate currentness, Engagement, Representation, Court authority,
         settlement execution, or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_mandate_grant.py
COLLABORATION / OWNERSHIP: CaseMatter and LegalMatterParty own canonical
                            matter/party identity; LegalClientActingCapacity
                            owns actor provenance; the published mandate
                            domain owns the sole breadth/capability vocabulary;
                            this artifact owns only immutable client-grant
                            evidence. Future IAM, registry/currentness,
                            firm acknowledgment, mandate, Engagement,
                            Representation and Court authorities remain
                            separate.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B4-CLIENT-MATTER-MANDATE-GRANT establishes exact
           client-side subject binding, actor/capacity provenance, reuse of
           the canonical LIMITED/TASK_SPECIFIC and preparation-oriented
           capability vocabulary, source and authorization evidence,
           server-derived UTC chronology, deterministic SHA3-512 integrity,
           strict hydration and explicit idempotency evidence. It creates no
           currentness, revocation, firm acknowledgment or runtime authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers, bounded references and
                             lowercase SHA3-512 fingerprints only; no raw PII,
                             credentials, tokens, JWT/session material or
                             evidence bodies are retained.
TENANT BOUNDARY: Tenant, matter, client party, subject identity and actor
                 capacity derive from exact canonical objects; cross-tenant,
                 cross-matter, wrong-party and non-client values reject without
                 fallback or inference.
AUTHORITY BOUNDARY: Immutable client-grant evidence only. Explicit upstream
                    authenticated intent is required; viewing, downloading,
                    opening a matter, prior instructions, invoices or platform
                    terms never become a grant. This value does not authenticate
                    the actor, authorize IAM, establish currentness, firm
                    acknowledgment, Engagement, Representation or Court action.
FINANCIAL AUTHORITY BOUNDARY: No payment, fund transfer, final settlement,
                              invoice execution or financial authority; Kennel
                              EOS remains exclusive financial execution
                              authority.
TRANSACTION BOUNDARY: Pure immutable construction, deterministic
                      serialization and strict hydration only; no database,
                      HTTP, IAM, registry, transaction, retry, notification or
                      network behavior.
FAIL-CLOSED DECLARATION: Malformed, cross-scope, non-client, stale-capacity,
                         unknown-capability, duplicate-capability, chronology,
                         schema or fingerprint drift rejects without coercion or
                         authority expansion.
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

from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    LegalClientActingCapacity,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate import (
    LegalClientMatterMandateBreadth,
    LegalClientMatterMandateCapability,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterParty,
    LegalMatterPartyRole,
    LegalMatterPartySide,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)


VERSION: Final[str] = "v1.0.0-L9B4-CLIENT-MATTER-MANDATE-GRANT"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-MANDATE-GRANT/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)
_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "grant_version",
    "client_grant_id",
    "tenant_id",
    "case_matter_id",
    "matter_fingerprint",
    "client_party_id",
    "subject_identity_fingerprint",
    "grant_actor_principal_id",
    "acting_capacity_id",
    "acting_capacity_fingerprint",
    "breadth",
    "scope_reference",
    "scope_fingerprint",
    "capabilities",
    "source_evidence_reference",
    "source_evidence_fingerprint",
    "authorization_evidence_reference",
    "authorization_evidence_fingerprint",
    "occurred_at",
    "effective_from",
    "effective_until",
    "idempotency_key",
    "fingerprint",
)
MANDATE_GRANT_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientMatterMandateGrantError(ValueError):
    """Stable, non-sensitive failure from grant-evidence validation."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded code and never echo authority-bearing input."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable error while retaining any technical cause internally."""
    error = LegalClientMatterMandateGrantError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    """Require one bounded opaque identity without trimming or coercion."""
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _fail(f"L9B4_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    """Require one explicit tenant and reject pseudo/global scopes."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9B4_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    """Require lowercase SHA3-512 hexadecimal evidence."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9B4_{name.upper()}_INVALID")
    return value


def _reference(name: str, value: object, *, limit: int = 512) -> str:
    """Require bounded NFC single-line evidence/reference text."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(
            ord(character) < 32
            or 0x7F <= ord(character) <= 0x9F
            or 0xD800 <= ord(character) <= 0xDFFF
            for character in value
        )
    ):
        _fail(f"L9B4_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or len(normalized) > limit:
        _fail(f"L9B4_{name.upper()}_INVALID")
    return normalized


def _timestamp(name: str, value: object) -> datetime:
    """Require an aware timestamp and normalize it to UTC microseconds."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9B4_{name.upper()}_INVALID", error)
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _fail(f"L9B4_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc)


def _normalize_capabilities(value: object) -> tuple[LegalClientMatterMandateCapability, ...]:
    """Reuse the canonical mandate enum with deterministic ordering."""
    if not isinstance(value, (tuple, list, set, frozenset)) or isinstance(value, str):
        _fail("L9B4_CAPABILITIES_INVALID")
    raw = tuple(cast(Any, value))
    try:
        capabilities = tuple(LegalClientMatterMandateCapability(item) for item in raw)
    except (TypeError, ValueError) as error:
        _fail("L9B4_CAPABILITY_UNKNOWN", error)
    if not capabilities:
        _fail("L9B4_CAPABILITIES_EMPTY")
    if len(set(capabilities)) != len(capabilities):
        _fail("L9B4_CAPABILITY_DUPLICATE")
    return tuple(sorted(capabilities, key=lambda item: item.value))


def _json_value(value: object) -> object:
    """Convert immutable values into deterministic JSON-safe values."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace(
            "+00:00", "Z"
        )
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    return value


def _digest(instance: "LegalClientMatterMandateGrant") -> str:
    """Hash every declared semantic field except the derived fingerprint."""
    payload = {field: _json_value(getattr(instance, field)) for field in _FIELDS[:-1]}
    return hashlib.sha3_512(
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=False,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalClientMatterMandateGrant:
    """Immutable bounded grant evidence for one exact client matter.

    The actor principal is provenance, never the grant subject. Construction
    requires explicit upstream authenticated intent represented by source
    evidence; this value does not authenticate the actor or grant IAM. It
    performs no persistence and owns no transaction, currentness, revocation,
    firm acknowledgment, Engagement, Representation, Court or finance.
    """

    client_grant_id: str
    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    client_party_id: str
    subject_identity_fingerprint: str
    grant_actor_principal_id: str
    acting_capacity_id: str
    acting_capacity_fingerprint: str
    breadth: LegalClientMatterMandateBreadth | str
    scope_reference: str
    scope_fingerprint: str
    capabilities: tuple[LegalClientMatterMandateCapability, ...] | list[str]
    source_evidence_reference: str
    source_evidence_fingerprint: str
    authorization_evidence_reference: str
    authorization_evidence_fingerprint: str
    occurred_at: datetime
    effective_from: datetime
    effective_until: datetime | None
    idempotency_key: str
    schema: str = SCHEMA
    grant_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate every semantic field and compute or verify integrity."""
        tenant = _tenant(self.tenant_id)
        grant_id = _identity("client_grant_id", self.client_grant_id)
        grant_version = _identity("grant_version", self.grant_version)
        matter_id = _identity("case_matter_id", self.case_matter_id)
        matter_fingerprint = _fingerprint("matter_fingerprint", self.matter_fingerprint)
        party_id = _identity("client_party_id", self.client_party_id)
        subject_fingerprint = _fingerprint(
            "subject_identity_fingerprint", self.subject_identity_fingerprint
        )
        principal = _identity("grant_actor_principal_id", self.grant_actor_principal_id)
        capacity_id = _identity("acting_capacity_id", self.acting_capacity_id)
        capacity_fingerprint = _fingerprint(
            "acting_capacity_fingerprint", self.acting_capacity_fingerprint
        )
        try:
            breadth = LegalClientMatterMandateBreadth(self.breadth)
        except (TypeError, ValueError) as error:
            _fail("L9B4_BREADTH_INVALID", error)
        scope_reference = _reference("scope_reference", self.scope_reference)
        scope_fingerprint = _fingerprint("scope_fingerprint", self.scope_fingerprint)
        capabilities = _normalize_capabilities(self.capabilities)
        source_reference = _reference("source_evidence_reference", self.source_evidence_reference)
        source_fingerprint = _fingerprint(
            "source_evidence_fingerprint", self.source_evidence_fingerprint
        )
        authorization_reference = _reference(
            "authorization_evidence_reference", self.authorization_evidence_reference
        )
        authorization_fingerprint = _fingerprint(
            "authorization_evidence_fingerprint", self.authorization_evidence_fingerprint
        )
        occurred = _timestamp("occurred_at", self.occurred_at)
        effective = _timestamp("effective_from", self.effective_from)
        until = None if self.effective_until is None else _timestamp("effective_until", self.effective_until)
        idempotency_key = _reference("idempotency_key", self.idempotency_key, limit=240)
        if self.schema != SCHEMA or grant_version != VERSION:
            _fail("L9B4_IDENTITY_INVALID")
        if effective < occurred:
            _fail("L9B4_EFFECTIVE_FROM_BEFORE_OCCURRED")
        if until is not None and until <= effective:
            _fail("L9B4_EFFECTIVE_UNTIL_INVALID")

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "grant_version", grant_version)
        object.__setattr__(self, "client_grant_id", grant_id)
        object.__setattr__(self, "case_matter_id", matter_id)
        object.__setattr__(self, "matter_fingerprint", matter_fingerprint)
        object.__setattr__(self, "client_party_id", party_id)
        object.__setattr__(self, "subject_identity_fingerprint", subject_fingerprint)
        object.__setattr__(self, "grant_actor_principal_id", principal)
        object.__setattr__(self, "acting_capacity_id", capacity_id)
        object.__setattr__(self, "acting_capacity_fingerprint", capacity_fingerprint)
        object.__setattr__(self, "breadth", breadth)
        object.__setattr__(self, "scope_reference", scope_reference)
        object.__setattr__(self, "scope_fingerprint", scope_fingerprint)
        object.__setattr__(self, "capabilities", capabilities)
        object.__setattr__(self, "source_evidence_reference", source_reference)
        object.__setattr__(self, "source_evidence_fingerprint", source_fingerprint)
        object.__setattr__(self, "authorization_evidence_reference", authorization_reference)
        object.__setattr__(self, "authorization_evidence_fingerprint", authorization_fingerprint)
        object.__setattr__(self, "occurred_at", occurred)
        object.__setattr__(self, "effective_from", effective)
        object.__setattr__(self, "effective_until", until)
        object.__setattr__(self, "idempotency_key", idempotency_key)

        digest = _digest(self)
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            _fail("L9B4_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact immutable grant snapshot without raw PII."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LegalClientMatterMandateGrant":
        """Hydrate only the exact schema and verify deterministic integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9B4_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, result.fingerprint):
            _fail("L9B4_FINGERPRINT_MISMATCH")
        return result

    @classmethod
    def from_canonical(
        cls,
        *,
        client_grant_id: str,
        case_matter: CaseMatter,
        party: LegalMatterParty,
        acting_capacity: LegalClientActingCapacity,
        breadth: LegalClientMatterMandateBreadth | str,
        scope_reference: str,
        scope_fingerprint: str,
        capabilities: tuple[LegalClientMatterMandateCapability, ...] | list[str],
        source_evidence_reference: str,
        source_evidence_fingerprint: str,
        authorization_evidence_reference: str,
        authorization_evidence_fingerprint: str,
        occurred_at: datetime,
        effective_from: datetime,
        idempotency_key: str,
        effective_until: datetime | None = None,
        grant_version: str = VERSION,
    ) -> "LegalClientMatterMandateGrant":
        """Derive a grant from exact canonical matter, party and capacity.

        The factory requires an OPEN matter and an exact client-side CLIENT
        party. It derives tenant, matter, party, subject and actor values from
        those objects and rejects cross-scope or stale capacity evidence. The
        actor/capacity binding is provenance only; authentication, IAM
        authorization, explicit confirmation, evidence sufficiency and all
        persistence/currentness decisions remain later-orchestrator duties.
        """
        if type(case_matter) is not CaseMatter:
            _fail("L9B4_CASE_MATTER_REQUIRED")
        if type(party) is not LegalMatterParty:
            _fail("L9B4_LEGAL_MATTER_PARTY_REQUIRED")
        if type(acting_capacity) is not LegalClientActingCapacity:
            _fail("L9B4_ACTING_CAPACITY_REQUIRED")
        try:
            case_matter.__post_init__()
            party.__post_init__()
            acting_capacity.__post_init__()
        except Exception as error:
            _fail("L9B4_CANONICAL_EVIDENCE_INVALID", error)
        if case_matter.state is not CaseMatterState.OPEN:
            _fail("L9B4_OPEN_CASE_MATTER_REQUIRED")
        if party.party_side is not LegalMatterPartySide.CLIENT_SIDE:
            _fail("L9B4_CLIENT_PARTY_REQUIRED")
        if party.matter_role is not LegalMatterPartyRole.CLIENT:
            _fail("L9B4_CLIENT_PARTY_ROLE_REQUIRED")
        if (
            party.tenant_id != case_matter.tenant_id
            or party.case_matter_id != case_matter.case_matter_id
            or party.matter_fingerprint != case_matter.fingerprint
        ):
            _fail("L9B4_PARTY_MATTER_MISMATCH")
        if (
            acting_capacity.tenant_id != case_matter.tenant_id
            or acting_capacity.case_matter_id != case_matter.case_matter_id
            or acting_capacity.matter_fingerprint != case_matter.fingerprint
            or acting_capacity.party_id != party.party_id
            or acting_capacity.subject_identity_fingerprint != party.subject_identity_fingerprint
        ):
            _fail("L9B4_CAPACITY_CORRELATION_MISMATCH")
        occurred = _timestamp("occurred_at", occurred_at)
        effective = _timestamp("effective_from", effective_from)
        if effective < max(case_matter.opened_at, party.registered_at, acting_capacity.effective_from):
            _fail("L9B4_EFFECTIVE_FROM_INVALID")
        if acting_capacity.effective_until is not None and effective >= acting_capacity.effective_until:
            _fail("L9B4_CAPACITY_NOT_VALID_AT_EFFECTIVE")
        return cls(
            client_grant_id=client_grant_id,
            tenant_id=case_matter.tenant_id,
            case_matter_id=case_matter.case_matter_id,
            matter_fingerprint=case_matter.fingerprint,
            client_party_id=party.party_id,
            subject_identity_fingerprint=party.subject_identity_fingerprint,
            grant_actor_principal_id=acting_capacity.principal_id,
            acting_capacity_id=acting_capacity.capacity_id,
            acting_capacity_fingerprint=acting_capacity.fingerprint,
            breadth=breadth,
            scope_reference=scope_reference,
            scope_fingerprint=scope_fingerprint,
            capabilities=capabilities,
            source_evidence_reference=source_evidence_reference,
            source_evidence_fingerprint=source_evidence_fingerprint,
            authorization_evidence_reference=authorization_evidence_reference,
            authorization_evidence_fingerprint=authorization_evidence_fingerprint,
            occurred_at=occurred,
            effective_from=effective,
            effective_until=effective_until,
            idempotency_key=idempotency_key,
            grant_version=grant_version,
        )


__all__ = [
    "MANDATE_GRANT_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientMatterMandateGrant",
    "LegalClientMatterMandateGrantError",
    "LegalClientMatterMandateBreadth",
    "LegalClientMatterMandateCapability",
]


# ARTIFACT: legal_client_matter_mandate_grant.py
# VERSION: v1.0.0-L9B4-CLIENT-MATTER-MANDATE-GRANT
# AUTHORITY BOUNDARY: immutable client-grant evidence only
# TENANT POSTURE: exact tenant/matter/client-party/capacity binding; no fallback
# FAIL-CLOSED POSTURE: strict schema, chronology, capability and fingerprint validation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
