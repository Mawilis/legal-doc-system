"""TITLE: Sheriff Appointment Evidence Registry Real-Mongo Certificate
VERSION: v1.0.1-SHERIFF-APPOINTMENT-EVIDENCE-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Isolated MongoDB replica-set certification of documentary persistence.
EPITOME: Prove replica-set topology, exact tenant-first indexes, majority-
    acknowledged caller transactions, append-only history, exact replay,
    caller abort, tenant isolation, currentness and corruption rejection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_sheriff_appointment_source_evidence_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Host-backed certificate for the Sheriff appointment
    source-evidence registry; no Minister/Board trust root, IAM or queue authority.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG:
    2026-11-02 v1.0.1-SHERIFF-APPOINTMENT-EVIDENCE-REGISTRY-REAL-MONGO-CERT
    Adds deterministic competing-successor certification using a two-party
    barrier and independent caller transactions.
    2026-11-02 v1.0.0-SHERIFF-APPOINTMENT-EVIDENCE-REGISTRY-REAL-MONGO-CERT
    Establishes isolated replica-set certification for transaction visibility,
    exact replay, abort rollback, indexes, tenant isolation and corruption.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic databases and opaque test IDs.
TENANT BOUNDARY: Exact tenant-first persistence; database dropped after each test.
AUTHORITY BOUNDARY: Persistence evidence only; no statutory authentication,
    FFC/insurance currentness, natural-person proof, IAM, office access or execution.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import os
from threading import Barrier
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.sheriff_appointment_source_evidence import (
    SheriffAppointmentCapacity,
    SheriffAppointmentIssuerAuthority,
    SheriffAppointmentSourceEvidence,
    SheriffAppointmentStatutoryBasis,
    SheriffSourceObservationState,
    SheriffSourceVerificationMethod,
)
from tools.eos.legal_operations.registry.sheriff_appointment_source_evidence_registry import (
    COLLECTION_NAME,
    FINGERPRINT_INDEX,
    HISTORY_INDEX,
    IDENTITY_INDEX,
    ROOT_INDEX,
    SUCCESSOR_INDEX,
    SheriffAppointmentEvidenceConflict,
    SheriffAppointmentEvidencePersistedInvalid,
    SheriffAppointmentEvidenceRetryTransaction,
    SheriffAppointmentEvidenceRevision,
    SheriffAppointmentEvidenceRegistry,
)


MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 11, 2, 10, 0, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context() -> Iterator[
    tuple[MongoClient[Any], Any, Any, SheriffAppointmentEvidenceRegistry]
]:
    """Require the explicitly provisioned isolated replica set; never skip."""
    if not MONGO_URI:
        pytest.fail("SHERIFF_APPOINTMENT_REAL_MONGO_URI_REQUIRED")

    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5_000,
        connectTimeoutMS=5_000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None

        database = client["wilsy_sheriff_evidence_" + uuid.uuid4().hex]
        collection = database.get_collection(
            COLLECTION_NAME,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        registry = SheriffAppointmentEvidenceRegistry(collection)
        registry.ensure_indexes()
        yield client, database, collection, registry
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def make_evidence(
    *,
    tenant_id: str,
    evidence_id: str,
    revision: int = 1,
    predecessor: str | None = None,
    observed_at: datetime = NOW,
    effective_from: datetime = NOW - timedelta(days=1),
    effective_until: datetime | None = None,
    instrument_fingerprint: str = "a" * 128,
) -> SheriffAppointmentSourceEvidence:
    """Create one synthetic section 2(1) observation with exact lineage."""
    return SheriffAppointmentSourceEvidence(
        tenant_id=tenant_id,
        evidence_id=evidence_id,
        revision=revision,
        principal_id="principal-sheriff",
        verified_subject_reference="subject-1",
        sheriff_office_id="office-jhb",
        district_id="district-jhb",
        court_reference="court-jhb",
        service_area_references=("area-jhb-central",),
        capacity=SheriffAppointmentCapacity.SHERIFF,
        statutory_basis=SheriffAppointmentStatutoryBasis.SECTION_2_1,
        issuer_authority=SheriffAppointmentIssuerAuthority.MINISTER,
        instrument_reference=f"ministerial-instrument-{revision}",
        instrument_fingerprint=instrument_fingerprint,
        source_uri="https://www.justice.gov.za/notice/synthetic-appointment",
        source_observation_state=SheriffSourceObservationState.HUMAN_OBSERVED_PUBLIC_RECORD,
        source_verification_method=SheriffSourceVerificationMethod.PUBLIC_WEB_OBSERVATION,
        source_verification_reference=f"observation-{revision}",
        verified_by_principal_id="independent-verifier",
        observed_at=observed_at,
        effective_from=effective_from,
        effective_until=effective_until,
        supersedes_fingerprint=predecessor,
    )


def make_revision(
    evidence: SheriffAppointmentSourceEvidence,
    predecessor_registry_fingerprint: str | None = None,
) -> SheriffAppointmentEvidenceRevision:
    """Bind a source observation to registry-owned revision lineage."""
    return SheriffAppointmentEvidenceRevision(
        revision=evidence.revision,
        predecessor_registry_fingerprint=predecessor_registry_fingerprint,
        evidence=evidence,
    )


def commit_revision(
    client: MongoClient[Any],
    registry: SheriffAppointmentEvidenceRegistry,
    value: SheriffAppointmentEvidenceRevision,
) -> SheriffAppointmentEvidenceRevision:
    """Commit exactly one revision with transaction lifecycle owned by caller."""
    with client.start_session() as session:
        with session.start_transaction():
            return registry.persist_revision(value, session=session)


def test_real_replica_set_supports_caller_transactions(
    mongo_context: tuple[MongoClient[Any], Any, Any, SheriffAppointmentEvidenceRegistry],
) -> None:
    client, _, _, _ = mongo_context
    hello = client.admin.command("hello")
    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None


def test_real_indexes_are_exact_tenant_first_and_have_no_ttl(
    mongo_context: tuple[MongoClient[Any], Any, Any, SheriffAppointmentEvidenceRegistry],
) -> None:
    _, _, collection, _ = mongo_context
    indexes = {
        row["name"]: row
        for row in collection.list_indexes()
        if row["name"] != "_id_"
    }
    assert set(indexes) == {
        IDENTITY_INDEX,
        ROOT_INDEX,
        SUCCESSOR_INDEX,
        FINGERPRINT_INDEX,
        HISTORY_INDEX,
    }
    for name, row in indexes.items():
        assert next(iter(row["key"])) == "tenant_id", name
        assert "expireAfterSeconds" not in row, name
    assert dict(indexes[IDENTITY_INDEX]["key"]) == {
        "tenant_id": 1,
        "evidence_id": 1,
        "revision": 1,
    }
    assert indexes[IDENTITY_INDEX].get("unique") is True
    assert indexes[ROOT_INDEX].get("unique") is True
    assert indexes[ROOT_INDEX].get("partialFilterExpression") == {"revision": 1}
    assert indexes[SUCCESSOR_INDEX].get("unique") is True
    assert indexes[SUCCESSOR_INDEX].get("partialFilterExpression") == {
        "supersedes_fingerprint": {"$type": "string"}
    }
    assert indexes[FINGERPRINT_INDEX].get("unique") is True


def test_real_commit_exact_replay_and_tenant_isolation(
    mongo_context: tuple[MongoClient[Any], Any, Any, SheriffAppointmentEvidenceRegistry],
) -> None:
    client, _, collection, registry = mongo_context
    tenant = "tenant-" + uuid.uuid4().hex
    value = make_revision(
        make_evidence(tenant_id=tenant, evidence_id="appointment-1")
    )
    assert commit_revision(client, registry, value) == value
    assert commit_revision(client, registry, value) == value
    assert collection.count_documents({"tenant_id": tenant}) == 1

    with client.start_session() as session:
        with session.start_transaction():
            history = registry.get_history(
                tenant_id=tenant,
                evidence_id="appointment-1",
                session=session,
            )
            assert history == (value,)
            assert registry.get_history_if_any(
                tenant_id="tenant-" + uuid.uuid4().hex,
                evidence_id="appointment-1",
                session=session,
            ) == ()


def test_real_caller_abort_rolls_back_append(
    mongo_context: tuple[MongoClient[Any], Any, Any, SheriffAppointmentEvidenceRegistry],
) -> None:
    client, _, collection, registry = mongo_context
    tenant = "tenant-" + uuid.uuid4().hex
    first = make_revision(
        make_evidence(tenant_id=tenant, evidence_id="appointment-2")
    )
    commit_revision(client, registry, first)

    second_evidence = make_evidence(
        tenant_id=tenant,
        evidence_id="appointment-2",
        revision=2,
        predecessor=first.evidence.fingerprint,
        observed_at=NOW + timedelta(seconds=1),
        effective_from=NOW + timedelta(days=1),
        instrument_fingerprint="b" * 128,
    )
    second = make_revision(second_evidence, first.registry_fingerprint)

    with client.start_session() as session:
        session.start_transaction()
        registry.persist_revision(second, session=session)
        session.abort_transaction()

    with client.start_session() as session:
        with session.start_transaction():
            history = registry.get_history(
                tenant_id=tenant,
                evidence_id="appointment-2",
                session=session,
            )
            assert history == (first,)
    assert collection.count_documents({"tenant_id": tenant}) == 1


def test_real_successor_lineage_and_derived_currentness(
    mongo_context: tuple[MongoClient[Any], Any, Any, SheriffAppointmentEvidenceRegistry],
) -> None:
    client, _, _, registry = mongo_context
    tenant = "tenant-" + uuid.uuid4().hex
    first = make_revision(
        make_evidence(tenant_id=tenant, evidence_id="appointment-3")
    )
    commit_revision(client, registry, first)
    second = make_revision(
        make_evidence(
            tenant_id=tenant,
            evidence_id="appointment-3",
            revision=2,
            predecessor=first.evidence.fingerprint,
            observed_at=NOW + timedelta(seconds=1),
            effective_from=NOW + timedelta(days=1),
            instrument_fingerprint="c" * 128,
        ),
        first.registry_fingerprint,
    )
    commit_revision(client, registry, second)

    with client.start_session() as session:
        with session.start_transaction():
            assert registry.resolve_current(
                tenant_id=tenant,
                evidence_id="appointment-3",
                at=NOW,
                session=session,
            ) == first
            assert registry.resolve_current(
                tenant_id=tenant,
                evidence_id="appointment-3",
                at=NOW + timedelta(days=2),
                session=session,
            ) == second


def test_real_divergent_replay_rejects_without_mutation(
    mongo_context: tuple[MongoClient[Any], Any, Any, SheriffAppointmentEvidenceRegistry],
) -> None:
    client, _, collection, registry = mongo_context
    tenant = "tenant-" + uuid.uuid4().hex
    original = make_revision(
        make_evidence(tenant_id=tenant, evidence_id="appointment-4")
    )
    commit_revision(client, registry, original)
    divergent = make_revision(
        make_evidence(
            tenant_id=tenant,
            evidence_id="appointment-4",
            instrument_fingerprint="d" * 128,
        )
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(SheriffAppointmentEvidenceConflict):
                registry.persist_revision(divergent, session=session)
    assert collection.count_documents({"tenant_id": tenant}) == 1


def test_real_persisted_fingerprint_corruption_fails_closed(
    mongo_context: tuple[MongoClient[Any], Any, Any, SheriffAppointmentEvidenceRegistry],
) -> None:
    client, _, collection, registry = mongo_context
    tenant = "tenant-" + uuid.uuid4().hex
    value = make_revision(
        make_evidence(tenant_id=tenant, evidence_id="appointment-5")
    )
    commit_revision(client, registry, value)
    result = collection.update_one(
        {"tenant_id": tenant, "evidence_id": "appointment-5"},
        {"$set": {"fingerprint": "0" * 128}},
    )
    assert result.modified_count == 1
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(SheriffAppointmentEvidencePersistedInvalid):
                registry.get_history_if_any(
                    tenant_id=tenant,
                    evidence_id="appointment-5",
                    session=session,
                )


def test_real_competing_successors_cannot_both_commit(
    mongo_context: tuple[MongoClient[Any], Any, Any, SheriffAppointmentEvidenceRegistry],
) -> None:
    client, _, collection, registry = mongo_context
    tenant = "tenant-" + uuid.uuid4().hex
    evidence_id = "appointment-race-" + uuid.uuid4().hex
    first = make_revision(
        make_evidence(tenant_id=tenant, evidence_id=evidence_id)
    )
    commit_revision(client, registry, first)

    candidates = (
        make_revision(
            make_evidence(
                tenant_id=tenant,
                evidence_id=evidence_id,
                revision=2,
                predecessor=first.evidence.fingerprint,
                observed_at=NOW + timedelta(seconds=1),
                effective_from=NOW + timedelta(days=1),
                instrument_fingerprint="e" * 128,
            ),
            first.registry_fingerprint,
        ),
        make_revision(
            make_evidence(
                tenant_id=tenant,
                evidence_id=evidence_id,
                revision=2,
                predecessor=first.evidence.fingerprint,
                observed_at=NOW + timedelta(seconds=2),
                effective_from=NOW + timedelta(days=1),
                instrument_fingerprint="f" * 128,
            ),
            first.registry_fingerprint,
        ),
    )
    barrier = Barrier(2)

    def compete(
        value: SheriffAppointmentEvidenceRevision,
    ) -> tuple[str, str]:
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    barrier.wait(timeout=15)
                    registry.persist_revision(value, session=session)
            return ("COMMITTED", value.evidence.fingerprint)
        except (
            SheriffAppointmentEvidenceConflict,
            SheriffAppointmentEvidenceRetryTransaction,
        ) as error:
            return ("REJECTED", type(error).__name__)
        except Exception as error:
            # The caller owns transaction commit. A write conflict raised at
            # commit is therefore surfaced as a raw PyMongo exception.
            from pymongo.errors import PyMongoError

            if isinstance(error, PyMongoError):
                return ("REJECTED", type(error).__name__)
            raise

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = tuple(pool.map(compete, candidates))

    assert sum(outcome[0] == "COMMITTED" for outcome in outcomes) == 1
    assert sum(outcome[0] == "REJECTED" for outcome in outcomes) == 1
    with client.start_session() as session:
        with session.start_transaction():
            history = registry.get_history(
                tenant_id=tenant,
                evidence_id=evidence_id,
                session=session,
            )
    assert len(history) == 2
    assert history[-1].evidence.fingerprint in {
        candidate.evidence.fingerprint for candidate in candidates
    }
    assert collection.count_documents(
        {"tenant_id": tenant, "evidence_id": evidence_id}
    ) == 2


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: tests/integration/test_sheriff_appointment_source_evidence_registry_real_mongo.py
# VERSION: v1.0.1-SHERIFF-APPOINTMENT-EVIDENCE-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo immutable documentary persistence only
# TENANT POSTURE: UUID-isolated tenant and database; no production tenant access
# FAIL-CLOSED POSTURE: missing topology, invalid index, replay divergence, abort failure or corruption fails
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
