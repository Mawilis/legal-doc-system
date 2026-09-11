"""Bounded host-backed PRDCA application-caller certificate.

TITLE: PRDCA Application Caller Operational Real-Mongo Certificate
VERSION: v1.0.0-M11-R8-R3B-P8-P3N-R1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies explicit application-owned Mongo transactions and durable
         runtime-to-ledger composition on the certified replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_prdca_application_real_mongo.py
COLLABORATION / OWNERSHIP: Host-backed certificate for prdca_application.py.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3N-R1 certifies application commit, exact
           replay, and failure rollback using bounded disposable Mongo data.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No secrets, providers, KMS, or production database.
TENANT BOUNDARY: Platform governance evidence only; no tenant authorization.
AUTHORITY BOUNDARY: Application transaction and deployment composition only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
REAL-MONGO ENVIRONMENT CONTRACT: TEST_VENDOR_MONGO_URI or local
                                  wilsyVendorCertRS replica-set URI.
"""
from __future__ import annotations

import base64
import hashlib
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pymongo import MongoClient

import tools.eos.governance.prdca as core
from tools.eos.governance.prdca_application import PRDCAApplication
from tools.eos.governance.prdca_ed25519 import (
    CryptographyEd25519KeyResolver,
    CryptographyEd25519Signer,
)
from tools.eos.governance.prdca_ledger import COLLECTION
from tools.eos.saas.billing.tenant_inbound_provider_credential_metadata_source_registry import (
    CAPABILITY_CLASS_CREDENTIAL_METADATA,
    TenantInboundCredentialMetadataSourceDescriptor,
    TenantInboundCredentialMetadataSourceRegistrationProvenance,
)


DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
AUTHORITY_KEY_ID = "prdca-key:application"
CAMPAIGN = "M11-R8-R3B-P8-P3D-P5-R8-P3N"
SEED = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")


class _FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 9, 10, 10, 0, tzinfo=timezone.utc)


@pytest.fixture()
def application(tmp_path: Path) -> Any:
    uri = os.environ.get("TEST_VENDOR_MONGO_URI", DEFAULT_URI)
    if "mongodb.net" in uri.lower():
        pytest.fail("Production or Atlas Mongo URI is forbidden")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    hello = client.admin.command("hello")
    assert hello.get("isWritablePrimary") is True
    assert hello.get("setName") == EXPECTED_REPLICA_SET
    database_name = f"prdca_application_cert_{uuid.uuid4().hex}"
    private_key = Ed25519PrivateKey.from_private_bytes(SEED)
    signer = CryptographyEd25519Signer(private_key)
    resolver = CryptographyEd25519KeyResolver(
        {AUTHORITY_KEY_ID: private_key.public_key()}
    )
    app = PRDCAApplication.from_mongo(
        mongo_client=client,
        database_name=database_name,
        signer=signer,
        key_resolver=resolver,
        deployment_evidence_key_resolver=resolver,
        clock=_FixedClock(),
        artifact_root=tmp_path,
    )
    app.initialize()
    try:
        yield app, client[database_name], signer
    finally:
        client.drop_database(database_name)
        client.close()


def _evidence(root: Path, signer: CryptographyEd25519Signer) -> core.AuthenticatedRuntimeDeploymentEvidence:
    artifact = root / "artifact.py"
    artifact.write_bytes(b"application-certified artifact")
    payload: dict[str, object] = {
        "artifact_path": "artifact.py",
        "artifact_version": "v1.0.0",
        "artifact_sha3_512": hashlib.sha3_512(artifact.read_bytes()).hexdigest(),
        "environment": "certification",
        "deployment_identity": "application-deployment-1",
        "deployment_event_identity": "application-deployment-event-1",
        "deployment_observed_at": "2026-09-10T10:00:00.000000Z",
        "campaign_identity": CAMPAIGN,
        "producer_authority": core.DEPLOYMENT_EVIDENCE_PRODUCER,
        "deployment_status": "SUCCEEDED",
    }
    evidence_id = hashlib.sha3_512(
        core._canonical_bytes(payload, core._EVIDENCE_FIELDS)
    ).hexdigest()
    envelope: dict[str, object] = {
        "envelope_schema": core.DEPLOYMENT_EVIDENCE_ENVELOPE_SCHEMA,
        "evidence_type": "AuthenticatedRuntimeDeploymentEvidence",
        "evidence_id": evidence_id,
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
        evidence_id=evidence_id,
        payload_schema=str(envelope["payload_schema"]),
        payload=core._mapping_proxy(payload),
        producer_authority=core.DEPLOYMENT_EVIDENCE_PRODUCER,
        attestation_key_id=AUTHORITY_KEY_ID,
        signature_algorithm=core.SIGNATURE_ALGORITHM,
        signature=str(envelope["signature"]),
        status=core.CERTIFICATE_STATUS_ACTIVE,
    )


