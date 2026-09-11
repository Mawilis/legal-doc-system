"""WILSY OS M11 R8-R3B-P7 inbound collection-authority issuance.
TITLE: Inbound Collection Authority Issuance and Atomic Authorization Consumption
VERSION: v1.0.0-M11-R8-R3B-P7-INBOUND-COLLECTION-AUTHORITY-ISSUANCE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Composes one provider-neutral collection authority from durable typed authorization evidence and consumes that authorization exactly once in a caller-owned transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/inbound_collection_authority_issuance.py
COLLABORATION / OWNERSHIP: SaaS collection-authority issuance owner; P3/P5 registries own persistence and lifecycle CAS while the caller owns transaction commit, abort, and retry.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.0.0-M11-R8-R3B-P7-INBOUND-COLLECTION-AUTHORITY-ISSUANCE establishes idempotency-first replay, P5-derived source replay, strict provenance, one-instant timing, and create-before-consume atomic composition.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped opaque identifiers only; no provider, credential, checkout, payment, settlement, or import-time network authority.
TENANT BOUNDARY: Every P3/P5 lookup and lifecycle transition uses the caller tenant and the same caller session.
AUTHORITY BOUNDARY: Collection-authority composition only; this module never issues authorization, selects providers, executes payment, or closes receivables.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns outbound financial execution and settlement evidence.
TRANSACTION BOUNDARY: The caller supplies an active session and owns transaction start, commit, abort, and whole-transaction retry.
FAIL-CLOSED DECLARATION: Missing, divergent, stale, corrupt, cross-tenant, cross-family, replay-inconsistent, and CAS-racing evidence rejects without inference.
"""
from __future__ import annotations

from datetime import datetime, timezone
import uuid
from typing import Any, NoReturn

from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from tools.eos.saas.domain.commercial_receivable import ReceivableFamily
from tools.eos.saas.domain.inbound_collection_authorization import (
    ClientInboundCollectionAuthorizationSubject,
    InboundCollectionAuthorization,
    PlatformInboundCollectionAuthorizationSubject,
)
from tools.eos.saas.domain.inbound_collection_authority import (
    ClientCollectionSource,
    InboundCollectionAuthority,
    PlatformCollectionSource,
)
from tools.eos.saas.billing.inbound_collection_authorization_registry import (
    InboundCollectionAuthorizationRecord,
    InboundCollectionAuthorizationRegistry,
)
from tools.eos.saas.billing.inbound_collection_authority_registry import (
    InboundCollectionAuthorityRegistry,
)


VERSION = "v1.0.0-M11-R8-R3B-P7-INBOUND-COLLECTION-AUTHORITY-ISSUANCE"


class InboundCollectionAuthorityIssuanceError(RuntimeError):
    """Structured fail-closed error for authority composition boundaries."""

    def __init__(self, code: str, message: str | None = None) -> None:
        self.code = code
        super().__init__(message or code)


def _fail(code: str, detail: object | None = None) -> NoReturn:
    """Raise a stable error without fabricating authority or lifecycle truth."""
    suffix = f": {detail}" if detail is not None else ""
    raise InboundCollectionAuthorityIssuanceError(code, f"{code}{suffix}")


