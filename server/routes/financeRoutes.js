/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - FINANCE KPI ROUTES [V1.0.0-SOURCE-AWARE-KPI-NEXUS]                                                                         ║
 * ║ [TENANT-SCOPED KPI HYDRATION | INVOICE/PAYMENT AGGREGATION | NO-FAKE-DATA SOURCE POSTURE | EXECUTIVE DASHBOARD TRUTH SOURCE]         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-SOURCE-AWARE-KPI-NEXUS | PRODUCTION READY | EXECUTIVE FINANCE READ MODEL                                               ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/financeRoutes.js                                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Required executive KPIs to come from real tenant sources, not placeholder dashboard theatre.        ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Mounted a tenant-scoped KPI source route with partial-source disclosure and proof hashes.      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import crypto from 'node:crypto';
import mongoose from 'mongoose';
import Tenant from '../models/Tenant.js';
import Invoice from '../models/Invoice.js';
import Payment from '../models/Payment.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';
import {
  SUPPORTED_EXECUTIVE_CURRENCIES,
  convertCurrency,
  createCurrencyProofHash,
  getLiveFxRate,
  normalizeCurrencyCode
} from '../services/currencyIntelligenceService.js';

const router = express.Router();

/**
 * @function normalizeFinanceTenantId
 * @description Resolves the active tenant from protected request context, headers or query values.
 * @param {Object} req - Express request.
 * @returns {string} Tenant identifier.
 * @collaboration Finance reads must never drift across tenants, especially in executive dashboards.
 */
const normalizeFinanceTenantId = (req = {}) => String(
  req.tenantId
  || req.tenantContext?.id
  || req.headers?.['x-tenant-id']
  || req.query?.tenantId
  || req.user?.tenantId
  || 'GLOBAL_ROOT'
).trim();

/**
 * @function createFinanceKpiProof
 * @description Builds a deterministic SHA3 proof hash for KPI envelopes.
 * @param {Object} payload - Finance KPI payload.
 * @returns {string} Uppercase proof hash.
 * @collaboration Executive KPI snapshots must be verifiable when exported into boardroom evidence.
 */
const createFinanceKpiProof = (payload = {}) => crypto
  .createHash('sha3-512')
  .update(JSON.stringify(payload, Object.keys(payload).sort()))
  .digest('hex')
  .toUpperCase();

/**
 * @function buildTenantLookup
 * @description Builds a safe tenant lookup that supports tenantId strings and Mongo object ids.
 * @param {string} tenantId - Candidate tenant id.
 * @returns {Object} Mongo query.
 * @collaboration Wilsy OS has legacy and sovereign tenant identifiers; this preserves isolation while reading both safely.
 */
const buildTenantLookup = (tenantId = '') => {
  const or = [{ tenantId }];
  if (mongoose.Types.ObjectId.isValid(tenantId)) {
    or.push({ _id: tenantId });
  }
  return { $or: or };
};

/**
 * @function sumAggregation
 * @description Extracts a numeric sum from a Mongo aggregate response.
 * @param {Array<Object>} rows - Aggregate rows.
 * @returns {number} Numeric aggregate sum.
 * @collaboration Keeps source math explicit and prevents undefined from becoming a hidden dashboard fracture.
 */
const sumAggregation = (rows = []) => Number(rows?.[0]?.total || 0);

/**
 * @function buildFinanceKpiSourceStatus
 * @description Derives a truthful KPI source status from available tenant finance sources.
 * @param {Object} sources - Source availability flags.
 * @returns {string} Source posture label.
 * @collaboration The Executive Dashboard should know whether KPIs came from invoices, payments, tenant billing, or partial data.
 */
const buildFinanceKpiSourceStatus = (sources = {}) => {
  const liveCount = Object.values(sources).filter(Boolean).length;
  if (liveCount >= 2) return 'FINANCE_KPI_SOURCE_LIVE';
  if (liveCount === 1) return 'FINANCE_KPI_PARTIAL_SOURCE';
  return 'FINANCE_KPI_SOURCE_REQUIRED';
};

/**
 * @route GET /api/finance/kpis
 * @description Returns source-aware finance KPIs for the active tenant.
 * @returns {Object} KPI payload with proof and source coverage.
 * @collaboration This endpoint is the missing ExecutiveDashboard finance truth source and intentionally avoids fake NPS/HR data.
 */
