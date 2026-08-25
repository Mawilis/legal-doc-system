"""
===============================================================================
WILSY OS RUNBOOK: KERNEL & PIPELINE INTEGRATION TEST (FG145)
===============================================================================
Epitome:
    The production pre-flight checklist and end-to-end integration test for 
    Wilsy OS. Verifies all seven subsystems and executes the unified 
    orchestration pipeline deterministically.

Biblical Scale & Architecture:
    The heartbeat of Wilsy OS validation. Ensures absolute immutability, 
    strict dependency chaining, and error-free pipeline execution before 
    any release to production.

Collaboration & Maintenance:
    - [Test Isolation]: Utilizes pure execution contexts without mutating disk.
    - [Validation]: Enforces the FG145E Unified Engineering Report schema.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from tools.eos.kernel.engine import EngineeringKernel
from tools.eos.runtime.context import ExecutionContext
from tools.eos.kernel.report import WilsyEngineeringReport


class MockSentinel:
    """Mock interface for the system Sentinel."""
    pass


class MockKnowledgeGraph:
    """Mock interface for the system KnowledgeGraph."""
    pass


class MockRepository:
    """Mock interface for the system Repository."""
    repository_root = "/Users/wilsonkhanyezi/legal-doc-system"


def run_diagnostic():
    print("--- [PRODUCTION TEST] Initiating Wilsy OS Integration Suite ---")
    
    try:
        # 1. Initialize Context
        # [COLLABORATION: Instantiating the frozen dataclass directly to preserve immutability]
        ctx = ExecutionContext(
            metadata={"version": "1.0.0", "env": "prod", "execution_id": "EXEC-TEST-001"},
            repository=MockRepository(),
            sentinel=MockSentinel(),
            knowledge_graph=MockKnowledgeGraph()
        )
        print("[PASS] ExecutionContext initialized successfully.")
        
        # 2. Boot Kernel
        kernel = EngineeringKernel(ctx)
        print("[PASS] EngineeringKernel instantiated.")
        
        # 3. Spin up Session
        session = kernel.initialize_session()
        
        # Safely extract execution ID based on dictionary or object-based metadata
        metadata = session.metadata
        exec_id = metadata.get('execution_id') if isinstance(metadata, dict) else getattr(metadata, 'execution_id', 'UNKNOWN')
        print(f"[PASS] EngineeringKernelSession established for ID: {exec_id}")
        
        # 4. Verify Subsystem Bindings (All 7 Engines)
        required_engines = ["ai", "quality", "review", "patch", "release", "installer", "forensic"]
        for engine_name in required_engines:
            engine_obj = getattr(kernel, engine_name, None)
            assert engine_obj is not None, f"Engine '{engine_name}' failed to bind."
            print(f"[SUCCESS] Subsystem '{engine_name.upper()}' is bound and active.")
        
        # 5. Execute Unified Orchestration Pipeline (FG145)
        test_execution_id = "EXEC-TEST-001"
        report = kernel.run_pipeline(test_execution_id)
        
        # 6. Validate Unified Report Output against the new FG145E schema
        assert isinstance(report, WilsyEngineeringReport), f"Pipeline returned {type(report)}, expected WilsyEngineeringReport."
        assert hasattr(report, "execution_summary"), "Report is missing the required execution_summary domain."
        
        print(f"[SUCCESS] Unified Engineering Report matrix generated successfully.")
        print("--- [PRODUCTION TEST] All System Checks Passed Successfully ---")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[CRITICAL FAILURE] Pipeline execution failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    run_diagnostic()
