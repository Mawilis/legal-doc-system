"""
WILSY OS — Legal Transition Work Materialization Receipt

TITLE:
    Immutable Transition-to-Work Materialization Receipt

VERSION:
    v1.0.0-P14-P12-TRANSITION-WORK-MATERIALIZATION-RECEIPT

PURPOSE:
    Preserve immutable historical evidence binding one exact persisted workflow
    transition to one exact selected work-materialization policy revision and
    the exact ordered work-item outputs produced by that composition.

REPLAY GUARANTEE:
    Later policy revisions cannot reinterpret an already materialized
    transition. A new transition caused by stage re-entry necessarily derives
    a different receipt identity.

AUTHORITY BOUNDARY:
    Historical composition evidence only. This value creates no work item,
    chooses no policy, assigns or supervises no principal, grants no IAM or
    professional authority, calculates no jurisdictional legal deadline,
    delivers no notification, invokes no AI and performs no financial action.

COMPETITIVE POSTURE:
    Stage-trigger automation is preserved with immutable policy provenance,
    deterministic replay identity and explicit historical output binding.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive for financial execution.

FAIL-CLOSED DECLARATION:
    Invalid scope, fingerprints, policy lineage, timestamps, duplicate output
    identities, schema drift or fingerprint divergence rejects without
    coercion or authority expansion.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Final, Mapping, NoReturn, cast


VERSION: Final[str] = (
    "v1.0.0-P14-P12-"
    "TRANSITION-WORK-MATERIALIZATION-RECEIPT"
)

SCHEMA: Final[str] = (
    "WILSY-LEGAL-TRANSITION-WORK-MATERIALIZATION-RECEIPT/V1"
)

_OUTPUT_SCHEMA: Final[str] = (
    "WILSY-LEGAL-TRANSITION-WORK-MATERIALIZATION-OUTPUT/V1"
)

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$"
)

_FINGERPRINT: Final[re.Pattern[str]] = re.compile(
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

_OUTPUT_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "work_item_id",
        "work_item_fingerprint",
    }
)

_RECEIPT_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "receipt_version",
        "receipt_id",
        "tenant_id",
        "case_matter_id",
        "transition_id",
        "transition_fingerprint",
        "workflow_definition_id",
        "target_stage_definition_id",
        "policy_id",
        "policy_revision",
        "policy_fingerprint",
        "outputs",
        "materialized_at",
        "fingerprint",
    }
)


class LegalTransitionWorkMaterializationReceiptError(ValueError):
    """Stable fail-closed receipt-domain validation error."""

    def __init__(
        self,
        code: str,
    ) -> None:
        self.code = code
        super().__init__(code)


def _fail(
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    error = LegalTransitionWorkMaterializationReceiptError(
        code
    )

    if cause is None:
        raise error

    raise error from cause


def _identity(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _fail(
            f"P14_P12_{name.upper()}_INVALID"
        )

    return value


def _tenant(
    value: object,
) -> str:
    tenant = _identity(
        "tenant_id",
        value,
    )

    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail(
            "P14_P12_TENANT_REQUIRED"
        )

    return tenant


def _fingerprint(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or _FINGERPRINT.fullmatch(value) is None
    ):
        _fail(
            f"P14_P12_{name.upper()}_INVALID"
        )

    return value


def _positive_revision(
    value: object,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
    ):
        _fail(
            "P14_P12_POLICY_REVISION_INVALID"
        )

    return value


def _timestamp(
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(
            "P14_P12_MATERIALIZED_AT_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


def _timestamp_text(
    value: datetime,
) -> str:
    return (
        value.astimezone(timezone.utc)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z")
    )


def _parse_timestamp(
    value: object,
) -> datetime:
    if not isinstance(value, str):
        _fail(
            "P14_P12_MATERIALIZED_AT_INVALID"
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
            "P14_P12_MATERIALIZED_AT_INVALID",
            error,
        )

    return _timestamp(parsed)


def _digest(
    payload: Mapping[str, object],
) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha3_512(
        encoded
    ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
)
class LegalTransitionWorkMaterializationOutput:
    """
    One exact work-item output bound into a materialization receipt.

    This is historical output evidence only and grants no work authority.
    """

    work_item_id: str
    work_item_fingerprint: str
    schema: str = _OUTPUT_SCHEMA

    def __post_init__(
        self,
    ) -> None:
        identity = _identity(
            "work_item_id",
            self.work_item_id,
        )

        fingerprint = _fingerprint(
            "work_item_fingerprint",
            self.work_item_fingerprint,
        )

        if self.schema != _OUTPUT_SCHEMA:
            _fail(
                "P14_P12_OUTPUT_SCHEMA_INVALID"
            )

        object.__setattr__(
            self,
            "work_item_id",
            identity,
        )
        object.__setattr__(
            self,
            "work_item_fingerprint",
            fingerprint,
        )

    def to_dict(
        self,
    ) -> dict[str, object]:
        """Serialize exact immutable output evidence."""
        return {
            "schema":
                self.schema,
            "work_item_id":
                self.work_item_id,
            "work_item_fingerprint":
                self.work_item_fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        value: object,
    ) -> "LegalTransitionWorkMaterializationOutput":
        """Hydrate only the exact output schema."""
        if (
            not isinstance(value, Mapping)
            or set(value) != _OUTPUT_FIELDS
        ):
            _fail(
                "P14_P12_OUTPUT_SCHEMA_INVALID"
            )

        return cls(
            schema=cast(
                str,
                value["schema"],
            ),
            work_item_id=cast(
                str,
                value["work_item_id"],
            ),
            work_item_fingerprint=cast(
                str,
                value["work_item_fingerprint"],
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class LegalTransitionWorkMaterializationReceipt:
    """
    Immutable transition/policy/output composition evidence.

    ``receipt_id`` is deterministically derived from the immutable transition
    and selected-policy binding. ``fingerprint`` covers the complete receipt,
    including ordered outputs and materialization timestamp.
    """

    tenant_id: str
    case_matter_id: str
    transition_id: str
    transition_fingerprint: str
    workflow_definition_id: str
    target_stage_definition_id: str
    policy_id: str
    policy_revision: int
    policy_fingerprint: str
    outputs: tuple[
        LegalTransitionWorkMaterializationOutput,
        ...,
    ]
    materialized_at: datetime

    schema: str = SCHEMA
    receipt_version: str = VERSION
    receipt_id: str = ""
    fingerprint: str = ""

    def __post_init__(
        self,
    ) -> None:
        tenant = _tenant(
            self.tenant_id
        )
        matter = _identity(
            "case_matter_id",
            self.case_matter_id,
        )
        transition = _identity(
            "transition_id",
            self.transition_id,
        )
        transition_fp = _fingerprint(
            "transition_fingerprint",
            self.transition_fingerprint,
        )
        workflow = _identity(
            "workflow_definition_id",
            self.workflow_definition_id,
        )
        stage = _identity(
            "target_stage_definition_id",
            self.target_stage_definition_id,
        )
        policy = _identity(
            "policy_id",
            self.policy_id,
        )
        revision = _positive_revision(
            self.policy_revision
        )
        policy_fp = _fingerprint(
            "policy_fingerprint",
            self.policy_fingerprint,
        )
        materialized = _timestamp(
            self.materialized_at
        )

        if self.schema != SCHEMA:
            _fail(
                "P14_P12_SCHEMA_INVALID"
            )

        if self.receipt_version != VERSION:
            _fail(
                "P14_P12_VERSION_INVALID"
            )

        if not isinstance(
            self.outputs,
            tuple,
        ):
            _fail(
                "P14_P12_OUTPUTS_INVALID"
            )

        outputs: list[
            LegalTransitionWorkMaterializationOutput
        ] = []

        seen_ids: set[str] = set()

        for value in self.outputs:
            if type(value) is not LegalTransitionWorkMaterializationOutput:
                _fail(
                    "P14_P12_OUTPUT_INVALID"
                )

            if value.work_item_id in seen_ids:
                _fail(
                    "P14_P12_DUPLICATE_WORK_ITEM_ID"
                )

            seen_ids.add(
                value.work_item_id
            )
            outputs.append(
                value
            )

        output_tuple = tuple(
            outputs
        )

        identity_payload: dict[str, object] = {
            "schema":
                SCHEMA,
            "receipt_version":
                VERSION,
            "tenant_id":
                tenant,
            "case_matter_id":
                matter,
            "transition_id":
                transition,
            "transition_fingerprint":
                transition_fp,
            "workflow_definition_id":
                workflow,
            "target_stage_definition_id":
                stage,
            "policy_id":
                policy,
            "policy_revision":
                revision,
            "policy_fingerprint":
                policy_fp,
        }

        derived_receipt_id = _digest(
            identity_payload
        )

        if self.receipt_id:
            supplied_receipt_id = _fingerprint(
                "receipt_id",
                self.receipt_id,
            )

            if not hmac.compare_digest(
                supplied_receipt_id,
                derived_receipt_id,
            ):
                _fail(
                    "P14_P12_RECEIPT_ID_MISMATCH"
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
            "transition_id",
            transition,
        )
        object.__setattr__(
            self,
            "transition_fingerprint",
            transition_fp,
        )
        object.__setattr__(
            self,
            "workflow_definition_id",
            workflow,
        )
        object.__setattr__(
            self,
            "target_stage_definition_id",
            stage,
        )
        object.__setattr__(
            self,
            "policy_id",
            policy,
        )
        object.__setattr__(
            self,
            "policy_revision",
            revision,
        )
        object.__setattr__(
            self,
            "policy_fingerprint",
            policy_fp,
        )
        object.__setattr__(
            self,
            "outputs",
            output_tuple,
        )
        object.__setattr__(
            self,
            "materialized_at",
            materialized,
        )
        object.__setattr__(
            self,
            "receipt_id",
            derived_receipt_id,
        )

        digest = _digest(
            self.semantic_dict()
        )

        if self.fingerprint:
            supplied_fingerprint = _fingerprint(
                "fingerprint",
                self.fingerprint,
            )

            if not hmac.compare_digest(
                supplied_fingerprint,
                digest,
            ):
                _fail(
                    "P14_P12_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    def semantic_dict(
        self,
    ) -> dict[str, object]:
        """
        Return exact fingerprint-bearing receipt semantics without fingerprint.
        """
        return {
            "schema":
                self.schema,
            "receipt_version":
                self.receipt_version,
            "receipt_id":
                self.receipt_id,
            "tenant_id":
                self.tenant_id,
            "case_matter_id":
                self.case_matter_id,
            "transition_id":
                self.transition_id,
            "transition_fingerprint":
                self.transition_fingerprint,
            "workflow_definition_id":
                self.workflow_definition_id,
            "target_stage_definition_id":
                self.target_stage_definition_id,
            "policy_id":
                self.policy_id,
            "policy_revision":
                self.policy_revision,
            "policy_fingerprint":
                self.policy_fingerprint,
            "outputs": [
                output.to_dict()
                for output in self.outputs
            ],
            "materialized_at":
                _timestamp_text(
                    self.materialized_at
                ),
        }

    def to_dict(
        self,
    ) -> dict[str, object]:
        """Serialize exact immutable receipt truth."""
        return {
            **self.semantic_dict(),
            "fingerprint":
                self.fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        value: object,
    ) -> "LegalTransitionWorkMaterializationReceipt":
        """Strictly hydrate exact receipt truth and verify integrity."""
        if (
            not isinstance(value, Mapping)
            or set(value) != _RECEIPT_FIELDS
        ):
            _fail(
                "P14_P12_SCHEMA_INVALID"
            )

        if value["schema"] != SCHEMA:
            _fail(
                "P14_P12_SCHEMA_INVALID"
            )

        if value["receipt_version"] != VERSION:
            _fail(
                "P14_P12_VERSION_INVALID"
            )

        raw_outputs = value[
            "outputs"
        ]

        if not isinstance(
            raw_outputs,
            (tuple, list),
        ):
            _fail(
                "P14_P12_OUTPUTS_INVALID"
            )

        outputs = tuple(
            LegalTransitionWorkMaterializationOutput.from_dict(
                entry
            )
            for entry in raw_outputs
        )

        return cls(
            schema=cast(
                str,
                value["schema"],
            ),
            receipt_version=cast(
                str,
                value["receipt_version"],
            ),
            receipt_id=cast(
                str,
                value["receipt_id"],
            ),
            tenant_id=cast(
                str,
                value["tenant_id"],
            ),
            case_matter_id=cast(
                str,
                value["case_matter_id"],
            ),
            transition_id=cast(
                str,
                value["transition_id"],
            ),
            transition_fingerprint=cast(
                str,
                value["transition_fingerprint"],
            ),
            workflow_definition_id=cast(
                str,
                value["workflow_definition_id"],
            ),
            target_stage_definition_id=cast(
                str,
                value["target_stage_definition_id"],
            ),
            policy_id=cast(
                str,
                value["policy_id"],
            ),
            policy_revision=cast(
                int,
                value["policy_revision"],
            ),
            policy_fingerprint=cast(
                str,
                value["policy_fingerprint"],
            ),
            outputs=outputs,
            materialized_at=_parse_timestamp(
                value["materialized_at"]
            ),
            fingerprint=cast(
                str,
                value["fingerprint"],
            ),
        )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalTransitionWorkMaterializationOutput",
    "LegalTransitionWorkMaterializationReceipt",
    "LegalTransitionWorkMaterializationReceiptError",
]


# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: legal_transition_work_materialization_receipt.py
# VERSION: v1.0.0-P14-P12-TRANSITION-WORK-MATERIALIZATION-RECEIPT
# AUTHORITY BOUNDARY: immutable historical composition evidence only
# POLICY SELECTION AUTHORITY: NONE
# WORK-ITEM CREATION AUTHORITY: NONE
# HISTORICAL POLICY REINTERPRETATION: FORBIDDEN
# STAGE REENTRY: new transition derives distinct receipt identity
# ASSIGNMENT AUTHORITY: NONE
# SUPERVISION AUTHORITY: NONE
# IAM / PROFESSIONAL AUTHORITY: NONE
# LEGAL-DEADLINE AUTHORITY: NONE
# NOTIFICATION-DELIVERY AUTHORITY: NONE
# AI EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
