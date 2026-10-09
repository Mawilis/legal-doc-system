"""Immutable currentness evidence for one historical client-matter mandate.

TITLE: WILSY OS Legal Client Matter Mandate Currentness Projection
VERSION: v1.0.0-L9B12-P1-CLIENT-MATTER-MANDATE-CURRENTNESS
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Determine, at one explicit evaluation instant, whether one immutable
         mandate formation remains usable by proving its exact grant and
         decisive acknowledgment lineage. This artifact derives no history,
         performs no persistence, and creates no downstream authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_mandate_currentness.py
COLLABORATION / OWNERSHIP: LegalClientMatterMandate remains immutable history;
                            grant and acknowledgment currentness projections
                            remain upstream authorities; a future composer owns
                            repository reads and caller transactions. This
                            module owns only the pure result contract.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B12-P1-CLIENT-MATTER-MANDATE-CURRENTNESS establishes the
           bounded currentness states, exact tenant/matter/client/subject and
           grant/acknowledgment identity binding, explicit aware-UTC evaluation,
           deterministic SHA3-512 integrity, strict hydration and immutable
           negative authority. It adds no composer, registry, lifecycle,
           Engagement, API, UI, Court or financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers and lowercase SHA3-512
                             fingerprints only; no PII, credentials, tokens,
                             raw evidence bodies, clock reads or mutable state.
TENANT BOUNDARY: One explicit non-global tenant is required. Mandate, grant
                 currentness and acknowledgment currentness must agree on the
                 exact tenant, matter, client party and subject identity.
AUTHORITY BOUNDARY: Pure derived currentness evidence only. No registry,
                    Mongo, CaseMatter, acting-capacity, conflict,
                    ClientAcceptance, IAM, Engagement, Representation, Court,
                    delivery or network authority is available here.
FINANCIAL AUTHORITY BOUNDARY: No financial execution, payment, settlement,
                              release or commercial authority; Kennel EOS remains
                              the exclusive financial execution authority.
TRANSACTION BOUNDARY: Immutable in-memory construction, serialization and
                      strict hydration only. A future composer owns reads,
                      transaction lifecycle, retries and persistence decisions.
FAIL-CLOSED DECLARATION: Corrupt, ambiguous, absent, temporally inapplicable,
                         divergent or incompletely bound evidence never becomes
                         CURRENT and is never repaired or inferred.
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

from tools.eos.legal_operations.domain.legal_client_matter_mandate import (
    LegalClientMatterMandate,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment_currentness import (
    LegalClientMatterMandateAcknowledgmentCurrentness,
    LegalClientMatterMandateAcknowledgmentCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_currentness import (
    LegalClientMatterMandateGrantCurrentness,
    LegalClientMatterMandateGrantCurrentnessState,
)


VERSION: Final[str] = "v1.0.0-L9B12-P1-CLIENT-MATTER-MANDATE-CURRENTNESS"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-MANDATE-CURRENTNESS/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)
_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "currentness_version",
    "currentness_id",
    "tenant_id",
    "mandate_id",
    "mandate_fingerprint",
    "case_matter_id",
    "matter_fingerprint",
    "client_party_id",
    "subject_identity_fingerprint",
    "client_grant_id",
    "client_grant_fingerprint",
    "firm_acknowledgment_id",
    "firm_acknowledgment_fingerprint",
    "effective_from",
    "effective_until",
    "evaluation_time",
    "grant_currentness_state",
    "grant_currentness_fingerprint",
    "grant_currentness_tenant_id",
    "grant_currentness_client_grant_id",
    "grant_currentness_client_grant_fingerprint",
    "grant_currentness_case_matter_id",
    "grant_currentness_matter_fingerprint",
    "grant_currentness_client_party_id",
    "grant_currentness_subject_identity_fingerprint",
    "acknowledgment_currentness_state",
    "acknowledgment_currentness_fingerprint",
    "acknowledgment_currentness_tenant_id",
    "acknowledgment_currentness_client_grant_id",
    "acknowledgment_currentness_client_grant_fingerprint",
    "acknowledgment_currentness_case_matter_id",
    "acknowledgment_currentness_matter_fingerprint",
    "acknowledgment_currentness_client_party_id",
    "acknowledgment_currentness_subject_identity_fingerprint",
    "decisive_acknowledgment_ids",
    "decisive_acknowledgment_fingerprints",
    "corruption_evidence_fingerprints",
    "state",
    "reason",
    "fingerprint",
)
CURRENTNESS_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientMatterMandateCurrentnessState(StrEnum):
    """Closed, fail-closed outcomes for one mandate at one instant."""

    FORMATION_ABSENT = "FORMATION_ABSENT"
    NOT_YET_EFFECTIVE = "NOT_YET_EFFECTIVE"
    EXPIRED = "EXPIRED"
    GRANT_NOT_CURRENT = "GRANT_NOT_CURRENT"
    ACKNOWLEDGMENT_NOT_CURRENT = "ACKNOWLEDGMENT_NOT_CURRENT"
    LINEAGE_MISMATCH = "LINEAGE_MISMATCH"
    AMBIGUOUS = "AMBIGUOUS"
    CORRUPT_BLOCKED = "CORRUPT_BLOCKED"
    CURRENT = "CURRENT"


class LegalClientMatterMandateCurrentnessReason(StrEnum):
    """Bounded machine-readable explanation for each projection state."""

    FORMATION_ABSENT = "FORMATION_ABSENT"
    NOT_YET_EFFECTIVE = "NOT_YET_EFFECTIVE"
    EXPIRED = "EXPIRED"
    GRANT_NOT_CURRENT = "GRANT_NOT_CURRENT"
    ACKNOWLEDGMENT_NOT_CURRENT = "ACKNOWLEDGMENT_NOT_CURRENT"
    LINEAGE_MISMATCH = "LINEAGE_MISMATCH"
    AMBIGUOUS = "AMBIGUOUS"
    CORRUPT_EVIDENCE = "CORRUPT_EVIDENCE"
    CURRENT = "CURRENT"


class LegalClientMatterMandateCurrentnessError(ValueError):
    """Stable, non-sensitive failure from projection validation."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one bounded code without echoing authority-bearing input."""
    error = LegalClientMatterMandateCurrentnessError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    """Require one bounded opaque identity without trimming or coercion."""
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"L9B12_P1_{name.upper()}_INVALID")
    return value


