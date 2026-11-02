"""Real-Mongo Sheriff appointment orchestration certificate.

TITLE: WILSY OS Sheriff Appointment Authority Real-Mongo Certificate
VERSION: v1.0.0-L8-SHERIFF-APPOINTMENT-AUTHORITY-REAL-MONGO-CERT
AUTHORITY: Host-backed current IAM, canonical P1, transaction, replay and append-only evidence proof.
EPITOME: Prove one active tenant Sheriff plus independent tenant admin can record current jurisdiction-bound appointment, FFC and indemnity evidence against canonical office truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_sheriff_office_appointment_authority_real_mongo.py
COLLABORATION / OWNERSHIP: IAM repositories own principal/membership/business-role/authorization-role facts; P1/L8-0 own District and SheriffOffice truth; appointment orchestrator composes same-transaction authority; appointment registry owns immutable history/currentness.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG: v1.0.0 proves real replica-set commit, exact replay, abort, currentness, multi-office appointments, wrong-role denial, self-verification denial, overlap conflict and foreign-office isolation.
COMPLIANCE: Sheriffs Act 90 of 1986, sections 2, 3, 5 and 30-34; POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenants/principals/offices; no real appointment, FFC, insurance, or customer data.
TENANT BOUNDARY: Every IAM, P1, and appointment record is exact-tenant scoped.
AUTHORITY BOUNDARY: Test proves WILSY admission of human-attested external facts only; no appointment issuance or external document authentication.
TRANSACTION BOUNDARY: Test owns each replica-set transaction; production orchestrator only receives the already-active session.
FAIL-CLOSED DECLARATION: Missing/inactive/wrong IAM, self-verification, P1 mismatch, stale revision, overlap, corruption, or transaction abort never creates authority.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import os
import sys
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    District,
    SheriffOffice,
)
from tools.eos.legal_operations.orchestration.sheriff_office_appointment_authority_orchestrator import (
    SheriffOfficeAppointmentOrchestrationError,
    record_sheriff_office_appointment_authority,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
    LegalOperationsLifecycleRegistry,
)
from tools.eos.legal_operations.registry.sheriff_office_appointment_authority_registry import (
    COLLECTION_NAME as APPOINTMENT_COLLECTION,
    SheriffOfficeAppointmentAuthorityRegistry,
)

VERSION = "v1.0.0-L8-SHERIFF-APPOINTMENT-AUTHORITY-REAL-MONGO-CERT"
MONGO_URI = os.getenv("WILSY_SHERIFF_APPOINTMENT_REAL_MONGO_URI")
EXPECTED_REPLICA_SET = "wilsySheriffAppointmentRS"
NOW = datetime(2026, 11, 2, 14, 0, tzinfo=UTC)


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Yield one verified writable isolated replica-set database; runtime failure is fatal."""
    if not MONGO_URI:
        pytest.skip("WILSY_SHERIFF_APPOINTMENT_REAL_MONGO_URI is not configured")
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5_000,
        retryWrites=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(
                f"L8_SOA_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(
                f"L8_SOA_MONGO_REPLICA_SET_MISMATCH:{hello.get('setName')!r}"
            )
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_SOA_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")

        database = client[f"legal_ops_sheriff_appointment_{uuid.uuid4().hex}"]
        options = {
            "write_concern": WriteConcern(w="majority", j=True),
            "read_concern": ReadConcern("majority"),
        }
        collections = {
            "lifecycle": database.get_collection(LIFECYCLE_COLLECTION, **options),
            "appointment": database.get_collection(APPOINTMENT_COLLECTION, **options),
            "principal": database.get_collection("principal_authorities", **options),
            "membership": database.get_collection("tenant_memberships", **options),
            "business": database.get_collection("tenant_business_roles", **options),
            "role": database.get_collection("role_assignments", **options),
        }
        LegalOperationsLifecycleRegistry.ensure_indexes(collections["lifecycle"])
        SheriffOfficeAppointmentAuthorityRegistry(
            collections["appointment"]
        ).ensure_indexes()
        PrincipalAuthorityRepository.ensure_indexes(collections["principal"])
        TenantMembershipRepository.ensure_indexes(collections["membership"])
        TenantBusinessRoleRepository.ensure_indexes(collections["business"])
        RoleAssignmentRepository.ensure_indexes(collections["role"])
        yield {"client": client, "database": database, "collections": collections}
    finally:
        active_error = sys.exc_info()[0] is not None
        try:
            if database is not None:
                try:
                    client.drop_database(database.name)
                except PyMongoError:
                    if not active_error:
                        raise
        finally:
            client.close()


