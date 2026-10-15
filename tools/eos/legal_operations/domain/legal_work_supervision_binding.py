"""TITLE: WILSY OS Legal Work Supervision Binding Domain.

VERSION: v1.0.1-G7F-R4-LEGAL-WORK-SUPERVISION-BINDING

AUTHORITY:
    Wilsy OS Core Governance / Python EOS Legal Operations.

EPITOME:
    Preserve one immutable supervision arrangement between one supervisee and
    one supervisor for either one Legal matter or one Legal work item.

    This value records operational supervision configuration only. It does not
    grant IAM permission, professional qualification, practising authority,
    matter authority, assignment authority, legal-event authority, billing,
    trust, payment, settlement or financial-execution authority.

COLLABORATION / OWNERSHIP:
    CaseMatter remains canonical matter truth.
    LegalWorkItem remains canonical operational work-item truth.
    LegalWorkAssignment remains historical work-assignment evidence.
    Professional qualification and regulatory appointment remain separately
    evidenced.
    Future orchestration must revalidate tenant membership, operating model,
    principal facts, qualification/appointment where applicable, work/matter
    scope and current IAM.
    Actual Legal commands must authorize again at execution time.

SUPERVISION MODEL:
    MATTER scope supervises Legal work across one matter.
    WORK_ITEM scope supervises one specific work item.

    Control level expresses operational review posture:
      OVERSIGHT              - ongoing supervision without mandatory pre-action
                               approval encoded by this value.
      REVIEW_REQUIRED        - work must enter a supervisor review process.
      PRIOR_APPROVAL_REQUIRED - governed action must receive supervisor approval
                                before the supervised workflow may proceed.

    These are workflow-control facts only and never substitute for underlying
    Legal-domain authority.

CURRENTNESS:
    No binding self-declares current. Effective chronology plus immutable
    supersession history will later be interpreted by certified orchestration
    and persistence.

FINANCIAL AUTHORITY:
    None. Kennel EOS remains exclusive financial execution authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import hmac
import json
from typing import Final, NoReturn


VERSION: Final[str] = (
    "v1.0.1-G7F-R4-LEGAL-WORK-SUPERVISION-BINDING"
)
SCHEMA: Final[str] = (
    "WILSY-LEGAL-WORK-SUPERVISION-BINDING/V1"
)


class LegalWorkSupervisionBindingError(ValueError):
    """Stable fail-closed supervision-binding failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalSupervisionScope(StrEnum):
    """Exact operational scope of one supervision arrangement."""

    MATTER = "MATTER"
    WORK_ITEM = "WORK_ITEM"


class LegalSupervisionControlLevel(StrEnum):
    """Operational control posture, never IAM or Legal-event authority."""

    OVERSIGHT = "OVERSIGHT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PRIOR_APPROVAL_REQUIRED = "PRIOR_APPROVAL_REQUIRED"


def _fail(code: str) -> NoReturn:
    raise LegalWorkSupervisionBindingError(code)


def _text(
    name: str,
    value: object,
    *,
    limit: int = 320,
) -> str:
    if not isinstance(value, str):
        _fail(f"G7F_R4_{name.upper()}_INVALID")

    normalized = value.strip()

    if (
        not normalized
        or normalized != value
        or len(normalized) > limit
    ):
        _fail(f"G7F_R4_{name.upper()}_INVALID")

    return normalized


def _tenant(value: object) -> str:
    tenant = _text(
        "tenant_id",
        value,
        limit=160,
    )

    if tenant.casefold() in {
        "default",
        "global",
        "root",
        "*",
    }:
        _fail("G7F_R4_TENANT_REQUIRED")

    return tenant


