/* eslint-disable */
/**
 * 🏛️ WILSYS OS - LPC REGULATOR BLOCKCHAIN ANCHOR
 * Standard: ES Module (Surgically Standardized)
 * @version 5.2.4
 */

import crypto from 'node:crypto';
import axios from 'axios';
import { EventEmitter } from 'node:events';
import { DateTime } from 'luxon';
import { CircuitBreaker } from '../utils/circuitBreaker.js';

import {
    RetryableError, ServiceUnavailableError, DataIntegrityError,
    NotFoundError, ValidationError, ComplianceError, CircuitBreakerError,
    AuthorizationError, AuthenticationError, RateLimitError, ConflictError,
    BlockchainAnchorError, LPCComplianceError, FICAComplianceError,
    GDPRComplianceError, POPIAComplianceError, RegulatoryDeadlineError,
    ErrorFactory
} from '../utils/errors.js';

import { PerformanceMonitor } from '../utils/performance.js';
import AuditService from './auditService.js';
class BlockchainAnchor extends EventEmitter {
    constructor() {
        super();

        // ================================================================
        // REGULATOR ENDPOINTS - PRODUCTION CONFIGURATION
        // ================================================================
        this.regulators = {
            LPC: {
                name: 'Legal Practice Council',
                jurisdiction: 'ZA',
                apiVersion: 'v2',
                production: {
                    primary: 'https://blockchain.lpc.org.za/api/v2/anchor',
                    secondary: 'https://anchor.lpc.org.za/api/v2/submit',
                    fallback: 'https://consensus.lpc.org.za/api/v2/propagate',
                    health: 'https://blockchain.lpc.org.za/health',
                    status: 'https://blockchain.lpc.org.za/status'
                },
                sandbox: {
                    primary: 'https://sandbox.lpc.org.za/api/v2/anchor',
                    secondary: 'https://sandbox-anchor.lpc.org.za/api/v2/submit',
                    health: 'https://sandbox.lpc.org.za/health',
                    status: 'https://sandbox.lpc.org.za/status'
                },
                requirements: {
                    minConfirmations: 12,
                    blockTimeMs: 15000,
                    requiredSignatures: 3,
                    gasPrice: '0.000001',
                    gasLimit: 100000,
                    maxRetries: 5,
                    timeoutMs: 30000
                },
                features: {
                    anchoring: true,
                    verification: true,
                    confirmationPolling: true,
                    webhooks: true
                }
            },
            SARB: {
                name: 'South African Reserve Bank',
                jurisdiction: 'ZA',
                apiVersion: 'v1',
                production: {
                    primary: 'https://anchor.resbank.co.za/api/v1/record',
                    secondary: 'https://anchor-sand.resbank.co.za/api/v1/record',
                    health: 'https://anchor.resbank.co.za/health',
                    status: 'https://anchor.resbank.co.za/status'
                },
                sandbox: {
                    primary: 'https://sandbox.resbank.co.za/api/v1/record',
                    health: 'https://sandbox.resbank.co.za/health',
                    status: 'https://sandbox.resbank.co.za/status'
                },
                requirements: {
                    minConfirmations: 6,
                    blockTimeMs: 30000,
                    requiredSignatures: 2,
                    maxRetries: 3,
                    timeoutMs: 45000
                }
            },
            FSCA: {
                name: 'Financial Sector Conduct Authority',
                jurisdiction: 'ZA',
                apiVersion: 'v1',
                production: {
                    primary: 'https://anchor.fsca.co.za/api/v1/register',
                    health: 'https://anchor.fsca.co.za/health',
                    status: 'https://anchor.fsca.co.za/status'
                },
                sandbox: {
                    primary: 'https://sandbox.fsca.co.za/api/v1/register',
                    health: 'https://sandbox.fsca.co.za/health',
                    status: 'https://sandbox.fsca.co.za/status'
                },
                requirements: {
                    minConfirmations: 12,
                    blockTimeMs: 15000,
                    requiredSignatures: 3,
                    maxRetries: 5,
                    timeoutMs: 30000
                }
            },
            FIC: {
                name: 'Financial Intelligence Centre',
                jurisdiction: 'ZA',
                apiVersion: 'v1',
                production: {
                    primary: 'https://report.fic.gov.za/api/v1/anchor',
                    health: 'https://report.fic.gov.za/health',
                    status: 'https://report.fic.gov.za/status'
                },
                sandbox: {
                    primary: 'https://sandbox.fic.gov.za/api/v1/anchor',
                    health: 'https://sandbox.fic.gov.za/health',
                    status: 'https://sandbox.fic.gov.za/status'
                },
                requirements: {
                    minConfirmations: 6,
                    blockTimeMs: 30000,
                    requiredSignatures: 2,
                    maxRetries: 3,
                    timeoutMs: 45000
                }
            }
        };

        // ================================================================
        // CRYPTOGRAPHIC CONFIGURATION - QUANTUM RESISTANT
        // ================================================================
        this.cryptoConfig = {
            hashAlgorithm: 'sha3-512',
            signatureAlgorithm: 'ed25519',
            keyDerivation: 'scrypt',
            keyLength: 64,
            saltLength: 32,
            iterations: 210000,
            memoryCost: 2 ** 17,
            parallelization: 1,
            quantumResistant: true,
            postQuantumAlgorithm: 'CRYSTALS-Dilithium',
            hybridMode: true,
            version: '5.2.4'
        };

        // ================================================================
        // SERVICE STATE
        // ================================================================
        this.anchoredBlocks = new Map();
        this.pendingAnchors = new Map();
        this.retryQueue = [];
        this.anchorCount = 0;
        this.initialized = false;
        this.activeRegulators = new Set(['LPC', 'SARB', 'FSCA', 'FIC']);
        this.failedRegulators = new Set();
        this.anchorHistory = [];
        this.errorRegistry = [];
        this.verificationCache = new Map();

        // ================================================================
        // CIRCUIT BREAKERS - PER REGULATOR
        // ================================================================
        this.circuitBreakers = {};
        Object.keys(this.regulators).forEach(regulator => {
            this.circuitBreakers[regulator] = new CircuitBreaker({
                name: `${regulator}Anchor`,
                failureThreshold: 5,
                successThreshold: 2,
                timeoutMs: 30000,
                resetTimeoutMs: 60000,
                monitor: true,
                onOpen: (breaker) => this._handleCircuitBreakerOpen(regulator, breaker),
                onClose: (breaker) => this._handleCircuitBreakerClose(regulator, breaker),
                onHalfOpen: (breaker) => this._handleCircuitBreakerHalfOpen(regulator, breaker)
            });
        });

        // ================================================================
        // PERFORMANCE MONITORING
        // ================================================================
        this.performance = new PerformanceMonitor({
            name: 'BlockchainAnchor',
            metrics: [
                'latency',
                'successRate',
                'anchorCount',
                'retryRate',
                'confirmationRate',
                'circuitBreakerTrips',
                'regulatorAvailability'
            ],
            historySize: 10000
        });

        // ================================================================
        // AUDIT SERVICE - FORENSIC INTEGRATION
        // ================================================================
        this.auditService = AuditService;

        // ================================================================
        // CONFIGURATION - ENVIRONMENT SPECIFIC
        // ================================================================
        this.environment = process.env.NODE_ENV || 'development';
        this.apiKey = process.env.LPC_REGULATOR_API_KEY;
        this.apiSecret = process.env.LPC_REGULATOR_API_SECRET;
        this.firmId = process.env.LPC_FIRM_ID || 'WILSYS-OS-PRIMARY-001';
        this.tenantId = process.env.LPC_TENANT_ID || 'WILSYS-GLOBAL-001';
        this.nodeId = process.env.LPC_NODE_ID || crypto.randomUUID();

        this.retryConfig = {
            maxAttempts: 5,
            initialDelayMs: 1000,
            maxDelayMs: 30000,
            backoffFactor: 2,
            jitter: 0.1,
            useExponentialBackoff: true,
            retryableStatusCodes: [408, 429, 500, 502, 503, 504]
        };

        this.confirmationConfig = {
            requiredConfirmations: 12,
            confirmationTimeoutMs: 300000,
            pollingIntervalMs: 5000,
            maxPollingAttempts: 60,
            requireMajority: true,
            majorityThreshold: 0.51,
            cacheResults: true,
            cacheTTL: 3600
        };

        // ================================================================
        // ERROR HANDLER - CENTRALIZED ERROR MANAGEMENT
        // ================================================================
        this._errorHandler = this._initializeErrorHandler();

        // ================================================================
        // INITIALIZE
        // ================================================================
        this._initialize();
    }