def _text(name: str, value: object) -> str:
    """Require the exact non-empty request identity used by tenant predicates."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"INVALID_{name.upper()}")
    return value


def _active_session(session: ClientSession) -> ClientSession:
    """Require a caller-owned active transaction and never create one."""
    if session is None or getattr(session, "in_transaction", False) is not True:
        _fail("ACTIVE_TRANSACTION_REQUIRED")
    return session


def _trusted_instant() -> datetime:
    """Capture the single service-owned aware UTC instant for a fresh transition."""
    return datetime.now(timezone.utc)


def _source_from_authorization(
    authorization: InboundCollectionAuthorization,
) -> tuple[ReceivableFamily, ClientCollectionSource | PlatformCollectionSource]:
    """Map only the strict typed P5 subject into its closed P3 source variant."""
    subject = authorization.subject_authority
    family = authorization.subject_authority_kind
    if family is ReceivableFamily.CLIENT and type(subject) is ClientInboundCollectionAuthorizationSubject:
        return family, ClientCollectionSource(
            tenant_id=subject.tenant_id,
            client_invoice_id=subject.client_invoice_id,
            commercial_receivable_id=subject.commercial_receivable_id,
            commercial_receivable_fingerprint=subject.commercial_receivable_fingerprint,
            client_invoice_fingerprint=subject.client_invoice_fingerprint,
            customer_id=subject.customer_id,
        )
    if family is ReceivableFamily.PLATFORM and type(subject) is PlatformInboundCollectionAuthorizationSubject:
        return family, PlatformCollectionSource(
            tenant_id=subject.tenant_id,
            platform_invoice_id=subject.platform_invoice_id,
            commercial_receivable_id=subject.commercial_receivable_id,
            commercial_receivable_fingerprint=subject.commercial_receivable_fingerprint,
            platform_invoice_fingerprint=subject.platform_invoice_fingerprint,
        )
    _fail("AUTHORIZATION_SOURCE_FAMILY_INVALID")


def _verify_authority_replay(
    existing: InboundCollectionAuthority,
    tenant_id: str,
    authorization_id: str,
    idempotency_key: str,
) -> InboundCollectionAuthority:
    """Return only an exact tenant/key/provenance replay; reject substitution."""
    if (
        existing.tenant_id != tenant_id
        or existing.idempotency_key != idempotency_key
        or existing.authorization_reference != authorization_id
    ):
        _fail("AUTHORITY_REPLAY_IDENTITY_CONFLICT")
    return existing


def _verify_source_replay(
    existing: InboundCollectionAuthority,
    tenant_id: str,
    authorization: InboundCollectionAuthorization,
    family: ReceivableFamily,
    source: ClientCollectionSource | PlatformCollectionSource,
    idempotency_key: str,
) -> None:
    """Require source and authorization provenance before classifying a replay."""
    if existing.tenant_id != tenant_id:
        _fail("SOURCE_REPLAY_TENANT_MISMATCH")
    if existing.source_authority_kind is not family:
        _fail("SOURCE_REPLAY_FAMILY_MISMATCH")
    if existing.source_authority.commercial_receivable_id != source.commercial_receivable_id:
        _fail("SOURCE_REPLAY_RECEIVABLE_MISMATCH")
    if existing.authorization_reference != authorization.inbound_collection_authorization_id:
        _fail("SOURCE_REPLAY_AUTHORIZATION_MISMATCH")
    if existing.authorization_evidence_fingerprint != authorization.authorization_evidence_fingerprint:
        _fail("SOURCE_REPLAY_AUTHORIZATION_FINGERPRINT_MISMATCH")
    if existing.idempotency_key == idempotency_key:
        _fail("SOURCE_HIT_SAME_KEY_AFTER_IDEMPOTENCY_MISS")
    _fail("SAME_AUTHORIZATION_DIFFERENT_P7_KEY")


def _construct_authority(
    authorization: InboundCollectionAuthorization,
    family: ReceivableFamily,
    source: ClientCollectionSource | PlatformCollectionSource,
    idempotency_key: str,
    authority_id: str,
    created_at: datetime,
) -> InboundCollectionAuthority:
    """Construct the immutable P3 authority exclusively from P5 facts."""
    subject = authorization.subject_authority
    return InboundCollectionAuthority(
        collection_authority_id=authority_id,
        tenant_id=authorization.tenant_id,
        source_authority_kind=family,
        source_authority=source,
        expected_amount_minor=subject.expected_outstanding_amount_minor,
        currency=subject.currency,
        idempotency_key=idempotency_key,
        issued_by_actor_id=authorization.principal_id,
        authorization_reference=authorization.inbound_collection_authorization_id,
        authorization_evidence_fingerprint=authorization.authorization_evidence_fingerprint,
        created_at=created_at,
        authorized_at=authorization.authorized_at,
    )


def _verify_consumption(
    consumed: InboundCollectionAuthorizationRecord,
    authorization: InboundCollectionAuthorization,
    consumed_at: datetime,
    authority_id: str,
) -> None:
    """Correlate the returned P5 lifecycle snapshot with the created authority."""
    if (
        consumed.authorization.inbound_collection_authorization_id != authorization.inbound_collection_authorization_id
        or consumed.authorization.authorization_evidence_fingerprint != authorization.authorization_evidence_fingerprint
        or consumed.consumed_at != consumed_at
        or consumed.consumed_by_collection_authority_id != authority_id
    ):
        _fail("CONSUMPTION_RESULT_CORRELATION_FAILED")


def issue_inbound_collection_authority(
    tenant_id: str,
    inbound_collection_authorization_id: str,
    collection_authority_idempotency_key: str,
    *,
    session: ClientSession,
    authorization_collection: Collection,
    authority_collection: Collection,
) -> InboundCollectionAuthority:
    """Compose one collection authority and consume its typed authorization atomically.

    The authority-idempotency lookup is first. After a miss, the durable P5 record
    supplies source, amount, currency, actor, and authorization provenance. Source
    replay is checked before usability, time, UUID generation, create, or consume.
    The caller must abort on any error and retry the whole transaction; this issuer
    never starts, commits, aborts, or nests a transaction.
    """
    tenant = _text("tenant_id", tenant_id)
    authorization_id = _text("inbound_collection_authorization_id", inbound_collection_authorization_id)
    idem = _text("collection_authority_idempotency_key", collection_authority_idempotency_key)
    tx = _active_session(session)

    existing = InboundCollectionAuthorityRegistry.get_by_idempotency_key(
        tenant, idem, authority_collection, session=tx
    )
    if existing is not None:
        return _verify_authority_replay(existing, tenant, authorization_id, idem)

    record = InboundCollectionAuthorizationRegistry.get(
        tenant, authorization_id, authorization_collection, session=tx
    )
    if record is None:
        _fail("AUTHORIZATION_NOT_FOUND")
    authorization = record.authorization
    if authorization.tenant_id != tenant or authorization.inbound_collection_authorization_id != authorization_id:
        _fail("AUTHORIZATION_IDENTITY_CONFLICT")
    family, source = _source_from_authorization(authorization)

    source_existing = InboundCollectionAuthorityRegistry.get_by_source_receivable(
        tenant, family, source.commercial_receivable_id, authority_collection, session=tx
    )
    if source_existing is not None:
        _verify_source_replay(source_existing, tenant, authorization, family, source, idem)

    trusted_at = _trusted_instant()
    if not record.is_currently_usable(trusted_at):
        _fail("AUTHORIZATION_NOT_CURRENTLY_USABLE")
    authority_id = uuid.uuid4().hex
    authority = _construct_authority(authorization, family, source, idem, authority_id, trusted_at)
    created = InboundCollectionAuthorityRegistry.create(authority, authority_collection, session=tx)
    consumed = InboundCollectionAuthorizationRegistry.consume(
        tenant,
        authorization_id,
        authorization.authorization_evidence_fingerprint,
        trusted_at,
        created.collection_authority_id,
        authorization_collection,
        session=tx,
    )
    _verify_consumption(consumed, authorization, trusted_at, created.collection_authority_id)
    return created


__all__ = [
    "InboundCollectionAuthorityIssuanceError",
    "VERSION",
    "issue_inbound_collection_authority",
]


# ARTIFACT: inbound_collection_authority_issuance.py
# VERSION: v1.0.0-M11-R8-R3B-P7-INBOUND-COLLECTION-AUTHORITY-ISSUANCE
# AUTHORITY BOUNDARY: Provider-neutral collection-authority composition only.
# TENANT POSTURE: Every lookup and lifecycle transition is tenant-scoped.
# FAIL-CLOSED POSTURE: Exact replay, provenance, usability, CAS, and correlation checks.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
