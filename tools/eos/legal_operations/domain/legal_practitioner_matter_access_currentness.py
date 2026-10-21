"""TITLE: WILSY P9 Pure Practitioner Matter Access Currentness.
VERSION: v1.0.0-P9-R94-PRACTITIONER-ACCESS-CURRENTNESS-GREEN
AUTHORITY: Python/EOS Legal Operations documentary projection only.
EPITOME: Exact-scope immutable history, validated revision chains,
    deterministic effective-time selection, explicit-deny precedence,
    and corruption/ambiguity fail-closed handling.
ABSOLUTE CANONICAL PATH:
    tools/eos/legal_operations/domain/legal_practitioner_matter_access_currentness.py
COLLABORATION / OWNERSHIP: WILSY OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 v1.0.0-P9-R94-PRACTITIONER-ACCESS-CURRENTNESS-GREEN
    Add pure evidence projection against frozen P9-R93 RED contracts.
TENANT BOUNDARY: Exact tenant, case matter and practitioner.
AUTHORITY BOUNDARY: ALLOW_UNVERIFIED is not permission or issuer
    authorization. No grants, ethical-wall clearance, professional
    status, supervisor approval or reassignment execution.
TRANSACTION BOUNDARY: None; pure function, no persistence or I/O.
FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Iterable, Final

from tools.eos.legal_operations.domain.legal_practitioner_matter_access import (
    LegalPractitionerMatterAccessDecision,
    LegalPractitionerMatterAccessEvidence,
)


VERSION: Final[str] = "v1.0.0-P9-R94-PRACTITIONER-ACCESS-CURRENTNESS-GREEN"


class LegalPractitionerMatterAccessCurrentnessState(StrEnum):
    """Documentary findings; none is an access authorization."""

    NO_APPLICABLE_EVIDENCE = "NO_APPLICABLE_EVIDENCE"
    ALLOW_UNVERIFIED = "ALLOW_UNVERIFIED"
    DENY_BLOCKED = "DENY_BLOCKED"
    AMBIGUOUS_BLOCKED = "AMBIGUOUS_BLOCKED"
    CORRUPT_BLOCKED = "CORRUPT_BLOCKED"


class LegalPractitionerMatterAccessCurrentnessError(ValueError):
    """Bounded input failure with no sensitive identifiers."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class LegalPractitionerMatterAccessCurrentness:
    """Pure evidence conclusion; never operational access permission."""

    tenant_id: str
    case_matter_id: str
    practitioner_principal_id: str
    evaluation_time: datetime
    state: LegalPractitionerMatterAccessCurrentnessState
    decisive_fingerprints: tuple[str, ...] = ()
    evidence_fingerprints: tuple[str, ...] = ()

    @property
    def permits_access(self) -> bool:
        """Never infer access from unverified documentary evidence."""
        return False


def _identity(name: str, value: object, *, tenant: bool = False) -> str:
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or len(value) > (160 if tenant else 200)
        or any(ord(ch) < 33 or ord(ch) == 127 for ch in value)
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


from tools.eos.legal_operations.service.legal_practitioner_matter_access_codec import (
    encode_practitioner_matter_access,
    verify_practitioner_matter_access,
)