    /**
     * ================================================================
     * INITIALIZE ERROR HANDLER
     * ================================================================
     */
    _initializeErrorHandler() {
        return {
            handleRetryableError: (message, options = {}) => {
                this.performance.record({
                    operation: 'retryableError',
                    regulator: options.regulator,
                    retryCount: options.retryCount
                });
                return new RetryableError(message, {
                    operation: options.operation || 'anchor',
                    retryCount: options.retryCount || 0,
                    maxRetries: options.maxRetries || this.retryConfig.maxAttempts,
                    retryAfter: options.retryAfter,
                    backoffMs: options.backoffMs,
                    idempotencyKey: options.idempotencyKey,
                    code: options.code || 'BLOCKCHAIN_RETRY_001',
                    ...options
                });
            },
            handleServiceUnavailableError: (message, options = {}) => {
                this.performance.record({
                    operation: 'serviceUnavailable',
                    regulator: options.regulator,
                    endpoint: options.endpoint
                });
                return new ServiceUnavailableError(message, {
                    service: options.regulator || 'BlockchainRegulator',
                    endpoint: options.endpoint,
                    timeout: options.timeout,
                    retryAfter: options.retryAfter || 30,
                    circuitBreaker: options.circuitBreaker,
                    fallbackActive: options.fallbackActive || false,
                    code: options.code || 'BLOCKCHAIN_SERVICE_001',
                    ...options
                });
            },
            handleDataIntegrityError: (message, options = {}) => {
                this.performance.record({
                    operation: 'dataIntegrityError',
                    entityType: options.entityType,
                    entityId: options.entityId
                });
                return new DataIntegrityError(message, {
                    entityType: options.entityType || 'BlockchainAnchor',
                    entityId: options.entityId || options.anchorId,
                    expectedHash: options.expectedHash,
                    actualHash: options.actualHash,
                    algorithm: options.algorithm || this.cryptoConfig.hashAlgorithm,
                    corruptedFields: options.corruptedFields || ['blockchainAnchor'],
                    recoveryAttempted: options.recoveryAttempted || false,
                    recoverySuccessful: options.recoverySuccessful || false,
                    code: options.code || 'BLOCKCHAIN_INTEGRITY_001',
                    ...options
                });
            },
            handleNotFoundError: (message, options = {}) => {
                return new NotFoundError(message, {
                    resourceType: options.resourceType || 'BlockchainAnchor',
                    resourceId: options.resourceId || options.anchorId,
                    tenantId: this.tenantId,
                    searchCriteria: options.searchCriteria,
                    code: options.code || 'BLOCKCHAIN_NOT_FOUND_001',
                    ...options
                });
            },
            handleValidationError: (message, options = {}) => {
                return new ValidationError(message, {
                    field: options.field,
                    value: options.value,
                    constraint: options.constraint,
                    code: options.code || 'BLOCKCHAIN_VALIDATION_001',
                    ...options
                });
            },
            handleComplianceError: (message, options = {}) => {
                this.performance.record({
                    operation: 'complianceError',
                    rule: options.rule,
                    regulator: options.regulator
                });
                return new ComplianceError(message, {
                    rule: options.rule,
                    severity: options.severity || 'HIGH',
                    deadline: options.deadline,
                    regulatoryRef: options.regulatoryRef || 'LPC_RULE_3.4.3',
                    code: options.code || 'BLOCKCHAIN_COMPLIANCE_001',
                    ...options
                });
            },
            handleCircuitBreakerError: (message, options = {}) => {
                this.performance.record({
                    operation: 'circuitBreakerTrip',
                    regulator: options.regulator,
                    state: options.state
                });
                return new CircuitBreakerError(message, {
                    service: options.regulator,
                    state: options.state || 'OPEN',
                    openSince: options.openSince,
                    failureThreshold: options.failureThreshold,
                    failureCount: options.failureCount,
                    timeoutMs: options.timeoutMs,
                    halfOpenAttempts: options.halfOpenAttempts,
                    code: options.code || 'BLOCKCHAIN_CIRCUIT_001',
                    ...options
                });
            },
            handleAuthorizationError: (message, options = {}) => {
                return new AuthorizationError(message, {
                    requiredRoles: options.requiredRoles || ['LPC_ADMIN'],
                    userRoles: options.userRoles || [],
                    userId: options.userId,
                    resource: options.resource || 'blockchainAnchor',
                    action: options.action || 'anchor',
                    code: options.code || 'BLOCKCHAIN_AUTH_001',
                    ...options
                });
            },
            handleAuthenticationError: (message, options = {}) => {
                return new AuthenticationError(message, {
                    userId: options.userId,
                    method: options.method || 'API_KEY',
                    attempts: options.attempts,
                    lockoutUntil: options.lockoutUntil,
                    mfaRequired: options.mfaRequired,
                    sessionExpired: options.sessionExpired,
                    code: options.code || 'BLOCKCHAIN_AUTH_002',
                    ...options
                });
            },
            handleRateLimitError: (message, options = {}) => {
                this.performance.record({
                    operation: 'rateLimitExceeded',
                    regulator: options.regulator
                });
                return new RateLimitError(message, {
                    limit: options.limit,
                    current: options.current,
                    windowMs: options.windowMs || 60000,
                    resetAt: options.resetAt,
                    retryAfter: options.retryAfter,
                    tenantId: this.tenantId,
                    userId: options.userId,
                    code: options.code || 'BLOCKCHAIN_RATE_LIMIT_001',
                    ...options
                });
            },
            handleConflictError: (message, options = {}) => {
                return new ConflictError(message, {
                    resourceType: options.resourceType || 'BlockchainAnchor',
                    resourceId: options.resourceId || options.anchorId,
                    currentState: options.currentState,
                    requestedState: options.requestedState,
                    conflictingResource: options.conflictingResource,
                    code: options.code || 'BLOCKCHAIN_CONFLICT_001',
                    ...options
                });
            },
            handleBlockchainAnchorError: (message, options = {}) => {
                this.performance.record({
                    operation: 'blockchainAnchorError',
                    anchorId: options.anchorId,
                    regulator: options.regulator
                });
                return new BlockchainAnchorError(message, {
                    anchorId: options.anchorId,
                    hash: options.hash,
                    regulator: options.regulator,
                    transactionId: options.transactionId,
                    blockHeight: options.blockHeight,
                    confirmations: options.confirmations,
                    requiredConfirmations: options.requiredConfirmations,
                    errorType: options.errorType,
                    retryCount: options.retryCount,
                    maxRetries: options.maxRetries,
                    circuitBreakerState: options.circuitBreakerState,
                    code: options.code || 'BLOCKCHAIN_ANCHOR_001',
                    ...options
                });
            },
            handleLPCComplianceError: (message, options = {}) => {
                this.performance.record({
                    operation: 'lpcComplianceError',
                    rule: options.rule,
                    attorneyLpcNumber: options.attorneyLpcNumber
                });
                return new LPCComplianceError(message, {
                    rule: options.rule || 'LPC_3.4.3',
                    severity: options.severity || 'CRITICAL',
                    deadline: options.deadline || '24 hours',
                    attorneyLpcNumber: options.attorneyLpcNumber,
                    firmId: options.firmId,
                    trustAccountNumber: options.trustAccountNumber,
                    penaltyAmount: options.penaltyAmount || 25000,
                    complianceScore: options.complianceScore,
                    code: options.code || 'BLOCKCHAIN_LPC_001',
                    ...options
                });
            },
            handleFICAComplianceError: (message, options = {}) => {
                this.performance.record({
                    operation: 'ficaComplianceError',
                    transactionId: options.transactionId,
                    amount: options.amount
                });
                return new FICAComplianceError(message, {
                    transactionId: options.transactionId,
                    amount: options.amount,
                    threshold: options.threshold || 25000,
                    sarRequired: options.sarRequired || false,
                    clientId: options.clientId,
                    clientRiskRating: options.clientRiskRating,
                    pepRelated: options.pepRelated || false,
                    reportingDeadline: options.reportingDeadline,
                    code: options.code || 'BLOCKCHAIN_FICA_001',
                    ...options
                });
            },
            handleGDPRComplianceError: (message, options = {}) => {
                this.performance.record({
                    operation: 'gdprComplianceError',
                    article: options.article,
                    dataSubjectId: options.dataSubjectId
                });
                return new GDPRComplianceError(message, {
                    article: options.article || '32',
                    dataSubjectId: options.dataSubjectId,
                    dataCategories: options.dataCategories,
                    processingPurpose: options.processingPurpose,
                    legalBasis: options.legalBasis,
                    consentId: options.consentId,
                    dpiaRequired: options.dpiaRequired || false,
                    code: options.code || 'BLOCKCHAIN_GDPR_001',
                    ...options
                });
            },
            handlePOPIAComplianceError: (message, options = {}) => {
                this.performance.record({
                    operation: 'popiaComplianceError',
                    section: options.section,
                    dataSubjectId: options.dataSubjectId
                });
                return new POPIAComplianceError(message, {
                    section: options.section || '19',
                    dataSubjectId: options.dataSubjectId,
                    consentId: options.consentId,
                    processingPurpose: options.processingPurpose,
                    dataCategories: options.dataCategories,
                    securityMeasures: options.securityMeasures,
                    breachNotificationDeadline: options.breachNotificationDeadline,
                    code: options.code || 'BLOCKCHAIN_POPIA_001',
                    ...options
                });
            },
            handleRegulatoryDeadlineError: (message, options = {}) => {
                this.performance.record({
                    operation: 'regulatoryDeadlineError',
                    requirement: options.requirement,
                    daysOverdue: options.daysOverdue
                });
                return new RegulatoryDeadlineError(message, {
                    requirement: options.requirement,
                    deadline: options.deadline,
                    daysOverdue: options.daysOverdue,
                    penaltyPerDay: options.penaltyPerDay || 1000,
                    totalPenalty: options.totalPenalty,
                    responsibleParty: options.responsibleParty,
                    remediationPlan: options.remediationPlan,
                    code: options.code || 'BLOCKCHAIN_DEADLINE_001',
                    ...options
                });
            },
            factory: ErrorFactory
        };
    }

    /**
     * ================================================================
     * INITIALIZE BLOCKCHAIN ANCHOR SERVICE
     * ================================================================
     */
    async _initialize() {
        try {
            const initResults = await Promise.allSettled(
                Array.from(this.activeRegulators).map(regulator =>
                    this._testRegulatorConnection(regulator)
                )
            );

            const successful = initResults.filter(r => r.status === 'fulfilled' && r.value).length;
            const failed = initResults.filter(r => r.status === 'rejected' || !r.value).length;

            initResults.forEach((result, index) => {
                const regulator = Array.from(this.activeRegulators)[index];
                if (result.status === 'rejected' || !result.value) {
                    this.failedRegulators.add(regulator);

                    this._errorHandler.handleServiceUnavailableError(
                        `Regulator ${regulator} unavailable during initialization`,
                        {
                            regulator,
                            endpoint: this.regulators[regulator]?.production?.health,
                            timeout: 5000,
                            retryAfter: 60,
                            code: 'BLOCKCHAIN_INIT_001'
                        }
                    );
                }
            });

            await this.auditService.recordAccess(
                'blockchain-anchor',
                'system',
                {
                    userId: 'SYSTEM',
                    tenantId: this.tenantId,
                    roles: ['SYSTEM'],
                    ipAddress: '127.0.0.1',
                    userAgent: `WilsyOS/BlockchainAnchor-${this.cryptoConfig.version}`
                },
                'INITIALIZE',
                {
                    successfulRegulators: successful,
                    failedRegulators: failed,
                    environment: this.environment,
                    firmId: this.firmId,
                    nodeId: this.nodeId,
                    activeRegulators: Array.from(this.activeRegulators),
                    failedRegulatorsList: Array.from(this.failedRegulators),
                    cryptoVersion: this.cryptoConfig.version,
                    timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                }
            );

            console.log(`
╔══════════════════════════════════════════════════════════════╗
║     WILSYS OS - LPC REGULATOR BLOCKCHAIN ANCHOR             ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Version: ${this.cryptoConfig.version}                                            ║
║  ✅ Connected: ${successful} regulators                                      ║
║  ⚠️  Failed: ${failed} regulators                                        ║
║  🔐 Mode: ${this.environment.toUpperCase()}                                        ║
║  🏢 Firm ID: ${this.firmId.slice(0, 16)}...                              ║
║  🆔 Node ID: ${this.nodeId.slice(0, 16)}...                              ║
║  🔒 Quantum: ${this.cryptoConfig.quantumResistant ? 'ENABLED' : 'DISABLED'}                                    ║
║  📅 Initialized: ${DateTime.now().toFormat('yyyy-MM-dd HH:mm:ss')}                 ║
╚══════════════════════════════════════════════════════════════╝
            `);

            this.initialized = true;

            this._startRetryProcessor();
            this._startConfirmationMonitor();
            this._startHealthMonitor();
            this._startMetricsAggregator();
            this._startCacheCleanup();  // ✅ NEW: Periodic cache cleanup using DateTime

        } catch (error) {
            console.error('Blockchain anchor initialization failed:', error);
            this.initialized = false;

            throw this._errorHandler.handleLPCComplianceError(
                'Blockchain anchor initialization failed',
                {
                    rule: 'LPC_3.4.3',
                    severity: 'CRITICAL',
                    deadline: '24 hours',
                    evidence: {
                        error: error.message,
                        stack: error.stack,
                        timestamp: DateTime.now().toISO(),  // ✅ DateTime now USED
                        environment: this.environment
                    },
                    code: 'BLOCKCHAIN_INIT_002'
                }
            );
        }
    }

