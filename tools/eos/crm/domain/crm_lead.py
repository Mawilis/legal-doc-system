"""Sovereign immutable CRM Lead domain truth for WILSY OS.

TITLE: WILSY OS Sovereign CRM Lead Pure Domain
VERSION: v1.1.0-CRM-LEAD-DOMAIN
AUTHORITY: Wilsy OS Core Governance
EPITOME:
    Establishes the first canonical Python EOS CRM business entity: one
    immutable, tenant-bound Lead with server-owned identity, governed lifecycle
    classifications, deterministic serialization, explicit consent/source
    posture, bounded scoring, and no persistence or execution authority.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/crm/domain/crm_lead.py
COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy OS Core Engineering
CERTIFICATION / UPDATE DATE:
    2026-10-06
CHANGELOG:
    v1.1.0-CRM-LEAD-DOMAIN adds strict durable hydration preserving exact
    server-owned Lead identity while revalidating all canonical fields.
    v1.0.0-CRM-LEAD-DOMAIN introduced the canonical immutable CRM Lead value
    contract derived from the certified P5/P5-R2 client contract freeze and
    P6A direct test-first certificate.
COMPLIANCE:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
SECURITY / PRIVACY POSTURE:
    Rejects blank, padded, global/root and legacy MASTER tenant identities;
    canonicalizes email without manufacturing identity; retains only explicit
    business values; owns no secrets, network calls, persistence, authorization
    lookup, browser storage, or transport authority.
TENANT BOUNDARY:
    tenant_id is mandatory exact canonical scope. This pure domain accepts no
    default tenant, no raw HTTP-header authority and no cross-tenant fallback.
AUTHORITY BOUNDARY:
    Canonical CRM Lead value truth only. Persistence, replay, authorization,
    lifecycle command orchestration, HTTP, account conversion, opportunity,
    deal, quote, contract, invoice and AI execution remain separate authorities.
FINANCIAL AUTHORITY BOUNDARY:
    Lead score, priority, industry and commercial interest are CRM evidence or
    signals only. They are not revenue, invoice, payment, settlement or
    accounting truth. Kennel EOS remains exclusive financial execution
    authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
import re
from typing import Final
from uuid import UUID, uuid4


CRM_LEAD_DOMAIN_VERSION: Final[str] = "v1.1.0-CRM-LEAD-DOMAIN"

_FORBIDDEN_TENANT_IDENTITIES: Final[frozenset[str]] = frozenset(
    {
        "MASTER",
        "GLOBAL_ROOT",
        "SOVEREIGN_ROOT",
        "WILSY-SOVEREIGN-ROOT",
    }
)

_EMAIL_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


class CrmLeadDomainError(ValueError):
    """Reject malformed or unauthorized CRM Lead domain state.

    This exception represents pure-domain validation failure only. It performs
    no persistence, transport, authorization lookup, transaction handling or
    financial execution.
    """


class CrmLeadStatus(StrEnum):
    """Canonical source-derived Lead lifecycle classifications.

    Values exactly preserve the frozen client contract. A Lead status remains
    CRM state only and never implies deal creation, revenue or financial truth.
    """

    NEW = "NEW"
    PROSPECTING = "PROSPECTING"
    CONTACTED = "CONTACTED"
    ENGAGED = "ENGAGED"


class CrmLeadSourceChannel(StrEnum):
    """Canonical source channel through which a Lead entered WILSY CRM."""

    MANUAL = "manual"
    WEBSITE = "website"
    EMAIL = "email"
    REFERRAL = "referral"
    CAMPAIGN = "campaign"
    IMPORT = "import"
    API = "api"


class CrmLeadPriority(StrEnum):
    """Operator priority classification for CRM work sequencing."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"


class CrmLeadConsentBasis(StrEnum):
    """Explicit recorded processing-basis classification for a CRM Lead.

    This enum records the business classification supplied to the domain. It
    does not itself determine regulatory compliance or legal authorization.
    """

    CONSENT = "CONSENT"
    LEGITIMATE_INTEREST = "LEGITIMATE_INTEREST"
    CONTRACT = "CONTRACT"
    LEGAL_OBLIGATION = "LEGAL_OBLIGATION"


