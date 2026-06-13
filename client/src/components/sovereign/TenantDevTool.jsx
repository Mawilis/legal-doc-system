/* eslint-disable */
/**
 * 🏛️ WILSY OS - TENANT DEVELOPMENT TOOL
 * @version 1.2.0
 * @description DEVELOPMENT ONLY - Remove before production!
 *              Allows manual tenant onboarding for testing real data connections.
 *
 * @team Collaboration Notes:
 * - FIXED: State management issue where isActive was true but no tenant data
 * - FIXED: "ONBOARD TENANT" button now properly enabled/disabled
 * - Added manual refresh option
 *
 * @last_updated: 2026-03-18
 */

import React, { useState, useEffect } from 'react';


/**
 * @function TenantDevTool
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const TenantDevTool = ({ onClose }) => {
  const [isActive, setIsActive] = useState(false);
  const [tenantId, setTenantId] = useState('tenant_123');
  const [tenantData, setTenantData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  console.log('[DEVTOOL] Rendering, isActive:', isActive, 'tenantData:', tenantData);

  useEffect(() => {
    // Check if already onboarded
    try {
      const user = localStorage.getItem('user');
      console.log('[DEVTOOL] Raw user from localStorage:', user);

      if (user) {
        const parsedUser = JSON.parse(user);
        console.log('[DEVTOOL] Parsed user:', parsedUser);

        // Only set active if we have valid tenant data
        if (parsedUser && parsedUser.tenantId) {
          setIsActive(true);
          setTenantData(parsedUser);
          setTenantId(parsedUser.tenantId);
        } else {
          // Invalid data - clear it
          console.log('[DEVTOOL] Invalid tenant data, clearing...');
          localStorage.removeItem('user');
          localStorage.removeItem('token');
          setIsActive(false);
          setTenantData(null);
        }
      } else {
        console.log('[DEVTOOL] No user found in localStorage');
        setIsActive(false);
        setTenantData(null);
      }
    } catch (e) {
      console.error('[TENANT] Error reading user data:', e);
      // Clear corrupted data
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      setIsActive(false);
      setTenantData(null);
    }
  }, []);

  
/**
 * @function handleOnboard
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const handleOnboard = () => {
    console.log('[DEVTOOL] Onboarding with tenantId:', tenantId);
    setIsLoading(true);

    try {
      const timestamp = Date.now();
      const mockUser = {
        id: `user_${timestamp}`,
        tenantId: tenantId,
        name: 'Test User',
        role: 'FOUNDER',
        email: 'test@wilsy.com',
        onboardedAt: new Date().toISOString()
      };

      const mockToken = 'jwt_' + Array(64).fill(0).map(() =>
        Math.floor(Math.random() * 16).toString(16)).join('');

      localStorage.setItem('user', JSON.stringify(mockUser));
      localStorage.setItem('token', mockToken);

      console.log('[TENANT] Onboarded successfully:', mockUser);

      // Update state immediately
      setIsActive(true);
      setTenantData(mockUser);

      // Force reload after a brief delay to ensure state updates are visible
      setTimeout(() => {
        window.location.reload();
      }, 500);
    } catch (error) {
      console.error('[DEVTOOL] Onboarding failed:', error);
      setIsLoading(false);
    }
  };

  
/**
 * @function handleLogout
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const handleLogout = () => {
    console.log('[DEVTOOL] Logging out');
    setIsLoading(true);

    localStorage.removeItem('user');
    localStorage.removeItem('token');

    setIsActive(false);
    setTenantData(null);

    setTimeout(() => {
      window.location.reload();
    }, 500);
  };

  
/**
 * @function handleClearAll
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const handleClearAll = () => {
    console.log('[DEVTOOL] Clearing all storage');
    setIsLoading(true);

    localStorage.clear();
    sessionStorage.clear();

    setIsActive(false);
    setTenantData(null);

    setTimeout(() => {
      window.location.reload();
    }, 500);
  };

  
/**
 * @function handleManualRefresh
 * @memberof WILSY_OS_CORE
 * @description Production-grade sovereign enterprise asset node optimized for 10-generation architectural distribution.
 * @returns {any} Matrix runtime feedback data context output
 */
