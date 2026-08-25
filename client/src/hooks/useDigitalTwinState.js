import { digitalTwinStore } from '../state/digitalTwinStore.js';
import { createSliceHook } from './createSliceHook.js';
export const useDigitalTwinState = createSliceHook(digitalTwinStore);
export default useDigitalTwinState;
