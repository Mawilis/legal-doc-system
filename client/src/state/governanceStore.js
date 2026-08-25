/* eslint-disable */
import { createSliceStore } from './createSliceStore.js';
export const governanceStore = createSliceStore('governance', {
  approvedCount: 0,
  blockedCount: 0,
  status: 'PENDING_CERTIFICATION',
  policyEnforcement: 'STRICT'
});
export default governanceStore;
