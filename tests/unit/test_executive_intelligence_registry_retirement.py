"""WILSY OS — Executive Intelligence Registry retirement certificate.

TITLE: Executive Intelligence Registry Retirement Certificate
VERSION: v1.0.0-WILSY-EXECUTIVE-INTELLIGENCE-REGISTRY-RETIREMENT-CERT
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Prevent reintroduction of the retired legacy executive registry.
EPITOME: Executive intelligence truth remains evidence-bound in Python EOS;
transport headers, mutable correlation registries, synthetic seals, and
synthetic verification claims do not establish sovereign intelligence authority.
CERTIFICATION/UPDATE DATE: 2026-09-03

AUTHORIZED RETIRED PREIMAGE:
  authority commit:
    90dcaab67b7ed2be4b562ef40e562c0dff1b2016
  bytes:
    23423
  SHA3-512:
    97f5d41cc06271fe62544bd303d878241449e7babfc55fd08c46ec3523cecd31c01a03a3efc1431b82b9bd2e1836b010883dcb60f53e5249399d4e7eee1518bc

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
    "tools.eos.executive.intelligence."
    "executive_intelligence_registry"
)

RETIRED_PATH = Path(
    "tools/eos/executive/intelligence/"
    "executive_intelligence_registry.py"
)

INTELLIGENCE_DIR = RETIRED_PATH.parent

FACADE_PATH = Path(
    "tools/eos/executive/intelligence/"
    "executive_intelligence_facade.py"
)

RETIRED_AUTHORITY_SHA = (
    "90dcaab67b7ed2be4b562ef40e562c0dff1b2016"
)

RETIRED_BYTES = 23423

RETIRED_SHA3_512 = (
    "97f5d41cc06271fe62544bd303d878241449e7babfc55fd08c46ec3523cecd31c"
    "01a03a3efc1431b82b9bd2e1836b010883dcb60f53e5249399d4e7eee1518bc"
)

LEGACY_PUBLIC_API = (
    "ExecutiveIntelligenceRegistry",
    "ExecutiveRequestContext",
    "ExecutiveResponseContext",
    "WilsyHeaders",
    "with_executive_context",
    "create_executive_intelligence_registry",
)

LEGACY_MODULE_BASENAME = (
    "executive_intelligence_registry"
)

SYNTHETIC_VERIFICATION_MARKER = (
    "X-Quantum-Verified"
)


def _intelligence_production_sources() -> tuple[tuple[Path, str], ...]:
    sources: list[tuple[Path, str]] = []

    for path in sorted(
        INTELLIGENCE_DIR.glob("*.py")
    ):
        if path == RETIRED_PATH:
            continue

        sources.append(
            (
                path,
                path.read_text(encoding="utf-8"),
            )
        )

    return tuple(sources)


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


def test_retired_module_path_is_absent() -> None:
    assert not RETIRED_PATH.exists()


def test_retired_module_import_fails_closed() -> None:
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
        "retired registry unexpectedly importable "
        f"in fresh interpreter: stdout={completed.stdout!r} "
        f"stderr={completed.stderr!r}"
    )


def test_legacy_public_api_is_not_reintroduced() -> None:
    for path, text in _repository_production_python_sources():
        for token in LEGACY_PUBLIC_API:
            assert token not in text, (
                f"{token!r} reintroduced in {path}"
            )


def test_legacy_module_identity_is_not_reintroduced() -> None:
    for path, text in _repository_production_python_sources():
        assert LEGACY_MODULE_BASENAME not in text, (
            "legacy registry module reference "
            f"reintroduced in {path}"
        )


def test_synthetic_verification_claim_is_not_reintroduced() -> None:
    for path, text in _intelligence_production_sources():
        assert SYNTHETIC_VERIFICATION_MARKER not in text, (
            "synthetic verification claim "
            f"reintroduced in {path}"
        )


def test_certified_facade_remains_learning_bound() -> None:
    text = FACADE_PATH.read_text(
        encoding="utf-8"
    )

    assert "ExecutiveLearningResult" in text
    assert "executive_learning_engine" in text

    for token in (
        LEGACY_MODULE_BASENAME,
        *LEGACY_PUBLIC_API,
        "X-Tenant-ID",
        "X-Trace-ID",
        "X-Request-Seal",
        SYNTHETIC_VERIFICATION_MARKER,
    ):
        assert token not in text
