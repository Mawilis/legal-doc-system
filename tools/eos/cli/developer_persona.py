#!/usr/bin/env python3
"""Interactive development-only operator for WILSY OS legal personas.

TITLE: WILSY OS Developer Legal Persona Operator
VERSION: v1.0.0-D15G-DEV-LEGAL-PERSONA-OPERATOR
AUTHORITY: Wilsy OS Core Governance
EPITOME: Local interactive operator that authenticates one existing tenant owner
         with canonical password plus durable TOTP, then delegates exactly one
         legal test-principal admission to the certified Python EOS developer
         persona provisioner without placing secrets in shell arguments.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/cli/developer_persona.py
COLLABORATION / OWNERSHIP: Python EOS development tooling owns interactive input
                           and local database lifecycle only; AuthRegistry owns
                           password/TOTP verification and the developer persona
                           provisioner owns admission transaction semantics.
CERTIFICATION / UPDATE DATE: 2026-09-24
CHANGELOG:
  v1.0.0-D15G-DEV-LEGAL-PERSONA-OPERATOR — Establishes an explicitly
    non-production, feature-flagged local operator for creating one certified
    Legal OS development persona. Owner email and all passwords/TOTP values are
    read interactively; password and TOTP secrets are never accepted as command
    arguments, logged, serialized, or returned. Owner authentication uses
    canonical AuthRegistry password verification plus existing durable MFA,
    while final tenant-owner/ENTERPRISE_ADMIN authority is independently
    re-resolved by the provisioner inside its transaction.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001 awareness.
SECURITY / PRIVACY POSTURE: Fails closed outside explicit non-production
                            enablement. Owner password, TOTP, and persona
                            password are transient local values obtained via
                            getpass and never echoed or emitted.
TENANT BOUNDARY: The authenticated owner's canonical tenant must exactly equal
                 the explicit --tenant-id before any target persona inputs are
                 collected. The provisioner revalidates the same tenant and
                 durable owner authority inside its Mongo transaction.
AUTHORITY BOUNDARY: Local development operator only. It cannot grant authority
                    directly, alter the owner, bypass MFA, issue JWT/session/
                    refresh material, expose an HTTP route, or authorize a
                    persona outside the provisioner's governed mappings.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial
                              execution authority.
TRANSACTION BOUNDARY: This operator owns no Mongo transaction. The provisioner
                      exclusively owns the target admission session and
                      with_transaction lifecycle.
"""

from __future__ import annotations

import argparse
from getpass import getpass
import json
import os
import sys
from enum import StrEnum
from typing import Final, Sequence

from tools.eos.auth.developer_persona_provisioner import (
    DeveloperLegalPersona,
    DeveloperPersonaProvisioningError,
    provision_developer_legal_persona,
)
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.kernel.db import connect_db, disconnect_db
from tools.eos.saas.auth.auth_registry import AuthRegistry
from tools.eos.saas.auth.password_blocklist import PwnedPasswordBlocklistChecker


VERSION: Final[str] = "v1.0.0-D15G-DEV-LEGAL-PERSONA-OPERATOR"
_ENABLE_ENV: Final[str] = "WILSY_DEVELOPER_PERSONA_PROVISIONING"
_ALLOWED_ENVIRONMENTS: Final[frozenset[str]] = frozenset(
    {"development", "dev", "local", "test", "testing"}
)
_TRUE_VALUES: Final[frozenset[str]] = frozenset({"1", "true", "yes", "on"})


