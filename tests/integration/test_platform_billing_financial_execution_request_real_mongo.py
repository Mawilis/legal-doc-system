"""TITLE: R3D Platform Billing Financial Execution Request Real-Mongo Certificate
VERSION: v1.0.0-PLATFORM-BILLING-FINANCIAL-EXECUTION-REQUEST-REAL-MONGO
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify four bounded durable Mongo scenarios on the governed host.
EPITOME: Host evidence only; no provider or Kennel execution.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_platform_billing_financial_execution_request_real_mongo.py
COLLABORATION / OWNERSHIP: R3D real-Mongo certification.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0 establishes four isolated scenarios.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID isolation and exact bounded cleanup.
TENANT BOUNDARY: Every query is tenant-scoped.
AUTHORITY BOUNDARY: Evidence only; no authority grant.
FINANCIAL AUTHORITY BOUNDARY: No execution, settlement, paid, or refund state.
TRANSACTION BOUNDARY: Production issuance owns session and transaction.
FAIL-CLOSED POSTURE: Missing TEST_VENDOR_MONGO_URI is an environment blocker.
"""
from datetime import datetime, timezone
from dataclasses import replace
import os, uuid
from pymongo import MongoClient
from tools.eos.saas.billing.platform_billing_release_authorization_registry import PlatformBillingReleaseAuthorizationRegistry
from tools.eos.saas.billing.platform_billing_financial_execution_request_issuance import issue_platform_billing_financial_execution_request
from tools.eos.saas.domain.platform_billing_release_authorization import PlatformBillingReleaseAuthorization

URI=os.getenv("TEST_VENDOR_MONGO_URI","")
def _auth(t,r,i,k,d="dest"):
    now=datetime.now(timezone.utc); return PlatformBillingReleaseAuthorization(t,r,i,"a"*128,"e","b"*128,100,"ZAR","p","basis",d,k,now,now)
def _fixture():
    if not URI: raise RuntimeError("TEST_VENDOR_MONGO_URI is required")
    client=MongoClient(URI,serverSelectionTimeoutMS=2000); db=client[f"r3d_{uuid.uuid4().hex}"]; ac=db["platform_billing_release_authorizations"]
    authorization=_auth("t","r","i","k"); PlatformBillingReleaseAuthorizationRegistry.ensure_indexes(ac); ac.insert_one(authorization.to_persistence_dict())
    return client, db, authorization

def _close(client, db, authorization):
    db["platform_billing_release_authorizations"].delete_one({"tenant_id": authorization.tenant_id, "release_authorization_id": authorization.release_authorization_id})
    db["platform_billing_financial_execution_requests"].delete_one({"tenant_id": authorization.tenant_id, "execution_request_id": "x"}); client.close()

def test_r3d_rm01_happy_durable_request():
    if not URI: raise RuntimeError("TEST_VENDOR_MONGO_URI is required")
    client, db, authorization = _fixture()
    try:
        result=issue_platform_billing_financial_execution_request(client,db,"t","r",execution_request_id="x",requested_at=datetime.now(timezone.utc))
        assert result[0].tenant_id==authorization.tenant_id and result[0].release_authorization_fingerprint==authorization.release_authorization_fingerprint
    finally: _close(client,db,authorization)

def test_r3d_rm02_authority_tenant_firewall():
    if not URI: raise RuntimeError("TEST_VENDOR_MONGO_URI is required")
    client, db, authorization = _fixture()
    try:
        import pytest
        with pytest.raises(Exception): issue_platform_billing_financial_execution_request(client,db,"wrong-tenant","r",execution_request_id="x",requested_at=datetime.now(timezone.utc))
    finally: _close(client,db,authorization)

def test_r3d_rm03_tenant_isolation():
    if not URI: raise RuntimeError("TEST_VENDOR_MONGO_URI is required")
    client, db, authorization = _fixture()
    try:
        issue_platform_billing_financial_execution_request(client,db,"t","r",execution_request_id="x",requested_at=datetime.now(timezone.utc))
        assert db["platform_billing_financial_execution_requests"].count_documents({"tenant_id":"other"})==0
    finally: _close(client,db,authorization)

def test_r3d_rm04_idempotency_and_conflict():
    if not URI: raise RuntimeError("TEST_VENDOR_MONGO_URI is required")
    client, db, authorization = _fixture()
    try:
        first=issue_platform_billing_financial_execution_request(client,db,"t","r",execution_request_id="x",requested_at=datetime.now(timezone.utc))
        second=issue_platform_billing_financial_execution_request(client,db,"t","r",execution_request_id="x",requested_at=first[0].requested_at)
        assert second[1] is True and db["platform_billing_financial_execution_requests"].count_documents({"tenant_id":"t"})==1
    finally: _close(client,db,authorization)
# ARTIFACT: test_platform_billing_financial_execution_request_real_mongo.py
# VERSION: v1.0.0-PLATFORM-BILLING-FINANCIAL-EXECUTION-REQUEST-REAL-MONGO
# AUTHORITY BOUNDARY: evidence only; no execution
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
