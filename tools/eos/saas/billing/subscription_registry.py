# -*- coding: utf-8 -*-
"""WILSY OS — sovereign subscription persistence registry.

TITLE:
    WILSY OS Subscription Registry — Real Mongo Persistence

VERSION:
    v1.1.1-SUBSCRIPTION-REAL-MONGO

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Canonical MongoDB persistence boundary for tenant-scoped subscription
    lifecycle truth. Replaces the former process-local in-memory store while
    preserving the established SubscriptionRegistry public lifecycle surface,
    adding durable idempotency, optimistic revision checks, invalid-persisted-
    truth signaling, infrastructure failure semantics, and strict tenant-bound
    lookups.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/subscription_registry.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy OS Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-09-03

CHANGELOG:
    v1.1.1-SUBSCRIPTION-REAL-MONGO:
        - Closes Codex VAS13-001 by persisting canonical creation material,
          validating complete SHA3-512 syntax, and recomputing the persisted
          digest before hydration or replay classification.
        - Closes Codex VAS13-002 by classifying duplicate-key conflicts from
          Mongo index/key evidence and distinguishing subscription identity
          collisions from tenant-idempotency collisions.
        - Adds fail-closed handling for unknown duplicate-key classes.
        - Preserves all v1.1.0 real-Mongo persistence, tenant isolation,
          concurrency, lifecycle and Kennel EOS authority boundaries.

    v1.1.0-SUBSCRIPTION-REAL-MONGO:
        - Retires the canonical process-local _subscriptions dictionary.
        - Persists SubscriptionEntity truth in MongoDB.
        - Adds deterministic tenant-scoped unique indexes.
        - Requires explicit tenant scope on subscription reads and mutations.
        - Rejects payload/header tenant disagreement before persistence access.
        - Requires explicit create idempotency keys.
        - Implements durable exact-replay vs conflicting-command semantics.
        - Adds persisted schema/revision/fingerprint metadata.
        - Adds optimistic revision conflict detection.
        - Distinguishes absence, invalid persisted truth, concurrency conflict,
          and persistence infrastructure failure.
        - Keeps API-router authorization responsibility outside this registry.
        - Removes false OPERATIONAL claims from in-memory health reporting.

    v1.0.3-FIXED:
        - Legacy in-memory subscription registry.
        - Guarded None tier anomaly handling.

COMPLIANCE:
    POPIA section 19.
    GDPR Article 32.
    SOC 2 CC7.2.
    ISO 27001-aligned persistence and tenant isolation.

SECURITY / PRIVACY POSTURE:
    Every subscription lookup and mutation is tenant-keyed. Persistence errors
    fail closed and are never converted into fabricated empty/healthy business
    truth. Cross-tenant absence does not reveal another tenant's subscription.
    Caller identity, tenant membership, role and permission must already have
    been resolved by sovereign Python authority before this registry receives
    a tenant reference.

TENANT BOUNDARY:
    ``tenant_id_header`` is retained as a compatibility parameter name only.
    It represents an already-authorized tenant scope supplied by an upstream
    Python authority boundary. A raw HTTP X-Tenant-ID header is NOT authority.
    Missing tenant scope fails closed. Payload tenant disagreement fails before
    Mongo access.

AUTHORITY BOUNDARY:
    Owns subscription persistence, lifecycle mutation, persisted hydration,
    durable create-idempotency evidence, tenant-scoped reads, and persistence
    failure signaling only. It does not authenticate principals, establish
    membership, grant permissions, resolve WILSY AI entitlement, meter AI
    usage, run intelligence, or own HTTP authorization.

FINANCIAL AUTHORITY BOUNDARY:
    Subscription state and billing configuration are commercial truth only.
    APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED.
    No payment execution or settlement truth is created here.
    Kennel EOS remains the exclusive financial execution authority.

STRUCTURAL GOVERNANCE:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
    DISCOVER -> MAP -> WIRE -> CLEAN -> CERTIFY -> OBSERVE -> INTELLIGENCE
    -> EVOLVE.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import uuid
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from ..domain.subscription import (
    AuditAction,
    AuditEntry,
    BillingFrequency,
    CollectionMethod,
    PlanTiers,
    SubscriptionEntity,
    SubscriptionStatus,
    period_days_for_frequency,
    to_annual_amount,
    to_monthly_amount,
)


VERSION = "v1.1.1-SUBSCRIPTION-REAL-MONGO"

_SCHEMA_VERSION = "WILSY-SUBSCRIPTION-REGISTRY/V1"

_MONGO_URI = (
    os.getenv("WILSY_SUBSCRIPTION_MONGO_URI")
    or os.getenv("MONGODB_URI")
    or "mongodb://127.0.0.1:27017/wilsy"
)

_SERVER_SELECTION_TIMEOUT_MS = int(
    os.getenv(
        "WILSY_SUBSCRIPTION_MONGO_SERVER_SELECTION_MS",
        "5000",
    )
)

logger = logging.getLogger(
    "WilsyOS.SubscriptionRegistry"
)

mongo_client = MongoClient(
    _MONGO_URI,
    connect=False,
    retryWrites=True,
    serverSelectionTimeoutMS=_SERVER_SELECTION_TIMEOUT_MS,
)

mongo_database = mongo_client.get_default_database(
    "wilsy"
)

subscriptions_collection: Collection[dict[str, Any]] = (
    mongo_database.get_collection(
        "subscriptions",
        write_concern=WriteConcern(
            w="majority",
            j=True,
        ),
        read_concern=ReadConcern("majority"),
    )
)

_REQUIRED_PERSISTED_FIELDS = frozenset(
    {
        "tenant_id",
        "subscription_id",
        "plan_id",
        "plan",
        "amount",
        "currency",
        "billing_frequency",
        "start_date",
        "current_period_start",
        "current_period_end",
        "idempotency_key",
        "seal_nonce",
        "proof_hash",
        "merkle_root",
    }
)

_MUTABLE_UPDATE_FIELDS = frozenset(
    {
        "plan",
        "plan_id",
        "plan_name",
        "plan_features",
        "amount",
        "tax_amount",
        "currency",
        "billing_frequency",
        "collection_method",
        "trial_end_date",
        "current_period_start",
        "current_period_end",
        "status",
        "cancel_reason",
        "pause_reason",
        "pause_until",
        "payment_method_id",
        "credit_balance",
        "last_invoice_id",
        "last_platform_invoice_id",
        "tier",
        "onboarding_ref",
        "billing_mode",
        "end_date",
        "sector",
        "region",
        "compliance_flags",
        "metadata",
        "tags",
        "user",
    }
)


class SubscriptionRegistryError(RuntimeError):
    """Represent bounded subscription-persistence failure.

    Authority:
        Persistence/read-integrity signaling only.

    Tenant scope:
        Raising this exception never widens tenant scope or establishes tenant
        membership.

    Mutation:
        Infrastructure, invalid persisted truth and optimistic-concurrency
        failures are explicit; callers must not convert them into success or
        fabricated absence.

    Idempotency:
        Durable idempotency conflicts are explicit and never silently reused.

    Financial boundary:
        No execution or settlement authority. Kennel EOS remains exclusive.
    """


def _text(value: Any, field_name: str) -> str:
    """Normalize one bounded identifier without granting authority."""
    if not isinstance(value, str):
        raise ValueError(
            f"{field_name} must be a string"
        )

    normalized = value.strip()

    if not normalized:
        raise ValueError(
            f"{field_name} must be non-blank"
        )

    if len(normalized) > 256:
        raise ValueError(
            f"{field_name} exceeds maximum length 256"
        )

    return normalized


def _authorized_tenant(
    tenant_id_header: Any,
) -> str:
    """Require explicit upstream-authorized tenant scope.

    The compatibility name ``tenant_id_header`` does not make a raw HTTP header
    authoritative. Upstream Python identity/membership/permission composition
    remains mandatory.
    """
    try:
        return _text(
            tenant_id_header,
            "tenant_id",
        )
    except ValueError as error:
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_TENANT_REQUIRED"
        ) from error


def _canonical_json(value: Any) -> str:
    """Serialize deterministic command evidence for SHA3-512."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
        default=str,
    )


