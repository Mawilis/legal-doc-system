"""One-tenant, fail-closed Founder Legal entitlement reconciliation.

This command never creates a tenant, principal, role, membership, plan, or
subscription. It only evolves the exact existing zero-rated Founder plan and
uses P42 to same-plan-upgrade the exact existing subscription, or calls the
non-mutating-subscription reconciliation path when Legal is already present.

Dry-run is the default. Pass --apply to perform the governed writes.
"""
from __future__ import annotations

import argparse
import json
import os
from typing import Any

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.kernel.db import get_client, get_database
from tools.eos.saas.billing.subscription_active_entitlement_composition_service import (
    SubscriptionActiveEntitlementCompositionService,
)
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    CURRENT_COLLECTION,
    HISTORY_COLLECTION,
)
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    COLLECTION as AUTHORIZATION_COLLECTION,
)


TENANT_ID = "WILSYTENANT-4CD2FZ4O"
PRINCIPAL_ID = "695e423c9d355c0675c6835d"
SUBSCRIPTION_ID = "WILSYSUB-93455E4E"
PLAN_ID = "WILSYPLAN-37B8164F"
BRANDING_FEATURE = "wilsy.vas.tenant_branding.enterprise.v1"
LEGAL_FEATURE = "legal.core"


class ReconciliationPreflightError(RuntimeError):
    """The exact live Founder source or authority evidence is not eligible."""


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise ReconciliationPreflightError(code)


def _identity(database: Any) -> SovereignIdentity:
    """Build a minimal projection only after resolving all live authority facts."""
    principal = PrincipalAuthorityRepository.get(
        PRINCIPAL_ID, database["principal_authorities"]
    )
    membership = TenantMembershipRepository.resolve(
        PRINCIPAL_ID, TENANT_ID, database["tenant_memberships"]
    )
    authorization_role = RoleAssignmentRepository.resolve(
        PRINCIPAL_ID, TENANT_ID, "ENTERPRISE_ADMIN", database["role_assignments"]
    )
    business_role = TenantBusinessRoleRepository.resolve(
        PRINCIPAL_ID, TENANT_ID, database["tenant_business_roles"]
    )
    _require(principal.status is PrincipalStatus.ACTIVE, "PRINCIPAL_NOT_ACTIVE")
    _require(
        membership.status is TenantMembershipStatus.ACTIVE,
        "TENANT_MEMBERSHIP_NOT_ACTIVE",
    )
    _require(
        authorization_role.status is RoleAssignmentStatus.ACTIVE,
        "ENTERPRISE_ADMIN_ASSIGNMENT_NOT_ACTIVE",
    )
    _require(
        business_role.status is TenantBusinessRoleStatus.ACTIVE
        and business_role.business_role == "tenant_owner",
        "TENANT_OWNER_BUSINESS_ROLE_NOT_ACTIVE",
    )
    return SovereignIdentity(
        identity_id=PRINCIPAL_ID,
        tenant_id=TENANT_ID,
        username=None,
        email=None,
        roles=[],
        permissions=[],
        auth_method="governed-founder-legal-reconciliation",
        status=principal.status,
    )


