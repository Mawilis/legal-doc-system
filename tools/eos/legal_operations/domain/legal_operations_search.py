"""Bounded canonical search for Legal Operations matters.

TITLE: WILSY OS Legal Operations Matter Search
VERSION: v1.0.1-L8-5D-LEGAL-OPERATIONS-MATTER-SEARCH
AUTHORITY: Wilsy OS Legal Operations deterministic read-only search projection.
EPITOME: Search only canonical CaseMatter.matter_reference values from L8-5
         current read models using exact or prefix matching, with explicit
         tenant scope, deterministic ordering, bounded result limits, and no
         fuzzy, client-name, workflow, AI, or financial inference.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_operations_search.py
COLLABORATION / OWNERSHIP: P1 owns CaseMatter truth; P2 owns durable snapshots;
                            L8-0 owns current-state selection; L8-5 owns entity
                            read models; L8-5D owns bounded retrieval semantics
                            only. HTTP/IAM, client authority, WILSY AI,
                            Intelligence, and client rendering remain separate
                            bounded gates.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.1-L8-5D-LEGAL-OPERATIONS-MATTER-SEARCH
           makes the exported search result require an immutable tuple for
           matches; search semantics and authority boundaries are unchanged.
           2026-09-23 v1.0.0-L8-5D-LEGAL-OPERATIONS-MATTER-SEARCH
           establishes canonical matter-reference search with exact/prefix
           modes, NFC input validation, case-insensitive comparison,
           deterministic reference/identity ordering, explicit result bounds,
           tenant/session propagation, and deliberate exclusion of client-name,
           fuzzy, semantic/vector, urgency, queue, billing, and financial truth.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Search consumes only opaque canonical matter
                             references already visible through tenant-scoped
                             L8-5 reads. No credentials, provider payloads,
                             embeddings, geospatial data, or new person/client
                             identity are accepted.
TENANT BOUNDARY: Every search enumerates CaseMatter models through exact-tenant
                 L8-5 scope and revalidates returned tenant/type/current values.
AUTHORITY BOUNDARY: Retrieval projection only. Search does not authorize,
                    mutate, register, close, receive, allocate, attempt, serve,
                    return, bill, invoice, pay, execute, settle, or recommend.
FINANCIAL AUTHORITY BOUNDARY: Search contains no payment or settlement truth;
                              Kennel EOS exclusively owns financial execution
                              and settlement.
TRANSACTION BOUNDARY: Caller-owned sessions are forwarded unchanged to L8-5.
                      This module starts, commits, aborts, and retries nothing.
FAIL-CLOSED DECLARATION: Invalid tenant/query/mode/limit, malformed read models,
                         tenant/type drift, or upstream evidence failure rejects
                         without fallback, fuzzy guessing, or partial results.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re
import unicodedata
from typing import Any, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
)
from tools.eos.legal_operations.domain.legal_operations_read_model import (
    LegalOperationsEntityReadModel,
    LegalOperationsReadModelError,
    list_entity_read_models,
)


VERSION: Final[str] = "v1.0.1-L8-5D-LEGAL-OPERATIONS-MATTER-SEARCH"
_MAX_QUERY_LENGTH: Final[int] = 256
_MAX_RESULTS: Final[int] = 100
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "global_root", "root", "master", "*"})


class LegalOperationsMatterSearchMode(StrEnum):
    """Supported deterministic matter-reference search modes only."""

    EXACT = "EXACT"
    PREFIX = "PREFIX"


class LegalOperationsMatterSearchError(RuntimeError):
    """Stable L8-5D search failure with no mutation or AI authority."""

    def __init__(self, code: str) -> None:
        """Create one bounded search failure code without exposing internals."""
        self.code = code
        super().__init__(code)


def _fail(
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one stable L8-5D error while retaining a governed root cause."""
    error = LegalOperationsMatterSearchError(code)
    if cause is None:
        raise error
    raise error from cause


def _tenant(value: object) -> str:
    """Require one canonical explicit tenant and reject pseudo/global aliases."""
    if not isinstance(value, str) or _IDENTITY.fullmatch(value) is None:
        _fail("L8_5D_TENANT_INVALID")
    tenant_id = cast(str, value)
    if tenant_id.casefold() in _FORBIDDEN_TENANTS:
        _fail("L8_5D_TENANT_INVALID")
    return tenant_id


