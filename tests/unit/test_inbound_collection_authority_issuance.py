"""WILSY OS M11 R8-R3B-P7 inbound collection-authority issuance certificate.
TITLE: Inbound Collection Authority Issuance Certificate
VERSION: v1.0.0-M11-R8-R3B-P7-INBOUND-COLLECTION-AUTHORITY-ISSUANCE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies idempotent replay, P5-derived provenance, strict boundaries, and atomic create-before-consume orchestration without external providers or database access.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_inbound_collection_authority_issuance.py
COLLABORATION / OWNERSHIP: SaaS collection-authority composition certificate owner; synthetic doubles exercise the caller-owned transaction contract.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.0.0-M11-R8-R3B-P7-INBOUND-COLLECTION-AUTHORITY-ISSUANCE-CERT certifies the complete bounded issuance slice, including Model-B key divergence, source replay precedence, lifecycle CAS correlation, and provider/AP/settlement firewalls.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic tenant-scoped values only; no secrets, network calls, provider adapters, or invoice mutations.
TENANT BOUNDARY: Every fixture and registry call carries the same explicit tenant identity.
AUTHORITY BOUNDARY: Tests cover collection-authority composition only; they cannot certify payment, settlement, or real Mongo behavior.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive for outbound financial execution truth.
TRANSACTION BOUNDARY: The fake active session records exact forwarding; the issuer never starts, commits, aborts, or nests transactions.
FAIL-CLOSED DECLARATION: Invalid request identity, replay divergence, stale lifecycle, race, and result-correlation failures reject.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import inspect
from pathlib import Path
from typing import Any, cast

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.saas.domain.commercial_receivable import ReceivableFamily
from tools.eos.saas.domain.inbound_collection_authorization import (
    ClientInboundCollectionAuthorizationSubject,
    InboundCollectionAuthorization,
    OPERATION,
    PlatformInboundCollectionAuthorizationSubject,
)
from tools.eos.saas.domain.inbound_collection_authority import (
    ClientCollectionSource,
    InboundCollectionAuthority,
    PlatformCollectionSource,
)
from tools.eos.saas.billing.inbound_collection_authorization_registry import (
    InboundCollectionAuthorizationLifecycleConflictError,
    InboundCollectionAuthorizationRecord,
)
from tools.eos.saas.billing.inbound_collection_authority_registry import (
    InboundCollectionAuthorityReplayConflictError,
)
from tools.eos.saas.billing import inbound_collection_authority_issuance as issuance


FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128
STAMP = datetime(2026, 9, 9, 8, 0, tzinfo=timezone.utc)
EXPIRY = STAMP + timedelta(hours=1)


class ActiveSession:
    """Minimal active caller-owned transaction marker."""

    in_transaction = True


ACTIVE = ActiveSession()


class FakeCollection:
    """Opaque collection handle; no database operations are performed by doubles."""


def client_authorization(
    *,
    authorization_id: str = "auth-a",
    tenant_id: str = "tenant-a",
    receivable_id: str = "receivable-a",
    idempotency_key: str = "auth-key-a",
    authorized_at: datetime = STAMP,
    expires_at: datetime = EXPIRY,
) -> InboundCollectionAuthorization:
    subject = ClientInboundCollectionAuthorizationSubject(
        tenant_id=tenant_id,
        commercial_receivable_id=receivable_id,
        client_invoice_id=f"client-invoice-{receivable_id}",
        commercial_receivable_fingerprint=FP_A,
        client_invoice_fingerprint=FP_B,
        expected_outstanding_amount_minor=12500,
        currency="ZAR",
        customer_id="customer-a",
    )
    return InboundCollectionAuthorization(
        inbound_collection_authorization_id=authorization_id,
        tenant_id=tenant_id,
        principal_id="principal-a",
        operation=OPERATION,
        subject_authority_kind=ReceivableFamily.CLIENT,
        subject_authority=subject,
        tenant_authorization_decision_id="decision-a",
        tenant_authorization_evidence_fingerprint=FP_C,
        idempotency_key=idempotency_key,
        authorized_at=authorized_at,
        expires_at=expires_at,
        expiry_policy_version="INBOUND_COLLECTION_AUTHORIZATION_EXPIRY_POLICY_V1",
    )


def platform_authorization() -> InboundCollectionAuthorization:
    subject = PlatformInboundCollectionAuthorizationSubject(
        tenant_id="tenant-a",
        commercial_receivable_id="platform-receivable-a",
        platform_invoice_id="platform-invoice-a",
        commercial_receivable_fingerprint=FP_A,
        platform_invoice_fingerprint=FP_B,
        expected_outstanding_amount_minor=12500,
        currency="ZAR",
    )
    return InboundCollectionAuthorization(
        inbound_collection_authorization_id="platform-auth-a",
        tenant_id="tenant-a",
        principal_id="principal-a",
        operation=OPERATION,
        subject_authority_kind=ReceivableFamily.PLATFORM,
        subject_authority=subject,
        tenant_authorization_decision_id="decision-platform-a",
        tenant_authorization_evidence_fingerprint=FP_C,
        idempotency_key="platform-auth-key-a",
        authorized_at=STAMP,
        expires_at=EXPIRY,
        expiry_policy_version="INBOUND_COLLECTION_AUTHORIZATION_EXPIRY_POLICY_V1",
    )


def record(
    authorization: InboundCollectionAuthorization,
    *,
    revoked_at: datetime | None = None,
    consumed_at: datetime | None = None,
    consumed_by: str | None = None,
) -> InboundCollectionAuthorizationRecord:
    return InboundCollectionAuthorizationRecord(
        authorization=authorization,
        revoked_at=revoked_at,
        revocation_reference="revocation-a" if revoked_at is not None else None,
        consumed_at=consumed_at,
        consumed_by_collection_authority_id=consumed_by,
    )


class FakeP5:
    """Deterministic P5 registry seam recording reads and single-use CAS calls."""

    current: InboundCollectionAuthorizationRecord | None = None
    consume_result: InboundCollectionAuthorizationRecord | None = None
    calls: list[tuple[str, Any]] = []
    consume_error: BaseException | None = None

    @classmethod
    def reset(cls, value: InboundCollectionAuthorizationRecord | None) -> None:
        cls.current = value
        cls.consume_result = None
        cls.calls = []
        cls.consume_error = None

    @classmethod
    def get(cls, tenant_id: str, authorization_id: str, collection: Any, *, session: Any = None) -> Any:
        cls.calls.append(("get", (tenant_id, authorization_id, collection, session)))
        if cls.current is None or cls.current.authorization.tenant_id != tenant_id or cls.current.authorization.inbound_collection_authorization_id != authorization_id:
            return None
        return cls.current

    @classmethod
    def consume(cls, tenant_id: str, authorization_id: str, fingerprint: str, consumed_at: datetime, consumed_by: str, collection: Any, *, session: Any = None) -> Any:
        cls.calls.append(("consume", (tenant_id, authorization_id, fingerprint, consumed_at, consumed_by, collection, session)))
        if cls.consume_error is not None:
            raise cls.consume_error
        if cls.consume_result is not None:
            return cls.consume_result
        if cls.current is None:
            raise InboundCollectionAuthorizationLifecycleConflictError("missing")
        return replace(cls.current, consumed_at=consumed_at, consumed_by_collection_authority_id=consumed_by)


class FakeP3:
    """Deterministic P3 registry seam recording replay and immutable create calls."""

    by_key: InboundCollectionAuthority | None = None
    by_source: InboundCollectionAuthority | None = None
    created: InboundCollectionAuthority | None = None
    calls: list[tuple[str, Any]] = []
    create_error: BaseException | None = None

    @classmethod
    def reset(cls) -> None:
        cls.by_key = None
        cls.by_source = None
        cls.created = None
        cls.calls = []
        cls.create_error = None

    @classmethod
    def get_by_idempotency_key(cls, tenant_id: str, key: str, collection: Any, *, session: Any = None) -> Any:
        cls.calls.append(("key", (tenant_id, key, collection, session)))
        return cls.by_key

    @classmethod
    def get_by_source_receivable(cls, tenant_id: str, family: ReceivableFamily, receivable_id: str, collection: Any, *, session: Any = None) -> Any:
        cls.calls.append(("source", (tenant_id, family, receivable_id, collection, session)))
        return cls.by_source

    @classmethod
    def create(cls, value: InboundCollectionAuthority, collection: Any, *, session: Any = None) -> InboundCollectionAuthority:
        cls.calls.append(("create", (value, collection, session)))
        if cls.create_error is not None:
            raise cls.create_error
        cls.created = value
        return value


def authority_for(authorization: InboundCollectionAuthorization, *, key: str = "p7-key-a", authority_id: str = "authority-a") -> InboundCollectionAuthority:
    subject = authorization.subject_authority
    if isinstance(subject, ClientInboundCollectionAuthorizationSubject):
        source: ClientCollectionSource | PlatformCollectionSource = ClientCollectionSource(
            subject.tenant_id, subject.client_invoice_id, subject.commercial_receivable_id,
            subject.commercial_receivable_fingerprint, subject.client_invoice_fingerprint, subject.customer_id,
        )
    else:
        source = PlatformCollectionSource(
            subject.tenant_id, subject.platform_invoice_id, subject.commercial_receivable_id,
            subject.commercial_receivable_fingerprint, subject.platform_invoice_fingerprint,
        )
    return InboundCollectionAuthority(
        authority_id, authorization.tenant_id, authorization.subject_authority_kind, source,
        subject.expected_outstanding_amount_minor, subject.currency, key, authorization.principal_id,
        authorization.inbound_collection_authorization_id, authorization.authorization_evidence_fingerprint,
        STAMP, authorization.authorized_at,
    )


@pytest.fixture(autouse=True)
def seams(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(issuance, "InboundCollectionAuthorityRegistry", FakeP3)
    monkeypatch.setattr(issuance, "InboundCollectionAuthorizationRegistry", FakeP5)
    monkeypatch.setattr(issuance, "_trusted_instant", lambda: STAMP)
    FakeP3.reset()
    FakeP5.reset(None)


def invoke() -> InboundCollectionAuthority:
    return _issue("tenant-a", "auth-a", "p7-key-a", ACTIVE)


def _issue(tenant: str, authorization_id: str, key: str, session: Any = ACTIVE) -> InboundCollectionAuthority:
    """Call the typed production API with synthetic doubles cast at the test boundary."""
    return issuance.issue_inbound_collection_authority(
        tenant, authorization_id, key, session=cast(Any, session),
        authorization_collection=cast(Any, FakeCollection()), authority_collection=cast(Any, FakeCollection()),
    )


def test_public_api_and_request_contract() -> None:
    signature = inspect.signature(issuance.issue_inbound_collection_authority)
    assert list(signature.parameters) == ["tenant_id", "inbound_collection_authorization_id", "collection_authority_idempotency_key", "session", "authorization_collection", "authority_collection"]
    assert issuance.VERSION == "v1.0.0-M11-R8-R3B-P7-INBOUND-COLLECTION-AUTHORITY-ISSUANCE"
    assert "BillingRegistry" not in Path(issuance.__file__).read_text(encoding="utf-8")


def test_fresh_path_is_p5_derived_create_then_consume() -> None:
    authorization = client_authorization()
    FakeP5.reset(record(authorization))
    result = invoke()
    assert result.collection_authority_id == FakeP3.created.collection_authority_id  # type: ignore[union-attr]
    assert result.authorization_reference == "auth-a"
    assert result.authorization_evidence_fingerprint == authorization.authorization_evidence_fingerprint
    assert result.expected_amount_minor == 12500
    assert result.currency == "ZAR"
    assert isinstance(result.source_authority, ClientCollectionSource)
    assert result.created_at == STAMP
    assert result.authorized_at == STAMP
    assert [name for name, _ in FakeP3.calls] == ["key", "source", "create"]
    assert [name for name, _ in FakeP5.calls] == ["get", "consume"]
    consume_args = FakeP5.calls[-1][1]
    assert consume_args[3] == STAMP
    assert consume_args[4] == result.collection_authority_id
    assert consume_args[-1] is ACTIVE


def test_exact_idempotency_hit_returns_without_p5_source_clock_or_writes() -> None:
    existing = authority_for(client_authorization())
    FakeP3.by_key = existing
    assert invoke() == existing
    assert [name for name, _ in FakeP3.calls] == ["key"]
    assert FakeP5.calls == []


def test_idempotency_hit_with_different_authorization_fails_closed() -> None:
    FakeP3.by_key = authority_for(client_authorization())
    with pytest.raises(issuance.InboundCollectionAuthorityIssuanceError):
        _issue("tenant-a", "other-auth", "p7-key-a")
    assert FakeP5.calls == []


def test_source_hit_same_key_after_key_miss_is_persistence_inconsistency() -> None:
    authorization = client_authorization()
    FakeP5.reset(record(authorization))
    FakeP3.by_source = authority_for(authorization, key="p7-key-a")
    with pytest.raises(issuance.InboundCollectionAuthorityIssuanceError, match="SOURCE_HIT_SAME_KEY"):
        invoke()
    assert [name for name, _ in FakeP5.calls] == ["get"]


def test_same_authorization_different_key_and_different_authorization_same_source_fail_without_consume() -> None:
    authorization = client_authorization()
    FakeP5.reset(record(authorization))
    FakeP3.by_source = authority_for(authorization, key="original-key")
    with pytest.raises(issuance.InboundCollectionAuthorityIssuanceError, match="SAME_AUTHORIZATION_DIFFERENT_P7_KEY"):
        _issue("tenant-a", "auth-a", "new-key")
    assert [name for name, _ in FakeP5.calls] == ["get"]

    other = client_authorization(authorization_id="auth-b")
    FakeP5.reset(record(other))
    FakeP3.by_source = authority_for(authorization, key="original-key")
    with pytest.raises(issuance.InboundCollectionAuthorityIssuanceError, match="SOURCE_REPLAY_AUTHORIZATION_MISMATCH"):
        _issue("tenant-a", "auth-b", "p7-key-b")
    assert [name for name, _ in FakeP5.calls] == ["get"]


@pytest.mark.parametrize(
    "value, code",
    [(None, "AUTHORIZATION_NOT_FOUND"), (record(client_authorization(), revoked_at=STAMP), "AUTHORIZATION_NOT_CURRENTLY_USABLE"), (record(client_authorization(), consumed_at=STAMP, consumed_by="authority-a"), "AUTHORIZATION_NOT_CURRENTLY_USABLE")],
)
def test_missing_revoked_and_consumed_fresh_paths_fail_closed(value: Any, code: str) -> None:
    FakeP5.reset(value)
    with pytest.raises(issuance.InboundCollectionAuthorityIssuanceError, match=code):
        invoke()
    assert [name for name, _ in FakeP3.calls] == ["key", "source"] if value is not None else [name for name, _ in FakeP3.calls] == ["key"]


def test_expired_authorization_rejects_and_no_uuid_or_writes() -> None:
    FakeP5.reset(record(client_authorization(authorized_at=STAMP - timedelta(hours=2), expires_at=STAMP - timedelta(seconds=1))))
    with pytest.raises(issuance.InboundCollectionAuthorityIssuanceError, match="NOT_CURRENTLY_USABLE"):
        invoke()
    assert [name for name, _ in FakeP3.calls] == ["key", "source"]


def test_platform_subject_mapping_is_exact_and_provider_neutral() -> None:
    authorization = platform_authorization()
    FakeP5.reset(record(authorization))
    result = _issue("tenant-a", "platform-auth-a", "p7-platform-key")
    assert isinstance(result.source_authority, PlatformCollectionSource)
    assert result.source_authority.platform_invoice_id == "platform-invoice-a"
    assert result.source_authority.commercial_receivable_id == "platform-receivable-a"
    assert "provider" not in result.to_dict()


def test_whitespace_and_inactive_transaction_reject() -> None:
    for args in [("", "auth-a", "key"), ("tenant-a", "", "key"), ("tenant-a", "auth-a", "")]:
        with pytest.raises(issuance.InboundCollectionAuthorityIssuanceError):
            _issue(*args)
    inactive = ActiveSession()
    inactive.in_transaction = False
    with pytest.raises(issuance.InboundCollectionAuthorityIssuanceError, match="ACTIVE_TRANSACTION_REQUIRED"):
        _issue("tenant-a", "auth-a", "key", inactive)


def test_create_duplicate_key_propagates_without_recovery() -> None:
    FakeP5.reset(record(client_authorization()))
    FakeP3.create_error = DuplicateKeyError("race")
    with pytest.raises(DuplicateKeyError):
        invoke()
    assert [name for name, _ in FakeP3.calls] == ["key", "source", "create"]
    assert [name for name, _ in FakeP5.calls] == ["get"]


def test_consume_cas_race_propagates_after_create() -> None:
    FakeP5.reset(record(client_authorization()))
    FakeP5.consume_error = InboundCollectionAuthorizationLifecycleConflictError("race")
    with pytest.raises(InboundCollectionAuthorizationLifecycleConflictError):
        invoke()
    assert [name for name, _ in FakeP3.calls] == ["key", "source", "create"]
    assert [name for name, _ in FakeP5.calls] == ["get", "consume"]


def test_consume_result_correlation_is_required() -> None:
    authorization = client_authorization()
    FakeP5.reset(record(authorization))
    FakeP5.consume_result = record(authorization, consumed_at=STAMP, consumed_by="wrong-authority")
    with pytest.raises(issuance.InboundCollectionAuthorityIssuanceError, match="CORRELATION"):
        invoke()


def test_source_fingerprint_and_authority_domain_are_strict() -> None:
    source = Path(issuance.__file__).read_text(encoding="utf-8")
    assert "get_by_source_receivable" in source
    assert "uuid.uuid4().hex" in source
    assert "InboundCollectionAuthorizationRegistry.consume" in source
    assert "P5" in source
    assert "payfast" not in source.lower()
    assert "payshap" not in source.lower()


def test_no_production_or_test_sibling_mutation_is_required_by_this_certificate() -> None:
    assert issuance.__file__.endswith("tools/eos/saas/billing/inbound_collection_authority_issuance.py")


# ARTIFACT: test_inbound_collection_authority_issuance.py
# VERSION: v1.0.0-M11-R8-R3B-P7-INBOUND-COLLECTION-AUTHORITY-ISSUANCE-CERT
# AUTHORITY BOUNDARY: Direct synthetic orchestration certificate only.
# TENANT POSTURE: Explicit tenant-scoped fixtures and registry calls.
# FAIL-CLOSED POSTURE: Replay, provenance, lifecycle, race, and mutation firewalls are asserted.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
