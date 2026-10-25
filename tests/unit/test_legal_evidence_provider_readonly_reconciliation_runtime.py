from __future__ import annotations

from pathlib import Path
import re
from types import SimpleNamespace

import pytest

from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_runtime import (
    AUDIT_URI_ENV,
    AWS_ROLE_ARN_ENV,
    LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError,
    audit_target_fingerprint,
    build_legal_evidence_provider_readonly_reconciliation_runtime,
)


def test_runtime_bootstrap_requires_explicit_audit_target_without_fallback() -> None:
    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError,
        match="RECONCILIATION_AUDIT_URI_REQUIRED",
    ):
        build_legal_evidence_provider_readonly_reconciliation_runtime(
            mongo_database=SimpleNamespace(client=object()),
            env={},
        )


def test_runtime_bootstrap_uses_a_named_deployment_owned_audit_uri() -> None:
    assert AUDIT_URI_ENV == "WILSY_LEGAL_EVIDENCE_RECONCILIATION_AUDIT_MONGODB_URI"


def test_runtime_bootstrap_rejects_same_business_and_audit_target_before_connecting() -> None:
    uri = "mongodb://localhost:27017/wilsy"
    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError,
        match="RECONCILIATION_AUDIT_TARGET_NOT_SEPARATE",
    ):
        build_legal_evidence_provider_readonly_reconciliation_runtime(
            mongo_database=SimpleNamespace(client=object()),
            env={
                "MONGODB_URI": uri,
                AUDIT_URI_ENV: uri,
                "WILSY_INTERNAL_AUTH_SERVICE_ID": "service",
                "WILSY_INTERNAL_AUTH_AUDIENCE": "audience",
                "WILSY_INTERNAL_AUTH_KEY_ID": "key",
                "WILSY_INTERNAL_AUTH_SECRET": "synthetic-only",
            },
        )


def test_runtime_bootstrap_builds_and_returns_canonical_graph_and_retained_audit_client(monkeypatch, caplog) -> None:
    audit_uri = "mongodb://audit.example:27017/audit"
    from tools.eos.legal_operations.service import legal_evidence_provider_readonly_reconciliation_runtime as runtime

    import logging
    caplog.set_level(logging.INFO, logger=runtime.__name__)

    class _Collection:
        def create_index(self, keys, *, unique, name):
            return name

        def find_one(self, query, *, session=None):
            return None

    class _Database:
        def __init__(self, name, client):
            self.name = name
            self.client = client
            self.collections = {}

        def __getitem__(self, name):
            return self.collections.setdefault(name, _Collection())

    class _Client:
        def __init__(self, database=None):
            self.database = database
            self.closed = False
            self.admin = SimpleNamespace(command=lambda command: {"ok": 1})

        def get_database(self):
            return self.database

        def close(self):
            self.closed = True

    business_client = _Client()
    business_database = _Database("business", business_client)
    audit_client = _Client()
    audit_database = _Database("audit", audit_client)
    audit_client.database = audit_database
    built = {}

    class _Registry:
        def __init__(self, collection):
            self.collection = collection
            self.indexes_ready = False

        def ensure_indexes(self):
            self.indexes_ready = True

    monkeypatch.setattr(runtime, "MongoClient", lambda *args, **kwargs: audit_client)
    s3_client = object()
    monkeypatch.setattr(runtime, "build_reconciliation_readonly_s3_client", lambda **kwargs: s3_client)
    monkeypatch.setattr(runtime, "_service_config", lambda env: ({"key-1": ("secret", "principal")}, "service-1", "audience-1"))
    monkeypatch.setattr(runtime, "_production_noninteractive_assurance_service", lambda database: object())
    monkeypatch.setattr(runtime, "PlatformPrivilegedEligibilityPrerequisiteRegistry", _Registry)
    monkeypatch.setattr(runtime, "PrivilegedEligibilityEvidenceRegistry", _Registry)
    monkeypatch.setattr(runtime, "SystemPermissionAssignmentRegistry", _Registry)
    monkeypatch.setattr(runtime, "PrivilegedActivationRegistry", _Registry)
    monkeypatch.setattr(runtime, "CurrentPlatformPrivilegedEligibilityPrerequisiteResolver", lambda **kwargs: object())
    monkeypatch.setattr(runtime, "CurrentPrivilegedEligibilityResolver", lambda **kwargs: object())
    monkeypatch.setattr(runtime, "CurrentSystemPermissionPossessionResolver", lambda **kwargs: object())
    monkeypatch.setattr(runtime, "PrivilegedActivationUseAuthority", lambda **kwargs: object())

    def _build(**kwargs):
        built.update(kwargs)
        return SimpleNamespace(business_client=business_client)

    monkeypatch.setattr(
        runtime,
        "build_legal_evidence_provider_readonly_reconciliation_production_composition",
        _build,
    )
    composition, retained_audit_client = runtime.build_legal_evidence_provider_readonly_reconciliation_runtime(
        mongo_database=business_database,
        env={
            "MONGODB_URI": "mongodb://business.example:27017/business",
            runtime.AUDIT_URI_ENV: audit_uri,
            "WILSY_LEGAL_EVIDENCE_S3_BUCKET": "wilsy-legal-evidence-test-bucket",
            "WILSY_LEGAL_EVIDENCE_S3_REGION": "af-south-1",
            runtime.AWS_ROLE_ARN_ENV: "arn:aws:iam::111111111111:role/test-reconciliation-readonly",
        },
    )
    assert composition.business_client is business_client
    assert retained_audit_client is audit_client
    assert retained_audit_client.closed is False
    assert built["audit_database"] is audit_database
    assert built["audit_client"] is audit_client
    assert built["s3_client"] is s3_client
    assert built["expected_audience"] == "audience-1"
    assert built["idempotency_registry"].__class__.__name__ == (
        "LegalEvidenceReconciliationOperationIdempotencyRegistry"
    )
    assert f"AUDIT_TARGET_FINGERPRINT={audit_target_fingerprint(audit_uri)}" in caplog.text



