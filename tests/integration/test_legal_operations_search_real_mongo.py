"""Host-backed certificate for bounded Legal Operations matter search.

TITLE: WILSY OS Legal Operations Matter Search Real-Mongo Certificate
VERSION: v1.0.1-L8-5D-LEGAL-OPERATIONS-MATTER-SEARCH-RM-CERT
AUTHORITY: Host-backed certification of canonical L8-5D matter search.
EPITOME: Prove exact and prefix CaseMatter.matter_reference retrieval on the
         real Mongo replica set with deterministic ordering and bounds,
         snapshot-session compatibility, current-over-history behavior, foreign
         isolation, corruption rejection, and explicit exclusion of client-name,
         fuzzy, semantic/vector, AI, and financial search authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_search_real_mongo.py
COLLABORATION / OWNERSHIP: Host certificate for L8-5D only. P1/P2/L8-0/L8-5
                            remain lifecycle, persistence, current-selection,
                            and entity-read authorities. HTTP/IAM, L8-7 client
                            authority, WILSY AI, Intelligence, and client
                            rendering remain separate bounded gates.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.1-L8-5D-LEGAL-OPERATIONS-MATTER-SEARCH-RM-CERT
           rebinds the host certificate to the immutable-result production
           patch; Mongo/search/runtime assertions are unchanged.
           2026-09-23 v1.0.0-L8-5D-LEGAL-OPERATIONS-MATTER-SEARCH-RM-CERT
           establishes real replica-set proof for exact/prefix canonical
           matter-reference search, deterministic ordering/limits, empty
           absence, closed-matter retrieval, caller snapshot-session
           propagation, foreign isolation, corruption rejection, bounded
           serialization, and production-version binding.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenants and opaque matter
                             references only; no real client/person, credential,
                             provider, embedding, geospatial, or payment data.
TENANT BOUNDARY: All writes and searches bind exact UUID-isolated tenants;
                 foreign durable evidence cannot satisfy a local search.
AUTHORITY BOUNDARY: Certificate and retrieval projection only. Search grants no
                    mutation, workflow, queue, AI recommendation, billing,
                    payment, execution, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
TRANSACTION BOUNDARY: The certificate owns Mongo sessions/transactions; L8-5D
                      forwards them and never starts, commits, aborts, or retries.
FAIL-CLOSED DECLARATION: Wrong/unavailable Mongo runtime, invalid search input,
                         corrupt evidence, tenant drift, or unsupported search
                         behavior fails certification without fallback.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import sys
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.domain.legal_operations_search import (
    VERSION as PRODUCTION_VERSION,
    LegalOperationsMatterSearchError,
    LegalOperationsMatterSearchMode,
    search_case_matters,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION,
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.1-L8-5D-LEGAL-OPERATIONS-MATTER-SEARCH-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 23, 13, 30, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Yield one verified writable isolated database; runtime failure is fatal."""
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        retryWrites=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(
                f"L8_5D_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(
                f"L8_5D_MONGO_REPLICA_SET_MISMATCH:{hello.get('setName')!r}"
            )
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_5D_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")

        database = client[f"legal_ops_l8_5d_search_{uuid.uuid4().hex}"]
        lifecycle = database.get_collection(
            COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        yield {
            "client": client,
            "database": database,
            "lifecycle": lifecycle,
        }
    finally:
        active_error = sys.exc_info()[0] is not None
        try:
            if database is not None:
                try:
                    client.drop_database(database.name)
                except PyMongoError:
                    if not active_error:
                        raise
        finally:
            client.close()


def _matter(
    tenant_id: str,
    matter_id: str,
    reference: str,
    *,
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


def _persist(value: CaseMatter, collection: Any, *, session: Any = None) -> None:
    """Persist one exact CaseMatter snapshot through canonical P2."""
    LegalOperationsLifecycleRegistry.create(
        value,
        collection,
        session=session,
    )


def test_real_mongo_exact_prefix_order_limit_and_snapshot_session(
    mongo_context: dict[str, Any],
) -> None:
    """Real durable matters satisfy deterministic exact/prefix search semantics."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant = f"tenant-{uuid.uuid4().hex}"

    for value in (
        _matter(tenant, "matter-z", "CASE-2026-200"),
        _matter(tenant, "matter-b", "CASE-2026-100B"),
        _matter(tenant, "matter-a", "case-2026-100A", closed=True),
        _matter(tenant, "matter-x", "OTHER-2026-001"),
    ):
        _persist(value, lifecycle)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        exact = search_case_matters(
            tenant_id=tenant,
            query="case-2026-200",
            mode=LegalOperationsMatterSearchMode.EXACT,
            lifecycle_collection=lifecycle,
            session=session,
        )
        prefix = search_case_matters(
            tenant_id=tenant,
            query="CASE-2026-1",
            mode=LegalOperationsMatterSearchMode.PREFIX,
            lifecycle_collection=lifecycle,
            limit=1,
            session=session,
        )
        session.commit_transaction()

    assert [model.entity_identity for model in exact.matches] == ["matter-z"]
    assert [model.entity_identity for model in prefix.matches] == ["matter-a"]
    assert isinstance(prefix.matches[0].current, CaseMatter)
    assert prefix.matches[0].current.state is CaseMatterState.CLOSED


def test_real_mongo_current_history_empty_absence_and_foreign_isolation(
    mongo_context: dict[str, Any],
) -> None:
    """Current truth survives history while empty and foreign scopes stay bounded."""
    lifecycle = mongo_context["lifecycle"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    foreign = f"tenant-{uuid.uuid4().hex}"

    opened = _matter(tenant, "matter-own", "CASE-OWN")
    closed = opened.transition_to(
        CaseMatterState.CLOSED,
        evidence_reference="closed-own",
        occurred_at=NOW + timedelta(minutes=1),
    )
    foreign_value = _matter(foreign, "matter-foreign", "CASE-OWN")
    for value in (opened, closed, foreign_value):
        _persist(value, lifecycle)

    local = search_case_matters(
        tenant_id=tenant,
        query="CASE-OWN",
        mode=LegalOperationsMatterSearchMode.EXACT,
        lifecycle_collection=lifecycle,
    )
    missing = search_case_matters(
        tenant_id=tenant,
        query="MISSING",
        mode=LegalOperationsMatterSearchMode.EXACT,
        lifecycle_collection=lifecycle,
    )

    assert [model.entity_identity for model in local.matches] == ["matter-own"]
    assert local.matches[0].current == closed
    assert {value.fingerprint for value in local.matches[0].history} == {
        opened.fingerprint,
        closed.fingerprint,
    }
    assert missing.matches == ()
    assert all(model.tenant_id == tenant for model in local.matches)


def test_real_mongo_corrupt_source_rejects_whole_search(
    mongo_context: dict[str, Any],
) -> None:
    """Corrupt matching P2 evidence never yields partial search output."""
    lifecycle = mongo_context["lifecycle"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    _persist(_matter(tenant, "matter-a", "CASE-A"), lifecycle)
    _persist(_matter(tenant, "matter-b", "CASE-B"), lifecycle)

    result = lifecycle.update_one(
        {
            "tenant_id": tenant,
            "entity_type": "CaseMatter",
            "entity_identity": "matter-a",
        },
        {"$set": {"p1_fingerprint": "f" * 128}},
    )
    assert result.matched_count == 1

    with pytest.raises(LegalOperationsMatterSearchError) as caught:
        search_case_matters(
            tenant_id=tenant,
            query="CASE-",
            mode=LegalOperationsMatterSearchMode.PREFIX,
            lifecycle_collection=lifecycle,
        )
    assert caught.value.code == "L8_5D_READ_MODEL_UNAVAILABLE"
    assert caught.value.__cause__ is not None


def test_real_mongo_search_output_excludes_client_ai_and_financial_authority(
    mongo_context: dict[str, Any],
) -> None:
    """Serialized search output remains canonical retrieval only."""
    lifecycle = mongo_context["lifecycle"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    _persist(_matter(tenant, "matter-1", "CASE-001"), lifecycle)

    result = search_case_matters(
        tenant_id=tenant,
        query="CASE",
        mode=LegalOperationsMatterSearchMode.PREFIX,
        lifecycle_collection=lifecycle,
    )
    payload = result.to_dict()
    assert set(payload) == {
        "tenant_id",
        "query",
        "mode",
        "limit",
        "matches",
    }
    serialized = str(payload).casefold()
    for forbidden in (
        "client_name",
        "embedding",
        "vector_score",
        "ai_score",
        "recommendation",
        "payment",
        "settlement",
        "invoice",
        "bank_execution",
        "provider_execution",
    ):
        assert forbidden not in serialized

    assert PRODUCTION_VERSION == "v1.0.1-L8-5D-LEGAL-OPERATIONS-MATTER-SEARCH"
    assert VERSION == "v1.0.1-L8-5D-LEGAL-OPERATIONS-MATTER-SEARCH-RM-CERT"


# ARTIFACT: test_legal_operations_search_real_mongo.py
# VERSION: v1.0.1-L8-5D-LEGAL-OPERATIONS-MATTER-SEARCH-RM-CERT
# AUTHORITY BOUNDARY: host-backed L8-5D canonical matter-reference search certificate only
# TENANT POSTURE: UUID-isolated exact tenant scope with caller snapshot-session compatibility
# FAIL-CLOSED POSTURE: runtime/input/corruption/tenant drift rejects without fuzzy, client-name, AI, or partial fallback
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
