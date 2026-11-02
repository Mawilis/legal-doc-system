"""Durable single-use registry for Deputy browser-device proof challenges.

TITLE: WILSY OS Deputy Device Provenance Registry
VERSION: v1.0.0-L8-6H-DEPUTY-DEVICE-PROVENANCE-REGISTRY
AUTHORITY: Python EOS Legal Operations challenge persistence and consumption.
EPITOME: Persist one exact server-issued L8-6G challenge, rehydrate it only
         through the canonical L8-6B binding, revalidate the exact authenticated
         session, verify WebCrypto P-256 proof, and atomically consume the
         challenge with its immutable provenance in one caller-owned transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/deputy_device_provenance_registry.py
COLLABORATION / OWNERSHIP: L8-6G owns challenge/provenance cryptographic meaning;
                            L8-6B owns canonical principal/Deputy binding;
                            AuthRegistry owns current session truth; this
                            registry owns persistence, hydration and one-time CAS.
COMPLIANCE: Privacy-by-design controls; no legal-compliance finding is made.
SECURITY / PRIVACY POSTURE: Stores public key, nonce, fingerprints and proof
                            metadata only. No private key, raw signature,
                            bearer, location, permission or biometric material.
TENANT BOUNDARY: Every query and write is exact tenant + challenge scoped.
AUTHORITY BOUNDARY: Browser key proof-of-possession only. No hardware
                    attestation, device trust, IAM grant, service or Return of
                    Service authority is created.
TRANSACTION BOUNDARY: Every operational method requires one already-active
                      caller-owned Mongo transaction. This registry never
                      starts, commits, aborts or retries a transaction.
TTL POSTURE: No TTL index; expiry is explicit challenge-domain truth.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG: v1.0.0-L8-6H-DEPUTY-DEVICE-PROVENANCE-REGISTRY establishes exact
           tenant/challenge persistence, current-session revalidation, strict
           challenge/provenance hydration, P-256 proof verification, and atomic
           single-use consumption inside the caller-owned transaction.
COMPLIANCE: Privacy-by-design engineering controls; no legal-compliance
            certification or regulatory finding is made by this module.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial
                              execution authority; no payment or settlement
                              truth is created or inferred here.
FAIL-CLOSED DECLARATION: Corrupt storage, stale session, scope drift, expired
                         challenge, invalid signature, replay, duplicate race,
                         inactive transaction or persistence failure rejects.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Any, Final, NoReturn, cast

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.deputy_device_provenance_authority import (
    DeputyDeviceProvenance,
    DeputyDeviceProvenanceAuthorityError,
    DeputyDeviceProvenanceChallenge,
)
from tools.eos.legal_operations.registry.deputy_principal_binding_registry import (
    DeputyPrincipalBindingRegistry,
    DeputyPrincipalBindingRegistryError,
)


VERSION: Final[str] = (
    "v1.0.0-L8-6H-DEPUTY-DEVICE-PROVENANCE-REGISTRY"
)
COLLECTION: Final[str] = "legal_operations_deputy_device_provenance_challenges"
IDENTITY_INDEX: Final[str] = (
    "legal_operations_deputy_device_challenge_identity_unique"
)
PRINCIPAL_HISTORY_INDEX: Final[str] = (
    "legal_operations_deputy_device_challenge_principal_history"
)

_IDENTIFIER: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,191}$"
)
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)
_CHALLENGE_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "version",
        "purpose",
        "algorithm",
        "challenge_id",
        "tenant_id",
        "principal_id",
        "deputy_id",
        "sheriff_office_id",
        "session_reference",
        "device_id",
        "public_key_spki",
        "public_key_fingerprint",
        "nonce",
        "issued_at",
        "expires_at",
        "challenge_fingerprint",
    }
)
_METADATA_FIELDS: Final[frozenset[str]] = frozenset(
    {"consumed_at", "provenance", "provenance_fingerprint"}
)
_PROVENANCE_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "version",
        "entity_type",
        "tenant_id",
        "principal_id",
        "deputy_id",
        "sheriff_office_id",
        "session_reference",
        "device_id",
        "public_key_spki",
        "public_key_fingerprint",
        "challenge_id",
        "challenge_fingerprint",
        "verified_at",
        "signature_fingerprint",
    }
)


class DeputyDeviceProvenanceRegistryError(RuntimeError):
    """Base stable L8-6H persistence-boundary failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class DeputyDeviceProvenanceRegistryTransactionRequiredError(
    DeputyDeviceProvenanceRegistryError
):
    """Caller did not supply one already-active Mongo transaction."""