def _seed_principal(
    collections: dict[str, Any],
    tenant: str,
    principal: str,
    *,
    business_role: str,
    authorization_role: str,
    authorization_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE,
) -> None:
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(principal, PrincipalStatus.ACTIVE, 0),
        collections["principal"],
    )
    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            principal,
            tenant,
            TenantMembershipStatus.ACTIVE,
            0,
        ),
        collections["membership"],
    )
    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            principal,
            tenant,
            business_role,
            TenantBusinessRoleStatus.ACTIVE,
            0,
            NOW,
            None,
        ),
        collections["business"],
    )
    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            principal,
            tenant,
            authorization_role,
            authorization_status,
            0,
        ),
        collections["role"],
    )


def _seed(
    collections: dict[str, Any],
    tenant: str,
    sheriff_principal: str,
    admin_principal: str,
    *,
    sheriff_business_role: str = "tenant_sheriff",
    sheriff_authorization_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE,
    office_id: str = "office-johannesburg",
    district_id: str = "district-gauteng",
    jurisdiction_code: str = "ZA-GP-JHB",
) -> None:
    _seed_principal(
        collections,
        tenant,
        sheriff_principal,
        business_role=sheriff_business_role,
        authorization_role="SHERIFF",
        authorization_status=sheriff_authorization_status,
    )
    _seed_principal(
        collections,
        tenant,
        admin_principal,
        business_role="tenant_admin",
        authorization_role="ENTERPRISE_ADMIN",
    )
    district = District(
        tenant_id=tenant,
        district_id=district_id,
        name=f"District {district_id}",
        jurisdiction_code=jurisdiction_code,
        evidence_reference=f"district-evidence-{district_id}",
    )
    office = SheriffOffice(
        tenant_id=tenant,
        sheriff_office_id=office_id,
        district_id=district_id,
        name=f"Sheriff Office {office_id}",
        evidence_reference=f"office-evidence-{office_id}",
    )
    LegalOperationsLifecycleRegistry.create(district, collections["lifecycle"])
    LegalOperationsLifecycleRegistry.create(office, collections["lifecycle"])


def _record(
    collections: dict[str, Any],
    tenant: str,
    sheriff_principal: str,
    admin_principal: str,
    session: Any,
    *,
    appointment_id: str = "appointment-1",
    expected_revision: int = 0,
    expected_predecessor_fingerprint: str | None = None,
    office_id: str = "office-johannesburg",
    appointment_effective_from: datetime = NOW - timedelta(days=30),
    appointment_effective_until: datetime | None = None,
    certificate_valid_from: datetime = NOW - timedelta(days=5),
    certificate_valid_until: datetime = NOW + timedelta(days=360),
    insurance_valid_from: datetime = NOW - timedelta(days=1),
    insurance_valid_until: datetime = NOW + timedelta(days=365),
    seed: str = "a",
    verifier_principal_id: str | None = None,
    verified_at: datetime = NOW,
):
    return record_sheriff_office_appointment_authority(
        tenant_id=tenant,
        appointment_id=appointment_id,
        expected_revision=expected_revision,
        expected_predecessor_fingerprint=expected_predecessor_fingerprint,
        principal_id=sheriff_principal,
        sheriff_office_id=office_id,
        appointment_kind="PERMANENT",
        appointment_instrument_reference=f"gazette:appointment:{appointment_id}",
        appointment_instrument_fingerprint=seed * 128,
        office_scope_instrument_reference=f"gazette:office-scope:{appointment_id}",
        office_scope_instrument_fingerprint=chr(ord(seed) + 1) * 128,
        fidelity_fund_certificate_reference=f"sabfs:ffc:{appointment_id}",
        fidelity_fund_certificate_fingerprint=chr(ord(seed) + 2) * 128,
        professional_indemnity_insurance_reference=f"insurer:pi:{appointment_id}",
        professional_indemnity_insurance_fingerprint=chr(ord(seed) + 3) * 128,
        appointment_effective_from=appointment_effective_from,
        appointment_effective_until=appointment_effective_until,
        certificate_valid_from=certificate_valid_from,
        certificate_valid_until=certificate_valid_until,
        professional_indemnity_insurance_valid_from=insurance_valid_from,
        professional_indemnity_insurance_valid_until=insurance_valid_until,
        verifier_principal_id=verifier_principal_id or admin_principal,
        verified_at=verified_at,
        lifecycle_collection=collections["lifecycle"],
        appointment_collection=collections["appointment"],
        principal_collection=collections["principal"],
        membership_collection=collections["membership"],
        business_role_collection=collections["business"],
        role_assignment_collection=collections["role"],
        session=session,
    )


