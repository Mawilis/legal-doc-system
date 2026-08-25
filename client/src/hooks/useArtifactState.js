import { artifactStore } from '../state/artifactStore.js';
import { createSliceHook } from './createSliceHook.js';
export const useArtifactState = createSliceHook(artifactStore);
export default useArtifactState;
