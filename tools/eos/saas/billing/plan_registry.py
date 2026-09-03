# -*- coding: utf-8 -*-
"""
TITLE:
    WILSY OS — Sovereign Plan Registry — Real Mongo Persistence

VERSION:
    v1.2.0-EXACT-TENANT-SCOPE

AUTHORITY:
    Wilsy OS Core Governance

PURPOSE:
    Own durable canonical Plan catalogue persistence and lifecycle orchestration
    while delegating all commercial-state validation and evidence generation to
    PlanEntity.

EPITOME:
    Durable catalogue truth is accepted only when canonical PlanEntity evidence
    hydrates successfully from MongoDB; persistence failure is never absence.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/plan_registry.py

OWNERSHIP:
    Python EOS SaaS / Billing — canonical Plan catalogue persistence owner.

COLLABORATION:
    PlanEntity owns commercial value validation, canonical state history,
    deterministic proofs and audit evidence.
    PlanRegistry owns catalogue persistence and lifecycle orchestration only.
    Plan HTTP authorization remains a separately certified phase.

CLASSIFICATION:
    Production Artifact

CERTIFICATION DATE:
    2026-09-03

CHANGELOG:
    2026-09-03 v1.2.0-EXACT-TENANT-SCOPE
        - Adds backwards-compatible keyword-only exact_tenant scope.
        - Default global-plus-tenant catalogue semantics remain unchanged.
        - Exact mode requires persisted Plan tenant ownership equality.
    2026-09-03 v1.1.1-STORAGE-ENVELOPE-CAS
        - Adds immutable Mongo identity plus monotonic _registry_revision
          transport evidence for optimistic lifecycle mutation.
        - Requires exact canonical PlanEntity serialization after removing only
          declared Mongo transport fields.
        - Rejects stale revision, replacement identity and competing persisted
          fields before catalogue mutation can succeed.
        - Gates successful lifecycle logging behind WILSY_MODEL_DEBUG.
        - Closes the P2R1 storage/CAS/canonicalization/logging Codex findings.
    2026-09-03 v1.1.0-PLAN-REAL-MONGO
        - Replaces in-memory catalogue authority with direct PyMongo persistence.
        - Persists canonical PlanEntity.to_dict() evidence without a second schema.
        - Adds deterministic fail-closed Mongo index contracts and majority
          read/write durability.
        - Preserves global plan-id/idempotency uniqueness and existing
          global-plan/tenant-scope catalogue semantics.
        - Adds optimistic compare-and-swap lifecycle persistence.
        - Makes persistence, hydration and index failures distinguishable from
          genuine catalogue absence.
    2026-09-03 v1.0.3-DOMAIN-PRICE-PASSTHROUGH
        - Removes destructive Registry float coercion before PlanEntity price
          validation.
        - Adopts PlanEntity integrity_root constructor input while preserving
          merkleRoot only as compatibility input.
        - Adds current governance/authority boundary metadata.
    2026-08-19 v1.0.2-FIXED
        - Fixed active conversion/type issues and timestamp construction.
    2026-08-19 v1.0.1-WILSY-ID
        - Changed generated IDs to WILSYPLAN-* identity.
    2026-08-19 v1.0.0-INSTITUTIONAL
        - Initial production release.

COMPLIANCE:
    POPIA §19 | GDPR §32 | SOC2 CC7.2 | ISO 27001

SECURITY / PRIVACY:
    No authentication authority is created here. MongoDB is durable catalogue
    evidence only. Caller commercial values remain subject to fail-closed
    PlanEntity validation.

TENANT BOUNDARY:
    tenant_id is catalogue scope evidence only. A supplied tenant context may
    view its own tenant-scoped plans plus global plans, matching the pre-Mongo
    Registry contract. This does not authenticate membership, role, permission,
    entitlement or subscription access.

AUTHORITY BOUNDARY:
    Registry creation/lifecycle establishes catalogue state only. It cannot grant
    subscription entitlement, WILSY AI access, membership, roles or permissions.

FINANCIAL AUTHORITY:
    NONE. Kennel EOS remains the exclusive payment, release, settlement,
    transfer and charge execution authority.

PERSISTENCE POSTURE:
    REAL MONGODB. Required indexes and persisted PlanEntity evidence fail closed.
    There is no in-memory authority fallback.

PUBLIC API INTENT:
    PlanRegistry.create/get/list/update/archive/reactivate/health_check.
"""

