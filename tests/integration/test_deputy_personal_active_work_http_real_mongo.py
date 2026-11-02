"""Live-IAM real-Mongo certificate for deputy personal active-work reads.

TITLE: WILSY OS Deputy Personal Work and Field Capability Live-IAM Real-Mongo Certificate
VERSION: v1.2.0-L8-6E-CURRENT-ASSIGNMENT-REAL-MONGO-CERT
AUTHORITY: Host-backed certification of DEPUTY IAM + L8-6B/L8-6C/L8-6D reads.
EPITOME: Preserve durable personal-work proof and certify real current P2
         ServiceAttempt rows produce exact bound-deputy field capabilities whose
         opaque evidence locators equal durable evidence_identity values, while
         SHERIFF and missing binding remain denied without cross-role fallback.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_deputy_personal_active_work_http_real_mongo.py
COLLABORATION / OWNERSHIP: Host certificate for L8-6C/L8-6D read composition.
                            IAM, L8-6B, P1/P2/L8-0/L8-5/P5M retain canonical
                            authority; command mutation remains separately gated.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG: 2026-11-02 v1.2.0-L8-6E-CURRENT-ASSIGNMENT-REAL-MONGO-CERT binds router reads to a caller-owned Mongo snapshot, provisions explicit P4B pointer/receipt fixtures, and pins the combined router version.
CHANGELOG: 2026-09-23 v1.1.0-L8-6D-DEPUTY-FIELD-CAPABILITY-LIVE-IAM-RM-CERT
           adds real-Mongo field-capability proof for exact durable current
           evidence_identity, ALLOCATED/ATTEMPTED command-kind mapping, sheriff
           denial, and router v1.5.0 binding while preserving L8-6C coverage.
           2026-09-23 v1.1.0-L8-6D-DEPUTY-FIELD-CAPABILITY-LIVE-IAM-RM-CERT
           establishes durable deputy allow, sheriff denial, exact bound-deputy
           filtering, current-state supersession, missing-binding denial,
           foreign work exclusion, and bounded non-financial response proof.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic principals/deputies/attempts.
TENANT BOUNDARY: IAM, binding and lifecycle evidence all use one exact tenant.
AUTHORITY BOUNDARY: Host personal-work/capability read certificate only; capability is not lifecycle mutation/service authorization.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Setup uses durable writes; product read route owns no tx.
FAIL-CLOSED DECLARATION: Runtime/IAM/binding/evidence/locator/capability/scope
                         failure denies without sheriff queue, command fallback,
                         or invented personal work.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import sys
from typing import Any, Iterator
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.api.legal_operations_router as legal_router
import tools.eos.api.tenant_authorization_http as authorization_http
import tools.eos.auth.authentication as authentication
import tools.eos.auth.tenant_access as tenant_access
import tools.eos.kernel.db as kernel_db
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepository,
)
from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.legal_operations.domain.deputy_principal_binding import (
    DeputyPrincipalBinding,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    Deputy,
    ServiceAttempt,
    ServiceAttemptState,
)
from tools.eos.legal_operations.registry.deputy_principal_binding_registry import (
    COLLECTION as BINDING_COLLECTION,
    DeputyPrincipalBindingRegistry,
)
from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ALLOCATION_CURRENT_COLLECTION,
    ALLOCATION_RECEIPT_COLLECTION,
    ProcessServiceAllocationCurrent,
    ProcessServiceAllocationReceipt,
    ProcessServiceAllocationRegistry,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.2.0-L8-6E-CURRENT-ASSIGNMENT-REAL-MONGO-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 23, 20, 0, tzinfo=timezone.utc)


class _PrincipalReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(self, principal_id: str, *, session: Any = None) -> Any:
        return PrincipalAuthorityRepository.get(
            principal_id,
            self.collection,
            session=session,
        )


class _MembershipReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> Any:
        return TenantMembershipRepository.resolve(
            principal_id,
            tenant_id,
            self.collection,
            session=session,
        )


class _RoleReader:
    """Resolve business roles and final authorization roles from split stores."""

    def __init__(self, role_collection: Any, business_collection: Any) -> None:
        self.role_collection = role_collection
        self.business_collection = business_collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> Any:
        if role_id in TENANT_ROLES:
            try:
                value = TenantBusinessRoleRepository.resolve(
                    principal_id,
                    tenant_id,
                    self.business_collection,
                    session=session,
                )
            except TenantBusinessRoleNotFoundError as error:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
                ) from error
            if value.business_role != role_id:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
                )
            return value
        return RoleAssignmentRepository.resolve(
            principal_id,
            tenant_id,
            role_id,
            self.role_collection,
            session=session,
        )


@pytest.fixture
def mongo_context(monkeypatch: pytest.MonkeyPatch) -> Iterator[dict[str, Any]]:
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        retryWrites=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(
                f"L8_6C_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(f"L8_6C_REPLICA_SET_MISMATCH:{hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_6C_WRITABLE_PRIMARY_UNAVAILABLE")

        database = client.get_database(
            f"l8_6c_personal_work_{uuid.uuid4().hex}",
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        collections = {
            "lifecycle": database.get_collection(LIFECYCLE_COLLECTION),
            "binding": database.get_collection(BINDING_COLLECTION),
            "principal": database.get_collection("principal_authorities"),
            "membership": database.get_collection("tenant_memberships"),
            "business": database.get_collection("tenant_business_roles"),
            "role": database.get_collection("role_assignments"),
            "allocation_receipts": database.get_collection(ALLOCATION_RECEIPT_COLLECTION),
            "allocation_current": database.get_collection(ALLOCATION_CURRENT_COLLECTION),
        }
        LegalOperationsLifecycleRegistry.ensure_indexes(collections["lifecycle"])
        DeputyPrincipalBindingRegistry.ensure_indexes(collections["binding"])
        PrincipalAuthorityRepository.ensure_indexes(collections["principal"])
        TenantMembershipRepository.ensure_indexes(collections["membership"])
        TenantBusinessRoleRepository.ensure_indexes(collections["business"])
        RoleAssignmentRepository.ensure_indexes(collections["role"])
        ProcessServiceAllocationRegistry.ensure_indexes(
            collections["allocation_receipts"], collections["allocation_current"]
        )
        monkeypatch.setattr(kernel_db, "get_client", lambda: client)
        monkeypatch.setattr(kernel_db, "get_database", lambda: database)
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


def _seed_iam(
    collections: dict[str, Any],
    *,
    principal_id: str,
    tenant_id: str,
    business_role: str,
    authorization_role: str,
) -> None:
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0),
        collections["principal"],
    )
    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            principal_id,
            tenant_id,
            TenantMembershipStatus.ACTIVE,
            0,
        ),
        collections["membership"],
    )
    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            principal_id,
            tenant_id,
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
            principal_id,
            tenant_id,
            authorization_role,
            RoleAssignmentStatus.ACTIVE,
            0,
        ),
        collections["role"],
    )


def _deputy(
    collections: dict[str, Any],
    *,
    tenant_id: str,
    deputy_id: str,
) -> Deputy:
    value = Deputy(
        tenant_id=tenant_id,
        deputy_id=deputy_id,
        sheriff_office_id="office-1",
        display_name=f"Deputy {deputy_id}",
        badge_reference=f"badge-{deputy_id}",
        evidence_reference=f"directory-{deputy_id}",
    )
    LegalOperationsLifecycleRegistry.create(value, collections["lifecycle"])
    return value


def _bind(
    collections: dict[str, Any],
    *,
    tenant_id: str,
    principal_id: str,
    deputy: Deputy,
) -> None:
    value = DeputyPrincipalBinding.from_deputy(
        principal_id=principal_id,
        deputy=deputy,
        bound_at=NOW,
        evidence_reference="binding-evidence",
    )
    DeputyPrincipalBindingRegistry.create(value, collections["binding"])


def _persist_attempt_chain(
    collections: dict[str, Any],
    *,
    tenant_id: str,
    attempt_id: str,
    deputy_id: str,
    terminal: ServiceAttemptState | None = None,
    attempted: bool = False,
) -> None:
    allocated = ServiceAttempt(
        tenant_id=tenant_id,
        attempt_id=attempt_id,
        instruction_id=f"instruction-{attempt_id}",
        document_id=f"document-{attempt_id}",
        deputy_id=deputy_id,
        allocated_at=NOW,
        allocation_evidence_reference=f"allocation-{attempt_id}",
    )
    LegalOperationsLifecycleRegistry.create(allocated, collections["lifecycle"])
    _seed_allocation_currentness(collections, tenant_id, allocated)
    if terminal is ServiceAttemptState.CANCELLED:
        cancelled = allocated.transition_to(
            ServiceAttemptState.CANCELLED,
            evidence_reference=f"cancelled-{attempt_id}",
            occurred_at=NOW + timedelta(minutes=1),
        )
        LegalOperationsLifecycleRegistry.create(cancelled, collections["lifecycle"])
        return
    if attempted or terminal is not None:
        attempted_value = allocated.transition_to(
            ServiceAttemptState.ATTEMPTED,
            evidence_reference=f"attempted-{attempt_id}",
            occurred_at=NOW + timedelta(minutes=1),
        )
        LegalOperationsLifecycleRegistry.create(
            attempted_value,
            collections["lifecycle"],
        )
        if terminal is not None:
            terminal_value = attempted_value.transition_to(
                terminal,
                evidence_reference=f"terminal-{attempt_id}",
                evidence_fingerprint="a" * 128,
                occurred_at=NOW + timedelta(minutes=2),
            )
            LegalOperationsLifecycleRegistry.create(
                terminal_value,
                collections["lifecycle"],
            )


def _seed_allocation_currentness(
    collections: dict[str, Any], tenant_id: str, attempt: ServiceAttempt
) -> None:
    """Seed test-only prior currentness and persist its matching P4B receipt."""
    source_fingerprint = "a" * 128
    prior_chain_fingerprint = "b" * 128
    prior_head_fingerprint = "c" * 128
    prior = ProcessServiceAllocationCurrent(
        tenant_id=tenant_id, document_id=attempt.document_id,
        process_document_fingerprint=source_fingerprint,
        custody_chain_fingerprint=prior_chain_fingerprint,
        custody_head_event_id=f"custody-head-{attempt.attempt_id}",
        custody_head_fingerprint=prior_head_fingerprint,
        custody_head_sequence_number=2, current_holder_reference="office-1",
        authority_evidence_reference=f"migration-head-{attempt.attempt_id}",
        authority_evidence_fingerprint="d" * 128,
    )
    receipt = ProcessServiceAllocationReceipt(
        tenant_id=tenant_id,
        allocation_command_id=f"allocation-command-{attempt.attempt_id}",
        idempotency_key=f"idempotency-{attempt.attempt_id}",
        instruction_id=attempt.instruction_id,
        case_matter_id=f"matter-{attempt.attempt_id}",
        document_id=attempt.document_id, district_id="district-1",
        sheriff_office_id="office-1", deputy_id=attempt.deputy_id,
        assignment_decision_id=f"assignment-{attempt.attempt_id}",
        assignment_decision_fingerprint="e" * 128,
        source_instruction_fingerprint="f" * 128,
        source_document_fingerprint=source_fingerprint,
        source_district_fingerprint="1" * 128,
        source_sheriff_office_fingerprint="2" * 128,
        source_deputy_fingerprint="3" * 128,
        prior_custody_chain_fingerprint=prior_chain_fingerprint,
        prior_custody_head_event_id=prior.custody_head_event_id,
        prior_custody_head_fingerprint=prior_head_fingerprint,
        prior_custody_head_sequence_number=prior.custody_head_sequence_number,
        from_holder_reference="office-1", to_holder_reference=attempt.deputy_id,
        allocation_custody_event_id=f"allocation-event-{attempt.attempt_id}",
        allocation_evidence_reference=attempt.allocation_evidence_reference,
        allocated_at=attempt.allocated_at, allocated_document_fingerprint="4" * 128,
        allocation_custody_event_fingerprint="5" * 128,
        result_custody_chain_fingerprint="6" * 128,
    )
    client = collections["lifecycle"].database.client
    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        collections["allocation_current"].insert_one(prior.to_dict(), session=session)
        ProcessServiceAllocationRegistry.persist_receipt_and_advance_current(
            receipt, prior, collections["allocation_receipts"],
            collections["allocation_current"], session=session,
        )
        session.commit_transaction()


def _identity(principal_id: str, tenant_id: str) -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=principal_id,
        tenant_id=tenant_id,
        username=principal_id,
        email=f"{principal_id}@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )


def _app(
    context: dict[str, Any],
    *,
    principal_id: str,
    tenant_id: str,
) -> FastAPI:
    app = FastAPI()
    register_error_handlers(app, debug=False)
    collections = context["collections"]
    app.dependency_overrides[authorization_http.get_current_identity] = (
        lambda: _identity(principal_id, tenant_id)
    )
    app.dependency_overrides[
        authentication.get_principal_authority_repository
    ] = lambda: _PrincipalReader(collections["principal"])
    app.dependency_overrides[
        tenant_access.get_tenant_membership_repository
    ] = lambda: _MembershipReader(collections["membership"])
    app.dependency_overrides[
        authorization_http.get_role_assignment_repository
    ] = lambda: _RoleReader(
        collections["role"],
        collections["business"],
    )
    app.dependency_overrides[legal_router.get_lifecycle_collection] = (
        lambda: collections["lifecycle"]
    )
    app.dependency_overrides[
        legal_router.get_deputy_principal_binding_collection
    ] = lambda: collections["binding"]
    assert legal_router._DEPUTY_QUEUE_READ not in app.dependency_overrides
    app.include_router(legal_router.router, prefix="/api")
    return app


def _get(
    context: dict[str, Any],
    *,
    principal_id: str,
    tenant_id: str,
    path: str = "/deputy/active-work",
) -> Any:
    """Issue one authenticated Legal Operations deputy read request."""
    with TestClient(
        _app(context, principal_id=principal_id, tenant_id=tenant_id)
    ) as client:
        return client.get(
            f"/api/legal-operations{path}",
            headers={"X-Tenant-ID": tenant_id},
        )


def test_real_deputy_gets_only_bound_active_work_with_current_supersession(
    mongo_context: dict[str, Any],
) -> None:
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"principal-{uuid.uuid4().hex}"
    deputy_id = f"deputy-{uuid.uuid4().hex}"
    other_deputy = f"deputy-{uuid.uuid4().hex}"

    _seed_iam(
        collections,
        principal_id=principal,
        tenant_id=tenant,
        business_role="tenant_deputy",
        authorization_role="DEPUTY",
    )
    deputy = _deputy(collections, tenant_id=tenant, deputy_id=deputy_id)
    _deputy(collections, tenant_id=tenant, deputy_id=other_deputy)
    _bind(
        collections,
        tenant_id=tenant,
        principal_id=principal,
        deputy=deputy,
    )

    _persist_attempt_chain(
        collections,
        tenant_id=tenant,
        attempt_id="attempt-allocated",
        deputy_id=deputy_id,
    )
    _persist_attempt_chain(
        collections,
        tenant_id=tenant,
        attempt_id="attempt-attempted",
        deputy_id=deputy_id,
        attempted=True,
    )
    _persist_attempt_chain(
        collections,
        tenant_id=tenant,
        attempt_id="attempt-completed",
        deputy_id=deputy_id,
        terminal=ServiceAttemptState.COMPLETED,
    )
    _persist_attempt_chain(
        collections,
        tenant_id=tenant,
        attempt_id="attempt-other",
        deputy_id=other_deputy,
    )

    response = _get(
        mongo_context,
        principal_id=principal,
        tenant_id=tenant,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == tenant
    assert body["visibility"] == "DEPUTY_PERSONAL_ACTIVE_WORK"
    assert body["deputy_id"] == deputy_id
    assert [
        item["attempt_id"] for item in body["active_attempts"]
    ] == ["attempt-allocated", "attempt-attempted"]
    assert all(item["deputy_id"] == deputy_id for item in body["active_attempts"])
    assert "attempt-completed" not in str(body)
    assert "attempt-other" not in str(body)


def test_real_deputy_field_capabilities_match_exact_current_p2_locators(
    mongo_context: dict[str, Any],
) -> None:
    """Capability locators equal the actual durable current snapshot identities."""
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"principal-{uuid.uuid4().hex}"
    deputy_id = f"deputy-{uuid.uuid4().hex}"

    _seed_iam(
        collections,
        principal_id=principal,
        tenant_id=tenant,
        business_role="tenant_deputy",
        authorization_role="DEPUTY",
    )
    deputy = _deputy(collections, tenant_id=tenant, deputy_id=deputy_id)
    _bind(
        collections,
        tenant_id=tenant,
        principal_id=principal,
        deputy=deputy,
    )
    _persist_attempt_chain(
        collections,
        tenant_id=tenant,
        attempt_id="attempt-allocated",
        deputy_id=deputy_id,
    )
    _persist_attempt_chain(
        collections,
        tenant_id=tenant,
        attempt_id="attempt-attempted",
        deputy_id=deputy_id,
        attempted=True,
    )

    response = _get(
        mongo_context,
        principal_id=principal,
        tenant_id=tenant,
        path="/deputy/field-capabilities",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == tenant
    assert body["visibility"] == "DEPUTY_FIELD_COMMAND_CAPABILITIES"
    assert body["deputy_id"] == deputy_id
    assert [value["attempt_id"] for value in body["capabilities"]] == [
        "attempt-allocated",
        "attempt-attempted",
    ]

    rows = list(
        collections["lifecycle"].find(
            {
                "tenant_id": tenant,
                "entity_type": "ServiceAttempt",
            }
        )
    )
    by_attempt_state = {
        (
            row["entity_identity"],
            row["p1_payload"]["state"],
        ): row["evidence_identity"]
        for row in rows
    }
    allocated, attempted = body["capabilities"]
    assert allocated["current_state"] == "ALLOCATED"
    assert allocated["current_evidence_identity"] == by_attempt_state[
        ("attempt-allocated", "ALLOCATED")
    ]
    assert allocated["next_command_kinds"] == [
        "TRANSITION_TO_ATTEMPTED"
    ]
    assert attempted["current_state"] == "ATTEMPTED"
    assert attempted["current_evidence_identity"] == by_attempt_state[
        ("attempt-attempted", "ATTEMPTED")
    ]
    assert attempted["next_command_kinds"] == [
        "RECORD_COMPLETED_OUTCOME",
        "RECORD_NOT_COMPLETED_OUTCOME",
    ]
    assert all(value["deputy_id"] == deputy_id for value in body["capabilities"])


def test_real_sheriff_is_denied_deputy_personal_route(
    mongo_context: dict[str, Any],
) -> None:
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    sheriff = f"sheriff-{uuid.uuid4().hex}"
    _seed_iam(
        collections,
        principal_id=sheriff,
        tenant_id=tenant,
        business_role="tenant_sheriff",
        authorization_role="SHERIFF",
    )

    response = _get(
        mongo_context,
        principal_id=sheriff,
        tenant_id=tenant,
    )
    capability_response = _get(
        mongo_context,
        principal_id=sheriff,
        tenant_id=tenant,
        path="/deputy/field-capabilities",
    )

    assert response.status_code == 403
    assert capability_response.status_code == 403
    assert collections["binding"].count_documents({}) == 0


def test_real_authorized_deputy_without_binding_is_denied_without_fallback(
    mongo_context: dict[str, Any],
) -> None:
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"principal-{uuid.uuid4().hex}"
    deputy_id = f"deputy-{uuid.uuid4().hex}"
    _seed_iam(
        collections,
        principal_id=principal,
        tenant_id=tenant,
        business_role="tenant_deputy",
        authorization_role="DEPUTY",
    )
    _deputy(collections, tenant_id=tenant, deputy_id=deputy_id)
    _persist_attempt_chain(
        collections,
        tenant_id=tenant,
        attempt_id="attempt-unbound",
        deputy_id=deputy_id,
    )

    response = _get(
        mongo_context,
        principal_id=principal,
        tenant_id=tenant,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "DEPUTY_IDENTITY_BINDING_REQUIRED"
    assert "attempt-unbound" not in response.text


def test_real_response_excludes_sheriff_invented_and_financial_truth(
    mongo_context: dict[str, Any],
) -> None:
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"principal-{uuid.uuid4().hex}"
    deputy_id = f"deputy-{uuid.uuid4().hex}"
    _seed_iam(
        collections,
        principal_id=principal,
        tenant_id=tenant,
        business_role="tenant_deputy",
        authorization_role="DEPUTY",
    )
    deputy = _deputy(collections, tenant_id=tenant, deputy_id=deputy_id)
    _bind(
        collections,
        tenant_id=tenant,
        principal_id=principal,
        deputy=deputy,
    )
    _persist_attempt_chain(
        collections,
        tenant_id=tenant,
        attempt_id="attempt-1",
        deputy_id=deputy_id,
    )

    response = _get(
        mongo_context,
        principal_id=principal,
        tenant_id=tenant,
    )
    assert response.status_code == 200
    serialized = str(response.json()).casefold()
    for forbidden in (
        "office_receipt",
        "deputy_assignment",
        "principal_id",
        "urgent",
        "distance",
        "gps",
        "billing",
        "invoice",
        "payment",
        "settlement",
        "revenue",
        "ai_score",
        "client_name",
    ):
        assert forbidden not in serialized

    assert legal_router.VERSION == (
        "v1.19.0-L8-6E-D22B5-SUBSCRIPTION-ADMISSION"
    )
    assert VERSION == (
        "v1.2.0-L8-6E-CURRENT-ASSIGNMENT-REAL-MONGO-CERT"
    )


# ARTIFACT: test_deputy_personal_active_work_http_real_mongo.py
# VERSION: v1.2.0-L8-6E-CURRENT-ASSIGNMENT-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: live-IAM real-Mongo bound-deputy personal-work and field-capability read certificate only
# TENANT POSTURE: exact authorized tenant + immutable principal-to-Deputy binding
# FAIL-CLOSED POSTURE: sheriff/missing-binding/evidence/locator/capability/scope failures deny without queue or command fallback
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
