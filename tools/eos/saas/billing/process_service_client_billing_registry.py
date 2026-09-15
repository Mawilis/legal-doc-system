"""Caller-owned durable persistence for P6D Billing commercial authority.

TITLE: Wilsy OS Process-Service Client Billing Authority Registry
VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-BILLING-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Strict tenant-scoped Mongo persistence and hydration for immutable
         client billing profile versions and instruction/profile bindings.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/process_service_client_billing_registry.py
COLLABORATION / OWNERSHIP: P6D persistence only; P6D domain owns validation,
                            P6C owns process-service amount/lineage, caller owns
                            collection, session, transaction, commit, and abort.
CERTIFICATION / UPDATE DATE: 2026-09-15
CHANGELOG: 2026-09-15 v1.0.0-PROCESS-SERVICE-CLIENT-BILLING-REGISTRY adds strict
           immutable replay, corruption rejection, and tenant isolation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every read/write/replay query includes tenant_id.
AUTHORITY BOUNDARY: Persistence and hydration only; no derivation or invoice issuance.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
TRANSACTION BOUNDARY: Caller owns sessions and transactions; this module never
                      starts, commits, aborts, retries, or closes them.
FAIL-CLOSED DECLARATION: Unknown schema, payload, identity, fingerprint, tenant,
                         duplicate, or conflict rejects with a stable code.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
import hashlib
import json
import re
from typing import Any, Final, NoReturn, cast

from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.billing.process_service_client_billing_authority import (
    SCHEMA as P6D_SCHEMA,
    VERSION as P6D_VERSION,
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
    InvoiceTaxType,
)

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-CLIENT-BILLING-REGISTRY"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-CLIENT-BILLING-REGISTRY/V1"
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_FORBIDDEN = frozenset({"default", "global", "global_root", "root", "master", "*"})


class ProcessServiceClientBillingRegistryError(RuntimeError):
    """Stable persistence error retaining technical cause without fabricating truth."""

    def __init__(self, code: str, cause: BaseException | None = None) -> None:
        """Create a governed error with optional original Mongo cause."""
        self.code = code
        super().__init__(code)
        if cause is not None: self.__cause__ = cause


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    raise ProcessServiceClientBillingRegistryError(code, cause)


def _tenant(value: object) -> str:
    if not isinstance(value, str) or _IDENTITY.fullmatch(value) is None or value.casefold() in _FORBIDDEN: _fail("P6D_TENANT_INVALID")
    return value


def _sha3(value: object, code: str) -> str:
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None: _fail(code)
    return value


def _digest(value: object) -> str:
    data = json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha3_512(data).hexdigest()


def _record(value: ClientBillingProfileVersion | InstructionBillingBinding) -> dict[str, object]:
    payload = value.to_dict()
    identity = cast(ClientBillingProfileVersion, value).billing_profile_version_id if type(value) is ClientBillingProfileVersion else cast(InstructionBillingBinding, value).binding_id
    evidence_identity = _digest({"tenant_id": value.tenant_id, "entity_type": type(value).__name__, "entity_identity": identity, "fingerprint": value.fingerprint})
    return {"schema": SCHEMA, "version": VERSION, "entity_type": type(value).__name__, "tenant_id": value.tenant_id, "entity_identity": identity, "payload": payload, "fingerprint": value.fingerprint, "evidence_identity": evidence_identity}


def _canonical(raw: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(raw); result.pop("_id", None); return result


def _time(value: object) -> datetime:
    if not isinstance(value, str): _fail("P6D_PAYLOAD_TIMESTAMP_INVALID")
    try: parsed = datetime.fromisoformat(value)
    except ValueError as error: _fail("P6D_PAYLOAD_TIMESTAMP_INVALID", error)
    if parsed.tzinfo is None or parsed.utcoffset() is None: _fail("P6D_PAYLOAD_TIMESTAMP_INVALID")
    return parsed


def _policy(payload: Mapping[str, Any]) -> tuple[TaxPolicy, PaymentTerms, DueDatePolicy, CollectionMethodPolicy]:
    required = {"policy_id", "version_id", "treatment", "rate_basis_points", "calculation_scope", "rounding_rule", "requires_customer_tax_id"}
    if not isinstance(payload.get("tax_policy"), Mapping) or set(payload["tax_policy"]) != required: _fail("P6D_PAYLOAD_SCHEMA_INVALID")
    t = cast(Mapping[str, Any], payload["tax_policy"])
    try: tax = TaxPolicy(policy_id=t["policy_id"], version_id=t["version_id"], treatment=TaxTreatment(t["treatment"]), rate_basis_points=t["rate_basis_points"], calculation_scope=TaxCalculationScope(t["calculation_scope"]), rounding_rule=TaxRoundingRule(t["rounding_rule"]), requires_customer_tax_id=t["requires_customer_tax_id"])
    except (KeyError, ValueError, ProcessServiceClientBillingAuthorityError) as error: _fail("P6D_PAYLOAD_POLICY_INVALID", error)
    terms_required = {"terms_id", "version_id", "rule", "days_after_issue"}
    if not isinstance(payload.get("payment_terms"), Mapping) or set(payload["payment_terms"]) != terms_required: _fail("P6D_PAYLOAD_SCHEMA_INVALID")
    p = cast(Mapping[str, Any], payload["payment_terms"])
    try: terms = PaymentTerms(terms_id=p["terms_id"], version_id=p["version_id"], rule=PaymentTermsRule(p["rule"]), days_after_issue=p["days_after_issue"])
    except (KeyError, ValueError, ProcessServiceClientBillingAuthorityError) as error: _fail("P6D_PAYLOAD_POLICY_INVALID", error)
    due_required = {"policy_id", "version_id", "rule"}
    if not isinstance(payload.get("due_date_policy"), Mapping) or set(payload["due_date_policy"]) != due_required: _fail("P6D_PAYLOAD_SCHEMA_INVALID")
    d = cast(Mapping[str, Any], payload["due_date_policy"])
    try: due = DueDatePolicy(policy_id=d["policy_id"], version_id=d["version_id"], rule=DueDateRule(d["rule"]))
    except (KeyError, ValueError, ProcessServiceClientBillingAuthorityError) as error: _fail("P6D_PAYLOAD_POLICY_INVALID", error)
    coll_required = {"policy_id", "version_id", "method"}
    if not isinstance(payload.get("collection_method"), Mapping) or set(payload["collection_method"]) != coll_required: _fail("P6D_PAYLOAD_SCHEMA_INVALID")
    c = cast(Mapping[str, Any], payload["collection_method"])
    try: collection = CollectionMethodPolicy(policy_id=c["policy_id"], version_id=c["version_id"], method=CollectionMethod(c["method"]))
    except (KeyError, ValueError, ProcessServiceClientBillingAuthorityError) as error: _fail("P6D_PAYLOAD_POLICY_INVALID", error)
    return tax, terms, due, collection


def _hydrate(raw: Mapping[str, Any], tenant: str) -> ClientBillingProfileVersion | InstructionBillingBinding:
    value = _canonical(raw)
    required = {"schema", "version", "entity_type", "tenant_id", "entity_identity", "payload", "fingerprint", "evidence_identity"}
    if set(value) != required: _fail("P6D_RECORD_SCHEMA_INVALID")
    if value["schema"] != SCHEMA or value["version"] != VERSION or value["tenant_id"] != tenant or value["entity_type"] not in {"ClientBillingProfileVersion", "InstructionBillingBinding"}: _fail("P6D_RECORD_VERSION_OR_TENANT_INVALID")
    payload = value["payload"]
    if not isinstance(payload, Mapping): _fail("P6D_PAYLOAD_SCHEMA_INVALID")
    _sha3(value["fingerprint"], "P6D_RECORD_FINGERPRINT_INVALID"); _sha3(value["evidence_identity"], "P6D_EVIDENCE_IDENTITY_INVALID")
    try:
        if value["entity_type"] == "ClientBillingProfileVersion":
            fields = {"schema", "version", "entity_type", "tenant_id", "billing_profile_id", "billing_profile_version_id", "customer_id", "customer_legal_name", "customer_tax_id", "customer_email", "customer_phone", "seller_jurisdiction", "customer_jurisdiction", "tax_policy", "payment_terms", "due_date_policy", "collection_method", "effective_from", "effective_to", "evidence_reference"}
            optional_tax_type = payload.get("invoice_tax_type")
            allowed_fields = fields | {"invoice_tax_type"}
            if set(payload) != fields and set(payload) != allowed_fields: _fail("P6D_PAYLOAD_SCHEMA_INVALID")
            tax, terms, due, collection = _policy(payload)
            result: ClientBillingProfileVersion | InstructionBillingBinding = ClientBillingProfileVersion(tenant_id=payload["tenant_id"], billing_profile_id=payload["billing_profile_id"], billing_profile_version_id=payload["billing_profile_version_id"], customer_id=payload["customer_id"], customer_legal_name=payload["customer_legal_name"], customer_tax_id=payload["customer_tax_id"], customer_email=payload["customer_email"], customer_phone=payload["customer_phone"], seller_jurisdiction=payload["seller_jurisdiction"], customer_jurisdiction=payload["customer_jurisdiction"], tax_policy=tax, payment_terms=terms, due_date_policy=due, collection_method=collection, effective_from=_time(payload["effective_from"]), effective_to=None if payload["effective_to"] is None else _time(payload["effective_to"]), evidence_reference=payload["evidence_reference"], invoice_tax_type=None if optional_tax_type is None else InvoiceTaxType(optional_tax_type))
        else:
            fields = {"schema", "version", "entity_type", "tenant_id", "binding_id", "instruction_id", "billing_profile_id", "billing_profile_version_id", "bound_at", "evidence_reference"}
            if set(payload) != fields: _fail("P6D_PAYLOAD_SCHEMA_INVALID")
            result = InstructionBillingBinding(tenant_id=payload["tenant_id"], binding_id=payload["binding_id"], instruction_id=payload["instruction_id"], billing_profile_id=payload["billing_profile_id"], billing_profile_version_id=payload["billing_profile_version_id"], bound_at=_time(payload["bound_at"]), evidence_reference=payload["evidence_reference"])
    except ProcessServiceClientBillingAuthorityError as error: _fail("P6D_PAYLOAD_INVALID", error)
    if result.tenant_id != tenant or result.to_dict() != dict(payload) or result.fingerprint != value["fingerprint"]: _fail("P6D_RECORD_FINGERPRINT_INVALID")
    identity = cast(ClientBillingProfileVersion, result).billing_profile_version_id if type(result) is ClientBillingProfileVersion else cast(InstructionBillingBinding, result).binding_id
    expected = _digest({"tenant_id": tenant, "entity_type": value["entity_type"], "entity_identity": identity, "fingerprint": value["fingerprint"]})
    if value["entity_identity"] != identity or value["evidence_identity"] != expected: _fail("P6D_RECORD_IDENTITY_INVALID")
    return result


def _active(session: object) -> bool:
    marker = getattr(session, "in_transaction", False)
    try: return bool(marker() if callable(marker) else marker)
    except Exception: return False


def _persist(value: ClientBillingProfileVersion | InstructionBillingBinding, collection: Any, *, session: object = None) -> ClientBillingProfileVersion | InstructionBillingBinding:
    record = _record(value); query = {"tenant_id": value.tenant_id, "evidence_identity": record["evidence_identity"]}
    try: existing = collection.find_one(query, session=session)
    except PyMongoError as error: _fail("P6D_PERSISTENCE_UNAVAILABLE", error)
    if existing is not None:
        current = _hydrate(cast(Mapping[str, Any], existing), value.tenant_id)
        if _canonical(cast(Mapping[str, Any], existing)) == record: return current
        _fail("P6D_REPLAY_CONFLICT")
    try:
        prior = collection.find_one({"tenant_id": value.tenant_id, "entity_type": type(value).__name__, "entity_identity": record["entity_identity"]}, session=session)
    except PyMongoError as error: _fail("P6D_PERSISTENCE_UNAVAILABLE", error)
    if prior is not None: _fail("P6D_REPLAY_CONFLICT")
    if type(value) is InstructionBillingBinding:
        try: instruction_prior = collection.find_one({"tenant_id": value.tenant_id, "entity_type": "InstructionBillingBinding", "payload.instruction_id": value.instruction_id}, session=session)
        except PyMongoError as error: _fail("P6D_PERSISTENCE_UNAVAILABLE", error)
        if instruction_prior is not None:
            _hydrate(cast(Mapping[str, Any], instruction_prior), value.tenant_id); _fail("P6D_REPLAY_CONFLICT")
    try: collection.insert_one(record, session=session)
    except DuplicateKeyError as error:
        if _active(session): _fail("P6D_RETRY_TRANSACTION_REQUIRED", error)
        try: raced = collection.find_one(query, session=session)
        except PyMongoError as read_error: _fail("P6D_PERSISTENCE_UNAVAILABLE", read_error)
        if raced is not None and _canonical(cast(Mapping[str, Any], raced)) == record: return _hydrate(cast(Mapping[str, Any], raced), value.tenant_id)
        _fail("P6D_REPLAY_CONFLICT", error)
    except PyMongoError as error:
        if _active(session) and error.has_error_label("TransientTransactionError") and not error.has_error_label("UnknownTransactionCommitResult"): _fail("P6D_RETRY_TRANSACTION_REQUIRED", error)
        _fail("P6D_PERSISTENCE_UNAVAILABLE", error)
    return _hydrate(record, value.tenant_id)


class ProcessServiceClientBillingRegistry:
    """Persist immutable P6D records while retaining all caller ownership."""

    @staticmethod
    def ensure_indexes(profile_collection: Any, binding_collection: Any) -> None:
        """Create deterministic tenant-scoped unique identity indexes."""
        try:
            profile_collection.create_index([("tenant_id", 1), ("evidence_identity", 1)], unique=True, name="p6d_profile_evidence_unique")
            profile_collection.create_index([("tenant_id", 1), ("entity_type", 1), ("entity_identity", 1)], unique=True, name="p6d_profile_identity_unique")
            binding_collection.create_index([("tenant_id", 1), ("evidence_identity", 1)], unique=True, name="p6d_binding_evidence_unique")
            binding_collection.create_index([("tenant_id", 1), ("entity_type", 1), ("entity_identity", 1)], unique=True, name="p6d_binding_identity_unique")
            binding_collection.create_index([("tenant_id", 1), ("entity_type", 1), ("payload.instruction_id", 1)], unique=True, name="p6d_instruction_binding_unique")
        except PyMongoError as error: _fail("P6D_PERSISTENCE_UNAVAILABLE", error)

    @staticmethod
    def create_profile(profile: ClientBillingProfileVersion, collection: Any, *, session: object = None) -> ClientBillingProfileVersion:
        """Persist or exactly replay one immutable profile version."""
        if type(profile) is not ClientBillingProfileVersion: _fail("P6D_PROFILE_REQUIRED")
        return cast(ClientBillingProfileVersion, _persist(profile, collection, session=session))

    @staticmethod
    def create_binding(binding: InstructionBillingBinding, collection: Any, *, session: object = None) -> InstructionBillingBinding:
        """Persist or exactly replay one immutable instruction binding."""
        if type(binding) is not InstructionBillingBinding: _fail("P6D_BINDING_REQUIRED")
        return cast(InstructionBillingBinding, _persist(binding, collection, session=session))

    @staticmethod
    def get_profile(tenant_id: str, evidence_identity: str, collection: Any, *, session: object = None) -> ClientBillingProfileVersion:
        """Hydrate one exact tenant-scoped profile evidence identity."""
        tenant = _tenant(tenant_id); _sha3(evidence_identity, "P6D_EVIDENCE_IDENTITY_INVALID")
        try: raw = collection.find_one({"tenant_id": tenant, "evidence_identity": evidence_identity}, session=session)
        except PyMongoError as error: _fail("P6D_PERSISTENCE_UNAVAILABLE", error)
        if raw is None: _fail("P6D_NOT_FOUND")
        result = _hydrate(cast(Mapping[str, Any], raw), tenant)
        if type(result) is not ClientBillingProfileVersion: _fail("P6D_TYPE_MISMATCH")
        return result

    @staticmethod
    def get_binding(tenant_id: str, evidence_identity: str, collection: Any, *, session: object = None) -> InstructionBillingBinding:
        """Hydrate one exact tenant-scoped instruction binding."""
        tenant = _tenant(tenant_id); _sha3(evidence_identity, "P6D_EVIDENCE_IDENTITY_INVALID")
        try: raw = collection.find_one({"tenant_id": tenant, "evidence_identity": evidence_identity}, session=session)
        except PyMongoError as error: _fail("P6D_PERSISTENCE_UNAVAILABLE", error)
        if raw is None: _fail("P6D_NOT_FOUND")
        result = _hydrate(cast(Mapping[str, Any], raw), tenant)
        if type(result) is not InstructionBillingBinding: _fail("P6D_TYPE_MISMATCH")
        return result


__all__ = ["VERSION", "SCHEMA", "ProcessServiceClientBillingRegistry", "ProcessServiceClientBillingRegistryError"]

# ARTIFACT: process_service_client_billing_registry.py
# VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-BILLING-REGISTRY
# AUTHORITY BOUNDARY: immutable P6D persistence/hydration only.
# TENANT POSTURE: every operation is tenant-scoped and cross-tenant silent.
# FAIL-CLOSED POSTURE: corruption, replay divergence, races, and unsupported schemas reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns financial execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
