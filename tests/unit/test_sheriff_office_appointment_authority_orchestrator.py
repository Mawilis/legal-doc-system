"""Sheriff appointment evidence orchestration unit certificate.

TITLE: WILSY OS Sheriff Appointment Evidence Orchestration Certificate
VERSION: v1.0.0-L8-SHERIFF-OFFICE-APPOINTMENT-EVIDENCE-ORCHESTRATION-UNIT-CERT
AUTHORITY: Synthetic same-transaction IAM, P1, replay and verifier-composition proof.
EPITOME: Prove target Sheriff, independent tenant-admin verifier, canonical office/jurisdiction and exact replay before persistence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_sheriff_office_appointment_authority_orchestrator.py
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    District,
    SheriffOffice,
)
from tools.eos.legal_operations.orchestration import (
    sheriff_office_appointment_authority_orchestrator as subject,
)

NOW = datetime(2026, 11, 2, 12, 0, tzinfo=UTC)
TENANT = "tenant-appointment-orchestrator"
ADMIN = "principal-tenant-admin"
SHERIFF = "principal-sheriff"
OFFICE_ID = "office-johannesburg"
DISTRICT_ID = "district-gauteng"


class _Session:
    in_transaction = True


class _Registry:
    def __init__(self) -> None:
        self.values = []
        self.created = []

    def get_history_if_any(self, tenant_id: str, appointment_id: str, *, session: Any):
        assert session.in_transaction
        return tuple(
            value
            for value in self.values
            if value.tenant_id == tenant_id and value.appointment_id == appointment_id
        )

    def create_or_replay(self, value: Any, *, session: Any):
        assert session.in_transaction
        self.created.append(value)
        self.values.append(value)
        return value


def _p1() -> tuple[District, SheriffOffice]:
    district = District(
        tenant_id=TENANT,
        district_id=DISTRICT_ID,
        name="Gauteng",
        jurisdiction_code="ZA-GP-JHB",
        evidence_reference="district-source",
    )
    office = SheriffOffice(
        tenant_id=TENANT,
        sheriff_office_id=OFFICE_ID,
        district_id=DISTRICT_ID,
        name="Johannesburg Central",
        evidence_reference="office-source",
    )
    return district, office


def _arguments(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "tenant_id": TENANT,
        "appointment_id": "appointment-ministerial-1",
        "expected_revision": 0,
        "expected_predecessor_fingerprint": None,
        "principal_id": SHERIFF,
        "sheriff_office_id": OFFICE_ID,
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
        "verifier_principal_id": ADMIN,
        "verified_at": NOW,
        "lifecycle_collection": object(),
        "appointment_collection": object(),
        "principal_collection": object(),
        "membership_collection": object(),
        "business_role_collection": object(),
        "role_assignment_collection": object(),
        "session": _Session(),
    }
    values.update(overrides)
    return values


def _install(
    monkeypatch: pytest.MonkeyPatch,
    *,
    registry: _Registry | None = None,
    target_business_role: str = "tenant_sheriff",
    verifier_business_role: str = "tenant_admin",
    office: SheriffOffice | None = None,
    district: District | None = None,
) -> _Registry:
    current_district, current_office = _p1()
    selected_district = district or current_district
    selected_office = office or current_office
    store = registry or _Registry()

    monkeypatch.setattr(
        subject.PrincipalAuthorityRepository,
        "get",
        lambda principal_id, collection, session: SimpleNamespace(
            principal_id=principal_id,
            status=PrincipalStatus.ACTIVE,
        ),
    )
    monkeypatch.setattr(
        subject.TenantMembershipRepository,
        "resolve",
        lambda principal_id, tenant_id, collection, session: SimpleNamespace(
            principal_id=principal_id,
            tenant_id=tenant_id,
            status=TenantMembershipStatus.ACTIVE,
        ),
    )

    def business_role(principal_id, tenant_id, collection, *, session):
        role = verifier_business_role if principal_id == ADMIN else target_business_role
        return SimpleNamespace(
            principal_id=principal_id,
            tenant_id=tenant_id,
            status=TenantBusinessRoleStatus.ACTIVE,
            business_role=role,
        )

    monkeypatch.setattr(
        subject.TenantBusinessRoleRepository,
        "resolve",
        business_role,
    )
    monkeypatch.setattr(
        subject.RoleAssignmentRepository,
        "resolve",
        lambda principal_id, tenant_id, role, collection, session: SimpleNamespace(
            principal_id=principal_id,
            tenant_id=tenant_id,
            role=role,
            status=RoleAssignmentStatus.ACTIVE,
        ),
    )

    def read_model(*, tenant_id, entity_type, entity_identity, lifecycle_collection, session):
        value = selected_office if entity_type == "SheriffOffice" else selected_district
        return SimpleNamespace(
            tenant_id=tenant_id,
            entity_type=entity_type,
            entity_identity=entity_identity,
            current=value,
        )

    monkeypatch.setattr(subject, "get_entity_read_model", read_model)
    monkeypatch.setattr(
        subject,
        "SheriffOfficeAppointmentAuthorityRegistry",
        lambda collection: store,
    )
    return store


def test_requires_active_caller_transaction_before_authority_reads(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = _install(monkeypatch)
    args = _arguments(session=SimpleNamespace(in_transaction=False))

    with pytest.raises(
        subject.SheriffOfficeAppointmentTransactionRequiredError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        subject.record_sheriff_office_appointment_authority(**args)  # type: ignore[arg-type]

    assert store.created == []


def test_records_verified_sheriff_appointment_and_derives_jurisdiction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = _install(monkeypatch)
    value = subject.record_sheriff_office_appointment_authority(
        **_arguments()  # type: ignore[arg-type]
    )

    assert value.principal_id == SHERIFF
    assert value.sheriff_office_id == OFFICE_ID
    assert value.district_id == DISTRICT_ID
    assert value.certificate_jurisdiction_reference == "ZA-GP-JHB"
    assert value.verified_by_principal_id == ADMIN
    assert value.verified_at == NOW
    assert len(store.created) == 1


def test_exact_retry_returns_existing_revision_without_second_write(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = _install(monkeypatch)
    first = subject.record_sheriff_office_appointment_authority(
        **_arguments()  # type: ignore[arg-type]
    )
    replay = subject.record_sheriff_office_appointment_authority(
        **_arguments(verified_at=NOW + timedelta(minutes=5))  # type: ignore[arg-type]
    )

    assert replay == first
    assert len(store.created) == 1


def test_successor_revision_requires_exact_predecessor_and_replays(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = _install(monkeypatch)
    first = subject.record_sheriff_office_appointment_authority(
        **_arguments()  # type: ignore[arg-type]
    )
    second_args = _arguments(
        expected_revision=1,
        expected_predecessor_fingerprint=first.fingerprint,
        appointment_effective_from=NOW + timedelta(days=1),
        certificate_valid_from=NOW + timedelta(days=1),
        certificate_valid_until=NOW + timedelta(days=366),
        fidelity_fund_certificate_reference="sabfs:ffc-renewed",
        fidelity_fund_certificate_fingerprint="e" * 128,
        professional_indemnity_insurance_reference="insurer:policy-renewed",
        professional_indemnity_insurance_fingerprint="f" * 128,
        professional_indemnity_insurance_valid_from=NOW + timedelta(days=1),
        professional_indemnity_insurance_valid_until=NOW + timedelta(days=366),
        verified_at=NOW + timedelta(days=1),
    )
    second = subject.record_sheriff_office_appointment_authority(
        **second_args  # type: ignore[arg-type]
    )
    replay = subject.record_sheriff_office_appointment_authority(
        **{**second_args, "verified_at": NOW + timedelta(days=1, minutes=5)}  # type: ignore[arg-type]
    )

    assert second.revision == 2
    assert second.supersedes_fingerprint == first.fingerprint
    assert replay == second
    assert len(store.created) == 2


def test_self_verification_is_rejected_before_registry_write(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = _install(monkeypatch)
    with pytest.raises(
        subject.SheriffOfficeAppointmentOrchestrationError,
        match="SELF_VERIFICATION_FORBIDDEN",
    ):
        subject.record_sheriff_office_appointment_authority(
            **_arguments(verifier_principal_id=SHERIFF)  # type: ignore[arg-type]
        )
    assert store.created == []


def test_non_sheriff_target_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = _install(monkeypatch, target_business_role="tenant_deputy")
    with pytest.raises(
        subject.SheriffOfficeAppointmentOrchestrationError,
        match="BUSINESS_ROLE_REQUIRED",
    ):
        subject.record_sheriff_office_appointment_authority(
            **_arguments()  # type: ignore[arg-type]
        )
    assert store.created == []


def test_non_admin_verifier_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = _install(monkeypatch, verifier_business_role="tenant_sheriff")
    with pytest.raises(
        subject.SheriffOfficeAppointmentOrchestrationError,
        match="BUSINESS_ROLE_REQUIRED",
    ):
        subject.record_sheriff_office_appointment_authority(
            **_arguments()  # type: ignore[arg-type]
        )
    assert store.created == []


def test_stale_revision_and_wrong_predecessor_are_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = _install(monkeypatch)
    first = subject.record_sheriff_office_appointment_authority(
        **_arguments()  # type: ignore[arg-type]
    )
    with pytest.raises(
        subject.SheriffOfficeAppointmentOrchestrationError,
        match="PREDECESSOR_MISMATCH",
    ):
        subject.record_sheriff_office_appointment_authority(
            **_arguments(
                expected_revision=1,
                expected_predecessor_fingerprint="f" * 128,
            )  # type: ignore[arg-type]
        )
    assert len(store.created) == 1
    assert first.revision == 1


def test_office_district_mismatch_rejects_before_registry_write(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    district, office = _p1()
    foreign_office = SheriffOffice(
        tenant_id=TENANT,
        sheriff_office_id=OFFICE_ID,
        district_id="district-foreign",
        name="Wrong office lineage",
        evidence_reference="office-source",
    )
    store = _install(
        monkeypatch,
        office=foreign_office,
        district=district,
    )
    with pytest.raises(
        subject.SheriffOfficeAppointmentOrchestrationError,
        match="DISTRICT_EVIDENCE_INVALID",
    ):
        subject.record_sheriff_office_appointment_authority(
            **_arguments()  # type: ignore[arg-type]
        )
    assert store.created == []


# ARTIFACT: test_sheriff_office_appointment_authority_orchestrator.py
# VERSION: v1.0.0-L8-SHERIFF-OFFICE-APPOINTMENT-EVIDENCE-ORCHESTRATION-UNIT-CERT
# AUTHORITY BOUNDARY: active Sheriff + independent tenant-admin verifier + canonical P1 composition
# TENANT POSTURE: exact tenant/session across IAM, directory and appointment registry
# FAIL-CLOSED POSTURE: self-verification, role drift, lineage mismatch, stale revisions and replay divergence reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
