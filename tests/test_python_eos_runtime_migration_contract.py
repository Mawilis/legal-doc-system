"""Python-EOS runtime migration contract tests.

TITLE: Python EOS Runtime Routing Migration Contract
VERSION: v2.0.0
AUTHORITY: Wilsy OS Core Governance
EPITOME: Protects route parity as the Vite API surface migrates from the Node BFF
         to canonical Python EOS, retaining Node only for the uncertified PDF port.
TENANT BOUNDARY: Routing only; endpoint authorities remain owned by their services.
AUTHORITY BOUNDARY: No identity, membership, permission, or session authority is created here.
FAIL-CLOSED POSTURE: Unmigrated PDF generation stays explicitly routed to its current owner until parity is certified.
END OF WILSY OS SOVEREIGN ARTIFACT
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VITE_CONFIG = ROOT / "client" / "vite.config.js"
SOURCE = VITE_CONFIG.read_text(encoding="utf-8")


def proxy_block(start_marker: str, end_marker: str) -> str:
    start = SOURCE.index(start_marker)
    end = SOURCE.index(end_marker, start)
    return SOURCE[start:end]


def test_legacy_auth_alias_targets_python_eos_and_preserves_canonical_prefix() -> None:
    auth_block = proxy_block("'/auth': {", "// Kennel invoice lifecycle endpoints")

    assert "target: 'http://localhost:9095'" in auth_block
    assert r"rewrite: (path) => path.replace(/^\/auth(?=\/|$)/, '/api/auth')" in auth_block
    assert "Auth backend unreachable – verify Python EOS on port 9095 is active." in auth_block
    assert "target: 'http://localhost:4000'" not in auth_block


def test_bff_forwarded_python_routes_are_directly_routed_to_eos() -> None:
    expected = (
        ("'/api/business/tenants': {", "'/api/plans': {", "target: 'http://localhost:9095'", r"rewrite: (path) => path.replace(/^\/api\/business\/tenants(?=\/|$)/, '/api/tenants')"),
        ("'/api/plans': {", "'/api/subscriptions': {", "target: 'http://localhost:9095'", None),
        ("'/api/subscriptions': {", "'/api/wilsy-ai/legal-services': {", "target: 'http://localhost:9095'", None),
        ("'/api/wilsy-ai/legal-services': {", "'/api/wilsy-ai/legal-next-actions': {", "target: 'http://localhost:9095'", None),
        ("'/api/wilsy-ai/legal-next-actions': {", "'/billing': {", "target: 'http://localhost:9095'", None),
        ("'/billing': {", "// Node's BFF previously stripped", "target: 'http://localhost:9095'", None),
        ("'/api/billing': {", "// Only explicitly unmigrated routes", "target: 'http://localhost:9095'", r"rewrite: (path) => path.replace(/^\/api(?=\/|$)/, '')"),
    )
    for start, end, target, rewrite in expected:
        block = proxy_block(start, end)
        assert target in block, start
        if rewrite:
            assert rewrite in block, start
        assert "target: 'http://localhost:4000'" not in block, start


def test_only_uncertified_pdf_route_remains_on_node_and_api_fallback_is_eos() -> None:
    pdf_block = proxy_block("'/api/generate/pdf': {", "// These paths were previously forwarded")
    api_block = proxy_block("      '/api': {", "\n    }\n  },\n  resolve:")

    assert "target: 'http://localhost:4000'" in pdf_block
    assert "LEGACY_PDF_RENDERER_UNAVAILABLE" in pdf_block
    assert "target: 'http://localhost:9095'" in api_block
    assert "PYTHON_EOS_UNAVAILABLE" in api_block
    assert "target: 'http://localhost:4000'" not in api_block
