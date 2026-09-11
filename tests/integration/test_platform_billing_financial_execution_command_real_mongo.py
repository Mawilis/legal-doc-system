"""TITLE: Kennel Platform Billing Command Runtime Certificate
VERSION: v1.0.1-KENNEL-PLATFORM-BILLING-FINANCIAL-EXECUTION-COMMAND-REAL-MONGO
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify durable R3D hydration into the Kennel platform command.
EPITOME: Host evidence only; provider execution is out of scope.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_platform_billing_financial_execution_command_real_mongo.py
COLLABORATION / OWNERSHIP: Kennel EOS platform command certificate.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.1 replaces source assertions with production-path Mongo scenarios.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: TEST_VENDOR_MONGO_URI only; bounded UUID data.
TENANT BOUNDARY: Every durable read is tenant-scoped.
AUTHORITY BOUNDARY: R3D-derived command evidence only.
FINANCIAL AUTHORITY BOUNDARY: No provider, settlement, paid, or refund mutation.
TRANSACTION BOUNDARY: R3D persists; R3E command issuance is pure.
FAIL-CLOSED POSTURE: Missing governed Mongo is an environment blocker.
"""
from datetime import datetime, timezone
import os, uuid
from pymongo import MongoClient
import pytest
from tools.eos.saas.billing.platform_billing_release_authorization_registry import PlatformBillingReleaseAuthorizationRegistry
from tools.eos.saas.billing.platform_billing_financial_execution_request_issuance import issue_platform_billing_financial_execution_request
from tools.eos.kennel.orchestration.platform_billing_financial_execution_command_issuance import issue_platform_billing_financial_execution_command
from tools.eos.saas.domain.platform_billing_release_authorization import PlatformBillingReleaseAuthorization

URI=os.getenv("TEST_VENDOR_MONGO_URI", "")
def _setup():
    if not URI: raise RuntimeError("TEST_VENDOR_MONGO_URI is required")
    client=MongoClient(URI,serverSelectionTimeoutMS=2000); db=client[f"r3e_{uuid.uuid4().hex}"]; auth=PlatformBillingReleaseAuthorization("t","r","i","a"*128,"e","b"*128,100,"ZAR","p","basis","dest","k",datetime.now(timezone.utc),datetime.now(timezone.utc)); col=db["platform_billing_release_authorizations"]; PlatformBillingReleaseAuthorizationRegistry.ensure_indexes(col); col.insert_one(auth.to_persistence_dict()); issue_platform_billing_financial_execution_request(client,db,"t","r",execution_request_id="x",requested_at=datetime.now(timezone.utc)); return client,db,auth
def _close(client,db,auth):
    db["platform_billing_financial_execution_requests"].delete_one({"tenant_id":"t","execution_request_id":"x"}); db["platform_billing_release_authorizations"].delete_one({"tenant_id":"t","release_authorization_id":auth.release_authorization_id}); client.close()
def test_r3e_rm01_durable_r3d_to_command():
    client,db,auth=_setup()
    try:
        command=issue_platform_billing_financial_execution_command("t","x",collection=db["platform_billing_financial_execution_requests"],issued_at=datetime.now(timezone.utc)); assert command.tenant_id==auth.tenant_id and command.amount_minor==100 and command.platform_invoice_id==auth.platform_invoice_id
    finally: _close(client,db,auth)
def test_r3e_rm02_wrong_tenant_fails_closed():
    client,db,auth=_setup()
    try:
        with pytest.raises(Exception): issue_platform_billing_financial_execution_command("other","x",collection=db["platform_billing_financial_execution_requests"],issued_at=datetime.now(timezone.utc))
    finally: _close(client,db,auth)
def test_r3e_rm03_durable_derivation():
    client,db,auth=_setup()
    try:
        command=issue_platform_billing_financial_execution_command("t","x",collection=db["platform_billing_financial_execution_requests"],issued_at=datetime.now(timezone.utc)); assert command.release_authorization_fingerprint==auth.release_authorization_fingerprint and command.currency==auth.currency and command.payment_destination_reference==auth.payment_destination_reference
    finally: _close(client,db,auth)
def test_r3e_rm04_deterministic_replay():
    client,db,auth=_setup(); stamp=datetime.now(timezone.utc)
    try:
        first=issue_platform_billing_financial_execution_command("t","x",collection=db["platform_billing_financial_execution_requests"],issued_at=stamp); second=issue_platform_billing_financial_execution_command("t","x",collection=db["platform_billing_financial_execution_requests"],issued_at=stamp); assert first==second
    finally: _close(client,db,auth)
# ARTIFACT: test_platform_billing_financial_execution_command_real_mongo.py
# VERSION: v1.0.1-KENNEL-PLATFORM-BILLING-FINANCIAL-EXECUTION-COMMAND-REAL-MONGO
# AUTHORITY BOUNDARY: evidence only; no execution.
# END OF WILSY OS SOVEREIGN ARTIFACT
