"""Direct adversarial P6D Billing customer/commercial-authority certificate.

TITLE: Wilsy OS Process-Service Client Billing Authority Certificate
VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-BILLING-AUTHORITY-CERT
AUTHORITY: Wilsy OS Core Governance
TENANT BOUNDARY: Explicit tenant/customer/profile identities; no inference.
AUTHORITY BOUNDARY: Profile, binding, and derived context only.
FINANCIAL AUTHORITY: Kennel EOS exclusively owns execution and settlement.
FAIL-CLOSED: Missing, divergent, corrupt, or cross-tenant evidence rejects.
CERTIFICATION / UPDATE DATE: 2026-09-15
"""
from datetime import datetime, timedelta, timezone
from dataclasses import FrozenInstanceError, replace

import pytest

from tools.eos.saas.billing.process_service_client_billing_authority import (
    ClientBillingProfileVersion,
    CollectionMethod,
    CollectionMethodPolicy,
    DueDatePolicy,
    DueDateRule,
    InstructionBillingBinding,
    PaymentTerms,
    PaymentTermsRule,
    ProcessServiceClientBillingAuthorityError,
    TaxCalculationScope,
    TaxPolicy,
    TaxRoundingRule,
    TaxTreatment,
)
from tools.eos.saas.billing.process_service_client_billing_registry import ProcessServiceClientBillingRegistry, ProcessServiceClientBillingRegistryError
from tools.eos.saas.billing.process_service_client_billing_authority import derive_process_service_commercial_context, assess_process_service_invoice_readiness

BASE = datetime(2026, 9, 15, 10, 0, tzinfo=timezone.utc)


class FakeCollection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[dict[str, object]] = []

    def create_index(self, keys: object, **kwargs: object) -> str:
        self.indexes.append({"key": keys, **kwargs}); return str(kwargs.get("name", "index"))

    def _match(self, row: dict[str, object], query: dict[str, object]) -> bool:
        for key, expected in query.items():
            current: object = row
            for part in key.split("."):
                if not isinstance(current, dict) or part not in current: return False
                current = current[part]
            if current != expected: return False
        return True

    def find_one(self, query: dict[str, object], *, session: object = None) -> dict[str, object] | None:
        return next((row for row in self.rows if self._match(row, query)), None)

    def insert_one(self, record: dict[str, object], *, session: object = None) -> object:
        if any(self._match(row, {"tenant_id": record["tenant_id"], "evidence_identity": record["evidence_identity"]}) for row in self.rows):
            from pymongo.errors import DuplicateKeyError
            raise DuplicateKeyError("duplicate")
        self.rows.append(dict(record)); return object()


def _profile(tenant: str = "tenant-a", version: str = "profile-v1") -> ClientBillingProfileVersion:
    return ClientBillingProfileVersion(
        tenant_id=tenant, billing_profile_id="profile-1", billing_profile_version_id=version,
        customer_id="customer-1", customer_legal_name="Example Customer", customer_tax_id=None,
        customer_email="billing@example.test", customer_phone=None, seller_jurisdiction="ZA-GP",
        customer_jurisdiction="ZA-GP", tax_policy=TaxPolicy("tax-policy", "tax-v1", TaxTreatment.EXEMPT, None, TaxCalculationScope.LINE, TaxRoundingRule.HALF_UP_MINOR_UNIT, False),
        payment_terms=PaymentTerms("terms", "terms-v1", PaymentTermsRule.DAYS_AFTER_ISSUE, 14),
        due_date_policy=DueDatePolicy("due", "due-v1", DueDateRule.ISSUE_DATE_PLUS_PAYMENT_TERMS),
        collection_method=CollectionMethodPolicy("collection", "collection-v1", CollectionMethod.SEND_INVOICE),
        effective_from=BASE, effective_to=None, evidence_reference="profile-evidence",
    )


def _binding(tenant: str = "tenant-a", profile_version: str = "profile-v1", instruction: str = "instruction-1") -> InstructionBillingBinding:
    return InstructionBillingBinding(tenant, "binding-1", instruction, "profile-1", profile_version, BASE + timedelta(minutes=1), "binding-evidence")


def test_profile_is_explicit_immutable_and_fingerprinted() -> None:
    profile = _profile()
    assert profile.to_dict() == profile.to_dict() and profile.fingerprint == profile.fingerprint
    with pytest.raises(FrozenInstanceError):
        profile.customer_id = "other"  # type: ignore[misc]
    with pytest.raises(ProcessServiceClientBillingAuthorityError, match="P6D_TENANT_INVALID"):
        _profile("global")
    with pytest.raises(ProcessServiceClientBillingAuthorityError, match="P6D_CUSTOMER_ID_INVALID"):
        replace(profile, customer_id="")


