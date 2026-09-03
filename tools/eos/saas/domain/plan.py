# -*- coding: utf-8 -*-
"""
WILSY OS — Sovereign Plan Domain Commercial Contract

TITLE:
    WILSY OS Sovereign Plan Domain Commercial Contract

VERSION:
    v1.1.9-LEGACY-UNSEALED-PROVENANCE

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Immutable, validated and deterministically sealed canonical commercial
    plan value contract.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/plan.py

OWNERSHIP:
    Python EOS owns sovereign commercial plan truth.
    PlanRegistry owns current in-memory catalogue orchestration and mutation
    authority. Durable catalogue persistence remains reserved for the separately
    certified Real-Mongo phase.

TENANT BOUNDARY:
    tenant_id is commercial scope evidence only. It is not authentication,
    membership, role, permission or entitlement authority.

AUTHORITY BOUNDARY:
    This domain validates and seals commercial state. Constructing or updating
    a PlanEntity does not authorize a caller to publish catalogue truth.

FINANCIAL AUTHORITY:
    Price and billing configuration are commercial truth only.
    REQUEST != AUTHORIZATION != PAYMENT != EXECUTION != SETTLEMENT.
    Kennel EOS remains the exclusive financial execution authority.

SECURITY / PRIVACY:
    Invalid commercial state fails closed. Deterministic SHA3-512 evidence
    binds canonical identity, price, currency, frequency, features, trial
    policy, lifecycle posture, commercial metadata and catalogue version.

CHANGELOG:
    2026-09-03 v1.1.9-LEGACY-UNSEALED-PROVENANCE
        - Labels every genuine unversioned legacy migration as explicitly
          content-unverified even when no sealed evidence or audit trail exists.
        - Preserves stronger LEGACY_V1 envelope-consistency status when valid
          sealed historical proof material is supplied.
        - Prevents marker-free legacy provenance from becoming indistinguishable
          from newly constructed current-v2 state.
    2026-09-03 v1.1.8-LEGACY-STATE-HISTORY-ISOLATION
        - Rejects state_history and stateHistory at the explicit legacy
          migration boundary as current-schema trust markers.
        - Prevents current verified-state material from being silently discarded
          through legacy migration and closes the final focused Codex finding.
    2026-09-03 v1.1.7-VERIFIABLE-STATE-HISTORY
        - Persists canonical commercial-state preimages for every catalogue
          version and recomputes each historical state proof during hydration.
        - Derives state_proof_lineage from contiguous verified state history
          rather than accepting historical hashes as standalone evidence.
        - Requires complete persisted current-audit actor, rationale, metadata
          and predecessor material.
        - Corrects PlanRegistry ownership wording to its current in-memory
          orchestration posture; durable persistence remains a later phase.
    2026-09-03 v1.1.6-AUDIT-CATALOGUE-TYPE-CONTRACT
        - Canonicalizes selected current audit catalogue-version evidence to
          a governed integer before AuditEntry construction.
        - Closes the bounded Pyright Any-or-None constructor handoff while
          preserving explicit-evidence, alias-conflict and fail-closed behavior.
        - PlanRegistry and direct certificate bytes remain unchanged.
    2026-09-03 v1.1.5-AUDIT-CATALOGUE-EVIDENCE
        - Requires explicit catalogue-version evidence during current AuditEntry
          persistence hydration.
        - Rejects contradictory snake/camel audit catalogue-version aliases.
        - Preserves equal dual aliases as one unambiguous current-v2 value.
        - Corrects historical flat-digest terminology from Merkle to the
          audit-bound SHA3-512 integrity-envelope digest.
    2026-09-03 v1.1.4-LEGACY-AUDIT-TYPE-CONTRACT
        - Canonicalizes the explicit legacy audit provenance value through the
          governed tuple/mapping normalizer before PlanEntity construction.
        - Closes the bounded Pyright type contract without changing trust,
          commercial, Registry, persistence or financial semantics.
    2026-09-03 v1.1.3-TRUST-ALIAS-ISOLATION
        - Rejects contradictory snake/camel proof-version aliases for current
          PlanEntity and AuditEntry persistence hydration.
        - Rejects current-v2 audit trust markers at the explicit legacy
          migration boundary.
        - Prevents current audit evidence from being laundered into opaque
          legacy provenance by removing only outer current-schema markers.
    2026-09-03 v1.1.2-TRUST-CLASS-INTEGRITY
        - Separates current persisted hydration from explicit legacy migration.
        - Requires complete current proof, integrity-root and state-lineage evidence.
        - Removes legacy trust-class selection from current AuditEntry hydration.
        - Binds current audit events to resolvable catalogue state-proof lineage.
        - Canonicalizes signed zero and renames flat hash semantics to integrity root.
        - Preserves `merkle_root` only as a documented compatibility alias.
    2026-09-03 v1.1.1-CODEX-REMEDIATED
        - Migrates unversioned legacy proof evidence without treating it as
          current canonical proof.
        - Binds complete legacy commercial/tenant state into fallback identity.
        - Rejects lossy float price projection and positive-value underflow.
        - Adds versioned, chained audit-event evidence and an audit-bound flat SHA3-512 integrity-envelope digest.
        - Preserves current PlanRegistry user audit-context compatibility
          without admitting user into commercial state.
    2026-09-03 v1.1.0-COMMERCIAL-CONTRACT
        - Adds deterministic commercial-state proofs.
        - Adds catalogue_version.
        - Binds features, tags and metadata into canonical proof.
        - Adds strict fail-closed value validation.
        - Deep-freezes mutable metadata.
        - Rejects mismatched persisted proof and merkle evidence.
        - Makes legacy missing identity hydration deterministic.
        - Protects identity/evidence fields from generic update().
        - Separates canonical state proof from audit-event proof.
        - Preserves Kennel EOS exclusive financial execution authority.

COMPLIANCE:
    POPIA §19 | GDPR Art. 32 | SOC2 CC7.2 | ISO 27001

PUBLIC API INTENT:
    PlanEntity, PlanTiers, PlanStatus, PlanFrequency, AuditAction,
    generate_plan_proof and parse_datetime remain domain-level APIs.

WILSY OS — ALL OR NOTHING.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import uuid
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
from types import MappingProxyType
from typing import Any, Dict, Optional, Tuple

# ─────────────────────────────────────────────────────────────────────────────
# ENUMS (mirroring Node constants)
# ─────────────────────────────────────────────────────────────────────────────

class PlanTiers(str, Enum):
    """Plan tier / type enumeration (as used in Node)."""
    FREE = "FREE"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"
    SOVEREIGN = "SOVEREIGN"
    ULTRA = "ULTRA"
    FOUNDER_ENTERPRISE = "FOUNDER_ENTERPRISE"


class PlanStatus(str, Enum):
    """Plan lifecycle statuses."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class PlanFrequency(str, Enum):
    """Billing frequencies for plans."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    ONE_TIME = "one_time"


class AuditAction(str, Enum):
    """Audit trail action types."""
    CREATE = "create"
    UPDATE = "update"
    ARCHIVE = "archive"
    REACTIVATE = "reactivate"


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

_PLAN_ID_RE = re.compile(
    r"^WILSYPLAN-[A-Z0-9][A-Z0-9_-]{3,63}$"
)

_CURRENCY_RE = re.compile(
    r"^[A-Z]{3}$"
)

_UPDATABLE_COMMERCIAL_FIELDS = frozenset(
    {
        "name",
        "description",
        "price",
        "currency",
        "billing_frequency",
        "trial_days",
        "plan_type",
        "features",
        "active",
        "metadata",
        "tags",
    }
)

_CURRENT_PROOF_VERSION = 2
_LEGACY_PROOF_VERSION = 1
_CURRENT_AUDIT_PROOF_VERSION = 2

_LEGACY_EVIDENCE_STATUS = (
    "LEGACY_V1_ENVELOPE_CONSISTENT_CONTENT_UNVERIFIED"
)

_LEGACY_UNSEALED_STATUS = (
    "LEGACY_UNVERSIONED_CONTENT_UNVERIFIED"
)

_INTEGRITY_ROOT_SEMANTICS = (
    "SHA3_512_FLAT_ENVELOPE_DIGEST_NOT_MERKLE_TREE"
)

_STATE_HISTORY_SEMANTICS = (
    "CANONICAL_STATE_PREIMAGE_CONSISTENCY_NOT_EXTERNAL_AUTHENTICITY"
)

_NONCOMMERCIAL_UPDATE_CONTEXT_FIELDS = frozenset(
    {
        "user",
    }
)

_SHA3_512_RE = re.compile(
    r"^[0-9A-F]{128}$"
)



def parse_datetime(
    val: Any,
) -> datetime:
    """Parse governed datetime evidence and fail closed on malformed input."""
    if isinstance(
        val,
        datetime,
    ):
        parsed = val

    elif isinstance(
        val,
        str,
    ):
        try:
            parsed = datetime.fromisoformat(
                val
            )
        except ValueError as exc:
            raise ValueError(
                "invalid ISO-8601 datetime"
            ) from exc

    else:
        raise TypeError(
            "datetime value must be datetime or ISO-8601 string"
        )

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=timezone.utc
        )

    return parsed.astimezone(
        timezone.utc
    )


def _canonical_price(
    value: Any,
) -> float:
    """
    Validate commercial price while preserving the retained float API only
    where decimal meaning survives projection exactly.
    """
    if isinstance(
        value,
        bool,
    ):
        raise TypeError(
            "price must be numeric, not bool"
        )

    try:
        decimal_value = Decimal(
            str(value)
        )
    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            "price must be a valid decimal amount"
        ) from exc

    if not decimal_value.is_finite():
        raise ValueError(
            "price must be finite"
        )

    if decimal_value < 0:
        raise ValueError(
            "price must be non-negative"
        )

    if decimal_value == 0:
        return 0.0

    projected = float(
        decimal_value
    )

    if not math.isfinite(
        projected
    ):
        raise ValueError(
            "price cannot exceed finite float projection"
        )

    round_trip = Decimal(
        str(projected)
    )

    if round_trip != decimal_value:
        raise ValueError(
            "price cannot be represented losslessly by retained float API"
        )

    return projected

def _canonical_price_text(
    value: Any,
) -> str:
    """Return deterministic decimal text for an accepted stored price."""
    projected = _canonical_price(
        value
    )

    if projected == 0:
        return "0"

    decimal_value = Decimal(
        str(
            projected
        )
    )

    text = format(
        decimal_value,
        "f",
    )

    if "." in text:
        text = text.rstrip(
            "0"
        ).rstrip(
            "."
        )

    return text or "0"

def _canonical_currency(
    value: Any,
) -> str:
    currency = str(
        value
    ).strip().upper()

    if not _CURRENCY_RE.fullmatch(
        currency
    ):
        raise ValueError(
            "currency must be a three-letter code"
        )

    return currency


def _canonical_nonnegative_int(
    value: Any,
    *,
    field_name: str,
    minimum: int = 0,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
    ):
        raise TypeError(
            f"{field_name} must be an integer"
        )

    if value < minimum:
        raise ValueError(
            f"{field_name} must be at least {minimum}"
        )

    return value


def _canonical_plan_type(
    value: Any,
) -> PlanTiers:
    if isinstance(
        value,
        PlanTiers,
    ):
        return value

    if isinstance(
        value,
        str,
    ):
        return PlanTiers(
            value.upper()
        )

    raise TypeError(
        "plan_type must be PlanTiers or governed string value"
    )


def _canonical_frequency(
    value: Any,
) -> PlanFrequency:
    if isinstance(
        value,
        PlanFrequency,
    ):
        return value

    if isinstance(
        value,
        str,
    ):
        return PlanFrequency(
            value.lower()
        )

    raise TypeError(
        "billing_frequency must be PlanFrequency or governed string value"
    )


def _canonical_string_tuple(
    value: Any,
    *,
    field_name: str,
) -> Tuple[str, ...]:
    if value is None:
        return ()

    if isinstance(
        value,
        str,
    ):
        raise TypeError(
            f"{field_name} must be a sequence of strings"
        )

    try:
        raw_values = tuple(
            value
        )
    except TypeError as exc:
        raise TypeError(
            f"{field_name} must be a sequence of strings"
        ) from exc

    result: list[str] = []
    seen: set[str] = set()

    for raw in raw_values:
        if not isinstance(
            raw,
            str,
        ):
            raise TypeError(
                f"{field_name} entries must be strings"
            )

        item = raw.strip()

        if not item:
            raise ValueError(
                f"{field_name} entries cannot be empty"
            )

        if item not in seen:
            seen.add(
                item
            )
            result.append(
                item
            )

    return tuple(
        result
    )


def _deep_freeze(
    value: Any,
) -> Any:
    """Deep-freeze commercial metadata to preserve frozen value semantics."""
    if isinstance(
        value,
        Mapping,
    ):
        return MappingProxyType(
            {
                str(key): _deep_freeze(item)
                for key, item in value.items()
            }
        )

    if isinstance(
        value,
        (list, tuple),
    ):
        return tuple(
            _deep_freeze(item)
            for item in value
        )

    return value


def _deep_thaw(
    value: Any,
) -> Any:
    """Project frozen domain values into deterministic JSON-compatible data."""
    if isinstance(
        value,
        Enum,
    ):
        return value.value

    if isinstance(
        value,
        datetime,
    ):
        return parse_datetime(
            value
        ).isoformat()

    if isinstance(
        value,
        Mapping,
    ):
        return {
            str(key): _deep_thaw(
                value[key]
            )
            for key in sorted(
                value,
                key=lambda item: str(item),
            )
        }

    if isinstance(
        value,
        (tuple, list),
    ):
        return [
            _deep_thaw(item)
            for item in value
        ]

    return value


def _legacy_plan_seed(
    data: Mapping[str, Any],
) -> str:
    """Bind deterministic fallback identity to complete legacy commercial scope."""
    active = data.get(
        "active",
        True,
    )

    if not isinstance(
        active,
        bool,
    ):
        raise TypeError(
            "active must be bool"
        )

    metadata = data.get(
        "metadata",
        {},
    )

    if not isinstance(
        metadata,
        Mapping,
    ):
        raise TypeError(
            "metadata must be a mapping"
        )

    material = {
        "name": str(
            data.get(
                "name",
                "",
            )
        ).strip(),
        "description": str(
            data.get(
                "description",
                "",
            )
        ).strip(),
        "planType": _canonical_plan_type(
            data.get(
                "plan_type",
                data.get(
                    "planType",
                    "PROFESSIONAL",
                ),
            )
        ).value,
        "price": _canonical_price_text(
            data.get(
                "price",
                0,
            )
        ),
        "currency": _canonical_currency(
            data.get(
                "currency",
                "ZAR",
            )
        ),
        "billingFrequency": _canonical_frequency(
            data.get(
                "billing_frequency",
                data.get(
                    "billingFrequency",
                    "monthly",
                ),
            )
        ).value,
        "trialDays": _canonical_nonnegative_int(
            data.get(
                "trial_days",
                data.get(
                    "trialDays",
                    0,
                ),
            ),
            field_name="trial_days",
        ),
        "features": list(
            _canonical_string_tuple(
                data.get(
                    "features",
                    (),
                ),
                field_name="features",
            )
        ),
        "active": active,
        "tenantId": (
            data.get(
                "tenant_id"
            )
            or data.get(
                "tenantId"
            )
        ),
        "kennelShard": str(
            data.get(
                "kennel_shard",
                data.get(
                    "kennelShard",
                    "EOS_PRIMARY",
                ),
            )
        ).strip(),
        "metadata": _deep_thaw(
            metadata
        ),
        "tags": list(
            _canonical_string_tuple(
                data.get(
                    "tags",
                    (),
                ),
                field_name="tags",
            )
        ),
        "createdAt": (
            data.get(
                "created_at"
            )
            or data.get(
                "createdAt"
            )
        ),
        "updatedAt": (
            data.get(
                "updated_at"
            )
            or data.get(
                "updatedAt"
            )
        ),
        "sealNonce": (
            data.get(
                "seal_nonce"
            )
            or data.get(
                "sealNonce"
            )
        ),
        "legacyProofHash": (
            data.get(
                "proof_hash"
            )
            or data.get(
                "proofHash"
            )
            or ""
        ),
        "legacyEnvelopeDigest": (
            data.get(
                "merkle_root"
            )
            or data.get(
                "merkleRoot"
            )
            or ""
        ),
    }

    encoded = json.dumps(
        _deep_thaw(
            material
        ),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode(
        "utf-8"
    )

    return hashlib.sha3_512(
        encoded
    ).hexdigest().upper()

def _legacy_plan_id(
    data: Mapping[str, Any],
) -> str:
    return (
        "WILSYPLAN-"
        + _legacy_plan_seed(
            data
        )[:32]
    )

def _legacy_idempotency_key(
    data: Mapping[str, Any],
) -> str:
    return (
        "WILSY-PLAN-READ-"
        + _legacy_plan_seed(
            data
        )
    )

def generate_plan_proof(
    plan_data: Dict[str, Any],
    action: str = "save",
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Generate deterministic SHA3-512 evidence for canonical commercial state."""
    active = plan_data.get(
        "active",
        True,
    )

    if not isinstance(
        active,
        bool,
    ):
        raise TypeError(
            "active must be bool"
        )

    trial_days = _canonical_nonnegative_int(
        plan_data.get(
            "trial_days",
            0,
        ),
        field_name="trial_days",
    )

    catalogue_version = _canonical_nonnegative_int(
        plan_data.get(
            "catalogue_version",
            1,
        ),
        field_name="catalogue_version",
        minimum=1,
    )

    proof_version = _canonical_nonnegative_int(
        plan_data.get(
            "proof_version",
            _CURRENT_PROOF_VERSION,
        ),
        field_name="proof_version",
        minimum=1,
    )

    if proof_version != _CURRENT_PROOF_VERSION:
        raise ValueError(
            "current canonical proof version is unsupported"
        )

    payload = {
        "proofVersion": proof_version,
        "action": str(
            action
        ),
        "planId": str(
            plan_data.get(
                "plan_id",
                "new",
            )
        ),
        "name": str(
            plan_data.get(
                "name",
                "",
            )
        ),
        "description": str(
            plan_data.get(
                "description",
                "",
            )
        ),
        "planType": _canonical_plan_type(
            plan_data.get(
                "plan_type",
                "PROFESSIONAL",
            )
        ).value,
        "price": _canonical_price_text(
            plan_data.get(
                "price",
                0,
            )
        ),
        "currency": _canonical_currency(
            plan_data.get(
                "currency",
                "ZAR",
            )
        ),
        "billingFrequency": _canonical_frequency(
            plan_data.get(
                "billing_frequency",
                "monthly",
            )
        ).value,
        "trialDays": trial_days,
        "features": _deep_thaw(
            plan_data.get(
                "features",
                (),
            )
        ),
        "active": active,
        "catalogueVersion": catalogue_version,
        "tenantId": plan_data.get(
            "tenant_id"
        ),
        "kennelShard": str(
            plan_data.get(
                "kennel_shard",
                "EOS_PRIMARY",
            )
        ),
        "idempotencyKey": str(
            plan_data.get(
                "idempotency_key",
                "",
            )
        ),
        "planMetadata": _deep_thaw(
            plan_data.get(
                "metadata",
                {},
            )
        ),
        "tags": _deep_thaw(
            plan_data.get(
                "tags",
                (),
            )
        ),
        "legacyProofHash": str(
            plan_data.get(
                "legacy_proof_hash",
                "",
            )
        ),
        "legacyEnvelopeDigest": str(
            plan_data.get(
                "legacy_envelope_digest",
                "",
            )
        ),
        "legacyEvidenceStatus": str(
            plan_data.get(
                "legacy_evidence_status",
                "",
            )
        ),
        "legacyAuditTrail": _deep_thaw(
            plan_data.get(
                "legacy_audit_trail",
                (),
            )
        ),
        "evidenceMetadata": _deep_thaw(
            metadata or {}
        ),
    }

    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode(
        "utf-8"
    )

    return hashlib.sha3_512(
        encoded
    ).hexdigest().upper()

