"""Isolated real-Mongo certificate for blocked tenant-owner genesis.

TITLE: Tenant-owner bootstrap real-Mongo ownership-evidence block certificate
VERSION: v1.3.0-ISSUE-300-OWNERSHIP-EVIDENCE-BLOCK-RM-CERT
AUTHORITY: Verify that unavailable independent ownership evidence cannot create
           tenant-local owner authority.
EPITOME: Use an explicitly configured disposable replica set and assert zero
         tenant, membership, authorization-role and business-role writes.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_owner_bootstrap_real_mongo.py
COLLABORATION / OWNERSHIP: Certificate for tools/eos/auth/tenant_owner_bootstrap.py
                            v1.0.3-ISSUE-300-OWNERSHIP-EVIDENCE-BLOCK.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG: 2026-11-02 v1.3.0-ISSUE-300-OWNERSHIP-EVIDENCE-BLOCK-RM-CERT observes PyMongo session creation during the blocked command, proves no transaction begins, exercises the real pretenant allowlist and adversarial caller claims, and preserves explicit loopback Mongo isolation and zero tenant-local writes.
CHANGELOG: 2026-11-02 v1.2.0-ISSUE-300-OWNERSHIP-EVIDENCE-BLOCK-RM-CERT requires an explicit isolated Mongo URI, rejects port 27027, and certifies zero owner-genesis records when the independent verifier is unavailable.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenant and principal only.
TENANT BOUNDARY: All reads and assertions use one unique synthetic tenant id.
AUTHORITY BOUNDARY: Integration evidence only; no ownership authority.
FINANCIAL AUTHORITY BOUNDARY: No financial or Kennel execution authority.
"""
from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from typing import Any
from urllib.parse import urlparse

import pytest
from pymongo import MongoClient

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_owner_bootstrap import (
    TenantOwnerBootstrapDenialCode,
    TenantOwnerBootstrapError,
    bootstrap_tenant_owner,
)
from tools.eos.saas.domain.tenant import (
    OrganizationProfile,
    SubscriptionPlan,
    TenantEntity,
)


VERSION = "v1.3.0-ISSUE-300-OWNERSHIP-EVIDENCE-BLOCK-RM-CERT"
MONGO_URI_ENV = "WILSY_ISSUE_300_REAL_MONGO_URI"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"


@pytest.fixture
def isolated_mongo() -> Iterator[tuple[MongoClient, str, str]]:
    """Require the explicit disposable loopback Mongo replica set and primary."""
    mongo_uri = os.environ.get(MONGO_URI_ENV)
    if not mongo_uri:
        pytest.fail(f"{MONGO_URI_ENV}_REQUIRED_FOR_REAL_MONGO_CERTIFICATE")
    parsed = urlparse(mongo_uri)
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        pytest.fail("ISSUE_300_LOOPBACK_MONGO_REQUIRED")
    if parsed.port is None:
        pytest.fail("ISSUE_300_EXPLICIT_MONGO_PORT_REQUIRED")
    if parsed.port == 27027:
        pytest.fail("ISSUE_300_PRODUCTION_MONGO_PORT_FORBIDDEN")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail("ISSUE_300_APPROVED_DISPOSABLE_REPLICA_SET_REQUIRED")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("ISSUE_300_MONGO_WRITABLE_PRIMARY_REQUIRED")
        principal_id = f"issue-300-principal-{uuid.uuid4().hex}"
        tenant_id = f"issue-300-tenant-{uuid.uuid4().hex}"
        yield client, principal_id, tenant_id
    finally:
        client.close()


def test_missing_independent_owner_proof_creates_no_tenant_authority(
    isolated_mongo: tuple[MongoClient, str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Provisioner allowlisting and caller claims cannot issue owner authority."""
    client, principal_id, tenant_id = isolated_mongo
    monkeypatch.setenv(
        "WILSY_PRETENANT_TENANT_PROVISIONER_PRINCIPAL_IDS",
        f'["{principal_id}"]',
    )
    identity = SovereignIdentity(
        identity_id=principal_id,
        tenant_id=tenant_id,
        username="synthetic@example.invalid",
        email="synthetic@example.invalid",
        roles=["tenant_owner", "ENTERPRISE_ADMIN"],
        permissions=["*", "tenant:*"],
        auth_method="certificate",
        status=PrincipalStatus.ACTIVE,
    )
    tenant = TenantEntity(
        organization=OrganizationProfile(
            "Synthetic Organization",
            "legal",
            SubscriptionPlan.ENTERPRISE,
            "Synthetic Organization Ltd",
            "REG-ISSUE-300",
            "synthetic@example.invalid",
            ["ZA"],
        ),
        tenant_id=tenant_id,
        verified=True,
    )
    database = client[f"issue_300_owner_block_{uuid.uuid4().hex}"]

    session_starts: list[str] = []
    original_start_session = MongoClient.start_session

    def observe_session_start(
        mongo_client: MongoClient,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        session_starts.append("start_session")
        return original_start_session(mongo_client, *args, **kwargs)

    monkeypatch.setattr(MongoClient, "start_session", observe_session_start)

    with pytest.raises(TenantOwnerBootstrapError) as raised:
        bootstrap_tenant_owner(identity=identity, tenant=tenant)

    assert raised.value.code is (
        TenantOwnerBootstrapDenialCode.OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE
    )
    assert session_starts == []
    for collection_name, selector in (
        ("tenants", {"tenant_id": tenant_id}),
        ("tenant_memberships", {"tenant_id": tenant_id}),
        ("role_assignments", {"tenant_id": tenant_id}),
        ("tenant_business_roles", {"tenant_id": tenant_id}),
    ):
        assert database[collection_name].count_documents(selector) == 0


# ARTIFACT: test_tenant_owner_bootstrap_real_mongo.py
# VERSION: v1.3.0-ISSUE-300-OWNERSHIP-EVIDENCE-BLOCK-RM-CERT
# AUTHORITY BOUNDARY: real-Mongo evidence only; no ownership grant
# TENANT POSTURE: unique synthetic tenant; approved wilsyVendorCertRS loopback set only; production port 27027 rejected
# FAIL-CLOSED POSTURE: deployment authority plus privileged caller claims still deny before any Mongo session/transaction
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
