"""WILSY OS immutable client-acceptance evidence domain.

TITLE: Legal Client Acceptance
VERSION: v1.0.0-L9A-CLIENT-ACCEPTANCE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Bind one bounded client-acceptance decision to an exact tenant,
         CaseMatter, opaque client/party subject and explicit acceptance scope
         without creating engagement, representation, Court or financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_acceptance.py
COLLABORATION / OWNERSHIP: CaseMatter owns matter identity; upstream identity
                            authorities own subject identity; L9A owns only
                            immutable acceptance-evidence semantics. A later
                            registry and IAM orchestrator must independently
                            prove actor authority and durable admission.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A-CLIENT-ACCEPTANCE establishes a pure immutable,
           tenant-and-matter-scoped client-acceptance evidence contract with
           opaque subject identity, bounded scope, actor and source-evidence
           provenance, UTC chronology and deterministic SHA3-512 integrity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Stores opaque subject references and fingerprints
                             only; no client name, email, address, credentials,
                             tokens, legal narrative or raw identity numbers.
TENANT BOUNDARY: Tenant and CaseMatter identity may be derived only from one
                 exact CaseMatter; direct hydration requires explicit tenant,
                 matter and source-matter fingerprint equality.
AUTHORITY BOUNDARY: Client-acceptance evidence only. Existence of this value
                    does not prove engagement, retainer, mandate,
                    representation, conflict clearance, waiver, portal access,
                    matter activation or Court authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                              execution and settlement authority.
TRANSACTION BOUNDARY: Pure immutable in-memory construction and deterministic
                      serialization; no database, HTTP, IAM, transaction,
                      retry, notification, Court or financial lifecycle.
FAIL-CLOSED DECLARATION: Malformed identity, scope, evidence, chronology,
                         schema or fingerprint drift rejects without coercion.
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

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)


VERSION: Final[str] = "v1.0.0-L9A-CLIENT-ACCEPTANCE"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-ACCEPTANCE/V1"
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


class LegalClientAcceptanceError(ValueError):
    """One fail-closed L9A client-acceptance domain failure with stable code."""

    def __init__(self, code: str) -> None:
        """Expose only a stable validation code, never authority-bearing input."""
        self.code = code
        super().__init__(code)


_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "acceptance_version",
    "tenant_id",
    "case_matter_id",
    "matter_fingerprint",
    "acceptance_id",
    "party_id",
    "subject_reference",
    "subject_identity_fingerprint",
    "acceptance_scope",
    "actor_principal_id",
    "accepted_at",
    "source_evidence_reference",
    "source_evidence_fingerprint",
    "fingerprint",
)
ACCEPTANCE_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable L9A error while retaining an internal technical cause."""
    error = LegalClientAcceptanceError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    """Require one canonical opaque identifier without trimming or coercion."""
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _fail(f"L9A_{name.upper()}_INVALID")
    return value


