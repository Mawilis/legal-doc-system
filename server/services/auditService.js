const crypto = require('crypto');
const { BlockchainAnchor } = require('./blockchainAnchor');

class AuditService {
    constructor() {
        this.anchors = new BlockchainAnchor();
    }

    async recordAccess(resource, identifier, userContext, action) {
        if (!userContext?.userId) {
            throw new Error('USER_CONTEXT_REQUIRED');
        }

        const auditEntry = {
            id: crypto.randomUUID(),
            resource,
            identifier,
            userId: userContext.userId,
            tenantId: userContext.tenantId,
            firmId: userContext.firmId,
            roles: userContext.roles,
            ipAddress: userContext.ipAddress,
            userAgent: userContext.userAgent,
            action,
            timestamp: new Date().toISOString(),
            regulatoryTags: this.getRegulatoryTags(resource, action)
        };

        auditEntry.hash = crypto
            .createHash('sha256')
            .update(JSON.stringify(auditEntry))
            .digest('hex');

        auditEntry.blockchainAnchor = await this.anchors.anchor(auditEntry.hash);
        
        console.log(`📋 AUDIT: ${action} - ${resource} - ${identifier} - ${auditEntry.id}`);
        return auditEntry;
    }

    getRegulatoryTags(resource, action) {
        const tags = [];
        if (resource.includes('attorney')) tags.push('LPC_RULE_17.3');
        if (resource.includes('trust')) tags.push('LPC_RULE_3.4');
        if (resource.includes('matter')) tags.push('LPC_RULE_21.1');
        if (action === 'VIEW') tags.push('POPIA_SECTION_20');
        if (action === 'EXPORT') tags.push('GDPR_ARTICLE_30');
        return tags;
    }
}

module.exports = new AuditService();
