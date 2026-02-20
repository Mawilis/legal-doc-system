/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ CLIENT ONBOARDING SERVICE — INVESTOR-GRADE ● FORENSIC ● PRODUCTION           ║
  ║ FICA Compliant | POPIA Compliant | Multi-tenant | Circuit Breaker           ║
  ║ Version: 5.0.1 - Production - ESLINT CLEAN                                  ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/

'use strict';

const mongoose = require('mongoose');
const crypto = require('crypto');
const { DateTime } = require('luxon');
const { EventEmitter } = require('events');
const CircuitBreaker = require('opossum');

// Core utilities
const auditLogger = require('../utils/auditLogger');
const logger = require('../utils/logger');
const metrics = require('../utils/metrics');
const tenantContext = require('../middleware/tenantContext');
const { 
    ValidationError, 
    DatabaseError, 
    FICAComplianceError,
    ResourceNotFoundError
} = require('../utils/errors');

// External services
const ficaService = require('./ficaScreeningService');
const notificationService = require('./notificationService');
const documentVerificationWorker = require('../workers/documentVerificationWorker');

// Validators
const { 
    validateSAIDNumber, 
    validateBusinessRegistration
} = require('../validators/saLegalValidators');

// ID Generators
const { 
    generateFICARefNumber
} = require('../utils/complianceIdGenerator');

require('dotenv').config();

// =================================================================================================================
// CONSTANTS - Production Grade Configuration
// =================================================================================================================
const CLIENT_TYPES = {
    INDIVIDUAL: {
        id: 'INDIVIDUAL',
        description: 'Individual person',
        requiredFields: ['firstName', 'lastName', 'idNumber', 'dateOfBirth', 'nationality'],
        optionalFields: ['email', 'phone', 'occupation', 'incomeBracket'],
        screeningRequired: true,
        documentTypes: ['ID_COPY', 'PROOF_OF_ADDRESS', 'PROOF_OF_INCOME'],
        ficaRiskLevel: 'STANDARD',
        popiaRequirements: ['consent', 'purpose'],
        retentionPeriod: 7 * 365 // 7 years in days
    },
    COMPANY: {
        id: 'COMPANY',
        description: 'Registered company',
        requiredFields: ['businessName', 'registrationNumber', 'businessType', 'dateOfIncorporation'],
        optionalFields: ['tradingName', 'vatNumber', 'taxNumber', 'industrySector'],
        screeningRequired: true,
        documentTypes: ['COMPANY_REGISTRATION', 'TAX_CLEARANCE', 'DIRECTOR_ID_COPIES', 'FINANCIAL_STATEMENTS'],
        ficaRiskLevel: 'ENHANCED',
        popiaRequirements: ['consent', 'purpose', 'justification'],
        retentionPeriod: 10 * 365 // 10 years in days
    },
    TRUST: {
        id: 'TRUST',
        description: 'Legal trust',
        requiredFields: ['trustName', 'registrationNumber', 'trustType', 'dateEstablished'],
        optionalFields: ['masterReference', 'taxNumber', 'industrySector'],
        screeningRequired: true,
        documentTypes: ['TRUST_DEED', 'LETTER_OF_AUTHORITY', 'TRUSTEE_ID_COPIES', 'TAX_CLEARANCE'],
        ficaRiskLevel: 'ENHANCED',
        popiaRequirements: ['consent', 'purpose', 'justification'],
        retentionPeriod: 10 * 365
    },
    NPO: {
        id: 'NPO',
        description: 'Non-profit organization',
        requiredFields: ['organizationName', 'registrationNumber', 'npoNumber', 'dateRegistered'],
        optionalFields: ['sector', 'taxNumber', 'fundingSources'],
        screeningRequired: true,
        documentTypes: ['NPO_REGISTRATION', 'CONSTITUTION', 'DIRECTOR_ID_COPIES', 'TAX_CLEARANCE'],
        ficaRiskLevel: 'STANDARD',
        popiaRequirements: ['consent', 'purpose'],
        retentionPeriod: 7 * 365
    },
    PARTNERSHIP: {
        id: 'PARTNERSHIP',
        description: 'Business partnership',
        requiredFields: ['partnershipName', 'registrationNumber', 'partnershipType', 'dateFormed'],
        optionalFields: ['taxNumber', 'industrySector'],
        screeningRequired: true,
        documentTypes: ['PARTNERSHIP_AGREEMENT', 'PARTNER_ID_COPIES', 'TAX_CLEARANCE'],
        ficaRiskLevel: 'STANDARD',
        popiaRequirements: ['consent', 'purpose'],
        retentionPeriod: 7 * 365
    }
};

const ONBOARDING_STATUS = {
    PENDING: 'PENDING',
    IN_PROGRESS: 'IN_PROGRESS',
    COMPLETED: 'COMPLETED',
    CANCELLED: 'CANCELLED',
    REJECTED: 'REJECTED',
    PENDING_FICA: 'PENDING_FICA',
    FICA_APPROVED: 'FICA_APPROVED',
    FICA_REJECTED: 'FICA_REJECTED',
    PENDING_REVIEW: 'PENDING_REVIEW',
    MANUAL_REVIEW: 'MANUAL_REVIEW',
    ESCALATED: 'ESCALATED'
};

