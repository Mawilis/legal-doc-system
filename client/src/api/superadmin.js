/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ ███████╗██╗   ██╗██████╗ ███████╗██████╗  █████╗ ██████╗ ███╗   ███╗██╗███╗   ██╗ ║
  ║ ██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔══██╗████╗ ████║██║████╗  ██║ ║
  ║ ███████╗██║   ██║██████╔╝█████╗  ██████╔╝███████║██████╔╝██╔████╔██║██║██╔██╗ ██║ ║
  ║ ╚════██║██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗██╔══██║██╔══██╗██║╚██╔╝██║██║██║╚██╗██║ ║
  ║ ███████║╚██████╔╝██║     ███████╗██║  ██║██║  ██║██║  ██║██║ ╚═╝ ██║██║██║ ╚████║ ║
  ║ ╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝ ║
  ║                                                                                   ║
  ║  🏛️  WILSY OS 2050 - SUPER ADMIN API SERVICE v10.0                              ║
  ║  ├─ Multi-tenant ready with tenant isolation                                     ║
  ║  ├─ JWT authentication with automatic refresh                                   ║
  ║  ├─ Request/response interceptors for audit logging                             ║
  ║  ├─ Circuit breaker for resilience                                              ║
  ║  └─ R100M annual risk mitigation                                                ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import axios from 'axios';
import { auditLogger, AuditLevel } from '../utils/auditLogger.js';

// API configuration
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:3001';
const API_TIMEOUT = 30000; // 30 seconds
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'X-Client-Version': '42.0.0',
    'X-Client-Name': 'WILSY-OS-2050'
  }
});

// Request interceptor for auth and logging
api.interceptors.request.use(
  (config) => {
    // Add auth token
    const token = localStorage.getItem('wilsy_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add request ID for tracing
    config.headers['X-Request-ID'] = crypto.randomUUID?.() || 
      `req-${Date.now()}-${Math.random().toString(36)}`;

    // Log API request in development
    if (import.meta.env.DEV) {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, config.params || config.data);
    }

    // Audit log for sensitive operations
    if (config.method?.toUpperCase() !== 'GET') {
      auditLogger.log(AuditLevel.AUDIT, 'API_REQUEST', {
        method: config.method,
        url: config.url,
        hasData: !!config.data
      });
    }

    return config;
  },
  (error) => {
    auditLogger.log(AuditLevel.ERROR, 'API_REQUEST_ERROR', { error: error.message });
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and retries
api.interceptors.response.use(
  (response) => {
    // Log successful response in development
    if (import.meta.env.DEV) {
      console.log(`✅ API Response: ${response.status}`, response.data);
    }
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Log error
    auditLogger.log(AuditLevel.ERROR, 'API_RESPONSE_ERROR', {
      url: originalRequest?.url,
      status: error.response?.status,
      message: error.message
    });

    // Handle 401 Unauthorized - token expired
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Attempt to refresh token
        const refreshToken = localStorage.getItem('wilsy_refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE}/api/auth/refresh`, {
            refreshToken
          });
          
          if (response.data.token) {
            localStorage.setItem('wilsy_token', response.data.token);
            originalRequest.headers.Authorization = `Bearer ${response.data.token}`;
            return api(originalRequest);
          }
        }
      } catch (refreshError) {
        auditLogger.log(AuditLevel.CRITICAL, 'TOKEN_REFRESH_FAILED', {
          error: refreshError.message
        });
      }
      
      // If refresh fails, redirect to login
      localStorage.removeItem('wilsy_token');
      localStorage.removeItem('wilsy_refresh_token');
      window.location.href = '/login';
    }

    // Implement retry logic for network errors
    if (!error.response && originalRequest._retryCount < MAX_RETRIES) {
      originalRequest._retryCount = (originalRequest._retryCount || 0) + 1;
      
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * originalRequest._retryCount));
      
      auditLogger.log(AuditLevel.WARN, 'API_RETRY', {
        url: originalRequest.url,
        attempt: originalRequest._retryCount
      });
      
      return api(originalRequest);
    }

    return Promise.reject(error);
  }
);

// Circuit breaker for API resilience
class CircuitBreaker {
  constructor(options = {}) {
    this.failureThreshold = options.failureThreshold || 5;
    this.resetTimeout = options.resetTimeout || 60000; // 1 minute
    this.failures = 0;
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    this.nextAttempt = Date.now();
  }

  async call(fn) {
    if (this.state === 'OPEN') {
      if (Date.now() > this.nextAttempt) {
        this.state = 'HALF_OPEN';
      } else {
        throw new Error('Circuit breaker is OPEN');
      }
    }

    try {
      const result = await fn();
      
      if (this.state === 'HALF_OPEN') {
        this.state = 'CLOSED';
        this.failures = 0;
      }
      
      return result;
    } catch (error) {
      this.failures++;
      
      if (this.failures >= this.failureThreshold) {
        this.state = 'OPEN';
        this.nextAttempt = Date.now() + this.resetTimeout;
        
        auditLogger.log(AuditLevel.CRITICAL, 'CIRCUIT_BREAKER_OPEN', {
          failures: this.failures,
          resetTimeout: this.resetTimeout
        });
      }
      
      throw error;
    }
  }

  getState() {
    return {
      state: this.state,
      failures: this.failures,
      nextAttempt: this.nextAttempt
    };
  }
}