def _legacy_envelope_digest(
    tenant_id: Optional[str],
    proof_hash: str,
    seal_nonce: str,
) -> str:
    """
    Recompute the historical flat SHA3 envelope.

    This establishes internal consistency only. It is not a Merkle tree and
    does not establish authenticity of the legacy proof content.
    """
    material = (
        f"{tenant_id or 'GLOBAL'}"
        f"|{proof_hash}"
        f"|{seal_nonce}"
    )

    return hashlib.sha3_512(
        material.encode(
            "utf-8"
        )
    ).hexdigest().upper()

def generate_audit_event_proof(
    *,
    action: AuditAction,
    timestamp: datetime,
    user: str,
    reason: Optional[str],
    metadata: Mapping[str, Any],
    plan_id: str,
    state_proof_hash: str,
    catalogue_version: int,
    previous_proof_hash: str,
) -> str:
    """Generate the current chained audit-event consistency proof."""
    payload = {
        "auditProofVersion": _CURRENT_AUDIT_PROOF_VERSION,
        "action": action.value,
        "timestamp": parse_datetime(
            timestamp
        ).isoformat(),
        "user": str(
            user
        ).strip() or "SYSTEM",
        "reason": (
            None
            if reason is None
            else str(
                reason
            )
        ),
        "metadata": _deep_thaw(
            metadata
        ),
        "planId": str(
            plan_id
        ).strip().upper(),
        "stateProofHash": str(
            state_proof_hash
        ).strip().upper(),
        "catalogueVersion": _canonical_nonnegative_int(
            catalogue_version,
            field_name="catalogue_version",
            minimum=1,
        ),
        "previousProofHash": str(
            previous_proof_hash
        ).strip().upper(),
    }

    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode(
        "utf-8"
    )

    return hashlib.sha3_512(
        encoded
    ).hexdigest().upper()

