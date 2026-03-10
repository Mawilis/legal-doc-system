/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ ████████╗███████╗███████╗████████╗███████╗                               ║
  ║ ╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝██╔════╝                               ║
  ║    ██║   █████╗  ███████╗   ██║   ███████╗                               ║
  ║    ██║   ██╔══╝  ╚════██║   ██║   ╚════██║                               ║
  ║    ██║   ███████╗███████║   ██║   ███████║                               ║
  ║    ╚═╝   ╚══════╝╚══════╝   ╚═╝   ╚══════╝                               ║
  ║                                                                           ║
  ║  🏛️  WILSY OS 2050 - TENANT MANAGEMENT TEST SUITE v10.0                  ║
  ║  ├─ Tests multi-tenant operations at scale                                ║
  ║  ├─ Validates CIPC compliance and POPIA redaction                        ║
  ║  └─ Fixed auditLogger mocks for all tests                                ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useTenantManagement, MOCK_TENANTS } from '../../src/hooks/useTenantManagement.js';
import { superAdminAPI } from '../../src/api/superadmin.js';

// Mock superAdminAPI
vi.mock('../../src/api/superadmin.js', () => ({
  superAdminAPI: {
    getTenants: vi.fn(),
    createTenant: vi.fn(),
    updateTenant: vi.fn(),
    suspendTenant: vi.fn()
  }
}));

// Mock auditLogger properly
vi.mock('../../src/utils/auditLogger.js', () => ({
  auditLogger: {
    log: vi.fn(),
    AuditLevel: {
      INFO: 'INFO',
      AUDIT: 'AUDIT',
      ERROR: 'ERROR',
      WARN: 'WARN',
      DEBUG: 'DEBUG',
      CRITICAL: 'CRITICAL',
      FORENSIC: 'FORENSIC'
    }
  }
}));


// Suppress React 18 act() and render warnings for cleaner forensic output
const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    if (/Warning.*not wrapped in act/.test(args[0])) return;
    if (/Warning.*ReactDOM\.render is no longer supported/.test(args[0])) return;
    if (/Warning.*unmountComponentAtNode is deprecated/.test(args[0])) return;
    originalError.call(console, ...args);
  };
});
afterAll(() => {
  console.error = originalError;
});

