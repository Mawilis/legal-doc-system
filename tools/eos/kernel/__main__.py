"""
===============================================================================
WILSY OS: KERNEL CLI (FG145F)
===============================================================================
Epitome:
    The singular execution entry point for the Wilsy EOS pipeline.
    Triggered via: python -m tools.eos.kernel

Biblical Scale & Architecture:
    One command orchestrates the entire billion-dollar lifecycle. 
    It enforces strict sequential execution from Runtime Initialization 
    to the generation of the Unified Engineering Report, exiting cleanly.
===============================================================================
"""

import sys
import time
from pathlib import Path

# Add project root to path to ensure module resolution
sys.path.append(str(Path.cwd()))

from tools.eos.runtime.context import ExecutionContext
from tools.eos.kernel.engine import EngineeringKernel

class BootSentinel: pass
class BootGraph: pass
class BootRepo:
    repository_root = str(Path.cwd())

def main():
    print("\n================================================================")
    print("WILSY OS KERNEL EXECUTION INITIATED (FG145F)")
    print("================================================================\n")
    
    try:
        exec_id = f"EXEC-CLI-{int(time.time())}"
        
        print(f"[1/11] Initialize Runtime State...")
        # Direct instantiation of the frozen context (bypassing legacy builders)
        ctx = ExecutionContext(
            metadata={"version": "1.0.0", "env": "prod", "execution_id": exec_id},
            repository=BootRepo(),
            sentinel=BootSentinel(),
            knowledge_graph=BootGraph()
        )
        
        print(f"[2/11] Validate Runtime...")
        kernel = EngineeringKernel(ctx)
        kernel.initialize_session()
        
        print(f"[3/11] to [9/11] Executing Unified Subsystems...")
        # The Kernel runs: Repository Intelligence -> Engineering Assurance -> 
        # Quality -> Review -> Patch -> Release -> Installer
        report = kernel.run_pipeline(exec_id)
        
        print(f"[10/11] Generate Unified Report...")
        report_dir = Path.cwd() / "reports"
        report_dir.mkdir(exist_ok=True)
        report_path = report_dir / f"{exec_id}_unified_report.json"
        
        report.serialize_to_disk(report_path)
        
        print(f"\n[11/11] Exit")
        print("\n================================================================")
        print("WILSY OS KERNEL EXECUTION COMPLETE. SYSTEM HALTED CLEANLY.")
        print("================================================================")
        sys.exit(0)
        
    except Exception as e:
        import traceback
        print(f"\n[CRITICAL FAILURE] Kernel panic during CLI execution: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
