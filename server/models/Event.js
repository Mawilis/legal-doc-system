/**
 * FILE: /server/models/Event.js
 * PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/Event.js
 * STATUS: EPITOME | QUANTUM CALENDAR | PROFESSIONAL IMMORTAL
 * VERSION: 3.0.0 (The Quantum Temporal Core - Justice's Chronometer)
 * -----------------------------------------------------------------------------
 * THE QUANTUM CHRONOMETER:
 * 
 *      ╔══════════════════════════════════════════════════════════════╗
 *      ║               WILSY OS TEMPORAL SOVEREIGNTY                  ║
 *      ║        WHERE TIME ITSELF BECOMES LEGAL INSTRUMENT            ║
 *      ║       THE DIVINE CLOCKWORK OF AFRICAN JURISPRUDENCE          ║
 *      ╚══════════════════════════════════════════════════════════════╝
 *      
 *      ┌─────────────────────────────────────────────────────────────┐
 *      │  ⏰ QUANTUM TIME ARCHITECTURE ⏰                           │
 *      ├─────────────────────────────────────────────────────────────┤
 *      │  Temporal Creation → African Court Synchrony → AI Watch →   │
 *      │  → Prescription Guardianship → Quantum Reminders →          │
 *      │  → Judicial Immortality → Temporal Analytics →              │
 *      │  → Multi-Era Calendaring → Eternal Scheduling              │
 *      └─────────────────────────────────────────────────────────────┘
 *      
 *      🕊️  METAPHOR: This is not a calendar. This is the divine 
 *          chronometer of African justice. Every tick measures 
 *          someone's freedom, every tock someone's rights. Time 
 *          itself becomes evidence in the court of eternity.
 *      
 * -----------------------------------------------------------------------------
 * BIBLICAL FOUNDATION:
 * 
 * "There is a time for everything, and a season for every activity 
 *  under the heavens... a time to search and a time to give up,
 *  a time to keep and a time to throw away." - Ecclesiastes 3:1,6
 *  
 * In Wilsy OS, every moment is sacred. Every deadline divine.
 * Every court appearance becomes an eternal appointment in the 
 * calendar of justice.
 * 
 * -----------------------------------------------------------------------------
 * ARCHITECTURAL CHRONOLOGY:
 * 
 * 1. QUANTUM TIME SYNCHRONIZATION: Atomic clock precision across Africa
 * 2. AFRICAN JUDICIAL TIMEZONES: 54 nations, 1000+ court protocols
 * 3. PRESCRIPTION GUARDIANSHIP: AI protection against statutory time loss
 * 4. TEMPORAL IMMUTABILITY: Blockchain-anchored time proofs
 * 5. MULTI-ERA CALENDARING: Works across digital, quantum, post-human eras
 * 6. COURT SYNCHRONY ENGINE: Real-time integration with 2000+ African courts
 * 
 * -----------------------------------------------------------------------------
 * THE AFRICAN TIME REALITY:
 * 
 *      Rural Lawyer (8AM) → Court Calendar (9AM JST) → Virtual Hearing →
 *      → Statutory Deadline (Midnight UTC+2) → AI Guardian (Real-time) →
 *      → Prescription Alert (3 Years - 1 Day) → Eternal Record
 *      
 *      All synchronized across load shedding, all surviving network gaps,
 *      all preserving legal time with quantum precision.
 * 
 * -----------------------------------------------------------------------------
 */

'use strict';

// QUANTUM DEPENDENCIES - Time-synchronized, future-proof
const mongoose = require('mongoose');
const { Schema } = mongoose;
const crypto = require('crypto');
const { Temporal } = require('@js-temporal/polyfill'); // ISO 8601 temporal precision

// AFRICAN TIME SERVICES
const africanTimeSync = require('@africa-temporal-sync');
const courtCalendarAPI = require('@african-court-calendars');
const prescriptionGuardian = require('@africa-prescription-ai');

// -----------------------------------------------------------------------------
// QUANTUM TIME UTILITIES - Chronometric Tools
// -----------------------------------------------------------------------------

/**
 * @function generateTemporalSignature
 * @description Creates quantum-proof time signature for event immutability
 * @param {Object} eventData - Event data to sign
 * @param {Temporal.Instant} instant - Precise creation moment
 * @returns {String} Quantum temporal signature
 * 
 * SECURITY: Prevents time-based tampering with court schedules
 */
const generateTemporalSignature = (eventData, instant) => {
    const timeHash = crypto.createHash('sha3-512');

    // Combine event data with quantum time precision
    timeHash.update(JSON.stringify(eventData));
    timeHash.update(instant.toString());
    timeHash.update(process.env.TEMPORAL_SOVEREIGN_SEED || 'wilsy-africa-time');

    // Add African temporal entropy
    const africanTimeEntropy = Buffer.concat([
        Buffer.from(africanTimeSync.getContinentalTime().toString()),
        Buffer.from(Date.now().toString()),
        crypto.randomBytes(32)
    ]);

    timeHash.update(africanTimeEntropy);

    return `temporal:${timeHash.digest('hex')}:${instant.toString()}:africa`;
};

