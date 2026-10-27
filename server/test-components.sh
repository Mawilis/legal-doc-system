#!/usr/bin/env bash
set -euo pipefail

# TITLE: Python EOS Component Certification
# VERSION: v1.0.0-PYTHON-EOS-COMPONENT-CERT
# AUTHORITY: Test execution only; no production or tenant authority.
# EPITOME: Certifies the canonical Python EOS PDF route without starting the retired Node BFF.
# ABSOLUTE CANONICAL PATH: server/test-components.sh
# CERTIFICATION / UPDATE DATE: 2026-10-27
# CHANGELOG: v1.0.0 replaces Node BFF startup checks with Python EOS route tests.
# SECURITY / PRIVACY POSTURE: No production database URI is loaded by this script.
# FAIL-CLOSED POSTURE: The script does not start a network listener or contact production services.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"

if [[ ! -x "$PYTHON" ]]; then
  echo "PYTHON_EOS_TEST_INTERPRETER_UNAVAILABLE" >&2
  exit 2
fi

cd "$ROOT"
"$PYTHON" -m py_compile tools/eos/api/server.py tools/eos/api/artifact_pdf_router.py
"$PYTHON" -m pytest -q tests/unit/test_artifact_pdf_router.py

# ARTIFACT: server/test-components.sh
# AUTHORITY BOUNDARY: Test execution only.
# END OF WILSY OS SOVEREIGN ARTIFACT