const ONBOARDING_STAGES = {
    INITIATED: { 
        id: 'INITIATED', 
        name: 'Onboarding Initiated', 
        order: 0,
        required: true,
        autoTransition: true,
        timeout: 24 * 60 * 60 * 1000 // 24 hours
    },
    CLIENT_INFO: { 
        id: 'CLIENT_INFO', 
        name: 'Client Information', 
        order: 1,
        required: true,
        autoTransition: false,
        timeout: 7 * 24 * 60 * 60 * 1000 // 7 days
    },
    FICA_SCREENING: { 
        id: 'FICA_SCREENING', 
        name: 'FICA Screening', 
        order: 2,
        required: true,
        autoTransition: true,
        timeout: 48 * 60 * 60 * 1000 // 48 hours
    },
    DOCUMENT_UPLOAD: { 
        id: 'DOCUMENT_UPLOAD', 
        name: 'Document Upload', 
        order: 3,
        required: true,
        autoTransition: false,
        timeout: 14 * 24 * 60 * 60 * 1000 // 14 days
    },
    DOCUMENT_VERIFICATION: { 
        id: 'DOCUMENT_VERIFICATION', 
        name: 'Document Verification', 
        order: 4,
        required: true,
        autoTransition: true,
        timeout: 72 * 60 * 60 * 1000 // 72 hours
    },
    REVIEW: { 
        id: 'REVIEW', 
        name: 'Review', 
        order: 5,
        required: true,
        autoTransition: false,
        timeout: 48 * 60 * 60 * 1000 // 48 hours
    },
    COMPLETED: { 
        id: 'COMPLETED', 
        name: 'Completed', 
        order: 6,
        required: true,
        autoTransition: false,
        timeout: null
    }
};

const SESSION_CONFIG = {
    DEFAULT_TTL: 30 * 24 * 60 * 60 * 1000, // 30 days
    EXTENDED_TTL: 90 * 24 * 60 * 60 * 1000, // 90 days
    CLEANUP_INTERVAL: 60 * 60 * 1000, // 1 hour
    MAX_RETRIES: 3,
    CIRCUIT_BREAKER_TIMEOUT: 5000,
    CIRCUIT_BREAKER_THRESHOLD: 0.5,
    BATCH_SIZE: 100,
    CACHE_TTL: 5 * 60 * 1000 // 5 minutes
};

const RISK_THRESHOLDS = {
    LOW: 25,
    MEDIUM: 50,
    HIGH: 75,
    CRITICAL: 90
};

// =================================================================================================================
// PRODUCTION SERVICE IMPLEMENTATION
// =================================================================================================================
class ClientOnboardingService extends EventEmitter {
    constructor() {
        super();
        
        // Core properties
        this.sessionCache = new Map();
        this.modelRegistry = new Map();
        this.circuitBreakers = new Map();
        this.healthStatus = {
            status: 'healthy',
            lastCheck: new Date().toISOString(),
            failures: []
        };
        
        // Initialize components
        this._initializeCircuitBreakers();
        this._startSessionCleanup();
        this._startHealthCheck();
        this._startMetricsCollection();
        
        // Bind methods
        this.createSession = this.createSession.bind(this);
        this.getSession = this.getSession.bind(this);
        this.updateSessionData = this.updateSessionData.bind(this);
        this.uploadDocument = this.uploadDocument.bind(this);
        this.getDocuments = this.getDocuments.bind(this);
        this.getStatistics = this.getStatistics.bind(this);
        
        logger.info('🚀 ClientOnboardingService initialized', {
            version: '5.0.1',
            environment: process.env.NODE_ENV || 'development',
            timestamp: new Date().toISOString()
        });
    }

    // =================================================================================================================
    // DYNAMIC MODEL LOADING - Registry-Aware
    // =================================================================================================================
    _getModels() {
        try {
            const Session = mongoose.models.OnboardingSession;
            const Document = mongoose.models.OnboardingDocument;
            
            if (!Session || !Document) {
                logger.warn('Models not fully initialized', {
                    session: !!Session,
                    document: !!Document
                });
            }
            
            return { Session, Document };
        } catch (error) {
            logger.error('Failed to get models from registry', { error: error.message });
            return { Session: null, Document: null };
        }
    }

    // =================================================================================================================
    // CIRCUIT BREAKER INITIALIZATION
    // =================================================================================================================
    _initializeCircuitBreakers() {
        const options = {
            timeout: SESSION_CONFIG.CIRCUIT_BREAKER_TIMEOUT,
            errorThresholdPercentage: SESSION_CONFIG.CIRCUIT_BREAKER_THRESHOLD * 100,
            resetTimeout: 30000,
            rollingCountTimeout: 10000,
            rollingCountBuckets: 10,
            name: 'database'
        };

        // Database operations circuit breaker
        this.circuitBreakers.set('database', new CircuitBreaker(async (operation) => {
            return await operation();
        }, options));

        // FICA service circuit breaker
        this.circuitBreakers.set('fica', new CircuitBreaker(async (operation) => {
            return await operation();
        }, {
            ...options,
            name: 'fica',
            timeout: 10000
        }));

        // Document service circuit breaker
        this.circuitBreakers.set('document', new CircuitBreaker(async (operation) => {
            return await operation();
        }, {
            ...options,
            name: 'document',
            timeout: 30000
        }));

        // Event handlers for circuit breakers
        for (const [name, breaker] of this.circuitBreakers) {
            breaker.on('open', () => {
                logger.error(`🔓 Circuit breaker opened: ${name}`);
                this.emit('circuit:open', { name, timestamp: new Date().toISOString() });
                metrics.increment('circuit_breaker.open', 1, { name });
            });
            
            breaker.on('halfOpen', () => {
                logger.warn(`⚠️ Circuit breaker half-open: ${name}`);
                this.emit('circuit:halfOpen', { name });
            });
            
            breaker.on('close', () => {
                logger.info(`🔒 Circuit breaker closed: ${name}`);
                this.emit('circuit:close', { name });
                metrics.increment('circuit_breaker.close', 1, { name });
            });
            
            breaker.on('fallback', (result, error) => {
                logger.warn(`🔄 Circuit breaker fallback: ${name}`, { error: error?.message });
                metrics.increment('circuit_breaker.fallback', 1, { name });
            });
        }
    }

