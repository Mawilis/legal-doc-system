import React, { createContext, useState, useContext, useEffect } from 'react';

const TenantContext = createContext();

export const TenantProvider = ({ children }) => {
  const [tenantId, setTenantId] = useState(() => {
    // Initialize from localStorage or sessionStorage
    return localStorage.getItem('wilsy_tenant_id') || 
           sessionStorage.getItem('wilsy_tenant_id') || 
           '';
  });
  
  const [userRole, setUserRole] = useState(() => {
    return localStorage.getItem('wilsy_user_role') || 
           sessionStorage.getItem('wilsy_user_role') || 
           'viewer';
  });
  
  const [userInfo, setUserInfo] = useState(() => {
    const stored = localStorage.getItem('wilsy_user_info');
    return stored ? JSON.parse(stored) : null;
  });
  
  // Persist changes to storage
  useEffect(() => {
    if (tenantId) {
      localStorage.setItem('wilsy_tenant_id', tenantId);
    }
  }, [tenantId]);
  
  useEffect(() => {
    if (userRole) {
      localStorage.setItem('wilsy_user_role', userRole);
    }
  }, [userRole]);
  
  useEffect(() => {
    if (userInfo) {
      localStorage.setItem('wilsy_user_info', JSON.stringify(userInfo));
    }
  }, [userInfo]);
  
  const updateTenant = (newTenantId, newUserRole = 'viewer', newUserInfo = null) => {
    setTenantId(newTenantId);
    setUserRole(newUserRole);
    if (newUserInfo) {
      setUserInfo(newUserInfo);
    }
  };
  
  const clearTenant = () => {
    localStorage.removeItem('wilsy_tenant_id');
    localStorage.removeItem('wilsy_user_role');
    localStorage.removeItem('wilsy_user_info');
    sessionStorage.removeItem('wilsy_tenant_id');
    sessionStorage.removeItem('wilsy_user_role');
    sessionStorage.removeItem('wilsy_user_info');
    
    setTenantId('');
    setUserRole('viewer');
    setUserInfo(null);
  };
  
  const hasPermission = (requiredRole) => {
    const roleHierarchy = {
      'superadmin': 4,
      'admin': 3,
      'manager': 2,
      'editor': 1,
      'viewer': 0
    };
    
    const currentLevel = roleHierarchy[userRole] || 0;
    const requiredLevel = roleHierarchy[requiredRole] || 0;
    
    return currentLevel >= requiredLevel;
  };
  
  const value = {
    tenantId,
    userRole,
    userInfo,
    updateTenant,
    clearTenant,
    hasPermission,
    isAuthenticated: !!tenantId
  };
  
  return (
    <TenantContext.Provider value={value}>
      {children}
    </TenantContext.Provider>
  );
};

export const useTenant = () => {
  const context = useContext(TenantContext);
  if (context === undefined) {
    throw new Error('useTenant must be used within a TenantProvider');
  }
  return context;
};

export default TenantContext;
