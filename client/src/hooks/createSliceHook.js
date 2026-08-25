/* eslint-disable */
import { useSyncExternalStore } from 'react';

export const createSliceHook = (store) => {
  return () => {
    const state = useSyncExternalStore(store.subscribe, store.getSnapshot);
    const metadata = store.getMetaData();
    return { data: state, metadata };
  };
};
