"""WILSY OS AI Legal Tool Gateway contract.

TITLE: WILSY OS AI Legal Tool Pre-Read Admission and Invocation Evidence
VERSION: v1.3.0-CX18-PRE-READ-ADMISSION
AUTHORITY: Pure composition of current IAM, entitlement, capacity, tool, and input evidence.
EPITOME: Separates non-persistent pre-read admission from immutable post-read
         invocation evidence for seven tenant-scoped legal read tools.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/domain/legal_ai_gateway.py
COLLABORATION / OWNERSHIP: The HTTP gateway supplies current canonical IAM and
                            commercial evidence; domain adapters own reads; the
                            invocation registry owns immutable evidence persistence.
CERTIFICATION / UPDATE DATE: 2026-10-13
CHANGELOG: v1.3.0-CX18 extracts require_legal_ai_tool_admission as the sole
           decision-bearing pre-read gate and build_legal_ai_tool_invocation_evidence
           as post-read construction, while retaining authorize_legal_ai_tool
           compatibility and the existing persisted evidence schema.
           v1.2.0-D57C-R1 established canonical reasoning entitlement and VAS
           capability admission independently from per-tool Legal IAM.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No prompt, reasoning, secret, provider payload, or
                             caller-asserted tenant/role/permission is accepted.
TENANT BOUNDARY: Exact non-pseudo tenant agreement across current gateway IAM,
                 underlying-domain IAM, entitlement, and capacity evidence.
AUTHORITY BOUNDARY: Admission and evidence composition only; no durable IAM,
                    legal lifecycle, entitlement, usage, or transaction authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
FAIL-CLOSED DECLARATION: Unknown tools, stale/denied IAM, tenant divergence,
                         inactive commercial evidence, exhausted capacity,
                         malformed input, and invalid result evidence reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Any, Final, cast

from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.saas.billing.subscription_wilsy_ai_entitlement_composition_service import CANONICAL_CAPABILITY_GRANTS
from tools.eos.saas.billing.wilsy_ai_commercial_policy import get_wilsy_ai_commercial_policy
from tools.eos.saas.billing.wilsy_ai_entitlement_provisioning import MODULE_ID as REASONING_MODULE_ID
from tools.eos.saas.billing.wilsy_ai_usage_capacity import WilsyAIUsageCapacity
from tools.eos.saas.domain.wilsy_ai_entitlement import WilsyAIEntitlement, WilsyAIEntitlementState

VERSION: Final[str] = "v1.3.0-CX18-PRE-READ-ADMISSION"
SCHEMA: Final[str] = "WILSY-AI-LEGAL-TOOL-GATEWAY/V1"
# Frozen because it participates in the persisted V1 fingerprint. Changing it
# would turn exact pre-CX18 replays into false divergence conflicts.
EVIDENCE_GATEWAY_VERSION: Final[str] = "v1.2.0-D57C-R1-WILSY-AI-LEGAL-RUNTIME-ADMISSION"
GATEWAY_PERMISSION: Final[str] = "wilsy_ai:legal_tool:read"
_HEX = re.compile(r"^[0-9a-f]{128}$")
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_TENANT_FORBIDDEN = frozenset({"default", "global", "root", "*", "global_root"})
CAPABILITIES: Final[tuple[str, ...]] = (
    "legal.read.instruction", "legal.read.attempt", "legal.read.execution",
    "legal.read.return", "legal.read.tariff_assessment",
    "legal.read.billing_eligibility", "legal.read.invoice",
)
AI_VAS_CAPABILITY: Final[str] = CANONICAL_CAPABILITY_GRANTS[0]
TOOL_IDENTITIES: Final[tuple[str, ...]] = (
    "legal.instruction.read.v1", "legal.attempt.read.v1", "legal.execution.read.v1",
    "legal.return.read.v1", "legal.tariff_assessment.read.v1",
    "legal.billing_eligibility.read.v1", "legal.invoice.read.v1",
)


class LegalAIToolGatewayError(ValueError):
    """Fail-closed admission or immutable-evidence contract fracture."""


@dataclass(frozen=True, slots=True)
class LegalAIToolContract:
    """Immutable allowlisted read-tool projection that grants no authority."""

    identity: str
    version: str
    underlying_permission: str
    capability: str
    entity_type: str
    pii_class: str
    allowed_fields: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.identity not in TOOL_IDENTITIES or self.version != "v1":
            raise LegalAIToolGatewayError("L7B_TOOL_IDENTITY_INVALID")
        if self.capability not in CAPABILITIES or not self.underlying_permission.startswith("legal_operations:"):
            raise LegalAIToolGatewayError("L7B_TOOL_CONTRACT_INVALID")
        if not self.allowed_fields or any(not isinstance(field, str) or not field.strip() for field in self.allowed_fields):
            raise LegalAIToolGatewayError("L7B_TOOL_FIELDS_INVALID")


TOOL_CONTRACTS: Final[dict[str, LegalAIToolContract]] = {
    "legal.instruction.read.v1": LegalAIToolContract("legal.instruction.read.v1", "v1", "legal_operations:instruction:read", "legal.read.instruction", "LegalInstruction", "LEGAL_PII", ("tenant_id", "instruction_id", "document_id", "state", "evidence_identity")),
    "legal.attempt.read.v1": LegalAIToolContract("legal.attempt.read.v1", "v1", "legal_operations:attempt:read", "legal.read.attempt", "ServiceAttempt", "LEGAL_PII", ("tenant_id", "attempt_id", "instruction_id", "document_id", "deputy_id", "state", "evidence_identity")),
    "legal.execution.read.v1": LegalAIToolContract("legal.execution.read.v1", "v1", "legal_operations:return:read", "legal.read.execution", "ServiceExecution", "LEGAL_PII", ("tenant_id", "execution_id", "attempt_id", "executed_at", "evidence_identity")),
    "legal.return.read.v1": LegalAIToolContract("legal.return.read.v1", "v1", "legal_operations:return:read", "legal.read.return", "ReturnOfService", "LEGAL_PII", ("tenant_id", "return_id", "execution_id", "attempt_id", "evidence_identity")),
    "legal.tariff_assessment.read.v1": LegalAIToolContract("legal.tariff_assessment.read.v1", "v1", "legal_operations:billing:read", "legal.read.tariff_assessment", "ProcessServiceTariffAssessment", "LEGAL_PII", ("tenant_id", "tariff_assessment_id", "service_execution_id", "assessed_total_minor_units", "currency")),
    "legal.billing_eligibility.read.v1": LegalAIToolContract("legal.billing_eligibility.read.v1", "v1", "legal_operations:billing:read", "legal.read.billing_eligibility", "ProcessServiceBillingEligibility", "LEGAL_PII", ("tenant_id", "billing_eligibility_id", "tariff_assessment_id", "eligible_minor_units", "currency")),
    "legal.invoice.read.v1": LegalAIToolContract("legal.invoice.read.v1", "v1", "legal_operations:invoice:read", "legal.read.invoice", "ClientInvoice", "LEGAL_PII", ("tenant_id", "invoice_id", "billing_eligibility_id", "total_minor", "currency", "issued_at")),
}


def _text(value: object, code: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise LegalAIToolGatewayError(code)
    return value


def _bounded_identity(value: object, code: str) -> str:
    text = _text(value, code)
    if _IDENTITY.fullmatch(text) is None:
        raise LegalAIToolGatewayError(code)
    return text


def _aware(value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise LegalAIToolGatewayError("L7B_OCCURRED_AT_INVALID")
    return value.astimezone(timezone.utc)


def _digest(value: object, code: str) -> str:
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        raise LegalAIToolGatewayError(code)
    return value


def _json(value: object) -> object:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, tuple):
        return [_json(item) for item in value]
    return value


@dataclass(frozen=True, slots=True)
class LegalAIToolAdmission:
    """Pure bounded pre-read result; neither durable evidence nor authority."""

    tenant_id: str
    principal_id: str
    tool_identity: str
    tool_version: str
    gateway_permission: str
    underlying_permission: str
    capability: str
    business_role: str
    entitlement_id: str
    entitlement_revision: int
    entitlement_fingerprint: str
    tier: str
    policy_fingerprint: str
    capacity_evidence_reference: str
    capacity_evidence_fingerprint: str
    resource_identity: str
    correlation_id: str
    input_fingerprint: str


@dataclass(frozen=True, slots=True)
class LegalAIToolInvocationEvidence:
    """Bounded immutable post-read fact; excludes prompts, reasoning, and secrets."""

    invocation_id: str
    tenant_id: str
    principal_id: str
    tool_identity: str
    tool_version: str
    gateway_permission: str
    underlying_permission: str
    capability: str
    business_role: str
    entitlement_id: str
    entitlement_revision: int
    entitlement_fingerprint: str
    tier: str
    policy_fingerprint: str
    capacity_evidence_reference: str
    capacity_evidence_fingerprint: str
    correlation_id: str
    input_fingerprint: str
    result_classification: str
    result_reference: str
    result_fingerprint: str
    occurred_at: datetime
    schema: str = SCHEMA
    gateway_version: str = EVIDENCE_GATEWAY_VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        for value in (self.invocation_id, self.tenant_id, self.principal_id, self.tool_identity, self.tool_version, self.underlying_permission, self.capability, self.business_role, self.entitlement_id, self.tier, self.capacity_evidence_reference, self.correlation_id, self.result_classification, self.result_reference):
            _text(value, "L7B_EVIDENCE_TEXT_INVALID")
        if self.tenant_id.lower() in _TENANT_FORBIDDEN or self.tool_identity not in TOOL_CONTRACTS or self.gateway_permission != GATEWAY_PERMISSION:
            raise LegalAIToolGatewayError("L7B_EVIDENCE_BINDING_INVALID")
        if not isinstance(self.entitlement_revision, int) or isinstance(self.entitlement_revision, bool) or self.entitlement_revision < 0:
            raise LegalAIToolGatewayError("L7B_EVIDENCE_REVISION_INVALID")
        for value in (self.entitlement_fingerprint, self.policy_fingerprint, self.capacity_evidence_fingerprint, self.input_fingerprint, self.result_fingerprint):
            _digest(value, "L7B_EVIDENCE_FINGERPRINT_INVALID")
        object.__setattr__(self, "occurred_at", _aware(self.occurred_at))
        payload = {name: _json(getattr(self, name)) for name in _EVIDENCE_FIELDS[:-1]}
        digest = hashlib.sha3_512(json.dumps(payload, ensure_ascii=False, sort_keys=False, separators=(",", ":")).encode()).hexdigest()
        if self.fingerprint and not hmac.compare_digest(self.fingerprint, digest):
            raise LegalAIToolGatewayError("L7B_EVIDENCE_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Return exact bounded evidence without hidden model/provider data."""
        return {name: _json(getattr(self, name)) for name in _EVIDENCE_FIELDS}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LegalAIToolInvocationEvidence":
        """Hydrate strict evidence and verify its deterministic fingerprint."""
        if not isinstance(payload, Mapping) or set(payload) != set(_EVIDENCE_FIELDS):
            raise LegalAIToolGatewayError("L7B_EVIDENCE_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        occurred = values.get("occurred_at")
        if isinstance(occurred, str):
            try:
                values["occurred_at"] = datetime.fromisoformat(occurred.replace("Z", "+00:00"))
            except ValueError as error:
                raise LegalAIToolGatewayError("L7B_OCCURRED_AT_INVALID") from error
        item = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, item.fingerprint):
            raise LegalAIToolGatewayError("L7B_EVIDENCE_FINGERPRINT_MISMATCH")
        return item


