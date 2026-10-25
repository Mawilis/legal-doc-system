"""Full-gate real-Mongo certification using the actual signed workload verifier.

CHANGELOG: v1.0.1 rounds test clock to MongoDB millisecond precision before persistence.
VERSION: v1.0.1-L10A2R-C4D7-RECONCILIATION-FULL-GATE-REAL-MONGO
AUTHORITY: Evidence-only certification; no production invocation.
AUTHORITY BOUNDARY: Current P3/P5, SYSTEM permission possession, and tenant scope only.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import pytest

import tests.integration.test_privileged_activation_issuance_service_real_mongo as p4_module
from tests.integration.test_privileged_activation_issuance_service_real_mongo import (
    PRINCIPAL,
    _issue,
    _seed,
    context,
)
from tools.eos.auth.current_system_permission_possession import (
    CurrentSystemPermissionPossessionResolver,
)
from tools.eos.auth.internal_service_noninteractive_assurance_service import (
    InternalServiceNoninteractiveAssuranceService,
)
from tools.eos.auth.internal_service_replay_registry import (
    COLLECTION as REPLAY_COLLECTION,
    InternalServiceReplayRegistry,
)
from tools.eos.auth.internal_service_trust import (
    body_sha3_512,
    canonical_request,
)
from tools.eos.auth.internal_service_workload_credential_authority import (
    PLATFORM_INTERNAL_SCOPE,
    InternalServiceWorkloadCredentialAuthority,
    WorkloadCredentialLifecycleStatus,
)
from tools.eos.auth.internal_service_workload_credential_registry import (
    COLLECTION as CREDENTIAL_HISTORY_COLLECTION,
    POINTER_COLLECTION as CREDENTIAL_POINTER_COLLECTION,
    InternalServiceWorkloadCredentialRegistry,
)
from tools.eos.auth.internal_service_workload_proof_service import (
    InternalServiceWorkloadProofService,
)
from tools.eos.auth.privileged_activation_use_authority import (
    PrivilegedActivationUseAuthority,
)
from tools.eos.auth.privileged_noninteractive_security_proof_registry import (
    COLLECTION as NONINTERACTIVE_PROOF_COLLECTION,
    PrivilegedNoninteractiveSecurityProofRegistry,
)
from tools.eos.auth.privileged_security_assurance import (
    PrivilegedAssurancePurpose,
)
from tools.eos.auth.privileged_security_assurance_evidence_registry import (
    COLLECTION as ASSURANCE_COLLECTION,
)
from tools.eos.auth.privileged_workload_trust_currentness_registry import (
    COLLECTION as WORKLOAD_CURRENTNESS_COLLECTION,
    PrivilegedWorkloadTrustCurrentnessRegistry,
)
from tools.eos.auth.system_permission_assignment import SystemPermissionAssignment
from tools.eos.auth.platform_authorization_decision_evidence_registry import (
    COLLECTION as PLATFORM_DECISION_COLLECTION,
    PlatformAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_authorization_gate import (
    RECONCILIATION_READ_PERMISSION,
    LegalEvidenceProviderReadOnlyReconciliationAuthorizationError,
    LegalEvidenceProviderReadOnlyReconciliationAuthorizationGate,
    build_server_configured_reconciliation_target,
)

SERVICE_ID = "legal-ops-reconciliation-service"
KEY_ID = "reconciliation-key-a"
SECRET = "test-only-internal-service-secret-never-used-in-production"
AUDIENCE = "wilsy-eos-reconciliation"


def _tenant_doc(tenant_id: str, *, created_at: datetime) -> dict[str, Any]:
    return {
        "tenant_id": tenant_id,
        "name": "Legal Evidence Reconciliation Certification",
        "organization": {
            "organization_name": "Legal Evidence Reconciliation Certification",
            "industry": "General",
            "plan": "ENTERPRISE",
            "legal_name": None,
            "tax_id": None,
            "contact_email": None,
            "regions": ["Africa"],
            "created_at": created_at.isoformat(),
        },
        "industry": "General",
        "plan": "ENTERPRISE",
        "regions": ["Africa"],
        "status": "ACTIVE",
        "created_at": created_at.isoformat(),
        "alias": tenant_id,
        "region": "ZA",
        "compliance_flags": {"certification": True},
        "verified": False,
    }


def _signed_request(*, body: bytes) -> dict[str, str]:
    timestamp = str(int(time.time()))
    nonce = secrets.token_hex(16)
    correlation_id = "reconciliation-" + uuid4().hex
    digest = body_sha3_512(body)
    canonical = canonical_request(
        version="v1",
        service_id=SERVICE_ID,
        audience=AUDIENCE,
        method="POST",
        path="/internal/reconciliation",
        timestamp=timestamp,
        nonce=nonce,
        body_sha3_512_value=digest,
        correlation_id=correlation_id,
    )
    signature = hmac.new(
        SECRET.encode("utf-8"),
        canonical,
        hashlib.sha256,
    ).hexdigest()
    return {
        "version": "v1",
        "service_id": SERVICE_ID,
        "audience": AUDIENCE,
        "key_id": KEY_ID,
        "timestamp": timestamp,
        "nonce": nonce,
        "body_sha3_512": digest,
        "correlation_id": correlation_id,
        "signature": signature,
        "method": "POST",
        "path": "/internal/reconciliation",
    }


def _build_full_gate(
    context_value: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[LegalEvidenceProviderReadOnlyReconciliationAuthorizationGate, dict[str, Any]]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    monkeypatch.setattr(p4_module, "NOW", now)

    _seed(context_value)
    with context_value["client"].start_session() as session:
        session.start_transaction()
        activation = _issue(
            context_value,
            key="reconciliation-full-gate-activation-" + uuid4().hex,
            session=session,
        )
        session.commit_transaction()

    database = context_value["database"]
    decision_audit_collection = database[PLATFORM_DECISION_COLLECTION]
    decision_evidence_registry = PlatformAuthorizationDecisionEvidenceRegistry(
        decision_audit_collection,
        audit_client=context_value["client"],
    )
    decision_evidence_registry.ensure_indexes()
    tenant_id = "tenant-reconciliation-" + uuid4().hex
    database["tenants"].insert_one(_tenant_doc(tenant_id, created_at=now))

    credential_registry = InternalServiceWorkloadCredentialRegistry(
        database[CREDENTIAL_HISTORY_COLLECTION],
        database[CREDENTIAL_POINTER_COLLECTION],
    )
    credential_registry.ensure_indexes()

    workload_registry = PrivilegedWorkloadTrustCurrentnessRegistry(
        database[WORKLOAD_CURRENTNESS_COLLECTION]
    )
    workload_registry.ensure_indexes()

    proof_registry = PrivilegedNoninteractiveSecurityProofRegistry(
        database[NONINTERACTIVE_PROOF_COLLECTION]
    )
    proof_registry.ensure_indexes()

    replay_collection = database[REPLAY_COLLECTION]
    InternalServiceReplayRegistry.ensure_indexes(replay_collection)

    credential = InternalServiceWorkloadCredentialAuthority(
        service_id=SERVICE_ID,
        key_id=KEY_ID,
        principal_id=PRINCIPAL,
        credential_scope=PLATFORM_INTERNAL_SCOPE,
        credential_revision=1,
        lifecycle_revision=1,
        lifecycle_status=WorkloadCredentialLifecycleStatus.CURRENT,
        status_changed_at=now - timedelta(minutes=1),
    )
    read_assignment = SystemPermissionAssignment.assign(
        assignment_id="reconciliation-read-" + uuid4().hex,
        principal_id=PRINCIPAL,
        permission_id=RECONCILIATION_READ_PERMISSION,
        assigned_by_principal_id="governed-system-grantor",
        assigned_at=now - timedelta(minutes=1),
        assignment_evidence_reference="reconciliation-read-evidence-" + uuid4().hex,
    )
    with context_value["client"].start_session() as session:
        session.start_transaction()
        credential_registry.create_or_replay(credential, session=session)
        context_value["assignment_registry"].create_or_replay(
            read_assignment,
            idempotency_key="reconciliation-read-assignment-" + uuid4().hex,
            session=session,
        )
        session.commit_transaction()

    workload_source = InternalServiceWorkloadProofService(
        replay_collection=replay_collection,
        credential_registry=credential_registry,
        principal_collection=context_value["principals"],
        workload_registry=workload_registry,
        clock=lambda: now,
    )
    noninteractive = InternalServiceNoninteractiveAssuranceService(
        workload_source=workload_source,
        workload_registry=workload_registry,
        proof_registry=proof_registry,
        evidence_registry=context_value["assurance_registry"],
        clock=lambda: now,
        proof_id_factory=lambda: "WILSY-NONINTERACTIVE-PROOF-" + uuid4().hex,
        evidence_id_factory=lambda: "WILSY-ASSURANCE-EVIDENCE-" + uuid4().hex,
    )
    use_authority = PrivilegedActivationUseAuthority(
        activation_registry=context_value["activation_registry"],
        eligibility_resolver=context_value["issuance_service"]._eligibility_resolver,
        noninteractive_assurance_service=noninteractive,
    )
    possession = CurrentSystemPermissionPossessionResolver(
        principal_collection=context_value["principals"],
        assignment_registry=context_value["assignment_registry"],
    )
    target = build_server_configured_reconciliation_target(
        mongo_database=database,
        env={
            "WILSY_LEGAL_EVIDENCE_RECONCILIATION_TENANT_ID": tenant_id,
            "WILSY_LEGAL_EVIDENCE_S3_BUCKET": "wilsy-legal-evidence-test",
            "WILSY_LEGAL_EVIDENCE_S3_REGION": "af-south-1",
        },
    )
    gate = LegalEvidenceProviderReadOnlyReconciliationAuthorizationGate(
        use_authority=use_authority,
        permission_possession_resolver=possession,
        scope_resolver=target.scope_resolver,
        workload_keys={KEY_ID: (SERVICE_ID, SECRET)},
        expected_audience=AUDIENCE,
        provider_name=target.provider_name,
        decision_evidence_registry=decision_evidence_registry,
    )
    return gate, {
        "activation": activation,
        "tenant_id": tenant_id,
        "target": target,
        "workload_registry": workload_registry,
        "workload_collection": database[WORKLOAD_CURRENTNESS_COLLECTION],
        "proof_registry": proof_registry,
        "replay_collection": replay_collection,
        "assurance_collection": database[ASSURANCE_COLLECTION],
        "read_assignment": read_assignment,
        "now": now,
        "decision_audit_collection": decision_audit_collection,
        "decision_evidence_registry": decision_evidence_registry,
    }


def test_full_gate_uses_actual_signed_workload_and_current_mongo_authorities(
    context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gate, setup = _build_full_gate(context, monkeypatch)
    body = b"{}"
    request = _signed_request(body=body)
    at = setup["now"] + timedelta(seconds=1)
    assurance_before = setup["assurance_collection"].count_documents({})
    decision_key = "reconciliation-full-gate-use-" + uuid4().hex

    with context["client"].start_session() as session:
        session.start_transaction()
        result = gate.authorize(
            request=request,
            body=body,
            idempotency_key=decision_key,
            at=at,
            session=session,
        )
        assert session.in_transaction is True
        assert result.principal_id == PRINCIPAL
        assert result.activation_id == setup["activation"].activation_id
        assert result.permission_assignment_id == setup["read_assignment"].assignment_id
        assert result.scope.tenant_id == setup["tenant_id"]
        assert result.provider_name == setup["target"].provider_name
        session.commit_transaction()

    assert setup["replay_collection"].count_documents({}) == 1
    assert setup["workload_collection"].count_documents({}) == 1
    assert setup["proof_registry"]._collection.count_documents({}) == 1
    assert setup["assurance_collection"].count_documents({}) == assurance_before + 1
    audit_row = setup["decision_audit_collection"].find_one({"idempotency_key": decision_key})
    assert audit_row is not None
    assert audit_row["decision"] == "ALLOW"
    assert audit_row["principal_id"] == PRINCIPAL
    assert audit_row["target_tenant_id"] == setup["tenant_id"]


def test_full_gate_abort_rolls_back_p3_evidence_and_replay_claim(
    context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gate, setup = _build_full_gate(context, monkeypatch)
    body = b"{}"
    request = _signed_request(body=body)
    at = setup["now"] + timedelta(seconds=1)
    assurance_before = setup["assurance_collection"].count_documents({})
    decision_key = "reconciliation-full-gate-abort-" + uuid4().hex

    with context["client"].start_session() as session:
        session.start_transaction()
        result = gate.authorize(
            request=request,
            body=body,
            idempotency_key=decision_key,
            at=at,
            session=session,
        )
        assert result.principal_id == PRINCIPAL
        assert session.in_transaction is True
        session.abort_transaction()

    assert setup["replay_collection"].count_documents({}) == 0
    assert setup["proof_registry"]._collection.count_documents({}) == 0
    assert setup["assurance_collection"].count_documents({}) == assurance_before
    assert context["database"][WORKLOAD_CURRENTNESS_COLLECTION].count_documents({}) == 0
    audit_row = setup["decision_audit_collection"].find_one({"idempotency_key": decision_key})
    assert audit_row is not None
    assert audit_row["decision"] == "ALLOW"
    assert audit_row["principal_id"] == PRINCIPAL


class _ReadOnlyRecordingS3Client:
    """S3 capability double: record reads and make any mutation fatal."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def list_multipart_uploads(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append("list_multipart_uploads")
        return {"Uploads": [], "IsTruncated": False}

    def list_object_versions(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append("list_object_versions")
        return {"Versions": [], "DeleteMarkers": [], "IsTruncated": False}

    def head_object(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append("head_object")
        raise AssertionError("empty enumeration must not trigger object HEAD")

    def create_multipart_upload(self, **kwargs: Any) -> dict[str, Any]:
        raise AssertionError("mutation API must never be invoked")

    def upload_part(self, **kwargs: Any) -> dict[str, Any]:
        raise AssertionError("mutation API must never be invoked")

    def complete_multipart_upload(self, **kwargs: Any) -> dict[str, Any]:
        raise AssertionError("mutation API must never be invoked")

    def abort_multipart_upload(self, **kwargs: Any) -> dict[str, Any]:
        raise AssertionError("mutation API must never be invoked")


def _actual_readonly_composition(context_value: dict[str, Any], setup: dict[str, Any], s3_client: Any):
    from typing import cast
    from botocore.client import BaseClient
    from tools.eos.legal_operations.service.legal_evidence_s3_storage_adapter import (
        LegalEvidenceS3StorageAdapter,
    )
    from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_provider import (
        LegalEvidenceProviderReadOnlyReconciliationProvider,
    )
    from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_factory import (
        build_legal_evidence_provider_readonly_reconciliation_dependencies,
    )

    adapter = LegalEvidenceS3StorageAdapter(
        setup["target"].storage_configuration,
        client=cast(BaseClient, s3_client),
    )
    facade = LegalEvidenceProviderReadOnlyReconciliationProvider(adapter)
    dependencies = build_legal_evidence_provider_readonly_reconciliation_dependencies(
        provider=facade,
        mongo_database=context_value["database"],
    )
    assert not hasattr(facade, "begin")
    assert not hasattr(facade, "write_chunk")
    assert not hasattr(facade, "complete")
    assert not hasattr(facade, "abort")
    return dependencies


def test_authorization_failure_calls_zero_real_adapter_provider_operations(
    context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gate, setup = _build_full_gate(context, monkeypatch)
    s3_client = _ReadOnlyRecordingS3Client()
    _actual_readonly_composition(context, setup, s3_client)
    body = b"{}"
    request = _signed_request(body=body)
    request["signature"] = "invalid-signature"
    decision_key = "reconciliation-provider-deny-" + uuid4().hex

    with context["client"].start_session() as session:
        session.start_transaction()
        with pytest.raises(
            LegalEvidenceProviderReadOnlyReconciliationAuthorizationError,
            match="^CURRENT_PLATFORM_OPERATOR_USE_DENIED$",
        ):
            gate.authorize(
                request=request,
                body=body,
                idempotency_key=decision_key,
                at=setup["now"] + timedelta(seconds=1),
                session=session,
            )
        session.abort_transaction()

    assert s3_client.calls == []
    audit_row = setup["decision_audit_collection"].find_one({"idempotency_key": decision_key})
    assert audit_row is not None
    assert audit_row["decision"] == "DENY"
    assert audit_row["reason_code"] == "CURRENT_PLATFORM_OPERATOR_USE_DENIED"
    assert audit_row["principal_id"] is None
    assert audit_row["identity_trust"] == "UNVERIFIED"


def test_authorized_composition_uses_actual_s3_adapter_read_only(
    context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gate, setup = _build_full_gate(context, monkeypatch)
    s3_client = _ReadOnlyRecordingS3Client()
    dependencies = _actual_readonly_composition(context, setup, s3_client)
    body = b"{}"
    request = _signed_request(body=body)
    at = setup["now"] + timedelta(seconds=1)

    with context["client"].start_session() as session:
        session.start_transaction()
        authorized = gate.authorize(
            request=request,
            body=body,
            idempotency_key="reconciliation-provider-allow-" + uuid4().hex,
            at=at,
            session=session,
        )
        result = dependencies.coordinator.reconcile(
            scope=authorized.scope,
            provider_name=authorized.provider_name,
            observed_at=at,
            session=session,
        )
        assert session.in_transaction is True
        assert result.coverage_complete is True
        assert result.orphan_proven is False
        assert result.provider_delete_authorized is False
        assert result.cleanup_authorized is False
        session.abort_transaction()

    assert s3_client.calls
    assert set(s3_client.calls) <= {"list_multipart_uploads", "list_object_versions"}
    assert "create_multipart_upload" not in s3_client.calls
    assert "upload_part" not in s3_client.calls
    assert "complete_multipart_upload" not in s3_client.calls
    assert "abort_multipart_upload" not in s3_client.calls
