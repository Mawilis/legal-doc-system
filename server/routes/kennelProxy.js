/* eslint-disable */
/**
 * ╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS – KENNEL EOS PROXY ROUTER [V1.5.0‑KENNEL‑ALL‑THE‑WAY]                                                 ║
 * ╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ FILE:           server/routes/kennelProxy.js                                                                   ║
 * ║ VERSION:        v1.5.0‑KENNEL‑ALL‑THE‑WAY                                                                     ║
 * ║ EPITOME:        Lean bridge Node BFF → Kennel (9095). Mandate: Kennel owns money + tenants.                     ║
 * ║                 • /api/billing/* | /billing/*   →  /billing/*                                                  ║
 * ║                 • /api/business/* | /business/* →  /api/*                                                       ║
 * ║                 • /api/tenants/*                →  /api/tenants/*                                               ║
 * ║                 • /api/subscriptions/*          →  /api/subscriptions/*                                        ║
 * ║ PATH:           /Users/wilsonkhanyezi/legal-doc-system/server/routes/kennelProxy.js                            ║
 * ║ COMPLIANCE:     POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001 · ECT Act §15                                   ║
 * ╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🔧 CHANGE LOG:                                                                                                  ║
 * ║   2026-08-24 v1.5.0-KENNEL-ALL-THE-WAY – /api/billing → /billing; business map; pay timeout 45s.               ║
 * ║   2026-08-24 v1.4.0-BILLING-PATHS – Map /billing/* without /api double-prefix.                                 ║
 * ║   2026-08-23 v1.3.0-PATH-FIXED – /business → /api tenants transform.                                           ║
 * ╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import axios from 'axios';
import logger from '../utils/logger.js';

const KENNEL_BASE_URL = (process.env.KENNEL_URL || process.env.KENNEL_EOS_URL || 'http://127.0.0.1:9095').replace(/\/$/, '');

const kennelClient = axios.create({
  baseURL: KENNEL_BASE_URL,
  timeout: Number(process.env.KENNEL_PROXY_TIMEOUT_MS || 30000),
  headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
  validateStatus: () => true,
});

/**
 * Map Node-facing path → Kennel path (path only, no query).
 * Order matters.
 */
function mapToKennelPath(originalUrl = '') {
  const raw = String(originalUrl || '').split('?')[0] || '/';
  let path = raw;

  // Billing: FastAPI APIRouter(prefix="/billing") — strip leading /api
  if (path.startsWith('/api/billing')) {
    return path.replace(/^\/api\/billing/, '/billing') || '/billing';
  }
  if (path.startsWith('/billing')) {
    return path;
  }

  // Business surface → Kennel /api/*
  if (path.startsWith('/api/business')) {
    path = path.replace(/^\/api\/business/, '') || '/';
    if (path === '/' || path === '') path = '/tenants';
    if (!path.startsWith('/api')) path = `/api${path.startsWith('/') ? path : `/${path}`}`;
    return path;
  }
  if (path.startsWith('/business')) {
    path = path.replace(/^\/business/, '') || '/';
    if (path === '/' || path === '') path = '/tenants';
    if (!path.startsWith('/api')) path = `/api${path.startsWith('/') ? path : `/${path}`}`;
    return path;
  }

  if (path.startsWith('/api/subscriptions')) {
    return path;
  }

  if (path.startsWith('/api/') || path === '/api') {
    return path;
  }

  if (!path.startsWith('/')) path = `/${path}`;
  return `/api${path}`;
}

function transformKennelResponse(kennelData) {
  if (kennelData == null) {
    return { success: false, data: null };
  }
  if (typeof kennelData !== 'object') {
    return { success: true, data: kennelData };
  }
  if (Object.prototype.hasOwnProperty.call(kennelData, 'success')) {
    return kennelData;
  }
  if (Array.isArray(kennelData.tenants)) {
    return {
      success: true,
      data: kennelData.tenants,
      total: kennelData.total ?? kennelData.tenants.length,
      _raw: kennelData,
    };
  }
  if (Array.isArray(kennelData.items) && kennelData.total != null) {
    return {
      success: true,
      data: kennelData.items,
      items: kennelData.items,
      total: kennelData.total,
      _raw: kennelData,
    };
  }
  if (Array.isArray(kennelData)) {
    return { success: true, data: kennelData, items: kennelData, total: kennelData.length };
  }
  return { success: true, data: kennelData };
}

