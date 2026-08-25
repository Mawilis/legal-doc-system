/* eslint-disable */
import React from 'react';
import { Globe, Compass } from 'lucide-react';

const Sovereign_Global_Topography = () => {
  return (
    <div data-testid="sovereign-global-topography" className="p-6 bg-stone-950 border border-stone-800 rounded-xl text-stone-100">
      <div className="flex items-center space-x-3 mb-4">
        <Globe className="w-5 h-5 text-amber-400" />
        <h3 className="text-lg font-black uppercase tracking-wider text-amber-400">GLOBAL TOPOGRAPHY & ORCHESTRATION</h3>
      </div>
      <p className="text-xs text-stone-400 font-mono">MULTI-REGION GEOGRAPHIC FAILOVER & REAL-TIME TRAFFIC SHARDING</p>
    </div>
  );
};

export default Sovereign_Global_Topography;
