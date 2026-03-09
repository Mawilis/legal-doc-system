#!/* eslint-env mocha */

/* eslint-disable */
import { expect } from "chai";
import mongoose from "mongoose";
import ValidationAudit, {
  AUDIT_ACTIONS,
  AUDIT_STATUS,
  SEVERITY_LEVELS,
  RETENTION_POLICIES,
  DATA_RESIDENCY,
} from '../../models/ValidationAudit.js';

describe('ValidationAudit Model - Forensic Grade Audit Trail', function() {
  const testTenantId = 'test-tenant-12345678';
  const testAuditId = 'audit-12345678-test';

  before(async () => {
    // Ensure clean connection
    if (mongoose.connection.readyState === 0) {
      await mongoose.connect(process.env.MONGODB_URI || process.env.MONGODB_URI,
          phone: '0821234567',
        },
        userIp: '192.168.1.100',
      });

      const redacted = audit.redactPII();
      expect(redacted.userIp).to.include('xxx');
    });

    it('should provide summary virtual property', async function() {
      const audit = new ValidationAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      const summary = audit.summary;
      expect(summary).to.be.an('object');
      expect(summary.auditId).to.equal(audit.auditId);
      expect(summary.valid).to.be.true;
    });

    it('should create audit entry with createAudit static method', async function() {
      const audit = await ValidationAudit.createAudit({
        tenantId: testTenantId,
        action: AUDIT_ACTIONS.ID_VALIDATION,
        resourceType: 'identity',
        validationResult: { valid: true },
      });

      expect(audit).to.exist;
      expect(audit.auditId).to.exist;
      expect(audit.tenantId).to.equal(testTenantId);
    });
  });
});
