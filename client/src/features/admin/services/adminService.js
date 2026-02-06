/**
 * File: client/src/features/admin/services/adminService.js
 * PATH: client/src/features/admin/services/adminService.js
 * STATUS: GOD-TIER | NERVOUS SYSTEM | PRODUCTION-READY
 * VERSION: 10.1.0
 * -----------------------------------------------------------------------------
 * PURPOSE
 * - The "Cortex" of the Admin Dashboard for Wilsy OS.
 * - Engineered specifically for South African Legal Firms (High Court Compliance).
 * - Manages communication with the Sovereign Control Plane.
 * - Handles caching, tracing, telemetry, and error normalization.
 *
 * ARCHITECTURAL SUPREMACY
 * 1. DISTRIBUTED TRACING: Injects 'X-Correlation-ID' for end-to-end legal auditing.
 * 2. CIRCUIT BREAKER: Prevents cascading failures in the Sovereign Control Plane.
 * 3. REQUEST COLLAPSING: Prevents "Thundering Herd" on dashboard metrics.
 * 4. LEGAL-GRADE TELEMETRY: Automatic latency warnings for UX preservation.
 * 5. RESPONSE UNWRAPPING: Uniform data extraction for clean frontend consumption.
 *
 * COLLABORATION
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - INTEGRATION: AuditService (Telemetry), AuthStore (Identity), LegalLog (Compliance)
 * -----------------------------------------------------------------------------
 * EPITOME:
 * Biblical worth billions no child's place.
 */

'use strict';

import AuditService from '../../auth/services/AuditService';

// --- SYSTEM CONFIGURATION ---
const API_ROOT = process.env.REACT_APP_API_URL || '/api/admin';

const CONFIG = {
  TIMEOUT_DEFAULT: 12000, // Adjusted for SA Network Latency
  TIMEOUT_LONG: 120000,   // 2 Minutes for massive Legal Doc exports
  RETRIES: 3,             // Aggressive retry for unstable connections
  BACKOFF: 500,           // Initial backoff in ms
  LATENCY_WARN_THRESHOLD: 1200, // Warn if request exceeds 1.2s
  MAX_CACHE_ITEMS: 150,
  CIRCUIT_BREAKER_THRESHOLD: 5  // Failures before tripping
};

/* ---------------------------------------------------------------------------
   1. SOVEREIGN CACHE LAYER (LRU & Request Collapsing)
   --------------------------------------------------------------------------- */
class SovereignCache {
  constructor(limit = CONFIG.MAX_CACHE_ITEMS) {
    this.limit = limit;
    this.map = new Map();
    this.pendingRequests = new Map(); // For Request Collapsing
  }

  get(key) {
    const item = this.map.get(key);
    if (!item) return null;
    if (Date.now() > item.expiry) {
      this.map.delete(key);
      return null;
    }
    return item.value;
  }

  set(key, value, ttl = 15000) {
    if (this.map.size >= this.limit) {
      const firstKey = this.map.keys().next().value;
      this.map.delete(firstKey);
    }
    this.map.set(key, { value, expiry: Date.now() + ttl });
  }

  /**
   * collapse
   * - Prevents multiple identical requests from hitting the network simultaneously.
   */
  async collapse(key, requestFn) {
    if (this.pendingRequests.has(key)) {
      return this.pendingRequests.get(key);
    }
    const promise = requestFn().finally(() => this.pendingRequests.delete(key));
    this.pendingRequests.set(key, promise);
    return promise;
  }

  clear() {
    this.map.clear();
    this.pendingRequests.clear();
  }
}

const apiCache = new SovereignCache();

/* ---------------------------------------------------------------------------
   2. CIRCUIT BREAKER (Stability Pattern)
   --------------------------------------------------------------------------- */
class CircuitBreaker {
  constructor() {
    this.failures = 0;
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    this.lastFailureTime = null;
  }

  onSuccess() {
    this.failures = 0;
    this.state = 'CLOSED';
  }

  onFailure() {
    this.failures++;
    if (this.failures >= CONFIG.CIRCUIT_BREAKER_THRESHOLD) {
      this.state = 'OPEN';
      this.lastFailureTime = Date.now();
    }
  }

