"""TITLE: WILSY OS Legal Work Assignment Domain.

VERSION: v1.0.1-G7F-R3-LEGAL-WORK-ASSIGNMENT

AUTHORITY:
    Wilsy OS Core Governance / Python EOS Legal Operations.

EPITOME:
    Preserve one immutable historical assignment of one Legal work item to one
    exact principal without granting permission, professional authority,
    matter authority, supervision authority or financial authority.

COLLABORATION / OWNERSHIP:
    LegalWorkItem owns operational work truth.
    This domain owns historical assignment evidence only.
    Future registry owns persistence/history/current derivation.
    Future orchestration must revalidate tenant membership, operating-model
    activation, work-item scope and current IAM before recording assignment.
    Actual Legal commands must re-authorize again at command time.
    Future supervision is a separate domain.

TENANT BOUNDARY:
    Exact non-pseudo tenant_id, case_matter_id and principal identity required.

ASSIGNMENT BOUNDARY:
    Assignment means responsibility for operational work only.
    It does not mean the principal is permitted to execute the underlying
    Legal operation.

CURRENTNESS BOUNDARY:
    No assignment is self-declared current. Current assignment must later be
    derived from immutable history.

REASSIGNMENT BOUNDARY:
    supersedes_assignment_id records explicit assignment lineage. It cannot
    equal assignment_id.

SUPERVISION BOUNDARY:
    No supervisor identity or supervision authority exists in this artifact.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_512
import hmac
import json
from typing import Final, NoReturn


VERSION: Final[str] = "v1.0.1-G7F-R3-LEGAL-WORK-ASSIGNMENT"
SCHEMA: Final[str] = "WILSY-LEGAL-WORK-ASSIGNMENT/V1"


class LegalWorkAssignmentError(ValueError):
    """Stable fail-closed Legal assignment validation failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise LegalWorkAssignmentError(code)


def _text(name: str, value: object, *, limit: int = 200) -> str:
    if not isinstance(value, str):
        _fail(f"G7F_R3_{name.upper()}_INVALID")

    normalized = value.strip()

    if (
        not normalized
        or normalized != value
        or len(normalized) > limit
    ):
        _fail(f"G7F_R3_{name.upper()}_INVALID")

    return normalized


def _tenant(value: object) -> str:
    tenant = _text("tenant_id", value, limit=160)

    if tenant.casefold() in {"default", "global", "root", "*"}:
        _fail("G7F_R3_TENANT_REQUIRED")

    return tenant


