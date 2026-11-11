"""WILSY OS Canonical Tenant Alias Retirement Certificate.
TITLE: Canonical Tenant and Physical Node Retirement
VERSION: v1.1.1-PYTHON-TENANT-AUTHORITY-ONLY-SOVEREIGN-METADATA
AUTHORITY: Wilsy OS Core Governance
EPITOME: Preserves exact dry-run/transaction tenant protections and rejects Node fallback resurrection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_retire_legacy_root_aliases.py
COLLABORATION / OWNERSHIP: EOS tenancy and authentication certificate owners.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG: v1.1.1-PYTHON-TENANT-AUTHORITY-ONLY-SOVEREIGN-METADATA completes privacy posture without changing tenant retirement assertions.
CHANGELOG: v1.1.0-PYTHON-TENANT-AUTHORITY-ONLY replaces retained Node middleware assertions with physical absence and canonical Python tenant gates; transaction and Founder invariants remain unchanged.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Read-only source inspection; no tenant records or credentials are read.
TENANT BOUNDARY: Synthetic tenant assertions only; no tenant data is mutated.
AUTHORITY BOUNDARY: Retirement regression evidence only; no migration or runtime authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

import ast
from pathlib import Path

from tools.eos.tenancy import retire_legacy_root_aliases as retirement


def test_exact_obsolete_allowlist_and_canonical_tenant() -> None:
    assert retirement.ALIASES == (
        "WILSY_ROOT",
        "MASTER",
        "WILSY_MASTER",
        "GLOBAL_ROOT",
        "WILSY_GLOBAL_ROOT",
    )
    assert retirement.CANONICAL_TENANT_ID == "WILSYTENANT-4CD2FZ4O"


def test_retirement_is_transactional_and_deletes_only_exact_registry_aliases() -> None:
    source = Path("tools/eos/tenancy/retire_legacy_root_aliases.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert "with_transaction" in attributes
    assert "delete_many" in attributes
    assert "insert_one" not in attributes
    assert "update_one" not in attributes
    assert "drop" not in attributes
    assert 'database["tenant_configs"].delete_many' in source
    assert "database.list_collection_names()" not in source
    assert "_preserved_inventory" not in source
    assert "sovereign_nodes" not in source


def test_retirement_mutates_no_pre_iam_collections() -> None:
    source = Path("tools/eos/tenancy/retire_legacy_root_aliases.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    mutation_targets = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in {"update_one", "update_many", "delete_one", "delete_many"}:
                mutation_targets.append(ast.unparse(node.func.value))
    assert mutation_targets == ["database['tenant_configs']"]


def test_founder_subscription_entitlement_and_authority_are_pre_and_post_invariants() -> None:
    source = Path("tools/eos/tenancy/retire_legacy_root_aliases.py").read_text(encoding="utf-8")
    assert 'database["tenants"]' in source
    assert 'database["subscriptions"]' in source
    assert 'database["tenant_product_entitlement_current"]' in source
    assert 'database["tenant_product_entitlement_history"]' in source
    assert 'database["tenant_authorization_decision_evidence"]' in source
    assert "FOUNDER_INVARIANT_CHANGED_DURING_RETIREMENT" in source


def test_dry_run_is_default_and_apply_is_explicit() -> None:
    source = Path("tools/eos/tenancy/retire_legacy_root_aliases.py").read_text(encoding="utf-8")
    assert 'parser.add_argument("--apply", action="store_true"' in source
    assert "if not apply:" in source
    assert '"legacy_collections_scanned": 0' in source


def test_runtime_tenant_boundaries_have_no_synthetic_root_fallbacks() -> None:
    """Only the Python tenant authorities survive; no Node fallback remains."""
    root = Path(".")
    for path in ("server/middleware/tenantGuard.js", "server/middleware/tenantContext.js", "server/routes/api.js", "server/controllers/authController.js", "services/auth/authService.js"):
        assert not (root / path).exists()
    source = (root / "tools/eos/saas/auth/auth_registry.py").read_text()
    assert "AUTH_TENANT_CANONICAL_INVALID" in source
    assert "_require_canonical_tenant" in source
    assert "DEFAULT_TENANT" not in source


def test_no_node_root_id_backfill_or_membership_inference_survives() -> None:
    """Removal cannot be replaced with a synthetic tenant fallback in EOS."""
    root = Path(".")
    source = (root / "tools/eos/auth/tenant_membership_repository.py").read_text()
    assert '"principal_id": principal_id, "tenant_id": tenant_id' in source
    for path in ("backfillRoles.js", "reset_admin.js", "server/middleware/tenant.middleware.js"):
        assert not (root / path).exists()

# ARTIFACT: Canonical Tenant Alias Retirement Certificate
# VERSION: v1.1.1-PYTHON-TENANT-AUTHORITY-ONLY-SOVEREIGN-METADATA
# AUTHORITY BOUNDARY: Offline source certification, no migration authority.
# TENANT POSTURE: Founder and exact tenant protections remain mandatory.
# FAIL-CLOSED POSTURE: No Node or synthetic root authority.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
