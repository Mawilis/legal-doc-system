"""TITLE: WILSY OS Ethical Wall Policy Evidence Domain.
VERSION: v1.0.0-G76-IMMUTABLE-DENY-FIRST-WALL-POLICY
AUTHORITY: Immutable matter-scoped wall-policy evidence; not institutional approval.
EPITOME: Defines revisioned practitioner restriction and membership evidence,
ratification provenance, expiry and revocation with deny-first pure evaluation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_work_ethical_wall_policy.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering; future
registries own persistence and future services must verify institutional truth.
CERTIFICATION / UPDATE DATE: 2026-10-21.
CHANGELOG: 2026-10-21 v1.0.0 introduces immutable revisions, SHA3-512
integrity, deterministic lineage and non-authorizing deny-first evaluation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque identities and fingerprints; no content.
TENANT BOUNDARY: Exact tenant and matter; cross-scope history is corruption.
AUTHORITY BOUNDARY: Recorded ratification is evidence, never runtime authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import json
import re
from typing import Final, Iterable

VERSION: Final[str] = "v1.0.0-G76-IMMUTABLE-DENY-FIRST-WALL-POLICY"
SCHEMA: Final[str] = "WILSY-LEGAL-ETHICAL-WALL-POLICY/V1"
_ID: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,199}\Z")
_HEX: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{128}\Z")


class EthicalWallPolicyError(ValueError):
    """Expose one stable content-free policy validation code."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class EthicalWallPolicyStatus(StrEnum):
    """Closed immutable revision status."""

    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class InstitutionalRatificationState(StrEnum):
    """Recorded ratification evidence; never self-verifying approval."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVOKED = "REVOKED"


class EthicalWallAccessState(StrEnum):
    """Deny-first evidence outcomes; positive evidence remains unverified."""

    DENIED_NO_POLICY = "DENIED_NO_POLICY"
    DENIED_ABSENT = "DENIED_ABSENT"
    DENIED_RESTRICTED = "DENIED_RESTRICTED"
    DENIED_UNRATIFIED = "DENIED_UNRATIFIED"
    DENIED_REJECTED = "DENIED_REJECTED"
    DENIED_REVOKED = "DENIED_REVOKED"
    DENIED_EXPIRED = "DENIED_EXPIRED"
    DENIED_CORRUPT = "DENIED_CORRUPT"
    ALLOW_RECORDED_UNVERIFIED = "ALLOW_RECORDED_UNVERIFIED"


def _id(name: str, value: object) -> str:
    if type(value) is not str or _ID.fullmatch(value) is None:
        raise EthicalWallPolicyError(name.upper() + "_INVALID")
    if name == "tenant_id" and value.casefold() in {"default", "global", "root", "*"}:
        raise EthicalWallPolicyError("TENANT_ID_INVALID")
    return value


def _fingerprint(name: str, value: object) -> str:
    if type(value) is not str or _HEX.fullmatch(value) is None:
        raise EthicalWallPolicyError(name.upper() + "_INVALID")
    return value


def _time(name: str, value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise EthicalWallPolicyError(name.upper() + "_INVALID")
    result = value.astimezone(timezone.utc)
    if result.microsecond or result != value:
        raise EthicalWallPolicyError(name.upper() + "_NONCANONICAL")
    return result


def _ids(name: str, values: object) -> tuple[str, ...]:
    if type(values) is not tuple:
        raise EthicalWallPolicyError(name.upper() + "_INVALID")
    result = tuple(_id(name, item) for item in values)
    if result != tuple(sorted(set(result))):
        raise EthicalWallPolicyError(name.upper() + "_NONCANONICAL")
    return result


def _fingerprints(name: str, values: object) -> tuple[str, ...]:
    if type(values) is not tuple:
        raise EthicalWallPolicyError(name.upper() + "_INVALID")
    result = tuple(_fingerprint(name, item) for item in values)
    if not result or result != tuple(sorted(set(result))):
        raise EthicalWallPolicyError(name.upper() + "_NONCANONICAL")
    return result


@dataclass(frozen=True, slots=True)
class EthicalWallPolicyRevision:
    """One immutable policy revision with no power to approve itself."""

    policy_id: str
    revision: int
    predecessor_fingerprint: str | None
    tenant_id: str
    case_matter_id: str
    protected_subject_fingerprints: tuple[str, ...]
    restricted_principal_ids: tuple[str, ...]
    permitted_principal_ids: tuple[str, ...]
    status: EthicalWallPolicyStatus | str
    effective_from: datetime
    effective_until: datetime
    source_evidence_reference: str
    source_evidence_fingerprint: str
    administrator_principal_id: str
    administrator_authorization_reference: str
    administrator_authorization_fingerprint: str
    ratification_state: InstitutionalRatificationState | str
    ratification_reference: str | None
    ratification_fingerprint: str | None
    schema: str = SCHEMA
    policy_version: str = VERSION
    fingerprint: str = field(init=False)

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or self.policy_version != VERSION:
            raise EthicalWallPolicyError("IDENTITY_INVALID")
        for name in (
            "policy_id", "tenant_id", "case_matter_id", "source_evidence_reference",
            "administrator_principal_id", "administrator_authorization_reference",
        ):
            object.__setattr__(self, name, _id(name, getattr(self, name)))
        if type(self.revision) is not int or self.revision < 1:
            raise EthicalWallPolicyError("REVISION_INVALID")
        predecessor = self.predecessor_fingerprint
        if self.revision == 1:
            if predecessor is not None:
                raise EthicalWallPolicyError("ROOT_PREDECESSOR_FORBIDDEN")
        else:
            predecessor = _fingerprint("predecessor_fingerprint", predecessor)
        object.__setattr__(self, "predecessor_fingerprint", predecessor)
        protected = _fingerprints(
            "protected_subject_fingerprints", self.protected_subject_fingerprints
        )
        restricted = _ids("restricted_principal_ids", self.restricted_principal_ids)
        permitted = _ids("permitted_principal_ids", self.permitted_principal_ids)
        # Overlap is retained so an explicit restriction can deterministically
        # override a recorded membership grant during evaluation.
        object.__setattr__(self, "protected_subject_fingerprints", protected)
        object.__setattr__(self, "restricted_principal_ids", restricted)
        object.__setattr__(self, "permitted_principal_ids", permitted)
        try:
            status = EthicalWallPolicyStatus(self.status)
            ratification = InstitutionalRatificationState(self.ratification_state)
        except (TypeError, ValueError) as error:
            raise EthicalWallPolicyError("STATE_INVALID") from error
        if status is EthicalWallPolicyStatus.REVOKED and ratification is not InstitutionalRatificationState.REVOKED:
            raise EthicalWallPolicyError("REVOCATION_RATIFICATION_REQUIRED")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "ratification_state", ratification)
        start, end = _time("effective_from", self.effective_from), _time(
            "effective_until", self.effective_until
        )
        if end <= start:
            raise EthicalWallPolicyError("WINDOW_INVALID")
        object.__setattr__(self, "effective_from", start)
        object.__setattr__(self, "effective_until", end)
        for name in ("source_evidence_fingerprint", "administrator_authorization_fingerprint"):
            object.__setattr__(self, name, _fingerprint(name, getattr(self, name)))
        reference, digest = self.ratification_reference, self.ratification_fingerprint
        if ratification is InstitutionalRatificationState.PENDING:
            if reference is not None or digest is not None:
                raise EthicalWallPolicyError("RATIFICATION_EVIDENCE_FORBIDDEN")
        else:
            if reference is None or digest is None:
                raise EthicalWallPolicyError("RATIFICATION_EVIDENCE_REQUIRED")
            object.__setattr__(self, "ratification_reference", _id("ratification_reference", reference))
            object.__setattr__(self, "ratification_fingerprint", _fingerprint("ratification_fingerprint", digest))
        material = {
            name: (getattr(self, name).value if isinstance(getattr(self, name), StrEnum)
                   else getattr(self, name).isoformat() if isinstance(getattr(self, name), datetime)
                   else getattr(self, name))
            for name in self.__dataclass_fields__ if name != "fingerprint"
        }
        raw = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
        object.__setattr__(self, "fingerprint", sha3_512(raw).hexdigest())

    @property
    def permits_operational_access(self) -> bool:
        """Never treat a stored policy revision as runtime authorization."""
        return False


@dataclass(frozen=True, slots=True)
class EthicalWallAccessDecision:
    """Pure evidence evaluation; point-of-read authorization remains separate."""

    tenant_id: str
    case_matter_id: str
    practitioner_principal_id: str
    evaluation_time: datetime
    state: EthicalWallAccessState
    decisive_policy_fingerprint: str | None = None

    @property
    def permits_operational_access(self) -> bool:
        """Refuse operational access even for recorded positive evidence."""
        return False


def evaluate_ethical_wall_access(
    *, tenant_id: str, case_matter_id: str, practitioner_principal_id: str,
    evaluation_time: datetime, revisions: Iterable[EthicalWallPolicyRevision],
) -> EthicalWallAccessDecision:
    """Derive deny-first recorded policy state from complete immutable history."""
    tenant, matter = _id("tenant_id", tenant_id), _id("case_matter_id", case_matter_id)
    principal, at = _id("practitioner_principal_id", practitioner_principal_id), _time(
        "evaluation_time", evaluation_time
    )

    def decision(state: EthicalWallAccessState,
                 fingerprint: str | None = None) -> EthicalWallAccessDecision:
        return EthicalWallAccessDecision(tenant, matter, principal, at, state, fingerprint)

    try:
        history = tuple(revisions)
        if not history:
            return decision(EthicalWallAccessState.DENIED_NO_POLICY)
        verified: list[EthicalWallPolicyRevision] = []
        for item in history:
            if type(item) is not EthicalWallPolicyRevision or replace(item).fingerprint != item.fingerprint:
                return decision(EthicalWallAccessState.DENIED_CORRUPT)
            if item.tenant_id != tenant or item.case_matter_id != matter:
                return decision(EthicalWallAccessState.DENIED_CORRUPT)
            verified.append(item)
        verified.sort(key=lambda item: item.revision)
        if verified[0].revision != 1 or len({item.revision for item in verified}) != len(verified):
            return decision(EthicalWallAccessState.DENIED_CORRUPT)
        for previous, current in zip(verified, verified[1:]):
            if (current.policy_id != previous.policy_id
                    or current.revision != previous.revision + 1
                    or current.predecessor_fingerprint != previous.fingerprint
                    or current.effective_from <= previous.effective_from
                    or previous.status is EthicalWallPolicyStatus.REVOKED):
                return decision(EthicalWallAccessState.DENIED_CORRUPT)
        applicable = [item for item in verified if item.effective_from <= at]
        if not applicable:
            return decision(EthicalWallAccessState.DENIED_NO_POLICY)
        current = applicable[-1]
        digest = current.fingerprint
        if current.status is EthicalWallPolicyStatus.REVOKED or current.ratification_state is InstitutionalRatificationState.REVOKED:
            return decision(EthicalWallAccessState.DENIED_REVOKED, digest)
        if at >= current.effective_until:
            return decision(EthicalWallAccessState.DENIED_EXPIRED, digest)
        if principal in current.restricted_principal_ids:
            return decision(EthicalWallAccessState.DENIED_RESTRICTED, digest)
        if principal not in current.permitted_principal_ids:
            return decision(EthicalWallAccessState.DENIED_ABSENT, digest)
        if current.ratification_state is InstitutionalRatificationState.REJECTED:
            return decision(EthicalWallAccessState.DENIED_REJECTED, digest)
        if current.ratification_state is not InstitutionalRatificationState.APPROVED:
            return decision(EthicalWallAccessState.DENIED_UNRATIFIED, digest)
        return decision(EthicalWallAccessState.ALLOW_RECORDED_UNVERIFIED, digest)
    except Exception:
        return decision(EthicalWallAccessState.DENIED_CORRUPT)


__all__ = [
    "VERSION", "SCHEMA", "EthicalWallPolicyError", "EthicalWallPolicyStatus",
    "InstitutionalRatificationState", "EthicalWallAccessState",
    "EthicalWallPolicyRevision", "EthicalWallAccessDecision",
    "evaluate_ethical_wall_access",
]

# ARTIFACT: legal_work_ethical_wall_policy.py
# VERSION: v1.0.0-G76-IMMUTABLE-DENY-FIRST-WALL-POLICY
# AUTHORITY BOUNDARY: immutable policy evidence and pure deny-first evaluation only
# TENANT POSTURE: exact tenant and matter; cross-scope history corrupt-blocked
# FAIL-CLOSED POSTURE: absence, restriction, pending, rejection, revocation, expiry and corruption deny
# OPERATIONAL ACCESS / INSTITUTIONAL APPROVAL / FINANCIAL AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