_EVIDENCE_FIELDS: Final[tuple[str, ...]] = (
    "invocation_id", "tenant_id", "principal_id", "tool_identity", "tool_version",
    "gateway_permission", "underlying_permission", "capability", "business_role",
    "entitlement_id", "entitlement_revision", "entitlement_fingerprint", "tier",
    "policy_fingerprint", "capacity_evidence_reference", "capacity_evidence_fingerprint",
    "correlation_id", "input_fingerprint", "result_classification", "result_reference",
    "result_fingerprint", "occurred_at", "schema", "gateway_version", "fingerprint",
)


def require_legal_ai_commercial_admission(*, tenant_id: str, entitlement: WilsyAIEntitlement, capacity: WilsyAIUsageCapacity) -> None:
    """Require current entitlement and capacity without creating authority or truth."""
    tenant = _text(tenant_id, "L7B_TENANT_REQUIRED")
    if not isinstance(entitlement, WilsyAIEntitlement) or not isinstance(capacity, WilsyAIUsageCapacity):
        raise LegalAIToolGatewayError("L7B_COMMERCIAL_EVIDENCE_INVALID")
    policy = get_wilsy_ai_commercial_policy(entitlement.tier)
    if (
        tenant.lower() in _TENANT_FORBIDDEN
        or entitlement.tenant_id != tenant or capacity.tenant_id != tenant
        or entitlement.module_id != REASONING_MODULE_ID
        or entitlement.lifecycle_state is not WilsyAIEntitlementState.ACTIVE
        or entitlement.policy_fingerprint != policy.policy_fingerprint
        or AI_VAS_CAPABILITY not in entitlement.capability_grants
        or capacity.entitlement_id != entitlement.entitlement_id
        or capacity.module_id != entitlement.module_id
        or capacity.entitlement_revision != entitlement.lifecycle_revision
        or not hmac.compare_digest(capacity.entitlement_fingerprint, entitlement.fingerprint)
    ):
        raise LegalAIToolGatewayError("L7B_ENTITLEMENT_DENIED")
    if capacity.daily_remaining_request_units <= 0 or capacity.monthly_remaining_automation_actions <= 0 or capacity.daily_exhausted or capacity.monthly_exhausted:
        raise LegalAIToolGatewayError("L7B_CAPACITY_EXHAUSTED")


