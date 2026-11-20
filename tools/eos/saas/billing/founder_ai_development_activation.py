"""Development-only staged Founder AI commercial activation command.

TITLE: WILSY Founder AI Development Activation Runner
VERSION: v1.3.0-PRECONNECT-ATLAS-DENIAL
AUTHORITY: WILSY OS Core Governance; source registries own all mutations.
EPITOME: Rehearse exact Founder plan -> subscription -> AI entitlement
         transitions on a loopback development Mongo replica set only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/founder_ai_development_activation.py
COLLABORATION / OWNERSHIP: PlanRegistry owns plan CAS; SubscriptionRegistry owns
                          subscription proof and audit; Founder reconciliation
                          delegates issuance/activation to D57B and P4.
CERTIFICATION / UPDATE DATE: 2026-11-20
CHANGELOG: v1.3.0-PRECONNECT-ATLAS-DENIAL rejects non-development,
           non-loopback and SRV MongoDB configuration before even attempting
           a database connection. No authentication, reads or writes occur
           against a rejected URI. v1.2.0-STAGED-READBACK-VERIFICATION re-reads canonical
           plan and subscription evidence after each committed development
           stage, detecting partial failures without inventing rollback truth.
           v1.1.0-MODULE-LEVEL-DEVELOPMENT-WRITE-GATE enforces
           loopback development-replica admission inside the exported stage
           entrypoint, so imported callers cannot bypass CLI-only guards.
           v1.0.0-LOCAL-FOUNDER-AI-COMMERCIAL-ROLLOUT creates
           dry-run-first exact-scope stage admission with explicit AI feature,
           independent registry mutations and no Atlas/production write path.
COMPLIANCE: POPIA s19; GDPR Art32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: No credentials or tenant source bodies are printed.
TENANT BOUNDARY: Exact Founder binding, no alias, tenant-name or role bypass.
AUTHORITY BOUNDARY: Authorized local operator only; no IAM grant, user command,
                    or production subscription/entitlement execution.
TRANSACTION BOUNDARY: PlanRegistry CAS is independent; subscription and P4 each
                      use caller-owned transactions in separate stages.
FINANCIAL AUTHORITY BOUNDARY: All source prices must remain exactly zero;
                              Kennel EOS alone executes money.
FAIL-CLOSED DECLARATION: Production env, Atlas/SRV transport, missing explicit
                         tier, source drift or partial stage rejects.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
import re
from typing import Any, Final
from urllib.parse import urlsplit

from tools.eos.kernel.db import connect_db, disconnect_db, get_client, get_database
import tools.eos.saas.billing.plan_registry as plan_registry_module
import tools.eos.saas.billing.subscription_registry as subscription_registry_module
from tools.eos.saas.billing.plan_registry import PlanRegistry
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.billing.founder_ai_entitlement_reconciliation import (
    BRANDING_FEATURE, FOUNDER_PLAN_ID, FOUNDER_SUBSCRIPTION_ID,
    FOUNDER_TENANT_ID, FounderAIReconciliationError,
    _canonical_plan, reconcile_founder_ai_entitlement,
)
from tools.eos.saas.billing.wilsy_ai_vas_feature_catalogue import WilsyAIVASFeatureId
from tools.eos.saas.domain.subscription import SubscriptionStatus, verify_subscription_integrity

VERSION: Final[str] = "v1.3.0-PRECONNECT-ATLAS-DENIAL"
_ALLOWED_FOUNDATION: Final[frozenset[str]] = frozenset(
    (BRANDING_FEATURE, "legal.core"),
)
_FINGERPRINT: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")


class FounderAIDevelopmentActivationError(RuntimeError):
    """Deterministic status for a refused or inconsistent dev rollout."""


def _guard_uri_before_connect(uri: str, environment: str) -> None:
    """Reject every remote and non-development URI before opening a socket."""
    if environment.strip().lower() not in {"development", "dev"}:
        raise FounderAIDevelopmentActivationError("FOUNDER_AI_DEV_ENV_REQUIRED")
    if not uri.startswith("mongodb://"):
        raise FounderAIDevelopmentActivationError("FOUNDER_AI_LOOPBACK_URI_REQUIRED")
    parsed = urlsplit(uri)
    authority = parsed.netloc.rsplit("@", 1)[-1]
    hosts = authority.split(",")
    if not hosts or any(host.split(":", 1)[0] not in {"localhost", "127.0.0.1"} for host in hosts):
        raise FounderAIDevelopmentActivationError("FOUNDER_AI_LOOPBACK_HOST_REQUIRED")


def _guard_development(uri: str, environment: str, database: Any, client: Any) -> None:
    """No production, SRV, non-loopback or non-replica writes from this tool."""
    _guard_uri_before_connect(uri, environment)
    if database is None or database.name != "wilsy":
        raise FounderAIDevelopmentActivationError("FOUNDER_AI_DEV_DATABASE_REQUIRED")
    hello = client.admin.command("hello")
    if not hello.get("setName") or hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
        raise FounderAIDevelopmentActivationError("FOUNDER_AI_DEV_REPLICA_PRIMARY_REQUIRED")


def _exact_preflight(database: Any, client: Any, feature: WilsyAIVASFeatureId) -> tuple[Any, Any]:
    """Read the canonical existing Founder plan/subscription without mutation."""
    with client.start_session() as session:
        with session.start_transaction():
            plan = _canonical_plan(database["plans"], session)
            entities = SubscriptionRegistry.list_entities(
                FOUNDER_TENANT_ID, collection=database["subscriptions"], session=session,
            )
            active = [row for row in entities if row.status is SubscriptionStatus.ACTIVE]
            if len(active) != 1:
                raise FounderAIDevelopmentActivationError("FOUNDER_AI_SUBSCRIPTION_CARDINALITY")
            subscription = active[0]
            if (subscription.subscription_id != FOUNDER_SUBSCRIPTION_ID
                or subscription.plan_id != FOUNDER_PLAN_ID
                or subscription.tenant_id != FOUNDER_TENANT_ID
                or subscription.billing_mode != "PLATFORM"
                or subscription.amount != 0
                or not verify_subscription_integrity(subscription)
                or plan.price != 0
                or plan.plan_type.value != "FOUNDER_ENTERPRISE"):
                raise FounderAIDevelopmentActivationError("FOUNDER_AI_SOURCE_INVALID")
            current = set(plan.features)
            if BRANDING_FEATURE not in current:
                raise FounderAIDevelopmentActivationError("FOUNDER_AI_BRANDING_FEATURE_REQUIRED")
            foreign = current - _ALLOWED_FOUNDATION - {feature.value}
            if foreign:
                raise FounderAIDevelopmentActivationError("FOUNDER_AI_UNEXPECTED_PLAN_FEATURE")
            if any(other.value in current for other in WilsyAIVASFeatureId if other is not feature):
                raise FounderAIDevelopmentActivationError("FOUNDER_AI_CONFLICTING_AI_FEATURE")
            return plan, subscription


def execute_development_stage(
    *, stage: str, feature: WilsyAIVASFeatureId,
    database: Any, client: Any, apply: bool = False,
    activation_reference: str | None = None,
    activation_fingerprint: str | None = None,
) -> dict[str, object]:
    """Run one explicitly selected, auditable development-only stage.

    Plan updates and subscription snapshot upgrades cannot be one transaction
    with the present PlanRegistry. An operator must complete and verify each
    stage before the next. This command never retries failed writes silently.
    """
    _guard_development(
        os.getenv("MONGODB_URI", ""), os.getenv("WILSY_ENV", ""),
        database, client,
    )
    if stage not in {"plan", "subscription", "entitlement"}:
        raise FounderAIDevelopmentActivationError("FOUNDER_AI_STAGE_INVALID")
    if type(feature) is not WilsyAIVASFeatureId:
        raise FounderAIDevelopmentActivationError("FOUNDER_AI_FEATURE_INVALID")
    plan, subscription = _exact_preflight(database, client, feature)
    if stage == "plan":
        if feature.value in plan.features:
            return {"stage": stage, "state": "ALREADY_CURRENT", "writes": False}
        if not apply:
            return {"stage": stage, "state": "PLAN_FEATURE_UPDATE_REQUIRED", "writes": False}
        evolved_features = sorted({*plan.features, feature.value})
        result = PlanRegistry.update(
            FOUNDER_PLAN_ID, {"features": evolved_features},
            tenant_id=FOUNDER_TENANT_ID, exact_tenant=True,
        )
        if result.get("success") is not True:
            raise FounderAIDevelopmentActivationError("FOUNDER_AI_PLAN_CAS_FAILED")
        committed_plan, _ = _exact_preflight(database, client, feature)
        if (feature.value not in committed_plan.features
            or committed_plan.price != 0
            or committed_plan.plan_type.value != "FOUNDER_ENTERPRISE"):
            raise FounderAIDevelopmentActivationError("FOUNDER_AI_PLAN_READBACK_FAILED")
        return {"stage": stage, "state": "PLAN_UPDATED_VERIFY_SUBSCRIPTION_NEXT", "writes": True}
    if feature.value not in plan.features:
        raise FounderAIDevelopmentActivationError("FOUNDER_AI_PLAN_FEATURE_NOT_CURRENT")
    if stage == "subscription":
        if (tuple(subscription.plan_features) == tuple(plan.features)
            and subscription.plan_catalogue_version == plan.catalogue_version):
            return {"stage": stage, "state": "ALREADY_CURRENT", "writes": False}
        if not apply:
            return {"stage": stage, "state": "SUBSCRIPTION_SNAPSHOT_UPDATE_REQUIRED", "writes": False}
        with client.start_session() as session:
            with session.start_transaction():
                changed = SubscriptionRegistry.upgrade(
                    FOUNDER_SUBSCRIPTION_ID, FOUNDER_TENANT_ID,
                    {"newPlanId": FOUNDER_PLAN_ID},
                    collection=database["subscriptions"], session=session,
                )
                if changed.get("success") is not True:
                    raise FounderAIDevelopmentActivationError("FOUNDER_AI_SUBSCRIPTION_CAS_FAILED")
                updated = changed["subscription"]
                if (updated.amount != 0 or updated.plan_id != FOUNDER_PLAN_ID
                    or tuple(updated.plan_features) != tuple(plan.features)
                    or updated.plan_catalogue_version != plan.catalogue_version):
                    raise FounderAIDevelopmentActivationError("FOUNDER_AI_SUBSCRIPTION_RESULT_INVALID")
        committed_plan, committed_subscription = _exact_preflight(database, client, feature)
        if (tuple(committed_subscription.plan_features) != tuple(committed_plan.features)
            or committed_subscription.plan_catalogue_version != committed_plan.catalogue_version
            or committed_subscription.amount != 0):
            raise FounderAIDevelopmentActivationError("FOUNDER_AI_SUBSCRIPTION_READBACK_FAILED")
        return {"stage": stage, "state": "SUBSCRIPTION_UPDATED_VERIFY_ENTITLEMENT_NEXT", "writes": True}
    if (tuple(subscription.plan_features) != tuple(plan.features)
        or subscription.plan_catalogue_version != plan.catalogue_version):
        raise FounderAIDevelopmentActivationError("FOUNDER_AI_SUBSCRIPTION_NOT_CURRENT")
    if not apply:
        with client.start_session() as session:
            with session.start_transaction():
                readiness = reconcile_founder_ai_entitlement(
                    subscription_collection=database["subscriptions"],
                    plan_collection=database["plans"],
                    entitlement_collection=database["wilsy_ai_entitlements"],
                    session=session,
                    idempotency_key="founder-ai-development-reconciliation-v1",
                    feature_id=feature,
                )
        return {"stage": stage, "state": readiness.lifecycle, "writes": False}
    if (not isinstance(activation_reference, str) or not activation_reference.strip()
        or not isinstance(activation_fingerprint, str)
        or _FINGERPRINT.fullmatch(activation_fingerprint) is None):
        raise FounderAIDevelopmentActivationError("FOUNDER_AI_ACTIVATION_EVIDENCE_REQUIRED")
    with client.start_session() as session:
        with session.start_transaction():
            activated = reconcile_founder_ai_entitlement(
                subscription_collection=database["subscriptions"],
                plan_collection=database["plans"],
                entitlement_collection=database["wilsy_ai_entitlements"],
                session=session,
                idempotency_key="founder-ai-development-reconciliation-v1",
                feature_id=feature, apply=True,
                activation_evidence_reference=activation_reference,
                activation_evidence_fingerprint=activation_fingerprint,
                occurred_at=datetime.now(timezone.utc),
            )
    return {"stage": stage, "state": activated.lifecycle, "writes": activated.applied}


def main() -> int:
    """CLI: dry-run by default; --apply is local-dev-only and stage-specific."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("plan", "subscription", "entitlement"), required=True)
    parser.add_argument("--feature", choices=[feature.value for feature in WilsyAIVASFeatureId], required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--activation-reference")
    parser.add_argument("--activation-fingerprint")
    args = parser.parse_args()
    connected = False
    try:
        uri = os.getenv("MONGODB_URI", "")
        environment = os.getenv("WILSY_ENV", "")
        if not uri:
            raise FounderAIDevelopmentActivationError("FOUNDER_AI_MONGODB_URI_REQUIRED")
        _guard_uri_before_connect(uri, environment)
        good, _ = connect_db()
        if not good:
            raise FounderAIDevelopmentActivationError("FOUNDER_AI_MONGO_CONNECTION_FAILED")
        connected = True
        client, database = get_client(), get_database()
        if client is None or database is None:
            raise FounderAIDevelopmentActivationError("FOUNDER_AI_DATABASE_UNAVAILABLE")
        _guard_development(uri, environment, database, client)
        # This is a dedicated operator process; bind registry canonical handles
        # only to the same verified loopback development database.
        plan_registry_module.plans_collection = database["plans"]
        subscription_registry_module.subscriptions_collection = database["subscriptions"]
        result = execute_development_stage(
            stage=args.stage, feature=WilsyAIVASFeatureId(args.feature),
            database=database, client=client, apply=args.apply,
            activation_reference=args.activation_reference,
            activation_fingerprint=args.activation_fingerprint,
        )
        print(json.dumps(result, sort_keys=True))
        return 0
    except (FounderAIDevelopmentActivationError, FounderAIReconciliationError) as error:
        print(json.dumps({"state": "DENIED", "code": str(error)}))
        return 2
    finally:
        if connected:
            disconnect_db()


if __name__ == "__main__":
    raise SystemExit(main())


# ARTIFACT: founder_ai_development_activation.py
# VERSION: v1.3.0-PRECONNECT-ATLAS-DENIAL
# AUTHORITY BOUNDARY: local-only stage coordination through canonical registries
# TENANT POSTURE: one exact Founder subscription/plan/tenant tuple only
# FAIL-CLOSED POSTURE: required tier, loopback replica and guarded stage writes
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
