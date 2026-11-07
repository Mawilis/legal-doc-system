from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.security.institutional_pki_crl_registry import (
    CURRENTNESS_COLLECTION,
    EVENT_COLLECTION,
    InstitutionalPKICRLCurrentnessRegistry,
    InstitutionalPKICRLRegistryError,
)

URI = os.getenv("INSTITUTIONAL_PKI_TEST_MONGODB_URI")
pytestmark = pytest.mark.skipif(not URI, reason="INSTITUTIONAL_PKI_TEST_MONGODB_URI is not configured")


def test_real_replica_set_persists_crl_high_water_and_append_only_events_atomically():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    database_name = f"institutional_pki_crl_{uuid.uuid4().hex}"
    database = client[database_name]
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") and hello.get("isWritablePrimary") is True
        registry = InstitutionalPKICRLCurrentnessRegistry(
            database[CURRENTNESS_COLLECTION],
            database[EVENT_COLLECTION],
        )
        registry.ensure_indexes()
        issuer_a = "a" * 64
        issuer_b = "b" * 64
        fingerprint_a_1 = "1" * 64
        fingerprint_a_2 = "2" * 64
        fingerprint_b_1 = "3" * 64
        instant = datetime.now(timezone.utc)

        def transact(callback):
            with client.start_session() as session:
                return session.with_transaction(
                    callback,
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern(w="majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )

        initial = {issuer_a: (1, fingerprint_a_1), issuer_b: (4, fingerprint_b_1)}
        assert transact(lambda session: registry.observe_bundle(
            initial, actor_reference="EOS-PKI-RUNTIME-TEST",
            observed_at=instant, session=session,
        )) == 2
        assert transact(lambda session: registry.observe_bundle(
            initial, actor_reference="EOS-PKI-RUNTIME-TEST",
            observed_at=instant, session=session,
        )) == 0

        advanced = {issuer_a: (2, fingerprint_a_2), issuer_b: (4, fingerprint_b_1)}
        assert transact(lambda session: registry.observe_bundle(
            advanced, actor_reference="EOS-PKI-RUNTIME-TEST",
            observed_at=instant, session=session,
        )) == 1
        current = database[CURRENTNESS_COLLECTION].find_one({"issuer_subject_sha256": issuer_a})
        assert current["crl_number"] == 2
        assert current["crl_fingerprint"] == fingerprint_a_2
        assert current["revision"] == 2
        assert database[EVENT_COLLECTION].count_documents({"issuer_subject_sha256": issuer_a}) == 2
        advanced_event = database[EVENT_COLLECTION].find_one({
            "issuer_subject_sha256": issuer_a,
            "crl_number": 2,
        })
        assert advanced_event["previous_crl_number"] == 1
        assert advanced_event["previous_crl_fingerprint"] == fingerprint_a_1

        with pytest.raises(InstitutionalPKICRLRegistryError, match="ROLLBACK_REJECTED"):
            transact(lambda session: registry.observe_bundle(
                {issuer_a: (1, fingerprint_a_1)},
                actor_reference="EOS-PKI-RUNTIME-TEST",
                observed_at=instant, session=session,
            ))
        current_after_rejection = database[CURRENTNESS_COLLECTION].find_one(
            {"issuer_subject_sha256": issuer_a}
        )
        assert current_after_rejection["crl_number"] == 2
        assert current_after_rejection["revision"] == 2
        assert database[EVENT_COLLECTION].count_documents({"issuer_subject_sha256": issuer_a}) == 2

        with pytest.raises(InstitutionalPKICRLRegistryError, match="NUMBER_REUSE_REJECTED"):
            transact(lambda session: registry.observe_bundle(
                {issuer_a: (2, "f" * 64)},
                actor_reference="EOS-PKI-RUNTIME-TEST",
                observed_at=instant, session=session,
            ))
        assert database[CURRENTNESS_COLLECTION].find_one(
            {"issuer_subject_sha256": issuer_a}
        )["crl_fingerprint"] == fingerprint_a_2
    finally:
        client.drop_database(database_name)
        assert database_name not in client.list_database_names()
        client.close()


def test_registry_requires_caller_owned_session_and_valid_scope():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    database_name = f"institutional_pki_crl_contract_{uuid.uuid4().hex}"
    database = client[database_name]
    try:
        registry = InstitutionalPKICRLCurrentnessRegistry(
            database[CURRENTNESS_COLLECTION],
            database[EVENT_COLLECTION],
        )
        with pytest.raises(InstitutionalPKICRLRegistryError, match="CALLER_SESSION_REQUIRED"):
            registry.observe_bundle(
                {"a" * 64: (1, "1" * 64)},
                actor_reference="EOS-PKI-RUNTIME-TEST",
                observed_at=datetime.now(timezone.utc),
                session=None,
            )
    finally:
        client.drop_database(database_name)
        client.close()
