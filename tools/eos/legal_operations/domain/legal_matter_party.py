"""WILSY OS immutable legal matter-party association authority.

TITLE: Legal Matter Party
VERSION: v1.0.0-L8-8A-LEGAL-MATTER-PARTY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Bind one opaque legal subject identity to one exact OPEN canonical
         CaseMatter as immutable party-position evidence without importing
         legacy Node party/conflict authority or storing raw identity numbers.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_matter_party.py
COLLABORATION / OWNERSHIP: P1 CaseMatter owns matter lifecycle truth; upstream
                            CRM/identity authorities own subject identity truth;
                            L8-8A owns only the immutable matter-to-subject party
                            association, position and descriptive presentation.
                            Later conflict authority must consume these facts and
                            must not infer conflict truth from browser/Node state.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-L8-8A-LEGAL-MATTER-PARTY establishes exact tenant/matter
           binding, immutable party identity, closed party-kind/side/role
           vocabularies, opaque subject references, SHA3-512 subject identity
           evidence, bounded descriptive name, deterministic SHA3-512 integrity
           and OPEN-matter admission. No conflict, client-acceptance, FICA,
           representation, billing or legal-outcome authority is created.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Stores no ID/passport/tax/account number, address,
                             phone, email, biometric or raw KYC material. Subject
                             identity is an opaque authority reference plus exact
                             lowercase SHA3-512 evidence fingerprint.
TENANT BOUNDARY: Tenant is derived from the supplied canonical CaseMatter and
                 every party value is bound to that exact tenant/matter.
AUTHORITY BOUNDARY: Matter-party association/position evidence only. CLIENT_SIDE
                    or ADVERSE_SIDE is not itself a conflict determination,
                    representation mandate, admission decision or legal finding.
FINANCIAL AUTHORITY BOUNDARY: No fee, trust, retainer, invoice, payment,
                               execution or settlement truth. Kennel EOS remains
                               exclusive for financial execution.
FAIL-CLOSED DECLARATION: Closed/malformed/foreign matter evidence, pseudo-tenant
                         scope, invalid party identity, raw-identity-shaped
                         subject references, malformed fingerprints, timestamps
                         and schema/fingerprint drift reject.
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
from typing import Any, Final, cast
import unicodedata

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)


VERSION: Final[str] = "v1.0.0-L8-8A-LEGAL-MATTER-PARTY"
SCHEMA: Final[str] = "WILSY-LEGAL-MATTER-PARTY/V1"

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_SUBJECT_REFERENCE: Final[re.Pattern[str]] = re.compile(
    r"^(crm|contact|organization|entity|client|subject):"
    r"[A-Za-z0-9][A-Za-z0-9._:-]{0,191}$"
)
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class LegalMatterPartyError(ValueError):
    """One fail-closed L8-8A party-domain failure with stable code."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalMatterPartyKind(StrEnum):
    """Closed legal-subject classifications without raw identity semantics."""

    INDIVIDUAL = "INDIVIDUAL"
    ORGANIZATION = "ORGANIZATION"
    GOVERNMENT_BODY = "GOVERNMENT_BODY"
    TRUST = "TRUST"
    ESTATE = "ESTATE"
    OTHER = "OTHER"


class LegalMatterPartySide(StrEnum):
    """Matter-relative position; this is not conflict-of-interest truth."""

    CLIENT_SIDE = "CLIENT_SIDE"
    ADVERSE_SIDE = "ADVERSE_SIDE"
    NEUTRAL = "NEUTRAL"
    THIRD_PARTY = "THIRD_PARTY"


class LegalMatterPartyRole(StrEnum):
    """Closed descriptive matter roles with no inferred legal conclusion."""

    CLIENT = "CLIENT"
    PLAINTIFF = "PLAINTIFF"
    DEFENDANT = "DEFENDANT"
    APPLICANT = "APPLICANT"
    RESPONDENT = "RESPONDENT"
    APPELLANT = "APPELLANT"
    PETITIONER = "PETITIONER"
    INTERESTED_PARTY = "INTERESTED_PARTY"
    WITNESS = "WITNESS"
    OTHER = "OTHER"


_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "party_version",
    "tenant_id",
    "case_matter_id",
    "matter_fingerprint",
    "party_id",
    "party_kind",
    "party_side",
    "matter_role",
    "subject_reference",
    "subject_identity_fingerprint",
    "display_name",
    "registered_at",
    "source_evidence_reference",
    "source_evidence_fingerprint",
    "fingerprint",
)
PARTY_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