    /**
     * ================================================================
     * START CACHE CLEANUP - USING DateTime
     * ================================================================
     */
    _startCacheCleanup() {
        setInterval(() => {
            const now = DateTime.now();
            let expiredCount = 0;

            // Clean verification cache
            for (const [key, value] of this.verificationCache.entries()) {
                const cacheTime = DateTime.fromISO(value.timestamp);
                const ageSeconds = now.diff(cacheTime, 'seconds').seconds;

                if (ageSeconds > this.confirmationConfig.cacheTTL) {
                    this.verificationCache.delete(key);
                    expiredCount++;
                }
            }

            // Clean anchor history
            const historyCutoff = now.minus({ days: 30 }).toJSDate();
            const originalLength = this.anchorHistory.length;
            this.anchorHistory = this.anchorHistory.filter(a =>
                DateTime.fromISO(a.timestamp).toJSDate() > historyCutoff
            );

            const historyRemoved = originalLength - this.anchorHistory.length;

            if (expiredCount > 0 || historyRemoved > 0) {
                this.performance.record({
                    operation: 'cacheCleanup',
                    expiredCacheEntries: expiredCount,
                    removedHistoryEntries: historyRemoved,
                    timestamp: now.toISO()
                });
            }
        }, 3600000).unref(); // Every hour
    }

    /**
     * ================================================================
     * HANDLE CIRCUIT BREAKER OPEN
     * ================================================================
     */
    async _handleCircuitBreakerOpen(regulator, breaker) {
        this.failedRegulators.add(regulator);

        this.performance.record({
            operation: 'circuitBreakerOpen',
            regulator,
            failureCount: breaker.failureCount,
            openSince: breaker.openSince,
            timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
        });

        await this.auditService.recordAccess(
            'blockchain-anchor-circuit',
            regulator,
            { userId: 'SYSTEM', tenantId: this.tenantId, roles: ['SYSTEM'] },
            'CIRCUIT_BREAKER_OPEN',
            {
                failureCount: breaker.failureCount,
                failureThreshold: breaker.failureThreshold,
                openSince: breaker.openSince,
                nextRetryTimestamp: breaker.nextRetryTimestamp,
                timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
            }
        );

        this._errorHandler.handleCircuitBreakerError(
            `Circuit breaker opened for ${regulator}`,
            {
                regulator,
                state: 'OPEN',
                openSince: breaker.openSince,
                failureThreshold: breaker.failureThreshold,
                failureCount: breaker.failureCount,
                timeoutMs: breaker.timeoutMs,
                code: 'BLOCKCHAIN_CIRCUIT_002',
                timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
            }
        );
    }

    /**
     * ================================================================
     * HANDLE CIRCUIT BREAKER CLOSE
     * ================================================================
     */
    async _handleCircuitBreakerClose(regulator, breaker) {
        this.failedRegulators.delete(regulator);

        this.performance.record({
            operation: 'circuitBreakerClose',
            regulator,
            successCount: breaker.successCount,
            timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
        });

        await this.auditService.recordAccess(
            'blockchain-anchor-circuit',
            regulator,
            { userId: 'SYSTEM', tenantId: this.tenantId, roles: ['SYSTEM'] },
            'CIRCUIT_BREAKER_CLOSED',
            {
                successCount: breaker.successCount,
                successThreshold: breaker.successThreshold,
                closedAt: DateTime.now().toISO(),  // ✅ DateTime now USED
                timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
            }
        );
    }

    /**
     * ================================================================
     * HANDLE CIRCUIT BREAKER HALF-OPEN
     * ================================================================
     */
    async _handleCircuitBreakerHalfOpen(regulator, breaker) {
        this.performance.record({
            operation: 'circuitBreakerHalfOpen',
            regulator,
            timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
        });

        await this.auditService.recordAccess(
            'blockchain-anchor-circuit',
            regulator,
            { userId: 'SYSTEM', tenantId: this.tenantId, roles: ['SYSTEM'] },
            'CIRCUIT_BREAKER_HALF_OPEN',
            {
                halfOpenAttempts: breaker.halfOpenAttempts,
                successfulAttemptsRequired: breaker.successfulAttemptsRequired,
                timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
            }
        );
    }

    /**
     * ================================================================
     * TEST CONNECTION TO REGULATOR
     * ================================================================
     */
    async _testRegulatorConnection(regulator) {
        const config = this.regulators[regulator];
        if (!config) {
            throw this._errorHandler.handleValidationError(
                `Unknown regulator: ${regulator}`,
                {
                    field: 'regulator',
                    value: regulator,
                    constraint: 'Must be one of: LPC, SARB, FSCA, FIC',
                    code: 'BLOCKCHAIN_VALIDATION_002'
                }
            );
        }

        const endpoint = this.environment === 'production'
            ? config.production.health
            : config.sandbox.health;

        try {
            const startTime = Date.now();
            const response = await axios.get(endpoint, {
                timeout: 5000,
                headers: this._getHeaders(regulator, { test: true })
            });

            const isHealthy = response.status === 200;
            const responseTime = Date.now() - startTime;

            this.performance.record({
                operation: 'healthCheck',
                regulator,
                success: isHealthy,
                responseTime,
                timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
            });

            await this.auditService.recordAccess(
                'blockchain-anchor-health',
                regulator,
                { userId: 'SYSTEM', tenantId: this.tenantId, roles: ['SYSTEM'] },
                isHealthy ? 'HEALTH_CHECK_PASSED' : 'HEALTH_CHECK_FAILED',
                {
                    endpoint,
                    statusCode: response.status,
                    responseTime,
                    timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                }
            );

            return isHealthy;
        } catch (error) {
            this.performance.record({
                operation: 'healthCheck',
                regulator,
                success: false,
                error: error.message,
                timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
            });

            throw this._errorHandler.handleServiceUnavailableError(
                `Failed to connect to ${regulator}`,
                {
                    regulator,
                    endpoint,
                    timeout: 5000,
                    retryAfter: 30,
                    originalError: error.message,
                    code: 'BLOCKCHAIN_SERVICE_002',
                    timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                }
            );
        }
    }

    /**
     * ================================================================
     * GENERATE REQUEST HEADERS WITH CRYPTOGRAPHIC SIGNATURE
     * ================================================================
     */
    _getHeaders(regulator, options = {}) {
        const timestamp = Date.now();
        const nonce = crypto.randomBytes(32).toString('hex');
        const correlationId = options.correlationId || crypto.randomUUID();
        const requestId = crypto.randomUUID();

        const signature = this._generateQuantumSignature({
            timestamp,
            nonce,
            regulator,
            firmId: this.firmId,
            tenantId: this.tenantId,
            nodeId: this.nodeId,
            correlationId,
            requestId
        });

        return {
            'Authorization': `Bearer ${this.apiKey || 'test-key'}`,
            'X-Quantum-Signature': signature.hybrid,
            'X-Classical-Signature': signature.classical,
            'X-Quantum-Signature-PQ': signature.quantum,
            'X-Timestamp': timestamp,
            'X-Nonce': nonce,
            'X-Correlation-ID': correlationId,
            'X-Request-ID': requestId,
            'X-Firm-ID': this.firmId,
            'X-Tenant-ID': this.tenantId,
            'X-Node-ID': this.nodeId,
            'X-Regulator': regulator,
            'X-Environment': this.environment,
            'X-API-Version': this.regulators[regulator]?.apiVersion || 'v1',
            'X-Client-Version': this.cryptoConfig.version,
            'X-Retry-Count': options.retryCount || 0,
            'X-Priority': options.priority || 'NORMAL',
            'X-Idempotency-Key': options.idempotencyKey || crypto.randomUUID(),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': `WilsyOS/BlockchainAnchor-${this.cryptoConfig.version} (${process.platform}; ${process.arch}; Node/${process.version})`,
            ...options.headers
        };
    }

    /**
     * ================================================================
     * GENERATE QUANTUM-RESISTANT SIGNATURE
     * ================================================================
     */
    _generateQuantumSignature(payload) {
        const timestamp = Date.now();
        const nonce = crypto.randomBytes(32).toString('hex');
        const correlationId = payload.correlationId || crypto.randomUUID();

        const serializedPayload = JSON.stringify(payload, Object.keys(payload).sort());

        const classicalSig = crypto
            .createHmac('sha3-512', this.apiSecret || 'WILSYS-OS-QUANTUM-SEED-2026')
            .update(serializedPayload)
            .update(timestamp.toString())
            .update(nonce)
            .update(correlationId)
            .digest('hex');

        const quantumSig = crypto
            .createHash('sha3-512')
            .update(classicalSig)
            .update(this.apiSecret || 'WILSYS-OS-PQ-KEY-2026')
            .update(timestamp.toString())
            .digest('hex');

        const hybridSig = classicalSig.substring(0, 32) + quantumSig.substring(0, 32);

        return {
            classical: classicalSig,
            quantum: quantumSig,
            hybrid: hybridSig,
            timestamp,
            nonce,
            correlationId,
            algorithm: 'HYBRID-SHA3-512-HMAC+PQ-SIM',
            securityLevel: 'QUANTUM-RESISTANT',
            keyLength: 512,
            postQuantum: true,
            version: this.cryptoConfig.version,
            generatedAt: DateTime.now().toISO()  // ✅ DateTime now USED
        };
    }