_CREATE_MATERIAL_SCHEMA = "WILSY-SUBSCRIPTION-CREATE/V1"
_SHA3_512_PREFIX = "sha3-512:"
_SHA3_512_HEX_LENGTH = 128


def _create_material(
    tenant_id: str,
    payload: dict[str, Any],
) -> str:
    """Return canonical persisted creation-command evidence.

    The material is immutable registry metadata. It is preserved across later
    subscription lifecycle mutation so durable idempotency can always be
    verified against the original normalized create command.
    """
    canonical_payload = dict(payload)
    canonical_payload["tenantId"] = tenant_id
    canonical_payload["idempotencyKey"] = _text(
        payload.get("idempotencyKey"),
        "idempotency_key",
    )

    return _canonical_json(
        {
            "schema": _CREATE_MATERIAL_SCHEMA,
            "tenant_id": tenant_id,
            "payload": canonical_payload,
        }
    )


def _fingerprint_create_material(
    create_material: str,
) -> str:
    """Return the exact SHA3-512 digest of canonical creation material."""
    return (
        _SHA3_512_PREFIX
        + hashlib.sha3_512(
            create_material.encode("utf-8")
        ).hexdigest()
    )


def _create_fingerprint(
    tenant_id: str,
    payload: dict[str, Any],
) -> str:
    """Bind durable create idempotency to canonical persisted material."""
    return _fingerprint_create_material(
        _create_material(
            tenant_id,
            payload,
        )
    )


def _valid_sha3_512_fingerprint(
    value: Any,
) -> bool:
    """Require exact lowercase SHA3-512 fingerprint syntax."""
    if not isinstance(value, str):
        return False

    if not value.startswith(
        _SHA3_512_PREFIX
    ):
        return False

    digest = value[
        len(_SHA3_512_PREFIX):
    ]

    return (
        len(digest)
        == _SHA3_512_HEX_LENGTH
        and all(
            character
            in "0123456789abcdef"
            for character in digest
        )
    )


def _validate_create_evidence(
    document: dict[str, Any],
) -> tuple[str, str]:
    """Validate immutable persisted create material and its digest.

    Validation is required before hydration, replay classification or lifecycle
    replacement. A syntactically valid but incorrect digest remains invalid
    persisted truth.
    """
    create_material = document.get(
        "_registry_create_material"
    )
    fingerprint = document.get(
        "_registry_create_fingerprint"
    )

    if (
        not isinstance(
            create_material,
            str,
        )
        or not create_material
        or not _valid_sha3_512_fingerprint(
            fingerprint
        )
    ):
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_INVALID_DOCUMENT"
        )

    try:
        decoded = json.loads(
            create_material
        )
    except (
        json.JSONDecodeError,
        TypeError,
    ) as error:
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_INVALID_DOCUMENT"
        ) from error

    if not isinstance(decoded, dict):
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_INVALID_DOCUMENT"
        )

    try:
        canonical = _canonical_json(
            decoded
        )
    except (
        TypeError,
        ValueError,
    ) as error:
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_INVALID_DOCUMENT"
        ) from error

    if canonical != create_material:
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_INVALID_DOCUMENT"
        )

    payload = decoded.get("payload")

    if (
        decoded.get("schema")
        != _CREATE_MATERIAL_SCHEMA
        or decoded.get("tenant_id")
        != document.get("tenant_id")
        or not isinstance(payload, dict)
        or payload.get("tenantId")
        != document.get("tenant_id")
        or payload.get("idempotencyKey")
        != document.get("idempotency_key")
    ):
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_INVALID_DOCUMENT"
        )

    expected = (
        _fingerprint_create_material(
            create_material
        )
    )

    assert isinstance(
        fingerprint,
        str,
    )

    if not hmac.compare_digest(
        fingerprint,
        expected,
    ):
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_INVALID_DOCUMENT"
        )

    return (
        create_material,
        fingerprint,
    )


def _collection() -> Collection[dict[str, Any]]:
    """Return configured subscription persistence without widening authority."""
    if subscriptions_collection is None:
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_UNAVAILABLE"
        )

    return subscriptions_collection


def _ensure_indexes() -> None:
    """Ensure deterministic tenant-scoped subscription persistence indexes."""
    collection = _collection()

    try:
        collection.create_index(
            [
                ("tenant_id", 1),
                ("subscription_id", 1),
            ],
            unique=True,
            name="tenant_subscription_unique",
        )
        collection.create_index(
            [
                ("tenant_id", 1),
                ("idempotency_key", 1),
            ],
            unique=True,
            name="tenant_idempotency_unique",
        )
        collection.create_index(
            [
                ("tenant_id", 1),
                ("status", 1),
            ],
            name="tenant_status",
        )
        collection.create_index(
            [
                ("tenant_id", 1),
                ("plan", 1),
            ],
            name="tenant_plan",
        )
    except PyMongoError as error:
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_UNAVAILABLE"
        ) from error


def _duplicate_key_kind(
    error: DuplicateKeyError,
) -> str | None:
    """Classify only the two governed subscription uniqueness contracts."""
    details = error.details

    if isinstance(details, dict):
        key_pattern = details.get(
            "keyPattern"
        )

        if isinstance(
            key_pattern,
            dict,
        ):
            fields = frozenset(
                str(field)
                for field in key_pattern
            )

            if fields == frozenset(
                {
                    "tenant_id",
                    "idempotency_key",
                }
            ):
                return "IDEMPOTENCY"

            if fields == frozenset(
                {
                    "tenant_id",
                    "subscription_id",
                }
            ):
                return "SUBSCRIPTION_ID"

        diagnostic = str(
            details.get(
                "errmsg",
                "",
            )
        )
    else:
        diagnostic = ""

    diagnostic = (
        diagnostic
        + " "
        + str(error)
    )

    if (
        "tenant_idempotency_unique"
        in diagnostic
    ):
        return "IDEMPOTENCY"

    if (
        "tenant_subscription_unique"
        in diagnostic
    ):
        return "SUBSCRIPTION_ID"

    return None