    // =================================================================================================================
    // VALIDATION METHODS
    // =================================================================================================================
    _validateClientType(clientType) {
        if (!clientType) {
            throw new ValidationError('Client type is required', { 
                validTypes: Object.keys(CLIENT_TYPES) 
            });
        }

        let typeId = clientType;
        if (typeof clientType === 'object' && clientType.id) {
            typeId = clientType.id;
        }

        if (!CLIENT_TYPES[typeId]) {
            throw new ValidationError('Invalid client type', { 
                provided: typeId,
                validTypes: Object.keys(CLIENT_TYPES) 
            });
        }

        return CLIENT_TYPES[typeId];
    }

    _validateRequiredFields(clientTypeConfig, data) {
        const missing = [];
        
        for (const field of clientTypeConfig.requiredFields) {
            if (!data[field]) {
                missing.push(field);
            }
        }

        if (missing.length > 0) {
            throw new ValidationError('Missing required fields', { 
                missing,
                clientType: clientTypeConfig.id 
            });
        }
    }

    _validateDocumentInfo(documentInfo) {
        const required = ['documentType', 'fileName', 'fileSize', 'mimeType'];
        const missing = required.filter(field => !documentInfo[field]);
        
        if (missing.length > 0) {
            throw new ValidationError('Invalid document info', { 
                missing,
                required 
            });
        }

        // Validate file size
        if (documentInfo.fileSize > 50 * 1024 * 1024) {
            throw new ValidationError('File size exceeds maximum limit', {
                maxSize: '50MB',
                provided: `${Math.round(documentInfo.fileSize / (1024 * 1024))}MB`
            });
        }

        // Validate mime type
        const allowedMimeTypes = [
            'application/pdf',
            'image/jpeg',
            'image/png',
            'image/tiff',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ];

        if (!allowedMimeTypes.includes(documentInfo.mimeType)) {
            throw new ValidationError('Invalid mime type', {
                allowed: allowedMimeTypes,
                provided: documentInfo.mimeType
            });
        }
    }

    _calculateRiskScore(clientTypeConfig, clientData) {
        let score = 0;
        const factors = [];

        // Base risk by client type
        switch(clientTypeConfig.ficaRiskLevel) {
            case 'ENHANCED':
                score += 30;
                factors.push({ factor: 'client_type_enhanced', score: 30, description: 'Enhanced due diligence required' });
                break;
            case 'STANDARD':
                score += 10;
                factors.push({ factor: 'client_type_standard', score: 10, description: 'Standard due diligence' });
                break;
        }

        // Geographic risk (simplified)
        if (clientData.countryOfResidence && clientData.countryOfResidence !== 'South Africa') {
            score += 20;
            factors.push({ factor: 'foreign_national', score: 20, description: 'Foreign national' });
        }

        // PEP check (would be from external service)
        if (clientData.isPoliticallyExposed) {
            score += 40;
            factors.push({ factor: 'politically_exposed', score: 40, description: 'Politically exposed person' });
        }

        // Income/wealth check
        if (clientData.annualIncome && clientData.annualIncome > 10000000) { // R10M+
            score += 15;
            factors.push({ factor: 'high_net_worth', score: 15, description: 'High net worth individual' });
        }

        return { score: Math.min(score, 100), factors };
    }

    // =================================================================================================================
    // ID GENERATION
    // =================================================================================================================
    _generateSessionId(clientType, tenantId) {
        const prefix = clientType === 'INDIVIDUAL' ? 'IND' : 
                      clientType === 'COMPANY' ? 'BUS' : 
                      clientType === 'TRUST' ? 'TRU' : 
                      clientType === 'NPO' ? 'NPO' : 'PAR';
        
        const timestamp = DateTime.now().toFormat('yyyyMMddHHmmss');
        const random = crypto.randomBytes(4).toString('hex').toUpperCase();
        const tenantSuffix = tenantId.replace(/[^a-zA-Z0-9]/g, '').slice(-4);
        
        return `ONB_${prefix}_${timestamp}_${random}_${tenantSuffix}`;
    }

    _generateDocumentId(documentType) {
        const type = documentType.substring(0, 3).toUpperCase();
        const timestamp = DateTime.now().toFormat('yyyyMMddHHmmss');
        const random = crypto.randomBytes(4).toString('hex').toUpperCase();
        
        return `DOC_${type}_${timestamp}_${random}`;
    }

    _generateCorrelationId() {
        return `corr_${Date.now()}_${crypto.randomBytes(8).toString('hex')}`;
    }

    // =================================================================================================================
    // AUDIT LOGGING
    // =================================================================================================================
    async _auditLog(action, data) {
        try {
            await auditLogger.audit({
                action,
                timestamp: new Date().toISOString(),
                correlationId: data.correlationId || this._generateCorrelationId(),
                tenantId: data.tenantId,
                userId: data.userId || tenantContext.getCurrentUser() || 'system',
                sessionId: data.sessionId,
                documentId: data.documentId,
                details: data
            });
        } catch (error) {
            logger.error('Audit log failed', { action, error: error.message });
        }
    }