def _tenant(value: object) -> str:
    """Require one explicit non-global tenant identity."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9A_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 hexadecimal evidence fingerprint."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9A_{name.upper()}_INVALID")
    return value


def _reference(name: str, value: object, *, limit: int = 512) -> str:
    """Require bounded non-empty NFC-normalized evidence/reference text."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(ord(character) < 32 for character in value)
    ):
        _fail(f"L9A_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or len(normalized) > limit:
        _fail(f"L9A_{name.upper()}_INVALID")
    return normalized


def _subject_reference(value: object) -> str:
    """Require the same opaque subject-reference vocabulary as matter parties."""
    reference = _reference("subject_reference", value, limit=224)
    if _SUBJECT_REFERENCE.fullmatch(reference) is None:
        _fail("L9A_SUBJECT_REFERENCE_INVALID")
    return reference


def _scope(value: object) -> str:
    """Require one bounded opaque scope reference without inventing taxonomy."""
    scope = _identity("acceptance_scope", value)
    reserved_prefix = scope.casefold().split(":", 1)[0]
    if reserved_prefix in {
        "engagement",
        "retainer",
        "mandate",
        "representation",
        "court",
        "waiver",
        "ethical_wall",
    }:
        _fail("L9A_ACCEPTANCE_SCOPE_INVALID")
    return scope


def _when(value: object) -> datetime:
    """Normalize aware datetime or ISO input to UTC; reject naive chronology."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail("L9A_ACCEPTED_AT_INVALID", error)
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _fail("L9A_ACCEPTED_AT_INVALID")
    return parsed.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    """Convert immutable values to deterministic JSON-safe values."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return value


@dataclass(frozen=True, slots=True)
class LegalClientAcceptance:
    """Immutable matter-scoped client-acceptance evidence.

    The object records only that an actor's supplied evidence binds a client or
    party subject to one bounded scope for one exact matter. It does not
    authenticate the actor, establish a client relationship, create engagement
    or representation, mutate a matter, authorize Court action, or create any
    financial truth. A later IAM-aware orchestrator owns those decisions and
    caller-owned persistence transactions.
    """

    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    acceptance_id: str
    party_id: str
    subject_reference: str
    subject_identity_fingerprint: str
    acceptance_scope: str
    actor_principal_id: str
    accepted_at: datetime
    source_evidence_reference: str
    source_evidence_fingerprint: str
    schema: str = SCHEMA
    acceptance_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate and canonicalize the complete immutable evidence record."""
        tenant = _tenant(self.tenant_id)
        matter_id = _identity("case_matter_id", self.case_matter_id)
        matter_fingerprint = _fingerprint(
            "matter_fingerprint", self.matter_fingerprint
        )
        acceptance_id = _identity("acceptance_id", self.acceptance_id)
        party_id = _identity("party_id", self.party_id)
        subject = _subject_reference(self.subject_reference)
        subject_fingerprint = _fingerprint(
            "subject_identity_fingerprint", self.subject_identity_fingerprint
        )
        scope = _scope(self.acceptance_scope)
        actor = _identity("actor_principal_id", self.actor_principal_id)
        accepted_at = _when(self.accepted_at)
        source_reference = _reference(
            "source_evidence_reference", self.source_evidence_reference
        )
        source_fingerprint = _fingerprint(
            "source_evidence_fingerprint", self.source_evidence_fingerprint
        )
        if self.schema != SCHEMA or self.acceptance_version != VERSION:
            _fail("L9A_IDENTITY_INVALID")

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "case_matter_id", matter_id)
        object.__setattr__(self, "matter_fingerprint", matter_fingerprint)
        object.__setattr__(self, "acceptance_id", acceptance_id)
        object.__setattr__(self, "party_id", party_id)
        object.__setattr__(self, "subject_reference", subject)
        object.__setattr__(self, "subject_identity_fingerprint", subject_fingerprint)
        object.__setattr__(self, "acceptance_scope", scope)
        object.__setattr__(self, "actor_principal_id", actor)
        object.__setattr__(self, "accepted_at", accepted_at)
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
            _fail("L9A_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact immutable evidence without raw client PII."""
        return {
            field: _json_value(getattr(self, field))
            for field in _FIELDS
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalClientAcceptance":
        """Hydrate only the exact schema and verify deterministic integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9A_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(Any, values))
        if (
            not isinstance(stored, str)
            or not hmac.compare_digest(stored, result.fingerprint)
        ):
            _fail("L9A_FINGERPRINT_MISMATCH")
        return result


def record_legal_client_acceptance(
    *,
    case_matter: CaseMatter,
    acceptance_id: str,
    party_id: str,
    subject_reference: str,
    subject_identity_fingerprint: str,
    acceptance_scope: str,
    actor_principal_id: str,
    accepted_at: datetime,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
) -> LegalClientAcceptance:
    """Bind acceptance evidence to one exact OPEN CaseMatter snapshot.

    This pure factory derives tenant, matter identity and matter fingerprint
    from the canonical CaseMatter. It does not prove the actor's IAM authority,
    that the subject is a client, or that the evidence is legally sufficient;
    those checks belong to a later orchestrator before persistence.
    """
    if type(case_matter) is not CaseMatter:
        _fail("L9A_CASE_MATTER_REQUIRED")
    if case_matter.state is not CaseMatterState.OPEN:
        _fail("L9A_OPEN_CASE_MATTER_REQUIRED")
    return LegalClientAcceptance(
        tenant_id=case_matter.tenant_id,
        case_matter_id=case_matter.case_matter_id,
        matter_fingerprint=case_matter.fingerprint,
        acceptance_id=acceptance_id,
        party_id=party_id,
        subject_reference=subject_reference,
        subject_identity_fingerprint=subject_identity_fingerprint,
        acceptance_scope=acceptance_scope,
        actor_principal_id=actor_principal_id,
        accepted_at=accepted_at,
        source_evidence_reference=source_evidence_reference,
        source_evidence_fingerprint=source_evidence_fingerprint,
    )


__all__ = [
    "ACCEPTANCE_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientAcceptance",
    "LegalClientAcceptanceError",
    "record_legal_client_acceptance",
]


# ARTIFACT: legal_client_acceptance.py
# VERSION: v1.0.0-L9A-CLIENT-ACCEPTANCE
# AUTHORITY BOUNDARY: immutable matter-scoped client-acceptance evidence only
# TENANT POSTURE: tenant/matter bind to exact OPEN CaseMatter evidence
# FAIL-CLOSED POSTURE: malformed, out-of-scope, naive, or drifted evidence rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
