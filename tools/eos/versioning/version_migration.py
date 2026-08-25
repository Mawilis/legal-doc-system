"""
===============================================================================
WILSY OS — INSTITUTIONAL VERSIONING ENGINE (FG209)
MODULE: SCHEMA & STATE MIGRATION ORCHESTRATOR
===============================================================================
Epitome:
    Transactional, multi-step migration engine for Schema and System State.
    Executes sequential upgrade paths and provides atomic rollback hooks in case 
    of execution failures.

Biblical Worth Billions:
    "Remember ye not the former things, neither consider the things of old. 
     Behold, I will do a new thing..." — Isaiah 43:18-19

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/versioning/version_migration.py
===============================================================================
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable, Any

from tools.eos.versioning.semantic_version import SemanticVersion
from tools.eos.versioning.version_comparator import VersionComparator

logger = logging.getLogger("wilsy.os.versioning.migration")


class MigrationError(Exception):
    """Raised when a migration step or execution pipeline fails."""
    pass


class BaseMigrationStep(ABC):
    """
    Abstract contract for an individual atomic version migration step.
    """

    def __init__(self, source_version: str, target_version: str) -> None:
        self.source_version = SemanticVersion.parse(source_version)
        self.target_version = SemanticVersion.parse(target_version)

    @abstractmethod
    def up(self, context: Dict[str, Any]) -> None:
        """Executes forward migration transformations."""
        pass

    @abstractmethod
    def down(self, context: Dict[str, Any]) -> None:
        """Executes rollback/reversion transformations."""
        pass


@dataclass
class MigrationResult:
    """Represents outcome of a multi-step migration run."""
    success: bool
    initial_version: SemanticVersion
    final_version: SemanticVersion
    steps_executed: int
    error_message: Optional[str] = None


class VersionMigrationOrchestrator:
    """
    Orchestrates linear execution chains of registered migration steps between 
    arbitrary semantic version boundaries.
    """

    def __init__(self) -> None:
        self._steps: Dict[str, BaseMigrationStep] = {}

    def register_step(self, step: BaseMigrationStep) -> None:
        """Registers a migration step keyed by 'source->target'."""
        key = f"{step.source_version}->{step.target_version}"
        self._steps[key] = step

    def execute_migration(
        self, 
        current_version: str, 
        target_version: str, 
        context: Dict[str, Any]
    ) -> MigrationResult:
        """
        Calculates and executes sequential forward migration steps.
        If any step fails, automatically triggers reverse rollback for completed steps.
        """
        start = SemanticVersion.parse(current_version)
        end = SemanticVersion.parse(target_version)

        if start == end:
            return MigrationResult(success=True, initial_version=start, final_version=end, steps_executed=0)

        if VersionComparator.is_older(start, end):
            raise MigrationError(f"Target version '{end}' is older than starting version '{start}'. Use rollback.")

        executed_steps: List[BaseMigrationStep] = []
        curr = start

        try:
            while curr < end:
                # Find matching step starting at curr
                next_step: Optional[BaseMigrationStep] = None
                for step in self._steps.values():
                    if step.source_version == curr and step.target_version <= end:
                        if next_step is None or step.target_version > next_step.target_version:
                            next_step = step

                if next_step is None:
                    raise MigrationError(f"No valid migration path step found from version '{curr}'.")

                logger.info("Executing migration step: %s -> %s", next_step.source_version, next_step.target_version)
                next_step.up(context)
                executed_steps.append(next_step)
                curr = next_step.target_version

            return MigrationResult(
                success=True,
                initial_version=start,
                final_version=curr,
                steps_executed=len(executed_steps)
            )

        except Exception as err:
            logger.error("Migration failed at stage '%s': %s. Initiating rollback.", curr, str(err))
            # Rollback completed steps in reverse order
            for rollback_step in reversed(executed_steps):
                try:
                    rollback_step.down(context)
                except Exception as rollback_err:
                    logger.critical("Fatal: Rollback step failed: %s", str(rollback_err))

            return MigrationResult(
                success=False,
                initial_version=start,
                final_version=curr,
                steps_executed=len(executed_steps),
                error_message=str(err)
            )
