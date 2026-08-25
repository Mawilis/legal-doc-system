/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS – SOVEREIGN PLATFORM INVOICE CONTROLLER [v1.2.0-CREATOR-LINEAGE]                                                              ║
 * ║ [WILSY OS → TENANT BILLING | SUBSCRIPTION-ANCHORED | METRIC-AWARE | AUDIT-DRIVEN | SUPER_ADMIN SCOPE]                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.1.0-PRODUCTION-FIX | PRODUCTION READY                                                                                      ║
 * ║ EPITOME: Create, pay, cancel, list, get, metrics for PlatformInvoice (Wilsy OS → tenant).                                             ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/controllers/platformInvoiceController.js                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated sovereign billing separation. [2026-05-15]                                           ║
 * ║ • AI Engineering (v1.0.0) – Initial controller. [2026-08-15]                                                                           ║
 * ║ • AI Engineering (v1.1.0) – Tenant resolution; SUPER_ADMIN cross-tenant create/list; uppercase status;                                 ║
 * ║                            single metric path; taxAmount at create; soft metrics import. [2026-08-15]                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COMPLIANCE: POPIA §19 │ GDPR §32 │ SOC2 §CC7.2                                                                                        ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import PlatformInvoice, { PLATFORM_INVOICE_STATUS } from '../models/PlatformInvoice.js';
import Subscription from '../models/Subscription.js';

// Soft metrics — never crash controller if registry is mid-reload
let observeInvoiceCreate = () => { };
let invoicesCreated = {
  platform: { inc: () => false },
  inc: () => false,
};
try {
  const metrics = await import('../metrics/prometheusMetrics.js');
  if (typeof metrics.observeInvoiceCreate === 'function') {
    observeInvoiceCreate = metrics.observeInvoiceCreate;
  }
  if (metrics.invoicesCreated) {
    invoicesCreated = metrics.invoicesCreated;
  }
} catch {
  /* metrics optional at boot */
}

function isModelDebugEnabled() {
  return (
    process.env.WILSY_MODEL_DEBUG === '1' ||
    process.env.WILSY_CONTROLLER_DEBUG === '1' ||
    process.env.WILSY_METRICS_DEBUG === '1'
  );
}

function modelDebug(message, ...args) {
  if (isModelDebugEnabled()) console.info(message, ...args);
}

function modelError(message, ...args) {
  console.error(message, ...args);
}


// ============================================================================
// HELPERS
// ============================================================================

/**
 * @function resolveTenantId
 * @description Resolves tenant from body, query, headers, or auth context.
 * @institutional SUPER_ADMIN may pass target tenantId in body/query for platform ops.
 */
function resolveTenantId(req) {
  const fromBody = req.body?.tenantId || req.body?.targetTenantId;
  const fromQuery = req.query?.tenantId;
  const fromHeader =
    req.headers?.['x-tenant-id'] ||
    req.headers?.['x-wilsy-tenant'] ||
    req.headers?.['x-tenantid'];
  const fromUser = req.user?.tenantId || req.auth?.tenantId;
  const fromContext = req.tenantId || req.tenant?.tenantId;

  return String(
    fromBody || fromQuery || fromHeader || fromUser || fromContext || ''
  ).trim();
}

/**
 * @function resolveActor
 * @description Human or system actor for audit trail (no PII beyond role/email claim if present).
 */
function resolveActor(req) {
  if (req.body?.user) return String(req.body.user);
  if (req.user?.email) return String(req.user.email);
  if (req.user?.id) return String(req.user.id);
  if (req.user?.role) return String(req.user.role);
  return 'SYSTEM';
}

/**
 * @function isPlatformOperator
 * @description Founder / SUPER_ADMIN may operate across tenants.
 */
function isPlatformOperator(req) {
  const role = String(req.user?.role || req.auth?.role || '').toUpperCase();
  return (
    role === 'SUPER_ADMIN' ||
    role === 'FOUNDER' ||
    role === 'FOUNDER_ARCHITECT' ||
    role === 'OMEGA' ||
    req.sovereignBypass === true
  );
}

