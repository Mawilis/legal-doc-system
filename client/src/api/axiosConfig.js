/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN AXIOS CONFIGURATION [V29.0.0-OMEGA]                                                                               ║
 * ║ [AUTOMATED FORENSIC SEALING | IDENTITY ANCHORING | BILLION DOLLAR SPEC]                                                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 29.0.0-OMEGA | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                        ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                        ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/api/axiosConfig.js                                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🛠️ FUNCTIONAL LOGIC:                                                                                                                   ║
 * ║ 1. Automated Sealing: Generates SHA3-512 seal for every strike to satisfy requireSovereignAuth.                                         ║
 * ║ 2. Identity Injection: Persists JWT and Tenant ID from localStorage into outbound headers.                                             ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import axios from 'axios';
import CryptoJS from 'crypto-js';
import { v4 as uuidv4 } from 'uuid';
import { getClientApiBaseUrl, getClientApiTimeout } from '../config/environment.js';

const apiClient = axios.create({
  baseURL: getClientApiBaseUrl(),
  timeout: getClientApiTimeout(),
  headers: {
    'Content-Type': 'application/json',
    'X-Institutional-Finality': 'TRUE'
  }
});

/**
 * 🛡️ REQUEST INTERCEPTOR: FORENSIC SIGNING
 * Generates the Sovereign DNA required for Master Core validation.
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('wilsy_auth_token');
    const tenantId = localStorage.getItem('wilsy_tenant_id') || 'WILSY_SOVEREIGN_ROOT';

    // 🧬 1. Generate Forensic Meta
    const requestId = uuidv4();
    const timestamp = new Date().toISOString();
    const nonce = CryptoJS.lib.WordArray.random(16).toString();

    // 🧬 2. Compute SHA3-512 Seal
    // We sign the payload (body) or an empty object if it's a GET request
    const payload = config.data || {};
    const message = `${requestId}|${timestamp}|${JSON.stringify(payload)}|${nonce}`;
    const seal = CryptoJS.SHA3(message, { outputLength: 512 }).toString();

    // 🧬 3. Inject Headers
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    config.headers['X-Tenant-ID'] = tenantId;
    config.headers['X-Request-ID'] = requestId;
    config.headers['X-Forensic-Timestamp'] = timestamp;
    config.headers['X-Cryptographic-Nonce'] = nonce;
    config.headers['X-Request-Seal'] = seal;
    config.headers['X-Sovereign-Version'] = '29.0.0-OMEGA';

    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 403) {
      console.error('[SECURITY] 🚨 Forensic Seal Rejected. Check client-server clock sync.');
    }
    return Promise.reject(error);
  }
);

export default apiClient;