describe('useTenantManagement - 10/10 Production Suite', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock successful API responses
    superAdminAPI.getTenants.mockResolvedValue({ 
      data: MOCK_TENANTS,
      total: MOCK_TENANTS.length 
    });
    superAdminAPI.createTenant.mockImplementation((data) => 
      Promise.resolve({ data: { id: `new-${Date.now()}`, ...data } })
    );
    superAdminAPI.updateTenant.mockImplementation((id, data) => 
      Promise.resolve({ data: { id, ...data } })
    );
    superAdminAPI.suspendTenant.mockResolvedValue({ success: true });
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  // ==========================================================================
  // TEST GROUP 1: Initialization
  // ==========================================================================
  describe('Initialization', () => {
    it('loads tenants on mount', async () => {
      const { result } = renderHook(() => useTenantManagement());
      
      expect(result.current.loading).toBe(true);
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      expect(result.current.tenants).toEqual(MOCK_TENANTS);
      expect(result.current.pagination.total).toBe(MOCK_TENANTS.length);
    });

    it('handles API failure gracefully with fallback', async () => {
      superAdminAPI.getTenants.mockRejectedValue(new Error('Network error'));
      
      const { result } = renderHook(() => useTenantManagement());
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      expect(result.current.error).toBeDefined();
      expect(result.current.tenants).toEqual(MOCK_TENANTS); // Fallback data
    });
  });

  // ==========================================================================
  // TEST GROUP 2: Tenant ID Validation
  // ==========================================================================
  describe('Tenant ID Validation', () => {
    it('validates CIPC registration numbers correctly', () => {
      const { result } = renderHook(() => useTenantManagement());
      
      // Valid CIPC formats
      expect(result.current.validateCIPCRegistration('2001/012345/21')).toBe(true);
      expect(result.current.validateCIPCRegistration('1998/045678/23')).toBe(true);
      expect(result.current.validateCIPCRegistration('2024/123456/07')).toBe(true);
      
      // Invalid formats
      expect(result.current.validateCIPCRegistration('2001/12345/21')).toBe(false);
      expect(result.current.validateCIPCRegistration('99/123456/21')).toBe(false);
      expect(result.current.validateCIPCRegistration('2001/1234567/21')).toBe(false);
      expect(result.current.validateCIPCRegistration('')).toBe(false);
      expect(result.current.validateCIPCRegistration(null)).toBe(false);
    });

    it('validates internal tenant IDs correctly', () => {
      const { result } = renderHook(() => useTenantManagement());
      
      expect(result.current.validateTenantId('dentons-001')).toBe(true);
      expect(result.current.validateTenantId('tenant-12345678')).toBe(true);
      expect(result.current.validateTenantId('ABC123XYZ')).toBe(true);
      expect(result.current.validateTenantId('short')).toBe(false);
      expect(result.current.validateTenantId('')).toBe(false);
      expect(result.current.validateTenantId(null)).toBe(false);
    });
  });

  // ==========================================================================
  // TEST GROUP 3: Get Single Tenant
  // ==========================================================================
  describe('Get Tenant', () => {
    it('fetches a single tenant by ID', async () => {
      superAdminAPI.getTenants.mockResolvedValue({ 
        data: [MOCK_TENANTS[0]] 
      });
      
      const { result } = renderHook(() => useTenantManagement());
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      let tenant;
      await act(async () => {
        tenant = await result.current.getTenant('dentons-001');
      });
      
      expect(tenant).toBeDefined();
      expect(tenant.id).toBe('dentons-001');
      expect(tenant.name).toBe('Dentons South Africa');
    });

    it('redacts PII when fetching tenant', async () => {
      superAdminAPI.getTenants.mockResolvedValue({ 
        data: [MOCK_TENANTS[0]] 
      });
      
      const { result } = renderHook(() => useTenantManagement());
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      let tenant;
      await act(async () => {
        tenant = await result.current.getTenant('dentons-001');
      });
      
      expect(tenant.contactInfo).toBeUndefined();
    });

    it('throws error for invalid tenant ID', async () => {
      const { result } = renderHook(() => useTenantManagement());
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      await expect(result.current.getTenant('')).rejects.toThrow('Tenant ID is required');
      await expect(result.current.getTenant(null)).rejects.toThrow('Tenant ID is required');
    });
  });

  // ==========================================================================
  // TEST GROUP 4: Create Tenant
  // ==========================================================================
  describe('Create Tenant', () => {
    it('creates a new tenant successfully', async () => {
      const { result } = renderHook(() => useTenantManagement());
      const newTenant = {
        name: 'New Law Firm',
        registration: '2024/123456/07',
        plan: 'Professional',
        jurisdiction: 'ZA'
      };
      
      superAdminAPI.createTenant.mockResolvedValue({ 
        data: { id: 'new-123', ...newTenant } 
      });
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      let createResult;
      await act(async () => {
        createResult = await result.current.createTenant(newTenant);
      });
      
      expect(createResult.success).toBe(true);
      expect(createResult.data).toMatchObject(newTenant);
    });

    it('handles creation failure', async () => {
      superAdminAPI.createTenant.mockRejectedValue(new Error('Duplicate registration'));
      
      const { result } = renderHook(() => useTenantManagement());
      const newTenant = { name: 'New Firm' };
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      let createResult;
      await act(async () => {
        createResult = await result.current.createTenant(newTenant);
      });
      
      expect(createResult.success).toBe(false);
      expect(createResult.error).toBeDefined();
    });
  });

  // ==========================================================================
  // TEST GROUP 5: Update Tenant
  // ==========================================================================
  describe('Update Tenant', () => {
    it('updates an existing tenant', async () => {
      const { result } = renderHook(() => useTenantManagement());
      const updates = { name: 'Updated Firm Name', plan: 'Ultra' };
      
      superAdminAPI.updateTenant.mockResolvedValue({ 
        data: { id: 'dentons-001', ...updates } 
      });
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      let updateResult;
      await act(async () => {
        updateResult = await result.current.updateTenant('dentons-001', updates);
      });
      
      expect(updateResult.success).toBe(true);
      expect(updateResult.data).toMatchObject(updates);
    });

    it('throws error when updating without ID', async () => {
      const { result } = renderHook(() => useTenantManagement());
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      await expect(result.current.updateTenant(null, {})).rejects.toThrow(
        'Tenant ID is required'
      );
    });
  });

  // ==========================================================================
  // TEST GROUP 6: Suspend Tenant
  // ==========================================================================
  describe('Suspend Tenant', () => {
    it('suspends a tenant', async () => {
      const { result } = renderHook(() => useTenantManagement());
      
      superAdminAPI.suspendTenant.mockResolvedValue({ success: true });
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      let suspendResult;
      await act(async () => {
        suspendResult = await result.current.suspendTenant('dentons-001', 'Non-compliance');
      });
      
      expect(suspendResult.success).toBe(true);
    });

    it('handles suspension failure', async () => {
      superAdminAPI.suspendTenant.mockRejectedValue(new Error('Tenant not found'));
      
      const { result } = renderHook(() => useTenantManagement());
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      let suspendResult;
      await act(async () => {
        suspendResult = await result.current.suspendTenant('invalid-id');
      });
      
      expect(suspendResult.success).toBe(false);
      expect(suspendResult.error).toBeDefined();
    });
  });

  // ==========================================================================
  // TEST GROUP 7: Compliance Checking
  // ==========================================================================
  describe('Compliance Checking', () => {
    it('checks tenant compliance', async () => {
      const { result } = renderHook(() => useTenantManagement());
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      let compliance;
      await act(async () => {
        compliance = await result.current.checkCompliance('dentons-001');
      });
      
      expect(compliance).toBeDefined();
      expect(compliance.compliant).toBe(true);
      expect(compliance.score).toBeGreaterThanOrEqual(95);
      expect(compliance.score).toBeLessThanOrEqual(100);
    });

    it('throws error when checking compliance without ID', async () => {
      const { result } = renderHook(() => useTenantManagement());
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      await expect(result.current.checkCompliance()).rejects.toThrow('Tenant ID is required');
    });
  });

  // ==========================================================================
  // TEST GROUP 8: Filtering and Pagination
  // ==========================================================================
  describe('Filtering and Pagination', () => {
    it('applies filters and resets page', async () => {
      const { result } = renderHook(() => useTenantManagement());
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      act(() => {
        result.current.applyFilters({ status: 'Active', plan: 'Enterprise' });
      });
      
      expect(result.current.filters).toEqual({
        status: 'Active',
        plan: 'Enterprise'
      });
      expect(result.current.pagination.page).toBe(1);
    });

    it('changes page', async () => {
      const { result } = renderHook(() => useTenantManagement());
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      act(() => {
        result.current.changePage(3);
      });
      
      expect(result.current.pagination.page).toBe(3);
    });
  });

  // ==========================================================================
  // TEST GROUP 9: Aggregate Metrics
  // ==========================================================================
  describe('Aggregate Metrics', () => {
    it('calculates total active tenants correctly', async () => {
      const { result } = renderHook(() => useTenantManagement());
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      expect(result.current.totalActiveTenants).toBe(7);
    });

    it('calculates total revenue correctly', async () => {
      const { result } = renderHook(() => useTenantManagement());
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      const expectedRevenue = MOCK_TENANTS.reduce((sum, t) => sum + (t.revenue || 0), 0);
      expect(result.current.totalRevenue).toBe(expectedRevenue);
    });

    it('calculates compliance rate correctly', async () => {
      const { result } = renderHook(() => useTenantManagement());
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      expect(result.current.complianceRate).toBe(87.5);
    });
  });

  // ==========================================================================
  // TEST GROUP 10: Clear Selected
  // ==========================================================================
  describe('Clear Selected', () => {
    it('clears selected tenant', async () => {
      superAdminAPI.getTenants.mockResolvedValue({ 
        data: [MOCK_TENANTS[0]] 
      });
      
      const { result } = renderHook(() => useTenantManagement());
      
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
      
      await act(async () => {
        await result.current.getTenant('dentons-001');
      });
      
      expect(result.current.selectedTenant).toBeDefined();
      
      act(() => {
        result.current.clearSelected();
      });
      
      expect(result.current.selectedTenant).toBeNull();
    });
  });
});