const HOP_BY_HOP = new Set([
  'host',
  'connection',
  'keep-alive',
  'proxy-authenticate',
  'proxy-authorization',
  'te',
  'trailers',
  'transfer-encoding',
  'upgrade',
  'content-length',
]);

function buildUpstreamHeaders(req, tenantId) {
  const headers = {};
  for (const [key, value] of Object.entries(req.headers || {})) {
    const lower = String(key).toLowerCase();
    if (HOP_BY_HOP.has(lower)) continue;
    if (value == null) continue;
    headers[key] = value;
  }
  headers['X-Tenant-ID'] = tenantId;
  headers['X-Tenant-Id'] = tenantId;
  headers['x-tenant-id'] = tenantId;

  if (req.user?.token) {
    headers.Authorization = `Bearer ${req.user.token}`;
  } else if (req.headers?.authorization) {
    headers.Authorization = req.headers.authorization;
  }

  if (!headers['Content-Type'] && !headers['content-type']) {
    headers['Content-Type'] = 'application/json';
  }
  headers.Accept = headers.Accept || headers.accept || 'application/json';
  return headers;
}

const router = express.Router();

router.all('*', async (req, res) => {
  const startTime = process.hrtime.bigint();

  try {
    const targetPath = mapToKennelPath(req.originalUrl || req.url);
    const method = (req.method || 'GET').toLowerCase();
    const tenantId =
      req.tenantId ||
      req.headers['x-tenant-id'] ||
      req.headers['X-Tenant-Id'] ||
      req.headers['X-Tenant-ID'] ||
      'GLOBAL_ROOT';

    const headers = buildUpstreamHeaders(req, tenantId);
    const isBillingWrite =
      targetPath.startsWith('/billing') && !['get', 'head', 'options'].includes(method);

    const config = {
      method,
      url: targetPath,
      headers,
      params: req.query,
      validateStatus: () => true,
      timeout: isBillingWrite
        ? Number(process.env.KENNEL_BILLING_TIMEOUT_MS || 45000)
        : Number(process.env.KENNEL_PROXY_TIMEOUT_MS || 30000),
    };

    if (method !== 'get' && method !== 'head' && req.body !== undefined) {
      config.data = req.body;
    }

    const response = await kennelClient.request(config);
    const transformedBody = transformKennelResponse(response.data);

    const ctype = response.headers?.['content-type'];
    if (ctype) res.setHeader('Content-Type', ctype);
    if (response.headers?.['x-wilsy-idempotency-key']) {
      res.setHeader('X-Wilsy-Idempotency-Key', response.headers['x-wilsy-idempotency-key']);
    }

    res.status(response.status || 502).json(transformedBody);

    const latencyMs = Number(process.hrtime.bigint() - startTime) / 1e6;
    logger.info('[KENNEL_PROXY] Request forwarded', {
      method: method.toUpperCase(),
      original: req.originalUrl,
      target: targetPath,
      status: response.status,
      latencyMs: Number(latencyMs.toFixed(3)),
      tenantId,
    });
  } catch (error) {
    logger.error('[KENNEL_PROXY] Error forwarding request:', {
      error: error.message,
      code: error.code,
      originalUrl: req.originalUrl,
    });

    if (error.response) {
      return res.status(error.response.status || 502).json({
        success: false,
        error: error.response.data || { message: 'Kennel error' },
      });
    }

    const isTimeout = error.code === 'ECONNABORTED' || /timeout/i.test(error.message || '');
    res.status(isTimeout ? 504 : 502).json({
      success: false,
      error: {
        code: isTimeout ? 'KENNEL_PROXY_TIMEOUT' : 'KENNEL_PROXY_ERROR',
        message: isTimeout ? 'Kennel EOS timed out.' : 'Failed to communicate with Kennel EOS.',
        detail: error.message,
      },
    });
  }
});

export default router;

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🏛️ INSTITUTIONAL CERTIFICATION SEAL — kennelProxy V1.5.0‑KENNEL‑ALL‑THE‑WAY
 * ═══════════════════════════════════════════════════════════════════════════════
 * Status:          CERTIFIED PRODUCTION ARTIFACT
 * Map:             /api/billing/* → /billing/* | /api/business/* → /api/*
 * Compliance:      POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001 · ECT Act §15
 * ═══════════════════════════════════════════════════════════════════════════════
 */
