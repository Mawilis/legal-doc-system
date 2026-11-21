"""WILSY AI exact-tenant audit and guarded reservation recovery certificate.

TITLE: WILSY OS AI Reconciliation Unit Certificate
VERSION: v1.0.0-EXACT-TENANT-RECONCILIATION-UNIT
AUTHORITY: WILSY OS Core Governance.
EPITOME: Certify bounded evidence joins, identity confinement, state refusal,
         freshness gates, and caller-owned transaction semantics without Mongo.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_usage_reconciliation.py
COLLABORATION / OWNERSHIP: Certifies the single canonical reconciliation audit
                           and admission registry dependency.
CERTIFICATION / UPDATE DATE: 2026-11-21
CHANGELOG: v1.0.0-EXACT-TENANT-RECONCILIATION-UNIT creates deterministic
           direct tests with no provider transport, credentials, or DB writes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic tenant and evidence identities only.
TENANT BOUNDARY: Verify exact tenant-scoped queries and refusal on mismatch.
AUTHORITY BOUNDARY: Audit and admission CAS tests; no provider or financial
                    execution, financial truth, IAM or entitlement creation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Uncertain executions remain held; incomplete evidence
                         and missing confirmation never cause release.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from tools.eos.intelligence.wilsy_ai_usage_reconciliation import (
    WilsyAIReconciliationError,
    audit_exact_tenant,
    release_expired_never_claimed,
)
from tools.eos.saas.domain.wilsy_ai_usage_admission import (
    WilsyAIUsageAdmission,
    WilsyAIUsageAdmissionState,
)

NOW = datetime(2026, 11, 22, 11, 0, tzinfo=timezone.utc)
TENANT = "tenant-reconciliation-cert"
ENTITLEMENT = "wai-" + "a" * 128
CONFIRM = "RELEASE_EXPIRED_UNCLAIMED_ONLY"


def make_admission(
    state: WilsyAIUsageAdmissionState = WilsyAIUsageAdmissionState.RESERVED,
    *,
    admission_id: str = "admission-1",
    reference: str | None = None,
    window_end: datetime | None = None,
) -> WilsyAIUsageAdmission:
    """Create one immutable bounded exact-tenant admission for the test."""
    end = window_end or NOW - timedelta(hours=2)
    return WilsyAIUsageAdmission(
        tenant_id=TENANT,
        admission_id=admission_id,
        idempotency_key="key-" + admission_id,
        entitlement_id=ENTITLEMENT,
        module_id="WILSY_AI_REASONING",
        entitlement_revision=1,
        entitlement_fingerprint="b" * 128,
        window_start=end - timedelta(days=1),
        window_end=end,
        reserved_request_units=1,
        state=state,
        created_at=end - timedelta(hours=2),
        updated_at=end - timedelta(hours=2),
        evidence_reference=reference,
    )


class Cursor:
    """Bounded in-memory Mongo cursor capturing query and projection."""

    def __init__(self, rows: list[dict[str, str]]) -> None:
        self.rows = rows
        self.sort_by = None
        self.limit_to = None

    def sort(self, field: str, order: int) -> "Cursor":
        self.sort_by = (field, order)
        return self

    def limit(self, amount: int) -> "Cursor":
        self.limit_to = amount
        return self

    def __iter__(self):
        return iter(self.rows[:self.limit_to])


class Collection:
    """Record exact tenant and entitlement predicates without persistence."""

    def __init__(self, ids: list[str]) -> None:
        self.ids = ids
        self.last_query: dict | None = None

    def find(self, query: dict, projection: dict, *, session: object):
        self.last_query = query
        return Cursor([{"admission_id": item} for item in self.ids])


class Database:
    """Expose only canonical collection names and a stable database identity."""

    name = "wilsy-reconciliation-cert"

    def __init__(self, ids: list[str]):
        self.admissions = Collection(ids)

    def __getitem__(self, key: str):
        if key == "wilsy_ai_usage_admissions":
            return self.admissions
        return object()


def sources(admissions: dict[str, WilsyAIUsageAdmission]):
    """Patch only repository adapters, not the production decision functions."""
    registry = Mock()
    registry.get.side_effect = lambda *, admission_id, **kwargs: admissions[admission_id]
    registry.transition.side_effect = lambda *, admission_id, **kwargs: replace(
        admissions[admission_id],
        state=kwargs["target_state"],
        evidence_reference=kwargs["evidence_reference"],
        updated_at=kwargs["occurred_at"],
        fingerprint="",
    )
    entitled = Mock()
    entitled.get_by_module.return_value = SimpleNamespace(entitlement_id=ENTITLEMENT)
    invocations = Mock()
    observations = Mock()
    context = [
        patch("tools.eos.intelligence.wilsy_ai_usage_reconciliation.WilsyAIEntitlementRegistry", return_value=entitled),
        patch("tools.eos.intelligence.wilsy_ai_usage_reconciliation.WilsyAIUsageAdmissionRegistry", return_value=registry),
        patch("tools.eos.intelligence.wilsy_ai_usage_reconciliation.AIModelInvocationRegistry", return_value=invocations),
        patch("tools.eos.intelligence.wilsy_ai_usage_reconciliation.WilsyAIUsageObservationRegistry", return_value=observations),
    ]
    return registry, entitled, invocations, observations, context


def test_exact_tenant_audit_counts_held_but_not_completed_or_vendor_billing() -> None:
    """Six unresolved holds must remain distinct from completed/billable work."""
    records = {
        f"admission-{index}": make_admission(
            WilsyAIUsageAdmissionState.RECONCILIATION_REQUIRED,
            admission_id=f"admission-{index}",
            reference=f"invocation-{index}",
        )
        for index in range(6)
    }
    db = Database(list(records))
    registry, entitled, invocations, observations, patches = sources(records)
    invocations.get.side_effect = lambda *, invocation_id, **kw: SimpleNamespace(
        invocation_id=invocation_id, tenant_id=TENANT,
        entitlement_id=ENTITLEMENT, request_units=1,
        fingerprint="c" * 128,
        outcome=SimpleNamespace(value="PROVIDER_UNAVAILABLE"),
    )
    from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import WilsyAIUsageObservationNotFoundError
    observations.get.side_effect = WilsyAIUsageObservationNotFoundError("M13P5B_OBSERVATION_NOT_FOUND")
    from contextlib import ExitStack
    with ExitStack() as stack:
        for item in patches:
            stack.enter_context(item)
        report = audit_exact_tenant(database=db, session=object(), tenant_id=TENANT, observed_at=NOW)
    assert report["held_units"] == 6
    assert report["admission_count"] == 6
    assert report["provider_billing_verified"] is False
    assert all(row["usage_observation"] == "ABSENT" for row in report["rows"])
    assert all(row["disposition"] == "PROVIDER_EVIDENCE_RECONCILIATION_REQUIRED" for row in report["rows"])
    assert db.admissions.last_query["tenant_id"] == TENANT
    assert db.admissions.last_query["entitlement_id"] == ENTITLEMENT
    assert invocations.get.call_count == 6
    assert observations.get.call_count == 6
    registry.transition.assert_not_called()


def test_bounded_exact_tenant_audit_refuses_oversized_source() -> None:
    """Never silently sample a source and report partial totals as final."""
    db = Database(["admission-1", "admission-2"])
    registry, entitled, invocations, observations, patches = sources({})
    from contextlib import ExitStack
    with ExitStack() as stack:
        for item in patches:
            stack.enter_context(item)
        with pytest.raises(WilsyAIReconciliationError, match="AUDIT_BOUND_EXCEEDED"):
            audit_exact_tenant(database=db, session=object(), tenant_id=TENANT, observed_at=NOW, max_admissions=1)
    registry.get.assert_not_called()
    registry.transition.assert_not_called()


@pytest.mark.parametrize("state", [
    WilsyAIUsageAdmissionState.CLAIMED,
    WilsyAIUsageAdmissionState.RECONCILIATION_REQUIRED,
    WilsyAIUsageAdmissionState.COMPLETED,
    WilsyAIUsageAdmissionState.RELEASED,
])
def test_uncertain_or_completed_execution_never_releases(state) -> None:
    """Only RESERVED, never provider-admitted or completed work, can release."""
    item = make_admission(state, reference="invocation-1")
    registry, entitled, invocations, observations, patches = sources({item.admission_id: item})
    from contextlib import ExitStack
    with ExitStack() as stack:
        for part in patches:
            stack.enter_context(part)
        with pytest.raises(WilsyAIReconciliationError, match="RELEASE_INELIGIBLE"):
            release_expired_never_claimed(
                database=Database([]), session=object(), tenant_id=TENANT,
                admission_id=item.admission_id, expected_fingerprint=item.fingerprint,
                observed_at=NOW, confirmation=CONFIRM,
            )
    registry.transition.assert_not_called()


def test_expired_never_claimed_requires_explicit_confirmation_and_exact_hash() -> None:
    """State and hash comparisons prevent accidental or stale-release recovery."""
    item = make_admission()
    registry, entitled, invocations, observations, patches = sources({item.admission_id: item})
    from contextlib import ExitStack
    with ExitStack() as stack:
        for part in patches:
            stack.enter_context(part)
        with pytest.raises(WilsyAIReconciliationError, match="NOT_CONFIRMED"):
            release_expired_never_claimed(
                database=Database([]), session=object(), tenant_id=TENANT,
                admission_id=item.admission_id, expected_fingerprint=item.fingerprint,
                observed_at=NOW, confirmation="",
            )
        with pytest.raises(WilsyAIReconciliationError, match="RELEASE_INELIGIBLE"):
            release_expired_never_claimed(
                database=Database([]), session=object(), tenant_id=TENANT,
                admission_id=item.admission_id, expected_fingerprint="f" * 128,
                observed_at=NOW, confirmation=CONFIRM,
            )
        released_hash = release_expired_never_claimed(
            database=Database([]), session=object(), tenant_id=TENANT,
            admission_id=item.admission_id, expected_fingerprint=item.fingerprint,
            observed_at=NOW, confirmation=CONFIRM,
        )
    assert len(released_hash) == 128
    registry.transition.assert_called_once()
    args = registry.transition.call_args.kwargs
    assert args["tenant_id"] == TENANT
    assert args["target_state"] is WilsyAIUsageAdmissionState.RELEASED


def test_nonexpired_or_cross_tenant_records_are_never_released() -> None:
    """No dynamic alias or tenant switching can grant an admission release."""
    item = make_admission(window_end=NOW + timedelta(hours=1))
    registry, entitled, invocations, observations, patches = sources({item.admission_id: item})
    from contextlib import ExitStack
    with ExitStack() as stack:
        for part in patches:
            stack.enter_context(part)
        with pytest.raises(WilsyAIReconciliationError, match="RELEASE_INELIGIBLE"):
            release_expired_never_claimed(
                database=Database([]), session=object(), tenant_id=TENANT,
                admission_id=item.admission_id, expected_fingerprint=item.fingerprint,
                observed_at=NOW, confirmation=CONFIRM,
            )
        other = replace(item, tenant_id="tenant-foreign-cert", fingerprint="")
        registry.get.return_value = other
        registry.get.side_effect = None
        with pytest.raises(WilsyAIReconciliationError, match="RELEASE_INELIGIBLE"):
            release_expired_never_claimed(
                database=Database([]), session=object(), tenant_id=TENANT,
                admission_id=other.admission_id, expected_fingerprint=other.fingerprint,
                observed_at=NOW + timedelta(hours=2), confirmation=CONFIRM,
            )
    registry.transition.assert_not_called()


# ARTIFACT: test_wilsy_ai_usage_reconciliation.py
# VERSION: v1.0.0-EXACT-TENANT-RECONCILIATION-UNIT
# AUTHORITY BOUNDARY: no provider calls or financial execution
# TENANT POSTURE: exact scoped synthetic fixture identities
# FAIL-CLOSED POSTURE: no uncertain execution recovery
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
