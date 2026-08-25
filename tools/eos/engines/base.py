"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Engine Integration Framework - Abstract Base Engine Contract.
    Defines the standard execution interface for all Wilsy OS kernel engines,
    mandating that every engine produces an immutable Artifact (FG150) rather than raw dictionaries.

Biblical Scale & Architecture:
    Production-ready abstract base class enforcing strict type safety and architectural discipline.
    Colossians 3:23 - "Whatever you do, work heartily, as for the Lord and not for men."
    Wilsy OS is billion-dollar software: future-proof, robust, and zero loose ends.

Collaboration & Maintenance:
    - [Architecture]: Universal engine contract for Repository, AI, Quality, Review, and Release engines.
    - Consumes: Execution context dictionaries or task parameters.
    - Produces: Immutable Artifact instances with SHA-256 integrity checksums.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from tools.eos.artifacts.artifact import Artifact


class BaseEngine(ABC):
    """
    Abstract Base Class for all Wilsy OS execution engines.
    Guarantees that engine execution outputs are strictly encapsulated within immutable Artifacts.
    """

    def __init__(self, engine_id: str, artifact_type: str) -> None:
        """
        Initializes the base engine with its unique identifier and target artifact classification.

        Args:
            engine_id (str): Unique registered identifier for the engine (e.g., 'core.repository').
            artifact_type (str): Domain classification of artifacts produced by this engine.
        """
        self.engine_id = engine_id
        self.artifact_type = artifact_type

    @abstractmethod
    def execute(self, execution_id: str, context: Dict[str, Any]) -> Artifact:
        """
        Executes the engine's core workload and returns an immutable Artifact.

        Args:
            execution_id (str): ID of the active execution plan run.
            context (Dict[str, Any]): Execution context parameters and input payloads.

        Returns:
            Artifact: Immutable, cryptographically hashed artifact representing execution output.
        """
        pass

    # [FUNCTION EXPLANATION]: Standardized helper to package raw output payloads into immutable Artifacts.
    def create_artifact(
        self,
        execution_id: str,
        payload: Any,
        metadata: Optional[Dict[str, Any]] = None,
        version: str = "1.0.0",
    ) -> Artifact:
        """
        Helper method to construct an Artifact bound to this engine's ID and artifact type.

        Args:
            execution_id (str): ID of the parent execution run.
            payload (Any): Core data structure produced by the engine execution.
            metadata (Optional[Dict[str, Any]]): Optional telemetry or contextual metadata.
            version (str): Contract version string.

        Returns:
            Artifact: Fully formed, frozen Artifact instance.
        """
        meta = metadata or {}
        meta.setdefault("engine_id", self.engine_id)
        meta.setdefault("status", "SUCCESS")

        return Artifact.create(
            execution_id=execution_id,
            engine_id=self.engine_id,
            artifact_type=self.artifact_type,
            payload=payload,
            metadata=meta,
            version=version,
        )
