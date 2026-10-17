"""
TITLE: WILSY OS Legal Work Completion Event
VERSION: v1.0.0-P14-R13-WORK-COMPLETION-EVENT
AUTHORITY: Wilsy OS Core Governance / Legal Operations

PURPOSE:
    Represent one immutable, exact-lineage completion fact for an existing
    Legal work item.

ARCHITECTURE:
    The original LegalWorkItem remains immutable. Completion is represented
    independently as append-only lifecycle evidence. A later registry will own
    durability; a later command service will prove caller IAM and compose exact
    work truth with completion evidence. A later currentness projection may
    derive whether completion is current.

AUTHORITY BOUNDARY:
    This domain validates and fingerprints completion evidence only. It does
    not authenticate an actor, grant IAM, assign/supervise work, mutate work
    status, satisfy dependencies, prove source legal-event completion, notify,
    invoke AI, or perform financial execution.

FINANCIAL AUTHORITY:
    None. Kennel EOS exclusively owns financial execution.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_512
import hmac
import json
import re
from typing import Final, NoReturn


VERSION: Final[str] = (
    "v1.0.0-P14-R13-WORK-COMPLETION-EVENT"
)

SCHEMA: Final[str] = (
    "WILSY-LEGAL-WORK-COMPLETION-EVENT/V1"
)

_FINGERPRINT_RE: Final[re.Pattern[str]] = (
    re.compile(
        r"^[0-9a-f]{128}$"
    )
)

_PSEUDO_TENANTS: Final[frozenset[str]] = (
    frozenset(
        {
            "default",
            "global",
            "global_root",
            "root",
            "master",
            "*",
        }
    )
)


class LegalWorkCompletionEventError(
    ValueError
):
    """Stable validation failure for immutable completion evidence."""

    def __init__(
        self,
        code: str,
    ) -> None:
        self.code = code
        super().__init__(
            code
        )


def _fail(
    code: str,
) -> NoReturn:
    raise LegalWorkCompletionEventError(
        code
    )


def _text(
    name: str,
    value: object,
    *,
    limit: int = 320,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value
        or value != value.strip()
        or len(value) > limit
    ):
        _fail(
            f"P14_R13_{name.upper()}_INVALID"
        )

    return value


def _tenant(
    value: object,
) -> str:
    tenant = _text(
        "tenant_id",
        value,
    )

    if (
        tenant.casefold()
        in _PSEUDO_TENANTS
    ):
        _fail(
            "P14_R13_TENANT_REQUIRED"
        )

    return tenant


def _fingerprint(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or _FINGERPRINT_RE.fullmatch(
            value
        )
        is None
    ):
        _fail(
            f"P14_R13_{name.upper()}_FINGERPRINT_INVALID"
        )

    return value


def _utc(
    name: str,
    value: object,
) -> datetime:
    if (
        not isinstance(
            value,
            datetime,
        )
        or value.tzinfo
        is None
        or value.utcoffset()
        is None
        or value.utcoffset()
        != timezone.utc.utcoffset(
            value
        )
    ):
        _fail(
            f"P14_R13_{name.upper()}_INVALID"
        )

    return value


def _canonical(
    values: Mapping[
        str,
        object,
    ],
) -> bytes:
    return json.dumps(
        values,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    ).encode(
        "utf-8"
    )


def _digest(
    values: Mapping[
        str,
        object,
    ],
) -> str:
    return sha3_512(
        _canonical(
            values
        )
    ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
)
class LegalWorkCompletionEvent:
    """
    Immutable completion evidence for one exact Legal work item.

    Authorization evidence fields record provenance only. Their presence never
    means this domain authenticated or authorized the actor.
    """

    tenant_id: str
    case_matter_id: str
    work_item_id: str
    work_item_fingerprint: str

    completion_evidence_reference: str
    completion_evidence_fingerprint: str
    completed_at: datetime

    actor_principal_id: str
    authorization_evidence_reference: str
    authorization_evidence_fingerprint: str

    schema: str = SCHEMA
    completion_event_version: str = VERSION
    completion_event_id: str = ""
    fingerprint: str = ""

    def __post_init__(
        self,
    ) -> None:
        if (
            self.schema != SCHEMA
            or self.completion_event_version
            != VERSION
        ):
            _fail(
                "P14_R13_IDENTITY_INVALID"
            )

        tenant = _tenant(
            self.tenant_id
        )

        matter = _text(
            "case_matter_id",
            self.case_matter_id,
        )

        work_id = _text(
            "work_item_id",
            self.work_item_id,
        )

        work_fp = _fingerprint(
            "work_item",
            self.work_item_fingerprint,
        )

        completion_reference = _text(
            "completion_evidence_reference",
            self.completion_evidence_reference,
        )

        completion_fp = _fingerprint(
            "completion_evidence",
            self.completion_evidence_fingerprint,
        )

        completed = _utc(
            "completed_at",
            self.completed_at,
        )

        actor = _text(
            "actor_principal_id",
            self.actor_principal_id,
        )

        authorization_reference = _text(
            "authorization_evidence_reference",
            self.authorization_evidence_reference,
        )

        authorization_fp = _fingerprint(
            "authorization_evidence",
            self.authorization_evidence_fingerprint,
        )

        identity_payload = {
            "tenant_id":
                tenant,
            "case_matter_id":
                matter,
            "work_item_id":
                work_id,
            "work_item_fingerprint":
                work_fp,
            "completion_evidence_reference":
                completion_reference,
            "completion_evidence_fingerprint":
                completion_fp,
            "completed_at":
                completed.isoformat(),
            "actor_principal_id":
                actor,
            "authorization_evidence_reference":
                authorization_reference,
            "authorization_evidence_fingerprint":
                authorization_fp,
        }

        expected_id = _digest(
            identity_payload
        )

        if self.completion_event_id:
            supplied_id = _fingerprint(
                "completion_event_id",
                self.completion_event_id,
            )

            if not hmac.compare_digest(
                supplied_id,
                expected_id,
            ):
                _fail(
                    "P14_R13_COMPLETION_EVENT_ID_MISMATCH"
                )

        object.__setattr__(
            self,
            "tenant_id",
            tenant,
        )
        object.__setattr__(
            self,
            "case_matter_id",
            matter,
        )
        object.__setattr__(
            self,
            "work_item_id",
            work_id,
        )
        object.__setattr__(
            self,
            "work_item_fingerprint",
            work_fp,
        )
        object.__setattr__(
            self,
            "completion_evidence_reference",
            completion_reference,
        )
        object.__setattr__(
            self,
            "completion_evidence_fingerprint",
            completion_fp,
        )
        object.__setattr__(
            self,
            "completed_at",
            completed,
        )
        object.__setattr__(
            self,
            "actor_principal_id",
            actor,
        )
        object.__setattr__(
            self,
            "authorization_evidence_reference",
            authorization_reference,
        )
        object.__setattr__(
            self,
            "authorization_evidence_fingerprint",
            authorization_fp,
        )
        object.__setattr__(
            self,
            "completion_event_id",
            expected_id,
        )

        expected_fingerprint = _digest(
            self.semantic_dict()
        )

        if self.fingerprint:
            supplied_fp = _fingerprint(
                "fingerprint",
                self.fingerprint,
            )

            if not hmac.compare_digest(
                supplied_fp,
                expected_fingerprint,
            ):
                _fail(
                    "P14_R13_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            expected_fingerprint,
        )

    def semantic_dict(
        self,
    ) -> dict[
        str,
        object,
    ]:
        """Return complete deterministic semantic truth."""
        return {
            "schema":
                self.schema,
            "completion_event_version":
                self.completion_event_version,
            "completion_event_id":
                self.completion_event_id,
            "tenant_id":
                self.tenant_id,
            "case_matter_id":
                self.case_matter_id,
            "work_item_id":
                self.work_item_id,
            "work_item_fingerprint":
                self.work_item_fingerprint,
            "completion_evidence_reference":
                self.completion_evidence_reference,
            "completion_evidence_fingerprint":
                self.completion_evidence_fingerprint,
            "completed_at":
                self.completed_at.isoformat(),
            "actor_principal_id":
                self.actor_principal_id,
            "authorization_evidence_reference":
                self.authorization_evidence_reference,
            "authorization_evidence_fingerprint":
                self.authorization_evidence_fingerprint,
        }

    def to_dict(
        self,
    ) -> dict[
        str,
        object,
    ]:
        """Serialize complete immutable completion evidence."""
        return {
            **self.semantic_dict(),
            "fingerprint":
                self.fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        value: object,
    ) -> "LegalWorkCompletionEvent":
        """Strictly hydrate one exact serialized completion event."""
        if not isinstance(
            value,
            dict,
        ):
            _fail(
                "P14_R13_PAYLOAD_INVALID"
            )

        required = {
            "schema",
            "completion_event_version",
            "completion_event_id",
            "tenant_id",
            "case_matter_id",
            "work_item_id",
            "work_item_fingerprint",
            "completion_evidence_reference",
            "completion_evidence_fingerprint",
            "completed_at",
            "actor_principal_id",
            "authorization_evidence_reference",
            "authorization_evidence_fingerprint",
            "fingerprint",
        }

        if set(
            value
        ) != required:
            _fail(
                "P14_R13_PAYLOAD_SCHEMA_INVALID"
            )

        raw_completed = value[
            "completed_at"
        ]

        if not isinstance(
            raw_completed,
            str,
        ):
            _fail(
                "P14_R13_COMPLETED_AT_INVALID"
            )

        try:
            completed = datetime.fromisoformat(
                raw_completed
            )
        except ValueError as error:
            raise LegalWorkCompletionEventError(
                "P14_R13_COMPLETED_AT_INVALID"
            ) from error

        try:
            return cls(
                schema=value[
                    "schema"
                ],  # type: ignore[arg-type]
                completion_event_version=value[
                    "completion_event_version"
                ],  # type: ignore[arg-type]
                completion_event_id=value[
                    "completion_event_id"
                ],  # type: ignore[arg-type]
                tenant_id=value[
                    "tenant_id"
                ],  # type: ignore[arg-type]
                case_matter_id=value[
                    "case_matter_id"
                ],  # type: ignore[arg-type]
                work_item_id=value[
                    "work_item_id"
                ],  # type: ignore[arg-type]
                work_item_fingerprint=value[
                    "work_item_fingerprint"
                ],  # type: ignore[arg-type]
                completion_evidence_reference=value[
                    "completion_evidence_reference"
                ],  # type: ignore[arg-type]
                completion_evidence_fingerprint=value[
                    "completion_evidence_fingerprint"
                ],  # type: ignore[arg-type]
                completed_at=completed,
                actor_principal_id=value[
                    "actor_principal_id"
                ],  # type: ignore[arg-type]
                authorization_evidence_reference=value[
                    "authorization_evidence_reference"
                ],  # type: ignore[arg-type]
                authorization_evidence_fingerprint=value[
                    "authorization_evidence_fingerprint"
                ],  # type: ignore[arg-type]
                fingerprint=value[
                    "fingerprint"
                ],  # type: ignore[arg-type]
            )
        except LegalWorkCompletionEventError:
            raise
        except (
            TypeError,
            KeyError,
            ValueError,
        ) as error:
            raise LegalWorkCompletionEventError(
                "P14_R13_DOCUMENT_INVALID"
            ) from error


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalWorkCompletionEvent",
    "LegalWorkCompletionEventError",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_work_completion_event.py
# VERSION: v1.0.0-P14-R13-WORK-COMPLETION-EVENT
# IMMUTABLE COMPLETION FACT: YES
# ORIGINAL WORK ITEM MUTATION: NONE
# EXACT WORK ID/FINGERPRINT BINDING: REQUIRED
# COMPLETION EVIDENCE: REQUIRED
# ACTOR PROVENANCE: REQUIRED
# AUTHORIZATION EVIDENCE PROVENANCE: REQUIRED
# DEPENDENCY SATISFACTION AUTHORITY: NONE
# ASSIGNMENT / SUPERVISION / IAM AUTHORITY: NONE
# LEGAL EVENT AUTHORITY: NONE
# AI EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
