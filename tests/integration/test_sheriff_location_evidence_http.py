"""Sheriff GPS read endpoint tests: appointment-bound office scope and access audit.

TITLE: WILSY OS Sheriff Appointment-Scoped Location Evidence HTTP Certificate
VERSION: v1.1.0-L8-SHERIFF-APPOINTMENT-SCOPED-LOCATION-READ-HTTP-CERT
AUTHORITY: Current tenant Sheriff IAM plus exact appointment, jurisdiction, FFC and indemnity evidence.
EPITOME: Prove a multi-office tenant can read only an attempt in an office for which the principal has current verified appointment authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_sheriff_location_evidence_http.py
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import tools.eos.api.legal_operations_router as read_api
from tools.eos.api.errors import register_error_handlers
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    District,
    ServiceAttempt,
    SheriffOffice,
)
from tools.eos.legal_operations.domain.sheriff_office_appointment_authority import (
    SheriffOfficeAppointmentAuthority,
)

TENANT, PRINCIPAL, OFFICE, ATTEMPT = (
    "tenant-sheriff-location",
    "sheriff-principal",
    "sheriff-office-1",
    "attempt-sheriff-1",
)
NOW = datetime(2026, 11, 2, 12, 0, tzinfo=UTC)
DISTRICT_ID = "district-gauteng"
JURISDICTION = "ZA-GP-JHB"


class Session:
    in_transaction = True


class Database:
    def get_collection(self, name: str) -> object:
        return SimpleNamespace(name=name)


def context(*, business_role: str = "tenant_sheriff") -> TenantAuthorizationContext:
    identity = SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id=TENANT,
        username="sheriff",
        email="sheriff@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
        session_reference=None,
    )
    decision = TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        business_role,
        "SHERIFF",
    )
    return TenantAuthorizationContext(identity, TENANT, decision)


def app() -> FastAPI:
    value = FastAPI()
    register_error_handlers(value, debug=False)
    value.dependency_overrides[read_api._QUEUE_READ] = context
    value.include_router(read_api.router, prefix="/api")
    return value


def _appointment(
    office_id: str,
    appointment_id: str,
    *,
    district_id: str = DISTRICT_ID,
    jurisdiction: str = JURISDICTION,
    appointment_until: datetime | None = None,
    certificate_until: datetime | None = None,
    insurance_until: datetime | None = None,
    seed: str = "a",
) -> SheriffOfficeAppointmentAuthority:
    return SheriffOfficeAppointmentAuthority(
        tenant_id=TENANT,
        appointment_id=appointment_id,
        revision=1,
        principal_id=PRINCIPAL,
        sheriff_office_id=office_id,
        district_id=district_id,
        appointment_kind="PERMANENT",
        appointment_instrument_reference=f"gazette:notice-{appointment_id}",
        appointment_instrument_fingerprint=seed * 128,
        office_scope_instrument_reference=f"gazette:notice-{appointment_id}:schedule",
        office_scope_instrument_fingerprint=chr(ord(seed) + 1) * 128,
        fidelity_fund_certificate_reference=f"sabfs:ffc-{appointment_id}",
        fidelity_fund_certificate_fingerprint=chr(ord(seed) + 2) * 128,
        certificate_jurisdiction_reference=jurisdiction,
        professional_indemnity_insurance_reference=f"insurer:policy-{appointment_id}",
        professional_indemnity_insurance_fingerprint=chr(ord(seed) + 3) * 128,
        professional_indemnity_insurance_valid_from=NOW - timedelta(days=1),
        professional_indemnity_insurance_valid_until=insurance_until or NOW + timedelta(days=365),
        appointment_effective_from=NOW - timedelta(days=30),
        appointment_effective_until=appointment_until,
        certificate_valid_from=NOW - timedelta(days=5),
        certificate_valid_until=certificate_until or NOW + timedelta(days=360),
        verified_by_principal_id="tenant-admin-verifier",
        verified_at=NOW - timedelta(days=1),
    )


def configure(
    monkeypatch: pytest.MonkeyPatch,
    *,
    appointments: tuple[SheriffOfficeAppointmentAuthority, ...],
    receipt_office_id: str = OFFICE,
    office_district_id: str = DISTRICT_ID,
    district_id: str = DISTRICT_ID,
    jurisdiction: str = JURISDICTION,
) -> list[dict[str, Any]]:
    database, session = Database(), Session()
    accesses: list[dict[str, Any]] = []
    pointer = SimpleNamespace(
        authority_evidence_reference="allocation-command-1",
        authority_evidence_fingerprint="a" * 128,
    )
    receipt = SimpleNamespace(
        fingerprint="a" * 128,
        tenant_id=TENANT,
        document_id="document-1",
        instruction_id="instruction-1",
        deputy_id="deputy-1",
        allocation_evidence_reference="allocation-1",
        sheriff_office_id=receipt_office_id,
    )
    attempt = ServiceAttempt(
        tenant_id=TENANT,
        attempt_id=ATTEMPT,
        document_id="document-1",
        instruction_id="instruction-1",
        deputy_id="deputy-1",
        allocated_at=NOW - timedelta(minutes=10),
        allocation_evidence_reference="allocation-1",
    )
    office = SheriffOffice(
        tenant_id=TENANT,
        sheriff_office_id=receipt_office_id,
        district_id=office_district_id,
        name="Johannesburg Central",
        evidence_reference="office-source",
    )
    district = District(
        tenant_id=TENANT,
        district_id=district_id,
        name="Gauteng",
        jurisdiction_code=jurisdiction,
        evidence_reference="district-source",
    )

    monkeypatch.setattr(
        read_api,
        "_workspace_projection_transaction",
        lambda callback: callback(session, database),
    )

    def read_model(*, tenant_id, entity_type, entity_identity, lifecycle_collection, session):
        current = {
            "ServiceAttempt": attempt,
            "SheriffOffice": office,
            "District": district,
        }[entity_type]
        return SimpleNamespace(
            tenant_id=tenant_id,
            entity_type=entity_type,
            entity_identity=entity_identity,
            current=current,
        )

    monkeypatch.setattr(read_api, "get_entity_read_model", read_model)
    monkeypatch.setattr(
        read_api,
        "list_entity_read_models",
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("tenant-wide office enumeration is forbidden")
        ),
    )

    class _AppointmentRegistry:
        def __init__(self, collection: Any) -> None:
            assert collection is not None

        def list_current_for_principal(
            self,
            tenant_id: str,
            principal_id: str,
            at: datetime,
            *,
            session: Any,
        ):
            assert tenant_id == TENANT
            assert principal_id == PRINCIPAL
            assert at == NOW
            assert session is not None
            return appointments

    monkeypatch.setattr(
        read_api,
        "SheriffOfficeAppointmentAuthorityRegistry",
        _AppointmentRegistry,
    )
    monkeypatch.setattr(read_api, "datetime", SimpleNamespace(now=lambda tz: NOW, UTC=UTC))
    monkeypatch.setattr(
        read_api,
        "ProcessServiceAllocationRegistry",
        SimpleNamespace(
            get_current=lambda *args, **kwargs: pointer,
            get_receipt_by_allocation_command_id=lambda *args, **kwargs: receipt,
        ),
    )
    monkeypatch.setattr(
        read_api,
        "ProcessServiceLocationEvidenceRegistry",
        SimpleNamespace(
            list_observations_for_attempt=lambda *args, **kwargs: (
                {"observation_id": "location-1", "latitude": -26.2, "longitude": 28.0},
            ),
            record_access=lambda **kwargs: accesses.append(kwargs),
        ),
    )
    return accesses


def test_multi_office_tenant_reads_only_the_exact_current_appointment_office(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = _appointment(OFFICE, "appointment-jhb", seed="a")
    second = _appointment(
        "office-cape-town",
        "appointment-cpt",
        district_id="district-western-cape",
        jurisdiction="ZA-WC-CPT",
        seed="5",
    )
    accesses = configure(monkeypatch, appointments=(first, second))

    with TestClient(app()) as client:
        response = client.get(
            f"/api/legal-operations/sheriff/attempts/{ATTEMPT}/location-evidence"
        )

    assert response.status_code == 200
    body = response.json()
    assert body["sheriff_office_id"] == OFFICE
    assert body["visibility"] == "CURRENT_VERIFIED_APPOINTMENT_OFFICE_LOCATION_EVIDENCE"
    assert body["appointment_id"] == "appointment-jhb"
    assert body["appointment_revision"] == 1
    assert body["observations"][0]["observation_id"] == "location-1"
    assert len(accesses) == 1
    assert accesses[0]["actor_principal_id"] == PRINCIPAL
    assert accesses[0]["actor_scope"] == "SHERIFF_OFFICE:" + OFFICE
    assert accesses[0]["grant_id"] == "all"
    assert accesses[0]["purpose"] == "SHERIFF_OFFICE_LOCATION_EVIDENCE_READ"


def test_sheriff_cannot_read_an_office_without_a_current_appointment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    other_office = _appointment(
        "office-cape-town",
        "appointment-cpt",
        district_id="district-western-cape",
        jurisdiction="ZA-WC-CPT",
        seed="5",
    )
    accesses = configure(monkeypatch, appointments=(other_office,))

    with TestClient(app()) as client:
        response = client.get(
            f"/api/legal-operations/sheriff/attempts/{ATTEMPT}/location-evidence"
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "SHERIFF_OFFICE_APPOINTMENT_REQUIRED"
    assert accesses == []


def test_sheriff_location_read_rejects_wrong_certificate_jurisdiction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    wrong_jurisdiction = _appointment(
        OFFICE,
        "appointment-wrong-jurisdiction",
        jurisdiction="ZA-WC-CPT",
        seed="5",
    )
    accesses = configure(monkeypatch, appointments=(wrong_jurisdiction,))

    with TestClient(app()) as client:
        response = client.get(
            f"/api/legal-operations/sheriff/attempts/{ATTEMPT}/location-evidence"
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "SHERIFF_OFFICE_APPOINTMENT_REQUIRED"
    assert accesses == []


def test_sheriff_location_read_rejects_expired_appointment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expired = _appointment(
        OFFICE,
        "appointment-expired",
        appointment_until=NOW,
        seed="a",
    )
    accesses = configure(monkeypatch, appointments=(expired,))

    with TestClient(app()) as client:
        response = client.get(
            f"/api/legal-operations/sheriff/attempts/{ATTEMPT}/location-evidence"
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "SHERIFF_OFFICE_APPOINTMENT_REQUIRED"
    assert accesses == []


def test_sheriff_location_read_rejects_expired_fidelity_fund_certificate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expired = _appointment(
        OFFICE,
        "appointment-expired-ffc",
        certificate_until=NOW,
        seed="a",
    )
    accesses = configure(monkeypatch, appointments=(expired,))

    with TestClient(app()) as client:
        response = client.get(
            f"/api/legal-operations/sheriff/attempts/{ATTEMPT}/location-evidence"
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "SHERIFF_OFFICE_APPOINTMENT_REQUIRED"
    assert accesses == []


def test_sheriff_location_read_rejects_expired_indemnity_insurance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expired = _appointment(
        OFFICE,
        "appointment-expired-insurance",
        insurance_until=NOW,
        seed="a",
    )
    accesses = configure(monkeypatch, appointments=(expired,))

    with TestClient(app()) as client:
        response = client.get(
            f"/api/legal-operations/sheriff/attempts/{ATTEMPT}/location-evidence"
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "SHERIFF_OFFICE_APPOINTMENT_REQUIRED"
    assert accesses == []


def test_non_sheriff_business_role_cannot_read_sheriff_location_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(read_api, "_workspace_projection_transaction", lambda callback: None)
    app_value = FastAPI()
    register_error_handlers(app_value, debug=False)
    app_value.dependency_overrides[read_api._QUEUE_READ] = lambda: context(
        business_role="tenant_deputy"
    )
    app_value.include_router(read_api.router, prefix="/api")

    with TestClient(app_value) as client:
        response = client.get(
            f"/api/legal-operations/sheriff/attempts/{ATTEMPT}/location-evidence"
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "LEGAL_OPERATIONS_SHERIFF_AUTHORITY_REQUIRED"


# ARTIFACT: test_sheriff_location_evidence_http.py
# VERSION: v1.1.0-L8-SHERIFF-APPOINTMENT-SCOPED-LOCATION-READ-HTTP-CERT
# AUTHORITY: current tenant Sheriff IAM plus current appointment, FFC and indemnity evidence for exact office
# AUDIT: every successful read records appointment fingerprint and exact office scope
# END OF WILSY OS SOVEREIGN ARTIFACT
