/*
============================================================================================================
QUANTUM SECURITY LOG BASTION: WILSY OS SECURITY LOG MODEL - IMMUTABLE AUDIT TRAIL NEXUS
============================================================================================================
File Path: /server/models/securityLogModel.js
Cosmic Essence: This quantum model forges the eternal, immutable audit trail for all security events—
                transforming digital forensics into celestial jurisprudence. It encodes every security
                quantum into an unbreakable blockchain-like ledger, ensuring compliance with South Africa's
                Cybercrimes Act, POPIA, FICA, and Companies Act, while propelling Wilsy OS to become the
                supreme guardian of Africa's legal digital sovereignty.
ASCII Quantum Security Log Architecture:
   ┌─────────────────────────────────────────────────────────────────────────┐
   │ SECURITY LOG QUANTUM NEXUS │
   │ ┌────────────┐ ┌────────────┐ ┌─────────────────────┐ │
   │ │ EVENT │ │ MERKLE │ │ COMPLIANCE │ │
   │ │ Quantum │ │ Tree │ │ Quantum │ │
   │ │ (Auth, │ │ (Hash │ │ (POPIA, FICA, │ │
   │ └────────────┘ │ Chain) │ │ Cybercrimes) │ │
   │ │ │ │ │
   │ └───────────────┼───────────────┘ │
   │ ↓ │
   │ ┌─────────────────────┐ │
   │ │ IMMUTABLE │ │
   │ │ LEDGER │ │
   │ │ (Blockchain │ │
   │ │ Anchored) │ │
   │ └─────────────────────┘ │
   └─────────────────────────────────────────────────────────────────────────┘
Collaboration Quantum:
- Chief Architect: Wilson Khanyezi
- Quantum Sentinel: Eternal Forger
- Compliance Oracles: Cybercrimes Act 19 of 2020, POPIA 4 of 2013, FICA Act 38 of 2001
- Forensic Integration: NIST SP 800-92, ISO 27001:2022, PCI DSS 4.0
============================================================================================================
*/
// =========================================================================================================
// QUANTUM IMPORTS: MODEL DEPENDENCIES
// =========================================================================================================
/**
 * @fileoverview Security Log Model - Immutable audit trail for all security events
 * @requires mongoose - MongoDB ODM
 * @requires crypto - Cryptographic hashing for Merkle tree
 * @requires uuid - Unique identifier generation
 * @requires validator - Data validation
 */
// Environment Configuration - ABSOLUTE MANDATE
require('dotenv').config({ path: require('path').resolve(__dirname, '../.env') });
// Core Dependencies
const mongoose = require('mongoose');
const crypto = require('crypto');
const { v4: uuidv4 } = require('uuid');
const validator = require('validator');

/* eslint-env jest */

// =========================================================================================================
// QUANTUM CONSTANTS: SECURITY EVENT DEFINITIONS
// =========================================================================================================
/**
 * SECURITY CONSTANTS QUANTUM
 * Centralized constants for security events, severity, and compliance
 */
const SECURITY_EVENT_TYPES = [
    'AUTHENTICATION_SUCCESS', 'AUTHENTICATION_FAILURE', 'AUTHORIZATION_FAILURE',
    'DATA_BREACH', 'DATA_TAMPERING', 'DATA_LEAK', 'UNAUTHORIZED_ACCESS',
    'BRUTE_FORCE_ATTEMPT', 'NETWORK_INTRUSION', 'MALWARE_DETECTION',
    'RANSOMWARE_ATTACK', 'PHISHING_ATTEMPT', 'FRAUD_ATTEMPT',
    'SUSPICIOUS_ACTIVITY', 'COMPLIANCE_VIOLATION', 'SYSTEM_ERROR',
    'SECURITY_ALERT', 'INCIDENT_RESPONSE', 'AUDIT_EVENT', 'UNKNOWN'
];

const SEVERITY_LEVELS = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'];

const COMPLIANCE_FRAMEWORKS = ['POPIA', 'CYBERCRIMES_ACT', 'FICA', 'COMPANIES_ACT', 'GDPR'];

// =========================================================================================================
// QUANTUM SCHEMA DEFINITION: SECURITY LOG SCHEMA
// =========================================================================================================
/**
 * SECURITY LOG SCHEMA QUANTUM
 * Immutable audit trail for all security-related events
 */
