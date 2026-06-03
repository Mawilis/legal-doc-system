/* eslint-disable */
/**
 * 🛰️ WILSY OS SOVEREIGN NAVIGATION
 * Future-proofed for 2050 Global Operations.
 */
import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar = () => {
  const navItems = [
    { name: 'Command Center', path: '/superadmin/dashboard', icon: '🏛️' },
    { name: 'Tenant Control', path: '/superadmin/tenants', icon: '🌍' },
    { name: 'User Authority', path: '/superadmin/users', icon: '👤' },
    { name: 'Forensic Audit', path: '/superadmin/audit', icon: '🔍' },
    { name: 'Quantum Security', path: '/superadmin/security', icon: '🛡️' },
    { name: 'System Config', path: '/superadmin/system', icon: '⚙️' },
  ];

  return (
    <aside className="w-64 h-screen bg-slate-900 text-slate-300 flex flex-col border-r border-slate-800 shadow-2xl">
      <div className="p-6 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold shadow-indigo-500/50 shadow-lg">W</div>
          <div>
            <h2 className="text-white font-bold tracking-tighter">WILSY OS</h2>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Supreme Admin</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 mt-6 px-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
                isActive ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20' : 'hover:bg-slate-800 hover:text-white'
              }`
            }
          >
            <span className="text-lg">{item.icon}</span>
            <span className="font-medium text-sm">{item.name}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-6 border-t border-slate-800">
        <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/50">
          <p className="text-[10px] text-slate-500 uppercase font-bold mb-1">Node Status</p>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            <span className="text-xs font-mono text-green-400">Quantum Link Active</span>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
