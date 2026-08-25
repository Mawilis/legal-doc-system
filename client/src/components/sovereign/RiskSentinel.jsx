/* eslint-disable */
import React from 'react';
import { ShieldAlert } from 'lucide-react';

const RiskSentinel = () => {
  return (
    <div data-testid="risk-sentinel" className="p-6 bg-stone-950 border border-stone-800 rounded-xl text-stone-100">
      <div className="flex items-center space-x-3 mb-4">
        <ShieldAlert className="w-5 h-5 text-amber-400" />
        <h3 className="text-lg font-black uppercase tracking-wider text-amber-400">RISK SENTINEL HUD</h3>
      </div>
      <p className="text-xs text-stone-400 font-mono">ZERO-TRUST ANOMALY DETECTION & CONTINUOUS FORENSIC AUDITING</p>
    </div>
  );
};

export default RiskSentinel;
