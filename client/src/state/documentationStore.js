/* eslint-disable */
import { createSliceStore } from './createSliceStore.js';
export const documentationStore = createSliceStore('documentation', {
  coveragePercent: 0.0,
  status: 'UNAUDITED',
  unvalidatedFiles: 0
});
export default documentationStore;
