"""Pure currentness projection for client Representation-authority history.

TITLE: WILSY OS Legal Client Matter Representation Authority Currentness
VERSION: v1.1.0-L9C11-P21A-CLIENT-REPRESENTATION-AUTHORITY-CURRENTNESS
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Derive one deterministic, immutable currentness snapshot for the
         exact representative-specific P7 history lineage at an explicit UTC
         instant. This projection never invents revocation, expiry,
         supersession or latest-wins authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_representation_authority_currentness.py
COLLABORATION / OWNERSHIP: P1 owns immutable client appointment decisions;
                            P7 owns exact tenant-scoped history reads; this
                            module owns only pure currentness mathematics.
                            A later composer owns the read/transaction seam.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.1.0-L9C11-P21A binds the exact positive P1 representative role
           and representation scope while preserving all prior states,
           fail-closed semantics and read-only behavior.
           v1.0.0-L9C11-P21A establishes explicit
           NO_AUTHORITY/APPOINTED/DECLINED/REQUIRES_REVIEW/AMBIGUOUS/
           CORRUPT_BLOCKED states, exact P7 lineage, explicit aware-UTC
           evaluation, future exclusion, exact-duplicate normalization,
           fail-closed corruption handling, order independence and
           deterministic SHA3-512 projection integrity. It creates no
           lifecycle, revocation, supersession, IAM, Representation, Court
           or financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only opaque identifiers and SHA3-512 fingerprints
                             are retained; no PII or source payload is
                             returned.
TENANT BOUNDARY: Every candidate must match the exact tenant, matter, matter
                 fingerprint, client party, subject fingerprint and
                 representative principal supplied by the caller.
AUTHORITY BOUNDARY: Pure derived client-authority currentness only. P1
                    decisions remain immutable history; this module does not
                    revoke, expire, replace, supersede or select a winner.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for
                              financial execution and settlement.
TRANSACTION BOUNDARY: Immutable construction and deterministic serialization;
                      no clock, network, persistence or transaction work.
FAIL-CLOSED DECLARATION: Any malformed, cross-lineage or contradictory
                         history yields CORRUPT_BLOCKED or AMBIGUOUS; only
                         one distinct eligible APPOINTED row is positive.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Any, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import (
    LegalClientMatterRepresentationAuthority,
    LegalClientMatterRepresentationAuthorityDecision,
)


VERSION: Final[str] = "v1.1.0-L9C11-P21A-CLIENT-REPRESENTATION-AUTHORITY-CURRENTNESS"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-REPRESENTATION-AUTHORITY-CURRENTNESS/V2"
UTC = timezone.utc
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
    "case_matter_id",
    "matter_fingerprint",
    "client_party_id",
    "subject_identity_fingerprint",
    "representative_principal_id",
    "representative_role",
    "representation_scope_capabilities",
    "evaluated_at",
    "decisive_effective_from",
    "decisive_authority_id",
    "decisive_authority_fingerprint",
    "candidate_authority_ids",
    "candidate_authority_fingerprints",
    "candidate_decisions",
    "normalized_authority_count",
    "eligible_authority_count",
    "corruption_evidence_fingerprints",
    "state",
    "reason",
    "fingerprint",
)
CURRENTNESS_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientMatterRepresentationAuthorityCurrentnessState(StrEnum):
    """Closed projection vocabulary; only APPOINTED is positive."""

    NO_AUTHORITY = "NO_AUTHORITY"
    APPOINTED = "APPOINTED"
    DECLINED = "DECLINED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"
    AMBIGUOUS = "AMBIGUOUS"
    CORRUPT_BLOCKED = "CORRUPT_BLOCKED"


class LegalClientMatterRepresentationAuthorityCurrentnessReason(StrEnum):
    """Bounded reason vocabulary corresponding to each projection state."""

    NO_AUTHORITY = "NO_AUTHORITY"
    APPOINTED = "APPOINTED"
    DECLINED = "DECLINED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"
    AMBIGUOUS = "AMBIGUOUS_AUTHORITIES"
    CORRUPT_EVIDENCE = "CORRUPT_EVIDENCE"


class LegalClientMatterRepresentationAuthorityCurrentnessError(ValueError):
    """Stable non-sensitive validation failure for projection evidence."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalClientMatterRepresentationAuthorityCurrentnessError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"L9C11_P21A_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9C11_P21A_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9C11_P21A_{name.upper()}_INVALID")
    return value


