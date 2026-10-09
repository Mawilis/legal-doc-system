"""Direct certificate for Process Service directory provisioning.

TITLE: WILSY OS Process Service Directory Provisioning Certificate
VERSION: v1.0.1-L8-1-PROCESS-SERVICE-DIRECTORY-PROVISIONING-CERT
AUTHORITY: Direct certificate for canonical L8-1 directory composition only.
EPITOME: Prove transaction-required District -> SheriffOffice -> Deputy
         provisioning, exact replay, tenant isolation, parent lineage,
         divergence rejection, session propagation, and non-financial results.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_process_service_directory_provisioning_orchestrator.py
COLLABORATION / OWNERSHIP: Certificate for
                            process_service_directory_provisioning_orchestrator.py;
                            P1/P2/L8-0 remain independent canonical authorities
                            and HTTP/IAM admission remains a later gate.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.1-L8-1-PROCESS-SERVICE-DIRECTORY-PROVISIONING-CERT
           narrows union-typed provisioning results to their exact P1 classes
           before class-specific lineage assertions, preserving all runtime
           checks while making the certificate statically exact.
           2026-09-23 v1.0.0-L8-1-PROCESS-SERVICE-DIRECTORY-PROVISIONING-CERT
           established adversarial direct coverage for create/exact replay,
           transaction ownership, tenant scope, missing/corrupt parent lineage,
           durable identity divergence, malformed values, and financial-boundary
           exclusion.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic in-memory identifiers only; no provider,
                             credential, secret, real customer, or payment data.
TENANT BOUNDARY: Tests prove every P2 read/write receives the exact tenant and
                 caller session and that foreign parent scope fails as absence.
AUTHORITY BOUNDARY: Certificate only. No IAM grant, instruction acceptance,
                    document receipt, allocation, attempt, service, return,
                    invoice, payment, execution, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
FAIL-CLOSED DECLARATION: Inactive transaction, invalid value, missing parent,
                         divergent identity/history, and broken office/district
                         lineage must reject without fallback or healing.
"""
from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace
from typing import Any, Callable

