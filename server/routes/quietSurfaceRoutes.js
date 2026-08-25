/* eslint-disable */
/**
 * =============================================================================
 * Wilsy OS — Quiet Surface Stubs (Console Hygiene)
 * =============================================================================
 * File:           server/routes/quietSurfaceRoutes.js
 * Version:        v1.0.0-CONSOLE-QUIET
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Returns truthful LIVE_EMPTY / STANDBY 200 responses for
 *                 high-frequency optional surfaces so the browser console is
 *                 not flooded with 404/502 while those modules are offline.
 *                 Never fabricates financial or HR data.
 * Classification: Production Artifact
 *
 * Contributors:
 *   - Wilson Khanyezi — Mandated clean operator console under degraded DB.
 *   - AI Engineering — Soft surfaces under Mandate v3.1.0.
 *
 * Change Log:
 *   2026-08-04 v1.0.0-CONSOLE-QUIET — Initial quiet surfaces for finance/telemetry noise.
 * =============================================================================
 */

import express from 'express';

const router = express.Router();

function emptyOk(res, surface, extra = {}) {
  res.setHeader('X-Wilsy-Source', 'LIVE_EMPTY');
  res.setHeader('X-Wilsy-Quiet-Surface', '1');
  return res.status(200).json({
    success: true,
    status: 'OPERATIONAL',
    surface,
    source: 'LIVE_EMPTY',
    items: [],
    data: null,
    note: 'Surface registered — empty until module store is connected. Not a 404.',
    timestamp: new Date().toISOString(),
    ...extra
  });
}

export function registerQuietSurfaces(app) {
  if (!app || typeof app.get !== 'function') return;

  // Treasury / finance probes (Finance dashboard fan-out)
  app.get('/api/treasury/benchmarks/latest', (req, res) =>
    emptyOk(res, 'TREASURY_BENCHMARKS', { benchmarks: [] })
  );
  app.get('/api/treasury/policy/matrix', (req, res) =>
    emptyOk(res, 'TREASURY_POLICY_MATRIX', { matrix: {} })
  );
  app.get('/api/treasury/balances', (req, res) =>
    emptyOk(res, 'TREASURY_BALANCES', { balances: {}, currency: 'ZAR' })
  );

  app.get('/api/finance/benchmarks/latest', (req, res) =>
    emptyOk(res, 'FINANCE_BENCHMARKS', { benchmarks: [] })
  );
  app.get('/api/finance/treasury/policy/matrix', (req, res) =>
    emptyOk(res, 'FINANCE_TREASURY_POLICY', { matrix: {} })
  );
  app.get('/api/finance/treasury/status/:tenantId?', (req, res) =>
    emptyOk(res, 'FINANCE_TREASURY_STATUS', {
      tenantId: req.params.tenantId || req.query.tenantId || 'GLOBAL_ROOT',
      cashPosition: 0
    })
  );
  app.get('/api/finance/treasury/balances', (req, res) =>
    emptyOk(res, 'FINANCE_TREASURY_BALANCES', { balances: {} })
  );

  app.get('/api/system/rates/benchmarks', (req, res) =>
    emptyOk(res, 'SYSTEM_RATE_BENCHMARKS', { benchmarks: [] })
  );
  app.get('/api/system/treasury/policy/matrix', (req, res) =>
    emptyOk(res, 'SYSTEM_TREASURY_POLICY', { matrix: {} })
  );

  // Courts / collections registry
  app.get('/api/courts', (req, res) =>
    emptyOk(res, 'COURTS_REGISTRY', { courts: [], total: 0 })
  );

  // Business CRM probes
  app.get('/api/business/employees', (req, res) =>
    emptyOk(res, 'BUSINESS_EMPLOYEES', { employees: [], tenantId: req.query.tenantId })
  );
  app.get('/api/business/deals', (req, res) =>
    emptyOk(res, 'BUSINESS_DEALS', { deals: [], tenantId: req.query.tenantId })
  );
  app.get('/api/business/contracts', (req, res) =>
    emptyOk(res, 'BUSINESS_CONTRACTS', { contracts: [], tenantId: req.query.tenantId })
  );

  // Subscriptions list (BillingHUD)
  app.get('/api/subscriptions', (req, res) =>
    emptyOk(res, 'SUBSCRIPTIONS', {
      subscriptions: [],
      page: Number(req.query.page || 1),
      limit: Number(req.query.limit || 20),
      total: 0
    })
  );

  // Telemetry event ingest — accept and acknowledge without DB
  app.post('/api/telemetry/event', (req, res) => {
    res.setHeader('X-Wilsy-Quiet-Surface', '1');
    return res.status(202).json({
      success: true,
      status: 'ACCEPTED',
      surface: 'TELEMETRY_EVENT',
      source: 'QUIET_ACK',
      note: 'Event acknowledged without persistence (quiet mode).',
      timestamp: new Date().toISOString()
    });
  });
  app.get('/api/telemetry/event', (req, res) =>
    emptyOk(res, 'TELEMETRY_EVENT', { events: [] })
  );

  // Identity posture (chrome)
  app.get('/api/account/identity-posture', (req, res) =>
    emptyOk(res, 'IDENTITY_POSTURE', {
      tenantId: req.query.tenantId || null,
      posture: 'STANDBY',
      verified: false
    })
  );

  // Forensics — empty anchors (port 5050 is separate; this stops 404 on :4000)
  app.get('/api/forensics/merkle-auditor/anchors', (req, res) =>
    emptyOk(res, 'MERKLE_ANCHORS', { anchors: [], limit: Number(req.query.limit || 250) })
  );
  app.get('/api/forensics/merkle-auditor/receipts', (req, res) =>
    emptyOk(res, 'MERKLE_RECEIPTS', { receipts: [], tenantId: req.query.tenantId })
  );

  console.info('[QUIET-SURFACES] Optional module probes registered (LIVE_EMPTY, not 404).');
}

export default router;