class DeveloperPersonaOperatorCode(StrEnum):
    """Stable, secret-free local operator failure classifications."""

    ENVIRONMENT_DENIED = "DEVELOPER_PERSONA_OPERATOR_ENVIRONMENT_DENIED"
    DATABASE_UNAVAILABLE = "DEVELOPER_PERSONA_OPERATOR_DATABASE_UNAVAILABLE"
    INPUT_INVALID = "DEVELOPER_PERSONA_OPERATOR_INPUT_INVALID"
    OWNER_AUTHENTICATION_FAILED = "DEVELOPER_PERSONA_OPERATOR_OWNER_AUTHENTICATION_FAILED"
    OWNER_MFA_REQUIRED = "DEVELOPER_PERSONA_OPERATOR_OWNER_MFA_REQUIRED"
    OWNER_MFA_FAILED = "DEVELOPER_PERSONA_OPERATOR_OWNER_MFA_FAILED"
    OWNER_TENANT_MISMATCH = "DEVELOPER_PERSONA_OPERATOR_OWNER_TENANT_MISMATCH"
    OWNER_PRINCIPAL_UNAVAILABLE = "DEVELOPER_PERSONA_OPERATOR_OWNER_PRINCIPAL_UNAVAILABLE"
    OWNER_PRINCIPAL_INACTIVE = "DEVELOPER_PERSONA_OPERATOR_OWNER_PRINCIPAL_INACTIVE"
    PASSWORD_CONFIRMATION_MISMATCH = "DEVELOPER_PERSONA_OPERATOR_PASSWORD_CONFIRMATION_MISMATCH"
    PROVISIONING_FAILED = "DEVELOPER_PERSONA_OPERATOR_PROVISIONING_FAILED"
    UNEXPECTED_FAILURE = "DEVELOPER_PERSONA_OPERATOR_UNEXPECTED_FAILURE"


class DeveloperPersonaOperatorError(RuntimeError):
    """Bounded local operator error containing only a stable code."""

    def __init__(self, code: DeveloperPersonaOperatorCode) -> None:
        """Create one candidate-free, identity-free diagnostic."""
        if not isinstance(code, DeveloperPersonaOperatorCode):
            raise TypeError("developer persona operator code is invalid")
        self.code = code
        super().__init__(code.value)

    def __str__(self) -> str:
        """Return only the stable operator code."""
        return self.code.value

    def __repr__(self) -> str:
        """Return deterministic diagnostics without secret-bearing state."""
        return f"DeveloperPersonaOperatorError(code={self.code.value!r})"


def _require_enabled_nonproduction_environment() -> None:
    """Reject production or absent explicit developer-persona enablement."""
    environment = os.getenv("ENV", "").strip().lower()
    enabled = os.getenv(_ENABLE_ENV, "").strip().lower()
    if environment not in _ALLOWED_ENVIRONMENTS or enabled not in _TRUE_VALUES:
        raise DeveloperPersonaOperatorError(
            DeveloperPersonaOperatorCode.ENVIRONMENT_DENIED
        )


def _required_prompt(label: str) -> str:
    """Read one non-secret trimmed interactive value or fail closed."""
    value = input(label)
    if not isinstance(value, str):
        raise DeveloperPersonaOperatorError(
            DeveloperPersonaOperatorCode.INPUT_INVALID
        )
    value = value.strip()
    if not value:
        raise DeveloperPersonaOperatorError(
            DeveloperPersonaOperatorCode.INPUT_INVALID
        )
    return value


def _secret_prompt(label: str) -> str:
    """Read one non-echoed secret without normalization."""
    value = getpass(label)
    if not isinstance(value, str) or not value:
        raise DeveloperPersonaOperatorError(
            DeveloperPersonaOperatorCode.INPUT_INVALID
        )
    return value


