/* eslint-disable */
import { createSliceStore } from './createSliceStore.js';
export const executionStore = createSliceStore('executions', {
  lastExecutionId: null,
  activeExecutionsCount: 0,
  status: 'IDLE'
});
export default executionStore;
