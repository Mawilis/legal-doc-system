"""Direct certificate for the pure Legal product availability projection.

TITLE: Legal Product Availability Projection Direct Certificate
VERSION: v1.0.0-D22B5-LEGAL-PRODUCT-AVAILABILITY-PROJECTION-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove exact Legal-only identity derivation, lifecycle mapping, lawful
         absence, caller-owned transaction propagation, integrity reproof, and
         fail-closed dependency behavior without MongoDB.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_product_availability_projection.py
COLLABORATION / OWNERSHIP: Bounded dependency doubles certify the D22B5 read
                            projection; real-Mongo certification is a later gate.
CERTIFICATION / UPDATE DATE: 2026-10-10
CHANGELOG: v1.0.0-D22B5-LEGAL-PRODUCT-AVAILABILITY-PROJECTION-CERT establishes
           the direct adversarial certificate for the frozen R6 contract.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque tenant and entitlement evidence.
TENANT BOUNDARY: Every fake read records exact tenant and caller dependencies.
AUTHORITY BOUNDARY: Projection behavior only; no IAM, HTTP, admission, or
                    commercial mutation.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
import inspect
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlementState,
)
from tools.eos.saas.entitlement import legal_product_availability_projection as projection
from tools.eos.saas.entitlement.product_catalogue import (
    TenantProductId,
    get_tenant_product,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import (
    derive_tenant_product_entitlement_id,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    TenantProductEntitlementRegistryError,
    TenantProductEntitlementRegistryNotFoundError,
    TenantProductEntitlementRegistryPersistenceUnavailableError,
    TenantProductEntitlementRegistryPersistedRecordInvalidError,
    TenantProductEntitlementRegistryRetryRequiredError,
    TenantProductEntitlementRegistryTransactionRequiredError,
)


TENANT = "tenant-legal-a"
ENTITLEMENT_ID = derive_tenant_product_entitlement_id(
    TENANT, TenantProductId.LEGAL_OPERATIONS
)


def entitlement(
    state: TenantProductEntitlementState,
    **changes: object,
) -> SimpleNamespace:
    """Build a minimal already-hydrated D22B1-shaped authority value."""
    values: dict[str, object] = {
        "tenant_id": TENANT,
        "entitlement_id": ENTITLEMENT_ID,
        "product_id": TenantProductId.LEGAL_OPERATIONS,
        "lifecycle_state": state,
    }
    values.update(changes)
    return SimpleNamespace(**values)


def invoke(**changes: object) -> projection.LegalProductAvailabilityProjection:
    """Invoke the projection with exact inert persistence/session sentinels."""
    values: dict[str, Any] = {
        "tenant_id": TENANT,
        "history_collection": object(),
        "current_collection": object(),
        "session": object(),
    }
    values.update(changes)
    return projection.resolve_legal_product_availability(**values)


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        (TenantProductEntitlementState.ACTIVE, True),
        (TenantProductEntitlementState.PENDING_SOURCE, False),
        (TenantProductEntitlementState.SUSPENDED, False),
        (TenantProductEntitlementState.REVOKED, False),
    ],
)
def test_exact_lifecycle_availability_mapping(
    monkeypatch: pytest.MonkeyPatch,
    state: TenantProductEntitlementState,
    expected: bool,
) -> None:
    """Only ACTIVE projects availability; every other canonical state does not."""
    monkeypatch.setattr(projection, "get_current", lambda *_a, **_k: entitlement(state))
    result = invoke()
    assert result.available is expected
    assert result.lifecycle_state is state


def test_not_found_is_lawful_absence_with_derived_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exact D22B2 absence projects unavailable without hiding other failures."""
    def absent(*_: object, **__: object) -> object:
        raise TenantProductEntitlementRegistryNotFoundError()

    monkeypatch.setattr(projection, "get_current", absent)
    result = invoke()
    assert result.available is False
    assert result.lifecycle_state is None
    assert result.entitlement_id == ENTITLEMENT_ID
    assert result.product_id is TenantProductId.LEGAL_OPERATIONS


def test_server_derives_exact_legal_identity_and_exposes_no_selector() -> None:
    """The public API cannot accept caller-selected product or entitlement IDs."""
    parameters = inspect.signature(
        projection.resolve_legal_product_availability
    ).parameters
    assert "product_id" not in parameters
    assert "entitlement_id" not in parameters
    assert ENTITLEMENT_ID == derive_tenant_product_entitlement_id(
        TENANT, TenantProductId.LEGAL_OPERATIONS
    )


