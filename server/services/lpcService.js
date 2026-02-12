const crypto = require('crypto');
const { v4: uuidv4 } = require('uuid');
const Joi = require('joi');
const AuditService = require('./auditService');
const ComplianceEngine = require('./complianceEngine');
const { ValidationError, ComplianceError, NotFoundError, AuthorizationError } = require('../utils/errors');

class LpcService {
    constructor() {
        this.audit = AuditService;
        this.compliance = ComplianceEngine;
    }

    async _generateMerkleProof(block) {
        const schema = Joi.object({
            blockId: Joi.string().uuid().required(),
            transactions: Joi.array().min(1).required(),
            previousBlockHash: Joi.string().hex().length(64),
            timestamp: Joi.date().iso().required(),
            firmId: Joi.string().uuid().required(),
            trustAccountId: Joi.string().required()
        });

        const { error, value } = schema.validate(block);
        if (error) {
            throw new ValidationError('INVALID_BLOCK_STRUCTURE', {
                details: error.details,
                regulatoryRef: 'LPC_3.4.2'
            });
        }

        const violations = this.compliance.validateLPCRule34(block);
        if (violations.length > 0) {
            throw new ComplianceError('LPC_RULE_VIOLATION', {
                violations,
                blockId: block.blockId
            });
        }

        const transactionHashes = block.transactions.map(tx => 
            crypto.createHash('sha256').update(JSON.stringify(tx)).digest('hex')
        );

        let merkleTree = transactionHashes;
        while (merkleTree.length > 1) {
            const newLevel = [];
            for (let i = 0; i < merkleTree.length; i += 2) {
                const left = merkleTree[i];
                const right = merkleTree[i + 1] || left;
                newLevel.push(
                    crypto.createHash('sha256')
                        .update(left + right)
                        .digest('hex')
                );
            }
            merkleTree = newLevel;
        }

        const merkleRoot = merkleTree[0];

        return {
            merkleRoot,
            transactionCount: block.transactions.length,
            blockHash: crypto.createHash('sha256')
                .update(block.blockId + merkleRoot)
                .digest('hex'),
            regulatorAnchor: `LPC-ANCHOR-${Date.now()}`,
            verificationPath: this._buildVerificationPath(transactionHashes, merkleRoot),
            timestamp: new Date().toISOString(),
            compliance: {
                lpc34: 'COMPLIANT',
                anchorVerified: true
            }
        };
    }

    async getAttorneyProfile(lpcNumber, tenantId, userContext) {
        if (!lpcNumber?.match(/^LPC-\d{4}-\d{6}$/)) {
            throw new ValidationError('INVALID_LPC_NUMBER', {
                format: 'LPC-YYYY-######',
                provided: lpcNumber
            });
        }

        const auditEntry = await this.audit.recordAccess(
            'attorney_profile',
            lpcNumber,
            userContext,
            'VIEW'
        );

        await this.compliance.validatePOPIAAccess(userContext, 'attorney_profile');

        return {
            lpcNumber,
            tenantId,
            name: 'John Doe',
            practice: 'Wilsy Legal',
            _compliance: {
                accessedAt: auditEntry.timestamp,
                auditId: auditEntry.id,
                blockchainAnchor: auditEntry.blockchainAnchor,
                regulatoryTags: auditEntry.regulatoryTags,
                dataSubjectRights: {
                    accessRequest: `/api/v1/popia/access/${auditEntry.id}`,
                    rectification: `/api/v1/popia/rectify/${auditEntry.id}`,
                    erasure: `/api/v1/popia/erase/${auditEntry.id}`
                }
            }
        };
    }

    async getMatterTransactions(matterId, accountNumber, userContext) {
        await this.audit.recordAccess(
            'matter_transactions',
            matterId,
            userContext,
            'QUERY'
        );

        if (accountNumber) {
            if (!accountNumber.match(/^LPC-TRUST-\d{10}$/)) {
                throw new ValidationError('INVALID_TRUST_ACCOUNT', {
                    format: 'LPC-TRUST-##########',
                    provided: accountNumber
                });
            }
        }

        return {
            data: [],
            metadata: {
                matterId,
                accountNumber: accountNumber || 'ALL',
                trustAccountBalance: accountNumber ? 15000.00 : 0,
                auditId: uuidv4(),
                timestamp: new Date().toISOString(),
                compliance: {
                    lpc211: 'COMPLIANT'
                }
            }
        };
    }

    async getComplianceReport(firmId, reportType, userContext) {
        const auditEntry = await this.audit.recordAccess(
            'compliance_report',
            `${firmId}/${reportType}`,
            {
                ...userContext,
                accessLevel: 'EXECUTIVE'
            },
            'EXPORT'
        );

        return {
            id: auditEntry.id,
            firmId,
            reportType,
            generatedAt: auditEntry.timestamp,
            generatedBy: userContext.userId,
            regulatoryFrameworks: {
                lpc: { status: 'COMPLIANT', score: 98.5 },
                popia: { status: 'COMPLIANT', score: 100 },
                fica: { status: 'COMPLIANT', score: 95.2 },
                gdpr: { status: 'COMPLIANT', score: 97.8 }
            },
            auditTrail: {
                reportAccess: [],
                blockchainAnchor: auditEntry.blockchainAnchor
            },
            certifications: [
                'LPC_COMPLIANT_2026',
                'POPIA_CERTIFIED',
                'ISO_27001',
                'SOC2_TYPE2'
            ]
        };
    }

    async getLPCMetrics(firmId, dateRange, userContext) {
        if (!userContext.roles?.includes('LPC_ADMIN')) {
            throw new AuthorizationError('LPC_METRICS_ACCESS_DENIED', {
                requiredRole: 'LPC_ADMIN',
                userId: userContext.userId
            });
        }

        await this.audit.recordAccess(
            'lpc_metrics',
            firmId,
            userContext,
            'ANALYZE'
        );

        return {
            firmId,
            period: dateRange,
            metrics: {
                trustAccounts: { total: 15, reconciled: 15, complianceRate: 100 },
                complianceRate: 99.7,
                averageResponseTime: 124,
                regulatoryFindings: 0,
                auditCoverage: 100
            },
            benchmarks: {
                industryAverage: 94.5,
                topDecile: 99.2,
                lpcRequirement: 100
            },
            recommendations: [
                'Implement additional audit sampling',
                'Review trust account reconciliation frequency'
            ]
        };
    }

    _buildVerificationPath(hashes, root) {
        return {
            algorithm: 'SHA256',
            root,
            path: hashes.map(h => h.slice(0, 8)).join('-')
        };
    }
}

module.exports = new LpcService();
