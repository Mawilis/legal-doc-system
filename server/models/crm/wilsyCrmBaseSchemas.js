/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRM BASE SCHEMAS                                                                                            ║
 * ║ TENANT-SAFE CRM DOCUMENT CONTRACTS                                                                                     ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Shared CRM Mongoose schema helpers.
 */

import mongoose from 'mongoose';

const { Schema } = mongoose;

/**
 * @function buildCrmAuditTrailSchema
 * @description Builds the reusable CRM audit trail subdocument schema.
 * @returns {Schema} Mongoose schema.
 * @collaboration Keeps all CRM records governance-ready without duplicating audit fields.
 */
function buildCrmAuditTrailSchema() {
  return new Schema(
    {
      actorId: { type: String, trim: true, default: null },
      actorEmail: { type: String, trim: true, lowercase: true, default: null },
      action: { type: String, trim: true, default: 'CREATED' },
      source: { type: String, trim: true, default: 'wilsy-crm' },
      traceId: { type: String, trim: true, default: null },
      recordedAt: { type: Date, default: Date.now },
    },
    { _id: false }
  );
}

/**
 * @function buildCrmEvidenceSchema
 * @description Builds the reusable CRM evidence subdocument schema.
 * @returns {Schema} Mongoose schema.
 * @collaboration Allows leads, deals, accounts and connectors to point to receipts without fake evidence.
 */
function buildCrmEvidenceSchema() {
  return new Schema(
    {
      receiptId: { type: String, trim: true, default: null },
      rootHash: { type: String, trim: true, default: null },
      sourceType: { type: String, trim: true, default: null },
      sourceId: { type: String, trim: true, default: null },
      sealedAt: { type: Date, default: null },
    },
    { _id: false }
  );
}

/**
 * @function buildCrmTenantFields
 * @description Builds tenant fields shared by all CRM documents.
 * @returns {Object} Shared tenant field definitions.
 * @collaboration Ensures all CRM source records can be queried by tenantId.
 */
function buildCrmTenantFields() {
  return {
    tenantId: { type: String, trim: true, index: true, required: true, default: 'MASTER' },
    ownerId: { type: String, trim: true, index: true, default: null },
    sourceSystem: { type: String, trim: true, index: true, default: 'wilsy-os' },
    sourceRecordId: { type: String, trim: true, index: true, default: null },
    status: { type: String, trim: true, index: true, default: 'ACTIVE' },
    tags: [{ type: String, trim: true }],
    metadata: { type: Schema.Types.Mixed, default: {} },
  };
}

/**
 * @function buildCrmSchemaOptions
 * @description Builds common CRM schema options.
 * @param {string} collection - MongoDB collection name.
 * @returns {Object} Schema options.
 * @collaboration Keeps CRM model timestamps and collection names consistent.
 */
function buildCrmSchemaOptions(collection) {
  return {
    collection,
    timestamps: true,
    minimize: false,
    versionKey: false,
  };
}

/**
 * @function getOrCreateModel
 * @description Returns an existing model or creates one.
 * @param {string} modelName - Model name.
 * @param {Schema} schema - Mongoose schema.
 * @returns {Object} Mongoose model.
 * @collaboration Prevents overwrite errors during hot reload and tests.
 */
function getOrCreateModel(modelName, schema) {
  return mongoose.models[modelName] || mongoose.model(modelName, schema);
}

export {
  Schema,
  buildCrmAuditTrailSchema,
  buildCrmEvidenceSchema,
  buildCrmSchemaOptions,
  buildCrmTenantFields,
  getOrCreateModel,
};
