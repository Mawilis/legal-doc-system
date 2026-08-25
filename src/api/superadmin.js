/**
 * @file superadmin.js
 * @description Wilsy OS Citadel - SuperAdmin API Gateway Client
 * @author Wilson Khanyezi (Founder & Architect, Wilsy (Pty) Ltd)
 * @version 55.1.0-MARS-BIBLICAL
 * @copyright 2026 Wilsy Global Enterprise. All rights reserved.
 * 
 * BIBLICAL WORTH BILLIONS COMPLIANCE:
 * - Unyielding error handling with explicit status code and message extraction.
 * - Zero undefined error messages; fully resilient against malformed gateway payloads.
 * - Production-grade asynchronous fetch wrappers with authorization token injection.
 */

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api/v1/superadmin';

/**
 * Helper to retrieve authorization headers for sovereign citadel requests.
 * @returns {Headers} Configured Headers object.
 */
function getSovereignHeaders() {
    const token = localStorage.getItem('wilsy_auth_token') || '';
    return new Headers({
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'X-Wilsy-Protocol': 'Mars-Sovereign-v55'
    });
}

/**
 * Fetches global citadel statistics and multi-tenant valuation aggregate.
 * @async
 * @returns {Promise<Object>} Global telemetry and financial metrics.
 * @throws {Error} Detailed error message with HTTP status if request fails.
 */
export async function getGlobalStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`, {
            method: 'GET',
            headers: getSovereignHeaders()
        });

        if (!response.ok) {
            let errorDetail = response.statusText || 'Unknown Gateway Fault';
            try {
                const errorJson = await response.json();
                errorDetail = errorJson.message || errorDetail;
            } catch (e) {
                // Fallback if response is not JSON
            }
            throw new Error(`Failed to fetch global stats (${response.status}): ${errorDetail}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('[Wilsy Citadel API] getGlobalStats error:', error);
        throw error;
    }
}

/**
 * Retrieves the complete enterprise tenant and firm registry for sovereign management.
 * @async
 * @returns {Promise<Array>} List of registered tenant firms.
 * @throws {Error} Detailed error message if registry fetch fails.
 */
export async function getFirms() {
    try {
        const response = await fetch(`${API_BASE_URL}/firms`, {
            method: 'GET',
            headers: getSovereignHeaders()
        });

        if (!response.ok) {
            let errorDetail = response.statusText || 'Registry Unavailable';
            try {
                const errorJson = await response.json();
                errorDetail = errorJson.message || errorDetail;
            } catch (e) {
                // Fallback if response is not JSON
            }
            throw new Error(`Failed to fetch firms registry (${response.status}): ${errorDetail}`);
        }

        const data = await response.json();
        return data.firms || data;
    } catch (error) {
        console.error('[Wilsy Citadel API] getFirms error:', error);
        throw error;
    }
}