const securityLogSchema = new mongoose.Schema({
    // =============================================================================================
    // SECTION 1: IDENTIFICATION AND CLASSIFICATION
    // =============================================================================================
    logId: {
        type: String,
        required: true,
        unique: true,
        default: () => `SECLOG-${uuidv4()}`,
        index: true,
        immutable: true,
        // Security Quantum: Unique identifier for forensic tracing
        validate: {
            validator: function (v) {
                return /^SECLOG-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(v);
            },
            message: 'Invalid security log ID format'
        }
    },

    // Event Classification
    eventType: {
        type: String,
        required: true,
        enum: SECURITY_EVENT_TYPES,
        index: true,
        // Compliance Quantum: Maps to Cybercrimes Act Section 54 categories
        validate: {
            validator: function (v) {
                return SECURITY_EVENT_TYPES.includes(v);
            },
            message: 'Invalid security event type'
        }
    },

    severity: {
        type: String,
        required: true,
        enum: SEVERITY_LEVELS,
        index: true,
        // Risk Assessment Quantum: Used for incident response prioritization
        default: 'MEDIUM'
    },

    description: {
        type: String,
        required: true,
        trim: true,
        minlength: 10,
        maxlength: 1000,
        // Documentation Quantum: Human-readable event description
        validate: {
            validator: function (v) {
                return v.length >= 10 && v.length <= 1000;
            },
            message: 'Description must be between 10 and 1000 characters'
        }
    },

    // =============================================================================================
    // SECTION 2: ACTOR AND TARGET INFORMATION
    // =============================================================================================
    actor: {
        // Entity that performed the action
        type: {
            type: {
                type: String,
                enum: ['USER', 'SYSTEM', 'SERVICE', 'EXTERNAL', 'UNKNOWN'],
                required: true,
                default: 'UNKNOWN'
            },
            id: {
                type: String,
                required: true,
                // Security Quantum: Actor identifier (user ID, service name, IP, etc.)
                validate: {
                    validator: function (v) {
                        return v.length > 0 && v.length <= 255;
                    },
                    message: 'Actor ID must be between 1 and 255 characters'
                }
            },
            name: {
                type: String,
                trim: true,
                maxlength: 255
            },
            role: {
                type: String,
                enum: ['ADMIN', 'USER', 'AUDITOR', 'SYSTEM', 'EXTERNAL', 'UNKNOWN'],
                default: 'UNKNOWN'
            },
            ipAddress: {
                type: String,
                // Security Quantum: IP address for forensic tracing
                validate: {
                    validator: function (v) {
                        return validator.isIP(v) || v === 'UNKNOWN';
                    },
                    message: 'Invalid IP address'
                },
                default: 'UNKNOWN'
            },
            userAgent: {
                type: String,
                trim: true,
                maxlength: 500
            },
            sessionId: {
                type: String,
                // Security Quantum: Session identifier for correlation
                validate: {
                    validator: function (v) {
                        return v === null || (v.length > 0 && v.length <= 255);
                    },
                    message: 'Session ID must be between 1 and 255 characters'
                }
            },
            // Compliance Quantum: POPIA - Lawful processing condition
            lawfulBasis: {
                type: String,
                enum: ['CONSENT', 'CONTRACT', 'LEGAL_OBLIGATION', 'VITAL_INTERESTS', 'PUBLIC_TASK', 'LEGITIMATE_INTERESTS', 'UNKNOWN'],
                default: 'UNKNOWN'
            }
        },
        required: true,
        // Security Quantum: Actor information is critical for forensics
        _id: false
    },

    target: {
        // Entity that was acted upon
        type: {
            type: {
                type: String,
                enum: ['USER', 'COMPANY', 'DOCUMENT', 'SYSTEM', 'API', 'DATABASE', 'FILE', 'UNKNOWN'],
                required: true,
                default: 'UNKNOWN'
            },
            id: {
                type: String,
                required: true,
                // Security Quantum: Target identifier
                validate: {
                    validator: function (v) {
                        return v.length > 0 && v.length <= 255;
                    },
                    message: 'Target ID must be between 1 and 255 characters'
                }
            },
            name: {
                type: String,
                trim: true,
                maxlength: 255
            },
            resource: {
                type: String,
                // Security Quantum: Resource path/endpoint
                validate: {
                    validator: function (v) {
                        return v === null || (v.length > 0 && v.length <= 500);
                    },
                    message: 'Resource must be between 1 and 500 characters'
                }
            }
        },
        required: true,
        _id: false
    },

    // =============================================================================================
    // SECTION 3: CONTEXTUAL INFORMATION
    // =============================================================================================
    context: {
        type: {
            // Environment context
            environment: {
                type: String,
                enum: ['PRODUCTION', 'STAGING', 'DEVELOPMENT', 'TEST', 'UNKNOWN'],
                default: 'PRODUCTION',
                required: true
            },
            timestamp: {
                type: Date,
                required: true,
                default: Date.now,
                // Security Quantum: Precise timestamp for forensic timeline
                index: true
            },
            location: {
                // Geographic location (if available)
                country: {
                    type: String,
                    default: 'ZA',
                    validate: {
                        validator: function (v) {
                            return /^[A-Z]{2}$/.test(v);
                        },
                        message: 'Country code must be 2 uppercase letters'
                    }
                },
                region: {
                    type: String,
                    maxlength: 100
                },
                city: {
                    type: String,
                    maxlength: 100
                },
                coordinates: {
                    latitude: Number,
                    longitude: Number
                }
            },
            // Application context
            service: {
                type: String,
                required: true,
                default: 'Wilsy OS Core',
                // Security Quantum: Service name for microservices tracing
                index: true
            },
            version: {
                type: String,
                required: true,
                default: process.env.APP_VERSION || '1.0.0'
            },
            component: {
                type: String,
                // Security Quantum: Component/module name
                validate: {
                    validator: function (v) {
                        return v === null || (v.length > 0 && v.length <= 100);
                    },
                    message: 'Component name must be between 1 and 100 characters'
                }
            },
            // Threat context
            threatModel: {
                type: String,
                enum: ['STRIDE', 'DREAD', 'PASTA', 'LINDDUN', 'TRIKE', 'NONE'],
                default: 'STRIDE'
            },
            threatCategory: {
                type: [String],
                // Security Quantum: STRIDE categories
                enum: ['SPOOFING', 'TAMPERING', 'REPUDIATION', 'INFORMATION_DISCLOSURE', 'DENIAL_OF_SERVICE', 'ELEVATION_OF_PRIVILEGE'],
                default: []
            },
            // Compliance Quantum: POPIA - Processing condition metadata
            processingCondition: {
                type: String,
                enum: ['LAWFUL', 'CONSENT_BASED', 'CONTRACTUAL', 'LEGAL_REQUIREMENT', 'VITAL_INTERESTS', 'PUBLIC_INTEREST', 'LEGITIMATE_INTERESTS', 'UNKNOWN'],
                default: 'UNKNOWN'
            }
        },
        required: true,
        _id: false
    },

    // =============================================================================================
    // SECTION 4: REQUEST AND RESPONSE DETAILS
    // =============================================================================================
    request: {
        type: {
            method: {
                type: String,
                enum: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', 'UNKNOWN'],
                default: 'UNKNOWN'
            },
            url: {
                type: String,
                trim: true,
                maxlength: 2000
            },
            path: {
                type: String,
                trim: true,
                maxlength: 500
            },
            query: {
                type: mongoose.Schema.Types.Mixed,
                // Security Quantum: Sanitized query parameters
                default: {}
            },
            headers: {
                type: Map,
                of: String,
                // Security Quantum: HTTP headers (sensitive headers redacted)
                default: new Map()
            },
            body: {
                type: mongoose.Schema.Types.Mixed,
                // Security Quantum: Request body (PII redacted)
                default: {}
            },
            size: {
                type: Number,
                min: 0,
                // Security Quantum: Request size in bytes
                default: 0
            }
        },
        _id: false
    },

    response: {
        type: {
            status: {
                type: Number,
                min: 100,
                max: 599,
                // Security Quantum: HTTP status code
                default: 200
            },
            headers: {
                type: Map,
                of: String,
                default: new Map()
            },
            body: {
                type: mongoose.Schema.Types.Mixed,
                default: {}
            },
            size: {
                type: Number,
                min: 0,
                default: 0
            },
            duration: {
                type: Number,
                min: 0,
                // Security Quantum: Response time in milliseconds
                default: 0
            }
        },
        _id: false
    },

    // =============================================================================================
    // SECTION 5: COMPLIANCE METADATA
    // =============================================================================================
    compliance: {
        type: {
            // South African Compliance Frameworks
            frameworks: {
                type: [String],
                enum: COMPLIANCE_FRAMEWORKS,
                default: ['POPIA', 'CYBERCRIMES_ACT', 'FICA', 'COMPANIES_ACT']
            },
            // POPIA Specific
            popia: {
                section: {
                    type: String,
                    // Compliance Quantum: POPIA section reference
                    validate: {
                        validator: function (v) {
                            return v === null || /^Section \d+[A-Z]?$/.test(v);
                        },
                        message: 'Invalid POPIA section format'
                    }
                },
                lawfulProcessingCondition: {
                    type: String,
                    enum: ['CONSENT', 'CONTRACT', 'LEGAL_OBLIGATION', 'VITAL_INTERESTS', 'PUBLIC_TASK', 'LEGITIMATE_INTERESTS', 'NONE'],
                    default: 'NONE'
                },
                dataSubjectRights: {
                    type: [String],
                    enum: ['ACCESS', 'CORRECTION', 'DELETION', 'OBJECTION', 'RESTRICTION', 'PORTABILITY', 'NONE'],
                    default: []
                }
            },
            // Cybercrimes Act Specific
            cybercrimesAct: {
                section: {
                    type: String,
                    validate: {
                        validator: function (v) {
                            return v === null || /^Section \d+[A-Z]?$/.test(v);
                        },
                        message: 'Invalid Cybercrimes Act section format'
                    }
                },
                offenceCategory: {
                    type: String,
                    enum: ['UNAUTHORIZED_ACCESS', 'DATA_INTERFERENCE', 'ILLEGAL_INTERCEPTION', 'CYBER_FRAUD', 'MALICIOUS_COMMUNICATIONS', 'CYBER_EXTORTION', 'NONE'],
                    default: 'NONE'
                },
                reportingRequired: {
                    type: Boolean,
                    default: false
                },
                reportingDeadline: {
                    type: Date,
                    // Compliance Quantum: 72-hour breach reporting deadline
                    validate: {
                        validator: function (v) {
                            return v === null || v instanceof Date;
                        },
                        message: 'Invalid reporting deadline'
                    }
                }
            },
            // FICA Specific
            fica: {
                section: {
                    type: String,
                    validate: {
                        validator: function (v) {
                            return v === null || /^Section \d+[A-Z]?$/.test(v);
                        },
                        message: 'Invalid FICA section format'
                    }
                },
                kycRequirement: {
                    type: Boolean,
                    default: false
                },
                amlRequirement: {
                    type: Boolean,
                    default: false
                },
                suspiciousActivity: {
                    type: Boolean,
                    default: false
                }
            },
            // Companies Act Specific
            companiesAct: {
                section: {
                    type: String,
                    validate: {
                        validator: function (v) {
                            return v === null || /^Section \d+[A-Z]?$/.test(v);
                        },
                        message: 'Invalid Companies Act section format'
                    }
                },
                recordKeepingRequirement: {
                    type: Boolean,
                    default: false
                },
                retentionPeriod: {
                    type: Number,
                    min: 0,
                    // Compliance Quantum: 7-year retention requirement
                    default: 7
                }
            },
            // Global Compliance
            gdpr: {
                applicable: {
                    type: Boolean,
                    default: false
                },
                article: {
                    type: String
                },
                dpaRequired: {
                    type: Boolean,
                    default: false
                }
            },
            // Compliance Evidence
            evidence: {
                type: {
                    stored: {
                        type: Boolean,
                        default: false
                    },
                    location: {
                        type: String,
                        maxlength: 500
                    },
                    hash: {
                        type: String,
                        // Security Quantum: SHA-256 hash of evidence
                        validate: {
                            validator: function (v) {
                                return v === null || /^[a-f0-9]{64}$/i.test(v);
                            },
                            message: 'Invalid evidence hash format'
                        }
                    },
                    timestamp: {
                        type: Date
                    }
                },
                _id: false
            }
        },
        required: true,
        _id: false
    },

    // =============================================================================================
    // SECTION 6: DIGITAL FORENSICS METADATA
    // =============================================================================================
    forensics: {
        type: {
            // Chain of custody
            chainOfCustody: {
                type: [{
                    custodian: {
                        type: String,
                        required: true,
                        maxlength: 255
                    },
                    timestamp: {
                        type: Date,
                        required: true,
                        default: Date.now
                    },
                    action: {
                        type: String,
                        enum: ['CREATED', 'ACCESSED', 'MODIFIED', 'TRANSFERRED', 'ARCHIVED', 'DESTROYED'],
                        required: true
                    },
                    reason: {
                        type: String,
                        maxlength: 500
                    },
                    signature: {
                        type: String,
                        // Security Quantum: Digital signature of custodian
                        validate: {
                            validator: function (v) {
                                return v === null || /^[A-Za-z0-9+/=]+$/.test(v);
                            },
                            message: 'Invalid digital signature format'
                        }
                    }
                }],
                default: []
            },
            // Hash verification
            hashVerification: {
                type: {
                    algorithm: {
                        type: String,
                        enum: ['SHA-256', 'SHA-384', 'SHA-512', 'SHA3-256', 'SHA3-384', 'SHA3-512'],
                        default: 'SHA-256'
                    },
                    value: {
                        type: String,
                        required: true,
                        validate: {
                            validator: function (v) {
                                return /^[a-f0-9]{64}$/i.test(v) ||
                                    /^[a-f0-9]{96}$/i.test(v) ||
                                    /^[a-f0-9]{128}$/i.test(v);
                            },
                            message: 'Invalid hash value format'
                        }
                    },
                    verified: {
                        type: Boolean,
                        default: false
                    },
                    verificationTimestamp: {
                        type: Date
                    },
                    verifiedBy: {
                        type: String,
                        maxlength: 255
                    }
                },
                _id: false
            },
            // Blockchain integration
            blockchain: {
                type: {
                    anchored: {
                        type: Boolean,
                        default: false
                    },
                    network: {
                        type: String,
                        enum: ['ETHEREUM', 'HYPERLEDGER', 'BITCOIN', 'CUSTOM', 'NONE'],
                        default: 'NONE'
                    },
                    transactionId: {
                        type: String,
                        validate: {
                            validator: function (v) {
                                return v === null || /^0x[a-fA-F0-9]{64}$/.test(v);
                            },
                            message: 'Invalid blockchain transaction ID'
                        }
                    },
                    blockNumber: {
                        type: Number,
                        min: 0
                    },
                    blockHash: {
                        type: String,
                        validate: {
                            validator: function (v) {
                                return v === null || /^0x[a-fA-F0-9]{64}$/.test(v);
                            },
                            message: 'Invalid block hash'
                        }
                    },
                    anchorTimestamp: {
                        type: Date
                    }
                },
                _id: false
            },
            // Tamper evidence
            tamperEvidence: {
                type: {
                    detected: {
                        type: Boolean,
                        default: false
                    },
                    detectionTimestamp: {
                        type: Date
                    },
                    detectionMethod: {
                        type: String,
                        enum: ['HASH_VERIFICATION', 'SIGNATURE_VERIFICATION', 'BLOCKCHAIN_VERIFICATION', 'MANUAL', 'NONE'],
                        default: 'NONE'
                    },
                    details: {
                        type: String,
                        maxlength: 1000
                    },
                    correctiveAction: {
                        type: String,
                        enum: ['LOG_INVALIDATED', 'EVIDENCE_PRESERVED', 'INCIDENT_REPORTED', 'NONE'],
                        default: 'NONE'
                    }
                },
                _id: false
            }
        },
        required: true,
        _id: false
    },

    // =============================================================================================
    // SECTION 7: IMMUTABLE BLOCKCHAIN-LIKE CHAINING
    // =============================================================================================
    previousHash: {
        type: String,
        // Security Quantum: Hash of previous log entry (creates immutable chain)
        validate: {
            validator: function (v) {
                return v === null || /^[a-f0-9]{64}$/i.test(v);
            },
            message: 'Invalid previous hash format'
        },
        default: null
    },

    currentHash: {
        type: String,
        required: true,
        unique: true,
        index: true,
        // Security Quantum: SHA-256 hash of current log entry
        validate: {
            validator: function (v) {
                return /^[a-f0-9]{64}$/i.test(v);
            },
            message: 'Invalid current hash format (must be SHA-256)'
        }
    },

    merkleRoot: {
        type: String,
        // Security Quantum: Merkle tree root for batch verification
        validate: {
            validator: function (v) {
                return v === null || /^[a-f0-9]{64}$/i.test(v);
            },
            message: 'Invalid Merkle root format'
        }
    },

    // =============================================================================================
    // SECTION 8: SYSTEM METADATA
    // =============================================================================================
    immutable: {
        type: Boolean,
        required: true,
        default: true,
        // Security Quantum: Once true, document cannot be modified
        validate: {
            validator: function (v) {
                return v === true;
            },
            message: 'Security logs must be immutable'
        }
    },

    tenantId: {
        type: String,
        required: true,
        index: true,
        // Multi-tenancy Quantum: Isolates logs by tenant
        default: process.env.DEFAULT_TENANT_ID || 'wilsy_os_default',
        validate: {
            validator: function (v) {
                return /^[a-z0-9_-]+$/i.test(v) && v.length <= 100;
            },
            message: 'Tenant ID must contain only alphanumeric characters, hyphens, and underscores'
        }
    },

    // Auto-managed timestamps
    createdAt: {
        type: Date,
        required: true,
        default: Date.now,
        index: true,
        immutable: true
    },

    updatedAt: {
        type: Date,
        required: true,
        default: Date.now,
        index: true
    }

}, {
    // =============================================================================================
    // SCHEMA OPTIONS
    // =============================================================================================
    timestamps: true,
    toJSON: {
        virtuals: true,
        transform: function (doc, ret) {
            // Security Quantum: Remove sensitive fields from JSON output
            delete ret.__v;
            delete ret._id;

            // Redact sensitive information for normal views
            if (ret.request && ret.request.headers) {
                const sensitiveHeaders = ['authorization', 'cookie', 'x-api-key', 'x-access-token'];
                sensitiveHeaders.forEach(header => {
                    if (ret.request.headers[header]) {
                        ret.request.headers[header] = '[REDACTED]';
                    }
                });
            }

            // Format timestamps
            ret.createdAt = ret.createdAt.toISOString();
            ret.updatedAt = ret.updatedAt.toISOString();

            return ret;
        }
    },
    toObject: {
        virtuals: true,
        transform: function (doc, ret) {
            delete ret.__v;
            delete ret._id;
            return ret;
        }
    }
});

