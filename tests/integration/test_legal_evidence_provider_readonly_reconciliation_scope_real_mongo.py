"""Real-Mongo certification for server-owned reconciliation tenant scope.

VERSION: v1.0.0-L10A2R-C4D7-RECONCILIATION-SCOPE-REAL-MONGO-CERT
AUTHORITY: TenantRegistry currentness and caller-owned transaction only.
AUTHORITY BOUNDARY: No provider I/O, IAM grant, route, or deletion authority.
"""

from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from contextlib import contextmanager
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceProviderDiscoveryScope,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_authorization_gate import (
    ServerConfiguredReconciliationScopeResolver,
    ServerOwnedReconciliationScopeResolutionError,
    build_server_configured_reconciliation_target,
)

URI_ENV = "TEST_VENDOR_MONGO_URI"
DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"


def _tenant_doc(tenant_id: str, *, status: str = "ACTIVE") -> dict[str, Any]:
    return {
        "tenant_id": tenant_id,
        "name": "Reconciliation Scope Certification",
        "organization": {
            "organization_name": "Reconciliation Scope Certification",
            "industry": "General",
            "plan": "ENTERPRISE",
            "legal_name": None,
            "tax_id": None,
            "contact_email": None,
            "regions": ["Africa"],
            "created_at": "2026-10-25T00:00:00+00:00",
        },
        "industry": "General",
        "plan": "ENTERPRISE",
        "regions": ["Africa"],
        "status": status,
        "created_at": "2026-10-25T00:00:00+00:00",
        "alias": tenant_id,
        "region": "ZA",
        "compliance_flags": {"certification": True},
        "verified": False,
    }


@contextmanager
def _mongo_state() -> Iterator[tuple[Any, Any, str]]:
    uri = os.environ.get(URI_ENV, DEFAULT_URI)
    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
        retryWrites=True,
    )
    database_name = "le_recon_scope_" + uuid4().hex
    database = client[database_name]
    collection = database["tenants"]
    try:
        client.admin.command("ping")
        hello = client.admin.command("hello")
        assert hello.get("setName") == "wilsyVendorCertRS"
        assert hello.get("isWritablePrimary") is True
        yield client, database, database_name
    finally:
        client.drop_database(database_name)
        assert database_name not in client.list_database_names()
        client.close()


def test_configured_scope_reads_uncommitted_tenant_through_same_session() -> None:
    """Scope is derived from deployment config and canonical registry in one transaction."""
    with _mongo_state() as (client, database, _):
        tenant_id = "tenant-reconcile-" + uuid4().hex
        target = build_server_configured_reconciliation_target(
            mongo_database=database,
            env={
                "WILSY_LEGAL_EVIDENCE_RECONCILIATION_TENANT_ID": tenant_id,
                "WILSY_LEGAL_EVIDENCE_S3_BUCKET": "wilsy-legal-evidence-test",
                "WILSY_LEGAL_EVIDENCE_S3_REGION": "af-south-1",
            },
        )
        session = client.start_session()
        try:
            session.start_transaction()
            database["tenants"].insert_one(
                _tenant_doc(tenant_id),
                session=session,
            )
            scope = target.scope_resolver.resolve_scope(
                principal_id="platform-operator-a",
                activation_id="platform-activation-a",
                at=datetime(2026, 10, 25, 7, 0, tzinfo=timezone.utc),
                session=session,
            )
            assert scope == LegalEvidenceProviderDiscoveryScope(
                tenant_id=tenant_id,
                tenant_scope_fingerprint=hashlib.sha3_512(
                    tenant_id.encode("utf-8")
                ).hexdigest(),
            )
            assert session.in_transaction is True
            session.abort_transaction()
        finally:
            if session.in_transaction:
                session.abort_transaction()
            session.end_session()

        assert database["tenants"].find_one({"tenant_id": tenant_id}) is None


def test_configured_scope_denies_inactive_persisted_tenant() -> None:
    with _mongo_state() as (client, database, _):
        tenant_id = "tenant-reconcile-inactive-" + uuid4().hex
        database["tenants"].insert_one(_tenant_doc(tenant_id, status="ARCHIVED"))
        resolver = ServerConfiguredReconciliationScopeResolver(
            tenant_id=tenant_id,
            provider_name="aws_s3",
            tenant_collection=database["tenants"],
        )
        with client.start_session() as session:
            session.start_transaction()
            with pytest.raises(
                ServerOwnedReconciliationScopeResolutionError,
                match="CANONICAL_TENANT_SCOPE_NOT_ACTIVE",
            ):
                resolver.resolve_scope(
                    principal_id="platform-operator-a",
                    activation_id="platform-activation-a",
                    at=datetime(2026, 10, 25, 7, 0, tzinfo=timezone.utc),
                    session=session,
                )
            session.abort_transaction()


def test_configured_scope_does_not_fall_back_to_another_tenant() -> None:
    with _mongo_state() as (client, database, _):
        present_tenant = "tenant-reconcile-present-" + uuid4().hex
        configured_tenant = "tenant-reconcile-configured-" + uuid4().hex
        database["tenants"].insert_one(_tenant_doc(present_tenant))
        resolver = ServerConfiguredReconciliationScopeResolver(
            tenant_id=configured_tenant,
            provider_name="aws_s3",
            tenant_collection=database["tenants"],
        )
        with client.start_session() as session:
            session.start_transaction()
            with pytest.raises(
                ServerOwnedReconciliationScopeResolutionError,
                match="CANONICAL_TENANT_SCOPE_NOT_ACTIVE",
            ):
                resolver.resolve_scope(
                    principal_id="platform-operator-a",
                    activation_id="platform-activation-a",
                    at=datetime(2026, 10, 25, 7, 0, tzinfo=timezone.utc),
                    session=session,
                )
            session.abort_transaction()
