/* eslint-disable */
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — Cockpit Status Bar
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           client/src/components/sovereign/CockpitStatusBar.jsx
 * Version:        v1.0.0-INSTITUTIONAL-SEAL
 * Authority:      Wilsy OS Core Governance
 * Epitome:        The living head‑up display (HUD) for the Founder Cockpit.
 *                 Displays real‑time Kennel health, active module context,
 *                 system telemetry, and quick command access—transforming the
 *                 dashboard into a dynamic, award‑winning command surface.
 * Classification: Production Artifact
 *
 * Contributors:
 *   - Wilson Khanyezi (CEO/Lead Architect) — Mandated zero‑loss observability
 *     and institutional‑grade real‑time intelligence.
 *   - AI Engineering — RECTIFIED: Produced this artifact under Sovereign Mandate v3.1.0
 *     as the pinnacle component of the Wilsy OS Living Cockpit.
 *
 * Change Log:
 *   2026-07-31 v1.0.0-INSTITUTIONAL-SEAL — Initial certified release.
 *
 * Forensic Relationships:
 *   Upstream:   react, lucide-react, ../../hooks/useKennelHealth
 *   Downstream: client/src/components/sovereign/FounderDashboard.jsx
 *   Shared Crypto / Events / Config: useKennelHealth hook, api service,
 *               X-Wilsy-Bridge: kernel-v1.1.1, PORT 4000, PORT 9095.
 *
 * Certification Seal: PRODUCTION_READY_v1.0.0-INSTITUTIONAL-SEAL
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import React from 'react';
import {
  Activity,
  Cpu,
  Database,
  Radio,
  Bell,
  User,
  Command,
  ChevronDown,
  CheckCircle,
  AlertCircle,
  XCircle,
} from 'lucide-react';
import { useKennelHealth } from '../../hooks/useKennelHealth';

/**
 * @component CockpitStatusBar
 * @description The top‑bar HUD for the Founder Dashboard, displaying real‑time
 *              Kennel health, module context, system telemetry, and quick actions.
 * @param {Object} props - Component properties.
 * @param {Object} props.activeModule - The currently active module metadata (label, layer, description).
 * @param {Object} props.osSpine - The operating system spine metrics (workers, latency, realDataRatio, mounted, commandCount).
 * @param {Function} props.onOpenCommandPalette - Callback to open the command palette.
 * @param {Function} props.onToggleNotifications - Callback to toggle the notification panel.
 * @param {Function} props.onToggleFounderPanel - Callback to toggle the founder profile panel.
 * @param {number} props.unreadCount - Number of unread notifications.
 * @param {string} props.founderInitials - Initials of the founder for display.
 * @param {string} props.founderName - Display name of the founder.
 * @returns {JSX.Element} The rendered Cockpit Status Bar.
 */
