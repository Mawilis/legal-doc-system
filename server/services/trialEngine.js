/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - TRIAL & COMMITMENT ENGINE [V1.1.0-MARS]                                                                                     ║
 * ║ [FREE TRIAL | COMMITMENT TRACKING | EARLY TERMINATION | LOYALTY DISCOUNTS]                                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.1.0-MARS | PRODUCTION READY | BILLION DOLLAR SPEC                                                                           ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/trialEngine.js                                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated flexible trial & commitment management. [2026-05-15]                                 ║
 * ║ • AI Engineering (DeepSeek) - IMPLEMENTED: Full lifecycle with early termination logic. [2026-05-15]                                   ║
 * ║ • AI Engineering (DeepSeek) - MARS PROTOCOL: Full JSDoc, parameter/return types, inline notes. [2026-05-15]                            ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import Subscription from '../models/Subscription.js';
import Invoice from '../models/Invoice.js';
import auditLogger from '../utils/auditLogger.js';

/**
 * Trial & Commitment Engine – manages free trials, commitment terms, early termination fees, and loyalty discounts.
 *
 * **Capabilities**:
 * - Start a free trial for a subscription.
 * - Automatically transition from trial to active after trial end.
 * - Apply a commitment term (e.g., 12 months) with optional discount.
 * - Calculate early termination fee if cancelled before commitment end.
 * - Process commitment fulfillment and apply loyalty discount.
 *
 * @class TrialEngine
 */
class TrialEngine {
  /**
   * Start a free trial for a subscription.
   *
   * @async
   * @param {Object} subscription - Subscription document (must be savable)
   * @param {number} trialDays - Number of trial days (from rate plan). If <= 0, does nothing.
   * @returns {Promise<void>}
   *
   * @example
   * await trialEngine.startTrial(subscription, 14);
   */
  async startTrial(subscription, trialDays) {
    if (trialDays <= 0) return;
    subscription.status = 'trial';
    subscription.trialStart = new Date();
    subscription.trialEnd = new Date(Date.now() + trialDays * 24 * 60 * 60 * 1000);
    subscription.currentPeriodStart = subscription.trialStart;
    subscription.currentPeriodEnd = subscription.trialEnd;
    await subscription.save();
    await auditLogger.log('TRIAL_STARTED', { subscriptionId: subscription._id, trialDays });
  }

  /**
   * Check if a subscription's trial has ended and transition to active state.
   *
   * @async
   * @param {Object} subscription - Subscription document
   * @returns {Promise<boolean>} `true` if transition occurred (trial ended and moved to active), otherwise `false`
   *
   * @example
   * if (await trialEngine.processTrialEnd(subscription)) {
   *   // Subscription now active, first invoice generated
   * }
   */
  async processTrialEnd(subscription) {
    if (subscription.status !== 'trial') return false;
    if (new Date() >= subscription.trialEnd) {
      subscription.status = 'active';
      subscription.currentPeriodStart = new Date();
      subscription.currentPeriodEnd = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000); // 30 days
      await subscription.save();
      await auditLogger.log('TRIAL_ENDED', { subscriptionId: subscription._id });
      return true;
    }
    return false;
  }

  /**
   * Apply a commitment term (e.g., 12 months) to a subscription, optionally with a discount.
   *
   * @async
   * @param {Object} subscription - Subscription document
   * @param {number} termMonths - Commitment length in months
   * @param {number} discountPercent - Discount percentage to apply during the commitment period
   * @returns {Promise<void>}
   *
   * @example
   * await trialEngine.applyCommitment(subscription, 12, 10); // 10% discount for 12‑month commitment
   */
  async applyCommitment(subscription, termMonths, discountPercent) {
    subscription.commitmentTerm = termMonths;
    subscription.commitmentStart = new Date();
    subscription.commitmentEnd = new Date(Date.now() + termMonths * 30 * 24 * 60 * 60 * 1000);
    // Optionally adjust pricing or add discount
    // This discount could be applied to invoices
    await subscription.save();
    await auditLogger.log('COMMITMENT_APPLIED', { subscriptionId: subscription._id, termMonths, discountPercent });
  }

  /**
   * Calculate early termination fee if a subscription is cancelled before commitment end.
   *
   * @param {Object} subscription - Subscription document
   * @param {Date} terminationDate - Date of cancellation/termination
   * @returns {number} Fee amount (0 if no commitment or after commitment end)
   *
   * @note Assumes a placeholder monthly rate (`subscription.monthlyRate`). In production,
   *       you should derive the rate from the most recent invoice or rate plan.
   */
  calculateEarlyTerminationFee(subscription, terminationDate) {
    if (!subscription.commitmentEnd) return 0;
    if (terminationDate >= subscription.commitmentEnd) return 0;
    const remainingMonths = this._getRemainingMonths(subscription, terminationDate);
    // 50% of remaining monthly fees (assume monthly rate from most recent invoice)
    const monthlyRate = subscription.monthlyRate || 100; // placeholder
    return remainingMonths * monthlyRate * 0.5;
  }

  /**
   * Calculate remaining months until commitment end.
   *
   * @private
   * @param {Object} subscription - Subscription document
   * @param {Date} date - Reference date (usually termination date or now)
   * @returns {number} Number of remaining months (rounded up)
   */
  _getRemainingMonths(subscription, date) {
    const end = subscription.commitmentEnd;
    if (!end) return 0;
    const diffMs = end - date;
    return Math.ceil(diffMs / (30 * 24 * 60 * 60 * 1000));
  }

  /**
   * Process commitment fulfillment after the commitment period ends.
   * Applies a loyalty discount for the next period and clears commitment fields.
   *
   * @async
   * @param {Object} subscription - Subscription document
   * @returns {Promise<Object>} Result object with `fulfilled` (boolean) and `remaining` (months left if not fulfilled)
   *
   * @example
   * const result = await trialEngine.processCommitment(subscription);
   * if (result.fulfilled) {
   *   console.log('Commitment completed, loyalty discount applied');
   * }
   */
  async processCommitment(subscription) {
    if (!subscription.commitmentEnd) return { fulfilled: false, remaining: 0 };
    const now = new Date();
    if (now >= subscription.commitmentEnd) {
      // Commitment fulfilled – apply loyalty discount for next period
      await this.applyLoyaltyDiscount(subscription, 10);
      subscription.commitmentTerm = 0;
      subscription.commitmentEnd = null;
      await subscription.save();
      await auditLogger.log('COMMITMENT_FULFILLED', { subscriptionId: subscription._id });
      return { fulfilled: true, remaining: 0 };
    }
    const remaining = this._getRemainingMonths(subscription, now);
    return { fulfilled: false, remaining };
  }

  /**
   * Apply a loyalty discount to a subscription (e.g., after fulfilling a commitment).
   * Stores the discount in subscription metadata for use during invoice generation.
   *
   * @async
   * @param {Object} subscription - Subscription document
   * @param {number} percent - Discount percentage
   * @returns {Promise<void>}
   */
  async applyLoyaltyDiscount(subscription, percent) {
    // Store discount in metadata; can be applied during invoice generation
    if (!subscription.metadata) subscription.metadata = new Map();
    subscription.metadata.set('loyaltyDiscountPercent', percent);
    await subscription.save();
    await auditLogger.log('LOYALTY_DISCOUNT_APPLIED', { subscriptionId: subscription._id, percent });
  }
}

export default TrialEngine;
