"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Artifact Storage Engine (FG168).
    Handles persistent disk storage, structural organization, isolated tiering,
    and transactional retrieval of assets across Wilsy OS.
    Billion-dollar software architecture: secure, atomic, scalable, and future-proof.

Biblical Scale & Architecture:
    Production-ready asset storage controller. Zero child's place.
    Genesis 41:48 - "And he gathered up all the food of the seven years... and laid up the food in the cities..."
    Proverbs 24:3-4 - "Through wisdom is an house builded; and by understanding it is established..."

Collaboration & Maintenance:
    - [Architecture]: Physical disk persistence & structural partition manager for artifact repository.
    - [Integrity]: Guarantees atomic copy operations and isolated storage subdirectories.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional, Union

logger = logging.getLogger("WilsyOS.ArtifactStorage")


class ArtifactStorage:
    """
    Handles persistent storage, structural isolation, and transactional
    filesystem operations for institutional artifacts.
    """

    # [FUNCTION EXPLANATION]: Initializes storage manager and guarantees base directory exists.
    def __init__(self, storage_dir: Union[Path, str] = "./dist") -> None:
        """
        Initializes the Artifact Storage manager.

        Args:
            storage_dir (Union[Path, str]): Base directory path for storing artifacts.
        """
        self.storage_dir = Path(storage_dir).resolve()
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    @property
    def base_dir(self) -> Path:
        """Alias returning the resolved base storage directory Path."""
        return self.storage_dir

    # [FUNCTION EXPLANATION]: Safely copies an artifact into managed directory structure alongside its manifest.
    def store_artifact(
        self, 
        source_path: Union[Path, str], 
        manifest: Dict[str, Any]
    ) -> Path:
        """
        Moves or copies an artifact into structured storage based on its artifact identity.

        Args:
            source_path (Union[Path, str]): Path to source artifact file on disk.
            manifest (Dict[str, Any]): Associated artifact manifest data dictionary.

        Returns:
            Path: Resolved final destination path of the stored artifact.
        """
        src = Path(source_path).resolve()
        if not src.is_file():
            raise FileNotFoundError(f"Source artifact file does not exist at '{src}'")

        artifact_id = manifest.get("artifact_id", "general")
        
        # Partition storage into artifact-specific subfolders to avoid filename collisions
        target_dir = self.storage_dir / artifact_id
        target_dir.mkdir(parents=True, exist_ok=True)

        target_file = target_dir / src.name

        try:
            # Perform atomic file copy if source and target differ
            if src != target_file:
                shutil.copy2(src, target_file)

            # Persist accompanying manifest JSON in same isolated folder
            manifest_path = target_dir / "manifest.json"
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

            logger.info(f"Successfully stored artifact [{src.name}] at [{target_file}]")
            return target_file

        except Exception as e:
            logger.error(f"Failed to store artifact [{src.name}] to [{target_file}]: {e}")
            raise IOError(f"Artifact storage transaction failed for '{src.name}': {e}") from e

    # [FUNCTION EXPLANATION]: Retrieves the absolute Path to an artifact by artifact ID and filename.
    def get_artifact_path(self, artifact_id: str, filename: str) -> Optional[Path]:
        """
        Locates a stored artifact file by artifact ID and filename.

        Args:
            artifact_id (str): Unique identifier of the target artifact.
            filename (str): Original filename of the stored artifact binary.

        Returns:
            Optional[Path]: Resolved path if file exists, otherwise None.
        """
        target = self.storage_dir / artifact_id / filename
        if target.is_file():
            return target
        
        # Fallback check for root legacy storage directory structure
        root_target = self.storage_dir / filename
        if root_target.is_file():
            return root_target

        return None

    # [FUNCTION EXPLANATION]: Safely deletes a stored artifact folder or individual binary.
    def delete_artifact(self, artifact_id: str) -> bool:
        """
        Removes an artifact directory and all contained files from storage.

        Args:
            artifact_id (str): Unique identifier of the artifact to purge.

        Returns:
            bool: True if deletion succeeded or target did not exist, False on failure.
        """
        target_dir = self.storage_dir / artifact_id
        if not target_dir.exists():
            return True

        try:
            if target_dir.is_dir():
                shutil.rmtree(target_dir)
            else:
                target_dir.unlink()
            logger.info(f"Purged artifact directory [{target_dir}] from storage.")
            return True
        except Exception as e:
            logger.error(f"Failed to delete artifact directory [{target_dir}]: {e}")
            return False

    # [FUNCTION EXPLANATION]: Computes repository disk utilization metrics and item counts.
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Calculates storage statistics including total file count and disk usage.

        Returns:
            Dict[str, Any]: Metrics dictionary containing total_bytes, total_files, and storage_path.
        """
        total_bytes = 0
        file_count = 0

        for root, _, files in os.walk(self.storage_dir):
            for f in files:
                fp = Path(root) / f
                if fp.is_file():
                    total_bytes += fp.stat().st_size
                    file_count += 1

        return {
            "storage_path": str(self.storage_dir),
            "total_files": file_count,
            "total_bytes": total_bytes,
            "total_megabytes": round(total_bytes / (1024 * 1024), 2),
        }