    // =================================================================================================================
    // PUBLIC API METHODS
    // =================================================================================================================
    async createSession(sessionId, tenantId, clientType, initialData = {}) {
        const correlationId = this._generateCorrelationId();
        const startTime = Date.now();
        const userId = tenantContext.getCurrentUser() || 'system';

        try {
            logger.info('Creating onboarding session', { 
                sessionId, 
                tenantId, 
                clientType,
                correlationId,
                userId
            });

            metrics.increment('onboarding.session.create.attempt', 1, { clientType });

            // Validate client type
            const clientTypeConfig = this._validateClientType(clientType);
            
            // Validate required fields
            this._validateRequiredFields(clientTypeConfig, initialData);

            // Validate specific ID formats based on client type
            if (clientType === 'INDIVIDUAL' && initialData.idNumber) {
                validateSAIDNumber(initialData.idNumber);
            }
            if (clientType === 'COMPANY' && initialData.registrationNumber) {
                validateBusinessRegistration(initialData.registrationNumber);
            }

            // Generate actual session ID if not provided
            const actualSessionId = sessionId || this._generateSessionId(clientTypeConfig.id, tenantId);

            // Get models
            const { Session } = this._getModels();
            
            if (!Session) {
                throw new DatabaseError('Session model not initialized', { 
                    tenantId,
                    availableModels: Object.keys(mongoose.models)
                });
            }

            // Calculate risk score
            const riskAssessment = this._calculateRiskScore(clientTypeConfig, initialData);

            // Create session document
            const session = new Session({
                sessionId: actualSessionId,
                tenantId,
                clientType: clientTypeConfig.id,
                clientData: initialData,
                status: ONBOARDING_STATUS.PENDING,
                currentStage: ONBOARDING_STAGES.INITIATED.id,
                stages: [{
                    stage: ONBOARDING_STAGES.INITIATED.id,
                    status: 'COMPLETED',
                    timestamp: new Date(),
                    data: initialData,
                    performedBy: userId,
                    ipAddress: initialData._ipAddress,
                    userAgent: initialData._userAgent,
                    correlationId
                }],
                riskScore: riskAssessment.score,
                riskFactors: riskAssessment.factors,
                metadata: {
                    createdAt: new Date(),
                    createdBy: userId,
                    createdByIp: initialData._ipAddress,
                    createdByUserAgent: initialData._userAgent,
                    updatedAt: new Date(),
                    updatedBy: userId,
                    correlationId
                },
                compliance: {
                    popiaConsent: initialData.popiaConsent || false,
                    popiaConsentTimestamp: initialData.popiaConsent ? new Date() : null,
                    ficaConsent: initialData.ficaConsent || false,
                    ficaConsentTimestamp: initialData.ficaConsent ? new Date() : null,
                    dataRetentionPeriod: clientTypeConfig.retentionPeriod,
                    ficaReference: generateFICARefNumber(actualSessionId)
                }
            });

            // Save with circuit breaker
            const savedSession = await this.circuitBreakers.get('database').fire(async () => {
                return await session.save();
            });

            // Cache session
            this.sessionCache.set(actualSessionId, {
                data: savedSession,
                expiresAt: Date.now() + SESSION_CONFIG.CACHE_TTL
            });

            // Trigger async FICA screening if required
            if (clientTypeConfig.screeningRequired) {
                this._triggerFICAScreening(actualSessionId, tenantId, initialData, userId).catch(err => {
                    logger.error('FICA screening failed', { sessionId: actualSessionId, error: err.message });
                });
            }

            // Audit log
            await this._auditLog('SESSION_CREATED', {
                sessionId: actualSessionId,
                tenantId,
                clientType: clientTypeConfig.id,
                userId,
                correlationId
            });

            // Emit event
            this.emit('session:created', {
                sessionId: actualSessionId,
                tenantId,
                clientType: clientTypeConfig.id,
                userId,
                timestamp: new Date().toISOString()
            });

            // Record metrics
            const duration = Date.now() - startTime;
            metrics.recordTiming('onboarding.session.create', duration, { clientType });
            metrics.increment('onboarding.session.create.success', 1, { clientType });

            logger.info('Session created successfully', {
                sessionId: actualSessionId,
                tenantId,
                duration,
                riskScore: riskAssessment.score
            });

            return savedSession;

        } catch (error) {
            metrics.increment('onboarding.session.create.error', 1, { 
                clientType,
                errorType: error.constructor.name 
            });

            logger.error('Failed to create session', {
                sessionId,
                tenantId,
                error: error.message,
                stack: error.stack,
                correlationId
            });

            if (error instanceof ValidationError || 
                error instanceof DatabaseError || 
                error instanceof FICAComplianceError) {
                throw error;
            }

            throw new DatabaseError('Failed to create session', { 
                cause: error.message,
                correlationId 
            });
        }
    }

    async getSession(sessionId, tenantId, options = {}) {
        const correlationId = this._generateCorrelationId();
        const startTime = Date.now();

        try {
            logger.debug('Getting session', { sessionId, tenantId, correlationId });

            metrics.increment('onboarding.session.get.attempt', 1);

            // Check cache first
            if (!options.skipCache) {
                const cached = this.sessionCache.get(sessionId);
                if (cached && cached.expiresAt > Date.now()) {
                    if (cached.data.tenantId === tenantId) {
                        logger.debug('Session found in cache', { sessionId });
                        metrics.increment('onboarding.session.get.cache_hit', 1);
                        return cached.data;
                    } else {
                        logger.warn('Tenant mismatch in cache', { 
                            sessionId, 
                            cachedTenant: cached.data.tenantId,
                            requestedTenant: tenantId 
                        });
                    }
                }
            }

            // Get model
            const { Session } = this._getModels();
            
            if (!Session) {
                return null;
            }

            // Query with circuit breaker
            const session = await this.circuitBreakers.get('database').fire(async () => {
                const query = Session.findOne({ sessionId, tenantId });
                
                if (options.populate !== false) {
                    query.populate({
                        path: 'documents',
                        match: { isDeleted: false },
                        select: '-fileData -encryptionMetadata'
                    });
                }
                
                return await query.lean(options.lean || false);
            });

            if (!session) {
                metrics.increment('onboarding.session.get.not_found', 1);
                return null;
            }

            // Update cache
            if (!options.skipCache) {
                this.sessionCache.set(sessionId, {
                    data: session,
                    expiresAt: Date.now() + SESSION_CONFIG.CACHE_TTL
                });
            }

            // Audit log for sensitive access
            if (session.riskScore >= RISK_THRESHOLDS.HIGH) {
                await this._auditLog('HIGH_RISK_SESSION_ACCESSED', {
                    sessionId,
                    tenantId,
                    correlationId
                });
            }

            const duration = Date.now() - startTime;
            metrics.recordTiming('onboarding.session.get', duration);
            metrics.increment('onboarding.session.get.success', 1);

            logger.debug('Session retrieved', {
                sessionId,
                duration
            });

            return session;

        } catch (error) {
            metrics.increment('onboarding.session.get.error', 1, { 
                errorType: error.constructor.name 
            });

            logger.error('Failed to get session', {
                sessionId,
                tenantId,
                error: error.message,
                correlationId
            });

            return null;
        }
    }