const handleManualRefresh = () => {
    window.location.reload();
  };

  return (
    <div className="fixed bottom-4 left-4 z-[10000] bg-black border border-gold/30 p-4 rounded-sm shadow-2xl w-96 max-w-[calc(100vw-2rem)]">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-gold text-xs font-black tracking-wider flex items-center gap-2">
          <span>🔧 TENANT DEV TOOL</span>
          <span className="text-[0.3rem] text-stone-600 font-mono">v1.2</span>
        </h3>
        <button
          onClick={onClose}
          className="text-stone-600 hover:text-stone-400 text-sm"
          aria-label="Close"
        >
          ✕
        </button>
      </div>

      <div className="space-y-3">
        {/* Status Indicator */}
        <div className="bg-stone-900/50 p-2 rounded-sm">
          <div className="text-stone-500 text-[0.5rem] font-black tracking-wider uppercase block mb-1">
            Current Status
          </div>
          <div className={`text-[0.6rem] font-mono px-2 py-1 rounded-sm flex items-center gap-2 ${
            isActive && tenantData
              ? 'bg-emerald-500/20 text-emerald-500 border border-emerald-500/30'
              : 'bg-gold/20 text-gold border border-gold/30'
          }`}>
            <span className={`w-2 h-2 rounded-full ${isActive && tenantData ? 'bg-emerald-500 animate-pulse' : 'bg-gold'}`}></span>
            {isActive && tenantData ? '✓ TENANT ACTIVE (PRODUCTION MODE)' : '○ DEMO MODE (PLACEHOLDERS)'}
          </div>
        </div>

        {/* Tenant ID Input */}
        <div>
          <label className="text-stone-500 text-[0.5rem] font-black tracking-wider uppercase block mb-1">
            Tenant ID
          </label>
          <input
            type="text"
            value={tenantId}
            onChange={(e) => setTenantId(e.target.value)}
            placeholder="tenant_123"
            disabled={isActive && !!tenantData}
            className={`w-full bg-stone-900 border text-[0.6rem] font-mono px-2 py-1 rounded-sm focus:border-gold focus:outline-none ${
              isActive && tenantData
                ? 'border-stone-800 text-stone-600 cursor-not-allowed'
                : 'border-stone-800 text-gold'
            }`}
          />
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={handleOnboard}
            disabled={isActive && !!tenantData || isLoading}
            className={`px-3 py-2 text-[0.55rem] font-black uppercase tracking-wider rounded-sm transition-all ${
              isActive && !!tenantData || isLoading
                ? 'bg-stone-800 text-stone-600 cursor-not-allowed'
                : 'bg-gold/20 border border-gold/30 text-gold hover:bg-gold/30'
            }`}
          >
            {isLoading ? 'PROCESSING...' : 'ONBOARD TENANT'}
          </button>

          <button
            onClick={handleLogout}
            disabled={!isActive || !tenantData || isLoading}
            className={`px-3 py-2 text-[0.55rem] font-black uppercase tracking-wider rounded-sm transition-all ${
              !isActive || !tenantData || isLoading
                ? 'bg-stone-800 text-stone-600 cursor-not-allowed'
                : 'bg-red-500/20 border border-red-500/30 text-red-500 hover:bg-red-500/30'
            }`}
          >
            {isLoading ? 'PROCESSING...' : 'LOGOUT'}
          </button>
        </div>

        {/* Clear Storage Button */}
        <button
          onClick={handleClearAll}
          disabled={isLoading}
          className={`w-full px-3 py-2 text-[0.5rem] font-mono transition-all rounded-sm ${
            isLoading
              ? 'bg-stone-800 text-stone-600 cursor-not-allowed'
              : 'text-stone-600 hover:text-stone-400 bg-stone-900/50 border border-stone-800 hover:bg-stone-900'
          }`}
        >
          {isLoading ? 'PROCESSING...' : 'CLEAR ALL STORAGE'}
        </button>

        {/* Manual Refresh Button */}
        <button
          onClick={handleManualRefresh}
          className="w-full px-3 py-2 text-[0.45rem] font-mono text-stone-700 hover:text-stone-500 bg-stone-900/30 border border-stone-800 rounded-sm transition-all"
        >
          ↻ MANUAL REFRESH
        </button>

        {/* Active Tenant Info */}
        {isActive && tenantData && (
          <div className="mt-2 p-2 bg-stone-900/30 rounded-sm border border-stone-800">
            <div className="text-[0.45rem] text-stone-500 font-mono mb-1">ACTIVE TENANT</div>
            <div className="text-[0.55rem] font-mono text-emerald-500 break-all">
              ID: {tenantData.tenantId}
            </div>
            <div className="text-[0.45rem] font-mono text-stone-400 mt-1">
              User: {tenantData.name} • Role: {tenantData.role}
            </div>
          </div>
        )}

        {/* Debug Info */}
        <div className="text-[0.35rem] text-stone-700 font-mono border-t border-stone-900 pt-2 mt-2">
          <div>isActive: {String(isActive)}</div>
          <div>hasTenantData: {String(!!tenantData)}</div>
          <div>isLoading: {String(isLoading)}</div>
        </div>

        {/* Warning */}
        <div className="text-[0.4rem] text-yellow-600/50 font-mono mt-2 border-t border-stone-900 pt-2">
          ⚠️ DEVELOPMENT ONLY - Remove before production deployment
        </div>
      </div>
    </div>
  );
};

export default TenantDevTool;
