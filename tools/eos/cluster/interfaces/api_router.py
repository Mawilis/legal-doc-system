"""
===============================================================================
WILSY OS — FG221 CLUSTER ORCHESTRATOR SUBSYSTEM
===============================================================================

File Path:
    tools/eos/cluster/interfaces/api_router.py

Epitome:
    REST API Controller and Handler for the Cluster Orchestrator Subsystem.
    Provides structured endpoint handlers and request/response DTO wrappers
    for remote cluster administration, heartbeat ingestion, job scheduling,
    and topology snapshot persistence.

Biblical Worth Billions:
    "Every draft of every court, every line of every code, must bear the 
    imprint of divinity and perfection."
    — Exodus 25:40

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union

from tools.eos.cluster.application.cluster_manager import ClusterManager
from tools.eos.cluster.application.load_balancer import LoadBalancingStrategy
from tools.eos.cluster.infrastructure.cluster_state_store import ClusterStateStore

logger = logging.getLogger("wilsy_os.cluster.api_router")


@dataclass
class APIResponse:
    """
    Standardized REST API JSON response wrapper for Wilsy OS Cluster Services.
    
    Attributes:
        success: Indicates whether the requested operation succeeded.
        status_code: HTTP-compatible status code (e.g. 200, 201, 400, 404, 500).
        message: Human-readable status or diagnostic message.
        data: Payload returned by the endpoint handler.
        timestamp: UTC timestamp when the response was constructed.
    """
    success: bool
    status_code: int
    message: str
    data: Optional[Any] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the response object into a standard dictionary."""
        return {
            "success": self.success,
            "status_code": self.status_code,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp
        }


class ClusterAPIRouter:
    """
    HTTP Controller and Dispatch Router for Cluster Management operations.
    """

    def __init__(
        self,
        cluster_manager: ClusterManager,
        state_store: Optional[ClusterStateStore] = None
    ) -> None:
        self.manager = cluster_manager
        self.state_store = state_store or ClusterStateStore()

    def get_cluster_status(self) -> Dict[str, Any]:
        """
        Endpoint: GET /api/v1/cluster/status
        
        Returns full real-time telemetry, node count, worker count, and scheduling stats.
        """
        try:
            status = self.manager.get_cluster_status()
            return APIResponse(
                success=True,
                status_code=200,
                message="Cluster telemetry retrieved successfully.",
                data=status
            ).to_dict()
        except Exception as exc:
            logger.error(f"[API_ERROR] Failed to fetch cluster status: {exc}")
            return APIResponse(
                success=False,
                status_code=500,
                message=f"Internal server error: {str(exc)}"
            ).to_dict()

    def register_node(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Endpoint: POST /api/v1/cluster/nodes
        
        Payload:
            node_id: str (required)
            hostname: str (required)
            ip_address: str (optional, default '127.0.0.1')
            cpu_cores: int (optional, default 8)
            memory_gb: float (optional, default 16.0)
            tags: dict (optional)
        """
        if not isinstance(payload, dict) or "node_id" not in payload or "hostname" not in payload:
            return APIResponse(
                success=False,
                status_code=400,
                message="Missing required parameters 'node_id' or 'hostname'."
            ).to_dict()

        try:
            node = self.manager.register_node(
                node_id=str(payload["node_id"]),
                hostname=str(payload["hostname"]),
                ip_address=str(payload.get("ip_address", "127.0.0.1")),
                cpu_cores=int(payload.get("cpu_cores", 8)),
                memory_gb=float(payload.get("memory_gb", 16.0)),
                tags=payload.get("tags", {})
            )
            self.state_store.save_snapshot(self.manager.registry)
            return APIResponse(
                success=True,
                status_code=201,
                message=f"Compute host node '{node.node_id}' registered successfully.",
                data=node.to_dict()
            ).to_dict()
        except Exception as exc:
            logger.error(f"[API_ERROR] Failed to register node: {exc}")
            return APIResponse(
                success=False,
                status_code=500,
                message=f"Failed to register node: {str(exc)}"
            ).to_dict()

    def register_worker(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Endpoint: POST /api/v1/cluster/workers
        
        Payload:
            worker_id: str (required)
            node_id: str (required)
            capabilities: list[str] (optional)
            max_capacity: int (optional, default 10)
        """
        if not isinstance(payload, dict) or "worker_id" not in payload or "node_id" not in payload:
            return APIResponse(
                success=False,
                status_code=400,
                message="Missing required parameters 'worker_id' or 'node_id'."
            ).to_dict()

        try:
            caps = set(payload.get("capabilities", []))
            worker = self.manager.register_worker(
                worker_id=str(payload["worker_id"]),
                node_id=str(payload["node_id"]),
                capabilities=caps,
                max_capacity=int(payload.get("max_capacity", 10))
            )
            self.state_store.save_snapshot(self.manager.registry)
            return APIResponse(
                success=True,
                status_code=201,
                message=f"Execution worker '{worker.worker_id}' registered and transitioned to READY.",
                data=worker.to_dict()
            ).to_dict()
        except Exception as exc:
            logger.error(f"[API_ERROR] Failed to register worker: {exc}")
            return APIResponse(
                success=False,
                status_code=500,
                message=f"Failed to register worker: {str(exc)}"
            ).to_dict()

    def process_heartbeat(self, worker_id: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Endpoint: POST /api/v1/cluster/workers/{worker_id}/heartbeat
        """
        p = payload or {}
        latency_ms = float(p.get("latency_ms", 0.0))

        success = self.manager.heartbeat(worker_id=worker_id, latency_ms=latency_ms)
        if success:
            return APIResponse(
                success=True,
                status_code=200,
                message=f"Heartbeat accepted for worker '{worker_id}'."
            ).to_dict()
        else:
            return APIResponse(
                success=False,
                status_code=404,
                message=f"Worker '{worker_id}' not found in registry."
            ).to_dict()

    def list_nodes(self) -> Dict[str, Any]:
        """
        Endpoint: GET /api/v1/cluster/nodes
        """
        nodes = [n.to_dict() for n in self.manager.registry.list_nodes()]
        return APIResponse(
            success=True,
            status_code=200,
            message=f"Retrieved {len(nodes)} host nodes.",
            data=nodes
        ).to_dict()

    def list_workers(self, capability: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
        """
        Endpoint: GET /api/v1/cluster/workers?capability=...&status=...
        """
        workers = self.manager.registry.list_workers(capability=capability)
        if status:
            workers = [w for w in workers if w.status.value.upper() == status.upper()]

        workers_data = [w.to_dict() for w in workers]
        return APIResponse(
            success=True,
            status_code=200,
            message=f"Retrieved {len(workers_data)} execution workers.",
            data=workers_data
        ).to_dict()

    def save_state_snapshot(self) -> Dict[str, Any]:
        """
        Endpoint: POST /api/v1/cluster/snapshots
        """
        try:
            filepath = self.state_store.save_snapshot(self.manager.registry)
            return APIResponse(
                success=True,
                status_code=200,
                message=f"Cluster state snapshot saved successfully.",
                data={"snapshot_path": filepath}
            ).to_dict()
        except Exception as exc:
            return APIResponse(
                success=False,
                status_code=500,
                message=f"Failed to persist state snapshot: {str(exc)}"
            ).to_dict()
