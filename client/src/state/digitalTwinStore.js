/* eslint-disable */
import { createSliceStore } from './createSliceStore.js';
export const digitalTwinStore = createSliceStore('digitalTwin', {
  repositorySync: 'UNSYNCED',
  stateDrift: '0.00%',
  lastMirrorHash: 'none'
});
export default digitalTwinStore;
