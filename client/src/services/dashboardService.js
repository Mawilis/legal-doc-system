/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - DASHBOARD SERVICE LAYER [V1.0.0-PRODUCTION-GRADE]                                                                         ║
 * ║ [EPITOME: KERNEL DASHBOARD CONTRACT CONSUMPTION | LIVE STATE STREAMING | ZERO FRONTEND CALCULATIONS]                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-PRODUCTION-GRADE | BILLION-DOLLAR ENTERPRISE SOFTWARE | BIBLICAL WORTH COMPLIANT                                       ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/dashboardService.js                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Mandated pure data rendering from frozen backend kernel contracts.                                 ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Built resilient fetch and event-stream adapters for FG217.                                  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

/**
 * @function fetchDashboardContract
 * @description Retrieves the unified 12-part authoritative dashboard state contract from the Kernel.
 * @returns {Promise<Object>} Authoritative dashboard state payload.
 * @throws {Error} If the HTTP request fails or contract is malformed.
 * @collaboration Guarantees single-source-of-truth telemetry for all console panels.
 */
export async function fetchDashboardContract() {
  const response = await fetch('/api/v1/dashboard', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'X-Sovereign-Client': 'Wilsy-OS-Executive-Console'
    }
  });

  if (!response.ok) {
    throw new Error(`Failed to retrieve dashboard contract: ${response.statusText}`);
  }

  const json = await response.json();
  if (!json.success || !json.data) {
    throw new Error('Invalid dashboard contract payload returned by kernel.');
  }

  return json.data;
}
