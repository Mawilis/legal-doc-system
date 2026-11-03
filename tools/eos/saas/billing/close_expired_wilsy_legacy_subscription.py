"""Close the one known expired WILSY legacy Professional subscription safely.

Dry-run by default. --apply invokes SubscriptionRegistry.cancel so the
canonical lifecycle proof and append-only audit trail are preserved.
The Founder subscription is read-only and must remain unchanged.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.domain.subscription import (
    SubscriptionStatus,
    verify_subscription_integrity,
)

TENANT_ID = "WILSYTENANT-4CD2FZ4O"
FOUNDER_ID = "WILSYSUB-93455E4E"
LEGACY_ID = "WILSYSUB-LEGACY-8A823D69D18B419DF4AE658C"
FOUNDER_PLAN_ID = "WILSYPLAN-37B8164F"
LEGACY_PLAN_ID = "WILSYPLAN-B877349B938833072C388A182ED4B497"


def require(condition: bool, code: str) -> None:
    if not condition:
        raise RuntimeError(code)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Persist cancellation through SubscriptionRegistry.",
    )
    args = parser.parse_args()

    founder = SubscriptionRegistry.get(FOUNDER_ID, tenant_id_header=TENANT_ID)
    legacy = SubscriptionRegistry.get(LEGACY_ID, tenant_id_header=TENANT_ID)
    require(founder is not None, "FOUNDER_SUBSCRIPTION_NOT_FOUND")
    require(legacy is not None, "LEGACY_SUBSCRIPTION_NOT_FOUND")
    require(founder.plan_id == FOUNDER_PLAN_ID, "FOUNDER_PLAN_MISMATCH")
    require(founder.status is SubscriptionStatus.ACTIVE, "FOUNDER_NOT_ACTIVE")
    require(founder.amount == 0, "FOUNDER_AMOUNT_MISMATCH")
    require(founder.billing_mode == "PLATFORM", "FOUNDER_BILLING_MODE_MISMATCH")
    require(verify_subscription_integrity(founder), "FOUNDER_INTEGRITY_INVALID")

    require(legacy.plan_id == LEGACY_PLAN_ID, "LEGACY_PLAN_MISMATCH")
    require(legacy.tier.value == "PROFESSIONAL", "LEGACY_TIER_MISMATCH")
    require(legacy.status is SubscriptionStatus.ACTIVE, "LEGACY_NOT_ACTIVE")
    require(legacy.amount == 299, "LEGACY_AMOUNT_MISMATCH")
    require(legacy.billing_mode == "PLATFORM", "LEGACY_BILLING_MODE_MISMATCH")
    require(verify_subscription_integrity(legacy), "LEGACY_INTEGRITY_INVALID")

    now = datetime.now(timezone.utc)
    period_end = legacy.current_period_end
    require(
        period_end.tzinfo is not None and period_end.utcoffset() is not None,
        "LEGACY_PERIOD_END_NOT_TIMEZONE_AWARE",
    )
    require(period_end < now, "LEGACY_SUBSCRIPTION_PERIOD_NOT_EXPIRED")

    result = {
        "outcome": "DRY_RUN_VALIDATED",
        "tenant_id": TENANT_ID,
        "founder_subscription_id": FOUNDER_ID,
        "legacy_subscription_id": LEGACY_ID,
        "legacy_period_end": period_end.isoformat(),
        "legacy_period_expired": True,
        "action": "CANCEL_LEGACY_WITH_APPEND_ONLY_AUDIT",
        "applied": False,
    }

    if args.apply:
        cancellation = SubscriptionRegistry.cancel(
            LEGACY_ID,
            tenant_id_header=TENANT_ID,
            cancel_reason="expired_legacy_subscription_cleanup",
            cancel_at_period_end=False,
        )
        require(cancellation.get("success") is True, "LEGACY_CANCELLATION_FAILED")

        legacy_after = SubscriptionRegistry.get(
            LEGACY_ID,
            tenant_id_header=TENANT_ID,
        )
        founder_after = SubscriptionRegistry.get(
            FOUNDER_ID,
            tenant_id_header=TENANT_ID,
        )
        require(legacy_after is not None, "LEGACY_MISSING_AFTER_CANCELLATION")
        require(
            legacy_after.status is SubscriptionStatus.CANCELLED,
            "LEGACY_NOT_CANCELLED",
        )
        require(
            verify_subscription_integrity(legacy_after),
            "LEGACY_POST_CANCEL_INTEGRITY_INVALID",
        )
        require(founder_after is not None, "FOUNDER_MISSING_AFTER_CANCELLATION")
        require(
            founder_after.status is SubscriptionStatus.ACTIVE
            and founder_after.plan_id == FOUNDER_PLAN_ID
            and founder_after.amount == 0
            and verify_subscription_integrity(founder_after),
            "FOUNDER_CHANGED_OR_INVALID",
        )
        result.update(
            outcome="LEGACY_CANCELLED",
            applied=True,
            legacy_status=legacy_after.status.value,
            legacy_audit_entries=len(legacy_after.audit_trail),
            founder_status=founder_after.status.value,
            founder_unchanged=True,
        )

    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
