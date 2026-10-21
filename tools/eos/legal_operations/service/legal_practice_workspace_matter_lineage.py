"""G79-R12 workspace matter lineage.

Pure identification and consistency checks only. This module does
NOT establish practitioner authorization, ethical-wall clearance,
tenancy, currentness, or permission to disclose content.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SUPPORTED_ENTITY_TYPES = frozenset({
    "CaseMatter",
    "LegalInstruction",
    "ProcessDocument",
    "ServiceAttempt",
    "ServiceExecution",
    "ReturnOfService",
})

_MATTER_REFERENCE_FIELDS = (
    "case_matter_id",
    "matter_id",
)

class MatterLineageError(ValueError):
    """A workspace record has missing or ambiguous matter lineage."""


def _require_reference(value: Any) -> str:
    if not isinstance(value, str):
        raise MatterLineageError(
            "G79_MATTER_LINEAGE_INVALID"
        )
    if not value or value != value.strip():
        raise MatterLineageError(
            "G79_MATTER_LINEAGE_INVALID"
        )
    return value


def require_matter_lineage(
    *,
    entity_type: str,
    row: Mapping[str, Any],
) -> str:
    """Validate one already-projected record's matter-reference fields.

    A matching reference is lineage metadata, not an access grant.
    The caller must independently verify the row's actual canonical
    parent relationship and all current confidentiality authority.
    """
    if entity_type not in SUPPORTED_ENTITY_TYPES:
        raise MatterLineageError(
            "G79_ENTITY_LINEAGE_UNSUPPORTED"
        )

    if not isinstance(row, Mapping):
        raise MatterLineageError(
            "G79_MATTER_LINEAGE_INVALID"
        )

    references = [
        _require_reference(row[field])
        for field in _MATTER_REFERENCE_FIELDS
        if field in row
    ]

    if not references:
        raise MatterLineageError(
            "G79_MATTER_LINEAGE_UNAVAILABLE"
        )

    if len(set(references)) != 1:
        raise MatterLineageError(
            "G79_MATTER_LINEAGE_AMBIGUOUS"
        )

    return references[0]


def require_uniform_matter_lineage(
    *,
    entity_type: str,
    rows: Sequence[Mapping[str, Any]],
) -> str | None:
    """Validate that a supplied group has one unambiguous matter.

    This must not be used to justify a tenant-wide read or
    to convert identifying metadata into disclosure authority.
    """
    matter: str | None = None

    for row in rows:
        current = require_matter_lineage(
            entity_type=entity_type,
            row=row,
        )
        if matter is None:
            matter = current
        elif current != matter:
            raise MatterLineageError(
                "G79_MATTER_LINEAGE_CROSS_MATTER"
            )

    return matter
