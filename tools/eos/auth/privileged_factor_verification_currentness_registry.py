"""WILSY OS durable current interactive factor-verification authority.

TITLE: Privileged Factor Verification Currentness Registry
VERSION: v1.1.0-P3-R3G-C6-FACTOR-BSON-UTC-HYDRATION
AUTHORITY: Wilsy OS Sovereign IAM
EPITOME: Persists exact secret-free factor verification currentness and terminal lifecycle state.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/privileged_factor_verification_currentness_registry.py
COLLABORATION / OWNERSHIP: Auth HTTP issuance and P3 interactive assurance composition.
CERTIFICATION / UPDATE DATE: 2026-10-14
CHANGELOG: v1.1.0-P3-R3G-C6-FACTOR-BSON-UTC-HYDRATION normalizes valid default-PyMongo BSON authenticated_at datetimes to aware UTC during strict hydration; v1.0.0 established reference currentness and terminal transitions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Secret-free references only; malformed persisted state fails closed.
TENANT BOUNDARY: No tenant membership, role, or permission authority.
AUTHORITY BOUNDARY: Factor-verification currentness only; no OTP verification or privileged activation.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller owns active transaction, commit, abort, and retry.

This registry owns immutable, reference-addressable factor-verification events
and terminal revocation/invalidation. It does not verify OTP material itself,
create sessions/tokens, establish eligibility, activate privilege, or assign
roles.

One factor_verification_reference identifies one logical verification event.
One session_reference may have multiple distinct verification events over time.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.privileged_channel_currentness import (
    FactorVerificationStatus,
    InteractiveFactorVerificationEvent,
)


VERSION = "v1.1.0-P3-R3G-C6-FACTOR-BSON-UTC-HYDRATION"
COLLECTION = "privileged_factor_verification_currentness"

REFERENCE_INDEX = "priv_factor_reference_unique"
PRINCIPAL_SESSION_INDEX = "priv_factor_principal_session_time"
STATUS_INDEX = "priv_factor_status_time"


class FactorCurrentnessRegistryError(RuntimeError):
    pass


class FactorCurrentnessConflictError(
    FactorCurrentnessRegistryError
):
    pass


class FactorCurrentnessPersistenceError(
    FactorCurrentnessRegistryError
):
    pass


def _identifier(name: str, value: object) -> str:
    if not isinstance(value, str):
        raise FactorCurrentnessRegistryError(
            f"{name} invalid"
        )

    cleaned = value.strip()

    if not cleaned or len(cleaned) > 1024:
        raise FactorCurrentnessRegistryError(
            f"{name} invalid"
        )

    return cleaned


def _active_transaction(session: object) -> Any:
    if session is None:
        raise FactorCurrentnessPersistenceError(
            "TRANSACTION_REQUIRED"
        )

    if not bool(
        getattr(
            session,
            "in_transaction",
            False,
        )
    ):
        raise FactorCurrentnessPersistenceError(
            "ACTIVE_TRANSACTION_REQUIRED"
        )

    return session


def _persisted(
    event: InteractiveFactorVerificationEvent,
    *,
    recorded_at: datetime,
) -> dict[str, object]:
    return {
        "factor_verification_reference":
            event.factor_verification_reference,
        "principal_id":
            event.principal_id,
        "session_reference":
            event.session_reference,
        "credential_revision":
            event.credential_revision,
        "authenticated_at":
            event.authenticated_at,
        "status":
            event.status.value,
        "recorded_at":
            recorded_at,
    }


def _hydrate(
    row: object,
) -> InteractiveFactorVerificationEvent:
    if not isinstance(row, dict):
        raise FactorCurrentnessPersistenceError(
            "PERSISTED_ROW_INVALID"
        )

    try:
        authenticated_at = row["authenticated_at"]
        if not isinstance(authenticated_at, datetime):
            raise TypeError("authenticated_at invalid")
        if authenticated_at.tzinfo is None:
            authenticated_at = authenticated_at.replace(tzinfo=timezone.utc)
        else:
            authenticated_at = authenticated_at.astimezone(timezone.utc)
        return InteractiveFactorVerificationEvent(
            factor_verification_reference=
                row[
                    "factor_verification_reference"
                ],
            principal_id=
                row["principal_id"],
            session_reference=
                row["session_reference"],
            credential_revision=
                row["credential_revision"],
            authenticated_at=authenticated_at,
            status=
                FactorVerificationStatus(
                    row["status"]
                ),
        )
    except (
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        raise FactorCurrentnessPersistenceError(
            "PERSISTED_ROW_INVALID"
        ) from error


class PrivilegedFactorVerificationCurrentnessRegistry:
    def __init__(
        self,
        collection: Any,
    ) -> None:
        self._collection = collection

    def ensure_indexes(
        self,
    ) -> None:
        indexes = (
            (
                [
                    (
                        "factor_verification_reference",
                        ASCENDING,
                    ),
                ],
                True,
                REFERENCE_INDEX,
            ),
            (
                [
                    (
                        "principal_id",
                        ASCENDING,
                    ),
                    (
                        "session_reference",
                        ASCENDING,
                    ),
                    (
                        "authenticated_at",
                        ASCENDING,
                    ),
                ],
                False,
                PRINCIPAL_SESSION_INDEX,
            ),
            (
                [
                    (
                        "status",
                        ASCENDING,
                    ),
                    (
                        "authenticated_at",
                        ASCENDING,
                    ),
                ],
                False,
                STATUS_INDEX,
            ),
        )

        try:
            for keys, unique, name in indexes:
                self._collection.create_index(
                    keys,
                    unique=unique,
                    name=name,
                )
        except PyMongoError as error:
            raise FactorCurrentnessPersistenceError(
                "INDEX_CREATION_FAILED"
            ) from error

    def get(
        self,
        *,
        factor_verification_reference: str,
        session: object = None,
    ) -> InteractiveFactorVerificationEvent | None:
        reference = _identifier(
            "factor_verification_reference",
            factor_verification_reference,
        )

        try:
            row = self._collection.find_one(
                {
                    "factor_verification_reference":
                        reference
                },
                session=session,
            )
        except PyMongoError as error:
            raise FactorCurrentnessPersistenceError(
                "PERSISTENCE_UNAVAILABLE"
            ) from error

        if row is None:
            return None

        event = _hydrate(row)

        if (
            event.factor_verification_reference
            != reference
        ):
            raise FactorCurrentnessPersistenceError(
                "REFERENCE_BINDING_MISMATCH"
            )

        return event

    def create_or_replay(
        self,
        event: InteractiveFactorVerificationEvent,
        *,
        recorded_at: datetime,
        session: object,
    ) -> InteractiveFactorVerificationEvent:
        tx = _active_transaction(
            session
        )

        if type(event) is not (
            InteractiveFactorVerificationEvent
        ):
            raise FactorCurrentnessRegistryError(
                "EVENT_REQUIRED"
            )

        if (
            event.status
            is not FactorVerificationStatus.VERIFIED
        ):
            raise FactorCurrentnessConflictError(
                "INITIAL_STATUS_MUST_BE_VERIFIED"
            )

        existing = self.get(
            factor_verification_reference=
                event.factor_verification_reference,
            session=tx,
        )

        if existing is not None:
            if existing == event:
                return existing

            raise FactorCurrentnessConflictError(
                "REFERENCE_COLLISION"
            )

        try:
            self._collection.insert_one(
                _persisted(
                    event,
                    recorded_at=recorded_at,
                ),
                session=tx,
            )
        except DuplicateKeyError as error:
            if error.has_error_label(
                "TransientTransactionError"
            ):
                raise

            raise FactorCurrentnessConflictError(
                "REFERENCE_COLLISION"
            ) from error

        except PyMongoError as error:
            if error.has_error_label(
                "TransientTransactionError"
            ):
                raise

            raise FactorCurrentnessPersistenceError(
                "PERSISTENCE_UNAVAILABLE"
            ) from error

        return event

    def terminate(
        self,
        *,
        factor_verification_reference: str,
        target_status: FactorVerificationStatus,
        session: object,
    ) -> InteractiveFactorVerificationEvent:
        tx = _active_transaction(
            session
        )

        if target_status not in {
            FactorVerificationStatus.REVOKED,
            FactorVerificationStatus.INVALIDATED,
        }:
            raise FactorCurrentnessConflictError(
                "TARGET_STATUS_NOT_TERMINAL"
            )

        reference = _identifier(
            "factor_verification_reference",
            factor_verification_reference,
        )

        current = self.get(
            factor_verification_reference=
                reference,
            session=tx,
        )

        if current is None:
            raise FactorCurrentnessConflictError(
                "FACTOR_EVENT_NOT_FOUND"
            )

        if (
            current.status
            is not FactorVerificationStatus.VERIFIED
        ):
            if current.status is target_status:
                return current

            raise FactorCurrentnessConflictError(
                "TERMINAL_STATUS"
            )

        try:
            result = self._collection.update_one(
                {
                    "factor_verification_reference":
                        reference,
                    "status":
                        FactorVerificationStatus
                        .VERIFIED
                        .value,
                },
                {
                    "$set": {
                        "status":
                            target_status.value
                    }
                },
                session=tx,
            )
        except PyMongoError as error:
            if error.has_error_label(
                "TransientTransactionError"
            ):
                raise

            raise FactorCurrentnessPersistenceError(
                "PERSISTENCE_UNAVAILABLE"
            ) from error

        if (
            getattr(
                result,
                "matched_count",
                0,
            )
            != 1
            or getattr(
                result,
                "modified_count",
                0,
            )
            != 1
        ):
            replay = self.get(
                factor_verification_reference=
                    reference,
                session=tx,
            )

            if (
                replay is not None
                and replay.status
                is target_status
            ):
                return replay

            raise FactorCurrentnessConflictError(
                "CURRENTNESS_CONFLICT"
            )

        updated = self.get(
            factor_verification_reference=
                reference,
            session=tx,
        )

        if (
            updated is None
            or updated.status
            is not target_status
        ):
            raise FactorCurrentnessPersistenceError(
                "TERMINAL_READBACK_FAILED"
            )

        return updated


__all__ = [
    "VERSION",
    "COLLECTION",
    "REFERENCE_INDEX",
    "PRINCIPAL_SESSION_INDEX",
    "STATUS_INDEX",
    "FactorCurrentnessRegistryError",
    "FactorCurrentnessConflictError",
    "FactorCurrentnessPersistenceError",
    "PrivilegedFactorVerificationCurrentnessRegistry",
]

# ARTIFACT: privileged_factor_verification_currentness_registry.py
# VERSION: v1.1.0-P3-R3G-C6-FACTOR-BSON-UTC-HYDRATION
# AUTHORITY BOUNDARY: Factor-verification currentness persistence only; no authentication or activation.
# TENANT POSTURE: No tenant authority.
# FAIL-CLOSED POSTURE: Exact references, active transactions, strict BSON hydration, and terminal lifecycle are mandatory.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
