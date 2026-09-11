"""Direct certificate for the PRDCA application caller.

TITLE: PRDCA Application Caller Direct Certificate
VERSION: v1.0.0-M11-R8-R3B-P8-P3N
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves explicit dependency injection and application-owned
         transaction commit/abort delegation without external side effects.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_prdca_application.py
COLLABORATION / OWNERSHIP: Direct certificate for prdca_application.py.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3N certifies the canonical application caller.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest

from tools.eos.governance.prdca_application import (
    PRDCAApplication,
    PRDCAApplicationError,
)


class _Session:
    def __init__(self) -> None:
        self.in_transaction = False
        self.committed = False
        self.aborted = False

    def __enter__(self) -> "_Session":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def start_transaction(self) -> None:
        self.in_transaction = True

    def commit_transaction(self) -> None:
        self.in_transaction = False
        self.committed = True

    def abort_transaction(self) -> None:
        self.in_transaction = False
        self.aborted = True


class _Client:
    def __init__(self) -> None:
        self.session = _Session()

    def start_session(self) -> _Session:
        return self.session


class _Runtime:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.sessions: list[object] = []

    def issue_and_persist_certificate_batch(self, **kwargs: object) -> object:
        self.sessions.append(kwargs["session"])
        if self.fail:
            raise RuntimeError("runtime failure")
        return "batch"


class _Ledger:
    def __init__(self) -> None:
        self.initialized = False

    def ensure_indexes(self) -> None:
        self.initialized = True

    def get_by_platform_registration_id(self, artifact_id: str) -> str:
        return artifact_id


def _application(runtime: _Runtime, client: _Client, ledger: _Ledger) -> PRDCAApplication:
    return PRDCAApplication(
        mongo_client=cast(Any, client),
        runtime=cast(Any, runtime),
        ledger=cast(Any, ledger),
    )


def test_application_requires_explicit_dependencies() -> None:
    with pytest.raises(PRDCAApplicationError):
        PRDCAApplication(mongo_client=cast(Any, None), runtime=cast(Any, object()), ledger=cast(Any, object()))


def test_application_owns_commit_and_forwards_caller_session() -> None:
    client = _Client()
    runtime = _Runtime()
    ledger = _Ledger()
    app = _application(runtime, client, ledger)
    assert app.issue_and_persist_certificate_batch(
        source_identity="source",
        source_contract_version="v1",
        implementation_identity="impl:source",
        capability_class="credential_metadata",
        campaign_identity="campaign",
        authority_key_id="prdca-key:test",
        deployment_evidence=cast(Any, SimpleNamespace()),
        descriptor=cast(Any, SimpleNamespace()),
    ) == "batch"
    assert client.session.committed is True
    assert client.session.aborted is False
    assert len(runtime.sessions) == 1


def test_application_aborts_and_surfaces_runtime_failure() -> None:
    client = _Client()
    app = _application(_Runtime(fail=True), client, _Ledger())
    with pytest.raises(RuntimeError, match="runtime failure"):
        app.issue_and_persist_certificate_batch(
            source_identity="source",
            source_contract_version="v1",
            implementation_identity="impl:source",
            capability_class="credential_metadata",
            campaign_identity="campaign",
            authority_key_id="prdca-key:test",
            deployment_evidence=cast(Any, SimpleNamespace()),
            descriptor=cast(Any, SimpleNamespace()),
        )
    assert client.session.aborted is True


def test_initialize_is_explicit_and_read_delegates() -> None:
    ledger = _Ledger()
    app = _application(_Runtime(), _Client(), ledger)
    app.initialize()
    assert ledger.initialized is True
    assert app.get_certificate_batch("artifact") == "artifact"


# ARTIFACT: test_prdca_application.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3N
# AUTHORITY BOUNDARY: direct application caller certificate only
# TENANT POSTURE: platform governance scope; no tenant authorization
# FAIL-CLOSED POSTURE: missing dependencies and surfaced transaction failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
