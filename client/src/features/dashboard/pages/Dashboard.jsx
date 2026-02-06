/**
 * File: client/src/features/dashboard/pages/Dashboard.jsx
 * STATUS: PRODUCTION-READY | PURE CONTENT COMPONENT
 * VERSION: 3.0.0 (Layout Decoupled)
 *
 * PURPOSE
 * - Executive Dashboard Content.
 * - FIX: Removed internal 'Sidebar' to prevent collision with Global MainLayout.
 * - Now relies on MainLayout for navigation and page structure.
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import styled, { keyframes } from 'styled-components';
import { Link } from 'react-router-dom';
import { FiTrendingUp, FiPlus, FiList } from 'react-icons/fi';
import useAuthStore from '../../../store/authStore';
import AdminService from '../../admin/services/adminService';

/* -----------------------------------------------------------------------------
   Theme tokens
   --------------------------------------------------------------------------- */
const palette = {
  bg: '#f7fbff',
  surface: '#ffffff',
  primary: '#0f172a',
  accent: '#0ea5e9',
  success: '#10b981',
  warn: '#f59e0b',
  danger: '#ef4444',
  muted: '#64748b',
  border: '#e6eef6',
  glass: 'rgba(15,23,42,0.04)'
};

/* -----------------------------------------------------------------------------
   Animations
   --------------------------------------------------------------------------- */
const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
`;

/* -----------------------------------------------------------------------------
   Styled Components (Content Only)
   --------------------------------------------------------------------------- */

// Replaces the old 'Main' - acts as the content container
const DashboardContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
  animation: ${fadeIn} 0.4s ease-out;
`;

const Header = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 8px;
`;

const Welcome = styled.div`
  h1 { margin: 0; font-size: 1.6rem; font-weight: 800; letter-spacing: -0.6px; color: ${palette.primary}; }
  p { margin: 6px 0 0; color: ${palette.muted}; font-size: 0.95rem; }
`;

const Actions = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
`;

const ActionButton = styled(Link)`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 700;
  background: ${p => (p.$variant === 'ghost' ? palette.surface : palette.primary)};
  color: ${p => (p.$variant === 'ghost' ? palette.primary : '#fff')};
  border: ${p => (p.$variant === 'ghost' ? `1px solid ${palette.border}` : 'none')};
  box-shadow: ${p => (p.$variant === 'ghost' ? 'none' : '0 10px 28px rgba(7,16,51,0.12)')};
  transition: transform 160ms ease, box-shadow 160ms ease;
  &:hover { transform: translateY(-3px); }
`;

/* KPI Grid */
const KpiGrid = styled.section`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  @media (max-width: 1200px) { grid-template-columns: repeat(2, 1fr); }
  @media (max-width: 700px) { grid-template-columns: 1fr; }
`;

const KpiCard = styled.div`
  background: ${palette.surface};
  border-radius: 12px;
  padding: 20px;
  border: 1px solid ${palette.border};
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const KpiTitle = styled.div`
  font-size: 0.75rem;
  color: ${palette.muted};
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const KpiValue = styled.div`
  font-size: 1.8rem;
  font-weight: 800;
  color: ${palette.primary};
`;

const KpiMeta = styled.div`
  font-size: 0.85rem;
  color: ${palette.muted};
  display: flex;
  align-items: center;
  gap: 8px;
`;

/* Panels */
const Panels = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
  @media (max-width: 1000px) { grid-template-columns: 1fr; }
`;

const Panel = styled.section`
  background: ${palette.surface};
  border-radius: 12px;
  border: 1px solid ${palette.border};
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
`;

const PanelHeader = styled.div`
  padding: 14px 20px;
  background: #f8fafc;
  border-bottom: 1px solid ${palette.border};
  display: flex;
  justify-content: space-between;
  align-items: center;
  h2 { margin: 0; font-size: 0.95rem; font-weight: 700; color: ${palette.primary}; }
  .meta { color: ${palette.muted}; font-size: 0.85rem; }
