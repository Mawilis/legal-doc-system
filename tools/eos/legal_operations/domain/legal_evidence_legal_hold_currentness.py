"""WILSY OS — pure Legal Evidence legal-hold currentness projection.

TITLE: Legal Evidence Legal Hold Currentness
VERSION: v1.0.1-L10A2R-C4D4B-CURRENTNESS-R2
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Derive exact provider-object legal-hold blocking currentness from
         immutable C4D4B hold history at one explicit evaluation instant,
         without persistence, IO, hidden clocks, hold issuance/release or
         downstream disposition authority.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_evidence_legal_hold_currentness.py
COLLABORATION / OWNERSHIP:
    C4D4B LegalEvidenceLegalHoldConstraint owns immutable hold facts.
    C4D4B durable registry owns append-only persistence/history only.
    This module owns pure currentness derivation from already-read bounded
    provider-object history. A later orchestration composer owns registry reads
    and caller-session propagation.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG:
    v1.0.1 restores strict deterministic from_dict hydration for serialized UTC timestamps and tuple-shaped evidence while preserving the certified currentness semantics.\n    v1.0.1-L10A2R-C4D4B-CURRENTNESS-R2 establishes exact lineage grouping,
    future-fact exclusion, fingerprint duplicate normalization, release
    qualification, corruption-first precedence, ambiguous-release blocking,
    independent-hold aggregation and deterministic SHA3-512 derived evidence.
COMPLIANCE:
    Pure derived Legal Operations evidence only. It does not determine whether
    law, court order, client instruction, investigation or regulation requires
    a legal hold and does not create or release a hold.
SECURITY / PRIVACY POSTURE:
    Operates only on opaque scope identifiers, timestamps and fingerprints.
    No raw evidence content, credentials, network access or provider IO.
TENANT BOUNDARY:
    Every supplied history fact must correlate to the exact requested tenant
    and provider-object version. Cross-scope evidence is corruption, never
    absence.
AUTHORITY BOUNDARY:
    Pure hold-blocking currentness derivation only. NO_HOLD_EVIDENCE and
    NO_HOLD_BLOCK_DEMONSTRATED are not retention satisfaction, orphan proof,
    deletion authorization, provider deletion authority or legal clearance.
FINANCIAL AUTHORITY BOUNDARY:
    No billing, payment, settlement or execution authority. Kennel EOS remains
    exclusive financial execution authority.

TRANSACTION BOUNDARY:
    None. This module performs no registry read and accepts no Mongo session.

PERSISTENCE BOUNDARY:
    None. Currentness is derived evidence and is never canonical durable truth.

TIME BOUNDARY:
    The caller supplies one explicit aware evaluation instant. No wall clock is
    read.

FAIL-CLOSED DECLARATION:
    Malformed or cross-scope history becomes CORRUPT_BLOCKED. Multiple distinct
    release times for one exact immutable hold lineage become AMBIGUOUS_BLOCKED.
    Corruption outranks ambiguity and normal currentness. Input ordering,
    insertion ordering and fingerprint ordering never create authority.
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

from tools.eos.legal_operations.domain.legal_evidence_legal_hold_constraint import (
    LegalEvidenceLegalHoldConstraint,
    LegalEvidenceLegalHoldState,
)


VERSION: Final[str] = (
    "v1.0.1-L10A2R-C4D4B-CURRENTNESS-R2"
)

SCHEMA: Final[str] = (
    "WILSY-LEGAL-EVIDENCE-LEGAL-HOLD-CURRENTNESS/V1"
)

UTC = timezone.utc

_HEX: Final[re.Pattern[str]] = re.compile(
    r"^[0-9a-f]{128}$"
)

_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {
        "default",
        "global",
        "global_root",
        "root",
        "master",
        "*",
    }
)

_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "currentness_version",
    "currentness_id",
    "tenant_id",
    "provider_name",
    "storage_reference",
    "object_version_reference",
    "evaluated_at",
    "state",
    "reason",
    "applicable_hold_references",
    "applicable_hold_fingerprints",
    "blocking_hold_references",
    "blocking_hold_fingerprints",
    "decisive_hold_references",
    "decisive_hold_fingerprints",
    "decisive_release_times",
    "corruption_evidence_fingerprints",
    "fingerprint",
)

CURRENTNESS_FIELDS: Final[frozenset[str]] = frozenset(
    _FIELDS
)


class LegalEvidenceLegalHoldCurrentnessState(
    StrEnum
):
    """Closed legal-hold currentness vocabulary without deletion authority."""

    NO_HOLD_EVIDENCE = "NO_HOLD_EVIDENCE"
    HOLD_BLOCKING = "HOLD_BLOCKING"
    NO_HOLD_BLOCK_DEMONSTRATED = (
        "NO_HOLD_BLOCK_DEMONSTRATED"
    )
    AMBIGUOUS_BLOCKED = "AMBIGUOUS_BLOCKED"
    CORRUPT_BLOCKED = "CORRUPT_BLOCKED"


class LegalEvidenceLegalHoldCurrentnessReason(
    StrEnum
):
    """Bounded explanation vocabulary for derived hold currentness."""

    NO_HOLD_EVIDENCE = "NO_HOLD_EVIDENCE"
    ACTIVE_HOLD = "ACTIVE_HOLD"
    RELEASED_HOLD_BEFORE_RELEASE = (
        "RELEASED_HOLD_BEFORE_RELEASE"
    )
    ALL_APPLICABLE_HOLDS_RELEASED = (
        "ALL_APPLICABLE_HOLDS_RELEASED"
    )
    AMBIGUOUS_RELEASE_EVIDENCE = (
        "AMBIGUOUS_RELEASE_EVIDENCE"
    )
    CORRUPT_EVIDENCE = "CORRUPT_EVIDENCE"


class LegalEvidenceLegalHoldCurrentnessError(
    ValueError
):
    """Stable non-sensitive validation failure for the pure projection."""

    def __init__(
        self,
        code: str,
    ) -> None:
        """Expose exactly one bounded error code."""

        self.code = code
        super().__init__(
            code
        )


def _fail(
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one stable currentness validation failure."""

    error = LegalEvidenceLegalHoldCurrentnessError(
        code
    )

    if cause is None:
        raise error

    raise error from cause


