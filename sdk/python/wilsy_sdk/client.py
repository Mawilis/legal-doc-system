"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG213 INSTITUTIONAL SDK - PYTHON CLIENT
FILE: sdk/python/wilsy_sdk/client.py
===============================================================================
Epitome:
    Official Wilsy OS Python SDK Client. Exposes all core capabilities (runtime
    execution, artifacts, reports, event streams, documentation, scheduler,
    digital twin, and knowledge graph search) interacting securely with the Kernel Gateway.

Biblical Worth Billions:
    "Where no counsel is, the people fall: but in the multitude of counsellors there is safety."
    — Proverbs 11:14

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: sdk/python/wilsy_sdk/client.py
===============================================================================
"""

import json
import urllib.request
import urllib.error
from typing import Any, Dict, Optional

class SdkResponse:
    def __init__(self, d: Dict[str, Any]):
        self.success = d.get("success", True)
        self.status_code = d.get("status_code", 200)
        self.message = d.get("message", "Success")
        self.data = d.get("data")
        self.timestamp = d.get("timestamp", "")
        self.execution_id = d.get("execution_id", "")

class WilsyClient:
    """Institutional client for interacting with the Wilsy OS Kernel Gateway API."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000", api_key: Optional[str] = None, jwt_token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.jwt_token = jwt_token

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        elif self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"
        return headers

    def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> SdkResponse:
        url = f"{self.base_url}{endpoint}"
        body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, headers=self._get_headers(), method=method)
        with urllib.request.urlopen(req) as response:
            parsed = json.loads(response.read().decode("utf-8"))
            return SdkResponse(parsed)

    def get_kernel_info(self) -> SdkResponse:
        """Retrieve core Wilsy OS kernel metadata and readiness."""
        return self._request("GET", "/api/v1/kernel")

    def list_engines(self) -> SdkResponse:
        """List all registered Wilsy OS executive modules and engines."""
        return self._request("GET", "/api/v1/engines")

    def execute_runtime(self, execution_id: str, module_code: str, payload: Dict[str, Any]) -> SdkResponse:
        """Execute a remote kernel execution entity contract."""
        data = {"execution_id": execution_id, "module_code": module_code, "payload": payload}
        return self._request("POST", "/api/v1/execution", data=data)

    def read_artifacts(self) -> SdkResponse:
        """Retrieve generated executive PDF reports and compilation artifacts."""
        return self._request("GET", "/api/v1/artifacts")

    def query_reports(self) -> SdkResponse:
        """Access executive summary reports and compliance metrics."""
        return self._request("GET", "/api/v1/reports")

    def subscribe_to_events(self) -> SdkResponse:
        """Query the event bus logs and system telemetry streams."""
        return self._request("GET", "/api/v1/events")

    def read_documentation(self) -> SdkResponse:
        """Index all system documentation and sovereign architecture guides."""
        return self._request("GET", "/api/v1/documentation")

    def trigger_scheduler(self, task_name: str, parameters: Dict[str, Any]) -> SdkResponse:
        """Schedule asynchronous kernel tasks and workflows."""
        data = {"task_name": task_name, "parameters": parameters}
        return self._request("POST", "/api/v1/scheduler", data=data)

    def access_digital_twin(self) -> SdkResponse:
        """Access digital twin multi-tenant simulation state."""
        return self._request("GET", "/api/v1/dashboard")

    def search_knowledge_graph(self) -> SdkResponse:
        """Search repository intelligence and kernel knowledge graph."""
        return self._request("GET", "/api/v1/repository")
