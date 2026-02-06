/**
 * File: client/src/features/dashboard/pages/DashboardWrapper.jsx
 * Path: client/src/features/dashboard/pages/DashboardWrapper.jsx
 * STATUS: PRODUCTION-READY | EPITOME | DASHBOARD WRAPPER
 * VERSION: 2026-01-14
 *
 * PURPOSE
 * - Top-level dashboard wrapper for Wilsy OS.
 * - Orchestrates data fetching, tenant scoping, RBAC gating, audit events,
 *   error handling, and renders child dashboard components (stats, charts, feed).
 *
 * COLLABORATION & OWNERSHIP (MANDATORY)
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - PRIMARY OWNER: @frontend-team (UI, accessibility, performance)
 * - BACKEND OWNER: @backend-team (endpoints: /api/admin/stats, /api/auth/switch-tenant)
 * - SECURITY OWNER: @security (RBAC, PII redaction, telemetry)
 * - SRE OWNER: @sre (caching, read-replica routing)
 * - QA OWNER: @qa (integration & contract tests)
 *
 * REVIEW CHECKLIST (PRE-MERGE)
 * - @frontend-team: confirm component imports and CSS modules exist.
 * - @backend-team: confirm /api/admin/stats and /api/auth/switch-tenant contract.
 * - @security: review that no PII is rendered in the UI and audit events are redacted.
 * - @qa: add tests for tenant switch, role gating, and error states.
 *
 * NOTES
 * - This component expects `fetchJson` helper at client/src/utils/fetch.js.
 * - Uses `useAuthStore` (client/src/store/authStore.js) for auth and tenant context.
 * - Emits client-side audit events via optional global `WilsyAudit.log` hook.
 * - Keep UI logic minimal; heavy aggregation and sensitive decisions are server-side.
 *
 * TODO (short)
 * - Add lazy-loaded chart components and skeletons.
 * - Add feature-flag gating for experimental widgets.
 * - Add accessibility audit and keyboard navigation tests.
 */

import React, { useEffect, useState, useCallback } from 'react';
import PropTypes from 'prop-types';
import useAuthStore from '../../../store/authStore';
import { fetchJson } from '../../../utils/fetch';
import Spinner from '../../../components/Spinner';
import ErrorBox from '../../../components/ErrorBox';
import StatsGrid from '../components/StatsGrid';
import AuditFeed from '../components/AuditFeed';
import TenantSelector from '../../../components/TenantSelector';
import ChartPlaceholder from '../components/ChartPlaceholder';
import './DashboardWrapper.css'; // ensure styles exist

/* Helper: emit client audit events (non-blocking) */
function emitClientAudit(eventType, metadata = {}) {
  try {
    if (typeof window !== 'undefined' && window.WilsyAudit && typeof window.WilsyAudit.log === 'function') {
      window.WilsyAudit.log(eventType, metadata);
    }
  } catch {
    // swallow to avoid UI impact
  }
}

/* Default empty stats shape */
const EMPTY_STATS = {
  mrr: 0,
  tenants: 0,
  docs: 0,
  users: 0,
  latency: null
};

/**
 * DashboardWrapper
 * - Fetches dashboard stats and recent audit logs.
 * - Supports tenant switching and role-based rendering.
 */