def _timestamp(name: str, value: object) -> datetime:
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9C11_P21A_{name.upper()}_INVALID", error)
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(f"L9C11_P21A_{name.upper()}_INVALID")
    return parsed.astimezone(UTC)


def _string_tuple(name: str, value: object, *, fingerprints: bool) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)):
        _fail(f"L9C11_P21A_{name.upper()}_INVALID")
    validator = _fingerprint if fingerprints else _identity
    values = tuple(validator(name, item) for item in cast(tuple[Any, ...] | list[Any], value))
    if len(set(values)) != len(values):
        _fail(f"L9C11_P21A_{name.upper()}_DUPLICATE")
    return values


def _decision_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)):
        _fail("L9C11_P21A_CANDIDATE_DECISIONS_INVALID")
    result: list[str] = []
    for item in cast(tuple[Any, ...] | list[Any], value):
        try:
            result.append(LegalClientMatterRepresentationAuthorityDecision(item).value)
        except (TypeError, ValueError) as error:
            _fail("L9C11_P21A_CANDIDATE_DECISION_INVALID", error)
    return tuple(result)


def _decision_value(value: object) -> str:
    """Normalize the P1 decision enum/string union to its closed value."""
    try:
        return LegalClientMatterRepresentationAuthorityDecision(value).value
    except (TypeError, ValueError) as error:
        _fail("L9C11_P21A_CANDIDATE_DECISION_INVALID", error)


def _state(value: object) -> LegalClientMatterRepresentationAuthorityCurrentnessState:
    try:
        return LegalClientMatterRepresentationAuthorityCurrentnessState(value)
    except (TypeError, ValueError) as error:
        _fail("L9C11_P21A_STATE_INVALID", error)


def _reason(value: object) -> LegalClientMatterRepresentationAuthorityCurrentnessReason:
    try:
        return LegalClientMatterRepresentationAuthorityCurrentnessReason(value)
    except (TypeError, ValueError) as error:
        _fail("L9C11_P21A_REASON_INVALID", error)


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    return value


def _projection_id(
    tenant: str,
    matter: str,
    matter_fingerprint: str,
    party: str,
    subject: str,
    representative: str,
    evaluated_at: datetime,
) -> str:
    payload = {
        "tenant_id": tenant,
        "case_matter_id": matter,
        "matter_fingerprint": matter_fingerprint,
        "client_party_id": party,
        "subject_identity_fingerprint": subject,
        "representative_principal_id": representative,
        "evaluated_at": _json_value(evaluated_at),
    }
    digest = hashlib.sha3_512(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:48]
    return f"representation-authority-currentness:{digest}"


def _corruption_marker(code: str) -> str:
    return hashlib.sha3_512(f"L9C11-P21A:{code}".encode("utf-8")).hexdigest()


