// File: /Users/wilsonkhanyezi/legal-doc-system/server/models/LedgerEvent.js
// Purpose: LedgerEvent model for multi-tenant financial events (credits/debits).
// Collaboration: If you change enums, index strategy, or retention rules,
// update controllers, migrations, README, and analytics jobs.
// - Migration scripts live in server/migrations
// - For production, ensure amounts are stored in smallest currency unit (cents) or use Decimal128.
// - Sensitive fields should be encrypted if required by compliance.

'use strict';

const mongoose = require('mongoose');

const TYPE = {
    CREDIT: 'credit',
    DEBIT: 'debit'
};

const LedgerEventSchema = new mongoose.Schema({
    tenantId: { type: mongoose.Schema.Types.ObjectId, required: true, index: true },
    // Use Decimal128 for high-precision money values; fallback to Number if not available
    amount: { type: mongoose.Schema.Types.Decimal128, required: true },
    currency: { type: String, required: true, default: 'ZAR' },
    type: { type: String, enum: Object.values(TYPE), required: true, index: true },
    reference: { type: String, default: null }, // e.g., invoice id, payment id
    description: { type: String, default: '' },
    metadata: { type: mongoose.Schema.Types.Mixed, default: {} },
    // Soft delete / archival flag (if you need to remove from reporting)
    archived: { type: Boolean, default: false, index: true }
}, {
    timestamps: true,
    versionKey: '__v'
});

// Indexes: tenant + createdAt for time-range queries; partial to exclude archived
LedgerEventSchema.index({ tenantId: 1, createdAt: -1 }, { partialFilterExpression: { archived: false } });
LedgerEventSchema.index({ tenantId: 1, type: 1, createdAt: -1 }, { partialFilterExpression: { archived: false } });

// Static helper: sum revenue for a tenant in a date range (returns Number)
LedgerEventSchema.statics.sumAmount = async function (tenantId, match = {}) {
    const baseMatch = { archived: false, ...(tenantId ? { tenantId } : {}), ...match };
    const res = await this.aggregate([
        { $match: baseMatch },
        { $group: { _id: null, total: { $sum: '$amount' } } }
    ]);
    if (!res || !res[0]) return mongoose.Types.Decimal128.fromString('0');
    return res[0].total;
};

// Static helper: sum credits for current month (returns Decimal128)
LedgerEventSchema.statics.sumCreditsForMonth = async function (tenantId, monthStart) {
    const match = {
        ...(tenantId ? { tenantId } : {}),
        createdAt: { $gte: monthStart },
        type: TYPE.CREDIT,
        archived: false
    };
    const res = await this.aggregate([
        { $match: match },
        { $group: { _id: null, totalRevenue: { $sum: '$amount' } } }
    ]);
    return (res && res[0] && res[0].totalRevenue) ? res[0].totalRevenue : mongoose.Types.Decimal128.fromString('0');
};

// Convenience factory to create a ledger event (ensures tenantId and amount normalization)
LedgerEventSchema.statics.createEvent = async function ({ tenantId, amount, currency = 'ZAR', type, reference = null, description = '', metadata = {} }) {
    if (!tenantId) throw new Error('tenantId is required');
    if (!type || !Object.values(TYPE).includes(type)) throw new Error('invalid ledger event type');
    // Accept Number or Decimal128; convert to Decimal128
    const amt = (amount && typeof amount === 'object' && amount._bsontype === 'Decimal128') ? amount : mongoose.Types.Decimal128.fromString(String(amount || 0));
    const ev = await this.create({ tenantId, amount: amt, currency, type, reference, description, metadata });
    return ev;
};

// Instance helper: mark archived
LedgerEventSchema.methods.archive = async function (archivedBy = null) {
    this.archived = true;
    if (!this.metadata) this.metadata = {};
    this.metadata.archivedBy = archivedBy;
    this.metadata.archivedAt = new Date();
    return this.save();
};

const LedgerEvent = mongoose.model('LedgerEvent', LedgerEventSchema);

module.exports = LedgerEvent;
module.exports.TYPE = TYPE;