def _request(app: PRDCAApplication, evidence: Any, source: str) -> tuple[dict[str, str], Any]:
    values = {
        "source_identity": source,
        "source_contract_version": "v1",
        "implementation_identity": "impl:application-source",
        "capability_class": CAPABILITY_CLASS_CREDENTIAL_METADATA,
        "campaign_identity": CAMPAIGN,
        "authority_key_id": AUTHORITY_KEY_ID,
    }
    prc = app.runtime.issue_platform_registration_certificate(**values)
    dcc = app.runtime.issue_deployment_certification_certificate(
        platform_registration=prc,
        deployment_evidence=evidence,
        campaign_identity=CAMPAIGN,
        authority_key_id=AUTHORITY_KEY_ID,
    )
    descriptor = TenantInboundCredentialMetadataSourceDescriptor.create(
        source_identity=source,
        source_contract_version="v1",
        implementation_identity="impl:application-source",
        capability_class=CAPABILITY_CLASS_CREDENTIAL_METADATA,
        registration_provenance=TenantInboundCredentialMetadataSourceRegistrationProvenance(
            platform_registration_id=prc.artifact_id,
            deployment_certification_id=dcc.artifact_id,
        ),
    )
    return values, descriptor


def test_application_commit_and_exact_replay(application: Any, tmp_path: Path) -> None:
    app, database, signer = application
    evidence = _evidence(tmp_path, signer)
    values, descriptor = _request(app, evidence, "source-application")
    first = app.issue_and_persist_certificate_batch(
        **values, deployment_evidence=evidence, descriptor=descriptor
    )
    replay = app.issue_and_persist_certificate_batch(
        **values, deployment_evidence=evidence, descriptor=descriptor
    )
    assert replay == first
    assert database[COLLECTION].count_documents({}) == 1
    assert app.get_certificate_batch(first.platform_registration.artifact_id) == first


def test_application_failure_aborts_real_transaction(application: Any, tmp_path: Path) -> None:
    app, database, signer = application
    evidence = _evidence(tmp_path, signer)
    values, _ = _request(app, evidence, "source-abort")
    invalid_descriptor = TenantInboundCredentialMetadataSourceDescriptor.create(
        source_identity="source-abort",
        source_contract_version="v1",
        implementation_identity="impl:application-source",
        capability_class=CAPABILITY_CLASS_CREDENTIAL_METADATA,
        registration_provenance=TenantInboundCredentialMetadataSourceRegistrationProvenance(
            platform_registration_id="wrong-platform-id",
            deployment_certification_id="wrong-deployment-id",
        ),
    )
    with pytest.raises(core.PRDCAIdentifierMismatchError):
        app.issue_and_persist_certificate_batch(
            **values, deployment_evidence=evidence, descriptor=invalid_descriptor
        )
    assert database[COLLECTION].count_documents({}) == 0


# ARTIFACT: test_prdca_application_real_mongo.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3N-R1
# AUTHORITY BOUNDARY: host-backed application caller certification only
# TENANT POSTURE: platform governance scope; no tenant authorization
# FAIL-CLOSED POSTURE: wrong host, failed composition, and aborted writes reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
