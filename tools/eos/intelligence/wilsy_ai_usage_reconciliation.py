"""WILSY OS exact-tenant AI usage reconciliation and guarded dormant reservation recovery.

TITLE: WILSY OS AI Usage Reconciliation Certificate
VERSION: v1.0.0-EXACT-TENANT-RECONCILIATION
AUTHORITY: Wilsy OS Core Governance; canonical C1A/C1B/M13 registries.
EPITOME: Read immutable model and usage evidence for held requests, and permit
         only explicitly confirmed, expired, never-claimed reservation release.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/wilsy_ai_usage_reconciliation.py
COLLABORATION / OWNERSHIP: Admission registry owns CAS; invocation registry
                           owns provider evidence; usage registry owns observed
                           consumption; Founder operator owns local execution.
CERTIFICATION / UPDATE DATE: 2026-11-21
CHANGELOG: v1.0.0-EXACT-TENANT-RECONCILIATION introduces bounded snapshot
           reconciliation and opt-in evidence-checked release of expired
           RESERVED admissions only; CLAIMED/RECONCILIATION_REQUIRED never
           release without separately certified provider reconciliation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No prompts, keys, raw provider responses, email,
                           transport logs, or vendor billing claims are read.
TENANT BOUNDARY: Exact tenant_id predicate in every read and CAS.
AUTHORITY BOUNDARY: Read-only audit; optional single-admission state transition.
FINANCIAL AUTHORITY BOUNDARY: No financial or provider settlement authority.
FAIL-CLOSED DECLARATION: No automatic retries, quota replenishment, fabricated
                         observations, uncertain-execution release, or cross-
                         tenant lookup; corrupt and oversized audits refuse.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Final

from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.intelligence.registry.ai_model_invocation_registry import (
    AIModelInvocationRegistry,
    AIModelInvocationRegistryNotFoundError,
    COLLECTION as INVOCATION_COLLECTION,
)
from tools.eos.saas.billing.wilsy_ai_entitlement_registry import (
    WilsyAIEntitlementRegistry,
    COLLECTION as ENTITLEMENT_COLLECTION,
)
from tools.eos.saas.billing.wilsy_ai_usage_admission_registry import (
    WilsyAIUsageAdmissionRegistry,
    COLLECTION as ADMISSION_COLLECTION,
)
from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import (
    WilsyAIUsageObservationRegistry,
    WilsyAIUsageObservationNotFoundError,
    COLLECTION as OBSERVATION_COLLECTION,
)
from tools.eos.saas.domain.wilsy_ai_usage_admission import (
    WilsyAIUsageAdmissionState,
)
from tools.eos.saas.billing.wilsy_ai_usage_admission_authority import MODULE_ID

VERSION: Final[str] = "v1.0.0-EXACT-TENANT-RECONCILIATION"
_MAX_ADMISSIONS: Final[int] = 500
_MIN_IDLE: Final[timedelta] = timedelta(hours=1)
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_HEX = re.compile(r"^[0-9a-f]{128}$")
_STATES = ("RESERVED", "CLAIMED", "RECONCILIATION_REQUIRED")
_CONFIRMATION: Final[str] = "RELEASE_EXPIRED_UNCLAIMED_ONLY"


class WilsyAIReconciliationError(RuntimeError):
    """Stable fail-closed audit or guarded-release refusal; no provider text."""


def _identity(value: str, *, name: str) -> str:
    """Validate an opaque tenant, database, or admission identifier."""
    if not isinstance(value, str) or _ID.fullmatch(value) is None:
        raise WilsyAIReconciliationError(f"AI_RECONCILIATION_{name}_INVALID")
    if name == "TENANT" and value.casefold() in {"default", "global", "root", "master", "*"}:
        raise WilsyAIReconciliationError("AI_RECONCILIATION_TENANT_FORBIDDEN")
    return value


def _when(value: datetime) -> datetime:
    """Normalize an aware UTC boundary without guessing from browser clocks."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise WilsyAIReconciliationError("AI_RECONCILIATION_CLOCK_INVALID")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class ReconciliationRow:
    """Non-secret bounded reconciliation projection; never provider truth."""

    admission_id: str
    admission_fingerprint: str
    state: str
    held_units: int
    window_end: str
    invocation_evidence: str
    provider_outcome: str
    usage_observation: str
    disposition: str

    def to_dict(self) -> dict[str, object]:
        """Return only certified bounded diagnostic fields."""
        return {name: getattr(self, name) for name in self.__dataclass_fields__}


