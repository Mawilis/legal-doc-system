"""WILSY OS immutable client self-appointment authorization evidence.

TITLE: WILSY OS Legal Client Matter Representation Authorization Evidence
VERSION: v1.0.0-L9C11-P17-CLIENT-REPRESENTATION-AUTHORIZATION-EVIDENCE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Preserve one positive, immutable evaluation snapshot proving that an
         authenticated exact client subject authorized one bounded internal
         Representation appointment. This value is evidence only; it is not a
         live authorization check, IAM grant, formed Representation, currentness
         state, Court authority, or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_representation_authorization_evidence.py
COLLABORATION / OWNERSHIP: CaseMatter, LegalMatterParty, Engagement, Mandate,
                            ActingCapacity and P1 Representation authority own
                            their evidence. This artifact owns only the
                            positive client-appointment authorization snapshot.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P17 establishes deterministic positive authorization
           evidence, SELF-only capacity, closed internal representative roles,
           exact tenant/matter/client lineage, mandate-bounded non-Court scope,
           strict hydration, immutable source revisions and SHA3-512 integrity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers, bounded references, lifecycle
                             snapshots and lowercase SHA3-512 only; no secrets,
                             passwords, tokens or full foreign objects.
TENANT BOUNDARY: Every actor, representative, role revision and lineage value
                 is explicitly bound to one tenant; no cross-tenant inference.
AUTHORITY BOUNDARY: Positive client self-appointment evidence only. The domain
                    does not authenticate, query IAM/currentness, select roles,
                    construct P1, persist records, or create Court authority.
FINANCIAL AUTHORITY BOUNDARY: No billing, payment, settlement, trust, release
                              or execution truth; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Pure immutable construction, deterministic serialization
                      and strict hydration only; no database, clock, network,
                      transaction, retry, registry or orchestration behavior.
FAIL-CLOSED DECLARATION: Malformed lineage, status, role, capacity, scope,
                         chronology, replay identity, schema or fingerprint
                         divergence rejects without coercion or authority gain.
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

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    LegalClientActingCapacityType,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate import (
    LegalClientMatterMandateCapability,
)


VERSION: Final[str] = "v1.0.0-L9C11-P17-CLIENT-REPRESENTATION-AUTHORIZATION-EVIDENCE"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-REPRESENTATION-AUTHORIZATION-EVIDENCE/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)
ELIGIBLE_REPRESENTATIVE_ROLES: Final[frozenset[str]] = frozenset(
    {"LEGAL_ATTORNEY", "LEGAL_PARTNER"}
)
_NON_COURT_CAPABILITIES: Final[frozenset[str]] = frozenset(
    capability.value
    for capability in LegalClientMatterMandateCapability
    if not capability.value.startswith("COURT_")
)
_MANDATE_CAPABILITIES: Final[frozenset[str]] = frozenset(
    capability.value for capability in LegalClientMatterMandateCapability
)

_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "authorization_version",
    "evidence_id",
    "tenant_id",
    "case_matter_id",
    "matter_fingerprint",
    "client_party_id",
    "subject_reference",
    "subject_identity_fingerprint",
    "client_subject_principal_id",
    "appointing_principal_id",
    "appointing_principal_status",
    "appointing_membership_status",
    "appointing_membership_revision",
    "appointing_role",
    "appointing_role_assignment_revision",
    "client_visibility_reference",
    "client_visibility_fingerprint",
    "client_visibility_status",
    "acting_capacity_id",
    "acting_capacity_fingerprint",
    "acting_capacity_type",
    "engagement_id",
    "engagement_fingerprint",
    "mandate_id",
    "mandate_fingerprint",
    "mandate_scope_reference",
    "mandate_scope_fingerprint",
    "mandate_capabilities",
    "representative_principal_id",
    "representative_principal_status",
    "representative_membership_status",
    "representative_membership_revision",
    "representative_role_assignment_revision",
    "representative_role",
    "representative_eligibility_policy_version",
    "representation_scope_capabilities",
    "decision",
    "source_evidence_reference",
    "source_evidence_fingerprint",
    "occurred_at",
    "effective_from",
    "idempotency_key",
    "fingerprint",
)
REPRESENTATION_AUTHORIZATION_EVIDENCE_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientMatterRepresentationAuthorizationDecision(StrEnum):
    """The sole durable positive client appointment decision."""

    AUTHORIZED = "AUTHORIZED"


class LegalClientMatterRepresentationAuthorizationEvidenceError(ValueError):
    """Stable, non-sensitive failure from evidence validation."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded code and never supplied evidence data."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable failure while retaining technical cause internally."""
    error = LegalClientMatterRepresentationAuthorizationEvidenceError(code)
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
        _fail(f"L9C11_P17_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    """Require one explicit non-global tenant identity."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9C11_P17_TENANT_REQUIRED")
    return tenant


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
        _fail(f"L9C11_P17_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or len(normalized) > limit:
        _fail(f"L9C11_P17_{name.upper()}_INVALID")
    return normalized


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 hexadecimal fingerprint."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9C11_P17_{name.upper()}_INVALID")
    return value


