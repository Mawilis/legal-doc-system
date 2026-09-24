"""WILSY OS durable tenant branding profile/current-selection registry.

TITLE: Tenant Branding Profile Registry
VERSION: v1.0.0-D21B4B-TENANT-BRANDING-PROFILE-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persist immutable D21B3 approved profiles and D21B4A selection history,
         and maintain one explicit tenant-scoped current-selection pointer with
         strict hydration, exact replay and caller-owned transaction CAS.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/tenant_branding_profile_registry.py
COLLABORATION / OWNERSHIP: D21B3 owns approved profile evidence; D21B4A owns
                            immutable selection facts; this registry owns only
                            durable profile/selection persistence and explicit
                            currentness. Callers own Mongo sessions/transactions.
                            Runtime projection must separately re-read the current
                            D21B2 entitlement before presenting any branding.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-D21B4B-TENANT-BRANDING-PROFILE-REGISTRY establishes strict
           tenant-scoped immutable profile and selection persistence, explicit
           current-pointer correlation, exact-current replay, deterministic
           uniqueness indexes, and compare-and-set advancement under an already
           active caller-owned Mongo transaction. Historical latest-row inference
           and browser/asset resolution are prohibited.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Persists only D21B3/D21B4A evidence and compact
                             currentness metadata. No asset bytes, raw URLs,
                             filesystem paths, base64, credentials, provider
                             clients, browser state or legacy bank/tax material.
TENANT BOUNDARY: Every profile, selection, current-pointer read/write/replay and
                 CAS predicate contains tenant_id. Foreign records are
                 indistinguishable from absence.
AUTHORITY BOUNDARY: Durable approved-profile persistence, historical selection
                    persistence and explicit current-pointer CAS only. Current
                    pointer does not prove D21B2 remains ACTIVE and creates no
                    browser, asset-resolution, IAM or legal authority.
FINANCIAL AUTHORITY BOUNDARY: No price, bank, tax, invoice, charge, payment,
                               execution or settlement truth. Kennel EOS remains
                               the exclusive financial execution authority.
TRANSACTION BOUNDARY: Every read/write operation requires an already-active
                      caller-owned Mongo session/transaction. This registry never
                      starts, commits, aborts, retries or closes transactions.
FAIL-CLOSED DECLARATION: Missing transactions, schema drift, corruption,
                         cross-tenant access, profile/selection divergence,
                         missing current pointers, provenance mismatch, duplicate
                         pointers, CAS races and persistence outages reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
import re
from typing import Any, Final, NoReturn, cast

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.tenant_branding_profile import (
    PROFILE_FIELDS,
    TenantBrandingProfile,
    TenantBrandingProfileError,
)
from tools.eos.saas.domain.tenant_branding_profile_selection import (
    SELECTION_FIELDS,
    TenantBrandingProfileSelection,
    TenantBrandingProfileSelectionError,
)


VERSION: Final[str] = "v1.0.0-D21B4B-TENANT-BRANDING-PROFILE-REGISTRY"
PROFILE_RECORD_SCHEMA: Final[str] = "WILSY-TENANT-BRANDING-PROFILE-RECORD/V1"
SELECTION_RECORD_SCHEMA: Final[str] = (
    "WILSY-TENANT-BRANDING-PROFILE-SELECTION-RECORD/V1"
)
CURRENT_SCHEMA: Final[str] = "WILSY-TENANT-BRANDING-PROFILE-CURRENT/V1"

PROFILE_COLLECTION: Final[str] = "tenant_branding_profiles"
SELECTION_COLLECTION: Final[str] = "tenant_branding_profile_selections"
CURRENT_COLLECTION: Final[str] = "tenant_branding_profile_current"

PROFILE_ID_INDEX_NAME: Final[str] = "tenant_branding_profile_tenant_profile_unique"
PROFILE_FINGERPRINT_INDEX_NAME: Final[str] = (
    "tenant_branding_profile_tenant_fingerprint_unique"
)
SELECTION_ID_INDEX_NAME: Final[str] = (
    "tenant_branding_selection_tenant_selection_unique"
)
SELECTION_REVISION_INDEX_NAME: Final[str] = (
    "tenant_branding_selection_tenant_revision_unique"
)
CURRENT_TENANT_INDEX_NAME: Final[str] = "tenant_branding_current_tenant_unique"

WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_SHA3: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class TenantBrandingProfileRegistryError(RuntimeError):
    """Base fail-closed D21B4B durable-registry error with stable code."""

    default_code = "D21B4B_REGISTRY_ERROR"

    def __init__(self, code: str | None = None) -> None:
        """Create one governed registry failure without inventing durable truth."""
        self.code = code or self.default_code
        super().__init__(self.code)


class TenantBrandingProfileRegistryInputError(TenantBrandingProfileRegistryError):
    """Caller input or collection dependency is invalid."""

    default_code = "D21B4B_INPUT_INVALID"


class TenantBrandingProfileRegistryTransactionRequiredError(
    TenantBrandingProfileRegistryError
):
    """An already-active caller-owned Mongo transaction is required."""

    default_code = "D21B4B_ACTIVE_TRANSACTION_REQUIRED"


class TenantBrandingProfileRegistryPersistedRecordInvalidError(
    TenantBrandingProfileRegistryError
):
    """Persisted profile, selection or pointer failed strict hydration."""

    default_code = "D21B4B_PERSISTED_RECORD_INVALID"


class TenantBrandingProfileRegistryProfileNotFoundError(
    TenantBrandingProfileRegistryError
):
    """Exact tenant-scoped approved profile is absent."""

    default_code = "D21B4B_PROFILE_NOT_FOUND"


class TenantBrandingProfileRegistrySelectionNotFoundError(
    TenantBrandingProfileRegistryError
):
    """Exact tenant-scoped selection fact is absent."""

    default_code = "D21B4B_SELECTION_NOT_FOUND"


class TenantBrandingProfileRegistryCurrentPointerMissingError(
    TenantBrandingProfileRegistryError
):
    """No explicit current branding selection exists for the tenant."""

    default_code = "D21B4B_CURRENT_POINTER_MISSING"


class TenantBrandingProfileRegistryMultipleCurrentPointerError(
    TenantBrandingProfileRegistryPersistedRecordInvalidError
):
    """More than one current pointer exists for one tenant."""

    default_code = "D21B4B_MULTIPLE_CURRENT_POINTERS"


class TenantBrandingProfileRegistryProfileConflictError(
    TenantBrandingProfileRegistryError
):
    """One tenant/profile identity is already bound to divergent evidence."""

    default_code = "D21B4B_PROFILE_CONFLICT"


class TenantBrandingProfileRegistrySelectionConflictError(
    TenantBrandingProfileRegistryError
):
    """Selection identity/revision is already bound to divergent evidence."""

    default_code = "D21B4B_SELECTION_CONFLICT"


class TenantBrandingProfileRegistryCurrentPointerConflictError(
    TenantBrandingProfileRegistryError
):
    """Selection lineage does not match durable explicit currentness."""

    default_code = "D21B4B_CURRENT_POINTER_CONFLICT"


class TenantBrandingProfileRegistryCorrelationError(
    TenantBrandingProfileRegistryPersistedRecordInvalidError
):
    """Pointer, selection and approved-profile provenance do not correlate."""

    default_code = "D21B4B_CURRENT_CORRELATION_INVALID"


class TenantBrandingProfileRegistryRetryRequiredError(
    TenantBrandingProfileRegistryError
):
    """A race requires the caller to abort and restart the whole transaction."""

    default_code = "D21B4B_WHOLE_TRANSACTION_RETRY_REQUIRED"


class TenantBrandingProfileRegistryPersistenceUnavailableError(
    TenantBrandingProfileRegistryError
):
    """Mongo persistence or cursor access is unavailable."""

    default_code = "D21B4B_PERSISTENCE_UNAVAILABLE"


class TenantBrandingProfilePersistenceOutcome(StrEnum):
    """Durable operation result; neither value grants browser presentation."""

    CREATED = "CREATED"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"


def _raise(
    error_type: type[TenantBrandingProfileRegistryError],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one stable registry error while preserving the technical cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    """Validate one bounded tenant/profile/selection identity exactly."""
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _raise(
            TenantBrandingProfileRegistryInputError,
            f"D21B4B_{name.upper()}_INVALID",
        )
    return cast(str, value)


def _tenant(value: object) -> str:
    """Validate a real tenant identity and reject pseudo-tenant scopes."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _raise(
            TenantBrandingProfileRegistryInputError,
            "D21B4B_TENANT_INVALID",
        )
    return tenant


