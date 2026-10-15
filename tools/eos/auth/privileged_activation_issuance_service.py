"""Minimal P4 privileged-activation issuance orchestration.

This service composes already-certified authority only.

Issuance requires, inside one caller-owned active transaction:

1. fresh P3 creation-purpose assurance;
2. exact current P2 privileged eligibility;
3. exact current SYSTEM possession of ``privileged_activation:issue``;
4. self-activation identity binding;
5. persistence through the certified activation registry.

Role, target class, tenant scope, and eligibility lineage are derived from
current P2 evidence. Principal identity is derived from fresh P3. The service
does not own transaction lifecycle, transport, current-use authority, or any
unrelated business authority.
"""

from __future__ import annotations

from datetime import datetime
from hashlib import sha3_512
from typing import Any, Callable, Mapping
from uuid import uuid4

from tools.eos.auth.privileged_activation import (
    ISSUANCE_PERMISSION,
    MAXIMUM_ACTIVATION_LIFETIME,
    PrivilegedActivation,
)
from tools.eos.auth.privileged_activation_registry import (
    PrivilegedActivationConflictError,
)
from tools.eos.auth.privileged_eligibility import (
    PrivilegedTargetClass,
)
from tools.eos.auth.privileged_security_assurance import (
    PrivilegedAssuranceChannel,
    PrivilegedAssurancePurpose,
)


_CREATION_PURPOSE = (
    PrivilegedAssurancePurpose
    .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
)


class PrivilegedActivationIssuanceError(
    RuntimeError
):
    """Fail-closed P4 issuance-composition error."""

    def __init__(
        self,
        code: str,
    ) -> None:
        self.code = code
        super().__init__(code)


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        raise PrivilegedActivationIssuanceError(
            name + "_INVALID"
        )

    return value


def _optional_tenant(
    value: object,
) -> str | None:
    if value is None:
        return None

    return _text(
        "TENANT_ID",
        value,
    )


def _active_transaction(
    session: object,
) -> object:
    if (
        session is None
        or getattr(
            session,
            "in_transaction",
            False,
        )
        is not True
    ):
        raise PrivilegedActivationIssuanceError(
            "ACTIVE_TRANSACTION_REQUIRED"
        )

    return session