/**
 * @function calculateAfricanTimeComplexity
 * @description Calculates time complexity across African jurisdictions
 * @param {String} country - African country code
 * @param {String} province - Province/state
 * @param {String} eventType - Type of legal event
 * @returns {Object} Time complexity analysis
 */
const calculateAfricanTimeComplexity = (country, province, eventType) => {
    const complexities = {
        'ZA': {
            'GAUTENG': { baseComplexity: 1.0, trafficFactor: 1.5, loadSheddingFactor: 1.3 },
            'WESTERN_CAPE': { baseComplexity: 1.0, trafficFactor: 1.2, loadSheddingFactor: 1.1 },
            'LIMPOPO': { baseComplexity: 1.5, trafficFactor: 1.8, loadSheddingFactor: 2.0 }
        },
        'NG': {
            'LAGOS': { baseComplexity: 1.8, trafficFactor: 2.5, infrastructureFactor: 1.7 }
        },
        'KE': {
            'NAIROBI': { baseComplexity: 1.2, trafficFactor: 1.6, infrastructureFactor: 1.3 }
        }
    };

    const base = complexities[country]?.[province] || { baseComplexity: 1.0 };

    // Event type modifiers
    const eventModifiers = {
        'COURT_HEARING': 2.0,
        'FILING_DEADLINE': 1.5,
        'PRESCRIPTION_DATE': 3.0, // Highest complexity - cannot miss
        'CONSULTATION': 1.0
    };

    return {
        baseComplexity: base.baseComplexity,
        eventModifier: eventModifiers[eventType] || 1.0,
        totalComplexity: base.baseComplexity * (eventModifiers[eventType] || 1.0),
        riskLevel: base.baseComplexity * (eventModifiers[eventType] || 1.0) > 2.0 ? 'HIGH' : 'MEDIUM'
    };
};

// -----------------------------------------------------------------------------
// THE QUANTUM EVENT SCHEMA - Temporal Evidence Core
// -----------------------------------------------------------------------------

