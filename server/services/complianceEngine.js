// ====================================================================
// FILE: server/services/complianceEngine.js - COMPLETE PRODUCTION
// ====================================================================
/**
 * WILSYS OS - COMPLIANCE ENGINE
 * LPC Rules 3.4, 17.3, 21.1, 35.2, 41.3, 55, 86, 95
 * POPIA Sections 19-22
 * GDPR Articles 30-35
 * FICA Section 28
 */

const { ValidationError, ComplianceError } = require('../utils/errors');

class ComplianceEngine {
    constructor() {
        this.ruleCache = new Map();
        this.violationThresholds = {
            CRITICAL: 0,
            HIGH: 7,
            MEDIUM: 30,
            LOW: 90
        };
    }

    /**
     * LPC RULE 3.4 - TRUST ACCOUNT RECONCILIATION
     * Cryptographic proof required for all trust transactions
     */
    validateLPCRule34(block) {
        const violations = [];

        // Rule 3.4.1: Daily reconciliation required
        if (!block.reconciliationTimestamp) {
            violations.push({
                rule: 'LPC_3.4.1',
                severity: 'CRITICAL',
                message: 'Missing daily reconciliation timestamp',
                regulatoryRef: 'Legal Practice Act 2014 s86(3)',
                deadline: '24 hours',
                remediation: 'Perform immediate trust account reconciliation'
            });
        }

        // Rule 3.4.2: Cryptographic proof (Merkle root) required
        if (!block.merkleRoot) {
            violations.push({
                rule: 'LPC_3.4.2',
                severity: 'CRITICAL',
                message: 'Merkle root required for trust accounting',
                regulatoryRef: 'LPC Rule 3.4.2',
                remediation: 'Generate merkle proof from transaction hashes',
                algorithm: 'SHA3-512'
            });
        }

        // Rule 3.4.3: Regulator node anchoring required
        if (!block.regulatorAnchor) {
            violations.push({
                rule: 'LPC_3.4.3',
                severity: 'HIGH',
                message: 'Block not anchored to LPC regulator node',
                regulatoryRef: 'LPC Rule 3.4.3',
                remediation: 'Submit anchor to lpc.regulator.gov.za',
                endpoint: 'https://lpc.regulator.gov.za/api/v1/anchor'
            });
        }

        // Rule 3.4.4: Transaction verification required
        if (block.transactions && block.transactions.length > 0) {
            const unverified = block.transactions.filter(tx => !tx.verified);
            if (unverified.length > 0) {
                violations.push({
                    rule: 'LPC_3.4.4',
                    severity: 'HIGH',
                    message: `${unverified.length} unverified transactions`,
                    regulatoryRef: 'LPC Rule 3.4.4',
                    transactionIds: unverified.map(tx => tx.id || tx.transactionId).filter(Boolean)
                });
            }
        }

        // Rule 3.4.5: Balance verification required
        if (block.balances) {
            const calculatedBalance = block.transactions?.reduce((sum, tx) =>
                sum + (tx.type === 'CREDIT' ? tx.amount : -tx.amount), block.openingBalance || 0
            );

            if (calculatedBalance !== block.balances.closing) {
                violations.push({
                    rule: 'LPC_3.4.5',
                    severity: 'CRITICAL',
                    message: 'Balance verification failed',
                    expected: block.balances.closing,
                    calculated: calculatedBalance,
                    discrepancy: Math.abs(calculatedBalance - block.balances.closing)
                });
            }
        }

        return violations;
    }

