"""
TITLE:
    WILSY OS Privileged Activation Current-Use Authority

VERSION:
    v1.0.0-P5-PRIVILEGED-ACTIVATION-CURRENT-USE-AUTHORITY

AUTHORITY:
    Wilsy OS Sovereign IAM

EPITOME:
    Authoritative P5 fail-closed current-use composition for an already-issued
    privileged activation. The authority revalidates the exact persisted P4
    activation, re-resolves its exact P2 eligibility lineage, and composes a
    fresh P3 assurance for PRIVILEGED_ACTIVATION_USE before privileged use.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/privileged_activation_use_authority.py

COLLABORATION / OWNERSHIP:
    P5 composes sealed P2 current privileged eligibility, sealed P3 privileged
    security assurance services, and sealed P4 privileged activation currentness.
    Caller code owns transaction lifecycle and transport context.

CERTIFICATION / UPDATE DATE:
    2026-10-15

CHANGELOG:
    v1.0.0-P5-PRIVILEGED-ACTIVATION-CURRENT-USE-AUTHORITY
        Initial sovereign P5 current-use authority. Separates activation tenant
        scope from interactive proof tenant, preserves exact P2 lineage,
        propagates caller session, and requires fresh P3 assurance for
        PRIVILEGED_ACTIVATION_USE.

COMPLIANCE:
    Fail-closed. No invented permission, role, activation, persistence, HTTP,
    break-glass, billing, payment, settlement, subscription, or financial truth.

SECURITY / PRIVACY POSTURE:
    Revalidates current P4/P2 authority before fresh P3 use-time assurance.
    No raw secret, credential, token, signature, or payment instrument is
    persisted by this module.

TENANT BOUNDARY:
    Activation tenant scope is exact. Platform-system-root activation requires
    tenant_id None. Interactive assurance proof tenant is separate and explicit.

AUTHORITY BOUNDARY:
    This module authorizes current privileged use only after exact P4, P2, and
    fresh P3 evidence. It does not issue or extend activations, create roles or
    permissions, own transaction lifecycle, expose HTTP authority, or create
    break-glass authority.

FINANCIAL AUTHORITY BOUNDARY:
    NONE. This module never executes, releases, records, settles, or infers
    payment or financial execution truth.
"""

from __future__ import annotations

from datetime import datetime
from typing import Mapping, Protocol

from tools.eos.auth.privileged_activation import (
    PrivilegedActivation,
)
from tools.eos.auth.privileged_eligibility import (
    PrivilegedTargetClass,
)
from tools.eos.auth.privileged_security_assurance import (
    PrivilegedAssurancePurpose,
)


class PrivilegedActivationUseError(RuntimeError):
    """Raised when P5 current privileged use cannot be authorized."""


class _ActivationRegistry(Protocol):
    """Read-only P4 current-activation dependency contract."""

    def resolve_current(
        self,
        *,
        tenant_id: str | None,
        principal_id: str,
        privileged_role_id: str,
        target_class: PrivilegedTargetClass,
        at: datetime,
        session: object | None = None,
    ) -> PrivilegedActivation | None:
        """Return the exact current P4 activation for the supplied scope."""


class _EligibilityResolver(Protocol):
    """Read-only P2 current-eligibility dependency contract."""

    def resolve(
        self,
        *,
        eligibility_evidence_id: str,
        at: datetime,
        session: object | None = None,
    ) -> object | None:
        """Return exact P2 evidence iff its live authority remains current."""


class _InteractiveAssuranceService(Protocol):
    """P3 interactive assurance composition dependency contract."""

    def compose(
        self,
        *,
        tenant_id: str,
        proof_reference: str,
        assurance_purpose: PrivilegedAssurancePurpose,
        idempotency_key: str,
        session: object,
    ) -> object:
        """Compose fresh interactive P3 evidence in the caller transaction."""


class _NoninteractiveAssuranceService(Protocol):
    """P3 noninteractive assurance composition dependency contract."""

    def compose(
        self,
        *,
        request: Mapping[str, str],
        body: bytes,
        keys: Mapping[str, tuple[str, str]],
        expected_audience: str,
        assurance_purpose: PrivilegedAssurancePurpose,
        idempotency_key: str,
        session: object,
    ) -> object:
        """Compose fresh noninteractive P3 evidence in the caller transaction."""


