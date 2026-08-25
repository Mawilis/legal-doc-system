"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Artifact Bus Framework - Pluggable Artifact Persistence Store (FG150B).
    Responsible solely for low-level artifact storage, retrieval, and existence
    checks across pluggable storage provider backends.

Biblical Scale & Architecture:
    Decoupled storage persistence layer. Abstracts physical media (Filesystem,
    SQLite, S3) behind a unified StorageBackend provider contract.
    Proverbs 24:27 - "Prepare your work outside; get everything ready for yourself in the field."

Collaboration & Maintenance:
    - [Architecture]: Pluggable storage facade enforcing raw Artifact persistence without catalog logic.
    - Consumes: Immutable Artifact instances (FG150A).
    - Produces: Persisted storage objects & retrieval streams.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional

from tools.eos.artifacts.artifact import Artifact


class StorageBackend(ABC):
    """Abstract storage provider contract for underlying artifact media."""

    @abstractmethod
    def save(self, artifact_id: str, data: dict) -> None:
        """Persists serialized artifact dictionary."""
        pass

    @abstractmethod
    def load(self, artifact_id: str) -> Optional[dict]:
        """Retrieves raw artifact dictionary by ID."""
        pass

    @abstractmethod
    def exists(self, artifact_id: str) -> bool:
        """Checks if an artifact exists in storage."""
        pass

    @abstractmethod
    def delete(self, artifact_id: str) -> bool:
        """Removes an artifact from storage."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clears all stored artifacts."""
        pass


class FileSystemStorageBackend(StorageBackend):
    """Default production filesystem backend with JSON serialization."""

    def __init__(self, base_directory: str = "/Users/wilsonkhanyezi/legal-doc-system/data/artifacts") -> None:
        self.base_dir = Path(base_directory)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, artifact_id: str) -> Path:
        return self.base_dir / f"{artifact_id}.json"

    def save(self, artifact_id: str, data: dict) -> None:
        file_path = self._get_path(artifact_id)
        temp_path = file_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_path.replace(file_path)

    def load(self, artifact_id: str) -> Optional[dict]:
        file_path = self._get_path(artifact_id)
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def exists(self, artifact_id: str) -> bool:
        return self._get_path(artifact_id).exists()

    def delete(self, artifact_id: str) -> bool:
        file_path = self._get_path(artifact_id)
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def clear(self) -> None:
        for file in self.base_dir.glob("*.json"):
            try:
                file.unlink()
            except OSError:
                pass


class InMemoryStorageBackend(StorageBackend):
    """In-memory storage provider for fast unit testing and isolated staging."""

    def __init__(self) -> None:
        self._memory: Dict[str, dict] = {}

    def save(self, artifact_id: str, data: dict) -> None:
        self._memory[artifact_id] = data

    def load(self, artifact_id: str) -> Optional[dict]:
        return self._memory.get(artifact_id)

    def exists(self, artifact_id: str) -> bool:
        return artifact_id in self._memory

    def delete(self, artifact_id: str) -> bool:
        if artifact_id in self._memory:
            del self._memory[artifact_id]
            return True
        return False

    def clear(self) -> None:
        self._memory.clear()


class ArtifactStore:
    """
    Primary interface for persisting and retrieving immutable Artifacts.
    Delegates physical operations to a pluggable StorageBackend.
    """

    def __init__(self, backend: Optional[StorageBackend] = None) -> None:
        """
        Initializes ArtifactStore with a chosen backend (defaults to FileSystemStorageBackend).
        """
        self.backend = backend or FileSystemStorageBackend()

    def store(self, artifact: Artifact) -> None:
        """
        Persists an immutable Artifact object.

        Args:
            artifact (Artifact): Immutable artifact instance to store.
        """
        data = {
            "artifact_id": artifact.artifact_id,
            "execution_id": artifact.execution_id,
            "engine_id": artifact.engine_id,
            "artifact_type": artifact.artifact_type,
            "created_at": artifact.created_at,
            "checksum": artifact.checksum,
            "payload": artifact.payload,
            "metadata": artifact.metadata,
            "version": artifact.version,
        }
        self.backend.save(artifact.artifact_id, data)

    def retrieve(self, artifact_id: str) -> Optional[Artifact]:
        """
        Retrieves and reconstructs an immutable Artifact by ID.

        Args:
            artifact_id (str): Unique ID of the artifact to retrieve.

        Returns:
            Optional[Artifact]: Reconstructed Artifact object or None if not found.
        """
        data = self.backend.load(artifact_id)
        if not data:
            return None

        return Artifact(
            artifact_id=data["artifact_id"],
            execution_id=data["execution_id"],
            engine_id=data["engine_id"],
            artifact_type=data["artifact_type"],
            created_at=data["created_at"],
            checksum=data["checksum"],
            payload=data["payload"],
            metadata=data.get("metadata", {}),
            version=data.get("version", "1.0.0"),
        )

    def exists(self, artifact_id: str) -> bool:
        """Checks if an artifact exists in the backend store."""
        return self.backend.exists(artifact_id)

    def delete(self, artifact_id: str) -> bool:
        """Deletes an artifact by ID."""
        return self.backend.delete(artifact_id)

    def clear(self) -> None:
        """Clears all persisted artifacts in the backend store."""
        self.backend.clear()