def _fingerprint(name: str, value: object) -> str:
    """Require one canonical lowercase SHA3-512-shaped fingerprint."""
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _raise(
            TenantBrandingProfileRegistryInputError,
            f"D21B4B_{name.upper()}_INVALID",
        )
    return cast(str, value)


def _positive_int(name: str, value: object) -> int:
    """Require one positive non-boolean revision integer."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        _raise(
            TenantBrandingProfileRegistryInputError,
            f"D21B4B_{name.upper()}_INVALID",
        )
    return value


def _sha3(value: object) -> str:
    """Return SHA3-512 over deterministic canonical JSON."""
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _target(collection: Any) -> Any:
    """Apply majority/journal durability when the collection supports options."""
    try:
        return collection.with_options(
            write_concern=WRITE_CONCERN,
            read_concern=READ_CONCERN,
        )
    except AttributeError:
        return collection


def _collection(value: Any, label: str) -> Any:
    """Require one collection-like dependency without creating a Mongo client."""
    if value is None:
        _raise(
            TenantBrandingProfileRegistryInputError,
            f"D21B4B_{label}_COLLECTION_REQUIRED",
        )
    return _target(value)


def _active_transaction(session: Any) -> Any:
    """Require an active caller transaction; registry owns no lifecycle."""
    if session is None:
        _raise(TenantBrandingProfileRegistryTransactionRequiredError)
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _raise(TenantBrandingProfileRegistryTransactionRequiredError)
    return session


def _rows(
    collection: Any,
    query: Mapping[str, object],
    *,
    session: Any,
) -> list[Mapping[str, Any]]:
    """Read at most two rows so impossible uniqueness violations surface."""
    target = _collection(collection, "QUERY")
    try:
        if hasattr(target, "find"):
            cursor = target.find(dict(query), session=session)
            if hasattr(cursor, "limit"):
                cursor = cursor.limit(2)
            return [cast(Mapping[str, Any], row) for row in cursor]
        if hasattr(target, "find_one"):
            row = target.find_one(dict(query), session=session)
            return [] if row is None else [cast(Mapping[str, Any], row)]
    except PyMongoError as error:
        _raise(
            TenantBrandingProfileRegistryPersistenceUnavailableError,
            cause=error,
        )
    _raise(
        TenantBrandingProfileRegistryInputError,
        "D21B4B_COLLECTION_INTERFACE_INVALID",
    )


_PROFILE_RECORD_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "version",
        "entity_type",
        "tenant_id",
        "profile_id",
        "profile_fingerprint",
        "evidence_identity",
        "profile_payload",
    }
)
_SELECTION_RECORD_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "version",
        "entity_type",
        "tenant_id",
        "selection_id",
        "selection_revision",
        "selection_fingerprint",
        "evidence_identity",
        "selection_payload",
    }
)


def _profile_evidence_identity(profile: TenantBrandingProfile) -> str:
    """Derive immutable registry identity for one approved profile record."""
    return _sha3(
        {
            "schema": PROFILE_RECORD_SCHEMA,
            "version": VERSION,
            "tenant_id": profile.tenant_id,
            "profile_id": profile.profile_id,
            "profile_fingerprint": profile.fingerprint,
        }
    )


def _selection_evidence_identity(
    selection: TenantBrandingProfileSelection,
) -> str:
    """Derive immutable registry identity for one historical selection record."""
    return _sha3(
        {
            "schema": SELECTION_RECORD_SCHEMA,
            "version": VERSION,
            "tenant_id": selection.tenant_id,
            "selection_id": selection.selection_id,
            "selection_revision": selection.selection_revision,
            "selection_fingerprint": selection.fingerprint,
        }
    )


def _profile_record(profile: TenantBrandingProfile) -> dict[str, object]:
    """Build one immutable strict approved-profile persistence record."""
    return {
        "schema": PROFILE_RECORD_SCHEMA,
        "version": VERSION,
        "entity_type": "TenantBrandingProfileRecord",
        "tenant_id": profile.tenant_id,
        "profile_id": profile.profile_id,
        "profile_fingerprint": profile.fingerprint,
        "evidence_identity": _profile_evidence_identity(profile),
        "profile_payload": profile.to_dict(),
    }


def _selection_record(
    selection: TenantBrandingProfileSelection,
) -> dict[str, object]:
    """Build one immutable strict profile-selection persistence record."""
    return {
        "schema": SELECTION_RECORD_SCHEMA,
        "version": VERSION,
        "entity_type": "TenantBrandingProfileSelectionRecord",
        "tenant_id": selection.tenant_id,
        "selection_id": selection.selection_id,
        "selection_revision": selection.selection_revision,
        "selection_fingerprint": selection.fingerprint,
        "evidence_identity": _selection_evidence_identity(selection),
        "selection_payload": selection.to_dict(),
    }


def _hydrate_profile(document: Mapping[str, Any]) -> TenantBrandingProfile:
    """Strictly hydrate and verify one persisted approved profile."""
    if not isinstance(document, Mapping):
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_PROFILE_RECORD_INVALID",
        )
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != _PROFILE_RECORD_FIELDS:
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_PROFILE_RECORD_SCHEMA_INVALID",
        )
    if (
        raw.get("schema") != PROFILE_RECORD_SCHEMA
        or raw.get("version") != VERSION
        or raw.get("entity_type") != "TenantBrandingProfileRecord"
    ):
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_PROFILE_RECORD_VERSION_UNSUPPORTED",
        )
    payload = raw.get("profile_payload")
    if not isinstance(payload, Mapping) or set(payload) != set(PROFILE_FIELDS):
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_PROFILE_PAYLOAD_SCHEMA_INVALID",
        )
    try:
        profile = TenantBrandingProfile.from_dict(
            cast(Mapping[str, object], payload)
        )
    except (TypeError, ValueError, TenantBrandingProfileError) as error:
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_PROFILE_PAYLOAD_INVALID",
            error,
        )
    expected_identity = _profile_evidence_identity(profile)
    if (
        raw.get("tenant_id") != profile.tenant_id
        or raw.get("profile_id") != profile.profile_id
        or raw.get("profile_fingerprint") != profile.fingerprint
        or raw.get("evidence_identity") != expected_identity
    ):
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_PROFILE_RECORD_CORRELATION_INVALID",
        )
    return profile


def _hydrate_selection(
    document: Mapping[str, Any],
) -> TenantBrandingProfileSelection:
    """Strictly hydrate and verify one persisted historical selection."""
    if not isinstance(document, Mapping):
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_SELECTION_RECORD_INVALID",
        )
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != _SELECTION_RECORD_FIELDS:
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_SELECTION_RECORD_SCHEMA_INVALID",
        )
    if (
        raw.get("schema") != SELECTION_RECORD_SCHEMA
        or raw.get("version") != VERSION
        or raw.get("entity_type") != "TenantBrandingProfileSelectionRecord"
    ):
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_SELECTION_RECORD_VERSION_UNSUPPORTED",
        )
    payload = raw.get("selection_payload")
    if not isinstance(payload, Mapping) or set(payload) != set(SELECTION_FIELDS):
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_SELECTION_PAYLOAD_SCHEMA_INVALID",
        )
    try:
        selection = TenantBrandingProfileSelection.from_dict(
            cast(Mapping[str, object], payload)
        )
    except (TypeError, ValueError, TenantBrandingProfileSelectionError) as error:
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_SELECTION_PAYLOAD_INVALID",
            error,
        )
    expected_identity = _selection_evidence_identity(selection)
    if (
        raw.get("tenant_id") != selection.tenant_id
        or raw.get("selection_id") != selection.selection_id
        or raw.get("selection_revision") != selection.selection_revision
        or raw.get("selection_fingerprint") != selection.fingerprint
        or raw.get("evidence_identity") != expected_identity
    ):
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_SELECTION_RECORD_CORRELATION_INVALID",
        )
    return selection


@dataclass(frozen=True, slots=True)
class TenantBrandingCurrentProfilePointer:
    """Explicit durable currentness pointer for one tenant branding stream.

    The pointer is compact currentness evidence only. It never embeds profile
    assets and never proves the referenced D21B2 entitlement remains ACTIVE.
    """

    tenant_id: str
    selection_id: str
    selection_revision: int
    selection_fingerprint: str
    profile_id: str
    profile_fingerprint: str
    branding_entitlement_id: str
    branding_entitlement_revision: int
    branding_entitlement_fingerprint: str
    branding_tier: str

    def __post_init__(self) -> None:
        """Validate every current-pointer correlation field fail closed."""
        _tenant(self.tenant_id)
        _identity("selection_id", self.selection_id)
        _positive_int("selection_revision", self.selection_revision)
        _fingerprint("selection_fingerprint", self.selection_fingerprint)
        _identity("profile_id", self.profile_id)
        _fingerprint("profile_fingerprint", self.profile_fingerprint)
        _identity("branding_entitlement_id", self.branding_entitlement_id)
        _positive_int(
            "branding_entitlement_revision",
            self.branding_entitlement_revision,
        )
        _fingerprint(
            "branding_entitlement_fingerprint",
            self.branding_entitlement_fingerprint,
        )
        _identity("branding_tier", self.branding_tier)

    @property
    def fingerprint(self) -> str:
        """Return deterministic SHA3-512 over the exact current-pointer payload."""
        return _sha3(self.to_dict(include_fingerprint=False))

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        """Serialize the exact pointer without profile asset material."""
        payload: dict[str, object] = {
            "schema": CURRENT_SCHEMA,
            "version": VERSION,
            "entity_type": "TenantBrandingCurrentProfilePointer",
            "tenant_id": self.tenant_id,
            "selection_id": self.selection_id,
            "selection_revision": self.selection_revision,
            "selection_fingerprint": self.selection_fingerprint,
            "profile_id": self.profile_id,
            "profile_fingerprint": self.profile_fingerprint,
            "branding_entitlement_id": self.branding_entitlement_id,
            "branding_entitlement_revision": self.branding_entitlement_revision,
            "branding_entitlement_fingerprint": (
                self.branding_entitlement_fingerprint
            ),
            "branding_tier": self.branding_tier,
        }
        if include_fingerprint:
            payload["fingerprint"] = _sha3(payload)
        return payload


_CURRENT_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "version",
        "entity_type",
        "tenant_id",
        "selection_id",
        "selection_revision",
        "selection_fingerprint",
        "profile_id",
        "profile_fingerprint",
        "branding_entitlement_id",
        "branding_entitlement_revision",
        "branding_entitlement_fingerprint",
        "branding_tier",
        "fingerprint",
    }
)


def _pointer_for(
    selection: TenantBrandingProfileSelection,
) -> TenantBrandingCurrentProfilePointer:
    """Project the only permitted current pointer from one selection fact."""
    tier = selection.branding_tier
    tier_value = tier.value if hasattr(tier, "value") else str(tier)
    return TenantBrandingCurrentProfilePointer(
        tenant_id=selection.tenant_id,
        selection_id=selection.selection_id,
        selection_revision=selection.selection_revision,
        selection_fingerprint=selection.fingerprint,
        profile_id=selection.profile_id,
        profile_fingerprint=selection.profile_fingerprint,
        branding_entitlement_id=selection.branding_entitlement_id,
        branding_entitlement_revision=selection.branding_entitlement_revision,
        branding_entitlement_fingerprint=(
            selection.branding_entitlement_fingerprint
        ),
        branding_tier=tier_value,
    )


def _hydrate_current(
    document: Mapping[str, Any],
) -> TenantBrandingCurrentProfilePointer:
    """Strictly hydrate one explicit current pointer and verify its seal."""
    if not isinstance(document, Mapping):
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_CURRENT_RECORD_INVALID",
        )
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != _CURRENT_FIELDS:
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_CURRENT_RECORD_SCHEMA_INVALID",
        )
    if (
        raw.get("schema") != CURRENT_SCHEMA
        or raw.get("version") != VERSION
        or raw.get("entity_type") != "TenantBrandingCurrentProfilePointer"
    ):
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_CURRENT_RECORD_VERSION_UNSUPPORTED",
        )
    try:
        pointer = TenantBrandingCurrentProfilePointer(
            tenant_id=cast(str, raw["tenant_id"]),
            selection_id=cast(str, raw["selection_id"]),
            selection_revision=cast(int, raw["selection_revision"]),
            selection_fingerprint=cast(str, raw["selection_fingerprint"]),
            profile_id=cast(str, raw["profile_id"]),
            profile_fingerprint=cast(str, raw["profile_fingerprint"]),
            branding_entitlement_id=cast(str, raw["branding_entitlement_id"]),
            branding_entitlement_revision=cast(
                int,
                raw["branding_entitlement_revision"],
            ),
            branding_entitlement_fingerprint=cast(
                str,
                raw["branding_entitlement_fingerprint"],
            ),
            branding_tier=cast(str, raw["branding_tier"]),
        )
    except TenantBrandingProfileRegistryError as error:
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_CURRENT_RECORD_INVALID",
            error,
        )
    if raw.get("fingerprint") != pointer.fingerprint:
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_CURRENT_FINGERPRINT_MISMATCH",
        )
    if pointer.to_dict() != raw:
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_CURRENT_RECORD_MISMATCH",
        )
    return pointer


@dataclass(frozen=True, slots=True)
class TenantBrandingCurrentProfile:
    """Correlated durable current pointer, selection fact and approved profile."""

    pointer: TenantBrandingCurrentProfilePointer
    selection: TenantBrandingProfileSelection
    profile: TenantBrandingProfile

    def __post_init__(self) -> None:
        """Require exact pointer→selection→profile provenance correlation."""
        if type(self.pointer) is not TenantBrandingCurrentProfilePointer:
            _raise(
                TenantBrandingProfileRegistryInputError,
                "D21B4B_CURRENT_POINTER_REQUIRED",
            )
        if type(self.selection) is not TenantBrandingProfileSelection:
            _raise(
                TenantBrandingProfileRegistryInputError,
                "D21B4B_SELECTION_REQUIRED",
            )
        if type(self.profile) is not TenantBrandingProfile:
            _raise(
                TenantBrandingProfileRegistryInputError,
                "D21B4B_PROFILE_REQUIRED",
            )
        expected = _pointer_for(self.selection)
        if (
            self.pointer.to_dict() != expected.to_dict()
            or self.profile.tenant_id != self.selection.tenant_id
            or self.profile.profile_id != self.selection.profile_id
            or self.profile.fingerprint != self.selection.profile_fingerprint
        ):
            _raise(TenantBrandingProfileRegistryCorrelationError)

    def to_dict(self) -> dict[str, object]:
        """Serialize correlated currentness evidence without adding authority."""
        return {
            "pointer": self.pointer.to_dict(),
            "selection": self.selection.to_dict(),
            "profile": self.profile.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class TenantBrandingSelectionPersistenceResult:
    """Outcome of one selection-history insert plus current-pointer advancement."""

    outcome: TenantBrandingProfilePersistenceOutcome
    current: TenantBrandingCurrentProfile

    def __post_init__(self) -> None:
        """Validate result shape without creating presentation authority."""
        if not isinstance(
            self.outcome,
            TenantBrandingProfilePersistenceOutcome,
        ):
            _raise(
                TenantBrandingProfileRegistryInputError,
                "D21B4B_OUTCOME_INVALID",
            )
        if type(self.current) is not TenantBrandingCurrentProfile:
            _raise(
                TenantBrandingProfileRegistryInputError,
                "D21B4B_CURRENT_REQUIRED",
            )


def ensure_indexes(
    profile_collection: Any,
    selection_collection: Any,
    current_collection: Any,
) -> None:
    """Create exact tenant-scoped uniqueness indexes; perform no data writes."""
    profiles = _collection(profile_collection, "PROFILE")
    selections = _collection(selection_collection, "SELECTION")
    current = _collection(current_collection, "CURRENT")
    try:
        profiles.create_index(
            [("tenant_id", ASCENDING), ("profile_id", ASCENDING)],
            unique=True,
            name=PROFILE_ID_INDEX_NAME,
        )
        profiles.create_index(
            [("tenant_id", ASCENDING), ("profile_fingerprint", ASCENDING)],
            unique=True,
            name=PROFILE_FINGERPRINT_INDEX_NAME,
        )
        selections.create_index(
            [("tenant_id", ASCENDING), ("selection_id", ASCENDING)],
            unique=True,
            name=SELECTION_ID_INDEX_NAME,
        )
        selections.create_index(
            [("tenant_id", ASCENDING), ("selection_revision", ASCENDING)],
            unique=True,
            name=SELECTION_REVISION_INDEX_NAME,
        )
        current.create_index(
            [("tenant_id", ASCENDING)],
            unique=True,
            name=CURRENT_TENANT_INDEX_NAME,
        )
    except (AttributeError, PyMongoError) as error:
        _raise(
            TenantBrandingProfileRegistryPersistenceUnavailableError,
            cause=error,
        )


def get_profile(
    tenant_id: str,
    profile_id: str,
    profile_collection: Any,
    *,
    session: Any,
) -> TenantBrandingProfile:
    """Read one exact tenant/profile record inside the caller transaction."""
    tx = _active_transaction(session)
    tenant = _tenant(tenant_id)
    identity = _identity("profile_id", profile_id)
    rows = _rows(
        profile_collection,
        {"tenant_id": tenant, "profile_id": identity},
        session=tx,
    )
    if not rows:
        _raise(TenantBrandingProfileRegistryProfileNotFoundError)
    if len(rows) > 1:
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_DUPLICATE_PROFILE_ID",
        )
    profile = _hydrate_profile(rows[0])
    if profile.tenant_id != tenant or profile.profile_id != identity:
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_PROFILE_TENANT_OR_ID_MISMATCH",
        )
    return profile


def get_selection(
    tenant_id: str,
    selection_id: str,
    selection_collection: Any,
    *,
    session: Any,
) -> TenantBrandingProfileSelection:
    """Read one exact tenant/selection fact inside the caller transaction."""
    tx = _active_transaction(session)
    tenant = _tenant(tenant_id)
    identity = _identity("selection_id", selection_id)
    rows = _rows(
        selection_collection,
        {"tenant_id": tenant, "selection_id": identity},
        session=tx,
    )
    if not rows:
        _raise(TenantBrandingProfileRegistrySelectionNotFoundError)
    if len(rows) > 1:
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_DUPLICATE_SELECTION_ID",
        )
    selection = _hydrate_selection(rows[0])
    if selection.tenant_id != tenant or selection.selection_id != identity:
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_SELECTION_TENANT_OR_ID_MISMATCH",
        )
    return selection


def _current_rows(
    tenant_id: str,
    current_collection: Any,
    *,
    session: Any,
) -> list[Mapping[str, Any]]:
    """Return bounded explicit current-pointer rows for one exact tenant."""
    return _rows(
        current_collection,
        {"tenant_id": _tenant(tenant_id)},
        session=session,
    )


def get_current(
    tenant_id: str,
    profile_collection: Any,
    selection_collection: Any,
    current_collection: Any,
    *,
    session: Any,
) -> TenantBrandingCurrentProfile:
    """Read and correlate explicit current pointer→selection→profile exactly.

    Historical selection order is never inspected. This proves durable
    currentness only; callers must separately prove the current D21B2
    entitlement remains ACTIVE before any presentation.
    """
    tx = _active_transaction(session)
    tenant = _tenant(tenant_id)
    rows = _current_rows(tenant, current_collection, session=tx)
    if not rows:
        _raise(TenantBrandingProfileRegistryCurrentPointerMissingError)
    if len(rows) > 1:
        _raise(TenantBrandingProfileRegistryMultipleCurrentPointerError)
    pointer = _hydrate_current(rows[0])
    if pointer.tenant_id != tenant:
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_CURRENT_TENANT_MISMATCH",
        )
    selection = get_selection(
        tenant,
        pointer.selection_id,
        selection_collection,
        session=tx,
    )
    profile = get_profile(
        tenant,
        pointer.profile_id,
        profile_collection,
        session=tx,
    )
    return TenantBrandingCurrentProfile(pointer, selection, profile)


def persist_profile(
    profile: TenantBrandingProfile,
    profile_collection: Any,
    *,
    session: Any,
) -> TenantBrandingProfile:
    """Persist or exactly replay one immutable approved D21B3 profile.

    Same tenant/profile identity plus identical canonical profile evidence is
    exact replay. Divergent evidence fails closed. Caller owns the transaction.
    """
    tx = _active_transaction(session)
    if type(profile) is not TenantBrandingProfile:
        _raise(
            TenantBrandingProfileRegistryInputError,
            "D21B4B_PROFILE_REQUIRED",
        )
    profiles = _collection(profile_collection, "PROFILE")
    existing_rows = _rows(
        profiles,
        {"tenant_id": profile.tenant_id, "profile_id": profile.profile_id},
        session=tx,
    )
    if len(existing_rows) > 1:
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_DUPLICATE_PROFILE_ID",
        )
    if existing_rows:
        existing = _hydrate_profile(existing_rows[0])
        if existing.to_dict() == profile.to_dict():
            return existing
        _raise(TenantBrandingProfileRegistryProfileConflictError)

    record = _profile_record(profile)
    try:
        profiles.insert_one(record, session=tx)
    except DuplicateKeyError as error:
        _raise(
            TenantBrandingProfileRegistryRetryRequiredError,
            cause=error,
        )
    except PyMongoError as error:
        _raise(
            TenantBrandingProfileRegistryPersistenceUnavailableError,
            cause=error,
        )

    persisted = get_profile(
        profile.tenant_id,
        profile.profile_id,
        profiles,
        session=tx,
    )
    if persisted.to_dict() != profile.to_dict():
        _raise(TenantBrandingProfileRegistryCorrelationError)
    return persisted


def _selection_by_revision(
    tenant_id: str,
    revision: int,
    selection_collection: Any,
    *,
    session: Any,
) -> TenantBrandingProfileSelection | None:
    """Read at most one exact tenant/revision selection; absence is explicit."""
    tenant = _tenant(tenant_id)
    revision_value = _positive_int("selection_revision", revision)
    rows = _rows(
        selection_collection,
        {
            "tenant_id": tenant,
            "selection_revision": revision_value,
        },
        session=session,
    )
    if len(rows) > 1:
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_DUPLICATE_SELECTION_REVISION",
        )
    return None if not rows else _hydrate_selection(rows[0])


def persist_selection_and_advance_current(
    selection: TenantBrandingProfileSelection,
    profile_collection: Any,
    selection_collection: Any,
    current_collection: Any,
    *,
    session: Any,
) -> TenantBrandingSelectionPersistenceResult:
    """Persist one D21B4A fact and atomically CAS explicit tenant currentness.

    The selected D21B3 profile must already exist durably with the exact
    fingerprint bound by the selection. Revision one requires no current
    pointer. Later revisions require the durable pointer to equal the selection's
    prior ID/fingerprint and immediately preceding revision. Exact replay is
    accepted only while that same selection remains current; historical replay
    never rewinds the pointer.
    """
    tx = _active_transaction(session)
    if type(selection) is not TenantBrandingProfileSelection:
        _raise(
            TenantBrandingProfileRegistryInputError,
            "D21B4B_SELECTION_REQUIRED",
        )
    profiles = _collection(profile_collection, "PROFILE")
    selections = _collection(selection_collection, "SELECTION")
    current = _collection(current_collection, "CURRENT")

    profile = get_profile(
        selection.tenant_id,
        selection.profile_id,
        profiles,
        session=tx,
    )
    if profile.fingerprint != selection.profile_fingerprint:
        _raise(TenantBrandingProfileRegistryCorrelationError)

    replay_rows = _rows(
        selections,
        {
            "tenant_id": selection.tenant_id,
            "selection_id": selection.selection_id,
        },
        session=tx,
    )
    if len(replay_rows) > 1:
        _raise(
            TenantBrandingProfileRegistryPersistedRecordInvalidError,
            "D21B4B_DUPLICATE_SELECTION_ID",
        )
    if replay_rows:
        existing = _hydrate_selection(replay_rows[0])
        if existing.to_dict() != selection.to_dict():
            _raise(TenantBrandingProfileRegistrySelectionConflictError)
        correlated = get_current(
            selection.tenant_id,
            profiles,
            selections,
            current,
            session=tx,
        )
        if correlated.selection.to_dict() != existing.to_dict():
            _raise(
                TenantBrandingProfileRegistryCurrentPointerConflictError,
                "D21B4B_STALE_SELECTION_REPLAY",
            )
        return TenantBrandingSelectionPersistenceResult(
            TenantBrandingProfilePersistenceOutcome.IDEMPOTENT_REPLAY,
            correlated,
        )

    same_revision = _selection_by_revision(
        selection.tenant_id,
        selection.selection_revision,
        selections,
        session=tx,
    )
    if same_revision is not None:
        _raise(TenantBrandingProfileRegistrySelectionConflictError)

    current_rows = _current_rows(
        selection.tenant_id,
        current,
        session=tx,
    )
    if len(current_rows) > 1:
        _raise(TenantBrandingProfileRegistryMultipleCurrentPointerError)

    prior_pointer: TenantBrandingCurrentProfilePointer | None
    if selection.selection_revision == 1:
        if current_rows:
            _hydrate_current(current_rows[0])
            _raise(TenantBrandingProfileRegistryCurrentPointerConflictError)
        if (
            selection.prior_selection_id is not None
            or selection.prior_selection_fingerprint is not None
        ):
            _raise(TenantBrandingProfileRegistryCurrentPointerConflictError)
        prior_pointer = None
    else:
        if not current_rows:
            _raise(TenantBrandingProfileRegistryCurrentPointerMissingError)
        prior_pointer = _hydrate_current(current_rows[0])
        if (
            prior_pointer.selection_revision + 1
            != selection.selection_revision
            or prior_pointer.selection_id != selection.prior_selection_id
            or prior_pointer.selection_fingerprint
            != selection.prior_selection_fingerprint
        ):
            _raise(TenantBrandingProfileRegistryCurrentPointerConflictError)
        prior_selection = get_selection(
            selection.tenant_id,
            prior_pointer.selection_id,
            selections,
            session=tx,
        )
        if _pointer_for(prior_selection).to_dict() != prior_pointer.to_dict():
            _raise(TenantBrandingProfileRegistryCorrelationError)

    record = _selection_record(selection)
    try:
        selections.insert_one(record, session=tx)
    except DuplicateKeyError as error:
        _raise(
            TenantBrandingProfileRegistryRetryRequiredError,
            cause=error,
        )
    except PyMongoError as error:
        _raise(
            TenantBrandingProfileRegistryPersistenceUnavailableError,
            cause=error,
        )

    next_pointer = _pointer_for(selection)
    try:
        if prior_pointer is None:
            current.insert_one(next_pointer.to_dict(), session=tx)
        else:
            result = current.update_one(
                prior_pointer.to_dict(),
                {"$set": next_pointer.to_dict()},
                session=tx,
            )
            if getattr(result, "matched_count", 0) != 1:
                _raise(TenantBrandingProfileRegistryRetryRequiredError)
    except TenantBrandingProfileRegistryError:
        raise
    except DuplicateKeyError as error:
        _raise(
            TenantBrandingProfileRegistryRetryRequiredError,
            cause=error,
        )
    except PyMongoError as error:
        _raise(
            TenantBrandingProfileRegistryPersistenceUnavailableError,
            cause=error,
        )

    persisted = get_current(
        selection.tenant_id,
        profiles,
        selections,
        current,
        session=tx,
    )
    if persisted.selection.to_dict() != selection.to_dict():
        _raise(TenantBrandingProfileRegistryCorrelationError)
    return TenantBrandingSelectionPersistenceResult(
        TenantBrandingProfilePersistenceOutcome.CREATED,
        persisted,
    )


class TenantBrandingProfileRegistry:
    """Static durable facade; owns no Mongo client or transaction lifecycle."""

    ensure_indexes = staticmethod(ensure_indexes)
    get_profile = staticmethod(get_profile)
    get_selection = staticmethod(get_selection)
    get_current = staticmethod(get_current)
    persist_profile = staticmethod(persist_profile)
    persist_selection_and_advance_current = staticmethod(
        persist_selection_and_advance_current
    )


__all__ = [
    "CURRENT_COLLECTION",
    "CURRENT_SCHEMA",
    "CURRENT_TENANT_INDEX_NAME",
    "PROFILE_COLLECTION",
    "PROFILE_FINGERPRINT_INDEX_NAME",
    "PROFILE_ID_INDEX_NAME",
    "PROFILE_RECORD_SCHEMA",
    "READ_CONCERN",
    "SELECTION_COLLECTION",
    "SELECTION_ID_INDEX_NAME",
    "SELECTION_RECORD_SCHEMA",
    "SELECTION_REVISION_INDEX_NAME",
    "TenantBrandingCurrentProfile",
    "TenantBrandingCurrentProfilePointer",
    "TenantBrandingProfilePersistenceOutcome",
    "TenantBrandingProfileRegistry",
    "TenantBrandingProfileRegistryCorrelationError",
    "TenantBrandingProfileRegistryCurrentPointerConflictError",
    "TenantBrandingProfileRegistryCurrentPointerMissingError",
    "TenantBrandingProfileRegistryError",
    "TenantBrandingProfileRegistryInputError",
    "TenantBrandingProfileRegistryMultipleCurrentPointerError",
    "TenantBrandingProfileRegistryPersistedRecordInvalidError",
    "TenantBrandingProfileRegistryPersistenceUnavailableError",
    "TenantBrandingProfileRegistryProfileConflictError",
    "TenantBrandingProfileRegistryProfileNotFoundError",
    "TenantBrandingProfileRegistryRetryRequiredError",
    "TenantBrandingProfileRegistrySelectionConflictError",
    "TenantBrandingProfileRegistrySelectionNotFoundError",
    "TenantBrandingProfileRegistryTransactionRequiredError",
    "TenantBrandingSelectionPersistenceResult",
    "VERSION",
    "WRITE_CONCERN",
    "ensure_indexes",
    "get_current",
    "get_profile",
    "get_selection",
    "persist_profile",
    "persist_selection_and_advance_current",
]

# ARTIFACT: tenant_branding_profile_registry.py
# VERSION: v1.0.0-D21B4B-TENANT-BRANDING-PROFILE-REGISTRY
# AUTHORITY BOUNDARY: immutable profile/selection persistence and explicit tenant current-pointer CAS only; no entitlement freshness, browser, asset-resolution, IAM or financial authority
# TENANT POSTURE: every profile, selection, replay, currentness read/write and CAS predicate is tenant-scoped
# FAIL-CLOSED POSTURE: active transaction required; strict schemas, corruption, divergence, duplicate pointers, stale lineage, races and outages reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
