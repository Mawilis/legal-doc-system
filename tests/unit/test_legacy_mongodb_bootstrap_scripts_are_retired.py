"""Ensure retired MongoDB bootstrap scripts contain only inert fail-closed shell."""

from pathlib import Path
import os
import re
import subprocess

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RETIRED_SCRIPTS = (
    "server/fix_tenant_auth.sh",
    "server/inject_master_user.sh",
    "server/elevate_wilsy_app.sh",
    "server/force_fix_wilsy.sh",
)
SAFE_STUB_BODY = re.compile(
    r"\Aset -euo pipefail\n"
    r"\n"
    r"printf '%s\\n' >&2 \\\n"
    r'  "DISABLED: [^"\n]*" \\\n'
    r'  "[^"$\x60\n]*"\n'
    r"exit 1\n?\Z"
)


@pytest.mark.parametrize("relative_path", RETIRED_SCRIPTS)
def test_legacy_mongodb_bootstrap_script_is_inert(
    relative_path: str, tmp_path: Path,
) -> None:
    script = REPOSITORY_ROOT / relative_path
    source = script.read_text(encoding="utf-8")

    assert "DISABLED:" in source
    assert "END OF WILSY OS SOVEREIGN ARTIFACT" in source
    assert "VERSION: v2.0.0" in source
    body = source[source.index("set -euo pipefail\n"): ]
    assert SAFE_STUB_BODY.fullmatch(body), (
        f"{relative_path} contains a command or shell construct outside the "
        "approved inert printf-and-exit stub"
    )

    # An empty PATH makes any unexpected external command fail immediately.
    result = subprocess.run(
        ["/bin/bash", str(script)],
        check=False,
        capture_output=True,
        text=True,
        timeout=5,
        env={**os.environ, "PATH": str(tmp_path)},
    )
    assert result.returncode == 1
    assert "DISABLED:" in result.stderr
    assert "mongosh" not in result.stderr.lower()
