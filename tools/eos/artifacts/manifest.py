"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Artifact Manifest Model & Generator (FG168).
    Structures declarative metadata, provenance tracking, cryptographic checksums,
    producer attribution, and execution context for stored institutional assets.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready artifact manifest engine. Zero child's place.
    Habakkuk 2:2 - "Write the vision, and make it plain upon tables, that he may run that readeth it."
    Colossians 3:23 - "And whatsoever ye do, do it heartily, as to the Lord, and not unto men."

Collaboration & Maintenance:
    - [Architecture]: Declarative manifest metadata engine for artifact auditability.
    - [Provenance]: Immutable tracking of Producer, Execution ID, Checksum, and Timestamp.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import datetime
import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Union

logger = logging.getLogger("WilsyOS.ArtifactManifest")


@dataclass
class ArtifactManifestData:
    """
    Structured dataclass representation of an artifact manifest.
    Holds full addressability, provenance, and metadata fields required by FG168.
    """
    artifact_id: str
    checksum: str
    producer: str
    execution_id: str
    artifact_name: str
    size_bytes: int
    created_at: str
    timestamp: float
    content_type: str = "application/octet-stream"
    schema_version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

    # [FUNCTION EXPLANATION]: Serializes the manifest dataclass into a python dictionary.
    def to_dict(self) -> Dict[str, Any]:
        """Converts manifest dataclass instance to a standard dictionary."""
        return asdict(self)

    # [FUNCTION EXPLANATION]: Serializes the manifest into a formatted JSON string.
    def to_json(self, indent: int = 2) -> str:
        """Converts manifest data to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    # [FUNCTION EXPLANATION]: Persists the manifest JSON directly to a specified file path.
    def save_to_file(self, target_path: Union[Path, str]) -> Path:
        """Writes manifest JSON to disk."""
        path = Path(target_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")
        logger.debug(f"Manifest written for artifact [{self.artifact_id}] at [{path}]")
        return path


class ArtifactManifest:
    """
    Factory, validator, and loader utility for structured artifact manifests.
    """

    # [FUNCTION EXPLANATION]: Generates a standardized manifest dictionary or data object for an artifact.
    @staticmethod
    def create_artifact_manifest(
        file_path: Union[Path, str],
        checksum: str,
        metadata: Optional[Dict[str, Any]] = None,
        producer: str = "SYSTEM_PROCESSOR",
        execution_id: str = "exec-unknown",
        artifact_id: Optional[str] = None,
        content_type: str = "application/octet-stream",
    ) -> Dict[str, Any]:
        """
        Generates a structured manifest dictionary for an artifact.

        Args:
            file_path (Union[Path, str]): Resolved path to the artifact on disk.
            checksum (str): Cryptographic SHA-256 digest string.
            metadata (Optional[Dict[str, Any]]): User or domain metadata tags.
            producer (str): Identifier of task/service that generated the asset.
            execution_id (str): Unique execution run identifier.
            artifact_id (Optional[str]): Explicit artifact ID (auto-derived if None).
            content_type (str): MIME type of the artifact.

        Returns:
            Dict[str, Any]: Standardized artifact manifest dictionary.
        """
        target = Path(file_path).resolve()
        now = datetime.datetime.now(datetime.timezone.utc)
        resolved_id = artifact_id or f"art-{checksum[:12]}"
        size_bytes = target.stat().st_size if target.exists() and target.is_file() else 0

        manifest_obj = ArtifactManifestData(
            artifact_id=resolved_id,
            checksum=checksum,
            producer=producer,
            execution_id=execution_id,
            artifact_name=target.name,
            size_bytes=size_bytes,
            created_at=now.isoformat(),
            timestamp=now.timestamp(),
            content_type=content_type,
            schema_version="1.0.0",
            metadata=metadata or {},
        )

        return manifest_obj.to_dict()

    # [FUNCTION EXPLANATION]: Creates an ArtifactManifestData object instance directly.
    @classmethod
    def build_data(
        cls,
        file_path: Union[Path, str],
        checksum: str,
        producer: str,
        execution_id: str,
        artifact_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        content_type: str = "application/octet-stream",
    ) -> ArtifactManifestData:
        """Constructs an ArtifactManifestData object."""
        manifest_dict = cls.create_artifact_manifest(
            file_path=file_path,
            checksum=checksum,
            metadata=metadata,
            producer=producer,
            execution_id=execution_id,
            artifact_id=artifact_id,
            content_type=content_type,
        )
        return ArtifactManifestData(**manifest_dict)

    # [FUNCTION EXPLANATION]: Deserializes an ArtifactManifestData instance from a dictionary.
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> ArtifactManifestData:
        """Constructs an ArtifactManifestData instance from a dictionary."""
        return ArtifactManifestData(**data)

    # [FUNCTION EXPLANATION]: Loads and parses an artifact manifest JSON file from disk.
    @staticmethod
    def load_from_file(manifest_path: Union[Path, str]) -> ArtifactManifestData:
        """
        Reads and parses an artifact manifest JSON file.

        Args:
            manifest_path (Union[Path, str]): Path to .json manifest file.

        Returns:
            ArtifactManifestData: Deserialized manifest instance.

        Raises:
            FileNotFoundError: If the manifest file path does not exist.
        """
        target = Path(manifest_path).resolve()
        if not target.is_file():
            raise FileNotFoundError(f"Manifest file not found at '{target}'")

        content = json.loads(target.read_text(encoding="utf-8"))
        return ArtifactManifestData(**content)
