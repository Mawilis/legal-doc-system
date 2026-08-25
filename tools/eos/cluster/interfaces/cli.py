"""
===============================================================================
WILSY OS — FG221 CLUSTER ORCHESTRATOR SUBSYSTEM
===============================================================================

File Path:
    tools/eos/cluster/interfaces/cli.py

Epitome:
    Administrative Command Line Interface for Wilsy OS Cluster Orchestration.
    Provides complete terminal-driven operational control over host nodes,
    execution workers, heartbeats, status reporting, and workload scheduling.

Biblical Worth Billions:
    "Let all things be done decently and in order."
    — 1 Corinthians 14:40

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import argparse
import json
import sys
from typing import List, Dict, Any, Optional

from tools.eos.cluster.application.cluster_manager import ClusterManager
from tools.eos.cluster.application.load_balancer import LoadBalancingStrategy
from tools.eos.cluster.infrastructure.cluster_state_store import ClusterStateStore


def build_parser() -> argparse.ArgumentParser:
    """Constructs the command-line argument parser for cluster administrative tools."""
    parser = argparse.ArgumentParser(
        prog="wilsy-cluster",
        description="Wilsy OS FG221 Cluster Orchestrator Administrative Interface"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Command: status
    subparsers.add_parser("status", help="Get real-time cluster health and metrics overview.")

    # Command: list-nodes
    subparsers.add_parser("list-nodes", help="List all registered compute host nodes.")

    # Command: list-workers
    workers_parser = subparsers.add_parser("list-workers", help="List all registered execution workers.")
    workers_parser.add_argument("--status", type=str, help="Filter workers by status (READY, EXECUTING, OFFLINE, etc.)")
    workers_parser.add_argument("--capability", type=str, help="Filter workers supporting a specific capability")

    # Command: register-node
    reg_node_p = subparsers.add_parser("register-node", help="Register a compute host node.")
    reg_node_p.add_argument("--node-id", required=True, help="Unique node identifier")
    reg_node_p.add_argument("--hostname", required=True, help="Node hostname")
    reg_node_p.add_argument("--ip", default="127.0.0.1", help="IP address")
    reg_node_p.add_argument("--cpu", type=int, default=8, help="CPU cores count")
    reg_node_p.add_argument("--memory", type=float, default=16.0, help="RAM in GB")

    # Command: register-worker
    reg_worker_p = subparsers.add_parser("register-worker", help="Register an execution worker.")
    reg_worker_p.add_argument("--worker-id", required=True, help="Unique worker identifier")
    reg_worker_p.add_argument("--node-id", required=True, help="Bound host node identifier")
    reg_worker_p.add_argument("--capabilities", nargs="*", default=[], help="Supported capability tags")
    reg_worker_p.add_argument("--capacity", type=int, default=10, help="Max execution capacity")

    # Command: ping
    ping_p = subparsers.add_parser("ping", help="Send a worker heartbeat ping.")
    ping_p.add_argument("--worker-id", required=True, help="Target worker identifier")
    ping_p.add_argument("--latency", type=float, default=1.5, help="Simulated latency in ms")

    # Command: snapshot-save
    subparsers.add_parser("snapshot-save", help="Persist a state snapshot of the cluster to disk.")

    return parser


def main(args: Optional[List[str]] = None) -> int:
    """
    Main CLI entrypoint function.
    
    Returns:
        int: Exit status code (0 for success, non-zero for error).
    """
    parser = build_parser()
    parsed_args = parser.parse_args(args)

    manager = ClusterManager(cluster_name="Wilsy-OS-Production-Cluster")
    store = ClusterStateStore()

    # Load existing state if available
    try:
        store.load_snapshot(manager.registry)
    except Exception:
        pass

    try:
        if parsed_args.command == "status":
            status = manager.get_cluster_status()
            print(json.dumps(status, indent=2))

        elif parsed_args.command == "list-nodes":
            nodes = [n.to_dict() for n in manager.registry.list_nodes()]
            print(json.dumps(nodes, indent=2))

        elif parsed_args.command == "list-workers":
            status_filter = parsed_args.status
            capability_filter = parsed_args.capability
            workers = manager.registry.list_workers(capability=capability_filter)
            if status_filter:
                workers = [w for w in workers if w.status.value.upper() == status_filter.upper()]
            print(json.dumps([w.to_dict() for w in workers], indent=2))

        elif parsed_args.command == "register-node":
            node = manager.register_node(
                node_id=parsed_args.node_id,
                hostname=parsed_args.hostname,
                ip_address=parsed_args.ip,
                cpu_cores=parsed_args.cpu,
                memory_gb=parsed_args.memory
            )
            store.save_snapshot(manager.registry)
            print(f"[SUCCESS] Compute host node '{node.node_id}' registered successfully.")

        elif parsed_args.command == "register-worker":
            caps = set(parsed_args.capabilities)
            worker = manager.register_worker(
                worker_id=parsed_args.worker_id,
                node_id=parsed_args.node_id,
                capabilities=caps,
                max_capacity=parsed_args.capacity
            )
            store.save_snapshot(manager.registry)
            print(f"[SUCCESS] Execution worker '{worker.worker_id}' registered and set to READY.")

        elif parsed_args.command == "ping":
            ok = manager.heartbeat(worker_id=parsed_args.worker_id, latency_ms=parsed_args.latency)
            if ok:
                print(f"[SUCCESS] Heartbeat recorded for worker '{parsed_args.worker_id}'.")
            else:
                print(f"[ERROR] Worker '{parsed_args.worker_id}' not found in registry.", file=sys.stderr)
                return 1

        elif parsed_args.command == "snapshot-save":
            path = store.save_snapshot(manager.registry)
            print(f"[SUCCESS] State snapshot saved to '{path}'.")

        return 0

    except Exception as exc:
        print(f"[CLI_ERROR] {str(exc)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