    async updateSessionData(sessionId, tenantId, stageId, data, performedBy = null) {
        const correlationId = this._generateCorrelationId();
        const startTime = Date.now();
        const userId = performedBy || tenantContext.getCurrentUser() || 'system';

        try {
            logger.info('Updating session', { sessionId, tenantId, stageId, correlationId, userId });

            metrics.increment('onboarding.session.update.attempt', 1, { stageId });

            // Validate stage
            if (!ONBOARDING_STAGES[stageId]) {
                throw new ValidationError('Invalid stage ID', {
                    provided: stageId,
                    validStages: Object.keys(ONBOARDING_STAGES)
                });
            }

            // Get model
            const { Session } = this._getModels();
            
            if (!Session) {
                throw new DatabaseError('Session model not initialized');
            }

            // Update with circuit breaker
            const session = await this.circuitBreakers.get('database').fire(async () => {
                return await Session.findOneAndUpdate(
                    { sessionId, tenantId },
                    {
                        $push: {
                            stages: {
                                stage: stageId,
                                status: 'COMPLETED',
                                timestamp: new Date(),
                                data,
                                performedBy: userId,
                                correlationId
                            }
                        },
                        $set: {
                            currentStage: stageId,
                            'metadata.updatedAt': new Date(),
                            'metadata.updatedBy': userId,
                            ...(stageId === ONBOARDING_STAGES.COMPLETED.id && {
                                status: ONBOARDING_STATUS.COMPLETED
                            })
                        }
                    },
                    { new: true, runValidators: true }
                );
            });

            if (!session) {
                throw new ResourceNotFoundError('Session not found', { sessionId, tenantId });
            }

            // Update cache
            this.sessionCache.set(sessionId, {
                data: session,
                expiresAt: Date.now() + SESSION_CONFIG.CACHE_TTL
            });

            // Audit log
            await this._auditLog('SESSION_UPDATED', {
                sessionId,
                tenantId,
                stageId,
                userId,
                correlationId
            });

            // Emit event
            this.emit('session:updated', {
                sessionId,
                tenantId,
                stageId,
                userId,
                timestamp: new Date().toISOString()
            });

            const duration = Date.now() - startTime;
            metrics.recordTiming('onboarding.session.update', duration, { stageId });
            metrics.increment('onboarding.session.update.success', 1, { stageId });

            logger.info('Session updated', {
                sessionId,
                stageId,
                duration
            });

            return session;

        } catch (error) {
            metrics.increment('onboarding.session.update.error', 1, { 
                stageId,
                errorType: error.constructor.name 
            });

            logger.error('Failed to update session', {
                sessionId,
                tenantId,
                stageId,
                error: error.message,
                correlationId
            });

            if (error instanceof ValidationError || error instanceof ResourceNotFoundError) {
                throw error;
            }

            throw new DatabaseError('Failed to update session', { cause: error.message });
        }
    }

    async uploadDocument(sessionId, tenantId, documentInfo, fileData, options = {}) {
        const correlationId = this._generateCorrelationId();
        const documentId = this._generateDocumentId(documentInfo.documentType);
        const startTime = Date.now();
        const userId = options.userId || tenantContext.getCurrentUser() || 'system';

        try {
            logger.info('Uploading document', { 
                sessionId, 
                tenantId, 
                documentType: documentInfo.documentType,
                documentId,
                correlationId,
                userId,
                fileSize: documentInfo.fileSize
            });

            metrics.increment('onboarding.document.upload.attempt', 1, { 
                documentType: documentInfo.documentType 
            });

            // Validate document info
            this._validateDocumentInfo(documentInfo);

            // Get models
            const { Session, Document } = this._getModels();
            
            if (!Document || !Session) {
                throw new DatabaseError('Models not initialized');
            }

            // Verify session exists and is active
            const session = await this.getSession(sessionId, tenantId, { lean: true });
            if (!session) {
                throw new ResourceNotFoundError('Session not found');
            }

            if (session.status === ONBOARDING_STATUS.COMPLETED || 
                session.status === ONBOARDING_STATUS.CANCELLED) {
                throw new ValidationError('Cannot upload documents to completed or cancelled session', {
                    sessionStatus: session.status
                });
            }

            // Generate file hash for deduplication
            const fileHash = crypto
                .createHash('sha256')
                .update(fileData)
                .digest('hex');

            // Check for duplicates
            const existingDocs = await Document.find({ 
                fileHash, 
                tenantId,
                isDeleted: false 
            });

            if (existingDocs.length > 0) {
                logger.warn('Duplicate document upload attempt', {
                    sessionId,
                    documentId,
                    fileHash,
                    existingDocs: existingDocs.map(d => d.documentId)
                });
                
                // Still allow upload but flag for review
                documentInfo.duplicateWarning = true;
            }

            // Encrypt document
            const encryptionKeyId = process.env.ENCRYPTION_KEY_ID || 'default-key';
            const iv = crypto.randomBytes(12);
            const cipher = crypto.createCipheriv('aes-256-gcm', Buffer.from(process.env.ENCRYPTION_KEY || 'default-key-32-bytes-long!!', 'utf8'), iv);
            
            const encryptedData = Buffer.concat([
                cipher.update(fileData),
                cipher.final()
            ]);
            
            const authTag = cipher.getAuthTag();

            // Create document
            const document = new Document({
                documentId,
                sessionId,
                tenantId,
                ...documentInfo,
                fileData: encryptedData,
                fileHash,
                encryptionMetadata: {
                    algorithm: 'AES-256-GCM',
                    keyId: encryptionKeyId,
                    iv: iv.toString('hex'),
                    authTag: authTag.toString('hex'),
                    encryptedAt: new Date(),
                    encryptedBy: userId
                },
                uploadedAt: new Date(),
                metadata: {
                    createdAt: new Date(),
                    createdBy: userId,
                    createdByIp: options.ipAddress,
                    createdByUserAgent: options.userAgent,
                    correlationId
                },
                chainOfCustody: [{
                    action: 'UPLOADED',
                    performedBy: userId,
                    ipAddress: options.ipAddress,
                    userAgent: options.userAgent,
                    timestamp: new Date()
                }]
            });

            // Save with circuit breaker
            const savedDocument = await this.circuitBreakers.get('document').fire(async () => {
                return await document.save();
            });

            // Update session with document reference
            await this.circuitBreakers.get('database').fire(async () => {
                return await Session.updateOne(
                    { sessionId, tenantId },
                    { 
                        $push: { documents: savedDocument._id },
                        $set: { 'metadata.updatedAt': new Date() }
                    }
                );
            });

            // Queue for async processing
            await documentVerificationWorker.queueForScanning(documentId, tenantId, {
                priority: 'HIGH',
                userId,
                correlationId
            });

            await documentVerificationWorker.queueForOCR(documentId, tenantId, {
                userId,
                correlationId
            });

            // Audit log
            await this._auditLog('DOCUMENT_UPLOADED', {
                documentId,
                sessionId,
                tenantId,
                documentType: documentInfo.documentType,
                fileSize: documentInfo.fileSize,
                fileHash,
                userId,
                correlationId
            });

            // Emit event
            this.emit('document:uploaded', {
                documentId,
                sessionId,
                tenantId,
                documentType: documentInfo.documentType,
                userId,
                timestamp: new Date().toISOString()
            });

            const duration = Date.now() - startTime;
            metrics.recordTiming('onboarding.document.upload', duration, { 
                documentType: documentInfo.documentType 
            });
            metrics.increment('onboarding.document.upload.success', 1, { 
                documentType: documentInfo.documentType 
            });

            logger.info('Document uploaded successfully', {
                documentId,
                sessionId,
                fileSize: documentInfo.fileSize,
                fileHash: fileHash.substring(0, 8),
                duration
            });

            return savedDocument;

        } catch (error) {
            metrics.increment('onboarding.document.upload.error', 1, { 
                documentType: documentInfo.documentType,
                errorType: error.constructor.name 
            });

            logger.error('Failed to upload document', {
                sessionId,
                tenantId,
                documentId,
                error: error.message,
                correlationId
            });

            if (error instanceof ValidationError || error instanceof ResourceNotFoundError) {
                throw error;
            }

            throw new DatabaseError('Failed to upload document', { cause: error.message });
        }
    }

