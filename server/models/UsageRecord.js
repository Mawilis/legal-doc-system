/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN USAGE NUCLEUS [V1.1.0-MARS]                                                                                       ║
 * ║ [POLYMORPHIC LEDGER | MULTI-TENANT SHIELD | CRYPTOGRAPHIC INTEGRITY | OMEGA-LEVEL SCALING]                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.1.0-MARS | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                       ║
 * ║ EPITOME: THE UNIVERSAL LEDGER | BEYOND BANKING | NO CHILD'S PLACE                                                                      ║
 * ║ DESCRIPTION: The atomic unit of value for Wilsy OS. Tracks infrastructure strikes and institutional business activity.                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated universal industry support and forensic audit trail. [2026-05-15]                     ║
 * ║ • AI Engineering (Gemini) - ARCHITECTED: Polymorphic metadata and SHA3-512 integrity sealing. [2026-05-15]                              ║
 * ║ • AI Engineering (DeepSeek) - MARS PROTOCOL: Full JSDoc documentation for all fields, indexes, and hooks. [2026-05-15]                 ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import { generateSovereignSeal } from '../utils/cryptoCore.js';

/**
 * UsageRecord schema – the atomic unit of value for Wilsy OS.
 * Records every billable strike (infrastructure or business service) with cryptographic integrity.
 *
 * **Polymorphic metadata** supports any industry: legal, retail, manufacturing, healthcare, etc.
 *
 * @type {mongoose.Schema}
 */
