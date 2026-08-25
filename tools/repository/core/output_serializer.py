"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    High-Performance Multi-Format Serialization and Output Encoding Engine.
    Orchestrates memory-safe conversion pipelines transforming dense repository 
    graph topologies and metric indices into machine and human formats.

Biblical Scale & Architecture:
    Built to handle high-frequency reporting telemetry for billion-dollar codebases. 
    Implements architectural isolation barriers to block raw data structure leaks,
    uses byte-exact sizing thresholds to prevent memory bloating, and structures
    optimized string builders for massive telemetry payloads.

Collaboration & Maintenance:
    - [Safety]: Enforces strict encapsulation boundaries against system object serialization.
    - [Performance]: Leverages pre-allocated array configurations for fast string joins.
    - [Compliance]: Fully satisfies the Layering and Orchestration Rules of the Kernel Constitution.

===============================================================================
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

# Initialize institutional logger
logger = logging.getLogger("wilsy.repository.core.output_serializer")


class OutputSerializer:
    """
    Industrial-grade encoding component managing structured schema serializations.
    """

    def __init__(self, max_byte_size: int = 500 * 1024) -> None:
        """
        Initializes the serialization engine with security limits.
        """
        self.max_byte_size = max_byte_size

    def serialize(self, data: Any, pretty: bool = True) -> str:
        """
        Encodes abstract system data structures into standard JSON strings with safety checks.
        """
        # Architectural Guard: Prevent internal graph components from leaking directly into outputs
        if isinstance(data, dict):
            if "RepositoryIndex" in data or any(k == "RepositoryIndex" for k in data.keys()):
                raise ValueError(
                    "Security Violation: Raw RepositoryIndex structures cannot be directly serialized. "
                    "Extract structured metrics payloads through official boundary methods."
                )
        elif isinstance(data, str) and "RepositoryIndex" in data:
            raise ValueError("Security Violation: Detected raw RepositoryIndex references within serialization context.")

        try:
            # Execute encoding operation with controlled spacing structures
            indentation = 4 if pretty else None
            serialized_data = json.dumps(data, indent=indentation, ensure_ascii=False)
        except TypeError as err:
            logger.error(f"Failed to encode target structural tree. Unserializable elements present: {err}")
            raise ValueError(f"Serialization failed due to type mismatch: {err}") from err

        # Verify strict structural buffer sizes to prevent resource exhaustions
        encoded_bytes_len = len(serialized_data.encode("utf-8"))
        if encoded_bytes_len > self.max_byte_size:
            logger.error(f"Payload overflow block triggered. Encoded footprint: {encoded_bytes_len} bytes.")
            raise ValueError(
                f"Serialized output volume ({encoded_bytes_len} bytes) violates safe standard limits "
                f"({self.max_byte_size} bytes). Apply truncation vectors at the crawler level."
            )

        return serialized_data

    def machine_json(self, data: Any) -> str:
        """
        Encodes input data into space-optimized, un-indented JSON data sequences.
        """
        return self.serialize(data, pretty=False)

    def pretty_json(self, data: Any) -> str:
        """
        Encodes input data into standard structural layout views.
        """
        return self.serialize(data, pretty=True)

    def human_output(self, data: Any) -> str:
        """
        Constructs ultra-clean, high-readability architectural summaries for system engineering eyes.
        """
        if isinstance(data, dict):
            files_list: List[Dict[str, Any]] = data.get("files", [])
            summary_title = data.get("summary", "Repository summary")
            total_count = data.get("fileCount", len(files_list))
            
            # Utilize sequential line lists for optimal assembly performance
            lines: List[str] = [
                f"Summary: {summary_title}",
                f"Files: {total_count}"
            ]
            
            # Format structural entries safely while applying low-latency output limits
            display_limit = 200
            for entry in files_list[:display_limit]:
                path_str = entry.get("path", "unknown-node")
                size_val = entry.get("size", 0)
                loc_val = entry.get("loc", 0)
                
                # Append granular record tracking block
                lines.append(f"- {path_str} ({size_val} bytes, {loc_val} LOC)")

            # Track explicit truncation status cleanly
            if len(files_list) > display_limit:
                lines.append(f"... {len(files_list) - display_limit} more files truncated from human viewport context.")

            # Append global architectural metrics if populated by the index engines
            if "metrics" in data:
                m = data["metrics"]
                lines.append("--- Metrics Telemetry ---")
                lines.append(f"  Total Directories    : {m.get('total_directories', 0)}")
                lines.append(f"  Total Active Files   : {m.get('total_files', 0)}")
                lines.append(f"  Total Lines Of Code  : {m.get('total_lines_of_code', 0)}")
                lines.append(f"  Total Capacity Volume: {m.get('total_bytes_volume', 0)} bytes")

            return "\n".join(lines)

        if isinstance(data, list):
            return "\n".join(f"- {str(item)}" for item in data)

        return str(data)
