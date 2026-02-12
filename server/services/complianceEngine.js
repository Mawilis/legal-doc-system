/**
 * WILSYS OS - COMPLIANCE ENGINE
 * ====================================================================
 * LPC RULES 3.4, 17.3, 21.1, 35.2, 41.3, 55, 86, 95
 * POPIA SECTIONS 19-22 · GDPR ARTICLES 30-35 · FICA SECTION 28
 * SARB GUIDANCE NOTE 6 · FSCA CRYPTO ASSET STANDARDS
 * 
 * This service provides:
 * - Real-time regulatory compliance validation
 * - Multi-jurisdictional rule enforcement
 * - Automated compliance scoring and certification
 * - Regulatory deadline management
 * - Compliance gap analysis
 * - Remediation workflow automation
 * - Regulatory reporting and analytics
 * 
 * @version 5.2.0
 * @author Wilson Khanyezi - Chief Quantum Sentinel
 * @copyright Wilsy OS (Pty) Ltd 2026
 * ====================================================================
 */

const crypto = require('crypto');
const { EventEmitter } = require('events');
const {
    ValidationError,
    ComplianceError,
    RegulatoryDeadlineError,
    ErrorFactory
} = require('../utils/errors');
const { PerformanceMonitor } = require('../utils/performance');
const { RegulatoryCalendar } = require('../utils/regulatoryCalendar');

/**
 * Compliance Engine
 * Centralized regulatory compliance validation and enforcement
 */
