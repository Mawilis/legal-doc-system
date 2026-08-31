# -*- coding: utf-8 -*-
"""TITLE: WILSY OS — WILSY INTELLIGENCE DOCK FACADE.

VERSION: 1.0.0
AUTHORITY: Wilsy OS Core Governance
EPITOME:
    Sovereign composition boundary for the Wilsy Intelligence Dock. The facade
    packages caller-authorized observations, knowledge-graph registration, and
    optional governed recommendations into deterministic intelligence-cycle
    receipts without manufacturing identity, tenant scope, evidence, confidence,
    approval, execution authority, or financial authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/intelligence_facade.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy OS Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-08-31

CHANGELOG:
    1.0.0:
        Resets the legacy FG229 facade to a sovereign Intelligence Dock baseline.

        Removes:
        - implicit subsystem observation generation;
        - synthetic ONLINE / operational-health assertions;
        - static autonomous-operation targeting;
        - automatic invocation of legacy synthetic reasoning;
        - automatic invocation of legacy approval-bearing explanation logic;
        - caller-free tenant/workspace/resource scope;
        - non-canonical string hashing;
        - implicit execution ownership.

        Introduces:
        - explicit intelligence-cycle identity;
        - explicit caller-authorized scope reference;
        - immutable Observation / Recommendation domain contracts;
        - strict same-scope composition;
        - duplicate observation rejection;
        - scope-separated knowledge-graph entity keys;
        - evidence-bound receipt material;
        - deterministic canonical SHA-256 receipts;
        - explicit NO_EVIDENCE semantics;
        - advisory-only authority posture;
        - dependency injection for the knowledge graph;
        - tenant-scoped local graph accounting;
        - fail-closed boundary validation.

COMPLIANCE:
    POPIA section 19;
    GDPR Article 32;
    SOC 2 CC7.2;
    ISO 27001-aligned integrity, minimization, traceability,
    tenant separation, and fail-closed operation.

SECURITY / PRIVACY POSTURE:
    This facade does not authenticate principals, derive identity, inspect tokens,
    infer tenant membership, or persist credentials. Callers must supply only
    observations and recommendations already authorized for the explicit scope.

TENANT BOUNDARY:
    ``scope_ref`` is an opaque reference to scope already resolved and authorized
    by a sovereign caller. Every observation and recommendation must carry the
    exact same scope reference. This facade never establishes, widens, merges,
    or infers scope.

AUTHORITY BOUNDARY:
    Intelligence-cycle output is descriptive and advisory only. Observations,
    recommendations, explanations, cycle receipts, and knowledge-graph registration
    do not grant business mutation authority, approval authority, autonomous
    execution authority, identity authority, or tenant authority.

FINANCIAL AUTHORITY BOUNDARY:
    Kennel EOS exclusively owns financial execution. Nothing in this artifact can
    approve, release, settle, transfer, execute, or infer financial authority.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional, Sequence, Tuple

from tools.eos.intelligence.domain.observation import (
    Observation,
    Recommendation,
)
from tools.eos.intelligence.knowledge.knowledge_graph import (
    KnowledgeGraphEngine,
)


VERSION = "1.0.0"

_PLATFORM_NAME = "Wilsy Intelligence Dock"
_ADVISORY_POSTURE = "ADVISORY_ONLY"
_FINANCIAL_EXECUTION_AUTHORITY = "KENNEL_EOS_EXCLUSIVE"

_OBSERVATION_EVIDENCE_PRESENT = "OBSERVATION_EVIDENCE_PRESENT"
_NO_OBSERVATION_EVIDENCE = "NO_OBSERVATION_EVIDENCE"

_GOVERNED_RECOMMENDATION_PRESENT = "GOVERNED_RECOMMENDATION_PRESENT"
_NO_RECOMMENDATION = "NO_RECOMMENDATION"


def _require_non_blank_string(
    value: Any,
    field_name: str,
    *,
    max_length: int = 512,
) -> str:
    """Return a trimmed non-blank string or fail closed."""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")

    normalized = value.strip()

    if not normalized:
        raise ValueError(f"{field_name} must be non-blank")

    if len(normalized) > max_length:
        raise ValueError(
            f"{field_name} exceeds maximum length {max_length}"
        )

    return normalized


def _require_identifier(
    value: Any,
    field_name: str,
) -> str:
    """Validate an explicit identifier without manufacturing a fallback."""
    normalized = _require_non_blank_string(
        value,
        field_name,
        max_length=256,
    )

    if any(character.isspace() for character in normalized):
        raise ValueError(
            f"{field_name} must not contain whitespace"
        )

    return normalized


def _canonical_sha256(
    payload: Dict[str, Any],
) -> str:
    """Return a deterministic SHA-256 integrity anchor.

    The checksum proves integrity of the serialized payload only.

    It does not prove:
    - evidence existence;
    - evidence authority;
    - tenant membership;
    - resource authorization;
    - recommendation correctness;
    - execution authority.
    """
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )

    digest = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()

    return f"sha256:{digest}"


def _scope_partition_key(
    scope_ref: str,
) -> str:
    """Return a non-authoritative deterministic scope partition key."""
    digest = hashlib.sha256(
        scope_ref.encode("utf-8")
    ).hexdigest()

    return f"SCOPE-{digest[:32].upper()}"


def _graph_entity_key(
    *,
    scope_ref: str,
    entity_type: str,
    entity_id: str,
) -> str:
    """Derive a tenant-separated technical knowledge-graph key.

    This technical key prevents direct identifier collisions between otherwise
    identical entity IDs from different authorized scopes.

    It is not evidence and does not grant authority.
    """
    canonical = json.dumps(
        {
            "scope_ref": scope_ref,
            "entity_type": entity_type,
            "entity_id": entity_id,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    digest = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()

    return f"KG-{digest[:40].upper()}"


def _normalize_observations(
    observations: Sequence[Observation],
    *,
    scope_ref: str,
) -> Tuple[Observation, ...]:
    """Validate a same-scope immutable observation collection.

    Empty history is permitted.

    Empty history remains explicitly empty and is never transformed into
    healthy, nominal, pristine, successful, or synthetic evidence.
    """
    if isinstance(observations, (str, bytes)):
        raise ValueError(
            "observations must be a sequence of Observation entities"
        )

    if not isinstance(observations, Sequence):
        raise ValueError(
            "observations must be a sequence of Observation entities"
        )

    normalized = tuple(observations)

    seen_ids: set[str] = set()

    for observation in normalized:
        if not isinstance(observation, Observation):
            raise TypeError(
                "observations must contain only Observation entities"
            )

        if observation.scope_ref != scope_ref:
            raise ValueError(
                "observation scope_ref does not match the "
                "authorized intelligence-cycle scope"
            )

        if observation.observation_id in seen_ids:
            raise ValueError(
                "duplicate observation_id is forbidden: "
                f"{observation.observation_id}"
            )

        seen_ids.add(
            observation.observation_id
        )

    return normalized


def _validate_recommendation(
    recommendation: Optional[Recommendation],
    *,
    scope_ref: str,
) -> Optional[Recommendation]:
    """Validate an optional already-governed recommendation.

    The facade does not manufacture a recommendation.

    Recommendation production belongs to an evidence-bound reasoning component.
    """
    if recommendation is None:
        return None

    if not isinstance(
        recommendation,
        Recommendation,
    ):
        raise TypeError(
            "recommendation must be a Recommendation entity or None"
        )

    if recommendation.scope_ref != scope_ref:
        raise ValueError(
            "recommendation scope_ref does not match the "
            "authorized intelligence-cycle scope"
        )

    return recommendation


def _observation_receipt(
    observation: Observation,
) -> Dict[str, Any]:
    """Return receipt material for one observed entity."""
    return {
        "observation_id": observation.observation_id,
        "checksum": observation.checksum,
        "source_subsystem": observation.source_subsystem,
        "metric_key": observation.metric_key,
        "timestamp": observation.timestamp,
    }


def _recommendation_receipt(
    recommendation: Recommendation,
) -> Dict[str, Any]:
    """Return integrity-bound recommendation receipt material."""
    return {
        "recommendation_id": recommendation.recommendation_id,
        "checksum": recommendation.checksum,
        "evidence_chain": list(
            recommendation.evidence_chain
        ),
        "confidence_score": recommendation.confidence_score,
        "confidence_basis": recommendation.confidence_basis,
        "risk_level": recommendation.risk_level,
    }


def _recommendation_explanation(
    recommendation: Recommendation,
) -> Dict[str, Any]:
    """Return neutral explainability without manufacturing approval.

    This deliberately replaces the legacy explanation behavior that declared
    static governance approval and execution ownership.
    """
    return {
        "recommendation_id": (
            recommendation.recommendation_id
        ),
        "action": (
            recommendation.action_title
        ),
        "target_subsystem": (
            recommendation.target_subsystem
        ),
        "rationale": (
            recommendation.rationale
        ),
        "confidence_score": (
            recommendation.confidence_score
        ),
        "confidence_basis": (
            recommendation.confidence_basis
        ),
        "risk_level": (
            recommendation.risk_level
        ),
        "evidence_chain": list(
            recommendation.evidence_chain
        ),
        "traceability_checksum": (
            recommendation.checksum
        ),
        "authority_posture": (
            _ADVISORY_POSTURE
        ),
        "approval_granted": False,
        "execution_authority_granted": False,
        "financial_execution_authority": (
            _FINANCIAL_EXECUTION_AUTHORITY
        ),
    }


class WilsyIntelligencePlatform:
    """Sovereign facade for evidence-bound Intelligence Dock composition.

    Authority:
        Composition and advisory packaging only.

        This class does not:
        - authenticate;
        - derive identity;
        - derive tenant membership;
        - authorize;
        - mutate business state;
        - approve actions;
        - execute operations;
        - execute financial transactions.

    Tenant scope:
        Every cycle requires an explicit caller-authorized ``scope_ref``.

        Mixed-scope observations or recommendations fail closed.

    Evidence posture:
        The facade consumes explicit Observation and Recommendation entities.

        It does not invoke legacy synthetic observers/reasoners and does not
        manufacture substitute evidence when no observations exist.

    Financial boundary:
        Kennel EOS remains the exclusive financial execution authority.
    """

    def __init__(
        self,
        knowledge_graph: Optional[KnowledgeGraphEngine] = None,
    ) -> None:
        self._knowledge_graph = (
            knowledge_graph
            if knowledge_graph is not None
            else KnowledgeGraphEngine()
        )

        self._scope_entities: Dict[
            str,
            set[str],
        ] = {}

    @property
    def platform_name(self) -> str:
        """Return the stable Intelligence Dock product name."""
        return _PLATFORM_NAME

    @property
    def version(self) -> str:
        """Return the sovereign facade contract version."""
        return VERSION

    @property
    def knowledge_graph(
        self,
    ) -> KnowledgeGraphEngine:
        """Return the configured knowledge-graph dependency.

        Exposure of this dependency does not alter its authority boundary.
        """
        return self._knowledge_graph

    def _register_scope_entity(
        self,
        *,
        scope_ref: str,
        entity_id: str,
        entity_type: str,
        payload: Dict[str, Any],
    ) -> str:
        """Register one entity using a scope-separated graph key."""
        graph_key = _graph_entity_key(
            scope_ref=scope_ref,
            entity_type=entity_type,
            entity_id=entity_id,
        )

        graph_payload = {
            **payload,
            "scope_partition": _scope_partition_key(
                scope_ref
            ),
            "authority_posture": (
                _ADVISORY_POSTURE
            ),
        }

        self._knowledge_graph.register_entity(
            graph_key,
            entity_type,
            graph_payload,
        )

        scope_entities = self._scope_entities.setdefault(
            scope_ref,
            set(),
        )

        scope_entities.add(
            graph_key
        )

        return graph_key

    def run_intelligence_cycle(
        self,
        *,
        cycle_id: str,
        scope_ref: str,
        observations: Sequence[Observation],
        recommendation: Optional[Recommendation] = None,
    ) -> Dict[str, Any]:
        """Package one explicit scope-bound intelligence cycle.

        The caller must supply:
        - an explicit cycle identity;
        - an already-authorized scope reference;
        - zero or more already-authorized observations;
        - optionally, an already-governed recommendation.

        Empty observation evidence is represented explicitly as
        ``NO_OBSERVATION_EVIDENCE``.

        The facade never turns missing evidence into nominal health, perfect
        success, synthetic confidence, or a fabricated recommendation.
        """
        normalized_cycle_id = _require_identifier(
            cycle_id,
            "cycle_id",
        )

        normalized_scope_ref = _require_identifier(
            scope_ref,
            "scope_ref",
        )

        normalized_observations = _normalize_observations(
            observations,
            scope_ref=normalized_scope_ref,
        )

        normalized_recommendation = _validate_recommendation(
            recommendation,
            scope_ref=normalized_scope_ref,
        )

        observation_graph_keys: list[str] = []

        for observation in normalized_observations:
            graph_key = self._register_scope_entity(
                scope_ref=normalized_scope_ref,
                entity_id=observation.observation_id,
                entity_type="OBSERVATION",
                payload=observation.to_dict(),
            )

            observation_graph_keys.append(
                graph_key
            )

        recommendation_payload: Optional[
            Dict[str, Any]
        ] = None

        recommendation_receipt: Optional[
            Dict[str, Any]
        ] = None

        explanation_payload: Optional[
            Dict[str, Any]
        ] = None

        recommendation_graph_key: Optional[
            str
        ] = None

        if normalized_recommendation is not None:
            recommendation_payload = (
                normalized_recommendation.to_dict()
            )

            recommendation_receipt = (
                _recommendation_receipt(
                    normalized_recommendation
                )
            )

            explanation_payload = (
                _recommendation_explanation(
                    normalized_recommendation
                )
            )

            recommendation_graph_key = (
                self._register_scope_entity(
                    scope_ref=normalized_scope_ref,
                    entity_id=(
                        normalized_recommendation.recommendation_id
                    ),
                    entity_type="RECOMMENDATION",
                    payload=recommendation_payload,
                )
            )

        evidence_status = (
            _OBSERVATION_EVIDENCE_PRESENT
            if normalized_observations
            else _NO_OBSERVATION_EVIDENCE
        )

        recommendation_status = (
            _GOVERNED_RECOMMENDATION_PRESENT
            if normalized_recommendation is not None
            else _NO_RECOMMENDATION
        )

        observation_receipts = [
            _observation_receipt(
                observation
            )
            for observation in normalized_observations
        ]

        receipt_payload: Dict[str, Any] = {
            "cycle_id": normalized_cycle_id,
            "scope_ref": normalized_scope_ref,
            "scope_partition": (
                _scope_partition_key(
                    normalized_scope_ref
                )
            ),
            "platform": self.platform_name,
            "version": VERSION,
            "observations_count": len(
                normalized_observations
            ),
            "observation_receipts": (
                observation_receipts
            ),
            "observation_graph_keys": (
                observation_graph_keys
            ),
            "evidence_status": evidence_status,
            "recommendation_status": (
                recommendation_status
            ),
            "recommendation_receipt": (
                recommendation_receipt
            ),
            "recommendation_graph_key": (
                recommendation_graph_key
            ),
            "authority_posture": (
                _ADVISORY_POSTURE
            ),
            "approval_granted": False,
            "execution_authority_granted": False,
            "financial_execution_authority": (
                _FINANCIAL_EXECUTION_AUTHORITY
            ),
        }

        receipt_checksum = _canonical_sha256(
            receipt_payload
        )

        return {
            **receipt_payload,
            "recommendation": (
                recommendation_payload
            ),
            "explanation": (
                explanation_payload
            ),
            "receipt_checksum": (
                receipt_checksum
            ),
        }

    def inspect_platform_state(
        self,
        *,
        scope_ref: str,
    ) -> Dict[str, Any]:
        """Return an integrity-bound scope-local facade state projection.

        ``INITIALIZED`` describes the Python facade object only.

        It is not:
        - a production-health assertion;
        - evidence of external-service availability;
        - evidence quality;
        - tenant authorization;
        - business approval;
        - execution readiness.
        """
        normalized_scope_ref = _require_identifier(
            scope_ref,
            "scope_ref",
        )

        scope_entities = self._scope_entities.get(
            normalized_scope_ref,
            set(),
        )

        state: Dict[str, Any] = {
            "platform": self.platform_name,
            "version": VERSION,
            "scope_ref": normalized_scope_ref,
            "scope_partition": (
                _scope_partition_key(
                    normalized_scope_ref
                )
            ),
            "lifecycle_state": "INITIALIZED",
            "scope_local_knowledge_nodes": len(
                scope_entities
            ),
            "authority_posture": (
                _ADVISORY_POSTURE
            ),
            "approval_granted": False,
            "execution_authority_granted": False,
            "financial_execution_authority": (
                _FINANCIAL_EXECUTION_AUTHORITY
            ),
        }

        return {
            "intelligence_state": state,
            "checksum": _canonical_sha256(
                state
            ),
        }


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: Wilsy Intelligence Dock Facade
# VERSION: 1.0.0
# AUTHORITY BOUNDARY:
#     Scope-bound advisory composition only. No authentication, identity
#     derivation, tenant-membership derivation, approval, business mutation,
#     autonomous execution, or execution authority.
# TENANT POSTURE:
#     Explicit caller-authorized scope_ref. Mixed-scope composition fails closed.
#     Knowledge-graph technical keys are scope-separated.
# FAIL-CLOSED POSTURE:
#     Missing or blank identifiers, invalid entity types, duplicate observation
#     identities, scope mismatch, and malformed composition inputs are rejected.
# FINANCIAL EXECUTION AUTHORITY:
#     Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
