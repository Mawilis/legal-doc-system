"""P5-A real-Mongo Temporal Operations observability certificate.

TITLE: Wilsy OS Temporal Operations Observability Real-Mongo Certificate
VERSION: v1.0.0-P5-A-TEMPORAL-OBSERVABILITY-REAL-MONGO
AUTHORITY: Integration verification only; no Legal or persistence authority.
EPITOME: Bind one terminal structured observation to actual Mongo transaction
         commit/abort commands for the authenticated P4 temporal endpoint.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_temporal_operations_observability_real_mongo.py
COLLABORATION / OWNERSHIP: P4 owns canonical reads; P5-A observes outcomes.
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG: 2026-10-19 v1.0.0 proves post-commit/post-abort event ordering,
           correlation ownership, non-disclosure and sink-failure isolation.
COMPLIANCE: POPIA section 19, GDPR Article 32 and SOC 2 CC7.2 controls.
SECURITY / PRIVACY POSTURE: Synthetic evidence; raw scope and secrets excluded.
TENANT BOUNDARY: Real current IAM admission precedes all observed route work.
AUTHORITY BOUNDARY: Observation cannot authorize or mutate Legal operations.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

import importlib.util
import logging
import os
from pathlib import Path
from typing import Any
import uuid

import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient, monitoring

import tools.eos.api.legal_operations_router as legal_router
from tools.eos.legal_operations.registry import (
    legal_matter_deadline_registry as deadline_registry,
)
from tools.eos.legal_operations.service import (
    legal_temporal_operations_read_service as temporal_service,
)


URI = os.environ["WILSY_P4_TEMPORAL_MONGO_URI"]
P4_PATH = Path(__file__).with_name(
    "test_legal_temporal_operations_http_real_mongo.py"
)
spec = importlib.util.spec_from_file_location(
    "_wilsy_p5_temporal_http_harness",
    P4_PATH,
)
assert spec is not None and spec.loader is not None
p4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p4)

PATH = "/api/legal-operations/temporal-operations"
SECRET = "Bearer p5-real-mongo-secret"


class _Listener(monitoring.CommandListener):
    """Capture transaction commands and exact session correlation."""

    def __init__(self, timeline: list[str]) -> None:
        self.timeline = timeline
        self.events: list[tuple[str, object, object]] = []

    def started(self, event: Any) -> None:
        if event.command_name not in (
            "find", "commitTransaction", "abortTransaction"
        ):
            return
        if event.command_name == "find" and event.command.get("find") not in (
            "legal_work_items", deadline_registry.COLLECTION
        ):
            return
        self.events.append((
            event.command_name,
            event.command.get("lsid"),
            event.command.get("txnNumber"),
        ))
        if event.command_name in ("commitTransaction", "abortTransaction"):
            self.timeline.append(event.command_name)

    def succeeded(self, event: Any) -> None:
        del event
        return None

    def failed(self, event: Any) -> None:
        del event
        return None


def _seeded(
    listener: _Listener,
) -> tuple[MongoClient[Any], Any, dict[str, Any], str, str]:
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
        event_listeners=[listener],
    )
    database = client["wilsy_p5_observe_" + uuid.uuid4().hex]
    tenant = "tenant-p5-observe-" + uuid.uuid4().hex
    principal = "principal-p5-observe-" + uuid.uuid4().hex
    hello = client.admin.command("hello")
    assert hello.get("isWritablePrimary") is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None

    values = p4.harness._collections(database)
    p4.harness._ensure_indexes(values)
    deadlines = database[deadline_registry.COLLECTION]
    deadline_registry.ensure_indexes(deadlines)
    p4.harness._seed_iam(values, principal, tenant)
    p4.harness._seed_work(client, values, principal, tenant)
    with client.start_session() as session:
        with session.start_transaction():
            deadline_registry.persist_deadline(
                p4._deadline(
                    "deadline-p5-observed",
                    "matter-http-1",
                    tenant,
                    2,
                ),
                deadlines,
                session=session,
            )
    listener.events.clear()
    listener.timeline.clear()
    return client, database, values, tenant, principal


@pytest.mark.parametrize("failure", [False, True])
def test_terminal_observation_follows_actual_transaction_command(
    monkeypatch: Any,
    failure: bool,
) -> None:
    timeline: list[str] = []
    listener = _Listener(timeline)
    client, database, values, tenant, principal = _seeded(listener)
    observations: list[dict[str, Any]] = []

    try:
        app = p4.harness._app(client, database, values, principal, tenant)
        monkeypatch.setattr(
            legal_router,
            "_db_handles",
            lambda: (client, database),
        )
        monkeypatch.setattr(
            legal_router,
            "_new_temporal_correlation_id",
            lambda: "temporal-server-owned-p5",
        )
        original_log = legal_router.logger.log

        def capture_log(*args: Any, **kwargs: Any) -> None:
            observation = kwargs["extra"]["wilsy_observation"]
            observations.append(observation)
            timeline.append("observation")
            original_log(*args, **kwargs)

        monkeypatch.setattr(legal_router.logger, "log", capture_log)

        if failure:
            original_reader = (
                temporal_service._CanonicalDeadlineReader.list_matter_deadlines
            )

            def fail_after_read(self: Any, **kwargs: Any) -> Any:
                original_reader(self, **kwargs)
                raise RuntimeError(f"injected {SECRET} matter-http-1")

            monkeypatch.setattr(
                temporal_service._CanonicalDeadlineReader,
                "list_matter_deadlines",
                fail_after_read,
            )

        with TestClient(app) as api:
            response = api.get(
                PATH,
                headers={
                    "X-Tenant-ID": tenant,
                    "X-Correlation-ID": "caller-correlation-must-not-win",
                    "Authorization": SECRET,
                },
            )

        expected_command = (
            "abortTransaction" if failure else "commitTransaction"
        )
        assert timeline == [expected_command, "observation"]
        assert len(observations) == 1
        observation = observations[0]
        assert observation["outcome"] == ("ERROR" if failure else "SUCCESS")
        assert observation["transaction_outcome"] == (
            "ABORTED" if failure else "COMMITTED"
        )
        assert response.headers["X-Correlation-ID"] == (
            "temporal-server-owned-p5"
        )
        rendered = str(observation)
        for forbidden in (
            tenant,
            principal,
            "matter-http-1",
            "deadline-p5-observed",
            SECRET,
            "caller-correlation-must-not-win",
        ):
            assert forbidden not in rendered
        assert response.status_code == (503 if failure else 200)

        finds = [event for event in listener.events if event[0] == "find"]
        endings = [
            event for event in listener.events
            if event[0] in ("commitTransaction", "abortTransaction")
        ]
        assert finds and len(endings) == 1
        assert all(event[1:] == finds[0][1:] for event in finds + endings)
    finally:
        client.drop_database(database.name)
        client.close()


@pytest.mark.parametrize("failure", [False, True])
def test_telemetry_sink_failure_preserves_real_transaction_and_http_outcome(
    monkeypatch: Any,
    failure: bool,
) -> None:
    timeline: list[str] = []
    listener = _Listener(timeline)
    client, database, values, tenant, principal = _seeded(listener)

    try:
        app = p4.harness._app(client, database, values, principal, tenant)
        monkeypatch.setattr(
            legal_router,
            "_db_handles",
            lambda: (client, database),
        )

        if failure:
            original_reader = (
                temporal_service._CanonicalDeadlineReader.list_matter_deadlines
            )

            def fail_after_read(self: Any, **kwargs: Any) -> Any:
                original_reader(self, **kwargs)
                raise RuntimeError("canonical failure without disclosure")

            monkeypatch.setattr(
                temporal_service._CanonicalDeadlineReader,
                "list_matter_deadlines",
                fail_after_read,
            )

        def broken_sink(*_args: Any, **_kwargs: Any) -> None:
            raise RuntimeError(f"sink unavailable {SECRET}")

        monkeypatch.setattr(legal_router.logger, "log", broken_sink)

        with TestClient(app) as api:
            response = api.get(PATH, headers={"X-Tenant-ID": tenant})

        assert response.status_code == (503 if failure else 200)
        assert timeline == [
            "abortTransaction" if failure else "commitTransaction"
        ]
    finally:
        client.drop_database(database.name)
        client.close()


# ARTIFACT: test_legal_temporal_operations_observability_real_mongo.py
# VERSION: v1.0.0-P5-A-TEMPORAL-OBSERVABILITY-REAL-MONGO
# AUTHORITY BOUNDARY: authenticated transaction/observation verification only
# TENANT POSTURE: synthetic own-tenant scope; foreign disclosure prohibited
# FAIL-CLOSED POSTURE: telemetry cannot change commit, abort or HTTP truth
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