class ComplianceEngine extends EventEmitter {
    constructor() {
        super();

        // ================================================================
        // SERVICE STATE
        // ================================================================
        this.initialized = false;
        this.ruleCache = new Map();
        this.violationRegistry = new Map();
        this.complianceScores = new Map();
        this.certificateRegistry = new Map();

        // ================================================================
        // PERFORMANCE MONITORING
        // ================================================================
        this.performance = new PerformanceMonitor({
            name: 'ComplianceEngine',
            metrics: ['latency', 'validationCount', 'violationRate', 'score']
        });

        // ================================================================
        // REGULATORY CALENDAR
        // ================================================================
        this.regulatoryCalendar = new RegulatoryCalendar();

        // ================================================================
        // LPC RULE DEFINITIONS
        // ================================================================
        this.lpcRules = {
            '3.4.1': {
                name: 'Daily Trust Reconciliation',
                severity: 'CRITICAL',
                deadline: '24 hours',
                penalty: 'R50,000 + suspension',
                statutoryRef: 'Legal Practice Act 2014 s86(3)',
                remediation: 'Perform immediate trust account reconciliation',
                validationFn: this._validateLPC341.bind(this)
            },
            '3.4.2': {
                name: 'Cryptographic Proof',
                severity: 'CRITICAL',
                deadline: 'Immediate',
                penalty: 'R100,000 + criminal charges',
                statutoryRef: 'LPC Rule 3.4.2',
                remediation: 'Generate Merkle proof from transaction hashes',
                validationFn: this._validateLPC342.bind(this)
            },
            '3.4.3': {
                name: 'Regulator Anchoring',
                severity: 'HIGH',
                deadline: '24 hours',
                penalty: 'R25,000',
                statutoryRef: 'LPC Rule 3.4.3',
                remediation: 'Submit anchor to lpc.regulator.gov.za',
                validationFn: this._validateLPC343.bind(this)
            },
            '17.3': {
                name: 'Attorney Profile Access Logging',
                severity: 'CRITICAL',
                deadline: 'Immediate',
                penalty: 'R75,000',
                statutoryRef: 'LPC Rule 17.3',
                remediation: 'Implement comprehensive audit logging',
                validationFn: this._validateLPC173.bind(this)
            },
            '21.1': {
                name: 'Transaction Traceability',
                severity: 'HIGH',
                deadline: '7 days',
                penalty: 'R40,000',
                statutoryRef: 'LPC Rule 21.1',
                remediation: 'Link all transactions to trust accounts',
                validationFn: this._validateLPC211.bind(this)
            },
            '35.2': {
                name: 'Executive Report Access',
                severity: 'CRITICAL',
                deadline: 'Immediate',
                penalty: 'R60,000',
                statutoryRef: 'LPC Rule 35.2',
                remediation: 'Implement role-based access control',
                validationFn: this._validateLPC352.bind(this)
            },
            '41.3': {
                name: 'Metrics Administrator Access',
                severity: 'HIGH',
                deadline: '7 days',
                penalty: 'R30,000',
                statutoryRef: 'LPC Rule 41.3',
                remediation: 'Restrict metrics to LPC_ADMIN role',
                validationFn: this._validateLPC413.bind(this)
            },
            '55.1': {
                name: 'Fidelity Certificate Requirement',
                severity: 'CRITICAL',
                deadline: '30 days',
                penalty: 'R100,000 + practice suspension',
                statutoryRef: 'LPC Rule 55(1)',
                remediation: 'Apply for Fidelity Fund certificate',
                validationFn: this._validateLPC551.bind(this)
            },
            '55.2': {
                name: 'Minimum Contribution',
                severity: 'HIGH',
                deadline: '30 days',
                penalty: 'R25,000',
                statutoryRef: 'LPC Rule 55(2)',
                remediation: 'Pay minimum R500 contribution',
                validationFn: this._validateLPC552.bind(this)
            },
            '55.4': {
                name: 'Certificate Validity',
                severity: 'CRITICAL',
                deadline: 'Immediate',
                penalty: 'R75,000 + practice restrictions',
                statutoryRef: 'LPC Rule 55(4)',
                remediation: 'Renew expired certificate',
                validationFn: this._validateLPC554.bind(this)
            },
            '86.1': {
                name: 'Trust Account Numbering',
                severity: 'CRITICAL',
                deadline: '7 days',
                penalty: 'R50,000',
                statutoryRef: 'LPC Rule 86(1)',
                remediation: 'Assign LPC-compliant account number',
                validationFn: this._validateLPC861.bind(this)
            },
            '86.2': {
                name: 'Positive Balance Requirement',
                severity: 'CRITICAL',
                deadline: '24 hours',
                penalty: 'R200,000 + criminal referral',
                statutoryRef: 'LPC Rule 86(2)',
                remediation: 'Rectify negative balance immediately',
                validationFn: this._validateLPC862.bind(this)
            },
            '86.3': {
                name: 'Client Sub-account Balances',
                severity: 'CRITICAL',
                deadline: '24 hours',
                penalty: 'R150,000',
                statutoryRef: 'LPC Rule 86(3)',
                remediation: 'Rectify all negative client balances',
                validationFn: this._validateLPC863.bind(this)
            },
            '95.3': {
                name: 'Annual Compliance Audit',
                severity: 'HIGH',
                deadline: 'Annual',
                penalty: 'R45,000',
                statutoryRef: 'LPC Rule 95(3)',
                remediation: 'Schedule annual compliance audit',
                validationFn: this._validateLPC953.bind(this)
            }
        };

        // ================================================================
        // POPIA SECTION DEFINITIONS
        // ================================================================
        this.popiaSections = {
            '19': {
                name: 'Security Measures',
                severity: 'CRITICAL',
                deadline: 'Immediate',
                penalty: 'R10,000,000 or 10 years imprisonment',
                statutoryRef: 'POPIA Section 19',
                remediation: 'Implement reasonable security measures',
                validationFn: this._validatePOPIA19.bind(this)
            },
            '20': {
                name: 'Record of Processing',
                severity: 'HIGH',
                deadline: '30 days',
                penalty: 'R5,000,000',
                statutoryRef: 'POPIA Section 20',
                remediation: 'Maintain comprehensive processing records',
                validationFn: this._validatePOPIA20.bind(this)
            },
            '21': {
                name: 'Breach Notification',
                severity: 'CRITICAL',
                deadline: '72 hours',
                penalty: 'R10,000,000',
                statutoryRef: 'POPIA Section 21',
                remediation: 'Notify Regulator and affected data subjects',
                validationFn: this._validatePOPIA21.bind(this)
            },
            '22': {
                name: 'Data Subject Access',
                severity: 'HIGH',
                deadline: '30 days',
                penalty: 'R5,000,000',
                statutoryRef: 'POPIA Section 22',
                remediation: 'Respond to access request',
                validationFn: this._validatePOPIA22.bind(this)
            }
        };

        // ================================================================
        // GDPR ARTICLE DEFINITIONS
        // ================================================================
        this.gdprArticles = {
            '30': {
                name: 'Records of Processing',
                severity: 'HIGH',
                deadline: 'Ongoing',
                penalty: '€10,000,000 or 2% global turnover',
                statutoryRef: 'GDPR Article 30',
                remediation: 'Maintain processing records',
                validationFn: this._validateGDPR30.bind(this)
            },
            '32': {
                name: 'Security of Processing',
                severity: 'CRITICAL',
                deadline: 'Immediate',
                penalty: '€20,000,000 or 4% global turnover',
                statutoryRef: 'GDPR Article 32',
                remediation: 'Implement appropriate technical measures',
                validationFn: this._validateGDPR32.bind(this)
            },
            '33': {
                name: 'Breach Notification',
                severity: 'CRITICAL',
                deadline: '72 hours',
                penalty: '€20,000,000 or 4% global turnover',
                statutoryRef: 'GDPR Article 33',
                remediation: 'Notify supervisory authority',
                validationFn: this._validateGDPR33.bind(this)
            },
            '35': {
                name: 'Data Protection Impact Assessment',
                severity: 'HIGH',
                deadline: 'Pre-processing',
                penalty: '€10,000,000 or 2% global turnover',
                statutoryRef: 'GDPR Article 35',
                remediation: 'Conduct DPIA for high-risk processing',
                validationFn: this._validateGDPR35.bind(this)
            }
        };

        // ================================================================
        // FICA SECTION DEFINITIONS
        // ================================================================
        this.ficaSections = {
            '28': {
                name: 'Transaction Monitoring',
                severity: 'HIGH',
                deadline: 'Immediate',
                penalty: 'R50,000,000',
                statutoryRef: 'FICA Section 28',
                remediation: 'Monitor and report suspicious transactions',
                validationFn: this._validateFICA28.bind(this)
            },
            '29': {
                name: 'Suspicious Activity Reporting',
                severity: 'CRITICAL',
                deadline: '15 days',
                penalty: 'R100,000,000',
                statutoryRef: 'FICA Section 29',
                remediation: 'Submit SAR to FIC',
                validationFn: this._validateFICA29.bind(this)
            }
        };

        // ================================================================
        // SARB GUIDANCE DEFINITIONS
        // ================================================================
        this.sarbGuidance = {
            'GN6.2026': {
                name: 'Trust Account Verification',
                severity: 'HIGH',
                deadline: '7 days',
                penalty: 'R1,000,000',
                statutoryRef: 'SARB Guidance Note 6',
                remediation: 'Verify trust account with bank',
                validationFn: this._validateSARBGN6.bind(this)
            }
        };

        // ================================================================
        // INITIALIZE
        // ================================================================
        this._initialize();
    }