    /**
     * LPC RULE 17.3 - ATTORNEY PROFILE ACCESS LOGGING
     * All access to attorney profiles must be logged
     */
    validateLPCRule173(auditEntry) {
        const violations = [];

        if (!auditEntry) {
            violations.push({
                rule: 'LPC_17.3.1',
                severity: 'CRITICAL',
                message: 'No audit entry provided for attorney profile access',
                regulatoryRef: 'LPC Rule 17.3'
            });
            return violations;
        }

        if (!auditEntry.userId) {
            violations.push({
                rule: 'LPC_17.3.2',
                severity: 'CRITICAL',
                message: 'User ID required for attorney profile access logging',
                regulatoryRef: 'LPC Rule 17.3'
            });
        }

        if (!auditEntry.timestamp) {
            violations.push({
                rule: 'LPC_17.3.3',
                severity: 'HIGH',
                message: 'Timestamp required for audit trail integrity',
                regulatoryRef: 'LPC Rule 17.3'
            });
        }

        if (!auditEntry.ipAddress) {
            violations.push({
                rule: 'LPC_17.3.4',
                severity: 'MEDIUM',
                message: 'IP address recommended for forensic tracking',
                regulatoryRef: 'LPC Rule 17.3'
            });
        }

        return violations;
    }

    /**
     * LPC RULE 21.1 - MATTER TRANSACTION TRACEABILITY
     * All matter transactions must be traceable to trust accounts
     */
    validateLPCRule211(transaction) {
        const violations = [];

        if (!transaction.matterId) {
            violations.push({
                rule: 'LPC_21.1.1',
                severity: 'CRITICAL',
                message: 'Matter ID required for transaction traceability',
                regulatoryRef: 'LPC Rule 21.1'
            });
        }

        if (transaction.amount > 100000 && !transaction.compliance?.ficaThresholdExceeded) {
            violations.push({
                rule: 'LPC_21.1.2',
                severity: 'HIGH',
                message: 'High-value transaction requires FICA verification',
                amount: transaction.amount,
                threshold: 100000,
                regulatoryRef: 'FICA Section 28'
            });
        }

        if (transaction.accountNumber &&
            !/^TRUST-[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}$/.test(transaction.accountNumber)) {
            violations.push({
                rule: 'LPC_21.1.3',
                severity: 'HIGH',
                message: 'Invalid trust account number format',
                provided: transaction.accountNumber,
                expectedFormat: 'TRUST-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX',
                regulatoryRef: 'LPC Rule 21.1.3'
            });
        }

        return violations;
    }

    /**
     * LPC RULE 35.2 - COMPLIANCE REPORTING ACCESS CONTROL
     * Executive-level access required for compliance reports
     */
    validateLPCRule352(userContext) {
        const violations = [];

        if (!userContext?.roles) {
            violations.push({
                rule: 'LPC_35.2.1',
                severity: 'CRITICAL',
                message: 'User roles required for access control',
                regulatoryRef: 'LPC Rule 35.2'
            });
            return violations;
        }

        const executiveRoles = ['COMPLIANCE_OFFICER', 'LPC_ADMIN', 'MANAGING_PARTNER', 'DIRECTOR'];
        const hasExecutiveAccess = userContext.roles.some(role => executiveRoles.includes(role));

        if (!hasExecutiveAccess) {
            violations.push({
                rule: 'LPC_35.2.2',
                severity: 'CRITICAL',
                message: 'Insufficient privileges for compliance report access',
                requiredRoles: executiveRoles,
                userRoles: userContext.roles,
                userId: userContext.userId,
                regulatoryRef: 'LPC Rule 35.2'
            });
        }

        return violations;
    }

    /**
     * LPC RULE 41.3 - METRICS ADMINISTRATOR ACCESS
     * LPC metrics require administrator privileges
     */
    validateLPCRule413(userContext) {
        const violations = [];

        if (!userContext?.roles?.includes('LPC_ADMIN')) {
            violations.push({
                rule: 'LPC_41.3.1',
                severity: 'CRITICAL',
                message: 'LPC Administrator access required for metrics',
                requiredRole: 'LPC_ADMIN',
                userId: userContext?.userId,
                regulatoryRef: 'LPC Rule 41.3'
            });
        }

        if (!userContext?.tenantId) {
            violations.push({
                rule: 'LPC_41.3.2',
                severity: 'HIGH',
                message: 'Tenant ID required for metrics isolation',
                regulatoryRef: 'LPC Rule 86.5'
            });
        }

        return violations;
    }

