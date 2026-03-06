/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ TYPESCRIPT DEFINITIONS - QUANTUM TEST FORTRESS                           ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import mongoose from 'mongoose';

export interface QuantumState {
  connectionId: string | null;
  durationMs: number | null;
  totalOperations: number;
  modelsCleaned: string[];
  collectionsCleared: string[];
  errors: any[];
  operations: QuantumOperation[];
}

export interface QuantumOperation {
  event: string;
  timestamp: string;
  performanceMs: number;
  [key: string]: any;
}

export interface ClearOptions {
  skipModels?: string[];
  forensicLog?: boolean;
}

export interface TransactionContext {
  session: mongoose.ClientSession | null;
  start(): Promise<mongoose.ClientSession>;
  commit(): Promise<void>;
  rollback(): Promise<void>;
}

export const FORENSIC_EVENTS: {
  CONNECTION_STARTED: 'CONNECTION_STARTED';
  CONNECTION_ESTABLISHED: 'CONNECTION_ESTABLISHED';
  CONNECTION_FAILED: 'CONNECTION_FAILED';
  CONNECTION_CLOSED: 'CONNECTION_CLOSED';
  COLLECTION_CLEARED: 'COLLECTION_CLEARED';
  MODEL_CLEANUP: 'MODEL_CLEANUP';
  TRANSACTION_START: 'TRANSACTION_START';
  TRANSACTION_COMMIT: 'TRANSACTION_COMMIT';
  TRANSACTION_ABORT: 'TRANSACTION_ABORT';
};

export const QUANTUM_CONFIG: {
  CONNECTION_RETRIES: number;
  RETRY_BACKOFF_MS: number;
  CONNECTION_TIMEOUT_MS: number;
  MAX_POOL_SIZE: number;
  MIN_POOL_SIZE: number;
  SOCKET_TIMEOUT_MS: number;
  FORENSIC_LOGGING: boolean;
};

export function setupTestDB(): Promise<string>;
export function teardownTestDB(): Promise<void>;
export function clearCollections(options?: ClearOptions): Promise<string[]>;
export function cleanupModels(modelNames: string | string[]): Promise<string[]>;
export function getQuantumState(): QuantumState | null;
export function resetQuantumState(): void;
export function createTransactionContext(): TransactionContext;
export function measurePerformance<T>(fn: () => Promise<T>, name: string): Promise<T>;

declare const _default: {
  setupTestDB: typeof setupTestDB;
  teardownTestDB: typeof teardownTestDB;
  clearCollections: typeof clearCollections;
  cleanupModels: typeof cleanupModels;
  getQuantumState: typeof getQuantumState;
  resetQuantumState: typeof resetQuantumState;
  createTransactionContext: typeof createTransactionContext;
  measurePerformance: typeof measurePerformance;
  FORENSIC_EVENTS: typeof FORENSIC_EVENTS;
  QUANTUM_CONFIG: typeof QUANTUM_CONFIG;
};

export default _default;
  