def test_readonly_s3_client_rejects_missing_role_arn() -> None:
    from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_runtime import (
        build_reconciliation_readonly_s3_client,
    )

    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError,
        match="RECONCILIATION_AWS_ROLE_ARN_REQUIRED",
    ):
        build_reconciliation_readonly_s3_client(env={}, region="af-south-1")


def test_readonly_s3_client_rejects_ambient_or_static_credentials(monkeypatch) -> None:
    from tools.eos.legal_operations.service import legal_evidence_provider_readonly_reconciliation_runtime as runtime

    class _Credentials:
        method = "env"

    class _Session:
        def get_credentials(self):
            return _Credentials()

    monkeypatch.setattr(runtime.boto3.session, "Session", lambda: _Session())
    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError,
        match="RECONCILIATION_AWS_WORKLOAD_IDENTITY_UNAVAILABLE",
    ):
        runtime.build_reconciliation_readonly_s3_client(
            env={runtime.AWS_ROLE_ARN_ENV: "arn:aws:iam::111111111111:role/test-readonly"},
            region="af-south-1",
        )


def test_readonly_s3_client_uses_only_temporary_credentials_from_assumed_role(monkeypatch) -> None:
    from tools.eos.legal_operations.service import legal_evidence_provider_readonly_reconciliation_runtime as runtime

    calls = []
    s3_client = object()

    class _Credentials:
        method = "assume-role-with-web-identity"

    class _Sts:
        def assume_role(self, **kwargs):
            calls.append(("assume_role", kwargs))
            return {"Credentials": {
                "AccessKeyId": "temporary-access",
                "SecretAccessKey": "temporary-secret",
                "SessionToken": "temporary-token",
            }}

    class _Session:
        def get_credentials(self):
            return _Credentials()

        def client(self, service, **kwargs):
            calls.append((service, kwargs))
            return _Sts() if service == "sts" else s3_client

    monkeypatch.setattr(runtime.boto3.session, "Session", lambda: _Session())
    result = runtime.build_reconciliation_readonly_s3_client(
        env={runtime.AWS_ROLE_ARN_ENV: "arn:aws:iam::111111111111:role/test-readonly"},
        region="af-south-1",
    )
    assert result is s3_client
    assume = next(kwargs for name, kwargs in calls if name == "assume_role")
    assert assume["DurationSeconds"] == 900
    assert assume["RoleSessionName"] == "wilsy-legal-evidence-reconciliation"
    s3 = next(kwargs for name, kwargs in calls if name == "s3")
    assert s3["aws_access_key_id"] == "temporary-access"
    assert s3["aws_secret_access_key"] == "temporary-secret"
    assert s3["aws_session_token"] == "temporary-token"
    assert s3["region_name"] == "af-south-1"