    /**
     * LPC RULE 55 - FIDELITY FUND COMPLIANCE
     * Annual contribution and certificate requirements
     */
    validateLPCRule55(fidelityRecord) {
        const violations = [];

        if (!fidelityRecord.certificateId) {
            violations.push({
                rule: 'LPC_55.1',
                severity: 'CRITICAL',
                message: 'Fidelity Fund certificate ID required',
                regulatoryRef: 'LPC Rule 55(1)'
            });
        }

        if (fidelityRecord.contributionAmount < 500) {
            violations.push({
                rule: 'LPC_55.2',
                severity: 'HIGH',
                message: 'Fidelity Fund contribution below minimum',
                required: 500,
                actual: fidelityRecord.contributionAmount,
                regulatoryRef: 'LPC Rule 55(2)'
            });
        }

        if (fidelityRecord.contributionAmount > 50000) {
            violations.push({
                rule: 'LPC_55.3',
                severity: 'MEDIUM',
                message: 'Contribution exceeds standard threshold, additional verification required',
                threshold: 50000,
                actual: fidelityRecord.contributionAmount,
                regulatoryRef: 'LPC Rule 55(3)'
            });
        }

        if (fidelityRecord.expiryDate && new Date(fidelityRecord.expiryDate) < new Date()) {
            violations.push({
                rule: 'LPC_55.4',
                severity: 'CRITICAL',
                message: 'Fidelity Fund certificate has expired',
                expiryDate: fidelityRecord.expiryDate,
                daysOverdue: Math.floor((new Date() - new Date(fidelityRecord.expiryDate)) / (1000 * 60 * 60 * 24)),
                regulatoryRef: 'LPC Rule 55(4)'
            });
        }

        return violations;
    }

    /**
     * LPC RULE 86 - TRUST ACCOUNT MANAGEMENT
     * Trust account opening and maintenance requirements
     */
    validateLPCRule86(trustAccount) {
        const violations = [];

        if (!trustAccount.accountNumber) {
            violations.push({
                rule: 'LPC_86.1',
                severity: 'CRITICAL',
                message: 'Trust account number required',
                regulatoryRef: 'LPC Rule 86(1)'
            });
        }

        if (trustAccount.balances?.current < 0) {
            violations.push({
                rule: 'LPC_86.2',
                severity: 'CRITICAL',
                message: 'Trust account has negative balance',
                balance: trustAccount.balances.current,
                regulatoryRef: 'LPC Rule 86(2)'
            });
        }

        if (trustAccount.clientBalances) {
            const negativeClients = trustAccount.clientBalances.filter(c => c.balance < 0);
            if (negativeClients.length > 0) {
                violations.push({
                    rule: 'LPC_86.3',
                    severity: 'CRITICAL',
                    message: `${negativeClients.length} client sub-accounts have negative balances`,
                    clients: negativeClients.map(c => c.clientId),
                    regulatoryRef: 'LPC Rule 86(3)'
                });
            }
        }

        return violations;
    }

    /**
     * LPC RULE 95 - COMPLIANCE AUDIT REQUIREMENTS
     * Annual compliance audit specifications
     */
    validateLPCRule95(audit) {
        const violations = [];

        if (!audit.auditor) {
            violations.push({
                rule: 'LPC_95.1',
                severity: 'CRITICAL',
                message: 'Compliance auditor must be identified',
                regulatoryRef: 'LPC Rule 95(1)'
            });
        }

        if (!audit.auditDate) {
            violations.push({
                rule: 'LPC_95.2',
                severity: 'CRITICAL',
                message: 'Audit date required',
                regulatoryRef: 'LPC Rule 95(2)'
            });
        }

        const oneYearAgo = new Date();
        oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);

        if (audit.auditDate && new Date(audit.auditDate) < oneYearAgo) {
            violations.push({
                rule: 'LPC_95.3',
                severity: 'HIGH',
                message: 'Compliance audit is overdue',
                lastAuditDate: audit.auditDate,
                requiredFrequency: 'Annual',
                regulatoryRef: 'LPC Rule 95(3)'
            });
        }