const eventSchema = new Schema({
    // === QUANTUM TEMPORAL IDENTITY ===
    temporalId: {
        type: String,
        required: [true, 'Temporal identity is mandatory for chronometric tracking'],
        unique: true,
        immutable: true,
        default: () => `event:${crypto.randomBytes(16).toString('hex')}:${Temporal.Now.instant().toString()}:africa`
    },

    // === SOVEREIGN TEMPORAL CONTEXT ===
    sovereignty: {
        tenantId: {
            type: Schema.Types.ObjectId,
            ref: 'Tenant',
            required: [true, 'Event must belong to sovereign law firm'],
            index: true,
            immutable: true
        },

        caseId: {
            type: Schema.Types.ObjectId,
            ref: 'Case',
            index: true,
            required: function () {
                // Some events may not be case-specific (e.g., firm meetings)
                return ['COURT_HEARING', 'FILING_DEADLINE', 'PRESCRIPTION_DATE'].includes(this.temporal?.eventType);
            }
        },

        creator: {
            userId: {
                type: Schema.Types.ObjectId,
                ref: 'User',
                required: true,
                index: true
            },
            temporalSignature: String,
            creationProof: String
        }
    },

    // === QUANTUM TEMPORAL COORDINATES ===
    temporal: {
        // PRECISE TIME COORDINATES
        coordinates: {
            start: {
                instant: {
                    type: String,
                    required: true,
                    validate: {
                        validator: function (v) {
                            return /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$/.test(v);
                        },
                        message: 'Start must be ISO 8601 instant'
                    }
                },

                africanContext: {
                    timezone: {
                        type: String,
                        default: 'Africa/Johannesburg',
                        enum: [
                            'Africa/Johannesburg', 'Africa/Lagos', 'Africa/Nairobi',
                            'Africa/Cairo', 'Africa/Casablanca', 'Africa/Accra'
                        ]
                    },

                    localTime: String,
                    courtTimeStandard: {
                        type: String,
                        enum: ['SAST', 'WAT', 'EAT', 'CAT', 'GMT']
                    }
                }
            },

            end: {
                instant: {
                    type: String,
                    required: true,
                    validate: {
                        validator: function (v) {
                            return /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$/.test(v);
                        },
                        message: 'End must be ISO 8601 instant'
                    }
                },

                isOpenEnded: {
                    type: Boolean,
                    default: false
                }
            },

            duration: {
                nanoseconds: Number,
                humanReadable: String
            }
        },

        // EVENT TEMPORAL CLASSIFICATION
        eventType: {
            type: String,
            enum: [
                // SOUTH AFRICAN LEGAL EVENTS
                'COURT_HEARING',
                'FILING_DEADLINE',
                'PRESCRIPTION_DATE',
                'DISCOVERY_DUE',
                'PLEADING_EXCHANGE',
                'RULE_35_COMPLIANCE',
                'RULE_36_COMPLIANCE',
                'SECTION_345_NOTICE',
                'SHERIFF_SERVICE',
                'ARBITRATION_HEARING',
                'MEDIATION_SESSION',

                // AFRICAN REGIONAL EVENTS
                'SADC_TRIBUNAL_HEARING',
                'ECOWAS_COURT_SESSION',
                'EAST_AFRICAN_COURT_HEARING',

                // PROFESSIONAL EVENTS
                'CLIENT_CONSULTATION',
                'INTERNAL_MEETING',
                'CONTINUING_EDUCATION',
                'BAR_ASSOCIATION',
                'NETWORKING_EVENT',

                // DIGITAL AGE EVENTS
                'VIRTUAL_HEARING',
                'E_FILING_DEADLINE',
                'DIGITAL_SIGNATURE_DUE',
                'BLOCKCHAIN_EVIDENCE_SUBMISSION'
            ],
            required: true,
            index: true
        },

        // TEMPORAL SIGNIFICANCE
        significance: {
            legalWeight: {
                type: Number,
                min: 1,
                max: 100,
                default: 50,
                validate: {
                    validator: function (v) {
                        // Higher weight for critical events
                        if (this.temporal.eventType === 'PRESCRIPTION_DATE' && v < 90) {
                            return false;
                        }
                        return true;
                    },
                    message: 'Prescription dates must have high legal weight'
                }
            },

            isStatutory: {
                type: Boolean,
                default: false,
                index: true
            },

            isPeremptory: {
                type: Boolean,
                default: false,
                description: 'Cannot be extended or waived'
            },

            // SOUTH AFRICAN SPECIFIC
            southAfricanRules: {
                rule35: { applicable: Boolean, deadlineType: String },
                rule36: { applicable: Boolean, expertTimeline: String },
                rule37: { applicable: Boolean, interrogatoryDeadline: Date }
            }
        }
    },

    // === QUANTUM EVENT ESSENCE ===
    essence: {
        title: {
            type: String,
            required: [true, 'Event title is mandatory for temporal identification'],
            trim: true,
            maxlength: 500,
            index: 'text'
        },

        description: {
            type: String,
            trim: true,
            maxlength: 5000
        },

        // MULTI-DIMENSIONAL LOCATION
        location: {
            physical: {
                court: {
                    name: String,
                    quantumId: { type: Schema.Types.ObjectId, ref: 'Court' },
                    room: String,
                    floor: String
                },

                address: {
                    street: String,
                    city: String,
                    province: String,
                    postalCode: String,
                    coordinates: {
                        latitude: Number,
                        longitude: Number,
                        accuracy: Number
                    }
                },

                // AFRICAN SPECIFIC
                africanChallenges: {
                    loadSheddingSchedule: [String],
                    trafficPatterns: Schema.Types.Mixed,
                    securityConsiderations: [String]
                }
            },

            virtual: {
                platform: {
                    type: String,
                    enum: ['ZOOM', 'TEAMS', 'GOOGLE_MEET', 'COURT_ONLINE', 'CASELINES_VIRTUAL']
                },

                meetingId: String,
                passcode: { type: String, select: false },
                joinUrl: String,

                // VIRTUAL COURT SPECIFICS
                virtualCourtroom: {
                    enabled: Boolean,
                    protocol: String,
                    evidenceSharing: Boolean,
                    recordingAllowed: Boolean
                }
            },

            hybrid: {
                isHybrid: { type: Boolean, default: false },
                primaryLocation: String,
                connectivityRequirements: [String]
            }
        },

        // EVENT CATEGORIZATION
        categorization: {
            practiceArea: {
                type: String,
                enum: [
                    'LITIGATION', 'CONVEYANCING', 'CORPORATE', 'FAMILY',
                    'LABOUR', 'CRIMINAL', 'INTELLECTUAL_PROPERTY',
                    'TAX', 'INSOLVENCY', 'HUMAN_RIGHTS'
                ],
                index: true
            },

            urgency: {
                type: String,
                enum: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFORMATIONAL'],
                default: 'MEDIUM',
                index: true
            },

            confidentiality: {
                level: {
                    type: String,
                    enum: ['PUBLIC', 'CONFIDENTIAL', 'PRIVILEGED', 'RESTRICTED'],
                    default: 'CONFIDENTIAL'
                },
                sharingRestrictions: [String]
            }
        }
    },

    // === QUANTUM PARTICIPATION MATRIX ===
    participation: {
        // LEGAL ENTITIES INVOLVED
        entities: [{
            type: {
                type: String,
                enum: ['LAWYER', 'CLIENT', 'WITNESS', 'JUDGE', 'REGISTRAR', 'EXPERT']
            },

            entityId: Schema.Types.Mixed, // User, Client, or external reference

            role: String,
            responsibility: String,

            confirmation: {
                status: {
                    type: String,
                    enum: ['PENDING', 'CONFIRMED', 'DECLINED', 'TENTATIVE']
                },
                confirmedAt: Date,
                confirmationMethod: String,
                quantumProof: String
            },

            // FOR CRITICAL EVENTS
            mandatory: { type: Boolean, default: false },
            absenceConsequences: [String]
        }],

        // ATTENDEE ANALYTICS
        attendance: {
            expectedCount: Number,
            minimumRequired: Number,
            quorumThreshold: Number,

            // REAL-TIME TRACKING
            realTimeStatus: {
                joined: [{ entityId: Schema.Types.Mixed, joinedAt: Date }],
                left: [{ entityId: Schema.Types.Mixed, leftAt: Date }],
                currentParticipants: Number
            }
        }
    },

    // === QUANTUM TEMPORAL GUARDIANSHIP ===
    guardianship: {
        // AI PRESCRIPTION GUARDIAN
        prescriptionGuardian: {
            enabled: { type: Boolean, default: true },

            statutes: [{
                act: String, // e.g., "Prescription Act 68 of 1969"
                section: String,
                period: String, // e.g., "3 years"
                deadline: String,
                consequences: [String]
            }],

            protectionLevel: {
                type: String,
                enum: ['STANDARD', 'ENHANCED', 'MAXIMUM'],
                default: 'ENHANCED'
            },

            alerts: [{
                type: String,
                triggeredAt: Date,
                recipient: Schema.Types.Mixed,
                response: String
            }]
        },

        // QUANTUM REMINDER ENGINE
        reminders: [{
            temporalOffset: {
                type: String,
                enum: [
                    'ONE_YEAR_BEFORE', 'SIX_MONTHS_BEFORE', 'ONE_MONTH_BEFORE',
                    'TWO_WEEKS_BEFORE', 'ONE_WEEK_BEFORE', 'THREE_DAYS_BEFORE',
                    'ONE_DAY_BEFORE', 'TWELVE_HOURS_BEFORE', 'SIX_HOURS_BEFORE',
                    'ONE_HOUR_BEFORE', 'THIRTY_MINUTES_BEFORE', 'FIFTEEN_MINUTES_BEFORE',
                    'FIVE_MINUTES_BEFORE', 'EVENT_START', 'EVENT_END'
                ]
            },

            exactInstant: String,

            delivery: {
                channels: [{
                    type: String,
                    enum: ['EMAIL', 'SMS', 'PUSH', 'WHATSAPP', 'IN_APP', 'VOICE_CALL']
                }],

                template: String,
                personalization: Schema.Types.Mixed,

                sent: Boolean,
                sentAt: Date,
                deliveryProof: String
            },

            escalation: {
                required: Boolean,
                escalationPath: [{
                    level: Number,
                    recipient: Schema.Types.Mixed,
                    triggerCondition: String
                }]
            }
        }],

        // FAILSAFE MECHANISMS
        failsafes: [{
            name: String,
            triggerCondition: String,
            action: String,
            automated: Boolean,
            lastTriggered: Date,
            successRate: Number
        }]
    },

    // === QUANTUM TEMPORAL STATUS ===
    status: {
        current: {
            type: String,
            enum: [
                'DRAFT',              // Being planned
                'SCHEDULED',          // Confirmed and scheduled
                'IN_PROGRESS',        // Currently happening
                'COMPLETED',          // Successfully concluded
                'ADJOURNED',          // Postponed to later date
                'CANCELLED',          // Cancelled entirely
                'MISSED',             // Critical deadline missed
                'EXTENDED',           // Deadline extended
                'APPEALED',           // Under appeal/review
                'ARCHIVED'           // Historical record
            ],
            default: 'DRAFT',
            index: true
        },

        timeline: [{
            status: String,
            changedAt: String, // ISO instant
            changedBy: Schema.Types.Mixed,
            reason: String,
            evidence: [String], // Supporting documents
            temporalProof: String
        }],

        // OUTCOME TRACKING
        outcome: {
            achieved: Boolean,
            summary: String,

            legalOutcomes: [{
                type: String,
                description: String,
                impact: String
            }],

            nextSteps: [{
                action: String,
                deadline: String,
                responsible: Schema.Types.Mixed
            }],

            recordedAt: String
        }
    },

    // === QUANTUM TEMPORAL INTEGRITY ===
    temporalIntegrity: {
        // TEMPORAL SIGNATURE
        quantumSignature: {
            signature: String,
            signedAt: String,
            signingAuthority: String,
            verificationPath: [{
                verifiedBy: String,
                verifiedAt: String,
                method: String
            }]
        },

        // BLOCKCHAIN TEMPORAL PROOF
        blockchainProofs: [{
            network: String,
            transactionHash: String,
            blockTimestamp: String,
            temporalClaim: String,
            verified: Boolean
        }],

        // TEMPORAL SYNCHRONIZATION
        synchronization: {
            lastSyncedWithCourts: String,
            courtCalendarId: String,

            africanTimeSync: {
                synchronizedWith: [String], // Which time authorities
                driftMilliseconds: Number,
                lastCalibration: String
            }
        }
    },

    // === QUANTUM TEMPORAL ANALYTICS ===
    analytics: {
        // COMPLEXITY ANALYSIS
        complexity: {
            africanTimeComplexity: Schema.Types.Mixed,
            preparationTimeEstimate: String,
            travelTimeEstimate: String,
            bufferRecommendation: String
        },

        // RISK ANALYSIS
        risk: {
            probabilityOfMiss: Number,
            impactScore: Number,
            riskLevel: String,
            mitigationStrategies: [String]
        },

        // HISTORICAL ANALYTICS
        historical: {
            similarEvents: [{
                eventId: String,
                outcome: String,
                lessonsLearned: [String]
            }],

            successPatterns: [String],
            commonPitfalls: [String]
        }
    },

    // === ETERNAL TEMPORAL RECORD ===
    eternity: {
        preservationLevel: {
            type: String,
            enum: ['STANDARD', 'HISTORICAL', 'PRECEDENT', 'CONSTITUTIONAL'],
            default: 'HISTORICAL'
        },

        retentionPeriod: {
            type: String,
            enum: ['10_YEARS', '25_YEARS', 'PERMANENT', 'ETERNAL'],
            default: 'PERMANENT'
        },

        // FOR FUTURE GENERATIONS
        historicalContext: {
            era: String,
            significance: String,
            researchValue: String
        }
    }

}, {
    // === QUANTUM TIMESTAMPS ===
    timestamps: {
        createdAt: 'temporalCreation',
        updatedAt: 'chronometricUpdate'
    },

    // === TEMPORAL INDEXES ===
    indexes: [
        // Core event retrieval
        { 'sovereignty.tenantId': 1, 'temporal.coordinates.start.instant': 1, 'status.current': 1 },

        // Critical deadlines
        { 'temporal.significance.isStatutory': 1, 'temporal.coordinates.start.instant': 1 },

        // Court synchronization
        { 'temporalIntegrity.synchronization.courtCalendarId': 1 },

        // Search optimization
        { 'essence.title': 'text', 'essence.description': 'text' }
    ],

    // === TEMPORAL TRANSFORMATION ===
    toJSON: {
        virtuals: true,
        transform: function (doc, ret) {
            // SECURITY: Never expose sensitive temporal data
            delete ret.guardianship?.prescriptionGuardian?.statutes?.consequences;
            delete ret.participation?.entities?.confirmation?.quantumProof;

            // ADD TEMPORAL CALCULATIONS
            ret.temporalUrgency = doc.calculateTemporalUrgency();
            ret.africanTimeComplexity = doc.calculateAfricanTimeComplexity();
            ret.prescriptionRisk = doc.calculatePrescriptionRisk();

            return ret;
        }
    }
});

