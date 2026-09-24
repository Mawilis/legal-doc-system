"""Direct unit certificate for the WILSY OS developer persona operator.

TITLE: WILSY OS Developer Legal Persona Operator Direct Certificate
VERSION: v1.0.0-D15G-DEV-LEGAL-PERSONA-OPERATOR-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Deterministically certifies the local development-only operator's
         non-production gate, secret-input posture, owner password+TOTP
         authentication, exact tenant binding, durable principal check, bounded
         delegation, cleanup, and secret-free output without network or MongoDB.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_developer_persona_operator.py
COLLABORATION / OWNERSHIP: Test-only certificate for
                           tools/eos/cli/developer_persona.py; production auth,
                           provisioner, Kernel DB, and financial surfaces remain
                           read-only.
CERTIFICATION / UPDATE DATE: 2026-09-24
CHANGELOG:
  v1.0.0-D15G-DEV-LEGAL-PERSONA-OPERATOR-CERT — Establishes direct evidence
    for explicit non-production enablement, non-secret CLI arguments, hidden
    password/TOTP collection, canonical owner authentication, MFA requirement,
    exact tenant match, ACTIVE PrincipalAuthority, provisioner delegation,
    cleanup on success/failure, bounded stderr, and absence of token/session/
    refresh or financial execution authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001 awareness.
SECURITY / PRIVACY POSTURE: Synthetic values only. No network, MongoDB, real
                            credential, OTP provider, or password blocklist
                            provider is contacted.
TENANT BOUNDARY: The fake durable user must match the explicit tenant selector;
                 cross-tenant admission fails before target persona input.
AUTHORITY BOUNDARY: Certificate only; no auth or legal persona authority is
                    created. All mutation is replaced with deterministic fakes.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial
                              execution authority.
"""

from __future__ import annotations

import ast
from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

import tools.eos.cli.developer_persona as mod
from tools.eos.auth.developer_persona_provisioner import (
    DeveloperLegalPersona,
    DeveloperPersonaProvisioningCode,
    DeveloperPersonaProvisioningError,
    DeveloperPersonaProvisioningResult,
)
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus


EXPECTED_VERSION = "v1.0.0-D15G-DEV-LEGAL-PERSONA-OPERATOR"
CERT_VERSION = "v1.0.0-D15G-DEV-LEGAL-PERSONA-OPERATOR-CERT"
TENANT = "TENANT-D15G-OPERATOR"
OWNER_ID = "OWNER-D15G-OPERATOR"
OWNER_EMAIL = "owner@example.invalid"
OWNER_PASSWORD = "owner synthetic password"
OWNER_OTP = "123456"
PERSONA_EMAIL = "persona@example.invalid"
PERSONA_PASSWORD = "persona synthetic passphrase"


class FakeChecker:
    """Marker blocklist object with no external capability."""

    pass


class FakeRegistry:
    """Record canonical password and TOTP authentication calls."""

    def __init__(self, harness: "Harness") -> None:
        self.harness = harness

    def authenticate(self, email: str, password: str) -> Any:
        self.harness.events.append(("authenticate", email, password))
        return self.harness.user

    def verify_otp(self, user_id: str, code: str) -> bool:
        self.harness.events.append(("verify_otp", user_id, code))
        return self.harness.otp_valid


class Harness:
    """Deterministic operator dependency graph."""

    def __init__(self) -> None:
        self.events: list[tuple[Any, ...]] = []
        self.connect_ok = True
        self.disconnect_calls = 0
        self.otp_valid = True
        self.user: Any = SimpleNamespace(
            id=OWNER_ID,
            tenantId=TENANT,
            mfaRegistered=True,
            email=OWNER_EMAIL,
        )
        self.principal: PrincipalAuthority | None = PrincipalAuthority(
            OWNER_ID,
            PrincipalStatus.ACTIVE,
            0,
        )
        self.provision_error: DeveloperPersonaProvisioningError | None = None
        self.provision_calls: list[dict[str, Any]] = []

    def result(self, persona: DeveloperLegalPersona) -> DeveloperPersonaProvisioningResult:
        """Return one synthetic committed provisioner result."""
        return DeveloperPersonaProvisioningResult(
            principal_id="PERSONA-D15G-1",
            tenant_id=TENANT,
            persona=persona,
            business_role="tenant_legal_partner",
            authorization_role="LEGAL_PARTNER",
            credential_revision=0,
            mfa_enrollment_required=True,
        )