def _document_for(
    entity: SubscriptionEntity,
    *,
    create_material: str,
    create_fingerprint: str,
    revision: int,
) -> dict[str, Any]:
    """Serialize one valid entity plus immutable registry metadata."""
    document = entity.to_dict()

    document["_registry_schema"] = _SCHEMA_VERSION
    document["_registry_create_material"] = (
        create_material
    )
    document["_registry_create_fingerprint"] = (
        create_fingerprint
    )
    document["_registry_revision"] = revision

    return document


def _hydrate(
    document: dict[str, Any],
) -> SubscriptionEntity:
    """Hydrate canonical persisted truth or fail closed as invalid."""
    if document.get("_registry_schema") != _SCHEMA_VERSION:
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_INVALID_DOCUMENT"
        )

    if not _REQUIRED_PERSISTED_FIELDS <= document.keys():
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_INVALID_DOCUMENT"
        )

    _validate_create_evidence(
        document
    )

    revision = document.get(
        "_registry_revision"
    )

    if (
        isinstance(revision, bool)
        or not isinstance(revision, int)
        or revision < 1
    ):
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_INVALID_DOCUMENT"
        )

    payload = {
        key: value
        for key, value in document.items()
        if (
            key != "_id"
            and not key.startswith("_registry_")
        )
    }

    try:
        entity = SubscriptionEntity.from_dict(
            payload
        )
    except (
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_INVALID_DOCUMENT"
        ) from error

    if (
        entity.tenant_id != document["tenant_id"]
        or entity.subscription_id
        != document["subscription_id"]
        or entity.idempotency_key
        != document["idempotency_key"]
    ):
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_INVALID_DOCUMENT"
        )

    return entity


def _find_document(
    subscription_id: str,
    tenant_id: str,
) -> dict[str, Any] | None:
    """Read one tenant-bound subscription without cross-tenant disclosure."""
    try:
        return _collection().find_one(
            {
                "tenant_id": tenant_id,
                "subscription_id": subscription_id,
            }
        )
    except PyMongoError as error:
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_UNAVAILABLE"
        ) from error


def _replace_document(
    previous: dict[str, Any],
    entity: SubscriptionEntity,
) -> SubscriptionEntity:
    """Persist one optimistic tenant-bound lifecycle mutation."""
    revision = previous.get(
        "_registry_revision"
    )

    create_material, fingerprint = (
        _validate_create_evidence(
            previous
        )
    )

    if (
        isinstance(revision, bool)
        or not isinstance(revision, int)
        or revision < 1
    ):
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_INVALID_DOCUMENT"
        )

    replacement = _document_for(
        entity,
        create_material=create_material,
        create_fingerprint=fingerprint,
        revision=revision + 1,
    )

    try:
        result = _collection().replace_one(
            {
                "tenant_id": entity.tenant_id,
                "subscription_id":
                    entity.subscription_id,
                "_registry_revision": revision,
            },
            replacement,
        )
    except PyMongoError as error:
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_UNAVAILABLE"
        ) from error

    if result.matched_count != 1:
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_CONCURRENT_MODIFICATION"
        )

    return _hydrate(replacement)


def _all_for_tenant(
    tenant_id: str,
) -> list[SubscriptionEntity]:
    """Hydrate all canonical subscription truth for one tenant only."""
    try:
        documents = list(
            _collection().find(
                {"tenant_id": tenant_id}
            )
        )
    except PyMongoError as error:
        raise SubscriptionRegistryError(
            "SUBSCRIPTION_REGISTRY_UNAVAILABLE"
        ) from error

    return [
        _hydrate(document)
        for document in documents
    ]


