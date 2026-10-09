"""Host-backed certificate for Process Service directory provisioning.

TITLE: WILSY OS Process Service Directory Provisioning Real-Mongo Certificate
VERSION: v1.0.0-L8-1-PROCESS-SERVICE-DIRECTORY-PROVISIONING-RM-CERT
AUTHORITY: Host-backed certification of canonical L8-1 directory composition.
EPITOME: Prove District -> SheriffOffice -> Deputy provisioning, exact replay,
         active-transaction/session propagation, tenant isolation, divergence
         rejection, rollback, lineage enforcement, and non-financial durability
         against the writable Wilsy certification Mongo replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_process_service_directory_provisioning_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: L8-1 owns provisioning composition; P1 owns immutable
                            directory semantics; P2 owns durable persistence and
                            hydration; L8-0 owns immutable-current validation.
                            This certificate caller exclusively owns Mongo
                            sessions, transactions, commit, abort, and cleanup.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-1-PROCESS-SERVICE-DIRECTORY-PROVISIONING-RM-CERT
           establishes host-backed create/replay, full directory lineage,
           caller-session propagation, foreign-parent absence, same-identity
           divergence rejection, pre-existing divergent-history rejection,
           whole-transaction rollback, and financial-boundary evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenants and identifiers only;
                             no customer, provider, credential, secret, browser,
                             payment, or external-service data is used.
TENANT BOUNDARY: Every read and write is exact-tenant scoped. A District in one
                 tenant cannot authorize an office in another tenant, and
                 foreign existence remains bounded absence.
AUTHORITY BOUNDARY: Certificate only. Directory provisioning does not create IAM
                    roles, legal instructions, document receipt, allocation,
                    attempts, service, returns, invoices, payments, execution,
                    settlement, or accounting truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; persisted directory evidence is
                              certified to contain no financial-authority fields.
TRANSACTION BOUNDARY: This certificate starts every transaction explicitly with
                      snapshot read concern and majority+journaled write concern.
                      L8-1/P2 must receive the same active caller session and
                      never start, commit, abort, or retry that transaction.
FAIL-CLOSED DECLARATION: Runtime unavailability, wrong replica set, missing
                         writable primary, foreign/missing parent, immutable
                         divergence, corrupt history, session loss, rollback
                         leakage, or financial-authority leakage fails.
"""
from __future__ import annotations

