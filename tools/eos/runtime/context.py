"""
===============================================================================
WILSY OS RUNTIME: EXECUTION CONTEXT
===============================================================================
Epitome:
    The immutable state container for a Wilsy EOS execution session. 
    It holds the single source of truth for the Sentinel, Knowledge Graph, 
    and Repository metadata.

Biblical Scale & Architecture:
    Designed for absolute consistency. The ExecutionContext is instantiated 
    once and passed to all engines, preventing race conditions or 
    dependency drift. No child's play; this is the runtime bedrock.
    
    INTEGRATION (FG145B): Fused with the Sentinel Cache Provider to ensure 
    sub-millisecond repository reads with filesystem fallback as the absolute 
    source of truth.

Collaboration & Maintenance:
    - Provides read-only access to system state.
    - Ensures all engines operate on a synchronized baseline.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from dataclasses import dataclass
from typing import Any, Optional
import logging

logger = logging.getLogger("WilsyOS.Runtime.ExecutionContext")

@dataclass(frozen=True)
class ExecutionContext:
    """
    The immutable container for the current Wilsy EOS runtime state.
    """
    metadata: Any  # ExecutionMetadata
    sentinel: Any  # SentinelSnapshot
    knowledge_graph: Any  # KnowledgeGraphSnapshot
    repository: Any  # RepositorySession

    def __repr__(self) -> str:
        # Safely extract execution_id whether metadata is a dict or an object
        if isinstance(self.metadata, dict):
            exec_id = self.metadata.get("execution_id", "UNKNOWN")
        else:
            exec_id = getattr(self.metadata, "execution_id", "UNKNOWN")
        return f"<ExecutionContext: {exec_id}>"

    @classmethod
    def validate(cls, context: Optional['ExecutionContext']) -> bool:
        """
        Verify the integrity of the context before passing it to engines.
        """
        if context is None:
            logger.error("ExecutionContext validation failed: Context instance is None.")
            return False

        is_valid = all([
            context.metadata is not None,
            context.sentinel is not None,
            context.knowledge_graph is not None,
            context.repository is not None
        ])

        if not is_valid:
            logger.warning("ExecutionContext integrity check failed: One or more foundational components are missing.")
        
        return is_valid
