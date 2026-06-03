/* eslint-disable */
/**
 * 📝 WILSY OS - SMART TEMPLATE ENGINE
 * Generational Document Automation.
 */
import React from 'react';

const SmartTemplates = () => {
  const templates = [
    { name: 'Family Trust Deed', code: 'TR-001', Category: 'Wealth' },
    { name: 'Quantum Service Agreement', code: 'SA-99', Category: 'Tech' },
    { name: 'Forensic Property Transfer', code: 'PT-40', Category: 'Real Estate' }
  ];

  return (
    <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-600">
      <header>
        <h2 className="text-3xl font-black text-white tracking-tighter uppercase">Smart Templates</h2>
        <p className="text-slate-500 font-mono text-xs uppercase tracking-[0.3em]">Automation: Active</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map((t) => (
          <div key={t.code} className="bg-slate-900/40 border border-slate-800 p-6 rounded-3xl hover:bg-indigo-900/10 hover:border-indigo-500/40 transition-all cursor-pointer group">
            <div className="flex justify-between items-start mb-4">
              <span className="text-2xl group-hover:scale-110 transition-transform">📄</span>
              <span className="text-[9px] bg-slate-800 px-2 py-1 rounded text-slate-400 font-bold">{t.Category}</span>
            </div>
            <h3 className="text-white font-bold text-sm mb-1">{t.name}</h3>
            <p className="text-[10px] text-slate-500 font-mono">{t.code}</p>
            <button className="mt-6 w-full py-2 bg-slate-800 hover:bg-indigo-600 text-white text-[10px] font-bold rounded-xl transition-colors uppercase">Generate Document</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SmartTemplates;
