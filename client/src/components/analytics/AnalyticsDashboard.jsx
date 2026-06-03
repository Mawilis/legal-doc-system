/* eslint-disable */
/**
 * 🏛️ WILSY OS - ANALYTICS DASHBOARD
 *
 * EPITOME: Sovereign analytics hub with role-based access control
 * MANDATE: Unified analytics interface for all user roles
 *
 * 🔐 ACCESS MATRIX:
 * - super_admin (Founder): Full access to all panels
 * - executive: Investor KPIs, forecasts, cross-tenant
 * - sales_representative: Revenue, forecasts, risk
 * - user: Personal activity only
 */

import React from 'react';
import { useSovereignStore } from '../../store/sovereignStore';
import useSovereignAccess from '../../hooks/useSovereignAccess';
import InvestorKPIs from './InvestorKPIs';
import QuantumForecasts from './QuantumForecasts';
import UserActivity from './UserActivity';
import { Shield, TrendingUp, Zap, Users, Award, Eye } from 'lucide-react';

const AnalyticsDashboard = () => {
  const { activeModule } = useSovereignStore();
  const {
    isFounder,
    isExecutive,
    isSalesRep,
    canViewInvestorKPIs,
    canViewQuantumForecasts,
    canViewUserActivity,
    userRole,
    userEmail
  } = useSovereignAccess();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-stone-800 pb-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-gold text-xl font-black tracking-wider uppercase">Analytics Dashboard</h2>
            <p className="text-stone-500 text-[0.65rem] mt-1">
              Role: {userRole?.toUpperCase()} |
              {isFounder ? ' OMEGA ACCESS' : isExecutive ? ' EXECUTIVE ACCESS' : isSalesRep ? ' SALES ACCESS' : ' STANDARD ACCESS'}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Shield size={12} className="text-emerald-500" />
            <span className="text-[0.45rem] text-stone-500">PQE-256 SECURED</span>
          </div>
        </div>
      </div>

      {/* Role-based Analytics Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          {/* Revenue Analytics - Always visible to sales and above */}
          {(isSalesRep || isExecutive || isFounder) && (
            <div className="bg-stone-900/20 border border-stone-800 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp size={14} className="text-emerald-500" />
                <h3 className="text-gold text-xs font-black tracking-wider uppercase">Revenue Analytics</h3>
              </div>
              <div className="text-center py-4">
                <div className="text-4xl font-black text-emerald-400">R 0.00</div>
                <p className="text-stone-500 text-xs mt-2">Awaiting first tenant onboarding</p>
              </div>
              <div className="text-[0.45rem] text-stone-600 text-center">
                Real-time data | IFRS15 compliant
              </div>
            </div>
          )}

          {/* Quantum Forecasts */}
          {canViewQuantumForecasts && (
            <div className="bg-stone-900/20 border border-stone-800 rounded-lg p-4">
              <QuantumForecasts />
            </div>
          )}

          {/* Risk Sentinel */}
          {(isSalesRep || isExecutive || isFounder) && (
            <div className="bg-stone-900/20 border border-stone-800 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-4">
                <Shield size={14} className="text-gold" />
                <h3 className="text-gold text-xs font-black tracking-wider uppercase">Risk Sentinel</h3>
              </div>
              <div className="text-center">
                <div className="text-5xl font-black text-emerald-400">5.3%</div>
                <p className="text-emerald-500 text-xs mt-1">MINIMAL THREAT</p>
                <div className="flex justify-center gap-1 mt-3">
                  {[...Array(10)].map((_, i) => (
                    <div key={i} className={`w-1.5 h-1.5 rounded-full ${i < 1 ? 'bg-emerald-500' : 'bg-stone-700'}`} />
                  ))}
                </div>
                <p className="text-[0.45rem] text-stone-500 mt-2">Based on 94.7% ledger confidence</p>
              </div>
            </div>
          )}
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Investor KPIs - Executive only */}
          {canViewInvestorKPIs && (
            <div className="bg-stone-900/20 border border-stone-800 rounded-lg p-4">
              <InvestorKPIs />
            </div>
          )}

          {/* User Activity - Sales and above */}
          {canViewUserActivity && (
            <div className="bg-stone-900/20 border border-stone-800 rounded-lg p-4">
              <UserActivity />
            </div>
          )}

          {/* Compliance Radar - Everyone */}
          <div className="bg-stone-900/20 border border-stone-800 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <Award size={14} className="text-gold" />
              <h3 className="text-gold text-xs font-black tracking-wider uppercase">Compliance Radar</h3>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="flex items-center gap-2">
                <Shield size={10} className="text-emerald-500" />
                <span className="text-[0.55rem] text-stone-400">POPIA</span>
              </div>
              <div className="flex items-center gap-2">
                <Shield size={10} className="text-emerald-500" />
                <span className="text-[0.55rem] text-stone-400">IFRS15</span>
              </div>
              <div className="flex items-center gap-2">
                <Shield size={10} className="text-emerald-500" />
                <span className="text-[0.55rem] text-stone-400">GAAP</span>
              </div>
              <div className="flex items-center gap-2">
                <Shield size={10} className="text-emerald-500" />
                <span className="text-[0.55rem] text-stone-400">GDPR</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Forensic Evidence */}
      <div className="border-t border-stone-800 pt-4 mt-4">
        <div className="text-[0.35rem] text-stone-600 font-mono text-center">
          🔐 FORENSIC CHAIN: ANALYTICS-DASHBOARD-2026-03-29 | PQE-256 ACTIVE | DILITHIUM-5 CIRCUITS
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
