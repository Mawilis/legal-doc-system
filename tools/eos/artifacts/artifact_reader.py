"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Artifact Bus Framework - Read-Only Reader Façade (FG150E).
    Provides a secure, read-only access layer combining ArtifactStore and
    ArtifactCatalog for querying execution artifacts and manifests without write permissions.

Biblical Scale & Architecture:
    Production-ready read-only abstraction. Enforces strict separation of concerns:
    zero write capabilities exposed, ensuring audit safety and thread-safe data inspection.
    Psalm 119:105 - "Your word is a lamp to my feet and a light to my path."

Collaboration & Maintenance:
    - [Architecture]: Read-only query facade consumed by reporting engines and external clients.
    - Consumes: ArtifactStore and ArtifactCatalog instances.
    - Produces: Read-only Artifact and ArtifactManifest views.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from typing import Optional, Sequence, Tuple

from tools.eos.artifacts.artifact import Artifact
from tools.eos.artifacts.artifact_catalog import ArtifactCatalog
from tools.eos.artifacts.artifact_manifest import ArtifactManifest
from tools.eos.artifacts.artifact_store import ArtifactStore


class ArtifactReader:
    """
    Read-only façade providing secure, query-optimized access to persisted
    artifacts and manifests via the store and catalog.
    """

    def __init__(self, store: ArtifactStore, catalog: ArtifactCatalog) -> None:
        """
        Initializes the ArtifactReader with an underlying store and catalog.

        Args:
            store (ArtifactStore): Persistence store containing raw artifact files/records.
            catalog (ArtifactCatalog): Indexing catalog providing multi-dimensional queries.
        """
        self._store = store
        self._catalog = catalog

    # [FUNCTION EXPLANATION]: Reads a single artifact by ID from the persistence store.
    def read(self, artifact_id: str) -> Optional[Artifact]:
        """
        Retrieves a single artifact by its unique ID.

        Args:
            artifact_id (str): Unique identifier of the artifact.

        Returns:
            Optional[Artifact]: Reconstructed Artifact object or None if not found.
        """
        return self._store.retrieve(artifact_id)

    # [FUNCTION EXPLANATION]: Reads multiple artifacts in batch by a collection of IDs.
    def read_many(self, artifact_ids: Sequence[str]) -> Tuple[Artifact, ...]:
        """
        Retrieves multiple artifacts by a sequence of IDs.

        Args:
            artifact_ids (Sequence[str]): Collection of artifact identifiers.

        Returns:
            Tuple[Artifact, ...]: Tuple of successfully retrieved Artifact objects.
        """
        artifacts = []
        for aid in artifact_ids:
            art = self._store.retrieve(aid)
            if art is not None:
                artifacts.append(art)
        return tuple(artifacts)

    # [FUNCTION EXPLANATION]: Reads an execution manifest and all its associated artifacts.
    def read_execution(self, execution_id: str) -> Tuple[Artifact, ...]:
        """
        Retrieves all artifacts produced during a specific execution run.

        Args:
            execution_id (str): ID of the execution plan run.

        Returns:
            Tuple[Artifact, ...]: Tuple of artifacts associated with the execution.
        """
        return self._catalog.by_execution(execution_id)

    # [FUNCTION EXPLANATION]: Retrieves the most recent artifact matching optional filters.
    def read_latest(
        self,
        engine_id: Optional[str] = None,
        artifact_type: Optional[str] = None,
        execution_id: Optional[str] = None,
    ) -> Optional[Artifact]:
        """
        Retrieves the single most recent artifact matching optional filters.

        Args:
            engine_id (Optional[str]): Filter by engine ID.
            artifact_type (Optional[str]): Filter by artifact domain type.
            execution_id (Optional[str]): Filter by execution ID.

        Returns:
            Optional[Artifact]: The latest matching Artifact or None.
        """
        return self._catalog.latest(engine_id=engine_id, artifact_type=artifact_type, execution_id=execution_id)

    # [FUNCTION EXPLANATION]: Reconstructs or resolves an execution manifest.
    def read_manifest(self, execution_id: str) -> ArtifactManifest:
        """
        Generates or reconstructs an immutable ArtifactManifest summarizing an execution run.

        Args:
            execution_id (str): ID of the execution plan run.

        Returns:
            ArtifactManifest: Sealed manifest containing all artifact IDs produced during the run.
        """
        artifacts = self._catalog.by_execution(execution_id)
        artifact_ids = [art.artifact_id for art in artifacts]
        return ArtifactManifest.create(execution_id=execution_id, artifact_ids=artifact_ids)
