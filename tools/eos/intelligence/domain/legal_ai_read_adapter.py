"""Canonical read adapters for the seven WILSY AI legal-tool projections.

VERSION: v1.0.0-L7B-WILSY-AI-LEGAL-READ-ADAPTER
AUTHORITY: Delegation to existing L7A/L7C projection callables.
EPITOME: Provides one bounded adapter map so the AI gateway reuses canonical
         Legal Operations hydration, tenant predicates, client policy and P6F
         invoice correlation without copying those rules.
TENANT BOUNDARY: The supplied authorized context and canonical providers bind tenant scope.
AUTHORITY BOUNDARY: Read composition only; no authorization, lifecycle, billing, or persistence authority.
FINANCIAL AUTHORITY BOUNDARY: Invoice reads remain evidence only; Kennel EOS owns execution and settlement.
FAIL-CLOSED DECLARATION: Unknown contracts, missing collections and malformed projections reject.
CHANGELOG: v1.0.0 establishes the seven explicit async adapter mappings.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.api import legal_operations_router as l7a
from tools.eos.api import legal_operations_billing_read_router as l7c
from tools.eos.intelligence.domain.legal_ai_gateway import LegalAIToolContract, LegalAIToolGatewayError, TOOL_CONTRACTS

VERSION: Final[str] = "v1.0.0-L7B-WILSY-AI-LEGAL-READ-ADAPTER"


class LegalAIReadAdapterError(LegalAIToolGatewayError):
    """Raised when canonical legal projection composition cannot be proven."""


class LegalAIReadAdapter:
    """Delegate each allowlisted tool to its existing canonical router callable."""

    __slots__ = ()

    async def read(self, *, contract: LegalAIToolContract, resource_identity: str, context: TenantAuthorizationContext, collections: Mapping[str, Any]) -> dict[str, object]:
        """Read and reduce one canonical projection; no duplicate hydration occurs."""
        if contract.identity not in TOOL_CONTRACTS or not isinstance(resource_identity, str) or not resource_identity.strip():
            raise LegalAIReadAdapterError("L7B_READ_INPUT_INVALID")
        try:
            if contract.identity == "legal.instruction.read.v1":
                value = await l7a.get_instruction(resource_identity, context=context, collection=collections["lifecycle"])
            elif contract.identity == "legal.attempt.read.v1":
                value = await l7a.get_attempt(resource_identity, context=context, collection=collections["lifecycle"])
            elif contract.identity == "legal.execution.read.v1":
                value = await l7a.get_execution(resource_identity, context=context, collection=collections["lifecycle"])
            elif contract.identity == "legal.return.read.v1":
                value = await l7a.get_return_of_service(resource_identity, context=context, collection=collections["lifecycle"])
            elif contract.identity == "legal.tariff_assessment.read.v1":
                value = await l7c.get_tariff_assessment(resource_identity, context=context, collection=collections["tariff"])
            elif contract.identity == "legal.billing_eligibility.read.v1":
                value = await l7c.get_billing_eligibility(resource_identity, context=context, collection=collections["eligibility"])
            elif contract.identity == "legal.invoice.read.v1":
                value = await l7c.get_invoice(resource_identity, context=context, invoice_collection=collections["invoice"], issuance_collection=collections["issuance"])
            else:
                raise LegalAIReadAdapterError("L7B_TOOL_UNKNOWN")
        except KeyError as error:
            raise LegalAIReadAdapterError("L7B_READ_COLLECTION_UNAVAILABLE") from error
        if not isinstance(value, Mapping) or not isinstance(value.get("data"), Mapping):
            raise LegalAIReadAdapterError("L7B_READ_PROJECTION_INVALID")
        data = value["data"]
        return {key: data[key] for key in contract.allowed_fields if key in data}


__all__ = ["VERSION", "LegalAIReadAdapter", "LegalAIReadAdapterError"]
# ARTIFACT: legal_ai_read_adapter.py
# VERSION: v1.0.0-L7B-WILSY-AI-LEGAL-READ-ADAPTER
# AUTHORITY BOUNDARY: canonical L7A/L7C read delegation only
# TENANT POSTURE: exact context and canonical router predicates
# FAIL-CLOSED POSTURE: unknown, missing or malformed projections reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
