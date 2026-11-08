"""Static guard for the repository-defined EOS runtime database ownership graph."""
from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLS_EOS = ROOT / "tools" / "eos"
NON_RUNTIME_PREFIXES = (
    "tools/eos/scripts/",
    "tools/eos/tests/",
    "tools/eos/docs/",
    "tools/eos/documentation/",
    "tools/eos/benchmark/",
)
NON_RUNTIME_FILES = {
    "tools/eos/__init__.py",
    "tools/eos/mock_kennel_server.py",
    "tools/eos/test_phase_integration.py",
    "tools/eos/run_aggregator_test.py",
    "tools/eos/run_dashboard_live_test.py",
    "tools/eos/run_scheduler_playbook.py",
    "tools/eos/ws_test_client.py",
    "tools/eos/packet_runner.py",
    "tools/eos/reliability/high_availability/heartbeat.py",
}
CANONICAL_CONNECTOR = "tools/eos/kernel/db.py"
ISOLATED_AUDIT_SINK = (
    "tools/eos/legal_operations/service/"
    "legal_evidence_provider_readonly_reconciliation_runtime.py"
)
OPERATOR_ONLY_CONNECTIONS = {
    "tools/eos/scripts/update_platform_tenant.py",
    "tools/eos/scripts/update_platform_tenant_direct.py",
    "tools/eos/tenancy/retire_legacy_root_aliases.py",
    "tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_audit_provisioner.py",
    "tools/eos/mongodb/read_only_index_verifier.py",
}


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _constructs_mongo_client(tree: ast.AST) -> bool:
    constructor_names = {"MongoClient", "AsyncMongoClient", "AsyncIOMotorClient"}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in {"pymongo", "motor.motor_asyncio"}:
            for imported in node.names:
                if imported.name in constructor_names:
                    constructor_names.add(imported.asname or imported.name)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Name) and function.id in constructor_names:
            return True
        if isinstance(function, ast.Attribute) and function.attr in {
            "MongoClient",
            "AsyncMongoClient",
            "AsyncIOMotorClient",
        }:
            return True
    return False


def test_mongo_client_ast_scan_detects_aliased_sync_and_async_constructors():
    direct_alias = ast.parse(
        "from pymongo import MongoClient as BusinessClient\n"
        "client = BusinessClient(uri)\n"
    )
    motor_alias = ast.parse(
        "from motor.motor_asyncio import AsyncIOMotorClient as AsyncBusinessClient\n"
        "client = AsyncBusinessClient(uri)\n"
    )
    module_attribute = ast.parse(
        "import pymongo\n"
        "client = pymongo.MongoClient(uri)\n"
    )
    assert _constructs_mongo_client(direct_alias)
    assert _constructs_mongo_client(motor_alias)
    assert _constructs_mongo_client(module_attribute)


def test_runtime_mongo_client_construction_is_confined_to_kernel_and_isolated_audit_sink():
    runtime_calls = set()
    for path in TOOLS_EOS.rglob("*.py"):
        relative = _relative(path)
        if (
            relative in NON_RUNTIME_FILES
            or relative in OPERATOR_ONLY_CONNECTIONS
            or relative.startswith(NON_RUNTIME_PREFIXES)
        ):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        if _constructs_mongo_client(tree):
            runtime_calls.add(relative)

    assert runtime_calls == {CANONICAL_CONNECTOR, ISOLATED_AUDIT_SINK}

    audit_source = (ROOT / ISOLATED_AUDIT_SINK).read_text(encoding="utf-8")
    assert 'AUDIT_URI_ENV = "WILSY_LEGAL_EVIDENCE_RECONCILIATION_AUDIT_MONGODB_URI"' in audit_source
    assert "require_distinct_mongo_deployments(business_uri, audit_uri)" in audit_source
    assert "require_tls_mongodb_uri(audit_uri)" in audit_source
    assert "audit_database.client is mongo_database.client" in audit_source

    audit_provisioner = (ROOT / "tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_audit_provisioner.py").read_text(encoding="utf-8")
    assert "def main()" in audit_provisioner
    assert 'if __name__ == "__main__":' in audit_provisioner
    assert "client.close()" in audit_provisioner

    index_verifier = (ROOT / "tools/eos/mongodb/read_only_index_verifier.py").read_text(encoding="utf-8")
    assert "def main()" in index_verifier
    assert 'if __name__ == "__main__":' in index_verifier
    assert "mutations_performed\": 0" in index_verifier

    connector = (ROOT / CANONICAL_CONNECTOR).read_text(encoding="utf-8")
    assert "MongoClient(" in connector
    assert "def resolve_mongo_uri" in connector
    assert 'os.getenv("MONGODB_URI")' in connector


