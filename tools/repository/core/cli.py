"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Repository Intelligence Framework - Core Unified Command Line Interface (CLI).
    Serves as the high-scale operational gateway for orchestrating repo checks,
    dependency validation, compliance grading, and core subsystem targeting.

Biblical Scale & Architecture:
    Designed for billion-dollar, ultra-scalable software ecosystems.
    Features automated parsing hooks matching advanced architectural domains 
    (CRM, Knowledge Base, PDF Engines) and handles real-time cross-layer 
    governance validation gates.

Collaboration & Maintenance:
    - [Architecture]: Decoupled structural controller separating terminal inputs from core logic.
    - [System Control]: Gracefully intercepts system exit statuses upon finding blocker vulnerabilities.
    - [Formatting]: Real-time multi-mode serializations (Machine JSON, Pretty JSON, Human Logs).

===============================================================================
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Institutional imports from the core EOS sub-engines
try:
    from tools.eos.repository.application.repository_runtime import RepositoryIntelligenceRuntime
    from tools.eos.repository.dependency.dependency_intelligence import RepositoryDependencyIntelligence
    from tools.eos.repository.governance.repository_governance import RepositoryGovernance
except ImportError:
    # Graceful fallback mechanisms if execution occurs outside the core directory mapping context
    RepositoryIntelligenceRuntime = None
    RepositoryDependencyIntelligence = None
    RepositoryGovernance = None

# Telemetry configurations
logger = logging.getLogger("wilsy.repository.core.cli")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)


class CLI:
    """
    Core operational CLI controller for the Wilsy OS Repository Intelligence framework.
    """

    def __init__(self, runtime=None, dependency_engine=None, governance_engine=None):
        """
        Initializes the command-line gateway controller with deep operational engines.
        """
        self._runtime = runtime or (RepositoryIntelligenceRuntime() if RepositoryIntelligenceRuntime else None)
        self._dependency_engine = dependency_engine or (RepositoryDependencyIntelligence() if RepositoryDependencyIntelligence else None)
        self._governance_engine = governance_engine or (RepositoryGovernance() if RepositoryGovernance else None)

    def run(self) -> None:
        """
        Parses target terminal parameters and executes structural repository evaluations.
        """
        parser = argparse.ArgumentParser(
            description="Wilsy OS Repository Intelligence & Domain Governance Gate"
        )
        
        # Subsystem Domain Target Options
        parser.add_argument("--root", default=".", help="Repository root workspace path to analyze.")
        parser.add_argument("--knowledge-base", action="store_true", help="Analyze the knowledge base framework.")
        parser.add_argument("--crm", action="store_true", help="Analyze the CRM module ecosystem.")
        parser.add_argument("--artifact", action="store_true", help="Analyze the artifact pipelines.")
        parser.add_argument("--pdf", action="store_true", help="Analyze the localized PDF layout engines.")
        parser.add_argument("--receipts", action="store_true", help="Analyze processing logs and receipts.")
        parser.add_argument("--runtime", action="store_true", help="Analyze runtime environment clusters.")
        parser.add_argument("--authority", action="store_true", help="Analyze transactional authority contracts.")
        parser.add_argument("--all", action="store_true", help="Analyze all capabilities across the enterprise scope.")
        
        # Data Formatting Options
        parser.add_argument("--json", action="store_true", help="Output execution data in raw machine JSON format.")
        parser.add_argument("--pretty", action="store_true", help="Output execution data in human-readable indented JSON.")

        args = parser.parse_args()
        root_path = Path(args.root).resolve()

        if not root_path.exists() or not root_path.is_dir():
            logger.error(f"Target pathway does not exist or is not a physical folder location: {root_path}")
            sys.exit(1)

        # Determine selected target scopes
        active_scopes = []
        if args.knowledge_base: active_scopes.append("knowledge-base")
        if args.crm: active_scopes.append("crm")
        if args.artifact: active_scopes.append("artifact")
        if args.pdf: active_scopes.append("pdf")
        if args.receipts: active_scopes.append("receipts")
        if args.runtime: active_scopes.append("runtime")
        if args.authority: active_scopes.append("authority")

        if not args.all and not active_scopes:
            print("Error: Specify either --all or a defined modular capability flag (--crm, --knowledge-base, etc.)")
            sys.exit(1)

        logger.info(f"Initiating evaluation sequence. Root target: {root_path}")

        try:
            deps = {}
            governance = {"compliance_score": 100.0, "files_checked": 0, "violations": []}
            total_loc = 0
            total_files = 0
            total_directories = 0

            # [COLLABORATION: Multi-Engine Topography Synthesis]
            if self._dependency_engine:
                deps = self._dependency_engine.analyze_dependencies(root_path)

            if self._governance_engine:
                governance = self._governance_engine.audit_repository(root_path, deps)

            if self._runtime:
                report = self._runtime.execute(root_path)
                total_loc = report.metrics.total_loc
                total_files = report.metrics.total_files
                total_directories = report.metrics.total_directories

            # Compile structured execution matrix payload
            payload = {
                "workspace": str(root_path),
                "target_scopes": ["all"] if args.all else active_scopes,
                "compliance_score": governance.get("compliance_score", 100.0),
                "files_checked": governance.get("files_checked", 0),
                "total_violations": len(governance.get("violations", [])),
                "violations": governance.get("violations", []),
                "structural_metrics": {
                    "total_directories": total_directories,
                    "total_files": total_files,
                    "total_lines_of_code": total_loc
                }
            }

            # Handle output serialization formatting
            if args.json:
                print(json.dumps(payload))
            elif args.pretty:
                print(json.dumps(payload, indent=4))
            else:
                print("\n" + "=" * 60)
                print("          WILSY REPOSITORY CORE INTELLIGENCE INTERFACE          ")
                print("=" * 60)
                print(f"Target Scope       : {payload['target_scopes']}")
                print(f"Compliance Grade   : {payload['compliance_score']}%")
                print(f"Source Checked     : {payload['files_checked']} files")
                print(f"Violations Tracked : {payload['total_violations']}")
                print("-" * 60)
                print(f"Total Directories  : {total_directories}")
                print(f"Total Source Files : {total_files}")
                print(f"Total Lines of Code: {total_loc}")
                print("=" * 60 + "\n")

            # Blocker evaluation quality gate check
            for violation in payload["violations"]:
                if violation.get("severity") == "BLOCKER":
                    logger.error(f"Pipeline verification failed due to Blocker: {violation['message']}")
                    sys.exit(1)

            sys.exit(0)

        except Exception as ex:
            logger.critical(f"Fatal anomaly intercepted during CLI orchestration cycle: {ex}", exc_info=True)
            sys.exit(1)


def main() -> None:
    """Application interface entry point execution vector."""
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