def _revision(name: str, value: object) -> int:
    """Require one explicit non-negative source revision."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _fail(f"L9C11_P17_{name.upper()}_INVALID")
    return value


def _active_principal_status(name: str, value: object) -> PrincipalStatus:
    """Require an explicitly recorded ACTIVE principal status."""
    try:
        status = PrincipalStatus(value)
    except (TypeError, ValueError) as error:
        _fail(f"L9C11_P17_{name.upper()}_INVALID", error)
    if status is not PrincipalStatus.ACTIVE:
        _fail(f"L9C11_P17_{name.upper()}_NOT_ACTIVE")
    return status


def _active_membership_status(name: str, value: object) -> TenantMembershipStatus:
    """Require an explicitly recorded ACTIVE tenant membership status."""
    try:
        status = TenantMembershipStatus(value)
    except (TypeError, ValueError) as error:
        _fail(f"L9C11_P17_{name.upper()}_INVALID", error)
    if status is not TenantMembershipStatus.ACTIVE:
        _fail(f"L9C11_P17_{name.upper()}_NOT_ACTIVE")
    return status


def _role(value: object) -> str:
    """Require one exact role from the frozen internal eligibility set."""
    if not isinstance(value, str) or value not in ELIGIBLE_REPRESENTATIVE_ROLES:
        _fail("L9C11_P17_REPRESENTATIVE_ROLE_INELIGIBLE")
    return value


def _capabilities(name: str, value: object, *, allow_court: bool) -> tuple[str, ...]:
    """Normalize the canonical Mandate capability vocabulary deterministically."""
    if not isinstance(value, (tuple, list, set, frozenset)) or not value:
        _fail(f"L9C11_P17_{name.upper()}_INVALID")
    normalized: set[str] = set()
    allowed = _MANDATE_CAPABILITIES if allow_court else _NON_COURT_CAPABILITIES
    for item in value:
        label = getattr(item, "value", item)
        if not isinstance(label, str) or label != label.strip() or not label:
            _fail(f"L9C11_P17_{name.upper()}_INVALID")
        label = label.upper()
        if not allow_court and label.startswith("COURT_"):
            _fail("L9C11_P17_COURT_SCOPE_FORBIDDEN")
        if label not in allowed:
            _fail(f"L9C11_P17_{name.upper()}_INVALID")
        normalized.add(label)
    return tuple(sorted(normalized))


def _timestamp(name: str, value: object) -> datetime:
    """Require an aware timestamp and normalize it to UTC microseconds."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9C11_P17_{name.upper()}_INVALID", error)
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _fail(f"L9C11_P17_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    """Convert immutable values into deterministic JSON-safe primitives."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat(
            timespec="microseconds"
        ).replace("+00:00", "Z")
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, (tuple, list)):
        return [_json_value(item) for item in value]
    return value


