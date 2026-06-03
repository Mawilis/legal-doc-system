/* eslint-disable */
/**
 * 🏛️ WILSY OS - CLIENT COVENANT BOARD
 * @version 1.0.1
 * @epitome BIBLICAL WORTH BILLIONS | CLIENT RELATIONSHIP MANAGEMENT
 * @description Sovereign client covenant management with contractual integrity,
 *              compliance tracking, and relationship health monitoring.
 *
 * @team Collaboration Notes:
 * - FIXED: Duplicate text elements causing test failures
 * - FIXED: Health bar colors now match correct values
 * - FIXED: Added unique test IDs for all elements
 * - FIXED: Compliance tag counts now accurate
 *
 * @last_updated: 2026-03-17
 */

import React, { useState } from 'react';
import { Briefcase, Users, FileText, CheckCircle, AlertTriangle, Clock, Globe, Shield } from 'lucide-react';

const Sovereign_Client_Covenant = () => {
  const [clients] = useState([
    {
      id: 1,
      name: 'Global Financial Trust',
      type: 'INSTITUTIONAL',
      covenant: 'ACTIVE',
      health: 98,
      lastAudit: '2026-03-15',
      compliance: ['POPIA', 'GDPR', 'SOC2'],
      value: 'R 45.2B'
    },
    {
      id: 2,
      name: 'Sovereign Wealth Partners',
      type: 'SOVEREIGN',
      covenant: 'ACTIVE',
      health: 95,
      lastAudit: '2026-03-14',
      compliance: ['GDPR', 'SOC2'],
      value: 'R 32.8B'
    },
    {
      id: 3,
      name: 'CryptoVault International',
      type: 'DIGITAL_ASSET',
      covenant: 'PENDING',
      health: 82,
      lastAudit: '2026-03-10',
      compliance: ['SOC2'],
      value: 'R 18.5B'
    },
    {
      id: 4,
      name: 'African Development Consortium',
      type: 'DEVELOPMENT',
      covenant: 'ACTIVE',
      health: 100,
      lastAudit: '2026-03-16',
      compliance: ['POPIA', 'GDPR'],
      value: 'R 27.3B'
    },
  ]);

  const [selectedClient, setSelectedClient] = useState(null);

  const getHealthColor = (health) => {
    if (health >= 95) return 'bg-emerald-500'; // For 98%, 95%, 100%
    if (health >= 85) return 'bg-gold';
    if (health >= 70) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getHealthTextColor = (health) => {
    if (health >= 95) return 'text-emerald-500';
    if (health >= 85) return 'text-gold';
    if (health >= 70) return 'text-orange-500';
    return 'text-red-500';
  };

  return (
    <div className="space-y-6" data-testid="client-covenant-container">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-gold text-lg font-black tracking-[4px] uppercase flex items-center gap-3" data-testid="covenant-header">
            <Briefcase size={20} className="text-gold" data-testid="covenant-icon" />
            CLIENT COVENANT BOARD
          </h2>
          <p className="text-stone-600 text-[0.65rem] font-black tracking-[3px] mt-2 uppercase" data-testid="covenant-subheader">
            COVENANT INTEGRITY MONITOR • REAL-TIME COMPLIANCE
          </p>
        </div>
        <div className="flex gap-3">
          <button
            className="px-6 py-3 bg-gold/10 border border-gold/30 text-gold text-[0.65rem] font-black tracking-[3px] uppercase rounded-sm hover:bg-gold/20 transition-all"
            data-testid="establish-covenant-btn"
          >
            ESTABLISH COVENANT
          </button>
          <button
            className="px-6 py-3 border border-stone-800 text-stone-400 text-[0.65rem] font-black tracking-[3px] uppercase rounded-sm hover:border-stone-700 transition-all"
            data-testid="audit-all-btn"
          >
            AUDIT ALL
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-4 gap-4" data-testid="stats-grid">
        <div className="bg-gradient-to-br from-[#0A0A0A] to-black border border-gold/10 rounded-lg p-5" data-testid="stat-total-clients">
          <div className="text-stone-600 text-[0.55rem] font-black tracking-[3px] uppercase mb-2">
            TOTAL CLIENTS
          </div>
          <div className="text-3xl font-black text-white font-mono" data-testid="total-clients-value">
            {clients.length}
          </div>
          <div className="text-emerald-500 text-[0.6rem] mt-2" data-testid="total-clients-trend">
            +1 this quarter
          </div>
        </div>
        <div className="bg-gradient-to-br from-[#0A0A0A] to-black border border-gold/10 rounded-lg p-5" data-testid="stat-active-covenants">
          <div className="text-stone-600 text-[0.55rem] font-black tracking-[3px] uppercase mb-2">
            ACTIVE COVENANTS
          </div>
          <div className="text-3xl font-black text-emerald-500 font-mono" data-testid="active-covenants-value">
            {clients.filter(c => c.covenant === 'ACTIVE').length}
          </div>
          <div className="text-stone-500 text-[0.6rem] mt-2" data-testid="active-covenants-percent">
            {Math.round((clients.filter(c => c.covenant === 'ACTIVE').length / clients.length) * 100)}% of total
          </div>
        </div>
        <div className="bg-gradient-to-br from-[#0A0A0A] to-black border border-gold/10 rounded-lg p-5" data-testid="stat-total-value">
          <div className="text-stone-600 text-[0.55rem] font-black tracking-[3px] uppercase mb-2">
            TOTAL VALUE
          </div>
          <div className="text-2xl font-black text-gold font-mono" data-testid="total-value-amount">
            R 123.8B
          </div>
          <div className="text-stone-500 text-[0.6rem] mt-2" data-testid="total-value-label">
            Assets under covenant
          </div>
        </div>
        <div className="bg-gradient-to-br from-[#0A0A0A] to-black border border-gold/10 rounded-lg p-5" data-testid="stat-compliance-rate">
          <div className="text-stone-600 text-[0.55rem] font-black tracking-[3px] uppercase mb-2">
            COMPLIANCE RATE
          </div>
          <div className="text-3xl font-black text-emerald-500 font-mono" data-testid="compliance-rate-value">
            98%
          </div>
          <div className="text-stone-500 text-[0.6rem] mt-2" data-testid="compliance-rate-label">
            Above threshold
          </div>
        </div>
      </div>

      {/* Client Grid */}
      <div className="grid grid-cols-2 gap-4" data-testid="clients-grid">
        {clients.map((client) => (
          <div
            key={client.id}
            className="bg-gradient-to-br from-[#0A0A0A] to-black border border-gold/10 rounded-lg p-6 hover:border-gold/30 transition-all cursor-pointer group"
            onClick={() => setSelectedClient(client)}
            data-testid={`client-${client.id}`}
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-white text-lg font-black mb-1" data-testid={`client-${client.id}-name`}>
                  {client.name}
                </h3>
                <span className="text-[0.55rem] text-stone-500 font-black tracking-[3px] uppercase" data-testid={`client-${client.id}-type`}>
                  {client.type}
                </span>
              </div>
              <div className={`px-3 py-1 rounded-sm text-[0.55rem] font-black tracking-wider ${
                client.covenant === 'ACTIVE'
                  ? 'bg-emerald-500/20 text-emerald-500 border border-emerald-500/30'
                  : 'bg-gold/20 text-gold border border-gold/30'
              }`} data-testid={`client-${client.id}-covenant`}>
                {client.covenant}
              </div>
            </div>

            <div className="space-y-3">
              {/* Health Meter */}
              <div data-testid={`client-${client.id}-health`}>
                <div className="flex justify-between text-[0.55rem] mb-1">
                  <span className="text-stone-500" data-testid={`client-${client.id}-health-label`}>COVENANT HEALTH</span>
                  <span className={getHealthTextColor(client.health)} data-testid={`client-${client.id}-health-value`}>
                    {client.health}%
                  </span>
                </div>
                <div className="h-1.5 bg-stone-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${getHealthColor(client.health)}`}
                    style={{ width: `${client.health}%` }}
                    data-testid={`client-${client.id}-health-bar`}
                  />
                </div>
              </div>

              {/* Compliance Tags */}
              <div className="flex gap-2" data-testid={`client-${client.id}-compliance`}>
                {client.compliance.map((cert) => (
                  <span
                    key={cert}
                    className="px-2 py-1 bg-stone-800 text-stone-400 text-[0.45rem] font-black rounded-sm"
                    data-testid={`client-${client.id}-compliance-${cert}`}
                  >
                    {cert}
                  </span>
                ))}
              </div>

              {/* Footer Info */}
              <div className="flex justify-between items-center pt-2 border-t border-white/5">
                <div className="flex items-center gap-2">
                  <Clock size={12} className="text-stone-600" data-testid={`client-${client.id}-clock`} />
                  <span className="text-[0.5rem] text-stone-500" data-testid={`client-${client.id}-last-audit`}>
                    Last Audit: {client.lastAudit}
                  </span>
                </div>
                <div className="text-gold text-[0.6rem] font-mono" data-testid={`client-${client.id}-value`}>
                  {client.value}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Selected Client Details */}
      {selectedClient && (
        <div className="bg-gradient-to-br from-[#0A0A0A] to-black border border-gold/10 rounded-lg p-6" data-testid="selected-client-details">
          <h3 className="text-gold text-[0.7rem] font-black tracking-[3px] uppercase mb-4 flex items-center gap-2" data-testid="selected-client-header">
            <FileText size={14} />
            COVENANT DETAILS: {selectedClient.name}
          </h3>
          <div className="grid grid-cols-3 gap-6">
            <div data-testid="selected-client-anchor">
              <div className="text-stone-600 text-[0.55rem] font-black tracking-[3px] uppercase mb-2">ANCHOR HASH</div>
              <div className="text-[0.6rem] text-white font-mono bg-black/50 p-2 rounded border border-stone-800" data-testid="selected-client-hash">
                0x7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069
              </div>
            </div>
            <div data-testid="selected-client-validation">
              <div className="text-stone-600 text-[0.55rem] font-black tracking-[3px] uppercase mb-2">VALIDATION STATUS</div>
              <div className="flex items-center gap-2 text-emerald-500" data-testid="selected-client-status">
                <CheckCircle size={14} />
                <span className="text-[0.6rem] font-black">CRYPTOGRAPHICALLY VERIFIED</span>
              </div>
            </div>
            <div data-testid="selected-client-next-audit">
              <div className="text-stone-600 text-[0.55rem] font-black tracking-[3px] uppercase mb-2">NEXT AUDIT</div>
              <div className="text-[0.6rem] text-gold font-mono" data-testid="selected-client-next-audit-date">
                2026-04-01 00:00 UTC
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sovereign_Client_Covenant;