    /**
     * Initialize compliance engine
     */
    async _initialize() {
        try {
            // Load rule cache
            await this._loadRuleCache();

            // Start deadline monitor
            this._startDeadlineMonitor();

            this.initialized = true;

            console.log(`
╔══════════════════════════════════════════════════════════════╗
║     WILSYS OS - COMPLIANCE ENGINE                           ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ Initialized: ${new Date().toISOString()}                         ║
║  ⚖️  LPC Rules: ${Object.keys(this.lpcRules).length}                                        ║
║  🔒 POPIA Sections: ${Object.keys(this.popiaSections).length}                                      ║
║  🇪🇺 GDPR Articles: ${Object.keys(this.gdprArticles).length}                                      ║
║  💰 FICA Sections: ${Object.keys(this.ficaSections).length}                                      ║
║  🏦 SARB Guidance: ${Object.keys(this.sarbGuidance).length}                                      ║
╚══════════════════════════════════════════════════════════════╝
            `);

        } catch (error) {
            console.error('Compliance engine initialization failed:', error);
            this.initialized = false;
        }
    }

    /**
     * Load rule cache
     */
    async _loadRuleCache() {
        // Load LPC rules
        Object.entries(this.lpcRules).forEach(([key, rule]) => {
            this.ruleCache.set(`LPC_${key.replace(/\./g, '_')}`, rule);
        });

        // Load POPIA sections
        Object.entries(this.popiaSections).forEach(([key, section]) => {
            this.ruleCache.set(`POPIA_${key}`, section);
        });

        // Load GDPR articles
        Object.entries(this.gdprArticles).forEach(([key, article]) => {
            this.ruleCache.set(`GDPR_${key}`, article);
        });

        // Load FICA sections
        Object.entries(this.ficaSections).forEach(([key, section]) => {
            this.ruleCache.set(`FICA_${key}`, section);
        });

        // Load SARB guidance
        Object.entries(this.sarbGuidance).forEach(([key, guidance]) => {
            this.ruleCache.set(`SARB_${key}`, guidance);
        });
    }

    /**
     * Start deadline monitor for regulatory deadlines
     */
    _startDeadlineMonitor() {
        setInterval(() => this._checkDeadlines(), 3600000).unref(); // Hourly
    }

    /**
     * Check for upcoming and missed deadlines
     */
    async _checkDeadlines() {
        const now = new Date();
        const upcomingDeadlines = [];
        const missedDeadlines = [];

        for (const [entityId, score] of this.complianceScores) {
            const violations = this.violationRegistry.get(entityId) || [];

            for (const violation of violations) {
                if (violation.deadline) {
                    const deadlineDate = new Date(violation.deadline);
                    const daysUntil = Math.ceil((deadlineDate - now) / (1000 * 60 * 60 * 24));

                    if (daysUntil <= 7 && daysUntil > 0) {
                        upcomingDeadlines.push({
                            ...violation,
                            entityId,
                            daysUntil
                        });
                    }

                    if (deadlineDate < now && violation.status === 'OPEN') {
                        missedDeadlines.push({
                            ...violation,
                            entityId,
                            daysOverdue: Math.abs(daysUntil)
                        });
                    }
                }
            }
        }

        if (upcomingDeadlines.length > 0) {
            this.emit('upcomingDeadlines', upcomingDeadlines);
        }

        if (missedDeadlines.length > 0) {
            this.emit('missedDeadlines', missedDeadlines);

            // Create regulatory deadline errors
            for (const deadline of missedDeadlines) {
                throw new RegulatoryDeadlineError(
                    `Regulatory deadline missed: ${deadline.rule}`,
                    {
                        requirement: deadline.rule,
                        deadline: deadline.deadline,
                        daysOverdue: deadline.daysOverdue,
                        entityId: deadline.entityId,
                        penalty: deadline.penalty,
                        regulatoryRef: deadline.statutoryRef
                    }
                );
            }
        }
    }

    // ================================================================
    // LPC RULE VALIDATIONS
    // ================================================================

    /**
     * LPC RULE 3.4.1 - Daily Trust Reconciliation
     */
    _validateLPC341(block) {
        const violations = [];

        if (!block.reconciliationTimestamp) {
            violations.push({
                rule: 'LPC_3.4.1',
                severity: 'CRITICAL',
                message: 'Missing daily reconciliation timestamp',
                deadline: this._calculateDeadline('24 hours'),
                statutoryRef: this.lpcRules['3.4.1'].statutoryRef,
                penalty: this.lpcRules['3.4.1'].penalty,
                remediation: this.lpcRules['3.4.1'].remediation
            });
        }

        return violations;
    }

    /**
     * LPC RULE 3.4.2 - Cryptographic Proof
     */
    _validateLPC342(block) {
        const violations = [];

        if (!block.merkleRoot) {
            violations.push({
                rule: 'LPC_3.4.2',
                severity: 'CRITICAL',
                message: 'Merkle root required for trust accounting',
                deadline: this._calculateDeadline('immediate'),
                statutoryRef: this.lpcRules['3.4.2'].statutoryRef,
                penalty: this.lpcRules['3.4.2'].penalty,
                remediation: this.lpcRules['3.4.2'].remediation,
                algorithm: 'SHA3-512'
            });
        }

        return violations;
    }

    /**
     * LPC RULE 3.4.3 - Regulator Anchoring
     */
    _validateLPC343(block) {
        const violations = [];

        if (!block.regulatorAnchor) {
            violations.push({
                rule: 'LPC_3.4.3',
                severity: 'HIGH',
                message: 'Block not anchored to LPC regulator node',
                deadline: this._calculateDeadline('24 hours'),
                statutoryRef: this.lpcRules['3.4.3'].statutoryRef,
                penalty: this.lpcRules['3.4.3'].penalty,
                remediation: this.lpcRules['3.4.3'].remediation,
                endpoint: 'https://lpc.regulator.gov.za/api/v1/anchor'
            });
        }

        return violations;
    }

