/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - PRODUCT CATALOG MODEL [V1.1.0-MARS]                                                                                         ║
 * ║ [3‑LAYER CAKE | MULTI‑TENANT ISOLATION | POLYMORPHIC METADATA]                                                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.1.0-MARS | PRODUCTION READY | BILLION DOLLAR SPEC                                                                           ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/Product.js                                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated multi‑tenant product catalog for any industry. [2026-05-15]                          ║
 * ║ • AI Engineering (DeepSeek) - IMPLEMENTED: 3‑layer cake schema with tiered pricing. [2026-05-15]                                       ║
 * ║ • AI Engineering (DeepSeek) - MARS PROTOCOL: Full JSDoc documentation for all schemas, fields, and sub‑schemas. [2026-05-15]           ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';

// ============================================================================
// 📊 TIER SCHEMA (for tiered pricing)
// ============================================================================

/**
 * Sub‑schema for a single pricing tier.
 * Used within `ChargeSchema.pricing.tiers` to define volume‑based pricing brackets.
 *
 * @example
 * // Tier 1: 1‑10 units at $49
 * { upTo: 10, price: 49, flatFee: 0 }
 * // Tier 2: 11‑50 units at $99
 * { upTo: 50, price: 99, flatFee: 0 }
 * // Tier 3: 51+ units at $149
 * { upTo: Infinity, price: 149, flatFee: 0 }
 */
const TierSchema = new mongoose.Schema({
  /**
   * Upper limit of the tier (inclusive). Use `Infinity` for the last tier.
   * @type {Number}
   * @required
   */
  upTo: { type: Number, required: true },
  /**
   * Price for this tier (e.g., $49 for the first 10 units).
   * @type {Number}
   * @required
   */
  price: { type: Number, required: true },
  /**
   * Optional flat fee added to the tier (e.g., a setup fee per tier).
   * @type {Number}
   * @default 0
   */
  flatFee: { type: Number, default: 0 }
});

// ============================================================================
// 💰 CHARGE SCHEMA (atomic pricing unit)
// ============================================================================

/**
 * Sub‑schema for a single charge (pricing component) within a rate plan.
 * Supports flat, tiered, volume, and package pricing models.
 */
const ChargeSchema = new mongoose.Schema({
  /**
   * Unique identifier for the charge (e.g., "CHARGE_AI_CALLS").
   * @type {String}
   * @required
   * @unique
   */
  chargeId: { type: String, unique: true, required: true },
  /**
   * Display name of the charge (e.g., "AI Processing Calls").
   * @type {String}
   * @required
   */
  name: { type: String, required: true },
  /**
   * Type of charge – determines billing behaviour.
   * @type {String}
   * @enum ['recurring', 'usage', 'one-time', 'minimum', 'overage', 'setup']
   * @required
   */
  type: {
    type: String,
    enum: ['recurring', 'usage', 'one-time', 'minimum', 'overage', 'setup'],
    required: true
  },
  /**
   * Pricing configuration for the charge.
   * @type {Object}
   */
  pricing: {
    /**
     * Pricing model – how the price is calculated.
     * @type {String}
     * @enum ['flat', 'tiered', 'volume', 'package']
     * @default 'flat'
     */
    model: { type: String, enum: ['flat', 'tiered', 'volume', 'package'], default: 'flat' },
    /**
     * Flat price (used when `model` is 'flat').
     * @type {Number}
     */
    price: { type: Number },
    /**
     * Array of tiers for tiered pricing (used when `model` is 'tiered').
     * @type {Array}
     */
    tiers: [TierSchema],
    /**
     * Unit of measurement (e.g., "API Call", "User", "GB").
     * @type {String}
     */
    unit: { type: String },
    /**
     * Number of units included in the base price (free allowance).
     * @type {Number}
     * @default 0
     */
    includedUnits: { type: Number, default: 0 },
    /**
     * Per‑unit rate for usage beyond `includedUnits`.
     * @type {Number}
     */
    overageRate: { type: Number },
    /**
     * Minimum monthly fee (for minimum commitment charges).
     * @type {Number}
     */
    minCommitment: { type: Number },
    /**
     * One‑time setup fee (for setup charges).
     * @type {Number}
     */
    setupFee: { type: Number }
  },
  /**
   * Billing schedule for recurring charges.
   * @type {Object}
   */
  billingSchedule: {
    /**
     * Billing interval unit.
     * @type {String}
     * @enum ['day', 'week', 'month', 'year']
     * @default 'month'
     */
    interval: { type: String, enum: ['day', 'week', 'month', 'year'], default: 'month' },
    /**
     * Number of intervals (e.g., `intervalCount: 3` with `interval: 'month'` = quarterly).
     * @type {Number}
     * @default 1
     */
    intervalCount: { type: Number, default: 1 },
    /**
     * Billing alignment – whether to align to calendar (e.g., first of month) or subscription anniversary.
     * @type {String}
     * @enum ['calendar', 'anniversary', 'custom']
     * @default 'calendar'
     */
    billingAlignment: { type: String, enum: ['calendar', 'anniversary', 'custom'], default: 'calendar' }
  },
  /**
   * Tax rate applied to this charge (e.g., 0.15 for 15% VAT).
   * @type {Number}
   * @default 0.15
   */
  taxRate: { type: Number, default: 0.15 }
});

