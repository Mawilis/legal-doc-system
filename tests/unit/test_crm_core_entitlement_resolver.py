"""
TITLE: WILSY OS CRM Core Entitlement Resolver Direct Certificate
VERSION: v1.0.2-P0-CRM-CORE-ENTITLEMENT-RESOLVER-LIFECYCLE-EVIDENCE-DERIVATION-TEST

CHANGELOG:
    - 2026-10-07 v1.0.2-P0-CRM-CORE-ENTITLEMENT-RESOLVER-LIFECYCLE-EVIDENCE-DERIVATION-TEST: freezes ACTIVE lifecycle evidence as lowercase SHA3-512 derived from the exact canonical uppercase SubscriptionEntity proof bytes and binds that digest to activation_evidence_fingerprint. The persisted subscription proof itself remains byte-exact and uppercase; no proof normalization or commercial-authority mutation is allowed.
    - 2026-10-07 v1.0.2-P0-CRM-CORE-ENTITLEMENT-RESOLVER-LIFECYCLE-EVIDENCE-DERIVATION-TEST: converges this direct resolver certificate with the canonical uppercase SHA3-512 SubscriptionEntity proof representation already certified by the crm.core entitlement domain. Resolver production remains unchanged in this test-first delivery.

AUTHORITY:
    Test-first certification of server-derived CRM Core commercial entitlement.

PURPOSE:
    Freeze the resolver boundary before production implementation. The resolver
    must derive entitlement exclusively from canonical tenant-bound subscription
    truth and must never accept caller-asserted subscription, plan, tier or
    feature authority.

SOURCE OF TRUTH:
    SubscriptionRegistry.list_entities(
        authorized tenant,
        authoritative collection,
        caller-owned session,
    )

FAIL-CLOSED POSTURE:
    - zero ACTIVE subscriptions => no entitlement;
    - more than one ACTIVE subscription => ambiguous authority error;
    - exactly one ACTIVE subscription without exact ``crm.core`` => no entitlement;
    - non-ACTIVE subscriptions cannot authorize CRM Core;
    - caller cannot supply subscription_id, plan_id, tier or entitlement boolean.

TRANSACTION POSTURE:
    Resolver forwards the exact caller-owned session and does not start, commit
    or abort MongoDB transactions.

EXECUTION BOUNDARY:
    No mailbox, send, consent, AI-send or financial execution authority.
"""

from __future__ import annotations

import hashlib
from inspect import signature
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.crm.domain.crm_core_entitlement import (
    CRM_CORE_FEATURE_ID,
    CrmCoreEntitlement,
    CrmCoreEntitlementState,
)
from tools.eos.saas.domain.subscription import SubscriptionStatus

from tools.eos.crm.service.crm_core_entitlement_resolver import (
    CrmCoreEntitlementResolverError,
    resolve_crm_core_entitlement,
)


TENANT = "WILSYTENANT-CRM-ENTITLEMENT-001"
SUBSCRIPTION = "WILSYSUB-CRM-CORE-001"
PLAN = "WILSYPLAN-CRM-CORE-001"
CATALOGUE_VERSION = 7
PROOF = "A" * 128
ACTIVATION_EVIDENCE = hashlib.sha3_512(
    PROOF.encode("ascii")
).hexdigest()


class _Session:
    pass


class _Collection:
    pass


def _subscription(
    *,
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE,
    features: tuple[str, ...] = ("crm.core",),
    subscription_id: str = SUBSCRIPTION,
    plan_id: str = PLAN,
    plan_catalogue_version: int = CATALOGUE_VERSION,
    proof_hash: str = PROOF,
) -> Any:
    return SimpleNamespace(
        tenant_id=TENANT,
        subscription_id=subscription_id,
        plan_id=plan_id,
        plan_catalogue_version=plan_catalogue_version,
        plan_features=features,
        status=status,
        proof_hash=proof_hash,
    )



def test_activation_evidence_is_sha3_512_of_exact_canonical_proof_bytes() -> None:
    expected = hashlib.sha3_512(
        PROOF.encode("ascii")
    ).hexdigest()

    assert ACTIVATION_EVIDENCE == expected
    assert len(ACTIVATION_EVIDENCE) == 128
    assert ACTIVATION_EVIDENCE == ACTIVATION_EVIDENCE.lower()
    assert all(
        character in "0123456789abcdef"
        for character in ACTIVATION_EVIDENCE
    )
    assert ACTIVATION_EVIDENCE != PROOF


def test_public_surface_accepts_only_authoritative_inputs() -> None:
    params = signature(resolve_crm_core_entitlement).parameters

    assert tuple(params) == (
        "tenant_id",
        "subscription_collection",
        "session",
    )

    forbidden = {
        "subscription_id",
        "plan_id",
        "plan",
        "tier",
        "feature_id",
        "has_crm_core",
        "entitled",
        "is_entitled",
    }

    assert forbidden.isdisjoint(params)


def test_exact_caller_session_is_forwarded_to_subscription_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _Session()
    collection = _Collection()
    observed: dict[str, Any] = {}

    def fake_list_entities(
        tenant_id_header: str | None = None,
        *,
        collection: Any = None,
        session: Any = None,
    ) -> tuple[Any, ...]:
        observed["tenant"] = tenant_id_header
        observed["collection"] = collection
        observed["session"] = session
        return (_subscription(),)

    monkeypatch.setattr(
        "tools.eos.crm.service.crm_core_entitlement_resolver."
        "SubscriptionRegistry.list_entities",
        fake_list_entities,
    )

    result = resolve_crm_core_entitlement(
        TENANT,
        collection,
        session,
    )

    assert observed == {
        "tenant": TENANT,
        "collection": collection,
        "session": session,
    }

    assert isinstance(result, CrmCoreEntitlement)