def project_legal_practitioner_matter_access_currentness(
    *,
    tenant_id: str,
    case_matter_id: str,
    practitioner_principal_id: str,
    evaluation_time: datetime,
    evidence: Iterable[LegalPractitionerMatterAccessEvidence],
) -> LegalPractitionerMatterAccessCurrentness:
    """Project documentary policy evidence without trusting issuer authority.

    All supplied records must be exact-scope and valid, including future
    evidence. Revision families are checked completely before evaluation.
    A successor supersedes its predecessor from its effective instant;
    expiration of the successor never resurrects its predecessor.
    Independent applicable explicit DENY evidence blocks ALLOW.
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
        for item in supplied:
            if type(item) is not LegalPractitionerMatterAccessEvidence:
                return _result(tenant, matter, practitioner, at, corrupt)

            # Revalidate even frozen objects, which can be forged by bypass.
            verify_practitioner_matter_access(item)

            if (
                item.tenant_id != tenant
                or item.case_matter_id != matter
                or item.practitioner_principal_id != practitioner
            ):
                return _result(tenant, matter, practitioner, at, corrupt)

            previous = by_fingerprint.get(item.fingerprint)
            if previous is not None:
                if encode_practitioner_matter_access(previous) != encode_practitioner_matter_access(item):
                    return _result(tenant, matter, practitioner, at, corrupt)
                continue

            family = families.setdefault(item.access_evidence_id, {})
            prior_revision = family.get(item.revision)
            if prior_revision is not None:
                # Divergent same-revision claims are corruption, not a
                # competition resolved by insertion order.
                if prior_revision.fingerprint != item.fingerprint:
                    return _result(tenant, matter, practitioner, at, corrupt)
                continue

            family[item.revision] = item
            by_fingerprint[item.fingerprint] = item

        # Validate full immutable history, not merely today's candidates.
        for family in families.values():
            previous_item: LegalPractitionerMatterAccessEvidence | None = None
            for revision in sorted(family):
                item = family[revision]
                if revision != (1 if previous_item is None else previous_item.revision + 1):
                    return _result(tenant, matter, practitioner, at, corrupt)

                if previous_item is None:
                    if item.supersedes_fingerprint is not None:
                        return _result(tenant, matter, practitioner, at, corrupt)
                else:
                    if (
                        item.supersedes_fingerprint != previous_item.fingerprint
                        or item.effective_from <= previous_item.effective_from
                    ):
                        return _result(tenant, matter, practitioner, at, corrupt)
                previous_item = item

    except Exception:
        return _result(tenant, matter, practitioner, at, corrupt)

    # Each immutable family contributes at most one effective current
    # revision; an expired successor cannot reactivate a prior revision.
    active: list[LegalPractitionerMatterAccessEvidence] = []
    for family in families.values():
        prior = [
            item for item in family.values()
            if item.effective_from <= at
        ]
        if not prior:
            continue
        selected = max(prior, key=lambda item: item.revision)
        if selected.effective_until is None or at < selected.effective_until:
            active.append(selected)

    history = tuple(by_fingerprint)
    if not active:
        return _result(
            tenant, matter, practitioner, at,
            LegalPractitionerMatterAccessCurrentnessState.NO_APPLICABLE_EVIDENCE,
            history=history,
        )

    denied = [
        item for item in active
        if item.decision is LegalPractitionerMatterAccessDecision.DENY
    ]
    if denied:
        return _result(
            tenant, matter, practitioner, at,
            LegalPractitionerMatterAccessCurrentnessState.DENY_BLOCKED,
            tuple(item.fingerprint for item in denied),
            history,
        )

    # Simultaneous independent ALLOW claims have no certified priority.
    latest_time = max(item.effective_from for item in active)
    simultaneous = [
        item for item in active if item.effective_from == latest_time
    ]
    if len(simultaneous) > 1:
        return _result(
            tenant, matter, practitioner, at,
            LegalPractitionerMatterAccessCurrentnessState.AMBIGUOUS_BLOCKED,
            tuple(item.fingerprint for item in simultaneous),
            history,
        )

    return _result(
        tenant, matter, practitioner, at,
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
# VERSION: v1.0.0-P9-R94-PRACTITIONER-ACCESS-CURRENTNESS-GREEN
# AUTHORITY BOUNDARY: documentary policy projection only
# AFFIRMATIVE ACCESS / ISSUER AUTHORIZATION: NONE
# ETHICAL WALL / LICENSING / SUPERVISOR APPROVAL: NONE
# REASSIGNMENT / FINANCIAL EXECUTION: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