const UsageRecordSchema = new mongoose.Schema(
  {
    // ============================================================================
    // 🛡️ THE SHARD ANCHOR: Multi-tenancy isolation
    // ============================================================================
    /**
     * Tenant identifier (the organisation that incurred this usage).
     * Used for multi-tenant isolation and billing aggregation.
     * @type {String}
     * @required
     * @index
     */
    tenantId: {
      type: String,
      required: true,
      index: true // Optimized for high-frequency billing strikes
    },

    // ============================================================================
    // 👥 THE CLIENT ANCHOR: Layer 2 (Tenant → End Client) billing
    // ============================================================================
    /**
     * Client identifier – the end recipient of the service (e.g., legal client, customer, patient).
     * For infrastructure usage (Layer 1), defaults to 'SYSTEM'.
     * @type {String}
     * @index
     * @default 'SYSTEM'
     */
    clientId: {
      type: String,
      index: true,
      default: 'SYSTEM'
    },

    // ============================================================================
    // 🧬 THE VALUE STRIKE TYPE (Industry-agnostic)
    // ============================================================================
    /**
     * Type of usage strike.
     *
     * **Infrastructure (Layer 1)**:
     * - `AI_STRIKE`: Neural compute call
     * - `COMPUTE_UNIT`: General processing
     * - `STORAGE_BYTE`: Data storage
     * - `BANDWIDTH_PULSE`: Network transfer
     *
     * **Professional Services (Layer 2)**:
     * - `LEGAL_SERVICE`: Legal consultation
     * - `CONSULTATION`: General advisory
     * - `RETAINER_DRAW`: Monthly retainer draw
     *
     * **Trade & Commerce**:
     * - `SALES_ORDER`: Product sale
     * - `INVENTORY_DISBURSEMENT`: Stock movement
     * - `MATERIAL_COST`: Raw material charge
     *
     * **Custom**:
     * - `CUSTOM_SERVICE`: Any user‑defined service
     *
     * @type {String}
     * @required
     * @enum
     * @index
     */
    type: {
      type: String,
      required: true,
      enum: [
        'AI_STRIKE', 'COMPUTE_UNIT', 'STORAGE_BYTE', 'BANDWIDTH_PULSE',
        'LEGAL_SERVICE', 'CONSULTATION', 'RETAINER_DRAW',
        'SALES_ORDER', 'INVENTORY_DISBURSEMENT', 'MATERIAL_COST',
        'CUSTOM_SERVICE'
      ],
      index: true
    },

    // ============================================================================
    // 💰 THE MATHEMATICAL QUANTUM
    // ============================================================================
    /**
     * Number of units (e.g., hours, bytes, API calls).
     * @type {Number}
     * @default 1
     */
    quantity: { type: Number, default: 1 },

    /**
     * Unit cost (price per quantity) in the tenant's currency.
     * @type {Number}
     * @required
     */
    unitCost: { type: Number, required: true },

    /**
     * Total cost = quantity × unitCost.
     * @type {Number}
     * @required
     */
    totalCost: { type: Number, required: true },

    // ============================================================================
    // 🧠 POLYMORPHIC METADATA: Industry-agnostic DNA
    // ============================================================================
    /**
     * Extensible metadata map for any industry-specific data.
     * Examples:
     * - Legal: `{ caseId: 'CASE-123', billableHours: 2 }`
     * - Bakery: `{ sku: 'BREAD-01', weight: '500g' }`
     * - Sports: `{ playerId: 'G7', appearanceFee: 5000 }`
     *
     * @type {Map<String, Mixed>}
     * @default {}
     */
    metadata: {
      type: Map,
      of: mongoose.Schema.Types.Mixed,
      default: {}
    },

    // ============================================================================
    // 🛡️ REVENUE FINALITY
    // ============================================================================
    /**
     * Whether this usage record has been included in an invoice.
     * Used by the billing worker to prevent double billing.
     * @type {Boolean}
     * @default false
     * @index
     */
    billed: { type: Boolean, default: false, index: true },

    /**
     * Reference to the Invoice document that includes this usage record.
     * @type {mongoose.Schema.Types.ObjectId}
     * @ref Invoice
     * @default null
     */
    invoiceId: { type: mongoose.Schema.Types.ObjectId, ref: 'Invoice', default: null },

    // ============================================================================
    // 🔍 FORENSIC TRACE
    // ============================================================================
    /**
     * Unique trace identifier for correlation across the system.
     * Auto‑generated if not provided.
     * @type {String}
     * @unique
     * @default `TRC-USG-${timestamp}-${random}`
     */
    traceId: {
      type: String,
      unique: true,
      default: () => `TRC-USG-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
    },

    // ============================================================================
    // 🔐 SOVEREIGN SEAL: Cryptographic proof of immutability
    // ============================================================================
    /**
     * SHA3‑512 hash of the core fields (`tenantId|type|totalCost|traceId`).
     * Generated automatically on create. Verifies the record hasn't been tampered with.
     * @type {String}
     * @required
     */
    sealHash: { type: String, required: true }
  },
  {
    timestamps: true,
    minimize: false // Ensures empty metadata objects are preserved for audit
  }
);

// ============================================================================
// 🧪 MIDDLEWARE: Pre‑validate hook for integrity sealing
// ============================================================================

/**
 * Pre‑validate hook: Generates the SHA3‑512 integrity seal for new usage records.
 * The seal is based on `tenantId`, `type`, `totalCost`, and `traceId`.
 *
 * @this {mongoose.Document}
 * @param {Function} next - Mongoose next callback
 * @returns {void}
 */
UsageRecordSchema.pre('validate', function(next) {
  if (this.isNew) {
    const sealData = `${this.tenantId}|${this.type}|${this.totalCost}|${this.traceId}`;
    this.sealHash = generateSovereignSeal(sealData);
  }
  next();
});

// ============================================================================
// ⚡ COMPOUND INDEXING FOR PERFORMANCE
// ============================================================================

/**
 * Compound indexes for efficient multi-tenant reporting and billing aggregation.
 */
UsageRecordSchema.index({ tenantId: 1, billed: 1, type: 1 });
UsageRecordSchema.index({ tenantId: 1, clientId: 1 });

// ============================================================================
// 🏛️ MODEL EXPORT
// ============================================================================

/**
 * UsageRecord model – the universal atomic ledger.
 * Use this model to record every billable action across the entire OS.
 *
 * @type {mongoose.Model}
 */
const UsageRecord = mongoose.model('UsageRecord', UsageRecordSchema);

export default UsageRecord;
