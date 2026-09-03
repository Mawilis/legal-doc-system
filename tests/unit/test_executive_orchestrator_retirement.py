"""WILSY OS — Executive Orchestrator retirement certificate.

TITLE: Executive Orchestrator Retirement Certificate
VERSION: v1.0.0-WILSY-EXECUTIVE-ORCHESTRATOR-RETIREMENT-CERT
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Prevent reintroduction of the retired synthetic executive orchestrator.
EPITOME: Orchestration must never manufacture sovereign intelligence facts,
identity authority, workflow execution claims, health claims, or mutable
process-local authority outside governed Python EOS evidence lineage.
CERTIFICATION/UPDATE DATE: 2026-09-03

AUTHORIZED RETIRED PREIMAGE:
  authority commit:
    1d3a4848038a70baed3e5061d902f33afec84e01
  bytes:
    4000
  SHA3-512:
    b4c48d409ddd6d9731bfea2c4f2cec384628b98e4f96dcfdfe5a2399f6731c73a0643dd1ed36f2230d76220fd4c1865c4aeb6f9b3abab1dbd7068dab19591e3c

GOVERNANCE:
  Python EOS is sovereign business and intelligence truth.
  Kennel EOS is the exclusive financial execution authority.
  Node is transport/orchestration/BFF only.
  NO EVIDENCE = NO FACT.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


RETIRED_MODULE = (
    "tools.eos.executive.orchestration."
    "executive_orchestrator"
)

RETIRED_PATH = Path(
    "tools/eos/executive/orchestration/"
    "executive_orchestrator.py"
)

FACADE_PATH = Path(
    "tools/eos/executive/intelligence/"
    "executive_intelligence_facade.py"
)

WORKFLOW_PATH = Path(
    "tools/eos/executive/intelligence/"
    "executive_workflow_engine.py"
)

LEGACY_PUBLIC_API = (
    "ExecutiveOrchestrator",
    "orchestrate_intent",
    "get_orchestration_state",
)

LEGACY_MODULE_BASENAME = "executive_orchestrator"

LEGACY_EXACT_AUTHORITY_MARKERS = (
    '"system_health": "OPTIMAL"',
    '"latency_budget": "Sub-500ms"',
    '"master_status": "ORCHESTRATING"',
    "WORKFLOW_EXECUTION -> PENDING",
)


def _repository_production_python_sources() -> tuple[tuple[Path, str], ...]:
    raw_paths = subprocess.check_output(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            "*.py",
        ],
        text=True,
    ).splitlines()

    sources: list[tuple[Path, str]] = []

    for raw_path in sorted(set(raw_paths)):
        path = Path(raw_path)

        if path == RETIRED_PATH:
            continue

        if "tests" in path.parts:
            continue

        if not path.is_file():
            continue

        sources.append(
            (
                path,
                path.read_text(encoding="utf-8"),
            )
        )

    return tuple(sources)


def test_retired_orchestrator_path_is_absent() -> None:
    assert not RETIRED_PATH.exists()


def test_retired_orchestrator_import_fails_in_fresh_process() -> None:
    code = (
        "import importlib\n"
        f"module = {RETIRED_MODULE!r}\n"
        "try:\n"
        "    importlib.import_module(module)\n"
        "except ModuleNotFoundError as exc:\n"
        "    if exc.name != module:\n"
        "        raise\n"
        "    raise SystemExit(0)\n"
        "raise SystemExit(9)\n"
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            code,
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, (
        "retired orchestrator unexpectedly importable "
        f"in fresh interpreter: stdout={completed.stdout!r} "
        f"stderr={completed.stderr!r}"
    )


def test_legacy_orchestrator_api_is_not_reintroduced() -> None:
    for path, text in _repository_production_python_sources():
        for token in LEGACY_PUBLIC_API:
            assert token not in text, (
                f"{token!r} reintroduced in {path}"
            )


def test_legacy_orchestrator_module_is_not_reintroduced() -> None:
    for path, text in _repository_production_python_sources():
        assert LEGACY_MODULE_BASENAME not in text, (
            "retired orchestrator module reference "
            f"reintroduced in {path}"
        )


def test_synthetic_orchestration_claims_are_not_reintroduced() -> None:
    for path, text in _repository_production_python_sources():
        for marker in LEGACY_EXACT_AUTHORITY_MARKERS:
            assert marker not in text, (
                "retired synthetic orchestration claim "
                f"{marker!r} reintroduced in {path}"
            )


def test_certified_facade_remains_evidence_bound() -> None:
    text = FACADE_PATH.read_text(encoding="utf-8")

    assert "ExecutiveLearningResult" in text
    assert "evidence_references" in text

    for token in (
        LEGACY_MODULE_BASENAME,
        *LEGACY_PUBLIC_API,
    ):
        assert token not in text


def test_frozen_workflow_remains_non_execution_authority() -> None:
    text = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "ExecutivePlanningResult" in text

    for token in (
        LEGACY_MODULE_BASENAME,
        *LEGACY_PUBLIC_API,
        '"system_health": "OPTIMAL"',
        "WORKFLOW_EXECUTION -> PENDING",
    ):
        assert token not in text