def _digest(instance: "LegalClientMatterRepresentationAuthorityCurrentness") -> str:
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
class LegalClientMatterRepresentationAuthorityCurrentness:
    """Immutable exact-lineage P1 currentness evidence.

    P7 history is representative-specific. One eligible distinct P1 row is
    projected to its decision state; two or more distinct eligible rows are
    AMBIGUOUS because no P1 supersession or latest-wins contract exists.
    ``effective_until`` remains source evidence and is intentionally not
    interpreted as a lifecycle expiry by this projection.
    """

    currentness_id: str
    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    client_party_id: str
    subject_identity_fingerprint: str
    representative_principal_id: str
    representative_role: str | None
    representation_scope_capabilities: tuple[str, ...] | list[str]
    evaluated_at: datetime
    decisive_effective_from: datetime | None
    decisive_authority_id: str | None
    decisive_authority_fingerprint: str | None
    candidate_authority_ids: tuple[str, ...]
    candidate_authority_fingerprints: tuple[str, ...]
    candidate_decisions: tuple[str, ...]
    normalized_authority_count: int
    eligible_authority_count: int
    corruption_evidence_fingerprints: tuple[str, ...]
    state: LegalClientMatterRepresentationAuthorityCurrentnessState | str
    reason: LegalClientMatterRepresentationAuthorityCurrentnessReason | str
    schema: str = SCHEMA
    currentness_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate state evidence and derive or verify deterministic integrity."""
        if self.schema != SCHEMA or self.currentness_version != VERSION:
            _fail("L9C11_P21A_IDENTITY_INVALID")
        currentness_id = _identity("currentness_id", self.currentness_id)
        tenant = _tenant(self.tenant_id)
        matter = _identity("case_matter_id", self.case_matter_id)
        matter_fp = _fingerprint("matter_fingerprint", self.matter_fingerprint)
        party = _identity("client_party_id", self.client_party_id)
        subject = _fingerprint("subject_identity_fingerprint", self.subject_identity_fingerprint)
        representative = _identity("representative_principal_id", self.representative_principal_id)
        role = None if self.representative_role is None else _identity("representative_role", self.representative_role)
        scope_value = self.representation_scope_capabilities
        if not isinstance(scope_value, (tuple, list, set, frozenset)):
            _fail("L9C11_P21A_SCOPE_INVALID")
        normalized_scope: set[str] = set()
        for item in scope_value:
            label = item.value if isinstance(item, StrEnum) else item
            if not isinstance(label, str) or not label or label != label.strip():
                _fail("L9C11_P21A_SCOPE_INVALID")
            normalized_scope.add(label)
        scope = tuple(sorted(normalized_scope))
        evaluated_at = _timestamp("evaluated_at", self.evaluated_at)
        decisive_time = None if self.decisive_effective_from is None else _timestamp(
            "decisive_effective_from", self.decisive_effective_from
        )
        decisive_id = None if self.decisive_authority_id is None else _identity(
            "decisive_authority_id", self.decisive_authority_id
        )
        decisive_fp = None if self.decisive_authority_fingerprint is None else _fingerprint(
            "decisive_authority_fingerprint", self.decisive_authority_fingerprint
        )
        candidate_ids = _string_tuple("candidate_authority_ids", self.candidate_authority_ids, fingerprints=False)
        candidate_fps = _string_tuple(
            "candidate_authority_fingerprints", self.candidate_authority_fingerprints, fingerprints=True
        )
        candidate_decisions = _decision_tuple(self.candidate_decisions)
        corruption = _string_tuple(
            "corruption_evidence_fingerprints", self.corruption_evidence_fingerprints, fingerprints=True
        )
        state = _state(self.state)
        reason = _reason(self.reason)
        counts = (self.normalized_authority_count, self.eligible_authority_count)
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in counts):
            _fail("L9C11_P21A_COUNT_INVALID")
        normalized_count, eligible_count = counts
        if eligible_count > normalized_count or len(candidate_ids) != len(candidate_fps) or len(candidate_ids) != len(candidate_decisions):
            _fail("L9C11_P21A_CANDIDATE_EVIDENCE_INVALID")
        positive = state is LegalClientMatterRepresentationAuthorityCurrentnessState.APPOINTED
        if not positive and (role is not None or scope):
            _fail("L9C11_P21A_NON_POSITIVE_BINDING_FORBIDDEN")
        if positive and (role is None or not scope):
            _fail("L9C11_P21A_POSITIVE_BINDING_REQUIRED")
        if state is LegalClientMatterRepresentationAuthorityCurrentnessState.NO_AUTHORITY:
            if candidate_ids or candidate_fps or candidate_decisions or decisive_time is not None or decisive_id is not None or decisive_fp is not None or corruption or eligible_count != 0:
                _fail("L9C11_P21A_NO_AUTHORITY_EVIDENCE_FORBIDDEN")
            expected_reason = LegalClientMatterRepresentationAuthorityCurrentnessReason.NO_AUTHORITY
        elif state in (
            LegalClientMatterRepresentationAuthorityCurrentnessState.APPOINTED,
            LegalClientMatterRepresentationAuthorityCurrentnessState.DECLINED,
            LegalClientMatterRepresentationAuthorityCurrentnessState.REQUIRES_REVIEW,
        ):
            if len(candidate_ids) != 1 or decisive_time is None or decisive_id is None or decisive_fp is None or corruption or eligible_count != 1:
                _fail("L9C11_P21A_DECISIVE_EVIDENCE_REQUIRED")
            if decisive_id != candidate_ids[0] or decisive_fp != candidate_fps[0] or state.value != candidate_decisions[0]:
                _fail("L9C11_P21A_DECISIVE_EVIDENCE_MISMATCH")
            if decisive_time > evaluated_at:
                _fail("L9C11_P21A_FUTURE_DECISIVE_EVIDENCE")
            expected_reason = LegalClientMatterRepresentationAuthorityCurrentnessReason(state.value)
        elif state is LegalClientMatterRepresentationAuthorityCurrentnessState.AMBIGUOUS:
            if len(candidate_ids) < 2 or decisive_time is not None or decisive_id is not None or decisive_fp is not None or corruption or eligible_count < 2:
                _fail("L9C11_P21A_AMBIGUITY_EVIDENCE_INVALID")
            expected_reason = LegalClientMatterRepresentationAuthorityCurrentnessReason.AMBIGUOUS
        else:
            if not corruption or candidate_ids or candidate_fps or candidate_decisions or decisive_time is not None or decisive_id is not None or decisive_fp is not None:
                _fail("L9C11_P21A_CORRUPT_EVIDENCE_INVALID")
            expected_reason = LegalClientMatterRepresentationAuthorityCurrentnessReason.CORRUPT_EVIDENCE
        if reason is not expected_reason:
            _fail("L9C11_P21A_REASON_STATE_MISMATCH")
        for name, value in (
            ("currentness_id", currentness_id),
            ("tenant_id", tenant),
            ("case_matter_id", matter),
            ("matter_fingerprint", matter_fp),
            ("client_party_id", party),
            ("subject_identity_fingerprint", subject),
            ("representative_principal_id", representative),
            ("representative_role", role),
            ("representation_scope_capabilities", scope),
            ("evaluated_at", evaluated_at),
            ("decisive_effective_from", decisive_time),
            ("decisive_authority_id", decisive_id),
            ("decisive_authority_fingerprint", decisive_fp),
            ("candidate_authority_ids", candidate_ids),
            ("candidate_authority_fingerprints", candidate_fps),
            ("candidate_decisions", candidate_decisions),
            ("corruption_evidence_fingerprints", corruption),
            ("state", state),
            ("reason", reason),
        ):
            object.__setattr__(self, name, value)
        digest = _digest(self)
        if self.fingerprint and (
            not isinstance(self.fingerprint, str) or not hmac.compare_digest(self.fingerprint, digest)
        ):
            _fail("L9C11_P21A_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @property
    def is_currently_appointed(self) -> bool:
        """Return true only for one distinct eligible APPOINTED authority."""
        return self.state is LegalClientMatterRepresentationAuthorityCurrentnessState.APPOINTED

    @property
    def is_usable(self) -> bool:
        """Expose the same narrow positive predicate for later firm gates."""
        return self.is_currently_appointed

    def to_dict(self) -> dict[str, object]:
        """Serialize exact immutable projection evidence."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LegalClientMatterRepresentationAuthorityCurrentness":
        """Hydrate the exact schema and verify deterministic integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9C11_P21A_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(dict[str, Any], values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, result.fingerprint):
            _fail("L9C11_P21A_FINGERPRINT_MISMATCH")
        return result


def _result(
    *,
    tenant: str,
    matter: str,
    matter_fingerprint: str,
    party: str,
    subject: str,
    representative: str,
    evaluated_at: datetime,
    normalized_count: int,
    eligible: tuple[LegalClientMatterRepresentationAuthority, ...] = (),
    state: LegalClientMatterRepresentationAuthorityCurrentnessState,
    reason: LegalClientMatterRepresentationAuthorityCurrentnessReason,
    decisive: LegalClientMatterRepresentationAuthority | None = None,
    corruption: tuple[str, ...] = (),
) -> LegalClientMatterRepresentationAuthorityCurrentness:
    ordered = tuple(sorted(eligible, key=lambda value: (value.effective_from, value.fingerprint, value.authority_id)))
    selected = decisive if state is LegalClientMatterRepresentationAuthorityCurrentnessState.APPOINTED else None
    return LegalClientMatterRepresentationAuthorityCurrentness(
        currentness_id=_projection_id(tenant, matter, matter_fingerprint, party, subject, representative, evaluated_at),
        tenant_id=tenant,
        case_matter_id=matter,
        matter_fingerprint=matter_fingerprint,
        client_party_id=party,
        subject_identity_fingerprint=subject,
        representative_principal_id=representative,
        representative_role=None if selected is None else selected.representative_role,
        representation_scope_capabilities=()
        if selected is None
        else selected.representation_scope_capabilities,
        evaluated_at=evaluated_at,
        decisive_effective_from=None if decisive is None else decisive.effective_from,
        decisive_authority_id=None if decisive is None else decisive.authority_id,
        decisive_authority_fingerprint=None if decisive is None else decisive.fingerprint,
        candidate_authority_ids=tuple(value.authority_id for value in ordered),
        candidate_authority_fingerprints=tuple(value.fingerprint for value in ordered),
        candidate_decisions=tuple(_decision_value(value.decision) for value in ordered),
        normalized_authority_count=normalized_count,
        eligible_authority_count=len(ordered),
        corruption_evidence_fingerprints=tuple(sorted(set(corruption))),
        state=state,
        reason=reason,
    )


def _corrupt(
    *,
    tenant: str,
    matter: str,
    matter_fingerprint: str,
    party: str,
    subject: str,
    representative: str,
    evaluated_at: datetime,
    evidence: tuple[str, ...],
    normalized_count: int = 0,
) -> LegalClientMatterRepresentationAuthorityCurrentness:
    return _result(
        tenant=tenant,
        matter=matter,
        matter_fingerprint=matter_fingerprint,
        party=party,
        subject=subject,
        representative=representative,
        evaluated_at=evaluated_at,
        normalized_count=normalized_count,
        state=LegalClientMatterRepresentationAuthorityCurrentnessState.CORRUPT_BLOCKED,
        reason=LegalClientMatterRepresentationAuthorityCurrentnessReason.CORRUPT_EVIDENCE,
        corruption=evidence or (_corruption_marker("UNKNOWN"),),
    )


def project_legal_client_matter_representation_authority_currentness(
    *,
    tenant_id: str,
    case_matter_id: str,
    matter_fingerprint: str,
    client_party_id: str,
    subject_identity_fingerprint: str,
    representative_principal_id: str,
    evaluated_at: datetime,
    authorities: Iterable[LegalClientMatterRepresentationAuthority],
) -> LegalClientMatterRepresentationAuthorityCurrentness:
    """Project one exact P7 lineage at an explicit instant.

    Every supplied row is strictly revalidated before future rows are
    excluded. Exact canonical duplicates collapse to one semantic row. Any
    distinct eligible row makes the result AMBIGUOUS; chronology never
    supersedes an earlier decision and ``effective_until`` is not interpreted
    as an invented lifecycle.
    """
    tenant = _tenant(tenant_id)
    matter = _identity("case_matter_id", case_matter_id)
    matter_fp = _fingerprint("matter_fingerprint", matter_fingerprint)
    party = _identity("client_party_id", client_party_id)
    subject = _fingerprint("subject_identity_fingerprint", subject_identity_fingerprint)
    representative = _identity("representative_principal_id", representative_principal_id)
    evaluated = _timestamp("evaluated_at", evaluated_at)
    try:
        history = tuple(authorities)
    except Exception:
        return _corrupt(
            tenant=tenant,
            matter=matter,
            matter_fingerprint=matter_fp,
            party=party,
            subject=subject,
            representative=representative,
            evaluated_at=evaluated,
            evidence=(_corruption_marker("ITERABLE"),),
        )
    malformed: list[str] = []
    valid: list[LegalClientMatterRepresentationAuthority] = []
    by_id: dict[str, LegalClientMatterRepresentationAuthority] = {}
    by_fingerprint: dict[str, LegalClientMatterRepresentationAuthority] = {}
    for candidate in history:
        if type(candidate) is not LegalClientMatterRepresentationAuthority:
            malformed.append(_corruption_marker("TYPE"))
            continue
        try:
            candidate.__post_init__()
            if (
                candidate.tenant_id != tenant
                or candidate.case_matter_id != matter
                or candidate.matter_fingerprint != matter_fp
                or candidate.client_party_id != party
                or candidate.subject_identity_fingerprint != subject
                or candidate.representative_principal_id != representative
            ):
                malformed.append(candidate.fingerprint)
                continue
            prior_id = by_id.get(candidate.authority_id)
            prior_fp = by_fingerprint.get(candidate.fingerprint)
            canonical = candidate.to_dict()
            if (prior_id is not None and prior_id.to_dict() != canonical) or (
                prior_fp is not None and prior_fp.to_dict() != canonical
            ):
                malformed.append(candidate.fingerprint)
                continue
            if prior_id is None and prior_fp is None:
                by_id[candidate.authority_id] = candidate
                by_fingerprint[candidate.fingerprint] = candidate
                valid.append(candidate)
        except Exception:
            malformed.append(_corruption_marker("MALFORMED"))
    if malformed:
        return _corrupt(
            tenant=tenant,
            matter=matter,
            matter_fingerprint=matter_fp,
            party=party,
            subject=subject,
            representative=representative,
            evaluated_at=evaluated,
            evidence=tuple(malformed),
            normalized_count=len(valid),
        )
    eligible = tuple(candidate for candidate in valid if candidate.effective_from <= evaluated)
    if not eligible:
        return _result(
            tenant=tenant,
            matter=matter,
            matter_fingerprint=matter_fp,
            party=party,
            subject=subject,
            representative=representative,
            evaluated_at=evaluated,
            normalized_count=len(valid),
            state=LegalClientMatterRepresentationAuthorityCurrentnessState.NO_AUTHORITY,
            reason=LegalClientMatterRepresentationAuthorityCurrentnessReason.NO_AUTHORITY,
        )
    if len(eligible) > 1:
        return _result(
            tenant=tenant,
            matter=matter,
            matter_fingerprint=matter_fp,
            party=party,
            subject=subject,
            representative=representative,
            evaluated_at=evaluated,
            normalized_count=len(valid),
            eligible=eligible,
            state=LegalClientMatterRepresentationAuthorityCurrentnessState.AMBIGUOUS,
            reason=LegalClientMatterRepresentationAuthorityCurrentnessReason.AMBIGUOUS,
        )
    decisive = next(iter(eligible))
    decision = LegalClientMatterRepresentationAuthorityCurrentnessState(_decision_value(decisive.decision))
    return _result(
        tenant=tenant,
        matter=matter,
        matter_fingerprint=matter_fp,
        party=party,
        subject=subject,
        representative=representative,
        evaluated_at=evaluated,
        normalized_count=len(valid),
        eligible=eligible,
        state=decision,
        reason=LegalClientMatterRepresentationAuthorityCurrentnessReason(decision.value),
        decisive=decisive,
    )


def evaluate_legal_client_matter_representation_authority_currentness(
    **kwargs: Any,
) -> LegalClientMatterRepresentationAuthorityCurrentness:
    """Named evaluation alias with identical pure projection semantics."""
    return project_legal_client_matter_representation_authority_currentness(**kwargs)


__all__ = [
    "CURRENTNESS_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientMatterRepresentationAuthorityCurrentness",
    "LegalClientMatterRepresentationAuthorityCurrentnessError",
    "LegalClientMatterRepresentationAuthorityCurrentnessReason",
    "LegalClientMatterRepresentationAuthorityCurrentnessState",
    "evaluate_legal_client_matter_representation_authority_currentness",
    "project_legal_client_matter_representation_authority_currentness",
]


# ARTIFACT: legal_client_matter_representation_authority_currentness.py
# VERSION: v1.1.0-L9C11-P21A-CLIENT-REPRESENTATION-AUTHORITY-CURRENTNESS
# AUTHORITY BOUNDARY: pure immutable P1 currentness projection only
# TENANT POSTURE: exact P7 tenant/matter/fingerprint/client/subject/representative lineage
# FAIL-CLOSED POSTURE: malformed, cross-lineage and multiplicity evidence cannot become appointed
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
