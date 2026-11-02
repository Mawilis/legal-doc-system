"""Real-Mongo Sheriff appointment evidence registry certificate.

TITLE: WILSY OS Sheriff Appointment Evidence Real-Mongo Certificate
VERSION: v1.0.0-L8-SHERIFF-OFFICE-APPOINTMENT-EVIDENCE-REAL-MONGO-CERT
AUTHORITY: Host-backed durable registry, transaction, replay and currentness proof.
EPITOME: Certify append-only Sheriff appointment and FFC evidence under a replica-set transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_sheriff_office_appointment_authority_registry_real_mongo.py
TENANT BOUNDARY: Unique synthetic tenant and collection per test.
AUTHORITY BOUNDARY: Registry persistence/currentness only; no external appointment authentication or IAM.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import os
import uuid

import pytest
from pymongo import MongoClient

from tools.eos.legal_operations.domain.sheriff_office_appointment_authority import (
    SheriffOfficeAppointmentAuthority,
)
from tools.eos.legal_operations.registry.sheriff_office_appointment_authority_registry import (
    COLLECTION_NAME,
    SheriffOfficeAppointmentAuthorityRegistry,
    SheriffOfficeAppointmentConflictError,
)

URI = os.getenv("WILSY_SHERIFF_APPOINTMENT_REAL_MONGO_URI")
NOW = datetime(2026, 11, 2, 10, 0, tzinfo=UTC)


@pytest.fixture
def runtime():
    if not URI:
        pytest.skip("WILSY_SHERIFF_APPOINTMENT_REAL_MONGO_URI is not configured")
    client = MongoClient(URI, serverSelectionTimeoutMS=5_000)
    client.admin.command("ping")
    database_name = f"test_sheriff_appointment_{uuid.uuid4().hex}"
    database = client[database_name]
    registry = SheriffOfficeAppointmentAuthorityRegistry(
        database[COLLECTION_NAME]
    )
    registry.ensure_indexes()
    try:
        yield client, database, registry
    finally:
        client.drop_database(database_name)
        client.close()


def _authority(**overrides: object) -> SheriffOfficeAppointmentAuthority:
    values: dict[str, object] = {
        "tenant_id": "tenant-real-mongo",
        "appointment_id": "appointment-real-1",
        "revision": 1,
        "principal_id": "principal-real-1",
        "sheriff_office_id": "office-real-1",
        "district_id": "district-real-1",
        "appointment_kind": "PERMANENT",
        "appointment_instrument_reference": "gazette:real:notice-1",
        "appointment_instrument_fingerprint": "a" * 128,
        "office_scope_instrument_reference": "gazette:real:notice-1:schedule",
        "office_scope_instrument_fingerprint": "b" * 128,
        "fidelity_fund_certificate_reference": "sabfs:real:ffc-1",
        "fidelity_fund_certificate_fingerprint": "c" * 128,
        "certificate_jurisdiction_reference": "ZA-GP-JHB",
        "professional_indemnity_insurance_reference": "insurer:policy-2026-1",
        "professional_indemnity_insurance_fingerprint": "9" * 128,
        "professional_indemnity_insurance_valid_from": NOW - timedelta(days=1),
        "professional_indemnity_insurance_valid_until": NOW + timedelta(days=365),
        "appointment_effective_from": NOW - timedelta(days=30),
        "appointment_effective_until": None,
        "certificate_valid_from": NOW - timedelta(days=5),
        "certificate_valid_until": NOW + timedelta(days=360),
        "verified_by_principal_id": "principal-real-admin",
        "verified_at": NOW - timedelta(days=1),
        "supersedes_fingerprint": None,
    }
    values.update(overrides)
    return SheriffOfficeAppointmentAuthority(**values)  # type: ignore[arg-type]


def test_real_mongo_exact_replay_successor_and_currentness(runtime) -> None:
    client, _, registry = runtime
    first = _authority()
    second = _authority(
        revision=2,
        appointment_effective_from=NOW + timedelta(hours=1),
        certificate_valid_from=NOW + timedelta(hours=1),
        certificate_valid_until=NOW + timedelta(days=366),
        fidelity_fund_certificate_reference="sabfs:real:ffc-renewed",
        fidelity_fund_certificate_fingerprint="d" * 128,
        professional_indemnity_insurance_reference="insurer:policy-renewed",
        professional_indemnity_insurance_fingerprint="8" * 128,
        professional_indemnity_insurance_valid_from=NOW + timedelta(hours=1),
        professional_indemnity_insurance_valid_until=NOW + timedelta(days=366),
        verified_at=NOW,
        supersedes_fingerprint=first.fingerprint,
    )

    with client.start_session() as session:
        with session.start_transaction():
            assert registry.create_or_replay(first, session=session) == first

    with client.start_session() as session:
        with session.start_transaction():
            assert registry.create_or_replay(first, session=session) == first

    with client.start_session() as session:
        with session.start_transaction():
            assert registry.create_or_replay(second, session=session) == second

    with client.start_session() as session:
        with session.start_transaction():
            before = registry.list_current_for_principal(
                first.tenant_id,
                first.principal_id,
                NOW,
                session=session,
            )
            after = registry.list_current_for_principal(
                first.tenant_id,
                first.principal_id,
                NOW + timedelta(hours=1),
                session=session,
            )
            history = registry.get_history(
                first.tenant_id,
                first.appointment_id,
                session=session,
            )

    assert before == (first,)
    assert after == (second,)
    assert history == (first, second)


def test_real_mongo_multi_office_and_multi_sheriff_projection(runtime) -> None:
    client, _, registry = runtime
    first = _authority()
    another_office = _authority(
        appointment_id="appointment-real-cape-town",
        sheriff_office_id="office-real-cape-town",
        district_id="district-real-cape-town",
        appointment_instrument_reference="gazette:real:notice-2",
        appointment_instrument_fingerprint="d" * 128,
        office_scope_instrument_reference="gazette:real:notice-2:schedule",
        office_scope_instrument_fingerprint="e" * 128,
        fidelity_fund_certificate_reference="sabfs:real:ffc-2",
        fidelity_fund_certificate_fingerprint="f" * 128,
    )
    second_sheriff = _authority(
        appointment_id="appointment-real-second-sheriff",
        principal_id="principal-real-2",
        appointment_instrument_reference="gazette:real:notice-3",
        appointment_instrument_fingerprint="1" * 128,
        office_scope_instrument_reference="gazette:real:notice-3:schedule",
        office_scope_instrument_fingerprint="2" * 128,
        fidelity_fund_certificate_reference="sabfs:real:ffc-3",
        fidelity_fund_certificate_fingerprint="3" * 128,
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.create_or_replay(first, session=session)
            registry.create_or_replay(another_office, session=session)
            registry.create_or_replay(second_sheriff, session=session)

    with client.start_session() as session:
        with session.start_transaction():
            principal_offices = registry.list_current_for_principal(
                first.tenant_id,
                first.principal_id,
                NOW,
                session=session,
            )
            office_sheriffs = registry.list_current_for_office(
                first.tenant_id,
                first.sheriff_office_id,
                NOW,
                session=session,
            )

    assert {item.sheriff_office_id for item in principal_offices} == {
        first.sheriff_office_id,
        another_office.sheriff_office_id,
    }
    assert {item.principal_id for item in office_sheriffs} == {
        first.principal_id,
        second_sheriff.principal_id,
    }


def test_real_mongo_overlapping_same_principal_office_is_rejected(runtime) -> None:
    client, _, registry = runtime
    first = _authority()
    duplicate = _authority(
        appointment_id="appointment-real-overlap",
        appointment_instrument_reference="gazette:real:notice-overlap",
        appointment_instrument_fingerprint="d" * 128,
        office_scope_instrument_reference="gazette:real:notice-overlap:schedule",
        office_scope_instrument_fingerprint="e" * 128,
        fidelity_fund_certificate_reference="sabfs:real:ffc-overlap",
        fidelity_fund_certificate_fingerprint="f" * 128,
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.create_or_replay(first, session=session)

    with client.start_session() as session:
        with pytest.raises(
            SheriffOfficeAppointmentConflictError,
            match="PRINCIPAL_OFFICE_OVERLAP",
        ):
            with session.start_transaction():
                registry.create_or_replay(duplicate, session=session)


def test_real_mongo_foreign_tenant_is_non_disclosing(runtime) -> None:
    client, _, registry = runtime
    first = _authority()

    with client.start_session() as session:
        with session.start_transaction():
            registry.create_or_replay(first, session=session)

    with client.start_session() as session:
        with session.start_transaction():
            assert registry.list_current_for_principal(
                "foreign-tenant",
                first.principal_id,
                NOW,
                session=session,
            ) == ()


# ARTIFACT: test_sheriff_office_appointment_authority_registry_real_mongo.py
# VERSION: v1.0.0-L8-SHERIFF-OFFICE-APPOINTMENT-EVIDENCE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-database immutable persistence and currentness only
# TENANT POSTURE: exact tenant-first isolation and non-disclosure
# FAIL-CLOSED POSTURE: transaction, replay, overlap, and scope corruption reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