def _moment(
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise PrivilegedActivationIssuanceError(
            "CLOCK_INVALID"
        )

    return value


class PrivilegedActivationIssuanceService:
    """Compose one exact P4 activation from sealed authorities."""

    def __init__(
        self,
        *,
        permission_resolver: Any,
        eligibility_resolver: Any,
        interactive_assurance_service: Any,
        noninteractive_assurance_service: Any,
        activation_registry: Any,
        activation_id_factory: Callable[[], str],
        clock: Callable[[], datetime],
        assurance_attempt_id_factory: Callable[[], str] | None = None,
    ) -> None:
        if not callable(
            activation_id_factory
        ):
            raise PrivilegedActivationIssuanceError(
                "ACTIVATION_ID_FACTORY_INVALID"
            )

        if not callable(clock):
            raise PrivilegedActivationIssuanceError(
                "CLOCK_INVALID"
            )

        self._permission_resolver = (
            permission_resolver
        )
        self._eligibility_resolver = (
            eligibility_resolver
        )
        self._interactive_assurance_service = (
            interactive_assurance_service
        )
        self._noninteractive_assurance_service = (
            noninteractive_assurance_service
        )
        self._activation_registry = (
            activation_registry
        )
        self._activation_id_factory = (
            activation_id_factory
        )
        self._clock = clock
        self._assurance_attempt_id_factory = (
            assurance_attempt_id_factory
            if assurance_attempt_id_factory is not None
            else lambda: uuid4().hex
        )

    @staticmethod
    def _validate_assurance(
        *,
        result: Any,
        expected_channel: PrivilegedAssuranceChannel,
    ) -> tuple[str, Any]:
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

        if (
            decision is None
            or evidence is None
        ):
            raise PrivilegedActivationIssuanceError(
                "ASSURANCE_RESULT_INVALID"
            )

        decision_principal = getattr(
            decision,
            "principal_id",
            None,
        )
        evidence_principal = getattr(
            evidence,
            "principal_id",
            None,
        )

        if (
            not isinstance(
                decision_principal,
                str,
            )
            or not decision_principal
            or (
                decision_principal
                != decision_principal.strip()
            )
            or evidence_principal
            != decision_principal
        ):
            raise PrivilegedActivationIssuanceError(
                "ASSURANCE_PRINCIPAL_INVALID"
            )

        if (
            getattr(
                decision,
                "assurance_channel",
                None,
            )
            is not expected_channel
            or getattr(
                evidence,
                "assurance_channel",
                None,
            )
            is not expected_channel
        ):
            raise PrivilegedActivationIssuanceError(
                "ASSURANCE_CHANNEL_INVALID"
            )

        if (
            getattr(
                decision,
                "assurance_purpose",
                None,
            )
            is not _CREATION_PURPOSE
            or getattr(
                evidence,
                "assurance_purpose",
                None,
            )
            is not _CREATION_PURPOSE
        ):
            raise PrivilegedActivationIssuanceError(
                "ASSURANCE_PURPOSE_INVALID"
            )

        if (
            getattr(
                decision,
                "sufficient",
                None,
            )
            is not True
            or getattr(
                evidence,
                "sufficient",
                None,
            )
            is not True
        ):
            raise PrivilegedActivationIssuanceError(
                "ASSURANCE_INSUFFICIENT"
            )

        evidence_id = getattr(
            evidence,
            "assurance_evidence_id",
            None,
        )

        fingerprint = getattr(
            evidence,
            "assurance_evidence_fingerprint",
            None,
        )

        if (
            not isinstance(evidence_id, str)
            or not evidence_id
            or evidence_id
            != evidence_id.strip()
        ):
            raise PrivilegedActivationIssuanceError(
                "ASSURANCE_EVIDENCE_ID_INVALID"
            )

        if (
            not isinstance(fingerprint, str)
            or len(fingerprint) != 128
            or fingerprint
            != fingerprint.lower()
            or any(
                char
                not in "0123456789abcdef"
                for char in fingerprint
            )
        ):
            raise PrivilegedActivationIssuanceError(
                "ASSURANCE_EVIDENCE_FINGERPRINT_INVALID"
            )

        return (
            decision_principal,
            evidence,
        )

    def _resolve_eligibility(
        self,
        *,
        principal_id: str,
        tenant_id: str | None,
        eligibility_evidence_id: str,
        at: datetime,
        session: object,
    ) -> Any:
        evidence = (
            self._eligibility_resolver
            .resolve(
                eligibility_evidence_id=
                    eligibility_evidence_id,
                at=at,
                session=session,
            )
        )

        if evidence is None:
            raise PrivilegedActivationIssuanceError(
                "ELIGIBILITY_NOT_CURRENT"
            )

        if (
            getattr(
                evidence,
                "eligibility_evidence_id",
                None,
            )
            != eligibility_evidence_id
        ):
            raise PrivilegedActivationIssuanceError(
                "ELIGIBILITY_EVIDENCE_ID_MISMATCH"
            )

        if (
            getattr(
                evidence,
                "principal_id",
                None,
            )
            != principal_id
        ):
            raise PrivilegedActivationIssuanceError(
                "ELIGIBILITY_PRINCIPAL_MISMATCH"
            )

        evidence_tenant = getattr(
            evidence,
            "tenant_id",
            None,
        )

        target_class = getattr(
            evidence,
            "target_class",
            None,
        )

        if (
            target_class
            is PrivilegedTargetClass
            .PLATFORM_SYSTEM_ROOT
        ):
            if (
                tenant_id is not None
                or evidence_tenant is not None
            ):
                raise PrivilegedActivationIssuanceError(
                    "ELIGIBILITY_SCOPE_MISMATCH"
                )

        elif (
            target_class
            is PrivilegedTargetClass
            .TENANT_PRIVILEGED
        ):
            if (
                tenant_id is None
                or evidence_tenant
                != tenant_id
            ):
                raise PrivilegedActivationIssuanceError(
                    "ELIGIBILITY_SCOPE_MISMATCH"
                )

        else:
            raise PrivilegedActivationIssuanceError(
                "ELIGIBILITY_TARGET_CLASS_INVALID"
            )

        role_id = getattr(
            evidence,
            "privileged_role_id",
            None,
        )

        if (
            not isinstance(role_id, str)
            or not role_id
            or role_id != role_id.strip()
        ):
            raise PrivilegedActivationIssuanceError(
                "ELIGIBILITY_ROLE_INVALID"
            )

        fingerprint = getattr(
            evidence,
            "eligibility_evidence_fingerprint",
            None,
        )

        if (
            not isinstance(fingerprint, str)
            or len(fingerprint) != 128
            or fingerprint
            != fingerprint.lower()
            or any(
                char
                not in "0123456789abcdef"
                for char in fingerprint
            )
        ):
            raise PrivilegedActivationIssuanceError(
                "ELIGIBILITY_EVIDENCE_FINGERPRINT_INVALID"
            )

        return evidence

    def _require_permission(
        self,
        *,
        principal_id: str,
        session: object,
    ) -> None:
        if (
            self._permission_resolver
            .possesses(
                principal_id=
                    principal_id,
                permission_id=
                    ISSUANCE_PERMISSION,
                session=session,
            )
            is not True
        ):
            raise PrivilegedActivationIssuanceError(
                "ISSUANCE_PERMISSION_NOT_CURRENT"
            )

    @staticmethod
    def _deterministic_activation_id(
        issuance_idempotency_key: str,
    ) -> str:
        """Bind one stable opaque activation identity to one issuance key."""

        payload = (
            "WILSY:P4:PRIVILEGED_ACTIVATION:"
            + issuance_idempotency_key
        ).encode(
            "utf-8"
        )

        return (
            "WILSYACTIVATION-"
            + sha3_512(
                payload
            ).hexdigest()
        )

    def _fresh_assurance_idempotency_key(
        self,
        issuance_idempotency_key: str,
    ) -> str:
        """Create a distinct P3 observation scope for this issuance attempt."""

        attempt = _text(
            "ASSURANCE_ATTEMPT_ID",
            self._assurance_attempt_id_factory(),
        )

        return (
            issuance_idempotency_key
            + ":assurance:"
            + attempt
        )

    def _validate_replay(
        self,
        *,
        history: tuple[PrivilegedActivation, ...],
        activation_id: str,
        principal_id: str,
        tenant_id: str | None,
        eligibility: Any,
        at: datetime,
        issuance_idempotency_key: str,
    ) -> PrivilegedActivation | None:
        """Return an exact still-current replay or fail closed."""

        if not history:
            return None

        original = history[0]
        latest = history[-1]

        if (
            original.activation_id
            != activation_id
            or original.issuance_idempotency_key
            != issuance_idempotency_key
            or original.principal_id
            != principal_id
            or original.actor_principal_id
            != principal_id
            or original.tenant_id
            != tenant_id
            or original.privileged_role_id
            != eligibility.privileged_role_id
            or original.target_class
            is not eligibility.target_class
            or original.eligibility_evidence_id
            != eligibility.eligibility_evidence_id
            or original.eligibility_evidence_fingerprint
            != eligibility.eligibility_evidence_fingerprint
        ):
            raise PrivilegedActivationIssuanceError(
                "ACTIVATION_REPLAY_LINEAGE_MISMATCH"
            )

        if not latest.is_current(
            at=at,
            tenant_id=tenant_id,
            principal_id=principal_id,
            privileged_role_id=
                eligibility.privileged_role_id,
            target_class=
                eligibility.target_class,
        ):
            raise PrivilegedActivationIssuanceError(
                "ACTIVATION_REPLAY_NOT_CURRENT"
            )

        return original

    def _history_replay(
        self,
        *,
        activation_id: str,
        principal_id: str,
        tenant_id: str | None,
        eligibility: Any,
        at: datetime,
        issuance_idempotency_key: str,
        session: object,
    ) -> PrivilegedActivation | None:
        """Read and validate existing issuance history after fresh authority."""

        history = (
            self._activation_registry
            .get_history(
                activation_id,
                session=session,
            )
        )

        return self._validate_replay(
            history=history,
            activation_id=activation_id,
            principal_id=principal_id,
            tenant_id=tenant_id,
            eligibility=eligibility,
            at=at,
            issuance_idempotency_key=
                issuance_idempotency_key,
        )

    def _persist(
        self,
        *,
        principal_id: str,
        tenant_id: str | None,
        eligibility: Any,
        assurance: Any,
        activated_at: datetime,
        issuance_idempotency_key: str,
        session: object,
    ) -> PrivilegedActivation:
        activation_id = (
            self._deterministic_activation_id(
                issuance_idempotency_key
            )
        )

        replay = self._history_replay(
            activation_id=activation_id,
            principal_id=principal_id,
            tenant_id=tenant_id,
            eligibility=eligibility,
            at=activated_at,
            issuance_idempotency_key=
                issuance_idempotency_key,
            session=session,
        )

        if replay is not None:
            return replay

        activation = (
            PrivilegedActivation.issue(
                activation_id=activation_id,
                tenant_id=tenant_id,
                principal_id=principal_id,
                actor_principal_id=
                    principal_id,
                privileged_role_id=
                    eligibility
                    .privileged_role_id,
                target_class=
                    eligibility.target_class,
                eligibility_evidence_id=
                    eligibility
                    .eligibility_evidence_id,
                eligibility_evidence_fingerprint=
                    eligibility
                    .eligibility_evidence_fingerprint,
                assurance_evidence_id=
                    assurance
                    .assurance_evidence_id,
                assurance_evidence_fingerprint=
                    assurance
                    .assurance_evidence_fingerprint,
                creation_assurance_purpose=
                    _CREATION_PURPOSE,
                activated_at=activated_at,
                effective_until=(
                    activated_at
                    + MAXIMUM_ACTIVATION_LIFETIME
                ),
                issuance_idempotency_key=
                    issuance_idempotency_key,
            )
        )

        try:
            persisted = (
                self._activation_registry
                .create_or_replay(
                    activation,
                    session=session,
                )
            )

        except PrivilegedActivationConflictError:
            concurrent = self._history_replay(
                activation_id=activation_id,
                principal_id=principal_id,
                tenant_id=tenant_id,
                eligibility=eligibility,
                at=activated_at,
                issuance_idempotency_key=
                    issuance_idempotency_key,
                session=session,
            )

            if concurrent is None:
                raise

            return concurrent

        if (
            not isinstance(
                persisted,
                PrivilegedActivation,
            )
        ):
            raise PrivilegedActivationIssuanceError(
                "ACTIVATION_PERSISTENCE_RESULT_INVALID"
            )

        return persisted

    def issue_interactive(
        self,
        *,
        tenant_id: str | None,
        eligibility_evidence_id: str,
        proof_tenant_id: str,
        proof_reference: str,
        issuance_idempotency_key: str,
        session: object,
    ) -> PrivilegedActivation:
        """Issue from fresh interactive creation-purpose P3."""

        tx = _active_transaction(
            session
        )

        requested_tenant = (
            _optional_tenant(
                tenant_id
            )
        )

        evidence_id = _text(
            "ELIGIBILITY_EVIDENCE_ID",
            eligibility_evidence_id,
        )

        replay_key = _text(
            "ISSUANCE_IDEMPOTENCY_KEY",
            issuance_idempotency_key,
        )

        proof_tenant = _text(
            "PROOF_TENANT_ID",
            proof_tenant_id,
        )

        proof = _text(
            "PROOF_REFERENCE",
            proof_reference,
        )

        assurance_result = (
            self
            ._interactive_assurance_service
            .compose(
                tenant_id=proof_tenant,
                proof_reference=proof,
                assurance_purpose=
                    _CREATION_PURPOSE,
                idempotency_key=(
                    self
                    ._fresh_assurance_idempotency_key(
                        replay_key
                    )
                ),
                session=tx,
            )
        )

        principal_id, assurance = (
            self._validate_assurance(
                result=assurance_result,
                expected_channel=(
                    PrivilegedAssuranceChannel
                    .INTERACTIVE_STRONG_AUTH
                ),
            )
        )

        activated_at = _moment(
            self._clock()
        )

        eligibility = (
            self._resolve_eligibility(
                principal_id=principal_id,
                tenant_id=requested_tenant,
                eligibility_evidence_id=
                    evidence_id,
                at=activated_at,
                session=tx,
            )
        )

        self._require_permission(
            principal_id=principal_id,
            session=tx,
        )

        return self._persist(
            principal_id=principal_id,
            tenant_id=requested_tenant,
            eligibility=eligibility,
            assurance=assurance,
            activated_at=activated_at,
            issuance_idempotency_key=
                replay_key,
            session=tx,
        )

    def issue_noninteractive(
        self,
        *,
        tenant_id: str | None,
        eligibility_evidence_id: str,
        request: Mapping[str, str],
        body: bytes,
        keys: Mapping[
            str,
            tuple[str, str],
        ],
        expected_audience: str,
        issuance_idempotency_key: str,
        session: object,
    ) -> PrivilegedActivation:
        """Issue from fresh noninteractive creation-purpose P3."""

        tx = _active_transaction(
            session
        )

        requested_tenant = (
            _optional_tenant(
                tenant_id
            )
        )

        evidence_id = _text(
            "ELIGIBILITY_EVIDENCE_ID",
            eligibility_evidence_id,
        )

        replay_key = _text(
            "ISSUANCE_IDEMPOTENCY_KEY",
            issuance_idempotency_key,
        )

        audience = _text(
            "EXPECTED_AUDIENCE",
            expected_audience,
        )

        assurance_result = (
            self
            ._noninteractive_assurance_service
            .compose(
                request=request,
                body=body,
                keys=keys,
                expected_audience=audience,
                assurance_purpose=
                    _CREATION_PURPOSE,
                idempotency_key=(
                    self
                    ._fresh_assurance_idempotency_key(
                        replay_key
                    )
                ),
                session=tx,
            )
        )

        principal_id, assurance = (
            self._validate_assurance(
                result=assurance_result,
                expected_channel=(
                    PrivilegedAssuranceChannel
                    .NONINTERACTIVE_WORKLOAD_PROOF
                ),
            )
        )

        workload_fact = getattr(
            assurance_result,
            "workload_fact",
            None,
        )

        if (
            workload_fact is None
            or getattr(
                workload_fact,
                "principal_id",
                None,
            )
            != principal_id
        ):
            raise PrivilegedActivationIssuanceError(
                "ASSURANCE_PRINCIPAL_INVALID"
            )

        activated_at = _moment(
            self._clock()
        )

        eligibility = (
            self._resolve_eligibility(
                principal_id=principal_id,
                tenant_id=requested_tenant,
                eligibility_evidence_id=
                    evidence_id,
                at=activated_at,
                session=tx,
            )
        )

        self._require_permission(
            principal_id=principal_id,
            session=tx,
        )

        return self._persist(
            principal_id=principal_id,
            tenant_id=requested_tenant,
            eligibility=eligibility,
            assurance=assurance,
            activated_at=activated_at,
            issuance_idempotency_key=
                replay_key,
            session=tx,
        )


__all__ = [
    "PrivilegedActivationIssuanceError",
    "PrivilegedActivationIssuanceService",
]
