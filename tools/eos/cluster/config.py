"""
===============================================================================
WILSY OS — FG221 CLUSTER ORCHESTRATOR SUBSYSTEM
===============================================================================

File Path:
    tools/eos/cluster/config.py

Epitome:
    Centralized configuration management for the Wilsy OS Cluster Orchestrator.
    Provides immutable data structures, environment variable defaults, factory
    initializers, and cluster deployment profiles.

Biblical Worth Billions:
    "For which of you, intending to build a tower, sitteth not down first, 
    and counteth the cost, whether he have sufficient to finish it?"
    — Luke 14:28

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from tools.eos.cluster.application.cluster_manager import ClusterManager
from tools.eos.cluster.application.load_balancer import LoadBalancingStrategy
from tools.eos.cluster.infrastructure.cluster_state_store import ClusterStateStore


@dataclass(frozen=True)
class ClusterConfig:
    """
    Immutable cluster configuration settings container.
    
    Attributes:
        cluster_name: Human-readable name for the cluster instance.
        heartbeat_interval_seconds: Polling loop frequency for detecting stale nodes.
        stale_timeout_seconds: Timeout before an unresponsive worker is marked OFFLINE.
        default_load_balancing_strategy: Default strategy for job assignment.
        max_default_worker_capacity: Default concurrency limit per worker.
        state_storage_directory: Disk location for snapshot persistence.
        auto_recovery_enabled: Whether stale workers should automatically trigger failover.
    """
    cluster_name: str = "Wilsy-OS-Production-Cluster"
    heartbeat_interval_seconds: float = 5.0
    stale_timeout_seconds: float = 15.0
    default_strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_LOADED
    max_default_worker_capacity: int = 10
    state_storage_directory: str = "./var/cluster_state"
    auto_recovery_enabled: bool = True

    @classmethod
    def from_env(cls) -> "ClusterConfig":
        """
        Instantiates ClusterConfig reading defaults from system environment variables.
        """
        cluster_name = os.getenv("WILSY_CLUSTER_NAME", "Wilsy-OS-Production-Cluster")
        
        try:
            hb_interval = float(os.getenv("WILSY_CLUSTER_HEARTBEAT_INTERVAL", "5.0"))
        except ValueError:
            hb_interval = 5.0

        try:
            stale_timeout = float(os.getenv("WILSY_CLUSTER_STALE_TIMEOUT", "15.0"))
        except ValueError:
            stale_timeout = 15.0

        strategy_str = os.getenv("WILSY_CLUSTER_DEFAULT_STRATEGY", "LEAST_LOADED").upper()
        strategy_map = {
            "ROUND_ROBIN": LoadBalancingStrategy.ROUND_ROBIN,
            "LEAST_LOADED": LoadBalancingStrategy.LEAST_LOADED,
            "CAPABILITY_MATCH": LoadBalancingStrategy.CAPABILITY_MATCH,
            "WEIGHTED_RANDOM": LoadBalancingStrategy.WEIGHTED_RANDOM,
            "RESOURCE_AWARE": LoadBalancingStrategy.RESOURCE_AWARE,
        }
        strategy = strategy_map.get(strategy_str, LoadBalancingStrategy.LEAST_LOADED)

        storage_dir = os.getenv("WILSY_CLUSTER_STATE_DIR", "./var/cluster_state")
        auto_recovery = os.getenv("WILSY_CLUSTER_AUTO_RECOVERY", "true").lower() in ("true", "1", "yes")

        return cls(
            cluster_name=cluster_name,
            heartbeat_interval_seconds=hb_interval,
            stale_timeout_seconds=stale_timeout,
            default_strategy=strategy,
            state_storage_directory=storage_dir,
            auto_recovery_enabled=auto_recovery
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts configuration attributes to dictionary representation."""
        return {
            "cluster_name": self.cluster_name,
            "heartbeat_interval_seconds": self.heartbeat_interval_seconds,
            "stale_timeout_seconds": self.stale_timeout_seconds,
            "default_strategy": self.default_strategy.value,
            "max_default_worker_capacity": self.max_default_worker_capacity,
            "state_storage_directory": self.state_storage_directory,
            "auto_recovery_enabled": self.auto_recovery_enabled
        }


def create_cluster_from_config(
    config: Optional[ClusterConfig] = None,
    event_bus: Optional[Any] = None,
    artifact_bus: Optional[Any] = None
) -> tuple[ClusterManager, ClusterStateStore]:
    """
    Factory function to initialize a fully-wired ClusterManager and ClusterStateStore
    instance configured according to system specifications.
    
    Args:
        config: Optional ClusterConfig instance. Defaults to ClusterConfig.from_env().
        event_bus: Optional event bus instance for cluster telemetry.
        artifact_bus: Optional storage bus instance for execution outputs.
        
    Returns:
        tuple[ClusterManager, ClusterStateStore]: Initialized manager and persistence store.
    """
    cfg = config or ClusterConfig.from_env()

    manager = ClusterManager(
        cluster_name=cfg.cluster_name,
        event_bus=event_bus,
        artifact_bus=artifact_bus,
        heartbeat_interval_seconds=cfg.heartbeat_interval_seconds,
        stale_timeout_seconds=cfg.stale_timeout_seconds
    )

    store = ClusterStateStore(storage_dir=cfg.state_storage_directory)

    # Attempt automatic state restoration if available
    try:
        store.load_snapshot(manager.registry)
    except Exception:
        pass

    return manager, store
