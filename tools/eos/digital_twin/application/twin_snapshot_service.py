"""
===============================================================================
WILSY OS — FG223 DIGITAL TWIN INTELLIGENCE PLATFORM
===============================================================================

File Path:
    tools/eos/digital_twin/application/twin_snapshot_service.py

Epitome:
    Generates cryptographically validated, immutable snapshots of the Digital 
    Twin Knowledge Graph. Publishes snapshot completion notifications to the Event 
    Bus and writes audit records to the Artifact Bus.

Biblical Worth Billions:
    "Write the vision, and make it plain upon tables, that he may run that readeth it."
    — Habakkuk 2:2

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import time
import uuid
import logging
from typing import Dict, Any, List, Optional
from tools.eos.digital_twin.domain.twin_snapshot import TwinSnapshot
from tools.eos.digital_twin.application.twin_engine import TwinEngine

logger = logging.getLogger("WilsyOS.DigitalTwin.SnapshotService")


class TwinSnapshotService:
    """
    Manages snapshot creation, retention, and cryptographic attestation 
    for the Digital Twin Platform.
    """

    def __init__(self, twin_engine: TwinEngine, artifact_bus: Optional[Any] = None):
        """
        Initializes the TwinSnapshotService.

        Args:
            twin_engine (TwinEngine): The target Digital Twin engine instance.
            artifact_bus (Optional[Any]): Artifact Bus instance for snapshot reports.
        """
        if not isinstance(twin_engine, TwinEngine):
            raise TypeError("TwinSnapshotService requires a valid TwinEngine instance.")

        self._twin_engine = twin_engine
        self._artifact_bus = artifact_bus
        self._snapshots: Dict[str, TwinSnapshot] = {}

    def create_snapshot(self, metadata: Optional[Dict[str, Any]] = None) -> TwinSnapshot:
        """
        Captures an immutable point-in-time snapshot of the current state graph.

        Args:
            metadata (Optional[Dict[str, Any]]): Contextual metadata tags.

        Returns:
            TwinSnapshot: Cryptographically signed snapshot instance.
        """
        try:
            snapshot_id = f"TWIN-SNAP-{uuid.uuid4().hex[:12].upper()}"
            entities, relationships = self._twin_engine.state.export_serialized_state()

            snapshot = TwinSnapshot(
                snapshot_id=snapshot_id,
                entities=entities,
                relationships=relationships,
                metadata=metadata or {}
            )

            self._snapshots[snapshot_id] = snapshot

            # Dispatch notification via TwinEngine event emitter
            self._twin_engine._emit_event("TwinSnapshotCompleted", {
                "snapshot_id": snapshot_id,
                "entities_count": snapshot.entities_count,
                "relationships_count": snapshot.relationships_count,
                "snapshot_hash": snapshot.snapshot_hash,
                "merkle_root": snapshot.merkle_root
            })

            # Record artifact if Artifact Bus is connected
            if self._artifact_bus and hasattr(self._artifact_bus, "publish_artifact"):
                try:
                    self._artifact_bus.publish_artifact("DIGITAL_TWIN_SNAPSHOT", snapshot.to_dict())
                except Exception as ab_err:
                    logger.warning(f"Failed to publish snapshot artifact [{snapshot_id}]: {str(ab_err)}")

            logger.info(f"Successfully generated TwinSnapshot [{snapshot_id}] with Merkle Root: {snapshot.merkle_root}")
            return snapshot

        except Exception as e:
            logger.error(f"Failed to create Digital Twin snapshot: {str(e)}")
            raise RuntimeError(f"TwinSnapshotService creation failure: {str(e)}")

    def get_snapshot(self, snapshot_id: str) -> Optional[TwinSnapshot]:
        return self._snapshots.get(snapshot_id)

    def list_snapshots(self) -> List[Dict[str, Any]]:
        return [snap.to_dict() for snap in self._snapshots.values()]
