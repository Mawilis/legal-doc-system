/* eslint-disable */
import { createSliceStore } from './createSliceStore.js';
export const predictionStore = createSliceStore('predictions', {
  technicalDebtScore: '0.00%',
  repositoryRiskLevel: 'Zero Risk',
  anomalyProbability: '0.000%'
});
export default predictionStore;