router.get('/kpis', async (req, res) => {
  const tenantId = normalizeFinanceTenantId(req);
  const currentYear = new Date().getFullYear();
  const yearStart = new Date(`${currentYear}-01-01T00:00:00.000Z`);
  const now = new Date();

  try {
    const tenant = await Tenant.findOne(buildTenantLookup(tenantId)).lean();
    const tenantAnchors = [tenantId, tenant?.tenantId, tenant?._id?.toString()].filter(Boolean);
    const invoiceTenantQuery = { tenantId: { $in: tenantAnchors } };
    const paymentTenantQuery = {
      $or: tenantAnchors.map(anchor => (
        mongoose.Types.ObjectId.isValid(anchor)
          ? { tenantId: new mongoose.Types.ObjectId(anchor) }
          : { tenantId: anchor }
      ))
    };

    const [
      invoiceIssuedRows,
      invoicePaidRows,
      paymentRows,
      invoiceCount,
      paidInvoiceCount
    ] = await Promise.all([
      Invoice.aggregate([
        { $match: { ...invoiceTenantQuery, issueDate: { $gte: yearStart, $lte: now } } },
        { $group: { _id: null, total: { $sum: '$totalAmount' } } }
      ]),
      Invoice.aggregate([
        { $match: { ...invoiceTenantQuery, issueDate: { $gte: yearStart, $lte: now } } },
        { $group: { _id: null, total: { $sum: '$amountPaid' } } }
      ]),
      Payment.aggregate([
        {
          $match: {
            ...paymentTenantQuery,
            paymentDate: { $gte: yearStart, $lte: now },
            status: { $in: ['SUCCESSFUL', 'RECONCILED'] }
          }
        },
        { $group: { _id: null, total: { $sum: '$totalAmount' } } }
      ]),
      Invoice.countDocuments(invoiceTenantQuery),
      Invoice.countDocuments({ ...invoiceTenantQuery, status: 'PAID' })
    ]);

    const invoiceIssued = sumAggregation(invoiceIssuedRows);
    const invoicePaid = sumAggregation(invoicePaidRows);
    const paymentRevenue = sumAggregation(paymentRows);
    const tenantMrr = Number(tenant?.billing?.monthlyRevenue || tenant?.billing?.mrr || 0);
    const revenueYtd = Math.max(paymentRevenue, invoicePaid, tenantMrr * (now.getMonth() + 1), 0);
    const arr = Math.max(tenantMrr * 12, revenueYtd > 0 ? revenueYtd / Math.max(1, now.getMonth() + 1) * 12 : 0);
    const sourceCoverage = {
      tenantBilling: Boolean(tenantMrr),
      invoices: invoiceCount > 0,
      payments: paymentRevenue > 0
    };
    const sourceStatus = buildFinanceKpiSourceStatus(sourceCoverage);
    const collectionEfficiency = invoiceIssued > 0 ? Number(((invoicePaid / invoiceIssued) * 100).toFixed(2)) : null;
    const payload = {
      revenue: revenueYtd,
      revenueYtd,
      arr,
      arrRunRate: arr,
      currency: 'ZAR',
      operatingCurrency: 'ZAR',
      expenses: null,
      profit: null,
      profitMargin: null,
      nps: null,
      employeeSatisfaction: null,
      activeSubscriptions: tenant?.subscription?.isActive ? 1 : 0,
      invoiceCount,
      paidInvoiceCount,
      collectionEfficiency,
      sourceStatus,
      source: 'financeRoutes.kpis',
      sourceCoverage,
      tenantId,
      syncedAt: now.toISOString(),
      targets: {
        revenue: null,
        arr: null,
        nps: null,
        employeeSatisfaction: null
      }
    };
    const proofHash = createFinanceKpiProof({
      tenantId,
      revenueYtd,
      arr,
      invoiceCount,
      paidInvoiceCount,
      sourceStatus,
      syncedAt: payload.syncedAt
    });

    await broadcastTelemetry(tenantId, 'FINANCE_KPI_SOURCE_READ', sourceStatus, 'financeRoutes', {
      proofHash,
      sourceCoverage
    }).catch(() => {});

    res.json({
      success: true,
      status: sourceStatus,
      data: {
        kpis: payload,
        proofHash
      }
    });
  } catch (error) {
    const sourceStatus = 'FINANCE_KPI_SOURCE_SILENT';
    await broadcastTelemetry(tenantId, 'FINANCE_KPI_SOURCE_SILENT', 'SOURCE_SILENT', 'financeRoutes', {
      message: error.message
    }).catch(() => {});

    res.status(200).json({
      success: false,
      status: sourceStatus,
      data: {
        kpis: {
          revenue: null,
          expenses: null,
          profit: null,
          profitMargin: null,
          arr: null,
          currency: 'ZAR',
          operatingCurrency: 'ZAR',
          nps: null,
          employeeSatisfaction: null,
          sourceStatus,
          source: 'financeRoutes.kpis',
          tenantId,
          syncedAt: new Date().toISOString()
        }
      },
      error: error.message
    });
  }
});