def _audit_link_token(
    entry: "AuditEntry",
) -> str:
    return entry.proof_hash


def _canonical_state_proof_lineage(
    value: Any,
) -> Tuple[Tuple[int, str], ...]:
    if value in (
        None,
        (),
        [],
    ):
        return ()

    if not isinstance(
        value,
        (
            list,
            tuple,
        ),
    ):
        raise TypeError(
            "state_proof_lineage must be a list or tuple"
        )

    normalized: list[tuple[int, str]] = []
    previous_version = 0

    for item in value:
        if isinstance(
            item,
            Mapping,
        ):
            version_raw = item.get(
                "catalogueVersion",
                item.get(
                    "catalogue_version"
                ),
            )

            proof_raw = item.get(
                "proofHash",
                item.get(
                    "proof_hash"
                ),
            )

        elif (
            isinstance(
                item,
                (
                    list,
                    tuple,
                ),
            )
            and len(item) == 2
        ):
            version_raw = item[0]
            proof_raw = item[1]

        else:
            raise TypeError(
                "state proof lineage entry is invalid"
            )

        version = _canonical_nonnegative_int(
            version_raw,
            field_name="state lineage catalogue_version",
            minimum=1,
        )

        proof_hash = str(
            proof_raw or ""
        ).strip().upper()

        if not _SHA3_512_RE.fullmatch(
            proof_hash
        ):
            raise ValueError(
                "state proof lineage requires SHA3-512 proof hashes"
            )

        if version <= previous_version:
            raise ValueError(
                "state proof lineage versions must be strictly increasing"
            )

        normalized.append(
            (
                version,
                proof_hash,
            )
        )

        previous_version = version

    return tuple(normalized)


def _canonical_legacy_audit_trail(
    value: Any,
) -> Tuple[Mapping[str, Any], ...]:
    if value in (
        None,
        (),
        [],
    ):
        return ()

    if not isinstance(
        value,
        (
            list,
            tuple,
        ),
    ):
        raise TypeError(
            "legacy_audit_trail must be a list or tuple"
        )

    result = []

    for entry in value:
        if not isinstance(
            entry,
            Mapping,
        ):
            raise TypeError(
                "legacy audit entry must be a mapping"
            )

        result.append(
            _deep_freeze(
                entry
            )
        )

    return tuple(result)


