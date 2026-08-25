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

logger = logging.getLogger("WilsyOS.Runtime.Builder")

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
        # Safely extract execution_id to prevent runtime crashes during logging
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

class ContextBuilder:
    """
    Factory orchestrator for constructing and validating the Wilsy OS ExecutionContext.
    Ensures all dependencies are structurally sound before runtime execution.
    """
    
    @staticmethod
    def build(metadata: Any, sentinel: Any, knowledge_graph: Any, repository: Any) -> 'ExecutionContext':
        """
        Assembles the immutable ExecutionContext and enforces validation bedrock.
        """
        context = ExecutionContext(
            metadata=metadata,
            sentinel=sentinel,
            knowledge_graph=knowledge_graph,
            repository=repository
        )
        
        if not ExecutionContext.validate(context):
            logger.error("ContextBuilder aborted: Failed to assemble a valid ExecutionContext.")
            raise ValueError("Wilsy OS Runtime Error: ContextBuilder received invalid foundational dependencies.")
            
        return context
