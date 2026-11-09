"""WILSY OS platform agreement and selected-capacity certificate.

TITLE: Platform Agreement Applicability Certificate
VERSION: v1.0.0-PLATFORM-ADMISSION-SELECTED-CAPACITY
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Distinguish mandatory platform agreements from product/practice IAM and
prove that a selected GLOBAL capacity is re-read rather than merged.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_acceptance_platform_admission.py
COLLABORATION / OWNERSHIP: LegalAcceptanceService, current membership/capacity
repositories and immutable document/acceptance registries.
UPDATE DATE: 2026-11-09.
CHANGELOG: v1.0.0-PLATFORM-ADMISSION-SELECTED-CAPACITY establishes exact revision,
platform scope, missing-document and caller-session regression evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY: Synthetic identities only; no production credentials.
TENANT / AUTHORITY BOUNDARY: Read-only test doubles, no IAM grants or persistence.
FINANCIAL AUTHORITY: Kennel EOS exclusively.
"""
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.workspace_bootstrap_projection import resolve_workspace_id
from tools.eos.legal_operations.service.legal_acceptance_service import (
    LegalAcceptanceService,
    LegalAcceptanceServiceError,
)


@pytest.fixture
def authority_service(monkeypatch: pytest.MonkeyPatch) -> tuple[LegalAcceptanceService, list[tuple[Any, ...]]]:
    """Supply exact synthetic current authorities and an empty document corpus.

    An empty approved corpus must remain required; no fake acceptance succeeds.
    The call trace proves that the caller's session reaches each authority read.
    """
    calls: list[tuple[Any, ...]] = []

    class Memberships:
        """Read only one independently ACTIVE synthetic membership revision."""

        def resolve(self, principal_id: str, tenant_id: str, *, session: Any = None) -> Any:
            """Return matching identity scope without issuing membership authority."""
            calls.append(("membership", principal_id, tenant_id, session))
            return SimpleNamespace(principal_id=principal_id, tenant_id=tenant_id, status=TenantMembershipStatus.ACTIVE, revision=5)

    class Capacities:
        """Expose exact role lookup while refusing ambiguous legacy resolution."""

        def resolve(self, *_args: Any, **_kwargs: Any) -> Any:
            """Fail if a GLOBAL selected session uses an ambiguous role lookup."""
            raise LegalAcceptanceServiceError("AMBIGUOUS_CAPACITY_LOOKUP_FORBIDDEN")

        def resolve_business_role(self, principal_id: str, tenant_id: str, business_role: str, *, session: Any = None) -> Any:
            """Return only the requested durable role and its independent revision."""
            calls.append(("capacity", principal_id, tenant_id, business_role, session))
            return SimpleNamespace(principal_id=principal_id, tenant_id=tenant_id, business_role=business_role, status=TenantBusinessRoleStatus.ACTIVE, revision=7)

    def tenant(tenant_id: str, *, session: Any = None) -> Any:
        """Preserve the exact selected tenant and caller-owned session."""
        calls.append(("tenant", tenant_id, session))
        return SimpleNamespace(tenant_id=tenant_id)

    service = LegalAcceptanceService(tenant_resolver=tenant, membership_repository=Memberships(), business_role_repository=Capacities())
    monkeypatch.setattr(service.acceptance_registry, "list_for_principal", lambda *_args, **_kwargs: ())
    monkeypatch.setattr(service.document_registry, "approved_for", lambda *_args, **_kwargs: None)
    return service, calls


def selected_identity(role: str = "tenant_owner", **changes: Any) -> SovereignIdentity:
    """Construct a synthetic already-authenticated GLOBAL selected-capacity view."""
    values: dict[str, Any] = dict(identity_id="principal-platform-cert", tenant_id="tenant-platform-cert", roles=[role], auth_method="JWT", status=PrincipalStatus.ACTIVE, principal_scope="GLOBAL", membership_revision=5, capacity_revision=7, workspace_id=resolve_workspace_id(role, tenant_id="tenant-platform-cert"))
    values.update(changes)
    return SovereignIdentity(**values)


@pytest.mark.parametrize("role,admin_required", [("tenant_owner", True), ("tenant_legal_partner", False)])
def test_platform_scope_and_selected_role_preserve_missing_document_gate(authority_service: Any, role: str, admin_required: bool) -> None:
    """An owner and partner retain distinct notice obligations and no practice grant."""
    service, calls = authority_service
    session = object()
    plan = service.status(selected_identity(role), session_id="synthetic-session", session=session)
    assert plan["admissionScope"] == "PLATFORM_WORKSPACE"
    assert plan["status"] == "USER_TERMS_REQUIRED"
    assert plan["documents"] == []
    assert ("ADMIN_RESPONSIBILITY_NOTICE" in plan["missingAgreementTypes"]) is admin_required
    assert calls == [("tenant", "tenant-platform-cert", session), ("membership", "principal-platform-cert", "tenant-platform-cert", session), ("capacity", "principal-platform-cert", "tenant-platform-cert", role, session)]
    assert "permissions" not in plan
    assert "entitlements" not in plan
    assert plan["ownerBinding"]["available"] is False


@pytest.mark.parametrize("changes", [
    {"membership_revision": 4},
    {"capacity_revision": 6},
    {"roles": ["tenant_owner", "tenant_legal_partner"]},
    {"roles": []},
    {"workspace_id": "LEGAL_PRACTICE"},
    {"principal_scope": "UNRECOGNIZED"},
])
def test_stale_or_ambiguous_selected_capacity_never_releases_platform(authority_service: Any, changes: dict[str, Any]) -> None:
    """Scope, revision or workspace divergence must fail before acceptance release."""
    service, _calls = authority_service
    with pytest.raises(LegalAcceptanceServiceError):
        service.status(selected_identity(**changes), session_id="synthetic-session")


# ARTIFACT: test_legal_acceptance_platform_admission.py
# VERSION: v1.0.0-PLATFORM-ADMISSION-SELECTED-CAPACITY
# AUTHORITY BOUNDARY: Synthetic currentness and applicability evidence only.
# TENANT POSTURE: Exact tenant/principal/capacity, no persistence mutation.
# FAIL-CLOSED POSTURE: Missing documents and stale authority never release entry.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