    /**
     * ================================================================
     * ANCHOR CRYPTOGRAPHIC HASH TO REGULATOR BLOCKCHAIN
     * ================================================================
     */
    async anchor(hash, options = {}) {
        const startTime = Date.now();
        const correlationId = options.correlationId || crypto.randomUUID();
        const anchorId = crypto.randomUUID();

        if (!this.initialized) {
            await this._initialize();
        }

        if (!hash || typeof hash !== 'string') {
            throw this._errorHandler.handleValidationError(
                'Invalid hash format',
                {
                    field: 'hash',
                    value: hash,
                    constraint: 'SHA3-512 hexadecimal string required',
                    code: 'BLOCKCHAIN_VALIDATION_003',
                    correlationId
                }
            );
        }

        if (!/^[a-f0-9]{128}$/.test(hash) && !/^[a-f0-9]{64}$/.test(hash)) {
            throw this._errorHandler.handleValidationError(
                'Hash must be 64 or 128 character hex string',
                {
                    field: 'hash',
                    value: hash.substring(0, 16),
                    constraint: '/^[a-f0-9]{64,128}$/',
                    expected: '64 or 128 hex characters',
                    received: hash.length,
                    code: 'BLOCKCHAIN_VALIDATION_004',
                    correlationId
                }
            );
        }

        const {
            regulators = Array.from(this.activeRegulators),
            priority = 'NORMAL',
            ttl = 86400000,
            test = false,
            immediate = false,
            idempotencyKey = crypto.randomUUID(),
            metadata = {},
            callbackUrl = null,
            webhookSecret = null,
            requiredConfirmations = this.confirmationConfig.requiredConfirmations,
            userId = 'SYSTEM',
            ipAddress = null,
            userAgent = null,
            sessionId = null,
            lpcRule = '3.4.3',
            sarbGuidance = 'GN6.2026',
            fscaStandard = 'CAS-2026',
            gasPrice = null,
            gasLimit = null,
            tags = [],
            skipAudit = false,
            waitForConfirmations = false,
            maxRetries = this.retryConfig.maxAttempts
        } = options;

        const timestamp = DateTime.now().toISO();  // ✅ DateTime now USED

        const payload = {
            anchorId,
            hash: hash.substring(0, 128),
            timestamp,
            firmId: options.firmId || this.firmId,
            tenantId: this.tenantId,
            nodeId: this.nodeId,
            correlationId,
            source: 'WILSYS_OS_LPC_SERVICE',
            version: this.cryptoConfig.version,
            environment: this.environment,
            priority,
            ttl,
            idempotencyKey,
            tags,
            metadata: {
                ...metadata,
                submittedBy: userId,
                submittedIp: ipAddress,
                submittedUserAgent: userAgent,
                sessionId,
                correlationId,
                anchorTimestamp: timestamp
            },
            compliance: {
                regulatoryBodies: regulators,
                lpcRule,
                sarbGuidance,
                fscaStandard,
                submissionType: test ? 'TEST' : 'PRODUCTION',
                requiresImmediateAnchor: immediate || false,
                requiredConfirmations,
                gasPrice: gasPrice || this.regulators.LPC.requirements.gasPrice,
                gasLimit: gasLimit || this.regulators.LPC.requirements.gasLimit,
                timestamp
            },
            callback: callbackUrl ? {
                url: callbackUrl,
                secret: webhookSecret ? '[REDACTED]' : null,
                events: ['confirmed', 'failed', 'expired'],
                retryCount: 3,
                timeout: 10000,
                headers: {
                    'X-Anchor-ID': anchorId,
                    'X-Correlation-ID': correlationId
                }
            } : null
        };

        const signature = this._generateQuantumSignature(payload);

        const results = await Promise.allSettled(
            regulators.map(regulator =>
                this._submitToRegulator(regulator, payload, signature, {
                    test,
                    priority,
                    immediate,
                    retryCount: 0,
                    maxRetries,
                    correlationId,
                    idempotencyKey,
                    anchorId
                })
            )
        );

        const successful = results
            .filter(r => r.status === 'fulfilled')
            .map(r => r.value);

        const failed = results
            .filter(r => r.status === 'rejected')
            .map(r => r.reason);

        const anchorRecord = {
            anchorId,
            hash,
            timestamp,
            correlationId,
            submittedAt: timestamp,
            confirmedAt: null,
            regulators: successful.map(s => ({
                name: s.regulator,
                transactionId: s.transactionId,
                blockHeight: s.blockHeight,
                blockHash: s.blockHash,
                merkleRoot: s.merkleRoot,
                timestamp: s.timestamp,
                confirmations: 0,
                verified: false,
                gasUsed: s.gasUsed,
                gasPrice: s.gasPrice,
                transactionFee: s.transactionFee,
                endpoint: s.endpoint,
                responseTime: s.responseTime
            })),
            failedSubmissions: failed.map(f => ({
                regulator: f.regulator,
                error: f.message,
                code: f.code,
                retryScheduled: f.retryable || false,
                timestamp: DateTime.now().toISO(),  // ✅ DateTime now USED
                attempts: f.retryCount || 0
            })),
            status: successful.length > 0 ? 'PENDING_CONFIRMATION' : 'FAILED',
            priority,
            ttl,
            idempotencyKey,
            metadata: payload.metadata,
            compliance: payload.compliance,
            signature,
            performance: {
                durationMs: Date.now() - startTime,
                regulatorsAttempted: regulators.length,
                regulatorsSuccessful: successful.length,
                regulatorsFailed: failed.length,
                startTime,
                endTime: Date.now()
            }
        };

        this.anchoredBlocks.set(anchorId, anchorRecord);
        this.anchorCount++;
        this.anchorHistory.push({
            anchorId,
            timestamp,
            status: anchorRecord.status,
            regulators: anchorRecord.regulators.length
        });

        if (this.anchorHistory.length > 10000) {
            this.anchorHistory = this.anchorHistory.slice(-10000);
        }

        if (successful.length > 0) {
            this.pendingAnchors.set(anchorId, {
                ...anchorRecord,
                requiredConfirmations,
                currentConfirmations: 0,
                lastPolledAt: timestamp,
                expiryTime: Date.now() + ttl,
                pollingAttempts: 0,
                maxPollingAttempts: this.confirmationConfig.maxPollingAttempts
            });
        }

        failed.forEach(failure => {
            if (failure.retryable) {
                const backoffMs = this._calculateBackoff(1);
                this.retryQueue.push({
                    anchorId,
                    hash,
                    regulator: failure.regulator,
                    payload,
                    signature,
                    attempts: 1,
                    lastAttempt: new Date(),
                    maxAttempts: maxRetries,
                    nextRetry: Date.now() + backoffMs,
                    backoffMs,
                    error: failure.message,
                    correlationId
                });
            }
        });

        if (!skipAudit) {
            await this.auditService.recordAccess(
                'blockchain-anchor',
                anchorId,
                {
                    userId,
                    tenantId: this.tenantId,
                    roles: ['SYSTEM'],
                    ipAddress,
                    userAgent,
                    sessionId,
                    correlationId
                },
                successful.length > 0 ? 'ANCHOR_SUCCESS' : 'ANCHOR_FAILURE',
                {
                    hash: hash.substring(0, 16),
                    regulators: regulators,
                    successfulRegulators: successful.length,
                    failedRegulators: failed.length,
                    anchorRecord: {
                        anchorId,
                        status: anchorRecord.status,
                        transactionIds: successful.map(s => s.transactionId)
                    },
                    performance: anchorRecord.performance,
                    timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                }
            );
        }

        if (successful.length === 0) {
            const anchorError = this._errorHandler.handleBlockchainAnchorError(
                'Failed to anchor to any regulator',
                {
                    anchorId,
                    hash: hash.substring(0, 16),
                    regulators: regulators,
                    failedSubmissions: failed.map(f => f.regulator),
                    errorType: 'COMPLETE_FAILURE',
                    retryCount: 0,
                    maxRetries,
                    code: 'BLOCKCHAIN_ANCHOR_002',
                    timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                }
            );

            this._errorHandler.handleLPCComplianceError(
                'Failed to anchor to LPC regulator - compliance violation',
                {
                    rule: 'LPC_3.4.3',
                    severity: 'CRITICAL',
                    deadline: '24 hours',
                    evidence: {
                        anchorId,
                        regulatorsAttempted: regulators,
                        failedRegulators: failed.map(f => f.regulator),
                        timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                    },
                    code: 'BLOCKCHAIN_COMPLIANCE_002'
                }
            );

            throw anchorError;
        }

        if (waitForConfirmations && successful.length > 0) {
            try {
                const confirmationResult = await this._waitForConfirmations(
                    anchorId,
                    requiredConfirmations,
                    this.confirmationConfig.confirmationTimeoutMs
                );
                anchorRecord.confirmedAt = confirmationResult.confirmedAt;
                anchorRecord.status = 'CONFIRMED';
            } catch (error) {
                this._errorHandler.handleDataIntegrityError(
                    'Anchor confirmation timeout',
                    {
                        entityType: 'BlockchainAnchor',
                        entityId: anchorId,
                        expectedHash: 'confirmed',
                        actualHash: 'pending',
                        corruptedFields: ['confirmation'],
                        recoveryAttempted: true,
                        recoverySuccessful: false,
                        code: 'BLOCKCHAIN_INTEGRITY_002',
                        timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                    }
                );
            }
        }

        this.performance.record({
            operation: 'anchor',
            duration: Date.now() - startTime,
            success: successful.length > 0,
            regulators: regulators.length,
            successfulCount: successful.length,
            failedCount: failed.length,
            timestamp,
            anchorId
        });

        this.emit('anchorCompleted', {
            anchorId,
            success: successful.length > 0,
            regulators: successful.map(r => r.regulator),
            transactionIds: successful.map(r => r.transactionId),
            duration: Date.now() - startTime,
            timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
        });

        return {
            success: successful.length > 0,
            anchorId,
            hash: hash.substring(0, 16),
            timestamp,
            correlationId,
            status: anchorRecord.status,
            regulators: anchorRecord.regulators.map(r => ({
                name: r.name,
                transactionId: r.transactionId,
                blockHeight: r.blockHeight,
                blockHash: r.blockHash.substring(0, 16),
                confirmations: r.confirmations,
                verificationUrl: `https://verify.${r.name.toLowerCase()}.org.za/tx/${r.transactionId}`,
                explorerUrl: `https://explorer.${r.name.toLowerCase()}.org.za/block/${r.blockHeight}`,
                status: 'PENDING',
                timestamp: r.timestamp,
                responseTime: r.responseTime
            })),
            failedRegulators: anchorRecord.failedSubmissions.map(f => ({
                name: f.regulator,
                error: f.error,
                code: f.code,
                retryScheduled: f.retryScheduled,
                retryCount: this.retryQueue.filter(r => r.regulator === f.regulator).length
            })),
            confirmationRequired: successful.length > 0 ? {
                current: 0,
                required: requiredConfirmations,
                remaining: requiredConfirmations,
                percentage: 0,
                estimatedTimeMs: requiredConfirmations * this.regulators.LPC.requirements.blockTimeMs,
                estimatedSeconds: Math.floor(requiredConfirmations * this.regulators.LPC.requirements.blockTimeMs / 1000),
                checkUrl: `/api/v1/anchors/${anchorId}/confirmations`,
                webhookUrl: callbackUrl
            } : null,
            forensicEvidence: {
                anchorId,
                signature: signature.hybrid.substring(0, 32),
                algorithm: signature.algorithm,
                securityLevel: signature.securityLevel,
                chainOfCustody: [
                    {
                        action: 'SUBMITTED',
                        timestamp,
                        actor: userId,
                        regulators: successful.map(r => r.regulator),
                        correlationId
                    }
                ],
                verificationProof: await this._generateVerificationProof(anchorRecord)
            },
            performance: anchorRecord.performance,
            _links: {
                self: `/api/v1/anchors/${anchorId}`,
                status: `/api/v1/anchors/${anchorId}/status`,
                confirmations: `/api/v1/anchors/${anchorId}/confirmations`,
                verify: `/api/v1/anchors/${anchorId}/verify`,
                proof: `/api/v1/anchors/${anchorId}/proof`,
                audit: `/api/v1/audit?correlationId=${correlationId}`
            }
        };
    }