// ============================================================================
// 📋 RATE PLAN SCHEMA (collection of charges)
// ============================================================================

/**
 * Sub‑schema for a rate plan (a pricing bundle) under a product.
 * A product can have multiple rate plans (e.g., Basic, Pro, Enterprise).
 */
const RatePlanSchema = new mongoose.Schema({
  /**
   * Unique identifier for the rate plan (e.g., "RATEPLAN_PRO_MONTHLY").
   * @type {String}
   * @required
   * @unique
   */
  ratePlanId: { type: String, unique: true, required: true },
  /**
   * Display name of the rate plan (e.g., "Professional Monthly").
   * @type {String}
   * @required
   */
  name: { type: String, required: true },
  /**
   * Billing period for the rate plan.
   * @type {String}
   * @enum ['monthly', 'yearly', 'one-time', 'custom']
   * @required
   */
  billingPeriod: { type: String, enum: ['monthly', 'yearly', 'one-time', 'custom'], required: true },
  /**
   * Array of charges included in this rate plan.
   * @type {Array}
   */
  charges: [ChargeSchema],
  /**
   * Number of free trial days (0 means no trial).
   * @type {Number}
   * @default 0
   */
  trialDays: { type: Number, default: 0 },
  /**
   * Commitment term in months (e.g., 12 for annual commitment).
   * @type {Number}
   * @default 1
   */
  commitmentTerm: { type: Number, default: 1 },
  /**
   * Discount percentage for committing to the full term.
   * @type {Number}
   * @default 0
   */
  commitmentDiscountPercent: { type: Number, default: 0 }
});

// ============================================================================
// 🏛️ PRODUCT SCHEMA (top level – a billable entity)
// ============================================================================

/**
 * Product schema – top level of the catalog hierarchy.
 * A product contains one or more rate plans, each containing charges.
 * Supports multi‑tenant isolation via `tenantId`.
 */
const ProductSchema = new mongoose.Schema({
  /**
   * Unique identifier for the product (e.g., "PROD_AI_PLATFORM").
   * @type {String}
   * @required
   * @unique
   */
  productId: { type: String, unique: true, required: true },
  /**
   * Display name of the product (e.g., "AI Processing Platform").
   * @type {String}
   * @required
   */
  name: { type: String, required: true },
  /**
   * Detailed description of the product.
   * @type {String}
   */
  description: { type: String },
  /**
   * Tenant ID for multi‑tenant isolation – only the owning tenant can access.
   * @type {String}
   * @required
   * @index
   */
  tenantId: { type: String, required: true, index: true },
  /**
   * Array of rate plans under this product.
   * @type {Array}
   */
  ratePlans: [RatePlanSchema],
  /**
   * Whether the product is active and available for sale.
   * @type {Boolean}
   * @default true
   */
  active: { type: Boolean, default: true },
  /**
   * Polymorphic metadata for industry‑specific fields (e.g., `{ legalDisclaimers: [...] }`).
   * @type {Map}
   */
  metadata: { type: Map, of: mongoose.Schema.Types.Mixed }
}, { timestamps: true });

// ============================================================================
// ⚡ INDEXES FOR PERFORMANCE
// ============================================================================

/**
 * Compound index for tenant isolation with active status.
 */
ProductSchema.index({ tenantId: 1, active: 1 });

/**
 * Unique index on productId for fast lookup.
 */
ProductSchema.index({ productId: 1 });

// ============================================================================
// 📤 MODEL EXPORT
// ============================================================================

/**
 * Product model – the top level of the product catalog.
 * Use this model to create, read, update, and delete products with their rate plans and charges.
 *
 * @type {mongoose.Model}
 *
 * @example
 * // Create a new product with a rate plan and charge
 * const product = await Product.create({
 *   productId: 'PROD_SAAS_PLATFORM',
 *   name: 'SaaS Platform',
 *   tenantId: 'TENANT_ABC',
 *   ratePlans: [{
 *     ratePlanId: 'RP_MONTHLY',
 *     name: 'Monthly Subscription',
 *     billingPeriod: 'monthly',
 *     charges: [{
 *       chargeId: 'CHG_AI_CALLS',
 *       name: 'AI Processing Calls',
 *       type: 'usage',
 *       pricing: { model: 'tiered', tiers: [{ upTo: 1000, price: 49 }, { upTo: Infinity, price: 99 }], unit: 'call' }
 *     }]
 *   }]
 * });
 */
const Product = mongoose.model('Product', ProductSchema);
export default Product;
