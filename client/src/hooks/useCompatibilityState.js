import { compatibilityStore } from '../state/compatibilityStore.js';
import { createSliceHook } from './createSliceHook.js';
export const useCompatibilityState = createSliceHook(compatibilityStore);
export default useCompatibilityState;