def _transaction(session: Any) -> None:
    session.start_transaction(
        read_concern=ReadConcern("snapshot"),
        write_concern=WriteConcern(w="majority", j=True),
    )


def test_real_mongo_commit_exact_replay_and_currentness(
    mongo_context: dict[str, Any],
) -> None:
    client, collections = mongo_context["client"], mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    sheriff, admin = f"sheriff-{uuid.uuid4().hex}", f"admin-{uuid.uuid4().hex}"
    _seed(collections, tenant, sheriff, admin)

    with client.start_session() as session:
        _transaction(session)
        created = _record(collections, tenant, sheriff, admin, session)
        session.commit_transaction()

    with client.start_session() as session:
        _transaction(session)
        replay = _record(
            collections,
            tenant,
            sheriff,
            admin,
            session,
            verified_at=NOW + timedelta(minutes=5),
        )
        current = SheriffOfficeAppointmentAuthorityRegistry(
            collections["appointment"]
        ).list_current_for_principal(
            tenant,
            sheriff,
            NOW,
            session=session,
        )
        session.commit_transaction()

    assert replay == created
    assert current == (created,)
    assert collections["appointment"].count_documents({"tenant_id": tenant}) == 1


def test_real_mongo_caller_abort_leaves_no_appointment(
    mongo_context: dict[str, Any],
) -> None:
    client, collections = mongo_context["client"], mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    sheriff, admin = f"sheriff-{uuid.uuid4().hex}", f"admin-{uuid.uuid4().hex}"
    _seed(collections, tenant, sheriff, admin)

    with client.start_session() as session:
        _transaction(session)
        created = _record(collections, tenant, sheriff, admin, session)
        assert created.revision == 1
        session.abort_transaction()

    assert collections["appointment"].count_documents({"tenant_id": tenant}) == 0


def test_real_mongo_wrong_sheriff_role_and_self_verification_write_nothing(
    mongo_context: dict[str, Any],
) -> None:
    client, collections = mongo_context["client"], mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    sheriff, admin = f"sheriff-{uuid.uuid4().hex}", f"admin-{uuid.uuid4().hex}"
    _seed(
        collections,
        tenant,
        sheriff,
        admin,
        sheriff_business_role="tenant_deputy",
    )

    with client.start_session() as session:
        _transaction(session)
        with pytest.raises(SheriffOfficeAppointmentOrchestrationError) as caught:
            _record(collections, tenant, sheriff, admin, session)
        assert caught.value.code == "L8_SOA_BUSINESS_ROLE_REQUIRED"
        session.abort_transaction()

    tenant_2 = f"tenant-{uuid.uuid4().hex}"
    sheriff_2, admin_2 = f"sheriff-{uuid.uuid4().hex}", f"admin-{uuid.uuid4().hex}"
    _seed(collections, tenant_2, sheriff_2, admin_2)

    with client.start_session() as session:
        _transaction(session)
        with pytest.raises(SheriffOfficeAppointmentOrchestrationError) as self_verify:
            _record(
                collections,
                tenant_2,
                sheriff_2,
                admin_2,
                session,
                verifier_principal_id=sheriff_2,
            )
        assert self_verify.value.code == "L8_SOA_SELF_VERIFICATION_FORBIDDEN"
        session.abort_transaction()

    assert collections["appointment"].count_documents({}) == 0