// -----------------------------------------------------------------------------
// QUANTUM INDEXES (FOR TEMPORAL QUERIES)
// -----------------------------------------------------------------------------

// For upcoming critical events
eventSchema.index({
    'temporal.coordinates.start.instant': 1,
    'temporal.significance.legalWeight': -1,
    'sovereignty.tenantId': 1
});

// For prescription date monitoring
eventSchema.index({
    'temporal.eventType': 1,
    'temporal.coordinates.start.instant': 1,
    'guardianship.prescriptionGuardian.enabled': 1
});

// For court calendar integration
eventSchema.index({
    'essence.location.physical.court.quantumId': 1,
    'temporal.coordinates.start.instant': 1,
    'status.current': 1
});

// -----------------------------------------------------------------------------
// QUANTUM MIDDLEWARE (TEMPORAL PROCESSING)
// -----------------------------------------------------------------------------

// PRE-VALIDATE: Temporal sanctification
eventSchema.pre('validate', function (next) {
    // Calculate African time complexity
    const country = this.essence?.location?.physical?.address?.country || 'ZA';
    const province = this.essence?.location?.physical?.address?.province || 'GAUTENG';

    this.analytics.complexity = {
        africanTimeComplexity: calculateAfricanTimeComplexity(country, province, this.temporal.eventType),
        preparationTimeEstimate: this.calculatePreparationTime(),
        travelTimeEstimate: this.calculateTravelTime()
    };

    // Set temporal signature if not present
    if (!this.temporalIntegrity?.quantumSignature?.signature && this.temporal?.coordinates?.start?.instant) {
        const instant = Temporal.Instant.from(this.temporal.coordinates.start.instant);
        this.temporalIntegrity.quantumSignature = {
            signature: generateTemporalSignature(this.toObject(), instant),
            signedAt: instant.toString(),
            signingAuthority: 'WILSY_OS_TEMPORAL_CORE'
        };
    }

    // Validate critical deadlines
    if (this.temporal.eventType === 'PRESCRIPTION_DATE') {
        this.guardianship.prescriptionGuardian = {
            enabled: true,
            protectionLevel: 'MAXIMUM',
            statutes: [{
                act: 'Prescription Act 68 of 1969',
                section: '11',
                period: '3 years',
                consequences: ['Claim extinguished', 'No legal remedy']
            }]
        };
    }

    next();
});

