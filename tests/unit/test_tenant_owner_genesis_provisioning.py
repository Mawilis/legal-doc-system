"""Focused unit certification for atomic EOS tenant-owner genesis composition."""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth.tenant_owner_genesis_provisioning import (
    TenantOwnerGenesisProvisioningCommand,
    TenantOwnerGenesisProvisioningError,
)
from tools.eos.auth.tenant_ownership_verifier import (
    TenantOwnershipOperation,
    TenantOwnershipVerificationRequest,
    VerifiedTenantOwnershipEvidence,
)


class _Session:
    def __init__(self, active: bool = True) -> None:
        self.active = active

    def in_transaction(self) -> bool:
        return self.active


def _request(*, tenant_id: str = "tenant-genesis-1", principal_id: str = "principal-owner-1"):
    return TenantOwnershipVerificationRequest(
        tenant_id=tenant_id,
        legal_entity_reference="entity-za-1",
        principal_id=principal_id,
        operation=TenantOwnershipOperation.TENANT_GENESIS,
        evaluated_at=datetime(2026, 11, 3, tzinfo=timezone.utc),
    )


def _evidence(request: Any | None = None) -> VerifiedTenantOwnershipEvidence:
    value = object.__new__(VerifiedTenantOwnershipEvidence)
    object.__setattr__(value, "request", request or _request())
    return value


class _Lifecycle:
    def __init__(self, event: object | None = None) -> None:
        self.event = event
        self.calls: list[dict[str, Any]] = []
        self.prepare_calls: list[Any] = []

    def prepare(self, request: Any) -> Any:
        self.prepare_calls.append(request)
        return _evidence(request)

    def execute(self, **kwargs: Any) -> object:
        self.calls.append(kwargs)
        return self.event or SimpleNamespace(
            tenant_id=kwargs["request"].tenant_id,
            legal_entity_reference=kwargs["request"].legal_entity_reference,
            principal_id=kwargs["request"].principal_id,
            operation=kwargs["request"].operation,
            command_id=kwargs["command_id"],
            revision=1,
        )


def _command(monkeypatch: pytest.MonkeyPatch, *, existing_roles: tuple[object, ...] = ()):
    calls: dict[str, Any] = {}
    lifecycle = _Lifecycle()

    def tenant_create(payload: dict[str, Any], *, session: object) -> dict[str, Any]:
        calls["tenant"] = (payload, session)
        return {"success": True, "tenant": SimpleNamespace(tenant_id=payload["tenant_id"])}

    def membership_insert(value: object, collection: object = None, *, session: object = None):
        calls["membership"] = (value, session)
        return value

    def role_insert(value: object, collection: object = None, *, session: object = None):
        calls["role"] = (value, session)
        return value

    def resolve_all(principal_id: str, tenant_id: str, collection: object = None, *, session: object = None):
        calls["resolve_all"] = (principal_id, tenant_id, session)
        return existing_roles

    def record_capacity(value: object, expected_revision: int | None, database: object, *, session: object = None):
        calls["capacity"] = (value, expected_revision, database, session)
        return value

    monkeypatch.setattr(
        "tools.eos.auth.tenant_owner_genesis_provisioning.TenantMembershipRepository.insert",
        staticmethod(membership_insert),
    )
    monkeypatch.setattr(
        "tools.eos.auth.tenant_owner_genesis_provisioning.RoleAssignmentRepository.insert",
        staticmethod(role_insert),
    )
    monkeypatch.setattr(
        "tools.eos.auth.tenant_owner_genesis_provisioning.TenantBusinessRoleRepository.resolve_all",
        staticmethod(resolve_all),
    )
    monkeypatch.setattr(
        "tools.eos.auth.tenant_owner_genesis_provisioning.TenantBusinessRoleRepository.record_capacity_revision",
        staticmethod(record_capacity),
    )
    command = TenantOwnerGenesisProvisioningCommand(
        lifecycle=lifecycle, tenant_create=tenant_create  # type: ignore[arg-type]
    )
    return command, lifecycle, calls


def test_genesis_composes_all_authorities_with_one_caller_session_and_preserves_other_capacity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    legal_partner = SimpleNamespace(business_role="legal_partner")
    command, lifecycle, calls = _command(monkeypatch, existing_roles=(legal_partner,))
    session = _Session()
    database = object()

    result = command.execute(
        request=_request(),
        evidence=_evidence(),
        actor_principal_id="principal-owner-1",
        command_id="owner-genesis-command-1",
        tenant_payload={"name": "Synthetic Legal Entity Ltd"},
        database=database,
        session=session,
    )

    assert result.tenant.tenant_id == "tenant-genesis-1"
    assert result.membership.principal_id == "principal-owner-1"
    assert result.membership.tenant_id == "tenant-genesis-1"
    assert result.authorization_role.role_id == "TENANT_OWNER"
    assert result.business_role.business_role == "tenant_owner"
    assert result.ownership_revision == 1
    assert calls["tenant"][0]["tenant_id"] == "tenant-genesis-1"
    assert calls["tenant"][1] is session
    assert lifecycle.calls[0]["session"] is session
    assert lifecycle.calls[0]["expected_revision"] == 0
    assert calls["membership"][1] is session
    assert calls["role"][1] is session
    assert calls["resolve_all"] == ("principal-owner-1", "tenant-genesis-1", session)
    assert calls["capacity"][1:] == (None, database, session)
    assert legal_partner.business_role == "legal_partner"


