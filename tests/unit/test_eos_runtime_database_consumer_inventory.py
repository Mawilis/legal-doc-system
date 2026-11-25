"""WILSY OS EOS Runtime Database Ownership Certificate.
TITLE: Python Runtime Database Ownership
VERSION: v1.4.8-MWT12-EXACT-RECOVERY-OPERATOR-CLASSIFICATION
CHANGELOG: v1.4.8-MWT12-EXACT-RECOVERY-OPERATOR-CLASSIFICATION classifies two separately authenticated
MW-T12 CLI-only recovery utilities as non-runtime constructors only with
explicit entrypoint, ephemeral localhost Mongo and synthetic Atlas TLS/read
bounds. New unclassified Mongo clients still fail the runtime ownership test.
CHANGELOG: v1.4.7-MWT12-LOOPBACK-OPERATOR-CLASSIFICATION records the
single local MW-T12 synthetic-replica recovery operator as non-runtime only
when its explicit CLI main guard, loopback binding, process ownership and
production denial remain present. The two-client runtime exclusivity assertion
is unchanged.
CHANGELOG: v1.4.6-EXACT-INDEX-OPERATOR-CLASSIFICATION classifies three explicitly guarded index-provisioning CLI tools separately from runtime Mongo clients and asserts their main guards.
CHANGELOG: v1.4.5-EXACT-FOUNDER-OPERATOR-ENTRYPOINT certifies the
 existing _main() guarded operator entrypoint rather than incorrectly
 requiring an unimplemented main() function; classification remains strict.
CHANGELOG: v1.4.4-EXPLICIT-FOUNDER-CLI-CLASSIFICATION categorizes
 the separately authorized, __main__-guarded development Founder admission
 operator as operator-only rather than a long-running EOS database consumer;
 this does not authorize runtime use or weaken canonical client ownership.
CHANGELOG: v1.4.3-PYTHON-RETIRED-K8S-WORKLOAD-ABSENCE asserts deployment, service, ingress, predictive deployment, and Kustomize workload manifests stay absent.
CHANGELOG: v1.4.2-PYTHON-RETIRED-KUBERNETES-MANIFEST-ABSENCE asserts the retired server/k8s workload directory stays absent.
CHANGELOG: v1.4.1-PYTHON-ENTRYPOINT-COMPLETE-SOVEREIGN-METADATA completes artifact privacy and authority posture without changing runtime ownership assertions.
CHANGELOG: v1.4.0-PYTHON-ENTRYPOINT-COMPLETE-CLASSIFICATION — verifies retained migration history, Python-owned migration surfaces, and complete retired Node entrypoint/tool classification.
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves Kernel-owned persistence and physical Node backend retirement.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_eos_runtime_database_consumer_inventory.py
COLLABORATION / OWNERSHIP: Kernel DB, registry and runtime certification owners.
CERTIFICATION / UPDATE DATE: 2026-11-24
CHANGELOG: v1.1.0-PHYSICAL-NODE-RETIREMENT replaces obsolete retained-file assertions with required absence; database ownership assertions remain intact.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Repository blob inspection only; no live records or credentials are read.
TENANT BOUNDARY: No tenant records or tenant authority are accessed.
AUTHORITY BOUNDARY: Repository ownership evidence only; no runtime or business authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

from tools.eos.governance.repository_integrity_guard import classify


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
    "tools/eos/auth/founder_development_admission.py",
    "tools/eos/ops/provision_atlas_company_document_indexes.py",
    "tools/eos/ops/provision_atlas_strategy_project_link_indexes.py",
    "tools/eos/ops/provision_local_strategy_project_link_indexes.py",
    "tools/eos/ops/mw_t12_local_eos_recovery.py",
    "tools/eos/ops/mw_t12_image_rollback_rehearsal.py",
    "tools/eos/ops/mw_t12_runtime_readiness.py",
}
LEGACY_MIGRATION_HISTORY = (
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
PYTHON_MIGRATION_OWNERS = (
    "tools/eos/saas/auth/migrations/refresh_token_tenant_backfill.py",
    "tools/eos/saas/auth/migrations/refresh_token_indexes.py",
    "tools/eos/saas/auth/migrations/reconcile_legacy_principal_authority.py",
    "tools/eos/saas/auth/migrations/reconcile_legacy_super_admin_tenant.py",
    "tools/eos/saas/billing/migrations/tenant_inbound_provider_credential_security_authority_index_migration.py",
    "tools/eos/saas/billing/migrations/tenant_inbound_merchant_configuration_lifecycle_idempotency_projection.py",
)


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
    # Explicit index-provisioning operators are not long-running EOS consumers.
    # Keep this narrow: assert each approved exception remains CLI guarded.
    for relative in (
        "tools/eos/ops/provision_atlas_company_document_indexes.py",
        "tools/eos/ops/provision_atlas_strategy_project_link_indexes.py",
        "tools/eos/ops/provision_local_strategy_project_link_indexes.py",
    ):
        tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"), filename=relative)
        main_functions = [node for node in tree.body
                          if isinstance(node, ast.FunctionDef) and node.name == "main"]
        assert len(main_functions) == 1, relative
        guards = [node for node in tree.body if isinstance(node, ast.If)
                  and isinstance(node.test, ast.Compare)
                  and isinstance(node.test.left, ast.Name)
                  and node.test.left.id == "__name__"
                  and len(node.test.comparators) == 1
                  and isinstance(node.test.comparators[0], ast.Constant)
                  and node.test.comparators[0].value == "__main__"]
        assert len(guards) == 1, relative
        assert any(isinstance(node, ast.Call)
                   and isinstance(node.func, ast.Name)
                   and node.func.id == "main"
                   for node in ast.walk(guards[0])), relative
    # MW-T12 owns an ephemeral loopback mongod solely as an explicit CLI
    # browser-certification operator; it never runs as an EOS service.
    # Do not permit arbitrary clients through this narrow exception.
    recovery_path = ROOT / "tools/eos/ops/mw_t12_local_eos_recovery.py"
    recovery_tree = ast.parse(recovery_path.read_text(encoding="utf-8"))
    recovery_source = recovery_path.read_text(encoding="utf-8")
    recovery_functions = {
        node.name: node for node in recovery_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert {"main", "_guard", "_wait_primary", "_stop_owned", "run"} <= recovery_functions.keys()
    recovery_guards = [
        node for node in recovery_tree.body
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.Compare)
        and isinstance(node.test.left, ast.Name)
        and node.test.left.id == "__name__"
        and len(node.test.comparators) == 1
        and isinstance(node.test.comparators[0], ast.Constant)
        and node.test.comparators[0].value == "__main__"
    ]
    assert len(recovery_guards) == 1
    assert any(
        isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        and node.func.id == "main"
        for node in ast.walk(recovery_guards[0])
    )
    assert _constructs_mongo_client(recovery_functions["_wait_primary"])
    assert all(
        not _constructs_mongo_client(node)
        for name, node in recovery_functions.items() if name != "_wait_primary"
    )
    assert 'connect_uri = f"mongodb://127.0.0.1:{port}/?directConnection=true"' in recovery_source
    assert '"--bind_ip", "127.0.0.1"' in recovery_source
    assert '"PRODUCTION_ENVIRONMENT_FORBIDDEN"' in recovery_source
    assert 'for key in ("ENV", "WILSY_ENV")' in recovery_source
    assert 'group.add_argument("--run", action="store_true")' in recovery_source
    assert 'group.add_argument("--check", action="store_true")' in recovery_source
    assert 'process = subprocess.Popen(' in recovery_source
    assert '_stop_owned(process)' in recovery_source

    # These two MW-T12 tools are explicit operator-only processes, never
    # authoritative runtime MongoDB consumers. Their admission is narrow:
    # future additional constructors elsewhere still break the set assertion.
    for relative, required_symbols in (
        ("tools/eos/ops/mw_t12_image_rollback_rehearsal.py",
         ("def main(", "def _wait_mongo(", "def _local_database_uri(",
          'f"mongodb://127.0.0.1:', "--rehearse",
          "client.close()", "IMAGE_MONGO_PRIMARY_UNVERIFIED")),
        ("tools/eos/ops/mw_t12_runtime_readiness.py",
         ("def main(", "def verify_scoped_test_database(",
          'TEST_ATLAS_HOST = "legal-doc-test.xmlpwmq.mongodb.net"',
          "SYNTHETIC_DB", "tlsAllowInvalidCertificates=False",
          "tlsAllowInvalidHostnames=False", "--verify-scoped-database",
          "ATLAS_ECS_ROLLBACK_CERTIFIED=FALSE")),
    ):
        source = (ROOT / relative).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=relative)
        functions = {node.name for node in tree.body
                     if isinstance(node, ast.FunctionDef)}
        assert "main" in functions, relative
        guards = [
            node for node in tree.body
            if isinstance(node, ast.If)
            and isinstance(node.test, ast.Compare)
            and isinstance(node.test.left, ast.Name)
            and node.test.left.id == "__name__"
            and len(node.test.comparators) == 1
            and isinstance(node.test.comparators[0], ast.Constant)
            and node.test.comparators[0].value == "__main__"
        ]
        assert len(guards) == 1, relative
        assert any(isinstance(node, ast.Call)
                   and isinstance(node.func, ast.Name)
                   and node.func.id == "main"
                   for node in ast.walk(guards[0])), relative
        assert _constructs_mongo_client(tree), relative
        for symbol in required_symbols:
            assert symbol in source, (relative, symbol)

    founder_cli = (ROOT / "tools/eos/auth/founder_development_admission.py").read_text(encoding="utf-8")
    assert 'if __name__ == "__main__":' in founder_cli
    assert "def _main()" in founder_cli
    assert "raise SystemExit(_main())" in founder_cli
    assert "MongoClient(" in founder_cli

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
    """Physical absence is required; inert compatibility files are obsolete."""
    for relative in (
        "server/server.js",
        "server/app.js",
        "server/worker.js",
        "server/jobs/scheduler.js",
        "server/package.json",
        "server/package-lock.json",
        "server/pm2.config.js",
        "server/pm2.config.mjs",
        "server/Dockerfile",
        "server/Dockerfile.worker",
        "server/config/cron-jobs.yml",
        "services/auth/package.json",
        "services/billing/package.json",
        "client/server/controllers/intelligenceController.js",
    ):
        assert not (ROOT / relative).exists()
    for manifest in (
        "server/k8s/deployment.yaml",
        "server/k8s/service.yaml",
        "server/k8s/ingress.yaml",
        "server/k8s/predictive-deployment.yaml",
        "server/k8s/kustomization.yaml",
    ):
        assert not (ROOT / manifest).exists(), manifest
    dev_stack = (ROOT / "scripts/start-dev-stack.sh").read_text()
    assert "uvicorn tools.eos.api.server:app" in dev_stack
    package = json.loads((ROOT / "package.json").read_text())
    assert package["scripts"]["dev"] == "bash scripts/start-dev-stack.sh"
    assert "uvicorn tools.eos.api.server:app" in package["scripts"]["dev:kernel"]
    for relative_path in LEGACY_MIGRATION_HISTORY:
        assert (ROOT / relative_path).is_file(), relative_path
        assert classify(relative_path) == "RETAIN", relative_path
    for relative_path in PYTHON_MIGRATION_OWNERS:
        assert (ROOT / relative_path).is_file(), relative_path
    assert classify("server/.babelrc") == "RETIRED_NODE_BACKEND"
    assert classify("scripts/wilsy-crm-r71a-terminal-evidence-summary-gate.js") == "RETIRED_NODE_BACKEND"
    assert classify("tests/unit/qrServices.test.js") == "RETIRED_NODE_BACKEND"
    assert classify("server/manifest.txt") == "RETAIN"
    assert classify("server/scripts/rollback-migration-production.patch") == "RETAIN"
    assert not any(
        "server/scripts/migrate" in value
        for value in (package["scripts"]["dev"], package["scripts"]["dev:kernel"])
    )

# ARTIFACT: EOS Runtime Database Ownership Certificate
# VERSION: v1.4.8-MWT12-EXACT-RECOVERY-OPERATOR-CLASSIFICATION
# AUTHORITY BOUNDARY: Offline repository ownership evidence.
# TENANT POSTURE: No data access or mutation.
# FAIL-CLOSED POSTURE: Duplicate persistence or Node runtime fails.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