  canRequest() {
    if (this.state === 'OPEN') {
      const now = Date.now();
      if (now - this.lastFailureTime > 30000) { // 30s cooldown
        this.state = 'HALF_OPEN';
        return true;
      }
      return false;
    }
    return true;
  }
}

const breaker = new CircuitBreaker();

/* ---------------------------------------------------------------------------
   3. THE CORE NETWORK ENGINE (Secure Transaction Layer)
   --------------------------------------------------------------------------- */

/**
 * generateCorrelationID
 * - Essential for Legal Audits in South African Law Firms.
 * - Links a specific user action to a server-side log entry.
 */
const generateCorrelationID = () => {
  if (crypto.randomUUID) return crypto.randomUUID();
  return `wilsy-trace-${Date.now()}-${Math.random().toString(36).substring(2, 15)}`;
};

/**
 * secureSovereignFetch
 * - The ultimate wrapper for Wilsy OS network communication.
 */
async function secureSovereignFetch(endpoint, options = {}) {
  const {
    method = 'GET',
    body = null,
    token = null,
    timeout = CONFIG.TIMEOUT_DEFAULT,
    isBlob = false,
    bypassCache = false
  } = options;

  if (!breaker.canRequest()) {
    throw new Error('SYSTEM_CIRCUIT_TRIPPED: Sovereign Control Plane is under high stress.');
  }

  const traceId = generateCorrelationID();
  const startTime = performance.now();

  // 1. Forensic Headers
  const headers = {
    'Accept': 'application/json',
    'X-Correlation-ID': traceId,
    'X-Wilsy-Platform': 'OS_ADMIN',
    'X-Legal-Region': 'ZA_SADC', // South Africa / SADC Compliance
    'X-Client-Timestamp': new Date().toISOString()
  };

  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (body && !(body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  let attempt = 0;

  // 2. Resilience Execution Loop
  while (attempt <= CONFIG.RETRIES) {
    attempt++;
    const controller = new AbortController();
    const abortId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(`${API_ROOT}${endpoint}`, {
        method,
        headers,
        body: body ? (body instanceof FormData ? body : JSON.stringify(body)) : null,
        signal: controller.signal
      });

      clearTimeout(abortId);
      breaker.onSuccess();

      // 3. Performance Telemetry
      const duration = Math.round(performance.now() - startTime);
      if (duration > CONFIG.LATENCY_WARN_THRESHOLD) {
        AuditService.log('PERFORMANCE_DEGRADATION', {
          severity: 'WARN',
          metadata: { endpoint, duration, traceId, node: 'ZA_JHB_PRODUCTION' }
        });
      }

      // 4. Critical Status Handlers
      if (response.status === 401) {
        // Broad-spectrum logout logic would be triggered here
        throw new Error('SOVEREIGN_AUTH_EXPIRED');
      }

      if (response.status === 403) {
        throw new Error('SOVEREIGN_ACCESS_DENIED: Level 1 Clearance Required');
      }

      // 5. Retry Logic for 5xx
      if (!response.ok && response.status >= 500 && attempt <= CONFIG.RETRIES) {
        const jitter = Math.random() * 200;
        const wait = CONFIG.BACKOFF * Math.pow(2, attempt) + jitter;
        await new Promise(r => setTimeout(r, wait));
        continue;
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `System Error: ${response.status}`);
      }

      // 6. Data Streaming (For Legal Documentation Exports)
      if (isBlob) return await response.blob();

      // 7. Uniform Unwrapping
      const result = await response.json();
      return result.data !== undefined ? result.data : result;

    } catch (err) {
      clearTimeout(abortId);

      if (err.name === 'AbortError') {
        err.message = 'NETWORK_TIMEOUT: Control plane did not respond in time.';
      }

      if (attempt > CONFIG.RETRIES) {
        breaker.onFailure();

        // Log Forensic Failure
        AuditService.log('SOVEREIGN_COMM_FAILURE', {
          severity: 'CRITICAL',
          metadata: { error: err.message, traceId, endpoint }
        });

        throw err;
      }

      // Exponential Backoff before next attempt
      await new Promise(r => setTimeout(r, CONFIG.BACKOFF * attempt));
    }
  }
}

/* ---------------------------------------------------------------------------
   4. SERVICE INTERFACE EXPORTS
   --------------------------------------------------------------------------- */