def _query(value: object) -> str:
    """Require bounded, trimmed, NFC-normalized matter-reference search text."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > _MAX_QUERY_LENGTH
        or unicodedata.normalize("NFC", value) != value
    ):
        _fail("L8_5D_QUERY_INVALID")
    return cast(str, value)


def _mode(value: object) -> LegalOperationsMatterSearchMode:
    """Require one explicit supported search mode without fuzzy fallback."""
    if type(value) is not LegalOperationsMatterSearchMode:
        _fail("L8_5D_MODE_INVALID")
    return cast(LegalOperationsMatterSearchMode, value)


def _limit(value: object) -> int:
    """Require an explicit positive result bound no greater than 100."""
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= _MAX_RESULTS:
        _fail("L8_5D_LIMIT_INVALID")
    return value


def _reference(model: LegalOperationsEntityReadModel, tenant_id: str) -> str:
    """Return one canonical current CaseMatter reference after exact revalidation."""
    if model.tenant_id != tenant_id:
        _fail("L8_5D_TENANT_MISMATCH")
    if model.entity_type != "CaseMatter" or type(model.current) is not CaseMatter:
        _fail("L8_5D_MATTER_MODEL_INVALID")
    current = cast(CaseMatter, model.current)
    if current.tenant_id != tenant_id or current.case_matter_id != model.entity_identity:
        _fail("L8_5D_MATTER_MODEL_INVALID")
    reference = current.matter_reference
    if (
        not isinstance(reference, str)
        or not reference
        or reference != reference.strip()
        or unicodedata.normalize("NFC", reference) != reference
    ):
        _fail("L8_5D_MATTER_REFERENCE_INVALID")
    return reference


@dataclass(frozen=True, slots=True)
class LegalOperationsMatterSearchResult:
    """Immutable bounded result set for canonical matter-reference retrieval.

    Results contain only L8-5 current-plus-history CaseMatter models whose
    current matter_reference satisfies the explicit query/mode. Search order is
    deterministic by casefolded matter_reference and canonical matter identity.
    Empty results are valid absence. This projection grants no client identity,
    workflow, queue, AI recommendation, mutation, billing, or financial
    authority.
    """

    tenant_id: str
    query: str
    mode: LegalOperationsMatterSearchMode
    limit: int
    matches: tuple[LegalOperationsEntityReadModel, ...]

    def __post_init__(self) -> None:
        """Revalidate every exported result against the complete search contract."""
        tenant = _tenant(self.tenant_id)
        query = _query(self.query)
        mode = _mode(self.mode)
        limit = _limit(self.limit)
        if type(self.matches) is not tuple:
            _fail("L8_5D_MATCHES_INVALID")
        if len(self.matches) > limit:
            _fail("L8_5D_RESULT_LIMIT_EXCEEDED")

        normalized_query = query.casefold()
        prior_key: tuple[str, str] | None = None
        for model in self.matches:
            reference = _reference(model, tenant)
            normalized_reference = reference.casefold()
            if mode is LegalOperationsMatterSearchMode.EXACT:
                if normalized_reference != normalized_query:
                    _fail("L8_5D_RESULT_MEMBERSHIP_INVALID")
            elif not normalized_reference.startswith(normalized_query):
                _fail("L8_5D_RESULT_MEMBERSHIP_INVALID")
            key = (normalized_reference, model.entity_identity)
            if prior_key is not None and key < prior_key:
                _fail("L8_5D_RESULT_ORDER_INVALID")
            prior_key = key

    def to_dict(self) -> dict[str, object]:
        """Serialize bounded search metadata and canonical L8-5 matter models."""
        return {
            "tenant_id": self.tenant_id,
            "query": self.query,
            "mode": self.mode.value,
            "limit": self.limit,
            "matches": [model.to_dict() for model in self.matches],
        }


def search_case_matters(
    *,
    tenant_id: str,
    query: str,
    mode: LegalOperationsMatterSearchMode,
    lifecycle_collection: Any,
    limit: int = 25,
    session: Any = None,
) -> LegalOperationsMatterSearchResult:
    """Search canonical CaseMatter.matter_reference within one tenant.

    L8-5 enumerates deterministic current-plus-history CaseMatter models under
    the exact tenant and caller-owned session. L8-5D compares only the current
    canonical matter_reference using case-insensitive EXACT or PREFIX semantics,
    sorts by normalized reference then canonical matter identity, and returns
    at most the explicit bounded limit.

    The function intentionally provides no client-name, fuzzy, substring,
    semantic/vector, AI-ranked, queue, urgency, billing, or financial search.
    Empty matches are valid. Any upstream read-model failure rejects the whole
    search instead of returning partial or guessed results.
    """
    tenant = _tenant(tenant_id)
    search_query = _query(query)
    search_mode = _mode(mode)
    result_limit = _limit(limit)

    try:
        models = list_entity_read_models(
            tenant_id=tenant,
            entity_type="CaseMatter",
            lifecycle_collection=lifecycle_collection,
            session=session,
        )
    except LegalOperationsReadModelError as error:
        _fail("L8_5D_READ_MODEL_UNAVAILABLE", error)

    normalized_query = search_query.casefold()
    matching: list[tuple[str, str, LegalOperationsEntityReadModel]] = []
    for model in models:
        reference = _reference(model, tenant)
        normalized_reference = reference.casefold()
        if search_mode is LegalOperationsMatterSearchMode.EXACT:
            is_match = normalized_reference == normalized_query
        else:
            is_match = normalized_reference.startswith(normalized_query)
        if is_match:
            matching.append(
                (normalized_reference, model.entity_identity, model)
            )

    matching.sort(key=lambda item: (item[0], item[1]))
    matches = tuple(item[2] for item in matching[:result_limit])
    return LegalOperationsMatterSearchResult(
        tenant_id=tenant,
        query=search_query,
        mode=search_mode,
        limit=result_limit,
        matches=matches,
    )


__all__ = [
    "VERSION",
    "LegalOperationsMatterSearchError",
    "LegalOperationsMatterSearchMode",
    "LegalOperationsMatterSearchResult",
    "search_case_matters",
]


# ARTIFACT: legal_operations_search.py
# VERSION: v1.0.1-L8-5D-LEGAL-OPERATIONS-MATTER-SEARCH
# AUTHORITY BOUNDARY: bounded canonical CaseMatter.matter_reference retrieval only; no AI, mutation, client, or financial authority
# TENANT POSTURE: exact L8-5 tenant-scoped CaseMatter current read models only
# FAIL-CLOSED POSTURE: invalid scope/query/mode/limit/evidence rejects without fuzzy, client-name, or partial fallback
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