    async getDocuments(sessionId, tenantId, options = {}) {
        const correlationId = this._generateCorrelationId();
        const startTime = Date.now();

        try {
            logger.debug('Getting documents', { sessionId, tenantId, correlationId });

            metrics.increment('onboarding.document.get.attempt', 1);

            const { Document } = this._getModels();
            
            if (!Document) {
                return [];
            }

            const query = Document.find({ 
                sessionId, 
                tenantId,
                isDeleted: false 
            });

            if (options.documentType) {
                query.where('documentType').equals(options.documentType);
            }

            if (options.verificationStatus) {
                query.where('processingStatus.verification.status').equals(options.verificationStatus);
            }

            if (options.sort) {
                query.sort(options.sort);
            } else {
                query.sort({ uploadedAt: -1 });
            }

            if (options.limit) {
                query.limit(options.limit);
            }

            if (options.skip) {
                query.skip(options.skip);
            }

            // Exclude file data by default for performance
            if (!options.includeFileData) {
                query.select('-fileData');
            }

            const documents = await this.circuitBreakers.get('database').fire(async () => {
                return await query.lean();
            });

            const duration = Date.now() - startTime;
            metrics.recordTiming('onboarding.document.get', duration);
            metrics.increment('onboarding.document.get.success', 1);

            logger.debug('Documents retrieved', {
                sessionId,
                count: documents.length,
                duration
            });

            return documents;

        } catch (error) {
            metrics.increment('onboarding.document.get.error', 1, { 
                errorType: error.constructor.name 
            });

            logger.error('Failed to get documents', {
                sessionId,
                tenantId,
                error: error.message,
                correlationId
            });
            return [];
        }
    }

    async getStatistics(tenantId, dateRange = {}, options = {}) {
        const correlationId = this._generateCorrelationId();
        const startTime = Date.now();

        try {
            logger.info('Getting statistics', { tenantId, correlationId });

            metrics.increment('onboarding.statistics.get.attempt', 1);

            const { Session, Document } = this._getModels();

            if (!Session || !Document) {
                return {
                    tenantId,
                    error: 'Models not initialized',
                    generatedAt: new Date().toISOString()
                };
            }

            // Get session statistics
            const sessionStats = await this.circuitBreakers.get('database').fire(async () => {
                return await Session.getStatistics(tenantId, dateRange);
            });

            // Get document statistics
            const documentStats = await this.circuitBreakers.get('database').fire(async () => {
                return await Document.getStatistics(tenantId, dateRange);
            });

            // Get completion metrics
            const completionMetrics = await this._getCompletionMetrics(tenantId, dateRange);

            const statistics = {
                tenantId,
                timeframe: {
                    start: dateRange.start || 'all',
                    end: dateRange.end || 'now'
                },
                sessions: sessionStats[0] || {
                    statusBreakdown: [],
                    clientTypeBreakdown: [],
                    ficaStatusBreakdown: [],
                    riskLevelBreakdown: [],
                    dailyStats: [],
                    averages: {}
                },
                documents: documentStats[0] || {
                    documentTypeBreakdown: [],
                    verificationStatusBreakdown: [],
                    virusScanStatusBreakdown: [],
                    fraudRiskBreakdown: [],
                    dailyStats: [],
                    totals: {}
                },
                completion: completionMetrics,
                generatedAt: new Date().toISOString(),
                correlationId
            };

            if (options.includeMetadata) {
                statistics.metadata = {
                    version: '1.0',
                    environment: process.env.NODE_ENV,
                    queryTime: Date.now() - startTime
                };
            }

            const duration = Date.now() - startTime;
            metrics.recordTiming('onboarding.statistics.get', duration);
            metrics.increment('onboarding.statistics.get.success', 1);

            logger.info('Statistics retrieved', {
                tenantId,
                duration
            });

            return statistics;

        } catch (error) {
            metrics.increment('onboarding.statistics.get.error', 1, { 
                errorType: error.constructor.name 
            });

            logger.error('Failed to get statistics', {
                tenantId,
                error: error.message,
                correlationId
            });

            return {
                tenantId,
                error: 'Failed to retrieve statistics',
                generatedAt: new Date().toISOString()
            };
        }
    }

