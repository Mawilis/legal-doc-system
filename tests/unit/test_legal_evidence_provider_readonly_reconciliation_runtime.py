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
