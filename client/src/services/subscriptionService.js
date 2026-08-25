/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN SUBSCRIPTION SERVICE [V1.0.0-OMEGA-SUBSCRIPTION]                                                                ║
 * ║ [RECURRING BILLING LIFECYCLE | FORENSIC SEALING | IDEMPOTENCY | KENNEL-AWARE]                                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-OMEGA | PRODUCTION READY | TRILLION DOLLAR SPEC                                                                        ║
 * ║ EPITOME: FRONTEND SERVICE FOR SUBSCRIPTION MANAGEMENT THAT OBLITERATES ZOHO BILLING, LEMLIST, AND HUBSPOT                             ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/subscriptionService.js                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ WHY THIS OBLITERATES THE COMPETITION:                                                                                                 ║
 * ║   - Zoho Billing requires manual reconciliation; our service provides real‑time audit trails.                                        ║
 * ║   - Lemlist has no native subscription management; we provide full lifecycle with cryptographic proofs.                               ║
 * ║   - HubSpot requires third‑party integrations; we are native and mesh‑aware.                                                          ║
 * ║   - Apollo.io lacks forensic sealing; every action returns a SHA3‑512 proof hash for boardroom audits.                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated enterprise‑grade subscription lifecycle with forensic integrity.                    ║
 * ║ • AI Engineering (DeepSeek) – ARCHITECTED: Full subscription service with create, list, get, pause, resume, cancel, upgrade,          ║
 * ║   downgrade, reactivate, and audit endpoints – all integrated with the Sovereign Kennel.                                              ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import sovereignClient from '../utils/sovereignClient';

/**
 * @class SubscriptionService
 * @description Provides a typed interface for interacting with the subscription API.
 * @collaboration All methods return the API response data directly, with the response envelope stripped.
 */
class SubscriptionService {
  /**
   * Creates a new subscription.
   * @param {Object} data - Subscription creation payload.
   * @param {string} data.tenantId - Target tenant ID.
   * @param {string} data.planId - Plan identifier.
   * @param {string} data.billingFrequency - 'monthly', 'quarterly', 'annual'.
   * @param {number} data.amount - Billing amount in minor units.
   * @param {string} data.currency - ISO 4217 currency code.
   * @param {string} [data.idempotencyKey] - Optional idempotency key.
   * @param {Object} [data.metadata] - Additional metadata.
   * @param {number} [data.trialPeriodDays] - Trial period in days.
   * @param {string} [data.startDate] - ISO start date.
   * @returns {Promise<Object>} Created subscription with proof.
   */
  async create(data) {
    const response = await sovereignClient.post('/subscriptions', data);
    return response.data?.data || response.data;
  }

  /**
   * Lists subscriptions with pagination.
   * @param {Object} [params] - Query parameters.
   * @param {number} [params.page=1] - Page number.
   * @param {number} [params.limit=20] - Items per page.
   * @param {string} [params.status] - Filter by status.
   * @returns {Promise<Object>} Paginated list of subscriptions.
   */
  async list({ page = 1, limit = 20, status } = {}) {
    const response = await sovereignClient.get('/subscriptions', { params: { page, limit, status } });
    return response.data?.data || response.data;
  }

  /**
   * Retrieves a single subscription by ID.
   * @param {string} subscriptionId - Subscription ID.
   * @returns {Promise<Object>} Subscription data.
   */
  async get(subscriptionId) {
    const response = await sovereignClient.get(`/subscriptions/${subscriptionId}`);
    return response.data?.data || response.data;
  }

  /**
   * Pauses an active subscription.
   * @param {string} subscriptionId - Subscription ID.
   * @param {Object} [options] - Pause options.
   * @param {string} [options.reason] - Reason for pause.
   * @param {string} [options.pauseUntil] - ISO date for auto‑resume.
   * @param {Object} [options.metadata] - Additional metadata.
   * @returns {Promise<Object>} Updated subscription with proof.
   */
  async pause(subscriptionId, { reason = '', pauseUntil = null, metadata = {} } = {}) {
    const response = await sovereignClient.patch(`/subscriptions/${subscriptionId}/pause`, {
      reason,
      pauseUntil,
      metadata,
    });
    return response.data?.data || response.data;
  }

