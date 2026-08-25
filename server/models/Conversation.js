/* eslint-disable */
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * Wilsy OS — Conversation Model (Kennel Phase 5)
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           server/models/Conversation.js
 * Version:        v5.0.0-KENNEL-PHASE5
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Mongoose schema for tenant‑scoped AI conversation threads.
 *                 Stores chat history with full isolation per tenant.
 * Classification: Production Artifact — Institutional Contract
 *
 * Contributors:
 *   - Wilson Khanyezi (CEO/Lead Architect) – Mandated server‑side history.
 *   - AI Engineering – Phase 5: schema design with indexes and validation.
 *
 * Change Log:
 *   2026-08-04 v5.0.0-KENNEL-PHASE5 — Initial creation.
 *
 * Forensic Relationships:
 *   Upstream:   None (core model)
 *   Downstream: controllers/conversationHistoryController.js
 *   Kennel:     tenantId index enforces isolation
 *
 * Certification Seal: PRODUCTION_READY_v5.0.0-KENNEL-PHASE5
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import mongoose from 'mongoose';

const { Schema, model } = mongoose;

/**
 * @constant CONVERSATION_TURN_SCHEMA
 * @description Sub‑document schema for a single conversation turn (user prompt + AI answer).
 */
const ConversationTurnSchema = new Schema(
  {
    promptText: {
      type: String,
      required: true,
      trim: true,
      maxlength: 10000,
      description: 'User prompt or question.',
    },
    answerText: {
      type: String,
      required: true,
      trim: true,
      maxlength: 50000,
      description: 'AI response to the prompt.',
    },
    intent: {
      type: String,
      trim: true,
      default: '',
      description: 'Optional intent classification (e.g., "what_next", "release_readiness").',
    },
    createdAt: {
      type: Date,
      default: Date.now,
      description: 'Timestamp when the turn was created.',
    },
  },
  { _id: false }
);

/**
 * @constant CONVERSATION_SCHEMA
 * @description Main schema for a conversation thread.
 */
const ConversationSchema = new Schema(
  {
    tenantId: {
      type: String,
      required: true,
      index: true,
      trim: true,
      description: 'Tenant isolation key – all queries must filter by this.',
    },
    title: {
      type: String,
      required: true,
      trim: true,
      maxlength: 200,
      description: 'Human‑readable title for the conversation.',
    },
    workspace: {
      type: String,
      default: 'Workspace',
      trim: true,
      maxlength: 100,
      description: 'Associated workspace (e.g., "CRM Setup", "Billing").',
    },
    turns: {
      type: [ConversationTurnSchema],
      default: [],
      description: 'Array of conversation turns (prompt + answer pairs).',
    },
  },
  {
    timestamps: true, // Automatically adds createdAt and updatedAt
    toJSON: { virtuals: true },
    toObject: { virtuals: true },
  }
);

// ────────────────────────────────────────────────────────────────────────────
// 🔍 INDEXES — Performance and isolation
// ────────────────────────────────────────────────────────────────────────────

ConversationSchema.index({ tenantId: 1, updatedAt: -1 });
ConversationSchema.index({ tenantId: 1, title: 1 });

// ────────────────────────────────────────────────────────────────────────────
// 🛡️ INSTANCE METHODS
// ────────────────────────────────────────────────────────────────────────────

/**
 * @method addTurn
 * @description Convenience method to append a turn to the conversation.
 * @param {Object} turn - { promptText, answerText, intent? }
 * @returns {Promise<this>} The updated thread.
 */
ConversationSchema.methods.addTurn = async function (turn) {
  const { promptText, answerText, intent = '' } = turn;
  if (!promptText || !answerText) {
    throw new Error('Both promptText and answerText are required for a turn.');
  }
  this.turns.push({
    promptText,
    answerText,
    intent,
    createdAt: new Date(),
  });
  this.updatedAt = new Date();
  return this.save();
};

/**
 * @method getLastNTurns
 * @description Retrieve the last N turns from the conversation.
 * @param {number} n - Number of turns to retrieve.
 * @returns {Array} Array of turn objects.
 */
ConversationSchema.methods.getLastNTurns = function (n = 10) {
  return this.turns.slice(-n);
};

// ────────────────────────────────────────────────────────────────────────────
// 🏛️ STATIC METHODS
// ────────────────────────────────────────────────────────────────────────────

/**
 * @static findByTenant
 * @description Retrieve all threads for a tenant, sorted by updatedAt descending.
 * @param {string} tenantId
 * @param {Object} options - { limit, skip }
 * @returns {Promise<Array>}
 */
ConversationSchema.statics.findByTenant = async function (tenantId, options = {}) {
  const { limit = 50, skip = 0 } = options;
  return this.find({ tenantId })
    .sort({ updatedAt: -1 })
    .skip(skip)
    .limit(limit)
    .lean()
    .exec();
};

/**
 * @static clearTenant
 * @description Delete all conversation threads for a tenant.
 * @param {string} tenantId
 * @returns {Promise<Object>} Delete result.
 */
ConversationSchema.statics.clearTenant = async function (tenantId) {
  return this.deleteMany({ tenantId });
};

// ────────────────────────────────────────────────────────────────────────────
// 🚀 MODEL EXPORT
// ────────────────────────────────────────────────────────────────────────────

const Conversation = model('Conversation', ConversationSchema);

export default Conversation;

/*
 * ═══════════════════════════════════════════════════════════════════════════════
 * INSTITUTIONAL CERTIFICATION SEAL — Model v5.0.0-KENNEL-PHASE5
 * ═══════════════════════════════════════════════════════════════════════════════
 * Schema designed for tenant isolation with proper indexes.
 * Includes instance and static methods for common operations.
 * Fully compatible with Mongoose 6+ and ES modules.
 * ═══════════════════════════════════════════════════════════════════════════════
 */
