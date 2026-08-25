import { documentationStore } from '../state/documentationStore.js';
import { createSliceHook } from './createSliceHook.js';
export const useDocumentationState = createSliceHook(documentationStore);
export default useDocumentationState;
