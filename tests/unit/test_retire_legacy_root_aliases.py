"""EOS certificate for the single canonical WILSY tenant boundary."""
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
    root = Path(".")
    tenant_guard = (root / "server/middleware/tenantGuard.js").read_text(encoding="utf-8")
    tenant_context = (root / "server/middleware/tenantContext.js").read_text(encoding="utf-8")
    tenant_resolver = (root / "server/middleware/tenantResolver.js").read_text(encoding="utf-8")
    tenant_scope = (root / "server/middleware/tenantScope.js").read_text(encoding="utf-8")
    api_routes = (root / "server/routes/api.js").read_text(encoding="utf-8")
    auth_controller = (root / "server/controllers/authController.js").read_text(encoding="utf-8")
    auth_service = (root / "services/auth/authService.js").read_text(encoding="utf-8")
    tenant_middleware = (root / "server/middleware/tenant.middleware.js").read_text(encoding="utf-8")
    node_routes = (root / "server/routes/nodeRoutes.js").read_text(encoding="utf-8")

    assert "SOVEREIGN_BYPASS_IDS" not in tenant_guard
    assert "tenantId = 'GLOBAL_ROOT'" not in tenant_guard
    assert "tenantId = 'wilsy-sovereign-root'" not in tenant_guard
    assert "TENANT_CONTEXT_REQUIRED" in tenant_guard
    assert "ROOT_DB_FALLBACK" not in tenant_context
    assert "Re-anchoring to Sovereign Root" not in tenant_context
    assert "TENANT_NOT_FOUND_OR_INACTIVE" in tenant_context
    assert "TENANT_DATABASE_UNAVAILABLE" in tenant_context
    assert "tenant_id: tenantId" in tenant_context
    assert "return store?.tenantId || null" in tenant_context
    assert "WILSYTENANT-4CD2FZ4O" in tenant_resolver
    assert "TENANT_NOT_AUTHORIZED" in tenant_resolver
    assert "retiredAliases" not in tenant_resolver
    assert "req.tenantId || req.context?.tenantId || 'GLOBAL_ROOT'" not in tenant_scope
    assert "'GLOBAL_ROOT'" not in api_routes
    assert "wilsy-sovereign-root" not in auth_controller
    assert "WILSY_ROOT" not in auth_service.split("const resolvedTenantId", 1)[0]
    assert "tenantId || 'wilsy-sovereign-root'" not in tenant_middleware
    assert "req.tenantId !== 'WILSY_ROOT'" not in node_routes


def test_retirement_uses_canonical_kernel_uri_resolution() -> None:
    source = Path("tools/eos/tenancy/retire_legacy_root_aliases.py").read_text(encoding="utf-8")
    assert "from tools.eos.kernel.db import resolve_mongo_uri" in source
    assert "uri = resolve_mongo_uri()" in source
    assert 'uri = os.getenv("MONGODB_URI")' not in source