/**
 * @route GET /api/finance/currency/convert
 * @description Converts an amount between supported currencies with live/source-silent FX governance.
 * @returns {Object} Conversion packet with proof hash and SARB-aware internal review signal.
 * @collaboration Wilsy OS is South African by default, but tenant executives can inspect foreign currency exposure without fake rates.
 */
router.get('/currency/convert', async (req, res) => {
  const tenantId = normalizeFinanceTenantId(req);
  const amount = Number(req.query?.amount || 0);
  const fromCurrency = normalizeCurrencyCode(req.query?.from || req.query?.fromCurrency || 'ZAR');
  const toCurrency = normalizeCurrencyCode(req.query?.to || req.query?.toCurrency || 'USD');

  try {
    const conversion = await convertCurrency({
      tenantId,
      amount,
      fromCurrency,
      toCurrency
    });
    await broadcastTelemetry(tenantId, 'FINANCE_FX_CONVERSION_READ', conversion.sourceStatus, 'financeRoutes', {
      fromCurrency,
      toCurrency,
      sourceStatus: conversion.sourceStatus,
      proofHash: conversion.proofHash
    }).catch(() => {});
    res.status(200).json({
      success: conversion.success,
      status: conversion.sourceStatus,
      data: conversion
    });
  } catch (error) {
    const sourceStatus = 'FX_CONVERSION_SOURCE_SILENT';
    const payload = {
      success: false,
      tenantId,
      sourceStatus,
      amount,
      fromCurrency,
      toCurrency,
      error: error.message,
      fetchedAt: new Date().toISOString()
    };
    const proofHash = createCurrencyProofHash(payload);
    await broadcastTelemetry(tenantId, 'FINANCE_FX_CONVERSION_SOURCE_SILENT', 'SOURCE_SILENT', 'financeRoutes', {
      message: error.message,
      proofHash
    }).catch(() => {});
    res.status(200).json({
      success: false,
      status: sourceStatus,
      data: {
        ...payload,
        proofHash
      }
    });
  }
});

/**
 * @route GET /api/finance/currency/rates
 * @description Returns a source-labelled FX watchlist from the ZAR operating base.
 * @returns {Object} Rate watchlist.
 * @collaboration Gives executives a daily currency radar without hard-coded stale rates.
 */
router.get('/currency/rates', async (req, res) => {
  const tenantId = normalizeFinanceTenantId(req);
  const baseCurrency = normalizeCurrencyCode(req.query?.base || 'ZAR');
  const requestedTargets = String(req.query?.targets || 'USD,EUR,GBP,TZS,KES')
    .split(',')
    .map(normalizeCurrencyCode)
    .filter(currency => currency !== baseCurrency);
  const targets = [...new Set(requestedTargets)].filter(currency => SUPPORTED_EXECUTIVE_CURRENCIES.includes(currency)).slice(0, 8);

  try {
    const rates = await Promise.all(targets.map(async quoteCurrency => (
      getLiveFxRate({ baseCurrency, quoteCurrency })
    )));
    const payload = {
      success: rates.some(rate => Boolean(rate.rate)),
      tenantId,
      baseCurrency,
      sourceStatus: rates.some(rate => rate.sourceStatus === 'FX_SOURCE_LIVE' || rate.sourceStatus === 'FX_SOURCE_CACHE')
        ? 'FX_WATCHLIST_PARTIAL_LIVE'
        : 'FX_WATCHLIST_SOURCE_SILENT',
      supportedCurrencies: SUPPORTED_EXECUTIVE_CURRENCIES,
      rates,
      fetchedAt: new Date().toISOString()
    };
    const proofHash = createCurrencyProofHash(payload);
    await broadcastTelemetry(tenantId, 'FINANCE_FX_WATCHLIST_READ', payload.sourceStatus, 'financeRoutes', {
      baseCurrency,
      count: rates.length,
      proofHash
    }).catch(() => {});
    res.status(200).json({
      success: payload.success,
      status: payload.sourceStatus,
      data: {
        ...payload,
        proofHash
      }
    });
  } catch (error) {
    const payload = {
      success: false,
      tenantId,
      baseCurrency,
      sourceStatus: 'FX_WATCHLIST_SOURCE_SILENT',
      supportedCurrencies: SUPPORTED_EXECUTIVE_CURRENCIES,
      rates: [],
      error: error.message,
      fetchedAt: new Date().toISOString()
    };
    const proofHash = createCurrencyProofHash(payload);
    await broadcastTelemetry(tenantId, 'FINANCE_FX_WATCHLIST_SOURCE_SILENT', 'SOURCE_SILENT', 'financeRoutes', {
      message: error.message,
      proofHash
    }).catch(() => {});
    res.status(200).json({
      success: false,
      status: payload.sourceStatus,
      data: {
        ...payload,
        proofHash
      }
    });
  }
});

export default router;