def _identity(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        raise LegalMatterPartyError(f"L8_8A_{name.upper()}_INVALID")
    return value


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        raise LegalMatterPartyError("L8_8A_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        raise LegalMatterPartyError(f"L8_8A_{name.upper()}_INVALID")
    return value


def _text(name: str, value: object, *, limit: int) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise LegalMatterPartyError(f"L8_8A_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if (
        not normalized
        or len(normalized) > limit
        or any(ord(character) < 32 for character in normalized)
    ):
        raise LegalMatterPartyError(f"L8_8A_{name.upper()}_INVALID")
    return normalized


def _subject_reference(value: object) -> str:
    reference = _text("subject_reference", value, limit=224)
    if _SUBJECT_REFERENCE.fullmatch(reference) is None:
        raise LegalMatterPartyError("L8_8A_SUBJECT_REFERENCE_INVALID")
    return reference


def _when(value: object) -> datetime:
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            raise LegalMatterPartyError("L8_8A_REGISTERED_AT_INVALID") from error
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        raise LegalMatterPartyError("L8_8A_REGISTERED_AT_INVALID")
    return parsed.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, StrEnum):
        return value.value
    return value


@dataclass(frozen=True, slots=True)
class LegalMatterParty:
    """Immutable subject-to-matter party association evidence."""

    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    party_id: str
    party_kind: LegalMatterPartyKind | str
    party_side: LegalMatterPartySide | str
    matter_role: LegalMatterPartyRole | str
    subject_reference: str
    subject_identity_fingerprint: str
    display_name: str
    registered_at: datetime
    source_evidence_reference: str
    source_evidence_fingerprint: str
    schema: str = SCHEMA
    party_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        tenant = _tenant(self.tenant_id)
        matter_id = _identity("case_matter_id", self.case_matter_id)
        matter_fingerprint = _fingerprint(
            "matter_fingerprint",
            self.matter_fingerprint,
        )
        party_id = _identity("party_id", self.party_id)
        try:
            party_kind = LegalMatterPartyKind(self.party_kind)
            party_side = LegalMatterPartySide(self.party_side)
            matter_role = LegalMatterPartyRole(self.matter_role)
        except (TypeError, ValueError) as error:
            raise LegalMatterPartyError("L8_8A_PARTY_CLASSIFICATION_INVALID") from error
        subject_reference = _subject_reference(self.subject_reference)
        subject_identity_fingerprint = _fingerprint(
            "subject_identity_fingerprint",
            self.subject_identity_fingerprint,
        )
        display_name = _text("display_name", self.display_name, limit=200)
        registered_at = _when(self.registered_at)
        source_reference = _text(
            "source_evidence_reference",
            self.source_evidence_reference,
            limit=512,
        )
        source_fingerprint = _fingerprint(
            "source_evidence_fingerprint",
            self.source_evidence_fingerprint,
        )
        if self.schema != SCHEMA or self.party_version != VERSION:
            raise LegalMatterPartyError("L8_8A_IDENTITY_INVALID")

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "case_matter_id", matter_id)
        object.__setattr__(self, "matter_fingerprint", matter_fingerprint)
        object.__setattr__(self, "party_id", party_id)
        object.__setattr__(self, "party_kind", party_kind)
        object.__setattr__(self, "party_side", party_side)
        object.__setattr__(self, "matter_role", matter_role)
        object.__setattr__(self, "subject_reference", subject_reference)
        object.__setattr__(
            self,
            "subject_identity_fingerprint",
            subject_identity_fingerprint,
        )
        object.__setattr__(self, "display_name", display_name)
        object.__setattr__(self, "registered_at", registered_at)
        object.__setattr__(self, "source_evidence_reference", source_reference)
        object.__setattr__(self, "source_evidence_fingerprint", source_fingerprint)

        payload = {
            field: _json_value(getattr(self, field))
            for field in _FIELDS[:-1]
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
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            raise LegalMatterPartyError("L8_8A_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize exact immutable party evidence with no raw PII identifiers."""
        return {
            field: _json_value(getattr(self, field))
            for field in _FIELDS
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LegalMatterParty":
        """Hydrate only the exact schema and verify deterministic integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            raise LegalMatterPartyError("L8_8A_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        item = cls(**cast(Any, values))
        if (
            not isinstance(stored, str)
            or not hmac.compare_digest(stored, item.fingerprint)
        ):
            raise LegalMatterPartyError("L8_8A_FINGERPRINT_MISMATCH")
        return item


def register_legal_matter_party(
    *,
    matter: CaseMatter,
    party_id: str,
    party_kind: LegalMatterPartyKind | str,
    party_side: LegalMatterPartySide | str,
    matter_role: LegalMatterPartyRole | str,
    subject_reference: str,
    subject_identity_fingerprint: str,
    display_name: str,
    registered_at: datetime,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
) -> LegalMatterParty:
    """Bind one subject to one exact OPEN canonical matter snapshot."""
    if type(matter) is not CaseMatter:
        raise LegalMatterPartyError("L8_8A_CASE_MATTER_REQUIRED")
    if matter.state is not CaseMatterState.OPEN:
        raise LegalMatterPartyError("L8_8A_OPEN_CASE_MATTER_REQUIRED")
    return LegalMatterParty(
        tenant_id=matter.tenant_id,
        case_matter_id=matter.case_matter_id,
        matter_fingerprint=matter.fingerprint,
        party_id=party_id,
        party_kind=party_kind,
        party_side=party_side,
        matter_role=matter_role,
        subject_reference=subject_reference,
        subject_identity_fingerprint=subject_identity_fingerprint,
        display_name=display_name,
        registered_at=registered_at,
        source_evidence_reference=source_evidence_reference,
        source_evidence_fingerprint=source_evidence_fingerprint,
    )


__all__ = [
    "PARTY_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalMatterParty",
    "LegalMatterPartyError",
    "LegalMatterPartyKind",
    "LegalMatterPartyRole",
    "LegalMatterPartySide",
    "register_legal_matter_party",
]


# ARTIFACT: legal_matter_party.py
# VERSION: v1.0.0-L8-8A-LEGAL-MATTER-PARTY
# AUTHORITY BOUNDARY: immutable matter-party association/position evidence only
# TENANT POSTURE: tenant/matter derived from exact OPEN P1 CaseMatter
# FAIL-CLOSED POSTURE: malformed/closed/foreign/drifted identity evidence rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
