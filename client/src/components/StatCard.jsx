/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS — SOVEREIGN STAT CARD COMPONENT [V2050.1.0-PRODUCTION-READY]                                                                  ║
 * ║ [BIBLICAL WORTH BILLIONS | ENTERPRISE METRIC NODE | QUANTUM TELEMETRY CARD]                                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2050.1.0-PRODUCTION-GRADE | PRODUCTION READY | BILLION-DOLLAR ENTERPRISE OPERATING SYSTEM COMPONENT                         ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/StatCard.jsx                                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Mandated pristine metric display cards with real-time telemetry and sovereign styling.               ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Production-ready StatCard component supporting data attributes for reliable test suites.       ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React from 'react';

/**
 * @function StatCard
 * @memberof WILSY_OS_COMPONENTS
 * @description Enterprise-grade metric card for displaying KPIs, telemetry counts, and sovereign financial metrics.
 * 
 * @param {Object} props Component properties
 * @param {string} props.title Title or label of the metric
 * @param {string|number} props.value Primary value or metric reading
 * @param {string} [props.change] Optional percentage change or operational status text
 * @param {string|React.ReactNode} [props.icon] Optional icon or emoji representation
 * @returns {JSX.Element} Rendered stat card component.
 */
export default function StatCard({ title, value, change, icon }) {
  return (
    <div 
      data-testid="stat-card" 
      data-title={title}
      className="bg-neutral-950 border border-neutral-800 p-6 rounded-xl shadow-[0_10px_30px_rgba(0,0,0,0.8)] relative overflow-hidden flex flex-col justify-between hover:border-[#D4AF37]/50 transition-all duration-300"
    >
      <div className="absolute top-0 right-0 w-24 h-24 bg-[radial-gradient(circle,_var(--tw-gradient-stops))] from-[#D4AF37]/10 to-transparent pointer-events-none"></div>
      
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-neutral-400 text-xs font-black uppercase tracking-[0.2em]">{title}</h3>
        {icon && <span className="text-2xl" aria-hidden="true">{icon}</span>}
      </div>

      <div className="my-2">
        <p className="text-4xl font-black font-mono text-white tracking-tight">{value}</p>
      </div>

      {change && (
        <div className="mt-3 pt-3 border-t border-neutral-900 flex items-center text-xs font-mono">
          <span className="text-emerald-400 font-bold">{change}</span>
        </div>
      )}
    </div>
  );
}
