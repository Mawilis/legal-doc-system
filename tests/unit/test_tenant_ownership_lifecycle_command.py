"""Unit certification for Issue #300 lifecycle command admission boundaries."""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth.tenant_ownership_lifecycle_command import (
    TenantOwnershipLifecycleCommand,
    TenantOwnershipLifecycleCommandError,
)
from tools.eos.auth.tenant_ownership_verifier import (
    TenantOwnershipOperation,
    TenantOwnershipVerificationError,
    TenantOwnershipVerificationRequest,
    UnavailableTenantOwnershipEvidenceVerifier,
    VerifiedTenantOwnershipEvidence,
)


class _Session:
    def in_transaction(self) -> bool:
        return True


class _TrustRoots:
    def current(self, trust_root_reference: str, *, at: Any, session: Any) -> object | None:
        return None


class _Registry:
    def __init__(self, current: object = None) -> None:
        self.current_value = current
        self.current_reads = 0
        self.appends = 0

    def current(self, *, tenant_id: str, session: Any) -> object:
        self.current_reads += 1
        return self.current_value

    def append(self, **kwargs: Any) -> object:
        self.appends += 1
        return object()


class _GenesisAuthorizer:
    def __init__(self, authorized: bool = True) -> None:
        self.authorized = authorized
        self.calls = 0

    def authorize_pretenant_provisioner(self, **kwargs: Any) -> object:
        self.calls += 1
        return SimpleNamespace(authorized=self.authorized)


class _Authorizer:
    def __init__(self, authorized: bool) -> None:
        self.authorized = authorized
        self.calls = 0

    def authorize_current_owner(self, **kwargs: Any) -> object:
        self.calls += 1
        return SimpleNamespace(authorized=self.authorized)


def _request(
    operation: TenantOwnershipOperation,
    *,
    principal_id: str = "successor-1",
) -> TenantOwnershipVerificationRequest:
    return TenantOwnershipVerificationRequest(
        tenant_id="tenant-1",
        legal_entity_reference="entity-1",
        principal_id=principal_id,
        operation=operation,
        evaluated_at=datetime(2026, 11, 2, tzinfo=timezone.utc),
    )


def _command(
    current: object = None,
    *,
    authorized: bool = True,
) -> tuple[TenantOwnershipLifecycleCommand, _Registry, _Authorizer]:
    registry = _Registry(current)
    authorizer = _Authorizer(authorized)
    command = TenantOwnershipLifecycleCommand(
        verifier=UnavailableTenantOwnershipEvidenceVerifier(),
        registry=registry,  # type: ignore[arg-type]
        transfer_actor_authorizer=authorizer,
        genesis_request_authorizer=_GenesisAuthorizer(),
        trust_root_currentness=_TrustRoots(),
    )
    return command, registry, authorizer


def test_command_rejects_missing_transaction_before_registry_read() -> None:
    command, registry, _ = _command()
    with pytest.raises(TenantOwnershipLifecycleCommandError) as raised:
        command.execute(
            request=_request(TenantOwnershipOperation.TENANT_GENESIS),
            evidence=object(),  # type: ignore[arg-type]
            actor_principal_id="provisioner-1",
            command_id="cmd-1",
            expected_revision=0,
            session=None,
        )
    assert str(raised.value) == "ACTIVE_TRANSACTION_REQUIRED"
    assert registry.current_reads == registry.appends == 0


def test_transfer_requires_exact_current_owner_before_verifier() -> None:
    current = SimpleNamespace(tenant_id="tenant-1", principal_id="owner-1")
    command, registry, authorizer = _command(current)
    with pytest.raises(TenantOwnershipLifecycleCommandError) as raised:
        command.execute(
            request=_request(TenantOwnershipOperation.OWNERSHIP_TRANSFER),
            evidence=object(),
            actor_principal_id="attacker-1",
            command_id="cmd-1",
            expected_revision=1,
            session=_Session(),
        )
    assert str(raised.value) == "ONLY_CURRENT_OWNER_MAY_PROPOSE_TRANSFER"
    assert authorizer.calls == registry.appends == 0


