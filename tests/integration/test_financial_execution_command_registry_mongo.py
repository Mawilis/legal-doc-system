"""Real-Mongo certificate for durable family-aware financial execution commands.

TITLE: Financial Execution Command Registry Mongo Certification
VERSION: v2.1.0-M11-P5-R2A-RM
AUTHORITY: Certification evidence only; no execution, settlement, or AP bridge.
EPITOME: Define the production-backed contract for strict family-aware command rows.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_financial_execution_command_registry_mongo.py
COLLABORATION / OWNERSHIP: Kennel EOS registry certification.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v2.1.0-M11-P5-R2A-RM activates the dedicated-replica-set certificate and replaces unconditional skips with durable family-aware registry assertions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every fixture and registry call is tenant-scoped.
FINANCIAL TRUTH BOUNDARY: Durable command evidence is not provider execution or settlement truth.
TRANSACTION BOUNDARY: Caller-owned Mongo sessions and whole-transaction retries remain the integration contract.
MONGO CERTIFICATION: Requires the dedicated replica set and must be run explicitly by an operator.
"""
from datetime import datetime, timezone
from typing import Any

import os
import uuid

import pytest
from pymongo import MongoClient

from tools.eos.kennel.domain.financial_execution_command import AccountsPayableCommandSource, FinancialExecutionCommand, PlatformBillingCommandSource

from tools.eos.kennel.registry.financial_execution_command_registry import (
    FinancialExecutionCommandPersistedRecordInvalidError,
    FinancialExecutionCommandRegistry,
)

COLLECTION = "kennel_financial_execution_commands"
NOW = datetime(2026, 9, 7, 10, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128


def ap_source(**changes: Any) -> AccountsPayableCommandSource:
    values = {"execution_request_id": "ap-request", "execution_request_fingerprint": FP_A, "selection_decision_id": "selection-1", "selection_decision_fingerprint": FP_B, "payable_id": "payable-1", "release_authorization_id": "release-1", "authorized_provider_name": "PAYSHAP"}
    values.update(changes)
    return AccountsPayableCommandSource(**values)


def platform_source(**changes: Any) -> PlatformBillingCommandSource:
    values = {"execution_request_id": "platform-request", "execution_request_fingerprint": FP_A, "routing_decision_id": "routing-1", "routing_decision_fingerprint": FP_B, "platform_invoice_id": "platform-invoice-1", "release_authorization_id": "platform-release-1", "release_authorization_fingerprint": FP_C, "authorized_provider_name": "STRIPE"}
    values.update(changes)
    return PlatformBillingCommandSource(**values)


def command(**changes: Any) -> FinancialExecutionCommand:
    source = changes.pop("source_authority", ap_source())
    values = {"tenant_id": "tenant-1", "execution_command_id": "command-1", "idempotency_key": "idem-1", "amount_minor": 1000, "currency": "ZAR", "payment_destination_reference": "destination-ref", "source_authority": source, "provider_name": source.authorized_provider_name, "created_at": NOW, "provider_metadata_reference": "metadata-ref"}
    values.update(changes)
    return FinancialExecutionCommand(**values)


@pytest.fixture()
def mongo_db() -> Any:
    """Provide one isolated database on the authorized local replica set."""
    uri = os.getenv("TEST_VENDOR_MONGO_URI")
    if not uri:
        pytest.fail("TEST_VENDOR_MONGO_URI is required for real-Mongo certification")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, retryWrites=True)
    database = client["command_registry_cert_" + uuid.uuid4().hex]
    try:
        hello = client.admin.command("hello")
        if hello.get("isWritablePrimary") is not True or hello.get("setName") != "wilsyVendorCertRS":
            pytest.fail("dedicated writable replica-set authority is required")
        FinancialExecutionCommandRegistry.ensure_indexes(database[COLLECTION])
        yield database
    finally:
        client.drop_database(database.name)
        client.close()


def test_ap_command_row_contract(mongo_db: Any) -> None:
    collection = mongo_db[COLLECTION]
    item = command()
    with mongo_db.client.start_session() as session:
        with session.start_transaction():
            assert FinancialExecutionCommandRegistry.create(item, collection, session=session).outcome == "CREATED"
            assert FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, collection, session=session) == item
    assert FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, collection).to_persisted()["source_authority_kind"] == "ACCOUNTS_PAYABLE"


def test_platform_command_row_contract(mongo_db: Any) -> None:
    collection = mongo_db[COLLECTION]
    item = command(source_authority=platform_source(), provider_name="STRIPE")
    assert FinancialExecutionCommandRegistry.create(item, collection).outcome == "CREATED"
    loaded = FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, collection)
    assert loaded == item
    assert loaded.to_persisted()["source_authority_kind"] == "PLATFORM_BILLING"


def test_nested_ap_subject_contract(mongo_db: Any) -> None:
    collection = mongo_db[COLLECTION]
    item = command()
    FinancialExecutionCommandRegistry.create(item, collection)
    row = collection.find_one({"tenant_id": item.tenant_id, "execution_command_id": item.execution_command_id})
    assert row is not None
    assert row["source_authority"]["payable_id"] == "payable-1"
    assert row["source_authority"]["release_authorization_id"] == "release-1"


def test_corruption_contract(mongo_db: Any) -> None:
    collection = mongo_db[COLLECTION]
    item = command()
    FinancialExecutionCommandRegistry.create(item, collection)
    collection.update_one({"tenant_id": item.tenant_id, "execution_command_id": item.execution_command_id}, {"$set": {"command_fingerprint": "f" * 128}})
    with pytest.raises(FinancialExecutionCommandPersistedRecordInvalidError):
        FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, collection)


# ARTIFACT: test_financial_execution_command_registry_mongo.py
# VERSION: v2.1.0-M11-P5-R2A-RM
# AUTHORITY BOUNDARY: real-Mongo certificate only; no execution or settlement authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
