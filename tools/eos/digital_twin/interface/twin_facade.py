"""
===============================================================================
WILSY OS — FG223 DIGITAL TWIN INTELLIGENCE PLATFORM
===============================================================================

File Path:
    tools/eos/digital_twin/interface/twin_facade.py

Epitome:
    Unified master facade and primary operational entrypoint for the Digital Twin
    Platform. Encapsulates TwinEngine, TwinRegistry, TwinSnapshotService, TwinQueryService,
    TwinSimulationService, and TwinPredictionService alongside all observational adapters.

Biblical Worth Billions:
    "Through wisdom is an house builded; and by understanding it is established:
    and by knowledge shall the chambers be filled with all precious and pleasant riches."
    — Proverbs 24:3-4

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import logging
from typing import Dict, Any, Optional

from tools.eos.digital_twin.domain.twin_state_graph import TwinStateGraph
from tools.eos.digital_twin.application.twin_engine import TwinEngine
from tools.eos.digital_twin.application.twin_registry import TwinRegistry
from tools.eos.digital_twin.application.twin_snapshot_service import TwinSnapshotService
from tools.eos.digital_twin.application.twin_query_service import TwinQueryService
from tools.eos.digital_twin.application.twin_simulation_service import TwinSimulationService
from tools.eos.digital_twin.application.twin_prediction_service import TwinPredictionService

from tools.eos.digital_twin.infrastructure.repository_adapter import RepositoryAdapter
from tools.eos.digital_twin.infrastructure.runtime_adapter import RuntimeAdapter
from tools.eos.digital_twin.infrastructure.marketplace_adapter import MarketplaceAdapter
from tools.eos.digital_twin.infrastructure.cluster_adapter import ClusterAdapter
from tools.eos.digital_twin.infrastructure.reliability_adapter import ReliabilityAdapter
from tools.eos.digital_twin.infrastructure.governance_adapter import GovernanceAdapter
from tools.eos.digital_twin.infrastructure.documentation_adapter import DocumentationAdapter
from tools.eos.digital_twin.infrastructure.compatibility_adapter import CompatibilityAdapter
from tools.eos.digital_twin.infrastructure.versioning_adapter import VersioningAdapter

logger = logging.getLogger("WilsyOS.DigitalTwin.Facade")


class DigitalTwinFacade:
    """
    Unified entrypoint for the FG223 Digital Twin Intelligence Platform.
    Provides single-call access to state synchronization, topological queries,
    immutable snapshotting, scenario simulation, and predictive risk forecasting.
    """

    def __init__(
        self,
        event_bus: Optional[Any] = None,
        artifact_bus: Optional[Any] = None
    ):
        """
        Initializes the Digital Twin Platform with all underlying engines,
        services, and observational adapters.

        Args:
            event_bus (Optional[Any]): Central event bus instance.
            artifact_bus (Optional[Any]): Central artifact storage bus instance.
        """
        self._graph = TwinStateGraph()
        self._engine = TwinEngine(state_graph=self._graph, event_bus=event_bus)
        self._registry = TwinRegistry(twin_engine=self._engine)
        self._snapshot_service = TwinSnapshotService(twin_engine=self._engine, artifact_bus=artifact_bus)
        self._query_service = TwinQueryService(twin_engine=self._engine)
        self._simulation_service = TwinSimulationService(twin_engine=self._engine)
        self._prediction_service = TwinPredictionService(twin_engine=self._engine)

        self._auto_register_default_adapters()
        logger.info("FG223 Digital Twin Intelligence Platform initialized successfully.")

    def _auto_register_default_adapters(self) -> None:
        """Registers all 9 standard observational subsystem adapters."""
        self._registry.register_adapter("repository", RepositoryAdapter())
        self._registry.register_adapter("runtime", RuntimeAdapter())
        self._registry.register_adapter("marketplace", MarketplaceAdapter())
        self._registry.register_adapter("cluster", ClusterAdapter())
        self._registry.register_adapter("reliability", ReliabilityAdapter())
        self._registry.register_adapter("governance", GovernanceAdapter())
        self._registry.register_adapter("documentation", DocumentationAdapter())
        self._registry.register_adapter("compatibility", CompatibilityAdapter())
        self._registry.register_adapter("versioning", VersioningAdapter())

    @property
    def engine(self) -> TwinEngine:
        return self._engine

    @property
    def registry(self) -> TwinRegistry:
        return self._registry

    @property
    def snapshots(self) -> TwinSnapshotService:
        return self._snapshot_service

    @property
    def query(self) -> TwinQueryService:
        return self._query_service

    @property
    def simulation(self) -> TwinSimulationService:
        return self._simulation_service

    @property
    def prediction(self) -> TwinPredictionService:
        return self._prediction_service

    def synchronize_platform(self) -> Dict[str, Any]:
        """
        Executes a complete observational synchronization pass across all subsystem adapters.

        Returns:
            Dict[str, Any]: Synchronization summary telemetry.
        """
        return self._registry.synchronize_all()

    def capture_snapshot(self, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generates an immutable, cryptographically verified state snapshot.

        Args:
            metadata (Optional[Dict[str, Any]]): Contextual key-value tags.

        Returns:
            Dict[str, Any]: Serialized snapshot metadata dictionary.
        """
        snapshot = self._snapshot_service.create_snapshot(metadata=metadata)
        return snapshot.to_dict()

    def run_health_and_predictive_analysis(self) -> Dict[str, Any]:
        """
        Computes predictive risk indicators and architectural drift metrics.

        Returns:
            Dict[str, Any]: Risk and drift telemetry dictionary.
        """
        return self._prediction_service.generate_predictions()

    def get_system_telemetry(self) -> Dict[str, Any]:
        """
        Retrieves full real-time telemetry of the digital twin topology state.

        Returns:
            Dict[str, Any]: Complete topology state report.
        """
        entities, relationships = self._graph.export_serialized_state()
        return {
            "entity_count": self._graph.entity_count,
            "relationship_count": self._graph.relationship_count,
            "drift_count": self._graph.drift_count,
            "registered_adapters": self._registry.registered_adapters,
            "last_sync_timestamp": self._registry.last_sync_timestamp,
            "entities": entities,
            "relationships": relationships
        }
