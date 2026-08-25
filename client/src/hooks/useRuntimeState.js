import { runtimeStore } from '../state/runtimeStore.js';
import { createSliceHook } from './createSliceHook.js';
export const useRuntimeState = createSliceHook(runtimeStore);
export default useRuntimeState;
