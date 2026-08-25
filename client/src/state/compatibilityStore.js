/* eslint-disable */
import { createSliceStore } from './createSliceStore.js';
export const compatibilityStore = createSliceStore('compatibility', {
  nativeEngines: 0,
  matrixStatus: 'UNCHECKED',
  abiVersion: 'FG211-FROZEN'
});
export default compatibilityStore;
