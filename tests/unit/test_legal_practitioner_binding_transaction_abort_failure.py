"""WILSY OS practitioner-binding transaction abort failure certificate.

TITLE: P12C-R4N-P9 Transaction Failure Isolation
VERSION: v1.0.0-P12C-R4N-P9-TRANSACTION-ABORT-FAILURE
AUTHORITY: Existing EOS practitioner-binding HTTP transaction boundary
EPITOME: Reject success when a failing transaction cannot be aborted
ABSOLUTE CANONICAL PATH: tests/unit/test_legal_practitioner_binding_transaction_abort_failure.py
COLLABORATION / OWNERSHIP: HTTP transaction behavioral certification
CERTIFICATION DATE: 2026-10-20
CHANGELOG: Initial abort-failure negative certificate
COMPLIANCE: WILSY OS engineering governance and transaction integrity
SECURITY / PRIVACY: No personal data or credentials
TENANT BOUNDARY: No authority projection or tenant override
AUTHORITY BOUNDARY: Tests only; no IAM decision or binding issuance
FINANCIAL AUTHORITY BOUNDARY: No financial execution
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from tools.eos.api import (
    legal_practitioner_matter_binding_router as api,
)


class BrokenAbortSession:
    """Simulate caller-owned transaction with failed rollback."""

    def __init__(self, fail_commit: bool) -> None:
        self.fail_commit = fail_commit
        self.in_transaction = False
        self.events: list[str] = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def start_transaction(self) -> None:
        self.events.append("start")
        self.in_transaction = True

    def commit_transaction(self) -> None:
        self.events.append("commit")
        if self.fail_commit:
            raise RuntimeError("INJECTED_COMMIT_FAILURE")
        self.in_transaction = False

    def abort_transaction(self) -> None:
        self.events.append("abort")
        raise RuntimeError("INJECTED_ABORT_FAILURE")


@pytest.mark.parametrize("fail_commit", [False, True])
def test_abort_failure_cannot_return_success(
    monkeypatch: pytest.MonkeyPatch,
    fail_commit: bool,
) -> None:
    """Failure during rollback must never yield a successful command."""
    session = BrokenAbortSession(fail_commit=fail_commit)
    database = object()

    monkeypatch.setattr(
        api,
        "get_client",
        lambda: SimpleNamespace(start_session=lambda: session),
    )
    monkeypatch.setattr(api, "get_database", lambda: database)

    def operation(active_session, active_database):
        assert active_session is session
        assert active_database is database
        session.events.append("service")
        if not fail_commit:
            raise RuntimeError("INJECTED_SERVICE_FAILURE")
        return {"result": "MUST_NOT_ESCAPE"}

    with pytest.raises(HTTPException) as captured:
        api._transaction(operation)

    assert captured.value.status_code == 503
    assert captured.value.detail == "P9_BINDING_AUTHORITY_UNAVAILABLE"

    expected = (
        ["start", "service", "commit", "abort"]
        if fail_commit
        else ["start", "service", "abort"]
    )
    assert session.events == expected


# ARTIFACT: test_legal_practitioner_binding_transaction_abort_failure.py
# VERSION: v1.0.0-P12C-R4N-P9-TRANSACTION-ABORT-FAILURE
# AUTHORITY BOUNDARY: transaction failure observation only
# TENANT POSTURE: no invented tenant authority
# FAIL-CLOSED POSTURE: abort failure cannot produce success
# FINANCIAL EXECUTION AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
