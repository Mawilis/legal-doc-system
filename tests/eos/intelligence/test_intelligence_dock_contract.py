# -*- coding: utf-8 -*-
"""TITLE: WILSY OS — INTELLIGENCE DOCK V1 CONTRACT CERTIFICATE.

TEST VERSION: v1.0.0-WILSY-INTELLIGENCE-DOCK-CONTRACT-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME:
    Non-skipping, deterministic certification of the sovereign Wilsy Intelligence
    Dock v1 domain and facade contract. The suite proves explicit evidence inputs,
    fail-closed scope composition, deterministic integrity receipts, advisory-only
    authority posture, and the Kennel EOS financial-execution boundary.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/eos/intelligence/test_intelligence_dock_contract.py
PRIMARY ARTIFACTS UNDER TEST:
    tools/eos/intelligence/domain/observation.py
    tools/eos/intelligence/intelligence_facade.py
COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy OS Core Engineering
CERTIFICATION / UPDATE DATE: 2026-08-31
CONTRACT:
    - sovereign domain and facade versions are exactly 1.0.0;
    - observation identity, scope, telemetry, and timestamps are caller supplied;
    - timestamps are timezone-aware and normalized to UTC;
    - evidence cannot exist without observation or external-source provenance;
    - hypotheses, recommendations, and decisions require explicit confidence basis;
    - confidence values are bounded to the closed interval [0.0, 1.0];
    - domain records are immutable and carry deterministic SHA-256 integrity anchors;
    - empty observation history remains explicit NO_OBSERVATION_EVIDENCE;
    - the facade never manufactures recommendations from missing evidence;
    - mixed-scope observations and recommendations fail closed;
    - duplicate observation identities fail closed;
    - graph registration is scope-separated;
    - receipts and scope-local state projections are deterministic;
    - recommendations and explanations remain advisory only;
    - approval and execution authority are never granted by the facade;
    - Kennel EOS remains the exclusive financial execution authority;
    - no conditional skips, dynamic fixture adaptation, or synthetic success paths
      are permitted in this certificate.
TENANT BOUNDARY:
    ``scope_ref`` is caller-authorized metadata. These tests prove separation and
    rejection of mixed scope; they do not establish tenant identity or authority.
AUTHORITY BOUNDARY:
    Intelligence Dock observations, evidence, hypotheses, recommendations,
    explanations, decisions, graph entries, and receipts are descriptive/advisory.
    This certificate grants no business mutation or autonomous execution authority.
FINANCIAL AUTHORITY BOUNDARY:
    Kennel EOS remains the exclusive financial execution authority.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest
from typing import Any, cast

from tools.eos.intelligence.domain.observation import (
    VERSION as DOMAIN_VERSION,
    Evidence,
    ExplainableDecision,
    Hypothesis,
    Observation,
    Recommendation,
)
from tools.eos.intelligence.intelligence_facade import (
    VERSION as FACADE_VERSION,
    WilsyIntelligencePlatform,
)


TEST_VERSION = "v1.0.0-WILSY-INTELLIGENCE-DOCK-CONTRACT-CERT"

_SCOPE_A = "TENANT-A:WORKSPACE-001"
_SCOPE_B = "TENANT-B:WORKSPACE-001"
_TIMESTAMP = "2026-08-31T12:34:56+02:00"
_NORMALIZED_TIMESTAMP = "2026-08-31T10:34:56+00:00"
_SHA256_PATTERN = r"^sha256:[0-9a-f]{64}$"


class TestIntelligenceDockContract(unittest.TestCase):
    """Certify the sovereign Intelligence Dock v1 truth and authority boundary."""

    @staticmethod
    def _observation(
        *,
        observation_id: str = "OBS-CERT-001",
        scope_ref: str = _SCOPE_A,
        raw_value: float = 42.5,
    ) -> Observation:
        return Observation(
            observation_id=observation_id,
            scope_ref=scope_ref,
            source_subsystem="CERTIFIED_TELEMETRY_SOURCE",
            metric_key="QUEUE_DEPTH",
            raw_value=raw_value,
            timestamp=_TIMESTAMP,
        )

    @staticmethod
    def _recommendation(
        *,
        recommendation_id: str = "REC-CERT-001",
        scope_ref: str = _SCOPE_A,
        confidence_score: float = 0.72,
    ) -> Recommendation:
        return Recommendation(
            recommendation_id=recommendation_id,
            scope_ref=scope_ref,
            action_title="Investigate observed queue growth",
            target_subsystem="WORKFLOW_ORCHESTRATOR",
            rationale="Explicit observation evidence indicates sustained queue growth.",
            confidence_score=confidence_score,
            confidence_basis="Bounded analysis of referenced observation evidence.",
            risk_level="MEDIUM",
            evidence_chain=("EVD-CERT-001",),
            created_at=_TIMESTAMP,
        )

    def test_versions_are_exact_sovereign_v1_contracts(self) -> None:
        """Domain and facade semantic versions must remain aligned at 1.0.0."""
        self.assertEqual(DOMAIN_VERSION, "1.0.0")
        self.assertEqual(FACADE_VERSION, "1.0.0")

    def test_observation_requires_explicit_inputs_and_normalizes_timestamp(self) -> None:
        """Observation must not synthesize identity, scope, telemetry, or time."""
        observation = self._observation()

        self.assertEqual(observation.observation_id, "OBS-CERT-001")
        self.assertEqual(observation.scope_ref, _SCOPE_A)
        self.assertEqual(observation.raw_value, 42.5)
        self.assertEqual(observation.timestamp, _NORMALIZED_TIMESTAMP)
        self.assertRegex(observation.checksum, _SHA256_PATTERN)

        observation_constructor = cast(Any, Observation)
        with self.assertRaises(TypeError):
            observation_constructor()

    def test_observation_checksum_is_deterministic_and_entity_is_immutable(self) -> None:
        """Equal explicit evidence must replay to one checksum and remain immutable."""
        first = self._observation()
        second = self._observation()

        self.assertEqual(first.checksum, second.checksum)

        with self.assertRaises(FrozenInstanceError):
            setattr(first, "raw_value", 99.0)

    def test_observation_rejects_nonfinite_telemetry_and_naive_timestamp(self) -> None:
        """Malformed telemetry and timestamps must fail closed."""
        with self.assertRaisesRegex(
            ValueError,
            r"^raw_value must not be NaN or infinite$",
        ):
            Observation(
                observation_id="OBS-NAN-001",
                scope_ref=_SCOPE_A,
                source_subsystem="CERTIFIED_TELEMETRY_SOURCE",
                metric_key="QUEUE_DEPTH",
                raw_value=float("nan"),
                timestamp=_TIMESTAMP,
            )

        with self.assertRaisesRegex(
            ValueError,
            r"^timestamp must include timezone information$",
        ):
            Observation(
                observation_id="OBS-TIME-001",
                scope_ref=_SCOPE_A,
                source_subsystem="CERTIFIED_TELEMETRY_SOURCE",
                metric_key="QUEUE_DEPTH",
                raw_value=1.0,
                timestamp="2026-08-31T12:34:56",
            )

    def test_evidence_requires_real_reference_material(self) -> None:
        """Evidence with no observation or external source reference is forbidden."""
        with self.assertRaisesRegex(
            ValueError,
            r"^evidence requires at least one observation or source reference$",
        ):
            Evidence(
                evidence_id="EVD-EMPTY-001",
                scope_ref=_SCOPE_A,
                source_type="TELEMETRY",
                summary="No provenance is available.",
                observations=(),
                source_refs=(),
                created_at=_TIMESTAMP,
            )

        evidence = Evidence(
            evidence_id="EVD-CERT-001",
            scope_ref=_SCOPE_A,
            source_type="TELEMETRY",
            summary="Queue-depth observation retained as supporting evidence.",
            observations=("OBS-CERT-001",),
            source_refs=("telemetry://queue-depth/OBS-CERT-001",),
            created_at=_TIMESTAMP,
        )

        self.assertEqual(evidence.observations, ("OBS-CERT-001",))
        self.assertEqual(
            evidence.source_refs,
            ("telemetry://queue-depth/OBS-CERT-001",),
        )
        self.assertRegex(evidence.checksum, _SHA256_PATTERN)

    def test_hypothesis_requires_bounded_confidence_and_basis(self) -> None:
        """Analytical confidence must be explicit, bounded, and evidence-linked."""
        hypothesis = Hypothesis(
            hypothesis_id="HYP-CERT-001",
            scope_ref=_SCOPE_A,
            statement="Queue growth may indicate constrained workflow throughput.",
            evidence_ids=("EVD-CERT-001",),
            confidence_score=0.61,
            confidence_basis="Observed queue growth across the supplied evidence window.",
            state="SUPPORTED",
            created_at=_TIMESTAMP,
        )

        self.assertEqual(hypothesis.confidence_score, 0.61)
        self.assertEqual(hypothesis.state, "SUPPORTED")
        self.assertRegex(hypothesis.checksum, _SHA256_PATTERN)

        with self.assertRaisesRegex(
            ValueError,
            r"^confidence_score must be a finite number between 0\.0 and 1\.0$",
        ):
            Hypothesis(
                hypothesis_id="HYP-BAD-001",
                scope_ref=_SCOPE_A,
                statement="Invalid confidence must fail.",
                evidence_ids=("EVD-CERT-001",),
                confidence_score=1.01,
                confidence_basis="Explicit but invalid score.",
                state="OPEN",
                created_at=_TIMESTAMP,
            )

    def test_recommendation_requires_bounded_confidence_and_remains_immutable(self) -> None:
        """Recommendation confidence is analytical metadata, never authority."""
        recommendation = self._recommendation()

        self.assertEqual(recommendation.confidence_score, 0.72)
        self.assertEqual(
            recommendation.confidence_basis,
            "Bounded analysis of referenced observation evidence.",
        )
        self.assertRegex(recommendation.checksum, _SHA256_PATTERN)

        with self.assertRaises(FrozenInstanceError):
            setattr(recommendation, "confidence_score", 1.0)

        with self.assertRaisesRegex(
            ValueError,
            r"^confidence_score must be a finite number between 0\.0 and 1\.0$",
        ):
            self._recommendation(confidence_score=1.01)

    def test_explainable_decision_records_disposition_without_execution_authority(self) -> None:
        """APPROVED is a governed record disposition, not an execution grant."""
        decision = ExplainableDecision(
            decision_id="DEC-CERT-001",
            scope_ref=_SCOPE_A,
            title="Review queue-capacity recommendation",
            rationale="Governance review accepted the advisory recommendation record.",
            evidence_ids=("EVD-CERT-001",),
            recommendation_ids=("REC-CERT-001",),
            confidence_score=0.70,
            confidence_basis="Governance review of supplied evidence and recommendation.",
            disposition="APPROVED",
            created_at=_TIMESTAMP,
        )

        projection = decision.to_dict()

        self.assertEqual(projection["disposition"], "APPROVED")
        self.assertNotIn("execution_authority_granted", projection)
        self.assertNotIn("financial_execution_authority", projection)
        self.assertRegex(decision.traceability_checksum, _SHA256_PATTERN)

    def test_zero_evidence_cycle_is_explicit_and_never_manufactures_recommendation(self) -> None:
        """Empty evidence must remain empty and advisory."""
        platform = WilsyIntelligencePlatform()

        result = platform.run_intelligence_cycle(
            cycle_id="CYCLE-ZERO-001",
            scope_ref=_SCOPE_A,
            observations=(),
        )

        self.assertEqual(result["evidence_status"], "NO_OBSERVATION_EVIDENCE")
        self.assertEqual(result["observations_count"], 0)
        self.assertEqual(result["observation_receipts"], [])
        self.assertEqual(result["observation_graph_keys"], [])
        self.assertEqual(result["recommendation_status"], "NO_RECOMMENDATION")
        self.assertIsNone(result["recommendation"])
        self.assertIsNone(result["explanation"])
        self.assertFalse(result["approval_granted"])
        self.assertFalse(result["execution_authority_granted"])
        self.assertEqual(
            result["financial_execution_authority"],
            "KENNEL_EOS_EXCLUSIVE",
        )
        self.assertRegex(result["receipt_checksum"], _SHA256_PATTERN)

    def test_same_scope_observation_and_recommendation_produce_advisory_receipt(self) -> None:
        """Explicit same-scope inputs may compose, but cannot become authority."""
        platform = WilsyIntelligencePlatform()
        observation = self._observation()
        recommendation = self._recommendation()

        result = platform.run_intelligence_cycle(
            cycle_id="CYCLE-GOVERNED-001",
            scope_ref=_SCOPE_A,
            observations=(observation,),
            recommendation=recommendation,
        )

        self.assertEqual(
            result["evidence_status"],
            "OBSERVATION_EVIDENCE_PRESENT",
        )
        self.assertEqual(
            result["recommendation_status"],
            "GOVERNED_RECOMMENDATION_PRESENT",
        )
        self.assertEqual(result["observations_count"], 1)
        self.assertEqual(
            result["observation_receipts"][0]["checksum"],
            observation.checksum,
        )
        self.assertEqual(
            result["recommendation_receipt"]["checksum"],
            recommendation.checksum,
        )
        self.assertEqual(
            result["explanation"]["authority_posture"],
            "ADVISORY_ONLY",
        )
        self.assertFalse(result["explanation"]["approval_granted"])
        self.assertFalse(result["explanation"]["execution_authority_granted"])
        self.assertEqual(
            result["explanation"]["financial_execution_authority"],
            "KENNEL_EOS_EXCLUSIVE",
        )

    def test_cross_scope_observation_fails_closed(self) -> None:
        """An observation from another scope cannot enter the authorized cycle."""
        platform = WilsyIntelligencePlatform()

        with self.assertRaisesRegex(
            ValueError,
            r"^observation scope_ref does not match the authorized intelligence-cycle scope$",
        ):
            platform.run_intelligence_cycle(
                cycle_id="CYCLE-CROSS-OBS-001",
                scope_ref=_SCOPE_A,
                observations=(self._observation(scope_ref=_SCOPE_B),),
            )

    def test_cross_scope_recommendation_fails_closed(self) -> None:
        """A recommendation from another scope cannot enter the cycle."""
        platform = WilsyIntelligencePlatform()

        with self.assertRaisesRegex(
            ValueError,
            r"^recommendation scope_ref does not match the authorized intelligence-cycle scope$",
        ):
            platform.run_intelligence_cycle(
                cycle_id="CYCLE-CROSS-REC-001",
                scope_ref=_SCOPE_A,
                observations=(),
                recommendation=self._recommendation(scope_ref=_SCOPE_B),
            )

    def test_duplicate_observation_identity_fails_closed(self) -> None:
        """Duplicate evidence identity in one cycle must never be silently merged."""
        platform = WilsyIntelligencePlatform()
        observation = self._observation()

        with self.assertRaisesRegex(
            ValueError,
            r"^duplicate observation_id is forbidden: OBS-CERT-001$",
        ):
            platform.run_intelligence_cycle(
                cycle_id="CYCLE-DUP-001",
                scope_ref=_SCOPE_A,
                observations=(observation, observation),
            )

    def test_invalid_entity_types_and_blank_cycle_identity_fail_closed(self) -> None:
        """Malformed composition inputs cannot be adapted into valid evidence."""
        platform = WilsyIntelligencePlatform()

        with self.assertRaisesRegex(
            TypeError,
            r"^observations must contain only Observation entities$",
        ):
            platform.run_intelligence_cycle(
                cycle_id="CYCLE-TYPE-001",
                scope_ref=_SCOPE_A,
                observations=cast(Any, ("not-an-observation",)),
            )

        with self.assertRaisesRegex(
            ValueError,
            r"^cycle_id must be non-blank$",
        ):
            platform.run_intelligence_cycle(
                cycle_id="   ",
                scope_ref=_SCOPE_A,
                observations=(),
            )

    def test_receipt_replay_is_deterministic_for_identical_explicit_inputs(self) -> None:
        """Fresh platform instances must replay the same receipt checksum."""
        observation = self._observation()
        recommendation = self._recommendation()

        first = WilsyIntelligencePlatform().run_intelligence_cycle(
            cycle_id="CYCLE-REPLAY-001",
            scope_ref=_SCOPE_A,
            observations=(observation,),
            recommendation=recommendation,
        )
        second = WilsyIntelligencePlatform().run_intelligence_cycle(
            cycle_id="CYCLE-REPLAY-001",
            scope_ref=_SCOPE_A,
            observations=(observation,),
            recommendation=recommendation,
        )

        self.assertEqual(first["receipt_checksum"], second["receipt_checksum"])
        self.assertEqual(
            first["observation_graph_keys"],
            second["observation_graph_keys"],
        )
        self.assertEqual(
            first["recommendation_graph_key"],
            second["recommendation_graph_key"],
        )

    def test_scope_partitioning_prevents_cross_scope_graph_key_collision(self) -> None:
        """The same entity ID in different scopes must receive different graph keys."""
        platform = WilsyIntelligencePlatform()

        scope_a_result = platform.run_intelligence_cycle(
            cycle_id="CYCLE-SCOPE-A-001",
            scope_ref=_SCOPE_A,
            observations=(
                self._observation(
                    observation_id="OBS-SHARED-001",
                    scope_ref=_SCOPE_A,
                ),
            ),
        )
        scope_b_result = platform.run_intelligence_cycle(
            cycle_id="CYCLE-SCOPE-B-001",
            scope_ref=_SCOPE_B,
            observations=(
                self._observation(
                    observation_id="OBS-SHARED-001",
                    scope_ref=_SCOPE_B,
                ),
            ),
        )

        scope_a_key = scope_a_result["observation_graph_keys"][0]
        scope_b_key = scope_b_result["observation_graph_keys"][0]

        self.assertNotEqual(scope_a_key, scope_b_key)
        self.assertIn(scope_a_key, platform.knowledge_graph.nodes)
        self.assertIn(scope_b_key, platform.knowledge_graph.nodes)

        scope_a_state = platform.inspect_platform_state(scope_ref=_SCOPE_A)
        scope_b_state = platform.inspect_platform_state(scope_ref=_SCOPE_B)

        self.assertEqual(
            scope_a_state["intelligence_state"]["scope_local_knowledge_nodes"],
            1,
        )
        self.assertEqual(
            scope_b_state["intelligence_state"]["scope_local_knowledge_nodes"],
            1,
        )
        self.assertNotEqual(
            scope_a_state["intelligence_state"]["scope_partition"],
            scope_b_state["intelligence_state"]["scope_partition"],
        )

    def test_platform_state_is_scope_local_advisory_and_deterministic(self) -> None:
        """State projection must not assert health, approval, or execution readiness."""
        platform = WilsyIntelligencePlatform()
        platform.run_intelligence_cycle(
            cycle_id="CYCLE-STATE-001",
            scope_ref=_SCOPE_A,
            observations=(self._observation(),),
        )

        first = platform.inspect_platform_state(scope_ref=_SCOPE_A)
        second = platform.inspect_platform_state(scope_ref=_SCOPE_A)
        state = first["intelligence_state"]

        self.assertEqual(first["checksum"], second["checksum"])
        self.assertEqual(state["lifecycle_state"], "INITIALIZED")
        self.assertEqual(state["scope_local_knowledge_nodes"], 1)
        self.assertEqual(state["authority_posture"], "ADVISORY_ONLY")
        self.assertFalse(state["approval_granted"])
        self.assertFalse(state["execution_authority_granted"])
        self.assertEqual(
            state["financial_execution_authority"],
            "KENNEL_EOS_EXCLUSIVE",
        )
        self.assertNotIn("status", state)
        self.assertNotIn("health", state)
        self.assertNotIn("execution_owner", state)
        self.assertRegex(first["checksum"], _SHA256_PATTERN)


# =============================================================================
# WILSY OS TEST ARTIFACT SEAL
# =============================================================================
# ARTIFACT: Intelligence Dock V1 Contract Certificate
# TEST VERSION: v1.0.0-WILSY-INTELLIGENCE-DOCK-CONTRACT-CERT
# PRIMARY ARTIFACTS:
#     tools/eos/intelligence/domain/observation.py
#     tools/eos/intelligence/intelligence_facade.py
# AUTHORITY BOUNDARY:
#     Evidence-bound, scope-separated advisory intelligence certification only.
# TENANT POSTURE:
#     Explicit caller-authorized scope_ref; mixed-scope composition fails closed.
# FAIL-CLOSED POSTURE:
#     Missing evidence, malformed inputs, duplicate identities, invalid confidence,
#     naive timestamps, non-finite telemetry, and scope mismatch cannot become truth.
# FINANCIAL EXECUTION AUTHORITY:
#     Kennel EOS exclusively.
# END OF WILSY OS TEST ARTIFACT
