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


def resolve_workspace_canonical_parents(
    *,
    matters: Sequence[Mapping[str, Any]],
    instructions: Sequence[Mapping[str, Any]],
    documents: Sequence[Mapping[str, Any]],
    attempts: Sequence[Mapping[str, Any]],
    executions: Sequence[Mapping[str, Any]],
    returns: Sequence[Mapping[str, Any]],
) -> dict[str, tuple[str, ...]]:
    """Resolve canonical parent chains from one trusted snapshot.

    Inputs must be canonical tenant-scoped lifecycle projections
    obtained by the caller under the same active transaction.
    This does NOT confer disclosure authority.
    """
    def ident(row: Mapping[str, Any], name: str) -> str:
        if not isinstance(row, Mapping) or name not in row:
            raise MatterLineageError("G79_CANONICAL_PARENT_UNAVAILABLE")
        return _require_reference(row[name])

    def unique(rows: Sequence[Mapping[str, Any]], name: str):
        indexed: dict[str, Mapping[str, Any]] = {}
        for row in rows:
            key = ident(row, name)
            if key in indexed:
                raise MatterLineageError("G79_CANONICAL_ID_DUPLICATED")
            indexed[key] = row
        return indexed

    m = unique(matters, "case_matter_id")
    i = unique(instructions, "instruction_id")
    d = unique(documents, "document_id")
    a = unique(attempts, "attempt_id")
    e = unique(executions, "service_execution_id")
    unique(returns, "return_id")

    def matter(value: str) -> str:
        if value not in m:
            raise MatterLineageError("G79_CANONICAL_MATTER_MISSING")
        return value

    def document(value: str) -> str:
        parent = d.get(value)
        if parent is None:
            raise MatterLineageError("G79_CANONICAL_DOCUMENT_MISSING")
        return matter(ident(parent, "case_matter_id"))

    def instruction(value: str) -> str:
        item = i.get(value)
        if item is None:
            raise MatterLineageError("G79_CANONICAL_INSTRUCTION_MISSING")
        direct = matter(ident(item, "case_matter_id"))
        if document(ident(item, "document_id")) != direct:
            raise MatterLineageError("G79_PARENT_MISMATCH")
        return direct

    def attempt(value: str) -> str:
        item = a.get(value)
        if item is None:
            raise MatterLineageError("G79_CANONICAL_ATTEMPT_MISSING")
        inst = ident(item, "instruction_id")
        doc = ident(item, "document_id")
        parent = instruction(inst)
        if document(doc) != parent or ident(i[inst], "document_id") != doc:
            raise MatterLineageError("G79_PARENT_MISMATCH")
        return parent

    def execution(value: str) -> str:
        item = e.get(value)
        if item is None:
            raise MatterLineageError("G79_CANONICAL_EXECUTION_MISSING")
        attempt_id = ident(item, "attempt_id")
        parent = attempt(attempt_id)
        for key in ("instruction_id", "document_id"):
            if ident(item, key) != ident(a[attempt_id], key):
                raise MatterLineageError("G79_PARENT_MISMATCH")
        return parent

    def returned(item: Mapping[str, Any]) -> str:
        execution_id = ident(item, "service_execution_id")
        parent = execution(execution_id)
        for key in ("attempt_id", "instruction_id", "document_id"):
            if ident(item, key) != ident(e[execution_id], key):
                raise MatterLineageError("G79_PARENT_MISMATCH")
        return parent

    return {
        "matters": tuple(matter(ident(row, "case_matter_id")) for row in matters),
        "instructions": tuple(instruction(ident(row, "instruction_id"))
                              for row in instructions),
        "documents": tuple(document(ident(row, "document_id"))
                           for row in documents),
        "attempts": tuple(attempt(ident(row, "attempt_id"))
                          for row in attempts),
        "executions": tuple(execution(ident(row, "service_execution_id"))
                            for row in executions),
        "returns": tuple(returned(row) for row in returns),
    }
