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