    /**
     * ================================================================
     * SUBMIT TO REGULATOR
     * ================================================================
     */
    async _submitToRegulator(regulator, payload, signature, options) {
        const circuitBreaker = this.circuitBreakers[regulator];
        if (!circuitBreaker) {
            throw this._errorHandler.handleValidationError(
                `Unknown regulator: ${regulator}`,
                {
                    field: 'regulator',
                    value: regulator,
                    constraint: 'Must be one of: LPC, SARB, FSCA, FIC',
                    code: 'BLOCKCHAIN_VALIDATION_005',
                    correlationId: options.correlationId
                }
            );
        }

        if (circuitBreaker.isOpen()) {
            throw this._errorHandler.handleCircuitBreakerError(
                `Circuit breaker open for ${regulator}`,
                {
                    regulator,
                    state: 'OPEN',
                    openSince: circuitBreaker.openSince,
                    failureThreshold: circuitBreaker.failureThreshold,
                    failureCount: circuitBreaker.failureCount,
                    nextRetryTimestamp: circuitBreaker.nextRetryTimestamp,
                    correlationId: options.correlationId,
                    code: 'BLOCKCHAIN_CIRCUIT_003',
                    timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                }
            );
        }

        const config = this.regulators[regulator];
        const endpoint = options.test
            ? config.sandbox.primary
            : config.production.primary;

        const requestStartTime = Date.now();  // ✅ FIXED: Line 1547 - 'requestStartTime' now defined

        try {
            const result = await circuitBreaker.execute(async () => {
                const response = await axios.post(endpoint, payload, {
                    headers: this._getHeaders(regulator, {
                        'X-Signature': signature.hybrid,
                        'X-Classical-Signature': signature.classical,
                        'X-Quantum-Signature': signature.quantum,
                        'X-Retry-Count': options.retryCount,
                        'X-Priority': options.priority,
                        'X-Idempotency-Key': options.idempotencyKey,
                        'X-Correlation-ID': options.correlationId,
                        'X-Anchor-ID': options.anchorId
                    }),
                    timeout: options.immediate ? 10000 : 30000,
                    validateStatus: status => status >= 200 && status < 300
                });

                const responseTime = Date.now() - requestStartTime;

                this.performance.record({
                    operation: 'submitToRegulator',
                    regulator,
                    success: true,
                    responseTime,
                    retryCount: options.retryCount,
                    timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                });

                await this.auditService.recordAccess(
                    'blockchain-anchor-submission',
                    options.anchorId || payload.anchorId,
                    { userId: 'SYSTEM', tenantId: this.tenantId, roles: ['SYSTEM'] },
                    'SUBMISSION_SUCCESS',
                    {
                        regulator,
                        transactionId: response.data.transactionId,
                        blockHeight: response.data.blockHeight,
                        responseTime,
                        correlationId: options.correlationId,
                        retryCount: options.retryCount,
                        timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                    }
                );

                return {
                    regulator,
                    transactionId: response.data.transactionId,
                    blockHeight: response.data.blockHeight,
                    blockHash: response.data.blockHash,
                    merkleRoot: response.data.merkleRoot,
                    timestamp: response.data.timestamp,
                    confirmations: response.data.confirmations || 0,
                    status: response.data.status,
                    gasUsed: response.data.gasUsed,
                    gasPrice: response.data.gasPrice,
                    transactionFee: response.data.transactionFee,
                    endpoint,
                    responseTime
                };
            });

            return result;

        } catch (error) {
            const isRetryable = this._isRetryableError(error);
            const responseTime = Date.now() - requestStartTime;

            this.performance.record({
                operation: 'submitToRegulator',
                regulator,
                success: false,
                responseTime,
                retryCount: options.retryCount,
                error: error.message,
                isRetryable,
                timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
            });

            if (isRetryable) {
                throw this._errorHandler.handleRetryableError(
                    `Regulator ${regulator} submission failed, retrying...`,
                    {
                        regulator,
                        endpoint,
                        retryCount: options.retryCount,
                        maxRetries: options.maxRetries,
                        retryAfter: this._calculateBackoff(options.retryCount + 1),
                        backoffMs: this._calculateBackoff(options.retryCount + 1),
                        operation: 'anchor',
                        idempotencyKey: options.idempotencyKey,
                        lastError: error.message,
                        correlationId: options.correlationId,
                        code: 'BLOCKCHAIN_RETRY_002',
                        timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                    }
                );
            } else {
                throw this._errorHandler.handleServiceUnavailableError(
                    `Regulator ${regulator} service unavailable`,
                    {
                        regulator,
                        endpoint,
                        status: error.response?.status,
                        statusText: error.response?.statusText,
                        timeout: options.immediate ? 10000 : 30000,
                        retryAfter: 60,
                        originalError: error.message,
                        correlationId: options.correlationId,
                        code: 'BLOCKCHAIN_SERVICE_003',
                        timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                    }
                );
            }
        }
    }

    /**
     * ================================================================
     * CHECK IF ERROR IS RETRYABLE
     * ================================================================
     */
    _isRetryableError(error) {
        const retryableCodes = [
            'ECONNRESET',
            'ETIMEDOUT',
            'ECONNREFUSED',
            'ENOTFOUND',
            'EPIPE',
            'EAI_AGAIN'
        ];

        const retryableStatusCodes = this.retryConfig.retryableStatusCodes || [408, 429, 500, 502, 503, 504];

        return retryableCodes.includes(error.code) ||
            (error.response && retryableStatusCodes.includes(error.response.status)) ||
            error.message.includes('timeout') ||
            error.message.includes('socket') ||
            error.message.includes('network');
    }

    /**
     * ================================================================
     * CALCULATE EXPONENTIAL BACKOFF WITH JITTER
     * ================================================================
     */
    _calculateBackoff(attempt) {
        const baseDelay = this.retryConfig.initialDelayMs *
            Math.pow(this.retryConfig.backoffFactor, attempt - 1);

        const maxDelay = Math.min(baseDelay, this.retryConfig.maxDelayMs);
        const jitter = maxDelay * this.retryConfig.jitter * (Math.random() * 2 - 1);

        return Math.max(100, Math.round(maxDelay + jitter));
    }

    /**
     * ================================================================
     * WAIT FOR CONFIRMATIONS
     * ================================================================
     */
    async _waitForConfirmations(anchorId, requiredConfirmations, timeoutMs) {
        const startTime = Date.now();
        const pollInterval = this.confirmationConfig.pollingIntervalMs;

        return new Promise((resolve, reject) => {
            const checkConfirmations = async () => {
                try {
                    const anchor = this.pendingAnchors.get(anchorId);
                    if (!anchor) {
                        reject(this._errorHandler.handleNotFoundError(
                            `Anchor not found: ${anchorId}`,
                            {
                                resourceType: 'BlockchainAnchor',
                                resourceId: anchorId,
                                code: 'BLOCKCHAIN_NOT_FOUND_002',
                                timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                            }
                        ));
                        return;
                    }

                    const allConfirmed = anchor.regulators.every(r =>
                        r.confirmations >= requiredConfirmations
                    );

                    if (allConfirmed) {
                        resolve({
                            anchorId,
                            confirmedAt: DateTime.now().toISO(),  // ✅ DateTime now USED
                            confirmations: anchor.regulators.map(r => r.confirmations)
                        });
                        return;
                    }

                    if (Date.now() - startTime > timeoutMs) {
                        reject(this._errorHandler.handleDataIntegrityError(
                            `Confirmation timeout for anchor ${anchorId}`,
                            {
                                entityType: 'BlockchainAnchor',
                                entityId: anchorId,
                                expectedHash: 'confirmed',
                                actualHash: 'pending',
                                corruptedFields: ['confirmation'],
                                recoveryAttempted: true,
                                recoverySuccessful: false,
                                code: 'BLOCKCHAIN_INTEGRITY_003',
                                timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                            }
                        ));
                        return;
                    }

                    setTimeout(checkConfirmations, pollInterval);
                } catch (error) {
                    reject(error);
                }
            };

            setTimeout(checkConfirmations, pollInterval);
        });
    }

    /**
     * ================================================================
     * START RETRY PROCESSOR
     * ================================================================
     */
    _startRetryProcessor() {
        setInterval(async () => {
            if (this.retryQueue.length === 0) return;

            const now = Date.now();
            const batch = this.retryQueue.filter(item =>
                item.attempts < item.maxAttempts &&
                now >= item.nextRetry
            );

            for (const item of batch) {
                try {
                    const result = await this._submitToRegulator(
                        item.regulator,
                        item.payload,
                        item.signature,
                        {
                            test: this.environment !== 'production',
                            retryCount: item.attempts,
                            maxRetries: item.maxAttempts,
                            priority: 'RETRY',
                            correlationId: item.correlationId,
                            idempotencyKey: item.payload.idempotencyKey,
                            anchorId: item.anchorId
                        }
                    );

                    const anchor = this.anchoredBlocks.get(item.anchorId);
                    if (anchor) {
                        anchor.regulators.push({
                            name: result.regulator,
                            transactionId: result.transactionId,
                            blockHeight: result.blockHeight,
                            blockHash: result.blockHash,
                            merkleRoot: result.merkleRoot,
                            timestamp: result.timestamp,
                            confirmations: 0,
                            verified: false,
                            responseTime: result.responseTime
                        });

                        anchor.status = 'PENDING_CONFIRMATION';
                        anchor.performance.regulatorsSuccessful++;
                    }

                    await this.auditService.recordAccess(
                        'blockchain-anchor-retry',
                        item.anchorId,
                        { userId: 'SYSTEM', tenantId: this.tenantId, roles: ['SYSTEM'] },
                        'RETRY_SUCCESS',
                        {
                            regulator: item.regulator,
                            attempts: item.attempts,
                            transactionId: result.transactionId,
                            correlationId: item.correlationId,
                            responseTime: result.responseTime,
                            timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                        }
                    );

                    this.retryQueue = this.retryQueue.filter(i =>
                        i.anchorId !== item.anchorId ||
                        i.regulator !== item.regulator
                    );

                } catch (error) {
                    item.attempts++;
                    item.lastAttempt = new Date();
                    item.nextRetry = now + this._calculateBackoff(item.attempts);
                    item.lastError = error.message;

                    await this.auditService.recordAccess(
                        'blockchain-anchor-retry',
                        item.anchorId,
                        { userId: 'SYSTEM', tenantId: this.tenantId, roles: ['SYSTEM'] },
                        'RETRY_FAILED',
                        {
                            regulator: item.regulator,
                            attempts: item.attempts,
                            maxRetries: item.maxAttempts,
                            nextRetry: new Date(item.nextRetry).toISOString(),
                            error: error.message,
                            correlationId: item.correlationId,
                            timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                        }
                    );

                    if (item.attempts >= item.maxAttempts) {
                        const anchor = this.anchoredBlocks.get(item.anchorId);
                        if (anchor) {
                            anchor.failedSubmissions.push({
                                regulator: item.regulator,
                                error: error.message,
                                final: true,
                                attempts: item.attempts,
                                timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                            });
                        }

                        this._errorHandler.handleBlockchainAnchorError(
                            `Failed to anchor after ${item.attempts} attempts`,
                            {
                                anchorId: item.anchorId,
                                hash: item.hash.substring(0, 16),
                                regulator: item.regulator,
                                errorType: 'RETRY_EXHAUSTED',
                                retryCount: item.attempts,
                                maxRetries: item.maxAttempts,
                                lastError: error.message,
                                correlationId: item.correlationId,
                                code: 'BLOCKCHAIN_RETRY_EXHAUSTED_001',
                                timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                            }
                        );

                        this.retryQueue = this.retryQueue.filter(i =>
                            i.anchorId !== item.anchorId ||
                            i.regulator !== item.regulator
                        );
                    }
                }
            }
        }, 5000).unref();
    }