def test_tax_requires_explicit_integer_rate_and_customer_tax_when_required() -> None:
    with pytest.raises(ProcessServiceClientBillingAuthorityError, match="P6D_TAX_RATE_REQUIRED"):
        TaxPolicy("tax", "v1", TaxTreatment.TAXABLE, None, TaxCalculationScope.LINE, TaxRoundingRule.DOWN_MINOR_UNIT, False)
    with pytest.raises(ProcessServiceClientBillingAuthorityError, match="P6D_TAX_RATE_NOT_APPLICABLE"):
        TaxPolicy("tax", "v1", TaxTreatment.EXEMPT, 1500, TaxCalculationScope.LINE, TaxRoundingRule.DOWN_MINOR_UNIT, False)
    with pytest.raises(ProcessServiceClientBillingAuthorityError, match="P6D_CUSTOMER_TAX_ID_REQUIRED"):
        replace(_profile(), tax_policy=TaxPolicy("tax", "v1", TaxTreatment.TAXABLE, 1500, TaxCalculationScope.LINE, TaxRoundingRule.DOWN_MINOR_UNIT, True))


def test_binding_is_explicit_and_does_not_infer_customer() -> None:
    binding = _binding()
    assert binding.instruction_id == "instruction-1" and binding.billing_profile_version_id == "profile-v1"
    with pytest.raises(ProcessServiceClientBillingAuthorityError, match="P6D_TENANT_INVALID"):
        _binding("root")


def test_registry_replay_divergence_and_tenant_isolation() -> None:
    profiles = FakeCollection(); bindings = FakeCollection()
    ProcessServiceClientBillingRegistry.ensure_indexes(profiles, bindings)
    profile = _profile(); stored = ProcessServiceClientBillingRegistry.create_profile(profile, profiles)
    replay = ProcessServiceClientBillingRegistry.create_profile(profile, profiles)
    assert replay.to_dict() == stored.to_dict() and len(profiles.rows) == 1
    with pytest.raises(ProcessServiceClientBillingRegistryError, match="P6D_REPLAY_CONFLICT"):
        ProcessServiceClientBillingRegistry.create_profile(replace(profile, customer_id="customer-2"), profiles)
    with pytest.raises(ProcessServiceClientBillingRegistryError, match="P6D_NOT_FOUND"):
        ProcessServiceClientBillingRegistry.get_profile("tenant-b", profile.fingerprint, profiles)


def test_binding_history_is_immutable_and_instruction_cannot_switch_profile() -> None:
    bindings = FakeCollection(); first = _binding(); ProcessServiceClientBillingRegistry.create_binding(first, bindings)
    assert ProcessServiceClientBillingRegistry.create_binding(first, bindings).to_dict() == first.to_dict()
    with pytest.raises(ProcessServiceClientBillingRegistryError, match="P6D_REPLAY_CONFLICT"):
        ProcessServiceClientBillingRegistry.create_binding(_binding(profile_version="profile-v2"), bindings)
    with pytest.raises(ProcessServiceClientBillingRegistryError, match="P6D_NOT_FOUND"):
        ProcessServiceClientBillingRegistry.get_binding("tenant-b", first.fingerprint, bindings)


def test_policy_and_registry_expose_no_invoice_or_execution_authority() -> None:
    import tools.eos.saas.billing.process_service_client_billing_authority as module
    forbidden = {"ClientInvoice", "Quotation", "Receivable", "Payment", "Settlement", "execute_payment", "settle"}
    assert not forbidden.intersection(dir(module))
    assert "Kennel EOS" in (module.__doc__ or "")


def test_context_preserves_p6c_amount_currency_and_removes_only_five_commercial_blockers() -> None:
    from tests.unit.test_process_service_client_invoice_handoff import _basis
    context = derive_process_service_commercial_context(p6c_basis=_basis(), binding=_binding(), profile=_profile())
    assert context.eligible_minor_units == 12500 and context.currency == "ZAR"
    assert context.instruction_id == "instruction-1" and context.customer_id == "customer-1"
    status, blockers = assess_process_service_invoice_readiness(context)
    assert status == "BLOCKED" and blockers == ("MONEY_ROUNDTRIP_UNSAFE",)
    with pytest.raises(ProcessServiceClientBillingAuthorityError, match="P6D_PROFILE_BINDING_MISMATCH"):
        derive_process_service_commercial_context(p6c_basis=_basis(), binding=_binding(profile_version="other"), profile=_profile())


# ARTIFACT: test_process_service_client_billing_authority.py
# VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-BILLING-AUTHORITY-CERT
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