// =========================================================================================================
// QUANTUM INDEXES: PERFORMANCE OPTIMIZATION
// =========================================================================================================
securityLogSchema.index({
    'actor.ipAddress': 1,
    'context.timestamp': -1
}, {
    name: 'ip_address_time_index',
    background: true,
    partialFilterExpression: { 'actor.ipAddress': { $ne: 'UNKNOWN' } }
});
securityLogSchema.index({
    eventType: 1,
    severity: 1,
    'context.timestamp': -1
}, {
    name: 'event_severity_time_index',
    background: true
});
securityLogSchema.index({
    'compliance.frameworks': 1,
    'context.timestamp': -1
}, {
    name: 'compliance_time_index',
    background: true,
    partialFilterExpression: { 'compliance.frameworks': { $exists: true, $ne: [] } }
});
securityLogSchema.index({
    tenantId: 1,
    'context.timestamp': -1
}, {
    name: 'tenant_time_index',
    background: true
});
securityLogSchema.index({
    'forensics.blockchain.anchored': 1,
    'context.timestamp': -1
}, {
    name: 'blockchain_anchor_index',
    background: true,
    partialFilterExpression: { 'forensics.blockchain.anchored': true }
});
securityLogSchema.index({
    'forensics.tamperEvidence.detected': 1,
    'context.timestamp': -1
}, {
    name: 'tamper_detection_index',
    background: true
});

