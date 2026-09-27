"""Immutable currentness projection for firm mandate acknowledgments.

TITLE: WILSY OS Legal Client Matter Mandate Acknowledgment Currentness
VERSION: v1.0.0-L9B10-P2-FIRM-MANDATE-ACKNOWLEDGMENT-CURRENTNESS
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Bind one already-composed acknowledgment currentness result to an
         exact client-grant lineage, explicit evaluation instant, decision
         evidence and deterministic integrity. This pure value never reads
         history or creates mandate authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_mandate_acknowledgment_currentness.py
COLLABORATION / OWNERSHIP: LegalClientMatterMandateAcknowledgment owns the
                            immutable decision evidence; a future composer
                            will select history and supply this projection.
                            Grant currentness, IAM, mandate, Engagement,
                            Representation, Court and finance remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B10-P2-FIRM-MANDATE-ACKNOWLEDGMENT-CURRENTNESS establishes
           explicit ACKNOWLEDGED/DECLINED/REQUIRES_REVIEW/NO_DECISION/
           AMBIGUOUS/CORRUPT_BLOCKED states, exact grant lineage, evidence
           binding, aware-UTC evaluation time, deterministic SHA3-512 and
           strict hydration. It performs no history selection or persistence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers and lowercase SHA3-512
                             fingerprints only; no PII, credentials, tokens,
                             raw evidence bodies or caller prose are retained.
TENANT BOUNDARY: One explicit non-global tenant and one exact grant lineage
                 are required; no fallback or cross-tenant inference exists.
AUTHORITY BOUNDARY: Pure currentness output shape and state invariants only.
                    No registry, clock, IAM, grant-currentness, mandate,
                    Engagement, Representation, Court or financial authority.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement, release or execution;
                              Kennel EOS remains exclusive financial authority.
TRANSACTION BOUNDARY: Immutable in-memory construction, serialization and
                      strict hydration only; no database, network, session,
                      transaction, retry, commit or abort behavior.
FAIL-CLOSED DECLARATION: Invalid lineage, state/evidence combination,
                         timestamp, schema or fingerprint rejects without
                         coercion, winner selection or authority expansion.
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


VERSION: Final[str] = "v1.0.0-L9B10-P2-FIRM-MANDATE-ACKNOWLEDGMENT-CURRENTNESS"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-MANDATE-ACKNOWLEDGMENT-CURRENTNESS/V1"
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
    "client_grant_id",
    "client_grant_fingerprint",
    "case_matter_id",
    "matter_fingerprint",
    "client_party_id",
    "subject_identity_fingerprint",
    "evaluation_time",
    "state",
    "reason",
    "acknowledgment_evidence_fingerprints",
    "decisive_acknowledgment_ids",
    "decisive_acknowledgment_fingerprints",
    "decisive_decisions",
    "corruption_evidence_fingerprints",
    "fingerprint",
)
CURRENTNESS_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientMatterMandateAcknowledgmentCurrentnessState(StrEnum):
    """Closed currentness outcomes at one explicit evaluation instant."""

    ACKNOWLEDGED = "ACKNOWLEDGED"
    DECLINED = "DECLINED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"
    NO_DECISION = "NO_DECISION"
    AMBIGUOUS = "AMBIGUOUS"
    CORRUPT_BLOCKED = "CORRUPT_BLOCKED"


class LegalClientMatterMandateAcknowledgmentCurrentnessReason(StrEnum):
    """Bounded explanation for each projection state."""

    ACKNOWLEDGED = "ACKNOWLEDGED"
    DECLINED = "DECLINED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"
    NO_DECISION = "NO_DECISION"
    AMBIGUOUS_DECISIONS = "AMBIGUOUS_DECISIONS"
    CORRUPT_EVIDENCE = "CORRUPT_EVIDENCE"


class LegalClientMatterMandateAcknowledgmentCurrentnessError(ValueError):
    """Stable non-sensitive projection validation failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one bounded code without echoing authority-bearing input."""
    error = LegalClientMatterMandateAcknowledgmentCurrentnessError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    """Require one bounded opaque identity without trimming or coercion."""
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"L9B10_P2_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    """Require one explicit non-global tenant identity."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9B10_P2_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 fingerprint."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9B10_P2_{name.upper()}_INVALID")
    return value


