/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS – DUNNING ENGINE [V1.0.0-SOVEREIGN]                                                                                        ║
 * ║ AUTHORITY: WILSY OS FINANCE & LEGAL | TERMINAL WORKFLOW COMPLIANT                                                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-SOVEREIGN | PRODUCTION‑GRADE | TRILLION‑DOLLAR SPEC                                                                   ║
 * ║ EPITOME: Institutional neural dunning – orchestrates payment reminders, escalation rules, and court‑ready collections.               ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/DunningEngine.js                                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN‑OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (Founder/Architect) – Mandated zero‑loss dunning governance with POPIA/GDPR compliance.                              ║
 * ║ • AI Engineering (DeepSeek) – Engineered production‑grade dunning logic with mock data layer.                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ CHANGE LOG:                                                                                                                            ║
 * ║ • 2026‑08‑01 v1.0.0‑SOVEREIGN – Initial creation: recommendation generation, status, and escalation simulation.                        ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import crypto from 'node:crypto';
import logger from '../utils/logger.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';

/**
 * @constant DEFAULT_DUNNING_RULES
 * @description Institutional dunning rules per jurisdiction.
 * Each rule defines escalation steps, intervals, and final actions.
 */
const DEFAULT_DUNNING_RULES = {
  global: {
    steps: [
      { level: 1, label: 'First Notice', daysOverdue: 7, action: 'REMINDER' },
      { level: 2, label: 'Second Notice', daysOverdue: 14, action: 'WARNING' },
      { level: 3, label: 'Final Notice', daysOverdue: 21, action: 'FINAL_WARNING' },
      { level: 4, label: 'Collections', daysOverdue: 30, action: 'ESCALATE_TO_COLLECTIONS' },
      { level: 5, label: 'Legal', daysOverdue: 45, action: 'LEGAL_ESCALATION' },
    ],
    interestRatePerDay: 0.0005, // 0.05% per day
    gracePeriodDays: 3,
  },
  ZA: {
    // South African specific rules (popia compliant)
    steps: [
      { level: 1, label: 'Herinnering', daysOverdue: 5, action: 'REMINDER' },
      { level: 2, label: 'Tweede Kennisgewing', daysOverdue: 12, action: 'WARNING' },
      { level: 3, label: 'Finale Kennisgewing', daysOverdue: 20, action: 'FINAL_WARNING' },
      { level: 4, label: 'Debsiste', daysOverdue: 30, action: 'ESCALATE_TO_COLLECTIONS' },
      { level: 5, label: 'Regsgeding', daysOverdue: 45, action: 'LEGAL_ESCALATION' },
    ],
    interestRatePerDay: 0.0006,
    gracePeriodDays: 5,
  },
};

/**
 * @class DunningEngine
 * @description Core service for managing dunning processes, generating recommendations,
 *              and tracking overdue accounts.
 * @collaboration Integrates with InvoiceEngine, Telemetry, and Legal escalation systems.
 */
class DunningEngine {
  /**
   * @constructor
   * @param {Object} options - Configuration options.
   * @param {Object} options.rules - Custom dunning rules (overrides default).
   * @param {Function} options.invoiceFetcher - Async function to fetch overdue invoices.
   * @param {Function} options.escalationHandler - Async function to handle escalations.
   */
  constructor(options = {}) {
    this.rules = options.rules || DEFAULT_DUNNING_RULES;
    this.invoiceFetcher = options.invoiceFetcher || this._defaultInvoiceFetcher;
    this.escalationHandler = options.escalationHandler || this._defaultEscalationHandler;
    this.logger = logger.child({ service: 'DunningEngine' });
    this.health = {
      status: 'OPERATIONAL',
      lastRun: null,
      recommendationsGenerated: 0,
      errors: 0,
    };
  }

