"""Direct certificate for current privileged eligibility."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import cast

import pytest
from pymongo.client_session import ClientSession

import tools.eos.auth.current_privileged_eligibility as current_module
from tools.eos.auth.current_platform_privileged_eligibility_prerequisite import (
    CurrentPlatformPrivilegedEligibilityPrerequisiteResolver,
)
from tools.eos.auth.platform_privileged_eligibility_prerequisite import (
    PlatformPrivilegedEligibilityPrerequisite,
)
from tools.eos.auth.platform_privileged_eligibility_prerequisite_registry import (
    PlatformPrivilegedEligibilityPrerequisiteRegistry,
)
from tools.eos.auth.principal_authority import PrincipalStatus
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityRepository,
)
from tools.eos.auth.privileged_eligibility import (
    ENTERPRISE_ADMIN,
    SOVEREIGN_ARCHITECT,
    evaluate_privileged_eligibility,
)
from tools.eos.auth.privileged_eligibility_evidence import (
    PrivilegedEligibilityEvidence,
)
from tools.eos.auth.privileged_eligibility_evidence_registry import (
    PrivilegedEligibilityEvidenceRegistry,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipRepository,
)
from tools.eos.auth.current_privileged_eligibility import (
    CurrentPrivilegedEligibilityError,
    CurrentPrivilegedEligibilityResolver,
)


AT = datetime(2026, 10, 14, 18, 30, tzinfo=timezone.utc)


class FakeCursor:
    def __init__(self, rows):
        self._rows = list(rows)

    def sort(self, *args, **kwargs):
        return self

    def __iter__(self):
        return iter(self._rows)


class FakeCollection:
    def __init__(self, rows=()):
        self.rows = list(rows)

    def find_one(self, query, session=None):
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return dict(row)
        return None

    def find(self, query, session=None):
        return FakeCursor(
            [
                dict(row)
                for row in self.rows
                if all(
                    row.get(key) == value
                    for key, value in query.items()
                )
            ]
        )


class Session:
    in_transaction = True


def typed_session() -> ClientSession:
    """Static-only adapter for a minimal fake session used by direct tests."""
    return cast(ClientSession, Session())


def prerequisite(
    *,
    source: str = "core-source-1",
) -> PlatformPrivilegedEligibilityPrerequisite:
    return PlatformPrivilegedEligibilityPrerequisite.designate(
        platform_prerequisite_id="platform-prerequisite-1",
        principal_id="principal-root",
        effective_from=AT,
        source_evidence_reference=source,
    )


def platform_evidence(
    current: PlatformPrivilegedEligibilityPrerequisite,
) -> PrivilegedEligibilityEvidence:
    decision = evaluate_privileged_eligibility(
        principal_id="principal-root",
        privileged_role_id=SOVEREIGN_ARCHITECT,
        principal_current=True,
        platform_prerequisite_proven=True,
    )

    return PrivilegedEligibilityEvidence.from_decision(
        eligibility_evidence_id="p2-platform",
        decision=decision,
        evaluated_at=AT,
        idempotency_key="idem-platform",
        platform_prerequisite_id=current.platform_prerequisite_id,
        platform_prerequisite_revision=current.revision,
        platform_prerequisite_fingerprint=current.prerequisite_fingerprint,
        platform_prerequisite_source_evidence_reference=
            current.source_evidence_reference,
    )


def tenant_evidence(
    *,
    workforce_required: bool = False,
) -> PrivilegedEligibilityEvidence:
    decision = evaluate_privileged_eligibility(
        principal_id="principal-tenant",
        privileged_role_id=ENTERPRISE_ADMIN,
        principal_current=True,
        tenant_id="tenant-a",
        tenant_membership_current=True,
        workforce_required=workforce_required,
        tenant_workforce_current=(
            True if workforce_required else None
        ),
    )

    return PrivilegedEligibilityEvidence.from_decision(
        eligibility_evidence_id=(
            "p2-tenant-workforce"
            if workforce_required
            else "p2-tenant"
        ),
        decision=decision,
        evaluated_at=AT,
        idempotency_key=(
            "idem-tenant-workforce"
            if workforce_required
            else "idem-tenant"
        ),
    )


def evidence_registry(
    value: PrivilegedEligibilityEvidence,
) -> PrivilegedEligibilityEvidenceRegistry:
    row = value.to_persisted()
    row["_scope_tenant_key"] = (
        "__PLATFORM__"
        if value.tenant_id is None
        else value.tenant_id
    )
    return PrivilegedEligibilityEvidenceRegistry(
        FakeCollection([row])
    )


def platform_resolver():
    return CurrentPlatformPrivilegedEligibilityPrerequisiteResolver(
        principal_collection=FakeCollection(),
        prerequisite_registry=
            PlatformPrivilegedEligibilityPrerequisiteRegistry(
                FakeCollection()
            ),
    )


def resolver(
    value: PrivilegedEligibilityEvidence,
    *,
    workforce_collection=None,
) -> CurrentPrivilegedEligibilityResolver:
    return CurrentPrivilegedEligibilityResolver(
        principal_collection=FakeCollection(),
        membership_collection=FakeCollection(),
        evidence_registry=evidence_registry(value),
        platform_prerequisite_resolver=platform_resolver(),
        workforce_relationship_collection=workforce_collection,
    )


def active_principal(principal_id: str):
    return SimpleNamespace(
        principal_id=principal_id,
        status=PrincipalStatus.ACTIVE,
    )


def active_membership(principal_id: str, tenant_id: str):
    return SimpleNamespace(
        principal_id=principal_id,
        tenant_id=tenant_id,
        status=TenantMembershipStatus.ACTIVE,
    )


def test_platform_requires_live_exact_lineage(monkeypatch) -> None:
    current = prerequisite()
    value = platform_evidence(current)
    service = resolver(value)

    monkeypatch.setattr(
        service._platform_prerequisite_resolver,
        "resolve",
        lambda **kwargs: current,
    )

    assert service.resolve(
        eligibility_evidence_id=value.eligibility_evidence_id,
        at=AT,
    ) == value


def test_platform_lineage_drift_denies(monkeypatch) -> None:
    original = prerequisite(source="core-source-1")
    current = prerequisite(source="core-source-2")
    value = platform_evidence(original)
    service = resolver(value)

    monkeypatch.setattr(
        service._platform_prerequisite_resolver,
        "resolve",
        lambda **kwargs: current,
    )

    assert service.resolve(
        eligibility_evidence_id=value.eligibility_evidence_id,
        at=AT,
    ) is None


def test_platform_absent_current_prerequisite_denies(monkeypatch) -> None:
    value = platform_evidence(prerequisite())
    service = resolver(value)

    monkeypatch.setattr(
        service._platform_prerequisite_resolver,
        "resolve",
        lambda **kwargs: None,
    )

    assert service.resolve(
        eligibility_evidence_id=value.eligibility_evidence_id,
        at=AT,
    ) is None


def test_legacy_platform_boolean_cannot_be_current(monkeypatch) -> None:
    value = platform_evidence(prerequisite())

    object.__setattr__(value, "platform_prerequisite_id", None)
    object.__setattr__(value, "platform_prerequisite_revision", None)
    object.__setattr__(value, "platform_prerequisite_fingerprint", None)
    object.__setattr__(
        value,
        "platform_prerequisite_source_evidence_reference",
        None,
    )

    monkeypatch.setattr(
        current_module.CurrentPrivilegedEligibilityResolver,
        "_evidence",
        lambda self, **kwargs: value,
    )

    service = CurrentPrivilegedEligibilityResolver(
        principal_collection=FakeCollection(),
        membership_collection=FakeCollection(),
        evidence_registry=PrivilegedEligibilityEvidenceRegistry(
            FakeCollection()
        ),
        platform_prerequisite_resolver=platform_resolver(),
    )

    assert service.resolve(
        eligibility_evidence_id="legacy-p2",
        at=AT,
    ) is None


def test_tenant_rechecks_live_principal_and_membership(
    monkeypatch,
) -> None:
    value = tenant_evidence()
    service = resolver(value)

    monkeypatch.setattr(
        PrincipalAuthorityRepository,
        "get",
        staticmethod(
            lambda principal_id, collection=None, session=None:
                active_principal(principal_id)
        ),
    )

    monkeypatch.setattr(
        TenantMembershipRepository,
        "resolve",
        staticmethod(
            lambda principal_id, tenant_id, collection=None, session=None:
                active_membership(principal_id, tenant_id)
        ),
    )

    assert service.resolve(
        eligibility_evidence_id=value.eligibility_evidence_id,
        at=AT,
    ) == value


def test_snapshot_principal_true_does_not_override_live_inactive(
    monkeypatch,
) -> None:
    value = tenant_evidence()
    service = resolver(value)

    monkeypatch.setattr(
        PrincipalAuthorityRepository,
        "get",
        staticmethod(
            lambda principal_id, collection=None, session=None:
                SimpleNamespace(
                    principal_id=principal_id,
                    status="REVOKED",
                )
        ),
    )

    assert value.principal_current is True
    assert service.resolve(
        eligibility_evidence_id=value.eligibility_evidence_id,
        at=AT,
    ) is None


def test_snapshot_membership_true_does_not_override_live_revoked(
    monkeypatch,
) -> None:
    value = tenant_evidence()
    service = resolver(value)

    monkeypatch.setattr(
        PrincipalAuthorityRepository,
        "get",
        staticmethod(
            lambda principal_id, collection=None, session=None:
                active_principal(principal_id)
        ),
    )

    monkeypatch.setattr(
        TenantMembershipRepository,
        "resolve",
        staticmethod(
            lambda principal_id, tenant_id, collection=None, session=None:
                SimpleNamespace(
                    principal_id=principal_id,
                    tenant_id=tenant_id,
                    status=TenantMembershipStatus.REVOKED,
                )
        ),
    )

    assert value.tenant_membership_current is True
    assert service.resolve(
        eligibility_evidence_id=value.eligibility_evidence_id,
        at=AT,
    ) is None


def test_workforce_required_needs_active_transaction(
    monkeypatch,
) -> None:
    value = tenant_evidence(workforce_required=True)
    service = resolver(
        value,
        workforce_collection=FakeCollection(),
    )

    monkeypatch.setattr(
        PrincipalAuthorityRepository,
        "get",
        staticmethod(
            lambda principal_id, collection=None, session=None:
                active_principal(principal_id)
        ),
    )

    monkeypatch.setattr(
        TenantMembershipRepository,
        "resolve",
        staticmethod(
            lambda principal_id, tenant_id, collection=None, session=None:
                active_membership(principal_id, tenant_id)
        ),
    )

    with pytest.raises(
        CurrentPrivilegedEligibilityError,
        match="WORKFORCE_CURRENTNESS_UNAVAILABLE",
    ):
        service.resolve(
            eligibility_evidence_id=value.eligibility_evidence_id,
            at=AT,
            session=None,
        )


def test_workforce_required_uses_live_currentness(monkeypatch) -> None:
    value = tenant_evidence(workforce_required=True)
    service = resolver(
        value,
        workforce_collection=FakeCollection(),
    )

    monkeypatch.setattr(
        PrincipalAuthorityRepository,
        "get",
        staticmethod(
            lambda principal_id, collection=None, session=None:
                active_principal(principal_id)
        ),
    )

    monkeypatch.setattr(
        TenantMembershipRepository,
        "resolve",
        staticmethod(
            lambda principal_id, tenant_id, collection=None, session=None:
                active_membership(principal_id, tenant_id)
        ),
    )

    monkeypatch.setattr(
        current_module,
        "list_principal_relationships",
        lambda *args, **kwargs: (),
    )

    monkeypatch.setattr(
        current_module,
        "derive_tenant_principal_workforce_currentness",
        lambda relationships, **kwargs:
            SimpleNamespace(
                tenant_id="tenant-a",
                principal_id="principal-tenant",
                observed_at=AT,
                has_active_relationship=True,
            ),
    )

    assert service.resolve(
        eligibility_evidence_id=value.eligibility_evidence_id,
        at=AT,
        session=typed_session(),
    ) == value


def test_workforce_snapshot_true_does_not_override_live_not_current(
    monkeypatch,
) -> None:
    value = tenant_evidence(workforce_required=True)
    service = resolver(
        value,
        workforce_collection=FakeCollection(),
    )

    monkeypatch.setattr(
        PrincipalAuthorityRepository,
        "get",
        staticmethod(
            lambda principal_id, collection=None, session=None:
                active_principal(principal_id)
        ),
    )

    monkeypatch.setattr(
        TenantMembershipRepository,
        "resolve",
        staticmethod(
            lambda principal_id, tenant_id, collection=None, session=None:
                active_membership(principal_id, tenant_id)
        ),
    )

    monkeypatch.setattr(
        current_module,
        "list_principal_relationships",
        lambda *args, **kwargs: (),
    )

    monkeypatch.setattr(
        current_module,
        "derive_tenant_principal_workforce_currentness",
        lambda relationships, **kwargs:
            SimpleNamespace(
                tenant_id="tenant-a",
                principal_id="principal-tenant",
                observed_at=AT,
                has_active_relationship=False,
            ),
    )

    assert value.tenant_workforce_current is True

    assert service.resolve(
        eligibility_evidence_id=value.eligibility_evidence_id,
        at=AT,
        session=typed_session(),
    ) is None


def test_wrong_target_role_or_ineligible_evidence_denies(
    monkeypatch,
) -> None:
    value = tenant_evidence()
    object.__setattr__(value, "eligible", False)

    monkeypatch.setattr(
        current_module.CurrentPrivilegedEligibilityResolver,
        "_evidence",
        lambda self, **kwargs: value,
    )

    service = CurrentPrivilegedEligibilityResolver(
        principal_collection=FakeCollection(),
        membership_collection=FakeCollection(),
        evidence_registry=PrivilegedEligibilityEvidenceRegistry(
            FakeCollection()
        ),
        platform_prerequisite_resolver=platform_resolver(),
    )

    assert service.resolve(
        eligibility_evidence_id="p2-ineligible",
        at=AT,
    ) is None


def test_invalid_identifier_and_naive_time_fail_closed() -> None:
    value = tenant_evidence()
    service = resolver(value)

    with pytest.raises(
        CurrentPrivilegedEligibilityError,
        match="ELIGIBILITY_EVIDENCE_ID_INVALID",
    ):
        service.resolve(
            eligibility_evidence_id="*",
            at=AT,
        )

    with pytest.raises(
        CurrentPrivilegedEligibilityError,
        match="EVALUATED_AT_INVALID",
    ):
        service.resolve(
            eligibility_evidence_id=value.eligibility_evidence_id,
            at=AT.replace(tzinfo=None),
        )


def test_surface_is_read_only_and_non_authorizing() -> None:
    names = set(dir(CurrentPrivilegedEligibilityResolver))

    forbidden = {
        "create",
        "issue",
        "activate",
        "grant",
        "revoke",
        "transition",
        "persist",
        "insert",
        "update",
        "delete",
        "commit",
        "start_transaction",
    }

    assert not (names & forbidden)
    assert {"resolve", "is_current"}.issubset(names)
