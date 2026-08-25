/* eslint-disable */
/**
 * =============================================================================
 * Wilsy OS — Statement Engine
 * =============================================================================
 * File:           client/src/components/billing/StatementEngine.jsx
 * Version:        v2.1.0-ENTERPRISE-PDF
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Period statements — retrieve, seal, export, email, print, verify.
 *                 Latency + SHA3-512 seal in status bar. Tenant isolation.
 * Classification: Production Artifact
 *
 * Change Log:
 *   2026-08-05 v2.1.0-ENTERPRISE-PDF — Email/print/download/PDF; latency; a11y.
 *   2026-08-05 v1.0.0-STATEMENT-FOUNDATION — Initial retrieve/seal/export.
 * =============================================================================
 */

import React, { useCallback, useMemo, useState } from 'react';
import {
  RefreshCw,
  FileText,
  ShieldCheck,
  Download,
  Search,
  BadgeCheck,
  AlertTriangle,
  Mail,
  Printer,
  Clock
} from 'lucide-react';
import sovereignClient from '../../utils/sovereignClient';
import styles from './StatementEngine.module.css';

const PERIODS = [
  { id: 'month', label: 'Month' },
  { id: 'quarter', label: 'Quarter' },
  { id: 'half-year', label: 'Half-year' },
  { id: 'year', label: 'Year' }
];

const SCOPES = [
  { id: 'PLATFORM', label: 'Platform statements' },
  { id: 'TENANT_CLIENT', label: 'Tenant → client statements' }
];

function formatMoney(amount = 0, currency = 'ZAR') {
  try {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: currency || 'ZAR',
      minimumFractionDigits: 2
    }).format(Number(amount || 0));
  } catch {
    return `R ${Number(amount || 0).toFixed(2)}`;
  }
}

function formatDate(value) {
  if (!value) return '—';
  const d = new Date(value);
  return Number.isNaN(d.getTime())
    ? String(value)
    : d.toLocaleDateString('en-ZA', { year: 'numeric', month: 'short', day: '2-digit' });
}

/**
 * @function StatementEngine
 * @param {Object} props
 * @param {string} props.tenantId
 * @param {string} [props.clientId]
 * @param {'PLATFORM'|'TENANT_CLIENT'} [props.issuerMode]
 * @param {Object} [props.issuerIdentity]
 * @param {string} [props.counterpartyName]
 * @param {Function} [props.onSealed]
 */