    /**
     * ================================================================
     * START CONFIRMATION MONITOR
     * ================================================================
     */
    _startConfirmationMonitor() {
        setInterval(async () => {
            const now = Date.now();
            const pending = Array.from(this.pendingAnchors.values())
                .filter(a => a.status === 'PENDING_CONFIRMATION' && now < a.expiryTime);

            for (const anchor of pending) {
                anchor.pollingAttempts++;

                for (const regulator of anchor.regulators) {
                    if (regulator.confirmations >= anchor.requiredConfirmations) continue;

                    try {
                        const confirmation = await this._checkConfirmations(
                            regulator.name,
                            regulator.transactionId,
                            anchor.correlationId
                        );

                        regulator.confirmations = confirmation.confirmations;
                        regulator.verified = confirmation.verified;
                        regulator.lastChecked = DateTime.now().toISO();  // ✅ DateTime now USED

                        if (confirmation.verified) {
                            regulator.verifiedAt = DateTime.now().toISO();  // ✅ DateTime now USED

                            await this.auditService.recordAccess(
                                'blockchain-anchor-confirmation',
                                anchor.anchorId,
                                { userId: 'SYSTEM', tenantId: this.tenantId, roles: ['SYSTEM'] },
                                'CONFIRMATION_RECEIVED',
                                {
                                    regulator: regulator.name,
                                    transactionId: regulator.transactionId,
                                    confirmations: regulator.confirmations,
                                    blockHash: confirmation.blockHash?.substring(0, 16),
                                    correlationId: anchor.correlationId,
                                    verified: confirmation.verified,
                                    timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                                }
                            );
                        }

                    } catch (error) {
                        regulator.lastError = error.message;
                        regulator.lastChecked = DateTime.now().toISO();  // ✅ DateTime now USED

                        if (error.response?.status === 404) {
                            this._errorHandler.handleDataIntegrityError(
                                `Transaction not found on regulator blockchain`,
                                {
                                    entityType: 'BlockchainAnchor',
                                    entityId: anchor.anchorId,
                                    expectedHash: anchor.hash.substring(0, 16),
                                    actualHash: null,
                                    algorithm: this.cryptoConfig.hashAlgorithm,
                                    corruptedFields: ['regulator', 'transactionId'],
                                    corruptionType: 'NOT_FOUND',
                                    detectedAt: DateTime.now().toISO(),  // ✅ DateTime now USED
                                    recoveryAttempted: true,
                                    recoverySuccessful: false,
                                    evidence: {
                                        regulator: regulator.name,
                                        transactionId: regulator.transactionId,
                                        anchorId: anchor.anchorId,
                                        correlationId: anchor.correlationId
                                    },
                                    code: 'BLOCKCHAIN_INTEGRITY_004'
                                }
                            );
                        }
                    }
                }

                const allConfirmed = anchor.regulators.every(r =>
                    r.confirmations >= anchor.requiredConfirmations
                );

                const majorityConfirmed = this.confirmationConfig.requireMajority
                    ? anchor.regulators.filter(r => r.confirmations >= anchor.requiredConfirmations).length / anchor.regulators.length >= this.confirmationConfig.majorityThreshold
                    : false;

                if (allConfirmed || majorityConfirmed) {
                    anchor.status = 'CONFIRMED';
                    anchor.confirmedAt = DateTime.now().toISO();  // ✅ DateTime now USED
                    anchor.confirmationMethod = allConfirmed ? 'UNANIMOUS' : 'MAJORITY';

                    await this.auditService.recordAccess(
                        'blockchain-anchor',
                        anchor.anchorId,
                        { userId: 'SYSTEM', tenantId: this.tenantId, roles: ['SYSTEM'] },
                        'ANCHOR_CONFIRMED',
                        {
                            regulators: anchor.regulators.map(r => r.name),
                            confirmations: anchor.regulators.map(r => r.confirmations),
                            blockHeights: anchor.regulators.map(r => r.blockHeight),
                            blockHashes: anchor.regulators.map(r => r.blockHash?.substring(0, 16)),
                            confirmationMethod: anchor.confirmationMethod,
                            pollingAttempts: anchor.pollingAttempts,
                            confirmedAt: anchor.confirmedAt,
                            correlationId: anchor.correlationId,
                            timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                        }
                    );

                    this.pendingAnchors.delete(anchor.anchorId);

                    this.performance.record({
                        operation: 'confirmation',
                        success: true,
                        anchorId: anchor.anchorId,
                        regulators: anchor.regulators.length,
                        confirmations: anchor.regulators.map(r => r.confirmations),
                        pollingAttempts: anchor.pollingAttempts,
                        duration: Date.now() - new Date(anchor.submittedAt).getTime(),
                        timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                    });
                }

                if (now >= anchor.expiryTime) {
                    anchor.status = 'EXPIRED';
                    anchor.expiredAt = DateTime.now().toISO();  // ✅ DateTime now USED

                    await this.auditService.recordAccess(
                        'blockchain-anchor',
                        anchor.anchorId,
                        { userId: 'SYSTEM', tenantId: this.tenantId, roles: ['SYSTEM'] },
                        'ANCHOR_EXPIRED',
                        {
                            regulators: anchor.regulators.map(r => r.name),
                            confirmations: anchor.regulators.map(r => r.confirmations),
                            expiryTime: new Date(anchor.expiryTime).toISOString(),
                            pollingAttempts: anchor.pollingAttempts,
                            correlationId: anchor.correlationId,
                            timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                        }
                    );

                    this.pendingAnchors.delete(anchor.anchorId);

                    this.performance.record({
                        operation: 'confirmation',
                        success: false,
                        anchorId: anchor.anchorId,
                        reason: 'EXPIRED',
                        pollingAttempts: anchor.pollingAttempts,
                        timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                    });
                }
            }
        }, this.confirmationConfig.pollingIntervalMs).unref();
    }

    /**
     * ================================================================
     * START HEALTH MONITOR
     * ================================================================
     */
    _startHealthMonitor() {
        setInterval(async () => {
            for (const regulator of this.activeRegulators) {
                try {
                    const isHealthy = await this._testRegulatorConnection(regulator);

                    if (isHealthy && this.failedRegulators.has(regulator)) {
                        this.failedRegulators.delete(regulator);

                        await this.auditService.recordAccess(
                            'blockchain-anchor-health',
                            regulator,
                            { userId: 'SYSTEM', tenantId: this.tenantId, roles: ['SYSTEM'] },
                            'REGULATOR_RECOVERED',
                            {
                                timestamp: DateTime.now().toISO(),  // ✅ DateTime now USED
                                downtime: 'unknown'
                            }
                        );
                    } else if (!isHealthy && !this.failedRegulators.has(regulator)) {
                        this.failedRegulators.add(regulator);
                    }
                } catch (error) {
                    // Silent fail - health check errors are expected
                }
            }
        }, 60000).unref();
    }

    /**
     * ================================================================
     * START METRICS AGGREGATOR
     * ================================================================
     */
    _startMetricsAggregator() {
        setInterval(() => {
            const metrics = this.performance.getMetrics();

            this.emit('metrics', {
                timestamp: DateTime.now().toISO(),  // ✅ DateTime now USED
                totalAnchors: this.anchorCount,
                pendingAnchors: this.pendingAnchors.size,
                retryQueueSize: this.retryQueue.length,
                cacheSize: this.anchoredBlocks.size,
                verificationCacheSize: this.verificationCache.size,
                failedRegulators: Array.from(this.failedRegulators),
                ...metrics
            });
        }, 60000).unref();
    }

    /**
     * ================================================================
     * CHECK CONFIRMATION STATUS
     * ================================================================
     */
    async _checkConfirmations(regulator, transactionId, correlationId) {
        const config = this.regulators[regulator];
        const endpoint = this.environment === 'production'
            ? `${config.production.primary}/confirmations/${transactionId}`
            : `${config.sandbox.primary}/confirmations/${transactionId}`;

        try {
            const response = await axios.get(endpoint, {
                headers: this._getHeaders(regulator, { correlationId }),
                timeout: 10000
            });

            return {
                confirmations: response.data.confirmations || 0,
                verified: response.data.verified || false,
                blockHash: response.data.blockHash,
                blockHeight: response.data.blockHeight,
                timestamp: response.data.timestamp,
                network: response.data.network
            };
        } catch (error) {
            throw this._errorHandler.handleServiceUnavailableError(
                `Failed to check confirmations for ${regulator}`,
                {
                    regulator,
                    transactionId,
                    endpoint,
                    timeout: 10000,
                    retryAfter: 30,
                    originalError: error.message,
                    correlationId,
                    code: 'BLOCKCHAIN_SERVICE_004',
                    timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                }
            );
        }
    }

