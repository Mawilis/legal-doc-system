"""Compose one mandate-currentness projection from authoritative history.

TITLE: WILSY OS Legal Client Matter Mandate Currentness Composer
VERSION: v1.0.0-L9B12-P2-CLIENT-MATTER-MANDATE-CURRENTNESS-COMPOSER
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Read one exact immutable mandate, its originating grant currentness,
         and its exact firm acknowledgment currentness under one caller-owned
         transaction snapshot, then construct the already-certified pure
         mandate-currentness projection. This artifact selects no authority,
         persists no projection and owns no transaction lifecycle.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_matter_mandate_currentness_composer.py
COLLABORATION / OWNERSHIP: Mandate registry owns immutable formation reads;
                            grant and acknowledgment currentness composers own
                            their authoritative read sets; the pure mandate
                            currentness domain owns state precedence and
                            integrity. This module owns only composition.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B12-P2-CLIENT-MATTER-MANDATE-CURRENTNESS-COMPOSER adds
           exact tenant/mandate reads, same-session/same-time propagation,
           published upstream composer delegation, fail-closed missing or
           corrupt evidence handling and zero currentness persistence. It adds
           no lifecycle, Engagement, Representation, Court, API or finance.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Caller supplies only tenant, mandate and explicit
                             aware evaluation time. Grant, acknowledgment,
                             matter, client and subject evidence is read from
                             canonical registries. Errors expose stable codes.
TENANT BOUNDARY: Every read is exact-tenant scoped. No global mandate lookup,
                 fallback identity or cross-tenant oracle exists.
AUTHORITY BOUNDARY: Read-only mandate-currentness composition. No CaseMatter
                    authority read outside the grant composer, no acting-
                    capacity reread, conflict, ClientAcceptance, IAM,
                    Engagement, Representation, Court or delivery authority.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement, release or execution;
                              Kennel EOS remains the exclusive financial
                              execution authority.
TRANSACTION BOUNDARY: Caller supplies and owns an active transaction. This
                      module never starts, commits, aborts, retries or creates
                      a session.
FAIL-CLOSED DECLARATION: Missing transaction, unavailable/corrupt upstream
                         evidence, lineage divergence and malformed input never
                         become CURRENT and are reported with bounded errors.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final, NoReturn

from tools.eos.legal_operations.domain.legal_client_matter_mandate import (
    LegalClientMatterMandate,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment_currentness import (
    LegalClientMatterMandateAcknowledgmentCurrentness,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_currentness import (
    LegalClientMatterMandateCurrentness,
    project_legal_client_matter_mandate_currentness,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_currentness import (
    LegalClientMatterMandateGrantCurrentness,
)
from tools.eos.legal_operations.orchestration import (
    legal_client_matter_mandate_acknowledgment_currentness_composer as acknowledgment_composer,
    legal_client_matter_mandate_grant_currentness_composer as grant_composer,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_mandate_registry as mandate_registry,
)


VERSION: Final[str] = "v1.0.0-L9B12-P2-CLIENT-MATTER-MANDATE-CURRENTNESS-COMPOSER"
UTC: Final[timezone] = timezone.utc


class LegalClientMatterMandateCurrentnessComposerError(RuntimeError):
    """Stable non-sensitive failure from read-only composition."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded code, never identifiers or source evidence."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one bounded fail-closed composition error."""
    error = LegalClientMatterMandateCurrentnessComposerError(code)
    if cause is None:
        raise error
    raise error from cause


def _text(name: str, value: object) -> str:
    """Require one bounded caller identity without trimming or coercion."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"L9B12_P2_{name.upper()}_INVALID")
    return value