def _canonical_json(payload: Mapping[str, object]) -> bytes:
    """Serialize one canonical payload with stable keys and separators."""
    return json.dumps(
        {key: _json_value(value) for key, value in payload.items()},
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _strict_hydration_capabilities(name: str, value: object) -> None:
    """Reject persisted capability arrays that are not already canonical."""
    if not isinstance(value, list) or any(
        not isinstance(item, str) or item != item.upper() for item in value
    ):
        _fail(f"L9C11_P17_{name.upper()}_INVALID")
    canonical = sorted(set(cast(list[str], value)))
    if len(canonical) != len(value) or value != canonical:
        _fail(f"L9C11_P17_{name.upper()}_NONCANONICAL")


def _evidence_id(payload: Mapping[str, object]) -> str:
    """Derive deterministic identity from every non-derived intent field."""
    digest = hashlib.sha3_512(_canonical_json(payload)).hexdigest()
    return f"client-representation-authorization:{digest}"


def _digest(instance: "LegalClientMatterRepresentationAuthorizationEvidence") -> str:
    """Hash every declared semantic field except the derived fingerprint."""
    payload = {
        field: getattr(instance, field)
        for field in _FIELDS[:-1]
    }
    return hashlib.sha3_512(_canonical_json(payload)).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalClientMatterRepresentationAuthorizationEvidence:
    """Immutable positive client self-appointment evidence snapshot.

    All live authority, IAM, currentness, role-selection and eligibility
    evaluation is performed by a future trusted issuer. This value object only
    validates and preserves the issuer's already-evaluated evidence.
    """

    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    client_party_id: str
    subject_reference: str
    subject_identity_fingerprint: str
    client_subject_principal_id: str
    appointing_principal_id: str
    appointing_principal_status: PrincipalStatus | str
    appointing_membership_status: TenantMembershipStatus | str
    appointing_membership_revision: int
    appointing_role: str
    appointing_role_assignment_revision: int
    client_visibility_reference: str
    client_visibility_fingerprint: str
    client_visibility_status: str
    acting_capacity_id: str
    acting_capacity_fingerprint: str
    acting_capacity_type: LegalClientActingCapacityType | str
    engagement_id: str
    engagement_fingerprint: str
    mandate_id: str
    mandate_fingerprint: str
    mandate_scope_reference: str
    mandate_scope_fingerprint: str
    mandate_capabilities: tuple[str, ...] | list[str]
    representative_principal_id: str
    representative_principal_status: PrincipalStatus | str
    representative_membership_status: TenantMembershipStatus | str
    representative_membership_revision: int
    representative_role_assignment_revision: int
    representative_role: str
    representative_eligibility_policy_version: str
    representation_scope_capabilities: tuple[str, ...] | list[str]
    decision: LegalClientMatterRepresentationAuthorizationDecision | str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    occurred_at: datetime
    effective_from: datetime
    idempotency_key: str
    schema: str = SCHEMA
    authorization_version: str = VERSION
    evidence_id: str = ""
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate snapshots, derive identity, and verify integrity."""
        if self.schema != SCHEMA or self.authorization_version != VERSION:
            _fail("L9C11_P17_IDENTITY_INVALID")

        normalized: dict[str, object] = {
            "tenant_id": _tenant(self.tenant_id),
            "case_matter_id": _identity("case_matter_id", self.case_matter_id),
            "matter_fingerprint": _fingerprint("matter_fingerprint", self.matter_fingerprint),
            "client_party_id": _identity("client_party_id", self.client_party_id),
            "subject_reference": _reference("subject_reference", self.subject_reference, limit=224),
            "subject_identity_fingerprint": _fingerprint("subject_identity_fingerprint", self.subject_identity_fingerprint),
            "client_subject_principal_id": _identity("client_subject_principal_id", self.client_subject_principal_id),
            "appointing_principal_id": _identity("appointing_principal_id", self.appointing_principal_id),
            "appointing_principal_status": _active_principal_status("appointing_principal_status", self.appointing_principal_status),
            "appointing_membership_status": _active_membership_status("appointing_membership_status", self.appointing_membership_status),
            "appointing_membership_revision": _revision("appointing_membership_revision", self.appointing_membership_revision),
            "appointing_role": _identity("appointing_role", self.appointing_role),
            "appointing_role_assignment_revision": _revision("appointing_role_assignment_revision", self.appointing_role_assignment_revision),
            "client_visibility_reference": _reference("client_visibility_reference", self.client_visibility_reference),
            "client_visibility_fingerprint": _fingerprint("client_visibility_fingerprint", self.client_visibility_fingerprint),
            "client_visibility_status": _reference("client_visibility_status", self.client_visibility_status, limit=32),
            "acting_capacity_id": _identity("acting_capacity_id", self.acting_capacity_id),
            "acting_capacity_fingerprint": _fingerprint("acting_capacity_fingerprint", self.acting_capacity_fingerprint),
            "engagement_id": _identity("engagement_id", self.engagement_id),
            "engagement_fingerprint": _fingerprint("engagement_fingerprint", self.engagement_fingerprint),
            "mandate_id": _identity("mandate_id", self.mandate_id),
            "mandate_fingerprint": _fingerprint("mandate_fingerprint", self.mandate_fingerprint),
            "mandate_scope_reference": _reference("mandate_scope_reference", self.mandate_scope_reference),
            "mandate_scope_fingerprint": _fingerprint("mandate_scope_fingerprint", self.mandate_scope_fingerprint),
            "mandate_capabilities": _capabilities("mandate_capabilities", self.mandate_capabilities, allow_court=True),
            "representative_principal_id": _identity("representative_principal_id", self.representative_principal_id),
            "representative_principal_status": _active_principal_status("representative_principal_status", self.representative_principal_status),
            "representative_membership_status": _active_membership_status("representative_membership_status", self.representative_membership_status),
            "representative_membership_revision": _revision("representative_membership_revision", self.representative_membership_revision),
            "representative_role_assignment_revision": _revision("representative_role_assignment_revision", self.representative_role_assignment_revision),
            "representative_role": _role(self.representative_role),
            "representative_eligibility_policy_version": _reference("representative_eligibility_policy_version", self.representative_eligibility_policy_version, limit=160),
            "representation_scope_capabilities": _capabilities("representation_scope_capabilities", self.representation_scope_capabilities, allow_court=False),
            "source_evidence_reference": _reference("source_evidence_reference", self.source_evidence_reference),
            "source_evidence_fingerprint": _fingerprint("source_evidence_fingerprint", self.source_evidence_fingerprint),
            "occurred_at": _timestamp("occurred_at", self.occurred_at),
            "effective_from": _timestamp("effective_from", self.effective_from),
            "idempotency_key": _reference("idempotency_key", self.idempotency_key, limit=240),
        }

        try:
            capacity_type = LegalClientActingCapacityType(self.acting_capacity_type)
        except (TypeError, ValueError) as error:
            _fail("L9C11_P17_ACTING_CAPACITY_TYPE_INVALID", error)
        if capacity_type is not LegalClientActingCapacityType.SELF:
            _fail("L9C11_P17_SELF_CAPACITY_REQUIRED")
        normalized["acting_capacity_type"] = capacity_type

        if normalized["appointing_principal_id"] != normalized["client_subject_principal_id"]:
            _fail("L9C11_P17_APPOINTING_PRINCIPAL_CLIENT_SUBJECT_MISMATCH")
        if normalized["appointing_role"] != "LEGAL_CLIENT":
            _fail("L9C11_P17_APPOINTING_ROLE_INVALID")
        if normalized["client_visibility_status"] != "ACTIVE":
            _fail("L9C11_P17_CLIENT_VISIBILITY_NOT_ACTIVE")
        try:
            decision = LegalClientMatterRepresentationAuthorizationDecision(self.decision)
        except (TypeError, ValueError) as error:
            _fail("L9C11_P17_DECISION_INVALID", error)
        normalized["decision"] = decision

        occurred_at = cast(datetime, normalized["occurred_at"])
        effective_from = cast(datetime, normalized["effective_from"])
        if effective_from < occurred_at:
            _fail("L9C11_P17_EFFECTIVE_FROM_BEFORE_OCCURRED")

        scope = cast(tuple[str, ...], normalized["representation_scope_capabilities"])
        mandate = cast(tuple[str, ...], normalized["mandate_capabilities"])
        if not set(scope).issubset(mandate):
            _fail("L9C11_P17_SCOPE_EXCEEDS_MANDATE")

        for name, value in normalized.items():
            object.__setattr__(self, name, value)

        intent = {
            field: getattr(self, field)
            for field in _FIELDS
            if field not in {"evidence_id", "fingerprint"}
        }
        derived_id = _evidence_id(intent)
        if self.evidence_id and self.evidence_id != derived_id:
            _fail("L9C11_P17_EVIDENCE_ID_MISMATCH")
        object.__setattr__(self, "evidence_id", derived_id)

        digest = _digest(self)
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            _fail("L9C11_P17_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @property
    def is_authorized(self) -> bool:
        """Return whether this immutable snapshot is the positive decision."""
        return self.decision is LegalClientMatterRepresentationAuthorizationDecision.AUTHORIZED

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact immutable evidence snapshot."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(
        cls, payload: Mapping[str, object]
    ) -> "LegalClientMatterRepresentationAuthorizationEvidence":
        """Hydrate only the exact schema and verify derived integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9C11_P17_SCHEMA_INVALID")
        _strict_hydration_capabilities(
            "mandate_capabilities", payload["mandate_capabilities"]
        )
        _strict_hydration_capabilities(
            "representation_scope_capabilities",
            payload["representation_scope_capabilities"],
        )
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, result.fingerprint):
            _fail("L9C11_P17_FINGERPRINT_MISMATCH")
        return result


__all__ = [
    "ELIGIBLE_REPRESENTATIVE_ROLES",
    "REPRESENTATION_AUTHORIZATION_EVIDENCE_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientMatterRepresentationAuthorizationDecision",
    "LegalClientMatterRepresentationAuthorizationEvidence",
    "LegalClientMatterRepresentationAuthorizationEvidenceError",
]


# ARTIFACT: legal_client_matter_representation_authorization_evidence.py
# VERSION: v1.0.0-L9C11-P17-CLIENT-REPRESENTATION-AUTHORIZATION-EVIDENCE
# AUTHORITY BOUNDARY: positive client self-appointment evidence only
# TENANT POSTURE: exact tenant/matter/client/role/revision lineage; no fallback
# FAIL-CLOSED POSTURE: strict schema, SELF capacity, role, scope and integrity validation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
