from __future__ import annotations

from types import SimpleNamespace

import pytest

from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_runtime import (
    AUDIT_URI_ENV,
    LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError,
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