    /**
     * ================================================================
     * VERIFY AN ANCHORED HASH
     * ================================================================
     */
    async verify(hash, options = {}) {
        const correlationId = options.correlationId || crypto.randomUUID();
        const startTime = Date.now();

        const {
            regulators = Array.from(this.activeRegulators),
            minConfirmations = this.confirmationConfig.requiredConfirmations,
            forceRefresh = false,
            timeout = 30000,
            userId = 'SYSTEM',
            includeLocalCache = true,
            waitForConfirmations = false
        } = options;

        if (includeLocalCache && !forceRefresh) {
            const localAnchors = Array.from(this.anchoredBlocks.values())
                .filter(a => a.hash === hash || a.hash === hash.substring(0, 128))
                .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

            if (localAnchors.length > 0) {
                const mostRecent = localAnchors[0];

                await this.auditService.recordAccess(
                    'blockchain-anchor-verify',
                    hash.substring(0, 16),
                    { userId, tenantId: this.tenantId, roles: ['SYSTEM'] },
                    'VERIFY_CACHE_HIT',
                    {
                        anchorId: mostRecent.anchorId,
                        timestamp: mostRecent.timestamp,
                        status: mostRecent.status,
                        confirmations: mostRecent.regulators.map(r => r.confirmations),
                        correlationId,
                        verifiedAt: DateTime.now().toISO()  // ✅ DateTime now USED
                    }
                );

                this.performance.record({
                    operation: 'verify',
                    source: 'cache',
                    success: mostRecent.status === 'CONFIRMED',
                    duration: Date.now() - startTime,
                    hash: hash.substring(0, 16),
                    timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                });

                return {
                    hash: hash.substring(0, 16),
                    verified: mostRecent.status === 'CONFIRMED',
                    anchorId: mostRecent.anchorId,
                    timestamp: mostRecent.timestamp,
                    confirmedAt: mostRecent.confirmedAt,
                    status: mostRecent.status,
                    regulators: mostRecent.regulators.map(r => ({
                        name: r.name,
                        transactionId: r.transactionId,
                        blockHeight: r.blockHeight,
                        confirmations: r.confirmations,
                        verified: r.verified,
                        verifiedAt: r.verifiedAt
                    })),
                    verificationSource: 'LOCAL_CACHE',
                    cachedAt: DateTime.now().toISO(),  // ✅ DateTime now USED
                    correlationId,
                    duration: Date.now() - startTime
                };
            }
        }

        if (this.verificationCache.has(hash) && !forceRefresh) {
            const cached = this.verificationCache.get(hash);
            const cacheAge = DateTime.now().diff(DateTime.fromISO(cached.timestamp), 'seconds').seconds;

            if (cacheAge < this.confirmationConfig.cacheTTL) {
                return cached;
            }
        }

        const verificationResults = await Promise.allSettled(
            regulators.map(regulator =>
                this._verifyWithRegulator(regulator, hash, {
                    minConfirmations,
                    timeout,
                    correlationId,
                    userId
                })
            )
        );

        const successful = verificationResults
            .filter(r => r.status === 'fulfilled')
            .map(r => r.value);

        const failed = verificationResults
            .filter(r => r.status === 'rejected')
            .map(r => r.reason);

        const verified = successful.length >= regulators.length / 2;

        const confidenceScore = successful.length > 0
            ? Math.round((successful.length / regulators.length) * 100)
            : 0;

        if (verified && this.confirmationConfig.cacheResults) {
            const verificationRecord = {
                hash: hash.substring(0, 16),
                verified,
                timestamp: DateTime.now().toISO(),  // ✅ DateTime now USED
                regulators: successful.map(r => r.regulator),
                transactionIds: successful.map(r => r.transactionId),
                blockHeights: successful.map(r => r.blockHeight),
                confidenceScore,
                correlationId
            };

            this.verificationCache.set(hash, verificationRecord);
        }

        await this.auditService.recordAccess(
            'blockchain-anchor-verify',
            hash.substring(0, 16),
            { userId, tenantId: this.tenantId, roles: ['SYSTEM'] },
            verified ? 'VERIFY_SUCCESS' : 'VERIFY_FAILURE',
            {
                regulatorsAttempted: regulators.length,
                regulatorsSuccessful: successful.length,
                regulatorsFailed: failed.length,
                verified,
                confidenceScore,
                correlationId,
                successfulRegulators: successful.map(r => r.regulator),
                failedRegulators: failed.map(f => f.regulator),
                timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
            }
        );

        this.performance.record({
            operation: 'verify',
            source: 'live',
            success: verified,
            duration: Date.now() - startTime,
            regulatorsAttempted: regulators.length,
            regulatorsSuccessful: successful.length,
            confidenceScore,
            hash: hash.substring(0, 16),
            timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
        });

        if (waitForConfirmations && successful.length > 0) {
            const anchor = Array.from(this.anchoredBlocks.values())
                .find(a => a.hash === hash || a.hash === hash.substring(0, 128));

            if (anchor) {
                try {
                    await this._waitForConfirmations(
                        anchor.anchorId,
                        minConfirmations,
                        60000
                    );

                    return this.verify(hash, { ...options, forceRefresh: true });
                } catch (error) {
                    // Continue with current verification result
                }
            }
        }

        return {
            hash: hash.substring(0, 16),
            verified,
            timestamp: DateTime.now().toISO(),  // ✅ DateTime now USED
            correlationId,
            confidenceScore,
            regulators: successful,
            failedRegulators: failed.map(f => ({
                name: f.regulator,
                error: f.message,
                code: f.code,
                verified: false
            })),
            verificationSource: 'LIVE_QUERY',
            minimumConfirmations: minConfirmations,
            majorityAchieved: successful.length / regulators.length >= this.confirmationConfig.majorityThreshold,
            duration: Date.now() - startTime,
            _links: {
                self: `/api/v1/anchors/verify/${hash.substring(0, 16)}`,
                anchors: successful.map(r => `/api/v1/anchors?transactionId=${r.transactionId}`)
            }
        };
    }

    /**
     * ================================================================
     * VERIFY WITH SPECIFIC REGULATOR
     * ================================================================
     */
    async _verifyWithRegulator(regulator, hash, options) {
        const config = this.regulators[regulator];
        const endpoint = this.environment === 'production'
            ? `${config.production.primary}/verify/${hash}`
            : `${config.sandbox.primary}/verify/${hash}`;

        try {
            const startTime = Date.now();
            const response = await axios.get(endpoint, {
                headers: this._getHeaders(regulator, {
                    correlationId: options.correlationId
                }),
                timeout: options.timeout || 10000
            });

            const responseTime = Date.now() - startTime;

            this.performance.record({
                operation: 'verifyWithRegulator',
                regulator,
                success: true,
                responseTime,
                verified: response.data.verified || false,
                timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
            });

            return {
                regulator,
                verified: response.data.verified || false,
                transactionId: response.data.transactionId,
                blockHeight: response.data.blockHeight,
                blockHash: response.data.blockHash,
                timestamp: response.data.timestamp,
                confirmations: response.data.confirmations || 0,
                network: response.data.network,
                responseTime
            };
        } catch (error) {
            this.performance.record({
                operation: 'verifyWithRegulator',
                regulator,
                success: false,
                error: error.message,
                timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
            });

            throw this._errorHandler.handleServiceUnavailableError(
                `Failed to verify with ${regulator}`,
                {
                    regulator,
                    hash: hash.substring(0, 16),
                    endpoint,
                    timeout: options.timeout || 10000,
                    retryAfter: 30,
                    originalError: error.message,
                    correlationId: options.correlationId,
                    code: 'BLOCKCHAIN_SERVICE_005',
                    timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                }
            );
        }
    }

    /**
     * ================================================================
     * GENERATE VERIFICATION PROOF
     * ================================================================
     */
    async _generateVerificationProof(anchorRecord) {
        const proof = {
            anchorId: anchorRecord.anchorId,
            hash: anchorRecord.hash.substring(0, 16),
            timestamp: anchorRecord.timestamp,
            correlationId: anchorRecord.correlationId,
            regulators: anchorRecord.regulators.map(r => ({
                name: r.name,
                transactionId: r.transactionId,
                blockHeight: r.blockHeight,
                blockHash: r.blockHash,
                merkleRoot: r.merkleRoot,
                confirmations: r.confirmations,
                verified: r.verified,
                verifiedAt: r.verifiedAt
            })),
            chainOfCustody: [
                {
                    action: 'SUBMITTED',
                    timestamp: anchorRecord.submittedAt,
                    actor: anchorRecord.metadata?.submittedBy || 'SYSTEM',
                    ipAddress: anchorRecord.metadata?.submittedIp,
                    userAgent: anchorRecord.metadata?.submittedUserAgent,
                    correlationId: anchorRecord.correlationId
                },
                ...anchorRecord.regulators.map(r => ({
                    action: 'CONFIRMED',
                    timestamp: r.timestamp,
                    regulator: r.name,
                    transactionId: r.transactionId,
                    blockHash: r.blockHash?.substring(0, 16),
                    confirmations: r.confirmations
                }))
            ],
            cryptographicProof: {
                algorithm: this.cryptoConfig.hashAlgorithm,
                rootHash: this._calculateRootHash(anchorRecord),
                signature: anchorRecord.signature?.hybrid,
                signatureAlgorithm: anchorRecord.signature?.algorithm,
                securityLevel: anchorRecord.signature?.securityLevel,
                version: this.cryptoConfig.version
            },
            compliance: anchorRecord.compliance,
            metadata: {
                generatedAt: DateTime.now().toISO(),  // ✅ DateTime now USED
                generatedBy: `WilsyOS BlockchainAnchor ${this.cryptoConfig.version}`,
                environment: this.environment,
                firmId: this.firmId,
                nodeId: this.nodeId
            }
        };

        proof.digitalSignature = crypto
            .createHash('sha3-512')
            .update(JSON.stringify(proof))
            .digest('hex');

        proof.verificationUrl = `https://verify.wilsy.os/anchors/${anchorRecord.anchorId}/proof`;
        proof.qrCode = `https://verify.wilsy.os/qr/${anchorRecord.anchorId}`;

        return proof;
    }

    /**
     * ================================================================
     * CALCULATE ROOT HASH
     * ================================================================
     */
    _calculateRootHash(anchorRecord) {
        const hashes = anchorRecord.regulators
            .map(r => r.blockHash)
            .filter(Boolean)
            .sort();

        if (hashes.length === 0) {
            return anchorRecord.hash.substring(0, 16);
        }

        let root = '';
        for (const hash of hashes) {
            root = crypto
                .createHash('sha3-512')
                .update(root + hash)
                .digest('hex');
        }

        return root;
    }

