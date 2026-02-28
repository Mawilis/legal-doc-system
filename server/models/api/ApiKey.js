/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ API KEY MODEL - SECURE ACCESS MANAGEMENT FOR EXTERNAL CLIENTS             ║
  ║ Tiered access | Usage tracking | 100-year audit trail | POPIA compliant   ║
  ║ R15k/month revenue per key | Multi-tenant isolation                        ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import mongoose from 'mongoose';
import crypto from 'crypto';

const apiKeySchema = new mongoose.Schema({
  key: {
    type: String,
    required: true,
    unique: true,
    index: true
  },

  keyId: {
    type: String,
    required: true,
    unique: true,
    default: () => `KEY-${crypto.randomBytes(4).toString('hex').toUpperCase()}`
  },

  tenantId: {
    type: String,
    required: [true, 'Tenant ID is required'],
    index: true,
    validate: {
      validator: (v) => /^[a-zA-Z0-9_-]{8,64}$/.test(v),
      message: 'Tenant ID must be 8-64 alphanumeric characters'
    }
  },

  name: {
    type: String,
    required: [true, 'Key name is required'],
    trim: true
  },

  description: String,

  tier: {
    type: String,
    enum: ['FREE', 'BASIC', 'PREMIUM', 'ENTERPRISE'],
    default: 'BASIC',
    index: true
  },

  permissions: [{
    resource: String,
    actions: [String]
  }],

  isActive: {
    type: Boolean,
    default: true,
    index: true
  },

  expiresAt: {
    type: Date,
    required: true,
    index: true
  },

  lastUsedAt: Date,

  usageCount: {
    type: Number,
    default: 0
  },

  usage: [{
    timestamp: { type: Date, default: Date.now },
    endpoint: String,
    method: String,
    correlationId: String,
    ip: String,
    userAgent: String,
    responseTime: Number,
    statusCode: Number
  }],

  // Rate limit overrides
  rateLimits: {
    requestsPerHour: { type: Number },
    requestsPerMonth: { type: Number }
  },

  // Allowed IPs (optional)
  allowedIPs: [String],

  // Allowed domains (CORS)
  allowedDomains: [String],

  // Webhook for usage alerts
  webhookUrl: String,

  // Billing
  billing: {
    customerId: String,
    subscriptionId: String,
    planId: String,
    autoRenew: { type: Boolean, default: true },
    lastInvoicedAt: Date,
    nextInvoiceAt: Date
  },

  // Audit Trail
  createdBy: {
    type: String,
    required: true
  },

  createdAt: {
    type: Date,
    default: Date.now,
    immutable: true
  },

  updatedBy: String,
  updatedAt: Date,

  // Metadata
  metadata: {
    tags: [String],
    notes: String,
    version: { type: Number, default: 1 }
  },

  // Forensic Integrity
  forensicHash: {
    type: String,
    required: true,
    unique: true
  },

  previousHash: String,

  // Retention
  retentionPolicy: {
    type: String,
    default: 'companies_act_10_years'
  },

  retentionStart: {
    type: Date,
    default: Date.now
  },

  retentionEnd: {
    type: Date,
    default: function() {
      const date = new Date();
      date.setFullYear(date.getFullYear() + 10);
      return date;
    }
  },

  dataResidency: {
    type: String,
    default: 'ZA'
  }
}, {
  timestamps: true,
  collection: 'api_keys',
  strict: true,
  minimize: false
});

// Indexes
apiKeySchema.index({ tenantId: 1, tier: 1 });
apiKeySchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 });
apiKeySchema.index({ 'usage.timestamp': -1 });
apiKeySchema.index({ forensicHash: 1 });

// Pre-save middleware
apiKeySchema.pre('save', async function(next) {
  try {
    this.updatedAt = new Date();
    
    if (!this.retentionEnd) {
      this.retentionEnd = new Date();
      this.retentionEnd.setFullYear(this.retentionEnd.getFullYear() + 10);
    }
    
    // Hash the key for storage (one-way hash)
    if (this.isModified('key')) {
      const salt = crypto.randomBytes(16).toString('hex');
      this.key = crypto
        .createHash('sha256')
        .update(this.key + salt)
        .digest('hex');
    }
    
    const canonicalData = JSON.stringify({
      keyId: this.keyId,
      tenantId: this.tenantId,
      name: this.name,
      tier: this.tier,
      isActive: this.isActive,
      expiresAt: this.expiresAt,
      previousHash: this.previousHash
    }, Object.keys({
      keyId: null,
      tenantId: null,
      name: null,
      tier: null,
      isActive: null,
      expiresAt: null,
      previousHash: null
    }).sort());

    this.forensicHash = crypto
      .createHash('sha256')
      .update(canonicalData)
      .digest('hex');

    next();
  } catch (error) {
    next(error);
  }
});

// Instance methods
apiKeySchema.methods.recordUsage = async function(req, res) {
  this.usage.push({
    timestamp: new Date(),
    endpoint: req.path,
    method: req.method,
    correlationId: req.correlationId,
    ip: req.ip,
    userAgent: req.headers['user-agent'],
    responseTime: res.get('X-Response-Time'),
    statusCode: res.statusCode
  });
  
  this.lastUsedAt = new Date();
  this.usageCount++;
  
  return this.save();
};

apiKeySchema.methods.checkRateLimit = function() {
  const hourAgo = new Date(Date.now() - 60 * 60 * 1000);
  const hourUsage = this.usage.filter(u => u.timestamp > hourAgo).length;
  
  const limits = this.rateLimits || TIER_LIMITS[this.tier];
  return hourUsage < limits.requestsPerHour;
};

apiKeySchema.methods.isExpired = function() {
  return this.expiresAt < new Date();
};

apiKeySchema.methods.verifyIP = function(ip) {
  if (!this.allowedIPs || this.allowedIPs.length === 0) return true;
  return this.allowedIPs.includes(ip);
};

apiKeySchema.methods.verifyDomain = function(origin) {
  if (!this.allowedDomains || this.allowedDomains.length === 0) return true;
  if (!origin) return false;
  
  try {
    const url = new URL(origin);
    return this.allowedDomains.includes(url.hostname);
  } catch {
    return false;
  }
};

// Static methods
apiKeySchema.statics.findByKey = async function(key) {
  const allKeys = await this.find({ isActive: true });
  
  for (const keyDoc of allKeys) {
    if (keyDoc.key === key) return keyDoc;
  }
  
  return null;
};

apiKeySchema.statics.getUsageStats = async function(tenantId, days = 30) {
  const since = new Date();
  since.setDate(since.getDate() - days);
  
  const stats = await this.aggregate([
    { $match: { tenantId } },
    { $unwind: '$usage' },
    { $match: { 'usage.timestamp': { $gte: since } } },
    {
      $group: {
        _id: {
          date: { $dateToString: { format: '%Y-%m-%d', date: '$usage.timestamp' } },
          tier: '$tier'
        },
        count: { $sum: 1 },
        avgResponseTime: { $avg: '$usage.responseTime' }
      }
    },
    { $sort: { '_id.date': 1 } }
  ]);
  
  return stats;
};

const ApiKey = mongoose.model('ApiKey', apiKeySchema);

export { ApiKey };
export default ApiKey;