def _lookup_evidence(
    *,
    admission: Any,
    invocation_registry: AIModelInvocationRegistry,
    observation_registry: WilsyAIUsageObservationRegistry,
    session: Any,
) -> tuple[str, str, str]:
    """Check exact-tenant evidence reference and never infer vendor charging."""
    reference = admission.evidence_reference
    if not reference:
        return "NOT_REFERENCED", "NOT_VERIFIED", "NOT_REFERENCED"
    try:
        evidence = invocation_registry.get(
            tenant_id=admission.tenant_id, invocation_id=reference, session=session,
        )
    except AIModelInvocationRegistryNotFoundError:
        return "ABSENT", "NOT_VERIFIED", "NOT_VERIFIED"
    if (evidence.entitlement_id != admission.entitlement_id
            or evidence.tenant_id != admission.tenant_id
            or evidence.request_units != admission.reserved_request_units):
        raise WilsyAIReconciliationError("AI_RECONCILIATION_INVOCATION_SCOPE_MISMATCH")
    outcome = evidence.outcome.value
    try:
        observation = observation_registry.get(
            tenant_id=admission.tenant_id,
            usage_observation_id=f"usage-{reference}",
            session=session,
        )
    except WilsyAIUsageObservationNotFoundError:
        return "VERIFIED", outcome, "ABSENT"
    if (observation.entitlement_id != admission.entitlement_id
            or observation.source_evidence_reference != evidence.invocation_id
            or observation.source_evidence_fingerprint != evidence.fingerprint
            or observation.request_units != evidence.request_units
            or observation.input_tokens != evidence.input_tokens
            or observation.output_tokens != evidence.output_tokens):
        raise WilsyAIReconciliationError("AI_RECONCILIATION_USAGE_EVIDENCE_MISMATCH")
    return "VERIFIED", outcome, "VERIFIED"