def _load_exact_sources(database: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    subscriptions = database["subscriptions"]
    plans = database["plans"]
    _require(
        subscriptions.count_documents({"tenant_id": TENANT_ID}) == 1,
        "FOUNDER_SUBSCRIPTION_CARDINALITY_INVALID",
    )
    subscription = subscriptions.find_one(
        {"subscription_id": SUBSCRIPTION_ID, "tenant_id": TENANT_ID}
    )
    plan = plans.find_one({"plan_id": PLAN_ID, "tenant_id": TENANT_ID})
    _require(subscription is not None, "FOUNDER_SUBSCRIPTION_NOT_FOUND")
    _require(plan is not None, "FOUNDER_PLAN_NOT_FOUND")
    assert subscription is not None and plan is not None

    _require(subscription.get("plan_id") == PLAN_ID, "SUBSCRIPTION_PLAN_MISMATCH")
    _require(subscription.get("tier") == "FOUNDER_ENTERPRISE", "SUBSCRIPTION_TIER_MISMATCH")
    _require(subscription.get("status") == "active", "SUBSCRIPTION_NOT_ACTIVE")
    _require(subscription.get("billing_mode") == "PLATFORM", "SUBSCRIPTION_BILLING_MODE_MISMATCH")
    _require(subscription.get("amount") == 0, "SUBSCRIPTION_NOT_ZERO_RATED")
    _require(plan.get("plan_type") == "FOUNDER_ENTERPRISE", "PLAN_TYPE_MISMATCH")
    _require(plan.get("tenant_id") == TENANT_ID, "PLAN_TENANT_MISMATCH")
    _require(plan.get("active") is True, "FOUNDER_PLAN_NOT_ACTIVE")
    _require(plan.get("price") == 0, "FOUNDER_PLAN_NOT_ZERO_RATED")

    plan_features = tuple(plan.get("features") or ())
    subscription_features = tuple(subscription.get("plan_features") or ())
    allowed = {
        (BRANDING_FEATURE,),
        (BRANDING_FEATURE, LEGAL_FEATURE),
    }
    _require(plan_features in allowed, "FOUNDER_PLAN_FEATURE_SET_UNEXPECTED")
    _require(
        subscription_features in allowed,
        "FOUNDER_SUBSCRIPTION_FEATURE_SNAPSHOT_UNEXPECTED",
    )
    _require(
        not (LEGAL_FEATURE in subscription_features and LEGAL_FEATURE not in plan_features),
        "SUBSCRIPTION_FEATURES_EXCEED_CANONICAL_PLAN",
    )
    return subscription, plan


def _existing_entitlement(database: Any) -> dict[str, Any] | None:
    current = database[CURRENT_COLLECTION]
    history = database[HISTORY_COLLECTION]
    current_count = current.count_documents({"tenant_id": TENANT_ID})
    history_count = history.count_documents({"tenant_id": TENANT_ID})
    _require(current_count <= 1, "LEGAL_ENTITLEMENT_CURRENT_CARDINALITY_INVALID")
    if current_count == 0:
        _require(history_count == 0, "LEGAL_ENTITLEMENT_HISTORY_WITHOUT_CURRENT")
        return None
    document = current.find_one({"tenant_id": TENANT_ID})
    _require(document is not None, "LEGAL_ENTITLEMENT_CURRENT_UNREADABLE")
    assert document is not None
    _require(
        document.get("product_id") == TenantProductId.LEGAL_OPERATIONS.value,
        "UNEXPECTED_TENANT_ENTITLEMENT_PRESENT",
    )
    _require(history_count >= 1, "LEGAL_ENTITLEMENT_HISTORY_MISSING")
    return document


def reconcile(*, apply: bool) -> dict[str, Any]:
    _require(bool(os.getenv("MONGODB_URI", "").strip()), "MONGODB_URI_UNAVAILABLE")
    client = get_client()
    database = get_database()
    try:
        _require(database.name == "wilsy", "NON_CANONICAL_DATABASE")
        hello = client.admin.command("hello")
        _require(bool(hello.get("setName")), "MONGO_REPLICA_SET_REQUIRED")
        _require(
            hello.get("isWritablePrimary", hello.get("ismaster")) is True,
            "MONGO_WRITABLE_PRIMARY_REQUIRED",
        )
        _require(
            hello.get("logicalSessionTimeoutMinutes") is not None,
            "MONGO_SESSIONS_REQUIRED",
        )

        identity = _identity(database)
        subscription, plan = _load_exact_sources(database)
        existing = _existing_entitlement(database)
        if existing is not None:
            _require(
                LEGAL_FEATURE in tuple(plan.get("features") or ())
                and LEGAL_FEATURE in tuple(subscription.get("plan_features") or ()),
                "EXISTING_ENTITLEMENT_COMMERCIAL_SOURCE_MISMATCH",
            )
            return {
                "outcome": "ALREADY_ISSUED",
                "tenant_id": TENANT_ID,
                "subscription_id": SUBSCRIPTION_ID,
                "entitlement_id": str(existing.get("entitlement_id", "")),
            }

        plan_features = tuple(plan.get("features") or ())
        subscription_features = tuple(subscription.get("plan_features") or ())
        action = "PERPETUAL_FOUNDER_RECONCILE"
        if not apply:
            return {
                "outcome": "DRY_RUN",
                "action": action,
                "tenant_id": TENANT_ID,
                "subscription_id": SUBSCRIPTION_ID,
                "plan_id": PLAN_ID,
                "issuance_basis": "PERPETUAL_PLATFORM_OWNER",
                "plan_mutation_required": False,
                "subscription_mutation_required": False,
                "writes_performed": False,
            }

        # The Founder term is perpetual platform-owner eligibility. P42 issues
        # Legal from that existing term without editing the plan or subscription.
        result = SubscriptionActiveEntitlementCompositionService.reconcile_existing(
            identity
        )

        _require(
            result.legal_entitlement_applicable is True,
            "LEGAL_ENTITLEMENT_NOT_APPLICABLE_AFTER_RECONCILIATION",
        )
        issuance = result.entitlement_issuance_result
        _require(issuance is not None, "LEGAL_ENTITLEMENT_ISSUANCE_RESULT_MISSING")
        entitlement = issuance.composition.entitlement
        evidence = issuance.authorization_evidence
        _require(entitlement.tenant_id == TENANT_ID, "ENTITLEMENT_TENANT_MISMATCH")
        _require(
            entitlement.product_id is TenantProductId.LEGAL_OPERATIONS,
            "ENTITLEMENT_PRODUCT_MISMATCH",
        )
        _require(evidence.principal_id == PRINCIPAL_ID, "AUTHORIZATION_PRINCIPAL_MISMATCH")
        _require(evidence.tenant_id == TENANT_ID, "AUTHORIZATION_TENANT_MISMATCH")
        _require(result.subscription.subscription_id == SUBSCRIPTION_ID, "RECONCILED_SUBSCRIPTION_MISMATCH")
        _require(result.subscription.plan_id == PLAN_ID, "RECONCILED_PLAN_MISMATCH")
        _require(result.subscription.tier == "FOUNDER_ENTERPRISE", "RECONCILED_TIER_MISMATCH")
        _require(result.subscription.amount == 0, "RECONCILED_SUBSCRIPTION_NOT_ZERO_RATED")
        _require(result.subscription.billing_mode == "PLATFORM", "RECONCILED_BILLING_MODE_MISMATCH")

        current = database[CURRENT_COLLECTION].find_one({"tenant_id": TENANT_ID})
        history_count = database[HISTORY_COLLECTION].count_documents(
            {"tenant_id": TENANT_ID}
        )
        authorization_count = database[AUTHORIZATION_COLLECTION].count_documents(
            {"tenant_id": TENANT_ID}
        )
        _require(current is not None, "LEGAL_ENTITLEMENT_CURRENT_NOT_COMMITTED")
        assert current is not None
        _require(
            current.get("entitlement_id") == entitlement.entitlement_id,
            "LEGAL_ENTITLEMENT_CURRENT_POINTER_MISMATCH",
        )
        _require(history_count == 2, "LEGAL_ENTITLEMENT_HISTORY_LINEAGE_INVALID")
        _require(authorization_count == 1, "AUTHORIZATION_EVIDENCE_LINEAGE_INVALID")
        return {
            "outcome": "RECONCILED",
            "action": action,
            "tenant_id": TENANT_ID,
            "subscription_id": SUBSCRIPTION_ID,
            "plan_id": PLAN_ID,
            "entitlement_id": entitlement.entitlement_id,
            "authorization_decision_id": evidence.authorization_decision_id,
            "history_records": history_count,
            "authorization_records": authorization_count,
        }
    finally:
        client.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="perform the exact governed plan evolution and P42 reconciliation",
    )
    args = parser.parse_args()
    try:
        result = reconcile(apply=args.apply)
    except Exception as error:
        # Emit only the stable code/type; never print connection strings or PII.
        print(
            json.dumps(
                {
                    "outcome": "FAILED_CLOSED",
                    "error_type": type(error).__name__,
                    "error_code": str(error) if isinstance(error, ReconciliationPreflightError) else "RECONCILIATION_FAILED",
                },
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