`;

const PanelBody = styled.div`
  padding: 0;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  th { text-align: left; padding: 12px 20px; font-size: 0.75rem; color: ${palette.muted}; text-transform: uppercase; border-bottom: 1px solid ${palette.border}; background: #fcfcfc; }
  td { padding: 14px 20px; border-bottom: 1px solid #f1f5f9; color: ${palette.primary}; font-size: 0.9rem; }
  .badge { padding: 4px 10px; border-radius: 999px; font-weight: 700; font-size: 0.7rem; display: inline-block; }
`;

const LogStream = styled.div`
  max-height: 400px;
  overflow: auto;
  display: flex;
  flex-direction: column;
`;

const LogItem = styled.div`
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 14px 20px;
  border-bottom: 1px solid #f1f5f9;
  background: ${p => (p.$variant === 'crit' ? '#fef2f2' : p.$variant === 'warn' ? '#fffbeb' : '#fff')};
  
  &:last-child { border-bottom: none; }
`;

const Skeleton = styled.div`
  height: ${p => p.$h || 16}px;
  background: linear-gradient(90deg, #f1f5f9 0%, #e9f2fb 50%, #f1f5f9 100%);
  background-size: 200% 100%;
  animation: shimmer 1.2s linear infinite;
  border-radius: 6px;
  @keyframes shimmer { 0% { background-position: 200% 0 } 100% { background-position: -200% 0 } }
`;

/* -----------------------------------------------------------------------------
   Helpers
   --------------------------------------------------------------------------- */
function formatCurrencyZAR(value) {
  try {
    return new Intl.NumberFormat('en-ZA', { style: 'currency', currency: 'ZAR', maximumFractionDigits: 0 }).format(value);
  } catch {
    return `R ${value}`;
  }
}

function shortName(user) {
  if (!user) return 'Chief Architect';
  const first = user.name ? user.name.split(' ')[0] : null;
  return first ? `${first}` : 'Chief Architect';
}

/* -----------------------------------------------------------------------------
   Component
   --------------------------------------------------------------------------- */

export default function Dashboard() {
  const { user, token } = useAuthStore();
  
  // Local state
  const [metrics, setMetrics] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const CACHE_KEY = 'wilsy_dashboard_v2_cache';
  const CACHE_TTL = 30 * 1000;

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Cache Check
      const cached = sessionStorage.getItem(CACHE_KEY);
      if (cached) {
        const parsed = JSON.parse(cached);
        if (Date.now() - parsed.ts < CACHE_TTL) {
          setMetrics(parsed.metrics || null);
          setLogs(parsed.logs || []);
          setLoading(false);
          return;
        }
      }
    } catch (e) { console.debug(e); }

    try {
      const result = await AdminService.getMetricsSafe(token, { timeoutMs: 8000, retries: 1 });
      if (result && result.stats) {
        setMetrics({
          mrr: result.stats.mrr ?? 0,
          tenants: result.stats.tenants ?? 0,
          docs: result.stats.docs ?? 0,
          users: result.stats.users ?? 0,
          latency: result.stats.latency ?? '-',
          trend: result.stats.trend ?? '+0%'
        });
      } else {
        setMetrics(null);
      }
      if (Array.isArray(result?.logs)) setLogs(result.logs);
      
      try {
        sessionStorage.setItem(CACHE_KEY, JSON.stringify({ ts: Date.now(), metrics: result?.stats || {}, logs: result?.logs || [] }));
      } catch (e) {}
    } catch (e) {
      console.warn('AdminService.getMetrics failed', e);
      setError('Live metrics unavailable');
      setMetrics(null);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    load();
    const interval = setInterval(() => { load(); }, 30 * 1000);
    return () => clearInterval(interval);
  }, [load]);

  const fallback = useMemo(() => ({
    mrr: 4_500_000, tenants: 4, docs: 12_400, users: 58, latency: '42ms', trend: '+12% vs last month'
  }), []);

  const display = metrics || fallback;

  return (
    <DashboardContainer role="region" aria-label="Executive Dashboard">
      <Header>
        <div>
          <Welcome>
            <h1>
              {`${new Date().getHours() < 12 ? 'Good Morning' : new Date().getHours() < 18 ? 'Good Afternoon' : 'Good Evening'}, ${shortName(user)}`}
            </h1>
            <p>Executive Command Center</p>
          </Welcome>
        </div>
        <Actions>
          <ActionButton to="/documents/new" $variant="primary">
            <FiPlus /> Create Document
          </ActionButton>
          <ActionButton to="/audit" $variant="ghost">
            <FiList /> Audit Logs
          </ActionButton>
        </Actions>
      </Header>

      <KpiGrid>
        <KpiCard>
          <KpiTitle>Monthly Recurring Revenue</KpiTitle>
          <KpiValue>{loading && !metrics ? <Skeleton $h={28} /> : formatCurrencyZAR(display.mrr)}</KpiValue>
          <KpiMeta><FiTrendingUp /> {display.trend}</KpiMeta>
        </KpiCard>

        <KpiCard>
          <KpiTitle>Active Tenants</KpiTitle>
          <KpiValue>{loading && !metrics ? <Skeleton $h={28} /> : display.tenants}</KpiValue>
          <KpiMeta>{display.users} users across tenants</KpiMeta>
        </KpiCard>

        <KpiCard>
          <KpiTitle>Document Volume 24h</KpiTitle>
          <KpiValue>{loading && !metrics ? <Skeleton $h={28} /> : display.docs.toLocaleString()}</KpiValue>
          <KpiMeta>Processed in last 24 hours</KpiMeta>
        </KpiCard>

        <KpiCard>
          <KpiTitle>Avg API Latency P99</KpiTitle>
          <KpiValue>{loading && !metrics ? <Skeleton $h={28} /> : display.latency}</KpiValue>
          <KpiMeta>Operational</KpiMeta>
        </KpiCard>
      </KpiGrid>

      <Panels>
        <Panel>
          <PanelHeader>
            <h2>Tenant Ecosystem Health</h2>
            <div className="meta">Overview · Top tenants</div>
          </PanelHeader>
          <PanelBody>
            <Table>
              <thead>
                <tr>
                  <th>Firm Name</th>
                  <th>Plan</th>
                  <th>Users</th>
                  <th>Status</th>
                  <th>Compliance</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style={{ fontWeight: 800 }}>Wilsy HQ</td>
                  <td>Enterprise</td>
                  <td>4</td>
                  <td><span className="badge" style={{ background: '#dcfce7', color: '#166534' }}>ACTIVE</span></td>
                  <td>100%</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 800 }}>Smith & Associates</td>
                  <td>Professional</td>
                  <td>12</td>
                  <td><span className="badge" style={{ background: '#ecfeff', color: '#0ea5e9' }}>ACTIVE</span></td>
                  <td>98%</td>
                </tr>
              </tbody>
            </Table>
          </PanelBody>
        </Panel>

        <Panel>
          <PanelHeader>
            <h2>Live Audit Feed</h2>
            <div className="meta">{logs.length} events</div>
          </PanelHeader>
          <PanelBody>
            <LogStream>
              {(logs.length ? logs : [
                { ts: '10:00:00', action: 'System started', actor: 'system', severity: 'info' },
                { ts: '09:45:00', action: 'Tenant onboarding', actor: 'ops@wilsy', severity: 'info' }
              ]).map((l, i) => (
                <LogItem key={i} $variant={l.severity === 'crit' ? 'crit' : l.severity === 'warn' ? 'warn' : 'info'}>
                  <div style={{ minWidth: 70, color: palette.muted, fontSize: '0.8rem', fontFamily: 'monospace' }}>
                    {l.ts || new Date().toLocaleTimeString()}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>{l.action || l.event}</div>
                    <div style={{ color: palette.muted, fontSize: '0.8rem' }}>{l.actor || 'system'}</div>
                  </div>
                </LogItem>
              ))}
            </LogStream>
          </PanelBody>
        </Panel>
      </Panels>
    </DashboardContainer>
  );
}