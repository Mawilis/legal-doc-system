"""WILSY OS governed privileged break-glass issuance service.

TITLE: Privileged Break-Glass Service
VERSION: v1.0.0-P7-GOVERNED-PRIVILEGED-BREAK-GLASS-SERVICE
AUTHORITY: Wilsy OS Sovereign IAM
EPITOME: Issue one exact P4 activation under fresh dual-control P7 authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/privileged_break_glass_service.py
COLLABORATION / OWNERSHIP: Composes sealed D12 current possession, P2 current eligibility,
    P3 interactive assurance, P4 activation persistence, and P6 revocability.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.0 establishes interactive dual-control emergency issuance.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Fresh strong-auth proof references are consumed but not persisted here.
TENANT BOUNDARY: Exact P2 tenant/platform scope is preserved without rebinding.
AUTHORITY BOUNDARY: P7 activation issuance only; no role, assignment, HTTP, token, or use authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS independently governs all finance.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_512
from typing import Any, Callable, Final, cast
from uuid import uuid4

from tools.eos.auth.current_system_permission_possession import CurrentSystemPermissionPossessionError
from tools.eos.auth.privileged_activation import MAXIMUM_ACTIVATION_LIFETIME, PrivilegedActivation, PrivilegedActivationError
from tools.eos.auth.privileged_activation_registry import PrivilegedActivationConflictError
from tools.eos.auth.privileged_break_glass_command_evidence import BREAK_GLASS_PERMISSION, PrivilegedBreakGlassCommandEvidence
from tools.eos.auth.privileged_break_glass_command_evidence_registry import PrivilegedBreakGlassCommandEvidenceRegistry, PrivilegedBreakGlassEvidenceConflictError
from tools.eos.auth.privileged_eligibility import PrivilegedTargetClass
from tools.eos.auth.privileged_security_assurance import PrivilegedAssuranceChannel, PrivilegedAssurancePurpose

VERSION: Final[str] = "v1.0.0-P7-GOVERNED-PRIVILEGED-BREAK-GLASS-SERVICE"
_PURPOSE = PrivilegedAssurancePurpose.PRIVILEGED_ELIGIBILITY_TO_ACTIVATION


class PrivilegedBreakGlassServiceError(RuntimeError):
    """Fail-closed bounded P7 orchestration error."""


@dataclass(frozen=True, slots=True)
class PrivilegedBreakGlassResult:
    """Exact durable P7 command evidence and corresponding P4 activation."""

    evidence: PrivilegedBreakGlassCommandEvidence
    activation: PrivilegedActivation


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or "*" in value or len(value) > 512:
        raise PrivilegedBreakGlassServiceError(name + "_INVALID")
    return value


def _moment(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise PrivilegedBreakGlassServiceError(name + "_INVALID")
    return value.astimezone(timezone.utc)


def _tx(session: object) -> object:
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError) as error:
        raise PrivilegedBreakGlassServiceError("ACTIVE_TRANSACTION_REQUIRED") from error
    if active is not True:
        raise PrivilegedBreakGlassServiceError("ACTIVE_TRANSACTION_REQUIRED")
    return session


class PrivilegedBreakGlassService:
    """Issue a bounded activation only after fresh requester+approver controls.

    Requester equals the activation subject, preserving P4 self-activation
    semantics. A distinct approver supplies independent current P7 permission
    and fresh P3 strong assurance. The caller exclusively owns transaction
    start, commit, abort, and whole-transaction retry.
    """

    def __init__(self, *, possession_resolver: Any, eligibility_resolver: Any, interactive_assurance_service: Any, activation_registry: Any, evidence_registry: PrivilegedBreakGlassCommandEvidenceRegistry, clock: Callable[[], datetime], assurance_attempt_id_factory: Callable[[], str] | None = None) -> None:
        """Bind existing sovereign resolvers and persistence authorities."""
        if not callable(clock):
            raise PrivilegedBreakGlassServiceError("CLOCK_INVALID")
        if type(evidence_registry) is not PrivilegedBreakGlassCommandEvidenceRegistry:
            raise PrivilegedBreakGlassServiceError("EVIDENCE_REGISTRY_REQUIRED")
        self._possession = possession_resolver
        self._eligibility = eligibility_resolver
        self._assurance = interactive_assurance_service
        self._activations = activation_registry
        self._evidence = evidence_registry
        self._clock = clock
        self._attempt = assurance_attempt_id_factory or (lambda: uuid4().hex)

    @staticmethod
    def _assignment(resolver: Any, principal_id: str, session: object) -> Any:
        try:
            assignment = resolver.resolve(principal_id=principal_id, permission_id=BREAK_GLASS_PERMISSION, session=session)
        except CurrentSystemPermissionPossessionError as error:
            raise PrivilegedBreakGlassServiceError("CURRENT_BREAK_GLASS_AUTHORITY_UNAVAILABLE") from error
        if assignment is None:
            raise PrivilegedBreakGlassServiceError("CURRENT_BREAK_GLASS_AUTHORITY_REQUIRED")
        if getattr(assignment, "principal_id", None) != principal_id or getattr(assignment, "permission_id", None) != BREAK_GLASS_PERMISSION:
            raise PrivilegedBreakGlassServiceError("BREAK_GLASS_ASSIGNMENT_BINDING_INVALID")
        return assignment

    def _fresh_assurance(self, *, tenant_id: str, proof_reference: str, principal_id: str, replay_key: str, role: str, session: object) -> Any:
        result = self._assurance.compose(tenant_id=tenant_id, proof_reference=proof_reference, assurance_purpose=_PURPOSE, idempotency_key=f"{replay_key}:{role}:assurance:{_text('ASSURANCE_ATTEMPT_ID', self._attempt())}", session=session)
        decision = getattr(result, "decision", None)
        evidence = getattr(result, "evidence", None)
        if decision is None or evidence is None or getattr(decision, "principal_id", None) != principal_id or getattr(evidence, "principal_id", None) != principal_id or getattr(decision, "sufficient", None) is not True or getattr(evidence, "sufficient", None) is not True or getattr(decision, "assurance_channel", None) is not PrivilegedAssuranceChannel.INTERACTIVE_STRONG_AUTH or getattr(evidence, "assurance_channel", None) is not PrivilegedAssuranceChannel.INTERACTIVE_STRONG_AUTH or getattr(evidence, "assurance_purpose", None) is not _PURPOSE:
            raise PrivilegedBreakGlassServiceError(role.upper() + "_CURRENT_ASSURANCE_REQUIRED")
        return evidence

    @staticmethod
    def _identity(prefix: str, requester: str, key: str) -> str:
        return prefix + sha3_512(("WILSY:P7:" + requester + ":" + key).encode("utf-8")).hexdigest()

    @staticmethod
    def _validate_replay(prior: PrivilegedBreakGlassCommandEvidence, *, requester: str, approver: str, tenant_id: str | None, reason_reference: str, eligibility: Any, requester_assignment: Any, approver_assignment: Any, effective_until: datetime) -> None:
        if prior.requester_principal_id != requester or prior.approver_principal_id != approver or prior.tenant_id != tenant_id or prior.reason_reference != reason_reference or prior.eligibility_evidence_id != getattr(eligibility, "eligibility_evidence_id", None) or prior.eligibility_evidence_fingerprint != getattr(eligibility, "eligibility_evidence_fingerprint", None) or prior.target_class is not getattr(eligibility, "target_class", None) or prior.privileged_role_id != getattr(eligibility, "privileged_role_id", None) or prior.requester_assignment_id != getattr(requester_assignment, "assignment_id", None) or prior.requester_assignment_revision != getattr(requester_assignment, "revision", None) or prior.requester_assignment_fingerprint != getattr(requester_assignment, "assignment_fingerprint", None) or prior.approver_assignment_id != getattr(approver_assignment, "assignment_id", None) or prior.approver_assignment_revision != getattr(approver_assignment, "revision", None) or prior.approver_assignment_fingerprint != getattr(approver_assignment, "assignment_fingerprint", None) or prior.effective_until != effective_until:
            raise PrivilegedBreakGlassServiceError("DIVERGENT_IDEMPOTENCY_REPLAY")

    def issue_interactive(self, *, requester_principal_id: str, approver_principal_id: str, tenant_id: str | None, requester_proof_tenant_id: str, requester_proof_reference: str, approver_proof_tenant_id: str, approver_proof_reference: str, eligibility_evidence_id: str, reason_reference: str, effective_until: datetime, idempotency_key: str, session: object) -> PrivilegedBreakGlassResult:
        """Issue or exactly replay one dual-control, short-lived P7 activation."""
        tx = _tx(session)
        requester = _text("REQUESTER_PRINCIPAL_ID", requester_principal_id)
        approver = _text("APPROVER_PRINCIPAL_ID", approver_principal_id)
        if requester == approver:
            raise PrivilegedBreakGlassServiceError("DUAL_CONTROL_REQUIRED")
        replay_key = _text("IDEMPOTENCY_KEY", idempotency_key)
        reason = _text("REASON_REFERENCE", reason_reference)
        evidence_id = _text("ELIGIBILITY_EVIDENCE_ID", eligibility_evidence_id)
        observed = _moment("AUTHORIZED_AT", self._clock())
        end = _moment("EFFECTIVE_UNTIL", effective_until)
        if end <= observed or end - observed > MAXIMUM_ACTIVATION_LIFETIME:
            raise PrivilegedBreakGlassServiceError("BREAK_GLASS_LIFETIME_INVALID")
        if tenant_id is not None:
            tenant_id = _text("TENANT_ID", tenant_id)

        requester_assignment = self._assignment(self._possession, requester, tx)
        approver_assignment = self._assignment(self._possession, approver, tx)
        requester_assurance = self._fresh_assurance(tenant_id=_text("REQUESTER_PROOF_TENANT_ID", requester_proof_tenant_id), proof_reference=_text("REQUESTER_PROOF_REFERENCE", requester_proof_reference), principal_id=requester, replay_key=replay_key, role="requester", session=tx)
        approver_assurance = self._fresh_assurance(tenant_id=_text("APPROVER_PROOF_TENANT_ID", approver_proof_tenant_id), proof_reference=_text("APPROVER_PROOF_REFERENCE", approver_proof_reference), principal_id=approver, replay_key=replay_key, role="approver", session=tx)

        eligibility = self._eligibility.resolve(eligibility_evidence_id=evidence_id, at=observed, session=tx)
        if eligibility is None or getattr(eligibility, "principal_id", None) != requester or getattr(eligibility, "tenant_id", None) != tenant_id:
            raise PrivilegedBreakGlassServiceError("CURRENT_TARGET_ELIGIBILITY_REQUIRED")
        target_class = getattr(eligibility, "target_class", None)
        if target_class not in (PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT, PrivilegedTargetClass.TENANT_PRIVILEGED):
            raise PrivilegedBreakGlassServiceError("TARGET_CLASS_INVALID")
        target_class = cast(PrivilegedTargetClass, target_class)
        if target_class is PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT and tenant_id is not None:
            raise PrivilegedBreakGlassServiceError("PLATFORM_SCOPE_TENANT_FORBIDDEN")

        prior = self._evidence.get_by_requester_idempotency(requester_principal_id=requester, idempotency_key=replay_key, session=tx)
        if prior is not None:
            self._validate_replay(prior, requester=requester, approver=approver, tenant_id=tenant_id, reason_reference=reason, eligibility=eligibility, requester_assignment=requester_assignment, approver_assignment=approver_assignment, effective_until=end)
            history = self._activations.get_history(prior.activation_id, session=tx)
            if not history or history[0].activation_fingerprint != prior.activation_fingerprint:
                raise PrivilegedBreakGlassServiceError("DURABLE_REPLAY_ACTIVATION_INVALID")
            if history[-1].status.value == "REVOKED":
                raise PrivilegedBreakGlassServiceError("TERMINAL_ACTIVATION_REPLAY_FORBIDDEN")
            return PrivilegedBreakGlassResult(prior, history[0])

        activation = PrivilegedActivation.issue(activation_id=self._identity("WILSYBREAKGLASSACTIVATION-", requester, replay_key), tenant_id=tenant_id, principal_id=requester, actor_principal_id=requester, privileged_role_id=getattr(eligibility, "privileged_role_id"), target_class=target_class, eligibility_evidence_id=evidence_id, eligibility_evidence_fingerprint=getattr(eligibility, "eligibility_evidence_fingerprint"), assurance_evidence_id=getattr(requester_assurance, "assurance_evidence_id"), assurance_evidence_fingerprint=getattr(requester_assurance, "assurance_evidence_fingerprint"), creation_assurance_purpose=_PURPOSE, activated_at=observed, effective_until=end, issuance_idempotency_key="P7:" + replay_key)
        command = PrivilegedBreakGlassCommandEvidence(evidence_id=self._identity("WILSYBREAKGLASSEVIDENCE-", requester, replay_key), idempotency_key=replay_key, requester_principal_id=requester, approver_principal_id=approver, tenant_id=tenant_id, target_class=target_class, privileged_role_id=activation.privileged_role_id, reason_reference=reason, requester_assignment_id=getattr(requester_assignment, "assignment_id"), requester_assignment_revision=getattr(requester_assignment, "revision"), requester_assignment_fingerprint=getattr(requester_assignment, "assignment_fingerprint"), approver_assignment_id=getattr(approver_assignment, "assignment_id"), approver_assignment_revision=getattr(approver_assignment, "revision"), approver_assignment_fingerprint=getattr(approver_assignment, "assignment_fingerprint"), eligibility_evidence_id=evidence_id, eligibility_evidence_fingerprint=activation.eligibility_evidence_fingerprint, requester_assurance_evidence_id=activation.assurance_evidence_id, requester_assurance_evidence_fingerprint=activation.assurance_evidence_fingerprint, approver_assurance_evidence_id=getattr(approver_assurance, "assurance_evidence_id"), approver_assurance_evidence_fingerprint=getattr(approver_assurance, "assurance_evidence_fingerprint"), activation_id=activation.activation_id, activation_fingerprint=activation.activation_fingerprint, authorized_at=observed, effective_until=end)
        try:
            durable_evidence = self._evidence.create_or_replay(command, session=tx)
            durable_activation = self._activations.create_or_replay(activation, session=tx)
        except (PrivilegedBreakGlassEvidenceConflictError, PrivilegedActivationConflictError, PrivilegedActivationError) as error:
            raise PrivilegedBreakGlassServiceError("BREAK_GLASS_PERSISTENCE_CONFLICT") from error
        if durable_evidence != command or durable_activation != activation:
            raise PrivilegedBreakGlassServiceError("BREAK_GLASS_PERSISTENCE_MISMATCH")
        return PrivilegedBreakGlassResult(durable_evidence, durable_activation)


__all__ = ["VERSION", "PrivilegedBreakGlassServiceError", "PrivilegedBreakGlassResult", "PrivilegedBreakGlassService"]

# ARTIFACT: privileged_break_glass_service.py
# VERSION: v1.0.0-P7-GOVERNED-PRIVILEGED-BREAK-GLASS-SERVICE
# AUTHORITY BOUNDARY: dual-control P7 issuance of one exact P4 activation only
# TENANT POSTURE: exact P2 target scope; platform tenant material forbidden
# FAIL-CLOSED POSTURE: stale authority, insufficient assurance, replay divergence, terminal state, and persistence failure reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
