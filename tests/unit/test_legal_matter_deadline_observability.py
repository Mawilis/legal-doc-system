"""D5 operational observability certificate for Legal Matter Deadline HTTP.

TITLE: Wilsy OS Legal Matter Deadline Operational Observability Certificate
VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D5-DEADLINE-OBSERVABILITY-CERT
AUTHORITY: Direct telemetry certificate only; no legal or persistence authority.
EPITOME: Prove pseudonymized bounded success/failure telemetry around the already
         certified D3B1 deadline HTTP surface without exposing evidence content
         or changing transaction outcomes.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_matter_deadline_observability.py
COLLABORATION / OWNERSHIP: D3B1 owns HTTP semantics; D5 certifies telemetry only.
CERTIFICATION / UPDATE DATE: 2026-10-11
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic identifiers only; raw tenant/matter/deadline
                             and legal evidence content must not enter telemetry.
TENANT BOUNDARY: Telemetry receives authorized context but stores only SHA3-512
                 pseudonymous locators.
AUTHORITY BOUNDARY: Observation only; logs never create legal facts or authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Logging failure cannot change canonical HTTP outcomes.
"""
from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import tools.eos.api.legal_matter_deadline_router as deadline_api
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.domain.legal_matter_deadline import (
    LegalMatterDeadline,
    LegalMatterDeadlineKind,
    LegalMatterDeadlineSourceType,
    LegalMatterDeadlineStatus,
)
from tools.eos.legal_operations.service.legal_matter_deadline_service import (
    LegalMatterDeadlineServiceError,
)


TENANT = "tenant-observability"
MATTER = "matter-observability"
DEADLINE = "deadline-observability"
NOW = datetime(2026, 10, 11, 13, 0, tzinfo=timezone.utc)
DUE = datetime(2026, 10, 20, 13, 0, tzinfo=timezone.utc)
SOURCE_REFERENCE = "evidence://private/court-order"
SOURCE_FINGERPRINT = "d" * 128


class _Session:
    def __init__(self) -> None:
        self.in_transaction = False

    def __enter__(self) -> "_Session":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def start_transaction(self) -> None:
        self.in_transaction = True

    def commit_transaction(self) -> None:
        self.in_transaction = False

    def abort_transaction(self) -> None:
        self.in_transaction = False


class _Client:
    def __init__(self, session: _Session) -> None:
        self._session = session

    def start_session(self) -> _Session:
        return self._session


class _Database:
    def get_collection(self, name: str) -> str:
        return name