export default function StatementEngine({
  tenantId = 'MASTER',
  clientId = '',
  issuerMode = 'PLATFORM',
  issuerIdentity = null,
  counterpartyName = '',
  onSealed = null
}) {
  const [scope, setScope] = useState('PLATFORM');
  const [period, setPeriod] = useState('month');
  const [loading, setLoading] = useState(false);
  const [sealing, setSealing] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [emailing, setEmailing] = useState(false);
  const [printing, setPrinting] = useState(false);
  const [error, setError] = useState(null);
  const [statement, setStatement] = useState(null);
  const [lastAction, setLastAction] = useState(null);
  const [latencyMs, setLatencyMs] = useState(null);

  const tid = String(tenantId || 'MASTER');

  const timed = useCallback(async (fn) => {
    const t0 = performance.now();
    try {
      return await fn();
    } finally {
      setLatencyMs(Math.round(performance.now() - t0));
    }
  }, []);

  const retrieve = useCallback(async () => {
    setLoading(true);
    setError(null);
    setLastAction('retrieve');
    try {
      await timed(async () => {
        if (scope === 'PLATFORM' || scope === 'TENANT_CLIENT') {
          const endpoint = scope === 'PLATFORM'
            ? '/billing/platform/invoices'
            : '/billing/client/invoices';
          const response = await sovereignClient.get(endpoint, {
            params: { limit: 250, offset: 0, sort_by: 'issued_at', sort_order: -1 },
            headers: { 'X-Tenant-ID': tid },
          });
          const payload = response?.data ?? response;
          const invoices = Array.isArray(payload) ? payload : payload?.items || payload?.invoices || [];
          const now = new Date();
          const start = new Date(now);
          if (period === 'month') start.setMonth(now.getMonth() - 1);
          if (period === 'quarter') start.setMonth(now.getMonth() - 3);
          if (period === 'half-year') start.setMonth(now.getMonth() - 6);
          if (period === 'year') start.setFullYear(now.getFullYear() - 1);
          const lineItems = invoices
            .filter((invoice) => {
              const issuedAt = new Date(invoice.issued_at || invoice.issueDate || invoice.created_at || 0);
              return !Number.isNaN(issuedAt.getTime()) && issuedAt >= start && issuedAt <= now;
            })
            .map((invoice) => ({
              invoiceId: invoice.invoice_id || invoice.id || invoice._id,
              invoiceNumber: invoice.invoice_number || invoice.invoiceNumber || invoice.id,
              description: invoice.line_items?.[0]?.description || invoice.description || (
                scope === 'PLATFORM' ? 'Platform invoice' : 'Client invoice'
              ),
              issueDate: invoice.issued_at || invoice.issueDate || invoice.created_at,
              status: invoice.status || 'ISSUED',
              amount: Number(invoice.total_amount ?? invoice.totalAmount ?? invoice.amount ?? 0),
              currency: invoice.currency || 'ZAR',
            }));
          setStatement({
            source: lineItems.length ? 'KENNEL_LEDGER' : 'LIVE_EMPTY',
            pipeline: scope === 'PLATFORM' ? 'PLATFORM' : 'TENANT_CLIENT',
            periodLabel: period,
            startDate: start.toISOString(),
            endDate: now.toISOString(),
            tenantId: tid,
            currency: lineItems[0]?.currency || 'ZAR',
            invoiceCount: lineItems.length,
            totalAmount: lineItems.reduce((total, item) => total + item.amount, 0),
            lineItems,
          });
          setLastAction(lineItems.length ? 'kennel-ledger' : 'LIVE_EMPTY');
          return;
        }
        const params = new URLSearchParams({ tenantId: tid, scope, period });
        if (clientId && scope === 'TENANT_CLIENT') params.set('clientId', String(clientId));
        const res = await sovereignClient.get(`/statements?${params.toString()}`);
        const data = res?.data;
        const item = Array.isArray(data?.items) ? data.items[0] : data?.statement || data;
        setStatement(item || null);
        setLastAction(item?.source || 'retrieved');
      });
    } catch (err) {
      setError(err?.response?.data?.message || err?.message || 'Retrieve failed');
      setStatement(null);
    } finally {
      setLoading(false);
    }
  }, [tid, scope, period, clientId, timed]);

  const seal = useCallback(async () => {
    if (!statement) return;
    setSealing(true);
    setError(null);
    try {
      await timed(async () => {
        const res = await sovereignClient.post('/statements/seal', {
          tenantId: tid,
          clientId: statement.clientId || clientId || '',
          scope,
          period,
          startDate: statement.startDate,
          endDate: statement.endDate,
          statementId: statement._id || statement.statementId
        });
        const sealed = res?.data || {};
        setStatement((prev) =>
          prev
            ? {
              ...prev,
              status: 'SEALED',
              sealHash: sealed.sealHash || prev.sealHash,
              proofHash: sealed.proofHash || prev.proofHash,
              sealedAt: sealed.timestamp || new Date().toISOString()
            }
            : prev
        );
        setLastAction('sealed');
        if (typeof onSealed === 'function') onSealed(sealed);
      });
    } catch (err) {
      setError(err?.response?.data?.message || err?.message || 'Seal failed');
    } finally {
      setSealing(false);
    }
  }, [statement, tid, clientId, scope, period, onSealed, timed]);

  const exportJson = useCallback(async () => {
    if (!statement) return;
    setExporting(true);
    setError(null);
    try {
      await timed(async () => {
        const res = await sovereignClient.post('/statements/export', {
          tenantId: tid,
          format: 'json',
          statement
        });
        const payload = res?.data?.statement || statement;
        const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `WILSY-STMT-${tid}-${period}.json`;
        a.click();
        URL.revokeObjectURL(url);
        setLastAction('exported-json');
      });
    } catch (err) {
      setError(err?.response?.data?.message || err?.message || 'Export failed');
    } finally {
      setExporting(false);
    }
  }, [statement, tid, period, timed]);

  const printStatement = useCallback(async () => {
    if (!statement) return;
    setPrinting(true);
    setError(null);
    try {
      await timed(async () => {
        const payload = {
          type: 'billing-statement',
          artifactType: 'billing-statement',
          title: `Statement ${statement.periodLabel || period}`,
          tenantId: tid,
          issuingEntity: scope === 'TENANT_CLIENT'
            ? (statement.issuingEntity || statement.businessName || issuerIdentity?.name || 'Tenant business')
            : 'Wilsy (Pty) Ltd',
          counterparty:
            statement.counterparty ||
            statement.customerName ||
            counterpartyName ||
            statement.clientId ||
            tid,
          jurisdiction: statement.jurisdiction || 'Republic of South Africa',
          sourcePosture: statement.source || 'SOURCE_LIVE',
          metadata: {
            watermark: 'Wilsy OS – Regulator Copy',
            period: statement.periodLabel || period,
            sealHash: statement.sealHash || statement.proofHash || '',
            statementId: statement._id || statement.statementId,
            issuerMode: scope === 'TENANT_CLIENT' ? 'TENANT_CLIENT' : issuerMode,
            issuerTenantIdentity: scope === 'TENANT_CLIENT'
              ? {
                tenantId: issuerIdentity?.tenantId || tid,
                name: issuerIdentity?.name || statement.businessName || '',
                status: issuerIdentity?.status || ''
              }
              : null,
            print: true
          },
          data: {
            ...statement,
            lineItems: statement.lineItems || []
          }
        };

        const res = await sovereignClient.post('/generate/pdf', payload, {
          responseType: 'blob',
          headers: { 'X-Tenant-ID': tid, Accept: 'application/pdf' }
        });

        const contentType = String(res?.headers?.['content-type'] || '');
        const data = res?.data;

        if (data instanceof Blob && (contentType.includes('json') || data.type === 'application/json')) {
          const text = await data.text();
          let msg = text;
          try { msg = JSON.parse(text)?.message || text; } catch (_) { }
          throw new Error(msg || 'PDF endpoint returned JSON');
        }

        if (!(data instanceof Blob) || data.size < 50) {
          throw new Error('Empty PDF response — check Bearer token and enterprise renderer');
        }

        const url = URL.createObjectURL(data);
        const win = window.open(url, '_blank', 'noopener,noreferrer');
        if (!win) {
          const a = document.createElement('a');
          a.href = url;
          a.download = `WILSY-STMT-${tid}-${period}.pdf`;
          a.click();
        }
        setTimeout(() => URL.revokeObjectURL(url), 120_000);
        setLastAction('print-pdf');
      });
    } catch (err) {
      setError(err?.response?.data?.message || err?.message || 'Print PDF failed');
    } finally {
      setPrinting(false);
    }
  }, [statement, tid, period, scope, issuerMode, issuerIdentity, counterpartyName, timed]);

  const emailStatement = useCallback(async () => {
    if (!statement) return;
    setEmailing(true);
    setError(null);
    try {
      await timed(async () => {
        await sovereignClient.post(
          '/statements/email',
          {
            tenantId: tid,
            statement,
            includeSeal: true,
            sealHash: statement.sealHash || statement.proofHash
          },
          { headers: { 'X-Tenant-ID': tid } }
        );
        setLastAction('emailed');
      });
    } catch (err) {
      setError(err?.response?.data?.message || err?.message || 'Email failed — mount POST /api/statements/email or use export');
    } finally {
      setEmailing(false);
    }
  }, [statement, tid, timed]);

  const lineItems = useMemo(
    () => (Array.isArray(statement?.lineItems) ? statement.lineItems : []),
    [statement]
  );

  const sealSnippet = (statement?.sealHash || statement?.proofHash || '').toString().slice(0, 24);

  return (
    <section className={styles.engine} aria-label="Statement Engine">
      <header className={styles.header}>
        <div className={styles.titleBlock}>
          <FileText size={18} aria-hidden />
          <div>
            <span className={styles.kicker}>Statement Engine</span>
            <h2 className={styles.title}>Retrieve · seal · email · print · export</h2>
          </div>
        </div>
        <span className={styles.sourcePill} data-source={statement?.source || 'IDLE'}>
          {statement?.source || 'IDLE'}
        </span>
      </header>

      <div className={styles.controls}>
        <label className={styles.field}>
          <span>Scope</span>
          <select
            className={styles.select}
            value={scope}
            onChange={(e) => setScope(e.target.value)}
            aria-label="Statement scope"
          >
            {SCOPES.map((s) => (
              <option key={s.id} value={s.id}>{s.label}</option>
            ))}
          </select>
        </label>
        <label className={styles.field}>
          <span>Period</span>
          <select
            className={styles.select}
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            aria-label="Statement period"
          >
            {PERIODS.map((p) => (
              <option key={p.id} value={p.id}>{p.label}</option>
            ))}
          </select>
        </label>
        <div className={styles.actions} role="group" aria-label="Statement operations">
          <button type="button" className={styles.primaryButton} onClick={retrieve} disabled={loading} aria-label="Retrieve statement">
            {loading ? <RefreshCw size={14} className={styles.spin} /> : <Search size={14} />}
            Retrieve
          </button>
          <button type="button" className={styles.secondaryButton} onClick={seal} disabled={!statement || sealing} aria-label="Seal statement">
            {sealing ? <RefreshCw size={14} className={styles.spin} /> : <ShieldCheck size={14} />}
            Seal
          </button>
          <button type="button" className={styles.secondaryButton} onClick={emailStatement} disabled={!statement || emailing} aria-label="Email statement">
            {emailing ? <RefreshCw size={14} className={styles.spin} /> : <Mail size={14} />}
            Email
          </button>
          <button type="button" className={styles.secondaryButton} onClick={printStatement} disabled={!statement || printing} aria-label="Print statement">
            {printing ? <RefreshCw size={14} className={styles.spin} /> : <Printer size={14} />}
            Print
          </button>
          <button type="button" className={styles.secondaryButton} onClick={exportJson} disabled={!statement || exporting} aria-label="Download statement JSON">
            {exporting ? <RefreshCw size={14} className={styles.spin} /> : <Download size={14} />}
            JSON
          </button>
        </div>
      </div>

      {error && (
        <div className={styles.error} role="alert">
          <AlertTriangle size={14} />
          <span>{error}</span>
        </div>
      )}

      {statement && (
        <div className={styles.statementCard}>
          <div className={styles.summary}>
            <article>
              <span>Period</span>
              <strong>{statement.periodLabel || period}</strong>
            </article>
            <article>
              <span>Invoices</span>
              <strong>{statement.invoiceCount ?? lineItems.length}</strong>
            </article>
            <article>
              <span>Total</span>
              <strong>{formatMoney(statement.totalAmount, statement.currency)}</strong>
            </article>
            <article>
              <span>Status</span>
              <strong>{statement.status || 'RETRIEVED'}</strong>
            </article>
          </div>
          {(sealSnippet || latencyMs != null) && (
            <div className={styles.statusBar}>
              {latencyMs != null && (
                <span className={styles.latency}>
                  <Clock size={12} aria-hidden /> {latencyMs} ms
                </span>
              )}
              {sealSnippet && (
                <span className={styles.sealHash}>
                  <BadgeCheck size={12} aria-hidden /> {sealSnippet}…
                </span>
              )}
            </div>
          )}
        </div>
      )}

      <div className={styles.tableWrap}>
        {!statement && !loading && (
          <div className={styles.empty}>Retrieve a period to load live invoice lines for this tenant only.</div>
        )}
        {loading && <div className={styles.empty}>Aggregating ledger…</div>}
        {statement && lineItems.length === 0 && (
          <div className={styles.empty}>
            LIVE_EMPTY — no invoices in this window for tenant <strong>{tid}</strong>.
          </div>
        )}
        {lineItems.length > 0 && (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Invoice</th>
                <th>Description</th>
                <th>Issued</th>
                <th>Status</th>
                <th>Amount</th>
              </tr>
            </thead>
            <tbody>
              {lineItems.map((li, idx) => (
                <tr key={`${li.invoiceId}-${idx}`}>
                  <td><code>{li.invoiceNumber || li.invoiceId || '—'}</code></td>
                  <td>{li.description || '—'}</td>
                  <td>{formatDate(li.issueDate)}</td>
                  <td>{li.status || '—'}</td>
                  <td>{formatMoney(li.amount, li.currency || statement.currency)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {(lastAction || latencyMs != null) && (
        <footer className={styles.footer}>
          Last action: <strong>{lastAction || '—'}</strong>
          {latencyMs != null && <> · <span className={styles.latency}>{latencyMs} ms</span></>}
          {' · '}Tenant <code>{tid}</code>
        </footer>
      )}
    </section>
  );
}

/**
 * =============================================================================
 * INSTITUTIONAL CERTIFICATION SEAL — StatementEngine v2.1.0-ENTERPRISE-PDF
 * =============================================================================
 */
