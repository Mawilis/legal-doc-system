"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Artifact Registry Engine (FG168).
    Central cataloging, ingestion, cryptographic verification, and lifecycle
    orchestration for institutional assets across Wilsy OS.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready artifact orchestrator. Zero child's place.
    1 Chronicles 28:12 - "And the pattern of all that he had by the spirit, of the courts of the house of the Lord..."
    Proverbs 18:10 - "The name of the Lord is a strong tower: the righteous runneth into it, and is safe."

Collaboration & Maintenance:
    - [Architecture]: Central catalog and retrieval coordinator for all registered artifacts.
    - [Integrity]: Enforces cryptographic validation during ingestion and audit cycles.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from .checksum import ArtifactChecksum
    from .manifest import ArtifactManifest
    from .storage import ArtifactStorage
except ImportError:
    from checksum import ArtifactChecksum
    from manifest import ArtifactManifest
    from storage import ArtifactStorage

logger = logging.getLogger("WilsyOS.ArtifactRegistry")


class ArtifactRegistry:
    """
    Orchestrates the ingestion, cataloging, cryptographic sealing,
    and query retrieval of institutional artifacts.
    """

    # [FUNCTION EXPLANATION]: Initializes registry with backing storage engine and catalog tracking.
    def __init__(
        self, 
        storage_dir: Union[Path, str] = "./dist",
        catalog_path: Optional[Union[Path, str]] = None,
    ) -> None:
        """
        Initializes the Artifact Registry instance.

        Args:
            storage_dir (Union[Path, str]): Directory root for artifact storage repository.
            catalog_path (Optional[Union[Path, str]]): Path to local catalog index JSON file.
        """
        self.storage_dir = Path(storage_dir).resolve()
        self.storage = ArtifactStorage(self.storage_dir)
        self.catalog_file = Path(catalog_path).resolve() if catalog_path else self.storage_dir / "registry_catalog.json"
        self._index: Dict[str, Dict[str, Any]] = {}
        self._load_catalog()

    # [FUNCTION EXPLANATION]: Ingests, computes checksums, creates manifest, and stores artifact safely.
    def register_artifact(
        self,
        file_path: Union[Path, str],
        metadata: Optional[Dict[str, Any]] = None,
        producer: str = "SYSTEM_PROCESSOR",
        execution_id: str = "exec-unknown",
        content_type: str = "application/octet-stream",
    ) -> Dict[str, Any]:
        """
        Registers a new artifact into the system registry with checksum sealing and manifest creation.

        Args:
            file_path (Union[Path, str]): Path to the artifact file on disk.
            metadata (Optional[Dict[str, Any]]): User-defined metadata or domain tags.
            producer (str): Identifier of component generating the artifact.
            execution_id (str): Pipeline execution identifier context.
            content_type (str): Asset MIME content type.

        Returns:
            Dict[str, Any]: Standardized registration result report dictionary.
        """
        target = Path(file_path).resolve()
        if not target.is_file():
            logger.error(f"Artifact registration failed: Source file missing at [{target}]")
            return {
                "status": "FAILED",
                "reason": f"Artifact file not found at {target}",
                "artifact_id": None,
                "checksum": None,
                "stored_path": None,
            }

        try:
            checksum = ArtifactChecksum.compute_file_checksum(target)
            manifest = ArtifactManifest.create_artifact_manifest(
                file_path=target,
                checksum=checksum,
                metadata=metadata or {},
                producer=producer,
                execution_id=execution_id,
                content_type=content_type,
            )

            stored_path = self.storage.store_artifact(target, manifest)
            artifact_id = manifest["artifact_id"]

            # Update in-memory catalog and persist
            self._index[artifact_id] = {
                "manifest": manifest,
                "stored_path": str(stored_path),
                "checksum": checksum,
                "registered_at": manifest["created_at"],
            }
            self._save_catalog()

            logger.info(f"Artifact [{artifact_id}] successfully registered and cryptographically sealed.")

            return {
                "status": "REGISTERED",
                "artifact_id": artifact_id,
                "artifact_name": target.name,
                "checksum": checksum,
                "stored_path": str(stored_path),
                "manifest": manifest,
                "comments": "Artifact successfully registered and cryptographically sealed.",
            }

        except Exception as e:
            logger.exception(f"Unexpected error registering artifact [{target.name}]: {e}")
            return {
                "status": "FAILED",
                "reason": str(e),
                "artifact_id": None,
                "checksum": None,
                "stored_path": None,
            }

    # [FUNCTION EXPLANATION]: Retrieves registered manifest data by unique artifact ID.
    def get_manifest(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves manifest dictionary for a registered artifact ID."""
        entry = self._index.get(artifact_id)
        if entry:
            return entry.get("manifest")
        return None

    # [FUNCTION EXPLANATION]: Verifies physical file integrity against recorded checksum in the registry.
    def verify_artifact_integrity(self, artifact_id: str) -> Dict[str, Any]:
        """
        Verifies cryptographic integrity of a registered artifact on disk.

        Args:
            artifact_id (str): Artifact ID to verify.

        Returns:
            Dict[str, Any]: Audit verification report.
        """
        entry = self._index.get(artifact_id)
        if not entry:
            return {"artifact_id": artifact_id, "valid": False, "reason": "Artifact ID not registered"}

        stored_path = Path(entry["stored_path"])
        expected_checksum = entry["checksum"]

        if not stored_path.is_file():
            return {"artifact_id": artifact_id, "valid": False, "reason": "Stored binary file missing on disk"}

        is_valid = ArtifactChecksum.verify_checksum(stored_path, expected_checksum)
        return {
            "artifact_id": artifact_id,
            "valid": is_valid,
            "stored_path": str(stored_path),
            "expected_checksum": expected_checksum,
            "reason": "Checksum verified match" if is_valid else "Checksum mismatch detected",
        }

    # [FUNCTION EXPLANATION]: Lists all registered artifacts, optionally filtered by producer or execution ID.
    def list_artifacts(
        self, 
        producer_filter: Optional[str] = None,
        execution_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lists registered artifacts matching optional filtering parameters."""
        results = []
        for artifact_id, record in self._index.items():
            manifest = record.get("manifest", {})
            if producer_filter and manifest.get("producer") != producer_filter:
                continue
            if execution_filter and manifest.get("execution_id") != execution_filter:
                continue
            results.append(record)
        return results

    # [FUNCTION EXPLANATION]: Internal helper to load registry catalog index from disk.
    def _load_catalog(self) -> None:
        """Loads index catalog JSON if present."""
        if self.catalog_file.is_file():
            try:
                content = self.catalog_file.read_text(encoding="utf-8")
                self._index = json.loads(content)
            except Exception as e:
                logger.warning(f"Could not parse registry catalog at [{self.catalog_file}]: {e}")
                self._index = {}
        else:
            self._index = {}

    # [FUNCTION EXPLANATION]: Internal helper to persist current registry catalog index to disk.
    def _save_catalog(self) -> None:
        """Persists in-memory index catalog to disk JSON."""
        try:
            self.catalog_file.parent.mkdir(parents=True, exist_ok=True)
            self.catalog_file.write_text(json.dumps(self._index, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to persist registry catalog to [{self.catalog_file}]: {e}")
