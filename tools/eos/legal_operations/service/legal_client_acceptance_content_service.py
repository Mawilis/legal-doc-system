"""WILSY OS authenticated client-acceptance content delivery seam.

TITLE: WILSY OS Legal Client Acceptance Content Delivery Service
VERSION: v1.0.0-L9A4-P2D-CLIENT-ACCEPTANCE-CONTENT-DELIVERY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Revalidate an already-issued LegalClientAcceptanceContext against
         current authenticated IAM, visibility, matter, party/capacity,
         instrument, lifecycle and approval authorities before resolving its
         server-owned content locator and returning bounded review content.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_client_acceptance_content_service.py
COLLABORATION / OWNERSHIP: P2C1 owns immutable context semantics; P2C2 owns
                            context durability; P2C3 owns issuance; the
                            injected ContentReader owns the already-sanctioned
                            storage capability. This service owns neither a
                            second content store nor ClientAcceptance.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P2D establishes authenticated, tenant-derived,
           dependency-revalidated content delivery with exact SHA3-512
           verification, bounded text media, caller-owned transaction/session
           propagation and server-only locator handling. HTTP, browser,
           ClientAcceptance, Engagement, Representation, Court and finance
           remain outside this artifact.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only tenant/principal values from active
                             SovereignIdentity are authoritative. The opaque
                             context ID is the only caller resource selector.
                             Raw locators, hashes used for lookup and source
                             failures never appear in errors or the result.
TENANT BOUNDARY: Every read and capability call is scoped to the exact
                 identity tenant and principal; no caller tenant, party,
                 capacity, approval or content reference is accepted.
AUTHORITY BOUNDARY: Review-content projection only after current canonical
                    revalidation. It is not acceptance, signature, mandate,
                    engagement, representation, Court authority or approval.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for
                              financial execution and settlement.
TRANSACTION BOUNDARY: A caller-owned active Mongo transaction is required for
                      the complete revalidation/read sequence. This service
                      never starts, commits, aborts, retries or reconciles it.
FAIL-CLOSED DECLARATION: Missing/expired context, inactive IAM or visibility,
                         stale/ambiguous source, terminal lifecycle,
                         rejected approval, missing/unsupported/altered content
                         and storage failure reject without projection.
"""
from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Final, Mapping, NoReturn, Protocol, cast

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.legal_operations.domain.legal_client_acceptance_context import (
    LegalClientAcceptanceContext,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_lifecycle import (
    LegalClientMatterAcceptanceInstrumentLifecycleStatus,
)
from tools.eos.legal_operations.domain.legal_operations_current_projection import (
    resolve_current_lifecycle_snapshot,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.registry import (
    legal_client_acceptance_context_registry as context_registry,
    legal_client_acting_capacity_registry as capacity_registry,
    legal_client_matter_acceptance_instrument_approval_registry as approval_registry,
    legal_client_matter_acceptance_instrument_lifecycle_registry as lifecycle_registry,
    legal_client_matter_acceptance_instrument_registry as instrument_registry,
    legal_client_matter_visibility_registry as visibility_registry,
    legal_matter_party_registry as party_registry,
    legal_operations_lifecycle_registry as matter_registry,
)
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationReason,
    authorize_tenant_operation,
)


VERSION: Final[str] = "v1.0.0-L9A4-P2D-CLIENT-ACCEPTANCE-CONTENT-DELIVERY"
PERMISSION: Final[str] = "legal_operations:client_matter:read"
OPERATION: Final[str] = "legal_client_matter_read"
UTC = timezone.utc
SUPPORTED_MEDIA_TYPES: Final[frozenset[str]] = frozenset(
    {"text/plain", "text/markdown"}
)
MAX_CONTENT_BYTES: Final[int] = 2_000_000


class LegalClientAcceptanceContentDeliveryError(RuntimeError):
    """Stable, non-sensitive fail-closed delivery error."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded semantic code, never supplied values."""
        self.code = code
        super().__init__(code)


class ContentReader(Protocol):
    """Server-owned capability for resolving one opaque content reference."""

    def read(
        self, content_reference: str, *, tenant_id: str, session: Any
    ) -> "StoredContent":
        """Return content for an internally supplied locator or fail closed."""
        ...


@dataclass(frozen=True, slots=True)
class StoredContent:
    """Internal reader result; it is never persisted by this service."""

    content: bytes
    media_type: str


@dataclass(frozen=True, slots=True)
class LegalClientAcceptanceContent:
    """Bounded client-safe review content with provenance integrity metadata.

    The value intentionally excludes the server locator, tenant, principal,
    party identifiers and approval evidence. It is a projection for review,
    not a legal acceptance or organisation-binding instrument.
    """

    acceptance_context_id: str
    instrument_id: str
    instrument_version: str
    title: str
    review_scope: str
    media_type: str
    content: str
    content_fingerprint: str
    content_bytes: int


Clock = Callable[[], datetime]


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one bounded error while retaining technical cause privately."""
    error = LegalClientAcceptanceContentDeliveryError(code)
    if cause is None:
        raise error
    raise error from cause


def _active_transaction(session: Any) -> Any:
    """Require one caller-owned active transaction before any source read."""
    if session is None:
        _fail("L9A4_P2D_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _fail("L9A4_P2D_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _identity(identity: SovereignIdentity) -> tuple[str, str]:
    """Derive exact tenant/principal only from an active identity."""
    if not isinstance(identity, SovereignIdentity):
        _fail("L9A4_P2D_IDENTITY_REQUIRED")
    if identity.status is not PrincipalStatus.ACTIVE:
        _fail("L9A4_P2D_PRINCIPAL_INACTIVE")
    if not identity.tenant_id or not identity.identity_id:
        _fail("L9A4_P2D_IDENTITY_INVALID")
    return identity.tenant_id, identity.identity_id


def _now(clock: Clock | None) -> datetime:
    """Read one aware UTC server instant."""
    value = datetime.now(UTC) if clock is None else clock()
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail("L9A4_P2D_SERVER_CLOCK_INVALID")
    return value.astimezone(UTC)


def _text(name: str, value: object) -> str:
    """Require one opaque non-empty identifier without coercion."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"L9A4_P2D_{name.upper()}_INVALID")
    return value


def _authorize(
    *, tenant: str, principal: str, principal_repository: Any,
    membership_repository: Any, business_role_repository: Any,
    role_assignment_repository: Any, session: Any,
) -> None:
    """Require active LEGAL_CLIENT IAM for the exact tenant/principal."""
    try:
        decision = authorize_tenant_operation(
            principal_id=principal,
            tenant_id=tenant,
            permission_id=PERMISSION,
            operation=OPERATION,
            principal_repository=principal_repository,
            membership_repository=membership_repository,
            business_role_repository=business_role_repository,
            role_assignment_repository=role_assignment_repository,
            session=session,
        )
    except Exception as error:
        _fail("L9A4_P2D_IAM_UNAVAILABLE", error)
    if (
        decision.authorized is not True
        or decision.reason is not TenantAuthorizationReason.AUTHORIZED
        or decision.business_role != "tenant_legal_client"
        or decision.authorization_role != "LEGAL_CLIENT"
    ):
        _fail("L9A4_P2D_LEGAL_CLIENT_AUTHORIZATION_REQUIRED")


def _matter(*, tenant: str, matter_id: str, collection: Any, session: Any) -> CaseMatter:
    """Resolve the exact current OPEN CaseMatter."""
    try:
        history = matter_registry.LegalOperationsLifecycleRegistry.get_entity_history(
            tenant, "CaseMatter", matter_id, collection, session=session
        )
        value = resolve_current_lifecycle_snapshot(history, expected_type=CaseMatter)
    except Exception as error:
        _fail("L9A4_P2D_MATTER_UNAVAILABLE", error)
    if type(value) is not CaseMatter or value.state is not CaseMatterState.OPEN:
        _fail("L9A4_P2D_MATTER_NOT_OPEN")
    if value.tenant_id != tenant or value.case_matter_id != matter_id:
        _fail("L9A4_P2D_MATTER_SCOPE_MISMATCH")
    return value


def _revalidate_dependencies(
    *, context: LegalClientAcceptanceContext, tenant: str, principal: str,
    matter_collection: Any, visibility_collection: Any, party_collection: Any,
    capacity_collection: Any, instrument_collection: Any,
    lifecycle_collection: Any, approval_collection: Any, session: Any,
    at: datetime, principal_repository: Any, membership_repository: Any,
    business_role_repository: Any, role_assignment_repository: Any,
) -> None:
    """Re-read every P2C3 dependency and compare immutable context bindings."""
    _authorize(
        tenant=tenant, principal=principal,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        business_role_repository=business_role_repository,
        role_assignment_repository=role_assignment_repository,
        session=session,
    )
    try:
        visibility = visibility_registry.LegalClientMatterVisibilityRegistry.resolve_current_active(
            tenant, principal, context.case_matter_id, visibility_collection, session=session
        )
    except Exception as error:
        _fail("L9A4_P2D_ACTIVE_VISIBILITY_REQUIRED", error)
    if (
        visibility.tenant_id != tenant
        or visibility.client_principal_id != principal
        or visibility.case_matter_id != context.case_matter_id
    ):
        _fail("L9A4_P2D_VISIBILITY_SCOPE_MISMATCH")
    matter = _matter(
        tenant=tenant, matter_id=context.case_matter_id,
        collection=matter_collection, session=session,
    )
    if not hmac.compare_digest(matter.fingerprint, context.matter_fingerprint):
        _fail("L9A4_P2D_MATTER_FINGERPRINT_STALE")
    try:
        parties = party_registry.list_matter_parties(
            tenant, matter.case_matter_id, party_collection, session=session
        )
        capacities = capacity_registry.list_valid_capacities_at(
            tenant, matter.case_matter_id, at, capacity_collection, session=session
        )
    except Exception as error:
        _fail("L9A4_P2D_PARTY_CAPACITY_UNAVAILABLE", error)
    party_map = {party.party_id: party for party in parties}
    pairs = [
        (party_map[capacity.party_id], capacity)
        for capacity in capacities
        if capacity.principal_id == principal
        and capacity.party_id in party_map
        and party_map[capacity.party_id].tenant_id == tenant
        and party_map[capacity.party_id].case_matter_id == matter.case_matter_id
        and party_map[capacity.party_id].matter_fingerprint == matter.fingerprint
        and party_map[capacity.party_id].subject_reference == capacity.subject_reference
        and party_map[capacity.party_id].subject_identity_fingerprint == capacity.subject_identity_fingerprint
    ]
    if len(pairs) != 1:
        _fail("L9A4_P2D_PARTY_CAPACITY_AMBIGUOUS" if len(pairs) > 1 else "L9A4_P2D_PARTY_CAPACITY_NOT_FOUND")
    party, capacity = pairs[0]
    if (
        party.party_id != context.party_id
        or party.fingerprint != getattr(context, "party_fingerprint", party.fingerprint)
        or party.subject_reference != context.subject_reference
        or party.subject_identity_fingerprint != context.subject_identity_fingerprint
        or capacity.capacity_id != context.capacity_id
        or capacity.fingerprint != context.capacity_fingerprint
    ):
        _fail("L9A4_P2D_PARTY_CAPACITY_STALE")
    try:
        instrument = instrument_registry.get_latest_effective_version(
            tenant, matter.case_matter_id, context.instrument_id, at,
            instrument_collection, session=session,
        )
    except Exception as error:
        _fail("L9A4_P2D_INSTRUMENT_UNAVAILABLE", error)
    if instrument is None:
        _fail("L9A4_P2D_INSTRUMENT_NOT_FOUND")
    if (
        instrument.tenant_id != tenant
        or instrument.case_matter_id != matter.case_matter_id
        or instrument.matter_fingerprint != matter.fingerprint
        or instrument.version != context.instrument_version
        or not hmac.compare_digest(instrument.fingerprint, context.instrument_fingerprint)
        or not hmac.compare_digest(instrument.content_fingerprint, context.content_fingerprint)
        or instrument.content_reference != context.content_reference
    ):
        _fail("L9A4_P2D_INSTRUMENT_STALE")
    try:
        lifecycle = lifecycle_registry.get_current_lifecycle(
            tenant, matter.case_matter_id, instrument.instrument_id,
            instrument.version, lifecycle_collection, session=session,
        )
    except Exception as error:
        _fail("L9A4_P2D_LIFECYCLE_UNAVAILABLE", error)
    if lifecycle is None or lifecycle.status is not LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE:
        _fail("L9A4_P2D_INSTRUMENT_NOT_ACTIVE")
    if (
        lifecycle.tenant_id != tenant
        or lifecycle.case_matter_id != matter.case_matter_id
        or lifecycle.instrument_id != instrument.instrument_id
        or lifecycle.version != instrument.version
        or lifecycle.instrument_fingerprint != instrument.fingerprint
        or lifecycle.matter_fingerprint != matter.fingerprint
        or lifecycle.status is not context.lifecycle_status
        or not hmac.compare_digest(lifecycle.fingerprint, context.lifecycle_fingerprint)
    ):
        _fail("L9A4_P2D_LIFECYCLE_STALE")
    try:
        approval = approval_registry.get_current_approval(
            tenant, matter.case_matter_id, instrument.instrument_id,
            instrument.version, instrument.fingerprint, instrument.content_fingerprint,
            approval_collection, at=at, session=session,
        )
    except Exception as error:
        _fail("L9A4_P2D_APPROVAL_UNAVAILABLE", error)
    decision = getattr(approval, "decision", None) if approval is not None else None
    if approval is None or getattr(decision, "value", decision) != "APPROVED":
        _fail("L9A4_P2D_APPROVAL_REQUIRED")
    if (
        approval.tenant_id != tenant
        or approval.case_matter_id != matter.case_matter_id
        or approval.instrument_id != instrument.instrument_id
        or approval.version != instrument.version
        or approval.instrument_fingerprint != instrument.fingerprint
        or approval.content_fingerprint != instrument.content_fingerprint
        or approval.approval_id != context.approval_id
        or approval.effective_from > at
        or not hmac.compare_digest(approval.fingerprint, context.approval_fingerprint)
    ):
        _fail("L9A4_P2D_APPROVAL_STALE")


def _read_content(
    *, reader: ContentReader, reference: str, tenant: str, expected: str, session: Any
) -> tuple[str, str, int]:
    """Resolve, size-check, decode and fingerprint content without exposing ref."""
    try:
        resource = reader.read(reference, tenant_id=tenant, session=session)
    except Exception as error:
        _fail("L9A4_P2D_CONTENT_UNAVAILABLE", error)
    if not isinstance(resource, StoredContent):
        _fail("L9A4_P2D_CONTENT_RESULT_INVALID")
    if resource.media_type not in SUPPORTED_MEDIA_TYPES:
        _fail("L9A4_P2D_CONTENT_MEDIA_TYPE_UNSUPPORTED")
    if not isinstance(resource.content, bytes) or not resource.content or len(resource.content) > MAX_CONTENT_BYTES:
        _fail("L9A4_P2D_CONTENT_BYTES_INVALID")
    digest = hashlib.sha3_512(resource.content).hexdigest()
    if not hmac.compare_digest(digest, expected):
        _fail("L9A4_P2D_CONTENT_FINGERPRINT_MISMATCH")
    try:
        text = resource.content.decode("utf-8")
    except UnicodeDecodeError as error:
        _fail("L9A4_P2D_CONTENT_ENCODING_INVALID", error)
    if not text.strip() or any(ord(character) in {0, 0xFFFE, 0xFFFF} for character in text):
        _fail("L9A4_P2D_CONTENT_TEXT_INVALID")
    return text, resource.media_type, len(resource.content)


def deliver_legal_client_acceptance_context_content(
    *,
    identity: SovereignIdentity,
    acceptance_context_id: str,
    context_collection: Any,
    matter_lifecycle_collection: Any,
    visibility_collection: Any,
    party_collection: Any,
    capacity_collection: Any,
    instrument_collection: Any,
    instrument_lifecycle_collection: Any,
    approval_collection: Any,
    content_reader: ContentReader,
    principal_repository: Any,
    membership_repository: Any,
    business_role_repository: Any,
    role_assignment_repository: Any,
    session: Any,
    clock: Clock | None = None,
) -> LegalClientAcceptanceContent:
    """Deliver one current, integrity-verified client-review content body.

    Only the authenticated identity and opaque context ID are caller inputs.
    Tenant/principal, content locator, fingerprints, party/capacity, source
    version, lifecycle and approval are read from canonical server authorities.
    The supplied session must already be inside the caller's transaction; the
    caller owns commit, abort, retry and unknown-commit handling. No database
    write, acceptance, organisation binding, Court or financial action occurs.
    """
    tx = _active_transaction(session)
    tenant, principal = _identity(identity)
    context_id = _text("acceptance_context_id", acceptance_context_id)
    at = _now(clock)
    try:
        context = context_registry.get_valid_context(
            tenant, context_id, at, context_collection, session=tx
        )
    except Exception as error:
        _fail("L9A4_P2D_CONTEXT_UNAVAILABLE", error)
    if context is None:
        _fail("L9A4_P2D_CONTEXT_EXPIRED_OR_NOT_FOUND")
    if context.actor_principal_id != principal or context.tenant_id != tenant:
        _fail("L9A4_P2D_CONTEXT_ACTOR_MISMATCH")
    _revalidate_dependencies(
        context=context, tenant=tenant, principal=principal,
        matter_collection=matter_lifecycle_collection,
        visibility_collection=visibility_collection, party_collection=party_collection,
        capacity_collection=capacity_collection, instrument_collection=instrument_collection,
        lifecycle_collection=instrument_lifecycle_collection,
        approval_collection=approval_collection, session=tx, at=at,
        principal_repository=principal_repository, membership_repository=membership_repository,
        business_role_repository=business_role_repository,
        role_assignment_repository=role_assignment_repository,
    )
    text, media_type, byte_count = _read_content(
        reader=content_reader, reference=context.content_reference, tenant=tenant,
        expected=context.content_fingerprint, session=tx,
    )
    return LegalClientAcceptanceContent(
        acceptance_context_id=context.acceptance_context_id,
        instrument_id=context.instrument_id,
        instrument_version=context.instrument_version,
        title=context.title,
        review_scope=context.review_scope,
        media_type=media_type,
        content=text,
        content_fingerprint=context.content_fingerprint,
        content_bytes=byte_count,
    )


__all__ = [
    "ContentReader",
    "LegalClientAcceptanceContent",
    "LegalClientAcceptanceContentDeliveryError",
    "MAX_CONTENT_BYTES",
    "OPERATION",
    "PERMISSION",
    "SUPPORTED_MEDIA_TYPES",
    "StoredContent",
    "VERSION",
    "deliver_legal_client_acceptance_context_content",
]


# ARTIFACT: legal_client_acceptance_content_service.py
# VERSION: v1.0.0-L9A4-P2D-CLIENT-ACCEPTANCE-CONTENT-DELIVERY
# AUTHORITY BOUNDARY: authenticated, revalidated review-content projection only
# TENANT POSTURE: exact identity tenant/principal and server-owned context scope
# FAIL-CLOSED POSTURE: stale, denied, expired, unsupported, missing or altered content rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
