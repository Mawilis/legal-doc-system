from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_legacy_express_forensic_router_is_not_registered_or_used_as_auth_bypass():
    app_source = (ROOT / "server/app.js").read_text(encoding="utf-8")
    api_source = (ROOT / "server/routes/api.js").read_text(encoding="utf-8")

    assert "forensicRoutes" not in app_source
    assert "forensicRoutes" not in api_source
    assert "isWilsyPublicForensicGatewayPath" not in app_source
    assert "app.use('/api/forensics'" not in app_source
    assert "router.use('/forensics'" not in api_source


def test_canonical_fastapi_application_mounts_python_forensic_router():
    source = (ROOT / "tools/eos/api/server.py").read_text(encoding="utf-8")
    assert "from .forensic_merkle_router import router as forensic_merkle_router" in source
    assert 'app.include_router(forensic_merkle_router, prefix="/api")' in source


def test_frontend_forensic_bridge_has_no_node_backend_fallback_or_root_tenant_default():
    source = (ROOT / "client/src/services/wilsyForensicMerkleClient.js").read_text(encoding="utf-8")
    assert "localhost:5050" not in source
    assert "127.0.0.1:5050" not in source
    assert "wilsy-sovereign-root" not in source
    assert "tools/eos/api/forensic_merkle_router.py" in source


def test_vite_application_api_proxy_targets_python_eos_only():
    source = (ROOT / "client/vite.config.js").read_text(encoding="utf-8")
    assert "target: 'http://127.0.0.1:9095'" in source
    assert "localhost:4000" not in source
    assert "127.0.0.1:4000" not in source


def test_forensic_ui_never_equates_root_presence_with_verified_chain():
    source = (ROOT / "client/src/components/chrome/WilsyForensicMerkleShowroom.jsx").read_text(encoding="utf-8")
    assert "chain.verified === true || run.verified === true || status.verified === true" in source
    assert "Boolean(merkleRoot || receiptMerkleRoot)" not in source
    assert "No external framework attestation" in source
    assert "'LOCAL_APPEND_ONLY_PENDING_WORM'" not in source
