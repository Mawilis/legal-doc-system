"""
===============================================================================
WILSY OS — COMPATIBILITY ENGINE APPLICATION SERVICE (FG208)
===============================================================================
Epitome:
    Core orchestration service for platform architecture protection and version
    negotiation. Evaluates incoming engine descriptors against kernel ABI bounds,
    validates required/optional platform capabilities, resolves migration adapters,
    and produces cryptographically signed, immutable compatibility decisions.

Biblical Worth Billions:
    "Which have borne the burden and heat of the day."
    — Matthew 20:12

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/compatibility/application/compatibility_engine.py
===============================================================================
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple

from tools.eos.compatibility.domain.compatibility_models import (
    CompatibilityStatus,
    EngineCompatibilityBlock,
    CompatibilityDecision,
)
from tools.eos.compatibility.domain.abi_contract import KernelABIContract
from tools.eos.compatibility.domain.compatibility_result import (
    CompatibilityEvaluationResult,
    CompatibilityEvaluationLog,
)
from tools.eos.compatibility.application.capability_registry import CapabilityRegistry
from tools.eos.compatibility.application.adapter_manager import AdapterManager

logger = logging.getLogger("WilsyOS.Compatibility.CompatibilityEngine")


class CompatibilityEngine:
    """
    Sovereign Application Service enforcing version compatibility and platform protection.
    """

    def __init__(
        self,
        kernel_contract: Optional[KernelABIContract] = None,
        capability_registry: Optional[CapabilityRegistry] = None,
        adapter_manager: Optional[AdapterManager] = None,
    ) -> None:
        self.kernel_contract = kernel_contract or KernelABIContract(
            kernel_version="2.0.0",
            abi_version="2.0",
            supported_abi_versions=["1.0", "2.0"],
            core_capabilities=[
                "ExecutionContext", "EventBus", "ArtifactBus", "EngineRegistry",
                "Scheduler", "Sentinel", "KnowledgeGraph", "Memory", "Replay",
                "Governance", "Observability"
            ],
            extension_capabilities=[
                "Dashboard", "DigitalTwin", "AiReasoning", "PredictionEngine", "CommandCenter"
            ]
        )
        self.capability_registry = capability_registry or CapabilityRegistry()
        self.adapter_manager = adapter_manager or AdapterManager()
        logger.info(
            "CompatibilityEngine online [Kernel Version: %s, Active ABI: %s]",
            self.kernel_contract.kernel_version,
            self.kernel_contract.abi_version
        )

    def evaluate_engine(
        self,
        execution_id: str,
        engine_block: EngineCompatibilityBlock
    ) -> CompatibilityEvaluationResult:
        """
        Executes complete compatibility negotiation flow for an engine descriptor block.
        """
        start_time = time.perf_counter()
        logs: List[CompatibilityEvaluationLog] = []
        sast_tz = timezone(timedelta(hours=2))

        def add_log(stage: str, passed: bool, detail: str) -> None:
            ts = datetime.now(sast_tz).strftime("%Y-%m-%d %H:%M:%S SAST")
            logs.append(CompatibilityEvaluationLog(stage=stage, passed=passed, detail=detail, timestamp=ts))

        # Stage 1: Descriptor Payload Sanity
        if not engine_block.engine_id or not engine_block.engine_version or not engine_block.abi_version:
            add_log("DESCRIPTOR_INGEST", False, "Engine descriptor missing mandatory identification fields.")
            decision = CompatibilityDecision.create(
                execution_id=execution_id,
                engine_id=engine_block.engine_id or "UNKNOWN",
                kernel_version=self.kernel_contract.kernel_version,
                engine_version=engine_block.engine_version or "0.0.0",
                abi_version=engine_block.abi_version or "0.0",
                required_capabilities=engine_block.required_capabilities,
                optional_capabilities=engine_block.optional_capabilities,
                missing_capabilities=[],
                adapter_selected=None,
                status=CompatibilityStatus.REJECTED
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return CompatibilityEvaluationResult.create(decision, logs, elapsed_ms)

        add_log("DESCRIPTOR_INGEST", True, f"Parsed descriptor for engine '{engine_block.engine_id}' v{engine_block.engine_version}.")

        # Stage 2: Kernel Version Bound Verification
        bounds_valid = self.kernel_contract.satisfies_version_bounds(
            engine_block.minimum_kernel_version,
            engine_block.maximum_kernel_version
        )
        if not bounds_valid:
            add_log(
                "KERNEL_VERSION_BOUNDS",
                False,
                f"Kernel version {self.kernel_contract.kernel_version} violates engine bounds "
                f"[{engine_block.minimum_kernel_version}, {engine_block.maximum_kernel_version})."
            )
        else:
            add_log(
                "KERNEL_VERSION_BOUNDS",
                True,
                f"Kernel version {self.kernel_contract.kernel_version} satisfies engine bounds "
                f"[{engine_block.minimum_kernel_version}, {engine_block.maximum_kernel_version})."
            )

        # Stage 3: Capability Negotiation
        missing_required, available_optional = self.capability_registry.evaluate_capability_requirements(
            engine_block.required_capabilities,
            engine_block.optional_capabilities
        )

        if missing_required:
            add_log("CAPABILITY_NEGOTIATION", False, f"Missing required capabilities: {missing_required}")
        else:
            add_log("CAPABILITY_NEGOTIATION", True, f"All required capabilities satisfied. Available optional: {available_optional}")

        # Stage 4: ABI Match & Adapter Resolution
        native_abi_supported = self.kernel_contract.is_abi_natively_supported(engine_block.abi_version)
        selected_adapter: Optional[str] = None

        if native_abi_supported and engine_block.abi_version == self.kernel_contract.abi_version:
            selected_adapter = "ADAPTER-ABI-V2-NATIVE"
            add_log("ABI_VERIFICATION", True, f"Native ABI version match ({engine_block.abi_version}).")
        else:
            adapter = self.adapter_manager.resolve_adapter(engine_block.abi_version, self.kernel_contract.kernel_version)
            if adapter:
                selected_adapter = adapter.adapter_id
                add_log("ABI_VERIFICATION", True, f"ABI mismatch resolved using adapter [{selected_adapter}].")
            else:
                add_log("ABI_VERIFICATION", False, f"Unsupported ABI version '{engine_block.abi_version}' with no adapter available.")

        # Stage 5: Status Synthesis Matrix
        if not bounds_valid or missing_required:
            final_status = CompatibilityStatus.INCOMPATIBLE
        elif not native_abi_supported and not selected_adapter:
            final_status = CompatibilityStatus.INCOMPATIBLE
        elif selected_adapter and (selected_adapter != "ADAPTER-ABI-V2-NATIVE"):
            final_status = CompatibilityStatus.ADAPTER_REQUIRED
        else:
            final_status = CompatibilityStatus.COMPATIBLE

        # Stage 6: Build Immutable Decision
        decision = CompatibilityDecision.create(
            execution_id=execution_id,
            engine_id=engine_block.engine_id,
            kernel_version=self.kernel_contract.kernel_version,
            engine_version=engine_block.engine_version,
            abi_version=engine_block.abi_version,
            required_capabilities=engine_block.required_capabilities,
            optional_capabilities=engine_block.optional_capabilities,
            missing_capabilities=missing_required,
            adapter_selected=selected_adapter,
            status=final_status
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        logger.info(
            "Compatibility evaluation completed for %s [Status: %s, Latency: %.3f ms]",
            engine_block.engine_id,
            final_status.value,
            elapsed_ms
        )

        return CompatibilityEvaluationResult.create(decision, logs, elapsed_ms)