const AdminService = {

  // --- ANALYTICS & STATS ---

  /**
   * getDashboardMetrics
   * - Unified stats for Legal Firm performance.
   * - Uses Request Collapsing to prevent duplicate hits.
   */
  async getDashboardMetrics(token) {
    if (!token) throw new Error('IDENTITY_REQUIRED');

    const cacheKey = 'dashboard_metrics';
    const cached = apiCache.get(cacheKey);
    if (cached) return cached;

    return await apiCache.collapse(cacheKey, async () => {
      const data = await secureSovereignFetch('/dashboard/metrics', { token });
      apiCache.set(cacheKey, data, 30000); // 30s TTL for metrics
      return data;
    });
  },

  // --- TENANT (LAW FIRM) GOVERNANCE ---

  async getLawFirms(token, filters = {}) {
    const qs = new URLSearchParams(filters).toString();
    return await secureSovereignFetch(`/tenants?${qs}`, { token });
  },

  async onboardNewFirm(payload, token) {
    const data = await secureSovereignFetch('/tenants', {
      method: 'POST',
      body: payload,
      token
    });
    apiCache.clear();
    return data;
  },

  async updateFirmSubscription(firmId, planId, token) {
    return await secureSovereignFetch(`/tenants/${firmId}/billing`, {
      method: 'PATCH',
      body: { planId },
      token
    });
  },

  async toggleFirmStatus(firmId, status, reason, token) {
    return await secureSovereignFetch(`/tenants/${firmId}/status`, {
      method: 'PUT',
      body: { status, reason },
      token
    });
  },

  // --- USER & LEGAL REPRESENTATIVE DIRECTORY ---

  async getAllUsers(token, params = {}) {
    const { page = 1, limit = 20, search = '', role = '' } = params;
    const qs = new URLSearchParams({ page, limit, q: search, role }).toString();

    return await secureSovereignFetch(`/users?${qs}`, { token });
  },

  async provisionAdmin(payload, token) {
    return await secureSovereignFetch('/users/provision', {
      method: 'POST',
      body: payload,
      token
    });
  },

  async updatePermissions(userId, permissions, token) {
    return await secureSovereignFetch(`/users/${userId}/permissions`, {
      method: 'PATCH',
      body: { permissions },
      token
    });
  },

  async expungeUser(userId, token) {
    // Permanent deletion for compliance with POPIA (Protection of Personal Information Act)
    return await secureSovereignFetch(`/users/${userId}/expunge`, {
      method: 'DELETE',
      token
    });
  },

  // --- FORENSICS, AUDITS & POPIA COMPLIANCE ---

  /**
   * fetchForensicRegistry
   * - Retrieves the immutable audit ledger.
   */
  async fetchForensicRegistry(token, criteria = {}) {
    const qs = new URLSearchParams(criteria).toString();
    return await secureSovereignFetch(`/audits/forensics?${qs}`, { token });
  },

  /**
   * downloadLegalExport
   * - High-capacity blob stream for Court documents or full Audit Logs.
   */
  async downloadLegalExport(token, exportId, format = 'PDF') {
    return await secureSovereignFetch(`/exports/${exportId}?format=${format}`, {
      token,
      isBlob: true,
      timeout: CONFIG.TIMEOUT_LONG
    });
  },

  // --- INFRASTRUCTURE & HEALTH ---

  async checkNodeHealth(token) {
    return await secureSovereignFetch('/system/health', { token, timeout: 5000 });
  },

  /**
   * rotateSystemKeys
   * - Rotates encryption keys for the Wilsy OS vault.
   */
  async rotateSystemKeys(token) {
    return await secureSovereignFetch('/system/security/rotate-keys', {
      method: 'POST',
      token
    });
  },

  // --- EMERGENCY PROTOCOLS ---

  /**
   * initiateProtocolZero
   * - Total Lockdown: Freezes all Law Firm access in case of a breach.
   */
  async initiateProtocolZero(token, secretKey) {
    return await secureSovereignFetch('/emergency/lockdown', {
      method: 'POST',
      body: { auth_verification: secretKey },
      token,
      timeout: CONFIG.TIMEOUT_LONG
    });
  }
};

export default AdminService;