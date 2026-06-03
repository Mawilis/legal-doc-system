/* eslint-disable */
/**
 * WILSY OS - SOVEREIGN CRM RECORD LEDGER
 * Production CRM collection for leads, contacts, accounts, deals and activity
 * modules. Empty collections are valid live state; no synthetic records.
 */

import mongoose from 'mongoose';

const { Schema } = mongoose;

export const CRM_RECORD_TYPES = [
  'lead',
  'contact',
  'account',
  'deal',
  'task',
  'meeting',
  'call',
  'campaign',
  'document',
  'visit',
  'project'
];

const CrmRecordSchema = new Schema({
  tenantId: { type: String, required: true, trim: true, index: true },
  type: { type: String, required: true, enum: CRM_RECORD_TYPES, index: true },

  externalId: { type: String, trim: true, default: '', index: true },
  sourceSystem: { type: String, trim: true, default: 'WILSY_OS' },
  recordOwner: { type: String, trim: true, default: '' },
  ownerId: { type: String, trim: true, default: '' },
  ownerName: { type: String, trim: true, default: '' },

  name: { type: String, trim: true, default: '' },
  salutation: { type: String, trim: true, default: '' },
  firstName: { type: String, trim: true, default: '' },
  lastName: { type: String, trim: true, default: '' },
  title: { type: String, trim: true, default: '' },
  department: { type: String, trim: true, default: '' },
  email: { type: String, trim: true, lowercase: true, default: '' },
  secondaryEmail: { type: String, trim: true, lowercase: true, default: '' },
  phone: { type: String, trim: true, default: '' },
  mobile: { type: String, trim: true, default: '' },
  homePhone: { type: String, trim: true, default: '' },
  otherPhone: { type: String, trim: true, default: '' },
  fax: { type: String, trim: true, default: '' },
  status: { type: String, trim: true, default: 'NEW' },
  score: { type: Number, min: 0, max: 100, default: null },
  leadSource: { type: String, trim: true, default: '' },
  lifecycleStage: { type: String, trim: true, default: '' },
  rating: { type: String, trim: true, default: '' },

  accountName: { type: String, trim: true, default: '' },
  company: { type: String, trim: true, default: '' },
  contactName: { type: String, trim: true, default: '' },
  accountSite: { type: String, trim: true, default: '' },
  accountNumber: { type: String, trim: true, default: '' },
  accountType: { type: String, trim: true, default: '' },
  parentAccount: { type: String, trim: true, default: '' },
  industry: { type: String, trim: true, default: '' },
  website: { type: String, trim: true, default: '' },
  companyDomainName: { type: String, trim: true, lowercase: true, default: '', index: true },
  tickerSymbol: { type: String, trim: true, default: '' },
  ownership: { type: String, trim: true, default: '' },
  employees: { type: Number, default: null },
  annualRevenue: { type: Number, default: null },

  street: { type: String, trim: true, default: '' },
  city: { type: String, trim: true, default: '' },
  state: { type: String, trim: true, default: '' },
  province: { type: String, trim: true, default: '' },
  postalCode: { type: String, trim: true, default: '' },
  country: { type: String, trim: true, default: '' },

  stage: { type: String, trim: true, default: '' },
  pipeline: { type: String, trim: true, default: 'default' },
  typeLabel: { type: String, trim: true, default: '' },
  nextStep: { type: String, trim: true, default: '' },
  value: { type: Number, default: 0 },
  amount: { type: Number, default: 0 },
  expectedRevenue: { type: Number, default: 0 },
  probability: { type: Number, min: 0, max: 100, default: 0 },
  currency: { type: String, trim: true, default: 'ZAR' },
  closingDate: { type: Date, default: null },
  campaignSource: { type: String, trim: true, default: '' },

  dueDate: { type: Date, default: null },
  startsAt: { type: Date, default: null },
  endsAt: { type: Date, default: null },
  completedAt: { type: Date, default: null },
  priority: { type: String, trim: true, default: '' },
  subject: { type: String, trim: true, default: '' },
  description: { type: String, trim: true, default: '' },
  reminder: { type: Boolean, default: false },
  repeat: { type: Boolean, default: false },

  callType: { type: String, trim: true, default: '' },
  callPurpose: { type: String, trim: true, default: '' },
  callResult: { type: String, trim: true, default: '' },
  durationSeconds: { type: Number, default: 0 },

  fileName: { type: String, trim: true, default: '' },
  fileType: { type: String, trim: true, default: '' },
  fileUrl: { type: String, trim: true, default: '' },
  folder: { type: String, trim: true, default: 'Document Library' },
  fileSize: { type: Number, default: 0 },

  visitType: { type: String, trim: true, default: '' },
  location: { type: String, trim: true, default: '' },
  projectPhase: { type: String, trim: true, default: '' },
  percentComplete: { type: Number, min: 0, max: 100, default: 0 },

  associations: [{
    type: { type: String, trim: true },
    id: { type: String, trim: true },
    name: { type: String, trim: true },
    role: { type: String, trim: true }
  }],
  tags: [{ type: String, trim: true }],

  metadata: { type: Schema.Types.Mixed, default: {} },
  createdBy: { type: String, trim: true, default: '' },
  updatedBy: { type: String, trim: true, default: '' }
}, {
  timestamps: true,
  strict: false
});

CrmRecordSchema.index({ tenantId: 1, type: 1, createdAt: -1 });
CrmRecordSchema.index({ tenantId: 1, type: 1, stage: 1 });
CrmRecordSchema.index({ tenantId: 1, type: 1, status: 1 });
CrmRecordSchema.index({ tenantId: 1, type: 1, email: 1 });
CrmRecordSchema.index({ tenantId: 1, type: 1, companyDomainName: 1 });
CrmRecordSchema.index({ tenantId: 1, type: 1, externalId: 1 });
CrmRecordSchema.index({
  name: 'text',
  email: 'text',
  phone: 'text',
  accountName: 'text',
  status: 'text',
  stage: 'text',
  industry: 'text',
  companyDomainName: 'text',
  title: 'text',
  subject: 'text',
  description: 'text',
  fileName: 'text',
  folder: 'text'
});

export default mongoose.models.CrmRecord || mongoose.model('CrmRecord', CrmRecordSchema);
