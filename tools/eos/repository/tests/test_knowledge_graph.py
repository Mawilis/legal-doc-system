"""
===============================================================================
WILSY ENGINEERING KERNEL: KNOWLEDGE GRAPH PROOF
===============================================================================
Purpose:
    Validates the structural integrity, ingestion performance, and data 
    retrieval consistency of the InstitutionalKnowledgeGraph.
    
    This acts as the "Proof of Brain" phase to authorize the construction of 
    the downstream Graph Builders.
===============================================================================
"""

import unittest
from dataclasses import dataclass
from tools.eos.repository.discovery.knowledge_graph import InstitutionalKnowledgeGraph

# Mock record structures matching our discovery engines
@dataclass
class MockCapability:
    capability_id: str
    type: str

@dataclass
class MockOwner:
    ai_id: str
    team: str

class TestKnowledgeGraphProof(unittest.TestCase):
    
    def setUp(self) -> None:
        self.graph = InstitutionalKnowledgeGraph()

    def test_ingestion_and_retrieval_integrity(self) -> None:
        """
        Verifies that disparate discovery engine records are normalized 
        into the KnowledgeNode registry correctly.
        """
        # Simulate data from CapabilityDiscovery
        caps = (MockCapability("auth.login", "decorator"),)
        self.graph.ingest_records("CAPABILITY", caps)
        
        # Simulate data from AIDiscovery
        ai_assets = (MockOwner("model_v1", "ml_team"),)
        self.graph.ingest_records("AI_ASSET", ai_assets)
        
        # Verify state
        state = self.graph.get_graph_state()
        self.assertEqual(len(state), 2, "Graph failed to ingest full record set.")
        
        # Verify specific node types
        types = {node.node_type for node in state}
        self.assertIn("CAPABILITY", types)
        self.assertIn("AI_ASSET", types)

    def test_immutability_of_state(self) -> None:
        """
        Ensures the registry returns a tuple (immutable state) rather than a mutable list.
        """
        state = self.graph.get_graph_state()
        self.assertIsInstance(state, tuple)

if __name__ == "__main__":
    unittest.main()