def _state_lineage_digest(
    lineage: Tuple[Tuple[int, str], ...],
) -> str:
    encoded = json.dumps(
        [
            {
                "catalogueVersion": version,
                "proofHash": proof_hash,
            }
            for version, proof_hash in lineage
        ],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode(
        "utf-8"
    )

    return hashlib.sha3_512(
        encoded
    ).hexdigest().upper()

# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN ENTITIES
# ─────────────────────────────────────────────────────────────────────────────


_STATE_HISTORY_STATE_KEYS = frozenset(
    {
        "proof_version",
        "plan_id",
        "name",
        "description",
        "price",
        "currency",
        "billing_frequency",
        "trial_days",
        "plan_type",
        "features",
        "active",
        "catalogue_version",
        "tenant_id",
        "kennel_shard",
        "idempotency_key",
        "metadata",
        "tags",
        "legacy_proof_hash",
        "legacy_envelope_digest",
        "legacy_evidence_status",
        "legacy_audit_trail",
    }
)


def _canonical_state_history(
    value: Any,
) -> Tuple[Mapping[str, Any], ...]:
    """
    Validate persisted commercial-state preimages.

    This proves deterministic content consistency only. It does not convert an
    unkeyed SHA3 digest into external authenticity evidence.
    """
    if value in (
        None,
        (),
        [],
    ):
        return ()

    if not isinstance(
        value,
        (
            list,
            tuple,
        ),
    ):
        raise TypeError(
            "state_history must be a list or tuple"
        )

    normalized: list[
        Mapping[str, Any]
    ] = []

    expected_version = 1

    for index, item in enumerate(
        value
    ):
        if not isinstance(
            item,
            Mapping,
        ):
            raise TypeError(
                "state history entry must be a mapping"
            )

        allowed_entry_keys = {
            "catalogueVersion",
            "catalogue_version",
            "proofHash",
            "proof_hash",
            "state",
        }

        unexpected = (
            set(item)
            - allowed_entry_keys
        )

        if unexpected:
            raise ValueError(
                "state history entry contains unknown fields: "
                + ", ".join(
                    sorted(unexpected)
                )
            )

        camel_version_present = (
            "catalogueVersion"
            in item
        )

        snake_version_present = (
            "catalogue_version"
            in item
        )

        if not (
            camel_version_present
            or snake_version_present
        ):
            raise ValueError(
                "state history entry requires catalogueVersion"
            )

        camel_version = item.get(
            "catalogueVersion"
        )

        snake_version = item.get(
            "catalogue_version"
        )

        if (
            camel_version_present
            and snake_version_present
            and camel_version
            != snake_version
        ):
            raise ValueError(
                "conflicting state-history catalogue-version aliases"
            )

        version = _canonical_nonnegative_int(
            (
                camel_version
                if camel_version_present
                else snake_version
            ),
            field_name="state history catalogue_version",
            minimum=1,
        )

        if version != expected_version:
            raise ValueError(
                "state history must be contiguous from catalogue version 1"
            )

        camel_proof_present = (
            "proofHash"
            in item
        )

        snake_proof_present = (
            "proof_hash"
            in item
        )

        if not (
            camel_proof_present
            or snake_proof_present
        ):
            raise ValueError(
                "state history entry requires proofHash"
            )

        camel_proof = item.get(
            "proofHash"
        )

        snake_proof = item.get(
            "proof_hash"
        )

        if (
            camel_proof_present
            and snake_proof_present
            and camel_proof
            != snake_proof
        ):
            raise ValueError(
                "conflicting state-history proof aliases"
            )

        proof_hash = str(
            (
                camel_proof
                if camel_proof_present
                else snake_proof
            )
            or ""
        ).strip().upper()

        if not _SHA3_512_RE.fullmatch(
            proof_hash
        ):
            raise ValueError(
                "state history entry requires SHA3-512 proofHash"
            )

        if "state" not in item:
            raise ValueError(
                "state history entry requires canonical state preimage"
            )

        raw_state = item[
            "state"
        ]

        if not isinstance(
            raw_state,
            Mapping,
        ):
            raise TypeError(
                "state history canonical state must be a mapping"
            )

        state = _deep_thaw(
            raw_state
        )

        if not isinstance(
            state,
            dict,
        ):
            raise TypeError(
                "state history canonical state must thaw to a dictionary"
            )

        missing_state_keys = (
            _STATE_HISTORY_STATE_KEYS
            - set(state)
        )

        extra_state_keys = (
            set(state)
            - _STATE_HISTORY_STATE_KEYS
        )

        if missing_state_keys:
            raise ValueError(
                "state history canonical state is incomplete: "
                + ", ".join(
                    sorted(missing_state_keys)
                )
            )

        if extra_state_keys:
            raise ValueError(
                "state history canonical state contains unknown fields: "
                + ", ".join(
                    sorted(extra_state_keys)
                )
            )

        state_version = (
            _canonical_nonnegative_int(
                state[
                    "catalogue_version"
                ],
                field_name="historical state catalogue_version",
                minimum=1,
            )
        )

        if state_version != version:
            raise ValueError(
                "state history coordinate disagrees with canonical state"
            )

        state_proof_version = (
            _canonical_nonnegative_int(
                state[
                    "proof_version"
                ],
                field_name="historical state proof_version",
                minimum=1,
            )
        )

        if (
            state_proof_version
            != _CURRENT_PROOF_VERSION
        ):
            raise ValueError(
                "historical current-state proof version is unsupported"
            )

        recomputed = generate_plan_proof(
            state
        )

        if recomputed != proof_hash:
            raise ValueError(
                "state history proof does not match canonical historical state"
            )

        normalized.append(
            _deep_freeze(
                {
                    "catalogueVersion":
                        version,
                    "proofHash":
                        proof_hash,
                    "state":
                        state,
                }
            )
        )

        expected_version += 1

    return tuple(
        normalized
    )


@dataclass(frozen=True)
class AuditEntry:
    """Current version-2 chained audit event."""

    action: AuditAction
    timestamp: datetime
    user: str = "SYSTEM"
    reason: Optional[str] = None
    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )
    proof_hash: str = ""
    proof_version: int = _CURRENT_AUDIT_PROOF_VERSION
    plan_id: str = ""
    state_proof_hash: str = ""
    catalogue_version: int = 1
    previous_proof_hash: str = ""

    def __post_init__(
        self,
    ) -> None:
        action = self.action

        if isinstance(
            action,
            str,
        ):
            action = AuditAction(
                action.lower()
            )

        if not isinstance(
            action,
            AuditAction,
        ):
            raise TypeError(
                "action must be AuditAction"
            )

        object.__setattr__(
            self,
            "action",
            action,
        )

        timestamp = parse_datetime(
            self.timestamp
        )

        object.__setattr__(
            self,
            "timestamp",
            timestamp,
        )

        user = str(
            self.user
        ).strip() or "SYSTEM"

        object.__setattr__(
            self,
            "user",
            user,
        )

        reason = (
            None
            if self.reason is None
            else str(
                self.reason
            )
        )

        object.__setattr__(
            self,
            "reason",
            reason,
        )

        if not isinstance(
            self.metadata,
            Mapping,
        ):
            raise TypeError(
                "audit metadata must be a mapping"
            )

        object.__setattr__(
            self,
            "metadata",
            _deep_freeze(
                self.metadata
            ),
        )

        proof_version = _canonical_nonnegative_int(
            self.proof_version,
            field_name="audit proof_version",
            minimum=1,
        )

        if proof_version != _CURRENT_AUDIT_PROOF_VERSION:
            raise ValueError(
                "legacy audit trust class is not valid for AuditEntry"
            )

        object.__setattr__(
            self,
            "proof_version",
            proof_version,
        )

        catalogue_version = _canonical_nonnegative_int(
            self.catalogue_version,
            field_name="catalogue_version",
            minimum=1,
        )

        object.__setattr__(
            self,
            "catalogue_version",
            catalogue_version,
        )

        plan_id = str(
            self.plan_id
        ).strip().upper()

        state_proof_hash = str(
            self.state_proof_hash
        ).strip().upper()

        previous_proof_hash = str(
            self.previous_proof_hash
        ).strip().upper()

        if not _PLAN_ID_RE.fullmatch(
            plan_id
        ):
            raise ValueError(
                "current audit event requires governed plan_id"
            )

        if not _SHA3_512_RE.fullmatch(
            state_proof_hash
        ):
            raise ValueError(
                "current audit event requires state proof"
            )

        if (
            previous_proof_hash
            and not _SHA3_512_RE.fullmatch(
                previous_proof_hash
            )
        ):
            raise ValueError(
                "invalid audit predecessor proof"
            )

        object.__setattr__(
            self,
            "plan_id",
            plan_id,
        )

        object.__setattr__(
            self,
            "state_proof_hash",
            state_proof_hash,
        )

        object.__setattr__(
            self,
            "previous_proof_hash",
            previous_proof_hash,
        )

        expected = generate_audit_event_proof(
            action=action,
            timestamp=timestamp,
            user=user,
            reason=reason,
            metadata=self.metadata,
            plan_id=plan_id,
            state_proof_hash=state_proof_hash,
            catalogue_version=catalogue_version,
            previous_proof_hash=previous_proof_hash,
        )

        supplied = str(
            self.proof_hash
        ).strip().upper()

        if supplied and supplied != expected:
            raise ValueError(
                "audit proof does not match canonical audit event"
            )

        object.__setattr__(
            self,
            "proof_hash",
            expected,
        )

    @property
    def integrity_status(
        self,
    ) -> str:
        return "CURRENT_V2_CHAIN_CONSISTENT"

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        return {
            "action": self.action.value,
            "timestamp": self.timestamp.isoformat(),
            "user": self.user,
            "reason": self.reason,
            "metadata": _deep_thaw(
                self.metadata
            ),
            "proofHash": self.proof_hash,
            "proofVersion": self.proof_version,
            "planId": self.plan_id,
            "stateProofHash": self.state_proof_hash,
            "catalogueVersion": self.catalogue_version,
            "previousProofHash": self.previous_proof_hash,
            "integrityStatus": self.integrity_status,
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "AuditEntry":
        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "audit entry must be a dictionary"
            )

        for field_name in (
            "action",
            "timestamp",
            "user",
            "reason",
            "metadata",
        ):
            if field_name not in data:
                raise ValueError(
                    "persisted current audit event requires explicit "
                    + field_name
                )

        def required_alias(
            camel: str,
            snake: str,
            label: str,
        ) -> Any:
            camel_present = (
                camel in data
            )

            snake_present = (
                snake in data
            )

            if not (
                camel_present
                or snake_present
            ):
                raise ValueError(
                    "persisted current audit event requires "
                    + camel
                )

            camel_value = (
                data.get(
                    camel
                )
            )

            snake_value = (
                data.get(
                    snake
                )
            )

            if (
                camel_present
                and snake_present
                and camel_value
                != snake_value
            ):
                raise ValueError(
                    "conflicting audit "
                    + label
                    + " aliases"
                )

            return (
                camel_value
                if camel_present
                else snake_value
            )

        proof_version_raw = required_alias(
            "proofVersion",
            "proof_version",
            "proof-version",
        )

        proof_version = (
            _canonical_nonnegative_int(
                proof_version_raw,
                field_name="audit proof_version",
                minimum=1,
            )
        )

        if (
            proof_version
            != _CURRENT_AUDIT_PROOF_VERSION
        ):
            raise ValueError(
                "persisted current audit event requires proofVersion 2"
            )

        proof_hash_raw = required_alias(
            "proofHash",
            "proof_hash",
            "proof",
        )

        if not isinstance(
            proof_hash_raw,
            str,
        ):
            raise TypeError(
                "persisted current audit proofHash must be str"
            )

        proof_hash = (
            proof_hash_raw.strip().upper()
        )

        if not _SHA3_512_RE.fullmatch(
            proof_hash
        ):
            raise ValueError(
                "persisted current audit event requires proofHash"
            )

        plan_id_raw = required_alias(
            "planId",
            "plan_id",
            "plan-id",
        )

        state_proof_raw = required_alias(
            "stateProofHash",
            "state_proof_hash",
            "state-proof",
        )

        catalogue_raw = required_alias(
            "catalogueVersion",
            "catalogue_version",
            "catalogue-version",
        )

        predecessor_raw = required_alias(
            "previousProofHash",
            "previous_proof_hash",
            "predecessor-proof",
        )

        if not isinstance(
            predecessor_raw,
            str,
        ):
            raise TypeError(
                "persisted current audit previousProofHash must be str"
            )

        catalogue_version = (
            _canonical_nonnegative_int(
                catalogue_raw,
                field_name="catalogue_version",
                minimum=1,
            )
        )

        user = data[
            "user"
        ]

        if not isinstance(
            user,
            str,
        ) or not user.strip():
            raise ValueError(
                "persisted current audit user must be a non-empty string"
            )

        reason = data[
            "reason"
        ]

        if (
            reason is not None
            and not isinstance(
                reason,
                str,
            )
        ):
            raise TypeError(
                "persisted current audit reason must be str or None"
            )

        metadata = data[
            "metadata"
        ]

        if not isinstance(
            metadata,
            Mapping,
        ):
            raise TypeError(
                "persisted current audit metadata must be a mapping"
            )

        action_raw = data[
            "action"
        ]

        if isinstance(
            action_raw,
            AuditAction,
        ):
            action = action_raw

        elif isinstance(
            action_raw,
            str,
        ):
            action = AuditAction(
                action_raw.lower()
            )

        else:
            raise TypeError(
                "audit action is invalid"
            )

        return cls(
            action=action,
            timestamp=parse_datetime(
                data[
                    "timestamp"
                ]
            ),
            user=user,
            reason=reason,
            metadata=metadata,
            proof_hash=proof_hash,
            proof_version=proof_version,
            plan_id=str(
                plan_id_raw
            ),
            state_proof_hash=str(
                state_proof_raw
            ),
            catalogue_version=
                catalogue_version,
            previous_proof_hash=
                predecessor_raw,
        )

