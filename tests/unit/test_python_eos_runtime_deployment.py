"""TITLE: WILSY OS Canonical Python EOS Runtime Deployment Regression
VERSION: v1.0.0-MW-T12-MONGO7-PYTHON-RUNTIME-CERT
AUTHORITY: WILSY OS Runtime Governance.
EPITOME: Protect the Python-only EOS deployment and isolated MongoDB 7
         recovery rehearsal without introducing production shortcuts.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_python_eos_runtime_deployment.py
COLLABORATION / OWNERSHIP: WILSY OS Python EOS runtime and MW-T12 recovery.
CERTIFICATION / UPDATE DATE: 2026-11-28
CHANGELOG: v1.0.0-MW-T12-MONGO7-PYTHON-RUNTIME-CERT adds synthetic MongoDB 7 hostname
           replica initialization and fail-closed response assertions to existing
           Python-only deployment tests; all prior assertions preserved.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Static manifests and synthetic no-network mocks only.
TENANT BOUNDARY: No tenant, Atlas or production data is accessed.
AUTHORITY BOUNDARY: Unit tests certify no runtime grant or release permission.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Invalid replica initialization denies recovery success.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_canonical_container_image_runs_python_eos_without_node_runtime():
    source = (ROOT / "Dockerfile.eos").read_text(encoding="utf-8")
    assert "FROM python:3.12-slim" in source
    assert "tools.eos.api.server:app" in source
    assert 'CMD ["python", "-m", "uvicorn"' in source
    assert "FROM node:" not in source
    assert "npm " not in source
    assert "node " not in source


def test_python_eos_compose_runs_api_and_durable_worker_as_python_services():
    source = (ROOT / "docker-compose.eos.yml").read_text(encoding="utf-8")
    assert "dockerfile: Dockerfile.eos" in source
    assert "MONGODB_URI:" in source
    assert '"${EOS_PORT:-9095}:9095"' in source
    assert "wilsy-eos:" in source
    assert "wilsy-eos-worker:" in source
    assert "tools.eos.runtime.worker_process" in source
    assert 'profiles: ["python-workers"]' in source
    assert "node:" not in source.lower()
    assert "server/Dockerfile" not in source
    assert "server/Dockerfile.worker" not in source


def test_python_eos_runtime_deployment_is_non_production_candidate():
    source = (ROOT / "docker-compose.eos.yml").read_text(encoding="utf-8")
    assert "staging" in source
    assert "candidate" in source


def test_repository_default_dockerfile_is_python_eos():
    source = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "FROM python:3.12-slim" in source
    assert "tools.eos.api.server:app" in source
    assert 'CMD ["python", "-m", "uvicorn"' in source
    assert "FROM node:" not in source
    assert "npm " not in source


def test_repository_default_compose_uses_python_eos_service():
    source = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "dockerfile: Dockerfile" in source
    assert "wilsy-eos:" in source
    assert "tools.eos.runtime.worker_process" in source
    assert "node:" not in source.lower()
    assert "server/Dockerfile" not in source


def test_default_compose_exposes_worker_only_behind_explicit_profile():
    source = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "wilsy-eos-worker:" in source
    assert 'profiles: ["python-workers"]' in source
    assert "tools.eos.runtime.worker_process" in source


def test_production_compose_runs_only_kennel_eos_python_api_and_worker():
    source = (ROOT / "docker-compose.prod.yml").read_text(encoding="utf-8")
    assert "dockerfile: Dockerfile" in source
    assert "ENV: production" in source
    assert "WILSY_ENV: production" in source
    assert "MONGODB_URI:" in source
    assert '"${EOS_PORT:-9095}:9095"' in source
    assert "tools.eos.runtime.worker_process" in source
    assert 'profiles: ["python-workers"]' in source
    assert "server/Dockerfile" not in source
    assert "server/.env.production" not in source
    assert "NODE_ENV" not in source
    assert "3000:3000" not in source
    assert "9096:9096" not in source
    assert "9090:9090" not in source
    assert "express" not in source.lower()
    assert "node:" not in source.lower()


def test_worker_service_has_no_http_healthcheck():
    for name in ("docker-compose.yml", "docker-compose.eos.yml", "docker-compose.prod.yml"):
        source = (ROOT / name).read_text(encoding="utf-8")
        worker = source.split("  wilsy-eos-worker:", 1)[1].split("\nnetworks:", 1)[0]
        assert "healthcheck:\n      disable: true" in worker


def test_node_backend_process_launchers_and_transport_are_absent():
    for path in (
        "server/server.js",
        "server/ecosystem.config.js",
        "server/deploy.sh",
        "server/tests/routes/wilsyAiAdvisoryProxy.test.js",
        "orchestrator.js",
    ):
        assert not (ROOT / path).exists(), f"retired Node backend artifact remains: {path}"

    import json

    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    assert "pm2" not in package.get("dependencies", {})
    assert "pm2" not in package.get("devDependencies", {})
    assert "server:start" not in package.get("scripts", {})
    assert "pm2:deploy" not in package.get("scripts", {})
    lock = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
    assert "pm2" not in lock["packages"][""].get("devDependencies", {})
    assert "pm2" not in lock["packages"][""].get("dependencies", {})


def test_mw_t12_disposable_replica_uses_mongo7_compatible_hostname(monkeypatch):
    """Exercise the exact recovery certificate's positive and denied Mongo initiation."""
    import pytest
    from tools.eos.ops import mw_t12_disposable_mongo_recovery as recovery

    monkeypatch.setattr(recovery.time, "sleep", lambda _: None)
    calls = []

    def success(_container, expression):
        calls.append(expression)
        if expression == "db.adminCommand({ping:1}).ok":
            return "1"
        if expression.startswith("JSON.stringify(rs.initiate"):
            assert 'host:"localhost:27017"' in expression
            assert 'host:"127.0.0.1:27017"' not in expression
            return '{"ok":1}'
        if expression == "db.hello().isWritablePrimary":
            return "true"
        raise AssertionError("Unexpected Mongo primary shell call")

    monkeypatch.setattr(recovery, "mongo", success)
    recovery.primary("synthetic-owned-container")
    assert len(calls) == 3

    def rejected(_container, expression):
        if expression == "db.adminCommand({ping:1}).ok":
            return "1"
        if expression.startswith("JSON.stringify(rs.initiate"):
            return '{"ok":0,"code":93}'
        raise AssertionError("Rejected initialization must not be treated as primary")

    monkeypatch.setattr(recovery, "mongo", rejected)
    with pytest.raises(recovery.RecoveryGateError) as error:
        recovery.primary("synthetic-owned-container")
    assert error.value.code == "MONGO_REPLICA_INIT_REJECTED"


# ARTIFACT: tests/unit/test_python_eos_runtime_deployment.py
# VERSION: v1.0.0-MW-T12-MONGO7-PYTHON-RUNTIME-CERT
# AUTHORITY BOUNDARY: Source-level runtime and synthetic Mongo initialization checks.
# TENANT POSTURE: No real tenant or remote data.
# FAIL-CLOSED POSTURE: Invalid source and Mongo receipts fail certification.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