def _text(
    name: str,
    value: object,
) -> str:
    """Require one exact non-empty opaque scope identity."""

    if (
        not isinstance(
            value,
            str,
        )
        or not value
        or value != value.strip()
    ):
        _fail(
            f"L10A2R_C4D4B_CURRENTNESS_R2_{name.upper()}_INVALID"
        )

    return value


def _tenant(
    value: object,
) -> str:
    """Require one exact non-global tenant identity."""

    tenant = _text(
        "tenant_id",
        value,
    )

    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail(
            "L10A2R_C4D4B_CURRENTNESS_R2_TENANT_REQUIRED"
        )

    return tenant


def _fingerprint(
    name: str,
    value: object,
) -> str:
    """Require one lowercase SHA3-512 evidence fingerprint."""

    if (
        not isinstance(
            value,
            str,
        )
        or _HEX.fullmatch(
            value
        )
        is None
    ):
        _fail(
            f"L10A2R_C4D4B_CURRENTNESS_R2_{name.upper()}_INVALID"
        )

    return value


def _timestamp(
    name: str,
    value: object,
) -> datetime:
    """Require one explicit aware instant normalized to UTC."""

    if (
        not isinstance(
            value,
            datetime,
        )
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(
            f"L10A2R_C4D4B_CURRENTNESS_R2_{name.upper()}_INVALID"
        )

    return value.astimezone(
        UTC
    ).replace(
        microsecond=value.microsecond
    )


def _json_value(
    value: object,
) -> object:
    """Convert currentness evidence to deterministic JSON-safe values."""

    if isinstance(
        value,
        datetime,
    ):
        return (
            value.astimezone(
                UTC
            )
            .isoformat(
                timespec="microseconds"
            )
            .replace(
                "+00:00",
                "Z",
            )
        )

    if isinstance(
        value,
        StrEnum,
    ):
        return value.value

    if isinstance(
        value,
        tuple,
    ):
        return [
            _json_value(
                item
            )
            for item in value
        ]

    return value


def _digest(
    instance: "LegalEvidenceLegalHoldCurrentness",
) -> str:
    """Fingerprint the complete semantic currentness payload."""

    payload = {
        field:
            _json_value(
                getattr(
                    instance,
                    field,
                )
            )
        for field in _FIELDS[:-1]
    }

    return hashlib.sha3_512(
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=False,
            separators=(
                ",",
                ":",
            ),
        ).encode(
            "utf-8"
        )
    ).hexdigest()


def _projection_id(
    tenant_id: str,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
    evaluated_at: datetime,
) -> str:
    """Derive deterministic in-memory identity for one evaluation."""

    payload = {
        "tenant_id":
            tenant_id,
        "provider_name":
            provider_name,
        "storage_reference":
            storage_reference,
        "object_version_reference":
            object_version_reference,
        "evaluated_at":
            evaluated_at.isoformat(
                timespec="microseconds"
            ),
    }

    digest = hashlib.sha3_512(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
        ).encode(
            "utf-8"
        )
    ).hexdigest()[:48]

    return (
        "legal-hold-currentness-"
        + digest
    )


def _corruption_fingerprint(
    index: int,
    code: str,
) -> str:
    """Produce one non-sensitive deterministic corruption marker."""

    return hashlib.sha3_512(
        (
            "L10A2R:C4D4B:CURRENTNESS:R2:"
            + str(index)
            + ":"
            + code
        ).encode(
            "utf-8"
        )
    ).hexdigest()


