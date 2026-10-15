"""
TITLE:
    WILSY OS Privileged Activation Revocation Command Evidence

VERSION:
    v1.0.1-P6-PRIVILEGED-ACTIVATION-REVOCATION-COMMAND-EVIDENCE-BSON-UTC

AUTHORITY:
    Wilsy OS IAM P6 explicit supervisory privileged-activation revocation
    command-evidence domain.

EPITOME:
    Represent one immutable, deterministic supervisory command intent to
    revoke one exact privileged activation. The evidence binds the supervising
    principal's current SYSTEM-permission assignment lineage, exact target
    activation scope, opaque revocation-reason reference, authorization time
    and idempotency identity without granting execution authority itself.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/
    privileged_activation_revocation_command_evidence.py

COLLABORATION / OWNERSHIP:
    IAM owns this evidence contract. Persistence belongs to the dedicated P6
    evidence registry. Execution belongs to the dedicated P6 command service.
    Existing privileged-activation domain and registry remain authoritative for
    activation state transition and history.

CERTIFICATION / UPDATE DATE:
    2026-10-15

CHANGELOG:
    v1.0.1-P6-PRIVILEGED-ACTIVATION-REVOCATION-COMMAND-EVIDENCE-BSON-UTC
        Accepts timezone-naive datetime only when hydrating persisted BSON,
        interpreting Mongo BSON datetime as UTC before normal domain
        validation. Fresh command composition still requires timezone-aware
        input and remains fail closed.
    v1.0.1-P6-PRIVILEGED-ACTIVATION-REVOCATION-COMMAND-EVIDENCE-BSON-UTC
        Initial immutable P6 supervisory revocation command-evidence domain.

COMPLIANCE:
    Deterministic SHA3-512 evidence identity; no raw review narrative;
    fail-closed scope validation; explicit actor/target separation; no
    authority inference from role names.

SECURITY / PRIVACY POSTURE:
    Stores opaque identifiers, assignment lineage fingerprints and opaque
    revocation-reason references only. No credentials, tokens, raw review
    narrative, payment data or financial execution truth are represented.

TENANT BOUNDARY:
    PLATFORM_SYSTEM_ROOT targets require tenant_id=None. TENANT_PRIVILEGED
    targets require one concrete tenant identifier. Target scope is immutable
    and cannot be rebound by this artifact.

AUTHORITY BOUNDARY:
    Evidence only. This module does not revoke an activation, assign a
    permission, assign a role, issue eligibility, compose assurance, create an
    activation, grant break-glass capability, expose HTTP authority or perform
    financial execution.

FINANCIAL AUTHORITY BOUNDARY:
    NONE.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_512
import json
from typing import Final, Mapping


VERSION: Final[str] = (
    "v1.0.0-P6-PRIVILEGED-ACTIVATION-"
    "REVOCATION-COMMAND-EVIDENCE"
)

SCHEMA: Final[str] = (
    "WILSY-PRIVILEGED-ACTIVATION-"
    "REVOCATION-COMMAND-EVIDENCE/V1"
)

PRIVILEGED_ACTIVATION_REVOKE_PERMISSION: Final[str] = (
    "privileged_activation:revoke"
)

PLATFORM_SYSTEM_ROOT: Final[str] = (
    "PLATFORM_SYSTEM_ROOT"
)

TENANT_PRIVILEGED: Final[str] = (
    "TENANT_PRIVILEGED"
)

_ALLOWED_TARGET_CLASSES: Final[frozenset[str]] = frozenset(
    {
        PLATFORM_SYSTEM_ROOT,
        TENANT_PRIVILEGED,
    }
)


class PrivilegedActivationRevocationCommandEvidenceError(
    ValueError
):
    """Raised when P6 revocation command evidence is invalid.

    This exception marks a fail-closed IAM boundary. Invalid identities,
    assignment lineage, target scope, self-revocation attempts, timestamps,
    reason references and idempotency identities are rejected before any
    persistence or activation-state transition can occur.
    """


def _fail(
    code: str,
) -> "NoReturn":
    raise PrivilegedActivationRevocationCommandEvidenceError(
        code
    )


try:
    from typing import NoReturn
except ImportError:  # pragma: no cover
    from typing_extensions import NoReturn


def _required_text(
    name: str,
    value: object,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        _fail(
            f"{name.upper()}_INVALID"
        )

    if not value:
        _fail(
            f"{name.upper()}_INVALID"
        )

    if value != value.strip():
        _fail(
            f"{name.upper()}_INVALID"
        )

    return value


def _fingerprint(
    name: str,
    value: object,
) -> str:
    normalized = _required_text(
        name,
        value,
    )

    if len(normalized) != 128:
        _fail(
            f"{name.upper()}_INVALID"
        )

    if normalized.lower() != normalized:
        _fail(
            f"{name.upper()}_INVALID"
        )

    try:
        int(
            normalized,
            16,
        )
    except ValueError:
        _fail(
            f"{name.upper()}_INVALID"
        )

    return normalized


def _positive_revision(
    value: object,
) -> int:
    if (
        isinstance(
            value,
            bool,
        )
        or not isinstance(
            value,
            int,
        )
        or value < 1
    ):
        _fail(
            "ACTOR_PERMISSION_ASSIGNMENT_REVISION_INVALID"
        )

    return value


def _utc_timestamp(
    name: str,
    value: object,
) -> datetime:
    if not isinstance(
        value,
        datetime,
    ):
        _fail(
            f"{name.upper()}_INVALID"
        )

    if value.tzinfo is None:
        _fail(
            f"{name.upper()}_INVALID"
        )

    normalized = value.astimezone(
        timezone.utc
    )

    if normalized.utcoffset() != timezone.utc.utcoffset(
        normalized
    ):
        _fail(
            f"{name.upper()}_INVALID"
        )

    return normalized


def _persisted_utc_timestamp(
    name: str,
    value: object,
) -> datetime:
    """Normalize Mongo BSON datetime while preserving strict command input.

    PyMongo decodes ordinary BSON UTC datetime values without ``tzinfo`` unless
    a timezone-aware codec option is configured. That transport representation
    is accepted only at persisted-document hydration and is explicitly rebound
    to UTC before passing through the normal domain timestamp validator.

    Fresh command composition continues to use ``_utc_timestamp`` directly and
    therefore rejects timezone-naive caller input.
    """

    if not isinstance(
        value,
        datetime,
    ):
        _fail(
            f"{name.upper()}_INVALID"
        )

    if value.tzinfo is None:
        value = value.replace(
            tzinfo=timezone.utc
        )

    return _utc_timestamp(
        name,
        value,
    )


def _target_scope(
    target_class: object,
    target_tenant_id: object,
) -> tuple[str, str | None]:
    normalized_class = _required_text(
        "target_class",
        target_class,
    )

    if normalized_class not in _ALLOWED_TARGET_CLASSES:
        _fail(
            "TARGET_CLASS_INVALID"
        )

    if normalized_class == PLATFORM_SYSTEM_ROOT:
        if target_tenant_id is not None:
            _fail(
                "PLATFORM_TARGET_TENANT_FORBIDDEN"
            )

        return (
            normalized_class,
            None,
        )

    if target_tenant_id is None:
        _fail(
            "TENANT_TARGET_TENANT_REQUIRED"
        )

    return (
        normalized_class,
        _required_text(
            "target_tenant_id",
            target_tenant_id,
        ),
    )


def _canonical_payload(
    *,
    actor_principal_id: str,
    actor_permission_id: str,
    actor_permission_assignment_id: str,
    actor_permission_assignment_revision: int,
    actor_permission_assignment_fingerprint: str,
    target_activation_id: str,
    target_principal_id: str,
    target_class: str,
    target_tenant_id: str | None,
    revocation_reason_reference: str,
    authorized_at: datetime,
    idempotency_key: str,
) -> Mapping[str, object]:
    return {
        "actor_permission_assignment_fingerprint": (
            actor_permission_assignment_fingerprint
        ),
        "actor_permission_assignment_id": (
            actor_permission_assignment_id
        ),
        "actor_permission_assignment_revision": (
            actor_permission_assignment_revision
        ),
        "actor_permission_id": actor_permission_id,
        "actor_principal_id": actor_principal_id,
        "authorized_at": (
            authorized_at.isoformat().replace(
                "+00:00",
                "Z",
            )
        ),
        "idempotency_key": idempotency_key,
        "revocation_reason_reference": (
            revocation_reason_reference
        ),
        "schema": SCHEMA,
        "target_activation_id": target_activation_id,
        "target_class": target_class,
        "target_principal_id": target_principal_id,
        "target_tenant_id": target_tenant_id,
        "version": VERSION,
    }


def _digest(
    payload: Mapping[str, object],
) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=True,
    ).encode(
        "utf-8"
    )

    return sha3_512(
        encoded
    ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
)
class PrivilegedActivationRevocationCommandEvidence:
    """Immutable P6 supervisory revocation command evidence.

    The value binds the supervising actor's exact current SYSTEM-permission
    assignment lineage to one exact privileged activation target and command
    intent. Construction is deterministic and self-revocation is rejected.

    This value grants no execution authority. A command service must separately
    re-resolve current permission possession, validate the target activation
    and persist this evidence through the dedicated caller-transaction-bound
    registry before invoking the existing privileged-activation revocation
    transition.
    """

    revocation_command_evidence_id: str
    actor_principal_id: str
    actor_permission_id: str
    actor_permission_assignment_id: str
    actor_permission_assignment_revision: int
    actor_permission_assignment_fingerprint: str
    target_activation_id: str
    target_principal_id: str
    target_class: str
    target_tenant_id: str | None
    revocation_reason_reference: str
    authorized_at: datetime
    idempotency_key: str
    fingerprint: str
    schema: str = SCHEMA
    version: str = VERSION

    def __post_init__(
        self,
    ) -> None:
        """Revalidate persisted or directly constructed immutable evidence."""

        actor = _required_text(
            "actor_principal_id",
            self.actor_principal_id,
        )

        permission = _required_text(
            "actor_permission_id",
            self.actor_permission_id,
        )

        if (
            permission
            != PRIVILEGED_ACTIVATION_REVOKE_PERMISSION
        ):
            _fail(
                "ACTOR_PERMISSION_ID_INVALID"
            )

        assignment_id = _required_text(
            "actor_permission_assignment_id",
            self.actor_permission_assignment_id,
        )

        assignment_revision = _positive_revision(
            self.actor_permission_assignment_revision
        )

        assignment_fingerprint = _fingerprint(
            "actor_permission_assignment_fingerprint",
            self.actor_permission_assignment_fingerprint,
        )

        activation_id = _required_text(
            "target_activation_id",
            self.target_activation_id,
        )

        target_principal = _required_text(
            "target_principal_id",
            self.target_principal_id,
        )

        if actor == target_principal:
            _fail(
                "SELF_REVOCATION_FORBIDDEN"
            )

        target_class, tenant_id = _target_scope(
            self.target_class,
            self.target_tenant_id,
        )

        reason_reference = _required_text(
            "revocation_reason_reference",
            self.revocation_reason_reference,
        )

        authorized_at = _utc_timestamp(
            "authorized_at",
            self.authorized_at,
        )

        idempotency_key = _required_text(
            "idempotency_key",
            self.idempotency_key,
        )

        payload = _canonical_payload(
            actor_principal_id=actor,
            actor_permission_id=permission,
            actor_permission_assignment_id=assignment_id,
            actor_permission_assignment_revision=assignment_revision,
            actor_permission_assignment_fingerprint=assignment_fingerprint,
            target_activation_id=activation_id,
            target_principal_id=target_principal,
            target_class=target_class,
            target_tenant_id=tenant_id,
            revocation_reason_reference=reason_reference,
            authorized_at=authorized_at,
            idempotency_key=idempotency_key,
        )

        expected_fingerprint = _digest(
            payload
        )

        expected_id = _digest(
            {
                "command_fingerprint": (
                    expected_fingerprint
                ),
                "schema": SCHEMA,
                "type": (
                    "PRIVILEGED_ACTIVATION_"
                    "REVOCATION_COMMAND"
                ),
            }
        )

        if (
            self.fingerprint
            != expected_fingerprint
        ):
            _fail(
                "FINGERPRINT_INVALID"
            )

        if (
            self.revocation_command_evidence_id
            != expected_id
        ):
            _fail(
                "REVOCATION_COMMAND_EVIDENCE_ID_INVALID"
            )

        if self.schema != SCHEMA:
            _fail(
                "SCHEMA_INVALID"
            )

        if self.version != VERSION:
            _fail(
                "VERSION_INVALID"
            )

        object.__setattr__(
            self,
            "actor_principal_id",
            actor,
        )

        object.__setattr__(
            self,
            "actor_permission_id",
            permission,
        )

        object.__setattr__(
            self,
            "actor_permission_assignment_id",
            assignment_id,
        )

        object.__setattr__(
            self,
            "actor_permission_assignment_revision",
            assignment_revision,
        )

        object.__setattr__(
            self,
            "actor_permission_assignment_fingerprint",
            assignment_fingerprint,
        )

        object.__setattr__(
            self,
            "target_activation_id",
            activation_id,
        )

        object.__setattr__(
            self,
            "target_principal_id",
            target_principal,
        )

        object.__setattr__(
            self,
            "target_class",
            target_class,
        )

        object.__setattr__(
            self,
            "target_tenant_id",
            tenant_id,
        )

        object.__setattr__(
            self,
            "revocation_reason_reference",
            reason_reference,
        )

        object.__setattr__(
            self,
            "authorized_at",
            authorized_at,
        )

        object.__setattr__(
            self,
            "idempotency_key",
            idempotency_key,
        )

    @classmethod
    def compose(
        cls,
        *,
        actor_principal_id: str,
        actor_permission_id: str,
        actor_permission_assignment_id: str,
        actor_permission_assignment_revision: int,
        actor_permission_assignment_fingerprint: str,
        target_activation_id: str,
        target_principal_id: str,
        target_class: str,
        target_tenant_id: str | None,
        revocation_reason_reference: str,
        authorized_at: datetime,
        idempotency_key: str,
    ) -> "PrivilegedActivationRevocationCommandEvidence":
        """Compose deterministic immutable P6 command evidence.

        This method validates actor and target identities, exact P6 permission,
        assignment lineage, scope, opaque reason reference, UTC authorization
        time and idempotency identity. It performs no database mutation and
        grants no revocation authority.
        """

        actor = _required_text(
            "actor_principal_id",
            actor_principal_id,
        )

        permission = _required_text(
            "actor_permission_id",
            actor_permission_id,
        )

        if (
            permission
            != PRIVILEGED_ACTIVATION_REVOKE_PERMISSION
        ):
            _fail(
                "ACTOR_PERMISSION_ID_INVALID"
            )

        assignment_id = _required_text(
            "actor_permission_assignment_id",
            actor_permission_assignment_id,
        )

        assignment_revision = _positive_revision(
            actor_permission_assignment_revision
        )

        assignment_fingerprint = _fingerprint(
            "actor_permission_assignment_fingerprint",
            actor_permission_assignment_fingerprint,
        )

        activation_id = _required_text(
            "target_activation_id",
            target_activation_id,
        )

        target_principal = _required_text(
            "target_principal_id",
            target_principal_id,
        )

        if actor == target_principal:
            _fail(
                "SELF_REVOCATION_FORBIDDEN"
            )

        normalized_class, tenant_id = _target_scope(
            target_class,
            target_tenant_id,
        )

        reason_reference = _required_text(
            "revocation_reason_reference",
            revocation_reason_reference,
        )

        normalized_authorized_at = _utc_timestamp(
            "authorized_at",
            authorized_at,
        )

        normalized_idempotency = _required_text(
            "idempotency_key",
            idempotency_key,
        )

        payload = _canonical_payload(
            actor_principal_id=actor,
            actor_permission_id=permission,
            actor_permission_assignment_id=assignment_id,
            actor_permission_assignment_revision=assignment_revision,
            actor_permission_assignment_fingerprint=assignment_fingerprint,
            target_activation_id=activation_id,
            target_principal_id=target_principal,
            target_class=normalized_class,
            target_tenant_id=tenant_id,
            revocation_reason_reference=reason_reference,
            authorized_at=normalized_authorized_at,
            idempotency_key=normalized_idempotency,
        )

        fingerprint = _digest(
            payload
        )

        evidence_id = _digest(
            {
                "command_fingerprint": fingerprint,
                "schema": SCHEMA,
                "type": (
                    "PRIVILEGED_ACTIVATION_"
                    "REVOCATION_COMMAND"
                ),
            }
        )

        return cls(
            revocation_command_evidence_id=evidence_id,
            actor_principal_id=actor,
            actor_permission_id=permission,
            actor_permission_assignment_id=assignment_id,
            actor_permission_assignment_revision=assignment_revision,
            actor_permission_assignment_fingerprint=assignment_fingerprint,
            target_activation_id=activation_id,
            target_principal_id=target_principal,
            target_class=normalized_class,
            target_tenant_id=tenant_id,
            revocation_reason_reference=reason_reference,
            authorized_at=normalized_authorized_at,
            idempotency_key=normalized_idempotency,
            fingerprint=fingerprint,
        )

    def to_document(
        self,
    ) -> dict[str, object]:
        """Return the exact persistence-safe canonical evidence document."""

        return {
            "revocation_command_evidence_id": (
                self.revocation_command_evidence_id
            ),
            "actor_principal_id": (
                self.actor_principal_id
            ),
            "actor_permission_id": (
                self.actor_permission_id
            ),
            "actor_permission_assignment_id": (
                self.actor_permission_assignment_id
            ),
            "actor_permission_assignment_revision": (
                self.actor_permission_assignment_revision
            ),
            "actor_permission_assignment_fingerprint": (
                self.actor_permission_assignment_fingerprint
            ),
            "target_activation_id": (
                self.target_activation_id
            ),
            "target_principal_id": (
                self.target_principal_id
            ),
            "target_class": (
                self.target_class
            ),
            "target_tenant_id": (
                self.target_tenant_id
            ),
            "revocation_reason_reference": (
                self.revocation_reason_reference
            ),
            "authorized_at": (
                self.authorized_at
            ),
            "idempotency_key": (
                self.idempotency_key
            ),
            "fingerprint": (
                self.fingerprint
            ),
            "schema": (
                self.schema
            ),
            "version": (
                self.version
            ),
        }

    @classmethod
    def from_document(
        cls,
        document: Mapping[str, object],
    ) -> "PrivilegedActivationRevocationCommandEvidence":
        """Hydrate and fully revalidate one persisted evidence document.

        Persisted rows are never trusted. Every field is narrowed through the
        same fail-closed validators used by composition before construction.
        The immutable constructor then recomputes and verifies deterministic
        fingerprint and command-evidence identity.
        """

        if not isinstance(
            document,
            Mapping,
        ):
            _fail(
                "PERSISTED_DOCUMENT_INVALID"
            )

        try:
            evidence_id = _required_text(
                "revocation_command_evidence_id",
                document[
                    "revocation_command_evidence_id"
                ],
            )

            actor = _required_text(
                "actor_principal_id",
                document[
                    "actor_principal_id"
                ],
            )

            permission = _required_text(
                "actor_permission_id",
                document[
                    "actor_permission_id"
                ],
            )

            assignment_id = _required_text(
                "actor_permission_assignment_id",
                document[
                    "actor_permission_assignment_id"
                ],
            )

            assignment_revision = _positive_revision(
                document[
                    "actor_permission_assignment_revision"
                ]
            )

            assignment_fingerprint = _fingerprint(
                "actor_permission_assignment_fingerprint",
                document[
                    "actor_permission_assignment_fingerprint"
                ],
            )

            activation_id = _required_text(
                "target_activation_id",
                document[
                    "target_activation_id"
                ],
            )

            target_principal = _required_text(
                "target_principal_id",
                document[
                    "target_principal_id"
                ],
            )

            target_class, target_tenant_id = _target_scope(
                document[
                    "target_class"
                ],
                document[
                    "target_tenant_id"
                ],
            )

            reason_reference = _required_text(
                "revocation_reason_reference",
                document[
                    "revocation_reason_reference"
                ],
            )

            authorized_at = _persisted_utc_timestamp(
                "authorized_at",
                document[
                    "authorized_at"
                ],
            )

            idempotency_key = _required_text(
                "idempotency_key",
                document[
                    "idempotency_key"
                ],
            )

            fingerprint = _fingerprint(
                "fingerprint",
                document[
                    "fingerprint"
                ],
            )

            schema = _required_text(
                "schema",
                document[
                    "schema"
                ],
            )

            version = _required_text(
                "version",
                document[
                    "version"
                ],
            )

        except KeyError as exc:
            raise PrivilegedActivationRevocationCommandEvidenceError(
                "PERSISTED_DOCUMENT_INVALID"
            ) from exc

        return cls(
            revocation_command_evidence_id=evidence_id,
            actor_principal_id=actor,
            actor_permission_id=permission,
            actor_permission_assignment_id=assignment_id,
            actor_permission_assignment_revision=assignment_revision,
            actor_permission_assignment_fingerprint=(
                assignment_fingerprint
            ),
            target_activation_id=activation_id,
            target_principal_id=target_principal,
            target_class=target_class,
            target_tenant_id=target_tenant_id,
            revocation_reason_reference=reason_reference,
            authorized_at=authorized_at,
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
            schema=schema,
            version=version,
        )


__all__ = [
    "VERSION",
    "SCHEMA",
    "PRIVILEGED_ACTIVATION_REVOKE_PERMISSION",
    "PLATFORM_SYSTEM_ROOT",
    "TENANT_PRIVILEGED",
    "PrivilegedActivationRevocationCommandEvidenceError",
    "PrivilegedActivationRevocationCommandEvidence",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: privileged_activation_revocation_command_evidence.py
# VERSION: v1.0.1-P6-PRIVILEGED-ACTIVATION-REVOCATION-COMMAND-EVIDENCE-BSON-UTC
# AUTHORITY BOUNDARY: IMMUTABLE P6 COMMAND EVIDENCE ONLY; NO EXECUTION AUTHORITY
# TENANT POSTURE: EXACT PLATFORM OR TENANT TARGET SCOPE; REBINDING FORBIDDEN
# FAIL-CLOSED POSTURE: DETERMINISTIC IDENTITY; CORRUPTION AND SELF-REVOCATION REJECTED
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