const CockpitStatusBar = ({
  activeModule,
  osSpine,
  onOpenCommandPalette,
  onToggleNotifications,
  onToggleFounderPanel,
  unreadCount = 0,
  founderInitials = 'WK',
  founderName = 'Wilson Khanyezi',
}) => {
  const kennelHealth = useKennelHealth();

  // Determine status color and label
  const getKennelStatus = (status) => {
    switch (status) {
      case 'online':
        return { color: '#10b981', label: 'CONNECTED', icon: CheckCircle };
      case 'degraded':
        return { color: '#f59e0b', label: 'DEGRADED', icon: AlertCircle };
      case 'offline':
        return { color: '#ef4444', label: 'OFFLINE', icon: XCircle };
      default:
        return { color: '#6b7280', label: 'UNKNOWN', icon: Activity };
    }
  };

  const status = getKennelStatus(kennelHealth.status);
  const StatusIcon = status.icon;

  return (
    <div className="cockpit-status-bar" style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 30px',
      background: 'var(--wilsy-surface, #070B18)',
      borderBottom: '1px solid var(--wilsy-border, rgba(212,175,55,0.15))',
      minHeight: '56px',
      flexShrink: 0,
      fontFamily: 'var(--font-mono, monospace)',
      fontSize: '0.65rem',
    }}>
      {/* LEFT: Kennel Health & Module Path */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '24px', flexShrink: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <StatusIcon size={14} color={status.color} />
          <span style={{ color: status.color, fontWeight: 900, letterSpacing: '0.5px' }}>
            KENNEL: {status.label}
          </span>
          {kennelHealth.version && (
            <span style={{ color: '#888', fontWeight: 400, fontSize: '0.55rem' }}>
              v{kennelHealth.version}
            </span>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#aaa' }}>
          <span style={{ color: '#D4AF37', fontWeight: 700 }}>{activeModule?.layer || 'SOVEREIGN'}</span>
          <span>→</span>
          <strong style={{ color: '#fff', fontWeight: 900, letterSpacing: '0.3px' }}>
            {activeModule?.label || 'WORKSPACE'}
          </strong>
        </div>
      </div>

      {/* CENTER: Live Metrics */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '18px', color: '#888' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Cpu size={12} /> Workers: <strong style={{ color: '#fff' }}>{osSpine?.workers || 0}</strong>
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Activity size={12} /> Latency: <strong style={{ color: '#fff' }}>{osSpine?.latency || 0}ms</strong>
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Database size={12} /> Real Data: <strong style={{ color: '#D4AF37' }}>{osSpine?.realDataRatio || 0}%</strong>
        </span>
      </div>

      {/* RIGHT: Actions & Profile */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexShrink: 0 }}>
        {/* Command Palette */}
        <button
          onClick={onOpenCommandPalette}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '6px 12px',
            borderRadius: '20px',
            border: '1px solid rgba(212,175,55,0.25)',
            background: 'rgba(0,0,0,0.3)',
            color: '#ccc',
            fontSize: '0.6rem',
            cursor: 'pointer',
            transition: 'all 0.2s',
            fontFamily: 'inherit',
          }}
          onMouseEnter={(e) => e.currentTarget.style.borderColor = '#D4AF37'}
          onMouseLeave={(e) => e.currentTarget.style.borderColor = 'rgba(212,175,55,0.25)'}
        >
          <Command size={14} />
          <span style={{ opacity: 0.7 }}>⌘K</span>
        </button>

        {/* Notifications */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={onToggleNotifications}
            style={{
              position: 'relative',
              background: 'transparent',
              border: 'none',
              color: '#aaa',
              cursor: 'pointer',
              padding: '4px',
              transition: 'color 0.2s',
            }}
          >
            <Bell size={18} />
            {unreadCount > 0 && (
              <span style={{
                position: 'absolute',
                top: '-4px',
                right: '-6px',
                background: '#ef4444',
                color: '#fff',
                fontSize: '0.5rem',
                fontWeight: 900,
                padding: '2px 6px',
                borderRadius: '12px',
                minWidth: '18px',
                textAlign: 'center',
                animation: 'pulseDot 1.5s infinite',
              }}>
                {unreadCount > 99 ? '99+' : unreadCount}
              </span>
            )}
          </button>
        </div>

        {/* Founder Profile */}
        <button
          onClick={onToggleFounderPanel}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            background: 'transparent',
            border: 'none',
            color: '#fff',
            cursor: 'pointer',
            padding: '4px 8px 4px 4px',
            borderRadius: '24px',
            transition: 'all 0.2s',
          }}
          onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(212,175,55,0.1)'}
          onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
        >
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            display: 'grid',
            placeItems: 'center',
            background: 'linear-gradient(135deg, #D4AF37, #8E6A12)',
            color: '#000',
            fontWeight: 900,
            fontSize: '0.75rem',
          }}>
            {founderInitials}
          </div>
          <span style={{ fontSize: '0.75rem', fontWeight: 500, color: '#eee' }}>
            {founderName}
          </span>
          <ChevronDown size={14} style={{ opacity: 0.6 }} />
        </button>
      </div>

      <style>{`
        @keyframes pulseDot {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(1.2); }
        }
      `}</style>
    </div>
  );
};

export default CockpitStatusBar;