function recordCreateMetric(tenantId, ok, seconds, extra = {}) {
  try {
    observeInvoiceCreate(
      tenantId || 'UNKNOWN',
      'PLATFORM',
      ok ? 'success' : 'error',
      Number(seconds) || 0
    );
    if (ok && invoicesCreated?.platform?.inc) {
      invoicesCreated.platform.inc({
        tenantId: tenantId || 'UNKNOWN',
        status: extra.status || 'ISSUED',
        currency: extra.currency || 'ZAR',
        planTier: extra.planTier || extra.tier || 'standard',
        source: 'platformInvoiceController',
      });
    } else if (ok && typeof invoicesCreated?.inc === 'function') {
      invoicesCreated.inc({
        tenantId: tenantId || 'UNKNOWN',
        type: 'PLATFORM',
        status: extra.status || 'ISSUED',
        currency: extra.currency || 'ZAR',
        tier: extra.planTier || extra.tier || 'standard',
        source: 'platformInvoiceController',
      });
    }
  } catch {
    /* non-fatal */
  }
}

// ============================================================================
// CREATE
// ============================================================================

/**
 * @function createPlatformInvoice
 * @route POST /api/platform/invoices
 * @description Creates a platform invoice anchored to a subscription.
 * @collaboration Subscription renewals / Billing HUD platform surface
 */
