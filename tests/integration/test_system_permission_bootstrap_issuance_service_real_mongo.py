"""TITLE: D11-R6 bootstrap issuance service real-Mongo vertical certificate.
VERSION: v1.0.0-P4-R4-D11-R6-ISSUANCE-REAL-MONGO
AUTHORITY: Wilsy OS Sovereign IAM certification against a writable replica set.
EPITOME: Proves signed creation, current creator read, and append-only bootstrap persistence in one caller transaction.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_system_permission_bootstrap_issuance_service_real_mongo.py
CERTIFICATION DATE: 2026-10-14
CHANGELOG: v1.0.0 establishes the frozen D11-D6 real-Mongo matrix.
COMPLIANCE: UUID isolation; canonical wilsy database is read-only; no tenant or personal data.
AUTHORITY BOUNDARY: No SYSTEM assignment, activation, break-glass, deletion, TTL, or finance.
"""
from __future__ import annotations

import base64
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import os
from typing import Any
from uuid import uuid4

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pymongo import MongoClient

from tools.eos.auth.system_permission_bootstrap_authority_registry import (
    SystemPermissionBootstrapAuthorityConflictError,
    SystemPermissionBootstrapAuthorityRegistry,
)
from tools.eos.auth.system_permission_bootstrap_creation_authorization import (
    SystemPermissionBootstrapCreationAuthorization,
    SystemPermissionBootstrapCreationAuthorizationError,
)
from tools.eos.auth.system_permission_bootstrap_creation_trust import (
    OPERATION,
    SCOPE,
    SystemPermissionBootstrapCreationTrustedKey,
    SystemPermissionBootstrapCreationTrustRoot,
    SystemPermissionBootstrapCreationTrustStatus,
)
from tools.eos.auth.system_permission_bootstrap_issuance_service import (
    SystemPermissionBootstrapIssuanceError,
    SystemPermissionBootstrapIssuanceService,
)

URI = os.environ.get("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)
ASSIGN_PURPOSE = "SEED_SYSTEM_PERMISSION_ASSIGNMENT_COMMAND_AUTHORITY"
REVOKE_PURPOSE = "SEED_SYSTEM_PERMISSION_REVOCATION_COMMAND_AUTHORITY"
PRINCIPALS = "principal_authorities"
BOOTSTRAPS = "system_permission_bootstrap_authorities"


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


@pytest.fixture()
def context() -> Any:
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
        retryWrites=True,
    )
    hello = client.admin.command("hello")
    assert hello.get("setName") == EXPECTED_REPLICA_SET
    assert hello.get("isWritablePrimary") is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    canonical_before = tuple(sorted(client["wilsy"].list_collection_names()))
    database_name = "wilsy_p4_r4_d11_r6_" + uuid4().hex[:20]
    assert database_name != "wilsy"
    database = client[database_name]
    principals = database[PRINCIPALS]
    bootstraps = database[BOOTSTRAPS]
    registry = SystemPermissionBootstrapAuthorityRegistry(bootstraps)
    registry.ensure_indexes()
    private = Ed25519PrivateKey.generate()
    public = _b64(private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw))
    trusted_key = SystemPermissionBootstrapCreationTrustedKey.create(
        creator_principal_id="principal-creator",
        public_key_base64url=public,
        valid_from=NOW - timedelta(hours=1),
        valid_until=NOW + timedelta(hours=1),
        status=SystemPermissionBootstrapCreationTrustStatus.ACTIVE,
        revision=1,
        provenance="installation-ceremony:real-mongo-evidence",
    )
    service = SystemPermissionBootstrapIssuanceService(
        principal_collection=principals,
        bootstrap_registry=registry,
        trust_root=SystemPermissionBootstrapCreationTrustRoot((trusted_key,)),
    )
    try:
        yield {
            "client": client,
            "database": database,
            "database_name": database_name,
            "principals": principals,
            "bootstraps": bootstraps,
            "registry": registry,
            "service": service,
            "private": private,
            "trusted_key": trusted_key,
            "canonical_before": canonical_before,
        }
        assert tuple(sorted(client["wilsy"].list_collection_names())) == canonical_before
    finally:
        client.drop_database(database_name)
        assert database_name not in client.list_database_names()
        client.close()


def _authorization(
    context: Any,
    *,
    purpose: str = ASSIGN_PURPOSE,
    bootstrap_id: str = "bootstrap-1",
    evidence: str = "evidence:create-1",
    idempotency_key: str = "idem-1",
) -> SystemPermissionBootstrapCreationAuthorization:
    key = context["trusted_key"]
    unsigned = SystemPermissionBootstrapCreationAuthorization(
        operation=OPERATION,
        scope=SCOPE,
        creator_principal_id="principal-creator",
        target_principal_id="principal-target",
        bootstrap_id=bootstrap_id,
        bootstrap_purpose=purpose,
        evidence_reference=evidence,
        key_id=key.key_id,
        trust_fingerprint=key.trust_fingerprint,
        issued_at=NOW - timedelta(minutes=1),
        expires_at=NOW + timedelta(minutes=10),
        nonce="nonce:" + bootstrap_id,
        idempotency_key=idempotency_key,
        signature_base64url=_b64(bytes(64)),
    )
    return replace(unsigned, signature_base64url=_b64(context["private"].sign(unsigned.signed_payload())))


