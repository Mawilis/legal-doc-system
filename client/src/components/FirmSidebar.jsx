/* eslint-disable */
/**
 * 🏢 WILSY OS - FIRM OPERATIONAL NAVIGATION
 * Optimized for Legal Process Outsourcing & Vault Management.
 * Biblical Structure | Vision 2050
 */
import React from 'react';
import { NavLink } from 'react-router-dom';

const FirmSidebar = () => {
  const navItems = [
    { name: 'Firm Overview', path: '/firm/dashboard', icon: '📊' },
    { name: 'Legal Vaults', path: '/firm/vaults', icon: '🗄️' },
    { name: 'Smart Templates', path: '/firm/templates', icon: '📝' },
    { name: 'Chain Verification', path: '/firm/forensics', icon: '🔗' },
    { name: 'Firm Settings', path: '/firm/settings', icon: '🛠️' },
  ];

  return (
    <aside className="w-64 h-screen bg-[#020617] text-slate-400 flex flex-col border-r border-indigo-900/20 shadow-xl">
      <div className="p-8">
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="w-16 h-16 bg-gradient-to-tr from-indigo-900 to-indigo-600 rounded-2xl flex items-center justify-center text-white text-2xl font-black shadow-2xl shadow-indigo-500/20">
            F
          </div>
          <div>
            <h2 className="text-white font-bold tracking-tight text-sm uppercase italic">Firm Operator</h2>
            <p className="text-[9px] text-indigo-500 font-mono tracking-[0.2em] mt-1">SOVEREIGN_NODE_v1.0</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-4 px-4 py-3 rounded-lg transition-all group ${
                isActive ? 'bg-indigo-600/10 text-indigo-400 border-l-2 border-indigo-500' : 'hover:bg-slate-800/50 hover:text-slate-200'
              }`
            }
          >
            <span className="opacity-70 group-hover:opacity-100">{item.icon}</span>
            <span className="text-xs font-bold uppercase tracking-wider">{item.name}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-6">
        <div className="bg-indigo-950/30 border border-indigo-900/30 p-4 rounded-xl">
          <div className="flex justify-between items-center mb-2">
            <span className="text-[9px] uppercase font-bold text-slate-500">Hash Integrity</span>
            <span className="text-[9px] font-mono text-green-500">99.9%</span>
          </div>
          <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
            <div className="bg-indigo-500 h-full w-[99%] animate-pulse"></div>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default FirmSidebar;