def _exact_identifier(value: object, code: str) -> str:
    """Require one non-empty, unpadded exact identifier."""

    if not isinstance(value, str):
        raise CrmLeadDomainError(code)

    if not value or not value.strip() or value != value.strip():
        raise CrmLeadDomainError(code)

    return value


def _tenant_id(value: object) -> str:
    """Require canonical tenant scope and reject root/default aliases."""

    tenant = _exact_identifier(value, "TENANT_ID_INVALID")

    if tenant.upper() in _FORBIDDEN_TENANT_IDENTITIES:
        raise CrmLeadDomainError("TENANT_ID_INVALID")

    return tenant


def _required_text(value: object, code: str) -> str:
    """Require non-empty text and return canonical trimmed representation."""

    if not isinstance(value, str):
        raise CrmLeadDomainError(code)

    normalized = value.strip()

    if not normalized:
        raise CrmLeadDomainError(code)

    return normalized


def _optional_text(value: object, code: str) -> str:
    """Require optional textual state to remain textual and trimmed."""

    if not isinstance(value, str):
        raise CrmLeadDomainError(code)

    return value.strip()


def _email(value: object) -> str:
    """Require a bounded syntactically valid email and lowercase it."""

    normalized = _required_text(value, "EMAIL_INVALID").lower()

    if len(normalized) > 320 or _EMAIL_PATTERN.fullmatch(normalized) is None:
        raise CrmLeadDomainError("EMAIL_INVALID")

    return normalized


def _score(value: object) -> int:
    """Require an integer CRM score in the inclusive range zero through 100."""

    if isinstance(value, bool) or not isinstance(value, int):
        raise CrmLeadDomainError("SCORE_INVALID")

    if value < 0 or value > 100:
        raise CrmLeadDomainError("SCORE_INVALID")

    return value


def _aware_utc(value: object, code: str) -> datetime:
    """Require one timezone-aware datetime and normalize it to UTC."""

    if not isinstance(value, datetime):
        raise CrmLeadDomainError(code)

    if value.tzinfo is None or value.utcoffset() is None:
        raise CrmLeadDomainError(code)

    return value.astimezone(UTC)


def _optional_aware_utc(value: object, code: str) -> datetime | None:
    """Require optional datetime state to be absent or timezone-aware UTC."""

    if value is None:
        return None

    return _aware_utc(value, code)


def _enum_member[T: StrEnum](
    value: object,
    enum_type: type[T],
    code: str,
) -> T:
    """Require an already-governed enum member without guessing aliases."""

    if not isinstance(value, enum_type):
        raise CrmLeadDomainError(code)

    return value


def _server_owned_lead_id() -> str:
    """Create one opaque server-owned UUID-based CRM Lead identifier."""

    return f"WILSYCRM-LEAD-{uuid4()}"


def _validate_lead_id(value: object) -> str:
    """Require the exact server-owned CRM Lead identifier representation."""

    lead_id = _exact_identifier(value, "LEAD_ID_INVALID")
    prefix = "WILSYCRM-LEAD-"

    if not lead_id.startswith(prefix):
        raise CrmLeadDomainError("LEAD_ID_INVALID")

    try:
        UUID(lead_id.removeprefix(prefix))
    except (ValueError, AttributeError) as error:
        raise CrmLeadDomainError("LEAD_ID_INVALID") from error

    return lead_id


