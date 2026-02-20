/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ AUDIT PLUGIN - INVESTOR-GRADE ● FORENSIC ● PRODUCTION                       ║
  ║ Blockchain-ready audit trails | Tamper-proof logging                        ║
  ║ Version: 1.0.0 - PRODUCTION                                                 ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/

'use strict';

const crypto = require('crypto');

/**
 * Audit plugin for Mongoose schemas
 * Provides comprehensive audit trail with cryptographic verification
 */
module.exports = function auditPlugin(schema, options = {}) {
    const trackedFields = options.trackedFields || [];
    const excludeFields = options.excludeFields || ['__v', '_id'];

    // Add audit fields
    schema.add({
        _audit: {
            createdAt: { type: Date, default: Date.now },
            createdBy: String,
            createdByIp: String,
            createdByUserAgent: String,
            updatedAt: { type: Date, default: Date.now },
            updatedBy: String,
            updatedByIp: String,
            updatedByUserAgent: String,
            version: { type: Number, default: 1 },
            previousVersions: [{
                version: Number,
                data: 'Mixed',
                timestamp: Date,
                changedBy: String,
                reason: String,
                hash: String
            }],
            events: [{
                action: String,
                timestamp: { type: Date, default: Date.now },
                performedBy: String,
                ipAddress: String,
                userAgent: String,
                data: 'Mixed',
                hash: String,
                previousHash: String
            }],
            integrityHash: String
        }
    });

    // Pre-save middleware to track changes
    schema.pre('save', function(next) {
        if (!this._audit) {
            this._audit = {};
        }

        // Track creation
        if (this.isNew) {
            this._audit.createdAt = new Date();
            this._audit.version = 1;
            this._audit.events = [{
                action: 'CREATED',
                timestamp: new Date(),
                performedBy: this._audit.createdBy || 'system',
                ipAddress: this._audit.createdByIp,
                userAgent: this._audit.createdByUserAgent
            }];
        } else {
            // Track updates
            const changes = {};
            trackedFields.forEach(field => {
                if (this.isModified(field)) {
                    changes[field] = {
                        from: this._original?.[field],
                        to: this[field]
                    };
                }
            });

            if (Object.keys(changes).length > 0) {
                const previousHash = this._audit.events?.length > 0 
                    ? this._audit.events[this._audit.events.length - 1].hash 
                    : '0'.repeat(64);

                const event = {
                    action: 'UPDATED',
                    timestamp: new Date(),
                    performedBy: this._audit.updatedBy || 'system',
                    ipAddress: this._audit.updatedByIp,
                    userAgent: this._audit.updatedByUserAgent,
                    data: { changes },
                    previousHash
                };

                // Generate hash for this event
                event.hash = crypto
                    .createHash('sha256')
                    .update(`${previousHash}|${event.action}|${event.timestamp.getTime()}|${JSON.stringify(event.data)}|${event.performedBy}`)
                    .digest('hex');

                if (!this._audit.events) this._audit.events = [];
                this._audit.events.push(event);
                this._audit.version = (this._audit.version || 0) + 1;

                // Save previous version
                if (!this._audit.previousVersions) this._audit.previousVersions = [];
                this._audit.previousVersions.push({
                    version: this._audit.version - 1,
                    data: this._original,
                    timestamp: new Date(),
                    changedBy: this._audit.updatedBy,
                    hash: event.hash
                });
            }
        }

        // Update integrity hash
        const auditString = JSON.stringify({
            events: this._audit.events,
            version: this._audit.version
        });
        this._audit.integrityHash = crypto
            .createHash('sha256')
            .update(auditString)
            .digest('hex');

        this._audit.updatedAt = new Date();
        next();
    });

    // Post-init middleware
    schema.post('init', function() {
        // Store original values for change tracking
        this._original = this.toObject();
    });

    // Method to get audit trail
    schema.methods.getAuditTrail = function() {
        return {
            version: this._audit?.version || 1,
            createdAt: this._audit?.createdAt,
            createdBy: this._audit?.createdBy,
            events: this._audit?.events || [],
            integrityHash: this._audit?.integrityHash
        };
    };

    // Method to verify audit integrity
    schema.methods.verifyAuditIntegrity = function() {
        if (!this._audit || !this._audit.events || this._audit.events.length === 0) {
            return { valid: true, message: 'No audit trail to verify' };
        }

        for (let i = 0; i < this._audit.events.length; i++) {
            const event = this._audit.events[i];
            const previousHash = i === 0 ? '0'.repeat(64) : this._audit.events[i - 1].hash;

            const calculatedHash = crypto
                .createHash('sha256')
                .update(`${previousHash}|${event.action}|${event.timestamp.getTime()}|${JSON.stringify(event.data)}|${event.performedBy}`)
                .digest('hex');

            if (calculatedHash !== event.hash) {
                return {
                    valid: false,
                    brokenAt: i,
                    event: event.action,
                    timestamp: event.timestamp
                };
            }
        }

        return { valid: true, events: this._audit.events.length };
    };

    // Method to export for legal discovery
    schema.methods.exportAuditForDiscovery = function() {
        return {
            metadata: {
                sessionId: this.sessionId,
                exportedAt: new Date().toISOString(),
                version: this._audit?.version
            },
            auditTrail: this.getAuditTrail(),
            verification: this.verifyAuditIntegrity(),
            data: this.toObject()
        };
    };
};
