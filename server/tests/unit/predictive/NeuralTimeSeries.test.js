/* eslint-disable */
import { expect } from 'chai';
import { NeuralTimeSeries } from '../../../algorithms/predictive/NeuralTimeSeries.js';

describe('🧠 NeuralTimeSeries - Unit Tests', () => {
  let neural;

  beforeEach(() => {
    neural = new NeuralTimeSeries({
      modelVersion: 'neural-2050-v6',
      layers: 48,
      parameters: '1.4B'
    });
  });

  it('should initialize with correct architecture', () => {
    expect(neural.layers).to.equal(48);
    expect(neoral.parameters).to.equal('1.4B');
  });

  it('should predict time series data', async () => {
    const historicalData = [100, 105, 110, 115, 120, 125, 130];
    const prediction = await neural.predict(historicalData, { horizon: 3 });
    
    expect(prediction).to.be.an('array');
    expect(prediction).to.have.length(3);
    prediction.forEach(value => {
      expect(value).to.be.a('number');
    });
  });

  it('should calculate confidence intervals', async () => {
    const historicalData = [100, 105, 110, 115, 120, 125, 130];
    const result = await neural.predictWithConfidence(historicalData, { horizon: 3 });
    
    expect(result).to.have.property('predictions');
    expect(result).to.have.property('lowerBound');
    expect(result).to.have.property('upperBound');
    expect(result.lowerBound).to.have.length(3);
    expect(result.upperBound).to.have.length(3);
  });

  it('should detect seasonality', async () => {
    const data = [100, 110, 100, 110, 100, 110, 100, 110];
    const seasonality = await neural.detectSeasonality(data);
    
    expect(seasonality).to.have.property('period');
    expect(seasonality).to.have.property('strength');
    expect(seasonality.strength).to.be.at.least(0.8);
  });
});
