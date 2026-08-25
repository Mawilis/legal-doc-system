/**
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG215 RUNTIME API SERVICE
FILE: client/src/services/runtimeApi.js
===============================================================================
Epitome:
    Consumes GET /api/v1/runtime, GET /api/v1/engines, and POST /api/v1/execution.

Biblical Worth Billions:
    "Honesty is the best policy." — Proverbs 11:3
===============================================================================
 */

const API_BASE = "http://127.0.0.1:8000/api/v1";
const API_KEY = "WILSY-OS-MASTER-API-KEY-2026";

async function request(endpoint, options = {}) {
    const headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
        ...(options.headers || {})
    };
    const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
    const json = await res.json();
    return json;
}

export const runtimeApi = {
    getRuntime: () => request("/kernel"),
    getEngines: () => request("/engines"),
    getEvents: () => request("/events"),
    getArtifacts: () => request("/artifacts"),
    getDigitalTwin: () => request("/dashboard"),
    getKnowledgeGraph: () => request("/repository"),
    getGovernance: () => request("/governance"),
    getPredictions: () => request("/predictions"),
    getDocumentation: () => request("/documentation"),
    getReports: () => request("/reports"),
    getVersions: () => request("/versions"),
    getCompatibility: () => request("/compatibility"),
    executeCommand: (executionId, moduleCode, payload) => request("/execution", {
        method: "POST",
        body: JSON.stringify({ execution_id: executionId, module_code: moduleCode, payload })
    })
};