def audit_exact_tenant(
    *,
    database: Any,
    session: Any,
    tenant_id: str,
    observed_at: datetime,
    max_admissions: int = _MAX_ADMISSIONS,
) -> dict[str, object]:
    """Read one exact tenant's active holds in a caller-owned snapshot.

    This is a snapshot of EOS observations, not a statement of external
    provider billing. Every persisted record is hydrated through its canonical
    registry and a malformed record fails the whole audit closed.
    """
    tenant = _identity(tenant_id, name="TENANT")
    now = _when(observed_at)
    if session is None or database is None:
        raise WilsyAIReconciliationError("AI_RECONCILIATION_SESSION_REQUIRED")
    if isinstance(max_admissions, bool) or not isinstance(max_admissions, int) or not 1 <= max_admissions <= _MAX_ADMISSIONS:
        raise WilsyAIReconciliationError("AI_RECONCILIATION_LIMIT_INVALID")
    entitlement = WilsyAIEntitlementRegistry(database[ENTITLEMENT_COLLECTION]).get_by_module(
        tenant_id=tenant, module_id=MODULE_ID, session=session,
    )
    admissions = WilsyAIUsageAdmissionRegistry(database[ADMISSION_COLLECTION])
    invocations = AIModelInvocationRegistry(database[INVOCATION_COLLECTION])
    observations = WilsyAIUsageObservationRegistry(database[OBSERVATION_COLLECTION])
    cursor = database[ADMISSION_COLLECTION].find(
        {"tenant_id": tenant, "entitlement_id": entitlement.entitlement_id,
         "state": {"$in": list(_STATES)}},
        {"admission_id": 1, "_id": 0}, session=session,
    ).sort("admission_id", 1).limit(max_admissions + 1)
    ids = [row["admission_id"] for row in cursor]
    if len(ids) > max_admissions:
        raise WilsyAIReconciliationError("AI_RECONCILIATION_AUDIT_BOUND_EXCEEDED")
    rows: list[ReconciliationRow] = []
    total_held = 0
    for admission_id in ids:
        item = admissions.get(tenant_id=tenant, admission_id=admission_id, session=session)
        if item.entitlement_id != entitlement.entitlement_id or item.state.value not in _STATES:
            raise WilsyAIReconciliationError("AI_RECONCILIATION_SCOPE_DRIFT")
        invocation, outcome, usage = _lookup_evidence(
            admission=item, invocation_registry=invocations,
            observation_registry=observations, session=session,
        )
        disposition = "PROVIDER_EVIDENCE_RECONCILIATION_REQUIRED"
        if item.state is WilsyAIUsageAdmissionState.CLAIMED:
            disposition = "CLAIMED_EXECUTION_UNCERTAIN"
        elif item.state is WilsyAIUsageAdmissionState.RESERVED:
            if item.evidence_reference is not None:
                raise WilsyAIReconciliationError("AI_RECONCILIATION_RESERVED_EVIDENCE_INVALID")
            if item.window_end + _MIN_IDLE <= now and item.updated_at + _MIN_IDLE <= now:
                disposition = "EXPIRED_NEVER_CLAIMED_GUARDED_RELEASE_ELIGIBLE"
            else:
                disposition = "RESERVED_NOT_ELIGIBLE"
        elif item.state is WilsyAIUsageAdmissionState.RECONCILIATION_REQUIRED and (
            invocation != "VERIFIED" or usage == "VERIFIED"
        ):
            disposition = "RECONCILIATION_EVIDENCE_ANOMALY"
        total_held += item.reserved_request_units
        rows.append(ReconciliationRow(
            admission_id=item.admission_id,
            admission_fingerprint=item.fingerprint,
            state=item.state.value,
            held_units=item.reserved_request_units,
            window_end=item.window_end.isoformat(),
            invocation_evidence=invocation,
            provider_outcome=outcome,
            usage_observation=usage,
            disposition=disposition,
        ))
    return {
        "schema": "WILSY-AI-RECONCILIATION-AUDIT/V1",
        "version": VERSION,
        "database_name": database.name,
        "tenant_scope": "EXACT_TENANT",
        "entitlement_module": MODULE_ID,
        "observed_at": now.isoformat(),
        "held_units": total_held,
        "admission_count": len(rows),
        "provider_billing_verified": False,
        "rows": [row.to_dict() for row in rows],
    }


def release_expired_never_claimed(
    *,
    database: Any,
    session: Any,
    tenant_id: str,
    admission_id: str,
    expected_fingerprint: str,
    observed_at: datetime,
    confirmation: str,
) -> str:
    """CAS-release ONLY an expired unclaimed RESERVED admission in caller transaction.

    No CLAIMED or RECONCILIATION_REQUIRED record can be released through this
    method. A fresh transaction and exact hash comparison protect against a
    concurrent provider claim. The transition creates cryptographically
    fingerprinted admission evidence, never a fabricated usage observation.
    """
    tenant = _identity(tenant_id, name="TENANT")
    identity = _identity(admission_id, name="ADMISSION")
    now = _when(observed_at)
    if (confirmation != _CONFIRMATION or not isinstance(expected_fingerprint, str)
            or _HEX.fullmatch(expected_fingerprint) is None or session is None):
        raise WilsyAIReconciliationError("AI_RECONCILIATION_RELEASE_NOT_CONFIRMED")
    entitlement = WilsyAIEntitlementRegistry(database[ENTITLEMENT_COLLECTION]).get_by_module(
        tenant_id=tenant, module_id=MODULE_ID, session=session,
    )
    registry = WilsyAIUsageAdmissionRegistry(database[ADMISSION_COLLECTION])
    admission = registry.get(tenant_id=tenant, admission_id=identity, session=session)
    if (admission.entitlement_id != entitlement.entitlement_id
            or admission.fingerprint != expected_fingerprint
            or admission.state is not WilsyAIUsageAdmissionState.RESERVED
            or admission.evidence_reference is not None
            or admission.window_end + _MIN_IDLE > now
            or admission.updated_at + _MIN_IDLE > now):
        raise WilsyAIReconciliationError("AI_RECONCILIATION_RELEASE_INELIGIBLE")
    evidence_ref = "reconcile-expired-" + hashlib.sha3_512(
        f"{tenant}|{identity}|{expected_fingerprint}".encode("utf-8"),
    ).hexdigest()[:48]
    released = registry.transition(
        tenant_id=tenant, admission_id=identity,
        target_state=WilsyAIUsageAdmissionState.RELEASED,
        evidence_reference=evidence_ref,
        occurred_at=now, session=session,
    )
    if released.state is not WilsyAIUsageAdmissionState.RELEASED:
        raise WilsyAIReconciliationError("AI_RECONCILIATION_RELEASE_UNVERIFIED")
    return released.fingerprint