def _tuple_text(
    name: str,
    value: object,
) -> tuple[str, ...]:
    """Require one tuple of exact opaque text values.

    Hold references identify directives rather than immutable facts. The same
    hold reference may therefore appear more than once when distinct immutable
    ACTIVE/RELEASED or independently sourced facts share that reference.
    Positional fact identity is preserved by the corresponding fingerprint
    tuple, whose duplicate-free contract remains separately enforced.
    """

    if not isinstance(
        value,
        (
            tuple,
            list,
        ),
    ):
        _fail(
            f"L10A2R_C4D4B_CURRENTNESS_R2_{name.upper()}_INVALID"
        )

    return tuple(
        _text(
            name,
            item,
        )
        for item in cast(
            tuple[object, ...]
            | list[object],
            value,
        )
    )




def _tuple_fingerprints(
    name: str,
    value: object,
) -> tuple[str, ...]:
    """Require one duplicate-free tuple of SHA3-512 fingerprints."""

    if not isinstance(
        value,
        (
            tuple,
            list,
        ),
    ):
        _fail(
            f"L10A2R_C4D4B_CURRENTNESS_R2_{name.upper()}_INVALID"
        )

    result = tuple(
        _fingerprint(
            name,
            item,
        )
        for item in cast(
            tuple[object, ...]
            | list[object],
            value,
        )
    )

    if len(
        set(
            result
        )
    ) != len(
        result
    ):
        _fail(
            f"L10A2R_C4D4B_CURRENTNESS_R2_{name.upper()}_DUPLICATE"
        )

    return result


def _tuple_optional_times(
    name: str,
    value: object,
) -> tuple[datetime | None, ...]:
    """Require one tuple of optional explicit aware timestamps."""

    if not isinstance(
        value,
        (
            tuple,
            list,
        ),
    ):
        _fail(
            f"L10A2R_C4D4B_CURRENTNESS_R2_{name.upper()}_INVALID"
        )

    result: list[
        datetime | None
    ] = []

    for item in cast(
        tuple[object, ...]
        | list[object],
        value,
    ):
        if item is None:
            result.append(
                None
            )
        else:
            result.append(
                _timestamp(
                    name,
                    item,
                )
            )

    return tuple(
        result
    )


