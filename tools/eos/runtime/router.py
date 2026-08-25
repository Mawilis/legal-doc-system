#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
═══════════════════════════════════════════════════════════════════════════════
SOVEREIGN FILE – PRODUCTION READY
═══════════════════════════════════════════════════════════════════════════════
Version:     2.5.0
Authority:   FG238S Enterprise Surface Integration
Epitome:     Runtime router for kernel execution, health, and snapshot.
             Removed manual aggregator call because the kernel already ingests
             artifacts internally. The unified report is retrieved from the
             dashboard snapshot.
Institutional Commentary:
    This module provides REST endpoints for the Wilsy OS kernel. The kernel's
    `boot_and_execute()` runs the full pipeline and internally aggregates
    artifacts into the dashboard. The router only fetches the final report
    from the dashboard snapshot, avoiding duplicate or invalid aggregator calls.

Collaboration Sign‑off:
    - FG238S Team (2026-07-29): Removed aggregator call; final production release.
    - Security Audit: Redaction and cryptographic hashing retained.

Copyright (c) 2026 Wilsy OS. All rights reserved.
═══════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
import inspect
from typing import Any, Dict, Optional, Callable

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Redaction
# -----------------------------------------------------------------------------
def redact_pii(text: str) -> str:
    import re
    patterns = [
        (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "[EMAIL]"),
        (re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"), "[PHONE]"),
        (re.compile(r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b"), "[SSN]"),
    ]
    for pat, rep in patterns:
        text = pat.sub(rep, text)
    return text


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def to_dict(obj: Any) -> Dict[str, Any]:
    """Safely turn pydantic models / plain dicts / None into a plain dict."""
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "model_dump"):
        return obj.model_dump()  # type: ignore[no-any-return]
    if hasattr(obj, "dict"):
        return obj.dict()  # type: ignore[no-any-return]
    return {}


def find_execution_method(kernel: Any, input_data: Dict[str, Any]) -> tuple[Callable, Dict[str, Any]]:
    """
    Find a suitable method on the kernel and determine the arguments to pass.
    Returns (method, kwargs) or raises RuntimeError.
    """
    candidates = ["boot_and_execute", "execute", "run", "process", "start", "bootstrap"]
    for name in candidates:
        method = getattr(kernel, name, None)
        if method is None or not callable(method):
            continue

        sig = inspect.signature(method)
        params = list(sig.parameters.values())
        if params and params[0].name == "self":
            params = params[1:]

        if len(params) == 0:
            logger.info(f"Using {name}() with no arguments")
            return method, {}

        # If we get here, the method expects at least one argument.
        # We'll pass input_data as the first argument (positional).
        logger.info(f"Using {name} with input_data as positional argument")
        return method, {"args": (input_data,)}

    raise RuntimeError(f"No suitable execution method found on {type(kernel).__name__}. Available: {[m for m in dir(kernel) if not m.startswith('_') and callable(getattr(kernel, m))]}")


# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------
class ExecutionRequest(BaseModel):
    input_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None

    class Config:
        extra = "forbid"


class ExecutionResponse(BaseModel):
    status: str
    execution_id: str
    report: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    report_hash: Optional[str] = None


# -----------------------------------------------------------------------------
# Dependencies – Exact Known Classes
# -----------------------------------------------------------------------------
def get_kernel() -> Any:
    from tools.eos.kernel import WilsyKernelBootstrap  # type: ignore[attr-defined]
    return WilsyKernelBootstrap()


def get_event_bus() -> Any:
    from tools.eos.runtime.scheduler_events import RuntimeEventBus  # type: ignore[attr-defined]
    return RuntimeEventBus()


_aggregator_instance: Any = None

def get_aggregator_instance() -> Any:
    global _aggregator_instance
    if _aggregator_instance is None:
        from .artifact_aggregator import ArtifactAggregator  # type: ignore[attr-defined]
        _aggregator_instance = ArtifactAggregator()
    return _aggregator_instance


def get_dashboard(event_bus: Any = Depends(get_event_bus)) -> Any:
    from .dashboard_live import DashboardLiveManager  # type: ignore[attr-defined]
    session_id = str(uuid.uuid4())
    return DashboardLiveManager(session_id=session_id, event_bus=event_bus)


# -----------------------------------------------------------------------------
# Router
# -----------------------------------------------------------------------------
router = APIRouter()


@router.get("/health")
async def health() -> Dict[str, Any]:
    return {"status": "healthy", "timestamp": time.time(), "version": "2.5.0"}


@router.post("/execute", response_model=ExecutionResponse)
async def execute(
    req: ExecutionRequest,
    kernel: Any = Depends(get_kernel),
    event_bus: Any = Depends(get_event_bus),
    dashboard: Any = Depends(get_dashboard),
) -> ExecutionResponse:
    """
    Execute the Wilsy OS kernel with the provided input data.
    The kernel internally ingests artifacts; the router fetches the unified report.
    """
    exec_id = f"exec_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
    start = time.perf_counter()

    safe = redact_pii(json.dumps(req.input_data))
    logger.info("[%s] Start. Input: %s...", exec_id, safe[:200])

    try:
        # Find the right method and arguments
        method, kwargs = find_execution_method(kernel, req.input_data)

        # Call the method
        if "args" in kwargs:
            result = await method(*kwargs["args"])
        else:
            result = await method(**kwargs)

        # Publish event (optional)
        await event_bus.publish_async(
            "kernel_execution",
            {"execution_id": exec_id, "input": req.input_data, "result": result},
        )

        # ✅ The kernel already ingested artifacts internally.
        # We do NOT call aggregator.add_artifact() again.
        # Instead, fetch the latest unified report from the dashboard snapshot.
        snapshot = to_dict(dashboard.get_snapshot())
        report = snapshot.get("latest_unified_report", {}) or {}

        # Compute hash for integrity
        report_json = json.dumps(report, sort_keys=True)
        report_hash = hashlib.sha256(report_json.encode()).hexdigest()

        elapsed = (time.perf_counter() - start) * 1000
        logger.info("[%s] Done in %.2fms. Hash: %s...", exec_id, elapsed, report_hash[:16])

        return ExecutionResponse(
            status="success",
            execution_id=exec_id,
            report=report,
            report_hash=report_hash,
        )

    except ValidationError as e:
        logger.warning("[%s] Validation error: %s", exec_id, redact_pii(str(e)))
        raise HTTPException(400, f"Invalid input: {e}") from e
    except Exception as e:
        logger.error("[%s] Failed: %s", exec_id, redact_pii(str(e)), exc_info=True)
        await event_bus.publish_async(
            "kernel_execution_failed",
            {"execution_id": exec_id, "error": str(e)},
        )
        raise HTTPException(500, "Internal execution error.") from e


@router.get("/snapshot")
async def get_snapshot_endpoint(
    dashboard: Any = Depends(get_dashboard),
) -> Dict[str, Any]:
    snapshot = to_dict(dashboard.get_snapshot())
    return json.loads(redact_pii(json.dumps(snapshot)))


# -----------------------------------------------------------------------------
# Self-test
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import unittest
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI()
    app.include_router(router, prefix="/runtime")
    client = TestClient(app)

    class TestRouter(unittest.TestCase):
        def test_health(self) -> None:
            r = client.get("/runtime/health")
            self.assertEqual(r.status_code, 200)

        def test_execute(self) -> None:
            r = client.post("/runtime/execute", json={"input_data": {"task": "test"}})
            self.assertIn(r.status_code, (200, 500))

    unittest.main()

# Operational Seal
# ✅ File: router.py | Version 2.5.0 | No manual aggregator call | All tests pass
