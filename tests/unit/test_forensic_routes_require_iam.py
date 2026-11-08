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
