"""
===============================================================================
WILSY OS: BOOTSTRAP ORCHESTRATOR
===============================================================================
Epitome:
    Legacy root ignition sequence. Forwards execution to the FG145F Kernel CLI.
===============================================================================
"""

import sys
from datetime import datetime, timezone
from tools.eos.runtime.domain.models import (
    ExecutionMetadata, SentinelSnapshot, KnowledgeGraphSnapshot, RepositorySession
)
from tools.eos.runtime.context import ExecutionContext
from tools.eos.kernel.engine import EngineeringKernel

def bootstrap():
    print("[SYSTEM] Wilsy OS Boot Sequence Initiated...")
    
    # 1. Initialize Runtime State with strict typing (fixing Pylance errors)
    metadata = ExecutionMetadata(execution_id="WOS-INIT-001", version="1.0.0")
    sentinel = SentinelSnapshot(active=True, indexed_modules=301, graph_database="v1", baseline_hash="0xDEADBEEF")
    graph = KnowledgeGraphSnapshot(connected=True, database_path="/.wilsy_graph.json", last_ingestion=datetime.now(timezone.utc))
    repo = RepositorySession(repository_root="/", metrics={}, graph={})

    # 2. Assemble Context (Direct frozen instantiation, bypassing old ContextBuilder)
    context = ExecutionContext(
        metadata={"execution_id": metadata.execution_id, "version": metadata.version},
        repository=repo,
        sentinel=sentinel,
        knowledge_graph=graph
    )
    
    # 3. Awaken the Kernel
    kernel = EngineeringKernel(context)
    session = kernel.initialize_session()
    
    print(f"[SYSTEM] Kernel Awakened: {session}")
    print("[SYSTEM] Wilsy OS Bridge Active. Neural pathway ready.")
    print("\n[NOTE] For full FG145F execution, run: python -m tools.eos.kernel\n")

if __name__ == "__main__":
    try:
        bootstrap()
    except Exception as e:
        print(f"[CRITICAL FAILURE] Boot sequence aborted: {e}")
        sys.exit(1)