    /**
     * LPC RULE 17.3 - Attorney Profile Access Logging
     */
    _validateLPC173(auditEntry) {
        const violations = [];

        if (!auditEntry) {
            violations.push({
                rule: 'LPC_17.3',
                severity: 'CRITICAL',
                message: 'No audit entry provided for attorney profile access',
                deadline: this._calculateDeadline('immediate'),
                statutoryRef: this.lpcRules['17.3'].statutoryRef,
                penalty: this.lpcRules['17.3'].penalty,
                remediation: this.lpcRules['17.3'].remediation
            });
        }

        if (!auditEntry.userId) {
            violations.push({
                rule: 'LPC_17.3',
                severity: 'CRITICAL',
                message: 'User ID required for attorney profile access logging',
                deadline: this._calculateDeadline('immediate'),
                statutoryRef: this.lpcRules['17.3'].statutoryRef,
                penalty: this.lpcRules['17.3'].penalty,
                remediation: this.lpcRules['17.3'].remediation
            });
        }

        return violations;
    }

    /**
     * LPC RULE 21.1 - Transaction Traceability
     */
    _validateLPC211(transaction) {
        const violations = [];

        if (!transaction.matterId) {
            violations.push({
                rule: 'LPC_21.1',
                severity: 'CRITICAL',
                message: 'Matter ID required for transaction traceability',
                deadline: this._calculateDeadline('7 days'),
                statutoryRef: this.lpcRules['21.1'].statutoryRef,
                penalty: this.lpcRules['21.1'].penalty,
                remediation: this.lpcRules['21.1'].remediation
            });
        }

        return violations;
    }

    /**
     * LPC RULE 35.2 - Executive Report Access
     */
    _validateLPC352(userContext) {
        const violations = [];

        if (!userContext?.roles) {
            violations.push({
                rule: 'LPC_35.2',
                severity: 'CRITICAL',
                message: 'User roles required for access control',
                deadline: this._calculateDeadline('immediate'),
                statutoryRef: this.lpcRules['35.2'].statutoryRef,
                penalty: this.lpcRules['35.2'].penalty,
                remediation: this.lpcRules['35.2'].remediation
            });
        }

        return violations;
    }

    /**
     * LPC RULE 41.3 - Metrics Administrator Access
     */
    _validateLPC413(userContext) {
        const violations = [];

        if (!userContext?.roles?.includes('LPC_ADMIN')) {
            violations.push({
                rule: 'LPC_41.3',
                severity: 'HIGH',
                message: 'LPC Administrator access required for metrics',
                deadline: this._calculateDeadline('7 days'),
                statutoryRef: this.lpcRules['41.3'].statutoryRef,
                penalty: this.lpcRules['41.3'].penalty,
                remediation: this.lpcRules['41.3'].remediation
            });
        }

        return violations;
    }

    /**
     * LPC RULE 55.1 - Fidelity Certificate Requirement
     */
    _validateLPC551(attorney) {
        const violations = [];

        if (!attorney.fidelityFund?.certificateId) {
            violations.push({
                rule: 'LPC_55.1',
                severity: 'CRITICAL',
                message: 'No valid Fidelity Fund certificate',
                deadline: this._calculateDeadline('30 days'),
                statutoryRef: this.lpcRules['55.1'].statutoryRef,
                penalty: this.lpcRules['55.1'].penalty,
                remediation: this.lpcRules['55.1'].remediation
            });
        }

        return violations;
    }

    /**
     * LPC RULE 55.2 - Minimum Contribution
     */
    _validateLPC552(certificate) {
        const violations = [];

        if (certificate.contributionAmount < 500) {
            violations.push({
                rule: 'LPC_55.2',
                severity: 'HIGH',
                message: 'Fidelity Fund contribution below minimum',
                required: 500,
                actual: certificate.contributionAmount,
                deadline: this._calculateDeadline('30 days'),
                statutoryRef: this.lpcRules['55.2'].statutoryRef,
                penalty: this.lpcRules['55.2'].penalty,
                remediation: this.lpcRules['55.2'].remediation
            });
        }

        return violations;
    }

    /**
     * LPC RULE 55.4 - Certificate Validity
     */
    _validateLPC554(certificate) {
        const violations = [];

        if (certificate.expiryDate && new Date(certificate.expiryDate) < new Date()) {
            const daysOverdue = Math.ceil(
                (new Date() - new Date(certificate.expiryDate)) / (1000 * 60 * 60 * 24)
            );

            violations.push({
                rule: 'LPC_55.4',
                severity: 'CRITICAL',
                message: 'Fidelity Fund certificate has expired',
                expiryDate: certificate.expiryDate,
                daysOverdue,
                deadline: this._calculateDeadline('immediate'),
                statutoryRef: this.lpcRules['55.4'].statutoryRef,
                penalty: this.lpcRules['55.4'].penalty,
                remediation: this.lpcRules['55.4'].remediation
            });
        }

        return violations;
    }

    /**
     * LPC RULE 86.1 - Trust Account Numbering
     */
    _validateLPC861(trustAccount) {
        const violations = [];

        if (!trustAccount.accountNumber) {
            violations.push({
                rule: 'LPC_86.1',
                severity: 'CRITICAL',
                message: 'Trust account number required',
                deadline: this._calculateDeadline('7 days'),
                statutoryRef: this.lpcRules['86.1'].statutoryRef,
                penalty: this.lpcRules['86.1'].penalty,
                remediation: this.lpcRules['86.1'].remediation
            });
        }

        return violations;
    }

    /**
     * LPC RULE 86.2 - Positive Balance Requirement
     */
    _validateLPC862(trustAccount) {
        const violations = [];

        if (trustAccount.balances?.current < 0) {
            violations.push({
                rule: 'LPC_86.2',
                severity: 'CRITICAL',
                message: 'Trust account has negative balance',
                balance: trustAccount.balances.current,
                deadline: this._calculateDeadline('24 hours'),
                statutoryRef: this.lpcRules['86.2'].statutoryRef,
                penalty: this.lpcRules['86.2'].penalty,
                remediation: this.lpcRules['86.2'].remediation
            });
        }

        return violations;
    }