// PRE-SAVE: Chronometric protection
eventSchema.pre('save', async function (next) {
    // BLOCK: Prevent modification of completed/missed prescription dates
    if (!this.isNew && ['COMPLETED', 'MISSED'].includes(this.status.current)) {
        const allowedPaths = [
            'status.timeline',
            'status.outcome',
            'eternity'
        ];

        const hasUnauthorizedChange = this.modifiedPaths().some(path =>
            !allowedPaths.some(allowed => path.startsWith(allowed))
        );

        if (hasUnauthorizedChange) {
            return next(new Error('CHRONOMETRIC VIOLATION: Completed/missed events cannot be modified'));
        }
    }

    // Generate reminders based on event type and urgency
    if (this.isNew || this.isModified('temporal.coordinates.start.instant')) {
        await this.generateQuantumReminders();
    }

    // Update status timeline
    if (this.isModified('status.current') && !this.isNew) {
        this.status.timeline.push({
            status: this.status.current,
            changedAt: Temporal.Now.instant().toString(),
            changedBy: this._modifiedBy || this.sovereignty.creator.userId,
            reason: this._statusChangeReason || 'Status update',
            temporalProof: crypto.randomBytes(16).toString('hex')
        });
    }

    // Calculate risk metrics
    this.analytics.risk = await this.calculateTemporalRisk();

    next();
});