export const createPlatformInvoice = async (req, res) => {
  const startTime = process.hrtime.bigint();
  const contextTenantId = resolveTenantId(req);
  const actor = resolveActor(req);
  const operator = isPlatformOperator(req);

  const {
    subscriptionId,
    amount,
    taxAmount = 0,
    taxRate,
    currency,
    collectionMethod,
    issuedAt,
    dueAt,
    idempotencyKey,
    metadata = {},
    tags = [],
  } = req.body || {};

  try {
    if (!subscriptionId) {
      return res.status(400).json({
        success: false,
        error: 'SUBSCRIPTION_ID_REQUIRED',
        message: 'subscriptionId is required.',
      });
    }

    const subscription = await Subscription.findById(subscriptionId).lean();
    if (!subscription) {
      return res.status(404).json({
        success: false,
        error: 'SUBSCRIPTION_NOT_FOUND',
        message: 'Subscription not found.',
      });
    }

    const billTenantId = String(subscription.tenantId || contextTenantId || '').trim();
    if (!billTenantId) {
      return res.status(400).json({
        success: false,
        error: 'TENANT_REQUIRED',
        message: 'Could not resolve tenantId for subscription.',
      });
    }

    // Tenant isolation: non-operators may only bill their own subscription tenant
    if (!operator && contextTenantId && contextTenantId !== billTenantId) {
      return res.status(403).json({
        success: false,
        error: 'TENANT_ISOLATION',
        message: 'Subscription does not belong to this tenant.',
      });
    }

    const finalAmount =
      amount != null ? Number(amount) : Number(subscription.amount ?? subscription.unitAmount ?? 0);
    if (!Number.isFinite(finalAmount) || finalAmount < 0) {
      return res.status(400).json({
        success: false,
        error: 'INVALID_AMOUNT',
        message: 'amount must be a non-negative number.',
      });
    }

    const finalTax = Number(taxAmount) || 0;
    const key =
      idempotencyKey ||
      `PLAT-${billTenantId}-${subscriptionId}-${issuedAt || 'now'}-${finalAmount}-${finalTax}`;

    // Idempotent short-circuit
    const existing = await PlatformInvoice.findOne({ idempotencyKey: key });
    if (existing) {
      return res.status(200).json({
        success: true,
        status: 'IDEMPOTENT_REPLAY',
        data: existing,
        invoiceId: existing._id,
      });
    }

    const subDoc = {
      ...subscription,
      _id: subscription._id,
      amount: finalAmount,
      currency: currency || subscription.currency || 'ZAR',
      collectionMethod: collectionMethod || subscription.collectionMethod || 'charge_automatically',
    };

    const invoice = await PlatformInvoice.createFromSubscription(subDoc, {
      issuedAt: issuedAt ? new Date(issuedAt) : new Date(),
      dueAt: dueAt ? new Date(dueAt) : undefined,
      collectionMethod: subDoc.collectionMethod,
      idempotencyKey: key,
      taxAmount: finalTax,
      taxRate: taxRate != null ? Number(taxRate) : undefined,
      metadata: {
        ...metadata,
        createdBy: actor,
        createdById: req.user?._id || req.user?.id || '',
        createdByEmail: req.user?.email || '',
        createdByRole: req.user?.role || req.user?.userRole || '',
        identitySource: 'PLATFORM_ROOT',
        issuerType: 'PLATFORM',
      },
      tags: Array.isArray(tags) ? tags : [],
      user: actor,
      createdBy: actor,
      createdById: String(req.user?._id || req.user?.id || ''),
      createdByEmail: String(req.user?.email || ''),
      createdByRole: String(req.user?.role || req.user?.userRole || ''),
      issuingEntity: 'Wilsy (Pty) Ltd',
      issuerType: 'PLATFORM',
    });

    const durationSeconds = Number(process.hrtime.bigint() - startTime) / 1e9;
    recordCreateMetric(billTenantId, true, durationSeconds, {
      status: invoice.status,
      currency: invoice.currency,
      planTier: invoice.planTier,
      tier: req.tier,
    });

    return res.status(201).json({
      success: true,
      status: 'OPERATIONAL',
      surface: 'PLATFORM_INVOICE_CREATE',
      data: invoice,
      invoiceId: invoice._id,
      invoiceNumber: invoice.invoiceNumber,
      proofHash: invoice.proofHash,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    const durationSeconds = Number(process.hrtime.bigint() - startTime) / 1e9;
    recordCreateMetric(contextTenantId || 'UNKNOWN', false, durationSeconds);
    modelError('[PLATFORM_INVOICE_CONTROLLER] createPlatformInvoice error:', error?.message || error);
    return res.status(500).json({
      success: false,
      error: 'PLATFORM_INVOICE_CREATE_FAILED',
      message: error?.message || 'Failed to create platform invoice.',
    });
  }
};

// ============================================================================
// PAY
// ============================================================================

/**
 * @function payPlatformInvoice
 * @route PUT /api/platform/invoices/:id/pay
 * @route POST /api/platform/invoices/:id/pay
 */
export const payPlatformInvoice = async (req, res) => {
  const startTime = process.hrtime.bigint();
  const contextTenantId = resolveTenantId(req);
  const operator = isPlatformOperator(req);
  const { id } = req.params;
  const {
    paymentReference,
    amount,
    reason = 'Payment received',
  } = req.body || {};
  const actor = resolveActor(req);

  try {
    if (!id) {
      return res.status(400).json({ success: false, error: 'INVOICE_ID_REQUIRED' });
    }

    const filter = { _id: id };
    if (!operator && contextTenantId) filter.tenantId = contextTenantId;

    const invoice = await PlatformInvoice.findOne(filter);
    if (!invoice) {
      return res.status(404).json({
        success: false,
        error: 'INVOICE_NOT_FOUND',
        message: 'Invoice not found or does not belong to this tenant.',
      });
    }

    if (typeof invoice.isPayable === 'function' && !invoice.isPayable()) {
      return res.status(400).json({
        success: false,
        error: 'NOT_PAYABLE',
        message: `Invoice is not payable (status: ${invoice.status}).`,
      });
    }

    await invoice.markAsPaid(paymentReference, {
      user: actor,
      reason,
      amount: amount != null ? Number(amount) : undefined,
    });

    const durationSeconds = Number(process.hrtime.bigint() - startTime) / 1e9;
    observeInvoiceCreate(invoice.tenantId, 'PLATFORM', 'pay_success', durationSeconds);

    return res.status(200).json({
      success: true,
      status: 'OPERATIONAL',
      surface: 'PLATFORM_INVOICE_PAY',
      data: invoice,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    const durationSeconds = Number(process.hrtime.bigint() - startTime) / 1e9;
    observeInvoiceCreate(contextTenantId || 'UNKNOWN', 'PLATFORM', 'pay_error', durationSeconds);
    modelError('[PLATFORM_INVOICE_CONTROLLER] payPlatformInvoice error:', error?.message || error);
    return res.status(500).json({
      success: false,
      error: 'PLATFORM_INVOICE_PAY_FAILED',
      message: error?.message || 'Failed to pay platform invoice.',
    });
  }
};

// ============================================================================
// CANCEL
// ============================================================================

/**
 * @function cancelPlatformInvoice
 * @route PUT /api/platform/invoices/:id/cancel
 * @route POST /api/platform/invoices/:id/cancel
 */
export const cancelPlatformInvoice = async (req, res) => {
  const contextTenantId = resolveTenantId(req);
  const operator = isPlatformOperator(req);
  const { id } = req.params;
  const { reason } = req.body || {};
  const actor = resolveActor(req);

  try {
    if (!id) {
      return res.status(400).json({ success: false, error: 'INVOICE_ID_REQUIRED' });
    }

    const filter = { _id: id };
    if (!operator && contextTenantId) filter.tenantId = contextTenantId;

    const invoice = await PlatformInvoice.findOne(filter);
    if (!invoice) {
      return res.status(404).json({
        success: false,
        error: 'INVOICE_NOT_FOUND',
        message: 'Invoice not found or does not belong to this tenant.',
      });
    }

    const paid = PLATFORM_INVOICE_STATUS?.PAID || 'PAID';
    if (String(invoice.status).toUpperCase() === String(paid).toUpperCase()) {
      return res.status(400).json({
        success: false,
        error: 'CANNOT_CANCEL_PAID',
        message: 'Cannot cancel a paid invoice.',
      });
    }

    await invoice.cancel(reason || 'Cancelled by request', { user: actor });

    return res.status(200).json({
      success: true,
      status: 'OPERATIONAL',
      surface: 'PLATFORM_INVOICE_CANCEL',
      data: invoice,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    modelError('[PLATFORM_INVOICE_CONTROLLER] cancelPlatformInvoice error:', error?.message || error);
    return res.status(500).json({
      success: false,
      error: 'PLATFORM_INVOICE_CANCEL_FAILED',
      message: error?.message || 'Failed to cancel platform invoice.',
    });
  }
};

// ============================================================================
// LIST / GET / METRICS
// ============================================================================

/**
 * @function listPlatformInvoices
 * @route GET /api/platform/invoices
 */
export const listPlatformInvoices = async (req, res) => {
  const contextTenantId = resolveTenantId(req);
  const operator = isPlatformOperator(req);
  const {
    page = 1,
    limit = 20,
    status,
    tenantId: queryTenantId,
    subscriptionId,
  } = req.query || {};

  try {
    const filter = {};
    if (operator) {
      const scopeTenant = queryTenantId || contextTenantId;
      if (scopeTenant && scopeTenant !== 'GLOBAL_ROOT' && scopeTenant !== 'MASTER') {
        filter.tenantId = scopeTenant;
      } else if (queryTenantId) {
        filter.tenantId = queryTenantId;
      }
      // bare GLOBAL_ROOT operator with no query → all platform invoices
    } else {
      if (!contextTenantId) {
        return res.status(400).json({
          success: false,
          error: 'TENANT_REQUIRED',
          message: 'tenantId required.',
        });
      }
      filter.tenantId = contextTenantId;
    }

    if (status) filter.status = String(status).toUpperCase();
    if (subscriptionId) filter.subscriptionRef = subscriptionId;

    const pageNum = Math.max(1, parseInt(page, 10) || 1);
    const limitNum = Math.min(100, Math.max(1, parseInt(limit, 10) || 20));
    const skip = (pageNum - 1) * limitNum;

    const [invoices, total] = await Promise.all([
      PlatformInvoice.find(filter).sort({ issuedAt: -1 }).skip(skip).limit(limitNum).lean(),
      PlatformInvoice.countDocuments(filter),
    ]);

    return res.status(200).json({
      success: true,
      status: 'OPERATIONAL',
      surface: 'PLATFORM_INVOICE_LIST',
      data: invoices,
      items: invoices,
      total,
      pagination: {
        page: pageNum,
        limit: limitNum,
        total,
        pages: Math.ceil(total / limitNum) || 0,
      },
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    modelError('[PLATFORM_INVOICE_CONTROLLER] listPlatformInvoices error:', error?.message || error);
    return res.status(500).json({
      success: false,
      error: 'PLATFORM_INVOICE_LIST_FAILED',
      message: error?.message || 'Failed to list platform invoices.',
    });
  }
};

/**
 * @function getPlatformInvoice
 * @route GET /api/platform/invoices/:id
 */
export const getPlatformInvoice = async (req, res) => {
  const contextTenantId = resolveTenantId(req);
  const operator = isPlatformOperator(req);
  const { id } = req.params;

  try {
    if (!id) {
      return res.status(400).json({ success: false, error: 'INVOICE_ID_REQUIRED' });
    }

    const filter = { _id: id };
    if (!operator && contextTenantId) filter.tenantId = contextTenantId;

    const invoice = await PlatformInvoice.findOne(filter).lean();
    if (!invoice) {
      return res.status(404).json({
        success: false,
        error: 'INVOICE_NOT_FOUND',
        message: 'Invoice not found or does not belong to this tenant.',
      });
    }

    return res.status(200).json({
      success: true,
      status: 'OPERATIONAL',
      surface: 'PLATFORM_INVOICE_GET',
      data: invoice,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    modelError('[PLATFORM_INVOICE_CONTROLLER] getPlatformInvoice error:', error?.message || error);
    return res.status(500).json({
      success: false,
      error: 'PLATFORM_INVOICE_GET_FAILED',
      message: error?.message || 'Failed to retrieve platform invoice.',
    });
  }
};

/**
 * @function getPlatformInvoiceMetrics
 * @route GET /api/platform/invoices/metrics
 */
export const getPlatformInvoiceMetrics = async (req, res) => {
  const contextTenantId = resolveTenantId(req);
  const operator = isPlatformOperator(req);
  const targetTenant = req.query?.tenantId || contextTenantId;

  try {
    if (!targetTenant) {
      return res.status(400).json({
        success: false,
        error: 'TENANT_REQUIRED',
        message: 'tenantId required.',
      });
    }

    if (!operator && contextTenantId && contextTenantId !== targetTenant) {
      return res.status(403).json({
        success: false,
        error: 'TENANT_ISOLATION',
        message: 'Cannot read metrics for another tenant.',
      });
    }

    const metrics = await PlatformInvoice.getTenantMetrics(targetTenant);
    return res.status(200).json({
      success: true,
      status: 'OPERATIONAL',
      surface: 'PLATFORM_INVOICE_METRICS',
      data: metrics,
      tenantId: targetTenant,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    modelError('[PLATFORM_INVOICE_CONTROLLER] getPlatformInvoiceMetrics error:', error?.message || error);
    return res.status(500).json({
      success: false,
      error: 'PLATFORM_INVOICE_METRICS_FAILED',
      message: error?.message || 'Failed to retrieve platform invoice metrics.',
    });
  }
};

/**
 * @function healthCheck
 * @route GET /api/platform/invoices/health
 */
export const healthCheck = (_req, res) => {
  res.status(200).json({
    status: 'OPERATIONAL',
    version: '1.1.0-PRODUCTION-FIX',
    timestamp: new Date().toISOString(),
    dependencies: {
      PlatformInvoice: PlatformInvoice?.modelName || 'PlatformInvoice',
      Subscription: Subscription?.modelName || 'Subscription',
      prometheus: 'soft-integrated',
    },
    capabilities: [
      'create',
      'pay',
      'cancel',
      'list',
      'get',
      'metrics',
      'idempotent_create',
      'super_admin_scope',
    ],
  });
};

export default {
  createPlatformInvoice,
  payPlatformInvoice,
  cancelPlatformInvoice,
  listPlatformInvoices,
  getPlatformInvoice,
  getPlatformInvoiceMetrics,
  healthCheck,
};

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * INSTITUTIONAL CERTIFICATION SEAL — platformInvoiceController v1.2.0-CREATOR-LINEAGE
 * ═══════════════════════════════════════════════════════════════════════════════
 * Status:     PRODUCTION READY
 * Fixes:      Tenant resolution; SUPER_ADMIN scope; uppercase PAID check;
 *             taxAmount at createFromSubscription; single create metric path;
 *             soft metrics import; idempotent replay
 * Metrics:    observeInvoiceCreate(tenant, PLATFORM, status, sec) + platform.inc
 * Compliance: POPIA §19 │ GDPR §32 │ SOC2 §CC7.2
 * ═══════════════════════════════════════════════════════════════════════════════
 */
