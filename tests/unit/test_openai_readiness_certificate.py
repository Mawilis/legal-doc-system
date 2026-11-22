"""No-generation OpenAI readiness fixture certificate.

TITLE: WILSY OS OpenAI Readiness Unit Certificate
VERSION: v1.0.0-NONGENERATIVE-READINESS-UNIT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove one GET model lookup and bounded error reporting without any
         Responses invocation, identity leakage, MongoDB writes, or retries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_openai_readiness_certificate.py
COLLABORATION / OWNERSHIP: Synthetic SDK model retrieval fixtures for
                           openai_readiness_certificate.py only.
CERTIFICATION / UPDATE DATE: 2026-11-21
CHANGELOG: v1.0.0-NONGENERATIVE-READINESS-UNIT adds isolated valid, invalid,
           HTTP rejection and transport exception certificates.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No live credentials or provider transport.
TENANT BOUNDARY: No tenant-bearing arguments or network metadata.
AUTHORITY BOUNDARY: Model lookup not grant of execution or billing authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
FAIL-CLOSED DECLARATION: No response generation and no retry on any failure.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from tools.eos.intelligence.providers.openai_readiness_certificate import (
    OpenAIReadinessRefused,
    inspect_model,
    main,
)


class VendorFailure(Exception):
    """Synthetic provider rejection with a secret error body that must not leak."""

    def __init__(self, code: int) -> None:
        super().__init__("secret vendor error")
        self.status_code = code


def test_exact_model_lookup_is_only_provider_call() -> None:
    """A passed preflight is not a proof of quota or token generation."""
    client = SimpleNamespace(
        models=SimpleNamespace(retrieve=Mock(return_value=SimpleNamespace(id="gpt-5-mini"))),
        responses=SimpleNamespace(create=Mock()),
    )
    result = inspect_model(client=client, model_id="gpt-5-mini")
    assert result["status"] == "MODEL_LOOKUP_VERIFIED"
    assert result["quota_verified"] is False
    assert result["generation_attempted"] is False
    assert result["wilsy_reservations_written"] is False
    client.models.retrieve.assert_called_once_with("gpt-5-mini")
    client.responses.create.assert_not_called()


@pytest.mark.parametrize("model", ["gtp-5-mini", "sk-secret", "key_secret", "", "gpt-" + "x" * 200])
def test_invalid_model_fails_before_any_provider_call(model: str) -> None:
    client = SimpleNamespace(models=SimpleNamespace(retrieve=Mock()))
    with pytest.raises(OpenAIReadinessRefused, match="OPENAI_PREFLIGHT_MODEL_ID_INVALID"):
        inspect_model(client=client, model_id=model)
    client.models.retrieve.assert_not_called()


@pytest.mark.parametrize("code", [400, 401, 403, 404, 429, 500])
def test_status_errors_are_bounded_without_vendor_body(code: int) -> None:
    client = SimpleNamespace(models=SimpleNamespace(retrieve=Mock(side_effect=VendorFailure(code))))
    report = inspect_model(client=client, model_id="gpt-5-mini")
    assert report["status"] == "NOT_VERIFIED"
    assert report["http_status"] == code
    assert report["failure_class"] == "VendorFailure"
    assert "secret" not in repr(report)
    client.models.retrieve.assert_called_once()


def test_malformed_provider_model_identity_fails_closed() -> None:
    client = SimpleNamespace(models=SimpleNamespace(retrieve=Mock(return_value=SimpleNamespace(id="other"))))
    with pytest.raises(OpenAIReadinessRefused, match="OPENAI_PREFLIGHT_MODEL_ID_MISMATCH"):
        inspect_model(client=client, model_id="gpt-5-mini")


def test_cli_injection_cannot_attempt_generation_or_persist_credentials(capsys: object, monkeypatch: object) -> None:
    """No non-test OpenAI client is constructed in this certificate."""
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-secret")
    client = SimpleNamespace(
        models=SimpleNamespace(retrieve=Mock(return_value=SimpleNamespace(id="gpt-5-mini"))),
        responses=SimpleNamespace(create=Mock()),
    )
    factory = Mock(return_value=client)
    result = main(["--model", "gpt-5-mini"], client_factory=factory)
    assert result == 0
    assert factory.call_count == 1
    assert client.models.retrieve.call_count == 1
    assert client.responses.create.call_count == 0
    stdout = capsys.readouterr().out
    assert "synthetic-secret" not in stdout
    assert '"quota_verified":false' in stdout


# ARTIFACT: test_openai_readiness_certificate.py
# VERSION: v1.0.0-NONGENERATIVE-READINESS-UNIT
# AUTHORITY BOUNDARY: synthetic GET-model readiness only
# TENANT POSTURE: no tenant or principal inputs
# FAIL-CLOSED POSTURE: no retries or generation despite provider rejection
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