from __future__ import annotations

import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional

from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConfigurationError, DuplicateKeyError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from ..domain.plan import (
    AuditAction,
    PlanEntity,
    PlanFrequency,
    PlanTiers,
)

logger = logging.getLogger("WilsyOS.PlanRegistry")

PLAN_REGISTRY_VERSION = "v1.2.0-EXACT-TENANT-SCOPE"

_REGISTRY_REVISION_FIELD = "_registry_revision"

_TRANSPORT_FIELDS = frozenset(
    {
        "_id",
        _REGISTRY_REVISION_FIELD,
    }
)

_DEBUG_LOGGING = (
    os.getenv(
        "WILSY_MODEL_DEBUG",
        "0",
    )
    == "1"
)


def _debug_success(
    event: str,
    plan_id: str,
) -> None:
    """Emit bounded successful lifecycle telemetry only in explicit debug mode."""

    if _DEBUG_LOGGING:
        logger.info(
            "[PLAN_REGISTRY] %s plan_id=%s",
            event,
            plan_id,
        )

_MONGO_URI = (
    os.getenv("WILSY_PLAN_MONGO_URI")
    or os.getenv("MONGODB_URI")
    or "mongodb://127.0.0.1:27017/wilsy"
)

_MONGO_SERVER_SELECTION_MS = int(
    os.getenv(
        "WILSY_PLAN_MONGO_SERVER_SELECTION_MS",
        "5000",
    )
)


def _resolve_database(
    client: MongoClient[Any],
) -> Database[Any]:
    configured = (
        os.getenv("WILSY_PLAN_MONGO_DATABASE")
        or ""
    ).strip()

    if configured:
        return client[configured]

    try:
        return client.get_default_database()
    except ConfigurationError:
        return client["wilsy"]


_mongo_client: MongoClient[Any] = MongoClient(
    _MONGO_URI,
    serverSelectionTimeoutMS=
        _MONGO_SERVER_SELECTION_MS,
    retryWrites=True,
)

_mongo_database = _resolve_database(
    _mongo_client
)

plans_collection: Collection[dict[str, Any]] = (
    _mongo_database.get_collection(
        "plans",
        write_concern=WriteConcern(
            w="majority",
            j=True,
        ),
        read_concern=ReadConcern(
            "majority"
        ),
    )
)

_INDEX_CONTRACT: tuple[
    tuple[
        str,
        list[
            tuple[
                str,
                int,
            ]
        ],
        bool,
        Optional[
            dict[
                str,
                Any,
            ]
        ],
    ],
    ...,
] = (
    (
        "plan_id_unique",
        [
            (
                "plan_id",
                ASCENDING,
            )
        ],
        True,
        {
            "plan_id": {
                "$type": "string"
            }
        },
    ),
    (
        "idempotency_key_unique",
        [
            (
                "idempotency_key",
                ASCENDING,
            )
        ],
        True,
        {
            "idempotency_key": {
                "$type": "string"
            }
        },
    ),
    (
        "tenant_active",
        [
            (
                "tenant_id",
                ASCENDING,
            ),
            (
                "active",
                ASCENDING,
            ),
        ],
        False,
        None,
    ),
    (
        "tenant_plan_type",
        [
            (
                "tenant_id",
                ASCENDING,
            ),
            (
                "plan_type",
                ASCENDING,
            ),
        ],
        False,
        None,
    ),
    (
        "catalogue_order",
        [
            (
                "created_at",
                ASCENDING,
            ),
            (
                "plan_id",
                ASCENDING,
            ),
        ],
        False,
        None,
    ),
)



@dataclass(
    frozen=True
)
class _StoredPlan:
    """Mongo transport envelope; never canonical PlanEntity commercial state."""

    plan: PlanEntity
    mongo_id: Any
    registry_revision: int


