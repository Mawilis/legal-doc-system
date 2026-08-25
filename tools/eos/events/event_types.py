"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Institutional Event Bus - Canonical Event Type Definitions (FG161).
    Establishes core event classification constants across all Wilsy OS engines,
    enabling decoupled, event-driven inter-service communication.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready institutional standards. Every event has a distinct purpose and domain.
    1 Corinthians 14:40 - "But all things should be done decently and in order."

Collaboration & Maintenance:
    - [Architecture]: Comprehensive event catalog defining institutional dispatch categories.
    - [Compliance]: Strict string enumeration ensuring type safety across the Event Bus.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from enum import Enum


class EventType(str, Enum):
    """
    Canonical institutional event classifications across Wilsy OS engines.
    Engines communicate exclusively via these published event types through the Event Bus.
    """

    # Execution lifecycle events
    EXECUTION_STARTED = "eos.execution.started"
    EXECUTION_COMPLETED = "eos.execution.completed"
    EXECUTION_FAILED = "eos.execution.failed"

    # Task execution telemetry
    TASK_STARTED = "eos.task.started"
    TASK_COMPLETED = "eos.task.completed"
    TASK_FAILED = "eos.task.failed"

    # Repository & Knowledge state events
    REPOSITORY_SCANNED = "eos.repository.scanned"
    KNOWLEDGE_GRAPH_UPDATED = "eos.knowledge_graph.updated"

    # Artifact & Decision events
    ARTIFACT_STORED = "eos.artifact.stored"
    ARTIFACT_PUBLISHED = "eos.artifact.published"
    DECISION_PRODUCED = "eos.decision.produced"

    # Quality & Review governance events
    QUALITY_PASSED = "eos.quality.passed"
    QUALITY_FAILED = "eos.quality.failed"
    REVIEW_PASSED = "eos.review.passed"
    REVIEW_FAILED = "eos.review.failed"

    # Release & Sentinel operational events
    RELEASE_PUBLISHED = "eos.release.published"
    SENTINEL_ALERT = "eos.sentinel.alert"
    SYSTEM_ALERT = "eos.system.alert"
