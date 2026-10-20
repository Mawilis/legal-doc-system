"""TITLE: WILSY OS Practitioner Matter Access Currentness Projection.
VERSION: v2.0.0-P47-R33-PRACTITIONER-ACCESS-CURRENTNESS-SERVICE
AUTHORITY: Python EOS Legal Operations documentary projection only.
EPITOME: Verifies exact-scope immutable history, revision lineage, effective
    periods and explicit-DENY precedence without creating access authority.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_practitioner_matter_access_currentness.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; history readers and
    provisioning provide codec-verified evidence to this pure service.
CERTIFICATION / UPDATE DATE: 2026-10-20
CHANGELOG:
    2026-10-20 v2.0.0-P47-R33-PRACTITIONER-ACCESS-CURRENTNESS-SERVICE
    Relocate currentness behavior from Domain to Service and re-verify every
    supplied immutable value through the canonical codec.
    2026-10-19 v1.0.0-P9-R94-PRACTITIONER-ACCESS-CURRENTNESS-GREEN
    Established deterministic documentary currentness and DENY precedence.
COMPLIANCE: LAW EK-006; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Pure in-memory projection; no identifiers logged.
TENANT BOUNDARY: Every supplied record must match the exact requested scope.
AUTHORITY BOUNDARY: ALLOW_UNVERIFIED is not permission, issuance authority,
    ethical-wall clearance, professional eligibility, approval or reassignment.
TRANSACTION BOUNDARY: None; no persistence or I/O.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Final, Iterable

from tools.eos.legal_operations.domain.legal_practitioner_matter_access import (
    LegalPractitionerMatterAccessDecision,
    LegalPractitionerMatterAccessEvidence,
)
from tools.eos.legal_operations.service.legal_practitioner_matter_access_codec import (
    encode_practitioner_matter_access,
    verify_practitioner_matter_access,
)


VERSION: Final[str] = (
    "v2.0.0-P47-R33-PRACTITIONER-ACCESS-CURRENTNESS-SERVICE"
)


class LegalPractitionerMatterAccessCurrentnessState(StrEnum):
    """Classify documentary findings; no state is runtime access permission."""

    NO_APPLICABLE_EVIDENCE = "NO_APPLICABLE_EVIDENCE"
    ALLOW_UNVERIFIED = "ALLOW_UNVERIFIED"
    DENY_BLOCKED = "DENY_BLOCKED"
    AMBIGUOUS_BLOCKED = "AMBIGUOUS_BLOCKED"
    CORRUPT_BLOCKED = "CORRUPT_BLOCKED"


class LegalPractitionerMatterAccessCurrentnessError(ValueError):
    """Expose a bounded input failure without sensitive identifiers."""

    def __init__(self, code: str) -> None:
        """Record one stable error code without rejected values."""
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class LegalPractitionerMatterAccessCurrentness:
    """Represent a pure evidence conclusion with no authorization semantics."""

    tenant_id: str
    case_matter_id: str
    practitioner_principal_id: str
    evaluation_time: datetime
    state: LegalPractitionerMatterAccessCurrentnessState
    decisive_fingerprints: tuple[str, ...] = ()
    evidence_fingerprints: tuple[str, ...] = ()

    @property
    def permits_access(self) -> bool:
        """Refuse to infer operational access from documentary evidence."""
        return False


def _identity(name: str, value: object, *, tenant: bool = False) -> str:
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or len(value) > (160 if tenant else 200)
        or any(ord(character) < 33 or ord(character) == 127 for character in value)
    ):
        raise LegalPractitionerMatterAccessCurrentnessError(
            "P9_R94_" + name.upper() + "_INVALID"
        )
    if tenant and value.casefold() in {"default", "global", "root", "*"}:
        raise LegalPractitionerMatterAccessCurrentnessError(
            "P9_R94_TENANT_ID_INVALID"
        )
    return value


def _moment(value: object) -> datetime:
    if (
        type(value) is not datetime
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalPractitionerMatterAccessCurrentnessError(
            "P9_R94_EVALUATION_TIME_INVALID"
        )
    return value.astimezone(timezone.utc)


def _result(
    tenant: str,
    matter: str,
    practitioner: str,
    at: datetime,
    state: LegalPractitionerMatterAccessCurrentnessState,
    decisive: tuple[str, ...] = (),
    history: tuple[str, ...] = (),
) -> LegalPractitionerMatterAccessCurrentness:
    return LegalPractitionerMatterAccessCurrentness(
        tenant_id=tenant,
        case_matter_id=matter,
        practitioner_principal_id=practitioner,
        evaluation_time=at,
        state=state,
        decisive_fingerprints=tuple(sorted(decisive)),
        evidence_fingerprints=tuple(sorted(history)),
    )


def project_legal_practitioner_matter_access_currentness(
    *,
    tenant_id: str,
    case_matter_id: str,
    practitioner_principal_id: str,
    evaluation_time: datetime,
    evidence: Iterable[LegalPractitionerMatterAccessEvidence],
) -> LegalPractitionerMatterAccessCurrentness:
    """Project verified documentary history without granting access.

    Every record, including future evidence, is codec-reverified under the
    exact tenant/matter/practitioner scope. Revision families are complete and
    monotonic; a successor supersedes its predecessor from its effective time,
    and expiry never resurrects the predecessor. Any applicable DENY blocks.

    Raises:
        LegalPractitionerMatterAccessCurrentnessError: For invalid query scope
            or evaluation time. Evidence corruption returns CORRUPT_BLOCKED.
    """
    tenant = _identity("tenant_id", tenant_id, tenant=True)
    matter = _identity("case_matter_id", case_matter_id)
    practitioner = _identity("practitioner_principal_id", practitioner_principal_id)
    at = _moment(evaluation_time)
    corrupt = LegalPractitionerMatterAccessCurrentnessState.CORRUPT_BLOCKED

    try:
        supplied = tuple(evidence)
    except Exception:
        return _result(tenant, matter, practitioner, at, corrupt)

    by_fingerprint: dict[str, LegalPractitionerMatterAccessEvidence] = {}
    families: dict[str, dict[int, LegalPractitionerMatterAccessEvidence]] = {}

    try:
        for unverified in supplied:
            if type(unverified) is not LegalPractitionerMatterAccessEvidence:
                return _result(tenant, matter, practitioner, at, corrupt)
            item = verify_practitioner_matter_access(unverified)
            if (
                item.tenant_id != tenant
                or item.case_matter_id != matter
                or item.practitioner_principal_id != practitioner
            ):
                return _result(tenant, matter, practitioner, at, corrupt)

            previous = by_fingerprint.get(item.fingerprint)
            if previous is not None:
                if (
                    encode_practitioner_matter_access(previous)
                    != encode_practitioner_matter_access(item)
                ):
                    return _result(tenant, matter, practitioner, at, corrupt)
                continue

            family = families.setdefault(item.access_evidence_id, {})
            prior_revision = family.get(item.revision)
            if prior_revision is not None:
                if prior_revision.fingerprint != item.fingerprint:
                    return _result(tenant, matter, practitioner, at, corrupt)
                continue

            family[item.revision] = item
            by_fingerprint[item.fingerprint] = item

        for family in families.values():
            previous_item: LegalPractitionerMatterAccessEvidence | None = None
            for revision in sorted(family):
                item = family[revision]
                expected = 1 if previous_item is None else previous_item.revision + 1
                if revision != expected:
                    return _result(tenant, matter, practitioner, at, corrupt)
                if previous_item is None:
                    if item.supersedes_fingerprint is not None:
                        return _result(tenant, matter, practitioner, at, corrupt)
                elif (
                    item.supersedes_fingerprint != previous_item.fingerprint
                    or item.effective_from <= previous_item.effective_from
                ):
                    return _result(tenant, matter, practitioner, at, corrupt)
                previous_item = item
    except Exception:
        return _result(tenant, matter, practitioner, at, corrupt)

    active: list[LegalPractitionerMatterAccessEvidence] = []
    for family in families.values():
        prior = [item for item in family.values() if item.effective_from <= at]
        if not prior:
            continue
        selected = max(prior, key=lambda item: item.revision)
        if selected.effective_until is None or at < selected.effective_until:
            active.append(selected)

    history = tuple(by_fingerprint)
    if not active:
        return _result(
            tenant,
            matter,
            practitioner,
            at,
            LegalPractitionerMatterAccessCurrentnessState.NO_APPLICABLE_EVIDENCE,
            history=history,
        )

    denied = [
        item
        for item in active
        if item.decision is LegalPractitionerMatterAccessDecision.DENY
    ]
    if denied:
        return _result(
            tenant,
            matter,
            practitioner,
            at,
            LegalPractitionerMatterAccessCurrentnessState.DENY_BLOCKED,
            tuple(item.fingerprint for item in denied),
            history,
        )

    latest_time = max(item.effective_from for item in active)
    simultaneous = [item for item in active if item.effective_from == latest_time]
    if len(simultaneous) > 1:
        return _result(
            tenant,
            matter,
            practitioner,
            at,
            LegalPractitionerMatterAccessCurrentnessState.AMBIGUOUS_BLOCKED,
            tuple(item.fingerprint for item in simultaneous),
            history,
        )

    return _result(
        tenant,
        matter,
        practitioner,
        at,
        LegalPractitionerMatterAccessCurrentnessState.ALLOW_UNVERIFIED,
        (simultaneous[0].fingerprint,),
        history,
    )


__all__ = [
    "VERSION",
    "LegalPractitionerMatterAccessCurrentnessState",
    "LegalPractitionerMatterAccessCurrentnessError",
    "LegalPractitionerMatterAccessCurrentness",
    "project_legal_practitioner_matter_access_currentness",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_practitioner_matter_access_currentness.py
# VERSION: v2.0.0-P47-R33-PRACTITIONER-ACCESS-CURRENTNESS-SERVICE
# AUTHORITY BOUNDARY: DOCUMENTARY POLICY PROJECTION ONLY
# TENANT POSTURE: EXACT-SCOPE CODEC-VERIFIED HISTORY
# FAIL-CLOSED POSTURE: CORRUPT, AMBIGUOUS AND DENY EVIDENCE BLOCKS
# AFFIRMATIVE ACCESS / ISSUER / ETHICAL-WALL / APPROVAL AUTHORITY: NONE
# REASSIGNMENT / FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
