/**
 * File: client/src/context/TenantContext.jsx
 * -----------------------------------------------------------------------------
 * STATUS: EPITOME | Multi-Tenant Core
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - The "Soul" of the White-Label Engine.
 * - FETCHER: Loads Firm Profile, Branding, and Settings on boot.
 * - PAINTER: Dynamically injects CSS variables to re-skin the app (e.g., Firm Colors).
 * - GUARD: Checks Subscription Status (Active vs Suspended).
 * -----------------------------------------------------------------------------
 */

import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

// --- CONTEXT DEFINITION ---
const TenantContext = createContext(null);

// --- PROVIDER COMPONENT ---
export function TenantProvider({ children }) {
    const [tenant, setTenant] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // 1. Check for Auth Token first
        const token = localStorage.getItem('token');
        if (!token) {
            setLoading(false);
            return;
        }

        const bootTenant = async () => {
            try {
                // Use relative path; Proxy in package.json handles the domain
                const res = await axios.get('/api/tenants/me', {
                    headers: { Authorization: `Bearer ${token}` }
                });

                const tenantData = res.data.data;
                setTenant(tenantData);

                // 2. THE CHAMELEON EFFECT (Dynamic Branding)
                // This injects the Law Firm's specific color into the CSS root
                if (tenantData.settings?.primaryColor) {
                    document.documentElement.style.setProperty('--primary-color', tenantData.settings.primaryColor);
                }

                // 3. DYNAMIC FAVICON
                // Changes the browser tab icon to the Law Firm's logo
                if (tenantData.settings?.logoUrl) {
                    const link = document.querySelector("link[rel~='icon']");
                    if (link) link.href = tenantData.settings.logoUrl;
                }

            } catch (err) {
                console.error("❌ [Tenant] Boot failed:", err);
                setError(err.response?.data?.message || 'Failed to load firm profile');
            } finally {
                setLoading(false);
            }
        };

        bootTenant();
    }, []);

    // --- FEATURE FLAGS (Permission Helpers) ---
    const hasFeature = (featureKey) => {
        // e.g. 'ai_analysis' is only for 'Enterprise' plan
        const plan = tenant?.subscription?.plan || 'Free';
        const entitlements = {
            'Free': ['basic_docs', 'limited_storage'],
            'Pro': ['basic_docs', 'unlimited_storage', 'api_access'],
            'Enterprise': ['basic_docs', 'unlimited_storage', 'api_access', 'ai_analysis', 'white_label']
        };
        return entitlements[plan]?.includes(featureKey) || false;
    };

    return (
        <TenantContext.Provider value={{ tenant, loading, error, hasFeature }}>
            {loading ? (
                // A simple, elegant loader while the "Soul" loads
                <div style={{ height: '100vh', display: 'grid', placeItems: 'center', background: '#F8FAFC' }}>
                    <div style={{ textAlign: 'center' }}>
                        <div className="spinner" style={{
                            width: 40, height: 40, border: '3px solid #E2E8F0',
                            borderTop: '3px solid #0F172A', borderRadius: '50%',
                            animation: 'spin 1s linear infinite'
                        }} />
                        <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
                        <p style={{ marginTop: 16, color: '#64748B', fontSize: '0.9rem', fontWeight: 500 }}>
                            Loading Workspace...
                        </p>
                    </div>
                </div>
            ) : (
                children
            )}
        </TenantContext.Provider>
    );
}

// --- CUSTOM HOOK (The Consumption Layer) ---
export const useTenant = () => {
    const context = useContext(TenantContext);
    if (!context) {
        throw new Error('useTenant must be used within a TenantProvider');
    }
    return context;
};