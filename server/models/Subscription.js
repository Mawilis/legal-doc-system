/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SUBSCRIPTION MODEL [V1.1.0-MARS]                                                                                            ║
 * ║ [TRIAL & COMMITMENT TRACKING | MULTI‑TENANT ISOLATION | STATE MACHINE]                                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.1.0-MARS | PRODUCTION READY | BILLION DOLLAR SPEC                                                                           ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/Subscription.js                                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated trial and commitment lifecycle. [2026-05-15]                                         ║
 * ║ • AI Engineering (DeepSeek) - IMPLEMENTED: Full subscription state machine. [2026-05-15]                                               ║
 * ║ • AI Engineering (DeepSeek) - MARS PROTOCOL: Full JSDoc documentation, field descriptions, index annotations. [2026-05-15]             ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';

/**
 * Subscription schema – tracks a customer's subscription to a product/rate plan.
 *
 * **Features**:
 * - Multi‑tenant isolation via `tenantId`.
 * - State machine: `trial` → `active` → `past_due` → `cancelled`/`expired`/`terminated`.
 * - Trial start/end tracking.
 * - Billing periods (`currentPeriodStart`/`currentPeriodEnd`).
 * - Commitment terms (minimum term, early termination fee).
 * - Snapshot of the rate plan at activation.
 */
const SubscriptionSchema = new mongoose.Schema({
  /**
   * Unique identifier for the subscription (e.g., "SUB_ABC123").
   * @type {String}
   * @required
   * @unique
   */
  subscriptionId: { type: String, unique: true, required: true },

  /**
   * Tenant ID that owns this subscription (for multi‑tenant isolation).
   * @type {String}
   * @required
   * @index
   */
  tenantId: { type: String, required: true, index: true },

  /**
   * Customer identifier – the entity paying for the subscription.
   * @type {String}
   * @required
   * @index
   */
  customerId: { type: String, required: true, index: true },

  /**
   * Reference to the `Product.productId` being subscribed to.
   * @type {String}
   * @required
   */
  productId: { type: String, required: true },

  /**
   * Reference to the chosen rate plan within the product.
   * @type {String}
   * @required
   */
  ratePlanId: { type: String, required: true },

  /**
   * Snapshot of the rate plan at the time of subscription activation.
   * Preserves pricing and charges even if the master catalog changes.
   * @type {Object}
   */
  ratePlanSnapshot: { type: mongoose.Schema.Types.Mixed },

  /**
   * Current subscription status.
   * - `trial`: Free trial period active.
   * - `active`: Regular billing period.
   * - `past_due`: Payment overdue.
   * - `cancelled`: Cancelled by customer (may still be active until period end).
   * - `expired`: Period ended without renewal.
   * - `terminated`: Admin/forced termination.
   * @type {String}
   * @enum ['trial', 'active', 'past_due', 'cancelled', 'expired', 'terminated']
   * @default 'trial'
   */
  status: {
    type: String,
    enum: ['trial', 'active', 'past_due', 'cancelled', 'expired', 'terminated'],
    default: 'trial'
  },

  /**
   * Start date of the trial period.
   * @type {Date}
   */
  trialStart: { type: Date },

  /**
   * End date of the trial period (after which billing starts).
   * @type {Date}
   */
  trialEnd: { type: Date },

  /**
   * Start date of the current billing period.
   * @type {Date}
   * @required
   */
  currentPeriodStart: { type: Date, required: true },

  /**
   * End date of the current billing period (when next invoice is due).
   * @type {Date}
   * @required
   */
  currentPeriodEnd: { type: Date, required: true },

  /**
   * Whether the subscription will cancel at the end of the current period.
   * @type {Boolean}
   * @default false
   */
  cancelAtPeriodEnd: { type: Boolean, default: false },

  /**
   * Timestamp when the subscription was cancelled (if cancelled).
   * @type {Date}
   */
  cancelledAt: { type: Date },

  /**
   * Timestamp when the subscription ended (if expired/terminated).
   * @type {Date}
   */
  endedAt: { type: Date },

  // ============================================================================
  // COMMITMENT TRACKING
  // ============================================================================

  /**
   * Minimum commitment term in months (0 = no commitment).
   * @type {Number}
   * @default 0
   */
  commitmentTerm: { type: Number, default: 0 },

  /**
   * Start date of the commitment period.
   * @type {Date}
   */
  commitmentStart: { type: Date },

  /**
   * End date of the commitment period.
   * @type {Date}
   */
  commitmentEnd: { type: Date },

  /**
   * Fee applied if the subscription is terminated before the commitment end.
   * @type {Number}
   * @default 0
   */
  earlyTerminationFee: { type: Number, default: 0 },

  /**
   * Polymorphic metadata for industry‑specific fields.
   * @type {Map}
   */
  metadata: { type: Map, of: mongoose.Schema.Types.Mixed }
}, { timestamps: true });

// ============================================================================
// ⚡ COMPOUND INDEXES FOR PERFORMANCE
// ============================================================================

/**
 * Compound index for tenant + customer queries (list subscriptions for a customer).
 */
SubscriptionSchema.index({ tenantId: 1, customerId: 1 });

/**
 * Index for expiring subscriptions (e.g., cron jobs to process renewals/expirations).
 */
SubscriptionSchema.index({ status: 1, currentPeriodEnd: 1 });

// ============================================================================
// 📤 MODEL EXPORT
// ============================================================================

/**
 * Subscription model – manages customer subscriptions to products and rate plans.
 * Use this model to create, renew, cancel, and track subscription lifecycles.
 *
 * @type {mongoose.Model}
 *
 * @example
 * const subscription = await Subscription.create({
 *   subscriptionId: 'SUB_ABC123',
 *   tenantId: 'TENANT_A',
 *   customerId: 'CUST_456',
 *   productId: 'PROD_SAAS',
 *   ratePlanId: 'RP_MONTHLY',
 *   currentPeriodStart: new Date(),
 *   currentPeriodEnd: new Date(Date.now() + 30 * 86400000),
 *   trialEnd: new Date(Date.now() + 7 * 86400000)
 * });
 */
const Subscription = mongoose.model('Subscription', SubscriptionSchema);
export default Subscription;