def _authenticate_owner(
    *,
    registry: AuthRegistry,
    tenant_id: str,
) -> SovereignIdentity:
    """Authenticate the local operator and bind identity to durable owner status.

    Authority:
        Password and TOTP verification are delegated to AuthRegistry. This
        helper does not infer owner authorization from credential role claims;
        the provisioner separately requires ACTIVE membership, tenant_owner,
        and ACTIVE ENTERPRISE_ADMIN inside its transaction.

    Tenant scope:
        The durable user tenant must exactly equal the explicit target tenant.

    Mutation semantics:
        None. No JWT, session, refresh token, OTP secret, MFA flag, role,
        membership, or owner authority is created or changed.

    Failure semantics:
        All authentication, tenant, and principal failures collapse to stable
        secret-free operator codes.

    Financial boundary:
        None. Kennel EOS remains exclusive.
    """
    owner_email = _required_prompt("Owner email: ")
    owner_password = _secret_prompt("Owner password: ")
    user = registry.authenticate(owner_email, owner_password)
    if user is None:
        raise DeveloperPersonaOperatorError(
            DeveloperPersonaOperatorCode.OWNER_AUTHENTICATION_FAILED
        )
    if user.tenantId != tenant_id:
        raise DeveloperPersonaOperatorError(
            DeveloperPersonaOperatorCode.OWNER_TENANT_MISMATCH
        )
    if not user.mfaRegistered:
        raise DeveloperPersonaOperatorError(
            DeveloperPersonaOperatorCode.OWNER_MFA_REQUIRED
        )

    otp = _secret_prompt("Owner six-digit MFA code: ")
    if len(otp) != 6 or not otp.isdigit() or not registry.verify_otp(user.id, otp):
        raise DeveloperPersonaOperatorError(
            DeveloperPersonaOperatorCode.OWNER_MFA_FAILED
        )

    try:
        authority = PrincipalAuthorityRepository.resolve(user.id)
    except (PrincipalAuthorityNotFoundError, PrincipalAuthorityRepositoryError) as error:
        raise DeveloperPersonaOperatorError(
            DeveloperPersonaOperatorCode.OWNER_PRINCIPAL_UNAVAILABLE
        ) from error
    if authority.status is not PrincipalStatus.ACTIVE:
        raise DeveloperPersonaOperatorError(
            DeveloperPersonaOperatorCode.OWNER_PRINCIPAL_INACTIVE
        )

    return SovereignIdentity(
        identity_id=authority.principal_id,
        tenant_id=tenant_id,
        username=user.email,
        email=user.email,
        roles=[],
        permissions=[],
        auth_method="LOCAL_DEVELOPER_PERSONA_OPERATOR_PASSWORD_TOTP",
        status=authority.status,
    )


def _collect_persona_inputs() -> tuple[str, str, str, str]:
    """Collect target profile and confirmed prospective password interactively."""
    persona_email = _required_prompt("Persona email: ")
    first_name = _required_prompt("Persona first name: ")
    last_name = _required_prompt("Persona last name: ")
    password = _secret_prompt("Persona password: ")
    confirmation = _secret_prompt("Confirm persona password: ")
    if confirmation != password:
        raise DeveloperPersonaOperatorError(
            DeveloperPersonaOperatorCode.PASSWORD_CONFIRMATION_MISMATCH
        )
    return persona_email, first_name, last_name, password


def build_parser() -> argparse.ArgumentParser:
    """Build the non-secret command-line contract for local persona admission.

    Command-line inputs intentionally contain only tenant and persona selectors.
    Owner identity, target contact/profile data, passwords, and TOTP are
    collected interactively so secrets never need to appear in shell history.
    """
    parser = argparse.ArgumentParser(
        prog="wilsy-developer-persona",
        description=(
            "Provision one development-only Legal OS persona through canonical "
            "owner password+TOTP authentication and Python EOS authority."
        ),
    )
    parser.add_argument(
        "--tenant-id",
        required=True,
        help="Exact canonical tenant_id for the existing owner and target persona.",
    )
    parser.add_argument(
        "--persona",
        required=True,
        choices=[persona.value for persona in DeveloperLegalPersona],
        help="Canonical legal development persona.",
    )
    return parser