def _tenant(value: object) -> str:
    """Require one explicit non-global tenant scope."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9B12_P1_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 hexadecimal fingerprint."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9B12_P1_{name.upper()}_INVALID")
    return value


def _optional_identity(name: str, value: object) -> str | None:
    """Validate optional identity evidence without inventing a value."""
    if value is None:
        return None
    return _identity(name, value)


def _optional_fingerprint(name: str, value: object) -> str | None:
    """Validate optional fingerprint evidence without inventing a value."""
    if value is None:
        return None
    return _fingerprint(name, value)


def _timestamp(name: str, value: object) -> datetime:
    """Require an aware timestamp and canonicalize it to UTC microseconds."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9B12_P1_{name.upper()}_INVALID", error)
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(f"L9B12_P1_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc).replace(microsecond=parsed.microsecond)


def _optional_timestamp(name: str, value: object) -> datetime | None:
    """Validate an optional aware timestamp."""
    if value is None:
        return None
    return _timestamp(name, value)


def _state(value: object) -> LegalClientMatterMandateCurrentnessState:
    """Parse only the published mandate-currentness vocabulary."""
    try:
        return LegalClientMatterMandateCurrentnessState(value)
    except (TypeError, ValueError) as error:
        _fail("L9B12_P1_STATE_INVALID", error)


def _reason(value: object) -> LegalClientMatterMandateCurrentnessReason:
    """Parse only the published bounded reason vocabulary."""
    try:
        return LegalClientMatterMandateCurrentnessReason(value)
    except (TypeError, ValueError) as error:
        _fail("L9B12_P1_REASON_INVALID", error)


def _upstream_state(name: str, value: object) -> str | None:
    """Validate an optional upstream state label without importing registries."""
    if value is None:
        return None
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"L9B12_P1_{name.upper()}_INVALID")
    return value


def _tuple_identities(name: str, value: object) -> tuple[str, ...]:
    """Validate an immutable ordered tuple of unique identities."""
    if not isinstance(value, (tuple, list)):
        _fail(f"L9B12_P1_{name.upper()}_INVALID")
    result = tuple(_identity(name, item) for item in cast(tuple[Any, ...] | list[Any], value))
    if len(set(result)) != len(result):
        _fail(f"L9B12_P1_{name.upper()}_DUPLICATE")
    return result


def _tuple_fingerprints(name: str, value: object) -> tuple[str, ...]:
    """Validate an immutable ordered tuple of unique fingerprints."""
    if not isinstance(value, (tuple, list)):
        _fail(f"L9B12_P1_{name.upper()}_INVALID")
    result = tuple(_fingerprint(name, item) for item in cast(tuple[Any, ...] | list[Any], value))
    if len(set(result)) != len(result):
        _fail(f"L9B12_P1_{name.upper()}_DUPLICATE")
    return result


