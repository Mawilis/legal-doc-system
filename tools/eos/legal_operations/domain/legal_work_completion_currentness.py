"""
TITLE: WILSY OS Legal Work Completion Currentness
VERSION: v1.0.0-P14-R16-WORK-COMPLETION-CURRENTNESS
AUTHORITY: Wilsy OS Core Governance / Legal Operations

PURPOSE:
    Purely derive completion currentness for one exact immutable LegalWorkItem
    from already-read immutable LegalWorkCompletionEvent evidence.

CURRENTNESS MATHEMATICS:
    - zero eligible events => NOT_COMPLETED
    - one exact eligible event => COMPLETED
    - multiple distinct eligible exact events => AMBIGUOUS
    - any cross-scope, wrong-work or temporally impossible event =>
      CORRUPT_BLOCKED
    - exact duplicate immutable facts normalize by fingerprint
    - completion events after evaluated_at are future facts and are excluded

AUTHORITY BOUNDARY:
    This projection performs no database access and grants no completion
    command authority, dependency satisfaction, IAM, assignment, supervision,
    legal-event, AI execution, notification, or financial authority.

ORIGINAL WORK POSTURE:
    LegalWorkItem remains immutable. Embedded work status is not used to invent
    lifecycle completion authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha3_512
import hmac
import json
import re
from typing import Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_work_completion_event import (
    LegalWorkCompletionEvent,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
)


VERSION: Final[str] = (
    "v1.0.0-P14-R16-WORK-COMPLETION-CURRENTNESS"
)

SCHEMA: Final[str] = (
    "WILSY-LEGAL-WORK-COMPLETION-CURRENTNESS/V1"
)

_FINGERPRINT_RE: Final[re.Pattern[str]] = (
    re.compile(
        r"^[0-9a-f]{128}$"
    )
)


class LegalWorkCompletionCurrentnessState(
    str,
    Enum,
):
    NOT_COMPLETED = "NOT_COMPLETED"
    COMPLETED = "COMPLETED"
    AMBIGUOUS = "AMBIGUOUS"
    CORRUPT_BLOCKED = "CORRUPT_BLOCKED"


class LegalWorkCompletionCurrentnessReason(
    str,
    Enum,
):
    NO_COMPLETION_EVENT = "NO_COMPLETION_EVENT"
    EXACT_COMPLETION_EVENT = "EXACT_COMPLETION_EVENT"
    MULTIPLE_COMPLETION_EVENTS = "MULTIPLE_COMPLETION_EVENTS"
    CORRUPT_COMPLETION_EVIDENCE = "CORRUPT_COMPLETION_EVIDENCE"


class LegalWorkCompletionCurrentnessError(
    ValueError
):
    """Stable pure-currentness validation failure."""

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
    raise LegalWorkCompletionCurrentnessError(
        code
    )


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value
        or value != value.strip()
        or len(value) > 320
    ):
        _fail(
            f"P14_R16_{name.upper()}_INVALID"
        )

    return value


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
            f"P14_R16_{name.upper()}_INVALID"
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
            f"P14_R16_{name.upper()}_INVALID"
        )

    return value


def _digest(
    value: dict[
        str,
        object,
    ],
) -> str:
    canonical = json.dumps(
        value,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )

    return sha3_512(
        canonical.encode(
            "utf-8"
        )
    ).hexdigest()


def _currentness_id(
    work_item: LegalWorkItem,
    evaluated_at: datetime,
) -> str:
    return _digest(
        {
            "tenant_id":
                work_item.tenant_id,
            "case_matter_id":
                work_item.case_matter_id,
            "work_item_id":
                work_item.work_item_id,
            "work_item_fingerprint":
                work_item.fingerprint,
            "evaluated_at":
                evaluated_at.isoformat(),
        }
    )


def _known_fingerprint(
    value: object,
) -> str:
    candidate = getattr(
        value,
        "fingerprint",
        None,
    )

    if (
        isinstance(
            candidate,
            str,
        )
        and _FINGERPRINT_RE.fullmatch(
            candidate
        )
        is not None
    ):
        return candidate

    return _digest(
        {
            "corrupt_type":
                type(value).__name__,
            "corrupt_repr":
                repr(value),
        }
    )


@dataclass(
    frozen=True,
    slots=True,
)
class LegalWorkCompletionCurrentness:
    """Immutable output of pure completion-currentness mathematics."""

    currentness_id: str
    tenant_id: str
    case_matter_id: str
    work_item_id: str
    work_item_fingerprint: str
    evaluated_at: datetime

    state: LegalWorkCompletionCurrentnessState
    reason: LegalWorkCompletionCurrentnessReason

    decisive_completion_event_id: str | None
    decisive_completion_event_fingerprint: str | None

    candidate_completion_event_ids: tuple[
        str,
        ...,
    ]
    candidate_completion_event_fingerprints: tuple[
        str,
        ...,
    ]
    corruption_evidence_fingerprints: tuple[
        str,
        ...,
    ]

    normalized_event_count: int
    eligible_event_count: int

    schema: str = SCHEMA
    currentness_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(
        self,
    ) -> None:
        if (
            self.schema != SCHEMA
            or self.currentness_version
            != VERSION
        ):
            _fail(
                "P14_R16_IDENTITY_INVALID"
            )

        currentness_id = _fingerprint(
            "currentness_id",
            self.currentness_id,
        )
        tenant = _text(
            "tenant_id",
            self.tenant_id,
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
            "work_item_fingerprint",
            self.work_item_fingerprint,
        )
        evaluated = _utc(
            "evaluated_at",
            self.evaluated_at,
        )

        try:
            state = (
                LegalWorkCompletionCurrentnessState(
                    self.state
                )
            )
        except (
            TypeError,
            ValueError,
        ) as error:
            raise LegalWorkCompletionCurrentnessError(
                "P14_R16_STATE_INVALID"
            ) from error

        try:
            reason = (
                LegalWorkCompletionCurrentnessReason(
                    self.reason
                )
            )
        except (
            TypeError,
            ValueError,
        ) as error:
            raise LegalWorkCompletionCurrentnessError(
                "P14_R16_REASON_INVALID"
            ) from error

        decisive_id = (
            None
            if self.decisive_completion_event_id
            is None
            else _fingerprint(
                "decisive_completion_event_id",
                self.decisive_completion_event_id,
            )
        )

        decisive_fp = (
            None
            if self.decisive_completion_event_fingerprint
            is None
            else _fingerprint(
                "decisive_completion_event_fingerprint",
                self.decisive_completion_event_fingerprint,
            )
        )

        candidate_ids = tuple(
            _fingerprint(
                "candidate_completion_event_id",
                value,
            )
            for value in self.candidate_completion_event_ids
        )

        candidate_fps = tuple(
            _fingerprint(
                "candidate_completion_event_fingerprint",
                value,
            )
            for value
            in self.candidate_completion_event_fingerprints
        )

        corruption = tuple(
            _fingerprint(
                "corruption_evidence_fingerprint",
                value,
            )
            for value
            in self.corruption_evidence_fingerprints
        )

        if (
            len(
                candidate_ids
            )
            != len(
                candidate_fps
            )
        ):
            _fail(
                "P14_R16_CANDIDATE_EVIDENCE_LENGTH_MISMATCH"
            )

        if (
            len(
                set(
                    candidate_ids
                )
            )
            != len(
                candidate_ids
            )
            or len(
                set(
                    candidate_fps
                )
            )
            != len(
                candidate_fps
            )
        ):
            _fail(
                "P14_R16_CANDIDATE_EVIDENCE_DUPLICATE"
            )

        if (
            len(
                set(
                    corruption
                )
            )
            != len(
                corruption
            )
        ):
            _fail(
                "P14_R16_CORRUPTION_EVIDENCE_DUPLICATE"
            )

        if (
            not isinstance(
                self.normalized_event_count,
                int,
            )
            or isinstance(
                self.normalized_event_count,
                bool,
            )
            or self.normalized_event_count
            < 0
        ):
            _fail(
                "P14_R16_NORMALIZED_EVENT_COUNT_INVALID"
            )

        if (
            not isinstance(
                self.eligible_event_count,
                int,
            )
            or isinstance(
                self.eligible_event_count,
                bool,
            )
            or self.eligible_event_count
            < 0
            or self.eligible_event_count
            > self.normalized_event_count
        ):
            _fail(
                "P14_R16_ELIGIBLE_EVENT_COUNT_INVALID"
            )

        if (
            state
            is LegalWorkCompletionCurrentnessState.COMPLETED
        ):
            if (
                decisive_id is None
                or decisive_fp is None
                or len(
                    candidate_ids
                )
                != 1
                or candidate_ids[
                    0
                ]
                != decisive_id
                or candidate_fps[
                    0
                ]
                != decisive_fp
                or self.eligible_event_count
                != 1
                or corruption
            ):
                _fail(
                    "P14_R16_COMPLETED_EVIDENCE_INVALID"
                )

            if (
                reason
                is not LegalWorkCompletionCurrentnessReason.EXACT_COMPLETION_EVENT
            ):
                _fail(
                    "P14_R16_COMPLETED_REASON_INVALID"
                )

        elif (
            state
            is LegalWorkCompletionCurrentnessState.NOT_COMPLETED
        ):
            if (
                decisive_id is not None
                or decisive_fp is not None
                or self.eligible_event_count
                != 0
                or corruption
            ):
                _fail(
                    "P14_R16_NOT_COMPLETED_EVIDENCE_INVALID"
                )

            if (
                reason
                is not LegalWorkCompletionCurrentnessReason.NO_COMPLETION_EVENT
            ):
                _fail(
                    "P14_R16_NOT_COMPLETED_REASON_INVALID"
                )

        elif (
            state
            is LegalWorkCompletionCurrentnessState.AMBIGUOUS
        ):
            if (
                decisive_id is not None
                or decisive_fp is not None
                or self.eligible_event_count
                < 2
                or len(
                    candidate_ids
                )
                < 2
                or corruption
            ):
                _fail(
                    "P14_R16_AMBIGUOUS_EVIDENCE_INVALID"
                )

            if (
                reason
                is not LegalWorkCompletionCurrentnessReason.MULTIPLE_COMPLETION_EVENTS
            ):
                _fail(
                    "P14_R16_AMBIGUOUS_REASON_INVALID"
                )

        elif (
            state
            is LegalWorkCompletionCurrentnessState.CORRUPT_BLOCKED
        ):
            if (
                decisive_id is not None
                or decisive_fp is not None
                or not corruption
            ):
                _fail(
                    "P14_R16_CORRUPTION_EVIDENCE_REQUIRED"
                )

            if (
                reason
                is not LegalWorkCompletionCurrentnessReason.CORRUPT_COMPLETION_EVIDENCE
            ):
                _fail(
                    "P14_R16_CORRUPTION_REASON_INVALID"
                )

        object.__setattr__(
            self,
            "currentness_id",
            currentness_id,
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
            "evaluated_at",
            evaluated,
        )
        object.__setattr__(
            self,
            "state",
            state,
        )
        object.__setattr__(
            self,
            "reason",
            reason,
        )
        object.__setattr__(
            self,
            "decisive_completion_event_id",
            decisive_id,
        )
        object.__setattr__(
            self,
            "decisive_completion_event_fingerprint",
            decisive_fp,
        )
        object.__setattr__(
            self,
            "candidate_completion_event_ids",
            candidate_ids,
        )
        object.__setattr__(
            self,
            "candidate_completion_event_fingerprints",
            candidate_fps,
        )
        object.__setattr__(
            self,
            "corruption_evidence_fingerprints",
            corruption,
        )

        digest = _digest(
            self.semantic_dict()
        )

        if self.fingerprint:
            supplied = _fingerprint(
                "fingerprint",
                self.fingerprint,
            )

            if not hmac.compare_digest(
                supplied,
                digest,
            ):
                _fail(
                    "P14_R16_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    def semantic_dict(
        self,
    ) -> dict[
        str,
        object,
    ]:
        return {
            "schema":
                self.schema,
            "currentness_version":
                self.currentness_version,
            "currentness_id":
                self.currentness_id,
            "tenant_id":
                self.tenant_id,
            "case_matter_id":
                self.case_matter_id,
            "work_item_id":
                self.work_item_id,
            "work_item_fingerprint":
                self.work_item_fingerprint,
            "evaluated_at":
                self.evaluated_at.isoformat(),
            "state":
                self.state.value,
            "reason":
                self.reason.value,
            "decisive_completion_event_id":
                self.decisive_completion_event_id,
            "decisive_completion_event_fingerprint":
                self.decisive_completion_event_fingerprint,
            "candidate_completion_event_ids":
                self.candidate_completion_event_ids,
            "candidate_completion_event_fingerprints":
                self.candidate_completion_event_fingerprints,
            "corruption_evidence_fingerprints":
                self.corruption_evidence_fingerprints,
            "normalized_event_count":
                self.normalized_event_count,
            "eligible_event_count":
                self.eligible_event_count,
        }

    def to_dict(
        self,
    ) -> dict[
        str,
        object,
    ]:
        value = self.semantic_dict()

        for name in (
            "candidate_completion_event_ids",
            "candidate_completion_event_fingerprints",
            "corruption_evidence_fingerprints",
        ):
            value[
                name
            ] = list(
                value[
                    name
                ]  # type: ignore[arg-type]
            )

        return {
            **value,
            "fingerprint":
                self.fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        value: object,
    ) -> "LegalWorkCompletionCurrentness":
        if not isinstance(
            value,
            dict,
        ):
            _fail(
                "P14_R16_PAYLOAD_INVALID"
            )

        required = {
            "schema",
            "currentness_version",
            "currentness_id",
            "tenant_id",
            "case_matter_id",
            "work_item_id",
            "work_item_fingerprint",
            "evaluated_at",
            "state",
            "reason",
            "decisive_completion_event_id",
            "decisive_completion_event_fingerprint",
            "candidate_completion_event_ids",
            "candidate_completion_event_fingerprints",
            "corruption_evidence_fingerprints",
            "normalized_event_count",
            "eligible_event_count",
            "fingerprint",
        }

        if set(
            value
        ) != required:
            _fail(
                "P14_R16_PAYLOAD_SCHEMA_INVALID"
            )

        raw_time = value[
            "evaluated_at"
        ]

        if not isinstance(
            raw_time,
            str,
        ):
            _fail(
                "P14_R16_EVALUATED_AT_INVALID"
            )

        try:
            evaluated = datetime.fromisoformat(
                raw_time
            )
        except ValueError as error:
            raise LegalWorkCompletionCurrentnessError(
                "P14_R16_EVALUATED_AT_INVALID"
            ) from error

        tuple_fields = {}

        for name in (
            "candidate_completion_event_ids",
            "candidate_completion_event_fingerprints",
            "corruption_evidence_fingerprints",
        ):
            raw = value[
                name
            ]

            if not isinstance(
                raw,
                list,
            ):
                _fail(
                    f"P14_R16_{name.upper()}_INVALID"
                )

            tuple_fields[
                name
            ] = tuple(
                raw
            )

        try:
            return cls(
                schema=value[
                    "schema"
                ],  # type: ignore[arg-type]
                currentness_version=value[
                    "currentness_version"
                ],  # type: ignore[arg-type]
                currentness_id=value[
                    "currentness_id"
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
                evaluated_at=evaluated,
                state=value[
                    "state"
                ],  # type: ignore[arg-type]
                reason=value[
                    "reason"
                ],  # type: ignore[arg-type]
                decisive_completion_event_id=value[
                    "decisive_completion_event_id"
                ],  # type: ignore[arg-type]
                decisive_completion_event_fingerprint=value[
                    "decisive_completion_event_fingerprint"
                ],  # type: ignore[arg-type]
                candidate_completion_event_ids=tuple_fields[
                    "candidate_completion_event_ids"
                ],  # type: ignore[arg-type]
                candidate_completion_event_fingerprints=tuple_fields[
                    "candidate_completion_event_fingerprints"
                ],  # type: ignore[arg-type]
                corruption_evidence_fingerprints=tuple_fields[
                    "corruption_evidence_fingerprints"
                ],  # type: ignore[arg-type]
                normalized_event_count=value[
                    "normalized_event_count"
                ],  # type: ignore[arg-type]
                eligible_event_count=value[
                    "eligible_event_count"
                ],  # type: ignore[arg-type]
                fingerprint=value[
                    "fingerprint"
                ],  # type: ignore[arg-type]
            )
        except LegalWorkCompletionCurrentnessError:
            raise
        except (
            TypeError,
            KeyError,
            ValueError,
        ) as error:
            raise LegalWorkCompletionCurrentnessError(
                "P14_R16_DOCUMENT_INVALID"
            ) from error


def project_legal_work_completion_currentness(
    *,
    work_item: LegalWorkItem,
    completion_events: tuple[
        LegalWorkCompletionEvent,
        ...,
    ],
    evaluated_at: datetime,
) -> LegalWorkCompletionCurrentness:
    """Purely project exact completion currentness at one UTC instant."""
    if type(
        work_item
    ) is not LegalWorkItem:
        _fail(
            "P14_R16_WORK_ITEM_REQUIRED"
        )

    at = _utc(
        "evaluated_at",
        evaluated_at,
    )

    if not isinstance(
        completion_events,
        tuple,
    ):
        _fail(
            "P14_R16_COMPLETION_EVENTS_INVALID"
        )

    normalized: dict[
        str,
        LegalWorkCompletionEvent,
    ] = {}

    corruption: set[
        str
    ] = set()

    for value in completion_events:
        if type(
            value
        ) is not LegalWorkCompletionEvent:
            corruption.add(
                _known_fingerprint(
                    value
                )
            )
            continue

        if (
            value.tenant_id
            != work_item.tenant_id
            or value.case_matter_id
            != work_item.case_matter_id
            or value.work_item_id
            != work_item.work_item_id
            or not hmac.compare_digest(
                value.work_item_fingerprint,
                work_item.fingerprint,
            )
            or value.completed_at
            < work_item.created_at
        ):
            corruption.add(
                value.fingerprint
            )
            continue

        normalized[
            value.fingerprint
        ] = value

    normalized_values = tuple(
        sorted(
            normalized.values(),
            key=lambda value: (
                value.completed_at,
                value.completion_event_id,
                value.fingerprint,
            ),
        )
    )

    eligible = tuple(
        value
        for value in normalized_values
        if value.completed_at
        <= at
    )

    candidate_ids = tuple(
        value.completion_event_id
        for value in eligible
    )

    candidate_fps = tuple(
        value.fingerprint
        for value in eligible
    )

    currentness_id = _currentness_id(
        work_item,
        at,
    )

    base = {
        "currentness_id":
            currentness_id,
        "tenant_id":
            work_item.tenant_id,
        "case_matter_id":
            work_item.case_matter_id,
        "work_item_id":
            work_item.work_item_id,
        "work_item_fingerprint":
            work_item.fingerprint,
        "evaluated_at":
            at,
        "candidate_completion_event_ids":
            candidate_ids,
        "candidate_completion_event_fingerprints":
            candidate_fps,
        "corruption_evidence_fingerprints":
            tuple(
                sorted(
                    corruption
                )
            ),
        "normalized_event_count":
            len(
                normalized_values
            ),
        "eligible_event_count":
            len(
                eligible
            ),
    }

    if corruption:
        return LegalWorkCompletionCurrentness(
            **base,
            state=(
                LegalWorkCompletionCurrentnessState.CORRUPT_BLOCKED
            ),
            reason=(
                LegalWorkCompletionCurrentnessReason.CORRUPT_COMPLETION_EVIDENCE
            ),
            decisive_completion_event_id=None,
            decisive_completion_event_fingerprint=None,
        )

    if not eligible:
        return LegalWorkCompletionCurrentness(
            **base,
            state=(
                LegalWorkCompletionCurrentnessState.NOT_COMPLETED
            ),
            reason=(
                LegalWorkCompletionCurrentnessReason.NO_COMPLETION_EVENT
            ),
            decisive_completion_event_id=None,
            decisive_completion_event_fingerprint=None,
        )

    if len(
        eligible
    ) > 1:
        return LegalWorkCompletionCurrentness(
            **base,
            state=(
                LegalWorkCompletionCurrentnessState.AMBIGUOUS
            ),
            reason=(
                LegalWorkCompletionCurrentnessReason.MULTIPLE_COMPLETION_EVENTS
            ),
            decisive_completion_event_id=None,
            decisive_completion_event_fingerprint=None,
        )

    typed_eligible = cast(
        tuple[
            LegalWorkCompletionEvent,
            ...,
        ],
        eligible,
    )

    decisive = typed_eligible[
        0
    ]

    return LegalWorkCompletionCurrentness(
        **base,
        state=(
            LegalWorkCompletionCurrentnessState.COMPLETED
        ),
        reason=(
            LegalWorkCompletionCurrentnessReason.EXACT_COMPLETION_EVENT
        ),
        decisive_completion_event_id=(
            decisive.completion_event_id
        ),
        decisive_completion_event_fingerprint=(
            decisive.fingerprint
        ),
    )


def evaluate_legal_work_completion_currentness(
    **kwargs: object,
) -> LegalWorkCompletionCurrentness:
    """Compatibility alias for explicit pure evaluation."""
    return project_legal_work_completion_currentness(
        **kwargs  # type: ignore[arg-type]
    )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalWorkCompletionCurrentness",
    "LegalWorkCompletionCurrentnessError",
    "LegalWorkCompletionCurrentnessReason",
    "LegalWorkCompletionCurrentnessState",
    "evaluate_legal_work_completion_currentness",
    "project_legal_work_completion_currentness",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_work_completion_currentness.py
# VERSION: v1.0.0-P14-R16-WORK-COMPLETION-CURRENTNESS
# PURE CURRENTNESS: YES
# PERSISTENCE: NONE
# ORIGINAL WORK MUTATION: NONE
# FUTURE FACTS: EXCLUDED
# EXACT DUPLICATES: NORMALIZED BY FINGERPRINT
# CORRUPTION OUTRANKS NORMAL RESULT: YES
# AMBIGUITY FAIL CLOSED: YES
# EMBEDDED WORK STATUS GRANTS COMPLETION AUTHORITY: NO
# COMPLETION COMMAND AUTHORITY: NONE
# DEPENDENCY SATISFACTION AUTHORITY: NONE
# ASSIGNMENT / SUPERVISION / IAM AUTHORITY: NONE
# LEGAL EVENT AUTHORITY: NONE
# AI EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