  /**
   * @private
   * @method _defaultInvoiceFetcher
   * @description Mock invoice fetcher – returns sample overdue invoices.
   * @param {string} tenantId - Tenant identifier.
   * @returns {Promise<Array>} Array of invoice objects.
   */
  async _defaultInvoiceFetcher(tenantId) {
    // In production, this would query the invoice database.
    // For now, return mock data.
    return [
      {
        id: 'INV-001',
        tenantId,
        amountDue: 1500.00,
        currency: 'ZAR',
        dueDate: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000), // 10 days overdue
        status: 'OVERDUE',
        customer: { id: 'CUST-001', name: 'Acme Corp' },
      },
      {
        id: 'INV-002',
        tenantId,
        amountDue: 2500.00,
        currency: 'ZAR',
        dueDate: new Date(Date.now() - 25 * 24 * 60 * 60 * 1000), // 25 days overdue
        status: 'OVERDUE',
        customer: { id: 'CUST-002', name: 'Beta Ltd' },
      },
      {
        id: 'INV-003',
        tenantId,
        amountDue: 500.00,
        currency: 'ZAR',
        dueDate: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000), // 2 days overdue
        status: 'OVERDUE',
        customer: { id: 'CUST-003', name: 'Gamma Inc' },
      },
    ];
  }

  /**
   * @private
   * @method _defaultEscalationHandler
   * @description Mock escalation handler – logs the escalation.
   * @param {Object} escalationData - Data about the escalation.
   * @returns {Promise<void>}
   */
  async _defaultEscalationHandler(escalationData) {
    this.logger.info('[DUNNING] Escalation triggered', escalationData);
    // In production, this would call legal APIs or collections services.
    return;
  }

  /**
   * @private
   * @method _getRulesForTenant
   * @description Returns the dunning rules for a given tenant/jurisdiction.
   * @param {string} tenantId - Tenant ID (could contain jurisdiction code).
   * @returns {Object} Rules object.
   */
  _getRulesForTenant(tenantId) {
    // Simple mapping: if tenantId starts with ZA, use ZA rules; otherwise global.
    const jurisdiction = tenantId && tenantId.toUpperCase().startsWith('ZA') ? 'ZA' : 'global';
    return this.rules[jurisdiction] || this.rules.global;
  }

  /**
   * @private
   * @method _calculateDaysOverdue
   * @param {Date} dueDate - Invoice due date.
   * @returns {number} Days overdue (0 if not overdue).
   */
  _calculateDaysOverdue(dueDate) {
    const now = new Date();
    const diffTime = now.getTime() - dueDate.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
  }

  /**
   * @private
   * @method _determineDunningStep
   * @description Given days overdue and rules, determine the dunning level.
   * @param {number} daysOverdue - Days overdue.
   * @param {Object} rules - Dunning rules for the tenant.
   * @returns {Object} The matching step object.
   */
  _determineDunningStep(daysOverdue, rules) {
    const steps = rules.steps;
    // Find the highest applicable step (level)
    let applicableStep = steps[0];
    for (const step of steps) {
      if (daysOverdue >= step.daysOverdue) {
        applicableStep = step;
      }
    }
    return applicableStep;
  }

  /**
   * @private
   * @method _calculateInterest
   * @param {number} amount - Original amount due.
   * @param {number} daysOverdue - Days overdue.
   * @param {number} interestRatePerDay - Daily interest rate.
   * @returns {number} Interest amount.
   */
  _calculateInterest(amount, daysOverdue, interestRatePerDay) {
    return amount * interestRatePerDay * daysOverdue;
  }

  /**
   * @public
   * @method generateRecommendations
   * @description Generates dunning recommendations for a given tenant.
   * @param {string} tenantId - Tenant identifier.
   * @param {Object} options - Optional filters (e.g., limit, status).
   * @returns {Promise<Object>} Recommendations object with status and items.
   */
  async generateRecommendations(tenantId, options = {}) {
    const traceId = options.traceId || `DUN-${crypto.randomBytes(8).toString('hex')}`;
    const startTime = Date.now();

    try {
      this.logger.info('[DUNNING] Generating recommendations', { tenantId, traceId });

      // 1. Fetch overdue invoices
      const invoices = await this.invoiceFetcher(tenantId);
      const recommendations = [];

      // 2. Process each invoice
      for (const invoice of invoices) {
        const daysOverdue = this._calculateDaysOverdue(new Date(invoice.dueDate));
        if (daysOverdue <= 0) continue; // skip not overdue

        const rules = this._getRulesForTenant(tenantId);
        const step = this._determineDunningStep(daysOverdue, rules);
        const interest = this._calculateInterest(
          invoice.amountDue,
          daysOverdue,
          rules.interestRatePerDay
        );
        const totalDue = invoice.amountDue + interest;

        recommendations.push({
          invoiceId: invoice.id,
          customer: invoice.customer,
          daysOverdue,
          step: step,
          interest,
          totalDue,
          currency: invoice.currency || 'ZAR',
          recommendedAction: step.action,
          message: step.label,
          timestamp: new Date().toISOString(),
        });
      }

      // 3. Update health
      this.health.lastRun = new Date().toISOString();
      this.health.recommendationsGenerated += recommendations.length;

      // 4. Broadcast telemetry
      await broadcastTelemetry(tenantId, 'DUNNING_RECOMMENDATIONS', 'GENERATED', 'DunningEngine', {
        traceId,
        count: recommendations.length,
        durationMs: Date.now() - startTime,
      });

      return {
        success: true,
        tenantId,
        recommendations,
        total: recommendations.length,
        generatedAt: new Date().toISOString(),
        traceId,
      };
    } catch (error) {
      this.health.errors += 1;
      this.logger.error('[DUNNING] Error generating recommendations', {
        tenantId,
        traceId,
        error: error.message,
      });
      throw error;
    }
  }

  /**
   * @public
   * @method getStatus
   * @description Returns the current operational status of the dunning engine.
   * @param {string} tenantId - Tenant identifier (optional).
   * @returns {Promise<Object>} Status object.
   */
  async getStatus(tenantId = 'GLOBAL_ROOT') {
    try {
      // In production, we might fetch active dunning cases from the database.
      // For mock, return a synthetic status.
      const rules = this._getRulesForTenant(tenantId);
      return {
        status: this.health.status,
        tenantId,
        engineVersion: '1.0.0-SOVEREIGN',
        lastRun: this.health.lastRun,
        recommendationsGenerated: this.health.recommendationsGenerated,
        activeRules: rules.steps.map(s => s.label),
        errorCount: this.health.errors,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      this.logger.error('[DUNNING] Status retrieval failed', { tenantId, error: error.message });
      throw error;
    }
  }

  /**
   * @public
   * @method escalate
   * @description Escalates a specific dunning case to collections or legal.
   * @param {string} invoiceId - Invoice ID to escalate.
   * @param {Object} escalationDetails - Reason and level.
   * @returns {Promise<Object>} Escalation result.
   */
  async escalate(invoiceId, escalationDetails) {
    const traceId = `ESC-${crypto.randomBytes(6).toString('hex')}`;
    try {
      this.logger.info('[DUNNING] Escalating invoice', { invoiceId, escalationDetails, traceId });
      // Call escalation handler (mock or real)
      await this.escalationHandler({
        invoiceId,
        ...escalationDetails,
        traceId,
        timestamp: new Date().toISOString(),
      });
      return {
        success: true,
        invoiceId,
        escalatedAt: new Date().toISOString(),
        traceId,
      };
    } catch (error) {
      this.logger.error('[DUNNING] Escalation failed', { invoiceId, error: error.message });
      throw error;
    }
  }

  /**
   * @public
   * @method healthCheck
   * @description Returns a simple health check for monitoring.
   * @returns {Object} Health status.
   */
  healthCheck() {
    return {
      status: this.health.status,
      version: '1.0.0-SOVEREIGN',
      uptime: process.uptime ? process.uptime() : null,
      timestamp: new Date().toISOString(),
    };
  }
}

// Export a singleton instance by default (or allow instantiation)
const defaultDunningEngine = new DunningEngine();

export default defaultDunningEngine;
export { DunningEngine, DEFAULT_DUNNING_RULES };