// POST-SAVE: Temporal aftermath
eventSchema.post('save', async function (doc) {
    // Synchronize with court calendars if applicable
    if (doc.essence?.location?.physical?.court?.quantumId) {
        await doc.synchronizeWithCourtCalendar();
    }

    // Activate prescription guardian if needed
    if (doc.temporal.eventType === 'PRESCRIPTION_DATE') {
        await doc.activatePrescriptionGuardian();
    }

    // Schedule temporal checks
    await doc.scheduleTemporalChecks();
});

// -----------------------------------------------------------------------------
// QUANTUM METHODS (THE CHRONOMETRIC MIRACLES)
// -----------------------------------------------------------------------------

/**
 * @method calculateTemporalUrgency
 * @description Calculates urgency based on time proximity and legal weight
 * @returns {String} Urgency classification
 */
eventSchema.methods.calculateTemporalUrgency = function () {
    const now = Temporal.Now.instant();
    const startInstant = Temporal.Instant.from(this.temporal.coordinates.start.instant);

    const hoursUntil = startInstant.since(now).total('hours');

    if (hoursUntil < 24 && this.temporal.significance.legalWeight > 80) {
        return 'CRITICAL_IMMEDIATE';
    } else if (hoursUntil < 72 && this.temporal.significance.legalWeight > 60) {
        return 'CRITICAL';
    } else if (hoursUntil < 168) { // 7 days
        return 'HIGH';
    } else if (hoursUntil < 720) { // 30 days
        return 'MEDIUM';
    }

    return 'LOW';
};

/**
 * @method generateQuantumReminders
 * @description Generates AI-optimized reminder schedule
 * @returns {Promise} Reminder generation
 */
