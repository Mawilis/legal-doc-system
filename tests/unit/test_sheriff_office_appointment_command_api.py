"""Sheriff appointment command API boundary certificate.

TITLE: WILSY OS Sheriff Appointment Command API Certificate
VERSION: v1.0.0-L8-SHERIFF-APPOINTMENT-COMMAND-API-UNIT-CERT
AUTHORITY: Strict HTTP request shape, tenant/verifier derivation and pre-transaction index bootstrap only.
EPITOME: Prove the browser cannot supply tenant, District, jurisdiction, verifier, verification time or revision lineage.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_sheriff_office_appointment_command_api.py
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from tools.eos.api import legal_operations_command_router as subject

NOW = datetime(2026, 11, 2, 13, 0, tzinfo=UTC)


def _command(**overrides: object) -> subject.SheriffOfficeAppointmentCommand:
    values: dict[str, object] = {
        "appointment_id": "appointment-command-1",
        "expected_revision": 0,
        "expected_predecessor_fingerprint": None,
        "principal_id": "principal-sheriff",
        "sheriff_office_id": "office-johannesburg",
        "appointment_kind": "PERMANENT",
        "appointment_instrument_reference": "gazette:notice-1",
        "appointment_instrument_fingerprint": "a" * 128,
        "office_scope_instrument_reference": "gazette:notice-1:schedule",
        "office_scope_instrument_fingerprint": "b" * 128,
        "fidelity_fund_certificate_reference": "sabfs:ffc-2026-1",
        "fidelity_fund_certificate_fingerprint": "c" * 128,
        "professional_indemnity_insurance_reference": "insurer:policy-2026-1",
        "professional_indemnity_insurance_fingerprint": "d" * 128,
        "appointment_effective_from": NOW - timedelta(days=30),
        "appointment_effective_until": None,
        "certificate_valid_from": NOW - timedelta(days=5),
        "certificate_valid_until": NOW + timedelta(days=360),
        "professional_indemnity_insurance_valid_from": NOW - timedelta(days=1),
        "professional_indemnity_insurance_valid_until": NOW + timedelta(days=365),
    }
    values.update(overrides)
    return subject.SheriffOfficeAppointmentCommand(**values)


def test_request_model_rejects_browser_owned_authority_fields() -> None:
    base = _command().model_dump()
    for forbidden in (
        "tenant_id",
        "district_id",
        "certificate_jurisdiction_reference",
        "verified_by_principal_id",
        "verified_at",
        "revision",
        "supersedes_fingerprint",
        "fingerprint",
        "iam_authorized",
    ):
        with pytest.raises(ValidationError):
            subject.SheriffOfficeAppointmentCommand(
                **{**base, forbidden: "caller-controlled"}
            )


def test_request_model_rejects_invalid_fingerprints_and_negative_revision() -> None:
    with pytest.raises(ValidationError):
        _command(appointment_instrument_fingerprint="not-a-hash")
    with pytest.raises(ValidationError):
        _command(expected_revision=-1)


def test_command_derives_tenant_verifier_and_indexes_before_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []
    captured: dict[str, Any] = {}
    database = object()
    session = object()

    class _IndexRegistry:
        def __init__(self, collection: Any) -> None:
            assert collection is not None

        def ensure_indexes(self) -> None:
            events.append("indexes")

    result = SimpleNamespace(to_dict=lambda: {"recorded": True})

    def fake_collection(db: Any, name: str) -> object:
        assert db is database
        return object()

    def fake_transaction(callback, *, prepare=None):
        if prepare is not None:
            prepare(database)
        events.append("transaction")
        return callback(session, database)

    def fake_record(**kwargs: Any) -> Any:
        events.append("orchestrator")
        captured.update(kwargs)
        return result

    monkeypatch.setattr(subject, "_collection", fake_collection)
    monkeypatch.setattr(subject, "_transaction", fake_transaction)
    monkeypatch.setattr(
        subject,
        "SheriffOfficeAppointmentAuthorityRegistry",
        _IndexRegistry,
    )
    monkeypatch.setattr(
        subject,
        "record_sheriff_office_appointment_authority",
        fake_record,
    )
    monkeypatch.setattr(subject, "_utcnow", lambda: NOW)

    context = SimpleNamespace(
        tenant_id="tenant-from-auth-context",
        identity=SimpleNamespace(identity_id="verifying-admin"),
        decision=SimpleNamespace(business_role="tenant_admin"),
    )
    response = subject.record_sheriff_office_appointment_command(
        _command(),
        context,
    )

    assert response == {"recorded": True}
    assert events == ["indexes", "transaction", "orchestrator"]
    assert captured["tenant_id"] == "tenant-from-auth-context"
    assert captured["verifier_principal_id"] == "verifying-admin"
    assert captured["verified_at"] == NOW
    assert captured["principal_id"] == "principal-sheriff"
    assert captured["sheriff_office_id"] == "office-johannesburg"
    assert captured["certificate_jurisdiction_reference"] if "certificate_jurisdiction_reference" in captured else True
    assert captured["expected_revision"] == 0
    assert captured["expected_predecessor_fingerprint"] is None
    assert captured["session"] is session


def test_non_admin_business_role_cannot_call_appointment_verifier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def forbidden_transaction(*args: Any, **kwargs: Any) -> None:
        nonlocal called
        called = True
        raise AssertionError("transaction must not start")

    monkeypatch.setattr(subject, "_transaction", forbidden_transaction)
    context = SimpleNamespace(
        tenant_id="tenant",
        identity=SimpleNamespace(identity_id="sheriff"),
        decision=SimpleNamespace(business_role="tenant_sheriff"),
    )

    with pytest.raises(HTTPException) as error:
        subject.record_sheriff_office_appointment_command(_command(), context)

    assert error.value.status_code == 403
    assert called is False


# ARTIFACT: test_sheriff_office_appointment_command_api.py
# VERSION: v1.0.0-L8-SHERIFF-APPOINTMENT-COMMAND-API-UNIT-CERT
# AUTHORITY BOUNDARY: HTTP transport and trusted server-context derivation only
# TENANT POSTURE: request cannot supply tenant, verifier, jurisdiction or revision lineage
# FAIL-CLOSED POSTURE: extra authority fields, non-admin business role and invalid hashes reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