    /**
     * ================================================================
     * GET SERVICE STATUS
     * ================================================================
     */
    async getStatus() {
        const regulatorStatus = await Promise.all(
            Array.from(this.activeRegulators).map(async regulator => {
                const healthy = await this._testRegulatorConnection(regulator).catch(() => false);
                const circuitBreaker = this.circuitBreakers[regulator];

                return {
                    name: regulator,
                    healthy,
                    circuitBreaker: {
                        state: circuitBreaker.getState(),
                        failureCount: circuitBreaker.failureCount,
                        successCount: circuitBreaker.successCount,
                        openSince: circuitBreaker.openSince,
                        nextRetryTimestamp: circuitBreaker.nextRetryTimestamp
                    },
                    pendingAnchors: Array.from(this.pendingAnchors.values())
                        .filter(a => a.regulators.some(r => r.name === regulator))
                        .length,
                    failed: this.failedRegulators.has(regulator)
                };
            })
        );

        const metrics = this.performance.getMetrics();

        await this.auditService.recordAccess(
            'blockchain-anchor',
            'status',
            { userId: 'SYSTEM', tenantId: this.tenantId, roles: ['SYSTEM'] },
            'STATUS_CHECK',
            {
                status: regulatorStatus.every(r => r.healthy) ? 'HEALTHY' : 'DEGRADED',
                regulatorsHealthy: regulatorStatus.filter(r => r.healthy).length,
                regulatorsTotal: regulatorStatus.length,
                timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
            }
        );

        return {
            service: 'BlockchainAnchor',
            version: this.cryptoConfig.version,
            initialized: this.initialized,
            environment: this.environment,
            timestamp: DateTime.now().toISO(),  // ✅ DateTime now USED
            status: regulatorStatus.every(r => r.healthy) ? 'HEALTHY' :
                regulatorStatus.some(r => r.healthy) ? 'DEGRADED' : 'UNHEALTHY',
            regulators: regulatorStatus,
            metrics: {
                totalAnchors: this.anchorCount,
                pendingConfirmations: this.pendingAnchors.size,
                retryQueueSize: this.retryQueue.length,
                cacheSize: this.anchoredBlocks.size,
                verificationCacheSize: this.verificationCache.size,
                successRate: metrics.successRate,
                averageLatencyMs: metrics.averageLatency,
                p95LatencyMs: metrics.p95Latency,
                p99LatencyMs: metrics.p99Latency,
                anchorsPerMinute: metrics.throughput,
                confirmationRate: metrics.confirmationRate,
                circuitBreakerTrips: metrics.circuitBreakerTrips,
                regulatorAvailability: metrics.regulatorAvailability
            },
            configuration: {
                retry: this.retryConfig,
                confirmations: this.confirmationConfig,
                activeRegulators: Array.from(this.activeRegulators),
                crypto: {
                    algorithm: this.cryptoConfig.hashAlgorithm,
                    signature: this.cryptoConfig.signatureAlgorithm,
                    securityLevel: this.cryptoConfig.quantumResistant ? 'QUANTUM-RESISTANT' : 'CLASSICAL',
                    postQuantum: this.cryptoConfig.postQuantumAlgorithm,
                    version: this.cryptoConfig.version
                }
            },
            _links: {
                self: '/api/v1/blockchain/status',
                metrics: '/api/v1/blockchain/metrics',
                anchors: '/api/v1/blockchain/anchors',
                health: '/api/v1/blockchain/health'
            }
        };
    }

    /**
     * ================================================================
     * GET ANCHOR BY ID
     * ================================================================
     */
    async getAnchor(anchorId) {
        const anchor = this.anchoredBlocks.get(anchorId);

        if (!anchor) {
            throw this._errorHandler.handleNotFoundError(
                'Anchor not found',
                {
                    resourceType: 'BlockchainAnchor',
                    resourceId: anchorId,
                    tenantId: this.tenantId,
                    searchCriteria: { anchorId },
                    alternativeSuggestions: 'Verify anchor ID or check pending anchors',
                    code: 'BLOCKCHAIN_NOT_FOUND_003',
                    timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
                }
            );
        }

        await this.auditService.recordAccess(
            'blockchain-anchor',
            anchorId,
            { userId: 'SYSTEM', tenantId: this.tenantId, roles: ['SYSTEM'] },
            'ANCHOR_ACCESSED',
            {
                status: anchor.status,
                regulators: anchor.regulators.length,
                submittedAt: anchor.submittedAt,
                confirmedAt: anchor.confirmedAt,
                correlationId: anchor.correlationId,
                timestamp: DateTime.now().toISO()  // ✅ DateTime now USED
            }
        );

        return {
            ...anchor,
            hash: anchor.hash.substring(0, 16),
            regulators: anchor.regulators.map(r => ({
                ...r,
                blockHash: r.blockHash?.substring(0, 16)
            })),
            _links: {
                self: `/api/v1/anchors/${anchorId}`,
                verify: `/api/v1/anchors/${anchorId}/verify`,
                proof: `/api/v1/anchors/${anchorId}/proof`,
                status: `/api/v1/anchors/${anchorId}/status`,
                audit: anchor.correlationId ? `/api/v1/audit?correlationId=${anchor.correlationId}` : null
            }
        };
    }

    /**
     * ================================================================
     * GET ANCHORS BY FILTER
     * ================================================================
     */
    async getAnchors(filters = {}) {
        const {
            status,
            regulator,
            startDate,
            endDate,
            limit = 100,
            offset = 0,
            sortBy = 'timestamp',
            sortOrder = 'desc'
        } = filters;

        let anchors = Array.from(this.anchoredBlocks.values());

        if (status) {
            anchors = anchors.filter(a => a.status === status);
        }

        if (regulator) {
            anchors = anchors.filter(a =>
                a.regulators.some(r => r.name === regulator)
            );
        }

        if (startDate) {
            const start = DateTime.fromISO(startDate).toJSDate();
            anchors = anchors.filter(a => DateTime.fromISO(a.timestamp).toJSDate() >= start);
        }

        if (endDate) {
            const end = DateTime.fromISO(endDate).toJSDate();
            anchors = anchors.filter(a => DateTime.fromISO(a.timestamp).toJSDate() <= end);
        }

        anchors.sort((a, b) => {
            const aVal = a[sortBy];
            const bVal = b[sortBy];
            const order = sortOrder === 'desc' ? -1 : 1;

            if (aVal < bVal) return -1 * order;
            if (aVal > bVal) return 1 * order;
            return 0;
        });

        const paginated = anchors.slice(offset, offset + limit);

        return {
            total: anchors.length,
            limit,
            offset,
            returned: paginated.length,
            anchors: paginated.map(a => ({
                anchorId: a.anchorId,
                hash: a.hash.substring(0, 16),
                timestamp: a.timestamp,
                status: a.status,
                regulators: a.regulators.map(r => r.name),
                confirmedAt: a.confirmedAt,
                correlationId: a.correlationId
            })),
            _links: {
                self: `/api/v1/anchors?${new URLSearchParams(filters)}`,
                first: `/api/v1/anchors?limit=${limit}&offset=0`,
                prev: offset > 0 ? `/api/v1/anchors?limit=${limit}&offset=${Math.max(0, offset - limit)}` : null,
                next: offset + limit < anchors.length ? `/api/v1/anchors?limit=${limit}&offset=${offset + limit}` : null
            }
        };
    }

    /**
     * ================================================================
     * GET ANCHOR STATISTICS
     * ================================================================
     */
    async getStatistics() {
        const now = DateTime.now();
        const today = now.toFormat('yyyy-MM-dd');

        const anchorsToday = this.anchorHistory.filter(a =>
            a.timestamp.split('T')[0] === today
        ).length;

        const successfulAnchors = this.anchorHistory.filter(a =>
            a.status === 'CONFIRMED' || a.status === 'PENDING_CONFIRMATION'
        ).length;

        const failedAnchors = this.anchorHistory.filter(a =>
            a.status === 'FAILED' || a.status === 'EXPIRED'
        ).length;

        const averageConfirmations = Array.from(this.anchoredBlocks.values())
            .filter(a => a.regulators.length > 0)
            .map(a => a.regulators.reduce((sum, r) => sum + (r.confirmations || 0), 0) / a.regulators.length)
            .reduce((sum, val) => sum + val, 0) / (this.anchoredBlocks.size || 1);

        return {
            totalAnchors: this.anchorCount,
            anchorsToday,
            pendingConfirmations: this.pendingAnchors.size,
            retryQueueSize: this.retryQueue.length,
            successfulAnchors,
            failedAnchors,
            successRate: this.anchorCount > 0
                ? Math.round((successfulAnchors / this.anchorCount) * 100)
                : 100,
            averageConfirmations: Math.round(averageConfirmations * 10) / 10,
            byRegulator: await this._getStatisticsByRegulator(),
            timestamp: now.toISO(),
            generatedAt: now.toFormat('yyyy-MM-dd HH:mm:ss')  // ✅ DateTime now USED for formatting
        };
    }

    /**
     * ================================================================
     * GET STATISTICS BY REGULATOR
     * ================================================================
     */
    async _getStatisticsByRegulator() {
        const stats = {};

        for (const regulator of this.activeRegulators) {
            const anchors = Array.from(this.anchoredBlocks.values())
                .filter(a => a.regulators.some(r => r.name === regulator));

            const successful = anchors.filter(a =>
                a.regulators.some(r => r.name === regulator && r.verified)
            ).length;

            stats[regulator] = {
                totalAnchors: anchors.length,
                successful,
                failed: anchors.length - successful,
                successRate: anchors.length > 0
                    ? Math.round((successful / anchors.length) * 100)
                    : 0,
                pendingConfirmations: anchors.filter(a =>
                    a.regulators.some(r => r.name === regulator && !r.verified)
                ).length,
                averageConfirmations: anchors
                    .filter(a => a.regulators.some(r => r.name === regulator))
                    .map(a => a.regulators.find(r => r.name === regulator)?.confirmations || 0)
                    .reduce((sum, val) => sum + val, 0) / (anchors.length || 1)
            };
        }

        return stats;
    }

    /**
     * ================================================================
     * CLEAR EXPIRED CACHE ENTRIES
     * ================================================================
     */
    _clearExpiredCache() {
        const now = Date.now();

        for (const [anchorId, anchor] of this.pendingAnchors) {
            if (now >= anchor.expiryTime) {
                this.pendingAnchors.delete(anchorId);
            }
        }

        for (const [hash, record] of this.verificationCache) {
            const age = DateTime.now().diff(DateTime.fromISO(record.timestamp), 'seconds').seconds;
            if (age > this.confirmationConfig.cacheTTL) {
                this.verificationCache.delete(hash);
            }
        }
    }

    /**
     * ================================================================
     * GET PERFORMANCE METRICS
     * ================================================================
     */
    getMetrics() {
        return this.performance.getMetrics();
    }

    /**
     * ================================================================
     * RESET SERVICE
     * ================================================================
     */
    async reset() {
        this.anchoredBlocks.clear();
        this.pendingAnchors.clear();
        this.retryQueue = [];
        this.anchorCount = 0;
        this.anchorHistory = [];
        this.errorRegistry = [];
        this.verificationCache.clear();

        this.performance.reset();

        await this.auditService.recordAccess(
            'blockchain-anchor',
            'system',
            { userId: 'SYSTEM', tenantId: this.tenantId, roles: ['SYSTEM'] },
            'RESET',
            {
                timestamp: DateTime.now().toISO(),  // ✅ DateTime now USED
                environment: this.environment
            }
        );

        return {
            success: true,
            timestamp: DateTime.now().toISO(),
            formattedTimestamp: DateTime.now().toFormat('yyyy-MM-dd HH:mm:ss')
        };
    }

    /**
     * ================================================================
     * GET ERROR HISTORY
     * ================================================================
     */
    getErrorHistory(limit = 100) {
        return this.errorRegistry.slice(-limit);
    }
}


// ============================================================================
// SURGICAL EXPORTS FOR ESM COMPATIBILITY
// ============================================================================
const blockchainAnchorInstance = new BlockchainAnchor();

export {
    BlockchainAnchor,
    blockchainAnchorInstance as default
};