def test_transfer_requires_canonical_authorization_decision() -> None:
    current = SimpleNamespace(tenant_id="tenant-1", principal_id="owner-1")
    command, registry, authorizer = _command(current, authorized=False)
    with pytest.raises(TenantOwnershipLifecycleCommandError) as raised:
        command.execute(
            request=_request(TenantOwnershipOperation.OWNERSHIP_TRANSFER),
            evidence=object(),
            actor_principal_id="owner-1",
            command_id="cmd-1",
            expected_revision=1,
            session=_Session(),
        )
    assert str(raised.value) == "CURRENT_OWNER_TRANSFER_AUTHORIZATION_DENIED"
    assert authorizer.calls == 1
    assert registry.appends == 0


def test_transfer_authorization_does_not_substitute_for_independent_evidence() -> None:
    current = SimpleNamespace(tenant_id="tenant-1", principal_id="owner-1")
    command, registry, authorizer = _command(current, authorized=True)
    with pytest.raises(TenantOwnershipVerificationError) as raised:
        command.execute(
            request=_request(TenantOwnershipOperation.OWNERSHIP_TRANSFER),
            evidence=object(),
            actor_principal_id="owner-1",
            command_id="cmd-1",
            expected_revision=1,
            session=_Session(),
        )
    assert raised.value.code == "VERIFIED_OWNERSHIP_EVIDENCE_REQUIRED"
    assert authorizer.calls == 1
    assert registry.appends == 0


def test_revoked_or_missing_issuer_root_is_rechecked_inside_commit_transaction() -> None:
    current = SimpleNamespace(tenant_id="tenant-1", principal_id="owner-1")
    command, registry, authorizer = _command(current, authorized=True)
    request = _request(TenantOwnershipOperation.OWNERSHIP_TRANSFER, principal_id="successor-1")
    evidence = object.__new__(VerifiedTenantOwnershipEvidence)
    issuer = SimpleNamespace(
        trust_root_reference="issuer-root",
        trust_root_fingerprint="issuer-fingerprint",
        key_id="issuer-key",
        key_revision=1,
        authority_scope="TENANT_OWNERSHIP_ISSUER",
        issuer_identity="independent-issuer",
        not_revoked=True,
    )
    object.__setattr__(evidence, "request", request)
    object.__setattr__(evidence, "issuer_authority", issuer)
    object.__setattr__(evidence, "recovery_authorization", None)
    with pytest.raises(TenantOwnershipVerificationError) as raised:
        command.execute(
            request=request, evidence=evidence,
            actor_principal_id="owner-1", command_id="cmd-root-revoked",
            expected_revision=1, session=_Session(),
        )
    assert raised.value.code == "OWNERSHIP_ISSUER_TRUST_ROOT_NOT_CURRENT"
    assert authorizer.calls == 1
    assert registry.appends == 0


def test_recovery_never_uses_ordinary_transfer_actor_authority() -> None:
    command, registry, authorizer = _command()
    with pytest.raises(TenantOwnershipVerificationError) as raised:
        command.prepare(_request(TenantOwnershipOperation.GOVERNED_RECOVERY))
    assert raised.value.code == "OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE"
    assert authorizer.calls == 0
    assert registry.appends == 0


def test_genesis_requires_existing_pretenant_provisioner_authority() -> None:
    registry = _Registry()
    authorizer = _Authorizer(authorized=True)
    command = TenantOwnershipLifecycleCommand(
        verifier=UnavailableTenantOwnershipEvidenceVerifier(),
        registry=registry,  # type: ignore[arg-type]
        transfer_actor_authorizer=authorizer,
        genesis_request_authorizer=_GenesisAuthorizer(authorized=False),
        trust_root_currentness=_TrustRoots(),
    )
    with pytest.raises(TenantOwnershipLifecycleCommandError) as raised:
        command.execute(
            request=_request(TenantOwnershipOperation.TENANT_GENESIS, principal_id="owner-1"),
            evidence=object(),
            actor_principal_id="unapproved-provisioner",
            command_id="genesis-2",
            expected_revision=0,
            session=_Session(),
        )
    assert str(raised.value) == "PRETENANT_PROVISIONER_AUTHORIZATION_DENIED"
    assert registry.current_reads == registry.appends == 0


def test_genesis_remains_denied_without_independent_issuer() -> None:
    command, registry, authorizer = _command()
    with pytest.raises(TenantOwnershipVerificationError) as raised:
        command.prepare(_request(TenantOwnershipOperation.TENANT_GENESIS, principal_id="owner-1"))
    assert raised.value.code == "OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE"
    assert authorizer.calls == registry.appends == 0
