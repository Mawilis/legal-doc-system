/* eslint-disable no-undef */
const { RiskAssessor } = require('../../../services/legal-engine/RiskAssessor');
const AuditLogger = require('../../../utils/auditLogger');

describe('RiskAssessor', () => {
  let riskAssessor;
  
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Create fresh instance
    riskAssessor = new RiskAssessor({
      strictMode: true,
      auditEnabled: true,
      defaultResidency: 'ZA'
    });
  });
  
  afterEach(() => {
    jest.clearAllMocks();
  });
  
  describe('Tenant Context', () => {
    test('should fail closed when tenant context missing in strict mode', async () => {
      const document = "Test document";
      const emptyContext = {};
      
      await expect(riskAssessor.assess(document, emptyContext))
        .rejects
        .toThrow('TENANT_CONTEXT_REQUIRED');
    });
    
    test('should accept assessment with valid tenant context', async () => {
      const document = "Standard service agreement";
      const validContext = {
        tenantId: 'test-tenant-123',
        user: {
          id: 'test-user-123',
          permissions: []
        }
      };
      
      const result = await riskAssessor.assess(document, validContext);
      
      expect(result).toHaveProperty('level');
      expect(result).toHaveProperty('score');
      expect(result.score).toBeGreaterThanOrEqual(0);
      expect(result.score).toBeLessThanOrEqual(100);
      expect(result.metadata).toHaveProperty('tenantId', 'test-tenant-123');
    });
    
    test('should work in non-strict mode without tenant context', async () => {
      const nonStrictAssessor = new RiskAssessor({ strictMode: false });
      const document = "Simple agreement.";
      const emptyContext = {};
      
      const result = await nonStrictAssessor.assess(document, emptyContext);
      
      expect(result).toHaveProperty('level');
      expect(result.score).toBeGreaterThanOrEqual(0);
    });
  });
  
  describe('Risk Detection', () => {
    test('should detect high financial risk patterns', async () => {
      const document = "The vendor shall have unlimited liability for all damages.";
      const context = {
        tenantId: 'test-tenant-123',
        user: { id: 'test-user-123', permissions: [] }
      };
      
      const result = await riskAssessor.assess(document, context);
      
      expect(result.score).toBeGreaterThan(50);
      expect(result.level).toBe('HIGH');
      expect(result.highRiskIssues.length).toBeGreaterThan(0);
      
      const financialIssues = result.highRiskIssues.filter(
        issue => issue.category === 'FINANCIAL'
      );
      expect(financialIssues.length).toBeGreaterThan(0);
    });
    
    test('should handle documents without risks', async () => {
      const document = "This is a simple agreement with no risks.";
      const context = {
        tenantId: 'test-tenant-123',
        user: { id: 'test-user-123', permissions: [] }
      };
      
      const result = await riskAssessor.assess(document, context);
      
      expect(result.score).toBeLessThan(50);
      expect(result.highRiskIssues.length).toBe(0);
    });
  });
  
  describe('Audit Logging', () => {
    test('should call AuditLogger.log when audit enabled', async () => {
      // Spy on the mock
      const logSpy = jest.spyOn(AuditLogger, 'log');
      
      const document = "Test contract for audit logging.";
      const context = {
        tenantId: 'test-tenant-123',
        user: { id: 'test-user-123', permissions: [] }
      };
      
      await riskAssessor.assess(document, context);
      
      expect(logSpy).toHaveBeenCalled();
      logSpy.mockRestore();
    });
    
    test('should not audit when audit disabled', async () => {
      const noAuditAssessor = new RiskAssessor({ auditEnabled: false });
      const logSpy = jest.spyOn(AuditLogger, 'log');
      
      const document = "Test contract.";
      const context = {
        tenantId: 'test-tenant-123',
        user: { id: 'test-user-123', permissions: [] }
      };
      
      await noAuditAssessor.assess(document, context);
      
      expect(logSpy).not.toHaveBeenCalled();
      logSpy.mockRestore();
    });
  });
  
  describe('Utility Methods', () => {
    test('should return health status', () => {
      const health = riskAssessor.health();
      
      expect(health).toHaveProperty('status', 'OK');
      expect(health).toHaveProperty('timestamp');
      expect(typeof health.timestamp).toBe('string');
    });
  });
});