@dataclass(frozen=True)
class PlanEntity:
    """
    Immutable commercial Plan value.

    Construction validates commercial state only. It does not authorize
    catalogue publication, tenant access, entitlement or financial execution.
    """

    name: str
    price: float
    currency: str
    billing_frequency: PlanFrequency
    plan_type: PlanTiers
    idempotency_key: str

    plan_id: str = field(
        default_factory=lambda:
            f"WILSYPLAN-{uuid.uuid4().hex[:8].upper()}"
    )
    description: str = ""
    trial_days: int = 0
    features: Tuple[str, ...] = field(
        default_factory=tuple
    )
    active: bool = True
    catalogue_version: int = 1
    proof_version: int = _CURRENT_PROOF_VERSION
    legacy_proof_hash: str = ""
    legacy_envelope_digest: str = ""
    legacy_evidence_status: str = ""
    legacy_audit_trail: Tuple[
        Mapping[str, Any],
        ...,
    ] = field(
        default_factory=tuple
    )
    tenant_id: Optional[str] = None
    kennel_shard: str = "EOS_PRIMARY"
    seal_nonce: str = field(
        default_factory=lambda:
            uuid.uuid4().hex
    )
    proof_hash: str = ""
    state_proof_lineage: Tuple[
        Tuple[int, str],
        ...,
    ] = field(
        default_factory=tuple
    )
    state_history: Tuple[
        Mapping[str, Any],
        ...,
    ] = field(
        default_factory=tuple
    )
    integrity_root: str = ""
    audit_trail: Tuple[
        AuditEntry,
        ...,
    ] = field(
        default_factory=tuple
    )
    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )
    tags: Tuple[str, ...] = field(
        default_factory=tuple
    )
    created_at: datetime = field(
        default_factory=lambda:
            datetime.now(
                timezone.utc
            )
    )
    updated_at: datetime = field(
        default_factory=lambda:
            datetime.now(
                timezone.utc
            )
    )

    def __post_init__(
        self,
    ) -> None:
        name = str(
            self.name
        ).strip()

        if not name:
            raise ValueError(
                "name is required"
            )

        object.__setattr__(
            self,
            "name",
            name,
        )

        object.__setattr__(
            self,
            "description",
            str(
                self.description
            ).strip(),
        )

        object.__setattr__(
            self,
            "price",
            _canonical_price(
                self.price
            ),
        )

        object.__setattr__(
            self,
            "currency",
            _canonical_currency(
                self.currency
            ),
        )

        object.__setattr__(
            self,
            "plan_type",
            _canonical_plan_type(
                self.plan_type
            ),
        )

        object.__setattr__(
            self,
            "billing_frequency",
            _canonical_frequency(
                self.billing_frequency
            ),
        )

        if not isinstance(
            self.active,
            bool,
        ):
            raise TypeError(
                "active must be bool"
            )

        object.__setattr__(
            self,
            "trial_days",
            _canonical_nonnegative_int(
                self.trial_days,
                field_name="trial_days",
            ),
        )

        object.__setattr__(
            self,
            "catalogue_version",
            _canonical_nonnegative_int(
                self.catalogue_version,
                field_name="catalogue_version",
                minimum=1,
            ),
        )

        proof_version = _canonical_nonnegative_int(
            self.proof_version,
            field_name="proof_version",
            minimum=1,
        )

        if proof_version != _CURRENT_PROOF_VERSION:
            raise ValueError(
                "PlanEntity construction supports only current proof version"
            )

        object.__setattr__(
            self,
            "proof_version",
            proof_version,
        )

        plan_id = str(
            self.plan_id
        ).strip().upper()

        if not _PLAN_ID_RE.fullmatch(
            plan_id
        ):
            raise ValueError(
                "plan_id must use governed WILSYPLAN-* identity syntax"
            )

        object.__setattr__(
            self,
            "plan_id",
            plan_id,
        )

        idempotency_key = str(
            self.idempotency_key
        ).strip()

        if not idempotency_key:
            raise ValueError(
                "idempotency_key is required"
            )

        object.__setattr__(
            self,
            "idempotency_key",
            idempotency_key,
        )

        kennel_shard = str(
            self.kennel_shard
        ).strip()

        if not kennel_shard:
            raise ValueError(
                "kennel_shard is required"
            )

        object.__setattr__(
            self,
            "kennel_shard",
            kennel_shard,
        )

        tenant_id = self.tenant_id

        if tenant_id is not None:
            tenant_id = (
                str(
                    tenant_id
                ).strip()
                or None
            )

        object.__setattr__(
            self,
            "tenant_id",
            tenant_id,
        )

        seal_nonce = str(
            self.seal_nonce
        ).strip()

        if not seal_nonce:
            raise ValueError(
                "seal_nonce is required"
            )

        object.__setattr__(
            self,
            "seal_nonce",
            seal_nonce,
        )

        object.__setattr__(
            self,
            "features",
            _canonical_string_tuple(
                self.features,
                field_name="features",
            ),
        )

        object.__setattr__(
            self,
            "tags",
            _canonical_string_tuple(
                self.tags,
                field_name="tags",
            ),
        )

        if not isinstance(
            self.metadata,
            Mapping,
        ):
            raise TypeError(
                "metadata must be a mapping"
            )

        object.__setattr__(
            self,
            "metadata",
            _deep_freeze(
                self.metadata
            ),
        )

        created_at = parse_datetime(
            self.created_at
        )

        updated_at = parse_datetime(
            self.updated_at
        )

        if updated_at < created_at:
            raise ValueError(
                "updated_at cannot precede created_at"
            )

        object.__setattr__(
            self,
            "created_at",
            created_at,
        )

        object.__setattr__(
            self,
            "updated_at",
            updated_at,
        )

        legacy_proof_hash = str(
            self.legacy_proof_hash
        ).strip().upper()

        legacy_envelope_digest = str(
            self.legacy_envelope_digest
        ).strip().upper()

        legacy_status = str(
            self.legacy_evidence_status
        ).strip()

        legacy_audit = (
            _canonical_legacy_audit_trail(
                self.legacy_audit_trail
            )
        )

        if legacy_status == _LEGACY_EVIDENCE_STATUS:
            if not (
                _SHA3_512_RE.fullmatch(
                    legacy_proof_hash
                )
                and _SHA3_512_RE.fullmatch(
                    legacy_envelope_digest
                )
            ):
                raise ValueError(
                    "legacy sealed provenance requires complete SHA3-512 evidence"
                )

            expected_legacy = (
                _legacy_envelope_digest(
                    tenant_id,
                    legacy_proof_hash,
                    seal_nonce,
                )
            )

            if legacy_envelope_digest != expected_legacy:
                raise ValueError(
                    "legacy envelope evidence is inconsistent"
                )

        elif legacy_status == _LEGACY_UNSEALED_STATUS:
            if (
                legacy_proof_hash
                or legacy_envelope_digest
            ):
                raise ValueError(
                    "unsealed legacy status cannot carry sealed legacy evidence"
                )

        elif legacy_status:
            raise ValueError(
                "legacy evidence status is invalid"
            )

        elif (
            legacy_proof_hash
            or legacy_envelope_digest
            or legacy_audit
        ):
            raise ValueError(
                "legacy provenance requires explicit legacy evidence status"
            )

        object.__setattr__(
            self,
            "legacy_proof_hash",
            legacy_proof_hash,
        )

        object.__setattr__(
            self,
            "legacy_envelope_digest",
            legacy_envelope_digest,
        )

        object.__setattr__(
            self,
            "legacy_evidence_status",
            legacy_status,
        )

        object.__setattr__(
            self,
            "legacy_audit_trail",
            legacy_audit,
        )

        canonical_proof = self.generate_proof()

        supplied_proof = str(
            self.proof_hash
        ).strip().upper()

        if (
            supplied_proof
            and supplied_proof != canonical_proof
        ):
            raise ValueError(
                "proof_hash does not match canonical plan state"
            )

        object.__setattr__(
            self,
            "proof_hash",
            canonical_proof,
        )

        supplied_lineage = (
            _canonical_state_proof_lineage(
                self.state_proof_lineage
            )
        )

        history = (
            _canonical_state_history(
                self.state_history
            )
        )

        current_state = (
            self._current_state_material()
        )

        appended_current_state = False

        if not history:
            if self.catalogue_version != 1:
                raise ValueError(
                    "catalogue versions above 1 require complete state history"
                )

            history = (
                _deep_freeze(
                    {
                        "catalogueVersion":
                            self.catalogue_version,
                        "proofHash":
                            canonical_proof,
                        "state":
                            current_state,
                    }
                ),
            )

        else:
            last_version = int(
                history[-1][
                    "catalogueVersion"
                ]
            )

            if (
                last_version
                == self.catalogue_version - 1
            ):
                history = (
                    history
                    + (
                        _deep_freeze(
                            {
                                "catalogueVersion":
                                    self.catalogue_version,
                                "proofHash":
                                    canonical_proof,
                                "state":
                                    current_state,
                            }
                        ),
                    )
                )

                appended_current_state = True

            elif (
                last_version
                == self.catalogue_version
            ):
                last_proof = str(
                    history[-1][
                        "proofHash"
                    ]
                )

                last_state = (
                    _deep_thaw(
                        history[-1][
                            "state"
                        ]
                    )
                )

                if last_proof != canonical_proof:
                    raise ValueError(
                        "current state history proof does not match canonical state"
                    )

                if last_state != current_state:
                    raise ValueError(
                        "current state history preimage does not match canonical state"
                    )

            elif (
                last_version
                > self.catalogue_version
            ):
                raise ValueError(
                    "state history references future catalogue version"
                )

            else:
                raise ValueError(
                    "state history is incomplete for current catalogue version"
                )

        history = (
            _canonical_state_history(
                history
            )
        )

        derived_lineage = tuple(
            (
                int(
                    entry[
                        "catalogueVersion"
                    ]
                ),
                str(
                    entry[
                        "proofHash"
                    ]
                ),
            )
            for entry in history
        )

        if supplied_lineage:
            accepted_lineages = {
                derived_lineage,
            }

            if appended_current_state:
                accepted_lineages.add(
                    derived_lineage[:-1]
                )

            if (
                supplied_lineage
                not in accepted_lineages
            ):
                raise ValueError(
                    "state proof lineage does not match verified state history"
                )

        object.__setattr__(
            self,
            "state_history",
            history,
        )

        object.__setattr__(
            self,
            "state_proof_lineage",
            derived_lineage,
        )

        lineage = derived_lineage

        audit_trail = tuple(
            self.audit_trail
        )

        if not all(
            isinstance(
                entry,
                AuditEntry,
            )
            for entry in audit_trail
        ):
            raise TypeError(
                "audit_trail entries must be current AuditEntry values"
            )

        lineage_map = dict(lineage)
        previous_token = ""

        for entry in audit_trail:
            if entry.plan_id != plan_id:
                raise ValueError(
                    "audit entry plan_id does not match plan"
                )

            expected_state_proof = lineage_map.get(
                entry.catalogue_version
            )

            if expected_state_proof is None:
                raise ValueError(
                    "audit entry catalogue version is absent from state lineage"
                )

            if entry.state_proof_hash != expected_state_proof:
                raise ValueError(
                    "audit state proof does not resolve to plan state lineage"
                )

            if entry.previous_proof_hash != previous_token:
                raise ValueError(
                    "audit predecessor chain is invalid"
                )

            previous_token = _audit_link_token(
                entry
            )

        object.__setattr__(
            self,
            "audit_trail",
            audit_trail,
        )

        canonical_root = self._compute_integrity_root()

        supplied_root = str(
            self.integrity_root
        ).strip().upper()

        if (
            supplied_root
            and supplied_root != canonical_root
        ):
            raise ValueError(
                "integrity_root does not match canonical plan evidence envelope"
            )

        object.__setattr__(
            self,
            "integrity_root",
            canonical_root,
        )

    @property
    def merkle_root(
        self,
    ) -> str:
        """
        Compatibility alias only.

        This is a flat SHA3-512 envelope digest, not a Merkle-tree root.
        """
        return self.integrity_root

    @property
    def legacy_merkle_root(
        self,
    ) -> str:
        return self.legacy_envelope_digest

    def _current_state_material(
        self,
    ) -> Dict[str, Any]:
        return {
            "proof_version":
                self.proof_version,
            "plan_id":
                self.plan_id,
            "name":
                self.name,
            "description":
                self.description,
            "price":
                self.price,
            "currency":
                self.currency,
            "billing_frequency":
                self.billing_frequency.value,
            "trial_days":
                self.trial_days,
            "plan_type":
                self.plan_type.value,
            "features":
                list(
                    self.features
                ),
            "active":
                self.active,
            "catalogue_version":
                self.catalogue_version,
            "tenant_id":
                self.tenant_id,
            "kennel_shard":
                self.kennel_shard,
            "idempotency_key":
                self.idempotency_key,
            "metadata":
                _deep_thaw(
                    self.metadata
                ),
            "tags":
                list(
                    self.tags
                ),
            "legacy_proof_hash":
                self.legacy_proof_hash,
            "legacy_envelope_digest":
                self.legacy_envelope_digest,
            "legacy_evidence_status":
                self.legacy_evidence_status,
            "legacy_audit_trail": [
                _deep_thaw(
                    entry
                )
                for entry
                in self.legacy_audit_trail
            ],
        }

    def _compute_state_history_digest(
        self,
    ) -> str:
        encoded = json.dumps(
            [
                _deep_thaw(
                    entry
                )
                for entry
                in self.state_history
            ],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode(
            "utf-8"
        )

        return hashlib.sha3_512(
            encoded
        ).hexdigest().upper()

    def _compute_audit_chain_head(
        self,
    ) -> str:
        encoded = json.dumps(
            [
                entry.to_dict()
                for entry in self.audit_trail
            ],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode(
            "utf-8"
        )

        return hashlib.sha3_512(
            encoded
        ).hexdigest().upper()

    def _compute_state_lineage_digest(
        self,
    ) -> str:
        return _state_lineage_digest(
            self.state_proof_lineage
        )

    def _compute_integrity_root(
        self,
    ) -> str:
        payload = {
            "semantics":
                _INTEGRITY_ROOT_SEMANTICS,
            "stateHistorySemantics":
                _STATE_HISTORY_SEMANTICS,
            "tenantId":
                self.tenant_id or "GLOBAL",
            "proofHash":
                self.proof_hash,
            "sealNonce":
                self.seal_nonce,
            "stateProofLineageDigest":
                self._compute_state_lineage_digest(),
            "stateHistoryDigest":
                self._compute_state_history_digest(),
            "auditChainHead":
                self._compute_audit_chain_head(),
        }

        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode(
            "utf-8"
        )

        return hashlib.sha3_512(
            encoded
        ).hexdigest().upper()

    def generate_proof(
        self,
        action: str = "save",
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> str:
        return generate_plan_proof(
            self._current_state_material(),
            action=action,
            metadata=metadata,
        )

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "currency": self.currency,
            "billing_frequency":
                self.billing_frequency.value,
            "trial_days":
                self.trial_days,
            "plan_type":
                self.plan_type.value,
            "features": list(
                self.features
            ),
            "active":
                self.active,
            "catalogue_version":
                self.catalogue_version,
            "proof_version":
                self.proof_version,
            "legacy_proof_hash":
                self.legacy_proof_hash,
            "legacy_envelope_digest":
                self.legacy_envelope_digest,
            "legacy_evidence_status":
                self.legacy_evidence_status,
            "legacy_audit_trail": [
                _deep_thaw(entry)
                for entry in self.legacy_audit_trail
            ],
            "tenant_id":
                self.tenant_id,
            "kennel_shard":
                self.kennel_shard,
            "idempotency_key":
                self.idempotency_key,
            "seal_nonce":
                self.seal_nonce,
            "proof_hash":
                self.proof_hash,
            "state_proof_lineage": [
                {
                    "catalogueVersion":
                        version,
                    "proofHash":
                        proof_hash,
                }
                for version, proof_hash
                in self.state_proof_lineage
            ],
            "state_history": [
                _deep_thaw(
                    entry
                )
                for entry
                in self.state_history
            ],
            "integrity_root":
                self.integrity_root,
            "merkle_root":
                self.integrity_root,
            "audit_trail": [
                entry.to_dict()
                for entry in self.audit_trail
            ],
            "metadata":
                _deep_thaw(
                    self.metadata
                ),
            "tags": list(
                self.tags
            ),
            "created_at":
                self.created_at.isoformat(),
            "updated_at":
                self.updated_at.isoformat(),
            "integrity_root_semantics":
                _INTEGRITY_ROOT_SEMANTICS,
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "PlanEntity":
        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "plan data must be a dictionary"
            )

        snake_version_present = (
            "proof_version" in data
        )

        camel_version_present = (
            "proofVersion" in data
        )

        snake_version = data.get(
            "proof_version"
        )

        camel_version = data.get(
            "proofVersion"
        )

        if (
            snake_version_present
            and camel_version_present
            and snake_version
            != camel_version
        ):
            raise ValueError(
                "conflicting plan proof-version aliases"
            )

        raw_proof_version = (
            snake_version
            if snake_version_present
            else camel_version
        )

        if raw_proof_version != _CURRENT_PROOF_VERSION:
            if raw_proof_version is None:
                raise ValueError(
                    "unversioned persisted record requires explicit legacy migration"
                )

            raise ValueError(
                "unsupported persisted plan proof version"
            )

        incoming_proof = str(
            data.get(
                "proof_hash",
                data.get(
                    "proofHash",
                    "",
                ),
            )
            or ""
        ).strip().upper()

        if not _SHA3_512_RE.fullmatch(
            incoming_proof
        ):
            raise ValueError(
                "current persisted record requires complete proof_hash"
            )

        canonical_root_raw = (
            data.get(
                "integrity_root"
            )
            or data.get(
                "integrityRoot"
            )
        )

        compatibility_root_raw = (
            data.get(
                "merkle_root"
            )
            or data.get(
                "merkleRoot"
            )
        )

        if (
            canonical_root_raw
            and compatibility_root_raw
            and str(
                canonical_root_raw
            ).strip().upper()
            != str(
                compatibility_root_raw
            ).strip().upper()
        ):
            raise ValueError(
                "integrity root and compatibility merkle alias disagree"
            )

        incoming_root = str(
            canonical_root_raw
            or compatibility_root_raw
            or ""
        ).strip().upper()

        if not _SHA3_512_RE.fullmatch(
            incoming_root
        ):
            raise ValueError(
                "current persisted record requires complete integrity_root"
            )

        snake_lineage_present = (
            "state_proof_lineage"
            in data
        )

        camel_lineage_present = (
            "stateProofLineage"
            in data
        )

        if not (
            snake_lineage_present
            or camel_lineage_present
        ):
            raise ValueError(
                "current persisted record requires state proof lineage"
            )

        snake_lineage = (
            _canonical_state_proof_lineage(
                data[
                    "state_proof_lineage"
                ]
            )
            if snake_lineage_present
            else ()
        )

        camel_lineage = (
            _canonical_state_proof_lineage(
                data[
                    "stateProofLineage"
                ]
            )
            if camel_lineage_present
            else ()
        )

        if (
            snake_lineage_present
            and camel_lineage_present
            and snake_lineage
            != camel_lineage
        ):
            raise ValueError(
                "conflicting state-proof-lineage aliases"
            )

        incoming_lineage = (
            snake_lineage
            if snake_lineage_present
            else camel_lineage
        )

        if not incoming_lineage:
            raise ValueError(
                "current persisted record requires state proof lineage"
            )

        snake_history_present = (
            "state_history"
            in data
        )

        camel_history_present = (
            "stateHistory"
            in data
        )

        if not (
            snake_history_present
            or camel_history_present
        ):
            raise ValueError(
                "current persisted record requires canonical state history"
            )

        snake_history = (
            _canonical_state_history(
                data[
                    "state_history"
                ]
            )
            if snake_history_present
            else ()
        )

        camel_history = (
            _canonical_state_history(
                data[
                    "stateHistory"
                ]
            )
            if camel_history_present
            else ()
        )

        if (
            snake_history_present
            and camel_history_present
            and snake_history
            != camel_history
        ):
            raise ValueError(
                "conflicting state-history aliases"
            )

        incoming_history = (
            snake_history
            if snake_history_present
            else camel_history
        )

        if not incoming_history:
            raise ValueError(
                "current persisted record requires canonical state history"
            )

        legacy_envelope_raw = (
            data.get(
                "legacy_envelope_digest"
            )
            or data.get(
                "legacyEnvelopeDigest"
            )
        )

        legacy_merkle_alias = (
            data.get(
                "legacy_merkle_root"
            )
            or data.get(
                "legacyMerkleRoot"
            )
        )

        if (
            legacy_envelope_raw
            and legacy_merkle_alias
            and str(
                legacy_envelope_raw
            ).strip().upper()
            != str(
                legacy_merkle_alias
            ).strip().upper()
        ):
            raise ValueError(
                "legacy envelope aliases disagree"
            )

        audit_entries = tuple(
            AuditEntry.from_dict(
                entry
            )
            for entry in data.get(
                "audit_trail",
                data.get(
                    "auditTrail",
                    [],
                ),
            )
        )

        entity = cls(
            name=data["name"],
            price=data["price"],
            currency=data["currency"],
            billing_frequency=
                _canonical_frequency(
                    data.get(
                        "billing_frequency",
                        data.get(
                            "billingFrequency",
                            "monthly",
                        ),
                    )
                ),
            plan_type=
                _canonical_plan_type(
                    data.get(
                        "plan_type",
                        data.get(
                            "planType",
                            "PROFESSIONAL",
                        ),
                    )
                ),
            idempotency_key=(
                data.get(
                    "idempotency_key"
                )
                or data.get(
                    "idempotencyKey"
                )
                or ""
            ),
            plan_id=(
                data.get(
                    "plan_id"
                )
                or data.get(
                    "planId"
                )
                or ""
            ),
            description=data.get(
                "description",
                "",
            ),
            trial_days=data.get(
                "trial_days",
                data.get(
                    "trialDays",
                    0,
                ),
            ),
            features=data.get(
                "features",
                [],
            ),
            active=data.get(
                "active",
                True,
            ),
            catalogue_version=data.get(
                "catalogue_version",
                data.get(
                    "catalogueVersion",
                    1,
                ),
            ),
            proof_version=
                _CURRENT_PROOF_VERSION,
            legacy_proof_hash=str(
                data.get(
                    "legacy_proof_hash",
                    data.get(
                        "legacyProofHash",
                        "",
                    ),
                )
                or ""
            ),
            legacy_envelope_digest=str(
                legacy_envelope_raw
                or legacy_merkle_alias
                or ""
            ),
            legacy_evidence_status=str(
                data.get(
                    "legacy_evidence_status",
                    data.get(
                        "legacyEvidenceStatus",
                        "",
                    ),
                )
                or ""
            ),
            legacy_audit_trail=data.get(
                "legacy_audit_trail",
                data.get(
                    "legacyAuditTrail",
                    [],
                ),
            ),
            tenant_id=(
                data.get(
                    "tenant_id"
                )
                or data.get(
                    "tenantId"
                )
            ),
            kennel_shard=data.get(
                "kennel_shard",
                data.get(
                    "kennelShard",
                    "EOS_PRIMARY",
                ),
            ),
            seal_nonce=(
                data.get(
                    "seal_nonce"
                )
                or data.get(
                    "sealNonce"
                )
                or ""
            ),
            proof_hash=incoming_proof,
            state_proof_lineage=incoming_lineage,
            state_history=incoming_history,
            integrity_root=incoming_root,
            audit_trail=audit_entries,
            metadata=data.get(
                "metadata",
                {},
            ),
            tags=data.get(
                "tags",
                [],
            ),
            created_at=parse_datetime(
                data.get(
                    "created_at",
                    data.get(
                        "createdAt"
                    ),
                )
            ),
            updated_at=parse_datetime(
                data.get(
                    "updated_at",
                    data.get(
                        "updatedAt"
                    ),
                )
            ),
        )

        if entity.state_proof_lineage != incoming_lineage:
            raise ValueError(
                "persisted current state proof lineage is incomplete"
            )

        if entity.state_history != incoming_history:
            raise ValueError(
                "persisted current canonical state history is incomplete"
            )

        return entity

    @classmethod
    def migrate_legacy_dict(
        cls,
        data: Dict[str, Any],
    ) -> "PlanEntity":
        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "legacy plan data must be a dictionary"
            )

        if (
            "proof_version" in data
            or "proofVersion" in data
        ):
            raise ValueError(
                "legacy migration accepts only unversioned records"
            )

        forbidden_current_markers = {
            "integrity_root",
            "integrityRoot",
            "state_proof_lineage",
            "stateProofLineage",
            "state_history",
            "stateHistory",
            "integrity_root_semantics",
            "integrityRootSemantics",
            "legacy_evidence_status",
            "legacyEvidenceStatus",
            "legacy_envelope_digest",
            "legacyEnvelopeDigest",
        }

        present = (
            forbidden_current_markers
            & set(data)
        )

        if present:
            raise ValueError(
                "legacy migration rejected current-schema markers: "
                + ", ".join(
                    sorted(present)
                )
            )

        created_raw = (
            data.get(
                "created_at"
            )
            or data.get(
                "createdAt"
            )
        )

        updated_raw = (
            data.get(
                "updated_at"
            )
            or data.get(
                "updatedAt"
            )
        )

        if (
            created_raw is None
            or updated_raw is None
        ):
            raise ValueError(
                "legacy migration requires historical created_at and updated_at"
            )

        tenant_id = (
            data.get(
                "tenant_id"
            )
            or data.get(
                "tenantId"
            )
        )

        incoming_proof = str(
            data.get(
                "proof_hash",
                data.get(
                    "proofHash",
                    "",
                ),
            )
            or ""
        ).strip().upper()

        incoming_envelope = str(
            data.get(
                "merkle_root",
                data.get(
                    "merkleRoot",
                    "",
                ),
            )
            or ""
        ).strip().upper()

        raw_seal_nonce = (
            data.get(
                "seal_nonce"
            )
            or data.get(
                "sealNonce"
            )
        )

        seed = _legacy_plan_seed(
            data
        )

        seal_nonce = (
            str(
                raw_seal_nonce
            ).strip()
            if raw_seal_nonce
            else (
                "LEGACY-"
                + seed[:32]
            )
        )

        legacy_status = (
            _LEGACY_UNSEALED_STATUS
        )
        legacy_proof_hash = ""
        legacy_envelope_digest = ""

        if (
            incoming_proof
            or incoming_envelope
        ):
            if not (
                incoming_proof
                and incoming_envelope
                and raw_seal_nonce
            ):
                raise ValueError(
                    "sealed legacy migration requires proof, envelope and seal nonce"
                )

            if not (
                _SHA3_512_RE.fullmatch(
                    incoming_proof
                )
                and _SHA3_512_RE.fullmatch(
                    incoming_envelope
                )
            ):
                raise ValueError(
                    "legacy sealed evidence must use SHA3-512 hex"
                )

            expected_envelope = (
                _legacy_envelope_digest(
                    tenant_id,
                    incoming_proof,
                    seal_nonce,
                )
            )

            if incoming_envelope != expected_envelope:
                raise ValueError(
                    "legacy envelope evidence is inconsistent"
                )

            legacy_status = (
                _LEGACY_EVIDENCE_STATUS
            )
            legacy_proof_hash = (
                incoming_proof
            )
            legacy_envelope_digest = (
                incoming_envelope
            )

        legacy_audit = data.get(
            "audit_trail",
            data.get(
                "auditTrail",
                [],
            ),
        )

        if legacy_audit:
            if not isinstance(
                legacy_audit,
                (
                    list,
                    tuple,
                ),
            ):
                raise TypeError(
                    "legacy audit trail must be a list or tuple"
                )

            current_audit_structural_markers = {
                "stateProofHash",
                "state_proof_hash",
                "catalogueVersion",
                "catalogue_version",
                "previousProofHash",
                "previous_proof_hash",
            }

            for index, entry in enumerate(
                legacy_audit
            ):
                if not isinstance(
                    entry,
                    Mapping,
                ):
                    raise TypeError(
                        "legacy audit entry must be a mapping"
                    )

                entry_keys = set(
                    entry
                )

                current_markers = (
                    current_audit_structural_markers
                    & entry_keys
                )

                camel_audit_version_present = (
                    "proofVersion"
                    in entry
                )

                snake_audit_version_present = (
                    "proof_version"
                    in entry
                )

                camel_audit_version = entry.get(
                    "proofVersion"
                )

                snake_audit_version = entry.get(
                    "proof_version"
                )

                if (
                    camel_audit_version_present
                    and snake_audit_version_present
                    and camel_audit_version
                    != snake_audit_version
                ):
                    raise ValueError(
                        "legacy audit entry contains conflicting proof-version aliases"
                    )

                audit_version = (
                    camel_audit_version
                    if camel_audit_version_present
                    else snake_audit_version
                )

                integrity_status = str(
                    entry.get(
                        "integrityStatus",
                        entry.get(
                            "integrity_status",
                            "",
                        ),
                    )
                    or ""
                ).strip().upper()

                if (
                    audit_version
                    == _CURRENT_AUDIT_PROOF_VERSION
                    or current_markers
                    or integrity_status.startswith(
                        "CURRENT_V2"
                    )
                ):
                    raise ValueError(
                        "legacy migration rejected current-v2 audit evidence "
                        f"at index {index}"
                    )

        if (
            legacy_audit
            and not legacy_status
        ):
            legacy_status = (
                _LEGACY_UNSEALED_STATUS
            )

        return cls(
            name=data["name"],
            price=data["price"],
            currency=data["currency"],
            billing_frequency=
                _canonical_frequency(
                    data.get(
                        "billing_frequency",
                        data.get(
                            "billingFrequency",
                            "monthly",
                        ),
                    )
                ),
            plan_type=
                _canonical_plan_type(
                    data.get(
                        "plan_type",
                        data.get(
                            "planType",
                            "PROFESSIONAL",
                        ),
                    )
                ),
            idempotency_key=(
                data.get(
                    "idempotency_key"
                )
                or data.get(
                    "idempotencyKey"
                )
                or _legacy_idempotency_key(
                    data
                )
            ),
            plan_id=(
                data.get(
                    "plan_id"
                )
                or data.get(
                    "planId"
                )
                or _legacy_plan_id(
                    data
                )
            ),
            description=data.get(
                "description",
                "",
            ),
            trial_days=data.get(
                "trial_days",
                data.get(
                    "trialDays",
                    0,
                ),
            ),
            features=data.get(
                "features",
                [],
            ),
            active=data.get(
                "active",
                True,
            ),
            catalogue_version=1,
            proof_version=
                _CURRENT_PROOF_VERSION,
            legacy_proof_hash=
                legacy_proof_hash,
            legacy_envelope_digest=
                legacy_envelope_digest,
            legacy_evidence_status=
                legacy_status,
            legacy_audit_trail=
                _canonical_legacy_audit_trail(
                    legacy_audit
                ),
            tenant_id=
                tenant_id,
            kennel_shard=data.get(
                "kennel_shard",
                data.get(
                    "kennelShard",
                    "EOS_PRIMARY",
                ),
            ),
            seal_nonce=
                seal_nonce,
            metadata=data.get(
                "metadata",
                {},
            ),
            tags=data.get(
                "tags",
                [],
            ),
            created_at=parse_datetime(
                created_raw
            ),
            updated_at=parse_datetime(
                updated_raw
            ),
        )

    def update(
        self,
        updates: Dict[str, Any],
    ) -> "PlanEntity":
        if not isinstance(
            updates,
            Mapping,
        ):
            raise TypeError(
                "updates must be a mapping"
            )

        commercial_updates = {
            key: value
            for key, value
            in updates.items()
            if key
            not in _NONCOMMERCIAL_UPDATE_CONTEXT_FIELDS
        }

        illegal = (
            set(commercial_updates)
            - _UPDATABLE_COMMERCIAL_FIELDS
        )

        if illegal:
            raise ValueError(
                "protected or unknown plan fields cannot be updated: "
                + ", ".join(
                    sorted(illegal)
                )
            )

        if not commercial_updates:
            return self

        return replace(
            self,
            **commercial_updates,
            catalogue_version=(
                self.catalogue_version + 1
            ),
            updated_at=datetime.now(
                timezone.utc
            ),
            proof_hash="",
            integrity_root="",
        )

    def add_audit_entry(
        self,
        action: AuditAction,
        user: str = "SYSTEM",
        reason: Optional[str] = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> "PlanEntity":
        evidence_metadata = (
            metadata or {}
        )

        if not isinstance(
            evidence_metadata,
            Mapping,
        ):
            raise TypeError(
                "audit metadata must be a mapping"
            )

        previous_proof_hash = (
            self.audit_trail[-1].proof_hash
            if self.audit_trail
            else ""
        )

        entry = AuditEntry(
            action=action,
            timestamp=datetime.now(
                timezone.utc
            ),
            user=user,
            reason=reason,
            metadata=evidence_metadata,
            proof_version=
                _CURRENT_AUDIT_PROOF_VERSION,
            plan_id=self.plan_id,
            state_proof_hash=
                self.proof_hash,
            catalogue_version=
                self.catalogue_version,
            previous_proof_hash=
                previous_proof_hash,
        )

        return replace(
            self,
            audit_trail=(
                self.audit_trail
                + (entry,)
            ),
            updated_at=datetime.now(
                timezone.utc
            ),
            integrity_root="",
        )

    def generate_evidence_package(
        self,
    ) -> Dict[str, Any]:
        sensitive = {
            "pii",
            "email",
            "phone",
            "ipAddress",
            "fullName",
            "nationalId",
        }

        safe_metadata = {
            key: _deep_thaw(value)
            for key, value
            in self.metadata.items()
            if key not in sensitive
        }

        package: Dict[str, Any] = {
            "_id":
                self.plan_id,
            "name":
                self.name,
            "description":
                self.description,
            "planType":
                self.plan_type.value,
            "price":
                self.price,
            "currency":
                self.currency,
            "billingFrequency":
                self.billing_frequency.value,
            "trialDays":
                self.trial_days,
            "features":
                list(self.features),
            "active":
                self.active,
            "catalogueVersion":
                self.catalogue_version,
            "proofVersion":
                self.proof_version,
            "tenantId":
                self.tenant_id,
            "kennelShard":
                self.kennel_shard,
            "proofHash":
                self.proof_hash,
            "integrityRoot":
                self.integrity_root,
            "integrityRootSemantics":
                _INTEGRITY_ROOT_SEMANTICS,
            "merkleRootCompatibilityAlias":
                self.integrity_root,
            "stateProofLineage": [
                {
                    "catalogueVersion":
                        version,
                    "proofHash":
                        proof_hash,
                }
                for version, proof_hash
                in self.state_proof_lineage
            ],
            "stateHistory": [
                _deep_thaw(
                    entry
                )
                for entry
                in self.state_history
            ],
            "stateHistorySemantics":
                _STATE_HISTORY_SEMANTICS,
            "auditChainHead":
                self._compute_audit_chain_head(),
            "auditTrail": [
                entry.to_dict()
                for entry
                in self.audit_trail
            ],
            "legacyProofHash":
                self.legacy_proof_hash,
            "legacyEnvelopeDigest":
                self.legacy_envelope_digest,
            "legacyEvidenceStatus":
                self.legacy_evidence_status,
            "legacyAuditTrail": [
                _deep_thaw(entry)
                for entry
                in self.legacy_audit_trail
            ],
            "generatedAt":
                datetime.now(
                    timezone.utc
                ).isoformat(),
            "compliance": {
                "popia": True,
                "gdpr": True,
                "soc2": True,
                "iso27001": True,
            },
            "metadata":
                safe_metadata,
            "tags":
                list(self.tags),
        }

        encoded = json.dumps(
            package,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode(
            "utf-8"
        )

        package["evidenceSeal"] = (
            hashlib.sha3_512(
                encoded
            ).hexdigest().upper()
        )

        return package

"""
════════════════════════════════════════════════════════════════════════════════
INSTITUTIONAL CERTIFICATION SEAL — WILSY OS PLAN DOMAIN COMMERCIAL CONTRACT
════════════════════════════════════════════════════════════════════════════════
Status:              PRODUCTION CONTRACT — DIRECT CERTIFICATION REQUIRED
Version:             v1.1.9-LEGACY-UNSEALED-PROVENANCE
Authority:           Wilsy OS Core Governance
Canonical path:      /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/plan.py
Commercial truth:    Python EOS
Persistence owner:   PlanRegistry
Financial execution: NONE — Kennel EOS remains exclusive
Tenant authority:    NONE — tenant_id is scope evidence only
Proof posture:       Deterministic SHA3-512 commercial-state evidence
Public API:          PlanEntity / enums / parse_datetime / generate_plan_proof
Pending work:        Real-Mongo PlanRegistry certification
Certification date:  2026-09-03
════════════════════════════════════════════════════════════════════════════════
WILSY OS — ALL OR NOTHING.
"""