class SubscriptionRegistry:
    """Canonical tenant-scoped Mongo subscription persistence service.

    Authority:
        Owns subscription persistence and lifecycle state only.

    Tenant scope:
        Every tenant-scoped method requires an explicit already-authorized
        tenant reference or a direct tenant argument where historically
        defined. Raw HTTP headers are not authority.

    Mutation:
        Create and lifecycle mutations persist in MongoDB. Mutations use durable
        tenant-scoped unique indexes and revision-checked replacements.

    Idempotency:
        Create requires an explicit key. Same tenant + key + canonical create
        fingerprint returns the exact persisted subscription. Same tenant + key
        + different fingerprint fails closed.

    Failure:
        Persistence outage, invalid persisted truth and concurrent mutation are
        explicit SubscriptionRegistryError conditions.

    Financial boundary:
        Commercial subscription truth does not execute or settle funds.
        Kennel EOS remains exclusive financial execution authority.
    """

    @classmethod
    def _period_end_from_start(
        cls,
        start: datetime,
        frequency: BillingFrequency,
    ) -> datetime:
        return start + timedelta(
            days=period_days_for_frequency(
                frequency
            )
        )

    @classmethod
    def _to_datetime(
        cls,
        value: Any,
    ) -> datetime | None:
        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(
                    value
                )
            except ValueError:
                return None

        return None

    @classmethod
    def _mutate(
        cls,
        subscription_id: str,
        tenant_id_header: Any,
        updater: Callable[
            [SubscriptionEntity],
            SubscriptionEntity,
        ],
    ) -> dict[str, Any]:
        tenant_id = _authorized_tenant(
            tenant_id_header
        )
        subscription_id = _text(
            subscription_id,
            "subscription_id",
        )

        previous = _find_document(
            subscription_id,
            tenant_id,
        )

        if previous is None:
            return {
                "success": False,
                "error": "Subscription not found",
            }

        entity = _hydrate(previous)

        try:
            replacement = updater(entity)
        except (TypeError, ValueError) as error:
            return {
                "success": False,
                "error": str(error),
            }

        persisted = _replace_document(
            previous,
            replacement,
        )

        return {
            "success": True,
            "subscription": persisted,
        }

    @classmethod
    def create(
        cls,
        payload: dict[str, Any],
        tenant_id_header: str | None = None,
    ) -> dict[str, Any]:
        """Persist one tenant subscription with durable create idempotency.

        Tenant:
            Requires already-authorized ``tenant_id_header``. If payload
            ``tenantId`` exists it must match exactly.

        Mutation:
            Inserts one canonical Mongo document only after validation.

        Idempotency:
            Explicit ``idempotencyKey`` is mandatory. Exact canonical replay
            returns the existing entity; conflicting reuse fails closed.

        Failure:
            Validation returns bounded failure dictionaries. Persistence and
            persisted-integrity failures raise SubscriptionRegistryError.

        Financial:
            Creates commercial subscription truth only; no payment execution or
            settlement authority.
        """
        tenant_id = _authorized_tenant(
            tenant_id_header
        )

        if not isinstance(payload, dict):
            return {
                "success": False,
                "error": "Invalid payload",
            }

        payload_tenant = payload.get(
            "tenantId"
        )

        if (
            payload_tenant is not None
            and str(payload_tenant).strip()
            != tenant_id
        ):
            return {
                "success": False,
                "error":
                    "SUBSCRIPTION_TENANT_SCOPE_MISMATCH",
            }

        required = (
            "planId",
            "plan",
            "amount",
            "currency",
            "billingFrequency",
            "startDate",
            "idempotencyKey",
        )

        for field_name in required:
            if field_name not in payload:
                return {
                    "success": False,
                    "error":
                        f"Missing required field: {field_name}",
                }

        try:
            idempotency_key = _text(
                payload["idempotencyKey"],
                "idempotency_key",
            )
        except ValueError as error:
            return {
                "success": False,
                "error": str(error),
            }

        create_material = _create_material(
            tenant_id,
            payload,
        )
        fingerprint = (
            _fingerprint_create_material(
                create_material
            )
        )

        _ensure_indexes()

        try:
            existing = _collection().find_one(
                {
                    "tenant_id": tenant_id,
                    "idempotency_key":
                        idempotency_key,
                }
            )
        except PyMongoError as error:
            raise SubscriptionRegistryError(
                "SUBSCRIPTION_REGISTRY_UNAVAILABLE"
            ) from error

        if existing is not None:
            existing_entity = _hydrate(
                existing
            )

            persisted_fingerprint = (
                existing[
                    "_registry_create_fingerprint"
                ]
            )

            if not hmac.compare_digest(
                persisted_fingerprint,
                fingerprint,
            ):
                return {
                    "success": False,
                    "error":
                        "SUBSCRIPTION_IDEMPOTENCY_CONFLICT",
                }

            return {
                "success": True,
                "subscription":
                    existing_entity,
                "replayed": True,
            }

        try:
            plan = PlanTiers(
                str(payload["plan"]).upper()
            )
            frequency = BillingFrequency(
                str(
                    payload["billingFrequency"]
                ).lower()
            )

            start_date = cls._to_datetime(
                payload["startDate"]
            )

            if start_date is None:
                return {
                    "success": False,
                    "error": "Invalid startDate",
                }

            period_start = (
                cls._to_datetime(
                    payload.get(
                        "currentPeriodStart"
                    )
                )
                or start_date
            )

            period_end = cls._to_datetime(
                payload.get(
                    "currentPeriodEnd"
                )
            )

            if period_end is None:
                period_end = (
                    cls._period_end_from_start(
                        period_start,
                        frequency,
                    )
                )

            status_value = SubscriptionStatus(
                str(
                    payload.get(
                        "status",
                        "active",
                    )
                ).lower()
            )

            collection_method = CollectionMethod(
                str(
                    payload.get(
                        "collectionMethod",
                        "charge_automatically",
                    )
                ).lower()
            )

            tier = PlanTiers(
                str(
                    payload.get(
                        "tier",
                        plan.value,
                    )
                ).upper()
            )

            billing_mode = str(
                payload.get(
                    "billingMode",
                    "PLATFORM",
                )
            ).upper()

            if billing_mode not in {
                "PLATFORM",
                "CLIENT",
            }:
                return {
                    "success": False,
                    "error":
                        "billingMode must be PLATFORM or CLIENT",
                }

            entity = SubscriptionEntity(
                tenant_id=tenant_id,
                plan_id=_text(
                    payload["planId"],
                    "plan_id",
                ),
                plan=plan,
                amount=float(
                    payload["amount"]
                ),
                currency=_text(
                    payload["currency"],
                    "currency",
                ).upper(),
                billing_frequency=frequency,
                start_date=start_date,
                current_period_start=period_start,
                current_period_end=period_end,
                idempotency_key=idempotency_key,
                kennel_shard=str(
                    payload.get(
                        "kennelShard",
                        "EOS_PRIMARY",
                    )
                ),
                plan_name=payload.get(
                    "planName"
                ),
                plan_features=list(
                    payload.get(
                        "planFeatures",
                        [],
                    )
                ),
                tax_amount=float(
                    payload.get(
                        "taxAmount",
                        0,
                    )
                ),
                collection_method=
                    collection_method,
                trial_end_date=
                    cls._to_datetime(
                        payload.get(
                            "trialEndDate"
                        )
                    ),
                status=status_value,
                payment_method_id=
                    payload.get(
                        "paymentMethodId"
                    ),
                credit_balance=float(
                    payload.get(
                        "creditBalance",
                        0,
                    )
                ),
                last_invoice_id=
                    payload.get(
                        "lastInvoiceId"
                    ),
                last_platform_invoice_id=
                    payload.get(
                        "lastPlatformInvoiceId"
                    ),
                seal_nonce=str(
                    payload.get(
                        "sealNonce",
                        uuid.uuid4().hex,
                    )
                ),
                proof_hash=str(
                    payload.get(
                        "proofHash",
                        "",
                    )
                ),
                merkle_root=str(
                    payload.get(
                        "merkleRoot",
                        "",
                    )
                ),
                trace_id=payload.get(
                    "traceId"
                ),
                tier=tier,
                onboarding_ref=
                    payload.get(
                        "onboardingRef"
                    ),
                billing_mode=billing_mode,
                end_date=cls._to_datetime(
                    payload.get(
                        "endDate"
                    )
                ),
                sector=payload.get(
                    "sector"
                ),
                region=payload.get(
                    "region"
                ),
                compliance_flags=dict(
                    payload.get(
                        "complianceFlags",
                        {},
                    )
                ),
                metadata=dict(
                    payload.get(
                        "metadata",
                        {},
                    )
                ),
                tags=list(
                    payload.get(
                        "tags",
                        [],
                    )
                ),
            )

            proof = entity.generate_proof(
                action="create",
                metadata={
                    "source":
                        "subscription_registry"
                },
            )

            audit = AuditEntry(
                action=AuditAction.CREATE,
                timestamp=datetime.now(
                    timezone.utc
                ),
                user=str(
                    payload.get(
                        "user",
                        "SYSTEM",
                    )
                ),
                reason="Subscription created",
                new_status=entity.status,
                tier=entity.tier,
                billing_mode=
                    entity.billing_mode,
                proof_hash=proof,
            )

            final_data = entity.to_dict()
            final_data["proof_hash"] = proof
            final_data["audit_trail"] = [
                audit.to_dict()
            ]

            final_entity = (
                SubscriptionEntity.from_dict(
                    final_data
                )
            )

            document = _document_for(
                final_entity,
                create_material=
                    create_material,
                create_fingerprint=
                    fingerprint,
                revision=1,
            )

            try:
                _collection().insert_one(
                    document
                )
            except DuplicateKeyError as error:
                duplicate_kind = (
                    _duplicate_key_kind(
                        error
                    )
                )

                if (
                    duplicate_kind
                    == "SUBSCRIPTION_ID"
                ):
                    return {
                        "success": False,
                        "error":
                            "SUBSCRIPTION_ID_COLLISION",
                    }

                if (
                    duplicate_kind
                    != "IDEMPOTENCY"
                ):
                    raise SubscriptionRegistryError(
                        "SUBSCRIPTION_REGISTRY_UNCLASSIFIED_DUPLICATE_KEY"
                    ) from error

                try:
                    replay = (
                        _collection().find_one(
                            {
                                "tenant_id":
                                    tenant_id,
                                "idempotency_key":
                                    idempotency_key,
                            }
                        )
                    )
                except PyMongoError as lookup_error:
                    raise SubscriptionRegistryError(
                        "SUBSCRIPTION_REGISTRY_UNAVAILABLE"
                    ) from lookup_error

                if replay is None:
                    raise SubscriptionRegistryError(
                        "SUBSCRIPTION_REGISTRY_CONCURRENT_MODIFICATION"
                    ) from error

                replay_entity = _hydrate(
                    replay
                )

                persisted_fingerprint = (
                    replay[
                        "_registry_create_fingerprint"
                    ]
                )

                if hmac.compare_digest(
                    persisted_fingerprint,
                    fingerprint,
                ):
                    return {
                        "success": True,
                        "subscription":
                            replay_entity,
                        "replayed": True,
                    }

                return {
                    "success": False,
                    "error":
                        "SUBSCRIPTION_IDEMPOTENCY_CONFLICT",
                }
            except PyMongoError as error:
                raise SubscriptionRegistryError(
                    "SUBSCRIPTION_REGISTRY_UNAVAILABLE"
                ) from error

            return {
                "success": True,
                "subscription": final_entity,
                "replayed": False,
            }

        except (
            TypeError,
            ValueError,
        ) as error:
            return {
                "success": False,
                "error": str(error),
            }

    @classmethod
    def get(
        cls,
        subscription_id: str,
        tenant_id_header: str | None = None,
    ) -> SubscriptionEntity | None:
        """Read one tenant-bound subscription.

        Tenant:
            Explicit already-authorized tenant scope is mandatory.

        Mutation:
            None.

        Failure:
            Cross-tenant lookup appears absent. Invalid persisted truth or
            infrastructure failure is explicit.

        Financial:
            Read-only commercial state; no execution authority.
        """
        tenant_id = _authorized_tenant(
            tenant_id_header
        )
        subscription_id = _text(
            subscription_id,
            "subscription_id",
        )

        document = _find_document(
            subscription_id,
            tenant_id,
        )

        if document is None:
            return None

        return _hydrate(document)

    @classmethod
    def list(
        cls,
        tenant_id_header: str | None = None,
        status: SubscriptionStatus | None = None,
        plan: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> dict[str, Any]:
        """List subscriptions inside one authorized tenant only.

        Tenant:
            Mandatory explicit scope.

        Mutation:
            None.

        Failure:
            Invalid pagination or persisted truth fails closed; persistence
            outage is never converted into an empty healthy list.

        Financial:
            Read-only commercial projection.
        """
        tenant_id = _authorized_tenant(
            tenant_id_header
        )

        if (
            isinstance(page, bool)
            or not isinstance(page, int)
            or page < 1
            or isinstance(limit, bool)
            or not isinstance(limit, int)
            or limit < 1
            or limit > 1000
        ):
            raise ValueError(
                "Invalid pagination"
            )

        query: dict[str, Any] = {
            "tenant_id": tenant_id
        }

        if status is not None:
            query["status"] = status.value

        if plan is not None:
            query["plan"] = _text(
                plan,
                "plan",
            ).upper()

        try:
            total = _collection().count_documents(
                query
            )
            documents = list(
                _collection()
                .find(query)
                .sort("start_date", -1)
                .skip((page - 1) * limit)
                .limit(limit)
            )
        except PyMongoError as error:
            raise SubscriptionRegistryError(
                "SUBSCRIPTION_REGISTRY_UNAVAILABLE"
            ) from error

        items = [
            _hydrate(document)
            for document in documents
        ]

        pages = (
            (total + limit - 1) // limit
            if total
            else 0
        )

        return {
            "items": items,
            "total": total,
            "pages": pages,
        }

    @classmethod
    def update(
        cls,
        subscription_id: str,
        payload: dict[str, Any],
        tenant_id_header: str | None = None,
    ) -> dict[str, Any]:
        """Persist a bounded tenant-scoped subscription update.

        Tenant:
            Mandatory explicit upstream-authorized scope.

        Mutation:
            Only established mutable commercial/lifecycle fields are admitted;
            tenant identity, subscription identity, create-idempotency evidence,
            registry revision and proof history cannot be caller-replaced.

        Idempotency:
            Uses optimistic revision matching; conflicting concurrent mutation
            fails closed.

        Financial:
            Does not execute or settle money.
        """
        if (
            not isinstance(payload, dict)
            or not payload
        ):
            return {
                "success": False,
                "error":
                    "SUBSCRIPTION_UPDATE_EMPTY",
            }

        fields = frozenset(payload)

        if not fields <= _MUTABLE_UPDATE_FIELDS:
            return {
                "success": False,
                "error":
                    "SUBSCRIPTION_UPDATE_INVALID_FIELDS",
            }

        def updater(
            existing: SubscriptionEntity,
        ) -> SubscriptionEntity:
            values = existing.to_dict()
            actor = str(
                payload.get(
                    "user",
                    "SYSTEM",
                )
            )

            for key, value in payload.items():
                if key == "user":
                    continue
                values[key] = value

            candidate = (
                SubscriptionEntity.from_dict(
                    values
                )
            )

            proof = candidate.generate_proof(
                action="update",
                metadata={
                    "fields":
                        sorted(
                            key
                            for key in payload
                            if key != "user"
                        )
                },
            )

            audit = AuditEntry(
                action=AuditAction.UPDATE,
                timestamp=datetime.now(
                    timezone.utc
                ),
                user=actor,
                reason="Subscription updated",
                previous_status=
                    existing.status,
                new_status=candidate.status,
                tier=candidate.tier,
                billing_mode=
                    candidate.billing_mode,
                proof_hash=proof,
            )

            final = candidate.to_dict()
            final["proof_hash"] = proof
            final["audit_trail"] = [
                *[
                    item.to_dict()
                    for item in
                    existing.audit_trail
                ],
                audit.to_dict(),
            ]

            return (
                SubscriptionEntity.from_dict(
                    final
                )
            )

        return cls._mutate(
            subscription_id,
            tenant_id_header,
            updater,
        )

    @classmethod
    def archive(
        cls,
        subscription_id: str,
        tenant_id_header: str | None = None,
    ) -> bool:
        """Archive via the established cancelled lifecycle without execution.

        Tenant:
            Mandatory explicit authorized scope.

        Mutation:
            Persists cancellation with reason ``archived``.

        Financial:
            Does not move money or establish settlement.
        """
        result = cls.cancel(
            subscription_id,
            tenant_id_header=
                tenant_id_header,
            cancel_reason="archived",
            cancel_at_period_end=False,
        )

        return bool(
            result.get("success")
        )

    @classmethod
    def pause(
        cls,
        subscription_id: str,
        tenant_id_header: str | None = None,
        pause_reason: str | None = None,
        pause_until: str | None = None,
    ) -> dict[str, Any]:
        """Persist ACTIVE -> PAUSED inside one authorized tenant.

        Mutation:
            Adds immutable audit evidence and revision-checked Mongo state.

        Failure:
            Non-active lifecycle state fails closed.

        Financial:
            Pause state is commercial truth only.
        """
        def updater(
            sub: SubscriptionEntity,
        ) -> SubscriptionEntity:
            if sub.status != SubscriptionStatus.ACTIVE:
                raise ValueError(
                    "Only active subscriptions can be paused"
                )

            occurred_at = datetime.now(
                timezone.utc
            )
            until = cls._to_datetime(
                pause_until
            )

            proof = sub.generate_proof(
                action="pause",
                metadata={
                    "reason": pause_reason
                },
            )

            audit = AuditEntry(
                action=AuditAction.PAUSE,
                timestamp=occurred_at,
                user="SYSTEM",
                reason=pause_reason,
                previous_status=sub.status,
                new_status=
                    SubscriptionStatus.PAUSED,
                tier=sub.tier,
                billing_mode=sub.billing_mode,
                proof_hash=proof,
            )

            values = sub.to_dict()
            values.update(
                {
                    "status":
                        SubscriptionStatus.PAUSED.value,
                    "paused_at":
                        occurred_at.isoformat(),
                    "pause_reason":
                        pause_reason,
                    "pause_until":
                        (
                            until.isoformat()
                            if until
                            else None
                        ),
                    "proof_hash": proof,
                    "audit_trail": [
                        *[
                            item.to_dict()
                            for item in
                            sub.audit_trail
                        ],
                        audit.to_dict(),
                    ],
                }
            )

            return (
                SubscriptionEntity.from_dict(
                    values
                )
            )

        return cls._mutate(
            subscription_id,
            tenant_id_header,
            updater,
        )

    @classmethod
    def resume(
        cls,
        subscription_id: str,
        tenant_id_header: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Persist PAUSED -> ACTIVE inside one authorized tenant.

        Mutation:
            Clears pause context and appends audit evidence.

        Failure:
            Non-paused lifecycle state fails closed.

        Financial:
            Resume does not execute or settle funds.
        """
        def updater(
            sub: SubscriptionEntity,
        ) -> SubscriptionEntity:
            if sub.status != SubscriptionStatus.PAUSED:
                raise ValueError(
                    "Only paused subscriptions can be resumed"
                )

            occurred_at = datetime.now(
                timezone.utc
            )

            proof = sub.generate_proof(
                action="resume",
                metadata=metadata or {},
            )

            audit = AuditEntry(
                action=AuditAction.RESUME,
                timestamp=occurred_at,
                user="SYSTEM",
                reason="Resumed",
                previous_status=sub.status,
                new_status=
                    SubscriptionStatus.ACTIVE,
                tier=sub.tier,
                billing_mode=sub.billing_mode,
                proof_hash=proof,
            )

            values = sub.to_dict()
            values.update(
                {
                    "status":
                        SubscriptionStatus.ACTIVE.value,
                    "resumed_at":
                        occurred_at.isoformat(),
                    "pause_reason": None,
                    "pause_until": None,
                    "proof_hash": proof,
                    "audit_trail": [
                        *[
                            item.to_dict()
                            for item in
                            sub.audit_trail
                        ],
                        audit.to_dict(),
                    ],
                }
            )

            return (
                SubscriptionEntity.from_dict(
                    values
                )
            )

        return cls._mutate(
            subscription_id,
            tenant_id_header,
            updater,
        )

    @classmethod
    def cancel(
        cls,
        subscription_id: str,
        tenant_id_header: str | None = None,
        cancel_reason: str | None = None,
        cancel_at_period_end: bool = True,
    ) -> dict[str, Any]:
        """Persist cancellation without claiming payment or settlement.

        Tenant:
            Mandatory authorized scope.

        Mutation:
            Writes CANCELLED status and append-only audit evidence.

        Financial:
            Cancellation is not a refund, payment execution, release or
            settlement.
        """
        def updater(
            sub: SubscriptionEntity,
        ) -> SubscriptionEntity:
            if sub.status in {
                SubscriptionStatus.CANCELLED,
                SubscriptionStatus.EXPIRED,
            }:
                raise ValueError(
                    "Subscription is already cancelled or expired"
                )

            occurred_at = datetime.now(
                timezone.utc
            )

            cancel_at = (
                sub.current_period_end
                if cancel_at_period_end
                else None
            )

            proof = sub.generate_proof(
                action="cancel",
                metadata={
                    "reason":
                        cancel_reason,
                    "at_period_end":
                        cancel_at_period_end,
                },
            )

            audit = AuditEntry(
                action=AuditAction.CANCEL,
                timestamp=occurred_at,
                user="SYSTEM",
                reason=cancel_reason,
                previous_status=sub.status,
                new_status=
                    SubscriptionStatus.CANCELLED,
                tier=sub.tier,
                billing_mode=sub.billing_mode,
                proof_hash=proof,
            )

            values = sub.to_dict()
            values.update(
                {
                    "status":
                        SubscriptionStatus.CANCELLED.value,
                    "cancelled_at":
                        occurred_at.isoformat(),
                    "cancel_reason":
                        cancel_reason,
                    "cancel_at":
                        (
                            cancel_at.isoformat()
                            if cancel_at
                            else None
                        ),
                    "proof_hash": proof,
                    "audit_trail": [
                        *[
                            item.to_dict()
                            for item in
                            sub.audit_trail
                        ],
                        audit.to_dict(),
                    ],
                }
            )

            return (
                SubscriptionEntity.from_dict(
                    values
                )
            )

        return cls._mutate(
            subscription_id,
            tenant_id_header,
            updater,
        )

    @classmethod
    def upgrade(
        cls,
        subscription_id: str,
        tenant_id_header: str | None = None,
        upgrade_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Persist one explicit plan upgrade inside the authorized tenant.

        Mutation:
            Plan/plan-id/amount/tier and audit evidence only.

        Financial:
            Pricing state does not execute collection or settlement.
        """
        data = upgrade_data or {}

        def updater(
            sub: SubscriptionEntity,
        ) -> SubscriptionEntity:
            new_plan = PlanTiers(
                str(
                    data.get(
                        "newPlan",
                        "",
                    )
                ).upper()
            )

            new_amount = float(
                data.get(
                    "newAmount",
                    sub.amount,
                )
            )

            new_plan_id = str(
                data.get(
                    "newPlanId",
                    sub.plan_id,
                )
            )

            occurred_at = datetime.now(
                timezone.utc
            )

            proof = sub.generate_proof(
                action="upgrade",
                metadata=data,
            )

            audit = AuditEntry(
                action=AuditAction.UPGRADE,
                timestamp=occurred_at,
                user="SYSTEM",
                reason=(
                    "Upgraded to "
                    + new_plan.value
                ),
                previous_status=sub.status,
                new_status=sub.status,
                tier=new_plan,
                billing_mode=sub.billing_mode,
                proof_hash=proof,
            )

            values = sub.to_dict()
            values.update(
                {
                    "plan": new_plan.value,
                    "plan_id": new_plan_id,
                    "amount": new_amount,
                    "tier": new_plan.value,
                    "proof_hash": proof,
                    "audit_trail": [
                        *[
                            item.to_dict()
                            for item in
                            sub.audit_trail
                        ],
                        audit.to_dict(),
                    ],
                }
            )

            return (
                SubscriptionEntity.from_dict(
                    values
                )
            )

        return cls._mutate(
            subscription_id,
            tenant_id_header,
            updater,
        )

    @classmethod
    def downgrade(
        cls,
        subscription_id: str,
        tenant_id_header: str | None = None,
        downgrade_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Persist one explicit plan downgrade inside the authorized tenant.

        Mutation:
            Plan/plan-id/amount/tier and audit evidence only.

        Financial:
            Pricing state does not execute payment or settlement.
        """
        data = downgrade_data or {}

        def updater(
            sub: SubscriptionEntity,
        ) -> SubscriptionEntity:
            new_plan = PlanTiers(
                str(
                    data.get(
                        "newPlan",
                        "",
                    )
                ).upper()
            )

            new_amount = float(
                data.get(
                    "newAmount",
                    sub.amount,
                )
            )

            new_plan_id = str(
                data.get(
                    "newPlanId",
                    sub.plan_id,
                )
            )

            occurred_at = datetime.now(
                timezone.utc
            )

            proof = sub.generate_proof(
                action="downgrade",
                metadata=data,
            )

            audit = AuditEntry(
                action=AuditAction.DOWNGRADE,
                timestamp=occurred_at,
                user="SYSTEM",
                reason=(
                    "Downgraded to "
                    + new_plan.value
                ),
                previous_status=sub.status,
                new_status=sub.status,
                tier=new_plan,
                billing_mode=sub.billing_mode,
                proof_hash=proof,
            )

            values = sub.to_dict()
            values.update(
                {
                    "plan": new_plan.value,
                    "plan_id": new_plan_id,
                    "amount": new_amount,
                    "tier": new_plan.value,
                    "proof_hash": proof,
                    "audit_trail": [
                        *[
                            item.to_dict()
                            for item in
                            sub.audit_trail
                        ],
                        audit.to_dict(),
                    ],
                }
            )

            return (
                SubscriptionEntity.from_dict(
                    values
                )
            )

        return cls._mutate(
            subscription_id,
            tenant_id_header,
            updater,
        )

    @classmethod
    def reactivate(
        cls,
        subscription_id: str,
        tenant_id_header: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Persist CANCELLED -> ACTIVE without inferring financial state.

        Mutation:
            Clears cancellation context and appends audit evidence.

        Financial:
            Reactivation is not payment authorization, execution or settlement.
        """
        def updater(
            sub: SubscriptionEntity,
        ) -> SubscriptionEntity:
            if sub.status != SubscriptionStatus.CANCELLED:
                raise ValueError(
                    "Only cancelled subscriptions can be reactivated"
                )

            occurred_at = datetime.now(
                timezone.utc
            )

            proof = sub.generate_proof(
                action="reactivate",
                metadata=metadata or {},
            )

            audit = AuditEntry(
                action=
                    AuditAction.REACTIVATE,
                timestamp=occurred_at,
                user="SYSTEM",
                reason="Reactivated",
                previous_status=sub.status,
                new_status=
                    SubscriptionStatus.ACTIVE,
                tier=sub.tier,
                billing_mode=sub.billing_mode,
                proof_hash=proof,
            )

            values = sub.to_dict()
            values.update(
                {
                    "status":
                        SubscriptionStatus.ACTIVE.value,
                    "reactivated_at":
                        occurred_at.isoformat(),
                    "cancel_reason": None,
                    "cancel_at": None,
                    "proof_hash": proof,
                    "audit_trail": [
                        *[
                            item.to_dict()
                            for item in
                            sub.audit_trail
                        ],
                        audit.to_dict(),
                    ],
                }
            )

            return (
                SubscriptionEntity.from_dict(
                    values
                )
            )

        return cls._mutate(
            subscription_id,
            tenant_id_header,
            updater,
        )

    @classmethod
    def get_audit(
        cls,
        subscription_id: str,
        tenant_id_header: str | None = None,
    ) -> list[dict[str, Any]] | None:
        """Return audit evidence for one authorized tenant subscription.

        Mutation:
            None.

        Tenant:
            Cross-tenant lookup appears absent.

        Financial:
            Audit evidence cannot establish settlement.
        """
        entity = cls.get(
            subscription_id,
            tenant_id_header,
        )

        if entity is None:
            return None

        return [
            audit.to_dict()
            for audit in entity.audit_trail
        ]

    @classmethod
    def get_metrics(
        cls,
        tenant_id: str,
    ) -> dict[str, Any]:
        """Compute subscription metrics from real persisted tenant truth.

        Tenant:
            ``tenant_id`` must be an already-authorized tenant scope.

        Mutation:
            None.

        Failure:
            Persistence failure is explicit and never converted into fabricated
            zero metrics.

        Financial:
            MRR/ARR are commercial analytics, not executed or settled money.
        """
        tenant = _authorized_tenant(
            tenant_id
        )

        subscriptions = _all_for_tenant(
            tenant
        )

        active = [
            item
            for item in subscriptions
            if item.status in {
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.TRIAL,
            }
        ]

        return {
            "totalSubscriptions":
                len(subscriptions),
            "activeSubscriptions":
                sum(
                    item.status
                    == SubscriptionStatus.ACTIVE
                    for item in subscriptions
                ),
            "trialSubscriptions":
                sum(
                    item.status
                    == SubscriptionStatus.TRIAL
                    for item in subscriptions
                ),
            "pausedSubscriptions":
                sum(
                    item.status
                    == SubscriptionStatus.PAUSED
                    for item in subscriptions
                ),
            "cancelledSubscriptions":
                sum(
                    item.status
                    == SubscriptionStatus.CANCELLED
                    for item in subscriptions
                ),
            "pastDueSubscriptions":
                sum(
                    item.status
                    == SubscriptionStatus.PAST_DUE
                    for item in subscriptions
                ),
            "totalMRR":
                sum(
                    to_monthly_amount(
                        item.amount,
                        item.billing_frequency,
                    )
                    for item in active
                ),
            "totalARR":
                sum(
                    to_annual_amount(
                        item.amount,
                        item.billing_frequency,
                    )
                    for item in active
                ),
            "totalCreditBalance":
                sum(
                    item.credit_balance
                    for item in subscriptions
                ),
        }

    @classmethod
    def detect_anomalies(
        cls,
        tenant_id: str,
        options: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Detect and audit bounded subscription anomalies for one tenant.

        Tenant:
            Requires explicit already-authorized tenant scope.

        Mutation:
            Detection appends persisted anomaly audit evidence for detected
            subscriptions. It does not modify entitlement or financial
            execution state.

        Failure:
            Invalid persisted truth or infrastructure failure fails closed.

        Financial:
            Anomaly detection is advisory evidence, never payment authority.
        """
        tenant = _authorized_tenant(
            tenant_id
        )
        options = options or {}

        limit_raw = options.get(
            "limit",
            100,
        )

        if (
            isinstance(limit_raw, bool)
            or not isinstance(limit_raw, int)
            or limit_raw < 1
            or limit_raw > 1000
        ):
            raise ValueError(
                "Invalid anomaly limit"
            )

        subscriptions = sorted(
            _all_for_tenant(tenant),
            key=lambda item:
                item.start_date,
            reverse=True,
        )[:limit_raw]

        anomalies: list[
            dict[str, Any]
        ] = []

        for sub in subscriptions:
            if sub.amount < 0:
                anomalies.append(
                    {
                        "subscriptionId":
                            sub.subscription_id,
                        "type":
                            "NEGATIVE_AMOUNT",
                        "severity":
                            "CRITICAL",
                        "description":
                            "Subscription amount is negative",
                        "value":
                            sub.amount,
                    }
                )

            if not sub.onboarding_ref:
                anomalies.append(
                    {
                        "subscriptionId":
                            sub.subscription_id,
                        "type":
                            "MISSING_ONBOARDING_REF",
                        "severity":
                            "WARNING",
                        "description":
                            "Subscription created without onboardingRef",
                    }
                )

        seen: dict[str, str] = {}

        for sub in subscriptions:
            if not sub.onboarding_ref:
                continue

            previous = seen.get(
                sub.onboarding_ref
            )

            if previous is not None:
                anomalies.append(
                    {
                        "subscriptionId":
                            sub.subscription_id,
                        "duplicateWith":
                            previous,
                        "type":
                            "DUPLICATE_ONBOARDING_REF",
                        "severity":
                            "WARNING",
                        "description":
                            "Same onboardingRef used for multiple subscriptions",
                        "value":
                            sub.onboarding_ref,
                    }
                )
            else:
                seen[
                    sub.onboarding_ref
                ] = sub.subscription_id

        if len(subscriptions) >= 2:
            chronological = sorted(
                subscriptions,
                key=lambda item:
                    item.start_date,
            )

            previous = chronological[-2]
            current = chronological[-1]

            if (
                previous.tier is not None
                and current.tier is not None
            ):
                tier_order = [
                    item.value
                    for item in PlanTiers
                ]

                previous_index = (
                    tier_order.index(
                        previous.tier.value
                    )
                )
                current_index = (
                    tier_order.index(
                        current.tier.value
                    )
                )

                if (
                    abs(
                        current_index
                        - previous_index
                    )
                    > 2
                ):
                    anomalies.append(
                        {
                            "subscriptionId":
                                current.subscription_id,
                            "type":
                                "SUSPICIOUS_TIER_JUMP",
                            "severity":
                                "WARNING",
                            "description":
                                (
                                    "Jump from "
                                    f"{previous.tier.value} "
                                    "to "
                                    f"{current.tier.value} "
                                    "in one renewal"
                                ),
                            "value": {
                                "previous":
                                    previous.tier.value,
                                "current":
                                    current.tier.value,
                            },
                        }
                    )

        for anomaly in anomalies:
            subscription_id = str(
                anomaly[
                    "subscriptionId"
                ]
            )

            def append_audit(
                sub: SubscriptionEntity,
                *,
                current_anomaly:
                    dict[str, Any] = anomaly,
            ) -> SubscriptionEntity:
                proof = sub.generate_proof(
                    action=
                        "anomaly_detected",
                    metadata={
                        "anomaly":
                            current_anomaly
                    },
                )

                audit = AuditEntry(
                    action=
                        AuditAction.ANOMALY_DETECTED,
                    timestamp=datetime.now(
                        timezone.utc
                    ),
                    user=
                        "SYSTEM_ANOMALY",
                    reason=str(
                        current_anomaly[
                            "type"
                        ]
                    ),
                    metadata={
                        "anomaly":
                            current_anomaly
                    },
                    proof_hash=proof,
                )

                values = sub.to_dict()
                values["proof_hash"] = proof
                values["audit_trail"] = [
                    *[
                        item.to_dict()
                        for item in
                        sub.audit_trail
                    ],
                    audit.to_dict(),
                ]

                return (
                    SubscriptionEntity.from_dict(
                        values
                    )
                )

            result = cls._mutate(
                subscription_id,
                tenant,
                append_audit,
            )

            if not result.get("success"):
                raise SubscriptionRegistryError(
                    "SUBSCRIPTION_REGISTRY_ANOMALY_AUDIT_FAILED"
                )

        return anomalies

    @classmethod
    def health_check(
        cls,
    ) -> dict[str, Any]:
        """Return bounded persistence health without exposing tenant truth.

        Tenant:
            No tenant data, identifiers or global subscription count is exposed.

        Mutation:
            None.

        Failure:
            Mongo outage reports DEGRADED rather than fabricated OPERATIONAL.

        Financial:
            No financial authority.
        """
        try:
            _collection().database.client.admin.command(
                "ping"
            )
        except PyMongoError:
            return {
                "status": "DEGRADED",
                "version": VERSION,
                "store_type": "mongo",
                "persistence": "UNAVAILABLE",
            }

        return {
            "status": "OPERATIONAL",
            "version": VERSION,
            "store_type": "mongo",
            "persistence": "READY",
        }


__all__ = [
    "SubscriptionRegistry",
    "SubscriptionRegistryError",
    "VERSION",
]

# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: tools/eos/saas/billing/subscription_registry.py
# VERSION: v1.1.1-SUBSCRIPTION-REAL-MONGO
# AUTHORITY BOUNDARY:
#   Canonical tenant-scoped subscription persistence and lifecycle mutation
#   only. Authentication, membership, permission, AI entitlement, AI metering,
#   payment execution and settlement remain outside this registry.
# TENANT POSTURE:
#   Every subscription persistence query is tenant-keyed. The compatibility
#   tenant_id_header argument is already-authorized scope, not raw-header
#   authority. Cross-tenant absence does not disclose another tenant's record.
# FAIL-CLOSED POSTURE:
#   Invalid persisted truth, missing tenant scope, infrastructure failure,
#   idempotency conflict and concurrent revision conflict are explicit.
# FINANCIAL EXECUTION AUTHORITY:
#   Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
