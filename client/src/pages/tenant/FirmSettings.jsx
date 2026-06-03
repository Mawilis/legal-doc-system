/* eslint-disable */
/**
 * 🛠️ WILSY OS - FIRM SETTINGS & COMPLIANCE
 * Multi-Jurisdiction Governance & Forensic Preferences.
 * Built for 10th Generation Wealth Infrastructure.
 */
import React, { useState } from 'react';

const FirmSettings = () => {
  const [settings, setSettings] = useState({
    autoHash: true,
    jurisdiction: 'South Africa',
    dataResidency: 'Local',
    multiTaxEnabled: true
  });

  return (
    <div className="space-y-8 animate-in slide-in-from-top-4 duration-700">
      <header>
        <h2 className="text-3xl font-black text-white tracking-tighter uppercase">Firm Settings</h2>
        <p className="text-slate-500 font-mono text-xs uppercase tracking-[0.3em]">Node: Operational Parameters</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Compliance & Jurisdiction */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-3xl p-8 hover:border-indigo-500/30 transition-all">
          <h3 className="text-indigo-400 font-bold text-xs uppercase tracking-[0.2em] mb-6">Global Compliance</h3>
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <span className="text-slate-300 text-sm">Primary Jurisdiction</span>
              <span className="text-white font-bold text-xs bg-slate-800 px-3 py-1 rounded-lg border border-slate-700">{settings.jurisdiction}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-300 text-sm">Multi-Jurisdiction Tax</span>
              <div className="w-10 h-5 bg-indigo-600 rounded-full relative">
                <div className="absolute right-1 top-1 w-3 h-3 bg-white rounded-full"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Forensic Preferences */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-3xl p-8 hover:border-indigo-500/30 transition-all">
          <h3 className="text-indigo-400 font-bold text-xs uppercase tracking-[0.2em] mb-6">Forensic Logic</h3>
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <span className="text-slate-300 text-sm">Automated Hash-Chaining</span>
              <span className="text-green-500 font-mono text-[10px] font-bold">ACTIVE_VERIFICATION</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-300 text-sm">Data Residency</span>
              <span className="text-slate-400 font-bold text-xs italic">{settings.dataResidency} Node</span>
            </div>
          </div>
        </div>
      </div>

      <div className="p-8 bg-indigo-950/20 border border-indigo-900/20 rounded-3xl">
        <h4 className="text-white font-bold text-sm mb-2">Biblical Integrity Clause</h4>
        <p className="text-indigo-300/60 text-xs leading-relaxed font-serif">
          "The configuration of this firm node is cryptographically sealed. Any change to the
          jurisdictional parameters will trigger a forensic audit across the 2050 Vision network."
        </p>
      </div>
    </div>
  );
};

export default FirmSettings;
