import { versionStore } from '../state/versionStore.js';
import { createSliceHook } from './createSliceHook.js';
export const useVersionState = createSliceHook(versionStore);
export default useVersionState;
