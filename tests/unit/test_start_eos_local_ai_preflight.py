"""WILSY OS nonbillable OpenAI launcher preflight certification.

TITLE: WILSY OS Local AI Preflight Unit Certificate
VERSION: v1.0.0-NONBILLABLE-PREFLIGHT-NEGATIVE-CERTIFICATE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify GET-only provider metadata check, safe outcomes and no
         paid inference in the canonical local AI launcher.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_start_eos_local_ai_preflight.py
COLLABORATION / OWNERSHIP: Certifies scripts/start-eos-local-ai.sh only;
                            no persistent or external provider side effects.
CERTIFICATION / UPDATE DATE: 2026-11-22
CHANGELOG: v1.0.0-NONBILLABLE-PREFLIGHT-NEGATIVE-CERTIFICATE proves
           metadata-only success and bounded HTTP/transport refusal.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Dummy credentials; no real provider requests.
TENANT BOUNDARY: No principal, tenant or subscription source touched.
AUTHORITY BOUNDARY: Static launcher and injected transport only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
FAIL-CLOSED DECLARATION: Every mock failure must refuse launch.
"""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import sys
import urllib.error
import urllib.request

import pytest


ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = ROOT / "scripts" / "start-eos-local-ai.sh"
DUMMY_KEY = "test-only-not-a-valid-provider-credential"


def _probe_code() -> str:
    """Load the actual embedded Python entrypoint rather than duplicating logic."""
    source = LAUNCHER.read_text(encoding="utf-8")
    assert source.count("python - <<'PY'") == 1
    return source.split("python - <<'PY'\n", 1)[1].split("\nPY\n", 1)[0]


def _exercise(monkeypatch: pytest.MonkeyPatch, replacement: object) -> tuple[int, str]:
    """Execute a mocked GET-only preflight and capture only public diagnostics."""
    monkeypatch.setenv("WILSY_AI_REASONING_MODEL", "gpt-5-mini")
    monkeypatch.setenv("OPENAI_API_KEY", DUMMY_KEY)
    monkeypatch.setattr(urllib.request, "urlopen", replacement)
    out = StringIO()
    err = StringIO()
    code = 0
    with redirect_stdout(out), redirect_stderr(err):
        try:
            exec(compile(_probe_code(), str(LAUNCHER), "exec"), {"__name__": "__main__"})
        except SystemExit as exit_error:
            code = int(exit_error.code)
    result = out.getvalue() + err.getvalue()
    assert DUMMY_KEY not in result
    return code, result


def test_shell_is_parseable_and_probe_only_is_separate() -> None:
    """The executable launcher must accept probe-only without invoking EOS."""
    result = subprocess.run(
        ["bash", "-n", str(LAUNCHER)],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    source = LAUNCHER.read_text(encoding="utf-8")
    assert '== "--probe-only"' in source
    assert 'method="GET"' in source
    assert 'method="POST"' not in source
    assert source.count("v1.2.0-NONBILLABLE-MODEL-METADATA-PREFLIGHT") == 3
    assert source.rstrip().endswith("# END OF WILSY OS SOVEREIGN ARTIFACT")


def test_nonbillable_metadata_success_disclaims_quota(monkeypatch: pytest.MonkeyPatch) -> None:
    """GET metadata validates no billable execution or account quota."""

    class Response:
        status = 200

        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *args: object) -> None:
            return None

    def fake_get(request: urllib.request.Request, timeout: int) -> Response:
        assert request.get_method() == "GET"
        assert request.full_url == "https://api.openai.com/v1/models/gpt-5-mini"
        assert request.get_header("Authorization") == "Bearer " + DUMMY_KEY
        assert timeout == 10
        return Response()

    code, output = _exercise(monkeypatch, fake_get)
    assert code == 0
    assert "EOS_LOCAL_AI_PREFLIGHT=MODEL_METADATA_VERIFIED_ONLY" in output
    assert "EOS_LOCAL_AI_QUOTA=NOT_VERIFIED" in output
    assert "EOS_LOCAL_AI_BILLABLE_EXECUTION=NOT_PERFORMED" in output


@pytest.mark.parametrize(
    ("status", "classification"),
    [
        (401, "CREDENTIAL_OR_ACCESS_REJECTED"),
        (403, "CREDENTIAL_OR_ACCESS_REJECTED"),
        (404, "MODEL_NOT_ACCESSIBLE"),
        (429, "RATE_LIMIT_OR_QUOTA_UNVERIFIED"),
        (503, "PROVIDER_HTTP_UNAVAILABLE"),
    ],
)
def test_http_failure_classified_without_body(
    monkeypatch: pytest.MonkeyPatch, status: int, classification: str,
) -> None:
    """Expected HTTP failures must not leak provider responses or allow launch."""

    def fake_get(request: urllib.request.Request, timeout: int) -> object:
        raise urllib.error.HTTPError(request.full_url, status, "secret-body", None, None)

    code, output = _exercise(monkeypatch, fake_get)
    assert code == 3
    assert "EOS_LOCAL_AI_PREFLIGHT=" + classification in output
    assert "EOS_LOCAL_AI_PREFLIGHT_HTTP_STATUS=" + str(status) in output
    assert "secret-body" not in output


def test_transport_unavailable_is_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Network failures fail closed without echoing their exception content."""

    def fake_get(request: urllib.request.Request, timeout: int) -> object:
        raise urllib.error.URLError("private-transport-detail")

    code, output = _exercise(monkeypatch, fake_get)
    assert code == 3
    assert "EOS_LOCAL_AI_PREFLIGHT=TRANSPORT_UNAVAILABLE" in output
    assert "private-transport-detail" not in output


# ARTIFACT: test_start_eos_local_ai_preflight.py
# VERSION: v1.0.0-NONBILLABLE-PREFLIGHT-NEGATIVE-CERTIFICATE
# AUTHORITY BOUNDARY: canonical local launcher injected transport only
# TENANT POSTURE: no tenant, identity, or persistent source touched
# FAIL-CLOSED POSTURE: no real keys or provider calls, all failures refuse
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
