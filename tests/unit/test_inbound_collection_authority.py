"""WILSY OS M11 R8-R4 authorization-provenance inbound collection authority unit certificate.
TITLE: Provider-Neutral Inbound Collection Authority Certificate
VERSION: v1.1.0-M11-R8-R3B-P3-AUTHORIZATION-PROVENANCE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Directly certifies immutable source-family, tenant, amount, time, and digest law.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_inbound_collection_authority.py
COLLABORATION / OWNERSHIP: SaaS commercial-collection domain certificate owner.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.1.0-M11-R8-R3B-P3-AUTHORIZATION-PROVENANCE certifies exact authorization-evidence fingerprint binding; v1.0.0-M11-R8-R2 certified the provider-neutral authority domain without persistence or transport fixtures.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no credentials or external provider calls.
TENANT BOUNDARY: Every fixture is explicitly tenant-scoped.
AUTHORITY BOUNDARY: Domain certificate only; no invoice, execution, payment, settlement, or persistence authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains the exclusive execution authority.
TRANSACTION BOUNDARY: No Mongo, HTTP, registry, or issuance tests.
FAIL-CLOSED DECLARATION: Invalid source shape, provenance, family, identity, time, money, and schema reject.
"""
from __future__ import annotations

import dataclasses
from datetime import datetime, timezone
from pathlib import Path

import pytest

from tools.eos.saas.domain.commercial_receivable import ReceivableFamily
from tools.eos.saas.domain.inbound_collection_authority import (
    ClientCollectionSource,
    InboundCollectionAuthority,
    InboundCollectionAuthorityError,
    PlatformCollectionSource,
)


STAMP = datetime(2026, 9, 9, 8, 30, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128


def client_source(*, tenant_id: str = "tenant-a", customer_id: str | None = "customer-1") -> ClientCollectionSource:
    return ClientCollectionSource("tenant-a" if tenant_id == "tenant-a" else tenant_id, "client-invoice-1", "receivable-1", FP_A, FP_B, customer_id)


def platform_source(*, tenant_id: str = "tenant-a") -> PlatformCollectionSource:
    return PlatformCollectionSource(tenant_id, "platform-invoice-1", "receivable-1", FP_A, FP_B)


def authority(
    *,
    source: ClientCollectionSource | PlatformCollectionSource | None = None,
    family: ReceivableFamily = ReceivableFamily.CLIENT,
    tenant_id: str = "tenant-a",
    collection_authority_id: str = "authority-opaque-1",
    expected_amount_minor: int = 12500,
    currency: str = "ZAR",
    idempotency_key: str = "collect-1",
    issued_by_actor_id: str = "actor-1",
    authorization_reference: str = "auth-evidence-1",
    authorization_evidence_fingerprint: str = FP_C,
    created_at: datetime = STAMP,
    authorized_at: datetime = STAMP,
) -> InboundCollectionAuthority:
    return InboundCollectionAuthority(
        collection_authority_id,
        tenant_id,
        family,
        source if source is not None else client_source(),
        expected_amount_minor,
        currency,
        idempotency_key,
        issued_by_actor_id,
        authorization_reference,
        authorization_evidence_fingerprint,
        created_at,
        authorized_at,
    )


def test_valid_client_and_platform_construction_and_closed_family_pairing() -> None:
    client = authority()
    platform = authority(source=platform_source(), family=ReceivableFamily.PLATFORM)
    assert client.source_authority_kind is ReceivableFamily.CLIENT
    assert isinstance(client.source_authority, ClientCollectionSource)
    assert platform.source_authority_kind is ReceivableFamily.PLATFORM
    assert isinstance(platform.source_authority, PlatformCollectionSource)
    assert set(ReceivableFamily) == {ReceivableFamily.CLIENT, ReceivableFamily.PLATFORM}


@pytest.mark.parametrize("field", ["tenant_id", "collection_authority_id", "issued_by_actor_id", "authorization_reference"])
def test_required_authority_text_rejects_empty(field: str) -> None:
    values = {field: ""}
    with pytest.raises(InboundCollectionAuthorityError):
        authority(**values)  # type: ignore[arg-type]


def test_collection_id_is_caller_supplied_and_opaque() -> None:
    value = authority(collection_authority_id="opaque-token-123")
    assert value.collection_authority_id == "opaque-token-123"
    assert all(part not in value.collection_authority_id for part in ("tenant-a", "client-invoice-1", "receivable-1", "customer-1"))


def test_currency_normalizes_uppercase_without_provider_constraint() -> None:
    assert authority(currency=" zar ").currency == "ZAR"
    assert authority(currency="usd").currency == "USD"


@pytest.mark.parametrize("currency", ["", "US", "USDD", "12A", "ZÄR", "ZAR1"])
def test_malformed_currency_rejects(currency: str) -> None:
    with pytest.raises(InboundCollectionAuthorityError):
        authority(currency=currency)


@pytest.mark.parametrize("amount", [0, -1, True, False, 1.5, "12500"])
def test_positive_integer_amount_is_required(amount: object) -> None:
    with pytest.raises(InboundCollectionAuthorityError):
        authority(expected_amount_minor=amount)  # type: ignore[arg-type]


def test_source_fingerprints_are_required_sha3_hex() -> None:
    with pytest.raises(InboundCollectionAuthorityError):
        ClientCollectionSource("tenant-a", "invoice", "receivable", "", FP_B)
    with pytest.raises(InboundCollectionAuthorityError):
        ClientCollectionSource("tenant-a", "invoice", "receivable", FP_A, "")
    with pytest.raises(InboundCollectionAuthorityError):
        PlatformCollectionSource("tenant-a", "invoice", "receivable", FP_A, "not-a-digest")


@pytest.mark.parametrize("fingerprint", ["", "a" * 127, "a" * 129, "g" * 128, "A" * 128])
def test_authorization_evidence_fingerprint_requires_lowercase_sha3_512_hex(fingerprint: str) -> None:
    with pytest.raises(InboundCollectionAuthorityError):
        authority(authorization_evidence_fingerprint=fingerprint)


def test_authorization_evidence_fingerprint_is_required_and_semantic() -> None:
    value = authority()
    assert value.authorization_evidence_fingerprint == FP_C
    assert value.to_dict()["authorization_evidence_fingerprint"] == FP_C
    assert authority(authorization_evidence_fingerprint="d" * 128).fingerprint != value.fingerprint
    assert authority().fingerprint == authority().fingerprint


def test_family_type_pairing_and_source_tenant_are_exact() -> None:
    with pytest.raises(InboundCollectionAuthorityError):
        authority(source=platform_source(), family=ReceivableFamily.CLIENT)
    with pytest.raises(InboundCollectionAuthorityError):
        authority(source=client_source(), family=ReceivableFamily.PLATFORM)
    with pytest.raises(InboundCollectionAuthorityError):
        authority(source=client_source(tenant_id="tenant-b"))
    with pytest.raises(InboundCollectionAuthorityError):
        authority(family="CLIENT")  # type: ignore[arg-type]
    with pytest.raises(InboundCollectionAuthorityError):
        authority(source={"tenant_id": "tenant-a"})  # type: ignore[arg-type]


def test_customer_is_optional_for_client_and_forbidden_by_platform_shape() -> None:
    assert client_source(customer_id=None).customer_id is None
    assert "customer_id" not in platform_source().to_dict()
    assert "client_invoice_id" not in platform_source().to_dict()
    assert "platform_invoice_id" not in client_source().to_dict()
    with pytest.raises(InboundCollectionAuthorityError):
        client_source(customer_id=" ")


def test_idempotency_is_required_and_conservatively_trimmed() -> None:
    assert authority(idempotency_key="  key-1  ").idempotency_key == "key-1"
    for key in ("", "   "):
        with pytest.raises(InboundCollectionAuthorityError):
            authority(idempotency_key=key)


@pytest.mark.parametrize("field", ["created_at", "authorized_at"])
def test_times_must_be_caller_supplied_and_aware(field: str) -> None:
    with pytest.raises(InboundCollectionAuthorityError):
        authority(**{field: None})  # type: ignore[arg-type]
    with pytest.raises(InboundCollectionAuthorityError):
        authority(**{field: datetime(2026, 9, 9)})  # type: ignore[arg-type]


def test_times_are_canonicalized_to_utc() -> None:
    offset = datetime(2026, 9, 9, 10, 30, tzinfo=timezone.utc)
    value = authority(created_at=offset, authorized_at=offset)
    assert value.created_at.tzinfo == timezone.utc
    assert value.authorized_at.tzinfo == timezone.utc


def test_all_three_value_objects_are_immutable() -> None:
    values = [client_source(), platform_source(), authority()]
    for value in values:
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError, TypeError)):
            setattr(value, next(iter(dataclasses.fields(value))).name, "changed")


def test_fingerprint_is_deterministic_complete_and_sha3_512() -> None:
    one = authority()
    two = authority()
    assert one.fingerprint == two.fingerprint
    assert len(one.fingerprint) == 128
    assert one.fingerprint == one.fingerprint.lower()
    assert one.to_dict()["fingerprint"] == one.fingerprint
    assert set(one.to_dict()) == {
        "collection_authority_id", "tenant_id", "source_authority_kind", "source_authority",
        "expected_amount_minor", "currency", "idempotency_key", "issued_by_actor_id",
        "authorization_reference", "authorization_evidence_fingerprint", "created_at", "authorized_at", "fingerprint",
    }


@pytest.mark.parametrize(
    "field, value",
    [
        ("collection_authority_id", "authority-2"),
        ("expected_amount_minor", 12501),
        ("currency", "EUR"),
        ("idempotency_key", "collect-2"),
        ("issued_by_actor_id", "actor-2"),
        ("authorization_reference", "auth-evidence-2"),
        ("authorization_evidence_fingerprint", "d" * 128),
        ("created_at", datetime(2026, 9, 9, 8, 31, tzinfo=timezone.utc)),
        ("authorized_at", datetime(2026, 9, 9, 8, 31, tzinfo=timezone.utc)),
    ],
)
def test_each_authority_semantic_field_changes_fingerprint(field: str, value: object) -> None:
    original = authority()
    assert authority(**{field: value}).fingerprint != original.fingerprint  # type: ignore[arg-type]


def test_source_semantic_change_changes_fingerprint_and_families_do_not_collide() -> None:
    changed = ClientCollectionSource("tenant-a", "client-invoice-2", "receivable-1", FP_A, FP_B, "customer-1")
    assert authority(source=changed).fingerprint != authority().fingerprint
    assert authority().fingerprint != authority(source=platform_source(), family=ReceivableFamily.PLATFORM).fingerprint


def test_strict_round_trip_rejects_unknown_and_forged_fingerprint() -> None:
    payload = authority().to_dict()
    assert InboundCollectionAuthority.from_dict(payload) == authority()
    missing_authorization_fingerprint = dict(payload)
    missing_authorization_fingerprint.pop("authorization_evidence_fingerprint")
    with pytest.raises(InboundCollectionAuthorityError):
        InboundCollectionAuthority.from_dict(missing_authorization_fingerprint)
    unknown = dict(payload)
    unknown["provider"] = "forbidden"
    with pytest.raises(InboundCollectionAuthorityError):
        InboundCollectionAuthority.from_dict(unknown)
    forged = dict(payload)
    forged["fingerprint"] = "b" * 128
    with pytest.raises(InboundCollectionAuthorityError):
        InboundCollectionAuthority.from_dict(forged)


def test_authorization_reference_remains_opaque_and_domain_does_not_resolve_it() -> None:
    value = authority(authorization_reference="opaque-auth-reference")
    assert value.authorization_reference == "opaque-auth-reference"
    assert "TenantAuthorization" not in Path(__file__).parents[2].joinpath(
        "tools/eos/saas/domain/inbound_collection_authority.py"
    ).read_text(encoding="utf-8")


def test_authority_does_not_mutate_invoice_like_inputs() -> None:
    client_record = {"tenant_id": "tenant-a", "client_invoice_id": "client-invoice-1", "amount_paid": 0, "outstanding_amount": 125.0}
    platform_record = {"tenant_id": "tenant-a", "platform_invoice_id": "platform-invoice-1", "status": "OPEN"}
    client_before, platform_before = dict(client_record), dict(platform_record)
    authority(source=client_source())
    authority(source=platform_source(), family=ReceivableFamily.PLATFORM)
    assert client_record == client_before
    assert platform_record == platform_before


def test_production_boundary_has_no_external_or_outbound_dependencies() -> None:
    production = Path(__file__).parents[2] / "tools/eos/saas/domain/inbound_collection_authority.py"
    source = production.read_text(encoding="utf-8")
    forbidden_imports = (
        "from tools.eos.kennel", "import tools.eos.kennel", "import requests", "import http",
        "FinancialExecutionCommand", "FinancialExecutionAttempt", "VendorBill", "PaymentDestination",
        "m_payment_id", "pf_payment_id",
    )
    for forbidden in forbidden_imports:
        assert forbidden not in source
    assert "payfast" not in source.lower() and "payshap" not in source.lower()
    assert "ClientCollectionSource" in source and "PlatformCollectionSource" in source


def test_authority_has_no_lifecycle_or_provider_fields() -> None:
    names = {field.name for field in dataclasses.fields(InboundCollectionAuthority)}
    assert not names.intersection({"status", "provider", "paid", "settled", "settlement", "m_payment_id", "pf_payment_id"})


# ARTIFACT: test_inbound_collection_authority.py
# VERSION: v1.1.0-M11-R8-R3B-P3-AUTHORIZATION-PROVENANCE
# AUTHORITY BOUNDARY: Provider-neutral domain certificate only.
# TENANT POSTURE: Explicit tenant/source pairing and synthetic fixtures.
# FAIL-CLOSED POSTURE: Invalid authority data, authorization provenance, and digest drift reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
