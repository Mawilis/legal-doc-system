/* eslint-disable */
import { runtimeStore } from './runtimeStore.js';
import { repositoryStore } from './repositoryStore.js';
import { governanceStore } from './governanceStore.js';
import { predictionStore } from './predictionStore.js';
import { eventStore } from './eventStore.js';
import { artifactStore } from './artifactStore.js';
import { documentationStore } from './documentationStore.js';
import { digitalTwinStore } from './digitalTwinStore.js';
import { compatibilityStore } from './compatibilityStore.js';
import { versionStore } from './versionStore.js';
import { reportStore } from './reportStore.js';
import { executionStore } from './executionStore.js';

export const allStores = {
  runtime: runtimeStore,
  repository: repositoryStore,
  governance: governanceStore,
  predictions: predictionStore,
  events: eventStore,
  artifacts: artifactStore,
  documentation: documentationStore,
  digitalTwin: digitalTwinStore,
  compatibility: compatibilityStore,
  versioning: versionStore,
  reports: reportStore,
  executions: executionStore
};

/**
 * Hydrates every store slice from the Authoritative Dashboard Contract snapshot.
 */
export const hydrateFullDashboard = (contractData) => {
  if (!contractData) return;
  Object.keys(allStores).forEach((sliceKey) => {
    if (contractData[sliceKey] !== undefined) {
      allStores[sliceKey].setInitialState(contractData[sliceKey]);
    }
  });
};

/**
 * Route incoming dynamic streaming delta payloads directly to the target slice store.
 */
export const dispatchStreamDelta = (type, payload) => {
  const [sliceKey] = type.split('.');
  if (allStores[sliceKey]) {
    allStores[sliceKey].mergeDelta(payload);
  }
};