def _timestamp(name: str, value: object) -> datetime:
    """Require an aware timestamp and normalize it to UTC microseconds."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9B10_P2_{name.upper()}_INVALID", error)
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(f"L9B10_P2_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc)


def _fingerprint_tuple(name: str, value: object, *, allow_empty: bool) -> tuple[str, ...]:
    """Validate an ordered tuple/list of unique fingerprints."""
    if not isinstance(value, (tuple, list)):
        _fail(f"L9B10_P2_{name.upper()}_INVALID")
    if not value and not allow_empty:
        _fail(f"L9B10_P2_{name.upper()}_REQUIRED")
    result = tuple(_fingerprint(name, item) for item in cast(tuple[Any, ...] | list[Any], value))
    if len(set(result)) != len(result):
        _fail(f"L9B10_P2_{name.upper()}_DUPLICATE")
    return result


def _identity_tuple(name: str, value: object, *, allow_empty: bool) -> tuple[str, ...]:
    """Validate an ordered tuple/list of unique opaque identities."""
    if not isinstance(value, (tuple, list)):
        _fail(f"L9B10_P2_{name.upper()}_INVALID")
    if not value and not allow_empty:
        _fail(f"L9B10_P2_{name.upper()}_REQUIRED")
    result = tuple(_identity(name, item) for item in cast(tuple[Any, ...] | list[Any], value))
    if len(set(result)) != len(result):
        _fail(f"L9B10_P2_{name.upper()}_DUPLICATE")
    return result


def _decision_tuple(value: object, *, allow_empty: bool) -> tuple[LegalClientMatterMandateAcknowledgmentCurrentnessState, ...]:
    """Validate only the three source acknowledgment decision values."""
    if not isinstance(value, (tuple, list)):
        _fail("L9B10_P2_DECISIVE_DECISIONS_INVALID")
    if not value and not allow_empty:
        _fail("L9B10_P2_DECISIVE_DECISIONS_REQUIRED")
    result: list[LegalClientMatterMandateAcknowledgmentCurrentnessState] = []
    for item in cast(tuple[Any, ...] | list[Any], value):
        try:
            decision = LegalClientMatterMandateAcknowledgmentCurrentnessState(item)
        except (TypeError, ValueError) as error:
            _fail("L9B10_P2_DECISIVE_DECISION_INVALID", error)
        if decision not in {
            LegalClientMatterMandateAcknowledgmentCurrentnessState.ACKNOWLEDGED,
            LegalClientMatterMandateAcknowledgmentCurrentnessState.DECLINED,
            LegalClientMatterMandateAcknowledgmentCurrentnessState.REQUIRES_REVIEW,
        }:
            _fail("L9B10_P2_DECISIVE_DECISION_INVALID")
        result.append(decision)
    return tuple(result)


def _state(value: object) -> LegalClientMatterMandateAcknowledgmentCurrentnessState:
    """Parse the closed projection state vocabulary."""
    try:
        return LegalClientMatterMandateAcknowledgmentCurrentnessState(value)
    except (TypeError, ValueError) as error:
        _fail("L9B10_P2_STATE_INVALID", error)


def _reason(value: object) -> LegalClientMatterMandateAcknowledgmentCurrentnessReason:
    """Parse the closed projection reason vocabulary."""
    try:
        return LegalClientMatterMandateAcknowledgmentCurrentnessReason(value)
    except (TypeError, ValueError) as error:
        _fail("L9B10_P2_REASON_INVALID", error)


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


def _digest(instance: "LegalClientMatterMandateAcknowledgmentCurrentness") -> str:
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


@dataclass(frozen=True, slots=True)
class LegalClientMatterMandateAcknowledgmentCurrentness:
    """Immutable currentness output for one exact grant and evaluation time.

    A future composer supplies already-selected history and state. This value
    does not sort records, read a registry, consult a clock, evaluate IAM or
    create mandate, Engagement, Representation, Court or financial authority.
    Only ``ACKNOWLEDGED`` is positive for a later mandate-forming gate.
    """

    currentness_id: str
    tenant_id: str
    client_grant_id: str
    client_grant_fingerprint: str
    case_matter_id: str
    matter_fingerprint: str
    client_party_id: str
    subject_identity_fingerprint: str
    evaluation_time: datetime
    state: LegalClientMatterMandateAcknowledgmentCurrentnessState | str
    reason: LegalClientMatterMandateAcknowledgmentCurrentnessReason | str
    acknowledgment_evidence_fingerprints: tuple[str, ...]
    decisive_acknowledgment_ids: tuple[str, ...]
    decisive_acknowledgment_fingerprints: tuple[str, ...]
    decisive_decisions: tuple[str, ...]
    corruption_evidence_fingerprints: tuple[str, ...] = ()
    schema: str = SCHEMA
    currentness_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate exact lineage, state-specific evidence and integrity."""
        if self.schema != SCHEMA or self.currentness_version != VERSION:
            _fail("L9B10_P2_IDENTITY_INVALID")
        currentness_id = _identity("currentness_id", self.currentness_id)
        tenant_id = _tenant(self.tenant_id)
        grant_id = _identity("client_grant_id", self.client_grant_id)
        grant_fp = _fingerprint("client_grant_fingerprint", self.client_grant_fingerprint)
        matter_id = _identity("case_matter_id", self.case_matter_id)
        matter_fp = _fingerprint("matter_fingerprint", self.matter_fingerprint)
        party_id = _identity("client_party_id", self.client_party_id)
        subject_fp = _fingerprint("subject_identity_fingerprint", self.subject_identity_fingerprint)
        evaluation = _timestamp("evaluation_time", self.evaluation_time)
        state = _state(self.state)
        reason = _reason(self.reason)
        evidence = _fingerprint_tuple(
            "acknowledgment_evidence_fingerprints",
            self.acknowledgment_evidence_fingerprints,
            allow_empty=True,
        )
        decisive_ids = _identity_tuple(
            "decisive_acknowledgment_ids", self.decisive_acknowledgment_ids, allow_empty=True
        )
        decisive_fps = _fingerprint_tuple(
            "decisive_acknowledgment_fingerprints",
            self.decisive_acknowledgment_fingerprints,
            allow_empty=True,
        )
        decisive_decisions = _decision_tuple(self.decisive_decisions, allow_empty=True)
        corruption = _fingerprint_tuple(
            "corruption_evidence_fingerprints",
            self.corruption_evidence_fingerprints,
            allow_empty=True,
        )
        if not (
            len(decisive_ids) == len(decisive_fps) == len(decisive_decisions)
        ):
            _fail("L9B10_P2_DECISIVE_EVIDENCE_LENGTH_MISMATCH")
        if any(item not in evidence for item in decisive_fps):
            _fail("L9B10_P2_DECISIVE_EVIDENCE_NOT_BOUND")

        positive_states = {
            LegalClientMatterMandateAcknowledgmentCurrentnessState.ACKNOWLEDGED,
            LegalClientMatterMandateAcknowledgmentCurrentnessState.DECLINED,
            LegalClientMatterMandateAcknowledgmentCurrentnessState.REQUIRES_REVIEW,
        }
        if state in positive_states:
            if reason.value != state.value or not evidence or not decisive_ids:
                _fail("L9B10_P2_DECISIVE_EVIDENCE_REQUIRED")
            if any(decision is not state for decision in decisive_decisions):
                _fail("L9B10_P2_STATE_EVIDENCE_MISMATCH")
            if corruption:
                _fail("L9B10_P2_CORRUPTION_EVIDENCE_FORBIDDEN")
        elif state is LegalClientMatterMandateAcknowledgmentCurrentnessState.NO_DECISION:
            if reason is not LegalClientMatterMandateAcknowledgmentCurrentnessReason.NO_DECISION:
                _fail("L9B10_P2_REASON_STATE_MISMATCH")
            if evidence or decisive_ids or decisive_fps or decisive_decisions or corruption:
                _fail("L9B10_P2_NO_DECISION_EVIDENCE_FORBIDDEN")
        elif state is LegalClientMatterMandateAcknowledgmentCurrentnessState.AMBIGUOUS:
            if reason is not LegalClientMatterMandateAcknowledgmentCurrentnessReason.AMBIGUOUS_DECISIONS:
                _fail("L9B10_P2_REASON_STATE_MISMATCH")
            if len(decisive_ids) < 2 or len(set(decisive_decisions)) < 2:
                _fail("L9B10_P2_AMBIGUITY_EVIDENCE_REQUIRED")
            if not evidence or corruption:
                _fail("L9B10_P2_AMBIGUITY_EVIDENCE_REQUIRED")
        elif state is LegalClientMatterMandateAcknowledgmentCurrentnessState.CORRUPT_BLOCKED:
            if reason is not LegalClientMatterMandateAcknowledgmentCurrentnessReason.CORRUPT_EVIDENCE:
                _fail("L9B10_P2_REASON_STATE_MISMATCH")
            if not corruption or evidence or decisive_ids or decisive_fps or decisive_decisions:
                _fail("L9B10_P2_CORRUPT_TRUSTED_EVIDENCE_FORBIDDEN")

        object.__setattr__(self, "currentness_id", currentness_id)
        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "client_grant_id", grant_id)
        object.__setattr__(self, "client_grant_fingerprint", grant_fp)
        object.__setattr__(self, "case_matter_id", matter_id)
        object.__setattr__(self, "matter_fingerprint", matter_fp)
        object.__setattr__(self, "client_party_id", party_id)
        object.__setattr__(self, "subject_identity_fingerprint", subject_fp)
        object.__setattr__(self, "evaluation_time", evaluation)
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "acknowledgment_evidence_fingerprints", evidence)
        object.__setattr__(self, "decisive_acknowledgment_ids", decisive_ids)
        object.__setattr__(self, "decisive_acknowledgment_fingerprints", decisive_fps)
        object.__setattr__(self, "decisive_decisions", decisive_decisions)
        object.__setattr__(self, "corruption_evidence_fingerprints", corruption)
        digest = _digest(self)
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            _fail("L9B10_P2_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @property
    def is_acknowledged(self) -> bool:
        """Return true only for current ACKNOWLEDGED evidence."""
        return self.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.ACKNOWLEDGED

    @property
    def is_usable(self) -> bool:
        """Expose the narrow positive predicate without forming a mandate."""
        return self.is_acknowledged

    def to_dict(self) -> dict[str, object]:
        """Serialize the complete immutable projection without raw evidence."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(
        cls, payload: Mapping[str, object]
    ) -> "LegalClientMatterMandateAcknowledgmentCurrentness":
        """Hydrate exact schema fields and verify deterministic integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9B10_P2_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(dict[str, Any], values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, result.fingerprint):
            _fail("L9B10_P2_FINGERPRINT_MISMATCH")
        return result


def project_legal_client_matter_mandate_acknowledgment_currentness(
    **values: object,
) -> LegalClientMatterMandateAcknowledgmentCurrentness:
    """Construct one state-safe projection from already-composed evidence.

    This pure function performs no registry read, sorting, clock access, IAM
    evaluation, grant-currentness computation, database work or downstream
    legal mutation. The caller supplies the independently selected evidence.
    """
    return LegalClientMatterMandateAcknowledgmentCurrentness(
        **cast(dict[str, Any], values)
    )


__all__ = [
    "CURRENTNESS_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientMatterMandateAcknowledgmentCurrentness",
    "LegalClientMatterMandateAcknowledgmentCurrentnessError",
    "LegalClientMatterMandateAcknowledgmentCurrentnessReason",
    "LegalClientMatterMandateAcknowledgmentCurrentnessState",
    "project_legal_client_matter_mandate_acknowledgment_currentness",
]


# ARTIFACT: legal_client_matter_mandate_acknowledgment_currentness.py
# VERSION: v1.0.0-L9B10-P2-FIRM-MANDATE-ACKNOWLEDGMENT-CURRENTNESS
# AUTHORITY BOUNDARY: immutable acknowledgment currentness projection only
# TENANT POSTURE: exact tenant/grant/matter/party binding; no fallback
# FAIL-CLOSED POSTURE: state/evidence, timestamp, schema and fingerprint validation; no history selection
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
