"""WILSY OS immutable legal client-matter Engagement formation evidence.

TITLE: WILSY OS Legal Client Matter Engagement
VERSION: v1.0.0-L9B1-CLIENT-MATTER-ENGAGEMENT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Record immutable evidence that the firm formed one Engagement with
         one exact client-side matter party for one exact CaseMatter, while
         binding (without re-authorizing) client acceptance, acting capacity,
         reviewed instrument, mandate scope, conflict disposition, firm
         decision and authorization evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_engagement.py
COLLABORATION / OWNERSHIP: P1 CaseMatter owns matter identity and lifecycle;
                            L8-8A owns matter-party association; L9A4-P1A
                            owns acting-capacity provenance; L9A owns client
                            acceptance; L9A4-P1B owns instrument identity;
                            future mandate, conflict-disposition and firm-IAM
                            authorities own their referenced evidence. L9B1
                            owns only immutable Engagement formation evidence.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B1-CLIENT-MATTER-ENGAGEMENT establishes exact immutable
           tenant/matter/client-party binding, acting-capacity and client-
           acceptance provenance, instrument/content provenance, opaque future
           mandate and conflict-disposition references, distinct firm-side
           decision and authorization evidence, UTC effectiveness chronology,
           strict hydration and deterministic SHA3-512 integrity. It creates
           no lifecycle, representation, Court or financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers, bounded references and
                             lowercase SHA3-512 fingerprints only; no names,
                             email, address, credentials, tokens, raw mandate,
                             conflict, session or JWT material is retained.
TENANT BOUNDARY: Tenant, CaseMatter, client party and subject identity are
                 derived from exact canonical objects and must agree across
                 every supplied prerequisite. No cross-tenant fallback exists.
AUTHORITY BOUNDARY: Immutable evidence of firm Engagement formation only. The
                    value does not authenticate or authorize any actor, verify
                    a registry, create mandate or conflict clearance, imply
                    representation, create Court authority, or establish
                    current lifecycle status.
FINANCIAL AUTHORITY BOUNDARY: No fee, billing, invoice, payment, settlement,
                              fund-transfer or commercial execution truth;
                              Kennel EOS remains exclusive for execution.
TRANSACTION BOUNDARY: Pure immutable in-memory construction, deterministic
                      serialization and strict hydration only; no database,
                      HTTP, IAM, registry, transaction, retry, notification,
                      lifecycle or network behavior.
FAIL-CLOSED DECLARATION: Malformed identities/references, non-client parties,
                         cross-scope prerequisites, invalid chronology, schema
                         drift or fingerprint divergence reject without
                         coercion, inference or authority expansion.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Any, Final, NoReturn, cast
import unicodedata

from tools.eos.legal_operations.domain.legal_client_acceptance import (
    LegalClientAcceptance,
)
from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    LegalClientActingCapacity,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument import (
    LegalClientMatterAcceptanceInstrument,
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


VERSION: Final[str] = "v1.0.0-L9B1-CLIENT-MATTER-ENGAGEMENT"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-ENGAGEMENT/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class LegalClientMatterEngagementError(ValueError):
    """One stable, non-sensitive failure from Engagement-domain validation."""

    def __init__(self, code: str) -> None:
        """Expose a bounded code without echoing any supplied authority data."""
        self.code = code
        super().__init__(code)


_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "engagement_version",
    "engagement_id",
    "tenant_id",
    "case_matter_id",
    "matter_fingerprint",
    "client_party_id",
    "subject_reference",
    "subject_identity_fingerprint",
    "acting_capacity_id",
    "acting_capacity_fingerprint",
    "client_acceptance_id",
    "client_acceptance_fingerprint",
    "instrument_id",
    "version",
    "instrument_fingerprint",
    "content_fingerprint",
    "mandate_id",
    "mandate_scope",
    "mandate_fingerprint",
    "conflict_disposition_id",
    "conflict_disposition_fingerprint",
    "firm_decision_id",
    "decision_actor_principal_id",
    "firm_decision_fingerprint",
    "authorization_evidence_reference",
    "authorization_evidence_fingerprint",
    "source_evidence_reference",
    "source_evidence_fingerprint",
    "effective_from",
    "idempotency_key",
    "fingerprint",
)
ENGAGEMENT_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable failure while preserving an internal technical cause."""
    error = LegalClientMatterEngagementError(code)
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
        _fail(f"L9B1_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    """Require one explicit tenant and reject pseudo/global scope."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9B1_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 hexadecimal evidence fingerprint."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9B1_{name.upper()}_INVALID")
    return value


def _reference(name: str, value: object, *, limit: int = 512) -> str:
    """Require bounded NFC single-line opaque reference text."""
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
        _fail(f"L9B1_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or len(normalized) > limit:
        _fail(f"L9B1_{name.upper()}_INVALID")
    return normalized


def _timestamp(name: str, value: object) -> datetime:
    """Require aware chronology and normalize it to UTC with microseconds."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9B1_{name.upper()}_INVALID", error)
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _fail(f"L9B1_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    """Convert immutable values to deterministic JSON-safe values."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat(
            timespec="microseconds"
        ).replace("+00:00", "Z")
    return value


@dataclass(frozen=True, slots=True)
class LegalClientMatterEngagement:
    """Immutable evidence that one firm formed one exact Engagement.

    Direct construction validates the complete explicit snapshot. The
    :meth:`from_canonical` factory is the preferred boundary: it derives all
    repeated tenant, matter, party, subject, capacity, acceptance and
    instrument values from exact canonical objects. Opaque mandate,
    conflict-disposition, firm-decision and authorization references are
    validated for shape only; this value does not verify those future
    authorities or grant any runtime permission.
    """

    engagement_id: str
    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    client_party_id: str
    subject_reference: str
    subject_identity_fingerprint: str
    acting_capacity_id: str
    acting_capacity_fingerprint: str
    client_acceptance_id: str
    client_acceptance_fingerprint: str
    instrument_id: str
    version: str
    instrument_fingerprint: str
    content_fingerprint: str
    mandate_id: str
    mandate_scope: str
    mandate_fingerprint: str
    conflict_disposition_id: str
    conflict_disposition_fingerprint: str
    firm_decision_id: str
    decision_actor_principal_id: str
    firm_decision_fingerprint: str
    authorization_evidence_reference: str
    authorization_evidence_fingerprint: str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    effective_from: datetime
    idempotency_key: str
    schema: str = SCHEMA
    engagement_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate every semantic field and compute/verify integrity."""
        if self.schema != SCHEMA or self.engagement_version != VERSION:
            _fail("L9B1_IDENTITY_INVALID")
        normalized: dict[str, object] = {
            "engagement_id": _identity("engagement_id", self.engagement_id),
            "tenant_id": _tenant(self.tenant_id),
            "case_matter_id": _identity("case_matter_id", self.case_matter_id),
            "matter_fingerprint": _fingerprint(
                "matter_fingerprint", self.matter_fingerprint
            ),
            "client_party_id": _identity("client_party_id", self.client_party_id),
            "subject_reference": _reference(
                "subject_reference", self.subject_reference, limit=224
            ),
            "subject_identity_fingerprint": _fingerprint(
                "subject_identity_fingerprint", self.subject_identity_fingerprint
            ),
            "acting_capacity_id": _identity(
                "acting_capacity_id", self.acting_capacity_id
            ),
            "acting_capacity_fingerprint": _fingerprint(
                "acting_capacity_fingerprint", self.acting_capacity_fingerprint
            ),
            "client_acceptance_id": _identity(
                "client_acceptance_id", self.client_acceptance_id
            ),
            "client_acceptance_fingerprint": _fingerprint(
                "client_acceptance_fingerprint", self.client_acceptance_fingerprint
            ),
            "instrument_id": _identity("instrument_id", self.instrument_id),
            "version": _identity("version", self.version),
            "instrument_fingerprint": _fingerprint(
                "instrument_fingerprint", self.instrument_fingerprint
            ),
            "content_fingerprint": _fingerprint(
                "content_fingerprint", self.content_fingerprint
            ),
            "mandate_id": _identity("mandate_id", self.mandate_id),
            "mandate_scope": _reference("mandate_scope", self.mandate_scope),
            "mandate_fingerprint": _fingerprint(
                "mandate_fingerprint", self.mandate_fingerprint
            ),
            "conflict_disposition_id": _identity(
                "conflict_disposition_id", self.conflict_disposition_id
            ),
            "conflict_disposition_fingerprint": _fingerprint(
                "conflict_disposition_fingerprint",
                self.conflict_disposition_fingerprint,
            ),
            "firm_decision_id": _identity(
                "firm_decision_id", self.firm_decision_id
            ),
            "decision_actor_principal_id": _identity(
                "decision_actor_principal_id", self.decision_actor_principal_id
            ),
            "firm_decision_fingerprint": _fingerprint(
                "firm_decision_fingerprint", self.firm_decision_fingerprint
            ),
            "authorization_evidence_reference": _reference(
                "authorization_evidence_reference",
                self.authorization_evidence_reference,
            ),
            "authorization_evidence_fingerprint": _fingerprint(
                "authorization_evidence_fingerprint",
                self.authorization_evidence_fingerprint,
            ),
            "source_evidence_reference": _reference(
                "source_evidence_reference", self.source_evidence_reference
            ),
            "source_evidence_fingerprint": _fingerprint(
                "source_evidence_fingerprint", self.source_evidence_fingerprint
            ),
            "effective_from": _timestamp("effective_from", self.effective_from),
            "idempotency_key": _reference(
                "idempotency_key", self.idempotency_key, limit=240
            ),
        }
        for field, value in normalized.items():
            object.__setattr__(self, field, value)
        payload = {
            field: _json_value(getattr(self, field)) for field in _FIELDS[:-1]
        }
        digest = hashlib.sha3_512(
            json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=False,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        if self.fingerprint != "":
            if not isinstance(self.fingerprint, str) or not hmac.compare_digest(
                self.fingerprint, digest
            ):
                _fail("L9B1_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize the complete immutable evidence without raw sensitive data."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalClientMatterEngagement":
        """Hydrate only the exact schema and verify deterministic integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9B1_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(
            stored, result.fingerprint
        ):
            _fail("L9B1_FINGERPRINT_MISMATCH")
        return result

    @classmethod
    def from_canonical(
        cls,
        *,
        engagement_id: str,
        case_matter: CaseMatter,
        party: LegalMatterParty,
        acting_capacity: LegalClientActingCapacity,
        client_acceptance: LegalClientAcceptance,
        instrument: LegalClientMatterAcceptanceInstrument,
        mandate_id: str,
        mandate_scope: str,
        mandate_fingerprint: str,
        conflict_disposition_id: str,
        conflict_disposition_fingerprint: str,
        firm_decision_id: str,
        decision_actor_principal_id: str,
        firm_decision_fingerprint: str,
        authorization_evidence_reference: str,
        authorization_evidence_fingerprint: str,
        source_evidence_reference: str,
        source_evidence_fingerprint: str,
        effective_from: datetime,
        idempotency_key: str,
    ) -> "LegalClientMatterEngagement":
        """Form evidence from exact canonical matter/client prerequisites.

        This factory derives repeated bindings and rejects closed matters,
        non-client parties, cross-tenant/matter inputs, mismatched party or
        subject evidence, acceptance actors without the supplied capacity,
        instrument drift and effectiveness before any prerequisite chronology.
        Mandate and conflict-disposition references remain opaque because their
        authoritative domains are deliberately future, separate gates.
        """
        canonical = (
            ("case_matter", CaseMatter, case_matter),
            ("party", LegalMatterParty, party),
            ("acting_capacity", LegalClientActingCapacity, acting_capacity),
            ("client_acceptance", LegalClientAcceptance, client_acceptance),
            (
                "instrument",
                LegalClientMatterAcceptanceInstrument,
                instrument,
            ),
        )
        for name, expected_type, value in canonical:
            if type(value) is not expected_type:
                _fail(f"L9B1_{name.upper()}_REQUIRED")
            try:
                value.__post_init__()  # type: ignore[attr-defined]
            except Exception as error:
                _fail(f"L9B1_{name.upper()}_INVALID", error)
        if case_matter.state is not CaseMatterState.OPEN:
            _fail("L9B1_OPEN_CASE_MATTER_REQUIRED")
        if party.party_side is not LegalMatterPartySide.CLIENT_SIDE:
            _fail("L9B1_CLIENT_PARTY_REQUIRED")
        if party.matter_role is not LegalMatterPartyRole.CLIENT:
            _fail("L9B1_CLIENT_PARTY_ROLE_REQUIRED")
        if (
            party.tenant_id != case_matter.tenant_id
            or party.case_matter_id != case_matter.case_matter_id
            or party.matter_fingerprint != case_matter.fingerprint
        ):
            _fail("L9B1_PARTY_MATTER_MISMATCH")
        if (
            acting_capacity.tenant_id != case_matter.tenant_id
            or acting_capacity.case_matter_id != case_matter.case_matter_id
            or acting_capacity.matter_fingerprint != case_matter.fingerprint
            or acting_capacity.party_id != party.party_id
            or acting_capacity.subject_reference != party.subject_reference
            or acting_capacity.subject_identity_fingerprint
            != party.subject_identity_fingerprint
        ):
            _fail("L9B1_CAPACITY_CORRELATION_MISMATCH")
        if acting_capacity.principal_id != client_acceptance.actor_principal_id:
            _fail("L9B1_ACCEPTANCE_ACTOR_CAPACITY_MISMATCH")
        if (
            client_acceptance.tenant_id != case_matter.tenant_id
            or client_acceptance.case_matter_id != case_matter.case_matter_id
            or client_acceptance.matter_fingerprint != case_matter.fingerprint
            or client_acceptance.party_id != party.party_id
            or client_acceptance.subject_reference != party.subject_reference
            or client_acceptance.subject_identity_fingerprint
            != party.subject_identity_fingerprint
        ):
            _fail("L9B1_CLIENT_ACCEPTANCE_CORRELATION_MISMATCH")
        if (
            instrument.tenant_id != case_matter.tenant_id
            or instrument.case_matter_id != case_matter.case_matter_id
            or instrument.matter_fingerprint != case_matter.fingerprint
        ):
            _fail("L9B1_INSTRUMENT_CORRELATION_MISMATCH")
        effective = _timestamp("effective_from", effective_from)
        if effective < max(
            case_matter.opened_at,
            party.registered_at,
            acting_capacity.effective_from,
            client_acceptance.accepted_at,
            instrument.effective_from,
        ):
            _fail("L9B1_EFFECTIVE_FROM_INVALID")
        if (
            acting_capacity.effective_until is not None
            and effective >= acting_capacity.effective_until
        ):
            _fail("L9B1_CAPACITY_NOT_VALID_AT_EFFECTIVE")
        return cls(
            engagement_id=engagement_id,
            tenant_id=case_matter.tenant_id,
            case_matter_id=case_matter.case_matter_id,
            matter_fingerprint=case_matter.fingerprint,
            client_party_id=party.party_id,
            subject_reference=party.subject_reference,
            subject_identity_fingerprint=party.subject_identity_fingerprint,
            acting_capacity_id=acting_capacity.capacity_id,
            acting_capacity_fingerprint=acting_capacity.fingerprint,
            client_acceptance_id=client_acceptance.acceptance_id,
            client_acceptance_fingerprint=client_acceptance.fingerprint,
            instrument_id=instrument.instrument_id,
            version=instrument.version,
            instrument_fingerprint=instrument.fingerprint,
            content_fingerprint=instrument.content_fingerprint,
            mandate_id=mandate_id,
            mandate_scope=mandate_scope,
            mandate_fingerprint=mandate_fingerprint,
            conflict_disposition_id=conflict_disposition_id,
            conflict_disposition_fingerprint=conflict_disposition_fingerprint,
            firm_decision_id=firm_decision_id,
            decision_actor_principal_id=decision_actor_principal_id,
            firm_decision_fingerprint=firm_decision_fingerprint,
            authorization_evidence_reference=authorization_evidence_reference,
            authorization_evidence_fingerprint=authorization_evidence_fingerprint,
            source_evidence_reference=source_evidence_reference,
            source_evidence_fingerprint=source_evidence_fingerprint,
            effective_from=effective,
            idempotency_key=idempotency_key,
        )


__all__ = [
    "ENGAGEMENT_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientMatterEngagement",
    "LegalClientMatterEngagementError",
]


# ARTIFACT: legal_client_matter_engagement.py
# VERSION: v1.0.0-L9B1-CLIENT-MATTER-ENGAGEMENT
# AUTHORITY BOUNDARY: immutable Engagement formation evidence only
# TENANT POSTURE: exact tenant/matter/client-party/capacity/acceptance binding
# FAIL-CLOSED POSTURE: malformed, cross-scope, naive, drifted or tampered evidence rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
