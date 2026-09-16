"""WILSY OS AI Legal Tool Gateway contract.

VERSION: v1.1.0-L7B-WILSY-AI-LEGAL-TOOL-GATEWAY
AUTHORITY: Read-only composition of existing IAM, entitlement, capacity and legal evidence.
EPITOME: Defines exactly seven tenant-scoped legal read tools and immutable,
         bounded invocation evidence without becoming a legal or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/domain/legal_ai_gateway.py
TENANT BOUNDARY: Explicit non-pseudo tenant and authenticated own-tenant context only.
AUTHORITY BOUNDARY: Gateway access and evidence composition; no lifecycle mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution and settlement.
FAIL-CLOSED DECLARATION: Unknown tools, mismatched context, inactive entitlement,
                         missing capability/permission/capacity, malformed input or evidence reject.
CHANGELOG: v1.1.0 binds capacity to the canonical entitlement fingerprint while
           preserving independent policy-fingerprint evidence and all gates.
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
from tools.eos.saas.domain.wilsy_ai_entitlement import WilsyAIEntitlement, WilsyAIEntitlementState
from tools.eos.saas.billing.wilsy_ai_usage_capacity import WilsyAIUsageCapacity

VERSION: Final[str] = "v1.1.0-L7B-WILSY-AI-LEGAL-TOOL-GATEWAY"
SCHEMA: Final[str] = "WILSY-AI-LEGAL-TOOL-GATEWAY/V1"
GATEWAY_PERMISSION: Final[str] = "wilsy_ai:legal_tool:read"
_HEX = re.compile(r"^[0-9a-f]{128}$")
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_TENANT_FORBIDDEN = frozenset({"default", "global", "root", "*", "global_root"})
CAPABILITIES: Final[tuple[str, ...]] = (
    "legal.read.instruction", "legal.read.attempt", "legal.read.execution",
    "legal.read.return", "legal.read.tariff_assessment",
    "legal.read.billing_eligibility", "legal.read.invoice",
)
TOOL_IDENTITIES: Final[tuple[str, ...]] = (
    "legal.instruction.read.v1", "legal.attempt.read.v1", "legal.execution.read.v1",
    "legal.return.read.v1", "legal.tariff_assessment.read.v1",
    "legal.billing_eligibility.read.v1", "legal.invoice.read.v1",
)


class LegalAIToolGatewayError(ValueError):
    """Raised when a gateway contract cannot be established fail closed."""


@dataclass(frozen=True, slots=True)
class LegalAIToolContract:
    """Immutable allowlisted read-tool projection; it grants no authority."""

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
class LegalAIToolInvocationEvidence:
    """Bounded immutable invocation fact; excludes prompts, reasoning, tokens and secrets."""

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
    gateway_version: str = VERSION
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
        when = _aware(self.occurred_at)
        object.__setattr__(self, "occurred_at", when)
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
        values = dict(payload); stored = values.pop("fingerprint")
        occurred = values.get("occurred_at")
        if isinstance(occurred, str):
            try: values["occurred_at"] = datetime.fromisoformat(occurred.replace("Z", "+00:00"))
            except ValueError as error: raise LegalAIToolGatewayError("L7B_OCCURRED_AT_INVALID") from error
        item = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, item.fingerprint):
            raise LegalAIToolGatewayError("L7B_EVIDENCE_FINGERPRINT_MISMATCH")
        return item


_EVIDENCE_FIELDS: Final[tuple[str, ...]] = tuple(LegalAIToolInvocationEvidence.__dataclass_fields__) if False else (
    "invocation_id", "tenant_id", "principal_id", "tool_identity", "tool_version", "gateway_permission", "underlying_permission", "capability", "business_role", "entitlement_id", "entitlement_revision", "entitlement_fingerprint", "tier", "policy_fingerprint", "capacity_evidence_reference", "capacity_evidence_fingerprint", "correlation_id", "input_fingerprint", "result_classification", "result_reference", "result_fingerprint", "occurred_at", "schema", "gateway_version", "fingerprint"
)


def authorize_legal_ai_tool(*, gateway_context: TenantAuthorizationContext, underlying_context: TenantAuthorizationContext, entitlement: WilsyAIEntitlement, capacity: WilsyAIUsageCapacity, tool_identity: str, input_payload: Mapping[str, object], occurred_at: datetime, result_classification: str = "READ", result_reference: str = "") -> LegalAIToolInvocationEvidence:
    """Apply gateway, IAM, entitlement, capability, capacity and input gates."""
    if not isinstance(gateway_context, TenantAuthorizationContext) or not isinstance(underlying_context, TenantAuthorizationContext):
        raise LegalAIToolGatewayError("L7B_CONTEXT_INVALID")
    contract = TOOL_CONTRACTS.get(tool_identity)
    if contract is None: raise LegalAIToolGatewayError("L7B_TOOL_UNKNOWN")
    tenant = _text(gateway_context.tenant_id, "L7B_TENANT_REQUIRED")
    if tenant.lower() in _TENANT_FORBIDDEN or underlying_context.tenant_id != tenant or entitlement.tenant_id != tenant or capacity.tenant_id != tenant:
        raise LegalAIToolGatewayError("L7B_TENANT_MISMATCH")
    if not gateway_context.decision.authorized or gateway_context.decision.reason.value != "AUTHORIZED" or not underlying_context.decision.authorized or underlying_context.decision.reason.value != "AUTHORIZED":
        raise LegalAIToolGatewayError("L7B_PERMISSION_DENIED")
    if str(getattr(entitlement.lifecycle_state, "value", entitlement.lifecycle_state)) != WilsyAIEntitlementState.ACTIVE.value or entitlement.fingerprint != capacity.entitlement_fingerprint or contract.capability not in entitlement.capability_grants:
        raise LegalAIToolGatewayError("L7B_ENTITLEMENT_DENIED")
    if capacity.daily_remaining_request_units <= 0 or capacity.monthly_remaining_automation_actions <= 0 or capacity.daily_exhausted or capacity.monthly_exhausted:
        raise LegalAIToolGatewayError("L7B_CAPACITY_EXHAUSTED")
    if not isinstance(input_payload, Mapping) or set(input_payload) != {"resource_identity", "entitlement_id", "correlation_id"} or any(not isinstance(value, str) or not value.strip() for value in input_payload.values()) or _IDENTITY.fullmatch(str(input_payload["resource_identity"])) is None or input_payload["entitlement_id"] != entitlement.entitlement_id:
        raise LegalAIToolGatewayError("L7B_INPUT_INVALID")
    raw = json.dumps(dict(input_payload), sort_keys=True, separators=(",", ":")).encode()
    input_fp = hashlib.sha3_512(raw).hexdigest()
    return LegalAIToolInvocationEvidence(
        invocation_id=str(input_payload["correlation_id"]), tenant_id=tenant,
        principal_id=gateway_context.identity.identity_id, tool_identity=tool_identity,
        tool_version=contract.version, gateway_permission=GATEWAY_PERMISSION,
        underlying_permission=contract.underlying_permission, capability=contract.capability,
        business_role=underlying_context.decision.business_role or "", entitlement_id=entitlement.entitlement_id,
        entitlement_revision=entitlement.lifecycle_revision, entitlement_fingerprint=entitlement.fingerprint,
        tier=str(getattr(entitlement.tier, "value", entitlement.tier)), policy_fingerprint=entitlement.policy_fingerprint,
        capacity_evidence_reference=f"capacity:{capacity.fingerprint}", capacity_evidence_fingerprint=capacity.fingerprint,
        correlation_id=str(input_payload["correlation_id"]), input_fingerprint=input_fp,
        result_classification=result_classification, result_reference=result_reference or str(input_payload["resource_identity"]),
        result_fingerprint=hashlib.sha3_512(str(result_reference or input_payload["resource_identity"]).encode()).hexdigest(), occurred_at=occurred_at,
    )


__all__ = ["VERSION", "SCHEMA", "GATEWAY_PERMISSION", "CAPABILITIES", "TOOL_IDENTITIES", "TOOL_CONTRACTS", "LegalAIToolGatewayError", "LegalAIToolContract", "LegalAIToolInvocationEvidence", "authorize_legal_ai_tool"]
# ARTIFACT: legal_ai_gateway.py
# VERSION: v1.1.0-L7B-WILSY-AI-LEGAL-TOOL-GATEWAY
# AUTHORITY BOUNDARY: allowlisted read composition and bounded evidence only
# TENANT POSTURE: exact active own-tenant IAM/entitlement/capacity gates
# FAIL-CLOSED POSTURE: malformed, missing, divergent or exhausted inputs reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
