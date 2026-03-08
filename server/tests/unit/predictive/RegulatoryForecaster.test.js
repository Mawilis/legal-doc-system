/* eslint-disable */
import { expect } from 'chai';
import { RegulatoryForecaster } from '../../../algorithms/predictive/RegulatoryForecaster.js';

describe('⚖️ RegulatoryForecaster - Unit Tests', () => {
  let forecaster;

  beforeEach(() => {
    forecaster = new RegulatoryForecaster({
      jurisdictions: 195,
      horizon: 24,
      quantumEnabled: true
    });
  });

  it('should initialize with global jurisdiction coverage', () => {
    expect(forecaster.jurisdictions).to.equal(195);
    expect(forecaster.horizon).to.equal(24);
  });

  it('should forecast regulatory changes', async () => {
    const forecast = await forecaster.forecastRegulations({
      jurisdiction: 'ZA',
      sector: 'financial'
    });
    
    expect(forecast).to.have.property('predictions');
    expect(forecast).to.have.property('confidence');
    expect(forecast).to.have.property('impactScore');
    expect(forecast.predictions).to.be.an('array');
  });

  it('should detect emerging regulations', async () => {
    const emerging = await forecaster.detectEmergingRegulations({
      jurisdictions: ['ZA', 'US', 'EU'],
      threshold: 0.8
    });
    
    expect(emerging).to.be.an('array');
    emerging.forEach(reg => {
      expect(reg).to.have.property('name');
      expect(reg).to.have.property('probability');
      expect(reg).to.have.property('timeline');
    });
  });

  it('should calculate compliance impact', async () => {
    const impact = await forecaster.calculateComplianceImpact({
      regulation: 'POPIA',
      organization: { size: 'enterprise', sector: 'legal' }
    });
    
    expect(impact).to.have.property('cost');
    expect(impact).to.have.property('timeline');
    expect(impact).to.have.property('risk');
    expect(impact.cost).to.be.a('number');
  });
});
