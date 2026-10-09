"""Real-Mongo certificate for context-bound L9A3 acceptance issuance.

TITLE: L9A3-R1 Context-Bound ClientAcceptance Real-Mongo Certificate
VERSION: v1.1.0-L9A3-R1-CONTEXT-BOUND-ACCEPTANCE-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove physical context loading, complete dependency revalidation,
         immutable acceptance persistence, exact replay, divergent intent,
         expiry, cross-tenant isolation, transaction abort and downstream
         authority boundaries against a UUID-isolated replica-set database.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_acceptance_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: L9A3 orchestrates; certified P2C1/P2C2/P2C3/P2D
                            authorities remain unchanged and are exercised.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.1.0 certifies server-derived acceptance issuance against real
           Mongo with caller-owned transactions and no downstream authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no URI,
                             credentials, bearer tokens or PII are printed.
TENANT BOUNDARY: Exact identity-derived tenant and context actor scope.
AUTHORITY BOUNDARY: Physical immutable client-acceptance evidence only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import timedelta
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tests.integration.test_legal_client_acceptance_context_orchestrator_real_mongo import (
    NOW,
    PRINCIPAL,
    TENANT,
    _Repo,
    _collections,
    _compose,
    _ensure_indexes,
    _identity,
    _issuer,
    _seed,
)
from tools.eos.legal_operations.orchestration.legal_client_acceptance_orchestrator import (
    LegalClientAcceptanceOrchestrationError,
    issue_legal_client_acceptance,
)
from tools.eos.legal_operations.registry import legal_client_acceptance_registry as acceptance_registry


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, dict[str, Any]]]:
    """Use one disposable UUID database and drop only that database."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5_000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != "wilsyVendorCertRS":
            pytest.skip("sanctioned replica set unavailable")
        if hello.get("isWritablePrimary") is not True:
            pytest.skip("sanctioned Mongo has no writable primary")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.skip("Mongo logical sessions unavailable")
        database = client[f"wilsy_l9a3_acceptance_{uuid4().hex}"]
        collections = _collections(database)
        collections["acceptance"] = database[acceptance_registry.COLLECTION]
        _ensure_indexes(collections)
        acceptance_registry.LegalClientAcceptanceRegistry.ensure_indexes(
            collections["acceptance"]
        )
        yield client, database, collections
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _acceptance_kwargs(collections: dict[str, Any], issuer: Any) -> dict[str, Any]:
    """Build only server wiring; no authority-bearing request fields exist."""
    return {
        "identity": _identity(),
        "acceptance_context_id": "context-p2c3-real",
        "confirmed": True,
        "idempotency_key": "acceptance-intent-p2e-real",
        "context_collection": collections["context"],
        "matter_lifecycle_collection": collections["matter"],
        "visibility_collection": collections["visibility"],
        "party_collection": collections["party"],
        "capacity_collection": collections["capacity"],
        "instrument_collection": collections["instrument"],
        "instrument_lifecycle_collection": collections["lifecycle"],
        "approval_collection": collections["approval"],
        "acceptance_collection": collections["acceptance"],
        "authorization_evidence_registry": issuer,
        "principal_repository": _Repo(collections["principal"], "principal"),
        "membership_repository": _Repo(collections["membership"], "membership"),
        "business_role_repository": _Repo(collections["assignment"], "assignment"),
        "role_assignment_repository": _Repo(collections["assignment"], "assignment"),
        "clock": lambda: NOW,
    }


def test_real_mongo_context_bound_acceptance_certificate(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Certify commit/replay/divergence/expiry/abort/isolation in one run."""
    client, database, collections = mongo_context
    _seed(client, collections)
    _compose(client, collections)
    issuer = _issuer(collections)
    kwargs = _acceptance_kwargs(collections, issuer)
    with client.start_session() as session:
        with session.start_transaction():
            first = issue_legal_client_acceptance(**kwargs, session=session)
    assert first.tenant_id == TENANT
    assert first.actor_principal_id == PRINCIPAL
    assert first.acceptance_scope == "client-information-review:v1"
    assert first.source_evidence_fingerprint == collections["instrument"].find_one(
        {"instrument_id": "instrument-p2c3-real"}
    )["content_fingerprint"]
    assert "server://p2c3/content" not in first.source_evidence_reference
    assert collections["acceptance"].count_documents({"tenant_id": TENANT}) == 1
    assert collections["authorization"].count_documents({"tenant_id": TENANT}) == 2

    with client.start_session() as session:
        with session.start_transaction():
            replay = issue_legal_client_acceptance(**kwargs, session=session)
    assert replay.to_dict() == first.to_dict()
    assert collections["acceptance"].count_documents({}) == 1

    divergent = dict(kwargs, idempotency_key="different-acceptance-intent")
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(LegalClientAcceptanceOrchestrationError):
                issue_legal_client_acceptance(**divergent, session=session)
    assert collections["acceptance"].count_documents({}) == 1

    expired = dict(kwargs, clock=lambda: NOW + timedelta(minutes=11))
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(LegalClientAcceptanceOrchestrationError):
                issue_legal_client_acceptance(**expired, session=session)

    other_tenant = dict(kwargs, identity=_identity(tenant="tenant-other"))
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(LegalClientAcceptanceOrchestrationError):
                issue_legal_client_acceptance(**other_tenant, session=session)

    with pytest.raises(RuntimeError):
        with client.start_session() as session:
            with session.start_transaction():
                issue_legal_client_acceptance(**kwargs, session=session)
                raise RuntimeError("synthetic caller abort")
    assert collections["acceptance"].count_documents({}) == 1
    assert not {
        "engagements",
        "representations",
        "court_authorities",
        "financial_approvals",
    } & set(database.list_collection_names())


@pytest.mark.parametrize(
    "mutation",
    ["visibility", "matter", "party", "capacity", "instrument", "lifecycle", "approval", "content", "membership", "role"],
)
def test_real_mongo_current_dependency_revalidation_rejects_source_drift(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]], mutation: str
) -> None:
    """Each post-context source invalidation prevents acceptance durability."""
    client, _database, collections = mongo_context
    _seed(client, collections)
    _compose(client, collections)
    if mutation == "visibility":
        collections["visibility"].delete_many({})
    elif mutation == "matter":
        collections["matter"].delete_many({})
    elif mutation == "party":
        collections["party"].delete_many({})
    elif mutation == "capacity":
        collections["capacity"].delete_many({})
    elif mutation == "instrument":
        collections["instrument"].delete_many({})
    elif mutation == "lifecycle":
        collections["lifecycle"].delete_many({})
    elif mutation == "approval":
        collections["approval"].delete_many({})
    elif mutation == "content":
        collections["instrument"].update_many({}, {"$set": {"content_fingerprint": "a" * 128}})
    elif mutation == "membership":
        collections["membership"].delete_many({})
    elif mutation == "role":
        collections["assignment"].delete_many({})
    kwargs = _acceptance_kwargs(collections, _issuer(collections))
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(LegalClientAcceptanceOrchestrationError):
                issue_legal_client_acceptance(**kwargs, session=session)
    assert collections["acceptance"].count_documents({}) == 0


# ARTIFACT: test_legal_client_acceptance_orchestrator_real_mongo.py
# VERSION: v1.1.0-L9A3-R1-CONTEXT-BOUND-ACCEPTANCE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated physical acceptance certificate only
# TENANT POSTURE: UUID-isolated database and exact identity/context scope
# FAIL-CLOSED POSTURE: stale, divergent, cross-tenant and aborted requests reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
