/* eslint-disable */
/**
 * WILSY OS - SOVEREIGN CRM ROUTES
 * Mounts the production CRM API expected by the Sales & CRM cockpit.
 */

import express from 'express';
import mongoose from 'mongoose';
import CrmRecord from '../models/CrmRecord.js';

const router = express.Router();

const RESOURCE_TYPES = {
  leads: 'lead',
  contacts: 'contact',
  accounts: 'account',
  deals: 'deal',
  tasks: 'task',
  meetings: 'meeting',
  calls: 'call',
  campaigns: 'campaign',
  documents: 'document',
  visits: 'visit',
  projects: 'project'
};

const DEFAULTS_BY_TYPE = {
  lead: { status: 'NEW', score: null, leadSource: 'Direct', lifecycleStage: 'lead' },
  contact: { status: 'ACTIVE', lifecycleStage: 'customer' },
  account: { status: 'ACTIVE', accountType: 'Customer' },
  deal: { status: 'OPEN', stage: 'qualification', pipeline: 'default', probability: 10, value: 0, amount: 0, expectedRevenue: 0, currency: 'ZAR' },
  task: { status: 'Not Started', priority: 'High' },
  meeting: { status: 'SCHEDULED' },
  call: { status: 'PLANNED', callType: 'Outbound' },
  campaign: { status: 'DRAFT' },
  document: { status: 'DRAFT', folder: 'Document Library' },
  visit: { status: 'PLANNED' },
  project: { status: 'OPEN', projectPhase: 'Discovery', percentComplete: 0 }
};

const CRM_FIELD_BLUEPRINTS = {
  lead: ['ownerName', 'name', 'firstName', 'lastName', 'accountName', 'title', 'email', 'phone', 'mobile', 'leadSource', 'status', 'score', 'industry', 'annualRevenue', 'city', 'country'],
  contact: ['ownerName', 'salutation', 'firstName', 'lastName', 'accountName', 'title', 'department', 'email', 'phone', 'mobile', 'homePhone', 'otherPhone', 'fax', 'leadSource'],
  account: ['ownerName', 'accountName', 'accountSite', 'parentAccount', 'accountNumber', 'accountType', 'industry', 'website', 'phone', 'fax', 'tickerSymbol', 'ownership', 'employees', 'annualRevenue', 'rating'],
  deal: ['ownerName', 'name', 'accountName', 'contactName', 'stage', 'pipeline', 'typeLabel', 'value', 'amount', 'probability', 'expectedRevenue', 'closingDate', 'nextStep', 'leadSource', 'campaignSource'],
  task: ['ownerName', 'subject', 'dueDate', 'contactName', 'accountName', 'status', 'priority', 'reminder', 'repeat', 'description'],
  meeting: ['ownerName', 'name', 'startsAt', 'endsAt', 'accountName', 'location', 'description'],
  call: ['ownerName', 'subject', 'phone', 'callType', 'callPurpose', 'callResult', 'startsAt', 'durationSeconds', 'contactName', 'accountName', 'description'],
  campaign: ['ownerName', 'name', 'status', 'startsAt', 'endsAt', 'value', 'expectedRevenue', 'description'],
  document: ['ownerName', 'fileName', 'fileType', 'fileUrl', 'folder', 'fileSize', 'accountName', 'contactName', 'status'],
  visit: ['ownerName', 'name', 'visitType', 'startsAt', 'accountName', 'contactName', 'location', 'status', 'description'],
  project: ['ownerName', 'name', 'accountName', 'projectPhase', 'status', 'priority', 'dueDate', 'percentComplete', 'value', 'description']
};

const getTenantId = (req) => (
  req.query.tenantId
  || req.headers['x-tenant-id']
  || req.tenantId
  || req.user?.tenantId
  || req.user?.tenant
  || 'WILSY_GLOBAL_ROOT'
).toString();

const getActor = (req) => (
  req.user?.id
  || req.user?._id
  || req.user?.email
  || req.headers['x-user-id']
  || 'system'
).toString();

const getResourceType = (resource) => RESOURCE_TYPES[resource];

