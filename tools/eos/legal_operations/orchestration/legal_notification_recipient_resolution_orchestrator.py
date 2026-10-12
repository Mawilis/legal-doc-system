"""WILSY OS current Legal notification recipient resolution composition.

TITLE: Legal Notification Recipient Resolution Orchestrator
VERSION: v1.1.0-L8-8H-RECIPIENT-RESOLUTION
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Revalidates one persisted RETURN_READY intent, its canonical return,
         instruction/document/matter chain, one explicit binding and current IAM.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_notification_recipient_resolution_orchestrator.py
COLLABORATION / OWNERSHIP: P1/P2 own lifecycle truth; L8-8F owns intent truth;
                            L8-8H owns recipient binding; IAM owns current status.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.1.0 removes unverifiable source-authority output and
           derives revocation/supersession-aware currentness from immutable
           binding and lifecycle histories.
           2026-10-12 v1.0.0 establishes opaque, ambiguity-intolerant current
           recipient resolution without contact lookup or delivery behavior.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Returns opaque principal and evidence identifiers;
                            no email, phone, address, message or provider state.
TENANT BOUNDARY: Every persistence read is exact-tenant scoped; global principal
                 status is conjunctively restricted by tenant membership.
AUTHORITY BOUNDARY: Resolution only; it cannot select by role or send anything.
TRANSACTION BOUNDARY: Caller owns one active transaction across every read.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing/corrupt/stale/foreign/ambiguous source,
                         binding, principal or membership evidence rejects.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Final, NoReturn, cast

from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.legal_operations.domain.legal_notification_recipient_binding import LegalNotificationEvent
from tools.eos.legal_operations.domain.legal_operations_current_projection import resolve_current_lifecycle_snapshot
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter, LegalInstruction, ProcessDocument, ReturnOfService
from tools.eos.legal_operations.domain.legal_return_ready_notification import LegalReturnReadyNotificationEvent, LegalReturnReadyNotificationStatus
from tools.eos.legal_operations.registry.legal_notification_recipient_binding_registry import LegalNotificationRecipientBindingRegistry
from tools.eos.legal_operations.domain.legal_notification_recipient_binding_lifecycle import LegalNotificationRecipientBindingLifecycleAction
from tools.eos.legal_operations.registry.legal_notification_recipient_binding_lifecycle_registry import LegalNotificationRecipientBindingLifecycleRegistry
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.legal_return_ready_notification_registry import LegalReturnReadyNotificationRegistry

VERSION: Final[str] = "v1.1.0-L8-8H-RECIPIENT-RESOLUTION"


class LegalNotificationRecipientResolutionError(RuntimeError):
    """Stable code-only failure for current recipient resolution."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalNotificationRecipientResolutionError(code)
    if cause is None:
        raise error
    raise error from cause


def _active(session: Any) -> Any:
    if session is None:
        _fail("L8_8H_RESOLUTION_ACTIVE_TRANSACTION_REQUIRED")
    active = getattr(session, "in_transaction", False)
    if callable(active):
        active = active()
    if active is not True:
        _fail("L8_8H_RESOLUTION_ACTIVE_TRANSACTION_REQUIRED")
    return session


@dataclass(frozen=True, slots=True)
class LegalNotificationRecipientResolution:
    """Bounded opaque result; not a contact address or delivery instruction."""

    tenant_id: str
    notification_id: str
    case_matter_id: str
    event: str
    recipient_principal_id: str
    binding_id: str
    binding_fingerprint: str
    currentness_fingerprint: str
    resolved_at: datetime


def _current(tenant: str, entity_type: str, identity: str, expected: type[Any], collection: Any, session: Any) -> Any:
    history = LegalOperationsLifecycleRegistry.get_entity_history(tenant, entity_type, identity, collection, session=session)
    try:
        return resolve_current_lifecycle_snapshot(history, expected_type=expected)
    except Exception as error:
        _fail("L8_8H_RESOLUTION_SOURCE_UNAVAILABLE", error)


