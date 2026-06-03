/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - REAL‑TIME REPORTING ENGINE [V1.1.0-MARS]                                                                                    ║
 * ║ [MRR | ARR | CHURN | LTV | USAGE ANALYTICS]                                                                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.1.0-MARS | PRODUCTION READY | BILLION DOLLAR SPEC                                                                           ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | BOARDROOM READY                                                                  ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/reportingEngine.js                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated real‑time boardroom KPIs. [2026-05-15]                                              ║
 * ║ • AI Engineering (DeepSeek) - IMPLEMENTED: All core metrics. [2026-05-15]                                                              ║
 * ║ • AI Engineering (DeepSeek) - MARS PROTOCOL: Full JSDoc, parameter/return types, inline notes. [2026-05-15]                            ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import Invoice from '../models/Invoice.js';
import Subscription from '../models/Subscription.js';
import UsageRecord from '../models/UsageRecord.js';

/**
 * Real‑time Reporting Engine – calculates boardroom KPIs for a tenant.
 *
 * **Metrics Provided**:
 * - MRR (Monthly Recurring Revenue)
 * - ARR (Annual Recurring Revenue)
 * - Churn Rate (percentage of customers lost in last month)
 * - Average Monthly Revenue (last 6 paid invoices)
 * - Average Customer Lifetime (in months)
 * - LTV (Lifetime Value = avgMonthly × avgLifetime)
 * - Usage Analytics (daily usage for a given metric, last N days)
 *
 * @class ReportingEngine
 */
class ReportingEngine {
  /**
   * Get the start of the current month (first day, 00:00:00.000).
   *
   * @returns {Date} First day of current month, midnight
   */
  getMonthStart() {
    const d = new Date();
    d.setDate(1);
    d.setHours(0, 0, 0, 0);
    return d;
  }

  /**
   * Get a date representing the start of the previous month.
   *
   * @returns {Date} First day of previous month, midnight
   */
  getLastMonth() {
    const d = new Date();
    d.setMonth(d.getMonth() - 1);
    return d;
  }

  /**
   * Calculate Monthly Recurring Revenue (MRR) – sum of all paid invoice totals
   * with periodStart in the current month.
   *
   * @param {string} tenantId - Tenant identifier
   * @returns {Promise<number>} MRR value (0 if none)
   */
  async getMRR(tenantId) {
    const result = await Invoice.aggregate([
      {
        $match: {
          tenantId,
          status: 'paid',
          periodStart: { $gte: this.getMonthStart() }
        }
      },
      { $group: { _id: null, mrr: { $sum: '$total' } } }
    ]);
    return result[0]?.mrr || 0;
  }

  /**
   * Calculate Annual Recurring Revenue (ARR) = MRR × 12.
   *
   * @param {string} tenantId - Tenant identifier
   * @returns {Promise<number>} ARR value
   */
  async getARR(tenantId) {
    const mrr = await this.getMRR(tenantId);
    return mrr * 12;
  }

  /**
   * Calculate churn rate (%) based on active subscriptions vs those cancelled
   * in the last month.
   *
   * @param {string} tenantId - Tenant identifier
   * @returns {Promise<number>} Churn percentage (0 if no active subscriptions)
   */
  async getChurnRate(tenantId) {
    const subscriptions = await Subscription.find({ tenantId });
    const activeCount = subscriptions.filter(s => s.status === 'active').length;
    const cancelledCount = subscriptions.filter(s => s.status === 'cancelled' && s.cancelledAt > this.getLastMonth()).length;
    if (activeCount === 0) return 0;
    return (cancelledCount / activeCount) * 100;
  }

  /**
   * Calculate average monthly revenue based on the last 6 paid invoices.
   *
   * @param {string} tenantId - Tenant identifier
   * @returns {Promise<number>} Average revenue (0 if no invoices)
   */
  async getAverageMonthlyRevenue(tenantId) {
    const invoices = await Invoice.find({ tenantId, status: 'paid' }).sort({ createdAt: -1 }).limit(6);
    const total = invoices.reduce((sum, inv) => sum + inv.total, 0);
    return invoices.length ? total / invoices.length : 0;
  }

  /**
   * Calculate average customer lifetime (in months) based on first and last
   * invoice dates for each customer.
   *
   * @param {string} tenantId - Tenant identifier
   * @returns {Promise<number>} Average lifetime in months (0 if no customers)
   */
  async getAverageCustomerLifetime(tenantId) {
    // Simplified: average months between first and last invoice
    const customers = await Invoice.aggregate([
      { $match: { tenantId, status: 'paid' } },
      { $group: { _id: '$customerId', first: { $min: '$periodStart' }, last: { $max: '$periodEnd' } } }
    ]);
    let totalMonths = 0;
    for (const c of customers) {
      const months = (c.last - c.first) / (30 * 24 * 60 * 60 * 1000);
      totalMonths += months;
    }
    return customers.length ? totalMonths / customers.length : 0;
  }

  /**
   * Calculate Lifetime Value (LTV) = average monthly revenue × average lifetime (months).
   *
   * @param {string} tenantId - Tenant identifier
   * @returns {Promise<number>} LTV value
   */
  async getLTV(tenantId) {
    const avgMonthly = await this.getAverageMonthlyRevenue(tenantId);
    const avgLifetime = await this.getAverageCustomerLifetime(tenantId);
    return avgMonthly * avgLifetime;
  }

  /**
   * Get daily usage analytics for a specific metric (e.g., 'AI_STRIKE') over the last N days.
   *
   * @param {string} tenantId - Tenant identifier
   * @param {string} metricName - Usage type (e.g., 'AI_STRIKE')
   * @param {number} [days=30] - Number of days to look back
   * @returns {Promise<Array>} Array of daily aggregates with `_id` (date string) and `total` (quantity sum)
   *
   * @example
   * const aiUsage = await reportingEngine.getUsageAnalytics('TENANT_A', 'AI_STRIKE', 7);
   * // [{ _id: '2026-05-15', total: 142 }, { _id: '2026-05-14', total: 98 }]
   */
  async getUsageAnalytics(tenantId, metricName, days = 30) {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    return await UsageRecord.aggregate([
      {
        $match: {
          tenantId,
          type: metricName,
          createdAt: { $gte: startDate }
        }
      },
      {
        $group: {
          _id: { $dateToString: { format: '%Y-%m-%d', date: '$createdAt' } },
          total: { $sum: '$quantity' }
        }
      },
      { $sort: { _id: 1 } }
    ]);
  }
}

export default ReportingEngine;
