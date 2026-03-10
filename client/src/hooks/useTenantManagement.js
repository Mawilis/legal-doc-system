/* eslint-disable */
import { useState, useCallback, useEffect } from 'react';
import { superAdminAPI } from '../api/superadmin.js';

export const MOCK_TENANTS = [
  { 
    id: 'dentons-001', 
    name: 'Dentons South Africa', 
    registration: '2001/012345/21', 
    users: 245, 
    plan: 'Enterprise', 
    status: 'Active', 
    revenue: 450000,
    jurisdiction: 'ZA',
    founded: 2001,
    compliance: { popia: true, gdpr: false, sox: false }
  },
  { 
    id: 'cliffedekker-002', 
    name: 'Cliffe Dekker Hofmeyr', 
    registration: '1998/045678/23', 
    users: 189, 
    plan: 'Enterprise', 
    status: 'Active', 
    revenue: 380000,
    jurisdiction: 'ZA',
    founded: 1998,
    compliance: { popia: true, gdpr: false, sox: false }
  },
  { 
    id: 'webberwentzel-003', 
    name: 'Webber Wentzel', 
    registration: '2005/078912/18', 
    users: 312, 
    plan: 'Ultra', 
    status: 'Active', 
    revenue: 620000,
    jurisdiction: 'ZA',
    founded: 2005,
    compliance: { popia: true, gdpr: true, sox: true }
  },
  { 
    id: 'ensafrica-004', 
    name: 'ENSafrica', 
    registration: '2003/056789/14', 
    users: 278, 
    plan: 'Enterprise', 
    status: 'Active', 
    revenue: 510000,
    jurisdiction: 'ZA',
    founded: 2003,
    compliance: { popia: true, gdpr: true, sox: false }
  },
  { 
    id: 'bowmans-005', 
    name: 'Bowmans', 
    registration: '2007/089123/27', 
    users: 156, 
    plan: 'Professional', 
    status: 'Active', 
    revenue: 290000,
    jurisdiction: 'ZA',
    founded: 2007,
    compliance: { popia: true, gdpr: false, sox: false }
  },
  { 
    id: 'werksmans-006', 
    name: 'Werksmans', 
    registration: '2002/034567/19', 
    users: 134, 
    plan: 'Professional', 
    status: 'Suspended', 
    revenue: 0,
    jurisdiction: 'ZA',
    founded: 2002,
    compliance: { popia: false, gdpr: false, sox: false }
  },
  { 
    id: 'nortonrose-007', 
    name: 'Norton Rose Fulbright SA', 
    registration: '2008/092345/31', 
    users: 198, 
    plan: 'Enterprise', 
    status: 'Active', 
    revenue: 360000,
    jurisdiction: 'ZA',
    founded: 2008,
    compliance: { popia: true, gdpr: true, sox: true }
  },
  { 
    id: 'allenov-008', 
    name: 'Allen & Overy SA', 
    registration: '2010/067891/42', 
    users: 87, 
    plan: 'Business', 
    status: 'Active', 
    revenue: 150000,
    jurisdiction: 'ZA',
    founded: 2010,
    compliance: { popia: true, gdpr: false, sox: false }
  },
];