def test_exact_session_and_collections_are_forwarded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Projection preserves caller transaction and collection object identity."""
    history, current, session = object(), object(), object()
    calls: list[tuple[object, ...]] = []

    def current_read(*args: object, **kwargs: object) -> object:
        calls.append((*args, kwargs["session"]))
        return entitlement(TenantProductEntitlementState.ACTIVE)

    monkeypatch.setattr(projection, "get_current", current_read)
    invoke(history_collection=history, current_collection=current, session=session)
    assert calls == [(TENANT, ENTITLEMENT_ID, history, current, session)]


@pytest.mark.parametrize(
    "changes",
    [
        {"tenant_id": "tenant-foreign"},
        {"entitlement_id": "tpe-wrong"},
        {"product_id": TenantProductId.CRM},
    ],
)
def test_hydrated_authority_mismatch_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    changes: dict[str, object],
) -> None:
    """Foreign tenant, wrong lineage, and non-Legal product never project."""
    monkeypatch.setattr(
        projection,
        "get_current",
        lambda *_a, **_k: entitlement(TenantProductEntitlementState.ACTIVE, **changes),
    )
    with pytest.raises(projection.LegalProductAvailabilityProjectionError) as raised:
        invoke()
    assert raised.value.code == "D22B5_HYDRATED_AUTHORITY_MISMATCH"


@pytest.mark.parametrize(
    "failure",
    [
        TenantProductEntitlementRegistryPersistedRecordInvalidError(),
        TenantProductEntitlementRegistryPersistenceUnavailableError(),
        TenantProductEntitlementRegistryRetryRequiredError(),
        TenantProductEntitlementRegistryTransactionRequiredError(),
        TenantProductEntitlementRegistryError(),
    ],
)
def test_registry_authority_failures_are_wrapped_and_chained(
    monkeypatch: pytest.MonkeyPatch,
    failure: TenantProductEntitlementRegistryError,
) -> None:
    """Corruption, outage, retry, transaction, and base failures remain fatal."""
    def fail(*_: object, **__: object) -> object:
        raise failure

    monkeypatch.setattr(projection, "get_current", fail)
    with pytest.raises(projection.LegalProductAvailabilityProjectionError) as raised:
        invoke()
    assert raised.value.code == "D22B5_REGISTRY_AUTHORITY_FAILURE"
    assert raised.value.__cause__ is failure


@pytest.mark.parametrize("tenant_id", ["", " tenant", "tenant ", "*", "root", "x" * 161])
def test_invalid_tenant_rejects_before_registry_read(
    monkeypatch: pytest.MonkeyPatch,
    tenant_id: str,
) -> None:
    """Malformed or pseudo-tenant input cannot reach durable authority."""
    monkeypatch.setattr(
        projection,
        "get_current",
        lambda *_a, **_k: pytest.fail("registry read occurred"),
    )
    with pytest.raises(projection.LegalProductAvailabilityProjectionError) as raised:
        invoke(tenant_id=tenant_id)
    assert raised.value.code == "D22B5_TENANT_ID_INVALID"


def test_workspace_is_projected_from_canonical_catalogue(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Workspace description is consumed from D22A rather than caller input."""
    monkeypatch.setattr(
        projection,
        "get_current",
        lambda *_a, **_k: entitlement(TenantProductEntitlementState.ACTIVE),
    )
    result = invoke()
    assert result.workspace_key == get_tenant_product(
        TenantProductId.LEGAL_OPERATIONS
    ).workspace_key


def test_result_is_immutable_and_exposes_only_frozen_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Projection contains only the six descriptive fields frozen by R6."""
    monkeypatch.setattr(
        projection,
        "get_current",
        lambda *_a, **_k: entitlement(TenantProductEntitlementState.ACTIVE),
    )
    result = invoke()
    assert {item.name for item in fields(result)} == {
        "tenant_id", "product_id", "workspace_key", "entitlement_id",
        "lifecycle_state", "available",
    }
    with pytest.raises(FrozenInstanceError):
        result.available = False  # type: ignore[misc]


def test_source_has_no_forbidden_authority_or_transaction_surface() -> None:
    """Static certificate excludes other products, HTTP, Mongo, and tx ownership."""
    source = Path(projection.__file__).read_text(encoding="utf-8")
    forbidden = (
        "TenantProductId.CRM", "TenantProductId.BILLING", "TenantProductId.HR",
        "start_transaction", "commit_transaction", "abort_transaction",
        ".find(", ".find_one(", "FastAPI", "APIRouter", "HTTPException",
        "workspace_bootstrap", "LegalAcceptance", "legal_router",
        "product_commercial_feature", "roles", "permission_namespace",
    )
    assert not [token for token in forbidden if token in source]


# ARTIFACT: test_legal_product_availability_projection.py
# VERSION: v1.0.0-D22B5-LEGAL-PRODUCT-AVAILABILITY-PROJECTION-CERT
# AUTHORITY BOUNDARY: direct pure projection certification only; no production authority
# TENANT POSTURE: synthetic exact-tenant dependency propagation and adversarial mismatch proof
# FAIL-CLOSED POSTURE: absence alone is unavailable; corruption and dependency failures remain fatal
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