def test_real_mongo_multi_office_appointments_are_independently_current(
    mongo_context: dict[str, Any],
) -> None:
    client, collections = mongo_context["client"], mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    sheriff, admin = f"sheriff-{uuid.uuid4().hex}", f"admin-{uuid.uuid4().hex}"
    _seed(collections, tenant, sheriff, admin)

    second_district = District(
        tenant_id=tenant,
        district_id="district-western-cape",
        name="Western Cape",
        jurisdiction_code="ZA-WC-CPT",
        evidence_reference="district-western-cape-evidence",
    )
    second_office = SheriffOffice(
        tenant_id=tenant,
        sheriff_office_id="office-cape-town",
        district_id=second_district.district_id,
        name="Cape Town Sheriff Office",
        evidence_reference="office-cape-town-evidence",
    )
    LegalOperationsLifecycleRegistry.create(second_district, collections["lifecycle"])
    LegalOperationsLifecycleRegistry.create(second_office, collections["lifecycle"])

    with client.start_session() as session:
        _transaction(session)
        first = _record(collections, tenant, sheriff, admin, session)
        second = _record(
            collections,
            tenant,
            sheriff,
            admin,
            session,
            appointment_id="appointment-cape-town",
            office_id="office-cape-town",
            seed="5",
        )
        session.commit_transaction()

    with client.start_session() as session:
        _transaction(session)
        current = SheriffOfficeAppointmentAuthorityRegistry(
            collections["appointment"]
        ).list_current_for_principal(
            tenant,
            sheriff,
            NOW,
            session=session,
        )
        session.commit_transaction()

    assert {item.sheriff_office_id for item in current} == {
        "office-johannesburg",
        "office-cape-town",
    }
    assert {item.certificate_jurisdiction_reference for item in current} == {
        "ZA-GP-JHB",
        "ZA-WC-CPT",
    }
    assert first.principal_id == second.principal_id == sheriff


def test_real_mongo_overlapping_second_appointment_conflicts(
    mongo_context: dict[str, Any],
) -> None:
    client, collections = mongo_context["client"], mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    sheriff, admin = f"sheriff-{uuid.uuid4().hex}", f"admin-{uuid.uuid4().hex}"
    _seed(collections, tenant, sheriff, admin)

    with client.start_session() as session:
        _transaction(session)
        first = _record(collections, tenant, sheriff, admin, session)
        session.commit_transaction()

    with client.start_session() as session:
        _transaction(session)
        with pytest.raises(SheriffOfficeAppointmentOrchestrationError) as caught:
            _record(
                collections,
                tenant,
                sheriff,
                admin,
                session,
                appointment_id="appointment-overlap",
                seed="5",
            )
        assert caught.value.code == "L8_SOA_APPOINTMENT_CONFLICT"
        session.abort_transaction()

    assert collections["appointment"].count_documents({"tenant_id": tenant}) == 1
    assert first.revision == 1


def test_real_mongo_wrong_predecessor_and_foreign_office_fail_closed(
    mongo_context: dict[str, Any],
) -> None:
    client, collections = mongo_context["client"], mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    sheriff, admin = f"sheriff-{uuid.uuid4().hex}", f"admin-{uuid.uuid4().hex}"
    _seed(collections, tenant, sheriff, admin)

    with client.start_session() as session:
        _transaction(session)
        _record(collections, tenant, sheriff, admin, session)
        session.commit_transaction()

    with client.start_session() as session:
        _transaction(session)
        with pytest.raises(SheriffOfficeAppointmentOrchestrationError) as predecessor:
            _record(
                collections,
                tenant,
                sheriff,
                admin,
                session,
                expected_revision=1,
                expected_predecessor_fingerprint="f" * 128,
            )
        assert predecessor.value.code == "L8_SOA_PREDECESSOR_MISMATCH"
        session.abort_transaction()

    with client.start_session() as session:
        _transaction(session)
        with pytest.raises(SheriffOfficeAppointmentOrchestrationError) as foreign:
            _record(
                collections,
                tenant,
                sheriff,
                admin,
                session,
                appointment_id="appointment-foreign-office",
                office_id="office-not-in-this-tenant",
                seed="5",
            )
        assert foreign.value.code == "L8_SOA_OFFICE_NOT_FOUND"
        session.abort_transaction()

    assert collections["appointment"].count_documents({"tenant_id": tenant}) == 1


# ARTIFACT: test_sheriff_office_appointment_authority_real_mongo.py
# VERSION: v1.0.0-L8-SHERIFF-APPOINTMENT-AUTHORITY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real IAM + P1 + appointment registry composition only
# TENANT POSTURE: all authority and evidence reads are exact-tenant and session scoped
# FAIL-CLOSED POSTURE: abort, wrong role, self-verification, stale lineage, overlap and foreign office reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