def _timestamp(name: str, value: object) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(f"G7F_R3_{name.upper()}_INVALID")

    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class LegalWorkAssignment:
    """One immutable historical principal assignment for one Legal work item."""

    assignment_id: str
    tenant_id: str
    case_matter_id: str
    work_item_id: str

    assignee_principal_id: str
    assigned_by_principal_id: str
    assigned_at: datetime

    assignment_reason_reference: str
    authorization_evidence_reference: str

    supersedes_assignment_id: str | None = None

    schema: str = SCHEMA
    assignment_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        assignment_id = _text(
            "assignment_id",
            self.assignment_id,
            limit=160,
        )
        tenant_id = _tenant(self.tenant_id)
        case_matter_id = _text(
            "case_matter_id",
            self.case_matter_id,
            limit=160,
        )
        work_item_id = _text(
            "work_item_id",
            self.work_item_id,
            limit=160,
        )

        assignee = _text(
            "assignee_principal_id",
            self.assignee_principal_id,
            limit=160,
        )
        assigned_by = _text(
            "assigned_by_principal_id",
            self.assigned_by_principal_id,
            limit=160,
        )
        assigned_at = _timestamp(
            "assigned_at",
            self.assigned_at,
        )

        reason = _text(
            "assignment_reason_reference",
            self.assignment_reason_reference,
            limit=320,
        )
        authorization_reference = _text(
            "authorization_evidence_reference",
            self.authorization_evidence_reference,
            limit=320,
        )

        supersedes = self.supersedes_assignment_id

        if supersedes is not None:
            supersedes = _text(
                "supersedes_assignment_id",
                supersedes,
                limit=160,
            )

            if supersedes == assignment_id:
                _fail("G7F_R3_SELF_SUPERSESSION_INVALID")

        if self.schema != SCHEMA or self.assignment_version != VERSION:
            _fail("G7F_R3_IDENTITY_INVALID")

        object.__setattr__(
            self,
            "assignment_id",
            assignment_id,
        )
        object.__setattr__(
            self,
            "tenant_id",
            tenant_id,
        )
        object.__setattr__(
            self,
            "case_matter_id",
            case_matter_id,
        )
        object.__setattr__(
            self,
            "work_item_id",
            work_item_id,
        )
        object.__setattr__(
            self,
            "assignee_principal_id",
            assignee,
        )
        object.__setattr__(
            self,
            "assigned_by_principal_id",
            assigned_by,
        )
        object.__setattr__(
            self,
            "assigned_at",
            assigned_at,
        )
        object.__setattr__(
            self,
            "assignment_reason_reference",
            reason,
        )
        object.__setattr__(
            self,
            "authorization_evidence_reference",
            authorization_reference,
        )
        object.__setattr__(
            self,
            "supersedes_assignment_id",
            supersedes,
        )

        digest = self._compute_fingerprint()

        if self.fingerprint:
            supplied = _text(
                "fingerprint",
                self.fingerprint,
                limit=128,
            )

            if (
                len(supplied) != 128
                or supplied.lower() != supplied
            ):
                _fail("G7F_R3_FINGERPRINT_INVALID")

            try:
                int(supplied, 16)
            except ValueError as error:
                raise LegalWorkAssignmentError(
                    "G7F_R3_FINGERPRINT_INVALID"
                ) from error

            if not hmac.compare_digest(
                supplied,
                digest,
            ):
                _fail("G7F_R3_FINGERPRINT_MISMATCH")

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    def semantic_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "assignment_version": self.assignment_version,
            "assignment_id": self.assignment_id,
            "tenant_id": self.tenant_id,
            "case_matter_id": self.case_matter_id,
            "work_item_id": self.work_item_id,
            "assignee_principal_id":
                self.assignee_principal_id,
            "assigned_by_principal_id":
                self.assigned_by_principal_id,
            "assigned_at": self.assigned_at.isoformat(),
            "assignment_reason_reference":
                self.assignment_reason_reference,
            "authorization_evidence_reference":
                self.authorization_evidence_reference,
            "supersedes_assignment_id":
                self.supersedes_assignment_id,
        }

    def _compute_fingerprint(self) -> str:
        canonical = json.dumps(
            self.semantic_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        return sha3_512(
            canonical.encode("utf-8")
        ).hexdigest()

    def to_dict(self) -> dict[str, object]:
        return {
            **self.semantic_dict(),
            "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        value: object,
    ) -> "LegalWorkAssignment":
        if not isinstance(value, dict):
            _fail("G7F_R3_PAYLOAD_INVALID")

        required = {
            "schema",
            "assignment_version",
            "assignment_id",
            "tenant_id",
            "case_matter_id",
            "work_item_id",
            "assignee_principal_id",
            "assigned_by_principal_id",
            "assigned_at",
            "assignment_reason_reference",
            "authorization_evidence_reference",
            "supersedes_assignment_id",
            "fingerprint",
        }

        if set(value) != required:
            _fail("G7F_R3_PAYLOAD_SCHEMA_INVALID")

        raw_time = value["assigned_at"]

        if not isinstance(raw_time, str):
            _fail("G7F_R3_ASSIGNED_AT_INVALID")

        try:
            assigned_at = datetime.fromisoformat(raw_time)
        except ValueError as error:
            raise LegalWorkAssignmentError(
                "G7F_R3_ASSIGNED_AT_INVALID"
            ) from error

        return cls(
            schema=value["schema"],
            assignment_version=value[
                "assignment_version"
            ],
            assignment_id=value["assignment_id"],
            tenant_id=value["tenant_id"],
            case_matter_id=value["case_matter_id"],
            work_item_id=value["work_item_id"],
            assignee_principal_id=value[
                "assignee_principal_id"
            ],
            assigned_by_principal_id=value[
                "assigned_by_principal_id"
            ],
            assigned_at=assigned_at,
            assignment_reason_reference=value[
                "assignment_reason_reference"
            ],
            authorization_evidence_reference=value[
                "authorization_evidence_reference"
            ],
            supersedes_assignment_id=value[
                "supersedes_assignment_id"
            ],
            fingerprint=value["fingerprint"],
        )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalWorkAssignment",
    "LegalWorkAssignmentError",
]

# ARTIFACT: legal_work_assignment.py
# VERSION: v1.0.1-G7F-R3-LEGAL-WORK-ASSIGNMENT
# AUTHORITY BOUNDARY: historical operational assignment evidence only
# ASSIGNMENT NOT AUTHORIZATION: YES
# SUPERVISION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# TENANT POSTURE: exact tenant correlation; cross-tenant inference prohibited
# FAIL-CLOSED POSTURE: malformed, incomplete, or divergent evidence rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