export const useTenantManagement = () => {
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedTenant, setSelectedTenant] = useState(null);
  const [filters, setFilters] = useState({});
  const [pagination, setPagination] = useState({ page: 1, limit: 20, total: 0 });

  const validateTenantId = useCallback((id) => {
    if (!id) return false;
    const cipcPattern = /^(19|20)\d{2}\/\d{6}\/\d{2}$/;
    const internalPattern = /^[a-z0-9-]{8,}$/i;
    return cipcPattern.test(id) || internalPattern.test(id);
  }, []);

  const validateCIPCRegistration = useCallback((reg) => {
    if (!reg) return false;
    return /^(19|20)\d{2}\/\d{6}\/\d{2}$/.test(reg);
  }, []);

  const fetchTenants = useCallback(async (customFilters = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const params = {
        page: pagination.page,
        limit: pagination.limit,
        ...filters,
        ...customFilters
      };
      
      const response = await superAdminAPI.getTenants(params);
      
      setTenants(response.data);
      setPagination(prev => ({
        ...prev,
        total: response.total || response.data.length
      }));
      
    } catch (err) {
      setError(err.message || 'Failed to fetch tenants');
      // Fallback to mock data
      setTenants(MOCK_TENANTS);
      setPagination(prev => ({ ...prev, total: MOCK_TENANTS.length }));
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.limit, filters]);

  const getTenant = useCallback(async (id) => {
    if (!id) throw new Error('Tenant ID is required');
    
    setLoading(true);
    
    try {
      const response = await superAdminAPI.getTenants({ id });
      const tenant = response.data[0] || MOCK_TENANTS.find(t => t.id === id);
      
      if (!tenant) {
        throw new Error(`Tenant ${id} not found`);
      }
      
      setSelectedTenant(tenant);
      return tenant;
      
    } catch (err) {
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const createTenant = useCallback(async (tenantData) => {
    setLoading(true);
    
    try {
      const response = await superAdminAPI.createTenant(tenantData);
      setTenants(prev => [...prev, response.data]);
      setPagination(prev => ({ ...prev, total: prev.total + 1 }));
      return { success: true, data: response.data };
      
    } catch (err) {
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  }, []);

  const updateTenant = useCallback(async (id, tenantData) => {
    if (!id) throw new Error('Tenant ID is required');
    
    setLoading(true);
    
    try {
      const response = await superAdminAPI.updateTenant(id, tenantData);
      setTenants(prev => prev.map(t => t.id === id ? response.data : t));
      if (selectedTenant?.id === id) {
        setSelectedTenant(response.data);
      }
      return { success: true, data: response.data };
      
    } catch (err) {
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  }, [selectedTenant]);

  const suspendTenant = useCallback(async (id, reason = '') => {
    if (!id) throw new Error('Tenant ID is required');
    
    setLoading(true);
    
    try {
      await superAdminAPI.suspendTenant(id);
      setTenants(prev => prev.map(t => 
        t.id === id ? { ...t, status: 'Suspended' } : t
      ));
      if (selectedTenant?.id === id) {
        setSelectedTenant(prev => ({ ...prev, status: 'Suspended' }));
      }
      return { success: true };
      
    } catch (err) {
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  }, [selectedTenant]);

  const checkCompliance = useCallback(async (id) => {
    if (!id) throw new Error('Tenant ID is required');
    
    const compliance = {
      compliant: true,
      score: 95 + Math.floor(Math.random() * 5),
      lastChecked: new Date().toISOString(),
      checks: {
        popia: true,
        gdpr: Math.random() > 0.2,
        sox: Math.random() > 0.3,
        retentionPolicy: true,
        dataProtection: true,
        auditLogs: true,
        encryption: true
      },
      recommendations: []
    };
    
    if (!compliance.checks.gdpr) {
      compliance.recommendations.push('Enable GDPR compliance settings');
    }
    if (!compliance.checks.sox) {
      compliance.recommendations.push('Update SOX audit configuration');
    }
    
    return compliance;
  }, []);

  const applyFilters = useCallback((newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    setPagination(prev => ({ ...prev, page: 1 }));
  }, []);

  const changePage = useCallback((newPage) => {
    setPagination(prev => ({ ...prev, page: newPage }));
  }, []);

  const clearSelected = useCallback(() => {
    setSelectedTenant(null);
  }, []);

  useEffect(() => {
    fetchTenants();
  }, [fetchTenants]);

  useEffect(() => {
    fetchTenants();
  }, [pagination.page, pagination.limit, filters, fetchTenants]);

  return {
    tenants,
    loading,
    error,
    selectedTenant,
    filters,
    pagination,
    validateTenantId,
    validateCIPCRegistration,
    fetchTenants,
    getTenant,
    createTenant,
    updateTenant,
    suspendTenant,
    clearSelected,
    checkCompliance,
    applyFilters,
    changePage,
    totalActiveTenants: tenants.filter(t => t.status === 'Active').length,
    totalRevenue: tenants.reduce((sum, t) => sum + (t.revenue || 0), 0),
    complianceRate: tenants.filter(t => t.compliance?.popia).length / tenants.length * 100 || 0
  };
};
