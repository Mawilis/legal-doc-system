import { governanceStore } from '../state/governanceStore.js';
import { createSliceHook } from './createSliceHook.js';
export const useGovernanceState = createSliceHook(governanceStore);
export default useGovernanceState;
