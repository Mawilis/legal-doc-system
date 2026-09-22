"""Production-configuration certificate for WILSY OS password recovery.

TITLE: WILSY OS Password Recovery Production Configuration Certificate
VERSION: v1.0.0-R10E73-PRODUCTION-RECOVERY-CONFIG-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies server-owned public recovery-origin alias precedence without
         trusting request Host or creating recovery, identity, or delivery truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_recovery_production_configuration.py
COLLABORATION / OWNERSHIP: Exercises auth_router production configuration
                           selection only; PasswordRecoveryRequestService retains
                           strict HTTPS/origin validation and issuance authority.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10E73-PRODUCTION-RECOVERY-CONFIG-CERT introduces bounded
           evidence for dedicated-origin precedence, established deployment
           aliases, explicit-empty fail-closed behavior, and total absence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No credentials, tokens, addresses, network, Mongo,
                            SMTP, request Host, or production secrets are used.
TENANT BOUNDARY: Configuration selection creates no tenant authority.
AUTHORITY BOUNDARY: Deterministic configuration evidence only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import pytest

from tools.eos.api.auth_router import _configured_password_recovery_origin

ORIGIN_KEYS = (
    "WILSY_PUBLIC_APP_ORIGIN",
    "WILSY_PUBLIC_APP_URL",
    "CLIENT_URL",
    "FRONTEND_URL",
    "APP_URL",
)


def _clear_origins(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ORIGIN_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_no_configured_origin_returns_empty_fail_closed_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_origins(monkeypatch)
    assert _configured_password_recovery_origin() == ""


def test_dedicated_recovery_origin_has_highest_precedence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_origins(monkeypatch)
    monkeypatch.setenv("WILSY_PUBLIC_APP_ORIGIN", "https://recovery.wilsy.example")
    monkeypatch.setenv("APP_URL", "https://app.wilsy.example")

    assert (
        _configured_password_recovery_origin()
        == "https://recovery.wilsy.example"
    )


@pytest.mark.parametrize(
    ("key", "value"),
    (
        ("WILSY_PUBLIC_APP_URL", "https://public.wilsy.example"),
        ("CLIENT_URL", "https://client.wilsy.example"),
        ("FRONTEND_URL", "https://frontend.wilsy.example"),
        ("APP_URL", "https://app.wilsy.example"),
    ),
)
def test_established_server_owned_origin_aliases_are_supported(
    monkeypatch: pytest.MonkeyPatch,
    key: str,
    value: str,
) -> None:
    _clear_origins(monkeypatch)
    monkeypatch.setenv(key, value)

    assert _configured_password_recovery_origin() == value


def test_explicit_empty_higher_precedence_origin_blocks_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_origins(monkeypatch)
    monkeypatch.setenv("WILSY_PUBLIC_APP_ORIGIN", "")
    monkeypatch.setenv("APP_URL", "https://app.wilsy.example")

    assert _configured_password_recovery_origin() == ""


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_password_recovery_production_configuration.py
# VERSION: v1.0.0-R10E73-PRODUCTION-RECOVERY-CONFIG-CERT
# AUTHORITY BOUNDARY: deterministic server-owned configuration evidence only
# TENANT POSTURE: no tenant authority is created or inferred
# FAIL-CLOSED POSTURE: absence/explicit-empty configuration remains unresolved
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
