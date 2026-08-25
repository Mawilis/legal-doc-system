/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - USE EXECUTION HOOK [V1.0.0-PRODUCTION-GRADE]                                                                               ║
 * ║ [EPITOME: OPERATOR COMMAND DISPATCHER | STATUS TRACKING & AUDIT FEED LOGGING]                                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-PRODUCTION-GRADE | BILLION-DOLLAR ENTERPRISE SOFTWARE | BIBLICAL WORTH COMPLIANT                                       ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/hooks/useExecution.js                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Enforced that UI button triggers dispatch ExecutionContext payloads seamlessly.                     ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Encapsulated dispatch state management and execution audit trails.                           ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { useState, useCallback } from 'react';
import { dispatchExecutionContext } from '../services/executionService';

/**
 * @function useExecution
 * @description Hook providing execution dispatch capabilities to UI components.
 * @returns {Object} `{ executeCommand, isExecuting, lastResult, error }`
 * @collaboration Connects UI operator buttons to the POST /execution pipeline.
 */
export function useExecution() {
  const [isExecuting, setIsExecuting] = useState(false);
  const [lastResult, setLastResult] = useState(null);
  const [error, setError] = useState(null);

  const executeCommand = useCallback(async (actionName, metadata = {}) => {
    setIsExecuting(true);
    setError(null);
    try {
      const result = await dispatchExecutionContext(actionName, metadata);
      setLastResult(result);
      return result;
    } catch (err) {
      console.error('[WILSY-USE-EXECUTION] Dispatch error:', err);
      setError(err.message);
      throw err;
    } finally {
      setIsExecuting(false);
    }
  }, []);

  return { executeCommand, isExecuting, lastResult, error };
}
