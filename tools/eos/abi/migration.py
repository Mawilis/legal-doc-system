"""
===============================================================================
WILSY OS KERNEL ARCHITECTURE - ENTERPRISE ENGINEERING PLATFORM
===============================================================================
PROJECT: Wilsy OS (Billion-Dollar Sovereign Infrastructure)
SUBSYSTEM: Kernel ABI & Core Governance Framework
MILESTONE: FG178.5 - Kernel ABI Freeze
MODULE: migration.py

COLLABORATION & ARCHITECTURAL NOTICE:
Handles version upgrades for persistent artifacts, execution journals,
and engine schemas across Kernel ABI version shifts.
===============================================================================
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable, Optional

logger = logging.getLogger("WilsyOS.ABI.Migration")


@dataclass
class MigrationStep:
    """A single migration transformation rule."""
    source_version: str
    target_version: str
    description: str
    transformer: Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class MigrationPlan:
    """Sequential sequence of steps to migrate payloads to latest ABI version."""
    payload_type: str
    initial_version: str
    target_version: str
    steps: List[MigrationStep] = field(default_factory=list)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = payload.copy()
        logger.info("Executing migration plan for '%s' from v%s to v%s", self.payload_type, self.initial_version, self.target_version)
        for step in self.steps:
            logger.debug("Applying step: %s -> %s (%s)", step.source_version, step.target_version, step.description)
            data = step.transformer(data)
            data["abi_version"] = step.target_version
        return data


class ABIMigrationEngine:
    """
    Registry and execution engine for schema and artifact upgrades across ABI versions.
    """

    def __init__(self) -> None:
        self._transformers: Dict[str, List[MigrationStep]] = {}

    def register_transformer(
        self,
        payload_type: str,
        source_version: str,
        target_version: str,
        description: str,
        transformer: Callable[[Dict[str, Any]], Dict[str, Any]],
    ) -> None:
        step = MigrationStep(
            source_version=source_version,
            target_version=target_version,
            description=description,
            transformer=transformer,
        )
        if payload_type not in self._transformers:
            self._transformers[payload_type] = []
        self._transformers[payload_type].append(step)
        logger.info("Registered migration transformer for '%s': v%s -> v%s", payload_type, source_version, target_version)

    def build_plan(
        self,
        payload_type: str,
        current_version: str,
        target_version: str,
    ) -> Optional[MigrationPlan]:
        if current_version == target_version:
            return MigrationPlan(payload_type=payload_type, initial_version=current_version, target_version=target_version)

        available_steps = self._transformers.get(payload_type, [])
        matching_steps = [
            s for s in available_steps if s.source_version == current_version and s.target_version == target_version
        ]

        if not matching_steps:
            logger.error("No migration path found for '%s' from v%s to v%s", payload_type, current_version, target_version)
            return None

        return MigrationPlan(
            payload_type=payload_type,
            initial_version=current_version,
            target_version=target_version,
            steps=matching_steps,
        )
