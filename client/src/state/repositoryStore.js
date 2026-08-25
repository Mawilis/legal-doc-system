/* eslint-disable */
import { createSliceStore } from './createSliceStore.js';
export const repositoryStore = createSliceStore('repository', {
  branch: 'main',
  commitHash: '0000000',
  uncommittedChanges: 0
});
export default repositoryStore;
