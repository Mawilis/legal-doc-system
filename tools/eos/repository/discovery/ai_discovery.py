"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    High-Fidelity Automated AI Asset and Cognitive Inventory Discovery Engine.
    Statically inspects repository structures for machine learning model artifacts,
    prompt engineering templates, and vector database indices.

Biblical Scale & Architecture:
    This is a billion-dollar, production-ready enterprise engine. No child's place.
    Operates via optimized filesystem traversal to index the system's "Cognitive Plane."
    Ensures that every AI asset is mapped, classified, and traceable within the 
    institutional architecture blueprint.

Collaboration & Maintenance:
    - [Reliability]: Implements structural detection for AI manifests and model artifacts.
    - [Security]: Safely maps AI footprint metadata without introspecting or loading binary weights.
    - [Data Integrity]: Delivers completely frozen data models to guarantee state stability.

===============================================================================
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

# Initialize institutional logger
logger = logging.getLogger("wilsy.eos.repository.discovery.ai_discovery")


@dataclass(frozen=True)
class AIRecord:
    """
    Immutable representation of an isolated operational AI asset or model artifact.
    """
    ai_id: str
    target_module: str
    ai_type: str  # e.g., 'MODEL_WEIGHTS', 'PROMPT_TEMPLATE', 'VECTOR_INDEX', 'INFERENCE_CONFIG'
    description: str


class AIDiscovery:
    """
    Industrial-grade AI Asset Extractor and Cognitive Mapping Component.
    Catalogs inference models, prompt templates, and vector stores for architectural correlation.
    """

    def __init__(self) -> None:
        """
        Initializes the discovery engine with institutional AI asset signatures.
        """
        # Mapping file extensions and path keywords to AI functional roles
        self._ai_patterns = {
            ".onnx": "MODEL_WEIGHTS",
            ".pt": "MODEL_WEIGHTS",
            ".pkl": "MODEL_WEIGHTS",
            ".bin": "MODEL_WEIGHTS",
            ".prompt": "PROMPT_TEMPLATE",
            ".vector": "VECTOR_INDEX",
            ".yaml": "INFERENCE_CONFIG",
            ".json": "INFERENCE_CONFIG"
        }

    def discover_in_file(self, repository_root: Path, relative_file_path: str) -> tuple[AIRecord, ...]:
        """
        Statically inspects a codebase node to isolate AI model, prompt, or index definitions.
        """
        full_path = Path(repository_root) / relative_file_path
        found_records: list[AIRecord] = []

        if not full_path.exists():
            return ()

        # Heuristic: Check path context (e.g., directories named 'models', 'prompts', 'vectors')
        path_str = str(full_path).lower()
        is_ai_asset = any(term in path_str for term in ["model", "prompt", "vector", "inference"])
        
        if is_ai_asset and full_path.suffix in self._ai_patterns:
            found_records.append(AIRecord(
                ai_id=full_path.stem,
                target_module=relative_file_path,
                ai_type=self._ai_patterns[full_path.suffix],
                description=f"Identified cognitive asset artifact: {full_path.name}"
            ))

        return tuple(found_records)

    def discover_all(self, repository_root: Path, file_manifest: tuple[str, ...]) -> tuple[AIRecord, ...]:
        """
        Compiles AI asset catalogs across the validated repository file manifest.
        """
        logger.info(f"Initiating full architectural AI Discovery sweep across {len(file_manifest)} targets.")
        master_registry: list[AIRecord] = []

        for relative_file_path in file_manifest:
            records = self.discover_in_file(repository_root, relative_file_path)
            master_registry.extend(records)

        logger.info(f"AI Discovery phase finalized. Successfully registered {len(master_registry)} AI assets.")
        return tuple(sorted(master_registry, key=lambda x: x.ai_id))