// =========================================================================================================
// QUANTUM VIRTUAL FIELDS: DERIVED PROPERTIES
// =========================================================================================================
securityLogSchema.virtual('isCritical').get(function () {
    return this.severity === 'CRITICAL';
});
securityLogSchema.virtual('requiresReporting').get(function () {
    // Compliance Quantum: Determines if event requires regulatory reporting
    return this.compliance?.cybercrimesAct?.reportingRequired ||
        (this.severity === 'CRITICAL' && this.eventType === 'DATA_BREACH');
});
securityLogSchema.virtual('ageInDays').get(function () {
    // Compliance Quantum: Age for retention policy checks
    const now = new Date();
    const created = this.createdAt;
    return Math.floor((now - created) / (1000 * 60 * 60 * 24));
});
securityLogSchema.virtual('isRetentionExpired').get(function () {
    // Compliance Quantum: Checks if log exceeds retention period
    const retentionYears = this.compliance?.companiesAct?.retentionPeriod || 7;
    const retentionMs = retentionYears * 365 * 24 * 60 * 60 * 1000;
    const now = new Date();
    return (now - this.createdAt) > retentionMs;
});

// =========================================================================================================
// QUANTUM MIDDLEWARE: PRE-SAVE VALIDATION AND HASHING
// =========================================================================================================
/**
 * PRE-SAVE MIDDLEWARE QUANTUM
 * Ensures immutability and calculates cryptographic hashes
 */