def test_zero_active_subscription_denies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "tools.eos.crm.service.crm_core_entitlement_resolver."
        "SubscriptionRegistry.list_entities",
        lambda *args, **kwargs: (),
    )

    assert (
        resolve_crm_core_entitlement(
            TENANT,
            _Collection(),
            _Session(),
        )
        is None
    )


def test_multiple_active_subscriptions_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "tools.eos.crm.service.crm_core_entitlement_resolver."
        "SubscriptionRegistry.list_entities",
        lambda *args, **kwargs: (
            _subscription(
                subscription_id="WILSYSUB-CRM-CORE-A",
            ),
            _subscription(
                subscription_id="WILSYSUB-CRM-CORE-B",
            ),
        ),
    )

    with pytest.raises(
        CrmCoreEntitlementResolverError,
        match="CRM_CORE_ENTITLEMENT_SUBSCRIPTION_AMBIGUOUS",
    ):
        resolve_crm_core_entitlement(
            TENANT,
            _Collection(),
            _Session(),
        )


def test_active_subscription_without_exact_crm_core_denies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "tools.eos.crm.service.crm_core_entitlement_resolver."
        "SubscriptionRegistry.list_entities",
        lambda *args, **kwargs: (
            _subscription(
                features=(
                    "documents.core",
                    "crm.analytics",
                ),
            ),
        ),
    )

    assert (
        resolve_crm_core_entitlement(
            TENANT,
            _Collection(),
            _Session(),
        )
        is None
    )


@pytest.mark.parametrize(
    "status",
    (
        SubscriptionStatus.TRIAL,
        SubscriptionStatus.PAUSED,
        SubscriptionStatus.PAST_DUE,
        SubscriptionStatus.CANCELLED,
        SubscriptionStatus.EXPIRED,
    ),
)
def test_non_active_subscription_never_authorizes(
    monkeypatch: pytest.MonkeyPatch,
    status: SubscriptionStatus,
) -> None:
    monkeypatch.setattr(
        "tools.eos.crm.service.crm_core_entitlement_resolver."
        "SubscriptionRegistry.list_entities",
        lambda *args, **kwargs: (
            _subscription(status=status),
        ),
    )

    assert (
        resolve_crm_core_entitlement(
            TENANT,
            _Collection(),
            _Session(),
        )
        is None
    )


def test_exact_active_crm_core_subscription_binds_entitlement_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _subscription()

    monkeypatch.setattr(
        "tools.eos.crm.service.crm_core_entitlement_resolver."
        "SubscriptionRegistry.list_entities",
        lambda *args, **kwargs: (source,),
    )

    result = resolve_crm_core_entitlement(
        TENANT,
        _Collection(),
        _Session(),
    )

    assert isinstance(result, CrmCoreEntitlement)
    assert result.tenant_id == TENANT
    assert result.feature_id == CRM_CORE_FEATURE_ID
    assert result.subscription_id == SUBSCRIPTION
    assert result.plan_id == PLAN
    assert result.plan_catalogue_version == CATALOGUE_VERSION
    assert result.subscription_proof_hash == PROOF
    assert result.subscription_proof_hash != ACTIVATION_EVIDENCE
    assert (
        result.activation_evidence_fingerprint
        == ACTIVATION_EVIDENCE
    )
    assert (
        result.lifecycle_state
        is CrmCoreEntitlementState.ACTIVE
    )


def test_exact_feature_match_is_case_and_whitespace_sensitive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for features in (
        ("CRM.CORE",),
        ("crm.core ",),
        (" crm.core",),
        ("crm.*",),
        ("*",),
    ):
        monkeypatch.setattr(
            "tools.eos.crm.service.crm_core_entitlement_resolver."
            "SubscriptionRegistry.list_entities",
            lambda *args, _features=features, **kwargs: (
                _subscription(features=_features),
            ),
        )

        assert (
            resolve_crm_core_entitlement(
                TENANT,
                _Collection(),
                _Session(),
            )
            is None
        )


def test_resolver_exposes_no_send_or_financial_execution_surface() -> None:
    forbidden = {
        "send",
        "send_email",
        "execute_payment",
        "settle",
        "charge",
        "authorize_payment",
        "grant_permission",
    }

    assert resolve_crm_core_entitlement.__name__ not in forbidden

    module = __import__(
        "tools.eos.crm.service.crm_core_entitlement_resolver",
        fromlist=["*"],
    )

    public = {
        name
        for name in dir(module)
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(public)


# ARTIFACT: test_crm_core_entitlement_resolver.py
# VERSION: v1.0.2-P0-CRM-CORE-ENTITLEMENT-RESOLVER-LIFECYCLE-EVIDENCE-DERIVATION-TEST
# AUTHORITY SOURCE: canonical tenant subscription snapshot only
# TRANSACTION: exact caller-owned session forwarding
# ZERO ACTIVE: deny
# MULTIPLE ACTIVE: fail closed
# FEATURE: exact crm.core only
# CALLER SUBSCRIPTION / PLAN / TIER / FEATURE ASSERTION: forbidden
# SEND / MAILBOX / CONSENT / AI-SEND AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN CERTIFICATE
