"""
===============================================================================
WILSY OS RUNTIME: DOMAIN MODELS
===============================================================================
Epitome:
    The immutable schema definitions for Wilsy EOS runtime components. 
    These models define the structure of the ExecutionContext state.

Biblical Scale & Architecture:
    These are the blueprints for system state. By enforcing immutability 
    via frozen dataclasses, we guarantee that once a session starts, 
    the underlying truth cannot be mutated. 

Collaboration & Maintenance:
    - ExecutionMetadata: Runtime identity and versioning.
    - SentinelSnapshot: Current state of system monitoring.
    - KnowledgeGraphSnapshot: Current state of the graph database.
    - RepositorySession: Current state of the filesystem/repo metrics.
===============================================================================
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime

@dataclass(frozen=True)
class ExecutionMetadata:
    execution_id: str
    started_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"

@dataclass(frozen=True)
class SentinelSnapshot:
    active: bool
    indexed_modules: int
    graph_database: str
    baseline_hash: str

@dataclass(frozen=True)
class KnowledgeGraphSnapshot:
    connected: bool
    database_path: str
    last_ingestion: datetime

@dataclass(frozen=True)
class RepositorySession:
    repository_root: str
    metrics: Dict[str, Any]
    graph: Dict[str, Any]