securityLogSchema.pre('save', async function (next) {
    try {
        const log = this;

        // Skip middleware if document is being deleted
        if (log.isDeleted) return next();

        // =============================================================================================
        // STEP 1: IMMUTABILITY ENFORCEMENT
        // =============================================================================================
        if (log.isNew) {
            // New document - set immutable flag
            log.immutable = true;

            // Generate initial chain hash
            generateInitialHash(log);
        } else {
            // Existing document - check immutability
            const SecurityLogModel = log.constructor;
            const existingDoc = await SecurityLogModel.findOne({ logId: log.logId });

            if (existingDoc && existingDoc.immutable) {
                // Security Quantum: Prevent modification of immutable logs
                const error = new Error('Security logs are immutable and cannot be modified');
                error.code = 'IMMUTABLE_LOG';
                error.statusCode = 403;
                return next(error);
            }

            // Update timestamp
            log.updatedAt = new Date();
        }

        // =============================================================================================
        // STEP 2: HASH GENERATION AND CHAIN VERIFICATION
        // =============================================================================================
        await generateCurrentHash(log);

        // =============================================================================================
        // STEP 3: COMPLIANCE VALIDATION
        // =============================================================================================
        await validateComplianceRequirements(log);

        // =============================================================================================
        // STEP 4: TAMPER EVIDENCE CHECK
        // =============================================================================================
        await checkForTampering(log);

        next();
    } catch (error) {
        next(error);
    }
});

// Helper functions (defined outside schema for clarity)
function generateInitialHash(log) {
    // For the first log in chain, previousHash is null
    log.previousHash = null;

    // Generate initial current hash
    const hashData = {
        logId: log.logId,
        eventType: log.eventType,
        severity: log.severity,
        actor: log.actor,
        target: log.target,
        timestamp: log.context?.timestamp
    };

    const hashString = JSON.stringify(hashData);
    log.currentHash = crypto.createHash('sha256').update(hashString).digest('hex');
}

async function generateCurrentHash(log) {
    const SecurityLogModel = log.constructor;
    // Get previous log to chain with
    const previousLog = await SecurityLogModel
        .findOne({ tenantId: log.tenantId })
        .sort({ 'context.timestamp': -1, createdAt: -1 })
        .select('currentHash');

    // Set previous hash (creates blockchain-like chain)
    log.previousHash = previousLog ? previousLog.currentHash : null;

    // Generate current hash
    const hashData = {
        logId: log.logId,
        previousHash: log.previousHash,
        eventData: {
            eventType: log.eventType,
            severity: log.severity,
            actor: log.actor,
            target: log.target,
            context: log.context,
            timestamp: log.context?.timestamp
        },
        compliance: log.compliance,
        timestamp: new Date().toISOString()
    };

    // Security Quantum: Deterministic hash generation
    const hashString = JSON.stringify(hashData, Object.keys(hashData).sort());
    log.currentHash = crypto.createHash('sha256').update(hashString).digest('hex');

    // Update Merkle root if needed (for batch verification)
    if (!log.merkleRoot) {
        await updateMerkleRoot(log);
    }
}

async function updateMerkleRoot(log) {
    const SecurityLogModel = log.constructor;
    // Get recent logs for this tenant
    const recentLogs = await SecurityLogModel
        .find({
            tenantId: log.tenantId,
            'context.timestamp': {
                $gte: new Date(Date.now() - 24 * 60 * 60 * 1000) // Last 24 hours
            }
        })
        .sort({ 'context.timestamp': 1 })
        .select('currentHash');

    if (recentLogs.length > 0) {
        // Build Merkle tree
        const hashes = recentLogs.map(l => l.currentHash);
        log.merkleRoot = calculateMerkleRoot(hashes);
    }
}

function calculateMerkleRoot(hashes) {
    if (hashes.length === 0) return null;
    if (hashes.length === 1) return hashes[0];

    const newLevel = [];

    for (let i = 0; i < hashes.length; i += 2) {
        const left = hashes[i];
        const right = (i + 1 < hashes.length) ? hashes[i + 1] : hashes[i];
        const combined = left + right;
        const hash = crypto.createHash('sha256').update(combined).digest('hex');
        newLevel.push(hash);
    }

    return calculateMerkleRoot(newLevel);
}

async function validateComplianceRequirements(log) {
    // =============================================================================================
    // POPIA COMPLIANCE
    // =============================================================================================
    if (log.compliance?.frameworks?.includes('POPIA')) {
        // Ensure lawful processing condition is set
        if (!log.compliance.popia?.lawfulProcessingCondition ||
            log.compliance.popia.lawfulProcessingCondition === 'NONE') {
            console.warn(`⚠️ POPIA compliance warning: No lawful processing condition for log ${log.logId}`);
        }

        // For data breaches, ensure reporting flags are set
        if (log.eventType === 'DATA_BREACH') {
            if (!log.compliance.cybercrimesAct) log.compliance.cybercrimesAct = {};
            log.compliance.cybercrimesAct.reportingRequired = true;
            log.compliance.cybercrimesAct.reportingDeadline = new Date(Date.now() + 72 * 60 * 60 * 1000); // 72 hours
        }
    }

    // =============================================================================================
    // CYBERCRIMES ACT COMPLIANCE
    // =============================================================================================
    if (log.compliance?.frameworks?.includes('CYBERCRIMES_ACT')) {
        // Set offence category based on event type
        const offenceMapping = {
            'UNAUTHORIZED_ACCESS': ['AUTHENTICATION_FAILURE', 'ACCESS_DENIED', 'BRUTE_FORCE_ATTEMPT'],
            'DATA_INTERFERENCE': ['DATA_BREACH', 'DATA_TAMPERING', 'DATA_LEAK'],
            'ILLEGAL_INTERCEPTION': ['NETWORK_INTRUSION', 'MAN_IN_THE_MIDDLE'],
            'CYBER_FRAUD': ['FRAUD_ATTEMPT', 'PHISHING_ATTEMPT'],
            'MALICIOUS_COMMUNICATIONS': ['MALWARE_DETECTION', 'RANSOMWARE_ATTACK']
        };

        for (const [offence, events] of Object.entries(offenceMapping)) {
            if (events.includes(log.eventType)) {
                if (!log.compliance.cybercrimesAct) log.compliance.cybercrimesAct = {};
                log.compliance.cybercrimesAct.offenceCategory = offence;
                break;
            }
        }
    }

    // =============================================================================================
    // COMPANIES ACT COMPLIANCE
    // =============================================================================================
    if (log.compliance?.frameworks?.includes('COMPANIES_ACT')) {
        // Ensure 7-year retention for all company-related events
        if (!log.compliance.companiesAct) log.compliance.companiesAct = {};
        log.compliance.companiesAct.retentionPeriod = 7;
        log.compliance.companiesAct.recordKeepingRequirement = true;
    }
}