def run(argv: Sequence[str] | None = None) -> dict[str, object]:
    """Execute one interactive local development-persona admission.

    Authority:
        Requires explicit non-production enablement, canonical owner
        password+TOTP authentication, ACTIVE PrincipalAuthority, and then the
        provisioner's independent tenant-owner/ENTERPRISE_ADMIN checks.

    Tenant scope:
        The --tenant-id selector must equal the authenticated owner's canonical
        durable user tenant before target persona details are collected.

    Mutation semantics:
        This function initializes the canonical Kernel DB lifecycle, then
        delegates the only target authority mutation to
        provision_developer_legal_persona. It creates no tokens or sessions.

    Idempotency:
        Create-only. Existing credential or authority conflicts are reported as
        failure by the provisioner; this operator does not convert them to
        replay success.

    Transaction ownership:
        None here. The provisioner owns its caller session and complete Mongo
        transaction retry lifecycle.

    Failure semantics:
        Raises DeveloperPersonaOperatorError with stable secret-free codes.
        Provisioner failures are collapsed at this user-facing local boundary
        while retaining their original exception chain internally.

    Financial boundary:
        No financial execution authority. Kennel EOS remains exclusive.
    """
    _require_enabled_nonproduction_environment()
    args = build_parser().parse_args(argv)
    tenant_id = str(args.tenant_id)
    persona_text = str(args.persona)
    if not tenant_id or tenant_id != tenant_id.strip():
        raise DeveloperPersonaOperatorError(
            DeveloperPersonaOperatorCode.INPUT_INVALID
        )
    try:
        persona = DeveloperLegalPersona(persona_text)
    except ValueError as error:
        raise DeveloperPersonaOperatorError(
            DeveloperPersonaOperatorCode.INPUT_INVALID
        ) from error

    connected = False
    try:
        success, _message = connect_db()
        if not success:
            raise DeveloperPersonaOperatorError(
                DeveloperPersonaOperatorCode.DATABASE_UNAVAILABLE
            )
        connected = True
        registry = AuthRegistry()
        owner_identity = _authenticate_owner(
            registry=registry,
            tenant_id=tenant_id,
        )
        persona_email, first_name, last_name, password = _collect_persona_inputs()
        try:
            result = provision_developer_legal_persona(
                owner_identity=owner_identity,
                tenant_id=tenant_id,
                email=persona_email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                persona=persona,
                password_blocklist_checker=PwnedPasswordBlocklistChecker(),
                auth_registry=registry,
            )
        except DeveloperPersonaProvisioningError as error:
            raise DeveloperPersonaOperatorError(
                DeveloperPersonaOperatorCode.PROVISIONING_FAILED
            ) from error
        return {
            "status": "CREATED",
            "principal_id": result.principal_id,
            "tenant_id": result.tenant_id,
            "persona": result.persona.value,
            "business_role": result.business_role,
            "authorization_role": result.authorization_role,
            "credential_revision": result.credential_revision,
            "mfa_enrollment_required": result.mfa_enrollment_required,
        }
    finally:
        if connected:
            disconnect_db()


def main(argv: Sequence[str] | None = None) -> int:
    """Run the local operator and emit only bounded non-secret output.

    Returns zero only after committed persona admission. Bounded operator errors
    print their stable code to stderr; unexpected failures print one generic
    stable code without exception text.
    """
    try:
        result = run(argv)
    except DeveloperPersonaOperatorError as error:
        print(error.code.value, file=sys.stderr)
        return 2
    except Exception:
        print(DeveloperPersonaOperatorCode.UNEXPECTED_FAILURE.value, file=sys.stderr)
        return 3
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DeveloperPersonaOperatorCode",
    "DeveloperPersonaOperatorError",
    "VERSION",
    "build_parser",
    "main",
    "run",
]


# ARTIFACT: tools/eos/cli/developer_persona.py
# VERSION: v1.0.0-D15G-DEV-LEGAL-PERSONA-OPERATOR
# AUTHORITY BOUNDARY: local development operator; canonical auth and provisioner remain authoritative
# TENANT POSTURE: explicit tenant selector must match authenticated owner before target input; provisioner revalidates durable owner scope
# FAIL-CLOSED POSTURE: production, disabled flag, invalid input, auth/MFA/tenant/principal failures, blocklist uncertainty, and provisioning failure deny
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
