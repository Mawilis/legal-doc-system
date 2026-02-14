/**
 * Retention policy manager for compliance with legal hold requirements
 */
class RetentionManager {
    constructor() {
        this.policies = new Map();
        this.defaultPolicy = {
            name: 'companies_act_10_years',
            duration: 3650, // 10 years in days
            legalReference: 'Companies Act 71 of 2008, Section 24',
            enforcementLevel: 'STRICT'
        };
        this._initializeDefaultPolicies();
    }

    _initializeDefaultPolicies() {
        // LPC Rule 17.3 - Attorney profile access logs (10 years)
        this.policies.set('LPC_17_3', {
            name: 'lpc_attorney_access_logs',
            duration: 3650,
            legalReference: 'LPC Rule 17.3 - Attorney Profile Access Logging',
            enforcementLevel: 'STRICT'
        });

        // LPC Rule 21.1 - Trust account records (10 years)
        this.policies.set('LPC_21_1', {
            name: 'lpc_trust_account_records',
            duration: 3650,
            legalReference: 'LPC Rule 21.1 - Trust Account Traceability',
            enforcementLevel: 'STRICT'
        });

        // LPC Rule 35.2 - Compliance reports (5 years)
        this.policies.set('LPC_35_2', {
            name: 'lpc_compliance_reports',
            duration: 1825,
            legalReference: 'LPC Rule 35.2 - Executive Reports',
            enforcementLevel: 'STANDARD'
        });

        // POPIA Section 20 - Records of processing (10 years)
        this.policies.set('POPIA_20', {
            name: 'popia_processing_records',
            duration: 3650,
            legalReference: 'POPIA Section 20 - Records of Processing',
            enforcementLevel: 'STRICT'
        });

        // FICA Section 28 - Transaction monitoring (5 years)
        this.policies.set('FICA_28', {
            name: 'fica_transaction_monitoring',
            duration: 1825,
            legalReference: 'FICA Section 28 - Accountable Institutions',
            enforcementLevel: 'STANDARD'
        });
    }

    getPolicy(policyKey) {
        return this.policies.get(policyKey) || this.defaultPolicy;
    }

    calculateExpiryDate(startDate, policyKey) {
        const policy = this.getPolicy(policyKey);
        const expiryDate = new Date(startDate);
        expiryDate.setDate(expiryDate.getDate() + policy.duration);
        return expiryDate;
    }

    isExpired(date, policyKey) {
        const policy = this.getPolicy(policyKey);
        const expiryDate = this.calculateExpiryDate(date, policyKey);
        return new Date() > expiryDate;
    }

    daysUntilExpiry(date, policyKey) {
        const expiryDate = this.calculateExpiryDate(date, policyKey);
        const diffTime = expiryDate - new Date();
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }

    applyRetentionMetadata(record, policyKey) {
        return {
            ...record,
            retentionPolicy: this.getPolicy(policyKey).name,
            retentionStart: new Date().toISOString(),
            retentionDays: this.getPolicy(policyKey).duration,
            retentionLegalReference: this.getPolicy(policyKey).legalReference
        };
    }
}

module.exports = { RetentionManager };
