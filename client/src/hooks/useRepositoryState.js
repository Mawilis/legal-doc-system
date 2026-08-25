import { repositoryStore } from '../state/repositoryStore.js';
import { createSliceHook } from './createSliceHook.js';
export const useRepositoryState = createSliceHook(repositoryStore);
export default useRepositoryState;
