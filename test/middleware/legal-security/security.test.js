/* eslint-disable no-undef */
const { 
  quantumLegalSecurityMiddleware, 
  getQuantumSecurityMetrics 
} = require('../../../middleware/legal-security/security.js');

describe('Quantum Legal Security Middleware', () => {
  test('should have quantum security metrics function', () => {
    const metrics = getQuantumSecurityMetrics();
    expect(metrics).toHaveProperty('quantumMetrics');
    expect(metrics).toHaveProperty('quantumConfig');
    expect(metrics.quantumConfig.dataResidency).toBe('ZA');
  });
  
  test('should export quantum middleware function', () => {
    expect(typeof quantumLegalSecurityMiddleware).toBe('function');
    expect(quantumLegalSecurityMiddleware.length).toBe(3); // req, res, next
  });
  
  test('quantum config should be immutable', () => {
    const { SECURITY_CONFIG } = require('../../../middleware/legal-security/security.js');
    expect(Object.isFrozen(SECURITY_CONFIG)).toBe(true);
    expect(Object.isFrozen(SECURITY_CONFIG.CONTENT_SECURITY_POLICY)).toBe(true);
  });
});
