import { eventStore } from '../state/eventStore.js';
import { createSliceHook } from './createSliceHook.js';
export const useEventState = createSliceHook(eventStore);
export default useEventState;
