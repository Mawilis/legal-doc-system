"""WILSY OS — Python EOS Runtime Retirement Certificate.

VERSION: v1.1.0-NODE-RESURRECTION-PREVENTION
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Prevent previously retired Node transports and service generators from
returning while preserving Python forensic and PDF route ownership.
ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_python_eos_forensic_runtime_retirement.py
COLLABORATION / OWNERSHIP: EOS runtime, client transport, CI retirement checks.
UPDATE DATE: 2026-11-09.
CHANGELOG: v1.1.0-NODE-RESURRECTION-PREVENTION replaces inspection of the legacy
Express app with required absence; forbids discovered repair generators and
standalone business listeners and executable retired-service package scripts.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT / AUTHORITY BOUNDARY: Read-only repository inspection; no tenant, account,
database, credential, financial execution or real MFA authority.
"""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RETIRED_ENTRYPOINTS = (
    "server/server.js",
    "server/app.js",
    "server/websocket/billingWsServer.js",
    "server/worker-bootstrap/fileWorkers.js",
    "server/scripts/bull-board.js",
    "server/monitoring/prometheusExporter.js",
    "fix_start_scripts.js",
    "repair_billing_syntax.js",
    "services/ledger/fix_connection.js",
    "services/ledger/repair_ledger_service.js",
    "services/ai/aiService.js",
    "services/crypto/cryptoService.js",
    "services/standards/standardsService.js",
)


@pytest.mark.parametrize("relative_path", RETIRED_ENTRYPOINTS)
def test_retired_node_entrypoints_and_generators_remain_absent(relative_path: str):
    """Enforce deletion rather than permitting dormant restartable authority."""
    assert not (ROOT / relative_path).exists(), relative_path


def test_legacy_forensic_router_is_not_registered_or_used_as_auth_bypass():
    """Retained migration routes cannot restore the removed forensic transport."""
    source = (ROOT / "server/routes/api.js").read_text(encoding="utf-8")
    assert "forensicRoutes" not in source
    assert "router.use('/forensics'" not in source
    assert "businessArtifactPdfController" not in source
    assert "generateSovereignArtifactPdf" not in source
    assert "router.post('/generate/pdf'" not in source


def test_canonical_fastapi_application_mounts_python_forensic_and_pdf_routers():
    """Python owns authenticated forensic and PDF HTTP composition."""
    source = (ROOT / "tools/eos/api/server.py").read_text(encoding="utf-8")
    assert "from .forensic_merkle_router import router as forensic_merkle_router" in source
    assert 'app.include_router(forensic_merkle_router, prefix="/api")' in source
    assert 'app.include_router(artifact_pdf_router, prefix="/api")' in source


def test_frontend_forensic_bridge_has_no_node_backend_fallback_or_root_tenant_default():
    """Browser presentation cannot fall back to an unauthenticated Node port."""
    source = (ROOT / "client/src/services/wilsyForensicMerkleClient.js").read_text(encoding="utf-8")
    assert "localhost:5050" not in source
    assert "127.0.0.1:5050" not in source
    assert "wilsy-sovereign-root" not in source
    assert "tools/eos/api/forensic_merkle_router.py" in source


def test_vite_application_api_proxy_targets_python_eos_only():
    """Keep the frontend build runtime separate from backend execution authority."""
    source = (ROOT / "client/vite.config.js").read_text(encoding="utf-8")
    assert "target: 'http://127.0.0.1:9095'" in source
    assert "localhost:4000" not in source
    assert "127.0.0.1:4000" not in source


def test_forensic_ui_never_equates_root_presence_with_verified_chain():
    """A displayed Merkle root cannot manufacture a verified-chain claim."""
    source = (ROOT / "client/src/components/chrome/WilsyForensicMerkleShowroom.jsx").read_text(encoding="utf-8")
    assert "chain.verified === true || run.verified === true || status.verified === true" in source
    assert "Boolean(merkleRoot || receiptMerkleRoot)" not in source
    assert "No external framework attestation" in source
    assert "key.includes('LOCAL_APPEND_ONLY_PENDING_WORM')" in source
    assert "return 'Append-only seal pending'" in source


def test_pm2_configs_have_no_business_runtime_registrations():
    """Prevent repository PM2 configuration from registering removed APIs."""
    for path in ("server/pm2.config.js", "server/pm2.config.mjs"):
        source = (ROOT / path).read_text(encoding="utf-8")
        assert "apps: []" in source
        assert "script:" not in source


@pytest.mark.parametrize("service", ("auth", "standards", "billing", "ledger", "ai", "crypto"))
def test_retired_service_packages_cannot_launch_node_apis(service: str):
    """Retain dependency metadata without an executable service entrypoint."""
    package = json.loads((ROOT / "services" / service / "package.json").read_text(encoding="utf-8"))
    assert "main" not in package
    assert not any(name.startswith(("start", "dev", "serve")) for name in package.get("scripts", {}))


def test_browser_certifier_never_launches_a_node_bff():
    """Disposable browser acceptance must exercise the Python API transport."""
    source = (ROOT / "tests/e2e/run-browser-cert.mjs").read_text(encoding="utf-8")
    assert "server/server.js" not in source
    assert "serverDirectory" not in source
    assert "BROWSER_CERT_LEGACY_API_PROXY_FORBIDDEN" in source


# SOVEREIGN ARTIFACT SEAL
# ARTIFACT: Python EOS Runtime Retirement Certificate
# VERSION: v1.1.0-NODE-RESURRECTION-PREVENTION
# AUTHORITY BOUNDARY: Repository regression evidence only.
# TENANT POSTURE: No persistence or identity mutation.
# FAIL-CLOSED POSTURE: Reintroduced entrypoints fail certification.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
