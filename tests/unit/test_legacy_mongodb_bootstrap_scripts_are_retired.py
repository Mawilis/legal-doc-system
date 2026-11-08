"""Ensure retired MongoDB bootstrap scripts cannot mutate identities or roles."""
from pathlib import Path
import subprocess

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RETIRED_SCRIPTS = (
    "server/fix_tenant_auth.sh",
    "server/inject_master_user.sh",
    "server/elevate_wilsy_app.sh",
    "server/force_fix_wilsy.sh",
)


@pytest.mark.parametrize("relative_path", RETIRED_SCRIPTS)
def test_legacy_mongodb_bootstrap_script_is_inert(relative_path: str) -> None:
    script = REPOSITORY_ROOT / relative_path
    source = script.read_text(encoding="utf-8")

    assert "DISABLED:" in source
    assert "exit 1" in source
    assert "mongosh " not in source
    assert "grantRolesToUser" not in source
    assert "db.users" not in source
    assert "--noauth" not in source
    assert ' -p "' not in source

    result = subprocess.run(
        ["bash", str(script)],
        check=False,
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 1
    assert "DISABLED:" in result.stderr
