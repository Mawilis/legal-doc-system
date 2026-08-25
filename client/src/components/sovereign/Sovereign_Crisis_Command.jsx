/* eslint-disable */
import React from 'react';
import { AlertTriangle, Zap } from 'lucide-react';

const Sovereign_Crisis_Command = () => {
  return (
    <div data-testid="sovereign-crisis-command" className="p-6 bg-stone-950 border border-stone-800 rounded-xl text-stone-100">
      <div className="flex items-center space-x-3 mb-4">
        <AlertTriangle className="w-5 h-5 text-amber-400" />
        <h3 className="text-lg font-black uppercase tracking-wider text-amber-400">CRISIS COMMAND & EMERGENCY SHUTDOWN</h3>
      </div>
      <p className="text-xs text-stone-400 font-mono">POST-QUANTUM KIL-SWITCH & IMMUTABLE DATA ISOLATION PROTOCOLS</p>
    </div>
  );
};

export default Sovereign_Crisis_Command;