class PrivilegedActivationUseAuthority:
    """Compose fail-closed current privileged use from sealed P2/P3/P4 truth."""

    def __init__(
        self,
        *,
        activation_registry: _ActivationRegistry,
        eligibility_resolver: _EligibilityResolver,
        interactive_assurance_service: (
            _InteractiveAssuranceService | None
        ) = None,
        noninteractive_assurance_service: (
            _NoninteractiveAssuranceService | None
        ) = None,
    ) -> None:
        """
        Bind existing sealed authorities without acquiring transaction ownership.

        Authority:
            Dependency composition only. No activation issuance, permission
            creation, role creation, break-glass, HTTP, or financial authority.

        Transaction ownership:
            The caller owns every supplied session and transaction.
        """
        self._activation_registry = activation_registry
        self._eligibility_resolver = eligibility_resolver
        self._interactive_assurance_service = (
            interactive_assurance_service
        )
        self._noninteractive_assurance_service = (
            noninteractive_assurance_service
        )

    def _current_activation_and_eligibility(
        self,
        *,
        tenant_id: str | None,
        principal_id: str,
        privileged_role_id: str,
        target_class: PrivilegedTargetClass,
        at: datetime,
        session: object | None,
    ) -> PrivilegedActivation:
        """Return exact current activation only when its exact P2 lineage is live."""
        activation = self._activation_registry.resolve_current(
            tenant_id=tenant_id,
            principal_id=principal_id,
            privileged_role_id=privileged_role_id,
            target_class=target_class,
            at=at,
            session=session,
        )

        if activation is None:
            raise PrivilegedActivationUseError(
                "CURRENT_PRIVILEGED_ACTIVATION_REQUIRED"
            )

        if not activation.is_current(
            at=at,
            tenant_id=tenant_id,
            principal_id=principal_id,
            privileged_role_id=privileged_role_id,
            target_class=target_class,
        ):
            raise PrivilegedActivationUseError(
                "CURRENT_PRIVILEGED_ACTIVATION_REQUIRED"
            )

        eligibility = self._eligibility_resolver.resolve(
            eligibility_evidence_id=(
                activation.eligibility_evidence_id
            ),
            at=at,
            session=session,
        )

        if eligibility is None:
            raise PrivilegedActivationUseError(
                "CURRENT_PRIVILEGED_ELIGIBILITY_REQUIRED"
            )

        if not self._eligibility_matches_activation(
            eligibility,
            activation,
        ):
            raise PrivilegedActivationUseError(
                "PRIVILEGED_ELIGIBILITY_LINEAGE_MISMATCH"
            )

        return activation

    def authorize_interactive(
        self,
        *,
        activation_tenant_id: str | None,
        proof_tenant_id: str,
        principal_id: str,
        privileged_role_id: str,
        target_class: PrivilegedTargetClass,
        at: datetime,
        proof_reference: str,
        idempotency_key: str,
        session: object,
    ) -> PrivilegedActivation:
        """
        Authorize current interactive privileged use.

        Authority:
            Requires an exact current P4 activation, exact current P2 evidence
            matching the activation lineage and scope, and a freshly composed P3
            interactive assurance for PRIVILEGED_ACTIVATION_USE.

        Tenant boundary:
            activation_tenant_id is the P4 activation scope. proof_tenant_id is
            the independent tenant context required by interactive P3 proof
            composition. Platform-root activation scope remains None.

        Mutation semantics:
            This method performs no P4 or P2 mutation. P3 may persist fresh
            assurance evidence using the caller-owned transaction.

        Idempotency:
            The caller supplies the P3 idempotency key. P5 itself creates no
            durable idempotency registry.

        Transaction ownership:
            session is caller-owned. P5 never commits or aborts it.

        Fail-closed behavior:
            Missing/stale activation, stale/mismatched P2, unavailable P3,
            insufficient P3, purpose mismatch, or principal mismatch denies use.

        Financial boundary:
            NONE.
        """
        activation = self._current_activation_and_eligibility(
            tenant_id=activation_tenant_id,
            principal_id=principal_id,
            privileged_role_id=privileged_role_id,
            target_class=target_class,
            at=at,
            session=session,
        )

        service = self._interactive_assurance_service

        if service is None:
            raise PrivilegedActivationUseError(
                "INTERACTIVE_ASSURANCE_SERVICE_REQUIRED"
            )

        result = service.compose(
            tenant_id=proof_tenant_id,
            proof_reference=proof_reference,
            assurance_purpose=(
                PrivilegedAssurancePurpose
                .PRIVILEGED_ACTIVATION_USE
            ),
            idempotency_key=idempotency_key,
            session=session,
        )

        self._validate_assurance_result(
            result,
            principal_id=principal_id,
        )

        return activation

    def authorize_noninteractive(
        self,
        *,
        activation_tenant_id: str | None,
        principal_id: str,
        privileged_role_id: str,
        target_class: PrivilegedTargetClass,
        at: datetime,
        request: Mapping[str, str],
        body: bytes,
        keys: Mapping[str, tuple[str, str]],
        expected_audience: str,
        idempotency_key: str,
        session: object,
    ) -> PrivilegedActivation:
        """
        Authorize current noninteractive privileged use.

        Authority:
            Requires exact current P4 and P2 authority and a freshly composed
            noninteractive P3 assurance for PRIVILEGED_ACTIVATION_USE.

        Tenant boundary:
            activation_tenant_id is the exact P4 activation scope. Workload
            principal identity is derived by the sealed P3 workload authority,
            not asserted by P5.

        Mutation semantics:
            P5 itself performs no durable mutation. P3 may persist fresh proof
            and assurance evidence inside the caller-owned transaction.

        Idempotency:
            The caller supplies the P3 idempotency key.

        Transaction ownership:
            session is caller-owned. P5 never commits or aborts it.

        Fail-closed behavior:
            Missing/stale activation, stale/mismatched P2, unavailable P3,
            insufficient P3, purpose mismatch, or principal mismatch denies use.

        Financial boundary:
            NONE.
        """
        activation = self._current_activation_and_eligibility(
            tenant_id=activation_tenant_id,
            principal_id=principal_id,
            privileged_role_id=privileged_role_id,
            target_class=target_class,
            at=at,
            session=session,
        )

        service = self._noninteractive_assurance_service

        if service is None:
            raise PrivilegedActivationUseError(
                "NONINTERACTIVE_ASSURANCE_SERVICE_REQUIRED"
            )

        result = service.compose(
            request=request,
            body=body,
            keys=keys,
            expected_audience=expected_audience,
            assurance_purpose=(
                PrivilegedAssurancePurpose
                .PRIVILEGED_ACTIVATION_USE
            ),
            idempotency_key=idempotency_key,
            session=session,
        )

        self._validate_assurance_result(
            result,
            principal_id=principal_id,
        )

        return activation

    @staticmethod
    def _validate_assurance_result(
        result: object,
        *,
        principal_id: str,
    ) -> None:
        """Fail closed unless the P3 result proves sufficient exact use assurance."""
        decision = getattr(
            result,
            "decision",
            None,
        )

        evidence = getattr(
            result,
            "evidence",
            None,
        )

        if decision is None or evidence is None:
            raise PrivilegedActivationUseError(
                "PRIVILEGED_USE_ASSURANCE_REQUIRED"
            )

        if getattr(
            decision,
            "sufficient",
            None,
        ) is not True:
            raise PrivilegedActivationUseError(
                "PRIVILEGED_USE_ASSURANCE_INSUFFICIENT"
            )

        purpose = getattr(
            evidence,
            "assurance_purpose",
            getattr(
                evidence,
                "purpose",
                None,
            ),
        )

        if purpose != (
            PrivilegedAssurancePurpose
            .PRIVILEGED_ACTIVATION_USE
        ):
            raise PrivilegedActivationUseError(
                "PRIVILEGED_USE_ASSURANCE_PURPOSE_INVALID"
            )

        evidence_principal = getattr(
            evidence,
            "principal_id",
            None,
        )

        if (
            evidence_principal is not None
            and evidence_principal != principal_id
        ):
            raise PrivilegedActivationUseError(
                "PRIVILEGED_USE_ASSURANCE_PRINCIPAL_MISMATCH"
            )

    @staticmethod
    def _eligibility_matches_activation(
        eligibility: object,
        activation: PrivilegedActivation,
    ) -> bool:
        """Return whether current P2 evidence exactly matches activation lineage."""
        evidence_id = getattr(
            eligibility,
            "eligibility_evidence_id",
            getattr(
                eligibility,
                "evidence_id",
                None,
            ),
        )

        fingerprint = getattr(
            eligibility,
            "eligibility_evidence_fingerprint",
            getattr(
                eligibility,
                "evidence_fingerprint",
                None,
            ),
        )

        return (
            evidence_id
            == activation.eligibility_evidence_id
            and fingerprint
            == activation.eligibility_evidence_fingerprint
            and getattr(
                eligibility,
                "tenant_id",
                object(),
            )
            == activation.tenant_id
            and getattr(
                eligibility,
                "principal_id",
                None,
            )
            == activation.principal_id
            and getattr(
                eligibility,
                "privileged_role_id",
                None,
            )
            == activation.privileged_role_id
            and getattr(
                eligibility,
                "target_class",
                None,
            )
            == activation.target_class
        )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: privileged_activation_use_authority.py
# VERSION: v1.0.0-P5-PRIVILEGED-ACTIVATION-CURRENT-USE-AUTHORITY
# AUTHORITY BOUNDARY:
#   Current privileged-use composition only. No activation issuance, role or
#   permission creation, transaction ownership, HTTP, or break-glass authority.
# TENANT POSTURE:
#   Exact activation tenant scope; platform-root tenant is None; interactive
#   proof tenant remains separate and explicit.
# FAIL-CLOSED POSTURE:
#   Missing/stale P4, stale/mismatched P2, or insufficient/wrong P3 denies use.
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