@dataclass(frozen=True, slots=True)
class CrmLead:
    """Immutable canonical CRM Lead business state.

    Mutation semantics:
        Instances never mutate in place. Future lifecycle commands must produce
        validated replacement values through separately certified operations.

    Tenant semantics:
        ``tenant_id`` is exact canonical scope and never inferred from headers,
        browser storage, MASTER aliases or global/root defaults.

    Identity semantics:
        ``lead_id`` is generated only by ``create`` and admitted during direct
        hydration only through the same UUID-shaped server-owned contract.

    Financial semantics:
        ``score``, ``priority`` and commercial context remain CRM classifications
        only; this entity owns no quote, invoice, payment, settlement or
        accounting authority.
    """

    lead_id: str
    tenant_id: str
    full_name: str
    company_name: str
    email: str
    phone: str
    mobile: str
    status: CrmLeadStatus
    owner_id: str
    source_channel: CrmLeadSourceChannel
    priority: CrmLeadPriority
    consent_basis: CrmLeadConsentBasis
    score: int
    industry: str
    due_at: datetime | None
    notes: str
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        """Validate and canonicalize complete immutable CRM Lead state."""

        lead_id = _validate_lead_id(self.lead_id)
        tenant_id = _tenant_id(self.tenant_id)
        full_name = _required_text(self.full_name, "FULL_NAME_INVALID")
        company_name = _required_text(self.company_name, "COMPANY_NAME_INVALID")
        email = _email(self.email)
        phone = _optional_text(self.phone, "PHONE_INVALID")
        mobile = _optional_text(self.mobile, "MOBILE_INVALID")
        owner_id = _exact_identifier(self.owner_id, "OWNER_ID_INVALID")

        status = _enum_member(
            self.status,
            CrmLeadStatus,
            "STATUS_INVALID",
        )
        source_channel = _enum_member(
            self.source_channel,
            CrmLeadSourceChannel,
            "SOURCE_CHANNEL_INVALID",
        )
        priority = _enum_member(
            self.priority,
            CrmLeadPriority,
            "PRIORITY_INVALID",
        )
        consent_basis = _enum_member(
            self.consent_basis,
            CrmLeadConsentBasis,
            "CONSENT_BASIS_INVALID",
        )

        score = _score(self.score)
        industry = _optional_text(self.industry, "INDUSTRY_INVALID")
        notes = _optional_text(self.notes, "NOTES_INVALID")
        due_at = _optional_aware_utc(self.due_at, "DUE_AT_INVALID")
        created_at = _aware_utc(self.created_at, "CREATED_AT_INVALID")
        updated_at = _aware_utc(self.updated_at, "UPDATED_AT_INVALID")

        if updated_at < created_at:
            raise CrmLeadDomainError("UPDATED_AT_INVALID")

        object.__setattr__(self, "lead_id", lead_id)
        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "full_name", full_name)
        object.__setattr__(self, "company_name", company_name)
        object.__setattr__(self, "email", email)
        object.__setattr__(self, "phone", phone)
        object.__setattr__(self, "mobile", mobile)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "owner_id", owner_id)
        object.__setattr__(self, "source_channel", source_channel)
        object.__setattr__(self, "priority", priority)
        object.__setattr__(self, "consent_basis", consent_basis)
        object.__setattr__(self, "score", score)
        object.__setattr__(self, "industry", industry)
        object.__setattr__(self, "due_at", due_at)
        object.__setattr__(self, "notes", notes)
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "updated_at", updated_at)

    @classmethod
    def create(
        cls,
        *,
        tenant_id: str,
        full_name: str,
        company_name: str,
        email: str,
        phone: str,
        mobile: str,
        status: CrmLeadStatus,
        owner_id: str,
        source_channel: CrmLeadSourceChannel,
        priority: CrmLeadPriority,
        consent_basis: CrmLeadConsentBasis,
        score: int,
        industry: str,
        due_at: datetime | None,
        notes: str,
        created_at: datetime,
    ) -> "CrmLead":
        """Create one immutable CRM Lead with server-owned identity.

        The caller supplies already-authorized tenant scope and explicit business
        values. This constructor owns only opaque Lead identity generation. It
        does not persist, authorize, infer tenant scope, create deals or perform
        financial execution.
        """

        canonical_created_at = _aware_utc(
            created_at,
            "CREATED_AT_INVALID",
        )

        return cls(
            lead_id=_server_owned_lead_id(),
            tenant_id=tenant_id,
            full_name=full_name,
            company_name=company_name,
            email=email,
            phone=phone,
            mobile=mobile,
            status=status,
            owner_id=owner_id,
            source_channel=source_channel,
            priority=priority,
            consent_basis=consent_basis,
            score=score,
            industry=industry,
            due_at=due_at,
            notes=notes,
            created_at=canonical_created_at,
            updated_at=canonical_created_at,
        )

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "CrmLead":
        """Hydrate exact persisted CRM Lead truth without creating new authority.

        Hydration preserves the durable server-owned ``lead_id`` and strictly
        revalidates tenant scope, governed enum values, score bounds, timestamps
        and the complete canonical field set. Missing or additional fields,
        malformed scalar encodings, or foreign financial/deal authority fail
        closed rather than being repaired, defaulted, ignored or inferred.

        This method performs no persistence, authorization, entitlement lookup,
        network operation, lifecycle command, AI inference or financial
        execution.
        """

        if not isinstance(data, dict):
            raise CrmLeadDomainError("DURABLE_DOCUMENT_INVALID")

        expected = {
            "lead_id",
            "tenant_id",
            "full_name",
            "company_name",
            "email",
            "phone",
            "mobile",
            "status",
            "owner_id",
            "source_channel",
            "priority",
            "consent_basis",
            "score",
            "industry",
            "due_at",
            "notes",
            "created_at",
            "updated_at",
        }

        if set(data) != expected:
            raise CrmLeadDomainError("DURABLE_DOCUMENT_INVALID")

        try:
            status = CrmLeadStatus(data["status"])
        except (TypeError, ValueError) as error:
            raise CrmLeadDomainError("STATUS_INVALID") from error

        try:
            source_channel = CrmLeadSourceChannel(data["source_channel"])
        except (TypeError, ValueError) as error:
            raise CrmLeadDomainError("SOURCE_CHANNEL_INVALID") from error

        try:
            priority = CrmLeadPriority(data["priority"])
        except (TypeError, ValueError) as error:
            raise CrmLeadDomainError("PRIORITY_INVALID") from error

        try:
            consent_basis = CrmLeadConsentBasis(data["consent_basis"])
        except (TypeError, ValueError) as error:
            raise CrmLeadDomainError("CONSENT_BASIS_INVALID") from error

        def parse_time(value: object, code: str) -> datetime:
            if not isinstance(value, str):
                raise CrmLeadDomainError(code)
            try:
                parsed = datetime.fromisoformat(value)
            except ValueError as error:
                raise CrmLeadDomainError(code) from error
            return _aware_utc(parsed, code)

        created_at = parse_time(data["created_at"], "CREATED_AT_INVALID")
        updated_at = parse_time(data["updated_at"], "UPDATED_AT_INVALID")

        due_raw = data["due_at"]
        if due_raw is None:
            due_at = None
        else:
            due_at = parse_time(due_raw, "DUE_AT_INVALID")

        return cls(
            lead_id=data["lead_id"],  # type: ignore[arg-type]
            tenant_id=data["tenant_id"],  # type: ignore[arg-type]
            full_name=data["full_name"],  # type: ignore[arg-type]
            company_name=data["company_name"],  # type: ignore[arg-type]
            email=data["email"],  # type: ignore[arg-type]
            phone=data["phone"],  # type: ignore[arg-type]
            mobile=data["mobile"],  # type: ignore[arg-type]
            status=status,
            owner_id=data["owner_id"],  # type: ignore[arg-type]
            source_channel=source_channel,
            priority=priority,
            consent_basis=consent_basis,
            score=data["score"],  # type: ignore[arg-type]
            industry=data["industry"],  # type: ignore[arg-type]
            due_at=due_at,
            notes=data["notes"],  # type: ignore[arg-type]
            created_at=created_at,
            updated_at=updated_at,
        )

    def to_dict(self) -> dict[str, object]:
        """Return deterministic persistence-neutral canonical Lead material.

        The result contains only CRM Lead truth owned by this domain. It does
        not synthesize aliases, monetary values, deal conversion, invoices,
        payment state, settlement state or accounting state.
        """

        return {
            "lead_id": self.lead_id,
            "tenant_id": self.tenant_id,
            "full_name": self.full_name,
            "company_name": self.company_name,
            "email": self.email,
            "phone": self.phone,
            "mobile": self.mobile,
            "status": self.status.value,
            "owner_id": self.owner_id,
            "source_channel": self.source_channel.value,
            "priority": self.priority.value,
            "consent_basis": self.consent_basis.value,
            "score": self.score,
            "industry": self.industry,
            "due_at": None if self.due_at is None else self.due_at.isoformat(),
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


__all__ = [
    "CRM_LEAD_DOMAIN_VERSION",
    "CrmLead",
    "CrmLeadConsentBasis",
    "CrmLeadDomainError",
    "CrmLeadPriority",
    "CrmLeadSourceChannel",
    "CrmLeadStatus",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: crm_lead.py
# VERSION: v1.1.0-CRM-LEAD-DOMAIN
# AUTHORITY BOUNDARY: immutable pure CRM Lead business-value truth only
# TENANT POSTURE: exact tenant scope; no MASTER/global/root/default fallback
# FAIL-CLOSED POSTURE: malformed identity, enums, score and timestamps reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
# =============================================================================
