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


def test_legacy_node_backend_has_no_supported_runtime_entrypoint():
    import json

    package = json.loads((ROOT / "server/package.json").read_text(encoding="utf-8"))
    assert "start" not in package["scripts"]
    assert "dev" not in package["scripts"]
    assert "predev" not in package["scripts"]
    assert "main" not in package

    pm2 = (ROOT / "server/ecosystem.config.js").read_text(encoding="utf-8")
    assert "apps: []" in pm2
    assert "server.js" not in pm2

    deploy = (ROOT / "server/deploy.sh").read_text(encoding="utf-8")
    assert "exit 1" in deploy
    assert "legacy Node deployment path has been retired" in deploy

    for dockerfile in ("server/Dockerfile", "server/Dockerfile.worker"):
        source = (ROOT / dockerfile).read_text(encoding="utf-8")
        assert "FROM scratch" in source
        assert "FROM node:" not in source.lower()
