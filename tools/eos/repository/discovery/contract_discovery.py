"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    High-Fidelity Automated Contract Discovery and Interface Mapping Engine.
    Statically isolates API schemas, interface definitions, and structural 
    type protocols that constitute the communication fabric of the system.

Biblical Scale & Architecture:
    This is a billion-dollar, production-ready enterprise engine. No child's place.
    Operates strictly via performance-optimized static matching matrices over
    the repository layout. Eliminates blind dependency coupling by defining
    immutable, typed contractual boundaries between architectural modules.

Collaboration & Maintenance:
    - [Reliability]: Implements strict structural classification parameters for interfaces.
    - [Security]: Safely isolates communication contracts from business logic implementations.
    - [Data Integrity]: Delivers completely frozen data models to guarantee zero state drift.

===============================================================================
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

# Initialize institutional logger
logger = logging.getLogger("wilsy.eos.repository.discovery.contract_discovery")


@dataclass(frozen=True)
class ContractSignature:
    """
    Immutable representation of an isolated operational communication interface contract.
    """
    contract_id: str
    target_module: str
    contract_type: str        # e.g., PROTOCOL, SCHEMA, INTERFACE, API_DEFINITION
    details: str


class ContractDiscovery:
    """
    Industrial-grade Contract Extractor and Interface Mapping Component.
    Parses structural definitions to catalog the architectural glue holding system modules together.
    """

    def __init__(self) -> None:
        """
        Initializes the contract discovery engine with optimized structural pattern matchers.
        """
        # Matches Protocol or Interface definitions (e.g., class MyService(Protocol):)
        self._interface_regex = re.compile(
            r'class\s+(\w+)\s*\(.*?(?:Protocol|Interface|Base).*?\)\s*:', re.IGNORECASE
        )
        
        # Matches schema class definitions (e.g., class UserSchema(BaseModel):)
        self._schema_regex = re.compile(
            r'class\s+(\w+)\s*\(.*?(?:Schema|Model|DTO).*?\)\s*:', re.IGNORECASE
        )
        
        # Matches gRPC or generic API definition anchors
        self._rpc_regex = re.compile(
            r'(?:message|service|rpc)\s+(\w+)\s*\{', re.IGNORECASE
        )

    def discover_in_file(self, repository_root: Path, relative_file_path: str) -> tuple[ContractSignature, ...]:
        """
        Statically inspects a codebase file to isolate all valid communication interface anchors.
        """
        full_path = Path(repository_root) / relative_file_path
        found_signatures: list[ContractSignature] = []

        if not full_path.exists() or full_path.suffix not in {".py", ".ts", ".js", ".proto"}:
            return ()

        logger.debug(f"Scanning structural interface layers for node: {relative_file_path}")

        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as src_file:
                for line_idx, line in enumerate(src_file, start=1):
                    cleaned_line = line.strip()

                    # 1. Inspect for Formal Interface / Protocol Contracts
                    interface_match = self._interface_regex.search(cleaned_line)
                    if interface_match:
                        found_signatures.append(ContractSignature(
                            contract_id=interface_match.group(1),
                            target_module=relative_file_path,
                            contract_type="PROTOCOL_INTERFACE",
                            details=f"Defined at line {line_idx}"
                        ))
                        continue

                    # 2. Inspect for Data Schema / DTO Contracts
                    schema_match = self._schema_regex.search(cleaned_line)
                    if schema_match:
                        found_signatures.append(ContractSignature(
                            contract_id=schema_match.group(1),
                            target_module=relative_file_path,
                            contract_type="DATA_SCHEMA",
                            details=f"Defined at line {line_idx}"
                        ))
                        continue

                    # 3. Inspect for RPC Service Definitions
                    rpc_match = self._rpc_regex.search(cleaned_line)
                    if rpc_match:
                        found_signatures.append(ContractSignature(
                            contract_id=rpc_match.group(1),
                            target_module=relative_file_path,
                            contract_type="RPC_SERVICE",
                            details=f"Defined at line {line_idx}"
                        ))

        except Exception as err:
            logger.error(f"Contract Discovery Fault: System failed to analyze interface layout of {relative_file_path}: {err}")

        return tuple(found_signatures)

    def discover_all(self, repository_root: Path, file_manifest: tuple[str, ...]) -> tuple[ContractSignature, ...]:
        """
        Compiles structural contract catalogs across the entirety of the validated repository file manifest.
        """
        logger.info(f"Initiating full architectural Contract Discovery sweep across {len(file_manifest)} targets.")
        master_registry: list[ContractSignature] = []

        for relative_file_path in file_manifest:
            signatures = self.discover_in_file(repository_root, relative_file_path)
            master_registry.extend(signatures)

        logger.info("Contract Discovery processing phase finalized successfully.")
        return tuple(sorted(master_registry, key=lambda x: x.contract_id))