  /**
   * Resumes a paused subscription.
   * @param {string} subscriptionId - Subscription ID.
   * @param {Object} [metadata] - Additional metadata.
   * @returns {Promise<Object>} Updated subscription with proof.
   */
  async resume(subscriptionId, metadata = {}) {
    const response = await sovereignClient.patch(`/subscriptions/${subscriptionId}/resume`, { metadata });
    return response.data?.data || response.data;
  }

  /**
   * Cancels a subscription.
   * @param {string} subscriptionId - Subscription ID.
   * @param {Object} [options] - Cancel options.
   * @param {string} [options.reason] - Cancellation reason.
   * @param {boolean} [options.immediate=false] - Cancel immediately or at period end.
   * @param {Object} [options.metadata] - Additional metadata.
   * @returns {Promise<Object>} Updated subscription with proof.
   */
  async cancel(subscriptionId, { reason = '', immediate = false, metadata = {} } = {}) {
    const response = await sovereignClient.delete(`/subscriptions/${subscriptionId}`, {
      data: { reason, immediate, metadata },
    });
    return response.data?.data || response.data;
  }

  /**
   * Upgrades a subscription to a higher‑tier plan.
   * @param {string} subscriptionId - Subscription ID.
   * @param {Object} data - Upgrade data.
   * @param {string} data.newPlanId - New plan ID.
   * @param {number} data.newAmount - New billing amount.
   * @param {string} data.newCurrency - New currency.
   * @param {Object} [data.metadata] - Additional metadata.
   * @returns {Promise<Object>} Updated subscription with proration proof.
   */
  async upgrade(subscriptionId, { newPlanId, newAmount, newCurrency, metadata = {} }) {
    const response = await sovereignClient.patch(`/subscriptions/${subscriptionId}/upgrade`, {
      newPlanId,
      newAmount,
      newCurrency,
      metadata,
    });
    return response.data?.data || response.data;
  }

  /**
   * Downgrades a subscription to a lower‑tier plan.
   * @param {string} subscriptionId - Subscription ID.
   * @param {Object} data - Downgrade data.
   * @param {string} data.newPlanId - New plan ID.
   * @param {number} data.newAmount - New billing amount.
   * @param {string} data.newCurrency - New currency.
   * @param {Object} [data.metadata] - Additional metadata.
   * @returns {Promise<Object>} Updated subscription with proration proof.
   */
  async downgrade(subscriptionId, { newPlanId, newAmount, newCurrency, metadata = {} }) {
    const response = await sovereignClient.patch(`/subscriptions/${subscriptionId}/downgrade`, {
      newPlanId,
      newAmount,
      newCurrency,
      metadata,
    });
    return response.data?.data || response.data;
  }

  /**
   * Reactivates a cancelled subscription.
   * @param {string} subscriptionId - Subscription ID.
   * @param {Object} [metadata] - Additional metadata.
   * @returns {Promise<Object>} Reactivated subscription with proof.
   */
  async reactivate(subscriptionId, metadata = {}) {
    const response = await sovereignClient.post(`/subscriptions/${subscriptionId}/reactivate`, { metadata });
    return response.data?.data || response.data;
  }

  /**
   * Retrieves the audit trail for a subscription.
   * @param {string} subscriptionId - Subscription ID.
   * @returns {Promise<Object>} Audit trail data.
   */
  async getAudit(subscriptionId) {
    const response = await sovereignClient.get(`/subscriptions/${subscriptionId}/audit`);
    return response.data?.data || response.data;
  }
}

// Export singleton instance
export const subscriptionService = new SubscriptionService();
export default subscriptionService;