def main(argv: list[str] | None = None) -> int:
    """Run an explicitly scoped local audit; mutation requires extra proof flags.

    The existing Python EOS MongoDB configuration is the only connection
    authority. The operator must provide both tenant and expected database
    identity; wrong-database audits and recovery fail before accessing records.
    """
    parser = argparse.ArgumentParser(description="WILSY AI exact-tenant evidence reconciliation")
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--expected-database", required=True)
    parser.add_argument("--release-expired-reserved", metavar="ADMISSION_ID")
    parser.add_argument("--expected-fingerprint")
    parser.add_argument("--confirm")
    args = parser.parse_args(argv)
    try:
        tenant = _identity(args.tenant_id, name="TENANT")
        expected_db = _identity(args.expected_database, name="DATABASE")
        from tools.eos.kernel import db as kernel_db
        ready, _message = kernel_db.connect_db()
        if not ready:
            raise WilsyAIReconciliationError("AI_RECONCILIATION_DATABASE_UNAVAILABLE")
        database, client = kernel_db.get_database(), kernel_db.get_client()
        if database is None or client is None or database.name != expected_db:
            raise WilsyAIReconciliationError("AI_RECONCILIATION_DATABASE_MISMATCH")
        now = datetime.now(timezone.utc).replace(microsecond=0)
        with client.start_session() as session:
            with session.start_transaction(
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority", j=True),
            ):
                report = audit_exact_tenant(
                    database=database, session=session,
                    tenant_id=tenant, observed_at=now,
                )
                if args.release_expired_reserved is not None:
                    new_hash = release_expired_never_claimed(
                        database=database, session=session, tenant_id=tenant,
                        admission_id=args.release_expired_reserved,
                        expected_fingerprint=args.expected_fingerprint,
                        observed_at=now, confirmation=args.confirm,
                    )
                    report["guarded_release"] = {
                        "state": "RELEASED", "new_evidence_fingerprint": new_hash,
                    }
                elif args.expected_fingerprint is not None or args.confirm is not None:
                    raise WilsyAIReconciliationError("AI_RECONCILIATION_RELEASE_ARGUMENTS_UNEXPECTED")
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
        return 0
    except Exception as error:
        # Deliberately suppress exception text (URI, credential, and driver
        # internals might otherwise leak); print only a bounded safe class.
        safe_class = type(error).__name__
        safe_code = (str(error) if isinstance(error, WilsyAIReconciliationError)
                     else "AI_RECONCILIATION_READ_OR_TRANSACTION_FAILED")
        print(json.dumps({"status": "REFUSED", "failure_class": safe_class,
                          "code": safe_code}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "VERSION", "WilsyAIReconciliationError", "ReconciliationRow",
    "audit_exact_tenant", "release_expired_never_claimed", "main",
]

# ARTIFACT: wilsy_ai_usage_reconciliation.py
# VERSION: v1.0.0-EXACT-TENANT-RECONCILIATION
# AUTHORITY BOUNDARY: exact-tenant read-only audit and guarded unclaimed release
# TENANT POSTURE: all persistence lookups and CAS are exact-tenant scoped
# FAIL-CLOSED POSTURE: uncertain provider attempts never become released usage
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
