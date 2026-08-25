"""
===============================================================================
WILSY OS — FG221 CLUSTER ORCHESTRATOR SUBSYSTEM
===============================================================================

File Path:
    tools/eos/cluster/infrastructure/cluster_state_store.py

Epitome:
    Thread-safe persistence adapter for taking point-in-time state snapshots
    of the cluster topology, node assignments, worker configurations, and health
    telemetry. Supports state recovery during cold boots and cluster restart sequences.

Biblical Worth Billions:
    "Write the vision, and make it plain upon tables, that he may run that
    readeth it."
    — Habakkuk 2:2

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import json
import logging
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List

from tools.eos.cluster.domain.cluster_node import ClusterNode
from tools.eos.cluster.domain.worker import Worker
from tools.eos.cluster.application.worker_registry import WorkerRegistry

logger = logging.getLogger("wilsy_os.cluster.state_store")


class ClusterStateStoreError(RuntimeError):
    """Raised when cluster state serialization or persistence operations fail."""
    pass


class ClusterStateStore:
    """
    Persistence adapter for exporting and restoring cluster topological state.
    """

    def __init__(self, storage_dir: Optional[str] = None) -> None:
        self.storage_dir = Path(storage_dir or "./var/cluster_state")
        self._lock = threading.RLock()
        self._ensure_storage_directory()

    def _ensure_storage_directory(self) -> None:
        """Guarantees the persistence directory exists on disk."""
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            logger.error(f"[STATE_STORE_INIT_FAILED] Could not create state directory '{self.storage_dir}': {exc}")

    def save_snapshot(
        self, 
        registry: WorkerRegistry, 
        snapshot_name: str = "cluster_snapshot_latest.json"
    ) -> str:
        """
        Serializes and writes the complete registry state to disk as JSON.
        
        Args:
            registry: Active WorkerRegistry instance.
            snapshot_name: Target filename for state snapshot.
            
        Returns:
            str: Full path to saved snapshot file.
        """
        with self._lock:
            nodes = registry.list_nodes()
            nodes_data = [node.to_dict() for node in nodes]
            
            # Unbound workers
            all_workers = registry.list_workers()
            unbound_workers = [w.to_dict() for w in all_workers if not w.node_id]

            snapshot_data = {
                "version": "1.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "node_count": len(nodes_data),
                "total_worker_count": len(all_workers),
                "nodes": nodes_data,
                "unbound_workers": unbound_workers,
                "cluster_stats": registry.get_cluster_stats()
            }

            filepath = self.storage_dir / snapshot_name
            try:
                temp_file = filepath.with_suffix(".tmp")
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(snapshot_data, f, indent=2)
                
                # Atomic swap
                temp_file.replace(filepath)
                logger.info(f"[SNAPSHOT_SAVED] Cluster state persisted to '{filepath}'.")
                return str(filepath)

            except Exception as exc:
                raise ClusterStateStoreError(f"[SAVE_SNAPSHOT_FAILED] {str(exc)}") from exc

    def load_snapshot(
        self, 
        registry: WorkerRegistry, 
        snapshot_name: str = "cluster_snapshot_latest.json"
    ) -> bool:
        """
        Loads a snapshot from disk and restores nodes and workers into the registry.
        
        Args:
            registry: Target WorkerRegistry to populate.
            snapshot_name: Source snapshot filename.
            
        Returns:
            bool: True if snapshot was successfully restored.
        """
        filepath = self.storage_dir / snapshot_name
        if not filepath.exists():
            logger.warning(f"[SNAPSHOT_NOT_FOUND] Snapshot file '{filepath}' does not exist.")
            return False

        with self._lock:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                nodes_raw = data.get("nodes", [])
                for node_data in nodes_raw:
                    node = ClusterNode.from_dict(node_data)
                    registry.register_node(node)

                unbound_raw = data.get("unbound_workers", [])
                for worker_data in unbound_raw:
                    worker = Worker.from_dict(worker_data)
                    registry.register_worker(worker)

                logger.info(f"[SNAPSHOT_RESTORED] Restored {len(nodes_raw)} nodes from '{filepath}'.")
                return True

            except Exception as exc:
                raise ClusterStateStoreError(f"[RESTORE_SNAPSHOT_FAILED] {str(exc)}") from exc

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """
        Lists available saved snapshot files with metadata.
        """
        with self._lock:
            snapshots = []
            if not self.storage_dir.exists():
                return snapshots

            for file in self.storage_dir.glob("*.json"):
                try:
                    stat = file.stat()
                    snapshots.append({
                        "filename": file.name,
                        "path": str(file),
                        "size_bytes": stat.st_size,
                        "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()
                    })
                except Exception:
                    pass
            return sorted(snapshots, key=lambda x: x["modified_at"], reverse=True)
