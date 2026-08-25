"""
===============================================================================
WILSY OS — COMPATIBILITY REPORT ARTIFACT MODEL (FG208)
===============================================================================
Epitome:
    Defines the formal compatibility artifact payload schema for Wilsy OS.
    Represents the immutable compatibility report published to the platform's
    Artifact Bus following version negotiation and capability check.

Biblical Worth Billions:
    "Write the vision, and make it plain upon tables, that he may run that readeth it."
    — Habakkuk 2:2

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/compatibility/reporting/compatibility_artifact.py
===============================================================================
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any


@dataclass(frozen=True)
class CompatibilityReportArtifact:
    """
    Immutable compatibility report artifact published to the Artifact Bus.
    
    Schema Identifier: compatibility_report_v1
    """
    schema_version: str
    execution_id: str
    engine_id: str
    kernel_version: str
    engine_version: str
    decision: str
    adapter: str
    missing_capabilities: List[str]
    timestamp: str
    sha256: str

    @classmethod
    def create(
        cls,
        execution_id: str,
        engine_id: str,
        kernel_version: str,
        engine_version: str,
        decision: str,
        adapter: Optional[str],
        missing_capabilities: List[str],
        timestamp: Optional[str] = None
    ) -> CompatibilityReportArtifact:
        """
        Factory method creating a cryptographically signed report artifact with SHA256 digest.
        """
        sast_tz = timezone(timedelta(hours=2))
        ts = timestamp or datetime.now(sast_tz).strftime("%Y-%m-%d %H:%M:%S SAST")
        adapter_name = adapter or "NONE"
        missing_sorted = sorted(missing_capabilities)

        raw_payload = {
            "schema_version": "compatibility_report_v1",
            "execution_id": execution_id,
            "engine_id": engine_id,
            "kernel_version": kernel_version,
            "engine_version": engine_version,
            "decision": decision,
            "adapter": adapter_name,
            "missing_capabilities": missing_sorted,
            "timestamp": ts,
        }
        digest = hashlib.sha256(json.dumps(raw_payload, sort_keys=True).encode("utf-8")).hexdigest()

        return cls(
            schema_version="compatibility_report_v1",
            execution_id=execution_id,
            engine_id=engine_id,
            kernel_version=kernel_version,
            engine_version=engine_version,
            decision=decision,
            adapter=adapter_name,
            missing_capabilities=missing_sorted,
            timestamp=ts,
            sha256=digest
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes artifact payload into dictionary representation."""
        return {
            "schema_version": self.schema_version,
            "execution_id": self.execution_id,
            "engine_id": self.engine_id,
            "kernel_version": self.kernel_version,
            "engine_version": self.engine_version,
            "decision": self.decision,
            "adapter": self.adapter,
            "missing_capabilities": list(self.missing_capabilities),
            "timestamp": self.timestamp,
            "sha256": self.sha256,
        }