const normalizeRecord = (record) => {
  const doc = record?.toObject ? record.toObject({ virtuals: true }) : record;
  if (!doc) return null;
  return {
    ...doc,
    id: doc._id?.toString?.() || doc.id,
    _id: doc._id?.toString?.() || doc._id
  };
};

const asyncRoute = (handler) => (req, res, next) => {
  Promise.resolve(handler(req, res, next)).catch(next);
};

const buildListQuery = (req, type) => {
  const tenantId = getTenantId(req);
  const query = { tenantId, type };
  const search = (req.query.search || '').toString().trim();
  const stage = (req.query.stage || '').toString().trim();
  const status = (req.query.status || '').toString().trim();
  const ownerName = (req.query.ownerName || '').toString().trim();
  const accountName = (req.query.accountName || '').toString().trim();

  if (type === 'deal' && stage && stage.toUpperCase() !== 'ALL') {
    query.stage = stage;
  }
  if (status && status.toUpperCase() !== 'ALL') query.status = status;
  if (ownerName && ownerName.toUpperCase() !== 'ALL') query.ownerName = ownerName;
  if (accountName && accountName.toUpperCase() !== 'ALL') query.accountName = accountName;

  if (search) {
    const pattern = new RegExp(search.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i');
    query.$or = [
      { name: pattern },
      { email: pattern },
      { phone: pattern },
      { accountName: pattern },
      { status: pattern },
      { stage: pattern },
      { industry: pattern },
      { companyDomainName: pattern },
      { subject: pattern },
      { description: pattern },
      { fileName: pattern },
      { folder: pattern },
      { title: pattern },
      { city: pattern },
      { country: pattern }
    ];
  }

  return query;
};

const sanitizeLimit = (value) => {
  const limit = Number(value);
  if (!Number.isFinite(limit)) return 50;
  return Math.min(Math.max(Math.floor(limit), 1), 500);
};

const sanitizeOffset = (value) => {
  const offset = Number(value);
  if (!Number.isFinite(offset)) return 0;
  return Math.max(Math.floor(offset), 0);
};

const normalizeImportRecord = (record, type, tenantId, actor, importId) => ({
  ...DEFAULTS_BY_TYPE[type],
  ...record,
  tenantId,
  type,
  createdBy: record.createdBy || actor,
  updatedBy: actor,
  metadata: {
    ...(record.metadata || {}),
    importId,
    importedAt: new Date().toISOString(),
    source: record.sourceSystem || record.metadata?.source || 'WILSY_CRM_IMPORT',
    sourceRecordId: record.externalId || record.metadata?.sourceRecordId || ''
  }
});

const computeDerivedFields = (payload) => {
  const next = { ...payload };
  if (!next.name) {
    next.name = [next.firstName, next.lastName].filter(Boolean).join(' ') || next.accountName || next.subject || next.fileName || '';
  }
  if (!next.accountName && next.company) next.accountName = next.company;
  if (!next.companyDomainName && next.website) {
    next.companyDomainName = next.website.replace(/^https?:\/\//, '').replace(/^www\./, '').split('/')[0];
  }
  if (next.amount && !next.value) next.value = next.amount;
  if (next.value && !next.amount) next.amount = next.value;
  if (next.type === 'deal') {
    const value = Number(next.value || next.amount || 0);
    const probability = Number(next.probability || 0) / 100;
    next.expectedRevenue = Number.isFinite(value * probability) ? Math.round(value * probability) : 0;
  }
  return next;
};

router.get('/health', (req, res) => {
  res.json({
    success: true,
    status: 'CRM_LEDGER_MOUNTED',
    resources: Object.keys(RESOURCE_TYPES),
    timestamp: new Date().toISOString()
  });
});

router.get('/schema', (req, res) => {
  res.json({
    success: true,
    resources: Object.keys(RESOURCE_TYPES),
    fields: CRM_FIELD_BLUEPRINTS,
    defaults: DEFAULTS_BY_TYPE,
    timestamp: new Date().toISOString()
  });
});

router.get('/summary', asyncRoute(async (req, res) => {
  const tenantId = getTenantId(req);
  const rows = await CrmRecord.aggregate([
    { $match: { tenantId } },
    { $group: { _id: '$type', total: { $sum: 1 }, value: { $sum: '$value' }, expectedRevenue: { $sum: '$expectedRevenue' } } }
  ]);
  const summary = rows.reduce((acc, row) => {
    acc[row._id] = { total: row.total, value: row.value, expectedRevenue: row.expectedRevenue };
    return acc;
  }, {});
  res.json({ success: true, tenantId, summary, timestamp: new Date().toISOString() });
}));

router.get('/:resource', asyncRoute(async (req, res) => {
  const type = getResourceType(req.params.resource);
  if (!type) {
    return res.status(404).json({ success: false, message: 'CRM resource is not registered' });
  }

  const limit = sanitizeLimit(req.query.limit);
  const offset = sanitizeOffset(req.query.offset);
  const query = buildListQuery(req, type);

  const [items, total] = await Promise.all([
    CrmRecord.find(query).sort({ createdAt: -1 }).skip(offset).limit(limit).lean(),
    CrmRecord.countDocuments(query)
  ]);

  return res.json({
    success: true,
    items: items.map(normalizeRecord),
    total,
    limit,
    offset,
    hasMore: offset + limit < total,
    tenantId: getTenantId(req),
    resource: req.params.resource
  });
}));

router.post('/:resource', asyncRoute(async (req, res) => {
  const type = getResourceType(req.params.resource);
  if (!type) {
    return res.status(404).json({ success: false, message: 'CRM resource is not registered' });
  }

  const tenantId = getTenantId(req);
  const actor = getActor(req);
  const payload = {
    ...DEFAULTS_BY_TYPE[type],
    ...req.body,
    tenantId,
    type,
    createdBy: actor,
    updatedBy: actor
  };
  const finalPayload = computeDerivedFields(payload);

  if (!finalPayload.name && !finalPayload.email && !finalPayload.phone && ['lead', 'contact', 'account', 'deal'].includes(type)) {
    return res.status(400).json({
      success: false,
      message: 'Name, email or phone is required for this CRM record'
    });
  }

  const created = await CrmRecord.create(finalPayload);
  return res.status(201).json(normalizeRecord(created));
}));

router.post('/:resource/import', asyncRoute(async (req, res) => {
  const type = getResourceType(req.params.resource);
  if (!type) {
    return res.status(404).json({ success: false, message: 'CRM resource is not registered' });
  }

  const records = Array.isArray(req.body?.records) ? req.body.records : [];
  if (!records.length) {
    return res.status(400).json({ success: false, message: 'Import payload must include records' });
  }
  if (records.length > 10000) {
    return res.status(413).json({ success: false, message: 'Import batch exceeds 10000 records' });
  }

  const tenantId = getTenantId(req);
  const actor = getActor(req);
  const mode = ['insert', 'upsert'].includes(req.body?.mode) ? req.body.mode : 'upsert';
  const dedupeKey = req.body?.dedupeKey || (['lead', 'contact'].includes(type) ? 'email' : 'name');
  const sourceSystem = req.body?.sourceSystem || 'WILSY_CRM_IMPORT';
  const importId = `CRM-IMPORT-${Date.now()}-${Math.random().toString(16).slice(2, 8).toUpperCase()}`;

  const report = {
    success: true,
    importId,
    resource: req.params.resource,
    mode,
    dedupeKey,
    received: records.length,
    inserted: 0,
    updated: 0,
    skipped: 0,
    errors: []
  };

  for (const [index, rawRecord] of records.entries()) {
    const payload = computeDerivedFields(normalizeImportRecord({ ...rawRecord, sourceSystem }, type, tenantId, actor, importId));
    const hasIdentity = payload.name || payload.email || payload.phone || payload.accountName;

    if (!hasIdentity) {
      report.skipped += 1;
      report.errors.push({ row: index + 1, message: 'Missing name, email, phone or account' });
      continue;
    }

    try {
      const dedupeValue = payload[dedupeKey];
      if (mode === 'upsert' && dedupeValue) {
        const existing = await CrmRecord.findOne({ tenantId, type, [dedupeKey]: dedupeValue });
        if (existing) {
          await CrmRecord.updateOne({ _id: existing._id }, { $set: payload });
          report.updated += 1;
          continue;
        }
      }

      await CrmRecord.create(payload);
      report.inserted += 1;
    } catch (error) {
      report.skipped += 1;
      report.errors.push({ row: index + 1, message: error.message });
    }
  }

  return res.status(201).json(report);
}));

router.post('/:resource/preview-import', asyncRoute(async (req, res) => {
  const type = getResourceType(req.params.resource);
  if (!type) {
    return res.status(404).json({ success: false, message: 'CRM resource is not registered' });
  }

  const records = Array.isArray(req.body?.records) ? req.body.records : [];
  if (!records.length) {
    return res.status(400).json({ success: false, message: 'Preview payload must include records' });
  }

  const tenantId = getTenantId(req);
  const dedupeKey = req.body?.dedupeKey || (['lead', 'contact'].includes(type) ? 'email' : 'name');
  const blueprint = CRM_FIELD_BLUEPRINTS[type] || [];
  const normalized = records.map(record => computeDerivedFields({ ...DEFAULTS_BY_TYPE[type], ...record, tenantId, type }));
  const mappedFieldSet = new Set();
  let missingIdentity = 0;

  normalized.forEach((record) => {
    blueprint.forEach((field) => {
      if (record[field] !== undefined && record[field] !== null && record[field] !== '') mappedFieldSet.add(field);
    });
    if (!record.name && !record.email && !record.phone && !record.accountName) missingIdentity += 1;
  });

  const dedupeValues = [...new Set(normalized.map(record => record[dedupeKey]).filter(Boolean))];
  const duplicateCandidates = dedupeValues.length
    ? await CrmRecord.countDocuments({ tenantId, type, [dedupeKey]: { $in: dedupeValues } })
    : 0;
  const fieldCoverage = blueprint.length ? Math.round((mappedFieldSet.size / blueprint.length) * 100) : 0;

  return res.json({
    success: true,
    resource: req.params.resource,
    sourceSystem: req.body?.sourceSystem || 'UNKNOWN',
    received: records.length,
    ready: Math.max(records.length - missingIdentity, 0),
    needsReview: missingIdentity,
    duplicateCandidates,
    dedupeKey,
    fieldCoverage,
    mappedFields: [...mappedFieldSet],
    missingIdentity
  });
}));

router.put('/:resource/:id', asyncRoute(async (req, res) => {
  const type = getResourceType(req.params.resource);
  if (!type) {
    return res.status(404).json({ success: false, message: 'CRM resource is not registered' });
  }
  if (!mongoose.Types.ObjectId.isValid(req.params.id)) {
    return res.status(400).json({ success: false, message: 'Invalid CRM record id' });
  }

  const updated = await CrmRecord.findOneAndUpdate(
    { _id: req.params.id, tenantId: getTenantId(req), type },
    computeDerivedFields({ ...req.body, type, updatedBy: getActor(req) }),
    { new: true, runValidators: true }
  );

  if (!updated) {
    return res.status(404).json({ success: false, message: 'CRM record not found' });
  }

  return res.json(normalizeRecord(updated));
}));

router.delete('/:resource/:id', asyncRoute(async (req, res) => {
  const type = getResourceType(req.params.resource);
  if (!type) {
    return res.status(404).json({ success: false, message: 'CRM resource is not registered' });
  }
  if (!mongoose.Types.ObjectId.isValid(req.params.id)) {
    return res.status(400).json({ success: false, message: 'Invalid CRM record id' });
  }

  const deleted = await CrmRecord.findOneAndDelete({
    _id: req.params.id,
    tenantId: getTenantId(req),
    type
  });

  if (!deleted) {
    return res.status(404).json({ success: false, message: 'CRM record not found' });
  }

  return res.json({ success: true, id: req.params.id });
}));

router.use((err, req, res, next) => {
  if (err?.name === 'ValidationError') {
    return res.status(400).json({ success: false, message: err.message });
  }
  if (err?.name === 'CastError') {
    return res.status(400).json({ success: false, message: 'Invalid CRM record id' });
  }
  return next(err);
});

export default router;