def test_genesis_rejects_inactive_or_missing_caller_transaction_before_writes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command, lifecycle, calls = _command(monkeypatch)
    with pytest.raises(TenantOwnerGenesisProvisioningError, match="ACTIVE_CALLER_TRANSACTION_REQUIRED"):
        command.execute(
            request=_request(), evidence=_evidence(),
            actor_principal_id="principal-owner-1", command_id="cmd-1",
            tenant_payload={"name": "Synthetic"}, database=object(), session=_Session(False),
        )
    assert calls == {}
    assert lifecycle.calls == []


def test_genesis_rejects_cross_principal_evidence_before_tenant_write(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command, lifecycle, calls = _command(monkeypatch)
    with pytest.raises(TenantOwnerGenesisProvisioningError, match="VERIFIED_OWNERSHIP_EVIDENCE_REQUIRED"):
        command.execute(
            request=_request(), evidence=_evidence(_request(principal_id="different-principal")),
            actor_principal_id="principal-owner-1", command_id="cmd-1",
            tenant_payload={"name": "Synthetic"}, database=object(), session=_Session(),
        )
    assert calls == {}
    assert lifecycle.calls == []


def test_genesis_rejects_actor_and_payload_tenant_scope_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command, _, calls = _command(monkeypatch)
    with pytest.raises(TenantOwnerGenesisProvisioningError, match="ACTOR_PRINCIPAL_SCOPE_MISMATCH"):
        command.execute(
            request=_request(), evidence=_evidence(),
            actor_principal_id="attacker", command_id="cmd-1",
            tenant_payload={"name": "Synthetic"}, database=object(), session=_Session(),
        )
    with pytest.raises(TenantOwnerGenesisProvisioningError, match="TENANT_ID_SCOPE_MISMATCH"):
        command.execute(
            request=_request(), evidence=_evidence(),
            actor_principal_id="principal-owner-1", command_id="cmd-2",
            tenant_payload={"name": "Synthetic", "tenant_id": "other-tenant"},
            database=object(), session=_Session(),
        )
    assert calls == {}


def test_genesis_rejects_duplicate_owner_capacity_without_overwriting_existing_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing_owner = SimpleNamespace(business_role="tenant_owner")
    command, lifecycle, calls = _command(monkeypatch, existing_roles=(existing_owner,))
    with pytest.raises(TenantOwnerGenesisProvisioningError, match="TENANT_OWNER_CAPACITY_ALREADY_EXISTS"):
        command.execute(
            request=_request(), evidence=_evidence(),
            actor_principal_id="principal-owner-1", command_id="cmd-1",
            tenant_payload={"name": "Synthetic"}, database=object(), session=_Session(),
        )
    assert "membership" in calls and "role" in calls
    assert "capacity" not in calls
    assert lifecycle.calls[0]["session"] is not None


def test_tenant_create_result_must_expose_exact_canonical_tenant_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _Session()
    lifecycle = _Lifecycle()
    command = TenantOwnerGenesisProvisioningCommand(
        lifecycle=lifecycle,
        tenant_create=lambda payload, *, session: {
            "success": True,
            "tenant": SimpleNamespace(display_name="tenant object without canonical id"),
        },
    )
    with pytest.raises(TenantOwnerGenesisProvisioningError, match="TENANT_REGISTRY_SCOPE_MISMATCH"):
        command.execute(
            request=_request(), evidence=_evidence(),
            actor_principal_id="principal-owner-1", command_id="cmd-tenant-shape",
            tenant_payload={"name": "Synthetic"}, database=object(), session=session,
        )
    assert lifecycle.calls == []


def test_genesis_rejects_ownership_event_scope_or_command_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: dict[str, Any] = {}
    bad_event = SimpleNamespace(
        tenant_id="tenant-genesis-1",
        legal_entity_reference="different-entity",
        principal_id="principal-owner-1",
        operation=TenantOwnershipOperation.TENANT_GENESIS,
        command_id="cmd-expected",
        revision=1,
    )
    lifecycle = _Lifecycle(event=bad_event)
    def tenant_create(payload: dict[str, Any], *, session: object) -> dict[str, Any]:
        calls["tenant"] = payload
        return {"success": True, "tenant": SimpleNamespace(tenant_id=payload["tenant_id"])}

    command = TenantOwnerGenesisProvisioningCommand(
        lifecycle=lifecycle,  # type: ignore[arg-type]
        tenant_create=tenant_create,
    )
    with pytest.raises(TenantOwnerGenesisProvisioningError, match="OWNERSHIP_GENESIS_RESULT_MISMATCH"):
        command.execute(
            request=_request(), evidence=_evidence(),
            actor_principal_id="principal-owner-1", command_id="cmd-expected",
            tenant_payload={"name": "Synthetic"}, database=object(), session=_Session(),
        )
    assert "tenant" in calls
    assert len(lifecycle.calls) == 1


def test_genesis_prepare_verifies_before_transaction_and_returns_exact_request_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command, lifecycle, calls = _command(monkeypatch)
    request = _request()
    evidence = command.prepare(request)
    assert evidence.request == request
    assert lifecycle.prepare_calls == [request]
    assert lifecycle.calls == []
    assert calls == {}


def test_genesis_prepare_rejects_non_genesis_before_provider_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command, lifecycle, calls = _command(monkeypatch)
    transfer_request = TenantOwnershipVerificationRequest(
        tenant_id="tenant-genesis-1",
        legal_entity_reference="entity-za-1",
        principal_id="principal-owner-1",
        operation=TenantOwnershipOperation.OWNERSHIP_TRANSFER,
        evaluated_at=datetime(2026, 11, 3, tzinfo=timezone.utc),
    )
    with pytest.raises(TenantOwnerGenesisProvisioningError, match="TENANT_GENESIS_REQUEST_REQUIRED"):
        command.prepare(transfer_request)
    assert lifecycle.prepare_calls == []
    assert lifecycle.calls == []
    assert calls == {}