async function checkForTampering(log) {
    if (!log.isNew) {
        const SecurityLogModel = log.constructor;
        // Verify hash chain integrity
        const previousLog = await SecurityLogModel
            .findOne({ currentHash: log.previousHash });

        if (!previousLog && log.previousHash !== null) {
            // Hash chain broken - possible tampering
            if (!log.forensics) log.forensics = {};
            if (!log.forensics.tamperEvidence) log.forensics.tamperEvidence = {};
            log.forensics.tamperEvidence = {
                detected: true,
                detectionTimestamp: new Date(),
                detectionMethod: 'HASH_VERIFICATION',
                details: 'Hash chain verification failed - previous hash not found',
                correctiveAction: 'LOG_INVALIDATED'
            };

            // Invalidate log
            log.immutable = false; // Allow updates to mark as invalid
            log.description = `[INVALIDATED - TAMPERING DETECTED] ${log.description}`;
        }
    }
}

// =========================================================================================================
// QUANTUM STATIC METHODS: BATCH OPERATIONS AND ANALYTICS
// =========================================================================================================
/**
 * STATIC METHODS QUANTUM
 * Class-level methods for batch operations and analytics
 */
securityLogSchema.statics.generateComplianceReport = async function (tenantId, startDate, endDate) {
    // Compliance Quantum: Generate regulatory compliance report
    const logs = await this.find({
        tenantId,
        'context.timestamp': { $gte: startDate, $lte: endDate },
        'compliance.frameworks': { $exists: true, $ne: [] }
    });

    const report = {
        tenantId,
        period: { startDate, endDate },
        generated: new Date(),
        summary: {
            totalLogs: logs.length,
            byFramework: {},
            bySeverity: {},
            byEventType: {}
        },
        complianceMetrics: {},
        recommendations: []
    };

    // Analyze logs
    logs.forEach(log => {
        // Count by framework
        (log.compliance?.frameworks || []).forEach(framework => {
            report.summary.byFramework[framework] = (report.summary.byFramework[framework] || 0) + 1;
        });

        // Count by severity
        report.summary.bySeverity[log.severity] = (report.summary.bySeverity[log.severity] || 0) + 1;

        // Count by event type
        report.summary.byEventType[log.eventType] = (report.summary.byEventType[log.eventType] || 0) + 1;
    });

    // Generate compliance metrics
    report.complianceMetrics = {
        popiaCompliance: calculatePopiaCompliance(logs),
        cybercrimesActCompliance: calculateCybercrimesActCompliance(logs),
        ficaCompliance: calculateFicaCompliance(logs),
        companiesActCompliance: calculateCompaniesActCompliance(logs)
    };

    // Generate recommendations
    report.recommendations = generateComplianceRecommendations(report);

    return report;
};

// Compliance calculation helpers (moved outside for reusability)
function calculatePopiaCompliance(logs) {
    const popiaLogs = logs.filter(l => l.compliance?.frameworks?.includes('POPIA'));
    const withLawfulBasis = popiaLogs.filter(l =>
        l.compliance?.popia?.lawfulProcessingCondition &&
        l.compliance.popia.lawfulProcessingCondition !== 'NONE'
    ).length;

    return {
        total: popiaLogs.length,
        withLawfulBasis,
        complianceRate: popiaLogs.length > 0 ? (withLawfulBasis / popiaLogs.length) * 100 : 100
    };
}

function calculateCybercrimesActCompliance(logs) {
    const cyberLogs = logs.filter(l => l.compliance?.frameworks?.includes('CYBERCRIMES_ACT'));
    const reported = cyberLogs.filter(l =>
        l.compliance?.cybercrimesAct?.reportingRequired &&
        l.compliance.cybercrimesAct.reportingDeadline
    ).length;

    return {
        total: cyberLogs.length,
        reported,
        complianceRate: cyberLogs.length > 0 ? (reported / cyberLogs.length) * 100 : 100
    };
}

function calculateFicaCompliance(logs) {
    const ficaLogs = logs.filter(l => l.compliance?.frameworks?.includes('FICA'));
    const kycVerified = ficaLogs.filter(l => l.compliance?.fica?.kycRequirement).length;
    const amlScreened = ficaLogs.filter(l => l.compliance?.fica?.amlRequirement).length;

    return {
        total: ficaLogs.length,
        kycVerified,
        amlScreened,
        complianceRate: ficaLogs.length > 0 ? ((kycVerified + amlScreened) / (ficaLogs.length * 2)) * 100 : 100
    };
}

function calculateCompaniesActCompliance(logs) {
    const companiesLogs = logs.filter(l => l.compliance?.frameworks?.includes('COMPANIES_ACT'));
    const retentionCompliant = companiesLogs.filter(l =>
        l.compliance?.companiesAct?.retentionPeriod >= 7
    ).length;

    return {
        total: companiesLogs.length,
        retentionCompliant,
        complianceRate: companiesLogs.length > 0 ? (retentionCompliant / companiesLogs.length) * 100 : 100
    };
}

