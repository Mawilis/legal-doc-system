import { predictionStore } from '../state/predictionStore.js';
import { createSliceHook } from './createSliceHook.js';
export const usePredictionState = createSliceHook(predictionStore);
export default usePredictionState;
