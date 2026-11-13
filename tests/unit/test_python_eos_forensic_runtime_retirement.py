"""WILSY OS Python EOS exclusivity and retired backend certificate.

TITLE: WILSY OS Python EOS Runtime Exclusivity Certificate
VERSION: v2.5.0-PYTHON-QR-CONTRACT-AND-ROUTER-CERT
CHANGELOG: v2.5.0-PYTHON-QR-CONTRACT-AND-ROUTER-CERT — requires the authenticated Python QR issue/verify mounts and exact-legacy contract regression owners.
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves physical removal of the retired Node business runtime, its
    direct test/tool consumers and package entrypoints while retaining the
    Python EOS route, persistence, scheduler and financial authority boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_python_eos_forensic_runtime_retirement.py
COLLABORATION / OWNERSHIP: Python EOS runtime, client transport and CI owners.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG:
  v2.5.0-PYTHON-QR-CONTRACT-AND-ROUTER-CERT requires authenticated Python
    QR routes, the fixed legacy payload contract certificate and tenant/tamper
    boundary tests as active regression owners.
  v2.4.1-POLICY-WILDCARD-CLASSIFICATION aligns this certificate with governed
    wildcard policy entries and validates concrete retired CRM, AI and search
    proof-harness paths.
  v2.4.0-PYTHON-ONLY-COMPLETE-SURFACE-CLASSIFICATION classifies the full
    deleted backend/config/tool/test set while retaining exact migration
    history and Python-owned migration surfaces.
  v2.1.0-RETIRED-NODE-BACKEND-REMOVAL records legacy test and script consumer
    retirement, confirms Python Merkle/subscription contracts, and checks the
    production-surface classifications for physically removed artifacts.
  v2.0.0-RETIRED-NODE-BACKEND-REMOVAL replaces dormant-source retention with
    exhaustive backend-source, dependency, scheduler and launcher absence.
  v1.3.0-CANONICAL-DEV-TRANSPORT-CERT established fixed development transport.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Repository-only reads; no identity, keys or data.
TENANT BOUNDARY: No tenant authority is constructed by this certificate.
AUTHORITY BOUNDARY: Repository regression evidence, not production activation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tools.eos.governance.repository_integrity_guard import classify

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOTS = (
    "server",
    "services",
    "client/server",
    "middleware",
    "models",
    "algorithms",
)
BACKEND_EXTENSIONS = {".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".sh"}
FORBIDDEN_DEPENDENCIES = {
    "express",
    "mongoose",
    "mongodb-memory-server",
    "pm2",
    "bullmq",
    "agenda",
    "node-cron",
    "ioredis",
    "redis",
    "jsonwebtoken",
    "speakeasy",
    "bcrypt",
}
RETIRED_NODE_CONSUMERS = (
    "tests/merkle.test.js",
    "tests/unit/qrServices.test.js",
    "tests/integration/qrPaymentFlow.test.js",
    "tests/unit/subscriptionModel.test.js",
    "scripts/test-queue-flow.js",
    "scripts/wilsy-generate-playbook.js",
)
RETAINED_NODE_MIGRATION_HISTORY = (
    "server/scripts/finalize-migration.js",
    "server/scripts/migrate-audit-legacy.js",
    "server/scripts/migrate-case-legacy.js",
    "server/scripts/migrate-documents-tenancy.js",
    "server/scripts/migrate-fixed.js",
    "server/scripts/migrate.js",
    "server/scripts/migration/DocumentMigrationEngine.js",
    "server/scripts/migration/MigrationLogger.js",
    "server/scripts/migration/MigrationRunner.js",
    "server/scripts/rollback-migration.js",
    "server/scripts/rollback-simple.js",
    "server/scripts/verify-migration-state-diagnostic.js",
    "server/scripts/verify-migration-state.js",
)
PYTHON_MIGRATION_SURFACES = (
    "tools/eos/saas/auth/migrations/refresh_token_tenant_backfill.py",
    "tools/eos/saas/auth/migrations/refresh_token_indexes.py",
    "tools/eos/saas/auth/migrations/reconcile_legacy_principal_authority.py",
    "tools/eos/saas/auth/migrations/reconcile_legacy_super_admin_tenant.py",
    "tools/eos/saas/billing/migrations/tenant_inbound_provider_credential_security_authority_index_migration.py",
    "tools/eos/saas/billing/migrations/tenant_inbound_merchant_configuration_lifecycle_idempotency_projection.py",
)
PYTHON_DOMAIN_CONTRACTS = (
    "tests/unit/test_forensic_merkle_registry.py",
    "tests/unit/test_forensic_merkle_router.py",
    "tests/unit/test_subscription_domain.py",
    "tests/unit/test_subscription_registry_transaction_injection.py",
    "tools/eos/api/subscription_router.py",
    "tools/eos/saas/billing/subscription_registry.py",
)
RETIRED_POLICY_PATTERNS = {
    "server/controllers/businessArtifactPdfController.js",
    "server/services/artifacts/wilsyEnterprisePdfRenderer.js",
    "server/services/qr/qrGenerator.js",
    "server/package.json",
    "server/package-lock.json",
    "server/*.js",
    "server/**/*.js",
    "server/**/*.mjs",
    "server/**/*.cjs",
    "server/**",
    "server/config/cron-jobs.yml",
    "services/*.js",
    "services/**/*.js",
    "client/server/**/*.js",
    "middleware/**/*.js",
    "models/**/*.js",
    "algorithms/**/*.js",
    "backfillRoles.js",
    "deploy-prod.sh",
    "scripts/seed.js",
    "scripts/test-queue-flow.js",
    "scripts/wilsy-account-command-center-production-gate.js",
    "scripts/wilsy-ai-*-proof-harness.js",
    "scripts/wilsy-crm-*.js",
    "scripts/wilsy-r73*.js",
    "tests/merkle.test.js",
    "tests/unit/qrServices.test.js",
    "tests/integration/qrPaymentFlow.test.js",
    "tests/unit/subscriptionModel.test.js",
}


@pytest.mark.parametrize("relative_path", BACKEND_ROOTS)
def test_retired_backend_trees_contain_no_executable_business_source(
    relative_path: str,
) -> None:
    """Audit/history artifacts survive; executable Node implementations do not."""
    directory = ROOT / relative_path
    remaining = sorted(
        str(path.relative_to(ROOT))
        for path in directory.rglob("*")
        if path.is_file()
        and path.suffix in BACKEND_EXTENSIONS
        and "node_modules" not in path.parts
    )
    expected = sorted(
        historical_path
        for historical_path in RETAINED_NODE_MIGRATION_HISTORY
        if relative_path == "server" and historical_path.startswith("server/")
    )
    assert remaining == expected
    for filename in (
        "package.json",
        "package-lock.json",
        "Dockerfile",
        "Dockerfile.worker",
        "nodemon.json",
    ):
        assert not (directory / filename).exists()


def test_retired_node_test_and_tool_consumers_stay_removed() -> None:
    """No remaining harness imports deleted Express, Mongoose or worker modules."""
    for relative_path in RETIRED_NODE_CONSUMERS:
        assert not (ROOT / relative_path).exists(), relative_path


def test_python_domain_contracts_remain_as_the_supported_regression_surfaces() -> None:
    """Python EOS owns forensic, QR, and subscription regression surfaces.

    QR byte compatibility is certified against the retained legacy source
    contract and fixed payload vectors. Merkle and PayShap endpoints remain
    separate authorities and are not described as QR signature parity.
    """
    for relative_path in PYTHON_DOMAIN_CONTRACTS:
        assert (ROOT / relative_path).is_file(), relative_path
    billing_source = (ROOT / "tools/eos/api/billing_router.py").read_text(
        encoding="utf-8"
    )
    assert '@router.post("/merkle/verify"' in billing_source
    assert "async def verify_invoice_chain" in billing_source
    assert '@router.get("/invoices/{invoice_id}/qr"' in billing_source
    assert '@qr_router.get("/verify/{encoded_payload}"' in billing_source
    assert (ROOT / "tools/eos/api/electrum_payshap_completion_router.py").is_file()
    server_source = (ROOT / "tools/eos/api/server.py").read_text(encoding="utf-8")
    assert 'app.include_router(qr_router, prefix="/api")' in server_source
    assert (ROOT / "tools/eos/saas/billing/invoice_qr_legacy_contract.py").is_file()
    assert (ROOT / "tests/unit/test_invoice_qr_legacy_contract.py").is_file()
    assert (ROOT / "tests/unit/test_billing_qr_tenant_boundary.py").is_file()


def test_retirement_policy_distinguishes_node_runtime_from_python_and_audit_history() -> None:
    """Classifications retire code and launch surfaces without deleting evidence."""
    for relative_path in (
        "server/controllers/businessArtifactPdfController.js",
        "server/services/qr/qrGenerator.js",
        "server/config/cron-jobs.yml",
        "services/auth/authService.js",
        "client/server/routes/intelligenceRoutes.js",
        "middleware/auditMiddleware.js",
        "models/validators/ficaValidators.js",
        "algorithms/neural/TemplateNeuralEngine.js",
        "backfillRoles.js",
        "deploy-prod.sh",
        "scripts/wilsy-ai-operator-proof-harness.js",
        "scripts/wilsy-crm-r71a-terminal-evidence-summary-gate.js",
        "scripts/wilsy-r73d-sovereign-search-live-http-smoke-gate.js",
    ):
        assert classify(relative_path) == "RETIRED_NODE_BACKEND", relative_path
        assert not (ROOT / relative_path).exists(), relative_path
    assert classify("tools/eos/api/server.py") == "SOVEREIGN"
    assert classify("server/.babelrc") == "RETIRED_NODE_BACKEND"
    assert classify("tests/unit/qrServices.test.js") == "RETIRED_NODE_BACKEND"
    assert classify("server/manifest.txt") == "RETAIN"
    assert classify("server/scripts/rollback-migration-production.patch") == "RETAIN"
    assert (ROOT / "server/manifest.txt").is_file()
    assert (ROOT / "server/scripts/rollback-migration-production.patch").is_file()
    assert not (ROOT / "server/config/cron-jobs.yml").exists()


def test_historical_migrations_and_python_migration_owners_remain_available() -> None:
    """Migration source is retained as history; active migrations remain Python-owned."""
    for relative_path in RETAINED_NODE_MIGRATION_HISTORY:
        assert (ROOT / relative_path).is_file(), relative_path
        assert classify(relative_path) == "RETAIN", relative_path
    for relative_path in PYTHON_MIGRATION_SURFACES:
        assert (ROOT / relative_path).is_file(), relative_path
    for relative_path in (
        "server/server.js",
        "server/app.js",
        "server/worker.js",
        "server/package.json",
        "server/package-lock.json",
        "server/routes/api.js",
        "server/jobs/scheduler.js",
    ):
        assert not (ROOT / relative_path).exists(), relative_path
    runtime_surfaces = (
        (ROOT / "package.json").read_text(encoding="utf-8"),
        (ROOT / "scripts/start-dev-stack.sh").read_text(encoding="utf-8"),
        (ROOT / "tools/eos/api/server.py").read_text(encoding="utf-8"),
    )
    assert not any("server/scripts/migrate" in surface for surface in runtime_surfaces)


def test_invoice_proof_client_uses_authenticated_python_reference_and_qr_routes() -> None:
    """Merkle checks send a seal reference; QR checks send signed bytes to EOS."""
    router = (ROOT / "tools/eos/api/billing_router.py").read_text(encoding="utf-8")
    component = (
        ROOT / "client/src/components/billing/ForensicProofBlock.jsx"
    ).read_text(encoding="utf-8")
    assert "_BILLING_FORENSIC_REFERENCE_VERIFY_AUTHORIZATION = RequireTenantAuthorization(" in router
    assert "authorization: TenantAuthorizationContext = Depends(" in router
    assert "tenant_id = authorization.tenant_id" in router
    assert "BILLING_PROOF_REFERENCE_CHECKED" in router
    assert "api.post(" in component
    assert "'/billing/merkle/verify'" in component
    assert "{ seal_hash: sealHash }" in component
    assert "`/billing/invoices/${encodeURIComponent(invoiceId)}/qr`" in component
    assert "`/qr/verify/${encodeURIComponent(encodedPayload)}`" in component
    assert "qrVerified" in component
    assert "tenant_id:" not in component


def test_root_tooling_has_no_node_business_dependencies_or_server_launcher() -> None:
    """Frontend/build tooling cannot reinstall a retired business API runtime."""
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    dependencies = set(package.get("dependencies", {})) | set(
        package.get("devDependencies", {})
    )
    assert not dependencies.intersection(FORBIDDEN_DEPENDENCIES)
    assert package["scripts"]["dev"] == "bash scripts/start-dev-stack.sh"
    assert "uvicorn tools.eos.api.server:app" in package["scripts"]["dev:kernel"]
    assert not re.search(r"pm2|server/|node-cron", " ".join(package["scripts"].values()))


def test_removed_node_artifacts_are_classified_as_retired_in_governance_policy() -> None:
    """Policy rules match deleted Node artifacts and separate retained history."""
    policy = json.loads(
        (ROOT / "tools/eos/governance/production_surface_policy.json").read_text(
            encoding="utf-8"
        )
    )
    classes = {
        entry["pattern"]: entry["class"]
        for entry in policy["rules"]
        if "pattern" in entry and "class" in entry
    }
    assert {
        path
        for path, classification in classes.items()
        if classification == "RETIRED_NODE_BACKEND"
    } >= RETIRED_POLICY_PATTERNS


def test_canonical_fastapi_application_mounts_python_forensic_and_pdf_routers() -> None:
    """Python exclusively composes the supported authenticated business APIs."""
    source = (ROOT / "tools/eos/api/server.py").read_text(encoding="utf-8")
    for router in (
        "forensic_merkle_router",
        "artifact_pdf_router",
        "auth_router",
        "global_principal_auth_router",
        "legal_operations_router",
        "tenant_module_workspace_router",
        "unified_my_work_router",
        "attention_router",
    ):
        assert router in source
    assert 'app.include_router(forensic_merkle_router, prefix="/api")' in source
    assert 'app.include_router(artifact_pdf_router, prefix="/api")' in source


def test_frontend_forensic_bridge_has_no_node_fallback_or_root_tenant_default() -> None:
    """The browser cannot revive unauthenticated legacy transport."""
    source = (ROOT / "client/src/services/wilsyForensicMerkleClient.js").read_text(
        encoding="utf-8"
    )
    assert not any(
        value in source
        for value in ("localhost:5050", "127.0.0.1:5050", "wilsy-sovereign-root")
    )
    assert "tools/eos/api/forensic_merkle_router.py" in source


def test_vite_application_api_proxy_uses_canonical_eos_and_test_owned_isolation() -> None:
    """Normal development uses 5173/9095; disposable tests own temporary ports."""
    source = (ROOT / "client/vite.config.js").read_text(encoding="utf-8")
    runner = (ROOT / "tests/e2e/run-browser-cert.mjs").read_text(encoding="utf-8")
    assert "port: 5173" in source
    assert "process.env.WILSY_EOS_DEV_TARGET" not in source
    assert "process.env.WILSY_VITE_PORT" not in source
    targets = re.findall(r"target\s*:\s*['\"](https?://[^'\"]+)['\"]", source)
    assert len(targets) >= 10
    assert set(targets) == {"http://127.0.0.1:9095"}
    assert not any(value in source for value in ("localhost:4000", "127.0.0.1:4000"))
    assert "replaceAll('http://127.0.0.1:9095', eosBaseUrl)" in runner


def test_forensic_ui_never_equates_root_presence_with_verified_chain() -> None:
    """Displayed evidence cannot manufacture institutional verification."""
    source = (
        ROOT / "client/src/components/chrome/WilsyForensicMerkleShowroom.jsx"
    ).read_text(encoding="utf-8")
    assert "chain.verified === true || run.verified === true || status.verified === true" in source
    assert "Boolean(merkleRoot || receiptMerkleRoot)" not in source
    assert "No external framework attestation" in source
    assert "key.includes('LOCAL_APPEND_ONLY_PENDING_WORM')" in source


def test_business_schedulers_and_workers_are_python_owned() -> None:
    """Only explicit Python workers may execute scheduled business work."""
    server = (ROOT / "tools/eos/api/server.py").read_text(encoding="utf-8")
    compose = (ROOT / "docker-compose.prod.yml").read_text(encoding="utf-8")
    assert "run_dunning_scheduler" in server
    assert "run_electrum_payshap_completion_worker" in server
    assert '"tools.eos.runtime.worker_process"' in compose
    assert "pm2" not in compose.lower()
    assert "server/worker" not in compose
    assert (ROOT / "tools/eos/runtime/worker_process.py").is_file()


def test_browser_certifier_and_deployment_never_launch_node_business_runtime() -> None:
    """Frontend Node tooling stays distinct from Python API execution."""
    runner = (ROOT / "tests/e2e/run-browser-cert.mjs").read_text(encoding="utf-8")
    assert "server/server.js" not in runner
    assert "BROWSER_CERT_LEGACY_API_PROXY_FORBIDDEN" in runner
    for filename in ("Dockerfile", "Dockerfile.eos"):
        source = (ROOT / filename).read_text(encoding="utf-8")
        assert '"tools.eos.api.server:app"' in source
        assert "FROM node:" not in source
        assert "npm start" not in source
    assert (ROOT / "server/manifest.txt").is_file()


# ARTIFACT: Python EOS Runtime Exclusivity Certificate
# VERSION: v2.5.0-PYTHON-QR-CONTRACT-AND-ROUTER-CERT
# AUTHORITY BOUNDARY: Repository evidence only; no business mutation or activation.
# TENANT POSTURE: No tenant data is accessed.
# FAIL-CLOSED POSTURE: Any resurrected Node implementation fails certification.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