from copy import deepcopy
import os
import sys
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.legal_operations.orchestration.process_service_directory_provisioning_orchestrator as l8_1
from tools.eos.legal_operations.domain.legal_operations_lifecycle import District
from tools.eos.legal_operations.orchestration.process_service_directory_provisioning_orchestrator import (
    VERSION as PRODUCTION_VERSION,
    ProcessServiceDirectoryProvisioningDisposition,
    ProcessServiceDirectoryProvisioningError,
    provision_deputy,
    provision_district,
    provision_sheriff_office,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION,
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.0-L8-1-PROCESS-SERVICE-DIRECTORY-PROVISIONING-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Yield one verified writable isolated database and clean it after the test.

    Host Mongo unavailability is a certificate failure rather than a skip:
    L8-1B is explicitly host-backed runtime evidence.
    """
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
                f"L8_1_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(
                f"L8_1_MONGO_REPLICA_SET_MISMATCH:{hello.get('setName')!r}"
            )
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_1_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")

        database = client[f"legal_ops_l8_1_directory_{uuid.uuid4().hex}"]
        lifecycle = database.get_collection(
            COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        yield {
            "client": client,
            "database": database,
            "lifecycle": lifecycle,
        }
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


def _transaction(client: Any) -> Any:
    """Start one caller-owned snapshot/majority transaction."""
    session = client.start_session()
    session.start_transaction(
        read_concern=ReadConcern("snapshot"),
        write_concern=WriteConcern(w="majority", j=True),
    )
    return session


def _tenant(prefix: str) -> str:
    """Return one valid isolated synthetic tenant identifier."""
    return f"{prefix}-{uuid.uuid4().hex}"


def _district_kwargs(tenant_id: str) -> dict[str, str]:
    """Return canonical synthetic District provisioning inputs."""
    return {
        "tenant_id": tenant_id,
        "district_id": "district-1",
        "name": "Johannesburg Central",
        "jurisdiction_code": "ZA-GP-JHB",
        "evidence_reference": "district-source",
    }


def _office_kwargs(tenant_id: str) -> dict[str, str]:
    """Return canonical synthetic SheriffOffice provisioning inputs."""
    return {
        "tenant_id": tenant_id,
        "sheriff_office_id": "office-1",
        "district_id": "district-1",
        "name": "Sheriff Johannesburg Central",
        "evidence_reference": "office-source",
    }


def _deputy_kwargs(tenant_id: str) -> dict[str, str]:
    """Return canonical synthetic Deputy provisioning inputs."""
    return {
        "tenant_id": tenant_id,
        "deputy_id": "deputy-1",
        "sheriff_office_id": "office-1",
        "display_name": "Deputy One",
        "badge_reference": "badge-1",
        "evidence_reference": "deputy-source",
    }


def _provision_full_lineage(
    *,
    tenant_id: str,
    lifecycle: Any,
    session: Any,
) -> tuple[Any, Any, Any]:
    """Provision District -> SheriffOffice -> Deputy in one caller transaction."""
    district = provision_district(
        **_district_kwargs(tenant_id),
        lifecycle_collection=lifecycle,
        session=session,
    )
    office = provision_sheriff_office(
        **_office_kwargs(tenant_id),
        lifecycle_collection=lifecycle,
        session=session,
    )
    deputy = provision_deputy(
        **_deputy_kwargs(tenant_id),
        lifecycle_collection=lifecycle,
        session=session,
    )
    return district, office, deputy


def _all_key_names(item: Any) -> set[str]:
    """Collect nested mapping keys for explicit financial-boundary assertions."""
    if isinstance(item, dict):
        names = set(item)
        for child in item.values():
            names.update(_all_key_names(child))
        return names
    if isinstance(item, list):
        names: set[str] = set()
        for child in item:
            names.update(_all_key_names(child))
        return names
    return set()


def test_real_mongo_full_lineage_commit_replay_and_session_propagation(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Certify committed lineage, exact no-write replay, and one caller session."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant_id = _tenant("tenant-l8-1-lineage")

    observed: list[tuple[str, object]] = []
    original_history = l8_1.LegalOperationsLifecycleRegistry.get_entity_history
    original_create = l8_1.LegalOperationsLifecycleRegistry.create

    def observed_history(
        tenant: str,
        entity_type: str,
        entity_identity: str,
        collection: Any,
        *,
        session: object = None,
    ) -> tuple[Any, ...]:
        observed.append(("history", session))
        return original_history(
            tenant,
            entity_type,
            entity_identity,
            collection,
            session=session,
        )

    def observed_create(
        value: Any,
        collection: Any,
        *,
        session: object = None,
        **kwargs: Any,
    ) -> Any:
        observed.append(("create", session))
        return original_create(
            value,
            collection,
            session=session,
            **kwargs,
        )

    monkeypatch.setattr(
        l8_1.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        staticmethod(observed_history),
    )
    monkeypatch.setattr(
        l8_1.LegalOperationsLifecycleRegistry,
        "create",
        staticmethod(observed_create),
    )

    session = _transaction(client)
    try:
        district, office, deputy = _provision_full_lineage(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=session,
        )
        assert district.disposition is ProcessServiceDirectoryProvisioningDisposition.CREATED
        assert office.disposition is ProcessServiceDirectoryProvisioningDisposition.CREATED
        assert deputy.disposition is ProcessServiceDirectoryProvisioningDisposition.CREATED
        assert observed
        assert all(observed_session is session for _, observed_session in observed)
        session.commit_transaction()
    finally:
        session.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant_id}) == 3
    assert lifecycle.count_documents(
        {"tenant_id": tenant_id, "entity_type": "District"}
    ) == 1
    assert lifecycle.count_documents(
        {"tenant_id": tenant_id, "entity_type": "SheriffOffice"}
    ) == 1
    assert lifecycle.count_documents(
        {"tenant_id": tenant_id, "entity_type": "Deputy"}
    ) == 1

    replay_session = _transaction(client)
    try:
        replay_district, replay_office, replay_deputy = _provision_full_lineage(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=replay_session,
        )
        assert replay_district.disposition is ProcessServiceDirectoryProvisioningDisposition.REPLAYED
        assert replay_office.disposition is ProcessServiceDirectoryProvisioningDisposition.REPLAYED
        assert replay_deputy.disposition is ProcessServiceDirectoryProvisioningDisposition.REPLAYED
        replay_session.commit_transaction()
    finally:
        replay_session.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant_id}) == 3
    histories = {
        entity_type: LegalOperationsLifecycleRegistry.get_entity_history(
            tenant_id,
            entity_type,
            identity,
            lifecycle,
        )
        for entity_type, identity in (
            ("District", "district-1"),
            ("SheriffOffice", "office-1"),
            ("Deputy", "deputy-1"),
        )
    }
    assert all(len(history) == 1 for history in histories.values())


def test_real_mongo_same_identity_divergence_and_foreign_parent_fail_closed(
    mongo_context: dict[str, Any],
) -> None:
    """Certify immutable divergence and foreign parent scope cannot write."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant_a = _tenant("tenant-l8-1-a")
    tenant_b = _tenant("tenant-l8-1-b")

    seed_session = _transaction(client)
    try:
        created = provision_district(
            **_district_kwargs(tenant_a),
            lifecycle_collection=lifecycle,
            session=seed_session,
        )
        assert created.disposition is ProcessServiceDirectoryProvisioningDisposition.CREATED
        seed_session.commit_transaction()
    finally:
        seed_session.end_session()

    divergent_session = _transaction(client)
    try:
        with pytest.raises(ProcessServiceDirectoryProvisioningError) as caught:
            provision_district(
                tenant_id=tenant_a,
                district_id="district-1",
                name="Changed District",
                jurisdiction_code="ZA-GP-JHB",
                evidence_reference="different-source",
                lifecycle_collection=lifecycle,
                session=divergent_session,
            )
        assert caught.value.code == "L8_1_DIRECTORY_IDENTITY_DIVERGENCE"
        divergent_session.abort_transaction()
    finally:
        divergent_session.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant_a}) == 1

    foreign_session = _transaction(client)
    try:
        with pytest.raises(ProcessServiceDirectoryProvisioningError) as foreign:
            provision_sheriff_office(
                **_office_kwargs(tenant_b),
                lifecycle_collection=lifecycle,
                session=foreign_session,
            )
        assert foreign.value.code == "L8_1_DISTRICT_NOT_FOUND"
        foreign_session.abort_transaction()
    finally:
        foreign_session.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant_b}) == 0


