"""Regression certificate for explicit local EOS database selection.

TITLE: WILSY EOS Local MFA Launcher Database Configuration Certificate
VERSION: v1.3.0-CANONICAL-DOTENV-DATABASE-SELECTION-CERTIFICATE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves launcher database selection uses the canonical EOS resolver,
         preserves process-environment precedence and configured nonproduction
         dotenv fallback, rejects malformed or unsafe targets, and allows
         structurally valid selections to reach the next startup gate.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_start_eos_local_mfa_configuration.py
COLLABORATION / OWNERSHIP: Certificate for scripts/start-eos-local-mfa.sh.
CERTIFICATION / UPDATE DATE: 2026-11-16
SECURITY / PRIVACY POSTURE: This test certificate checks local MFA startup configuration without granting authentication, disclosing secrets, or weakening KMS controls.
FINANCIAL AUTHORITY BOUNDARY: MFA configuration tests confer no payment, settlement or financial execution authority; Kennel EOS remains exclusive.
CHANGELOG:
  v1.3.0-CANONICAL-DOTENV-DATABASE-SELECTION-CERTIFICATE verifies that the
    configured repository dotenv target passes launcher preflight when the
    process has no MONGODB_URI, while retaining explicit-process precedence.
  v1.2.0-EXPLICIT-MONGODB-TARGET-CERTIFICATE separates malformed URI,
    authentication, replica-set, and authSource refusal coverage and proves
    accepted preflight stops at the controlled missing-AWS test double.
  v1.1.0-EXPLICIT-MONGODB-TARGET-CERTIFICATE verifies either production
    environment marker independently blocks launch, including conflicting
    marker values.
  v1.0.0-EXPLICIT-MONGODB-TARGET-CERTIFICATE covers missing, invalid,
    authenticated replica-set, explicit remote URI, and production-refusal paths.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Tests perform no database connection or tenant record operation.
AUTHORITY BOUNDARY: Launcher preflight only; no EOS, MongoDB or AWS authority.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_LAUNCHER = _REPOSITORY_ROOT / "scripts" / "start-eos-local-mfa.sh"
_SECRET_MARKER = "URI_SECRET_MUST_NOT_APPEAR"
_INVALID_TARGET_CODE = "EOS_LOCAL_MFA_CONFIG_ERROR=MONGODB_URI_INVALID_OR_UNVERIFIABLE_TARGET"
_AWS_GATE_CODE = "EOS_LOCAL_MFA_CONFIG_ERROR=AWS_CLI_REQUIRED"


@pytest.fixture
def isolated_launcher_path(tmp_path: Path) -> str:
    """Expose only dirname; no AWS CLI or database tools can run in tests."""
    path_dir = tmp_path / "path"
    path_dir.mkdir()
    dirname = shutil.which("dirname")
    assert dirname is not None
    (path_dir / "dirname").symlink_to(dirname)
    return str(path_dir)


def _invoke_launcher(
    path: str,
    *,
    uri: str | None = None,
    environment_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PATH"] = path
    environment.pop("MONGODB_URI", None)
    environment.pop("ENV", None)
    environment.pop("WILSY_ENV", None)
    if uri is not None:
        environment["MONGODB_URI"] = uri
    if environment_overrides:
        environment.update(environment_overrides)
    return subprocess.run(
        ["/bin/bash", str(_LAUNCHER)],
        cwd=_REPOSITORY_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )


def _assert_no_uri_secret(result: subprocess.CompletedProcess[str]) -> None:
    assert _SECRET_MARKER not in result.stdout + result.stderr


def test_launcher_uses_configured_nonproduction_dotenv_target_without_process_uri(
    isolated_launcher_path: str,
) -> None:
    result = _invoke_launcher(isolated_launcher_path)
    assert result.returncode == 2
    assert _AWS_GATE_CODE in result.stderr
    assert _INVALID_TARGET_CODE not in result.stderr
    _assert_no_uri_secret(result)


def test_invalid_explicit_process_uri_is_not_replaced_by_dotenv(
    isolated_launcher_path: str,
) -> None:
    result = _invoke_launcher(
        isolated_launcher_path,
        uri=f"not-a-mongodb-uri-{_SECRET_MARKER}",
    )
    assert result.returncode == 2
    assert _INVALID_TARGET_CODE in result.stderr
    assert _AWS_GATE_CODE not in result.stderr
    _assert_no_uri_secret(result)


def test_launcher_rejects_malformed_uri_without_echoing_it(isolated_launcher_path: str) -> None:
    result = _invoke_launcher(
        isolated_launcher_path,
        uri=f"not-a-mongodb-uri-{_SECRET_MARKER}",
    )
    assert result.returncode == 2
    assert _INVALID_TARGET_CODE in result.stderr
    _assert_no_uri_secret(result)


def test_launcher_rejects_local_uri_without_authentication(isolated_launcher_path: str) -> None:
    result = _invoke_launcher(
        isolated_launcher_path,
        uri="mongodb://127.0.0.1:27017/wilsy?replicaSet=rs0&authSource=admin",
    )
    assert result.returncode == 2
    assert _INVALID_TARGET_CODE in result.stderr


@pytest.mark.parametrize(
    "query",
    [
        "replicaSet=wrong&authSource=admin",
        "replicaSet=rs0",
    ],
    ids=["wrong-replica-set", "missing-auth-source"],
)
def test_launcher_rejects_wrong_or_incomplete_local_replica_configuration(
    isolated_launcher_path: str,
    query: str,
) -> None:
    result = _invoke_launcher(
        isolated_launcher_path,
        uri=f"mongodb://operator:{_SECRET_MARKER}@127.0.0.1:27017/wilsy?{query}",
    )
    assert result.returncode == 2
    assert _INVALID_TARGET_CODE in result.stderr
    _assert_no_uri_secret(result)


def test_valid_authenticated_rs0_target_passes_preflight_without_database_connection(
    isolated_launcher_path: str,
) -> None:
    result = _invoke_launcher(
        isolated_launcher_path,
        uri=(
            f"mongodb://operator:{_SECRET_MARKER}@127.0.0.1:27017/wilsy"
            "?replicaSet=rs0&authSource=admin"
        ),
    )
    assert result.returncode == 2
    assert _AWS_GATE_CODE in result.stderr
    assert _INVALID_TARGET_CODE not in result.stderr
    _assert_no_uri_secret(result)


def test_valid_remote_uri_passes_preflight_without_database_connection(isolated_launcher_path: str) -> None:
    result = _invoke_launcher(
        isolated_launcher_path,
        uri=(
            f"mongodb+srv://operator:{_SECRET_MARKER}@eos-dev.example.invalid/wilsy"
            "?retryWrites=true&w=majority"
        ),
    )
    assert result.returncode == 2
    assert _AWS_GATE_CODE in result.stderr
    assert _INVALID_TARGET_CODE not in result.stderr
    _assert_no_uri_secret(result)


@pytest.mark.parametrize(
    "overrides",
    [
        {"WILSY_ENV": "production"},
        {"WILSY_ENV": "development", "ENV": "production"},
    ],
    ids=["wilsy-env-production", "either-marker-production"],
)
def test_launcher_refuses_production_environment(
    isolated_launcher_path: str,
    overrides: dict[str, str],
) -> None:
    result = _invoke_launcher(
        isolated_launcher_path,
        uri=f"mongodb+srv://operator:{_SECRET_MARKER}@eos-dev.example.invalid/wilsy",
        environment_overrides=overrides,
    )
    assert result.returncode == 2
    assert "EOS_LOCAL_MFA_CONFIG_ERROR=PRODUCTION_ENVIRONMENT_NOT_ALLOWED" in result.stderr
    _assert_no_uri_secret(result)


# ARTIFACT: tests/unit/test_start_eos_local_mfa_configuration.py
# VERSION: v1.3.0-CANONICAL-DOTENV-DATABASE-SELECTION-CERTIFICATE
# AUTHORITY BOUNDARY: Tests only launcher refusal and safe target parsing.
# TENANT POSTURE: No tenant, membership, factor, session or database records are read or written.
# FAIL-CLOSED POSTURE: Invalid configuration fails before AWS, KMS, MongoDB or EOS startup.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
