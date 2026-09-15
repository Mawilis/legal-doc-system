"""Host-backed P6D ordinary Mongo certificate.

TITLE: Wilsy OS Process-Service Client Billing Authority Real-Mongo Certificate
VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-BILLING-AUTHORITY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
TENANT BOUNDARY: Every profile/binding read and write is tenant-scoped.
TRANSACTION BOUNDARY: The certificate owns cleanup only; registry owns none.
FINANCIAL AUTHORITY: Kennel EOS exclusively owns execution and settlement.
FAIL-CLOSED: Runtime availability may skip; product/index/corruption failures fail.
CERTIFICATION / UPDATE DATE: 2026-09-15
"""
from datetime import datetime, timezone
from dataclasses import replace
import os
from uuid import uuid4

import pytest
from typing import Any
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.billing.process_service_client_billing_authority import (
    ClientBillingProfileVersion,
    CollectionMethod,
    CollectionMethodPolicy,
    DueDatePolicy,
    DueDateRule,
    InstructionBillingBinding,
    PaymentTerms,
    PaymentTermsRule,
    TaxCalculationScope,
    TaxPolicy,
    TaxRoundingRule,
    TaxTreatment,
)
from tools.eos.saas.billing.process_service_client_billing_registry import ProcessServiceClientBillingRegistry, ProcessServiceClientBillingRegistryError

URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 15, 10, 0, tzinfo=timezone.utc)


@pytest.fixture()
def mongo() -> Any:
    try:
        client = MongoClient(URI, serverSelectionTimeoutMS=2000)
        hello = client.admin.command("hello")
    except Exception as error:
        pytest.skip(f"Mongo hello unavailable: {error}")
    if hello.get("setName") != REPLICA_SET:
        client.close(); pytest.skip("wrong replica set")
    if not hello.get("isWritablePrimary", hello.get("ismaster", False)):
        client.close(); pytest.skip("no writable primary")
    database = client.get_database(f"p6d_{uuid4().hex}", read_concern=ReadConcern("majority"), write_concern=WriteConcern("majority", j=True))
    try:
        yield client, database
    finally:
        try: client.drop_database(database.name)
        finally: client.close()


def _profile() -> ClientBillingProfileVersion:
    return ClientBillingProfileVersion("tenant-a", "profile-1", "profile-v1", "customer-1", "Example Customer", None, "billing@example.test", None, "ZA-GP", "ZA-GP", TaxPolicy("tax", "tax-v1", TaxTreatment.EXEMPT, None, TaxCalculationScope.LINE, TaxRoundingRule.HALF_UP_MINOR_UNIT, False), PaymentTerms("terms", "terms-v1", PaymentTermsRule.DAYS_AFTER_ISSUE, 14), DueDatePolicy("due", "due-v1", DueDateRule.ISSUE_DATE_PLUS_PAYMENT_TERMS), CollectionMethodPolicy("collection", "collection-v1", CollectionMethod.SEND_INVOICE), BASE, None, "profile-evidence")


def _binding() -> InstructionBillingBinding:
    return InstructionBillingBinding("tenant-a", "binding-1", "instruction-1", "profile-1", "profile-v1", BASE, "binding-evidence")


def test_profile_binding_roundtrip_replay_corruption_and_tenant_isolation(mongo: tuple[Any, Any]) -> None:
    _, database = mongo
    profiles = database.get_collection("profiles"); bindings = database.get_collection("bindings")
    ProcessServiceClientBillingRegistry.ensure_indexes(profiles, bindings)
    profile = _profile(); binding = _binding()
    first = ProcessServiceClientBillingRegistry.create_profile(profile, profiles)
    assert ProcessServiceClientBillingRegistry.create_profile(profile, profiles).to_dict() == first.to_dict()
    with pytest.raises(ProcessServiceClientBillingRegistryError, match="P6D_REPLAY_CONFLICT"):
        ProcessServiceClientBillingRegistry.create_profile(replace(profile, customer_id="customer-divergent"), profiles)
    assert ProcessServiceClientBillingRegistry.create_binding(binding, bindings).to_dict() == binding.to_dict()
    evidence_identity = profiles.find_one({"tenant_id": "tenant-a"})["evidence_identity"]
    assert isinstance(evidence_identity, str)
    assert ProcessServiceClientBillingRegistry.get_profile("tenant-a", evidence_identity, profiles).to_dict() == profile.to_dict()
    with pytest.raises(ProcessServiceClientBillingRegistryError, match="P6D_NOT_FOUND"):
        ProcessServiceClientBillingRegistry.get_profile("tenant-b", profile.fingerprint, profiles)
    raw = profiles.find_one({"tenant_id": "tenant-a", "evidence_identity": evidence_identity})
    assert raw is not None
    profiles.update_one({"_id": raw["_id"]}, {"$set": {"fingerprint": "0" * 128}})
    with pytest.raises(ProcessServiceClientBillingRegistryError, match="P6D_RECORD_FINGERPRINT_INVALID"):
        ProcessServiceClientBillingRegistry.get_profile("tenant-a", evidence_identity, profiles)