class DeputyDeviceProvenanceRegistryConflictError(
    DeputyDeviceProvenanceRegistryError
):
    """Challenge identity, lifecycle or scope conflicts with the request."""


class DeputyDeviceProvenanceRegistryPersistedRecordInvalidError(
    DeputyDeviceProvenanceRegistryError
):
    """Persisted challenge/provenance bytes fail strict domain validation."""


class DeputyDeviceProvenanceRegistryRetryTransactionError(
    DeputyDeviceProvenanceRegistryError
):
    """A duplicate-key race requires retrying the complete caller transaction."""


class DeputyDeviceProvenanceRegistryPersistenceError(
    DeputyDeviceProvenanceRegistryError
):
    """Mongo persistence failed without a safe conflict classification."""


def _raise(
    error_type: type[DeputyDeviceProvenanceRegistryError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _require_transaction(session: object) -> object:
    """Require the caller's existing active transaction; never own its lifecycle."""
    if session is None:
        _raise(
            DeputyDeviceProvenanceRegistryTransactionRequiredError,
            "L8_6H_ACTIVE_TRANSACTION_REQUIRED",
        )
    try:
        marker = getattr(session, "in_transaction", None)
        active = marker() if callable(marker) else marker
    except Exception as error:
        _raise(
            DeputyDeviceProvenanceRegistryTransactionRequiredError,
            "L8_6H_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )
    if active is not True:
        _raise(
            DeputyDeviceProvenanceRegistryTransactionRequiredError,
            "L8_6H_ACTIVE_TRANSACTION_REQUIRED",
        )
    return session


def _identifier(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTIFIER.fullmatch(value) is None
    ):
        _raise(
            DeputyDeviceProvenanceRegistryError,
            f"L8_6H_{name.upper()}_INVALID",
        )
    return value


def _tenant(value: object) -> str:
    tenant = _identifier("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _raise(
            DeputyDeviceProvenanceRegistryError,
            "L8_6H_TENANT_REQUIRED",
        )
    return tenant


def _utc(value: object, code: str) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _raise(DeputyDeviceProvenanceRegistryError, code)
    return value.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return _utc(value, "L8_6H_TIMESTAMP_INVALID").isoformat(
        timespec="microseconds"
    )


def _parse_iso(value: object, code: str) -> datetime:
    if not isinstance(value, str):
        _raise(DeputyDeviceProvenanceRegistryPersistedRecordInvalidError, code)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        _raise(
            DeputyDeviceProvenanceRegistryPersistedRecordInvalidError,
            code,
            error,
        )
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        _raise(DeputyDeviceProvenanceRegistryPersistedRecordInvalidError, code)
    normalized = parsed.astimezone(timezone.utc)
    if normalized.isoformat(timespec="microseconds") != value:
        _raise(DeputyDeviceProvenanceRegistryPersistedRecordInvalidError, code)
    return normalized


def _challenge_document(
    challenge: DeputyDeviceProvenanceChallenge,
) -> dict[str, object]:
    if type(challenge) is not DeputyDeviceProvenanceChallenge:
        _raise(
            DeputyDeviceProvenanceRegistryError,
            "L8_6H_CHALLENGE_REQUIRED",
        )
    try:
        payload = challenge.to_dict()
    except DeputyDeviceProvenanceAuthorityError as error:
        _raise(
            DeputyDeviceProvenanceRegistryError,
            "L8_6H_CHALLENGE_INVALID",
            error,
        )
    if set(payload) != _CHALLENGE_FIELDS:
        _raise(
            DeputyDeviceProvenanceRegistryError,
            "L8_6H_CHALLENGE_SERIALIZATION_INVALID",
        )
    return dict(payload)


def _same(left: object, right: object) -> bool:
    """Constant-time compare only canonical SHA3-512 fingerprints."""
    return (
        isinstance(left, str)
        and isinstance(right, str)
        and hmac.compare_digest(left, right)
    )


def _provenance_document(
    value: DeputyDeviceProvenance,
) -> dict[str, object]:
    if type(value) is not DeputyDeviceProvenance:
        _raise(
            DeputyDeviceProvenanceRegistryError,
            "L8_6H_PROVENANCE_REQUIRED",
        )
    try:
        payload = value.to_dict()
        fingerprint = value.fingerprint
    except DeputyDeviceProvenanceAuthorityError as error:
        _raise(
            DeputyDeviceProvenanceRegistryError,
            "L8_6H_PROVENANCE_INVALID",
            error,
        )
    if set(payload) != _PROVENANCE_FIELDS:
        _raise(
            DeputyDeviceProvenanceRegistryError,
            "L8_6H_PROVENANCE_SERIALIZATION_INVALID",
        )
    return {**payload, "fingerprint": fingerprint}


class DeputyDeviceProvenanceRegistry:
    """Persist and consume L8-6G challenges in one exact transaction.

    The one-document lifecycle is intentional: a single compare-and-set writes
    consumed_at and the provenance payload together. A transaction rollback
    therefore rolls back both. The registry does not enroll a device or make
    ongoing trust/currentness claims.
    """

    def __init__(
        self,
        collection: Any,
        *,
        auth_registry: Any,
        binding_collection: Any,
    ) -> None:
        if collection is None:
            _raise(
                DeputyDeviceProvenanceRegistryError,
                "L8_6H_COLLECTION_REQUIRED",
            )
        if auth_registry is None or not callable(
            getattr(auth_registry, "is_session_current", None)
        ):
            _raise(
                DeputyDeviceProvenanceRegistryError,
                "L8_6H_AUTH_REGISTRY_REQUIRED",
            )
        if binding_collection is None:
            _raise(
                DeputyDeviceProvenanceRegistryError,
                "L8_6H_BINDING_COLLECTION_REQUIRED",
            )
        self._collection = collection
        self._auth_registry = auth_registry
        self._binding_collection = binding_collection

    def ensure_indexes(self) -> None:
        """Create deterministic non-TTL identity and history indexes."""
        try:
            self._collection.create_index(
                [("tenant_id", ASCENDING), ("challenge_id", ASCENDING)],
                unique=True,
                name=IDENTITY_INDEX,
            )
            self._collection.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("principal_id", ASCENDING),
                    ("issued_at", ASCENDING),
                ],
                unique=False,
                name=PRINCIPAL_HISTORY_INDEX,
            )
        except PyMongoError as error:
            _raise(
                DeputyDeviceProvenanceRegistryPersistenceError,
                "L8_6H_INDEX_PERSISTENCE_FAILURE",
                error,
            )

    def _require_current_session(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        session_reference: str,
        at: datetime,
        session: object,
    ) -> None:
        try:
            current = self._auth_registry.is_session_current(
                tenant_id,
                principal_id,
                session_reference,
                at=at,
                session=session,
            )
        except Exception as error:
            _raise(
                DeputyDeviceProvenanceRegistryError,
                "L8_6H_SESSION_AUTHORITY_UNAVAILABLE",
                error,
            )
        if current is not True:
            _raise(
                DeputyDeviceProvenanceRegistryConflictError,
                "L8_6H_AUTHENTICATED_SESSION_NOT_CURRENT",
            )

    def _resolve_binding(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        session: object,
    ) -> Any:
        try:
            binding = DeputyPrincipalBindingRegistry.resolve_by_principal(
                tenant_id,
                principal_id,
                self._binding_collection,
                session=session,
            )
        except DeputyPrincipalBindingRegistryError as error:
            _raise(
                DeputyDeviceProvenanceRegistryConflictError,
                "L8_6H_CANONICAL_DEPUTY_BINDING_UNAVAILABLE",
                error,
            )
        if (
            binding.tenant_id != tenant_id
            or binding.principal_id != principal_id
        ):
            _raise(
                DeputyDeviceProvenanceRegistryPersistedRecordInvalidError,
                "L8_6H_CANONICAL_DEPUTY_BINDING_SCOPE_INVALID",
            )
        return binding

    def _hydrate_challenge(
        self,
        row: Mapping[str, object],
        *,
        session: object,
    ) -> DeputyDeviceProvenanceChallenge:
        """Rebuild challenge through canonical binding and compare exact bytes."""
        if not isinstance(row, Mapping):
            _raise(
                DeputyDeviceProvenanceRegistryPersistedRecordInvalidError,
                "L8_6H_PERSISTED_RECORD_INVALID",
            )
        payload = {key: value for key, value in row.items() if key != "_id"}
        if set(payload) != _CHALLENGE_FIELDS | _METADATA_FIELDS:
            _raise(
                DeputyDeviceProvenanceRegistryPersistedRecordInvalidError,
                "L8_6H_PERSISTED_RECORD_SHAPE_INVALID",
            )
        tenant = _tenant(payload.get("tenant_id"))
        principal = _identifier("principal_id", payload.get("principal_id"))
        binding = self._resolve_binding(
            tenant_id=tenant,
            principal_id=principal,
            session=session,
        )
        try:
            challenge = DeputyDeviceProvenanceChallenge.issue(
                binding=binding,
                session_reference=cast(str, payload["session_reference"]),
                challenge_id=cast(str, payload["challenge_id"]),
                public_key_spki_der=self._decode_b64(
                    cast(str, payload["public_key_spki"])
                ),
                nonce=self._decode_b64(cast(str, payload["nonce"])),
                issued_at=_parse_iso(
                    payload["issued_at"],
                    "L8_6H_ISSUED_AT_INVALID",
                ),
                expires_at=_parse_iso(
                    payload["expires_at"],
                    "L8_6H_EXPIRES_AT_INVALID",
                ),
            )
        except DeputyDeviceProvenanceRegistryError:
            raise
        except Exception as error:
            _raise(
                DeputyDeviceProvenanceRegistryPersistedRecordInvalidError,
                "L8_6H_PERSISTED_CHALLENGE_INVALID",
                error,
            )
        canonical = _challenge_document(challenge)
        persisted = {key: payload[key] for key in _CHALLENGE_FIELDS}
        if canonical != persisted:
            _raise(
                DeputyDeviceProvenanceRegistryPersistedRecordInvalidError,
                "L8_6H_PERSISTED_CHALLENGE_MISMATCH",
            )
        consumed_at = payload["consumed_at"]
        provenance = payload["provenance"]
        provenance_fingerprint = payload["provenance_fingerprint"]
        if consumed_at is None:
            if provenance is not None or provenance_fingerprint is not None:
                _raise(
                    DeputyDeviceProvenanceRegistryPersistedRecordInvalidError,
                    "L8_6H_UNCONSUMED_RECORD_HAS_PROVENANCE",
                )
        else:
            _parse_iso(consumed_at, "L8_6H_CONSUMED_AT_INVALID")
            if (
                not isinstance(provenance, Mapping)
                or set(provenance) != _PROVENANCE_FIELDS | {"fingerprint"}
                or not isinstance(provenance_fingerprint, str)
                or not _same(provenance.get("fingerprint"), provenance_fingerprint)
            ):
                _raise(
                    DeputyDeviceProvenanceRegistryPersistedRecordInvalidError,
                    "L8_6H_CONSUMED_RECORD_PROVENANCE_INVALID",
                )
            provenance_payload = {
                key: value for key, value in provenance.items() if key != "fingerprint"
            }
            provenance_digest = hashlib.sha3_512(
                json.dumps(
                    provenance_payload,
                    ensure_ascii=True,
                    allow_nan=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()
            verified_at = _parse_iso(
                provenance.get("verified_at"),
                "L8_6H_PROVENANCE_VERIFIED_AT_INVALID",
            )
            signature_fingerprint = provenance.get("signature_fingerprint")
            if (
                provenance.get("schema") != canonical.get("schema")
                or provenance.get("version") != canonical.get("version")
                or provenance.get("entity_type") != "DeputyDeviceProvenance"
                or provenance.get("tenant_id") != tenant
                or provenance.get("principal_id") != principal
                or provenance.get("deputy_id") != challenge.deputy_id
                or provenance.get("sheriff_office_id") != challenge.sheriff_office_id
                or provenance.get("session_reference") != challenge.session_reference
                or provenance.get("device_id") != challenge.device_id
                or provenance.get("public_key_spki") != challenge.public_key_spki
                or provenance.get("public_key_fingerprint") != challenge.public_key_fingerprint
                or provenance.get("challenge_id") != challenge.challenge_id
                or provenance.get("challenge_fingerprint")
                != canonical["challenge_fingerprint"]
                or verified_at < challenge.issued_at
                or verified_at > challenge.expires_at
                or not isinstance(signature_fingerprint, str)
                or re.fullmatch(r"[0-9a-f]{128}", signature_fingerprint) is None
                or not _same(provenance.get("fingerprint"), provenance_digest)
            ):
                _raise(
                    DeputyDeviceProvenanceRegistryPersistedRecordInvalidError,
                    "L8_6H_CONSUMED_PROVENANCE_SCOPE_INVALID",
                )
        return challenge

    @staticmethod
    def _decode_b64(value: str) -> bytes:
        import base64

        if not isinstance(value, str) or not value:
            _raise(
                DeputyDeviceProvenanceRegistryPersistedRecordInvalidError,
                "L8_6H_BASE64_VALUE_INVALID",
            )
        try:
            decoded = base64.b64decode(
                value + "=" * (-len(value) % 4),
                altchars=b"-_",
                validate=True,
            )
        except (ValueError, TypeError) as error:
            _raise(
                DeputyDeviceProvenanceRegistryPersistedRecordInvalidError,
                "L8_6H_BASE64_VALUE_INVALID",
                error,
            )
        return decoded

    def create(
        self,
        challenge: DeputyDeviceProvenanceChallenge,
        *,
        session: object,
    ) -> DeputyDeviceProvenanceChallenge:
        """Persist one exact challenge; only an unconsumed exact replay is idempotent."""
        tx = _require_transaction(session)
        document = _challenge_document(challenge)
        tenant = _tenant(challenge.tenant_id)
        principal = _identifier("principal_id", challenge.principal_id)
        self._require_current_session(
            tenant_id=tenant,
            principal_id=principal,
            session_reference=challenge.session_reference,
            at=challenge.issued_at,
            session=tx,
        )
        binding = self._resolve_binding(
            tenant_id=tenant,
            principal_id=principal,
            session=tx,
        )
        if (
            binding.deputy_id != challenge.deputy_id
            or binding.sheriff_office_id != challenge.sheriff_office_id
        ):
            _raise(
                DeputyDeviceProvenanceRegistryConflictError,
                "L8_6H_CHALLENGE_BINDING_MISMATCH",
            )
        selector = {
            "tenant_id": tenant,
            "challenge_id": challenge.challenge_id,
        }
        try:
            existing = self._collection.find_one(selector, session=tx)
        except PyMongoError as error:
            _raise(
                DeputyDeviceProvenanceRegistryPersistenceError,
                "L8_6H_READ_PERSISTENCE_FAILURE",
                error,
            )
        if existing is not None:
            persisted = self._hydrate_challenge(
                cast(Mapping[str, object], existing),
                session=tx,
            )
            existing_payload = _challenge_document(persisted)
            if existing_payload == document and existing.get("consumed_at") is None:
                return persisted
            _raise(
                DeputyDeviceProvenanceRegistryConflictError,
                "L8_6H_DIVERGENT_OR_CONSUMED_CHALLENGE_REPLAY",
            )
        stored = {
            **document,
            "consumed_at": None,
            "provenance": None,
            "provenance_fingerprint": None,
        }
        try:
            self._collection.insert_one(stored, session=tx)
        except DuplicateKeyError as error:
            _raise(
                DeputyDeviceProvenanceRegistryRetryTransactionError,
                "L8_6H_DUPLICATE_RACE_RETRY_TRANSACTION",
                error,
            )
        except PyMongoError as error:
            _raise(
                DeputyDeviceProvenanceRegistryPersistenceError,
                "L8_6H_WRITE_PERSISTENCE_FAILURE",
                error,
            )
        try:
            readback = self._collection.find_one(selector, session=tx)
        except PyMongoError as error:
            _raise(
                DeputyDeviceProvenanceRegistryPersistenceError,
                "L8_6H_READBACK_PERSISTENCE_FAILURE",
                error,
            )
        if readback is None:
            _raise(
                DeputyDeviceProvenanceRegistryPersistenceError,
                "L8_6H_CREATE_READBACK_MISSING",
            )
        hydrated = self._hydrate_challenge(
            cast(Mapping[str, object], readback),
            session=tx,
        )
        if (
            _challenge_document(hydrated) != document
            or readback.get("consumed_at") is not None
        ):
            _raise(
                DeputyDeviceProvenanceRegistryPersistedRecordInvalidError,
                "L8_6H_CREATE_READBACK_MISMATCH",
            )
        return hydrated

    def get(
        self,
        tenant_id: str,
        challenge_id: str,
        *,
        session: object,
    ) -> DeputyDeviceProvenanceChallenge:
        """Resolve one exact tenant/challenge record; never expose cross-tenant state."""
        tx = _require_transaction(session)
        tenant = _tenant(tenant_id)
        identity = _identifier("challenge_id", challenge_id)
        try:
            row = self._collection.find_one(
                {"tenant_id": tenant, "challenge_id": identity},
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                DeputyDeviceProvenanceRegistryPersistenceError,
                "L8_6H_READ_PERSISTENCE_FAILURE",
                error,
            )
        if row is None:
            _raise(
                DeputyDeviceProvenanceRegistryConflictError,
                "L8_6H_CHALLENGE_NOT_FOUND",
            )
        return self._hydrate_challenge(
            cast(Mapping[str, object], row),
            session=tx,
        )

    def get_consumed_provenance(
        self,
        *,
        tenant_id: str,
        challenge_id: str,
        principal_id: str,
        session_reference: str,
        at: datetime,
        session: object,
    ) -> DeputyDeviceProvenance:
        """Load an already-consumed challenge proof for signed offline event sync."""
        tx = _require_transaction(session)
        tenant = _tenant(tenant_id)
        identity = _identifier("challenge_id", challenge_id)
        current_principal = _identifier("principal_id", principal_id)
        current_session = _identifier("session_reference", session_reference)
        try:
            row = self._collection.find_one(
                {"tenant_id": tenant, "challenge_id": identity},
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                DeputyDeviceProvenanceRegistryPersistenceError,
                "L8_6H_READ_UNAVAILABLE",
                error,
            )
        if row is None:
            _raise(DeputyDeviceProvenanceRegistryConflictError, "L8_6H_CHALLENGE_NOT_FOUND")
        challenge = self._hydrate_challenge(
            cast(Mapping[str, object], row),
            session=tx,
        )
        payload = cast(Mapping[str, object], row)
        if payload.get("consumed_at") is None or not isinstance(payload.get("provenance"), Mapping):
            _raise(DeputyDeviceProvenanceRegistryConflictError, "L8_6H_CHALLENGE_NOT_CONSUMED")
        provenance = DeputyDeviceProvenance.from_persisted(
            cast(Mapping[str, object], payload["provenance"])
        )
        if (
            provenance.tenant_id != tenant
            or provenance.principal_id != challenge.principal_id
            or provenance.deputy_id != challenge.deputy_id
            or provenance.sheriff_office_id != challenge.sheriff_office_id
            or provenance.session_reference != challenge.session_reference
            or provenance.device_id != challenge.device_id
            or provenance.challenge_id != challenge.challenge_id
            or provenance.principal_id != current_principal
        ):
            _raise(
                DeputyDeviceProvenanceRegistryPersistedRecordInvalidError,
                "L8_6H_PROVENANCE_SCOPE_MISMATCH",
            )
        self._require_current_session(
            tenant_id=tenant,
            principal_id=provenance.principal_id,
            session_reference=current_session,
            at=_utc(at, "L8_6H_CURRENT_SESSION_TIME_INVALID"),
            session=tx,
        )
        return provenance

    def verify_and_consume(
        self,
        *,
        tenant_id: str,
        challenge_id: str,
        signature_p1363: bytes,
        verified_at: datetime,
        session: object,
    ) -> DeputyDeviceProvenance:
        """Verify exact persisted challenge and atomically consume it once.

        The caller must re-evaluate current Deputy IAM authorities in the same
        transaction before invoking this operation. This registry independently
        revalidates the exact AuthRegistry session. One Mongo update writes both
        consumed_at and provenance; the caller owns commit/rollback.
        """
        tx = _require_transaction(session)
        tenant = _tenant(tenant_id)
        identity = _identifier("challenge_id", challenge_id)
        observed = _utc(verified_at, "L8_6H_VERIFIED_AT_INVALID")
        selector = {"tenant_id": tenant, "challenge_id": identity}
        try:
            row = self._collection.find_one(selector, session=tx)
        except PyMongoError as error:
            _raise(
                DeputyDeviceProvenanceRegistryPersistenceError,
                "L8_6H_READ_PERSISTENCE_FAILURE",
                error,
            )
        if row is None:
            _raise(
                DeputyDeviceProvenanceRegistryConflictError,
                "L8_6H_CHALLENGE_NOT_FOUND",
            )
        challenge = self._hydrate_challenge(
            cast(Mapping[str, object], row),
            session=tx,
        )
        if row.get("consumed_at") is not None:
            _raise(
                DeputyDeviceProvenanceRegistryConflictError,
                "L8_6H_CHALLENGE_ALREADY_CONSUMED",
            )
        self._require_current_session(
            tenant_id=tenant,
            principal_id=challenge.principal_id,
            session_reference=challenge.session_reference,
            at=observed,
            session=tx,
        )
        try:
            provenance = DeputyDeviceProvenance.verify(
                challenge=challenge,
                signature_p1363=signature_p1363,
                verified_at=observed,
            )
        except DeputyDeviceProvenanceAuthorityError as error:
            _raise(
                DeputyDeviceProvenanceRegistryConflictError,
                "L8_6H_PROOF_VERIFICATION_REJECTED",
                error,
            )
        provenance_payload = _provenance_document(provenance)
        challenge_payload = _challenge_document(challenge)
        if (
            provenance.tenant_id != tenant
            or provenance.principal_id != challenge.principal_id
            or provenance.deputy_id != challenge.deputy_id
            or provenance.sheriff_office_id != challenge.sheriff_office_id
            or provenance.session_reference != challenge.session_reference
            or provenance.device_id != challenge.device_id
            or provenance.challenge_id != identity
            or provenance.challenge_fingerprint
            != challenge_payload["challenge_fingerprint"]
        ):
            _raise(
                DeputyDeviceProvenanceRegistryConflictError,
                "L8_6H_PROOF_SCOPE_MISMATCH",
            )
        consumed_at = _iso(observed)
        cas = {
            **selector,
            "challenge_fingerprint": challenge_payload["challenge_fingerprint"],
            "session_reference": challenge.session_reference,
            "expires_at": challenge_payload["expires_at"],
            "consumed_at": None,
            "provenance": None,
            "provenance_fingerprint": None,
        }
        try:
            result = self._collection.update_one(
                cas,
                {
                    "$set": {
                        "consumed_at": consumed_at,
                        "provenance": provenance_payload,
                        "provenance_fingerprint": provenance.fingerprint,
                    }
                },
                upsert=False,
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                DeputyDeviceProvenanceRegistryPersistenceError,
                "L8_6H_CONSUME_PERSISTENCE_FAILURE",
                error,
            )
        if (
            getattr(result, "matched_count", None) != 1
            or getattr(result, "modified_count", None) != 1
        ):
            _raise(
                DeputyDeviceProvenanceRegistryConflictError,
                "L8_6H_CHALLENGE_CONSUMPTION_CONFLICT",
            )
        try:
            persisted = self._collection.find_one(selector, session=tx)
        except PyMongoError as error:
            _raise(
                DeputyDeviceProvenanceRegistryPersistenceError,
                "L8_6H_CONSUME_READBACK_FAILURE",
                error,
            )
        if persisted is None:
            _raise(
                DeputyDeviceProvenanceRegistryPersistenceError,
                "L8_6H_CONSUME_READBACK_MISSING",
            )
        hydrated = self._hydrate_challenge(
            cast(Mapping[str, object], persisted),
            session=tx,
        )
        persisted_provenance = persisted.get("provenance")
        if (
            persisted.get("consumed_at") != consumed_at
            or not isinstance(persisted_provenance, Mapping)
            or dict(persisted_provenance) != provenance_payload
            or not _same(
                persisted.get("provenance_fingerprint"),
                provenance.fingerprint,
            )
            or hydrated.to_dict() != challenge_payload
        ):
            _raise(
                DeputyDeviceProvenanceRegistryPersistedRecordInvalidError,
                "L8_6H_CONSUME_READBACK_MISMATCH",
            )
        return provenance


def ensure_indexes(collection: Any) -> None:
    """Create governed indexes on one explicit collection during controlled bootstrap."""
    if collection is None:
        _raise(
            DeputyDeviceProvenanceRegistryError,
            "L8_6H_COLLECTION_REQUIRED",
        )
    try:
        collection.create_index(
            [("tenant_id", ASCENDING), ("challenge_id", ASCENDING)],
            unique=True,
            name=IDENTITY_INDEX,
        )
        collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("principal_id", ASCENDING),
                ("issued_at", ASCENDING),
            ],
            unique=False,
            name=PRINCIPAL_HISTORY_INDEX,
        )
    except PyMongoError as error:
        _raise(
            DeputyDeviceProvenanceRegistryPersistenceError,
            "L8_6H_INDEX_PERSISTENCE_FAILURE",
            error,
        )


__all__ = [
    "VERSION",
    "COLLECTION",
    "IDENTITY_INDEX",
    "PRINCIPAL_HISTORY_INDEX",
    "DeputyDeviceProvenanceRegistry",
    "DeputyDeviceProvenanceRegistryError",
    "DeputyDeviceProvenanceRegistryTransactionRequiredError",
    "DeputyDeviceProvenanceRegistryConflictError",
    "DeputyDeviceProvenanceRegistryPersistedRecordInvalidError",
    "DeputyDeviceProvenanceRegistryRetryTransactionError",
    "DeputyDeviceProvenanceRegistryPersistenceError",
    "ensure_indexes",
]


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: deputy_device_provenance_registry.py
# VERSION: v1.0.0-L8-6H-DEPUTY-DEVICE-PROVENANCE-REGISTRY
# AUTHORITY BOUNDARY: Persisted one-time browser-key proof-of-possession only.
# TENANT POSTURE: Exact tenant/challenge and canonical binding/session scope.
# REPLAY POSTURE: Atomic consumed_at + provenance compare-and-set.
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive.
# FAIL-CLOSED POSTURE: Corrupt, expired, stale, replayed, cross-scope or failed writes reject.
# END OF WILSY OS SOVEREIGN ARTIFACT