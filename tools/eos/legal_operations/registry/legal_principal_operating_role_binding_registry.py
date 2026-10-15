"""
TITLE: WILSY OS Legal Principal Operating Role Binding Registry
VERSION: v1.0.1-CX27-R5A-R2-LEGAL-PRINCIPAL-OPERATING-ROLE-BINDING-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations.
CLASSIFICATION: EMERGING CANONICAL
EPITOME: Immutable exact-tenant append-only revision persistence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_principal_operating_role_binding_registry.py
COLLABORATION / OWNERSHIP: CX27-D owns durable occupancy history and effective-window projections only; callers own transaction lifecycle and all access authority remains external.
CERTIFICATION / UPDATE DATE: 2026-10-15
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Stores opaque tenant, principal, role, evidence, window, lineage, and fingerprint facts; no credentials, permissions, tokens, or financial truth.
TENANT BOUNDARY: Every durable predicate begins with exact non-pseudo tenant_id.
AUTHORITY BOUNDARY: Persistence and occupancy projection only; no authentication, IAM, matter, workflow, assignment, supervision, entitlement, or execution authority.
TRANSACTION OWNERSHIP: Caller-owned active Mongo transaction required.
CURRENTNESS: Derived from immutable revision history; no mutable pointer.
TTL: FORBIDDEN.
UPDATE / REPLACE / DELETE: FORBIDDEN.
IAM AUTHORITY: NONE.
BUSINESS-ROLE AUTHORITY: NONE.
MATTER AUTHORITY: NONE.
WORK-ASSIGNMENT AUTHORITY: NONE.
SUPERVISION AUTHORITY: NONE.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
CHANGELOG: v1.0.1 completes sovereign metadata without changing immutable registry semantics.
"""


from __future__ import annotations

from datetime import datetime, timezone
import hmac
from typing import Any, Final, NoReturn

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError


from tools.eos.legal_operations.domain.legal_principal_operating_role_binding import LegalPrincipalOperatingRoleBinding


VERSION: Final[str] = "v1.0.1-CX27-R5A-R2-LEGAL-PRINCIPAL-OPERATING-ROLE-BINDING-REGISTRY"

COLLECTION_NAME: Final[str] = (
    "legal_principal_operating_role_bindings"
)

IDENTITY_INDEX_NAME: Final[str] = (
    "legal_principal_operating_role_bindings_identity_unique"
)

FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_principal_operating_role_bindings_fingerprint_unique"
)

HISTORY_INDEX_NAME: Final[str] = (
    "legal_principal_operating_role_bindings_history"
)

CURRENTNESS_INDEX_NAME: Final[str] = (
    "legal_principal_operating_role_bindings_currentness"
)



class RegistryError(RuntimeError):
    """Base fail-closed durable-registry error."""


class RegistryTransactionRequiredError(RegistryError):
    """Caller failed to provide an active Mongo transaction."""


class RegistryConflictError(RegistryError):
    """Immutable identity, replay, fingerprint, or lineage conflicts."""


class RegistryNotFoundError(RegistryError):
    """Exact tenant-scoped durable truth does not exist."""


class RegistryPersistedRecordInvalidError(RegistryError):
    """Persisted data failed canonical hydration or scope correlation."""


def _fail(
    exc: type[RegistryError],
    code: str,
) -> NoReturn:
    raise exc(code)


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        _fail(
            RegistryConflictError,
            f"CX27_R5A_R2_{name.upper()}_INVALID",
        )

    return value


def _revision(
    name: str,
    value: object,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
    ):
        _fail(
            RegistryConflictError,
            f"CX27_R5A_R2_{name.upper()}_INVALID",
        )

    return value


def _moment(value: object) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(
            RegistryConflictError,
            "CX27_R5A_R2_AT_INVALID",
        )

    return value.astimezone(timezone.utc)


def _transaction(session: Any) -> Any:
    if (
        session is None
        or not bool(
            getattr(
                session,
                "in_transaction",
                False,
            )
        )
    ):
        _fail(
            RegistryTransactionRequiredError,
            "CX27_R5A_R2_ACTIVE_CALLER_TRANSACTION_REQUIRED",
        )

    return session


def _without_id(
    raw: Any,
) -> dict[str, object]:
    if not isinstance(raw, dict):
        _fail(
            RegistryPersistedRecordInvalidError,
            "CX27_R5A_R2_PERSISTED_RECORD_INVALID",
        )

    return {
        str(key): value
        for key, value in raw.items()
        if key != "_id"
    }



