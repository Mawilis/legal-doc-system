import { reportStore } from '../state/reportStore.js';
import { createSliceHook } from './createSliceHook.js';
export const useReportState = createSliceHook(reportStore);
export default useReportState;
