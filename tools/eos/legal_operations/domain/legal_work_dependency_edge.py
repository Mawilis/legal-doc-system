"""
TITLE: WILSY OS Legal Work Dependency Edge
VERSION: v1.0.0-P14-R8-WORK-DEPENDENCY-EDGE
AUTHORITY: Wilsy OS Core Governance / Legal Operations

PURPOSE:
    Represent one immutable runtime dependency relation between an exact
    predecessor work item and exact successor work item emitted under one
    immutable transition-work materialization receipt.

CRITICAL SEPARATIONS:
    Dependency edge is not dependency satisfaction.
    Dependency satisfaction is not work completion.
    Edge existence is not a mutable blocked flag.
    This artifact does not claim a global runtime DAG.

TENANT BOUNDARY:
    Exact tenant scope is part of every durable identity.

AUTHORITY BOUNDARY:
    Dependency topology evidence only. No completion, satisfaction, assignment,
    supervision, IAM, professional, legal-event, notification, AI or financial
    authority.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive for financial execution.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
import re
from typing import Final, Mapping, NoReturn


VERSION: Final[str] = (
    "v1.0.0-P14-R8-WORK-DEPENDENCY-EDGE"
)

SCHEMA: Final[str] = (
    "WILSY-LEGAL-WORK-DEPENDENCY-EDGE/V1"
)

_FINGERPRINT_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9a-f]{128}$"
)

_PSEUDO_TENANTS: Final[frozenset[str]] = frozenset(
    {
        "default",
        "global",
        "global_root",
        "root",
        "master",
        "*",
    }
)


class LegalWorkDependencyEdgeError(
    ValueError
):
    """Stable fail-closed dependency-edge domain error."""

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
    raise LegalWorkDependencyEdgeError(
        code
    )


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > 320
    ):
        _fail(
            f"P14_R8_{name.upper()}_INVALID"
        )

    return value


def _tenant(
    value: object,
) -> str:
    tenant = _text(
        "tenant_id",
        value,
    )

    if tenant.casefold() in _PSEUDO_TENANTS:
        _fail(
            "P14_R8_TENANT_REQUIRED"
        )

    return tenant


def _fingerprint(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or _FINGERPRINT_RE.fullmatch(
            value
        )
        is None
    ):
        _fail(
            f"P14_R8_{name.upper()}_FINGERPRINT_INVALID"
        )

    return value


def _digest(
    payload: object,
) -> str:
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode(
        "utf-8"
    )

    return hashlib.sha3_512(
        raw
    ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
)
class LegalWorkDependencyEdge:
    """
    Immutable receipt-bound runtime predecessor→successor relation.

    This class records topology only. It intentionally does not represent
    satisfaction, completion, release, blocked state or command authority.
    """

    tenant_id: str
    case_matter_id: str

    source_materialization_receipt_id: str
    source_materialization_receipt_fingerprint: str

    predecessor_work_item_id: str
    predecessor_work_item_fingerprint: str

    successor_work_item_id: str
    successor_work_item_fingerprint: str

    schema: str = SCHEMA
    edge_version: str = VERSION
    dependency_edge_id: str = ""
    fingerprint: str = ""

    def __post_init__(
        self,
    ) -> None:
        tenant = _tenant(
            self.tenant_id
        )

        matter = _text(
            "case_matter_id",
            self.case_matter_id,
        )

        receipt_id = _fingerprint(
            "source_materialization_receipt_id",
            self.source_materialization_receipt_id,
        )

        receipt_fp = _fingerprint(
            "source_materialization_receipt",
            self.source_materialization_receipt_fingerprint,
        )

        predecessor_id = _text(
            "predecessor_work_item_id",
            self.predecessor_work_item_id,
        )

        predecessor_fp = _fingerprint(
            "predecessor_work_item",
            self.predecessor_work_item_fingerprint,
        )

        successor_id = _text(
            "successor_work_item_id",
            self.successor_work_item_id,
        )

        successor_fp = _fingerprint(
            "successor_work_item",
            self.successor_work_item_fingerprint,
        )

        if predecessor_id == successor_id:
            _fail(
                "P14_R8_SELF_DEPENDENCY"
            )

        if self.schema != SCHEMA:
            _fail(
                "P14_R8_SCHEMA_INVALID"
            )

        if self.edge_version != VERSION:
            _fail(
                "P14_R8_VERSION_INVALID"
            )

        identity_payload: dict[
            str,
            object,
        ] = {
            "schema":
                SCHEMA,
            "edge_version":
                VERSION,
            "tenant_id":
                tenant,
            "case_matter_id":
                matter,
            "source_materialization_receipt_id":
                receipt_id,
            "source_materialization_receipt_fingerprint":
                receipt_fp,
            "predecessor_work_item_id":
                predecessor_id,
            "predecessor_work_item_fingerprint":
                predecessor_fp,
            "successor_work_item_id":
                successor_id,
            "successor_work_item_fingerprint":
                successor_fp,
        }

        derived_id = _digest(
            identity_payload
        )

        if self.dependency_edge_id:
            supplied_id = _fingerprint(
                "dependency_edge_id",
                self.dependency_edge_id,
            )

            if not hmac.compare_digest(
                supplied_id,
                derived_id,
            ):
                _fail(
                    "P14_R8_DEPENDENCY_EDGE_ID_MISMATCH"
                )

        semantic_payload = dict(
            identity_payload
        )

        semantic_payload[
            "dependency_edge_id"
        ] = derived_id

        derived_fingerprint = _digest(
            semantic_payload
        )

        if self.fingerprint:
            supplied_fingerprint = _fingerprint(
                "fingerprint",
                self.fingerprint,
            )

            if not hmac.compare_digest(
                supplied_fingerprint,
                derived_fingerprint,
            ):
                _fail(
                    "P14_R8_FINGERPRINT_MISMATCH"
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
            "source_materialization_receipt_id",
            receipt_id,
        )
        object.__setattr__(
            self,
            "source_materialization_receipt_fingerprint",
            receipt_fp,
        )
        object.__setattr__(
            self,
            "predecessor_work_item_id",
            predecessor_id,
        )
        object.__setattr__(
            self,
            "predecessor_work_item_fingerprint",
            predecessor_fp,
        )
        object.__setattr__(
            self,
            "successor_work_item_id",
            successor_id,
        )
        object.__setattr__(
            self,
            "successor_work_item_fingerprint",
            successor_fp,
        )
        object.__setattr__(
            self,
            "dependency_edge_id",
            derived_id,
        )
        object.__setattr__(
            self,
            "fingerprint",
            derived_fingerprint,
        )

    def semantic_dict(
        self,
    ) -> dict[str, object]:
        """Return exact immutable semantic dependency-edge truth."""
        return {
            "schema":
                self.schema,
            "edge_version":
                self.edge_version,
            "tenant_id":
                self.tenant_id,
            "case_matter_id":
                self.case_matter_id,
            "source_materialization_receipt_id":
                self.source_materialization_receipt_id,
            "source_materialization_receipt_fingerprint":
                self.source_materialization_receipt_fingerprint,
            "predecessor_work_item_id":
                self.predecessor_work_item_id,
            "predecessor_work_item_fingerprint":
                self.predecessor_work_item_fingerprint,
            "successor_work_item_id":
                self.successor_work_item_id,
            "successor_work_item_fingerprint":
                self.successor_work_item_fingerprint,
        }

    def to_dict(
        self,
    ) -> dict[str, object]:
        """Serialize exact immutable durable representation."""
        value = self.semantic_dict()

        value[
            "dependency_edge_id"
        ] = self.dependency_edge_id

        value[
            "fingerprint"
        ] = self.fingerprint

        return value

    @classmethod
    def from_dict(
        cls,
        raw: Mapping[
            str,
            object,
        ],
    ) -> "LegalWorkDependencyEdge":
        """Strictly hydrate one exact durable dependency edge."""
        if not isinstance(
            raw,
            Mapping,
        ):
            _fail(
                "P14_R8_DOCUMENT_INVALID"
            )

        expected = {
            "schema",
            "edge_version",
            "tenant_id",
            "case_matter_id",
            "source_materialization_receipt_id",
            "source_materialization_receipt_fingerprint",
            "predecessor_work_item_id",
            "predecessor_work_item_fingerprint",
            "successor_work_item_id",
            "successor_work_item_fingerprint",
            "dependency_edge_id",
            "fingerprint",
        }

        actual = set(
            raw
        )

        if actual != expected:
            _fail(
                "P14_R8_DOCUMENT_FIELDS_INVALID"
            )

        try:
            value = cls(
                schema=raw["schema"],  # type: ignore[arg-type]
                edge_version=raw["edge_version"],  # type: ignore[arg-type]
                tenant_id=raw["tenant_id"],  # type: ignore[arg-type]
                case_matter_id=raw["case_matter_id"],  # type: ignore[arg-type]
                source_materialization_receipt_id=raw[
                    "source_materialization_receipt_id"
                ],  # type: ignore[arg-type]
                source_materialization_receipt_fingerprint=raw[
                    "source_materialization_receipt_fingerprint"
                ],  # type: ignore[arg-type]
                predecessor_work_item_id=raw[
                    "predecessor_work_item_id"
                ],  # type: ignore[arg-type]
                predecessor_work_item_fingerprint=raw[
                    "predecessor_work_item_fingerprint"
                ],  # type: ignore[arg-type]
                successor_work_item_id=raw[
                    "successor_work_item_id"
                ],  # type: ignore[arg-type]
                successor_work_item_fingerprint=raw[
                    "successor_work_item_fingerprint"
                ],  # type: ignore[arg-type]
                dependency_edge_id=raw[
                    "dependency_edge_id"
                ],  # type: ignore[arg-type]
                fingerprint=raw[
                    "fingerprint"
                ],  # type: ignore[arg-type]
            )
        except LegalWorkDependencyEdgeError:
            raise
        except (
            TypeError,
            KeyError,
            ValueError,
        ) as error:
            raise LegalWorkDependencyEdgeError(
                "P14_R8_DOCUMENT_INVALID"
            ) from error

        if value.to_dict() != dict(
            raw
        ):
            _fail(
                "P14_R8_DOCUMENT_CORRELATION_INVALID"
            )

        return value


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_work_dependency_edge.py
# VERSION: v1.0.0-P14-R8-WORK-DEPENDENCY-EDGE
# DEPENDENCY EDGE != DEPENDENCY SATISFACTION
# DEPENDENCY SATISFACTION != WORK COMPLETION
# BLOCKED STATE: NOT STORED
# GLOBAL DAG AUTHORITY: NOT CLAIMED
# ASSIGNMENT / SUPERVISION / IAM AUTHORITY: NONE
# NOTIFICATION / AI / LEGAL-EVENT AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