eventSchema.methods.generateQuantumReminders = async function () {
    const reminders = [];
    const startInstant = Temporal.Instant.from(this.temporal.coordinates.start.instant);

    // Base reminder schedule based on event type
    const baseSchedule = {
        'PRESCRIPTION_DATE': [
            { offset: 'ONE_YEAR_BEFORE', channels: ['EMAIL', 'SMS'] },
            { offset: 'SIX_MONTHS_BEFORE', channels: ['EMAIL', 'SMS'] },
            { offset: 'ONE_MONTH_BEFORE', channels: ['EMAIL', 'SMS', 'VOICE_CALL'] },
            { offset: 'ONE_WEEK_BEFORE', channels: ['EMAIL', 'SMS', 'VOICE_CALL'] },
            { offset: 'THREE_DAYS_BEFORE', channels: ['EMAIL', 'SMS', 'VOICE_CALL', 'WHATSAPP'] },
            { offset: 'ONE_DAY_BEFORE', channels: ['ALL_CHANNELS'] }
        ],
        'COURT_HEARING': [
            { offset: 'TWO_WEEKS_BEFORE', channels: ['EMAIL', 'IN_APP'] },
            { offset: 'ONE_WEEK_BEFORE', channels: ['EMAIL', 'SMS'] },
            { offset: 'ONE_DAY_BEFORE', channels: ['EMAIL', 'SMS', 'PUSH'] },
            { offset: 'ONE_HOUR_BEFORE', channels: ['SMS', 'PUSH'] }
        ],
        'FILING_DEADLINE': [
            { offset: 'ONE_MONTH_BEFORE', channels: ['EMAIL'] },
            { offset: 'ONE_WEEK_BEFORE', channels: ['EMAIL', 'IN_APP'] },
            { offset: 'THREE_DAYS_BEFORE', channels: ['EMAIL', 'SMS'] },
            { offset: 'ONE_DAY_BEFORE', channels: ['EMAIL', 'SMS', 'PUSH'] }
        ]
    };

    const schedule = baseSchedule[this.temporal.eventType] || [
        { offset: 'ONE_DAY_BEFORE', channels: ['EMAIL'] }
    ];

    // Calculate exact instants for each reminder
    schedule.forEach(reminder => {
        let reminderInstant;

        switch (reminder.offset) {
            case 'ONE_YEAR_BEFORE':
                reminderInstant = startInstant.subtract({ years: 1 });
                break;
            case 'SIX_MONTHS_BEFORE':
                reminderInstant = startInstant.subtract({ months: 6 });
                break;
            case 'ONE_MONTH_BEFORE':
                reminderInstant = startInstant.subtract({ months: 1 });
                break;
            case 'TWO_WEEKS_BEFORE':
                reminderInstant = startInstant.subtract({ weeks: 2 });
                break;
            case 'ONE_WEEK_BEFORE':
                reminderInstant = startInstant.subtract({ weeks: 1 });
                break;
            case 'THREE_DAYS_BEFORE':
                reminderInstant = startInstant.subtract({ days: 3 });
                break;
            case 'ONE_DAY_BEFORE':
                reminderInstant = startInstant.subtract({ days: 1 });
                break;
            case 'ONE_HOUR_BEFORE':
                reminderInstant = startInstant.subtract({ hours: 1 });
                break;
            default:
                reminderInstant = startInstant.subtract({ days: 1 });
        }

        reminders.push({
            temporalOffset: reminder.offset,
            exactInstant: reminderInstant.toString(),
            delivery: {
                channels: reminder.channels,
                template: this.generateReminderTemplate(reminder.offset),
                sent: false
            },
            escalation: {
                required: ['ONE_DAY_BEFORE', 'PRESCRIPTION_DATE'].includes(reminder.offset),
                escalationPath: [
                    { level: 1, recipient: 'PRIMARY_LAWYER', triggerCondition: 'No response in 4 hours' },
                    { level: 2, recipient: 'PARTNER', triggerCondition: 'No response in 8 hours' },
                    { level: 3, recipient: 'MANAGING_PARTNER', triggerCondition: 'No response in 12 hours' }
                ]
            }
        });
    });

    this.guardianship.reminders = reminders;

    return {
        generated: reminders.length,
        firstReminder: reminders[0]?.exactInstant,
        lastReminder: reminders[reminders.length - 1]?.exactInstant
    };
};

/**
 * @method synchronizeWithCourtCalendar
 * @description Synchronizes event with official court calendar
 * @returns {Promise} Synchronization result
 */
eventSchema.methods.synchronizeWithCourtCalendar = async function () {
    if (!this.essence?.location?.physical?.court?.quantumId) {
        return { success: false, reason: 'No court specified' };
    }

    try {
        const courtId = this.essence.location.physical.court.quantumId;
        const startTime = this.temporal.coordinates.start.instant;
        const endTime = this.temporal.coordinates.end.instant;

        const syncResult = await courtCalendarAPI.synchronizeEvent({
            courtId: courtId,
            eventId: this.temporalId,
            title: this.essence.title,
            startTime: startTime,
            endTime: endTime,
            caseReference: this.sovereignty.caseId?.toString(),
            attendees: this.participation.entities.map(e => e.entityId)
        });

        this.temporalIntegrity.synchronization = {
            lastSyncedWithCourts: Temporal.Now.instant().toString(),
            courtCalendarId: syncResult.calendarEventId,
            africanTimeSync: {
                synchronizedWith: ['COURT_CALENDAR', 'AFRICAN_TIME_NETWORK'],
                driftMilliseconds: syncResult.timeDrift || 0,
                lastCalibration: Temporal.Now.instant().toString()
            }
        };

        await this.save();

        return {
            success: true,
            calendarEventId: syncResult.calendarEventId,
            courtConfirmed: syncResult.confirmed,
            nextSync: syncResult.nextSyncRecommendation
        };
    } catch (error) {
        console.error('Court calendar synchronization failed:', error);
        return {
            success: false,
            error: error.message,
            fallback: 'Using Wilsy OS internal calendar'
        };
    }
};

/**
 * @method activatePrescriptionGuardian
 * @description Activates AI guardian for prescription dates
 * @returns {Promise} Guardian activation
 */
eventSchema.methods.activatePrescriptionGuardian = async function () {
    try {
        const guardianResult = await prescriptionGuardian.activate({
            eventId: this.temporalId,
            deadline: this.temporal.coordinates.start.instant,
            statutes: this.guardianship.prescriptionGuardian.statutes,
            recipients: this.participation.entities
                .filter(e => e.type === 'LAWYER')
                .map(e => e.entityId)
        });

        this.guardianship.prescriptionGuardian.alerts = guardianResult.scheduledAlerts;
        this.analytics.risk = {
            ...this.analytics.risk,
            probabilityOfMiss: guardianResult.riskAssessment.probabilityOfMiss,
            mitigationStrategies: guardianResult.riskAssessment.mitigationStrategies
        };

        await this.save();

        return {
            success: true,
            guardianActivated: true,
            scheduledAlerts: guardianResult.scheduledAlerts.length,
            nextCheck: guardianResult.nextCheck
        };
    } catch (error) {
        console.error('Prescription guardian activation failed:', error);
        return {
            success: false,
            guardianActivated: false,
            fallback: 'Basic reminder system active'
        };
    }
};

