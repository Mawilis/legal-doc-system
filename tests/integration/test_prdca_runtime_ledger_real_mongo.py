"""Bounded host-backed PRDCA runtime-to-ledger certificate.

TITLE: PRDCA Runtime/Ledger End-to-End Real-Mongo Certificate
VERSION: v1.0.0-M11-R8-R3B-P8-P3L-R2
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies runtime composition, caller-owned Mongo transactions,
         durable batch persistence, abort rollback, and exact replay.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_prdca_runtime_ledger_real_mongo.py
COLLABORATION / OWNERSHIP: Host-backed certificate for prdca_runtime.py and
                            prdca_ledger.py; core issuance remains owned by
                            prdca.py and transaction lifecycle by the caller.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3L-R2 certifies end-to-end runtime-to-ledger
           composition on the certified local Mongo replica set.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Disposable database only; no secrets, providers,
                             KMS, external clients, or deployment truth creation.
TENANT BOUNDARY: Platform governance evidence only; no tenant authorization.
AUTHORITY BOUNDARY: Composition and persistence certification only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
REAL-MONGO ENVIRONMENT CONTRACT: TEST_VENDOR_MONGO_URI or the certified local
                                  wilsyVendorCertRS replica-set URI.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import uuid
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pymongo import MongoClient

import tools.eos.governance.prdca as core
from tools.eos.governance.prdca_ed25519 import (
    CryptographyEd25519KeyResolver,
    CryptographyEd25519Signer,
)
from tools.eos.governance.prdca_ledger import (
    COLLECTION,
    PRDCAMongoLedger,
    PRDCAMongoSession,
)
from tools.eos.governance.prdca_runtime import compose_prdca_runtime
from tools.eos.saas.billing.tenant_inbound_provider_credential_metadata_source_registry import (
    CAPABILITY_CLASS_CREDENTIAL_METADATA,
    TenantInboundCredentialMetadataSourceDescriptor,
    TenantInboundCredentialMetadataSourceRegistrationProvenance,
)


DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
AUTHORITY_KEY_ID = "prdca-key:runtime"
CAMPAIGN = "M11-R8-R3B-P8-P3D-P5-R8-P3L"


class _FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 9, 10, 10, 0, tzinfo=timezone.utc)


@pytest.fixture()
def runtime_db() -> Any:
    """Yield one disposable database after proving the certified host topology."""
    uri = os.environ.get("TEST_VENDOR_MONGO_URI", DEFAULT_URI)
    if "mongodb.net" in uri.lower():
        pytest.fail("Atlas or production Mongo URI is forbidden for this certificate")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    hello = client.admin.command("hello")
    assert hello.get("isWritablePrimary") is True
    assert hello.get("setName") == EXPECTED_REPLICA_SET
    db_name = f"prdca_runtime_ledger_cert_{uuid.uuid4().hex}"
    database = client[db_name]
    try:
        yield database
    finally:
        client.drop_database(db_name)
        client.close()


def _evidence(root: Path, signer: CryptographyEd25519Signer) -> core.AuthenticatedRuntimeDeploymentEvidence:
    artifact = root / "artifact.py"
    artifact.write_bytes(b"certified runtime artifact")
    payload: dict[str, object] = {
        "artifact_path": "artifact.py",
        "artifact_version": "v1.0.0",
        "artifact_sha3_512": hashlib.sha3_512(artifact.read_bytes()).hexdigest(),
        "environment": "certification",
        "deployment_identity": "runtime-deployment-1",
        "deployment_event_identity": "runtime-deployment-event-1",
        "deployment_observed_at": "2026-09-10T10:00:00.000000Z",
        "campaign_identity": CAMPAIGN,
        "producer_authority": core.DEPLOYMENT_EVIDENCE_PRODUCER,
        "deployment_status": "SUCCEEDED",
    }
    envelope: dict[str, object] = {
        "envelope_schema": core.DEPLOYMENT_EVIDENCE_ENVELOPE_SCHEMA,
        "evidence_type": "AuthenticatedRuntimeDeploymentEvidence",
        "evidence_id": hashlib.sha3_512(
            core._canonical_bytes(payload, core._EVIDENCE_FIELDS)
        ).hexdigest(),
        "payload_schema": core.DEPLOYMENT_EVIDENCE_SCHEMA,
        "payload": payload,
        "producer_authority": core.DEPLOYMENT_EVIDENCE_PRODUCER,
        "attestation_key_id": AUTHORITY_KEY_ID,
        "signature_algorithm": core.SIGNATURE_ALGORITHM,
        "signature": "pending",
        "status": core.CERTIFICATE_STATUS_ACTIVE,
    }
    signing_view = {
        field: envelope[field]
        for field in core._EVIDENCE_ENVELOPE_FIELDS
        if field != "signature"
    }
    envelope["signature"] = base64.urlsafe_b64encode(
        signer.sign(
            core._canonical_bytes(
                signing_view,
                tuple(field for field in core._EVIDENCE_ENVELOPE_FIELDS if field != "signature"),
            )
        )
    ).decode("ascii").rstrip("=")
    return core.AuthenticatedRuntimeDeploymentEvidence(
        envelope_schema=str(envelope["envelope_schema"]),
        evidence_type=str(envelope["evidence_type"]),
        evidence_id=str(envelope["evidence_id"]),
        payload_schema=str(envelope["payload_schema"]),
        payload=core._mapping_proxy(payload),
        producer_authority=str(envelope["producer_authority"]),
        attestation_key_id=str(envelope["attestation_key_id"]),
        signature_algorithm=str(envelope["signature_algorithm"]),
        signature=str(envelope["signature"]),
        status=str(envelope["status"]),
    )


def _runtime(root: Path, database: Any) -> tuple[Any, Any, core.AuthenticatedRuntimeDeploymentEvidence]:
    private_key = Ed25519PrivateKey.from_private_bytes(bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"))
    signer = CryptographyEd25519Signer(private_key)
    resolver = CryptographyEd25519KeyResolver(
        {AUTHORITY_KEY_ID: private_key.public_key()}
    )
    ledger = PRDCAMongoLedger(database[COLLECTION])
    ledger.ensure_indexes()
    runtime = compose_prdca_runtime(
        signer=signer,
        key_resolver=resolver,
        deployment_evidence_key_resolver=resolver,
        ledger=ledger,
        clock=_FixedClock(),
        artifact_root=root,
    )
    return runtime, ledger, _evidence(root, signer)


def _inputs(runtime: Any, evidence: core.AuthenticatedRuntimeDeploymentEvidence, source: str) -> tuple[dict[str, str], Any]:
    values = {
        "source_identity": source,
        "source_contract_version": "v1",
        "implementation_identity": "impl:runtime-source",
        "capability_class": CAPABILITY_CLASS_CREDENTIAL_METADATA,
        "campaign_identity": CAMPAIGN,
        "authority_key_id": AUTHORITY_KEY_ID,
    }
    prc = runtime.issue_platform_registration_certificate(**values)
    dcc = runtime.issue_deployment_certification_certificate(
        platform_registration=prc,
        deployment_evidence=evidence,
        campaign_identity=CAMPAIGN,
        authority_key_id=AUTHORITY_KEY_ID,
    )
    descriptor = TenantInboundCredentialMetadataSourceDescriptor.create(
        source_identity=source,
        source_contract_version="v1",
        implementation_identity="impl:runtime-source",
        capability_class=CAPABILITY_CLASS_CREDENTIAL_METADATA,
        registration_provenance=TenantInboundCredentialMetadataSourceRegistrationProvenance(
            platform_registration_id=prc.artifact_id,
            deployment_certification_id=dcc.artifact_id,
        ),
    )
    return values, descriptor


def test_runtime_composition_commit_and_exact_replay(runtime_db: Any, tmp_path: Path) -> None:
    runtime, ledger, evidence = _runtime(tmp_path, runtime_db)
    values, descriptor = _inputs(runtime, evidence, "source-runtime")
    with runtime_db.client.start_session() as session:
        session.start_transaction()
        first = runtime.issue_and_persist_certificate_batch(
            **values, deployment_evidence=evidence, descriptor=descriptor,
            session=PRDCAMongoSession(session),
        )
        session.commit_transaction()
        session.start_transaction()
        replay = runtime.issue_and_persist_certificate_batch(
            **values, deployment_evidence=evidence, descriptor=descriptor,
            session=PRDCAMongoSession(session),
        )
        session.commit_transaction()
    assert replay == first
    assert runtime_db[COLLECTION].count_documents({}) == 1
    hydrated = ledger.get_by_platform_registration_id(first.platform_registration.artifact_id)
    assert hydrated == first


def test_runtime_composition_caller_abort_is_not_durable(runtime_db: Any, tmp_path: Path) -> None:
    runtime, _, evidence = _runtime(tmp_path, runtime_db)
    values, descriptor = _inputs(runtime, evidence, "source-aborted")
    with runtime_db.client.start_session() as session:
        session.start_transaction()
        runtime.issue_and_persist_certificate_batch(
            **values, deployment_evidence=evidence, descriptor=descriptor,
            session=PRDCAMongoSession(session),
        )
        session.abort_transaction()
    assert runtime_db[COLLECTION].count_documents({}) == 0


def test_runtime_composition_exposes_no_transaction_lifecycle(runtime_db: Any, tmp_path: Path) -> None:
    runtime, _, _ = _runtime(tmp_path, runtime_db)
    public_names = set(type(runtime).__dict__)
    assert "start_transaction" not in public_names
    assert "commit" not in public_names
    assert "abort" not in public_names


# ARTIFACT: test_prdca_runtime_ledger_real_mongo.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3L-R2
# AUTHORITY BOUNDARY: host-backed runtime-to-ledger composition certification only
# TENANT POSTURE: platform governance scope; no tenant authorization
# FAIL-CLOSED POSTURE: wrong host topology, aborted writes, and hydration failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