def _context() -> TenantAuthorizationContext:
    identity = SovereignIdentity(
        identity_id="principal-observability",
        tenant_id=TENANT,
        username="operator",
        email="operator@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )
    return TenantAuthorizationContext(
        identity=identity,
        tenant_id=TENANT,
        decision=TenantAuthorizationDecision(
            True,
            TenantAuthorizationReason.AUTHORIZED,
            "tenant_legal_partner",
            "LEGAL_PARTNER",
        ),
    )


def _deadline(*, matter: str = MATTER) -> LegalMatterDeadline:
    return LegalMatterDeadline(
        tenant_id=TENANT,
        case_matter_id=matter,
        deadline_id=DEADLINE,
        deadline_kind=LegalMatterDeadlineKind.FILING,
        title="Private evidenced filing title",
        due_at=DUE,
        source_type=LegalMatterDeadlineSourceType.COURT_ORDER,
        source_reference=SOURCE_REFERENCE,
        source_evidence_fingerprint=SOURCE_FINGERPRINT,
        jurisdiction_reference="jurisdiction://court/example",
        created_at=NOW,
        status=LegalMatterDeadlineStatus.ACTIVE,
    )


def _payload() -> dict[str, Any]:
    return {
        "deadline_id": DEADLINE,
        "deadline_kind": "FILING",
        "title": "Private evidenced filing title",
        "due_at": DUE.isoformat(),
        "source_type": "COURT_ORDER",
        "source_reference": SOURCE_REFERENCE,
        "source_evidence_fingerprint": SOURCE_FINGERPRINT,
        "jurisdiction_reference": "jurisdiction://court/example",
        "created_at": NOW.isoformat(),
        "status": "ACTIVE",
    }


def _client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    session = _Session()
    monkeypatch.setattr(
        deadline_api,
        "_db_handles",
        lambda: (_Client(session), _Database()),
    )
    app = FastAPI()
    app.dependency_overrides[deadline_api._WRITE] = _context
    app.dependency_overrides[deadline_api._READ] = _context
    app.include_router(deadline_api.router, prefix="/api")
    return TestClient(app)


def _observations(caplog: pytest.LogCaptureFixture) -> list[dict[str, Any]]:
    return [
        getattr(record, "wilsy_observation")
        for record in caplog.records
        if hasattr(record, "wilsy_observation")
    ]


def test_create_success_emits_only_pseudonymized_bounded_observation(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = _client(monkeypatch)
    monkeypatch.setattr(
        deadline_api,
        "record_legal_matter_deadline",
        lambda **_kwargs: _deadline(),
    )
    caplog.set_level(logging.INFO, logger="WilsyOS.API.LegalMatterDeadlineRouter")

    response = client.post(
        f"/api/legal-operations/matters/{MATTER}/deadlines",
        json=_payload(),
    )
    assert response.status_code == 200

    observations = _observations(caplog)
    assert len(observations) == 1
    observation = observations[0]
    assert observation == {
        "event": "LEGAL_MATTER_DEADLINE_HTTP",
        "operation": "CREATE",
        "outcome": "SUCCESS",
        "tenant_ref": deadline_api._telemetry_ref(TENANT),
        "matter_ref": deadline_api._telemetry_ref(MATTER),
        "deadline_ref": deadline_api._telemetry_ref(DEADLINE),
        "http_status": 200,
    }
    rendered = str(observation)
    for forbidden in (
        TENANT,
        MATTER,
        DEADLINE,
        SOURCE_REFERENCE,
        SOURCE_FINGERPRINT,
        "Private evidenced filing title",
        "principal-observability",
        "LEGAL_PARTNER",
    ):
        assert forbidden not in rendered


def test_list_success_emits_count_without_evidence_content(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = _client(monkeypatch)
    monkeypatch.setattr(
        deadline_api,
        "list_legal_matter_deadlines",
        lambda **_kwargs: (_deadline(), _deadline()),
    )
    caplog.set_level(logging.INFO, logger="WilsyOS.API.LegalMatterDeadlineRouter")

    response = client.get(f"/api/legal-operations/matters/{MATTER}/deadlines")
    assert response.status_code == 200

    observation = _observations(caplog)[0]
    assert observation["operation"] == "LIST"
    assert observation["outcome"] == "SUCCESS"
    assert observation["count"] == 2
    assert "deadline_ref" not in observation
    assert SOURCE_REFERENCE not in str(observation)


def test_service_failure_emits_bounded_error_code_and_http_status(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = _client(monkeypatch)

    def fail(**_kwargs: Any) -> LegalMatterDeadline:
        raise LegalMatterDeadlineServiceError("DEADLINE_CONFLICT")

    monkeypatch.setattr(deadline_api, "record_legal_matter_deadline", fail)
    caplog.set_level(logging.WARNING, logger="WilsyOS.API.LegalMatterDeadlineRouter")

    response = client.post(
        f"/api/legal-operations/matters/{MATTER}/deadlines",
        json=_payload(),
    )
    assert response.status_code == 409

    observation = _observations(caplog)[0]
    assert observation["operation"] == "CREATE"
    assert observation["outcome"] == "ERROR"
    assert observation["http_status"] == 409
    assert observation["error_code"] == "DEADLINE_CONFLICT"


def test_detail_matter_mismatch_is_observed_as_bounded_not_available(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = _client(monkeypatch)
    monkeypatch.setattr(
        deadline_api,
        "get_legal_matter_deadline",
        lambda **_kwargs: _deadline(matter="matter-other"),
    )
    caplog.set_level(logging.WARNING, logger="WilsyOS.API.LegalMatterDeadlineRouter")

    response = client.get(
        f"/api/legal-operations/matters/{MATTER}/deadlines/{DEADLINE}"
    )
    assert response.status_code == 404

    observation = _observations(caplog)[0]
    assert observation["operation"] == "DETAIL"
    assert observation["outcome"] == "ERROR"
    assert observation["http_status"] == 404
    assert observation["error_code"] == "DEADLINE_NOT_AVAILABLE"


def test_logging_failure_never_changes_canonical_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _client(monkeypatch)
    monkeypatch.setattr(
        deadline_api,
        "record_legal_matter_deadline",
        lambda **_kwargs: _deadline(),
    )

    def broken_log(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("synthetic logger outage")

    monkeypatch.setattr(deadline_api.logger, "log", broken_log)

    response = client.post(
        f"/api/legal-operations/matters/{MATTER}/deadlines",
        json=_payload(),
    )
    assert response.status_code == 200
    assert response.json()["data"]["deadline_id"] == DEADLINE


def test_observability_version_and_source_boundaries_are_sealed() -> None:
    assert deadline_api.VERSION == (
        "v1.1.0-LEGAL-OPS-COMPLETION-D5-DEADLINE-OBSERVABILITY"
    )
    source = open(deadline_api.__file__, encoding="utf-8").read()
    assert "source_reference" not in source.split("def _observe(", 1)[1].split(
        "class LegalMatterDeadlineCommand", 1
    )[0]
    assert "source_evidence_fingerprint" not in source.split(
        "def _observe(", 1
    )[1].split("class LegalMatterDeadlineCommand", 1)[0]
    assert "payment_state" not in source.lower()
    assert "settlement_state" not in source.lower()
    assert "ai_inferred_due_at" not in source.lower()


# ARTIFACT: test_legal_matter_deadline_observability.py
# VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D5-DEADLINE-OBSERVABILITY-CERT
# AUTHORITY BOUNDARY: operational telemetry certificate only
# TENANT POSTURE: raw tenant/matter/deadline identifiers excluded from telemetry
# FAIL-CLOSED POSTURE: telemetry cannot alter legal or transaction outcomes
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
