"""Regression checks for forensic API authentication and tenant-isolation composition."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_forensics_is_not_in_the_global_integrity_shield_bypass_allowlist() -> None:
    source = (ROOT / "server/middleware/DNA_PASS_FIX.js").read_text(encoding="utf-8")
    assert "'forensics'," not in source


def test_forensic_router_is_mounted_only_after_authentication_and_tenant_isolation() -> None:
    source = (ROOT / "server/routes/api.js").read_text(encoding="utf-8")
    auth = source.index("router.use(requireSovereignAuth);")
    tenant_guard = source.index("router.use(tenantGuard);")
    tenant_isolation = source.index("router.use(enforceTenantIsolation);")
    forensic_mount = source.index("router.use('/forensics', forensics);")

    assert auth < tenant_guard < tenant_isolation < forensic_mount
    assert source.count("router.use('/forensics', forensics);") == 1


def test_application_does_not_mount_forensics_around_the_protected_api_nexus() -> None:
    source = (ROOT / "server/app.js").read_text(encoding="utf-8")
    assert "import forensicRoutes from './routes/forensicRoutes.js';" not in source
    assert "app.use('/api/forensics', forensicRoutes);" not in source
    assert "app.use('/api', routes);" in source


def test_forensic_handlers_use_only_the_authenticated_tenant_scope() -> None:
    source = (ROOT / "server/routes/forensicRoutes.js").read_text(encoding="utf-8")

    assert "router.use(requireForensicTenantScope);" in source
    assert "req.forensicTenantId" in source
    assert "normalizeTenantId(" not in source
    assert "req.query.tenantId ||" not in source
    assert "req.body?.tenantId ||" not in source
    assert "req.headers['x-tenant-id'] ||" not in source
    assert "$in: aliases" not in source
    assert "GLOBAL_ROOT', 'WILSY_ROOT', 'WILSY_GLOBAL_ROOT" not in source
    assert "listLocalAnchors({\n    tenantId: req.forensicTenantId," in source


def test_local_forensic_anchors_are_filtered_by_exact_authenticated_tenant() -> None:
    source = (ROOT / "server/services/ForensicMerkleAuditor.js").read_text(encoding="utf-8")

    assert "async listLocalAnchors({ tenantId, limit = 20 } = {})" in source
    assert "FORENSIC_TENANT_SCOPE_REQUIRED" in source
    assert ".filter((anchor) => anchor.tenantId === authenticatedTenantId)" in source


def test_forensic_chain_reads_do_not_merge_legacy_root_aliases() -> None:
    source = (ROOT / "server/services/ForensicMerkleAuditor.js").read_text(encoding="utf-8")

    assert "buildTenantAliases" not in source
    assert "ForensicLog.find({ tenantId: authenticatedTenantId })" in source
    assert "$in: aliases" not in source


def test_forensic_routes_do_not_claim_unverified_assets_or_vaults_are_intact() -> None:
    source = (ROOT / "server/routes/forensicRoutes.js").read_text(encoding="utf-8")

    assert "integrityStatus: 'UNVERIFIED'" in source
    assert "ASSET_INTEGRITY_VERIFIER_UNAVAILABLE" in source
    assert "integrityStatus: 'VERIFIED_INTACT'" not in source
    assert "status: 'VAULT_STATUS_UNVERIFIED'" in source
    assert "VAULT_STATUS_SOURCE_UNAVAILABLE" in source
    assert "status: 'VAULT_ANCHORED'" not in source


def test_forensic_status_route_omits_global_paths_and_last_run_payloads() -> None:
    source = (ROOT / "server/routes/forensicRoutes.js").read_text(encoding="utf-8")
    status_route = source.split("router.get('/merkle-auditor/status'", 1)[1].split("});", 1)[0]

    assert "tenantId: req.forensicTenantId" in status_route
    assert "localAnchorPath" not in status_route
    assert "lastRun" not in status_route
    assert "json(forensicMerkleAuditor.getStatus())" not in status_route