@pytest.fixture()
def harness(monkeypatch: pytest.MonkeyPatch) -> Harness:
    """Install deterministic DB, auth, principal, blocklist, and provisioner seams."""
    h = Harness()

    def connect_db() -> tuple[bool, str]:
        h.events.append(("connect_db",))
        return h.connect_ok, "synthetic"

    def disconnect_db() -> None:
        h.disconnect_calls += 1
        h.events.append(("disconnect_db",))

    class RegistryFactory:
        def __new__(cls) -> FakeRegistry:
            return FakeRegistry(h)

    class PrincipalRepo:
        @staticmethod
        def resolve(principal_id: str) -> PrincipalAuthority:
            h.events.append(("principal.resolve", principal_id))
            if h.principal is None:
                raise mod.PrincipalAuthorityNotFoundError("synthetic")
            return h.principal

    def provision(**kwargs: Any) -> DeveloperPersonaProvisioningResult:
        h.events.append(("provision",))
        h.provision_calls.append(kwargs)
        if h.provision_error is not None:
            raise h.provision_error
        return h.result(kwargs["persona"])

    monkeypatch.setattr(mod, "connect_db", connect_db)
    monkeypatch.setattr(mod, "disconnect_db", disconnect_db)
    monkeypatch.setattr(mod, "AuthRegistry", RegistryFactory)
    monkeypatch.setattr(mod, "PrincipalAuthorityRepository", PrincipalRepo)
    monkeypatch.setattr(mod, "PwnedPasswordBlocklistChecker", FakeChecker)
    monkeypatch.setattr(mod, "provision_developer_legal_persona", provision)
    monkeypatch.setenv("ENV", "development")
    monkeypatch.setenv("WILSY_DEVELOPER_PERSONA_PROVISIONING", "1")
    return h


def _install_prompts(
    monkeypatch: pytest.MonkeyPatch,
    *,
    inputs: list[str] | None = None,
    secrets: list[str] | None = None,
) -> None:
    """Install exact ordered visible and hidden prompt responses."""
    input_values = iter(inputs or [OWNER_EMAIL, PERSONA_EMAIL, "Legal", "Partner"])
    secret_values = iter(
        secrets
        or [OWNER_PASSWORD, OWNER_OTP, PERSONA_PASSWORD, PERSONA_PASSWORD]
    )
    monkeypatch.setattr("builtins.input", lambda _label: next(input_values))
    monkeypatch.setattr(mod, "getpass", lambda _label: next(secret_values))


def _run(
    harness: Harness,
    monkeypatch: pytest.MonkeyPatch,
    *,
    persona: str = "LEGAL_PARTNER",
) -> dict[str, object]:
    """Run one successful synthetic operator invocation."""
    _install_prompts(monkeypatch)
    return mod.run(["--tenant-id", TENANT, "--persona", persona])


def test_version_parser_and_public_surface_are_exact() -> None:
    """Freeze version, non-secret CLI inputs, and exported public API."""
    assert mod.VERSION == EXPECTED_VERSION
    parser = mod.build_parser()
    option_strings = {
        option
        for action in parser._actions
        for option in action.option_strings
    }
    assert option_strings == {"-h", "--help", "--tenant-id", "--persona"}
    assert "--password" not in option_strings
    assert "--otp" not in option_strings
    assert "--owner-email" not in option_strings
    assert "--persona-email" not in option_strings
    assert set(mod.__all__) == {
        "DeveloperPersonaOperatorCode",
        "DeveloperPersonaOperatorError",
        "VERSION",
        "build_parser",
        "main",
        "run",
    }


@pytest.mark.parametrize(
    ("environment", "flag"),
    [
        ("production", "1"),
        ("prod", "1"),
        ("", "1"),
        ("development", "0"),
        ("development", ""),
    ],
)
def test_environment_denies_before_db_or_prompt(
    harness: Harness,
    monkeypatch: pytest.MonkeyPatch,
    environment: str,
    flag: str,
) -> None:
    """Production or missing feature enablement fails before DB and secrets."""
    monkeypatch.setenv("ENV", environment)
    monkeypatch.setenv("WILSY_DEVELOPER_PERSONA_PROVISIONING", flag)
    with pytest.raises(mod.DeveloperPersonaOperatorError) as caught:
        mod.run(["--tenant-id", TENANT, "--persona", "LEGAL_PARTNER"])
    assert caught.value.code is mod.DeveloperPersonaOperatorCode.ENVIRONMENT_DENIED
    assert harness.events == []
    assert harness.disconnect_calls == 0