def test_real_mongo_whole_directory_transaction_abort_leaves_no_rows(
    mongo_context: dict[str, Any],
) -> None:
    """Certify the caller can abort the complete directory lineage atomically."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant_id = _tenant("tenant-l8-1-rollback")

    session = _transaction(client)
    try:
        district, office, deputy = _provision_full_lineage(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=session,
        )
        assert district.disposition is ProcessServiceDirectoryProvisioningDisposition.CREATED
        assert office.disposition is ProcessServiceDirectoryProvisioningDisposition.CREATED
        assert deputy.disposition is ProcessServiceDirectoryProvisioningDisposition.CREATED
        assert lifecycle.count_documents(
            {"tenant_id": tenant_id},
            session=session,
        ) == 3
        session.abort_transaction()
    finally:
        session.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant_id}) == 0


def test_real_mongo_preexisting_divergent_directory_history_rejects(
    mongo_context: dict[str, Any],
) -> None:
    """Certify legacy/corrupt immutable forks are never healed or selected."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant_id = _tenant("tenant-l8-1-history")

    first = District(
        tenant_id,
        "district-1",
        "Johannesburg Central",
        "ZA-GP-JHB",
        "district-source-1",
    )
    second = District(
        tenant_id,
        "district-1",
        "Johannesburg Central Changed",
        "ZA-GP-JHB",
        "district-source-2",
    )

    seed_session = _transaction(client)
    try:
        LegalOperationsLifecycleRegistry.create(
            first,
            lifecycle,
            session=seed_session,
        )
        LegalOperationsLifecycleRegistry.create(
            second,
            lifecycle,
            session=seed_session,
        )
        seed_session.commit_transaction()
    finally:
        seed_session.end_session()

    assert lifecycle.count_documents(
        {
            "tenant_id": tenant_id,
            "entity_type": "District",
            "entity_identity": "district-1",
        }
    ) == 2

    provision_session = _transaction(client)
    try:
        with pytest.raises(ProcessServiceDirectoryProvisioningError) as caught:
            provision_district(
                tenant_id=tenant_id,
                district_id="district-1",
                name="Johannesburg Central",
                jurisdiction_code="ZA-GP-JHB",
                evidence_reference="district-source-1",
                lifecycle_collection=lifecycle,
                session=provision_session,
            )
        assert caught.value.code == "L8_1_DIRECTORY_HISTORY_DIVERGENT"
        provision_session.abort_transaction()
    finally:
        provision_session.end_session()

    assert lifecycle.count_documents(
        {
            "tenant_id": tenant_id,
            "entity_type": "District",
            "entity_identity": "district-1",
        }
    ) == 2


def test_real_mongo_directory_records_have_no_financial_authority_fields(
    mongo_context: dict[str, Any],
) -> None:
    """Certify durable directory evidence cannot imply financial execution."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant_id = _tenant("tenant-l8-1-financial")

    session = _transaction(client)
    try:
        _provision_full_lineage(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=session,
        )
        session.commit_transaction()
    finally:
        session.end_session()

    documents = list(lifecycle.find({"tenant_id": tenant_id}))
    assert len(documents) == 3
    forbidden = {
        "payment",
        "settlement",
        "paid_state",
        "refund",
        "invoice",
        "billing_execution",
        "bank_execution",
        "provider_execution",
    }
    for document in documents:
        assert forbidden.isdisjoint(_all_key_names(deepcopy(document)))

    assert PRODUCTION_VERSION == "v1.0.1-L8-1-PROCESS-SERVICE-DIRECTORY-PROVISIONING"
    assert VERSION == "v1.0.0-L8-1-PROCESS-SERVICE-DIRECTORY-PROVISIONING-RM-CERT"


# ARTIFACT: test_process_service_directory_provisioning_orchestrator_real_mongo.py
# VERSION: v1.0.0-L8-1-PROCESS-SERVICE-DIRECTORY-PROVISIONING-RM-CERT
# AUTHORITY BOUNDARY: host-backed L8-1 directory provisioning certificate only
# TENANT POSTURE: UUID-isolated exact tenant scope with foreign-parent absence
# FAIL-CLOSED POSTURE: runtime/session/lineage/divergence/rollback leakage fails
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
