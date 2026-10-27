"""Python-EOS runtime migration contract tests.

TITLE: Legacy Authentication Alias Routing Contract
VERSION: v1.0.0
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves the legacy browser /auth alias reaches canonical Python EOS
         authentication without changing the still-required general API BFF.
TENANT BOUNDARY: Routing only; authentication and tenant authority remain in EOS.
AUTHORITY BOUNDARY: No identity, membership, permission, or session authority is created here.
FAIL-CLOSED POSTURE: Route migration is accepted only when the canonical target and path rewrite are explicit.
END OF WILSY OS SOVEREIGN ARTIFACT
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VITE_CONFIG = ROOT / "client" / "vite.config.js"


def test_legacy_auth_alias_targets_python_eos_and_preserves_canonical_prefix() -> None:
    source = VITE_CONFIG.read_text(encoding="utf-8")
    start = source.index("'/auth': {")
    end = source.index("// Kennel invoice lifecycle endpoints", start)
    auth_block = source[start:end]

    assert "target: 'http://localhost:9095'" in auth_block
    assert "rewrite: (path) => path.replace(/^\\/auth(?=\\/|$)/, '/api/auth')" in auth_block
    assert "Auth backend unreachable – verify Python EOS on port 9095 is active." in auth_block
    assert "target: 'http://localhost:4000'" not in auth_block


def test_general_api_fallback_is_not_retargeted_before_route_parity() -> None:
    source = VITE_CONFIG.read_text(encoding="utf-8")
    start = source.index("      '/api': {")
    end = source.index("\n      }", start)
    api_block = source[start:end]

    # The broader Node-owned route set is not yet migrated. Keep the fallback
    # intact until every route has a certified Python-EOS equivalent.
    assert "target: 'http://localhost:4000'" in api_block