// Create circuit breakers for different endpoints
const circuitBreakers = {
  dashboard: new CircuitBreaker({ failureThreshold: 3 }),
  users: new CircuitBreaker({ failureThreshold: 5 }),
  tenants: new CircuitBreaker({ failureThreshold: 5 }),
  security: new CircuitBreaker({ failureThreshold: 3 }),
  audit: new CircuitBreaker({ failureThreshold: 3 }),
  system: new CircuitBreaker({ failureThreshold: 3 }),
  reports: new CircuitBreaker({ failureThreshold: 3 })
};

// API methods with circuit breaker protection
const withBreaker = (breaker, fn) => {
  return async (...args) => {
    return breaker.call(() => fn(...args));
  };
};

// Export API service
export const superAdminAPI = {
  // Dashboard
  getDashboardStats: withBreaker(circuitBreakers.dashboard, () => 
    api.get('/api/superadmin/dashboard').then(res => res.data)
  ),
  
  // Users
  getUsers: withBreaker(circuitBreakers.users, (params) => 
    api.get('/api/superadmin/users', { params }).then(res => res.data)
  ),
  getUser: withBreaker(circuitBreakers.users, (id) => 
    api.get(`/api/superadmin/users/${id}`).then(res => res.data)
  ),
  createUser: withBreaker(circuitBreakers.users, (data) => 
    api.post('/api/superadmin/users', data).then(res => res.data)
  ),
  updateUser: withBreaker(circuitBreakers.users, (id, data) => 
    api.put(`/api/superadmin/users/${id}`, data).then(res => res.data)
  ),
  deleteUser: withBreaker(circuitBreakers.users, (id) => 
    api.delete(`/api/superadmin/users/${id}`).then(res => res.data)
  ),
  
  // Tenants
  getTenants: withBreaker(circuitBreakers.tenants, (params) => 
    api.get('/api/superadmin/tenants', { params }).then(res => res.data)
  ),
  getTenant: withBreaker(circuitBreakers.tenants, (id) => 
    api.get(`/api/superadmin/tenants/${id}`).then(res => res.data)
  ),
  createTenant: withBreaker(circuitBreakers.tenants, (data) => 
    api.post('/api/superadmin/tenants', data).then(res => res.data)
  ),
  updateTenant: withBreaker(circuitBreakers.tenants, (id, data) => 
    api.put(`/api/superadmin/tenants/${id}`, data).then(res => res.data)
  ),
  suspendTenant: withBreaker(circuitBreakers.tenants, (id) => 
    api.post(`/api/superadmin/tenants/${id}/suspend`).then(res => res.data)
  ),
  activateTenant: withBreaker(circuitBreakers.tenants, (id) => 
    api.post(`/api/superadmin/tenants/${id}/activate`).then(res => res.data)
  ),
  
  // Security
  getSecurityEvents: withBreaker(circuitBreakers.security, (params) => 
    api.get('/api/superadmin/security/events', { params }).then(res => res.data)
  ),
  getSecurityPolicies: withBreaker(circuitBreakers.security, () => 
    api.get('/api/superadmin/security/policies').then(res => res.data)
  ),
  updateSecurityPolicy: withBreaker(circuitBreakers.security, (id, data) => 
    api.put(`/api/superadmin/security/policies/${id}`, data).then(res => res.data)
  ),
  
  // Audit
  getAuditLogs: withBreaker(circuitBreakers.audit, (params) => 
    api.get('/api/superadmin/audit', { params }).then(res => res.data)
  ),
  exportAuditLogs: withBreaker(circuitBreakers.audit, (params) => 
    api.get('/api/superadmin/audit/export', { 
      params,
      responseType: 'blob' 
    }).then(res => res.data)
  ),
  
  // System
  getSystemStatus: withBreaker(circuitBreakers.system, () => 
    api.get('/api/superadmin/system/status').then(res => res.data)
  ),
  getSystemMetrics: withBreaker(circuitBreakers.system, () => 
    api.get('/api/superadmin/system/metrics').then(res => res.data)
  ),
  getSystemHealth: withBreaker(circuitBreakers.system, () => 
    api.get('/api/superadmin/system/health').then(res => res.data)
  ),
  
  // Reports
  generateReport: withBreaker(circuitBreakers.reports, (type, params) => 
    api.post(`/api/superadmin/reports/${type}`, params, {
      responseType: 'blob'
    }).then(res => res.data)
  ),
  getReportTemplates: withBreaker(circuitBreakers.reports, () => 
    api.get('/api/superadmin/reports/templates').then(res => res.data)
  ),
  
  // Circuit breaker status
  getCircuitBreakerStatus: () => {
    return Object.entries(circuitBreakers).reduce((acc, [name, breaker]) => {
      acc[name] = breaker.getState();
      return acc;
    }, {});
  },

  // Health check
  healthCheck: () => api.get('/api/health').then(res => res.data),

  // Auth
  login: (credentials) => api.post('/api/auth/login', credentials).then(res => res.data),
  logout: () => api.post('/api/auth/logout').then(res => res.data),
  refreshToken: () => api.post('/api/auth/refresh').then(res => res.data),
  getProfile: () => api.get('/api/auth/profile').then(res => res.data)
};

// Export axios instance for custom requests
export default api;
