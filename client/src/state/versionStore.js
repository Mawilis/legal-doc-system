/* eslint-disable */
import { createSliceStore } from './createSliceStore.js';
export const versionStore = createSliceStore('versioning', {
  kernel: '1.0.0-PRODUCTION',
  platform: '1.0.0-PRODUCTION',
  phase: 'PHASE VII // EOS'
});
export default versionStore;