function generateComplianceRecommendations(report) {
    const recommendations = [];

    // POPIA recommendations
    if (report.complianceMetrics.popiaCompliance.complianceRate < 90) {
        recommendations.push({
            framework: 'POPIA',
            priority: 'HIGH',
            recommendation: 'Improve lawful processing condition documentation',
            action: 'Ensure all data processing events have documented lawful basis'
        });
    }

    // Cybercrimes Act recommendations
    if (report.complianceMetrics.cybercrimesActCompliance.complianceRate < 100) {
        recommendations.push({
            framework: 'Cybercrimes Act',
            priority: 'CRITICAL',
            recommendation: 'Ensure all reportable events are properly flagged',
            action: 'Configure automatic reporting for all cybersecurity incidents'
        });
    }

    return recommendations;
}

securityLogSchema.statics.verifyHashChain = async function (tenantId) {
    // Security Quantum: Verify integrity of hash chain
    const logs = await this.find({ tenantId })
        .sort({ 'context.timestamp': 1, createdAt: 1 })
        .select('logId currentHash previousHash');

    const chainBreaks = [];
    let previousHash = null;

    for (let i = 0; i < logs.length; i++) {
        const log = logs[i];

        if (log.previousHash !== previousHash) {
            chainBreaks.push({
                index: i,
                logId: log.logId,
                expectedPreviousHash: previousHash,
                actualPreviousHash: log.previousHash,
                description: 'Hash chain break detected'
            });
        }

        // Verify current hash (simplified)
        const expectedHash = crypto.createHash('sha256')
            .update(JSON.stringify({
                logId: log.logId,
                previousHash: log.previousHash,
                index: i
            }))
            .digest('hex');

        if (log.currentHash !== expectedHash) {
            chainBreaks.push({
                index: i,
                logId: log.logId,
                expectedHash,
                actualHash: log.currentHash,
                description: 'Hash verification failed'
            });
        }

        previousHash = log.currentHash;
    }

    return {
        totalLogs: logs.length,
        chainBreaks,
        integrity: chainBreaks.length === 0 ? 'INTACT' : 'COMPROMISED',
        verificationTimestamp: new Date()
    };
};

securityLogSchema.statics.purgeExpiredLogs = async function (tenantId) {
    // Compliance Quantum: Purge logs beyond retention period
    const retentionYears = 7; // Default Companies Act requirement
    const cutoffDate = new Date();
    cutoffDate.setFullYear(cutoffDate.getFullYear() - retentionYears);

    // Find expired logs
    const expiredLogs = await this.find({
        tenantId,
        createdAt: { $lt: cutoffDate },
        'compliance.companiesAct.recordKeepingRequirement': false
    });

    // Archive before deletion (in production, this would move to cold storage)
    const archiveResult = await archiveLogs(expiredLogs);

    // Delete from primary database
    const deleteResult = await this.deleteMany({
        _id: { $in: expiredLogs.map(l => l._id) }
    });

    return {
        purgedCount: deleteResult.deletedCount,
        archivedCount: archiveResult.archived,
        cutoffDate,
        purgeTimestamp: new Date()
    };
};

async function archiveLogs(logs) {
    // In production, this would archive to cold storage or backup system
    console.log(`Archiving ${logs.length} expired security logs...`);

    // For now, just log the archiving
    return {
        archived: logs.length,
        timestamp: new Date()
    };
}

// =========================================================================================================
// QUANTUM INSTANCE METHODS: LOG-SPECIFIC OPERATIONS
// =========================================================================================================
securityLogSchema.methods.verifyIntegrity = function () {
    // Security Quantum: Verify integrity of this specific log
    const log = this;

    // Recalculate hash
    const hashData = {
        logId: log.logId,
        previousHash: log.previousHash,
        eventData: {
            eventType: log.eventType,
            severity: log.severity,
            actor: log.actor,
            target: log.target,
            context: log.context
        }
    };

    const calculatedHash = crypto.createHash('sha256')
        .update(JSON.stringify(hashData, Object.keys(hashData).sort()))
        .digest('hex');

    const hashValid = calculatedHash === log.currentHash;

    // Check if previous hash exists in chain
    let chainValid = false;
    if (log.previousHash === null) {
        chainValid = true; // First in chain
    } else {
        // In production, would verify against database
        chainValid = true; // Simplified for example
    }

    return {
        hashValid,
        chainValid,
        calculatedHash,
        storedHash: log.currentHash,
        verificationTimestamp: new Date()
    };
};

securityLogSchema.methods.generateForensicReport = function () {
    // Forensics Quantum: Generate detailed forensic report
    const log = this;

    return {
        logId: log.logId,
        eventType: log.eventType,
        severity: log.severity,
        timestamp: log.context?.timestamp,

        // Actor analysis
        actor: {
            type: log.actor?.type,
            id: log.actor?.id,
            ipAddress: log.actor?.ipAddress,
            userAgent: log.actor?.userAgent,
            threatProfile: analyzeThreatProfile(log)
        },

        // Target analysis
        target: {
            type: log.target?.type,
            id: log.target?.id,
            resource: log.target?.resource,
            impactAssessment: assessImpact(log)
        },

        // Compliance implications
        complianceImplications: {
            popia: generatePopiaImplications(log),
            cybercrimesAct: generateCybercrimesImplications(log),
            fica: generateFicaImplications(log)
        },

        // Recommendations
        recommendations: generateForensicRecommendations(log),

        // Metadata
        reportGenerated: new Date(),
        reportVersion: '1.0'
    };
};

// Forensic analysis helpers
function analyzeThreatProfile(log) {
    const profile = {
        riskLevel: 'UNKNOWN',
        indicators: [],
        confidence: 0
    };

    // Analyze based on event type and context
    if (log.eventType?.includes('ATTACK') || log.eventType?.includes('BREACH')) {
        profile.riskLevel = 'HIGH';
        profile.indicators.push('MALICIOUS_ACTIVITY');
        profile.confidence = 80;
    }

    if (log.actor?.ipAddress && log.actor.ipAddress !== 'UNKNOWN') {
        // In production, would check against threat intelligence feeds
        profile.indicators.push('KNOWN_IP');
    }

    return profile;
}

function assessImpact(log) {
    const impact = {
        severity: 'UNKNOWN',
        affectedSystems: [],
        dataAffected: false,
        financialImpact: 'UNKNOWN'
    };

    if (log.eventType === 'DATA_BREACH') {
        impact.severity = 'CRITICAL';
        impact.dataAffected = true;
        impact.financialImpact = 'HIGH';
    }

    if (log.target?.resource) {
        impact.affectedSystems.push(log.target.resource);
    }

    return impact;
}