def require_legal_ai_tool_admission(
    *, gateway_context: TenantAuthorizationContext,
    underlying_context: TenantAuthorizationContext,
    entitlement: WilsyAIEntitlement,
    capacity: WilsyAIUsageCapacity,
    tool_identity: str,
    input_payload: Mapping[str, object],
) -> LegalAIToolAdmission:
    """Perform every final decision-bearing gate before domain materialization.

    The operation is pure, non-persistent, and transaction-agnostic. Success is
    an ephemeral admission result, not invocation evidence or durable authority.
    """
    if not isinstance(gateway_context, TenantAuthorizationContext) or not isinstance(underlying_context, TenantAuthorizationContext):
        raise LegalAIToolGatewayError("L7B_CONTEXT_INVALID")
    contract = TOOL_CONTRACTS.get(tool_identity)
    if contract is None:
        raise LegalAIToolGatewayError("L7B_TOOL_UNKNOWN")
    tenant = _text(gateway_context.tenant_id, "L7B_TENANT_REQUIRED")
    if (
        tenant.lower() in _TENANT_FORBIDDEN
        or getattr(gateway_context.identity, "tenant_id", tenant) != tenant
        or underlying_context.tenant_id != tenant
        or getattr(underlying_context.identity, "tenant_id", tenant) != tenant
    ):
        raise LegalAIToolGatewayError("L7B_TENANT_MISMATCH")
    if (
        not gateway_context.decision.authorized
        or gateway_context.decision.reason.value != "AUTHORIZED"
        or not underlying_context.decision.authorized
        or underlying_context.decision.reason.value != "AUTHORIZED"
    ):
        raise LegalAIToolGatewayError("L7B_PERMISSION_DENIED")
    require_legal_ai_commercial_admission(tenant_id=tenant, entitlement=entitlement, capacity=capacity)
    if not isinstance(input_payload, Mapping) or set(input_payload) != {"resource_identity", "correlation_id"}:
        raise LegalAIToolGatewayError("L7B_INPUT_INVALID")
    resource_identity = _bounded_identity(input_payload["resource_identity"], "L7B_INPUT_INVALID")
    correlation_id = _bounded_identity(input_payload["correlation_id"], "L7B_INPUT_INVALID")
    canonical_input = {"correlation_id": correlation_id, "resource_identity": resource_identity}
    input_fingerprint = hashlib.sha3_512(json.dumps(canonical_input, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return LegalAIToolAdmission(
        tenant_id=tenant,
        principal_id=_text(gateway_context.identity.identity_id, "L7B_PRINCIPAL_REQUIRED"),
        tool_identity=tool_identity,
        tool_version=contract.version,
        gateway_permission=GATEWAY_PERMISSION,
        underlying_permission=contract.underlying_permission,
        capability=contract.capability,
        business_role=_text(underlying_context.decision.business_role, "L7B_BUSINESS_ROLE_REQUIRED"),
        entitlement_id=entitlement.entitlement_id,
        entitlement_revision=entitlement.lifecycle_revision,
        entitlement_fingerprint=entitlement.fingerprint,
        tier=str(getattr(entitlement.tier, "value", entitlement.tier)),
        policy_fingerprint=entitlement.policy_fingerprint,
        capacity_evidence_reference=f"capacity:{capacity.fingerprint}",
        capacity_evidence_fingerprint=capacity.fingerprint,
        resource_identity=resource_identity,
        correlation_id=correlation_id,
        input_fingerprint=input_fingerprint,
    )


def build_legal_ai_tool_invocation_evidence(
    *, admission: LegalAIToolAdmission,
    occurred_at: datetime,
    result_classification: str = "READ",
    result_reference: str = "",
) -> LegalAIToolInvocationEvidence:
    """Construct immutable evidence after read success without persisting it."""
    if not isinstance(admission, LegalAIToolAdmission):
        raise LegalAIToolGatewayError("L7B_ADMISSION_INVALID")
    classification = _text(result_classification, "L7B_RESULT_INVALID")
    reference = _text(result_reference or admission.resource_identity, "L7B_RESULT_INVALID")
    return LegalAIToolInvocationEvidence(
        invocation_id=admission.correlation_id, tenant_id=admission.tenant_id,
        principal_id=admission.principal_id, tool_identity=admission.tool_identity,
        tool_version=admission.tool_version, gateway_permission=admission.gateway_permission,
        underlying_permission=admission.underlying_permission, capability=admission.capability,
        business_role=admission.business_role, entitlement_id=admission.entitlement_id,
        entitlement_revision=admission.entitlement_revision,
        entitlement_fingerprint=admission.entitlement_fingerprint, tier=admission.tier,
        policy_fingerprint=admission.policy_fingerprint,
        capacity_evidence_reference=admission.capacity_evidence_reference,
        capacity_evidence_fingerprint=admission.capacity_evidence_fingerprint,
        correlation_id=admission.correlation_id, input_fingerprint=admission.input_fingerprint,
        result_classification=classification, result_reference=reference,
        result_fingerprint=hashlib.sha3_512(reference.encode()).hexdigest(),
        occurred_at=occurred_at,
    )


def authorize_legal_ai_tool(
    *, gateway_context: TenantAuthorizationContext,
    underlying_context: TenantAuthorizationContext,
    entitlement: WilsyAIEntitlement,
    capacity: WilsyAIUsageCapacity,
    tool_identity: str,
    input_payload: Mapping[str, object],
    occurred_at: datetime,
    result_classification: str = "READ",
    result_reference: str = "",
) -> LegalAIToolInvocationEvidence:
    """Compatibility composition of canonical admission plus evidence build."""
    admission = require_legal_ai_tool_admission(
        gateway_context=gateway_context, underlying_context=underlying_context,
        entitlement=entitlement, capacity=capacity, tool_identity=tool_identity,
        input_payload=input_payload,
    )
    return build_legal_ai_tool_invocation_evidence(
        admission=admission, occurred_at=occurred_at,
        result_classification=result_classification, result_reference=result_reference,
    )


__all__ = [
    "VERSION", "SCHEMA", "EVIDENCE_GATEWAY_VERSION", "GATEWAY_PERMISSION", "AI_VAS_CAPABILITY", "CAPABILITIES",
    "TOOL_IDENTITIES", "TOOL_CONTRACTS", "LegalAIToolGatewayError",
    "LegalAIToolContract", "LegalAIToolAdmission", "LegalAIToolInvocationEvidence",
    "require_legal_ai_commercial_admission", "require_legal_ai_tool_admission",
    "build_legal_ai_tool_invocation_evidence", "authorize_legal_ai_tool",
]

# ARTIFACT: legal_ai_gateway.py
# VERSION: v1.3.0-CX18-PRE-READ-ADMISSION
# AUTHORITY BOUNDARY: pure pre-read admission and bounded post-read evidence only
# TENANT POSTURE: exact current own-tenant IAM, entitlement, and capacity gates
# FAIL-CLOSED POSTURE: malformed, denied, divergent, stale, or exhausted inputs reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