def _active_transaction(session: Any) -> Any:
    """Require an already-active caller-owned transaction before any read."""
    if session is None:
        _fail("L9B12_P2_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _fail("L9B12_P2_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _evaluation_time(value: object) -> datetime:
    """Require one explicit aware evaluation instant and normalize to UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail("L9B12_P2_EVALUATION_TIME_INVALID")
    return value.astimezone(UTC).replace(microsecond=value.microsecond)


def _formation_absent(
    *, tenant_id: str, mandate_id: str, evaluation_time: datetime
) -> LegalClientMatterMandateCurrentness:
    """Construct truthful absent-formation evidence through the pure domain."""
    return project_legal_client_matter_mandate_currentness(
        tenant_id=tenant_id,
        mandate_id=mandate_id,
        mandate=None,
        grant_currentness=None,
        acknowledgment_currentness=None,
        evaluation_time=evaluation_time,
    )


def _require_upstream_types(
    grant_currentness: object,
    acknowledgment_currentness: object,
) -> tuple[
    LegalClientMatterMandateGrantCurrentness,
    LegalClientMatterMandateAcknowledgmentCurrentness,
]:
    """Reject forged or unavailable upstream objects before projection."""
    if type(grant_currentness) is not LegalClientMatterMandateGrantCurrentness:
        _fail("L9B12_P2_GRANT_CURRENTNESS_INVALID")
    if type(acknowledgment_currentness) is not LegalClientMatterMandateAcknowledgmentCurrentness:
        _fail("L9B12_P2_ACKNOWLEDGMENT_CURRENTNESS_INVALID")
    return grant_currentness, acknowledgment_currentness


class LegalClientMatterMandateCurrentnessComposer:
    """Compose one exact mandate-currentness value in a caller transaction.

    The public boundary accepts only exact ``tenant_id``, ``mandate_id``, an
    explicit aware evaluation time and an already-active caller session. The
    mandate-bound grant and acknowledgment identities are never caller claims;
    they are read from the immutable mandate and delegated to the published
    upstream composers. No method starts, commits, aborts, retries or persists
    a transaction, and no currentness value is written.
    """

    def __init__(
        self,
        *,
        mandate_collection: Any,
        grant_collection: Any,
        grant_lifecycle_collection: Any,
        matter_lifecycle_collection: Any,
        acknowledgment_collection: Any,
    ) -> None:
        """Bind explicit canonical collection handles without resolving a DB."""
        if any(
            value is None
            for value in (
                mandate_collection,
                grant_collection,
                grant_lifecycle_collection,
                matter_lifecycle_collection,
                acknowledgment_collection,
            )
        ):
            _fail("L9B12_P2_COLLECTION_REQUIRED")
        self._mandate_collection = mandate_collection
        self._grant_composer = grant_composer.LegalClientMatterMandateGrantCurrentnessComposer(
            grant_collection=grant_collection,
            lifecycle_collection=grant_lifecycle_collection,
            matter_lifecycle_collection=matter_lifecycle_collection,
        )
        self._acknowledgment_composer = acknowledgment_composer.LegalClientMatterMandateAcknowledgmentCurrentnessComposer(
            grant_collection=grant_collection,
            acknowledgment_collection=acknowledgment_collection,
        )

    def compose_currentness(
        self,
        tenant_id: str,
        mandate_id: str,
        evaluation_time: datetime,
        session: Any,
    ) -> LegalClientMatterMandateCurrentness:
        """Read exact evidence and construct the certified pure projection.

        Mandate registry, grant-currentness and acknowledgment-currentness
        reads receive the identical session and explicit evaluation instant.
        Missing mandate formation returns ``FORMATION_ABSENT``. Any corrupt or
        unavailable upstream evidence fails closed without synthetic authority.
        """
        transaction = _active_transaction(session)
        tenant = _text("tenant_id", tenant_id)
        requested_mandate_id = _text("mandate_id", mandate_id)
        at = _evaluation_time(evaluation_time)
        try:
            mandate = mandate_registry.get_mandate(
                tenant,
                requested_mandate_id,
                self._mandate_collection,
                session=transaction,
            )
        except mandate_registry.LegalClientMatterMandateRegistryNotFoundError:
            return _formation_absent(
                tenant_id=tenant,
                mandate_id=requested_mandate_id,
                evaluation_time=at,
            )
        except mandate_registry.LegalClientMatterMandateRegistryError as error:
            _fail("L9B12_P2_MANDATE_READ_FAILED", error)
        if type(mandate) is not LegalClientMatterMandate:
            _fail("L9B12_P2_MANDATE_INVALID")
        if mandate.tenant_id != tenant or mandate.mandate_id != requested_mandate_id:
            _fail("L9B12_P2_MANDATE_CORRELATION_INVALID")
        try:
            grant_value = self._grant_composer.compose_currentness(
                tenant,
                mandate.client_grant_reference,
                at,
                transaction,
            )
        except grant_composer.LegalClientMatterMandateGrantCurrentnessComposerError as error:
            _fail("L9B12_P2_GRANT_CURRENTNESS_READ_FAILED", error)
        try:
            acknowledgment_value = self._acknowledgment_composer.compose_currentness(
                tenant,
                mandate.client_grant_reference,
                at,
                transaction,
            )
        except acknowledgment_composer.LegalClientMatterMandateAcknowledgmentCurrentnessComposerError as error:
            _fail("L9B12_P2_ACKNOWLEDGMENT_CURRENTNESS_READ_FAILED", error)
        grant, acknowledgment = _require_upstream_types(grant_value, acknowledgment_value)
        try:
            return project_legal_client_matter_mandate_currentness(
                tenant_id=tenant,
                mandate_id=requested_mandate_id,
                mandate=mandate,
                grant_currentness=grant,
                acknowledgment_currentness=acknowledgment,
                evaluation_time=at,
            )
        except ValueError as error:
            _fail("L9B12_P2_PROJECTION_FAILED", error)


def compose_currentness(
    *,
    tenant_id: str,
    mandate_id: str,
    evaluation_time: datetime,
    session: Any,
    mandate_collection: Any,
    grant_collection: Any,
    grant_lifecycle_collection: Any,
    matter_lifecycle_collection: Any,
    acknowledgment_collection: Any,
) -> LegalClientMatterMandateCurrentness:
    """Compose through a one-shot functional boundary with the same contract."""
    composer = LegalClientMatterMandateCurrentnessComposer(
        mandate_collection=mandate_collection,
        grant_collection=grant_collection,
        grant_lifecycle_collection=grant_lifecycle_collection,
        matter_lifecycle_collection=matter_lifecycle_collection,
        acknowledgment_collection=acknowledgment_collection,
    )
    return composer.compose_currentness(tenant_id, mandate_id, evaluation_time, session)


__all__ = [
    "VERSION",
    "LegalClientMatterMandateCurrentnessComposer",
    "LegalClientMatterMandateCurrentnessComposerError",
    "compose_currentness",
]


# ARTIFACT: legal_client_matter_mandate_currentness_composer.py
# VERSION: v1.0.0-L9B12-P2-CLIENT-MATTER-MANDATE-CURRENTNESS-COMPOSER
# AUTHORITY BOUNDARY: read-only composition of pure mandate currentness
# TENANT POSTURE: exact tenant-bound mandate, grant and acknowledgment reads
# FAIL-CLOSED POSTURE: active transaction, upstream and projection validation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