@dataclass(
    frozen=True,
    slots=True,
)
class LegalEvidenceLegalHoldCurrentness:
    """Immutable pure currentness evidence for one exact provider object.

    This value reports whether supplied C4D4B history demonstrates a legal-hold
    preservation block at ``evaluated_at``. It never constitutes deletion
    authorization, legal clearance, retention satisfaction, orphan proof,
    provider mutation authority or permission to release a hold.
    """

    currentness_id: str
    tenant_id: str
    provider_name: str
    storage_reference: str
    object_version_reference: str
    evaluated_at: datetime
    state: LegalEvidenceLegalHoldCurrentnessState | str
    reason: LegalEvidenceLegalHoldCurrentnessReason | str
    applicable_hold_references: tuple[str, ...]
    applicable_hold_fingerprints: tuple[str, ...]
    blocking_hold_references: tuple[str, ...]
    blocking_hold_fingerprints: tuple[str, ...]
    decisive_hold_references: tuple[str, ...]
    decisive_hold_fingerprints: tuple[str, ...]
    decisive_release_times: tuple[
        datetime | None,
        ...,
    ]
    corruption_evidence_fingerprints: tuple[str, ...]
    schema: str = SCHEMA
    currentness_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(
        self,
    ) -> None:
        """Validate exact derived evidence and verify SHA3-512 integrity."""

        if (
            self.schema != SCHEMA
            or self.currentness_version
            != VERSION
        ):
            _fail(
                "L10A2R_C4D4B_CURRENTNESS_R2_IDENTITY_INVALID"
            )

        currentness_id = _text(
            "currentness_id",
            self.currentness_id,
        )

        tenant = _tenant(
            self.tenant_id
        )

        provider = _text(
            "provider_name",
            self.provider_name,
        )

        storage = _text(
            "storage_reference",
            self.storage_reference,
        )

        object_version = _text(
            "object_version_reference",
            self.object_version_reference,
        )

        evaluated_at = _timestamp(
            "evaluated_at",
            self.evaluated_at,
        )

        try:
            state = (
                LegalEvidenceLegalHoldCurrentnessState(
                    self.state
                )
            )
        except (
            TypeError,
            ValueError,
        ) as error:
            _fail(
                "L10A2R_C4D4B_CURRENTNESS_R2_STATE_INVALID",
                error,
            )

        try:
            reason = (
                LegalEvidenceLegalHoldCurrentnessReason(
                    self.reason
                )
            )
        except (
            TypeError,
            ValueError,
        ) as error:
            _fail(
                "L10A2R_C4D4B_CURRENTNESS_R2_REASON_INVALID",
                error,
            )

        applicable_refs = _tuple_text(
            "applicable_hold_references",
            self.applicable_hold_references,
        )

        applicable_fps = _tuple_fingerprints(
            "applicable_hold_fingerprints",
            self.applicable_hold_fingerprints,
        )

        blocking_refs = _tuple_text(
            "blocking_hold_references",
            self.blocking_hold_references,
        )

        blocking_fps = _tuple_fingerprints(
            "blocking_hold_fingerprints",
            self.blocking_hold_fingerprints,
        )

        decisive_refs = _tuple_text(
            "decisive_hold_references",
            self.decisive_hold_references,
        )

        decisive_fps = _tuple_fingerprints(
            "decisive_hold_fingerprints",
            self.decisive_hold_fingerprints,
        )

        decisive_release_times = (
            _tuple_optional_times(
                "decisive_release_times",
                self.decisive_release_times,
            )
        )

        corruption = _tuple_fingerprints(
            "corruption_evidence_fingerprints",
            self.corruption_evidence_fingerprints,
        )

        if (
            len(
                applicable_refs
            )
            != len(
                applicable_fps
            )
        ):
            _fail(
                "L10A2R_C4D4B_CURRENTNESS_R2_APPLICABLE_EVIDENCE_LENGTH_MISMATCH"
            )

        if (
            len(
                blocking_refs
            )
            != len(
                blocking_fps
            )
        ):
            _fail(
                "L10A2R_C4D4B_CURRENTNESS_R2_BLOCKING_EVIDENCE_LENGTH_MISMATCH"
            )

        if not (
            len(
                decisive_refs
            )
            == len(
                decisive_fps
            )
            == len(
                decisive_release_times
            )
        ):
            _fail(
                "L10A2R_C4D4B_CURRENTNESS_R2_DECISIVE_EVIDENCE_LENGTH_MISMATCH"
            )

        if state is (
            LegalEvidenceLegalHoldCurrentnessState.NO_HOLD_EVIDENCE
        ):
            if (
                applicable_refs
                or applicable_fps
                or blocking_refs
                or blocking_fps
                or decisive_refs
                or decisive_fps
                or decisive_release_times
                or corruption
            ):
                _fail(
                    "L10A2R_C4D4B_CURRENTNESS_R2_NO_HOLD_EVIDENCE_PAYLOAD_INVALID"
                )

            expected_reason = (
                LegalEvidenceLegalHoldCurrentnessReason.NO_HOLD_EVIDENCE
            )

        elif state is (
            LegalEvidenceLegalHoldCurrentnessState.CORRUPT_BLOCKED
        ):
            if not corruption:
                _fail(
                    "L10A2R_C4D4B_CURRENTNESS_R2_CORRUPTION_EVIDENCE_REQUIRED"
                )

            expected_reason = (
                LegalEvidenceLegalHoldCurrentnessReason.CORRUPT_EVIDENCE
            )

        elif state is (
            LegalEvidenceLegalHoldCurrentnessState.AMBIGUOUS_BLOCKED
        ):
            if (
                not decisive_refs
                or not decisive_fps
                or corruption
            ):
                _fail(
                    "L10A2R_C4D4B_CURRENTNESS_R2_AMBIGUITY_EVIDENCE_REQUIRED"
                )

            expected_reason = (
                LegalEvidenceLegalHoldCurrentnessReason.AMBIGUOUS_RELEASE_EVIDENCE
            )

        elif state is (
            LegalEvidenceLegalHoldCurrentnessState.HOLD_BLOCKING
        ):
            if (
                not blocking_refs
                or not blocking_fps
                or not decisive_refs
                or not decisive_fps
                or corruption
            ):
                _fail(
                    "L10A2R_C4D4B_CURRENTNESS_R2_BLOCKING_EVIDENCE_REQUIRED"
                )

            if reason not in {
                LegalEvidenceLegalHoldCurrentnessReason.ACTIVE_HOLD,
                LegalEvidenceLegalHoldCurrentnessReason.RELEASED_HOLD_BEFORE_RELEASE,
            }:
                _fail(
                    "L10A2R_C4D4B_CURRENTNESS_R2_BLOCKING_REASON_INVALID"
                )

            expected_reason = reason

        else:
            if (
                not applicable_refs
                or not applicable_fps
                or blocking_refs
                or blocking_fps
                or corruption
            ):
                _fail(
                    "L10A2R_C4D4B_CURRENTNESS_R2_NONBLOCKING_EVIDENCE_INVALID"
                )

            expected_reason = (
                LegalEvidenceLegalHoldCurrentnessReason.ALL_APPLICABLE_HOLDS_RELEASED
            )

        if reason is not expected_reason:
            _fail(
                "L10A2R_C4D4B_CURRENTNESS_R2_REASON_STATE_MISMATCH"
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
            "provider_name",
            provider,
        )
        object.__setattr__(
            self,
            "storage_reference",
            storage,
        )
        object.__setattr__(
            self,
            "object_version_reference",
            object_version,
        )
        object.__setattr__(
            self,
            "evaluated_at",
            evaluated_at,
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
            "applicable_hold_references",
            applicable_refs,
        )
        object.__setattr__(
            self,
            "applicable_hold_fingerprints",
            applicable_fps,
        )
        object.__setattr__(
            self,
            "blocking_hold_references",
            blocking_refs,
        )
        object.__setattr__(
            self,
            "blocking_hold_fingerprints",
            blocking_fps,
        )
        object.__setattr__(
            self,
            "decisive_hold_references",
            decisive_refs,
        )
        object.__setattr__(
            self,
            "decisive_hold_fingerprints",
            decisive_fps,
        )
        object.__setattr__(
            self,
            "decisive_release_times",
            decisive_release_times,
        )
        object.__setattr__(
            self,
            "corruption_evidence_fingerprints",
            corruption,
        )

        digest = _digest(
            self
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
                    "L10A2R_C4D4B_CURRENTNESS_R2_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    @property
    def preservation_blocking(
        self,
    ) -> bool:
        """Return true for blocking, ambiguous, or corrupt hold currentness."""

        return self.state in {
            LegalEvidenceLegalHoldCurrentnessState.HOLD_BLOCKING,
            LegalEvidenceLegalHoldCurrentnessState.AMBIGUOUS_BLOCKED,
            LegalEvidenceLegalHoldCurrentnessState.CORRUPT_BLOCKED,
        }

    @property
    def deletion_authorized(
        self,
    ) -> bool:
        """Return false unconditionally; currentness never authorizes deletion."""

        return False

    @property
    def provider_delete_authorized(
        self,
    ) -> bool:
        """Return false unconditionally; provider mutation remains out of scope."""

        return False

    def to_dict(
        self,
    ) -> dict[str, object]:
        """Serialize complete immutable currentness evidence deterministically."""

        return {
            field:
                _json_value(
                    getattr(
                        self,
                        field,
                    )
                )
            for field in _FIELDS
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalEvidenceLegalHoldCurrentness":
        """Hydrate the exact schema and verify supplied SHA3-512 integrity."""

        if (
            not isinstance(
                payload,
                Mapping,
            )
            or set(
                payload
            )
            != set(
                _FIELDS
            )
        ):
            _fail(
                "L10A2R_C4D4B_CURRENTNESS_R2_SCHEMA_INVALID"
            )

        values = dict(
            payload
        )

        stored = values.pop(
            "fingerprint"
        )

        def _parse_serialized_timestamp(
            name: str,
            value: object,
        ) -> datetime:
            if not isinstance(
                value,
                str,
            ):
                _fail(
                    f"L10A2R_C4D4B_CURRENTNESS_R2_{name.upper()}_INVALID"
                )

            try:
                parsed = datetime.fromisoformat(
                    value.replace(
                        "Z",
                        "+00:00",
                    )
                )
            except ValueError as error:
                _fail(
                    f"L10A2R_C4D4B_CURRENTNESS_R2_{name.upper()}_INVALID",
                    error,
                )

            return _timestamp(
                name,
                parsed,
            )

        values[
            "evaluated_at"
        ] = _parse_serialized_timestamp(
            "evaluated_at",
            values.get(
                "evaluated_at"
            ),
        )

        raw_release_times = values.get(
            "decisive_release_times"
        )

        if not isinstance(
            raw_release_times,
            list,
        ):
            _fail(
                "L10A2R_C4D4B_CURRENTNESS_R2_DECISIVE_RELEASE_TIMES_INVALID"
            )

        values[
            "decisive_release_times"
        ] = tuple(
            (
                None
                if item is None
                else _parse_serialized_timestamp(
                    "decisive_release_times",
                    item,
                )
            )
            for item in raw_release_times
        )

        for tuple_field in (
            "applicable_hold_references",
            "applicable_hold_fingerprints",
            "blocking_hold_references",
            "blocking_hold_fingerprints",
            "decisive_hold_references",
            "decisive_hold_fingerprints",
            "corruption_evidence_fingerprints",
        ):
            raw = values.get(
                tuple_field
            )

            if not isinstance(
                raw,
                list,
            ):
                _fail(
                    f"L10A2R_C4D4B_CURRENTNESS_R2_{tuple_field.upper()}_INVALID"
                )

            values[
                tuple_field
            ] = tuple(
                raw
            )

        try:
            result = cls(
                **cast(
                    dict[str, Any],
                    values,
                )
            )
        except TypeError as error:
            _fail(
                "L10A2R_C4D4B_CURRENTNESS_R2_SCHEMA_INVALID",
                error,
            )

        if (
            not isinstance(
                stored,
                str,
            )
            or not hmac.compare_digest(
                stored,
                result.fingerprint,
            )
        ):
            _fail(
                "L10A2R_C4D4B_CURRENTNESS_R2_FINGERPRINT_MISMATCH"
            )

        return result


def _known_fingerprint(
    index: int,
    value: object,
    code: str,
) -> str:
    """Retain an already-valid fingerprint or return a safe corruption marker."""

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
        and _HEX.fullmatch(
            candidate
        )
        is not None
    ):
        return candidate

    return _corruption_fingerprint(
        index,
        code,
    )


def _lineage(
    value: LegalEvidenceLegalHoldConstraint,
) -> tuple[
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    datetime,
]:
    """Return exact immutable hold lineage excluding state/release."""

    return (
        value.tenant_id,
        value.provider_name,
        value.storage_reference,
        value.object_version_reference,
        value.hold_reference,
        value.source_evidence_reference,
        value.source_evidence_fingerprint,
        value.imposed_at,
    )


def _corrupt_result(
    *,
    tenant_id: str,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
    evaluated_at: datetime,
    corruption: tuple[str, ...],
) -> LegalEvidenceLegalHoldCurrentness:
    """Return fail-closed corruption currentness with no positive authority."""

    return LegalEvidenceLegalHoldCurrentness(
        currentness_id=_projection_id(
            tenant_id,
            provider_name,
            storage_reference,
            object_version_reference,
            evaluated_at,
        ),
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        evaluated_at=evaluated_at,
        state=LegalEvidenceLegalHoldCurrentnessState.CORRUPT_BLOCKED,
        reason=LegalEvidenceLegalHoldCurrentnessReason.CORRUPT_EVIDENCE,
        applicable_hold_references=(),
        applicable_hold_fingerprints=(),
        blocking_hold_references=(),
        blocking_hold_fingerprints=(),
        decisive_hold_references=(),
        decisive_hold_fingerprints=(),
        decisive_release_times=(),
        corruption_evidence_fingerprints=tuple(
            sorted(
                set(
                    corruption
                )
            )
        ),
    )


def project_legal_evidence_legal_hold_currentness(
    *,
    tenant_id: str,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
    evaluated_at: datetime,
    history: Iterable[
        LegalEvidenceLegalHoldConstraint
    ],
) -> LegalEvidenceLegalHoldCurrentness:
    """Project exact provider-object hold currentness at explicit time.

    Exact duplicate immutable facts normalize by fingerprint. Facts imposed
    after ``evaluated_at`` are excluded. ACTIVE and RELEASED facts qualify one
    another only when all immutable lineage fields match exactly. Multiple
    distinct release times for one lineage are ambiguous and block. Any
    independently applicable blocking lineage blocks the provider object.
    Malformed or cross-scope history yields CORRUPT_BLOCKED.
    """

    tenant = _tenant(
        tenant_id
    )
    provider = _text(
        "provider_name",
        provider_name,
    )
    storage = _text(
        "storage_reference",
        storage_reference,
    )
    object_version = _text(
        "object_version_reference",
        object_version_reference,
    )
    at = _timestamp(
        "evaluated_at",
        evaluated_at,
    )

    try:
        supplied = tuple(
            history
        )
    except Exception:
        return _corrupt_result(
            tenant_id=tenant,
            provider_name=provider,
            storage_reference=storage,
            object_version_reference=object_version,
            evaluated_at=at,
            corruption=(
                _corruption_fingerprint(
                    0,
                    "ITERABLE",
                ),
            ),
        )

    corruption: list[str] = []
    normalized: dict[
        str,
        LegalEvidenceLegalHoldConstraint,
    ] = {}

    for index, value in enumerate(
        supplied
    ):
        if type(
            value
        ) is not LegalEvidenceLegalHoldConstraint:
            corruption.append(
                _known_fingerprint(
                    index,
                    value,
                    "TYPE",
                )
            )
            continue

        try:
            value.__post_init__()
        except Exception:
            corruption.append(
                _known_fingerprint(
                    index,
                    value,
                    "MALFORMED",
                )
            )
            continue

        if (
            value.tenant_id
            != tenant
            or value.provider_name
            != provider
            or value.storage_reference
            != storage
            or value.object_version_reference
            != object_version
        ):
            corruption.append(
                value.fingerprint
            )
            continue

        existing = normalized.get(
            value.fingerprint
        )

        if (
            existing is not None
            and existing != value
        ):
            corruption.append(
                value.fingerprint
            )
            continue

        normalized[
            value.fingerprint
        ] = value

    if corruption:
        return _corrupt_result(
            tenant_id=tenant,
            provider_name=provider,
            storage_reference=storage,
            object_version_reference=object_version,
            evaluated_at=at,
            corruption=tuple(
                corruption
            ),
        )

    applicable = tuple(
        value
        for value in normalized.values()
        if value.imposed_at <= at
    )

    if not applicable:
        return LegalEvidenceLegalHoldCurrentness(
            currentness_id=_projection_id(
                tenant,
                provider,
                storage,
                object_version,
                at,
            ),
            tenant_id=tenant,
            provider_name=provider,
            storage_reference=storage,
            object_version_reference=object_version,
            evaluated_at=at,
            state=LegalEvidenceLegalHoldCurrentnessState.NO_HOLD_EVIDENCE,
            reason=LegalEvidenceLegalHoldCurrentnessReason.NO_HOLD_EVIDENCE,
            applicable_hold_references=(),
            applicable_hold_fingerprints=(),
            blocking_hold_references=(),
            blocking_hold_fingerprints=(),
            decisive_hold_references=(),
            decisive_hold_fingerprints=(),
            decisive_release_times=(),
            corruption_evidence_fingerprints=(),
        )

    ordered_applicable = tuple(
        sorted(
            applicable,
            key=lambda value: (
                value.hold_reference,
                value.source_evidence_reference,
                value.source_evidence_fingerprint,
                value.imposed_at,
                value.fingerprint,
            ),
        )
    )

    groups: dict[
        tuple[
            str,
            str,
            str,
            str,
            str,
            str,
            str,
            datetime,
        ],
        list[
            LegalEvidenceLegalHoldConstraint
        ],
    ] = {}

    for value in ordered_applicable:
        groups.setdefault(
            _lineage(
                value
            ),
            [],
        ).append(
            value
        )

    ambiguous: list[
        LegalEvidenceLegalHoldConstraint
    ] = []

    blockers: list[
        tuple[
            LegalEvidenceLegalHoldConstraint,
            datetime | None,
            LegalEvidenceLegalHoldCurrentnessReason,
        ]
    ] = []

    decisive_nonblocking: list[
        tuple[
            LegalEvidenceLegalHoldConstraint,
            datetime | None,
        ]
    ] = []

    for lineage in sorted(
        groups,
        key=lambda item: (
            item[4],
            item[5],
            item[6],
            item[7],
        ),
    ):
        values = tuple(
            sorted(
                groups[
                    lineage
                ],
                key=lambda value: (
                    value.state.value,
                    (
                        value.released_at.isoformat()
                        if value.released_at
                        is not None
                        else ""
                    ),
                    value.fingerprint,
                ),
            )
        )

        active = tuple(
            value
            for value in values
            if value.state
            is LegalEvidenceLegalHoldState.ACTIVE
        )

        released = tuple(
            value
            for value in values
            if value.state
            is LegalEvidenceLegalHoldState.RELEASED
        )

        release_times = {
            value.released_at
            for value in released
        }

        if len(
            release_times
        ) > 1:
            ambiguous.extend(
                values
            )
            continue

        release_time = (
            next(
                iter(
                    release_times
                )
            )
            if release_times
            else None
        )

        if release_time is not None:
            release_fact = released[0]

            if at < release_time:
                blockers.append(
                    (
                        release_fact,
                        release_time,
                        LegalEvidenceLegalHoldCurrentnessReason.RELEASED_HOLD_BEFORE_RELEASE,
                    )
                )
            else:
                decisive_nonblocking.append(
                    (
                        release_fact,
                        release_time,
                    )
                )

            continue

        if active:
            blockers.append(
                (
                    active[0],
                    None,
                    LegalEvidenceLegalHoldCurrentnessReason.ACTIVE_HOLD,
                )
            )

    if ambiguous:
        decisive = tuple(
            sorted(
                {
                    value.fingerprint:
                        value
                    for value in ambiguous
                }.values(),
                key=lambda value: (
                    value.hold_reference,
                    value.fingerprint,
                ),
            )
        )

        return LegalEvidenceLegalHoldCurrentness(
            currentness_id=_projection_id(
                tenant,
                provider,
                storage,
                object_version,
                at,
            ),
            tenant_id=tenant,
            provider_name=provider,
            storage_reference=storage,
            object_version_reference=object_version,
            evaluated_at=at,
            state=LegalEvidenceLegalHoldCurrentnessState.AMBIGUOUS_BLOCKED,
            reason=LegalEvidenceLegalHoldCurrentnessReason.AMBIGUOUS_RELEASE_EVIDENCE,
            applicable_hold_references=tuple(
                value.hold_reference
                for value in ordered_applicable
            ),
            applicable_hold_fingerprints=tuple(
                value.fingerprint
                for value in ordered_applicable
            ),
            blocking_hold_references=(),
            blocking_hold_fingerprints=(),
            decisive_hold_references=tuple(
                value.hold_reference
                for value in decisive
            ),
            decisive_hold_fingerprints=tuple(
                value.fingerprint
                for value in decisive
            ),
            decisive_release_times=tuple(
                value.released_at
                for value in decisive
            ),
            corruption_evidence_fingerprints=(),
        )

    if blockers:
        ordered_blockers = tuple(
            sorted(
                blockers,
                key=lambda item: (
                    item[0].hold_reference,
                    item[0].fingerprint,
                ),
            )
        )

        reason = (
            LegalEvidenceLegalHoldCurrentnessReason.ACTIVE_HOLD
            if any(
                item[2]
                is LegalEvidenceLegalHoldCurrentnessReason.ACTIVE_HOLD
                for item in ordered_blockers
            )
            else LegalEvidenceLegalHoldCurrentnessReason.RELEASED_HOLD_BEFORE_RELEASE
        )

        return LegalEvidenceLegalHoldCurrentness(
            currentness_id=_projection_id(
                tenant,
                provider,
                storage,
                object_version,
                at,
            ),
            tenant_id=tenant,
            provider_name=provider,
            storage_reference=storage,
            object_version_reference=object_version,
            evaluated_at=at,
            state=LegalEvidenceLegalHoldCurrentnessState.HOLD_BLOCKING,
            reason=reason,
            applicable_hold_references=tuple(
                value.hold_reference
                for value in ordered_applicable
            ),
            applicable_hold_fingerprints=tuple(
                value.fingerprint
                for value in ordered_applicable
            ),
            blocking_hold_references=tuple(
                item[0].hold_reference
                for item in ordered_blockers
            ),
            blocking_hold_fingerprints=tuple(
                item[0].fingerprint
                for item in ordered_blockers
            ),
            decisive_hold_references=tuple(
                item[0].hold_reference
                for item in ordered_blockers
            ),
            decisive_hold_fingerprints=tuple(
                item[0].fingerprint
                for item in ordered_blockers
            ),
            decisive_release_times=tuple(
                item[1]
                for item in ordered_blockers
            ),
            corruption_evidence_fingerprints=(),
        )

    ordered_nonblocking = tuple(
        sorted(
            decisive_nonblocking,
            key=lambda item: (
                item[0].hold_reference,
                item[0].fingerprint,
            ),
        )
    )

    return LegalEvidenceLegalHoldCurrentness(
        currentness_id=_projection_id(
            tenant,
            provider,
            storage,
            object_version,
            at,
        ),
        tenant_id=tenant,
        provider_name=provider,
        storage_reference=storage,
        object_version_reference=object_version,
        evaluated_at=at,
        state=LegalEvidenceLegalHoldCurrentnessState.NO_HOLD_BLOCK_DEMONSTRATED,
        reason=LegalEvidenceLegalHoldCurrentnessReason.ALL_APPLICABLE_HOLDS_RELEASED,
        applicable_hold_references=tuple(
            value.hold_reference
            for value in ordered_applicable
        ),
        applicable_hold_fingerprints=tuple(
            value.fingerprint
            for value in ordered_applicable
        ),
        blocking_hold_references=(),
        blocking_hold_fingerprints=(),
        decisive_hold_references=tuple(
            item[0].hold_reference
            for item in ordered_nonblocking
        ),
        decisive_hold_fingerprints=tuple(
            item[0].fingerprint
            for item in ordered_nonblocking
        ),
        decisive_release_times=tuple(
            item[1]
            for item in ordered_nonblocking
        ),
        corruption_evidence_fingerprints=(),
    )


def evaluate_legal_evidence_legal_hold_currentness(
    **kwargs: Any,
) -> LegalEvidenceLegalHoldCurrentness:
    """Named evaluation alias over the same pure projection contract."""

    return project_legal_evidence_legal_hold_currentness(
        **kwargs
    )


__all__ = [
    "CURRENTNESS_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalEvidenceLegalHoldCurrentness",
    "LegalEvidenceLegalHoldCurrentnessError",
    "LegalEvidenceLegalHoldCurrentnessReason",
    "LegalEvidenceLegalHoldCurrentnessState",
    "evaluate_legal_evidence_legal_hold_currentness",
    "project_legal_evidence_legal_hold_currentness",
]


# ARTIFACT: legal_evidence_legal_hold_currentness.py
# VERSION: v1.0.1-L10A2R-C4D4B-CURRENTNESS-R2
# AUTHORITY BOUNDARY: pure legal-hold currentness derivation only
# TENANT POSTURE: exact tenant/provider-object correlation; cross-scope blocks
# LINEAGE POSTURE: release qualifies only exact immutable hold lineage
# AMBIGUITY POSTURE: multiple release times for one lineage block fail-closed
# CORRUPTION POSTURE: malformed/cross-scope evidence outranks normal results
# TIME POSTURE: explicit caller-supplied aware evaluation instant only
# PERSISTENCE POSTURE: none; derived currentness is not canonical durable truth
# HOLD POSTURE: no issuance, release, activation or transition authority
# RETENTION POSTURE: no retention-satisfaction authority
# ORPHAN POSTURE: no orphan proof or inference authority
# DELETION POSTURE: no deletion authorization or provider mutation authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
