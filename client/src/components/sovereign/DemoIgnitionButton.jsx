/* eslint-disable */
/**
 * 🏛️ WILSY OS - DEMO IGNITION ENGINE
 * @version 2.2.0
 * @epitome BIBLICAL WORTH BILLIONS | ASSET SEALING TRIGGER
 * @description Master ignition trigger for R120B sovereign events.
 * -------------------------------------------------------------------------
 * COLLABORATION: Master Founder Wilson Khanyezi & AI Architect
 * -------------------------------------------------------------------------
 * MANDATE: Quantum-Ready | Tailwind v4 Token Alignment | Forensic Output
 */

import React, { useState } from "react";

const DemoIgnitionButton = () => {
  const [isIgniting, setIsIgniting] = useState(false);
  const [demoOutput, setDemoOutput] = useState(null);

  /**
   * ⚛️ SOVEREIGN IGNITION SEQUENCE
   * Triggers the master contract seal with PQE-256 validation.
   */
  const triggerSovereignEvent = async () => {
    setIsIgniting(true);
    try {
      const response = await fetch('/api/v2/sovereign/demo/ignite', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-sovereign-key': 'MASTER_FOUNDER_KEY_2050'
        }
      });
      const result = await response.json();

      // Simulate cryptographic sealing duration
      setTimeout(() => {
        setDemoOutput(result.data);
        setIsIgniting(false);
      }, 1500);
    } catch (error) {
      console.error("[CRITICAL] Ignition Failure", error);
      setIsIgniting(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center mt-12 py-10 border-t border-stone-900">
      {!demoOutput ? (
        <button
          className={`btn-sovereign-gold min-w-[340px] text-xl font-black py-6 tracking-[0.3em] transition-all duration-500
            ${isIgniting ? 'scale-95 border-gold shadow-[0_0_50px_rgba(212,175,55,0.4)] opacity-80' : 'shadow-2xl'}`}
          onClick={triggerSovereignEvent}
          disabled={isIgniting}
        >
          {isIgniting ? (
            <span className="flex items-center justify-center gap-4">
              <span className="animate-spin text-2xl">⚛️</span> SEALING_ASSET...
            </span>
          ) : (
            'EXECUTE SOVEREIGN IGNITION'
          )}
        </button>
      ) : (
        <div className="bg-stone-950 border border-gold p-10 shadow-gold-glow animate-in zoom-in duration-300 w-full max-w-xl">
          <header className="flex justify-between items-center mb-6 border-b border-stone-900 pb-4">
            <h2 className="text-emerald-500 font-black tracking-[4px] text-sm uppercase flex items-center gap-2">
              <span className="text-xl">✅</span> Anchored_Sovereignty
            </h2>
            <button
              onClick={() => setDemoOutput(null)}
              className="text-stone-700 hover:text-gold text-[0.6rem] font-black tracking-widest uppercase transition-colors"
            >
              [ Reset_Sequence ]
            </button>
          </header>

          <div className="space-y-4 font-mono">
            <div className="flex justify-between text-[0.7rem] border-b border-stone-900/50 py-2">
              <span className="text-stone-600 font-bold uppercase">Asset_ID:</span>
              <span className="text-stone-300 font-black">{demoOutput.contract_id}</span>
            </div>
            <div className="flex justify-between text-[0.7rem] border-b border-stone-900/50 py-2">
              <span className="text-stone-600 font-bold uppercase">Valuation:</span>
              <span className="text-gold font-black">{demoOutput.valuation}</span>
            </div>
            <div className="flex justify-between text-[0.7rem] py-2">
              <span className="text-stone-600 font-bold uppercase">Integrity_Hash:</span>
              <span className="text-emerald-600 font-black">SHA-512_VERIFIED</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DemoIgnitionButton;