def _json_value(value: object) -> object:
    """Convert immutable values to deterministic JSON-safe values."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace(
            "+00:00", "Z"
        )
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    return value


def _digest(instance: "LegalClientMatterMandateCurrentness") -> str:
    """Hash every semantic field except the derived fingerprint."""
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


def _projection_id(tenant_id: str, mandate_id: str, evaluation_time: datetime) -> str:
    """Derive a deterministic in-memory projection identity."""
    payload = {
        "tenant_id": tenant_id,
        "mandate_id": mandate_id,
        "evaluation_time": evaluation_time.isoformat(timespec="microseconds"),
    }
    digest = hashlib.sha3_512(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:48]
    return f"currentness-{digest}"


@dataclass(frozen=True, slots=True)
class LegalClientMatterMandateCurrentness:
    """Immutable currentness evidence for one historical mandate.

    The value contains only already-derived scalar evidence. The factory below
    accepts exact canonical domain values but performs no registry reads, clock
    access, persistence, transaction work, authorization, or downstream legal
    mutation. Only ``CURRENT`` is usable by a future Engagement composer.
    """

    currentness_id: str
    tenant_id: str
    mandate_id: str | None
    mandate_fingerprint: str | None
    case_matter_id: str | None
    matter_fingerprint: str | None
    client_party_id: str | None
    subject_identity_fingerprint: str | None
    client_grant_id: str | None
    client_grant_fingerprint: str | None
    firm_acknowledgment_id: str | None
    firm_acknowledgment_fingerprint: str | None
    effective_from: datetime | None
    effective_until: datetime | None
    evaluation_time: datetime
    grant_currentness_state: str | None
    grant_currentness_fingerprint: str | None
    grant_currentness_tenant_id: str | None
    grant_currentness_client_grant_id: str | None
    grant_currentness_client_grant_fingerprint: str | None
    grant_currentness_case_matter_id: str | None
    grant_currentness_matter_fingerprint: str | None
    grant_currentness_client_party_id: str | None
    grant_currentness_subject_identity_fingerprint: str | None
    acknowledgment_currentness_state: str | None
    acknowledgment_currentness_fingerprint: str | None
    acknowledgment_currentness_tenant_id: str | None
    acknowledgment_currentness_client_grant_id: str | None
    acknowledgment_currentness_client_grant_fingerprint: str | None
    acknowledgment_currentness_case_matter_id: str | None
    acknowledgment_currentness_matter_fingerprint: str | None
    acknowledgment_currentness_client_party_id: str | None
    acknowledgment_currentness_subject_identity_fingerprint: str | None
    decisive_acknowledgment_ids: tuple[str, ...]
    decisive_acknowledgment_fingerprints: tuple[str, ...]
    corruption_evidence_fingerprints: tuple[str, ...]
    state: LegalClientMatterMandateCurrentnessState | str
    reason: LegalClientMatterMandateCurrentnessReason | str
    schema: str = SCHEMA
    currentness_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate exact schema, state evidence and deterministic integrity."""
        if self.schema != SCHEMA or self.currentness_version != VERSION:
            _fail("L9B12_P1_IDENTITY_INVALID")
        currentness_id = _identity("currentness_id", self.currentness_id)
        tenant_id = _tenant(self.tenant_id)
        mandate_id = _optional_identity("mandate_id", self.mandate_id)
        mandate_fp = _optional_fingerprint("mandate_fingerprint", self.mandate_fingerprint)
        matter_id = _optional_identity("case_matter_id", self.case_matter_id)
        matter_fp = _optional_fingerprint("matter_fingerprint", self.matter_fingerprint)
        party_id = _optional_identity("client_party_id", self.client_party_id)
        subject_fp = _optional_fingerprint(
            "subject_identity_fingerprint", self.subject_identity_fingerprint
        )
        grant_id = _optional_identity("client_grant_id", self.client_grant_id)
        grant_fp = _optional_fingerprint("client_grant_fingerprint", self.client_grant_fingerprint)
        acknowledgment_id = _optional_identity(
            "firm_acknowledgment_id", self.firm_acknowledgment_id
        )
        acknowledgment_fp = _optional_fingerprint(
            "firm_acknowledgment_fingerprint", self.firm_acknowledgment_fingerprint
        )
        effective_from = _optional_timestamp("effective_from", self.effective_from)
        effective_until = _optional_timestamp("effective_until", self.effective_until)
        evaluation_time = _timestamp("evaluation_time", self.evaluation_time)
        if effective_from is not None and effective_until is not None and effective_until <= effective_from:
            _fail("L9B12_P1_EFFECTIVE_INTERVAL_INVALID")
        grant_state = _upstream_state("grant_currentness_state", self.grant_currentness_state)
        grant_currentness_fp = _optional_fingerprint(
            "grant_currentness_fingerprint", self.grant_currentness_fingerprint
        )
        acknowledgment_state = _upstream_state(
            "acknowledgment_currentness_state", self.acknowledgment_currentness_state
        )
        acknowledgment_currentness_fp = _optional_fingerprint(
            "acknowledgment_currentness_fingerprint",
            self.acknowledgment_currentness_fingerprint,
        )
        upstream_identities = (
            ("grant_currentness_tenant_id", self.grant_currentness_tenant_id),
            ("grant_currentness_client_grant_id", self.grant_currentness_client_grant_id),
            ("grant_currentness_case_matter_id", self.grant_currentness_case_matter_id),
            ("grant_currentness_client_party_id", self.grant_currentness_client_party_id),
            ("acknowledgment_currentness_tenant_id", self.acknowledgment_currentness_tenant_id),
            (
                "acknowledgment_currentness_client_grant_id",
                self.acknowledgment_currentness_client_grant_id,
            ),
            (
                "acknowledgment_currentness_case_matter_id",
                self.acknowledgment_currentness_case_matter_id,
            ),
            (
                "acknowledgment_currentness_client_party_id",
                self.acknowledgment_currentness_client_party_id,
            ),
        )
        normalized_upstream_ids = {
            name: _optional_identity(name, value) for name, value in upstream_identities
        }
        upstream_fingerprints = (
            ("grant_currentness_client_grant_fingerprint", self.grant_currentness_client_grant_fingerprint),
            ("grant_currentness_matter_fingerprint", self.grant_currentness_matter_fingerprint),
            ("grant_currentness_subject_identity_fingerprint", self.grant_currentness_subject_identity_fingerprint),
            (
                "acknowledgment_currentness_client_grant_fingerprint",
                self.acknowledgment_currentness_client_grant_fingerprint,
            ),
            (
                "acknowledgment_currentness_matter_fingerprint",
                self.acknowledgment_currentness_matter_fingerprint,
            ),
            (
                "acknowledgment_currentness_subject_identity_fingerprint",
                self.acknowledgment_currentness_subject_identity_fingerprint,
            ),
        )
        normalized_upstream_fps = {
            name: _optional_fingerprint(name, value) for name, value in upstream_fingerprints
        }
        decisive_ids = _tuple_identities(
            "decisive_acknowledgment_ids", self.decisive_acknowledgment_ids
        )
        decisive_fps = _tuple_fingerprints(
            "decisive_acknowledgment_fingerprints",
            self.decisive_acknowledgment_fingerprints,
        )
        corruption = _tuple_fingerprints(
            "corruption_evidence_fingerprints", self.corruption_evidence_fingerprints
        )
        if len(decisive_ids) != len(decisive_fps):
            _fail("L9B12_P1_DECISIVE_EVIDENCE_LENGTH_MISMATCH")
        state = _state(self.state)
        reason = _reason(self.reason)

        if state is LegalClientMatterMandateCurrentnessState.FORMATION_ABSENT:
            forbidden = (
                mandate_fp,
                matter_id,
                matter_fp,
                party_id,
                subject_fp,
                grant_id,
                grant_fp,
                acknowledgment_id,
                acknowledgment_fp,
                effective_from,
                effective_until,
                grant_state,
                grant_currentness_fp,
                acknowledgment_state,
                acknowledgment_currentness_fp,
            )
            if any(value is not None for value in forbidden) or decisive_ids or decisive_fps or corruption:
                _fail("L9B12_P1_FORMATION_ABSENT_EVIDENCE_FORBIDDEN")
            if mandate_id is None:
                _fail("L9B12_P1_MANDATE_ID_REQUIRED")
            if any(value is not None for value in normalized_upstream_ids.values()) or any(
                value is not None for value in normalized_upstream_fps.values()
            ):
                _fail("L9B12_P1_FORMATION_ABSENT_EVIDENCE_FORBIDDEN")
        else:
            required = (
                mandate_id,
                mandate_fp,
                matter_id,
                matter_fp,
                party_id,
                subject_fp,
                grant_id,
                grant_fp,
                acknowledgment_id,
                acknowledgment_fp,
                effective_from,
                grant_state,
                grant_currentness_fp,
                acknowledgment_state,
                acknowledgment_currentness_fp,
            )
            if any(value is None for value in required):
                _fail("L9B12_P1_EVIDENCE_REQUIRED")
            if state is LegalClientMatterMandateCurrentnessState.CORRUPT_BLOCKED:
                if not corruption:
                    _fail("L9B12_P1_CORRUPTION_EVIDENCE_REQUIRED")
            elif corruption:
                _fail("L9B12_P1_CORRUPTION_EVIDENCE_FORBIDDEN")

        expected_reason = (
            LegalClientMatterMandateCurrentnessReason.CORRUPT_EVIDENCE
            if state is LegalClientMatterMandateCurrentnessState.CORRUPT_BLOCKED
            else LegalClientMatterMandateCurrentnessReason(state.value)
        )
        if reason is not expected_reason:
            _fail("L9B12_P1_REASON_STATE_MISMATCH")
        if state is LegalClientMatterMandateCurrentnessState.CURRENT:
            if grant_state != LegalClientMatterMandateGrantCurrentnessState.CURRENT.value:
                _fail("L9B12_P1_CURRENT_GRANT_REQUIRED")
            if acknowledgment_state != LegalClientMatterMandateAcknowledgmentCurrentnessState.ACKNOWLEDGED.value:
                _fail("L9B12_P1_CURRENT_ACKNOWLEDGMENT_REQUIRED")
            if len(decisive_ids) != 1 or len(decisive_fps) != 1:
                _fail("L9B12_P1_DECISIVE_ACKNOWLEDGMENT_REQUIRED")
        object.__setattr__(self, "currentness_id", currentness_id)
        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "mandate_id", mandate_id)
        object.__setattr__(self, "mandate_fingerprint", mandate_fp)
        object.__setattr__(self, "case_matter_id", matter_id)
        object.__setattr__(self, "matter_fingerprint", matter_fp)
        object.__setattr__(self, "client_party_id", party_id)
        object.__setattr__(self, "subject_identity_fingerprint", subject_fp)
        object.__setattr__(self, "client_grant_id", grant_id)
        object.__setattr__(self, "client_grant_fingerprint", grant_fp)
        object.__setattr__(self, "firm_acknowledgment_id", acknowledgment_id)
        object.__setattr__(self, "firm_acknowledgment_fingerprint", acknowledgment_fp)
        object.__setattr__(self, "effective_from", effective_from)
        object.__setattr__(self, "effective_until", effective_until)
        object.__setattr__(self, "evaluation_time", evaluation_time)
        object.__setattr__(self, "grant_currentness_state", grant_state)
        object.__setattr__(self, "grant_currentness_fingerprint", grant_currentness_fp)
        object.__setattr__(self, "acknowledgment_currentness_state", acknowledgment_state)
        object.__setattr__(self, "acknowledgment_currentness_fingerprint", acknowledgment_currentness_fp)
        for name, value in normalized_upstream_ids.items():
            object.__setattr__(self, name, value)
        for name, value in normalized_upstream_fps.items():
            object.__setattr__(self, name, value)
        object.__setattr__(self, "decisive_acknowledgment_ids", decisive_ids)
        object.__setattr__(self, "decisive_acknowledgment_fingerprints", decisive_fps)
        object.__setattr__(self, "corruption_evidence_fingerprints", corruption)
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "reason", reason)
        digest = _digest(self)
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            _fail("L9B12_P1_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @property
    def is_current(self) -> bool:
        """Return true only for the exact positive state."""
        return self.state is LegalClientMatterMandateCurrentnessState.CURRENT

    @property
    def is_usable(self) -> bool:
        """Expose the same narrow positive predicate as ``is_current``."""
        return self.is_current

    @property
    def reason_code(self) -> LegalClientMatterMandateCurrentnessReason:
        """Expose the bounded machine-readable reason."""
        return cast(LegalClientMatterMandateCurrentnessReason, self.reason)

    def to_dict(self) -> dict[str, object]:
        """Serialize complete immutable evidence without mutable state."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LegalClientMatterMandateCurrentness":
        """Hydrate exact fields and verify the supplied SHA3-512 fingerprint."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9B12_P1_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(dict[str, Any], values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, result.fingerprint):
            _fail("L9B12_P1_FINGERPRINT_MISMATCH")
        return result


def _lineage_matches(value: LegalClientMatterMandateCurrentness) -> bool:
    """Check exact mandate/grant/acknowledgment identity and scope lineage."""
    same_grant = (
        value.grant_currentness_tenant_id == value.tenant_id
        and value.grant_currentness_client_grant_id == value.client_grant_id
        and value.grant_currentness_client_grant_fingerprint == value.client_grant_fingerprint
    )
    same_ack_grant = (
        value.acknowledgment_currentness_tenant_id == value.tenant_id
        and value.acknowledgment_currentness_client_grant_id == value.client_grant_id
        and value.acknowledgment_currentness_client_grant_fingerprint == value.client_grant_fingerprint
    )
    same_subject = all(
        (
            getattr(value, f"{prefix}_case_matter_id") == value.case_matter_id
            and getattr(value, f"{prefix}_matter_fingerprint") == value.matter_fingerprint
            and getattr(value, f"{prefix}_client_party_id") == value.client_party_id
            and getattr(value, f"{prefix}_subject_identity_fingerprint")
            == value.subject_identity_fingerprint
        )
        for prefix in ("grant_currentness", "acknowledgment_currentness")
    )
    return same_grant and same_ack_grant and same_subject


def _from_values(
    *,
    tenant_id: str,
    mandate_id: str,
    mandate: LegalClientMatterMandate | None,
    grant_currentness: LegalClientMatterMandateGrantCurrentness | None,
    acknowledgment_currentness: LegalClientMatterMandateAcknowledgmentCurrentness | None,
    evaluation_time: datetime,
) -> LegalClientMatterMandateCurrentness:
    """Build scalar evidence from exact canonical immutable values."""
    tenant = _tenant(tenant_id)
    requested_mandate_id = _identity("mandate_id", mandate_id)
    at = _timestamp("evaluation_time", evaluation_time)
    currentness_id = _projection_id(tenant, requested_mandate_id, at)
    if mandate is None:
        if grant_currentness is not None or acknowledgment_currentness is not None:
            _fail("L9B12_P1_FORMATION_ABSENT_UPSTREAM_FORBIDDEN")
        return LegalClientMatterMandateCurrentness(
            currentness_id=currentness_id,
            tenant_id=tenant,
            mandate_id=requested_mandate_id,
            mandate_fingerprint=None,
            case_matter_id=None,
            matter_fingerprint=None,
            client_party_id=None,
            subject_identity_fingerprint=None,
            client_grant_id=None,
            client_grant_fingerprint=None,
            firm_acknowledgment_id=None,
            firm_acknowledgment_fingerprint=None,
            effective_from=None,
            effective_until=None,
            evaluation_time=at,
            grant_currentness_state=None,
            grant_currentness_fingerprint=None,
            grant_currentness_tenant_id=None,
            grant_currentness_client_grant_id=None,
            grant_currentness_client_grant_fingerprint=None,
            grant_currentness_case_matter_id=None,
            grant_currentness_matter_fingerprint=None,
            grant_currentness_client_party_id=None,
            grant_currentness_subject_identity_fingerprint=None,
            acknowledgment_currentness_state=None,
            acknowledgment_currentness_fingerprint=None,
            acknowledgment_currentness_tenant_id=None,
            acknowledgment_currentness_client_grant_id=None,
            acknowledgment_currentness_client_grant_fingerprint=None,
            acknowledgment_currentness_case_matter_id=None,
            acknowledgment_currentness_matter_fingerprint=None,
            acknowledgment_currentness_client_party_id=None,
            acknowledgment_currentness_subject_identity_fingerprint=None,
            decisive_acknowledgment_ids=(),
            decisive_acknowledgment_fingerprints=(),
            corruption_evidence_fingerprints=(),
            state=LegalClientMatterMandateCurrentnessState.FORMATION_ABSENT,
            reason=LegalClientMatterMandateCurrentnessReason.FORMATION_ABSENT,
        )
    if type(mandate) is not LegalClientMatterMandate:
        _fail("L9B12_P1_MANDATE_INVALID")
    if mandate.tenant_id != tenant or mandate.mandate_id != requested_mandate_id:
        _fail("L9B12_P1_MANDATE_CORRELATION_INVALID")
    if type(grant_currentness) is not LegalClientMatterMandateGrantCurrentness:
        _fail("L9B12_P1_GRANT_CURRENTNESS_REQUIRED")
    if type(acknowledgment_currentness) is not LegalClientMatterMandateAcknowledgmentCurrentness:
        _fail("L9B12_P1_ACKNOWLEDGMENT_CURRENTNESS_REQUIRED")
    assert grant_currentness is not None and acknowledgment_currentness is not None
    corruption: tuple[str, ...] = tuple(
        dict.fromkeys(
            fp
            for fp in (
                grant_currentness.fingerprint
                if grant_currentness.state is LegalClientMatterMandateGrantCurrentnessState.CORRUPT_BLOCKED
                else None,
                acknowledgment_currentness.fingerprint
                if acknowledgment_currentness.state
                is LegalClientMatterMandateAcknowledgmentCurrentnessState.CORRUPT_BLOCKED
                else None,
            )
            if fp is not None
        )
    )
    grant_state = cast(str, getattr(grant_currentness.state, "value", grant_currentness.state))
    acknowledgment_state = cast(
        str,
        getattr(acknowledgment_currentness.state, "value", acknowledgment_currentness.state),
    )
    if grant_currentness.state is LegalClientMatterMandateGrantCurrentnessState.CORRUPT_BLOCKED or acknowledgment_currentness.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.CORRUPT_BLOCKED:
        state = LegalClientMatterMandateCurrentnessState.CORRUPT_BLOCKED
    elif grant_currentness.state is LegalClientMatterMandateGrantCurrentnessState.AMBIGUOUS or acknowledgment_currentness.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.AMBIGUOUS:
        state = LegalClientMatterMandateCurrentnessState.AMBIGUOUS
    elif at < mandate.effective_from:
        state = LegalClientMatterMandateCurrentnessState.NOT_YET_EFFECTIVE
    elif mandate.effective_until is not None and at >= mandate.effective_until:
        state = LegalClientMatterMandateCurrentnessState.EXPIRED
    elif grant_currentness.state is not LegalClientMatterMandateGrantCurrentnessState.CURRENT:
        state = LegalClientMatterMandateCurrentnessState.GRANT_NOT_CURRENT
    elif acknowledgment_currentness.state is not LegalClientMatterMandateAcknowledgmentCurrentnessState.ACKNOWLEDGED:
        state = LegalClientMatterMandateCurrentnessState.ACKNOWLEDGMENT_NOT_CURRENT
    elif len(acknowledgment_currentness.decisive_acknowledgment_ids) != 1 or len(acknowledgment_currentness.decisive_acknowledgment_fingerprints) != 1:
        state = LegalClientMatterMandateCurrentnessState.AMBIGUOUS
    else:
        state = LegalClientMatterMandateCurrentnessState.CURRENT
    if state is LegalClientMatterMandateCurrentnessState.CURRENT and (
        not _lineage_matches(
            LegalClientMatterMandateCurrentness(
                currentness_id=currentness_id,
                tenant_id=tenant,
                mandate_id=mandate.mandate_id,
                mandate_fingerprint=mandate.fingerprint,
                case_matter_id=mandate.case_matter_id,
                matter_fingerprint=mandate.matter_fingerprint,
                client_party_id=mandate.client_party_id,
                subject_identity_fingerprint=mandate.subject_identity_fingerprint,
                client_grant_id=mandate.client_grant_reference,
                client_grant_fingerprint=mandate.client_grant_fingerprint,
                firm_acknowledgment_id=mandate.firm_acknowledgment_reference,
                firm_acknowledgment_fingerprint=mandate.firm_acknowledgment_fingerprint,
                effective_from=mandate.effective_from,
                effective_until=mandate.effective_until,
                evaluation_time=at,
                grant_currentness_state=grant_state,
                grant_currentness_fingerprint=grant_currentness.fingerprint,
                grant_currentness_tenant_id=grant_currentness.tenant_id,
                grant_currentness_client_grant_id=grant_currentness.client_grant_id,
                grant_currentness_client_grant_fingerprint=grant_currentness.client_grant_fingerprint,
                grant_currentness_case_matter_id=grant_currentness.case_matter_id,
                grant_currentness_matter_fingerprint=grant_currentness.matter_fingerprint,
                grant_currentness_client_party_id=grant_currentness.client_party_id,
                grant_currentness_subject_identity_fingerprint=grant_currentness.subject_identity_fingerprint,
                acknowledgment_currentness_state=acknowledgment_state,
                acknowledgment_currentness_fingerprint=acknowledgment_currentness.fingerprint,
                acknowledgment_currentness_tenant_id=acknowledgment_currentness.tenant_id,
                acknowledgment_currentness_client_grant_id=acknowledgment_currentness.client_grant_id,
                acknowledgment_currentness_client_grant_fingerprint=acknowledgment_currentness.client_grant_fingerprint,
                acknowledgment_currentness_case_matter_id=acknowledgment_currentness.case_matter_id,
                acknowledgment_currentness_matter_fingerprint=acknowledgment_currentness.matter_fingerprint,
                acknowledgment_currentness_client_party_id=acknowledgment_currentness.client_party_id,
                acknowledgment_currentness_subject_identity_fingerprint=acknowledgment_currentness.subject_identity_fingerprint,
                decisive_acknowledgment_ids=acknowledgment_currentness.decisive_acknowledgment_ids,
                decisive_acknowledgment_fingerprints=acknowledgment_currentness.decisive_acknowledgment_fingerprints,
                corruption_evidence_fingerprints=corruption,
                state=state,
                reason=LegalClientMatterMandateCurrentnessReason.CURRENT,
            )
        )
        or acknowledgment_currentness.decisive_acknowledgment_ids[0] != mandate.firm_acknowledgment_reference
        or acknowledgment_currentness.decisive_acknowledgment_fingerprints[0] != mandate.firm_acknowledgment_fingerprint
    ):
        state = LegalClientMatterMandateCurrentnessState.LINEAGE_MISMATCH
    return LegalClientMatterMandateCurrentness(
        currentness_id=currentness_id,
        tenant_id=tenant,
        mandate_id=mandate.mandate_id,
        mandate_fingerprint=mandate.fingerprint,
        case_matter_id=mandate.case_matter_id,
        matter_fingerprint=mandate.matter_fingerprint,
        client_party_id=mandate.client_party_id,
        subject_identity_fingerprint=mandate.subject_identity_fingerprint,
        client_grant_id=mandate.client_grant_reference,
        client_grant_fingerprint=mandate.client_grant_fingerprint,
        firm_acknowledgment_id=mandate.firm_acknowledgment_reference,
        firm_acknowledgment_fingerprint=mandate.firm_acknowledgment_fingerprint,
        effective_from=mandate.effective_from,
        effective_until=mandate.effective_until,
        evaluation_time=at,
        grant_currentness_state=grant_state,
        grant_currentness_fingerprint=grant_currentness.fingerprint,
        grant_currentness_tenant_id=grant_currentness.tenant_id,
        grant_currentness_client_grant_id=grant_currentness.client_grant_id,
        grant_currentness_client_grant_fingerprint=grant_currentness.client_grant_fingerprint,
        grant_currentness_case_matter_id=grant_currentness.case_matter_id,
        grant_currentness_matter_fingerprint=grant_currentness.matter_fingerprint,
        grant_currentness_client_party_id=grant_currentness.client_party_id,
        grant_currentness_subject_identity_fingerprint=grant_currentness.subject_identity_fingerprint,
        acknowledgment_currentness_state=acknowledgment_state,
        acknowledgment_currentness_fingerprint=acknowledgment_currentness.fingerprint,
        acknowledgment_currentness_tenant_id=acknowledgment_currentness.tenant_id,
        acknowledgment_currentness_client_grant_id=acknowledgment_currentness.client_grant_id,
        acknowledgment_currentness_client_grant_fingerprint=acknowledgment_currentness.client_grant_fingerprint,
        acknowledgment_currentness_case_matter_id=acknowledgment_currentness.case_matter_id,
        acknowledgment_currentness_matter_fingerprint=acknowledgment_currentness.matter_fingerprint,
        acknowledgment_currentness_client_party_id=acknowledgment_currentness.client_party_id,
        acknowledgment_currentness_subject_identity_fingerprint=acknowledgment_currentness.subject_identity_fingerprint,
        decisive_acknowledgment_ids=acknowledgment_currentness.decisive_acknowledgment_ids,
        decisive_acknowledgment_fingerprints=acknowledgment_currentness.decisive_acknowledgment_fingerprints,
        corruption_evidence_fingerprints=corruption,
        state=state,
        reason=(
            LegalClientMatterMandateCurrentnessReason.CORRUPT_EVIDENCE
            if state is LegalClientMatterMandateCurrentnessState.CORRUPT_BLOCKED
            else LegalClientMatterMandateCurrentnessReason(state.value)
        ),
    )


def project_legal_client_matter_mandate_currentness(
    *,
    tenant_id: str,
    mandate_id: str,
    mandate: LegalClientMatterMandate | None,
    grant_currentness: LegalClientMatterMandateGrantCurrentness | None,
    acknowledgment_currentness: LegalClientMatterMandateAcknowledgmentCurrentness | None,
    evaluation_time: datetime,
) -> LegalClientMatterMandateCurrentness:
    """Project exact canonical evidence without persistence or clock access.

    The caller supplies already-hydrated immutable values. This function does
    not query a registry, read Mongo, select history, authorize an actor, or
    create Engagement/financial authority. ``CURRENT`` requires exact grant,
    matter, party, subject and decisive acknowledgment identity equality.
    """
    return _from_values(
        tenant_id=tenant_id,
        mandate_id=mandate_id,
        mandate=mandate,
        grant_currentness=grant_currentness,
        acknowledgment_currentness=acknowledgment_currentness,
        evaluation_time=evaluation_time,
    )


__all__ = [
    "CURRENTNESS_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientMatterMandateCurrentness",
    "LegalClientMatterMandateCurrentnessError",
    "LegalClientMatterMandateCurrentnessReason",
    "LegalClientMatterMandateCurrentnessState",
    "project_legal_client_matter_mandate_currentness",
]


# ARTIFACT: legal_client_matter_mandate_currentness.py
# VERSION: v1.0.0-L9B12-P1-CLIENT-MATTER-MANDATE-CURRENTNESS
# AUTHORITY BOUNDARY: immutable mandate-currentness projection only
# TENANT POSTURE: exact tenant/matter/client/subject and grant/ack identity binding
# FAIL-CLOSED POSTURE: strict state, temporal, lineage, schema and fingerprint validation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