    // =================================================================================================================
    // PRIVATE HELPER METHODS
    // =================================================================================================================
    async _triggerFICAScreening(sessionId, tenantId, clientData, userId) {
        try {
            logger.info('Triggering FICA screening', { sessionId, tenantId, userId });

            const result = await this.circuitBreakers.get('fica').fire(async () => {
                return await ficaService.screenClient(sessionId, tenantId, clientData, userId);
            });

            if (result.status === 'APPROVED') {
                await this.updateSessionData(
                    sessionId, 
                    tenantId, 
                    ONBOARDING_STAGES.FICA_SCREENING.id,
                    {
                        status: 'APPROVED',
                        reference: result.reference,
                        riskLevel: result.riskLevel,
                        timestamp: new Date().toISOString()
                    },
                    userId
                );

                // Update session with FICA status
                const { Session } = this._getModels();
                if (Session) {
                    await Session.updateOne(
                        { sessionId, tenantId },
                        {
                            $set: {
                                ficaStatus: 'APPROVED',
                                ficaReference: result.reference,
                                ficaResults: result,
                                'compliance.ficaConsent': true,
                                'compliance.ficaConsentTimestamp': new Date()
                            }
                        }
                    );
                }

                // Notify client
                await notificationService.notifyClient(sessionId, tenantId, 'FICA_APPROVED', {
                    reference: result.reference
                });

            } else if (result.status === 'REJECTED') {
                await this.updateSessionData(
                    sessionId, 
                    tenantId, 
                    ONBOARDING_STAGES.FICA_SCREENING.id,
                    {
                        status: 'REJECTED',
                        reason: result.reason,
                        timestamp: new Date().toISOString()
                    },
                    userId
                );

                const { Session } = this._getModels();
                if (Session) {
                    await Session.updateOne(
                        { sessionId, tenantId },
                        {
                            $set: {
                                ficaStatus: 'REJECTED',
                                ficaResults: result,
                                status: ONBOARDING_STATUS.FICA_REJECTED
                            }
                        }
                    );
                }

                await notificationService.notifyClient(sessionId, tenantId, 'FICA_REJECTED', {
                    reason: result.reason
                });

            } else if (result.status === 'PENDING') {
                const { Session } = this._getModels();
                if (Session) {
                    await Session.updateOne(
                        { sessionId, tenantId },
                        {
                            $set: {
                                ficaStatus: 'PENDING',
                                status: ONBOARDING_STATUS.PENDING_FICA
                            }
                        }
                    );
                }
            }

            // Audit log
            await this._auditLog('FICA_SCREENING_COMPLETED', {
                sessionId,
                tenantId,
                result: result.status,
                reference: result.reference,
                userId
            });

            this.emit('fica:screening_completed', {
                sessionId,
                tenantId,
                status: result.status,
                reference: result.reference
            });

        } catch (error) {
            logger.error('FICA screening failed', { 
                sessionId, 
                tenantId, 
                error: error.message 
            });
            
            metrics.increment('onboarding.fica.screening.error', 1);

            // Queue for retry with exponential backoff
            setTimeout(() => {
                this._triggerFICAScreening(sessionId, tenantId, clientData, userId);
            }, 60000 * Math.pow(2, (error.attempts || 0))); // Exponential backoff
        }
    }

    async _getCompletionMetrics(tenantId, dateRange) {
        const { Session } = this._getModels();
        
        if (!Session) {
            return {
                averageCompletionTime: 0,
                completionRate: 0,
                dropoffRate: 0
            };
        }

        const match = { tenantId };
        
        if (dateRange.start || dateRange.end) {
            match.createdAt = {};
            if (dateRange.start) match.createdAt.$gte = new Date(dateRange.start);
            if (dateRange.end) match.createdAt.$lte = new Date(dateRange.end);
        }

        const results = await Session.aggregate([
            { $match: match },
            {
                $group: {
                    _id: null,
                    total: { $sum: 1 },
                    completed: {
                        $sum: { $cond: [{ $eq: ['$status', ONBOARDING_STATUS.COMPLETED] }, 1, 0] }
                    },
                    cancelled: {
                        $sum: { $cond: [{ $eq: ['$status', ONBOARDING_STATUS.CANCELLED] }, 1, 0] }
                    },
                    rejected: {
                        $sum: { $cond: [{ $eq: ['$status', ONBOARDING_STATUS.REJECTED] }, 1, 0] }
                    },
                    completedSessions: {
                        $push: {
                            $cond: [
                                { $eq: ['$status', ONBOARDING_STATUS.COMPLETED] },
                                {
                                    createdAt: '$createdAt',
                                    completedAt: '$metadata.updatedAt',
                                    stages: { $size: '$stages' }
                                },
                                null
                            ]
                        }
                    }
                }
            }
        ]);

        if (results.length === 0) {
            return {
                averageCompletionTime: 0,
                completionRate: 0,
                dropoffRate: 0
            };
        }

        const result = results[0];
        
        // Calculate average completion time
        const completionTimes = result.completedSessions
            .filter(s => s && s.completedAt)
            .map(s => new Date(s.completedAt) - new Date(s.createdAt));
        
        const averageCompletionTime = completionTimes.length > 0
            ? completionTimes.reduce((a, b) => a + b, 0) / completionTimes.length
            : 0;

        // Calculate completion rate
        const completionRate = result.total > 0
            ? (result.completed / result.total) * 100
            : 0;

        // Calculate dropoff rate (cancelled + rejected)
        const dropoffRate = result.total > 0
            ? ((result.cancelled + result.rejected) / result.total) * 100
            : 0;

        return {
            averageCompletionTime,
            completionRate,
            dropoffRate,
            totalSessions: result.total,
            completedSessions: result.completed,
            cancelledSessions: result.cancelled,
            rejectedSessions: result.rejected
        };
    }