def resolve_legal_notification_recipient(
    *, tenant_id: str, notification_id: str, resolved_at: datetime,
    lifecycle_collection: Any, notification_collection: Any, binding_collection: Any, binding_lifecycle_collection: Any,
    principal_collection: Any, membership_collection: Any, session: Any,
) -> LegalNotificationRecipientResolution:
    """Resolve exactly one currently authorized opaque RETURN_READY recipient.

    The caller cannot nominate a recipient, contact address, role or source
    matter. All scope is derived from persisted intent and canonical lifecycle
    evidence, and ambiguity is a hard failure rather than an ordering policy.
    """
    tx = _active(session)
    if not isinstance(resolved_at, datetime) or resolved_at.tzinfo is None or resolved_at.utcoffset() is None:
        _fail("L8_8H_RESOLUTION_TIME_INVALID")
    at = resolved_at.astimezone(timezone.utc)
    if at != resolved_at or at.tzinfo != timezone.utc:
        _fail("L8_8H_RESOLUTION_TIME_INVALID")
    try:
        intent = LegalReturnReadyNotificationRegistry(notification_collection).get_by_notification_id(tenant_id=tenant_id, notification_id=notification_id, session=tx)
        if intent is None:
            _fail("L8_8H_RESOLUTION_INTENT_UNAVAILABLE")
        if intent.status is not LegalReturnReadyNotificationStatus.PENDING or intent.event is not LegalReturnReadyNotificationEvent.RETURN_READY:
            _fail("L8_8H_RESOLUTION_INTENT_INVALID")
        returned = cast(ReturnOfService, _current(intent.tenant_id, "ReturnOfService", intent.return_id, ReturnOfService, lifecycle_collection, tx))
        instruction = cast(LegalInstruction, _current(intent.tenant_id, "LegalInstruction", intent.instruction_id, LegalInstruction, lifecycle_collection, tx))
        document = cast(ProcessDocument, _current(intent.tenant_id, "ProcessDocument", intent.document_id, ProcessDocument, lifecycle_collection, tx))
        if (returned.fingerprint != intent.return_fingerprint or returned.instruction_id != instruction.instruction_id or returned.document_id != document.document_id or instruction.document_id != document.document_id or instruction.case_matter_id != document.case_matter_id):
            _fail("L8_8H_RESOLUTION_SOURCE_SCOPE_MISMATCH")
        matter = cast(CaseMatter, _current(intent.tenant_id, "CaseMatter", instruction.case_matter_id, CaseMatter, lifecycle_collection, tx))
        if matter.case_matter_id != instruction.case_matter_id:
            _fail("L8_8H_RESOLUTION_SOURCE_SCOPE_MISMATCH")
        bindings = LegalNotificationRecipientBindingRegistry(binding_collection).list_scope(intent.tenant_id, matter.case_matter_id, LegalNotificationEvent.RETURN_READY, session=tx)
        lifecycle = LegalNotificationRecipientBindingLifecycleRegistry(binding_lifecycle_collection).list_scope(intent.tenant_id, matter.case_matter_id, LegalNotificationEvent.RETURN_READY, session=tx)
        by_id = {value.binding_id: value for value in bindings}
        if len(by_id) != len(bindings):
            _fail("L8_8H_RESOLUTION_BINDING_CORRUPT")
        terminated: set[str] = set()
        for change in lifecycle:
            target = by_id.get(change.target_binding_id)
            if target is None or target.fingerprint != change.target_binding_fingerprint or change.effective_at <= target.effective_from or (target.effective_until is not None and change.effective_at > target.effective_until):
                _fail("L8_8H_RESOLUTION_LIFECYCLE_INVALID")
            if change.target_binding_id in terminated:
                _fail("L8_8H_RESOLUTION_LIFECYCLE_AMBIGUOUS")
            if change.action is LegalNotificationRecipientBindingLifecycleAction.SUPERSEDED:
                successor = by_id.get(cast(str, change.successor_binding_id))
                if successor is None or successor.fingerprint != change.successor_binding_fingerprint or successor.effective_from != change.effective_at or (successor.tenant_id, successor.case_matter_id, successor.event) != (target.tenant_id, target.case_matter_id, target.event):
                    _fail("L8_8H_RESOLUTION_SUCCESSOR_INVALID")
            terminated.add(change.target_binding_id)
        effective = tuple(value for value in bindings if value.is_effective_at(at) and not any(change.target_binding_id == value.binding_id and change.effective_at <= at for change in lifecycle))
        if not effective:
            _fail("L8_8H_RESOLUTION_BINDING_UNAVAILABLE")
        if len(effective) != 1:
            _fail("L8_8H_RESOLUTION_BINDING_AMBIGUOUS")
        binding = effective[0]
        principal = PrincipalAuthorityRepository.get(binding.recipient_principal_id, principal_collection, session=tx)
        membership = TenantMembershipRepository.resolve(binding.recipient_principal_id, intent.tenant_id, membership_collection, session=tx)
        if principal.status is not PrincipalStatus.ACTIVE or membership.status is not TenantMembershipStatus.ACTIVE:
            _fail("L8_8H_RESOLUTION_RECIPIENT_NOT_CURRENT")
    except LegalNotificationRecipientResolutionError:
        raise
    except Exception as error:
        _fail("L8_8H_RESOLUTION_AUTHORITY_UNAVAILABLE", error)
    currentness_fingerprint = hashlib.sha3_512(json.dumps({"tenant_id": intent.tenant_id, "notification_id": intent.notification_id, "case_matter_id": matter.case_matter_id, "event": LegalNotificationEvent.RETURN_READY.value, "resolved_at": at.isoformat(timespec="microseconds").replace("+00:00", "Z"), "selected_binding_fingerprint": binding.fingerprint, "binding_history": sorted(value.fingerprint for value in bindings), "lifecycle_history": sorted(value.fingerprint for value in lifecycle)}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return LegalNotificationRecipientResolution(
        tenant_id=intent.tenant_id, notification_id=intent.notification_id,
        case_matter_id=matter.case_matter_id, event=LegalNotificationEvent.RETURN_READY.value,
        recipient_principal_id=binding.recipient_principal_id,
        binding_id=binding.binding_id, binding_fingerprint=binding.fingerprint,
        currentness_fingerprint=currentness_fingerprint,
        resolved_at=at,
    )


__all__ = ["VERSION", "LegalNotificationRecipientResolution", "LegalNotificationRecipientResolutionError", "resolve_legal_notification_recipient"]

# ARTIFACT: legal_notification_recipient_resolution_orchestrator.py
# VERSION: v1.1.0-L8-8H-RECIPIENT-RESOLUTION
# AUTHORITY BOUNDARY: current opaque recipient resolution only; no role inference, contact lookup or dispatch
# TENANT POSTURE: exact tenant source reads plus conjunctive current membership
# FAIL-CLOSED POSTURE: absent, stale, corrupt, foreign or ambiguous evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