def test_connection_failure_collects_no_credentials_and_never_disconnects(
    harness: Harness,
) -> None:
    """Unavailable canonical DB fails before owner credential collection."""
    harness.connect_ok = False
    with pytest.raises(mod.DeveloperPersonaOperatorError) as caught:
        mod.run(["--tenant-id", TENANT, "--persona", "LEGAL_PARTNER"])
    assert caught.value.code is mod.DeveloperPersonaOperatorCode.DATABASE_UNAVAILABLE
    assert harness.events == [("connect_db",)]
    assert harness.disconnect_calls == 0


def test_success_authenticates_owner_then_delegates_exact_inputs_and_cleans_up(
    harness: Harness,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Success proves password+TOTP auth, ACTIVE principal, delegation, and cleanup."""
    result = _run(harness, monkeypatch)

    assert [event[0] for event in harness.events] == [
        "connect_db",
        "authenticate",
        "verify_otp",
        "principal.resolve",
        "provision",
        "disconnect_db",
    ]
    assert harness.events[1] == ("authenticate", OWNER_EMAIL, OWNER_PASSWORD)
    assert harness.events[2] == ("verify_otp", OWNER_ID, OWNER_OTP)
    assert harness.events[3] == ("principal.resolve", OWNER_ID)
    assert harness.disconnect_calls == 1
    assert len(harness.provision_calls) == 1

    call = harness.provision_calls[0]
    identity = call["owner_identity"]
    assert identity.identity_id == OWNER_ID
    assert identity.tenant_id == TENANT
    assert identity.status is PrincipalStatus.ACTIVE
    assert identity.roles == []
    assert identity.permissions == []
    assert call["tenant_id"] == TENANT
    assert call["email"] == PERSONA_EMAIL
    assert call["password"] == PERSONA_PASSWORD
    assert call["first_name"] == "Legal"
    assert call["last_name"] == "Partner"
    assert call["persona"] is DeveloperLegalPersona.LEGAL_PARTNER
    assert isinstance(call["password_blocklist_checker"], FakeChecker)
    assert isinstance(call["auth_registry"], FakeRegistry)

    assert result == {
        "status": "CREATED",
        "principal_id": "PERSONA-D15G-1",
        "tenant_id": TENANT,
        "persona": "LEGAL_PARTNER",
        "business_role": "tenant_legal_partner",
        "authorization_role": "LEGAL_PARTNER",
        "credential_revision": 0,
        "mfa_enrollment_required": True,
    }
    rendered = repr(result)
    assert OWNER_PASSWORD not in rendered
    assert OWNER_OTP not in rendered
    assert PERSONA_PASSWORD not in rendered


def test_invalid_owner_password_fails_before_mfa_or_target_inputs(
    harness: Harness,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Credential failure cannot fall through to MFA or persona creation."""
    harness.user = None
    _install_prompts(
        monkeypatch,
        inputs=[OWNER_EMAIL],
        secrets=[OWNER_PASSWORD],
    )
    with pytest.raises(mod.DeveloperPersonaOperatorError) as caught:
        mod.run(["--tenant-id", TENANT, "--persona", "LEGAL_PARTNER"])
    assert caught.value.code is mod.DeveloperPersonaOperatorCode.OWNER_AUTHENTICATION_FAILED
    assert [event[0] for event in harness.events] == [
        "connect_db",
        "authenticate",
        "disconnect_db",
    ]
    assert harness.disconnect_calls == 1
    assert harness.provision_calls == []


def test_tenant_mismatch_fails_before_mfa_or_target_inputs(
    harness: Harness,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Durable user tenant cannot be redirected by the CLI selector."""
    harness.user.tenantId = "FOREIGN-TENANT"
    _install_prompts(
        monkeypatch,
        inputs=[OWNER_EMAIL],
        secrets=[OWNER_PASSWORD],
    )
    with pytest.raises(mod.DeveloperPersonaOperatorError) as caught:
        mod.run(["--tenant-id", TENANT, "--persona", "LEGAL_PARTNER"])
    assert caught.value.code is mod.DeveloperPersonaOperatorCode.OWNER_TENANT_MISMATCH
    assert [event[0] for event in harness.events] == [
        "connect_db",
        "authenticate",
        "disconnect_db",
    ]
    assert harness.provision_calls == []


def test_missing_mfa_enrollment_fails_before_totp_and_target_inputs(
    harness: Harness,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Operator never creates or bypasses MFA for the owner."""
    harness.user.mfaRegistered = False
    _install_prompts(
        monkeypatch,
        inputs=[OWNER_EMAIL],
        secrets=[OWNER_PASSWORD],
    )
    with pytest.raises(mod.DeveloperPersonaOperatorError) as caught:
        mod.run(["--tenant-id", TENANT, "--persona", "LEGAL_PARTNER"])
    assert caught.value.code is mod.DeveloperPersonaOperatorCode.OWNER_MFA_REQUIRED
    assert not any(event[0] == "verify_otp" for event in harness.events)
    assert harness.provision_calls == []


@pytest.mark.parametrize("otp", ["12345", "abcdef", "654321"])
def test_invalid_or_rejected_totp_fails_before_principal_and_provisioning(
    harness: Harness,
    monkeypatch: pytest.MonkeyPatch,
    otp: str,
) -> None:
    """Malformed or rejected TOTP cannot reach owner authority or mutation."""
    if otp == "654321":
        harness.otp_valid = False
    _install_prompts(
        monkeypatch,
        inputs=[OWNER_EMAIL],
        secrets=[OWNER_PASSWORD, otp],
    )
    with pytest.raises(mod.DeveloperPersonaOperatorError) as caught:
        mod.run(["--tenant-id", TENANT, "--persona", "LEGAL_PARTNER"])
    assert caught.value.code is mod.DeveloperPersonaOperatorCode.OWNER_MFA_FAILED
    assert not any(event[0] == "principal.resolve" for event in harness.events)
    assert harness.provision_calls == []


def test_missing_or_inactive_durable_principal_fails_closed(
    harness: Harness,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Authenticated credential projection never substitutes for durable principal truth."""
    harness.principal = None
    _install_prompts(monkeypatch)
    with pytest.raises(mod.DeveloperPersonaOperatorError) as missing:
        mod.run(["--tenant-id", TENANT, "--persona", "LEGAL_PARTNER"])
    assert missing.value.code is mod.DeveloperPersonaOperatorCode.OWNER_PRINCIPAL_UNAVAILABLE
    assert harness.provision_calls == []

    harness.events.clear()
    harness.principal = PrincipalAuthority(
        OWNER_ID,
        PrincipalStatus.SUSPENDED,
        1,
    )
    _install_prompts(monkeypatch)
    with pytest.raises(mod.DeveloperPersonaOperatorError) as inactive:
        mod.run(["--tenant-id", TENANT, "--persona", "LEGAL_PARTNER"])
    assert inactive.value.code is mod.DeveloperPersonaOperatorCode.OWNER_PRINCIPAL_INACTIVE
    assert harness.provision_calls == []


def test_persona_password_confirmation_mismatch_stops_before_provisioning(
    harness: Harness,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Target credential mismatch never reaches the provisioner."""
    _install_prompts(
        monkeypatch,
        secrets=[
            OWNER_PASSWORD,
            OWNER_OTP,
            PERSONA_PASSWORD,
            "different confirmation",
        ],
    )
    with pytest.raises(mod.DeveloperPersonaOperatorError) as caught:
        mod.run(["--tenant-id", TENANT, "--persona", "LEGAL_PARTNER"])
    assert caught.value.code is mod.DeveloperPersonaOperatorCode.PASSWORD_CONFIRMATION_MISMATCH
    assert harness.provision_calls == []
    assert harness.disconnect_calls == 1


def test_provisioner_failure_is_bounded_and_database_is_disconnected(
    harness: Harness,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Provisioner diagnostics are not rendered through the local operator."""
    harness.provision_error = DeveloperPersonaProvisioningError(
        DeveloperPersonaProvisioningCode.PERSISTENCE_FAILURE
    )
    _install_prompts(monkeypatch)
    with pytest.raises(mod.DeveloperPersonaOperatorError) as caught:
        mod.run(["--tenant-id", TENANT, "--persona", "LEGAL_PARTNER"])
    assert caught.value.code is mod.DeveloperPersonaOperatorCode.PROVISIONING_FAILED
    assert str(caught.value) == caught.value.code.value
    assert harness.disconnect_calls == 1


def test_main_emits_only_stable_bounded_errors(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """CLI stderr cannot reveal exception diagnostics or transient secrets."""
    secret = "PRIVATE-DIAGNOSTIC-SECRET"

    def bounded(_argv: Any = None) -> dict[str, object]:
        raise mod.DeveloperPersonaOperatorError(
            mod.DeveloperPersonaOperatorCode.OWNER_MFA_FAILED
        )

    monkeypatch.setattr(mod, "run", bounded)
    assert mod.main([]) == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert output.err.strip() == mod.DeveloperPersonaOperatorCode.OWNER_MFA_FAILED.value

    def unexpected(_argv: Any = None) -> dict[str, object]:
        raise RuntimeError(secret)

    monkeypatch.setattr(mod, "run", unexpected)
    assert mod.main([]) == 3
    output = capsys.readouterr()
    assert output.out == ""
    assert output.err.strip() == mod.DeveloperPersonaOperatorCode.UNEXPECTED_FAILURE.value
    assert secret not in output.err


def test_error_object_and_result_contract_have_no_secret_fields() -> None:
    """Stable operator errors and delegated result model contain no credential state."""
    error = mod.DeveloperPersonaOperatorError(
        mod.DeveloperPersonaOperatorCode.INPUT_INVALID
    )
    assert vars(error) == {
        "code": mod.DeveloperPersonaOperatorCode.INPUT_INVALID
    }
    assert str(error) == mod.DeveloperPersonaOperatorCode.INPUT_INVALID.value
    assert "password" not in repr(error).lower()
    result_fields = {field.name for field in fields(DeveloperPersonaProvisioningResult)}
    assert {"password", "password_hash", "otp", "token", "refresh_token"}.isdisjoint(
        result_fields
    )


def test_source_excludes_secret_arguments_token_issuance_http_and_financial_authority() -> None:
    """Static evidence freezes the intended local-only, non-token boundary."""
    source_path = Path(mod.__file__).resolve()
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(source_path))

    string_literals = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    assert "--password" not in string_literals
    assert "--otp" not in string_literals
    assert "--owner-email" not in string_literals
    assert "--persona-email" not in string_literals

    called_attributes = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert {
        "create_session",
        "generate_jwt",
        "generate_access_jwt",
        "generate_pre_auth_jwt",
        "generate_refresh_token",
        "create_otp_secret",
        "get_otp_uri",
        "update_user",
    }.isdisjoint(called_attributes)

    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)
    assert not any(module.startswith("fastapi") for module in imported_modules)
    assert not any(".billing" in module for module in imported_modules)
    assert not any("kennel" in module.lower() for module in imported_modules)


def test_structural_sovereign_contract_is_exact() -> None:
    """Freeze institutional header, version agreement, and end seal."""
    source = Path(mod.__file__).read_text(encoding="utf-8")
    for field in (
        "TITLE:",
        "VERSION:",
        "AUTHORITY:",
        "EPITOME:",
        "ABSOLUTE CANONICAL PATH:",
        "COLLABORATION / OWNERSHIP:",
        "CERTIFICATION / UPDATE DATE:",
        "CHANGELOG:",
        "COMPLIANCE:",
        "SECURITY / PRIVACY POSTURE:",
        "TENANT BOUNDARY:",
        "AUTHORITY BOUNDARY:",
        "FINANCIAL AUTHORITY BOUNDARY:",
    ):
        assert field in source
    assert source.count(EXPECTED_VERSION) == 4
    forbidden_placeholder = "TO" + "DO"
    forbidden_fix_marker = "FIX" + "ME"
    assert forbidden_placeholder not in source
    assert forbidden_fix_marker not in source
    assert source.rstrip().endswith("# END OF WILSY OS SOVEREIGN ARTIFACT")
    assert CERT_VERSION in Path(__file__).read_text(encoding="utf-8")


# ARTIFACT: tests/unit/test_developer_persona_operator.py
# VERSION: v1.0.0-D15G-DEV-LEGAL-PERSONA-OPERATOR-CERT
# AUTHORITY BOUNDARY: direct offline evidence for the local development operator only
# TENANT POSTURE: exact authenticated-owner tenant binding before target persona input
# FAIL-CLOSED POSTURE: environment, DB, password, MFA, tenant, principal, confirmation, and provisioning failures deny
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