class PlanRegistry:
    """
    Durable Mongo-backed Plan catalogue registry.

    All business-facing methods remain classmethods to preserve the established
    Python/Node bridge contract. The module-level ``plans_collection`` is the
    bounded persistence seam used by real-Mongo certification.
    """

    @classmethod
    def _generate_idempotency_key(
        cls,
    ) -> str:
        return (
            "WILSY-IDEMP-"
            + uuid.uuid4().hex[
                :16
            ].upper()
        )

    @classmethod
    def _to_bool(
        cls,
        value: Any,
    ) -> bool:
        if value is None:
            return True

        if isinstance(
            value,
            bool,
        ):
            return value

        if isinstance(
            value,
            str,
        ):
            lowered = value.lower()

            if lowered in (
                "true",
                "1",
                "yes",
                "on",
            ):
                return True

            if lowered in (
                "false",
                "0",
                "no",
                "off",
            ):
                return False

            return bool(
                value
            )

        try:
            return bool(
                value
            )
        except Exception:
            return True

    @classmethod
    def _ensure_indexes(
        cls,
    ) -> None:
        for (
            name,
            keys,
            unique,
            partial,
        ) in _INDEX_CONTRACT:
            kwargs: dict[
                str,
                Any,
            ] = {
                "name": name,
            }

            if unique:
                kwargs[
                    "unique"
                ] = True

            if partial is not None:
                kwargs[
                    "partialFilterExpression"
                ] = partial

            observed_name = (
                plans_collection.create_index(
                    keys,
                    **kwargs,
                )
            )

            if (
                observed_name
                != name
            ):
                raise RuntimeError(
                    "PLAN_REGISTRY_INDEX_NAME_MISMATCH:"
                    f"{name}:{observed_name}"
                )

        information = (
            plans_collection
            .index_information()
        )

        for (
            name,
            keys,
            unique,
            partial,
        ) in _INDEX_CONTRACT:
            details = information.get(
                name
            )

            if details is None:
                raise RuntimeError(
                    "PLAN_REGISTRY_INDEX_MISSING:"
                    + name
                )

            if list(
                details.get(
                    "key",
                    [],
                )
            ) != keys:
                raise RuntimeError(
                    "PLAN_REGISTRY_INDEX_KEY_MISMATCH:"
                    + name
                )

            if bool(
                details.get(
                    "unique",
                    False,
                )
            ) != unique:
                raise RuntimeError(
                    "PLAN_REGISTRY_INDEX_UNIQUENESS_MISMATCH:"
                    + name
                )

            if partial is not None:
                if (
                    details.get(
                        "partialFilterExpression"
                    )
                    != partial
                ):
                    raise RuntimeError(
                        "PLAN_REGISTRY_INDEX_PARTIAL_MISMATCH:"
                        + name
                    )

    @classmethod
    def _hydrate(
        cls,
        document: Mapping[
            str,
            Any,
        ],
    ) -> _StoredPlan:
        """
        Hydrate canonical PlanEntity evidence plus exact Mongo transport metadata.

        Only ``_id`` and ``_registry_revision`` may exist outside canonical
        ``PlanEntity.to_dict()`` material.
        """

        if (
            "_id"
            not in document
        ):
            raise ValueError(
                "PLAN_REGISTRY_MONGO_ID_REQUIRED"
            )

        mongo_id = document[
            "_id"
        ]

        revision = document.get(
            _REGISTRY_REVISION_FIELD
        )

        if (
            isinstance(
                revision,
                bool,
            )
            or not isinstance(
                revision,
                int,
            )
            or revision < 1
        ):
            raise ValueError(
                "PLAN_REGISTRY_REVISION_INVALID"
            )

        payload = {
            key:
                value
            for key, value
            in document.items()
            if key
            not in _TRANSPORT_FIELDS
        }

        plan = (
            PlanEntity.from_dict(
                payload
            )
        )

        canonical = (
            plan.to_dict()
        )

        if (
            payload
            != canonical
        ):
            unexpected = sorted(
                set(payload)
                - set(canonical)
            )

            missing = sorted(
                set(canonical)
                - set(payload)
            )

            mismatched = sorted(
                key
                for key
                in (
                    set(payload)
                    & set(canonical)
                )
                if (
                    payload[key]
                    != canonical[key]
                )
            )

            raise ValueError(
                "PLAN_REGISTRY_NONCANONICAL_DOCUMENT:"
                f"unexpected={unexpected}:"
                f"missing={missing}:"
                f"mismatched={mismatched}"
            )

        return _StoredPlan(
            plan=plan,
            mongo_id=mongo_id,
            registry_revision=revision,
        )

    @classmethod
    def _load_catalogue(
        cls,
    ) -> list[
        _StoredPlan
    ]:
        cls._ensure_indexes()

        documents = (
            plans_collection
            .find(
                {}
            )
            .sort(
                [
                    (
                        "created_at",
                        ASCENDING,
                    ),
                    (
                        "plan_id",
                        ASCENDING,
                    ),
                ]
            )
        )

        return [
            cls._hydrate(
                document
            )
            for document
            in documents
        ]

    @classmethod
    def _get_record(
        cls,
        plan_id: str,
        tenant_id: Optional[
            str
        ] = None,
        *,
        exact_tenant: bool = False,
    ) -> Optional[
        _StoredPlan
    ]:
        """Resolve one validated Mongo record under catalogue-scope semantics."""

        for record in (
            cls._load_catalogue()
        ):
            plan = (
                record.plan
            )

            if (
                plan.plan_id
                != plan_id
            ):
                continue

            if exact_tenant:
                if (
                    tenant_id is None
                    or plan.tenant_id
                    != tenant_id
                ):
                    return None

            elif (
                tenant_id
                and plan.tenant_id
                and plan.tenant_id
                != tenant_id
            ):
                return None

            return record

        return None

    @classmethod
    def _replace_current(
        cls,
        existing: _StoredPlan,
        updated: PlanEntity,
    ) -> None:
        """
        Replace exactly one observed Mongo storage generation.

        The predicate binds immutable Mongo identity, the monotonic transport
        revision, the complete prior canonical PlanEntity state and the exact
        persisted key set. A stale or ABA writer therefore cannot overwrite a
        different observed Mongo generation.
        """

        canonical_existing = (
            existing.plan
            .to_dict()
        )

        expected_keys = sorted(
            [
                *canonical_existing.keys(),
                "_id",
                _REGISTRY_REVISION_FIELD,
            ]
        )

        predicate: dict[
            str,
            Any,
        ] = dict(
            canonical_existing
        )

        predicate[
            "_id"
        ] = (
            existing.mongo_id
        )

        predicate[
            _REGISTRY_REVISION_FIELD
        ] = (
            existing.registry_revision
        )

        predicate[
            "$expr"
        ] = {
            "$setEquals": [
                {
                    "$map": {
                        "input": {
                            "$objectToArray":
                                "$$ROOT"
                        },
                        "as":
                            "field",
                        "in":
                            "$$field.k",
                    }
                },
                expected_keys,
            ]
        }

        replacement: dict[
            str,
            Any,
        ] = (
            updated.to_dict()
        )

        replacement[
            "_id"
        ] = (
            existing.mongo_id
        )

        replacement[
            _REGISTRY_REVISION_FIELD
        ] = (
            existing.registry_revision
            + 1
        )

        result = (
            plans_collection
            .replace_one(
                predicate,
                replacement,
                upsert=False,
            )
        )

        if (
            result.matched_count
            != 1
        ):
            raise RuntimeError(
                "PLAN_REGISTRY_CONCURRENT_MUTATION"
            )

    @classmethod
    def create(
        cls,
        payload: Dict[
            str,
            Any,
        ],
        tenant_id: Optional[
            str
        ] = None,
    ) -> Dict[
        str,
        Any,
    ]:
        """
        Create and durably persist one canonical PlanEntity.

        Required input remains compatible with the pre-Mongo Registry:
        name, price, currency, billingFrequency, planType and idempotencyKey.
        """

        try:
            required = [
                "name",
                "price",
                "currency",
                "billingFrequency",
                "planType",
                "idempotencyKey",
            ]

            for field in required:
                if field not in payload:
                    return {
                        "success":
                            False,
                        "error":
                            "Missing required field: "
                            + field,
                    }

            plan_type_str = str(
                payload[
                    "planType"
                ]
            ).upper()

            try:
                plan_type_enum = (
                    PlanTiers(
                        plan_type_str
                    )
                )
            except ValueError:
                return {
                    "success":
                        False,
                    "error":
                        "Invalid planType: "
                        + plan_type_str,
                }

            frequency_str = str(
                payload[
                    "billingFrequency"
                ]
            ).lower()

            try:
                frequency_enum = (
                    PlanFrequency(
                        frequency_str
                    )
                )
            except ValueError:
                return {
                    "success":
                        False,
                    "error":
                        "Invalid billingFrequency: "
                        + frequency_str,
                }

            idempotency_key = (
                payload[
                    "idempotencyKey"
                ]
            )

            effective_tenant = (
                payload.get(
                    "tenantId"
                )
                or tenant_id
            )

            plan_id = (
                payload.get(
                    "plan_id"
                )
                or (
                    "WILSYPLAN-"
                    + uuid.uuid4().hex[
                        :8
                    ].upper()
                )
            )

            plan = PlanEntity(
                plan_id=plan_id,
                name=payload[
                    "name"
                ],
                description=
                    payload.get(
                        "description",
                        "",
                    ),
                price=payload[
                    "price"
                ],
                currency=str(
                    payload[
                        "currency"
                    ]
                ).upper(),
                billing_frequency=
                    frequency_enum,
                trial_days=int(
                    payload.get(
                        "trialDays",
                        0,
                    )
                ),
                plan_type=
                    plan_type_enum,
                features=
                    payload.get(
                        "features",
                        [],
                    ),
                active=cls._to_bool(
                    payload.get(
                        "active",
                        True,
                    )
                ),
                tenant_id=
                    effective_tenant,
                kennel_shard=
                    payload.get(
                        "kennelShard",
                        "EOS_PRIMARY",
                    ),
                idempotency_key=
                    idempotency_key,
                seal_nonce=
                    payload.get(
                        "sealNonce",
                        uuid.uuid4().hex,
                    ),
                proof_hash=
                    payload.get(
                        "proofHash",
                        "",
                    ),
                integrity_root=
                    payload.get(
                        "integrityRoot",
                        payload.get(
                            "merkleRoot",
                            "",
                        ),
                    ),
                metadata=
                    payload.get(
                        "metadata",
                        {},
                    ),
                tags=
                    payload.get(
                        "tags",
                        [],
                    ),
            )

            plan = (
                plan.add_audit_entry(
                    action=
                        AuditAction.CREATE,
                    user=payload.get(
                        "user",
                        "SYSTEM",
                    ),
                    reason=
                        "Plan created",
                    metadata={
                        "source":
                            "registry"
                    },
                )
            )

            catalogue = (
                cls._load_catalogue()
            )

            if any(
                current.plan.idempotency_key
                == plan.idempotency_key
                for current
                in catalogue
            ):
                return {
                    "success":
                        False,
                    "error":
                        "Idempotency key "
                        f"'{plan.idempotency_key}' "
                        "already exists",
                }

            if any(
                current.plan.plan_id
                == plan.plan_id
                for current
                in catalogue
            ):
                return {
                    "success":
                        False,
                    "error":
                        "Plan ID "
                        f"'{plan.plan_id}' "
                        "already exists",
                }

            document: dict[
                str,
                Any,
            ] = (
                plan.to_dict()
            )

            document[
                _REGISTRY_REVISION_FIELD
            ] = 1

            try:
                plans_collection.insert_one(
                    document
                )
            except DuplicateKeyError:
                return {
                    "success":
                        False,
                    "error":
                        "Duplicate plan catalogue key",
                }

            _debug_success(
                "create",
                plan.plan_id,
            )

            return {
                "success":
                    True,
                "plan":
                    plan,
            }

        except Exception as exc:
            logger.error(
                "❌ [PLAN_REGISTRY] Create failed: %s",
                str(
                    exc
                ),
            )

            return {
                "success":
                    False,
                "error":
                    str(
                        exc
                    ),
            }

    @classmethod
    def get(
        cls,
        plan_id: str,
        tenant_id: Optional[
            str
        ] = None,
        *,
        exact_tenant: bool = False,
    ) -> Optional[
        PlanEntity
    ]:
        """
        Retrieve one canonical plan.

        ``None`` means genuine absence or genuine catalogue-scope mismatch.
        Persistence, transport-envelope or canonical hydration failure propagates.
        """

        record = (
            cls._get_record(
                plan_id,
                tenant_id,
                exact_tenant=
                    exact_tenant,
            )
        )

        if (
            record
            is None
        ):
            return None

        return (
            record.plan
        )

    @classmethod
    def list(
        cls,
        tenant_id: Optional[
            str
        ] = None,
        active: Optional[
            bool
        ] = None,
        plan_type: Optional[
            PlanTiers
        ] = None,
        page: int = 1,
        limit: int = 20,
        *,
        exact_tenant: bool = False,
    ) -> Dict[
        str,
        Any,
    ]:
        """
        List validated catalogue truth with the established return shape.

        Persistence or hydration failure propagates. An empty result therefore
        means the validated catalogue actually contains no matching plan.
        """

        all_plans = [
            record.plan
            for record
            in cls._load_catalogue()
        ]

        if exact_tenant:
            all_plans = [
                plan
                for plan
                in all_plans
                if (
                    tenant_id
                    is not None
                    and plan.tenant_id
                    == tenant_id
                )
            ]

        elif tenant_id:
            all_plans = [
                plan
                for plan
                in all_plans
                if (
                    plan.tenant_id
                    == tenant_id
                    or plan.tenant_id
                    is None
                )
            ]

        if active is not None:
            all_plans = [
                plan
                for plan
                in all_plans
                if plan.active
                == active
            ]

        if plan_type:
            all_plans = [
                plan
                for plan
                in all_plans
                if plan.plan_type
                == plan_type
            ]

        total = len(
            all_plans
        )

        start = (
            page - 1
        ) * limit

        end = (
            start
            + limit
        )

        items = all_plans[
            start:end
        ]

        pages = (
            (
                total
                + limit
                - 1
            )
            // limit
            if limit > 0
            else 0
        )

        return {
            "items":
                items,
            "total":
                total,
            "pages":
                pages,
        }

    @classmethod
    def update(
        cls,
        plan_id: str,
        payload: Dict[
            str,
            Any,
        ],
        tenant_id: Optional[
            str
        ] = None,
        *,
        exact_tenant: bool = False,
    ) -> Dict[
        str,
        Any,
    ]:
        """Update one plan using immutable PlanEntity evolution plus Mongo CAS."""

        try:
            stored = cls._get_record(
                plan_id,
                tenant_id,
                exact_tenant=
                    exact_tenant,
            )

            if stored is None:
                return {
                    "success":
                        False,
                    "error":
                        "Plan not found",
                }

            existing = stored.plan

            protected = {
                "plan_id",
                "idempotency_key",
                "created_at",
                "seal_nonce",
                "proof_hash",
                "merkle_root",
                "integrity_root",
                "state_proof_lineage",
                "state_history",
                "catalogue_version",
                "proof_version",
                "audit_trail",
            }

            safe_payload = {
                key:
                    value
                for (
                    key,
                    value,
                )
                in payload.items()
                if key
                not in protected
            }

            if (
                "plan_type"
                in safe_payload
                and isinstance(
                    safe_payload[
                        "plan_type"
                    ],
                    str,
                )
            ):
                safe_payload[
                    "plan_type"
                ] = PlanTiers(
                    safe_payload[
                        "plan_type"
                    ].upper()
                )

            if (
                "billing_frequency"
                in safe_payload
                and isinstance(
                    safe_payload[
                        "billing_frequency"
                    ],
                    str,
                )
            ):
                safe_payload[
                    "billing_frequency"
                ] = PlanFrequency(
                    safe_payload[
                        "billing_frequency"
                    ].lower()
                )

            updated_plan = (
                existing.update(
                    safe_payload
                )
            )

            updated_plan = (
                updated_plan
                .add_audit_entry(
                    action=
                        AuditAction.UPDATE,
                    user=payload.get(
                        "user",
                        "SYSTEM",
                    ),
                    reason=
                        "Plan updated",
                    metadata={
                        "updated_fields":
                            list(
                                safe_payload.keys()
                            )
                    },
                )
            )

            cls._replace_current(
                stored,
                updated_plan,
            )

            _debug_success(
                "update",
                plan_id,
            )

            return {
                "success":
                    True,
                "plan":
                    updated_plan,
            }

        except Exception as exc:
            logger.error(
                "❌ [PLAN_REGISTRY] Update failed: %s",
                str(
                    exc
                ),
            )

            return {
                "success":
                    False,
                "error":
                    str(
                        exc
                    ),
            }

    @classmethod
    def archive(
        cls,
        plan_id: str,
        tenant_id: Optional[
            str
        ] = None,
        *,
        exact_tenant: bool = False,
    ) -> bool:
        """
        Soft-delete a plan.

        ``False`` means genuine absence/scope mismatch only. Infrastructure and
        evidence failures propagate.
        """

        try:
            stored = cls._get_record(
                plan_id,
                tenant_id,
                exact_tenant=
                    exact_tenant,
            )

            if stored is None:
                return False

            existing = stored.plan

            updated_plan = (
                existing.update(
                    {
                        "active":
                            False
                    }
                )
            )

            updated_plan = (
                updated_plan
                .add_audit_entry(
                    action=
                        AuditAction.ARCHIVE,
                    user="SYSTEM",
                    reason=
                        "Plan archived",
                )
            )

            cls._replace_current(
                stored,
                updated_plan,
            )

            _debug_success(
                "archive",
                plan_id,
            )

            return True

        except Exception:
            logger.exception(
                "❌ [PLAN_REGISTRY] Archive failed: %s",
                plan_id,
            )
            raise

    @classmethod
    def reactivate(
        cls,
        plan_id: str,
        tenant_id: Optional[
            str
        ] = None,
    ) -> bool:
        """
        Reactivate an archived plan.

        ``False`` means genuine absence/scope mismatch only. Infrastructure and
        evidence failures propagate.
        """

        try:
            stored = cls._get_record(
                plan_id,
                tenant_id,
            )

            if stored is None:
                return False

            existing = stored.plan

            if existing.active:
                return True

            updated_plan = (
                existing.update(
                    {
                        "active":
                            True
                    }
                )
            )

            updated_plan = (
                updated_plan
                .add_audit_entry(
                    action=
                        AuditAction.REACTIVATE,
                    user="SYSTEM",
                    reason=
                        "Plan reactivated",
                )
            )

            cls._replace_current(
                stored,
                updated_plan,
            )

            _debug_success(
                "reactivate",
                plan_id,
            )

            return True

        except Exception:
            logger.exception(
                "❌ [PLAN_REGISTRY] Reactivate failed: %s",
                plan_id,
            )
            raise

    @classmethod
    def health_check(
        cls,
    ) -> Dict[
        str,
        Any,
    ]:
        """
        Return bounded Mongo catalogue health.

        A red health result never claims durable truth is available.
        """

        timestamp = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        try:
            (
                plans_collection
                .database
                .client
                .admin
                .command(
                    "ping"
                )
            )

            catalogue = (
                cls._load_catalogue()
            )

            indexes = (
                plans_collection
                .index_information()
            )

            return {
                "status":
                    "OPERATIONAL",
                "version":
                    PLAN_REGISTRY_VERSION,
                "timestamp":
                    timestamp,
                "store_type":
                    "mongo",
                "plan_count":
                    len(
                        catalogue
                    ),
                "required_indexes":
                    sorted(
                        name
                        for (
                            name,
                            _keys,
                            _unique,
                            _partial,
                        )
                        in _INDEX_CONTRACT
                    ),
                "observed_indexes":
                    sorted(
                        name
                        for name
                        in indexes
                        if name
                        != "_id_"
                    ),
                "write_concern":
                    "majority+journal",
                "read_concern":
                    "majority",
            }

        except Exception as exc:
            logger.error(
                "❌ [PLAN_REGISTRY] Health unavailable: %s",
                str(
                    exc
                ),
            )

            return {
                "status":
                    "UNAVAILABLE",
                "version":
                    PLAN_REGISTRY_VERSION,
                "timestamp":
                    timestamp,
                "store_type":
                    "mongo",
                "error":
                    str(
                        exc
                    ),
            }


"""
INSTITUTIONAL CERTIFICATION SEAL — WILSY OS PLAN REGISTRY

Status:
    PRODUCTION REGISTRY CONTRACT — REAL MONGODB PERSISTENCE

Version:
    v1.2.0-EXACT-TENANT-SCOPE

Authority:
    Wilsy OS Core Governance

Canonical path:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/plan_registry.py

Catalogue owner:
    PlanRegistry

Commercial validation:
    PlanEntity / Python EOS

Persistence:
    REAL MONGODB — canonical PlanEntity evidence, majority reads/writes.

Failure semantics:
    Mongo/index/hydration failure cannot masquerade as absence or empty truth.

Tenant authority:
    NONE — tenant_id is catalogue scope evidence only.

Financial execution:
    NONE — Kennel EOS remains exclusive.

HTTP authority:
    NONE — Plan HTTP authorization remains separately certified.

Certification date:
    2026-09-03

WILSY OS — ALL OR NOTHING.
"""
