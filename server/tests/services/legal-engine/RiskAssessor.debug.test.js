/* eslint-disable no-undef */
const { RiskAssessor } = require('../../../services/legal-engine/RiskAssessor');

describe('RiskAssessor Debug', () => {
  test('can instantiate RiskAssessor', () => {
    const assessor = new RiskAssessor({ strictMode: true });
    expect(assessor).toBeDefined();
    expect(assessor.strictMode).toBe(true);
  });
  
  test('should have health method', () => {
    const assessor = new RiskAssessor();
    const health = assessor.health();
    expect(health).toHaveProperty('status');
    expect(health.status).toBe('OK');
  });
  
  test('assess method exists', () => {
    const assessor = new RiskAssessor();
    expect(typeof assessor.assess).toBe('function');
  });
});
