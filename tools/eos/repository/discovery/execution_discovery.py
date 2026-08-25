"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    High-Fidelity Automated Execution Discovery and Runtime Hook Extraction Engine.
    Statically isolates architectural entry points, API route definitions, scheduled 
    worker tasks, and daemon execution nodes across the repository topography.

Biblical Scale & Architecture:
    This is a billion-dollar, production-ready enterprise engine. No child's place.
    Operates strictly via performance-optimized static matching matrices over
    the repository layout. Eliminates blind execution loops by translating runtime 
    triggers into frozen, type-safe telemetry records.

Collaboration & Maintenance:
    - [Reliability]: Implements strict structural classification parameters.
    - [Security]: Safely isolates routing topography schemas from operational modules.
    - [Data Integrity]: Delivers completely frozen data models to guarantee zero state drift.

===============================================================================
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

# Initialize institutional logger
logger = logging.getLogger("wilsy.eos.repository.discovery.execution_discovery")


@dataclass(frozen=True)
class ExecutionSignature:
    """
    Immutable representation of an isolated operational code runtime execution node.
    """
    execution_id: str
    target_module: str
    entry_type: str        # e.g., HTTP_ENDPOINT, CRON_JOB, ASYNC_WORKER, CLI_ENTRY
    trigger_context: str   # e.g., "GET /api/v1/docs", "0 0 * * *", "kafka.topic.events"


class ExecutionDiscovery:
    """
    Industrial-grade Execution Entry Point Extractor and Runtime Mapping Component.
    Parses structural hooks to catalog valid application gateways and processing flows.
    """

    def __init__(self) -> None:
        """
        Initializes the execution discovery engine with pre-compiled structural regex matrices.
        """
        # Matches API routing definitions (e.g., @app.get("/path"), @router.post('/path'))
        self._http_regex = re.compile(
            r'@(?:\w+\.)?(?:get|post|put|delete|patch|route)\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE
        )
        
        # Matches scheduled worker loops or cron jobs (e.g., @periodic_task(cron="0 * * * *"))
        self._cron_regex = re.compile(
            r'(?:cron|schedule|periodic)[^=]*=\s*["\']([^"\']+)["\']', re.IGNORECASE
        )
        
        # Matches background worker consumer subscriptions (e.g., @rabbitmq.consume("topic"))
        self._worker_regex = re.compile(
            r'@(?:\w+\.)?(?:consume|worker|listener|queue|topic)\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE
        )
        
        # Matches raw main entry points (e.g., if __name__ == "__main__:")
        self._cli_regex = re.compile(
            r'if\s+__name__\s*==\s*["\']__main__["\']\s*:'
        )

    def discover_in_file(self, repository_root: Path, relative_file_path: str) -> tuple[ExecutionSignature, ...]:
        """
        Statically inspects a codebase file to isolate all valid runtime execution anchors.
        """
        full_path = Path(repository_root) / relative_file_path
        found_signatures: list[ExecutionSignature] = []

        if not full_path.exists() or full_path.suffix not in {".py", ".ts", ".js"}:
            return ()

        logger.debug(f"Scanning structural execution layers for node: {relative_file_path}")

        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as src_file:
                for line_idx, line in enumerate(src_file, start=1):
                    cleaned_line = line.strip()

                    # 1. Inspect for HTTP Routing Infrastructure
                    http_match = self._http_regex.search(cleaned_line)
                    if http_match:
                        route_path = http_match.group(1)
                        # Derive standard action verbs from line context
                        verb_match = re.search(r'(get|post|put|delete|patch)', cleaned_line, re.IGNORECASE)
                        verb = verb_match.group(1).upper() if verb_match else "GET"
                        
                        found_signatures.append(ExecutionSignature(
                            execution_id=f"exec.http.{relative_file_path.replace('/', '.')}.line_{line_idx}",
                            target_module=relative_file_path,
                            entry_type="HTTP_ENDPOINT",
                            trigger_context=f"{verb} {route_path}"
                        ))
                        continue

                    # 2. Inspect for Background Event Worker Consumers
                    worker_match = self._worker_regex.search(cleaned_line)
                    if worker_match:
                        topic_channel = worker_match.group(1)
                        found_signatures.append(ExecutionSignature(
                            execution_id=f"exec.worker.{relative_file_path.replace('/', '.')}.line_{line_idx}",
                            target_module=relative_file_path,
                            entry_type="ASYNC_WORKER",
                            trigger_context=topic_channel
                        ))
                        continue

                    # 3. Inspect for Automated Cron / Periodic Cycles
                    if "periodic" in cleaned_line or "cron" in cleaned_line:
                        cron_match = self._cron_regex.search(cleaned_line)
                        if cron_match:
                            cron_schedule = cron_match.group(1)
                            found_signatures.append(ExecutionSignature(
                                execution_id=f"exec.cron.{relative_file_path.replace('/', '.')}.line_{line_idx}",
                                target_module=relative_file_path,
                                entry_type="CRON_JOB",
                                trigger_context=cron_schedule
                            ))
                            continue

                    # 4. Inspect for System CLI Executable Blocks
                    if self._cli_regex.match(cleaned_line):
                        found_signatures.append(ExecutionSignature(
                            execution_id=f"exec.cli.{relative_file_path.replace('/', '.')}.line_{line_idx}",
                            target_module=relative_file_path,
                            entry_type="CLI_ENTRY",
                            trigger_context="__main__"
                        ))

        except Exception as err:
            logger.error(f"Execution Discovery Fault: System failed to analyze runtime layout of {relative_file_path}: {err}")

        return tuple(found_signatures)

    def discover_all(self, repository_root: Path, file_manifest: tuple[str, ...]) -> tuple[ExecutionSignature, ...]:
        """
        Compiles execution entry catalogs across the entirety of the validated repository file manifest.
        """
        logger.info(f"Initiating full architectural Execution Discovery sweep across {len(file_manifest)} targets.")
        master_registry: list[ExecutionSignature] = []

        for relative_file_path in file_manifest:
            signatures = self.discover_in_file(repository_root, relative_file_path)
            master_registry.extend(signatures)

        logger.info("Execution Discovery processing phase finalized successfully.")
        return tuple(sorted(master_registry, key=lambda x: x.execution_id))

