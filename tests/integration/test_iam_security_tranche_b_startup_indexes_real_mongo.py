"""Real-Mongo Tranche-B canonical startup index certification."""
from __future__ import annotations

import os
import uuid

from fastapi.testclient import TestClient
from pymongo import MongoClient

from tools.eos.api import server
from tools.eos.auth.internal_service_replay_registry import (
    COLLECTION as REPLAY_COLLECTION,
)
from tools.eos.auth.internal_service_workload_credential_registry import (
    COLLECTION as CREDENTIAL_COLLECTION,
    POINTER_COLLECTION as CREDENTIAL_POINTER_COLLECTION,
)
from tools.eos.auth.privileged_workload_trust_currentness_registry import (
    COLLECTION as WORKLOAD_COLLECTION,
)
from tools.eos.auth.privileged_noninteractive_security_proof_registry import (
    COLLECTION as PROOF_COLLECTION,
)
from tools.eos.auth.privileged_security_assurance_evidence_registry import (
    COLLECTION as ASSURANCE_COLLECTION,
)


def _indexes(database, name: str) -> list[dict]:
    return [
        dict(row)
        for row in database[
            name
        ].list_indexes()
    ]


def test_canonical_startup_creates_tranche_b_indexes(
    monkeypatch,
) -> None:
    client = MongoClient(
        os.environ[
            "WILSY_VENDOR_CERT_MONGO_URI"
        ]
    )

    database = client[
        "wilsy_iam_tranche_b_"
        + uuid.uuid4().hex
    ]

    monkeypatch.setattr(
        server,
        "connect_db",
        lambda: (
            True,
            "CERT",
        ),
    )
    monkeypatch.setattr(
        server,
        "get_database",
        lambda: database,
    )
    monkeypatch.setattr(
        server,
        "get_client",
        lambda: client,
    )
    monkeypatch.setattr(
        server,
        "disconnect_db",
        lambda: None,
    )
    monkeypatch.setenv(
        "WILSY_DUNNING_SCHEDULER_ENABLED",
        "false",
    )

    app = server.WilsyAPIServer(
        reasoning_provider_binding=None,
    ).get_app()

    with TestClient(app):
        pass

    replay = _indexes(
        database,
        REPLAY_COLLECTION,
    )
    credential = _indexes(
        database,
        CREDENTIAL_COLLECTION,
    )
    pointer = _indexes(
        database,
        CREDENTIAL_POINTER_COLLECTION,
    )
    workload = _indexes(
        database,
        WORKLOAD_COLLECTION,
    )
    proof = _indexes(
        database,
        PROOF_COLLECTION,
    )
    assurance = _indexes(
        database,
        ASSURANCE_COLLECTION,
    )

    for indexes in (
        replay,
        credential,
        pointer,
        workload,
        proof,
        assurance,
    ):
        assert len(indexes) >= 2

    replay_ttl = [
        row
        for row in replay
        if "expireAfterSeconds"
        in row
    ]

    assert len(replay_ttl) == 1
    assert (
        replay_ttl[0][
            "expireAfterSeconds"
        ]
        == 0
    )

    for indexes in (
        credential,
        pointer,
        workload,
        proof,
        assurance,
    ):
        assert all(
            "expireAfterSeconds"
            not in row
            for row in indexes
        )

    database.client.drop_database(
        database.name
    )
    client.close()


# ARTIFACT: test_iam_security_tranche_b_startup_indexes_real_mongo.py
# VERSION: v1.0.0-P3-R3G-S6-A2-IAM-SECURITY-STARTUP-INDEX-REAL-MONGO
# AUTHORITY BOUNDARY: Disposable Real-Mongo index observation only.
# TENANT POSTURE: UUID-isolated certification database.
# FAIL-CLOSED POSTURE: Missing indexes or unexpected TTL topology fails.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