def _seed_principal(context: Any, status: str, *, session: Any = None) -> None:
    context["principals"].insert_one(
        {"principal_id": "principal-creator", "status": status, "revision": 1},
        session=session,
    )


def test_replica_set_sessions_uuid_isolation_indexes_and_no_forbidden_surfaces(context: Any) -> None:
    hello = context["client"].admin.command("hello")
    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    assert context["database_name"].startswith("wilsy_p4_r4_d11_r6_")
    indexes = tuple(context["bootstraps"].list_indexes())
    assert indexes and all("expireAfterSeconds" not in index for index in indexes)
    assert not hasattr(context["registry"], "delete")
    assert not hasattr(context["service"], "start_session")
    assert not hasattr(context["service"], "commit_transaction")
    assert not hasattr(context["service"], "abort_transaction")


@pytest.mark.parametrize("purpose", [ASSIGN_PURPOSE, REVOKE_PURPOSE])
def test_same_transaction_creator_read_and_bootstrap_create_commit_one(context: Any, purpose: str) -> None:
    authorization = _authorization(
        context,
        purpose=purpose,
        bootstrap_id="bootstrap-" + purpose[-10:].lower(),
        idempotency_key="idem-" + purpose[-10:].lower(),
    )
    with context["client"].start_session() as session:
        session.start_transaction()
        _seed_principal(context, "ACTIVE", session=session)
        issued = context["service"].issue(authorization, now=NOW, session=session)
        assert context["bootstraps"].count_documents({"bootstrap_id": issued.bootstrap_id}, session=session) == 1
        session.commit_transaction()
    assert context["bootstraps"].count_documents({"bootstrap_id": authorization.bootstrap_id}) == 1
    assert set(context["database"].list_collection_names()) <= {PRINCIPALS, BOOTSTRAPS}


def test_abort_persists_zero_and_service_owns_no_transaction_lifecycle(context: Any) -> None:
    _seed_principal(context, "ACTIVE")
    authorization = _authorization(context)
    with context["client"].start_session() as session:
        session.start_transaction()
        context["service"].issue(authorization, now=NOW, session=session)
        assert context["bootstraps"].count_documents({}, session=session) == 1
        session.abort_transaction()
    assert context["bootstraps"].count_documents({}) == 0


def test_exact_replay_and_divergent_replay(context: Any) -> None:
    _seed_principal(context, "ACTIVE")
    exact = _authorization(context)
    with context["client"].start_session() as session:
        session.start_transaction()
        first = context["service"].issue(exact, now=NOW, session=session)
        assert context["service"].issue(exact, now=NOW, session=session) == first
        session.commit_transaction()
    divergent = _authorization(context, evidence="evidence:divergent")
    with context["client"].start_session() as session:
        session.start_transaction()
        with pytest.raises(SystemPermissionBootstrapAuthorityConflictError):
            context["service"].issue(divergent, now=NOW, session=session)
        session.abort_transaction()
    assert context["bootstraps"].count_documents({}) == 1


@pytest.mark.parametrize(
    ("status", "expected"),
    [(None, "CREATOR_PRINCIPAL_NOT_FOUND"), ("SUSPENDED", "CREATOR_PRINCIPAL_NOT_CURRENT"), ("REVOKED", "CREATOR_PRINCIPAL_NOT_CURRENT")],
)
def test_missing_and_nonactive_creator_reject(context: Any, status: str | None, expected: str) -> None:
    if status is not None:
        _seed_principal(context, status)
    with context["client"].start_session() as session:
        session.start_transaction()
        with pytest.raises(SystemPermissionBootstrapIssuanceError, match=expected):
            context["service"].issue(_authorization(context), now=NOW, session=session)
        session.abort_transaction()
    assert context["bootstraps"].count_documents({}) == 0


def test_closed_purpose_and_no_side_effect_collections(context: Any) -> None:
    with pytest.raises(SystemPermissionBootstrapCreationAuthorizationError, match="BOOTSTRAP_PURPOSE_NOT_ALLOWED"):
        _authorization(context, purpose="privileged_activation:issue")
    assert set(context["database"].list_collection_names()) <= {PRINCIPALS, BOOTSTRAPS}
    assert not ({"system_permission_assignments", "privileged_activations", "payments", "settlements"} & set(context["database"].list_collection_names()))


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_system_permission_bootstrap_issuance_service_real_mongo.py
# VERSION: v1.0.0-P4-R4-D11-R6-ISSUANCE-REAL-MONGO
# TENANT POSTURE: UUID ISOLATED; CANONICAL WILSY DATABASE UNTOUCHED
# FAIL-CLOSED POSTURE: EXACT SIGNATURE, CURRENT CREATOR, TRANSACTION, PURPOSE, REPLAY
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS REMAINS EXCLUSIVE
# END OF WILSY OS SOVEREIGN ARTIFACT