def test_audit_target_fingerprint_is_stable_and_excludes_credentials() -> None:
    first = "mongodb://user-one:secret-one@audit.example:27017/audit?tls=true&authSource=admin"
    second = "mongodb://user-two:secret-two@audit.example:27017/audit?tls=true&authSource=admin"
    assert audit_target_fingerprint(first) == audit_target_fingerprint(second)
    assert audit_target_fingerprint(first) != audit_target_fingerprint(
        "mongodb://audit-other.example:27017/audit?tls=true&authSource=admin"
    )


def test_production_manifest_binds_all_required_reconciliation_secret_inputs() -> None:
    manifest = Path("k8s/eos-api-production.yaml").read_text(encoding="utf-8")
    expected = {
        "WILSY_INTERNAL_AUTH_SERVICE_ID": "internal-auth-service-id",
        "WILSY_INTERNAL_AUTH_AUDIENCE": "internal-auth-audience",
        "WILSY_INTERNAL_AUTH_KEY_ID": "internal-auth-key-id",
        "WILSY_INTERNAL_AUTH_SECRET": "internal-auth-secret",
        AUDIT_URI_ENV: "legal-evidence-reconciliation-audit-mongodb-uri",
        "WILSY_LEGAL_EVIDENCE_RECONCILIATION_TENANT_ID": "legal-evidence-reconciliation-tenant-id",
    }
    assert "path: /api/legal-operations/evidence-provider/reconciliation/health" in manifest
    for variable, secret_key in expected.items():
        binding = re.compile(
            rf"- name: {re.escape(variable)}\s+"
            rf"valueFrom:\s+secretKeyRef:\s+"
            rf"name: wilsy-eos-runtime-secrets\s+"
            rf"key: {re.escape(secret_key)}(?:\s|$)"
        )
        assert binding.search(manifest), f"missing exact Secret binding for {variable}"

    config_bindings = {
        "WILSY_LEGAL_EVIDENCE_S3_BUCKET": "legal-evidence-s3-bucket",
        "WILSY_LEGAL_EVIDENCE_S3_REGION": "legal-evidence-s3-region",
        "WILSY_LEGAL_EVIDENCE_S3_KMS_KEY_ID": "legal-evidence-s3-kms-key-id",
        AWS_ROLE_ARN_ENV: "legal-evidence-reconciliation-aws-role-arn",
    }
    for variable, config_key in config_bindings.items():
        binding = re.compile(
            rf"- name: {re.escape(variable)}\s+"
            rf"valueFrom:\s+configMapKeyRef:\s+"
            rf"name: wilsy-eos-runtime\s+"
            rf"key: {re.escape(config_key)}(?:\s|$)"
        )
        assert binding.search(manifest), f"missing exact ConfigMap binding for {variable}"


def test_runtime_authority_example_declares_fail_closed_provider_and_reconciliation_inputs() -> None:
    example = Path("k8s/eos-api-runtime-authority.example.yaml").read_text(encoding="utf-8")
    for key in (
        "legal-evidence-s3-bucket",
        "legal-evidence-s3-region",
        "legal-evidence-s3-kms-key-id",
        "legal-evidence-reconciliation-aws-role-arn",
        "internal-auth-service-id",
        "internal-auth-audience",
        "internal-auth-key-id",
        "internal-auth-secret",
        "legal-evidence-reconciliation-tenant-id",
        "legal-evidence-reconciliation-audit-mongodb-uri",
    ):
        assert f"{key}: \"\"" in example


def test_audit_target_fingerprint_ignores_credentials_but_binds_target() -> None:
    first = audit_target_fingerprint("mongodb://user-one:secret-one@audit.example:27017/audit")
    rotated = audit_target_fingerprint("mongodb://user-two:secret-two@audit.example:27017/audit")
    other_database = audit_target_fingerprint("mongodb://user-two:secret-two@audit.example:27017/audit_other")
    assert first == rotated
    assert first != other_database
    assert "secret" not in first