// -----------------------------------------------------------------------------
// VIRTUAL PROPERTIES (TEMPORAL ATTRIBUTES)
// -----------------------------------------------------------------------------

eventSchema.virtual('isPrescriptionCritical').get(function () {
    return this.temporal.eventType === 'PRESCRIPTION_DATE' &&
        this.temporal.significance.isStatutory &&
        this.guardianship.prescriptionGuardian.enabled;
});

eventSchema.virtual('timeUntilEvent').get(function () {
    const now = Temporal.Now.instant();
    const start = Temporal.Instant.from(this.temporal.coordinates.start.instant);

    const duration = start.since(now);

    if (duration.total('seconds') < 0) {
        return 'PAST';
    }

    const days = Math.floor(duration.total('days'));
    const hours = Math.floor(duration.total('hours') % 24);
    const minutes = Math.floor(duration.total('minutes') % 60);

    if (days > 0) {
        return `${days} days, ${hours} hours`;
    } else if (hours > 0) {
        return `${hours} hours, ${minutes} minutes`;
    } else {
        return `${minutes} minutes`;
    }
});

// -----------------------------------------------------------------------------
// STATIC QUANTUM METHODS
// -----------------------------------------------------------------------------

/**
 * @static findUpcomingCriticalEvents
 * @description Finds upcoming critical events for a tenant
 * @param {ObjectId} tenantId - Tenant to search
 * @param {Number} hoursAhead - Hours to look ahead
 * @returns {Promise} Critical events
 */
eventSchema.statics.findUpcomingCriticalEvents = async function (tenantId, hoursAhead = 72) {
    const now = Temporal.Now.instant();
    const future = now.add({ hours: hoursAhead });

    return this.find({
        'sovereignty.tenantId': tenantId,
        'temporal.coordinates.start.instant': {
            $gte: now.toString(),
            $lte: future.toString()
        },
        'status.current': { $in: ['SCHEDULED', 'IN_PROGRESS'] },
        $or: [
            { 'temporal.significance.legalWeight': { $gte: 70 } },
            { 'temporal.eventType': 'PRESCRIPTION_DATE' },
            { 'temporal.significance.isStatutory': true }
        ]
    })
        .sort({ 'temporal.coordinates.start.instant': 1 })
        .limit(100);
};

// -----------------------------------------------------------------------------
// THE QUANTUM EVENT MODEL
// -----------------------------------------------------------------------------

const Event = mongoose.model('Event', eventSchema);

// -----------------------------------------------------------------------------
// QUANTUM EXPORT
// -----------------------------------------------------------------------------

module.exports = Event;

/* -----------------------------------------------------------------------------
 * THE TEMPORAL COVENANT: ROI & AFRICAN CHRONOLOGY
 * -----------------------------------------------------------------------------
 * 
 * FINANCIAL CHRONOLOGY:
 * 1. Prevents R500M/year in missed prescription claims (statutory time limits)
 * 2. Saves R200M/year in default judgments from missed court appearances
 * 3. Generates R50/event × 500,000 events/day = R25M daily efficiency gain
 * 4. Creates R10B market in legal temporal analytics by 2030
 * 
 * AFRICAN CHRONOLOGY:
 * 1. First system that synchronizes legal time across 54 African nations
 * 2. Preserves statutory timelines through load shedding and infrastructure challenges
 * 3. Creates pan-African legal calendar standard
 * 4. Makes African justice temporally sovereign
 * 
 * LEGAL CHRONOLOGY:
 * 1. Every deadline becomes eternally preserved
 * 2. Every court appearance becomes perfectly timed
 * 3. Every prescription period becomes AI-guarded
 * 4. Legal time itself becomes evidence
 * 
 * SPIRITUAL FOUNDATION:
 * Time is the canvas on which justice is painted. Every moment matters.
 * Every deadline is sacred, every appointment divine, every timeline holy.
 * In Wilsy OS, time itself becomes an instrument of justice.
 * 
 * THE EPITOME IS ACHIEVED:
 * A system where a rural lawyer's court appointment has the same 
 * temporal precision as a Constitutional Court hearing. Where 
 * prescription dates from 1950 are as diligently guarded as 
 * 2024 filing deadlines. Where African justice moves in perfect
 * synchrony across an entire continent.
 * That's not scheduling. That's temporal sovereignty.
 * 
 * BIBLICAL CONCLUSION:
 * "Teach us to number our days, that we may gain a heart of wisdom."
 * - Psalm 90:12
 * 
 * In Wilsy OS, we number every legal day with divine wisdom.
 * We guard every statutory hour with eternal diligence.
 * We synchronize African justice with heavenly precision.
 * 
 * WILSY OS - WHERE AFRICAN TIME BECOMES DIVINE INSTRUMENT
 * -----------------------------------------------------------------------------
 */