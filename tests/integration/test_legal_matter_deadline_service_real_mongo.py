"""D3A deadline service real-Mongo orchestration certificate.

TITLE: Wilsy OS Legal Matter Deadline Service Real-Mongo Certificate
VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D3A-DEADLINE-SERVICE-RM-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify canonical matter correlation through D3A into D2 persistence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system-legal-deadline-engine/tests/integration/test_legal_matter_deadline_service_real_mongo.py
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0-LEGAL-OPS-COMPLETION-D3A-DEADLINE-SERVICE-RM-CERT establishes disposable orchestration evidence.
TENANT BOUNDARY: UUID database and exact tenant/matter predicates.
TRANSACTION BOUNDARY: Test caller owns transaction lifecycle.
AUTHORITY BOUNDARY: Matter correlation and D1/D2 composition only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Infrastructure, correlation, replay or corruption drift fails.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
import uuid
import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry import legal_matter_deadline_registry as deadline_registry
from tools.eos.legal_operations.service import legal_matter_deadline_service as service

URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
NOW = datetime(2026, 10, 11, 8, 0, tzinfo=timezone.utc)

@pytest.fixture
def mongo() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
    client: MongoClient[Any] = MongoClient(URI, serverSelectionTimeoutMS=3000, retryWrites=True, tz_aware=True); db: Any = None
    try:
        try: hello = client.admin.command("hello")
        except PyMongoError as error: pytest.fail(f"D3A_MONGO_UNAVAILABLE:{type(error).__name__}")
        assert hello.get("setName") == "wilsyVendorCertRS" and hello.get("isWritablePrimary", hello.get("ismaster")) is True
        db = client[f"deadline_d3a_{uuid.uuid4().hex}"]; matters = db["legal_operations_lifecycle"]; deadlines = db[deadline_registry.COLLECTION]
        LegalOperationsLifecycleRegistry.ensure_indexes(matters); deadline_registry.ensure_indexes(deadlines)
        yield client, matters, deadlines
    finally:
        if db is not None: client.drop_database(db.name)
        client.close()

def seed(client: MongoClient[Any], matters: Any, tenant: str) -> None:
    with client.start_session() as session:
        with session.start_transaction(): LegalOperationsLifecycleRegistry.create(CaseMatter(tenant_id=tenant, case_matter_id="matter-1", matter_reference="MAT-1", opened_at=NOW, evidence_reference="matter:1"), matters, session=session)

def args(tenant: str, matters: Any, deadlines: Any, session: Any, **changes: object) -> dict[str, object]:
    values: dict[str, object] = {"tenant_id": tenant, "case_matter_id": "matter-1", "deadline_id": "deadline-1", "deadline_kind": "FILING", "title": "Deadline", "due_at": NOW + timedelta(days=7), "source_type": "COURT_ORDER", "source_reference": "evidence:order", "source_evidence_fingerprint": "a" * 128, "jurisdiction_reference": "jurisdiction:court", "created_at": NOW, "matter_collection": matters, "deadline_collection": deadlines, "session": session}
    values.update(changes); return values

def test_real_service_commit_replay_isolation_abort_and_missing_matter(mongo: tuple[MongoClient[Any], Any, Any]) -> None:
    client, matters, deadlines = mongo; seed(client, matters, "tenant-a"); seed(client, matters, "tenant-b")
    with client.start_session() as session:
        with session.start_transaction():
            first = service.record_legal_matter_deadline(**args("tenant-a", matters, deadlines, session))  # type: ignore[arg-type]
            assert service.record_legal_matter_deadline(**args("tenant-a", matters, deadlines, session)) == first  # type: ignore[arg-type]
    assert deadlines.count_documents({"tenant_id": "tenant-a"}) == 1
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(service.LegalMatterDeadlineServiceError, match="DEADLINE_CONFLICT"):
                service.record_legal_matter_deadline(**args("tenant-a", matters, deadlines, session, title="Divergent"))  # type: ignore[arg-type]
    with client.start_session() as session:
        with session.start_transaction():
            service.record_legal_matter_deadline(**args("tenant-b", matters, deadlines, session))  # type: ignore[arg-type]
    assert deadlines.count_documents({"deadline_id": "deadline-1"}) == 2
    with client.start_session() as session:
        session.start_transaction()
        service.record_legal_matter_deadline(**args("tenant-b", matters, deadlines, session, deadline_id="deadline-aborted"))  # type: ignore[arg-type]
        session.abort_transaction()
    assert deadlines.count_documents({"deadline_id": "deadline-aborted"}) == 0
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(service.LegalMatterDeadlineServiceError, match="DEADLINE_MATTER_NOT_AVAILABLE"): service.record_legal_matter_deadline(**args("tenant-missing", matters, deadlines, session))  # type: ignore[arg-type]
        assert deadlines.count_documents({"tenant_id": "tenant-missing"}, session=session) == 0
        session.abort_transaction()
    row = deadlines.find_one({"tenant_id": "tenant-a"}); assert isinstance(row, dict)
    assert not any(key in row for key in ("payment", "settlement", "ai_generated", "overdue"))
    deadlines.update_one({"tenant_id": "tenant-a", "deadline_id": "deadline-1"}, {"$set": {"fingerprint": "0" * 128}})
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(service.LegalMatterDeadlineServiceError, match="DEADLINE_CORRUPT"):
                service.get_legal_matter_deadline(tenant_id="tenant-a", deadline_id="deadline-1", deadline_collection=deadlines, session=session)

# ARTIFACT: test_legal_matter_deadline_service_real_mongo.py
# VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D3A-DEADLINE-SERVICE-RM-CERT
# AUTHORITY BOUNDARY: physical current-matter and D1/D2 orchestration evidence only
# TENANT POSTURE: isolated database and exact tenant predicates
# FAIL-CLOSED POSTURE: infrastructure, matter, transaction and replay drift fail
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