        return violations;
    }

    /**
     * POPIA SECTION 19 - SECURITY MEASURES
     * Reasonable security measures for personal information
     */
    validatePOPIASection19(userContext) {
        const violations = [];

        if (!userContext.encrypted && userContext.transportSecurity !== 'TLS1.3') {
            violations.push({
                rule: 'POPIA_19.1',
                severity: 'CRITICAL',
                message: 'Access must be encrypted (TLS 1.3 required)',
                regulatoryRef: 'POPIA Section 19',
                remediation: 'Enable HTTPS with TLS 1.3'
            });
        }

        if (!userContext.sessionId) {
            violations.push({
                rule: 'POPIA_19.2',
                severity: 'MEDIUM',
                message: 'Session tracking recommended for security monitoring',
                regulatoryRef: 'POPIA Section 19(b)'
            });
        }

        return violations;
    }

    /**
     * POPIA SECTION 20 - RECORD OF PROCESSING
     * Maintain record of all processing activities
     */
    validatePOPIASection20(auditEntry) {
        const violations = [];

        if (!auditEntry) {
            violations.push({
                rule: 'POPIA_20.1',
                severity: 'CRITICAL',
                message: 'Processing record required for POPIA compliance',
                regulatoryRef: 'POPIA Section 20'
            });
            return violations;
        }

        if (!auditEntry.userId) {
            violations.push({
                rule: 'POPIA_20.2',
                severity: 'HIGH',
                message: 'Data subject identifier recommended for access records',
                regulatoryRef: 'POPIA Section 20(a)'
            });
        }

        if (!auditEntry.consentId && auditEntry.action === 'PROCESS') {
            violations.push({
                rule: 'POPIA_20.3',
                severity: 'CRITICAL',
                message: 'Consent ID required for processing personal information',
                regulatoryRef: 'POPIA Section 20(b)'
            });
        }

        return violations;
    }

    /**
     * POPIA SECTION 21 - BREACH NOTIFICATION
     * Notification requirements for security compromises
     */
    validatePOPIASection21(breach) {
        const violations = [];

        if (!breach.detectedAt) {
            violations.push({
                rule: 'POPIA_21.1',
                severity: 'CRITICAL',
                message: 'Breach detection timestamp required',
                regulatoryRef: 'POPIA Section 21'
            });
        }

        const notificationDelay = breach.notifiedAt ?
            new Date(breach.notifiedAt) - new Date(breach.detectedAt) : null;

        if (notificationDelay > 72 * 60 * 60 * 1000) {
            violations.push({
                rule: 'POPIA_21.2',
                severity: 'HIGH',
                message: 'Breach notification exceeds 72-hour requirement',
                delayHours: Math.round(notificationDelay / (60 * 60 * 1000)),
                regulatoryRef: 'POPIA Section 21(2)'
            });
        }

        return violations;
    }

    /**
     * FICA SECTION 28 - TRANSACTION MONITORING
     * Suspicious transaction reporting requirements
     */
    validateFICASection28(transaction) {
        const violations = [];

        if (transaction.amount > 25000 && !transaction.compliance?.ficaVerified) {
            violations.push({
                rule: 'FICA_28.1',
                severity: 'HIGH',
                message: 'Transaction exceeds R25,000 threshold - FICA verification required',
                amount: transaction.amount,
                threshold: 25000,
                regulatoryRef: 'FICA Section 28(1)'
            });
        }

        if (transaction.amount > 100000 && !transaction.compliance?.sarSubmitted) {
            violations.push({
                rule: 'FICA_28.2',
                severity: 'CRITICAL',
                message: 'Suspicious Activity Report (SAR) required for transactions over R100,000',
                amount: transaction.amount,
                threshold: 100000,
                regulatoryRef: 'FICA Section 28(2)'
            });
        }

        if (transaction.currency && transaction.currency !== 'ZAR') {
            violations.push({
                rule: 'FICA_28.3',
                severity: 'MEDIUM',
                message: 'Foreign currency transaction requires enhanced due diligence',
                currency: transaction.currency,
                regulatoryRef: 'FICA Section 28(3)'
            });
        }

        return violations;
    }

    /**
     * GDPR ARTICLE 30 - RECORDS OF PROCESSING ACTIVITIES
     * Maintain detailed records of all processing
     */
    validateGDPRArticle30(processingRecord) {
        const violations = [];

        if (!processingRecord.controller) {
            violations.push({
                rule: 'GDPR_30.1',
                severity: 'CRITICAL',
                message: 'Data controller must be identified',
                regulatoryRef: 'GDPR Article 30(1)'
            });
        }

        if (!processingRecord.purpose) {
            violations.push({
                rule: 'GDPR_30.2',
                severity: 'CRITICAL',
                message: 'Processing purpose must be documented',
                regulatoryRef: 'GDPR Article 30(1)(b)'
            });
        }

        if (!processingRecord.dataCategories || processingRecord.dataCategories.length === 0) {
            violations.push({
                rule: 'GDPR_30.3',
                severity: 'HIGH',
                message: 'Categories of personal data must be documented',
                regulatoryRef: 'GDPR Article 30(1)(c)'
            });
        }

        return violations;
    }

    /**
     * GDPR ARTICLE 32 - SECURITY OF PROCESSING
     * Implement appropriate technical measures
     */
    validateGDPRArticle32(securityMeasures) {
        const violations = [];

        if (!securityMeasures.encryption) {
            violations.push({
                rule: 'GDPR_32.1',
                severity: 'CRITICAL',
                message: 'Encryption required for personal data processing',
                regulatoryRef: 'GDPR Article 32(1)(a)'
            });
        }

        if (!securityMeasures.pseudonymization) {
            violations.push({
                rule: 'GDPR_32.2',
                severity: 'MEDIUM',
                message: 'Pseudonymization recommended for high-risk processing',
                regulatoryRef: 'GDPR Article 32(1)(a)'
            });
        }

        if (!securityMeasures.confidentiality) {
            violations.push({
                rule: 'GDPR_32.3',
                severity: 'CRITICAL',
                message: 'Confidentiality measures required',
                regulatoryRef: 'GDPR Article 32(1)(b)'
            });
        }

        return violations;
    }

    /**
     * COMPREHENSIVE COMPLIANCE SCORE CALCULATION
     * Aggregates all violations into weighted score
     */
    calculateComplianceScore(violations) {
        if (!violations || violations.length === 0) {
            return 100;
        }

        const weights = {
            CRITICAL: 25,
            HIGH: 10,
            MEDIUM: 5,
            LOW: 1
        };

        let totalDeduction = 0;

        violations.forEach(violation => {
            totalDeduction += weights[violation.severity] || 5;
        });

        const score = Math.max(0, 100 - totalDeduction);
        return Math.round(score);
    }

    /**
     * GENERATE COMPLIANCE CERTIFICATE
     * Formal compliance certification document
     */
    generateComplianceCertificate(entityId, entityType, score, violations) {
        const certificateId = `LPC-CERT-${Date.now()}-${entityId.slice(-8)}`;

        return {
            certificateId,
            entityId,
            entityType,
            issuedAt: new Date().toISOString(),
            expiresAt: new Date(new Date().setFullYear(new Date().getFullYear() + 1)).toISOString(),
            complianceScore: score,
            status: score >= 90 ? 'COMPLIANT' : score >= 70 ? 'PARTIALLY_COMPLIANT' : 'NON_COMPLIANT',
            violations: violations.map(v => ({
                rule: v.rule,
                severity: v.severity,
                message: v.message
            })),
            verificationUrl: `https://verify.wilsy.os/certificates/${certificateId}`,
            qrCode: `https://verify.wilsy.os/qr/${certificateId}`,
            regulatoryBodies: ['LPC', 'FSCA', 'SARB'],
            issuedBy: 'Wilsy OS Compliance Engine v5.0.3',
            digitalSignature: require('crypto')
                .createHash('sha3-512')
                .update(certificateId + entityId + score + new Date().toISOString())
                .digest('hex')
                .substring(0, 64)
        };
    }
}

module.exports = new ComplianceEngine();