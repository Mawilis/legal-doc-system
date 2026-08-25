/* eslint-disable */
import React from 'react';
import { FileCheck, Shield } from 'lucide-react';

const Sovereign_Client_Covenant = () => {
  return (
    <div data-testid="sovereign-client-covenant" className="p-6 bg-stone-950 border border-stone-800 rounded-xl text-stone-100">
      <div className="flex items-center space-x-3 mb-4">
        <FileCheck className="w-5 h-5 text-amber-400" />
        <h3 className="text-lg font-black uppercase tracking-wider text-amber-400">CLIENT COVENANT & LEGAL CONTRACTS</h3>
      </div>
      <p className="text-xs text-stone-400 font-mono">CRYPTOGRAPHICALLY SEALED INSTITUTIONAL AGREEMENTS</p>
    </div>
  );
};

export default Sovereign_Client_Covenant;