class LegalPrincipalOperatingRoleBindingRegistry:
    """Own immutable durable history for LegalPrincipalOperatingRoleBinding, and nothing else."""

    def __init__(
        self,
        collection: Any,
    ) -> None:
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create exact unique/read indexes and never create TTL."""
        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("principal_operating_role_binding_id", ASCENDING),
                ("binding_revision", ASCENDING),
            ],
            unique=True,
            name="legal_principal_operating_role_bindings_identity_unique",
        )
        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("fingerprint", ASCENDING),
            ],
            unique=True,
            name="legal_principal_operating_role_bindings_fingerprint_unique",
        )
        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("principal_operating_role_binding_id", ASCENDING),
                ("binding_revision", ASCENDING),
            ],
            unique=False,
            name="legal_principal_operating_role_bindings_history",
        )
        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("principal_operating_role_binding_id", ASCENDING),
                ("effective_from", ASCENDING),
                ("binding_revision", ASCENDING),
            ],
            unique=False,
            name="legal_principal_operating_role_bindings_currentness",
        )
        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("principal_id", ASCENDING),
                ("effective_from", ASCENDING),
                ("binding_revision", ASCENDING),
            ],
            unique=False,
            name="legal_principal_operating_role_principal_history",
        )
        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("operating_role_id", ASCENDING),
                ("operating_role_revision", ASCENDING),
                ("principal_id", ASCENDING),
                ("binding_revision", ASCENDING),
            ],
            unique=False,
            name="legal_principal_operating_role_role_history",
        )

    @staticmethod
    def _hydrate(
        raw: Any,
    ) -> LegalPrincipalOperatingRoleBinding:
        try:
            return LegalPrincipalOperatingRoleBinding.from_dict(
                _without_id(raw)
            )
        except Exception as exc:
            raise RegistryPersistedRecordInvalidError(
                "CX27_R5A_R2_PERSISTED_RECORD_INVALID"
            ) from exc

    @staticmethod
    def _equal(
        left: LegalPrincipalOperatingRoleBinding,
        right: LegalPrincipalOperatingRoleBinding,
    ) -> bool:
        return (
            hmac.compare_digest(
                left.fingerprint,
                right.fingerprint,
            )
            and left == right
        )

    @staticmethod
    def _validate_history(
        values: tuple[
            LegalPrincipalOperatingRoleBinding,
            ...
        ],
    ) -> tuple[
        LegalPrincipalOperatingRoleBinding,
        ...
    ]:
        """Reject gaps, family drift, bad predecessor links and ambiguity."""
        previous: LegalPrincipalOperatingRoleBinding | None = None

        for expected_revision, item in enumerate(
            values,
            1,
        ):
            if (
                item.binding_revision
                != expected_revision
            ):
                _fail(
                    RegistryConflictError,
                    "CX27_R5A_R2_REVISION_GAP",
                )

            if previous is None:
                if (
                    item.supersedes_fingerprint
                    is not None
                ):
                    _fail(
                        RegistryConflictError,
                        "CX27_R5A_R2_FIRST_REVISION_SUPERSEDES",
                    )
            else:
                if not (item.principal_operating_role_binding_id == previous.principal_operating_role_binding_id and item.principal_id == previous.principal_id and item.operating_role_id == previous.operating_role_id):
                    _fail(
                        RegistryConflictError,
                        "CX27_R5A_R2_REVISION_FAMILY_CHANGED",
                    )

                if (
                    item.supersedes_fingerprint
                    != previous.fingerprint
                ):
                    _fail(
                        RegistryConflictError,
                        "CX27_R5A_R2_PREDECESSOR_FINGERPRINT_MISMATCH",
                    )

            previous = item

        return values

    def get_revision(
        self,
        tenant_id: str,
        identity: str,
        revision: int,
        *,
        session: Any,
    ) -> LegalPrincipalOperatingRoleBinding:
        """Return one exact tenant-scoped immutable revision."""
        tx = _transaction(session)
        tenant = _text(
            "tenant_id",
            tenant_id,
        )
        durable_id = _text(
            "principal_operating_role_binding_id",
            identity,
        )
        rev = _revision(
            "binding_revision",
            revision,
        )

        raw = self._collection.find_one(
            {
                "tenant_id": tenant,
                "principal_operating_role_binding_id": durable_id,
                "binding_revision": rev,
            },
            session=tx,
        )

        if raw is None:
            _fail(
                RegistryNotFoundError,
                "CX27_R5A_R2_REVISION_NOT_FOUND",
            )

        value = self._hydrate(raw)

        if (
            value.tenant_id != tenant
            or value.principal_operating_role_binding_id
            != durable_id
            or value.binding_revision
            != rev
        ):
            _fail(
                RegistryPersistedRecordInvalidError,
                "CX27_R5A_R2_PERSISTED_SCOPE_MISMATCH",
            )

        return value

    def get_history_if_any(
        self,
        tenant_id: str,
        identity: str,
        *,
        session: Any,
    ) -> tuple[
        LegalPrincipalOperatingRoleBinding,
        ...
    ]:
        """Return strict immutable lineage or an empty tuple."""
        tx = _transaction(session)
        tenant = _text(
            "tenant_id",
            tenant_id,
        )
        durable_id = _text(
            "principal_operating_role_binding_id",
            identity,
        )

        rows = tuple(
            self._collection.find(
                {
                    "tenant_id": tenant,
                    "principal_operating_role_binding_id": durable_id,
                },
                session=tx,
            ).sort(
                "binding_revision",
                ASCENDING,
            )
        )

        values = tuple(
            self._hydrate(raw)
            for raw in rows
        )

        for value in values:
            if (
                value.tenant_id != tenant
                or value.principal_operating_role_binding_id
                != durable_id
            ):
                _fail(
                    RegistryPersistedRecordInvalidError,
                    "CX27_R5A_R2_PERSISTED_SCOPE_MISMATCH",
                )

        return self._validate_history(
            values
        )

    def get_history(
        self,
        tenant_id: str,
        identity: str,
        *,
        session: Any,
    ) -> tuple[
        LegalPrincipalOperatingRoleBinding,
        ...
    ]:
        """Return strict immutable history and reject absence."""
        values = self.get_history_if_any(
            tenant_id,
            identity,
            session=session,
        )

        if not values:
            _fail(
                RegistryNotFoundError,
                "CX27_R5A_R2_HISTORY_NOT_FOUND",
            )

        return values

    def persist_revision(
        self,
        value: LegalPrincipalOperatingRoleBinding,
        *,
        session: Any,
    ) -> LegalPrincipalOperatingRoleBinding:
        """Append exact next immutable revision or return exact replay."""
        tx = _transaction(session)

        if not isinstance(
            value,
            LegalPrincipalOperatingRoleBinding,
        ):
            _fail(
                RegistryConflictError,
                "CX27_R5A_R2_DOMAIN_VALUE_REQUIRED",
            )

        identity_query = {
            "tenant_id": value.tenant_id,
            "principal_operating_role_binding_id":
                value.principal_operating_role_binding_id,
            "binding_revision":
                value.binding_revision,
        }

        existing_raw = (
            self._collection.find_one(
                identity_query,
                session=tx,
            )
        )

        if existing_raw is not None:
            existing = self._hydrate(
                existing_raw
            )

            if self._equal(
                existing,
                value,
            ):
                return existing

            _fail(
                RegistryConflictError,
                "CX27_R5A_R2_DIVERGENT_REPLAY",
            )

        fingerprint_raw = (
            self._collection.find_one(
                {
                    "tenant_id":
                        value.tenant_id,
                    "fingerprint":
                        value.fingerprint,
                },
                session=tx,
            )
        )

        if fingerprint_raw is not None:
            collision = self._hydrate(
                fingerprint_raw
            )

            if not self._equal(
                collision,
                value,
            ):
                _fail(
                    RegistryConflictError,
                    "CX27_R5A_R2_FINGERPRINT_COLLISION",
                )

        history = self.get_history_if_any(
            value.tenant_id,
            value.principal_operating_role_binding_id,
            session=tx,
        )

        if (
            value.binding_revision
            != len(history) + 1
        ):
            _fail(
                RegistryConflictError,
                "CX27_R5A_R2_REVISION_SEQUENCE_CONFLICT",
            )

        if history:
            predecessor = history[-1]

            if not (value.principal_operating_role_binding_id == predecessor.principal_operating_role_binding_id and value.principal_id == predecessor.principal_id and value.operating_role_id == predecessor.operating_role_id):
                _fail(
                    RegistryConflictError,
                    "CX27_R5A_R2_REVISION_FAMILY_CHANGED",
                )

            if (
                value.supersedes_fingerprint
                != predecessor.fingerprint
            ):
                _fail(
                    RegistryConflictError,
                    "CX27_R5A_R2_PREDECESSOR_FINGERPRINT_MISMATCH",
                )

            if (
                value.effective_from
                < predecessor.effective_from
            ):
                _fail(
                    RegistryConflictError,
                    "CX27_R5A_R2_EFFECTIVE_TIME_REGRESSION",
                )

        elif (
            value.supersedes_fingerprint
            is not None
        ):
            _fail(
                RegistryConflictError,
                "CX27_R5A_R2_FIRST_REVISION_SUPERSEDES",
            )

        try:
            self._collection.insert_one(
                value.to_dict(),
                session=tx,
            )
        except DuplicateKeyError:
            raced_raw = (
                self._collection.find_one(
                    identity_query,
                    session=tx,
                )
            )

            if raced_raw is not None:
                raced = self._hydrate(
                    raced_raw
                )

                if self._equal(
                    raced,
                    value,
                ):
                    return raced

            _fail(
                RegistryConflictError,
                "CX27_R5A_R2_COMPETING_REVISION_CONFLICT",
            )

        return self.get_revision(
            value.tenant_id,
            value.principal_operating_role_binding_id,
            value.binding_revision,
            session=tx,
        )

    def resolve_current(
        self,
        tenant_id: str,
        identity: str,
        at: datetime,
        *,
        session: Any,
    ) -> LegalPrincipalOperatingRoleBinding | None:
        """Derive current truth from immutable history; store no pointer."""
        moment = _moment(at)

        history = self.get_history_if_any(
            tenant_id,
            identity,
            session=session,
        )

        applicable = tuple(
            value
            for value in history
            if value.effective_from <= moment
        )

        if not applicable:
            return None

        latest = applicable[-1]

        if (
            latest.effective_until
            is not None
            and moment
            >= latest.effective_until
        ):
            return None

        return latest

    def list_current_for_principal(
        self,
        tenant_id: str,
        principal_id: str,
        at: datetime,
        *,
        session: Any,
    ) -> tuple[LegalPrincipalOperatingRoleBinding, ...]:
        """Return current operating-role occupancy for one principal."""
        tx = _transaction(session)
        tenant = _text(
            "tenant_id",
            tenant_id,
        )
        principal = _text(
            "principal_id",
            principal_id,
        )
        moment = _moment(at)

        rows = tuple(
            self._collection.find(
                {
                    "tenant_id": tenant,
                    "principal_id": principal,
                },
                session=tx,
            )
        )

        families: dict[
            str,
            list[LegalPrincipalOperatingRoleBinding],
        ] = {}

        for raw in rows:
            item = self._hydrate(raw)

            if (
                item.tenant_id != tenant
                or item.principal_id != principal
            ):
                _fail(
                    RegistryPersistedRecordInvalidError,
                    "CX27_R5A_R2_PERSISTED_SCOPE_MISMATCH",
                )

            families.setdefault(
                item.principal_operating_role_binding_id,
                [],
            ).append(item)

        current: list[LegalPrincipalOperatingRoleBinding] = []

        for family in families.values():
            ordered = self._validate_history(
                tuple(
                    sorted(
                        family,
                        key=lambda item: item.binding_revision,
                    )
                )
            )

            applicable = tuple(
                item
                for item in ordered
                if item.effective_from <= moment
            )

            if not applicable:
                continue

            latest = applicable[-1]

            if (
                latest.effective_until is None
                or moment < latest.effective_until
            ):
                current.append(latest)

        return tuple(
            sorted(
                current,
                key=lambda item: (
                    item.operating_role_id,
                    item.principal_operating_role_binding_id,
                ),
            )
        )



__all__ = [
    "VERSION",
    "COLLECTION_NAME",
    "IDENTITY_INDEX_NAME",
    "FINGERPRINT_INDEX_NAME",
    "HISTORY_INDEX_NAME",
    "CURRENTNESS_INDEX_NAME",
    "LegalPrincipalOperatingRoleBindingRegistry",
    "RegistryError",
    "RegistryTransactionRequiredError",
    "RegistryConflictError",
    "RegistryNotFoundError",
    "RegistryPersistedRecordInvalidError",
]

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: legal_principal_operating_role_binding_registry.py
# VERSION: v1.0.1-CX27-R5A-R2-LEGAL-PRINCIPAL-OPERATING-ROLE-BINDING-REGISTRY
# APPEND-ONLY IMMUTABLE HISTORY: YES
# CALLER-OWNED ACTIVE TRANSACTION REQUIRED: YES
# MUTABLE CURRENT POINTER: NONE
# TTL / UPDATE / REPLACE / DELETE AUTHORITY: NONE
# IAM / BUSINESS-ROLE / MATTER AUTHORITY: NONE
# TENANT POSTURE: exact tenant-first reads, writes, replay, and projections
# FAIL-CLOSED POSTURE: invalid input, transaction absence, conflict, corruption, ambiguity, overlap, race, and outage reject
# WORK-ASSIGNMENT / SUPERVISION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