def _timestamp(
    name: str,
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(f"G7F_R4_{name.upper()}_INVALID")

    return value.astimezone(timezone.utc)


def _optional_text(
    name: str,
    value: object,
    *,
    limit: int = 320,
) -> str | None:
    if value is None:
        return None
    return _text(name, value, limit=limit)


def _optional_timestamp(
    name: str,
    value: object,
) -> datetime | None:
    if value is None:
        return None
    return _timestamp(name, value)


@dataclass(frozen=True, slots=True)
class LegalWorkSupervisionBinding:
    """One immutable operational Legal supervision arrangement."""

    supervision_binding_id: str

    tenant_id: str
    case_matter_id: str

    scope: LegalSupervisionScope | str
    work_item_id: str | None

    supervisee_principal_id: str
    supervisor_principal_id: str

    control_level: LegalSupervisionControlLevel | str

    supervision_plan_reference: str
    supervision_basis_reference: str

    effective_from: datetime
    effective_until: datetime | None = None

    supersedes_supervision_binding_id: str | None = None

    schema: str = SCHEMA
    supervision_binding_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        binding_id = _text(
            "supervision_binding_id",
            self.supervision_binding_id,
            limit=160,
        )

        tenant_id = _tenant(self.tenant_id)

        matter_id = _text(
            "case_matter_id",
            self.case_matter_id,
            limit=160,
        )

        try:
            scope = LegalSupervisionScope(
                self.scope
            )
        except (TypeError, ValueError) as error:
            raise LegalWorkSupervisionBindingError(
                "G7F_R4_SCOPE_INVALID"
            ) from error

        work_item_id = _optional_text(
            "work_item_id",
            self.work_item_id,
            limit=160,
        )

        if (
            scope is LegalSupervisionScope.WORK_ITEM
            and work_item_id is None
        ):
            _fail(
                "G7F_R4_WORK_ITEM_SCOPE_REQUIRES_WORK_ITEM"
            )

        if (
            scope is LegalSupervisionScope.MATTER
            and work_item_id is not None
        ):
            _fail(
                "G7F_R4_MATTER_SCOPE_FORBIDS_WORK_ITEM"
            )

        supervisee = _text(
            "supervisee_principal_id",
            self.supervisee_principal_id,
            limit=160,
        )

        supervisor = _text(
            "supervisor_principal_id",
            self.supervisor_principal_id,
            limit=160,
        )

        if hmac.compare_digest(
            supervisee,
            supervisor,
        ):
            _fail(
                "G7F_R4_SELF_SUPERVISION_INVALID"
            )

        try:
            control_level = (
                LegalSupervisionControlLevel(
                    self.control_level
                )
            )
        except (TypeError, ValueError) as error:
            raise LegalWorkSupervisionBindingError(
                "G7F_R4_CONTROL_LEVEL_INVALID"
            ) from error

        plan_reference = _text(
            "supervision_plan_reference",
            self.supervision_plan_reference,
        )

        basis_reference = _text(
            "supervision_basis_reference",
            self.supervision_basis_reference,
        )

        effective_from = _timestamp(
            "effective_from",
            self.effective_from,
        )

        effective_until = _optional_timestamp(
            "effective_until",
            self.effective_until,
        )

        if (
            effective_until is not None
            and effective_until <= effective_from
        ):
            _fail(
                "G7F_R4_EFFECTIVE_PERIOD_INVALID"
            )

        supersedes = _optional_text(
            "supersedes_supervision_binding_id",
            self.supersedes_supervision_binding_id,
            limit=160,
        )

        if (
            supersedes is not None
            and hmac.compare_digest(
                supersedes,
                binding_id,
            )
        ):
            _fail(
                "G7F_R4_SELF_SUPERSESSION_INVALID"
            )

        if (
            self.schema != SCHEMA
            or self.supervision_binding_version
            != VERSION
        ):
            _fail("G7F_R4_IDENTITY_INVALID")

        object.__setattr__(
            self,
            "supervision_binding_id",
            binding_id,
        )
        object.__setattr__(
            self,
            "tenant_id",
            tenant_id,
        )
        object.__setattr__(
            self,
            "case_matter_id",
            matter_id,
        )
        object.__setattr__(
            self,
            "scope",
            scope,
        )
        object.__setattr__(
            self,
            "work_item_id",
            work_item_id,
        )
        object.__setattr__(
            self,
            "supervisee_principal_id",
            supervisee,
        )
        object.__setattr__(
            self,
            "supervisor_principal_id",
            supervisor,
        )
        object.__setattr__(
            self,
            "control_level",
            control_level,
        )
        object.__setattr__(
            self,
            "supervision_plan_reference",
            plan_reference,
        )
        object.__setattr__(
            self,
            "supervision_basis_reference",
            basis_reference,
        )
        object.__setattr__(
            self,
            "effective_from",
            effective_from,
        )
        object.__setattr__(
            self,
            "effective_until",
            effective_until,
        )
        object.__setattr__(
            self,
            "supersedes_supervision_binding_id",
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
                _fail(
                    "G7F_R4_FINGERPRINT_INVALID"
                )

            try:
                int(supplied, 16)
            except ValueError as error:
                raise LegalWorkSupervisionBindingError(
                    "G7F_R4_FINGERPRINT_INVALID"
                ) from error

            if not hmac.compare_digest(
                supplied,
                digest,
            ):
                _fail(
                    "G7F_R4_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    def semantic_dict(
        self,
    ) -> dict[str, object]:
        return {
            "schema": self.schema,
            "supervision_binding_version":
                self.supervision_binding_version,
            "supervision_binding_id":
                self.supervision_binding_id,
            "tenant_id": self.tenant_id,
            "case_matter_id":
                self.case_matter_id,
            "scope":
                LegalSupervisionScope(
                    self.scope
                ).value,
            "work_item_id":
                self.work_item_id,
            "supervisee_principal_id":
                self.supervisee_principal_id,
            "supervisor_principal_id":
                self.supervisor_principal_id,
            "control_level":
                LegalSupervisionControlLevel(
                    self.control_level
                ).value,
            "supervision_plan_reference":
                self.supervision_plan_reference,
            "supervision_basis_reference":
                self.supervision_basis_reference,
            "effective_from":
                self.effective_from.isoformat(),
            "effective_until": (
                self.effective_until.isoformat()
                if self.effective_until
                is not None
                else None
            ),
            "supersedes_supervision_binding_id":
                self.supersedes_supervision_binding_id,
        }

    def _compute_fingerprint(
        self,
    ) -> str:
        canonical = json.dumps(
            self.semantic_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

        return sha3_512(
            canonical.encode("utf-8")
        ).hexdigest()

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            **self.semantic_dict(),
            "fingerprint":
                self.fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        value: object,
    ) -> "LegalWorkSupervisionBinding":
        if not isinstance(value, dict):
            _fail("G7F_R4_PAYLOAD_INVALID")

        required = {
            "schema",
            "supervision_binding_version",
            "supervision_binding_id",
            "tenant_id",
            "case_matter_id",
            "scope",
            "work_item_id",
            "supervisee_principal_id",
            "supervisor_principal_id",
            "control_level",
            "supervision_plan_reference",
            "supervision_basis_reference",
            "effective_from",
            "effective_until",
            "supersedes_supervision_binding_id",
            "fingerprint",
        }

        if set(value) != required:
            _fail(
                "G7F_R4_PAYLOAD_SCHEMA_INVALID"
            )

        def required_time(
            name: str,
        ) -> datetime:
            raw = value[name]

            if not isinstance(raw, str):
                _fail(
                    f"G7F_R4_{name.upper()}_INVALID"
                )

            try:
                return datetime.fromisoformat(raw)
            except ValueError as error:
                raise LegalWorkSupervisionBindingError(
                    f"G7F_R4_{name.upper()}_INVALID"
                ) from error

        def optional_time(
            name: str,
        ) -> datetime | None:
            raw = value[name]

            if raw is None:
                return None

            if not isinstance(raw, str):
                _fail(
                    f"G7F_R4_{name.upper()}_INVALID"
                )

            try:
                return datetime.fromisoformat(raw)
            except ValueError as error:
                raise LegalWorkSupervisionBindingError(
                    f"G7F_R4_{name.upper()}_INVALID"
                ) from error

        return cls(
            schema=value["schema"],
            supervision_binding_version=value[
                "supervision_binding_version"
            ],
            supervision_binding_id=value[
                "supervision_binding_id"
            ],
            tenant_id=value["tenant_id"],
            case_matter_id=value[
                "case_matter_id"
            ],
            scope=value["scope"],
            work_item_id=value[
                "work_item_id"
            ],
            supervisee_principal_id=value[
                "supervisee_principal_id"
            ],
            supervisor_principal_id=value[
                "supervisor_principal_id"
            ],
            control_level=value[
                "control_level"
            ],
            supervision_plan_reference=value[
                "supervision_plan_reference"
            ],
            supervision_basis_reference=value[
                "supervision_basis_reference"
            ],
            effective_from=required_time(
                "effective_from"
            ),
            effective_until=optional_time(
                "effective_until"
            ),
            supersedes_supervision_binding_id=value[
                "supersedes_supervision_binding_id"
            ],
            fingerprint=value[
                "fingerprint"
            ],
        )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalSupervisionControlLevel",
    "LegalSupervisionScope",
    "LegalWorkSupervisionBinding",
    "LegalWorkSupervisionBindingError",
]

# ARTIFACT: legal_work_supervision_binding.py
# VERSION: v1.0.1-G7F-R4-LEGAL-WORK-SUPERVISION-BINDING
# AUTHORITY BOUNDARY: immutable operational supervision evidence only
# SUPERVISION NOT IAM: YES
# SUPERVISION NOT ASSIGNMENT: YES
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# TENANT POSTURE: exact tenant correlation; cross-tenant inference prohibited
# FAIL-CLOSED POSTURE: malformed, incomplete, or divergent evidence rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