def test_business_registry_consumers_use_kernel_or_caller_owned_same_client_graph():
    kernel_owned = (
        "tools/eos/saas/tenancy/tenant_registry.py",
        "tools/eos/saas/billing/plan_registry.py",
        "tools/eos/saas/billing/subscription_registry.py",
        "tools/eos/saas/employee/employee_registry.py",
        "tools/eos/kennel/evidence/payshap_evidence_store.py",
        "tools/eos/api/owner_commercial_workspace_router.py",
        "tools/eos/api/payshap_webhook_router.py",
        "tools/eos/api/billing_router.py",
        "tools/eos/saas/billing/order_number_service.py",
        "tools/eos/saas/billing/financial_approval_aggregator.py",
        "tools/eos/saas/auth/password_reset_service.py",
        "tools/eos/saas/auth/password_recovery_contact_verification_service.py",
        "tools/eos/saas/billing/platform_billing_release_authorization_issuance.py",
    )
    for relative in kernel_owned:
        source = (ROOT / relative).read_text(encoding="utf-8")
        assert any(
            marker in source
            for marker in ("get_database", "get_client", "kernel_db")
        ), f"{relative} no longer exposes the canonical kernel DB binding"

    injected_execution = (
        ROOT / "tools/eos/saas/billing/"
        "platform_billing_financial_execution_request_issuance.py"
    ).read_text(encoding="utf-8")
    assert "client: MongoClient, database: Any" in injected_execution
    assert 'getattr(database, "client", None) is not client' in injected_execution
    assert 'getattr(session, "in_transaction", False) is not True' in injected_execution

    order_numbers = (ROOT / "tools/eos/saas/billing/order_number_service.py").read_text(encoding="utf-8")
    assert "ORDER_NUMBER_CANONICAL_DATABASE_UNAVAILABLE" in order_numbers
    assert "ORDER_NUMBER_RUNTIME_REBIND_REQUIRED" in order_numbers

    approvals = (ROOT / "tools/eos/saas/billing/financial_approval_aggregator.py").read_text(encoding="utf-8")
    assert "FINANCIAL_APPROVAL_AGGREGATOR_MIXED_CLIENT_GRAPH" in approvals


def test_legacy_node_backend_is_not_a_supported_runtime_entrypoint():
    bff = (ROOT / "server/server.js").read_text(encoding="utf-8")
    assert "Legacy Node BFF runtime is retired" in bff
    assert "process.exitCode = 1" in bff

    pm2 = (ROOT / "server/ecosystem.config.js").read_text(encoding="utf-8")
    assert "apps: []" in pm2
    assert "script:" not in pm2

    deploy = (ROOT / "server/deploy.sh").read_text(encoding="utf-8")
    assert "legacy Node deployment path has been retired" in deploy
    assert "exit 1" in deploy

    server_package = json.loads((ROOT / "server/package.json").read_text(encoding="utf-8"))
    assert not {"start", "dev", "predev"}.intersection(server_package["scripts"])
    assert "main" not in server_package

    for dockerfile in ("server/Dockerfile", "server/Dockerfile.worker"):
        source = (ROOT / dockerfile).read_text(encoding="utf-8")
        assert "FROM scratch" in source
        assert "LEGACY_NODE_BACKEND_RETIRED" in source
        assert "FROM node:" not in source.lower()

    dev_stack = (ROOT / "scripts/start-dev-stack.sh").read_text(encoding="utf-8")
    assert "uvicorn tools.eos.api.server:app" in dev_stack
    assert "server/app.js" not in dev_stack
    assert "server/jobs/scheduler.js" not in dev_stack

    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    assert package["scripts"]["dev"] == "bash scripts/start-dev-stack.sh"
    assert "uvicorn tools.eos.api.server:app" in package["scripts"]["dev:kernel"]
    assert "scheduler" not in " ".join(package["scripts"].values()).lower()