export default function DashboardWrapper({ initialTenantId = null }) {
  const { user, token, refreshUser, switchTenant, getAuthHeaders } = useAuthStore();
  const [stats, setStats] = useState(EMPTY_STATS);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tenantId, setTenantId] = useState(initialTenantId || (user && user.tenantId) || null);
  const [isSwitching, setIsSwitching] = useState(false);

  const isAdmin = (user && (user.role === 'SUPER_ADMIN' || user.role === 'TENANT_ADMIN'));

  const correlationId = React.useMemo(() => `dash_${Date.now()}_${Math.floor(Math.random() * 10000)}`, []);

  /* Fetch dashboard stats (server-side aggregation) */
  const fetchStats = useCallback(async (signal) => {
    setLoading(true);
    setError(null);
    try {
      const headers = getAuthHeaders();
      // include tenant context if present
      const url = tenantId ? `/api/admin/stats?tenantId=${encodeURIComponent(tenantId)}` : '/api/admin/stats';
      const data = await fetchJson(url, { method: 'GET', headers, signal });
      // Defensive: normalize shape
      const payload = data && data.stats ? data.stats : {};
      setStats({
        mrr: Number(payload.mrr || 0),
        tenants: Number(payload.tenants || 0),
        docs: Number(payload.docs || 0),
        users: Number(payload.users || 0),
        latency: payload.latency || null
      });
      setLogs(Array.isArray(data.logs) ? data.logs : []);
      emitClientAudit('DASHBOARD.VIEW', { correlationId, tenantId });
    } catch (err) {
      if (err.name === 'AbortError') return;
      setError(err.message || 'Failed to load dashboard');
      emitClientAudit('DASHBOARD.ERROR', { correlationId, error: err.message, tenantId });
    } finally {
      setLoading(false);
    }
  }, [tenantId, getAuthHeaders, correlationId]);

  useEffect(() => {
    const controller = new AbortController();
    fetchStats(controller.signal);
    // Polling: refresh every 30s for live feed (configurable)
    const interval = setInterval(() => fetchStats(controller.signal), 30000);
    return () => {
      controller.abort();
      clearInterval(interval);
    };
  }, [fetchStats]);

  /* Tenant switch handler (UI-level convenience) */
  const handleTenantSwitch = async (newTenantId) => {
    if (!newTenantId || newTenantId === tenantId) return;
    setIsSwitching(true);
    setError(null);
    try {
      // Use store helper which calls server and rotates token if supported
      const result = await switchTenant(newTenantId);
      // refresh local user context
      await refreshUser();
      setTenantId(newTenantId);
      emitClientAudit('DASHBOARD.TENANT_SWITCH', { correlationId, tenantId: newTenantId });
      // refetch stats for new tenant
      await fetchStats();
    } catch (err) {
      setError(err.message || 'Tenant switch failed');
      emitClientAudit('DASHBOARD.TENANT_SWITCH_FAILED', { correlationId, error: err.message, tenantId: newTenantId });
      throw err;
    } finally {
      setIsSwitching(false);
    }
  };

  /* Render helpers */
  const renderHeader = () => (
    <header className="dashboard-header">
      <div className="dashboard-title">
        <h1>Dashboard</h1>
        <p className="muted">Overview of tenants, revenue, documents and activity</p>
      </div>
      <div className="dashboard-controls">
        <TenantSelector
          currentTenant={tenantId}
          tenants={user && user.tenants ? user.tenants : []}
          onSwitch={handleTenantSwitch}
          disabled={!isAdmin || isSwitching}
        />
      </div>
    </header>
  );

  const renderBody = () => {
    if (loading) return <Spinner message="Loading dashboard…" />;

    if (error) return <ErrorBox title="Dashboard error" message={error} onRetry={() => fetchStats()} />;

    return (
      <main className="dashboard-main">
        <section className="dashboard-stats">
          <StatsGrid stats={stats} />
        </section>

        <section className="dashboard-charts">
          {/* Charts are lazy-loaded components; placeholders used until implemented */}
          <div className="chart-row">
            <ChartPlaceholder title="MRR Trend" subtitle="Monthly recurring revenue" />
            <ChartPlaceholder title="Document Volume" subtitle="Documents created by tenant" />
          </div>
        </section>

        <section className="dashboard-audit">
          <h2>Recent Audit Events</h2>
          <AuditFeed logs={logs} />
        </section>
      </main>
    );
  };

  return (
    <div className="dashboard-wrapper" data-correlation-id={correlationId}>
      {renderHeader()}
      {renderBody()}
    </div>
  );
}

DashboardWrapper.propTypes = {
  initialTenantId: PropTypes.string
};