import pytest

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    Deputy,
    District,
    SheriffOffice,
)
from tools.eos.legal_operations.orchestration.process_service_directory_provisioning_orchestrator import (
    VERSION as PRODUCTION_VERSION,
    ProcessServiceDirectoryProvisioningDisposition,
    ProcessServiceDirectoryProvisioningError,
    ProcessServiceDirectoryTransactionRequiredError,
    provision_deputy,
    provision_district,
    provision_sheriff_office,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.1-L8-1-PROCESS-SERVICE-DIRECTORY-PROVISIONING-CERT"


class FakeSession:
    """Minimal caller-owned transaction marker for direct composition tests."""

    def __init__(self, in_transaction: bool) -> None:
        self.in_transaction = in_transaction


class FakeCollection:
    """In-memory collection implementing only the governed P2 methods used."""

    def __init__(self) -> None:
        self.docs: list[dict[str, Any]] = []
        self.calls: list[tuple[str, object, dict[str, object]]] = []

    def find(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> list[dict[str, Any]]:
        """Return exact matches while recording session and tenant predicate."""
        self.calls.append(("find", session, deepcopy(query)))
        return [
            deepcopy(document)
            for document in self.docs
            if all(document.get(key) == value for key, value in query.items())
        ]

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> dict[str, Any] | None:
        """Return first exact match while recording P2 caller scope."""
        self.calls.append(("find_one", session, deepcopy(query)))
        for document in self.docs:
            if all(document.get(key) == value for key, value in query.items()):
                return deepcopy(document)
        return None

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: object = None,
    ) -> object:
        """Append one P2 record without adding independent semantics."""
        self.calls.append(("insert_one", session, deepcopy(document)))
        self.docs.append(deepcopy(document))
        return SimpleNamespace(inserted_id=len(self.docs))


def expect_code(
    code: str,
    operation: Callable[[], object],
    *,
    error_type: type[ProcessServiceDirectoryProvisioningError] = (
        ProcessServiceDirectoryProvisioningError
    ),
) -> None:
    """Assert one stable L8-1 failure code."""
    with pytest.raises(error_type) as caught:
        operation()
    assert caught.value.code == code
    assert str(caught.value) == code


def test_district_create_exact_replay_and_session_propagation() -> None:
    """One new District is created once and exact repeat becomes no-write replay."""
    collection = FakeCollection()
    session = FakeSession(True)

    created = provision_district(
        tenant_id="tenant-a",
        district_id="district-1",
        name="Johannesburg Central",
        jurisdiction_code="ZA-GP-JHB",
        evidence_reference="district-source",
        lifecycle_collection=collection,
        session=session,
    )
    replayed = provision_district(
        tenant_id="tenant-a",
        district_id="district-1",
        name="Johannesburg Central",
        jurisdiction_code="ZA-GP-JHB",
        evidence_reference="district-source",
        lifecycle_collection=collection,
        session=session,
    )

    assert created.disposition is ProcessServiceDirectoryProvisioningDisposition.CREATED
    assert replayed.disposition is ProcessServiceDirectoryProvisioningDisposition.REPLAYED
    assert created.value == replayed.value
    assert len(collection.docs) == 1
    assert sum(call[0] == "insert_one" for call in collection.calls) == 1
    assert all(call[1] is session for call in collection.calls)
    assert all(
        query.get("tenant_id") == "tenant-a"
        for _, _, query in collection.calls
        if "tenant_id" in query
    )


def test_full_directory_lineage_provisions_in_dependency_order() -> None:
    """District, office, then deputy produce canonical non-financial P1 facts."""
    collection = FakeCollection()
    session = FakeSession(True)

    district = provision_district(
        tenant_id="tenant-a",
        district_id="district-1",
        name="Johannesburg Central",
        jurisdiction_code="ZA-GP-JHB",
        evidence_reference="district-source",
        lifecycle_collection=collection,
        session=session,
    )
    office = provision_sheriff_office(
        tenant_id="tenant-a",
        sheriff_office_id="office-1",
        district_id="district-1",
        name="Sheriff Johannesburg Central",
        evidence_reference="office-source",
        lifecycle_collection=collection,
        session=session,
    )
    deputy = provision_deputy(
        tenant_id="tenant-a",
        deputy_id="deputy-1",
        sheriff_office_id="office-1",
        display_name="Deputy One",
        badge_reference="badge-1",
        evidence_reference="deputy-source",
        lifecycle_collection=collection,
        session=session,
    )

    assert district.disposition is ProcessServiceDirectoryProvisioningDisposition.CREATED
    assert office.disposition is ProcessServiceDirectoryProvisioningDisposition.CREATED
    assert deputy.disposition is ProcessServiceDirectoryProvisioningDisposition.CREATED

    district_value = district.value
    office_value = office.value
    deputy_value = deputy.value
    assert isinstance(district_value, District)
    assert isinstance(office_value, SheriffOffice)
    assert isinstance(deputy_value, Deputy)
    assert office_value.district_id == district_value.district_id
    assert deputy_value.sheriff_office_id == office_value.sheriff_office_id
    assert {type(value).__name__ for value in (district_value, office_value, deputy_value)} == {
        "District",
        "SheriffOffice",
        "Deputy",
    }
    forbidden = {
        "payment",
        "settlement",
        "paid_state",
        "refund",
        "invoice",
        "billing_execution",
    }
    for result in (district, office, deputy):
        assert not forbidden.intersection(result.to_dict())


def test_missing_and_foreign_parent_scope_fail_before_child_write() -> None:
    """Office/deputy provisioning never invents or cross-resolves a parent."""
    collection = FakeCollection()
    session = FakeSession(True)
    provision_district(
        tenant_id="tenant-a",
        district_id="district-1",
        name="Johannesburg Central",
        jurisdiction_code="ZA-GP-JHB",
        evidence_reference="district-source",
        lifecycle_collection=collection,
        session=session,
    )
    writes_before = sum(call[0] == "insert_one" for call in collection.calls)

    expect_code(
        "L8_1_DISTRICT_NOT_FOUND",
        lambda: provision_sheriff_office(
            tenant_id="tenant-b",
            sheriff_office_id="office-b",
            district_id="district-1",
            name="Foreign Office",
            evidence_reference="office-source",
            lifecycle_collection=collection,
            session=session,
        ),
    )
    expect_code(
        "L8_1_SHERIFF_OFFICE_NOT_FOUND",
        lambda: provision_deputy(
            tenant_id="tenant-a",
            deputy_id="deputy-missing",
            sheriff_office_id="office-missing",
            display_name="Missing Deputy",
            badge_reference="badge-missing",
            evidence_reference="deputy-source",
            lifecycle_collection=collection,
            session=session,
        ),
    )
    assert sum(call[0] == "insert_one" for call in collection.calls) == writes_before


def test_same_identity_different_fact_rejects_without_second_write() -> None:
    """Provisioning cannot create divergent immutable truth for one identity."""
    collection = FakeCollection()
    session = FakeSession(True)
    provision_district(
        tenant_id="tenant-a",
        district_id="district-1",
        name="Johannesburg Central",
        jurisdiction_code="ZA-GP-JHB",
        evidence_reference="district-source",
        lifecycle_collection=collection,
        session=session,
    )
    writes_before = sum(call[0] == "insert_one" for call in collection.calls)

    expect_code(
        "L8_1_DIRECTORY_IDENTITY_DIVERGENCE",
        lambda: provision_district(
            tenant_id="tenant-a",
            district_id="district-1",
            name="Changed District",
            jurisdiction_code="ZA-GP-JHB",
            evidence_reference="different-source",
            lifecycle_collection=collection,
            session=session,
        ),
    )
    assert sum(call[0] == "insert_one" for call in collection.calls) == writes_before
    assert len(collection.docs) == 1


def test_preexisting_divergent_immutable_history_fails_closed() -> None:
    """Legacy/corrupt two-fact history is rejected rather than arbitrarily healed."""
    collection = FakeCollection()
    session = FakeSession(True)
    first = District(
        "tenant-a",
        "district-1",
        "Johannesburg Central",
        "ZA-GP-JHB",
        "district-source-1",
    )
    second = District(
        "tenant-a",
        "district-1",
        "Johannesburg Central Changed",
        "ZA-GP-JHB",
        "district-source-2",
    )
    LegalOperationsLifecycleRegistry.create(first, collection, session=session)
    LegalOperationsLifecycleRegistry.create(second, collection, session=session)
    writes_before = sum(call[0] == "insert_one" for call in collection.calls)

    expect_code(
        "L8_1_DIRECTORY_HISTORY_DIVERGENT",
        lambda: provision_district(
            tenant_id="tenant-a",
            district_id="district-1",
            name="Johannesburg Central",
            jurisdiction_code="ZA-GP-JHB",
            evidence_reference="district-source-1",
            lifecycle_collection=collection,
            session=session,
        ),
    )
    assert sum(call[0] == "insert_one" for call in collection.calls) == writes_before


def test_deputy_rejects_office_whose_canonical_district_is_absent() -> None:
    """A directly seeded orphan office cannot become a trusted deputy parent."""
    collection = FakeCollection()
    session = FakeSession(True)
    orphan = SheriffOffice(
        "tenant-a",
        "office-orphan",
        "district-missing",
        "Orphan Office",
        "legacy-seed",
    )
    LegalOperationsLifecycleRegistry.create(orphan, collection, session=session)
    writes_before = sum(call[0] == "insert_one" for call in collection.calls)

    expect_code(
        "L8_1_OFFICE_DISTRICT_NOT_FOUND",
        lambda: provision_deputy(
            tenant_id="tenant-a",
            deputy_id="deputy-1",
            sheriff_office_id="office-orphan",
            display_name="Deputy One",
            badge_reference="badge-1",
            evidence_reference="deputy-source",
            lifecycle_collection=collection,
            session=session,
        ),
    )
    assert sum(call[0] == "insert_one" for call in collection.calls) == writes_before


def test_active_transaction_is_required_before_any_database_access() -> None:
    """Missing/inactive transaction fails before P2 history or persistence."""
    collection = FakeCollection()

    expect_code(
        "L8_1_ACTIVE_TRANSACTION_REQUIRED",
        lambda: provision_district(
            tenant_id="tenant-a",
            district_id="district-1",
            name="Johannesburg Central",
            jurisdiction_code="ZA-GP-JHB",
            evidence_reference="district-source",
            lifecycle_collection=collection,
            session=None,
        ),
        error_type=ProcessServiceDirectoryTransactionRequiredError,
    )
    expect_code(
        "L8_1_ACTIVE_TRANSACTION_REQUIRED",
        lambda: provision_district(
            tenant_id="tenant-a",
            district_id="district-1",
            name="Johannesburg Central",
            jurisdiction_code="ZA-GP-JHB",
            evidence_reference="district-source",
            lifecycle_collection=collection,
            session=FakeSession(False),
        ),
        error_type=ProcessServiceDirectoryTransactionRequiredError,
    )
    assert collection.calls == []


def test_malformed_p1_input_is_bounded_and_has_no_write() -> None:
    """Pseudo tenant and malformed identity cannot reach persistence."""
    collection = FakeCollection()
    session = FakeSession(True)

    expect_code(
        "L8_1_DIRECTORY_VALUE_INVALID",
        lambda: provision_district(
            tenant_id="global",
            district_id="district-1",
            name="Johannesburg Central",
            jurisdiction_code="ZA-GP-JHB",
            evidence_reference="district-source",
            lifecycle_collection=collection,
            session=session,
        ),
    )
    expect_code(
        "L8_1_DIRECTORY_VALUE_INVALID",
        lambda: provision_district(
            tenant_id="tenant-a",
            district_id="invalid/district",
            name="Johannesburg Central",
            jurisdiction_code="ZA-GP-JHB",
            evidence_reference="district-source",
            lifecycle_collection=collection,
            session=session,
        ),
    )
    assert collection.calls == []


def test_result_and_module_versions_are_frozen_to_l8_1_release() -> None:
    """Certificate remains bound to the intended sovereign production release."""
    assert PRODUCTION_VERSION == "v1.0.1-L8-1-PROCESS-SERVICE-DIRECTORY-PROVISIONING"
    assert VERSION == "v1.0.1-L8-1-PROCESS-SERVICE-DIRECTORY-PROVISIONING-CERT"


# ARTIFACT: test_process_service_directory_provisioning_orchestrator.py
# VERSION: v1.0.1-L8-1-PROCESS-SERVICE-DIRECTORY-PROVISIONING-CERT
# AUTHORITY BOUNDARY: direct L8-1 directory provisioning certificate only
# TENANT POSTURE: exact synthetic tenant and caller-session propagation
# FAIL-CLOSED POSTURE: invalid transaction/value/parent/history/divergence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT