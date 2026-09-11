"""WILSY OS M11 R8-R3B-P4 typed inbound collection authorization certificate.
TITLE: Typed Inbound Collection Authorization Domain Certificate
VERSION: v1.1.0-M11-R8-R3B-P6D-EXPIRY-POLICY-PROVENANCE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Directly certifies immutable tenant/principal, typed receivable subject, provenance, expiry, and SHA3-512 evidence law.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_inbound_collection_authorization.py
COLLABORATION / OWNERSHIP: SaaS authorization-domain certificate owner.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.1.0-M11-R8-R3B-P6D-EXPIRY-POLICY-PROVENANCE-CERT certifies mandatory policy-version provenance, fingerprint divergence, and policy-neutral representability; v1.0.0-M11-R8-R3B-P4 certified the first typed inbound collection authorization evidence domain.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only; no credentials or external calls.
TENANT BOUNDARY: Every subject and top-level authorization fixture carries an explicit tenant.
AUTHORITY BOUNDARY: Immutable authorization evidence only; construction is not current validity, consumption, payment, settlement, or closure.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains the exclusive execution authority.
TRANSACTION BOUNDARY: Pure domain tests; no persistence, HTTP, registry, issuance, or provider tests.
FAIL-CLOSED DECLARATION: Invalid identity, operation, family pairing, provenance, amount, currency, time, expiry, schema, or digest rejects.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import hashlib
import inspect
import json
from pathlib import Path
from typing import Any

import pytest

from tools.eos.saas.domain.commercial_receivable import ReceivableFamily
from tools.eos.saas.domain.inbound_collection_authorization import (
    ClientInboundCollectionAuthorizationSubject,
    InboundCollectionAuthorization,
    InboundCollectionAuthorizationError,
    OPERATION,
    PlatformInboundCollectionAuthorizationSubject,
)


STAMP = datetime(2026, 9, 9, 9, 0, tzinfo=timezone.utc)
EXPIRY = STAMP + timedelta(hours=1)
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128
POLICY_V1 = "INBOUND_COLLECTION_AUTHORIZATION_EXPIRY_POLICY_V1"


def client_subject(**changes: object) -> ClientInboundCollectionAuthorizationSubject:
    values: dict[str, Any] = {
        "tenant_id": "tenant-a",
        "commercial_receivable_id": "receivable-a",
        "client_invoice_id": "invoice-a",
        "commercial_receivable_fingerprint": HEX_A,
        "client_invoice_fingerprint": HEX_B,
        "expected_outstanding_amount_minor": 12500,
        "currency": "ZAR",
        "customer_id": "customer-a",
    }
    values.update(changes)
    return ClientInboundCollectionAuthorizationSubject(**values)


def platform_subject(**changes: object) -> PlatformInboundCollectionAuthorizationSubject:
    values: dict[str, Any] = {
        "tenant_id": "tenant-a",
        "commercial_receivable_id": "receivable-platform-a",
        "platform_invoice_id": "platform-invoice-a",
        "commercial_receivable_fingerprint": HEX_A,
        "platform_invoice_fingerprint": HEX_B,
        "expected_outstanding_amount_minor": 12500,
        "currency": "ZAR",
    }
    values.update(changes)
    return PlatformInboundCollectionAuthorizationSubject(**values)


def authorization(**changes: object) -> InboundCollectionAuthorization:
    values: dict[str, Any] = {
        "inbound_collection_authorization_id": "ica-a",
        "tenant_id": "tenant-a",
        "principal_id": "principal-a",
        "operation": OPERATION,
        "subject_authority_kind": ReceivableFamily.CLIENT,
        "subject_authority": client_subject(),
        "tenant_authorization_decision_id": "decision-a",
        "tenant_authorization_evidence_fingerprint": HEX_C,
        "idempotency_key": "  idem-a  ",
        "authorized_at": STAMP,
        "expires_at": EXPIRY,
        "expiry_policy_version": POLICY_V1,
    }
    values.update(changes)
    return InboundCollectionAuthorization(**values)


def test_valid_client_and_platform_authorizations_reuse_canonical_family() -> None:
    client = authorization()
    platform = authorization(
        subject_authority_kind=ReceivableFamily.PLATFORM,
        subject_authority=platform_subject(),
    )
    assert isinstance(client.subject_authority, ClientInboundCollectionAuthorizationSubject)
    assert isinstance(platform.subject_authority, PlatformInboundCollectionAuthorizationSubject)
    assert set(ReceivableFamily) == {ReceivableFamily.CLIENT, ReceivableFamily.PLATFORM}
    assert client.operation == "authorize_inbound_collection"


@pytest.mark.parametrize("field", ["tenant_id", "commercial_receivable_id", "client_invoice_id"])
def test_client_required_text_rejects_empty(field: str) -> None:
    with pytest.raises(InboundCollectionAuthorizationError):
        client_subject(**{field: ""})


@pytest.mark.parametrize("field", ["tenant_id", "commercial_receivable_id", "platform_invoice_id"])
def test_platform_required_text_rejects_empty(field: str) -> None:
    with pytest.raises(InboundCollectionAuthorizationError):
        platform_subject(**{field: ""})


@pytest.mark.parametrize("field", ["inbound_collection_authorization_id", "tenant_id", "principal_id", "tenant_authorization_decision_id"])
def test_authorization_required_opaque_text_rejects_empty_or_surrounding_space(field: str) -> None:
    with pytest.raises(InboundCollectionAuthorizationError):
        authorization(**{field: ""})
    with pytest.raises(InboundCollectionAuthorizationError):
        authorization(**{field: " padded"})


def test_authorization_id_is_opaque_and_domain_does_not_generate_it() -> None:
    value = authorization(inbound_collection_authorization_id="wilsy-owned-opaque-id")
    assert value.inbound_collection_authorization_id == "wilsy-owned-opaque-id"
    assert "tenant-a" not in value.inbound_collection_authorization_id
    assert "invoice-a" not in value.inbound_collection_authorization_id


def test_operation_is_fixed_and_arbitrary_operations_reject() -> None:
    assert InboundCollectionAuthorization.OPERATION == OPERATION == "authorize_inbound_collection"
    with pytest.raises(InboundCollectionAuthorizationError):
        authorization(operation="collect_payment")
    with pytest.raises(InboundCollectionAuthorizationError):
        authorization(operation="authorize_inbound_collection ")


def test_family_pairing_is_closed_and_exact() -> None:
    with pytest.raises(InboundCollectionAuthorizationError):
        authorization(subject_authority_kind=ReceivableFamily.CLIENT, subject_authority=platform_subject())
    with pytest.raises(InboundCollectionAuthorizationError):
        authorization(subject_authority_kind=ReceivableFamily.PLATFORM, subject_authority=client_subject())
    with pytest.raises(InboundCollectionAuthorizationError):
        authorization(subject_authority_kind="CLIENT")
    with pytest.raises(InboundCollectionAuthorizationError):
        authorization(subject_authority_kind=ReceivableFamily.CLIENT, subject_authority=object())


def test_top_level_tenant_must_match_subject_tenant() -> None:
    with pytest.raises(InboundCollectionAuthorizationError):
        authorization(tenant_id="tenant-b")
    with pytest.raises(InboundCollectionAuthorizationError):
        authorization(subject_authority=client_subject(tenant_id="tenant-b"))


def test_client_subject_customer_is_optional_and_platform_has_no_customer_field() -> None:
    assert client_subject(customer_id=None).customer_id is None
    with pytest.raises(InboundCollectionAuthorizationError):
        client_subject(customer_id=" ")
    assert "customer_id" not in platform_subject().to_dict()
    assert "client_invoice_id" not in platform_subject().to_dict()


@pytest.mark.parametrize("subject_factory,field", [(client_subject, "client_invoice_fingerprint"), (client_subject, "commercial_receivable_fingerprint"), (platform_subject, "platform_invoice_fingerprint"), (platform_subject, "commercial_receivable_fingerprint")])
@pytest.mark.parametrize("bad", ["", "a" * 127, "a" * 129, "g" * 128, "A" * 128])
def test_invoice_and_receivable_fingerprints_require_lowercase_sha3_512(subject_factory, field: str, bad: str) -> None:
    with pytest.raises(InboundCollectionAuthorizationError):
        subject_factory(**{field: bad})


@pytest.mark.parametrize("amount", [0, -1, True, False, 1.5])
def test_subject_amount_requires_positive_integer(amount: object) -> None:
    with pytest.raises(InboundCollectionAuthorizationError):
        client_subject(expected_outstanding_amount_minor=amount)


def test_subject_amount_and_currency_are_bound_exactly_and_currency_is_canonicalized() -> None:
    value = client_subject(expected_outstanding_amount_minor=1, currency=" zar ")
    assert value.expected_outstanding_amount_minor == 1
    assert value.currency == "ZAR"
    with pytest.raises(InboundCollectionAuthorizationError):
        client_subject(currency="US")
    with pytest.raises(InboundCollectionAuthorizationError):
        client_subject(currency="ZAR1")


def test_upstream_tenant_authorization_provenance_is_required_and_strict() -> None:
    with pytest.raises(InboundCollectionAuthorizationError):
        authorization(tenant_authorization_decision_id="")
    for bad in ("", "a" * 127, "a" * 129, "g" * 128, "A" * 128):
        with pytest.raises(InboundCollectionAuthorizationError):
            authorization(tenant_authorization_evidence_fingerprint=bad)


def test_idempotency_is_required_and_trimmed_without_becoming_authority_to_change_subject() -> None:
    value = authorization()
    assert value.idempotency_key == "idem-a"
    with pytest.raises(InboundCollectionAuthorizationError):
        authorization(idempotency_key="   ")
    assert value.subject_authority.commercial_receivable_id == "receivable-a"


def test_authorization_times_are_aware_bounded_and_caller_supplied() -> None:
    value = authorization()
    assert value.authorized_at == STAMP and value.expires_at == EXPIRY
    with pytest.raises(InboundCollectionAuthorizationError):
        authorization(authorized_at=datetime(2026, 9, 9, 9, 0))
    with pytest.raises(InboundCollectionAuthorizationError):
        authorization(expires_at=datetime(2026, 9, 9, 10, 0))
    with pytest.raises(InboundCollectionAuthorizationError):
        authorization(expires_at=STAMP)
    with pytest.raises(InboundCollectionAuthorizationError):
        authorization(expires_at=STAMP - timedelta(seconds=1))


def test_expiry_policy_version_is_required_nonempty_and_future_representable() -> None:
    values: dict[str, Any] = {
        "inbound_collection_authorization_id": "ica-a",
        "tenant_id": "tenant-a",
        "principal_id": "principal-a",
        "operation": OPERATION,
        "subject_authority_kind": ReceivableFamily.CLIENT,
        "subject_authority": client_subject(),
        "tenant_authorization_decision_id": "decision-a",
        "tenant_authorization_evidence_fingerprint": HEX_C,
        "idempotency_key": "idem-a",
        "authorized_at": STAMP,
        "expires_at": EXPIRY,
    }
    with pytest.raises(TypeError):
        InboundCollectionAuthorization(**values)  # type: ignore[call-arg]
    with pytest.raises(InboundCollectionAuthorizationError):
        authorization(expiry_policy_version="")
    with pytest.raises(InboundCollectionAuthorizationError):
        authorization(expiry_policy_version="   ")
    future = authorization(expiry_policy_version="INBOUND_COLLECTION_AUTHORIZATION_EXPIRY_POLICY_V2")
    assert future.expiry_policy_version == "INBOUND_COLLECTION_AUTHORIZATION_EXPIRY_POLICY_V2"
    assert "expiry_policy_id" not in InboundCollectionAuthorization.__dataclass_fields__
    assert "duration_seconds" not in InboundCollectionAuthorization.__dataclass_fields__
    assert "ttl_seconds" not in InboundCollectionAuthorization.__dataclass_fields__


def test_domain_does_not_select_current_policy_or_calculate_expiry() -> None:
    value = authorization(expiry_policy_version="HISTORICAL_POLICY_VERSION")
    assert value.expires_at == EXPIRY
    source = Path(__file__).parents[2] / "tools/eos/saas/domain/inbound_collection_authorization.py"
    text = source.read_text(encoding="utf-8")
    assert "timedelta" not in text
    assert "datetime.now" not in text
    assert "INBOUND_COLLECTION_AUTHORIZATION_EXPIRY_POLICY_V1" not in text


def test_all_three_domain_objects_are_immutable() -> None:
    subject = client_subject()
    value = authorization()
    with pytest.raises(FrozenInstanceError):
        subject.tenant_id = "tenant-b"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        value.principal_id = "principal-b"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        value.subject_authority = platform_subject()  # type: ignore[misc]


def test_complete_evidence_fingerprint_is_deterministic_sha3_512_and_excludes_itself() -> None:
    one = authorization()
    two = authorization()
    assert one.authorization_evidence_fingerprint == two.authorization_evidence_fingerprint
    assert len(one.authorization_evidence_fingerprint) == 128
    assert one.authorization_evidence_fingerprint == one.authorization_evidence_fingerprint.lower()
    canonical = json.dumps(
        one._semantic_payload(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    assert one.authorization_evidence_fingerprint == hashlib.sha3_512(canonical).hexdigest()


@pytest.mark.parametrize(
    "field, replacement",
    [
        ("inbound_collection_authorization_id", "ica-b"),
        ("principal_id", "principal-b"),
        ("tenant_authorization_decision_id", "decision-b"),
        ("tenant_authorization_evidence_fingerprint", "d" * 128),
        ("idempotency_key", "idem-b"),
        ("authorized_at", STAMP + timedelta(seconds=1)),
        ("expires_at", EXPIRY + timedelta(seconds=1)),
        ("expiry_policy_version", "INBOUND_COLLECTION_AUTHORIZATION_EXPIRY_POLICY_V2"),
    ],
)
def test_each_top_level_semantic_change_changes_fingerprint(field: str, replacement: object) -> None:
    base = authorization()
    changed = replace(base, **{field: replacement})
    assert changed.authorization_evidence_fingerprint != base.authorization_evidence_fingerprint


def test_operation_family_and_complete_subject_participate_in_fingerprint() -> None:
    base = authorization()
    assert replace(base, operation=OPERATION).authorization_evidence_fingerprint == base.authorization_evidence_fingerprint
    platform = replace(base, subject_authority_kind=ReceivableFamily.PLATFORM, subject_authority=platform_subject())
    assert platform.authorization_evidence_fingerprint != base.authorization_evidence_fingerprint
    changed_subject = replace(base, subject_authority=client_subject(commercial_receivable_id="receivable-b"))
    assert changed_subject.authorization_evidence_fingerprint != base.authorization_evidence_fingerprint
    changed_amount = replace(base, subject_authority=client_subject(expected_outstanding_amount_minor=12501))
    assert changed_amount.authorization_evidence_fingerprint != base.authorization_evidence_fingerprint
    changed_currency = replace(base, subject_authority=client_subject(currency="EUR"))
    assert changed_currency.authorization_evidence_fingerprint != base.authorization_evidence_fingerprint


def test_changed_tenant_with_matching_subject_changes_fingerprint() -> None:
    base = authorization()
    changed = replace(base, tenant_id="tenant-b", subject_authority=client_subject(tenant_id="tenant-b"))
    assert changed.authorization_evidence_fingerprint != base.authorization_evidence_fingerprint


def test_to_dict_round_trip_is_strict_and_fingerprint_is_recomputed() -> None:
    value = authorization()
    persisted = value.to_dict()
    assert persisted["authorization_evidence_fingerprint"] == value.authorization_evidence_fingerprint
    assert InboundCollectionAuthorization.from_dict(persisted) == value
    with pytest.raises(InboundCollectionAuthorizationError):
        InboundCollectionAuthorization.from_dict({key: item for key, item in persisted.items() if key != "authorization_evidence_fingerprint"})
    with pytest.raises(InboundCollectionAuthorizationError):
        InboundCollectionAuthorization.from_dict({**persisted, "extra": True})
    with pytest.raises(InboundCollectionAuthorizationError):
        InboundCollectionAuthorization.from_dict({**persisted, "authorization_evidence_fingerprint": "b" * 128})


def test_domain_has_no_mutable_lifecycle_consumption_or_external_authority_fields() -> None:
    fields = set(InboundCollectionAuthorization.__dataclass_fields__)
    forbidden = {"is_revoked", "revoked_at", "is_consumed", "consumed_at", "collection_authority_id", "provider", "status", "settlement"}
    assert not forbidden.intersection(fields)
    source = Path(__file__).parents[2] / "tools/eos/saas/domain/inbound_collection_authorization.py"
    text = source.read_text(encoding="utf-8").lower()
    for forbidden_text in ("payfast", "payshap", "financialexecutioncommand", "financialexecutionattempt", "vendorbill", "paymentdestination", "clientinvoice", "platforminvoice", "pymongo", "requests", "http"):
        assert forbidden_text not in text
    assert "inbound_collection_authorization_id" in inspect.signature(InboundCollectionAuthorization).parameters


# ARTIFACT: test_inbound_collection_authorization.py
# VERSION: v1.1.0-M11-R8-R3B-P6D-EXPIRY-POLICY-PROVENANCE-CERT
# AUTHORITY BOUNDARY: Typed immutable authorization evidence certificate only.
# TENANT POSTURE: Explicit tenant and typed CLIENT/PLATFORM subject fixtures.
# FAIL-CLOSED POSTURE: Invalid identity, provenance, family, expiry, lifecycle, external dependency, and digest paths reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
