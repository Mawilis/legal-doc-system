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


def test_python_eos_compose_is_a_single_python_application_runtime():
    source = (ROOT / "docker-compose.eos.yml").read_text(encoding="utf-8")
    assert "dockerfile: Dockerfile.eos" in source
    assert "MONGODB_URI:" in source
    assert '"${EOS_PORT:-9095}:9095"' in source
    assert "wilsy-eos:" in source
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
    assert "tools.eos" not in source
    assert "node:" not in source.lower()
    assert "server/Dockerfile" not in source