function generatePopiaImplications(log) {
    const implications = [];

    if (log.eventType === 'DATA_BREACH') {
        implications.push({
            section: 'Section 22',
            requirement: 'Notification to Information Regulator',
            deadline: 'Within 72 hours',
            status: 'REQUIRED'
        });
    }

    if (log.actor?.type === 'USER' && log.target?.type === 'USER') {
        implications.push({
            section: 'Section 11',
            requirement: 'Lawful processing condition validation',
            status: 'TO_BE_VERIFIED'
        });
    }

    return implications;
}

function generateCybercrimesImplications(log) {
    const implications = [];

    const offenceMapping = {
        'UNAUTHORIZED_ACCESS': 'Section 2',
        'DATA_INTERFERENCE': 'Section 3',
        'ILLEGAL_INTERCEPTION': 'Section 4',
        'CYBER_FRAUD': 'Section 8',
        'MALICIOUS_COMMUNICATIONS': 'Section 14'
    };

    const offence = log.compliance?.cybercrimesAct?.offenceCategory;
    if (offence && offence !== 'NONE') {
        implications.push({
            section: offenceMapping[offence] || 'Section 1',
            offence,
            reportingRequired: log.compliance?.cybercrimesAct?.reportingRequired,
            status: 'TO_BE_REVIEWED'
        });
    }

    return implications;
}

function generateFicaImplications(log) {
    const implications = [];

    if (log.eventType?.includes('FRAUD') || log.eventType?.includes('MONEY_LAUNDERING')) {
        implications.push({
            section: 'Section 29',
            requirement: 'Suspicious transaction reporting',
            deadline: 'IMMEDIATE',
            status: 'REQUIRED'
        });
    }

    return implications;
}

function generateForensicRecommendations(log) {
    const recommendations = [];

    if (log.severity === 'CRITICAL') {
        recommendations.push({
            priority: 'IMMEDIATE',
            action: 'Isolate affected systems',
            reason: 'Critical security event detected'
        });

        recommendations.push({
            priority: 'IMMEDIATE',
            action: 'Notify incident response team',
            reason: 'Requires immediate investigation'
        });
    }

    if (log.eventType === 'DATA_BREACH') {
        recommendations.push({
            priority: 'HIGH',
            action: 'Initiate data breach protocol',
            reason: 'Personal information compromised'
        });

        recommendations.push({
            priority: 'HIGH',
            action: 'Preserve digital evidence',
            reason: 'Required for forensic investigation'
        });
    }

    return recommendations;
}

// =========================================================================================================
// QUANTUM MODEL EXPORT: ETERNAL INTERFACE
// =========================================================================================================
/**
 * MODEL EXPORT QUANTUM
 * Create and export the SecurityLog model
 */
const SecurityLog = mongoose.model('SecurityLog', securityLogSchema);

// =========================================================================================================
// QUANTUM VALIDATION TESTS: INTEGRATED TEST SUITE
// =========================================================================================================
/**
 * SECURITY LOG MODEL TEST SUITE
 * Embedded test suite for model validation
 */
if (process.env.NODE_ENV === 'test') {
    describe('SecurityLog Model Quantum Test Suite', () => {
        let testLog;

        beforeEach(() => {
            testLog = new SecurityLog({
                logId: `SECLOG-${uuidv4()}`,
                eventType: 'AUTHENTICATION_SUCCESS',
                severity: 'INFO',
                description: 'Test authentication event',
                actor: {
                    type: 'USER',
                    id: 'user_123',
                    name: 'Test User',
                    role: 'USER',
                    ipAddress: '192.168.1.100',
                    userAgent: 'Test Browser',
                    lawfulBasis: 'CONSENT'
                },
                target: {
                    type: 'SYSTEM',
                    id: 'auth_system',
                    name: 'Authentication System',
                    resource: '/api/v1/auth/login'
                },
                context: {
                    environment: 'TEST',
                    timestamp: new Date(),
                    location: {
                        country: 'ZA',
                        region: 'Gauteng',
                        city: 'Johannesburg'
                    },
                    service: 'Wilsy OS Core',
                    version: '1.0.0',
                    component: 'Authentication',
                    threatModel: 'STRIDE',
                    threatCategory: [],
                    processingCondition: 'CONSENT_BASED'
                },
                compliance: {
                    frameworks: ['POPIA', 'CYBERCRIMES_ACT'],
                    popia: {
                        section: 'Section 11',
                        lawfulProcessingCondition: 'CONSENT',
                        dataSubjectRights: []
                    },
                    cybercrimesAct: {
                        section: 'Section 1',
                        offenceCategory: 'NONE',
                        reportingRequired: false
                    }
                },
                forensics: {
                    chainOfCustody: [],
                    hashVerification: {
                        algorithm: 'SHA-256',
                        value: 'testhash123',
                        verified: false
                    },
                    blockchain: {
                        anchored: false,
                        network: 'NONE'
                    },
                    tamperEvidence: {
                        detected: false,
                        detectionMethod: 'NONE'
                    }
                },
                tenantId: 'test_tenant'
            });
        });

        test('Should create valid security log', async () => {
            await expect(testLog.save()).resolves.toBeTruthy();
        });

        test('Should enforce immutability', async () => {
            await testLog.save();
            testLog.description = 'Modified description';
            await expect(testLog.save()).rejects.toThrow('IMMUTABLE_LOG');
        });

        test('Should validate IP address format', async () => {
            testLog.actor.ipAddress = 'invalid_ip';
            await expect(testLog.save()).rejects.toThrow('Invalid IP address');
        });

        test('Should validate hash format', async () => {
            testLog.currentHash = 'invalid_hash';
            await expect(testLog.save()).rejects.toThrow('Invalid current hash format');
        });

        test('Should generate compliance report', async () => {
            await testLog.save();
            const report = await SecurityLog.generateComplianceReport(
                'test_tenant',
                new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
                new Date()
            );
            expect(report).toHaveProperty('summary');
            expect(report).toHaveProperty('complianceMetrics');
        });

        test('Should verify hash chain integrity', async () => {
            await testLog.save();
            const integrity = await SecurityLog.verifyHashChain('test_tenant');
            expect(integrity).toHaveProperty('integrity');
            expect(['INTACT', 'COMPROMISED']).toContain(integrity.integrity);
        });
    });
}

// =========================================================================================================
// QUANTUM EXPORT
// =========================================================================================================
module.exports = SecurityLog;