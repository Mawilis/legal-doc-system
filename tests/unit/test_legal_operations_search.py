"""Direct certificate for bounded Legal Operations matter search.

TITLE: WILSY OS Legal Operations Matter Search Certificate
VERSION: v1.0.1-L8-5D-LEGAL-OPERATIONS-MATTER-SEARCH-CERT
AUTHORITY: Direct adversarial certification of L8-5D canonical search.
EPITOME: Prove exact and prefix CaseMatter.matter_reference retrieval from
         tenant-scoped L8-5 current models, deterministic ordering and bounds,
         caller-session propagation, current-over-history behavior, strict
         invalid-input rejection, corruption translation, and explicit
         exclusion of client-name, fuzzy, semantic/vector, AI, and financial
         search authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_operations_search.py
COLLABORATION / OWNERSHIP: Certificate for legal_operations_search.py only.
                            P1/P2/L8-0/L8-5 retain lifecycle, persistence,
                            current-selection, and entity-read authority.
                            HTTP/IAM, L8-7 client authority, WILSY AI,
                            Intelligence, and client rendering remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.1-L8-5D-LEGAL-OPERATIONS-MATTER-SEARCH-CERT
           adds constructor-level rejection of mutable search-match containers
           and rebinds the certificate to production v1.0.1.
           2026-09-23 v1.0.0-L8-5D-LEGAL-OPERATIONS-MATTER-SEARCH-CERT
           establishes exact/prefix matter-reference search proofs, casefolded
           comparison, deterministic reference/identity ordering, bounded
           limits, empty absence, closed-matter retrieval, tenant/session
           isolation, corrupt evidence rejection, aggregate self-validation,
           and unsupported-search exclusion.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque tenant/matter references only; no
                             real client, person, credential, provider,
                             embedding, geospatial, or payment data.
TENANT BOUNDARY: Every fake durable read is exact-tenant scoped and every
                 returned model remains bound to the requested tenant.
AUTHORITY BOUNDARY: Certificate only. Search grants no mutation, workflow,
                    queue, AI recommendation, billing, payment, execution, or
                    settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
TRANSACTION BOUNDARY: Caller-owned session markers are forwarded through L8-5;
                      no helper starts, commits, aborts, or retries.
FAIL-CLOSED DECLARATION: Invalid scope/query/mode/limit, corrupt evidence,
                         membership/order drift, or unsupported inference fails.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.domain.legal_operations_read_model import (
    get_entity_read_model,
)
from tools.eos.legal_operations.domain.legal_operations_search import (
    VERSION as PRODUCTION_VERSION,
    LegalOperationsMatterSearchError,
    LegalOperationsMatterSearchMode,
    LegalOperationsMatterSearchResult,
    search_case_matters,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.1-L8-5D-LEGAL-OPERATIONS-MATTER-SEARCH-CERT"
NOW = datetime(2026, 9, 23, 13, 0, tzinfo=timezone.utc)
TENANT = "tenant-l8-5d"
FOREIGN = "tenant-l8-5d-foreign"


class FakeSession:
    """Opaque caller-owned session marker used only for propagation proof."""


def _lookup(document: dict[str, Any], key: str) -> Any:
    """Resolve one Mongo-style dotted key inside a fake durable row."""
    value: Any = document
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


class FakeCollection:
    """Minimal Mongo-compatible collection preserving exact read/session scope."""

    def __init__(self) -> None:
        self.docs: list[dict[str, Any]] = []
        self.calls: list[tuple[str, object, dict[str, object]]] = []

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> dict[str, Any] | None:
        """Return the first exact match while recording caller session."""
        self.calls.append(("find_one", session, deepcopy(query)))
        for document in self.docs:
            if all(_lookup(document, key) == value for key, value in query.items()):
                return deepcopy(document)
        return None

    def find(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> list[dict[str, Any]]:
        """Return all exact matches while recording caller session."""
        self.calls.append(("find", session, deepcopy(query)))
        return [
            deepcopy(document)
            for document in self.docs
            if all(_lookup(document, key) == value for key, value in query.items())
        ]

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: object = None,
    ) -> object:
        """Persist one fake immutable P2 row without extra semantics."""
        self.calls.append(("insert_one", session, deepcopy(document)))
        self.docs.append(deepcopy(cast(dict[str, Any], document)))
        return object()


def _matter(
    matter_id: str,
    reference: str,
    *,
    tenant_id: str = TENANT,
    closed: bool = False,
) -> CaseMatter:
    """Build one canonical matter with optional explicit closed current state."""
    value = CaseMatter(
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        matter_reference=reference,
        opened_at=NOW,
        evidence_reference=f"opened-{matter_id}",
    )
    if not closed:
        return value
    return value.transition_to(
        CaseMatterState.CLOSED,
        evidence_reference=f"closed-{matter_id}",
        occurred_at=NOW + timedelta(minutes=1),
    )


def _persist(
    value: CaseMatter,
    collection: FakeCollection,
    *,
    session: object = None,
) -> None:
    """Persist one canonical CaseMatter snapshot through the real P2 registry."""
    LegalOperationsLifecycleRegistry.create(
        value,
        collection,
        session=session,
    )


def _expect(code: str, operation: Any) -> None:
    """Assert one stable L8-5D failure code."""
    with pytest.raises(LegalOperationsMatterSearchError) as caught:
        operation()
    assert caught.value.code == code
    assert str(caught.value) == code


def test_exact_and_prefix_search_are_case_insensitive_and_deterministic() -> None:
    """EXACT/PREFIX search only canonical matter_reference current values."""
    collection = FakeCollection()
    for value in (
        _matter("matter-z", "CASE-2026-200"),
        _matter("matter-b", "CASE-2026-100B"),
        _matter("matter-a", "case-2026-100A"),
        _matter("matter-x", "OTHER-2026-001"),
    ):
        _persist(value, collection)

    exact = search_case_matters(
        tenant_id=TENANT,
        query="case-2026-200",
        mode=LegalOperationsMatterSearchMode.EXACT,
        lifecycle_collection=collection,
    )
    prefix = search_case_matters(
        tenant_id=TENANT,
        query="CASE-2026-1",
        mode=LegalOperationsMatterSearchMode.PREFIX,
        lifecycle_collection=collection,
    )

    assert [model.entity_identity for model in exact.matches] == ["matter-z"]
    assert [model.entity_identity for model in prefix.matches] == [
        "matter-a",
        "matter-b",
    ]
    assert [cast(CaseMatter, model.current).matter_reference for model in prefix.matches] == [
        "case-2026-100A",
        "CASE-2026-100B",
    ]


def test_result_limit_empty_absence_and_closed_matter_retrieval_are_bounded() -> None:
    """Limit truncates deterministic results; closed matters remain searchable."""
    collection = FakeCollection()
    for value in (
        _matter("matter-c", "CASE-300"),
        _matter("matter-a", "CASE-100", closed=True),
        _matter("matter-b", "CASE-200"),
    ):
        _persist(value, collection)

    limited = search_case_matters(
        tenant_id=TENANT,
        query="CASE-",
        mode=LegalOperationsMatterSearchMode.PREFIX,
        lifecycle_collection=collection,
        limit=2,
    )
    missing = search_case_matters(
        tenant_id=TENANT,
        query="MISSING",
        mode=LegalOperationsMatterSearchMode.EXACT,
        lifecycle_collection=collection,
    )

    assert [model.entity_identity for model in limited.matches] == [
        "matter-a",
        "matter-b",
    ]
    assert cast(CaseMatter, limited.matches[0].current).state is CaseMatterState.CLOSED
    assert missing.matches == ()
    assert missing.to_dict()["matches"] == []


def test_current_over_history_and_tenant_session_isolation_are_preserved() -> None:
    """Search uses L8-0 current models and forwards exact tenant/session scope."""
    collection = FakeCollection()
    session = FakeSession()
    opened = _matter("matter-own", "CASE-OWN")
    closed = opened.transition_to(
        CaseMatterState.CLOSED,
        evidence_reference="matter-close",
        occurred_at=NOW + timedelta(minutes=1),
    )
    _persist(opened, collection, session=session)
    _persist(closed, collection, session=session)
    _persist(_matter("matter-foreign", "CASE-OWN", tenant_id=FOREIGN), collection)
    collection.calls.clear()

    result = search_case_matters(
        tenant_id=TENANT,
        query="case-own",
        mode=LegalOperationsMatterSearchMode.EXACT,
        lifecycle_collection=collection,
        session=session,
    )

    assert [model.entity_identity for model in result.matches] == ["matter-own"]
    assert result.matches[0].current == closed
    assert {value.fingerprint for value in result.matches[0].history} == {
        opened.fingerprint,
        closed.fingerprint,
    }
    assert collection.calls == [
        (
            "find",
            session,
            {
                "tenant_id": TENANT,
                "entity_type": "CaseMatter",
            },
        )
    ]


def test_invalid_scope_query_mode_and_limit_reject_before_persistence() -> None:
    """Malformed search inputs fail before any durable read."""
    collection = FakeCollection()

    for code, operation in (
        (
            "L8_5D_TENANT_INVALID",
            lambda: search_case_matters(
                tenant_id="global",
                query="CASE",
                mode=LegalOperationsMatterSearchMode.PREFIX,
                lifecycle_collection=collection,
            ),
        ),
        (
            "L8_5D_QUERY_INVALID",
            lambda: search_case_matters(
                tenant_id=TENANT,
                query=" CASE",
                mode=LegalOperationsMatterSearchMode.PREFIX,
                lifecycle_collection=collection,
            ),
        ),
        (
            "L8_5D_MODE_INVALID",
            lambda: search_case_matters(
                tenant_id=TENANT,
                query="CASE",
                mode=cast(Any, "PREFIX"),
                lifecycle_collection=collection,
            ),
        ),
        (
            "L8_5D_LIMIT_INVALID",
            lambda: search_case_matters(
                tenant_id=TENANT,
                query="CASE",
                mode=LegalOperationsMatterSearchMode.PREFIX,
                lifecycle_collection=collection,
                limit=101,
            ),
        ),
    ):
        _expect(code, operation)
    assert collection.calls == []


def test_corrupt_l8_5_source_fails_whole_search_without_partial_results() -> None:
    """P2/L8-5 corruption is translated and never becomes partial search output."""
    collection = FakeCollection()
    _persist(_matter("matter-a", "CASE-A"), collection)
    _persist(_matter("matter-b", "CASE-B"), collection)
    row = next(
        item for item in collection.docs if item["entity_identity"] == "matter-a"
    )
    row["p1_fingerprint"] = "f" * 128

    with pytest.raises(LegalOperationsMatterSearchError) as caught:
        search_case_matters(
            tenant_id=TENANT,
            query="CASE-",
            mode=LegalOperationsMatterSearchMode.PREFIX,
            lifecycle_collection=collection,
        )

    assert caught.value.code == "L8_5D_READ_MODEL_UNAVAILABLE"
    assert caught.value.__cause__ is not None


def test_public_result_rejects_mutable_matches_container() -> None:
    """Frozen result semantics reject a mutable list supplied by a caller."""
    collection = FakeCollection()
    _persist(_matter("matter-a", "CASE-A"), collection)
    model = get_entity_read_model(
        tenant_id=TENANT,
        entity_type="CaseMatter",
        entity_identity="matter-a",
        lifecycle_collection=collection,
    )

    _expect(
        "L8_5D_MATCHES_INVALID",
        lambda: LegalOperationsMatterSearchResult(
            tenant_id=TENANT,
            query="CASE-A",
            mode=LegalOperationsMatterSearchMode.EXACT,
            limit=25,
            matches=cast(Any, [model]),
        ),
    )


def test_public_result_self_validation_and_unsupported_search_exclusion() -> None:
    """Public result cannot admit wrong membership or unsupported search authority."""
    collection = FakeCollection()
    _persist(_matter("matter-a", "CASE-A"), collection)
    model = get_entity_read_model(
        tenant_id=TENANT,
        entity_type="CaseMatter",
        entity_identity="matter-a",
        lifecycle_collection=collection,
    )

    _expect(
        "L8_5D_RESULT_MEMBERSHIP_INVALID",
        lambda: LegalOperationsMatterSearchResult(
            tenant_id=TENANT,
            query="OTHER",
            mode=LegalOperationsMatterSearchMode.EXACT,
            limit=25,
            matches=(model,),
        ),
    )

    result = search_case_matters(
        tenant_id=TENANT,
        query="CASE",
        mode=LegalOperationsMatterSearchMode.PREFIX,
        lifecycle_collection=collection,
    )
    assert set(result.to_dict()) == {
        "tenant_id",
        "query",
        "mode",
        "limit",
        "matches",
    }
    documentation = (search_case_matters.__doc__ or "").casefold()
    for excluded in (
        "client-name",
        "fuzzy",
        "semantic/vector",
        "ai-ranked",
        "queue",
        "billing",
        "financial",
    ):
        assert excluded in documentation
    serialized = str(result.to_dict()).casefold()
    for forbidden in (
        "client_name",
        "embedding",
        "score",
        "payment",
        "settlement",
        "invoice",
    ):
        assert forbidden not in serialized

    assert PRODUCTION_VERSION == "v1.0.1-L8-5D-LEGAL-OPERATIONS-MATTER-SEARCH"
    assert VERSION == "v1.0.1-L8-5D-LEGAL-OPERATIONS-MATTER-SEARCH-CERT"


# ARTIFACT: test_legal_operations_search.py
# VERSION: v1.0.1-L8-5D-LEGAL-OPERATIONS-MATTER-SEARCH-CERT
# AUTHORITY BOUNDARY: direct L8-5D canonical matter-reference search certificate only
# TENANT POSTURE: exact tenant/session-scoped CaseMatter current read models only
# FAIL-CLOSED POSTURE: invalid input/evidence/membership rejects without fuzzy, client-name, AI, or partial fallback
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