    // =================================================================================================================
    // BACKGROUND TASKS
    // =================================================================================================================
    _startSessionCleanup() {
        this._cleanupInterval = setInterval(() => {
            const now = Date.now();
            let expiredCount = 0;

            // Clean up expired sessions from cache
            for (const [sessionId, cached] of this.sessionCache) {
                if (cached.expiresAt < now) {
                    this.sessionCache.delete(sessionId);
                    expiredCount++;
                }
            }

            if (expiredCount > 0) {
                logger.debug('Cleaned up expired sessions from cache', { count: expiredCount });
                metrics.setGauge('onboarding.cache.size', this.sessionCache.size);
            }
        }, SESSION_CONFIG.CLEANUP_INTERVAL);

        // Prevent Node.js from hanging on this interval
        this._cleanupInterval.unref();
    }

    _startHealthCheck() {
        this._healthCheckInterval = setInterval(async () => {
            try {
                const health = await this.healthCheck();
                this.healthStatus = {
                    ...health,
                    lastCheck: new Date().toISOString()
                };

                if (health.status !== 'healthy') {
                    logger.warn('Health check degraded', health);
                    this.emit('health:degraded', health);
                    metrics.increment('onboarding.health.degraded', 1);
                } else {
                    metrics.setGauge('onboarding.health.status', 1);
                }
            } catch (error) {
                logger.error('Health check failed', { error: error.message });
                metrics.increment('onboarding.health.failed', 1);
            }
        }, 60000); // Check every minute

        this._healthCheckInterval.unref();
    }

    _startMetricsCollection() {
        this._metricsInterval = setInterval(() => {
            try {
                metrics.setGauge('onboarding.cache.size', this.sessionCache.size);
                
                // Circuit breaker metrics
                for (const [name, breaker] of this.circuitBreakers) {
                    metrics.setGauge(`circuit_breaker.${name}.status`, breaker.opened ? 0 : 1);
                    metrics.setGauge(`circuit_breaker.${name}.pending`, breaker.pending);
                    metrics.setGauge(`circuit_breaker.${name}.failures`, breaker.stats.failures);
                }
            } catch (error) {
                logger.error('Metrics collection failed', { error: error.message });
            }
        }, 30000); // Collect metrics every 30 seconds

        this._metricsInterval.unref();
    }

    // =================================================================================================================
    // HEALTH CHECK & SHUTDOWN
    // =================================================================================================================
    async healthCheck() {
        const { Session, Document } = this._getModels();
        
        const status = {
            service: 'ClientOnboardingService',
            version: '5.0.1',
            timestamp: new Date().toISOString(),
            status: 'healthy',
            dependencies: {},
            metrics: {
                cacheSize: this.sessionCache.size,
                circuitBreakers: {}
            }
        };

        try {
            // Check database
            if (mongoose.connection.readyState === 1) {
                await mongoose.connection.db.admin().ping();
                status.dependencies.database = { 
                    status: 'healthy',
                    latency: await this._measureDatabaseLatency()
                };
            } else {
                status.dependencies.database = { 
                    status: 'disconnected',
                    readyState: mongoose.connection.readyState
                };
                status.status = 'degraded';
            }

            // Check models
            status.dependencies.models = {
                session: !!Session,
                document: !!Document
            };

            if (!Session || !Document) {
                status.status = 'degraded';
            }

            // Check circuit breakers
            for (const [name, breaker] of this.circuitBreakers) {
                status.metrics.circuitBreakers[name] = {
                    status: breaker.opened ? 'open' : 'closed',
                    pending: breaker.pending,
                    failures: breaker.stats.failures,
                    successRate: breaker.stats.successful / (breaker.stats.total || 1)
                };
            }

            // Check external services
            try {
                const ficaHealth = await ficaService.healthCheck();
                status.dependencies.fica = ficaHealth;
            } catch (error) {
                status.dependencies.fica = { status: 'unhealthy', error: error.message };
                status.status = 'degraded';
            }

            try {
                const notificationHealth = await notificationService.healthCheck();
                status.dependencies.notification = notificationHealth;
            } catch (error) {
                status.dependencies.notification = { status: 'unhealthy', error: error.message };
                status.status = 'degraded';
            }

        } catch (error) {
            status.status = 'unhealthy';
            status.error = error.message;
        }

        return status;
    }

    async _measureDatabaseLatency() {
        const start = Date.now();
        await mongoose.connection.db.admin().ping();
        return Date.now() - start;
    }

    async shutdown() {
        logger.info('Shutting down ClientOnboardingService');

        // Clear intervals
        if (this._cleanupInterval) {
            clearInterval(this._cleanupInterval);
            this._cleanupInterval = null;
        }

        if (this._healthCheckInterval) {
            clearInterval(this._healthCheckInterval);
            this._healthCheckInterval = null;
        }

        if (this._metricsInterval) {
            clearInterval(this._metricsInterval);
            this._metricsInterval = null;
        }

        // Close circuit breakers
        for (const [name, breaker] of this.circuitBreakers) {
            breaker.shutdown();
        }

        // Clear caches
        this.sessionCache.clear();
        this.modelRegistry.clear();

        logger.info('ClientOnboardingService shutdown complete');
        return true;
    }
}

// Export singleton instance
module.exports = new ClientOnboardingService();
