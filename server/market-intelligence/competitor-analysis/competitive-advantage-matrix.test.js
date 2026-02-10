/* eslint-env jest */
const CompetitiveAdvantageMatrix = require('./competitive-advantage-matrix');

// Mock dependencies
jest.mock('../../utils/logger', () => ({
  info: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  debug: jest.fn()
}));

jest.mock('../../utils/auditLogger', () => ({
  audit: jest.fn(),
  security: jest.fn(),
  compliance: jest.fn()
}));

jest.mock('../../utils/cryptoUtils', () => ({
  encrypt: jest.fn((data) => `encrypted_${data}`),
  decrypt: jest.fn((data) => data.replace('encrypted_', '')),
  hash: jest.fn(() => 'hashed_value')
}));

describe('CompetitiveAdvantageMatrix', () => {
  let matrix;

  beforeEach(() => {
    matrix = new CompetitiveAdvantageMatrix();
    jest.clearAllMocks();
  });

  describe('Initialization', () => {
    test('should initialize with empty matrix', () => {
      expect(matrix.getMatrix()).toEqual({});
    });
  });

  describe('addCompetitor', () => {
    test('should add competitor to matrix', () => {
      const competitor = {
        id: 'comp1',
        name: 'Competitor 1',
        strengths: ['tech', 'team'],
        weaknesses: ['market', 'funding']
      };

      matrix.addCompetitor(competitor);
      const result = matrix.getMatrix();

      expect(result['comp1']).toBeDefined();
      expect(result['comp1'].name).toBe('Competitor 1');
    });
  });

  describe('analyzeAdvantage', () => {
    test('should calculate competitive advantage score', () => {
      const competitor = {
        id: 'comp1',
        name: 'Competitor 1',
        strengths: ['tech', 'team'],
        weaknesses: ['market']
      };

      matrix.addCompetitor(competitor);
      const score = matrix.analyzeAdvantage('comp1');

      expect(typeof score).toBe('number');
      expect(score).toBeGreaterThanOrEqual(0);
      expect(score).toBeLessThanOrEqual(100);
    });
  });

  describe('generateReport', () => {
    test('should generate valid report', () => {
      const competitors = [
        {
          id: 'comp1',
          name: 'Competitor 1',
          strengths: ['tech'],
          weaknesses: ['market']
        },
        {
          id: 'comp2',
          name: 'Competitor 2',
          strengths: ['market'],
          weaknesses: ['tech']
        }
      ];

      competitors.forEach(comp => matrix.addCompetitor(comp));
      const report = matrix.generateReport();

      expect(report).toHaveProperty('timestamp');
      expect(report).toHaveProperty('analysis');
      expect(report).toHaveProperty('recommendations');
      expect(Array.isArray(report.competitors)).toBe(true);
    });
  });

  describe('Security and Compliance', () => {
    test('should handle encrypted data', () => {
      const encryptedCompetitor = {
        id: 'encrypted_comp1',
        name: 'encrypted_Competitor X',
        strengths: ['encrypted_tech'],
        weaknesses: ['encrypted_market']
      };

      matrix.addCompetitor(encryptedCompetitor);
      
      // The cryptoUtils mock should be called
      const cryptoUtils = require('../../utils/cryptoUtils');
      expect(cryptoUtils.decrypt).toHaveBeenCalled();
    });

    test('should audit analysis operations', () => {
      const competitor = {
        id: 'comp1',
        name: 'Competitor 1',
        strengths: ['tech'],
        weaknesses: ['market']
      };

      matrix.addCompetitor(competitor);
      matrix.analyzeAdvantage('comp1');

      const auditLogger = require('../../utils/auditLogger');
      expect(auditLogger.audit).toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    test('should handle non-existent competitor', () => {
      expect(() => {
        matrix.analyzeAdvantage('nonexistent');
      }).toThrow('Competitor not found');
    });

    test('should handle invalid competitor data', () => {
      expect(() => {
        matrix.addCompetitor({ invalid: 'data' });
      }).toThrow('Invalid competitor data');
    });
  });
});
