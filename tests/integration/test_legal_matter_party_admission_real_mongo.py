"""Real-Mongo certificate for L8-8C legal matter-party admission.

VERSION: v1.0.0-L8-8C-LEGAL-MATTER-PARTY-ADMISSION-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_matter_party_admission_real_mongo.py
TRANSACTION BOUNDARY: Test caller owns all sessions/transactions.
AUTHORITY BOUNDARY: Physical P2 -> L8-0 -> L8-8A -> L8-8B composition evidence.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.orchestration import legal_matter_party_admission as admission
from tools.eos.legal_operations.registry import legal_matter_party_registry as party_registry
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
    LegalOperationsLifecycleRegistry,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 25, 15, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any, Any]]:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(
                f"host Mongo unavailable during hello: {type(error).__name__}: {error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("replica set has no writable primary")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.skip("replica set has no logical-session capability")

        database = client[f"wilsy_l8_8c_admission_{uuid.uuid4().hex}"]
        lifecycle = database.get_collection(
            LIFECYCLE_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        parties = database.get_collection(
            party_registry.COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        party_registry.ensure_indexes(parties)
        yield client, database, lifecycle, parties
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _matter(
    tenant: str,
    matter_id: str = "matter-1",
) -> CaseMatter:
    return CaseMatter(
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_reference=f"REF-{matter_id}",
        opened_at=NOW,
        evidence_reference=f"intake:{matter_id}",
    )


def _seed_matter(
    client: MongoClient[Any],
    lifecycle: Any,
    value: CaseMatter,
    *,
    close: bool = False,
) -> CaseMatter:
    with client.start_session() as session:
        with session.start_transaction():
            LegalOperationsLifecycleRegistry.create(
                value,
                lifecycle,
                session=session,
            )
            if not close:
                return value
            closed = value.transition_to(
                CaseMatterState.CLOSED,
                evidence_reference="closure:1",
                occurred_at=NOW + timedelta(hours=1),
            )
            LegalOperationsLifecycleRegistry.create(
                closed,
                lifecycle,
                session=session,
            )
            return closed


def _admit(
    *,
    tenant: str,
    client: MongoClient[Any],
    lifecycle: Any,
    parties: Any,
    party_id: str = "party-1",
    subject_fingerprint: str = FP_A,
    session: Any | None = None,
) -> Any:
    def call(active_session: Any) -> Any:
        return admission.admit_legal_matter_party(
            tenant_id=tenant,
            case_matter_id="matter-1",
            party_id=party_id,
            party_kind=LegalMatterPartyKind.ORGANIZATION,
            party_side=LegalMatterPartySide.CLIENT_SIDE,
            matter_role=LegalMatterPartyRole.CLIENT,
            subject_reference="organization:acme",
            subject_identity_fingerprint=subject_fingerprint,
            display_name="Acme Legal",
            registered_at=NOW + timedelta(minutes=1),
            source_evidence_reference=f"party-source:{party_id}",
            source_evidence_fingerprint=FP_B,
            lifecycle_collection=lifecycle,
            party_collection=parties,
            session=active_session,
        )

    if session is not None:
        return call(session)
    with client.start_session() as owned:
        with owned.start_transaction():
            return call(owned)


def test_real_open_matter_admission_commit_and_exact_replay(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    client, _, lifecycle, parties = mongo_context
    tenant = f"tenant-open-{uuid.uuid4().hex}"
    current = _seed_matter(client, lifecycle, _matter(tenant))

    first = _admit(
        tenant=tenant,
        client=client,
        lifecycle=lifecycle,
        parties=parties,
    )
    replay = _admit(
        tenant=tenant,
        client=client,
        lifecycle=lifecycle,
        parties=parties,
    )

    assert first.party == replay.party
    assert first.matter == current
    assert first.party.matter_fingerprint == current.fingerprint
    assert parties.count_documents({"tenant_id": tenant}) == 1


def test_real_closed_current_matter_rejects_and_creates_no_party(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    client, _, lifecycle, parties = mongo_context
    tenant = f"tenant-closed-{uuid.uuid4().hex}"
    _seed_matter(client, lifecycle, _matter(tenant), close=True)

    with pytest.raises(admission.LegalMatterPartyAdmissionMatterNotOpenError):
        _admit(
            tenant=tenant,
            client=client,
            lifecycle=lifecycle,
            parties=parties,
        )
    assert parties.count_documents({"tenant_id": tenant}) == 0


def test_real_foreign_tenant_scope_is_absent_without_cross_tenant_disclosure(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    client, _, lifecycle, parties = mongo_context
    tenant = f"tenant-a-{uuid.uuid4().hex}"
    foreign = f"tenant-b-{uuid.uuid4().hex}"
    _seed_matter(client, lifecycle, _matter(tenant))

    with pytest.raises(admission.LegalMatterPartyAdmissionMatterNotFoundError):
        _admit(
            tenant=foreign,
            client=client,
            lifecycle=lifecycle,
            parties=parties,
        )
    assert parties.count_documents({}) == 0


def test_real_caller_abort_rolls_back_admitted_party(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    client, _, lifecycle, parties = mongo_context
    tenant = f"tenant-abort-{uuid.uuid4().hex}"
    _seed_matter(client, lifecycle, _matter(tenant))

    with client.start_session() as session:
        session.start_transaction()
        result = _admit(
            tenant=tenant,
            client=client,
            lifecycle=lifecycle,
            parties=parties,
            session=session,
        )
        assert result.party.tenant_id == tenant
        assert parties.count_documents(
            {"tenant_id": tenant},
            session=session,
        ) == 1
        session.abort_transaction()

    assert parties.count_documents({"tenant_id": tenant}) == 0


def test_real_corrupt_case_matter_history_rejects_before_party_persistence(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    client, _, lifecycle, parties = mongo_context
    tenant = f"tenant-corrupt-{uuid.uuid4().hex}"
    _seed_matter(client, lifecycle, _matter(tenant))
    original = deepcopy(
        lifecycle.find_one(
            {
                "tenant_id": tenant,
                "entity_type": "CaseMatter",
            }
        )
    )
    assert isinstance(original, dict)

    lifecycle.update_one(
        {"_id": original["_id"]},
        {"$set": {"p1_payload.matter_reference": "TAMPERED"}},
    )

    with pytest.raises(
        admission.LegalMatterPartyAdmissionAuthorityUnavailableError
    ):
        _admit(
            tenant=tenant,
            client=client,
            lifecycle=lifecycle,
            parties=parties,
        )
    assert parties.count_documents({"tenant_id": tenant}) == 0

    lifecycle.replace_one({"_id": original["_id"]}, original)


# ARTIFACT: test_legal_matter_party_admission_real_mongo.py
# VERSION: v1.0.0-L8-8C-LEGAL-MATTER-PARTY-ADMISSION-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical durable-current CaseMatter-to-party composition evidence only
# TENANT POSTURE: UUID-isolated database and exact tenant/type/matter reads
# FAIL-CLOSED POSTURE: closed/foreign/corrupt/aborted matter admission leaves no party truth
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
