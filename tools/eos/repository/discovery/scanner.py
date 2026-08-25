"""
===============================================================================
WILSY ENGINEERING KERNEL: DISCOVERY SCANNER
===============================================================================
Epitome:
    RepositoryDiscoveryScanner: High-Fidelity Architectural Explorer.
    Traverses the filesystem and normalizes artifacts for ingestion into the 
    Institutional Knowledge Graph.

Collaboration & Maintenance:
    - [Reliability]: Implements robust recursive traversal with absolute path 
      normalization to prevent resolution errors.
    - [Data Integrity]: Normalizes file artifacts into ingestion-ready records 
      for the central Knowledge Graph.
===============================================================================
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List
from tools.eos.repository.discovery.knowledge_graph import InstitutionalKnowledgeGraph

# Initialize institutional logger
logger = logging.getLogger("wilsy.eos.repository.discovery.scanner")

@dataclass
class DiscoveryRecord:
    """
    [Internal]: Lightweight container for ingestion into the Knowledge Graph.
    """
    node_id: str
    node_type: str
    path: str
    owner: str
    docs: str

class RepositoryDiscoveryScanner:
    """
    Industrial-grade Discovery Scanner.
    """

    def __init__(self, graph: InstitutionalKnowledgeGraph) -> None:
        self._graph = graph

    def scan(self, root_path: str, target_extensions: List[str] = [".py", ".js"]) -> None:
        """
        [Creation Event]: Scans directory and performs batch ingestion.
        """
        logger.info(f"Initiating discovery scan at: {root_path}")
        
        records: List[DiscoveryRecord] = []
        root = Path(root_path).resolve()
        
        for entry in root.rglob("*"):
            if entry.is_file() and entry.suffix in target_extensions:
                try:
                    # Robust relative path calculation
                    relative_path = entry.resolve().relative_to(root)
                    node_id = str(relative_path)
                except ValueError:
                    # Fallback for edge cases
                    node_id = entry.name

                # Normalization
                record = DiscoveryRecord(
                    node_id=node_id,
                    node_type="MODULE",
                    path=str(entry),
                    owner="WILSY_SYSTEM_CORE",
                    docs="verified"
                )
                records.append(record)
        
        # Batch ingestion via Graph API
        self._graph.ingest_records(source_engine="SCANNER", records=tuple(records))
        logger.info(f"Discovery scan complete. Ingested {len(records)} artifacts.")