    /**
     * LPC RULE 86.3 - Client Sub-account Balances
     */
    _validateLPC863(trustAccount) {
        const violations = [];

        if (trustAccount.clientBalances) {
            const negativeClients = trustAccount.clientBalances.filter(c => c.balance < 0);

            if (negativeClients.length > 0) {
                violations.push({
                    rule: 'LPC_86.3',
                    severity: 'CRITICAL',
                    message: `${negativeClients.length} client sub-accounts have negative balances`,
                    clients: negativeClients.map(c => ({
                        clientId: c.clientId,
                        balance: c.balance,
                        daysNegative: Math.ceil(
                            (new Date() - new Date(c.lastUpdated || Date.now())) / (1000 * 60 * 60 * 24)
                        )
                    })),
                    deadline: this._calculateDeadline('24 hours'),
                    statutoryRef: this.lpcRules['86.3'].statutoryRef,
                    penalty: this.lpcRules['86.3'].penalty,
                    remediation: this.lpcRules['86.3'].remediation
                });
            }
        }

        return violations;
    }

    /**
     * LPC RULE 95.3 - Annual Compliance Audit
     */
    _validateLPC953(audit) {
        const violations = [];

        const oneYearAgo = new Date();
        oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);

        if (!audit.auditDate || new Date(audit.auditDate) < oneYearAgo) {
            violations.push({
                rule: 'LPC_95.3',
                severity: 'HIGH',
                message: 'Compliance audit is overdue',
                lastAuditDate: audit.auditDate,
                deadline: this._calculateDeadline('annual'),
                statutoryRef: this.lpcRules['95.3'].statutoryRef,
                penalty: this.lpcRules['95.3'].penalty,
                remediation: this.lpcRules['95.3'].remediation
            });
        }

