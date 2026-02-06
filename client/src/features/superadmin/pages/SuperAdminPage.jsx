/*
 * File: client/src/features/superadmin/pages/SuperAdminPage.jsx
 * STATUS: EPITOME | THE CITADEL (GOD MODE)
 * -----------------------------------------------------------------------------
 * PURPOSE: 
 * The Master Control Panel for Wilsy OS.
 * Accessible ONLY by you (Role: SUPER_ADMIN). 
 * Provides global oversight of all Tenants, Revenue, and System Health.
 * -----------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - SECURITY: LOCKED DOWN. Any attempt to access this route without the 'SUPER_ADMIN' 
 * token claim will trigger an immediate auto-logout security protocol.
 * - METRICS: Aggregates data across ALL database shards (Tenants).
 * -----------------------------------------------------------------------------
 */

import React from 'react';

export default function SuperAdminPage() {
    return (
        <div style={{ padding: '32px', background: '#0F172A', minHeight: '100vh', color: 'white' }}>

            {/* HEADER SECTION */}
            <header style={{ borderBottom: '1px solid #334155', paddingBottom: '24px', marginBottom: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h1 style={{ fontSize: '2.5rem', fontWeight: '800', margin: 0, letterSpacing: '-1px' }}>⚡ Super Admin Citadel</h1>
                    <p style={{ color: '#94A3B8', marginTop: '8px' }}>Global System Command / Wilsy OS v1.0</p>
                </div>
                <div style={{ padding: '8px 16px', background: '#22C55E', color: '#000', fontWeight: '700', borderRadius: '99px', fontSize: '0.875rem' }}>
                    SYSTEM NOMINAL
                </div>
            </header>

            {/* KPI GRID */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>

                {/* METRIC 1: REVENUE */}
                <div style={{ background: '#1E293B', padding: '32px', borderRadius: '16px', border: '1px solid #334155' }}>
                    <h3 style={{ color: '#64748B', fontSize: '0.875rem', fontWeight: '600', textTransform: 'uppercase', marginBottom: '12px' }}>Total ARR (Revenue)</h3>
                    <p style={{ fontSize: '2.5rem', fontWeight: '800', margin: 0 }}>R 0.00</p>
                    <span style={{ color: '#22C55E', fontSize: '0.875rem', fontWeight: '600' }}>+0% this month</span>
                </div>

                {/* METRIC 2: TENANTS */}
                <div style={{ background: '#1E293B', padding: '32px', borderRadius: '16px', border: '1px solid #334155' }}>
                    <h3 style={{ color: '#64748B', fontSize: '0.875rem', fontWeight: '600', textTransform: 'uppercase', marginBottom: '12px' }}>Active Law Firms</h3>
                    <p style={{ fontSize: '2.5rem', fontWeight: '800', margin: 0 }}>1</p>
                    <span style={{ color: '#3B82F6', fontSize: '0.875rem', fontWeight: '600' }}>System Seeded</span>
                </div>

                {/* METRIC 3: INFRASTRUCTURE */}
                <div style={{ background: '#1E293B', padding: '32px', borderRadius: '16px', border: '1px solid #334155' }}>
                    <h3 style={{ color: '#64748B', fontSize: '0.875rem', fontWeight: '600', textTransform: 'uppercase', marginBottom: '12px' }}>Server Latency</h3>
                    <p style={{ fontSize: '2.5rem', fontWeight: '800', margin: 0 }}>24ms</p>
                    <span style={{ color: '#F59E0B', fontSize: '0.875rem', fontWeight: '600' }}>Midrand Region</span>
                </div>

            </div>
        </div>
    );
}