        return violations;
    }

    // ================================================================
    // POPIA SECTION VALIDATIONS
    // ================================================================

    /**
     * POPIA SECTION 19 - Security Measures
     */
    _validatePOPIA19(userContext) {
        const violations = [];

        if (!userContext.encrypted && userContext.transportSecurity !== 'TLS1.3') {
            violations.push({
                rule: 'POPIA_19',
                severity: 'CRITICAL',
                message: 'Access must be encrypted (TLS 1.3 required)',
                deadline: this._calculateDeadline('immediate'),
                statutoryRef: this.popiaSections['19'].statutoryRef,
                penalty: this.popiaSections['19'].penalty,
                remediation: this.popiaSections['19'].remediation
            });
        }

        return violations;
    }

    /**
     * POPIA SECTION 20 - Record of Processing
     */
    _validatePOPIA20(auditEntry) {
        const violations = [];

        if (!auditEntry) {
            violations.push({
                rule: 'POPIA_20',
                severity: 'HIGH',
                message: 'Processing record required for POPIA compliance',
                deadline: this._calculateDeadline('30 days'),
                statutoryRef: this.popiaSections['20'].statutoryRef,
                penalty: this.popiaSections['20'].penalty,
                remediation: this.popiaSections['20'].remediation
            });
        }

        return violations;
    }

    /**
     * POPIA SECTION 21 - Breach Notification
     */
    _validatePOPIA21(breach) {
        const violations = [];

        if (!breach.detectedAt) {
            violations.push({
                rule: 'POPIA_21',
                severity: 'CRITICAL',
                message: 'Breach detection timestamp required',
                deadline: this._calculateDeadline('72 hours'),
                statutoryRef: this.popiaSections['21'].statutoryRef,
                penalty: this.popiaSections['21'].penalty,
                remediation: this.popiaSections['21'].remediation
            });
        }

        const notificationDelay = breach.notifiedAt ?
            new Date(breach.notifiedAt) - new Date(breach.detectedAt) : null;

        if (notificationDelay > 72 * 60 * 60 * 1000) {
            violations.push({
                rule: 'POPIA_21',
                severity: 'HIGH',
                message: 'Breach notification exceeds 72-hour requirement',
                delayHours: Math.round(notificationDelay / (60 * 60 * 1000)),
                deadline: this._calculateDeadline('72 hours'),
                statutoryRef: this.popiaSections['21'].statutoryRef,
                penalty: this.popiaSections['21'].penalty,
                remediation: this.popiaSections['21'].remediation
            });
        }

        return violations;
    }

    /**
     * POPIA SECTION 22 - Data Subject Access
     */
    _validatePOPIA22(dsar) {
        const violations = [];

        if (!dsar.requestDate) {
            violations.push({
                rule: 'POPIA_22',
                severity: 'HIGH',
                message: 'DSAR request date required',
                deadline: this._calculateDeadline('30 days'),
                statutoryRef: this.popiaSections['22'].statutoryRef,
                penalty: this.popiaSections['22'].penalty,
                remediation: this.popiaSections['22'].remediation
            });
        }

        const responseDelay = dsar.responseDate ?
            new Date(dsar.responseDate) - new Date(dsar.requestDate) : null;

        if (responseDelay > 30 * 24 * 60 * 60 * 1000) {
            violations.push({
                rule: 'POPIA_22',
                severity: 'HIGH',
                message: 'DSAR response exceeds 30-day requirement',
                delayDays: Math.ceil(responseDelay / (24 * 60 * 60 * 1000)),
                deadline: this._calculateDeadline('30 days'),
                statutoryRef: this.popiaSections['22'].statutoryRef,
                penalty: this.popiaSections['22'].penalty,
                remediation: this.popiaSections['22'].remediation
            });
        }

        return violations;
    }

    // ================================================================
    // GDPR ARTICLE VALIDATIONS
    // ================================================================

    /**
     * GDPR ARTICLE 30 - Records of Processing
     */
    _validateGDPR30(processingRecord) {
        const violations = [];

        if (!processingRecord.controller) {
            violations.push({
                rule: 'GDPR_30',
                severity: 'HIGH',
                message: 'Data controller must be identified',
                deadline: this._calculateDeadline('ongoing'),
                statutoryRef: this.gdprArticles['30'].statutoryRef,
                penalty: this.gdprArticles['30'].penalty,
                remediation: this.gdprArticles['30'].remediation
            });
        }

        if (!processingRecord.purpose) {
            violations.push({
                rule: 'GDPR_30',
                severity: 'HIGH',
                message: 'Processing purpose must be documented',
                deadline: this._calculateDeadline('ongoing'),
                statutoryRef: this.gdprArticles['30'].statutoryRef,
                penalty: this.gdprArticles['30'].penalty,
                remediation: this.gdprArticles['30'].remediation
            });
        }

        return violations;
    }

    /**
     * GDPR ARTICLE 32 - Security of Processing
     */
    _validateGDPR32(securityMeasures) {
        const violations = [];

        if (!securityMeasures.encryption) {
            violations.push({
                rule: 'GDPR_32',
                severity: 'CRITICAL',
                message: 'Encryption required for personal data processing',
                deadline: this._calculateDeadline('immediate'),
                statutoryRef: this.gdprArticles['32'].statutoryRef,
                penalty: this.gdprArticles['32'].penalty,
                remediation: this.gdprArticles['32'].remediation
            });
        }

        return violations;
    }

    /**
     * GDPR ARTICLE 33 - Breach Notification
     */
    _validateGDPR33(breach) {
        const violations = [];

        if (!breach.notifiedAt) {
            violations.push({
                rule: 'GDPR_33',
                severity: 'CRITICAL',
                message: 'Breach notification required within 72 hours',
                deadline: this._calculateDeadline('72 hours'),
                statutoryRef: this.gdprArticles['33'].statutoryRef,
                penalty: this.gdprArticles['33'].penalty,
                remediation: this.gdprArticles['33'].remediation
            });
        }

        return violations;
    }

    /**
     * GDPR ARTICLE 35 - Data Protection Impact Assessment
     */
    _validateGDPR35(processing) {
        const violations = [];

        if (processing.highRisk && !processing.dpiaCompleted) {
            violations.push({
                rule: 'GDPR_35',
                severity: 'HIGH',
                message: 'DPIA required for high-risk processing',
                deadline: this._calculateDeadline('pre-processing'),
                statutoryRef: this.gdprArticles['35'].statutoryRef,
                penalty: this.gdprArticles['35'].penalty,
                remediation: this.gdprArticles['35'].remediation
            });
        }

        return violations;
    }

    // ================================================================
    // FICA SECTION VALIDATIONS
    // ================================================================

    /**
     * FICA SECTION 28 - Transaction Monitoring
     */
    _validateFICA28(transaction) {
        const violations = [];

        if (transaction.amount > 25000 && !transaction.compliance?.ficaVerified) {
            violations.push({
                rule: 'FICA_28',
                severity: 'HIGH',
                message: 'Transaction exceeds R25,000 threshold - FICA verification required',
                amount: transaction.amount,
                threshold: 25000,
                deadline: this._calculateDeadline('immediate'),
                statutoryRef: this.ficaSections['28'].statutoryRef,
                penalty: this.ficaSections['28'].penalty,
                remediation: this.ficaSections['28'].remediation
            });
        }

        return violations;
    }

    /**
     * FICA SECTION 29 - Suspicious Activity Reporting
     */
    _validateFICA29(transaction) {
        const violations = [];

        if (transaction.amount > 100000 && !transaction.compliance?.sarSubmitted) {
            violations.push({
                rule: 'FICA_29',
                severity: 'CRITICAL',
                message: 'Suspicious Activity Report (SAR) required for transactions over R100,000',
                amount: transaction.amount,
                threshold: 100000,
                deadline: this._calculateDeadline('15 days'),
                statutoryRef: this.ficaSections['29'].statutoryRef,
                penalty: this.ficaSections['29'].penalty,
                remediation: this.ficaSections['29'].remediation
            });
        }

        return violations;
    }

    // ================================================================
    // SARB GUIDANCE VALIDATIONS
    // ================================================================

    /**
     * SARB GUIDANCE NOTE 6 - Trust Account Verification
     */
    _validateSARBGN6(trustAccount) {
        const violations = [];

        if (!trustAccount.compliance?.bankConfirmed) {
            violations.push({
                rule: 'SARB_GN6.2026',
                severity: 'HIGH',
                message: 'Trust account not verified with bank',
                deadline: this._calculateDeadline('7 days'),
                statutoryRef: this.sarbGuidance['GN6.2026'].statutoryRef,
                penalty: this.sarbGuidance['GN6.2026'].penalty,
                remediation: this.sarbGuidance['GN6.2026'].remediation
            });
        }

        return violations;
    }

    // ================================================================
    // PUBLIC API METHODS
    // ================================================================

    /**
     * Validate entity against all applicable regulations
     */
    async validateCompliance(entity, entityType, context = {}) {
        const startTime = Date.now();

        if (!this.initialized) {
            await this._initialize();
        }

        const violations = [];

        // Select validation rules based on entity type
        switch (entityType) {
            case 'block':
                violations.push(...this._validateLPC341(entity));
                violations.push(...this._validateLPC342(entity));
                violations.push(...this._validateLPC343(entity));
                break;

            case 'attorney':
                violations.push(...this._validateLPC551(entity));
                if (entity.fidelityFund) {
                    violations.push(...this._validateLPC552(entity.fidelityFund));
                    violations.push(...this._validateLPC554(entity.fidelityFund));
                }
                break;

            case 'trust_account':
                violations.push(...this._validateLPC861(entity));
                violations.push(...this._validateLPC862(entity));
                violations.push(...this._validateLPC863(entity));
                violations.push(...this._validateSARBGN6(entity));
                break;

            case 'transaction':
                violations.push(...this._validateLPC211(entity));
                violations.push(...this._validateFICA28(entity));
                violations.push(...this._validateFICA29(entity));
                break;

            case 'audit':
                violations.push(...this._validateLPC173(entity));
                violations.push(...this._validateLPC953(entity));
                violations.push(...this._validatePOPIA20(entity));
                violations.push(...this._validateGDPR30(entity));
                break;

            case 'user_context':
                violations.push(...this._validateLPC352(entity));
                violations.push(...this._validateLPC413(entity));
                violations.push(...this._validatePOPIA19(entity));
                violations.push(...this._validateGDPR32(entity));
                break;

            case 'breach':
                violations.push(...this._validatePOPIA21(entity));
                violations.push(...this._validateGDPR33(entity));
                break;

            case 'dsar':
                violations.push(...this._validatePOPIA22(entity));
                violations.push(...this._validateGDPR35(entity));
                break;
        }

        // Calculate compliance score
        const score = this.calculateComplianceScore(violations);

        // Store violations for this entity
        if (entity.id || entity._id) {
            const entityId = entity.id || entity._id.toString();
            this.violationRegistry.set(entityId, violations);
            this.complianceScores.set(entityId, score);
        }

        // Update performance metrics
        this.performance.record({
            operation: 'validateCompliance',
            duration: Date.now() - startTime,
            success: true,
            entityType,
            violationCount: violations.length,
            score
        });

        return {
            compliant: violations.length === 0,
            score,
            violations,
            summary: {
                total: violations.length,
                critical: violations.filter(v => v.severity === 'CRITICAL').length,
                high: violations.filter(v => v.severity === 'HIGH').length,
                medium: violations.filter(v => v.severity === 'MEDIUM').length,
                low: violations.filter(v => v.severity === 'LOW').length
            },
            remediation: violations.map(v => ({
                rule: v.rule,
                action: v.remediation,
                deadline: v.deadline,
                priority: v.severity
            })),
            timestamp: new Date().toISOString(),
            duration: Date.now() - startTime
        };
    }

    /**
     * Calculate compliance score based on violations
     */
    calculateComplianceScore(violations) {
        if (!violations || violations.length === 0) {
            return 100;
        }

        const weights = {
            'CRITICAL': 25,
            'HIGH': 10,
            'MEDIUM': 5,
            'LOW': 1
        };

        let totalDeduction = 0;

        violations.forEach(violation => {
            totalDeduction += weights[violation.severity] || 5;
        });

        const score = Math.max(0, 100 - totalDeduction);
        return Math.round(score);
    }

    /**
     * Calculate deadline from relative time
     */
    _calculateDeadline(relativeTime) {
        const now = new Date();

        switch (relativeTime) {
            case 'immediate':
                return now.toISOString();
            case '24 hours':
                return new Date(now.getTime() + 24 * 60 * 60 * 1000).toISOString();
            case '7 days':
                return new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString();
            case '30 days':
                return new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000).toISOString();
            case '72 hours':
                return new Date(now.getTime() + 72 * 60 * 60 * 1000).toISOString();
            case '15 days':
                return new Date(now.getTime() + 15 * 24 * 60 * 60 * 1000).toISOString();
            case 'annual':
                return new Date(now.getFullYear(), 11, 31).toISOString();
            case 'ongoing':
            case 'pre-processing':
                return null;
            default:
                return new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString();
        }
    }

    /**
     * Generate compliance certificate
     */
    generateComplianceCertificate(entityId, entityType, score, violations) {
        const certificateId = `LPC-CERT-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`;
        const timestamp = new Date().toISOString();
        const expiryDate = new Date();
        expiryDate.setFullYear(expiryDate.getFullYear() + 1);

        const certificate = {
            certificateId,
            entityId,
            entityType,
            issuedAt: timestamp,
            expiresAt: expiryDate.toISOString(),
            complianceScore: score,
            status: score >= 90 ? 'COMPLIANT' :
                score >= 70 ? 'PARTIALLY_COMPLIANT' :
                    'NON_COMPLIANT',
            violations: violations.map(v => ({
                rule: v.rule,
                severity: v.severity,
                message: v.message,
                deadline: v.deadline
            })),
            regulatoryFrameworks: {
                lpc: this._checkFrameworkCompliance(violations, 'LPC'),
                popia: this._checkFrameworkCompliance(violations, 'POPIA'),
                gdpr: this._checkFrameworkCompliance(violations, 'GDPR'),
                fica: this._checkFrameworkCompliance(violations, 'FICA'),
                sarb: this._checkFrameworkCompliance(violations, 'SARB')
            },
            verificationUrl: `https://verify.wilsy.os/certificates/${certificateId}`,
            qrCode: `https://verify.wilsy.os/qr/${certificateId}`,
            regulatoryBodies: ['LPC', 'FSCA', 'SARB', 'FIC'],
            issuedBy: 'Wilsy OS Compliance Engine v5.2.0',
            digitalSignature: crypto
                .createHash('sha3-512')
                .update(certificateId + entityId + score + timestamp)
                .digest('hex')
        };

        this.certificateRegistry.set(certificateId, certificate);

        return certificate;
    }

    /**
     * Check compliance status for a regulatory framework
     */
    _checkFrameworkCompliance(violations, framework) {
        const frameworkViolations = violations.filter(v =>
            v.rule && v.rule.startsWith(framework)
        );

        return {
            compliant: frameworkViolations.length === 0,
            violationCount: frameworkViolations.length,
            criticalViolations: frameworkViolations.filter(v => v.severity === 'CRITICAL').length,
            highViolations: frameworkViolations.filter(v => v.severity === 'HIGH').length
        };
    }

    /**
     * Get compliance status for an entity
     */
    async getComplianceStatus(entityId) {
        const violations = this.violationRegistry.get(entityId) || [];
        const score = this.complianceScores.get(entityId) || 100;

        return {
            entityId,
            timestamp: new Date().toISOString(),
            complianceScore: score,
            status: score >= 90 ? 'COMPLIANT' :
                score >= 70 ? 'PARTIALLY_COMPLIANT' :
                    'NON_COMPLIANT',
            violations: {
                total: violations.length,
                critical: violations.filter(v => v.severity === 'CRITICAL').length,
                high: violations.filter(v => v.severity === 'HIGH').length,
                medium: violations.filter(v => v.severity === 'MEDIUM').length,
                low: violations.filter(v => v.severity === 'LOW').length,
                items: violations.slice(0, 10) // Most recent 10
            },
            remediation: violations
                .filter(v => v.severity === 'CRITICAL' || v.severity === 'HIGH')
                .map(v => ({
                    rule: v.rule,
                    action: v.remediation,
                    deadline: v.deadline,
                    priority: v.severity
                })),
            certificates: Array.from(this.certificateRegistry.values())
                .filter(c => c.entityId === entityId)
                .sort((a, b) => new Date(b.issuedAt) - new Date(a.issuedAt))
        };
    }

    /**
     * Get compliance analytics
     */
    async getComplianceAnalytics(tenantId, options = {}) {
        const metrics = this.performance.getMetrics();
        const allViolations = Array.from(this.violationRegistry.values()).flat();

        const analytics = {
            tenantId,
            timestamp: new Date().toISOString(),
            summary: {
                totalEntities: this.complianceScores.size,
                averageScore: this.complianceScores.size > 0
                    ? Math.round(Array.from(this.complianceScores.values()).reduce((a, b) => a + b, 0) / this.complianceScores.size)
                    : 100,
                totalViolations: allViolations.length,
                criticalViolations: allViolations.filter(v => v.severity === 'CRITICAL').length,
                highViolations: allViolations.filter(v => v.severity === 'HIGH').length,
                mediumViolations: allViolations.filter(v => v.severity === 'MEDIUM').length,
                lowViolations: allViolations.filter(v => v.severity === 'LOW').length
            },
            byFramework: {
                lpc: {
                    violations: allViolations.filter(v => v.rule?.startsWith('LPC')).length,
                    critical: allViolations.filter(v => v.rule?.startsWith('LPC') && v.severity === 'CRITICAL').length
                },
                popia: {
                    violations: allViolations.filter(v => v.rule?.startsWith('POPIA')).length,
                    critical: allViolations.filter(v => v.rule?.startsWith('POPIA') && v.severity === 'CRITICAL').length
                },
                gdpr: {
                    violations: allViolations.filter(v => v.rule?.startsWith('GDPR')).length,
                    critical: allViolations.filter(v => v.rule?.startsWith('GDPR') && v.severity === 'CRITICAL').length
                },
                fica: {
                    violations: allViolations.filter(v => v.rule?.startsWith('FICA')).length,
                    critical: allViolations.filter(v => v.rule?.startsWith('FICA') && v.severity === 'CRITICAL').length
                },
                sarb: {
                    violations: allViolations.filter(v => v.rule?.startsWith('SARB')).length,
                    critical: allViolations.filter(v => v.rule?.startsWith('SARB') && v.severity === 'CRITICAL').length
                }
            },
            bySeverity: {
                critical: allViolations.filter(v => v.severity === 'CRITICAL').length,
                high: allViolations.filter(v => v.severity === 'HIGH').length,
                medium: allViolations.filter(v => v.severity === 'MEDIUM').length,
                low: allViolations.filter(v => v.severity === 'LOW').length
            },
            deadlines: {
                upcoming: Array.from(this.violationRegistry.entries())
                    .flatMap(([id, violations]) =>
                        violations.filter(v => v.deadline)
                            .map(v => ({
                                entityId: id,
                                rule: v.rule,
                                deadline: v.deadline,
                                daysUntil: Math.ceil((new Date(v.deadline) - new Date()) / (1000 * 60 * 60 * 24))
                            }))
                    )
                    .filter(d => d.daysUntil > 0 && d.daysUntil <= 7)
                    .sort((a, b) => a.daysUntil - b.daysUntil),
                missed: Array.from(this.violationRegistry.entries())
                    .flatMap(([id, violations]) =>
                        violations.filter(v => v.deadline && new Date(v.deadline) < new Date())
                            .map(v => ({
                                entityId: id,
                                rule: v.rule,
                                deadline: v.deadline,
                                daysOverdue: Math.ceil((new Date() - new Date(v.deadline)) / (1000 * 60 * 60 * 24))
                            }))
                    )
                    .sort((a, b) => b.daysOverdue - a.daysOverdue)
            },
            performance: {
                averageLatencyMs: metrics.averageLatency,
                validationsPerMinute: metrics.throughput,
                violationRate: metrics.errorRate,
                cacheHitRate: this.ruleCache.size > 0 ? 100 : 0
            }
        };

        return analytics;
    }

    /**
     * Get service health status
     */
    async healthCheck() {
        return {
            service: 'ComplianceEngine',
            version: '5.2.0',
            initialized: this.initialized,
            status: 'HEALTHY',
            timestamp: new Date().toISOString(),
            metrics: {
                rulesLoaded: this.ruleCache.size,
                activeViolations: Array.from(this.violationRegistry.values()).flat().length,
                entitiesTracked: this.complianceScores.size,
                certificatesIssued: this.certificateRegistry.size
            },
            performance: this.performance.getMetrics(),
            _links: {
                self: '/api/v1/compliance/health',
                analytics: '/api/v1/compliance/analytics',
                rules: '/api/v1/compliance/rules'
            }
        };
    }
}

module.exports = new ComplianceEngine();