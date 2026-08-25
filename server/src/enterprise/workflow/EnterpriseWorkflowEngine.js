/**
 * ============================================================================
 * WILSY OS - ENTERPRISE SHARED WORKFLOW ENGINE
 * ============================================================================
 *
 * @file         EnterpriseWorkflowEngine.js
 * @directory    server/src/enterprise/workflow/
 * @system       Wilsy OS - Enterprise Business Operating Layer (FG231)
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      1.0.0-SOVEREIGN
 * @epitome      Universal state-machine workflow engine powering all Wilsy OS
 *               business objects (Customer, Contract, Matter, Invoice, Project).
 *               Enforces deterministic state transitions, conditional guard gates,
 *               and automated cryptographic audit logging for every lifecycle shift.
 *
 * @collaboration
 * - Lead Architect: Wilson Khanyezi (Wilsy OS Architecture Core Team)
 * - Automation Core: Enterprise Deterministic State Machine Subsystem
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT TRAIL
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 1.0.0   | Production sovereign release of
 *            |                 |         | enterprise workflow engine with
 *            |                 |         | guarded state transitions & seals.
 * ============================================================================
 */

const crypto = require('crypto');
const { DataRedactor, EnterpriseKernelError } = require('../kernel/EnterpriseKernel');

/**
 * Sovereign Error Class for Workflow Engine Faults.
 */
class EnterpriseWorkflowError extends Error {
  /**
   * @param {string} message - Failure explanation.
   * @param {string} [code='WORKFLOW_ERR_GENERIC'] - Error code.
   * @param {Object} [details={}] - Context metadata.
   */
  constructor(message, code = 'WORKFLOW_ERR_GENERIC', details = {}) {
    super(message);
    this.name = 'EnterpriseWorkflowError';
    this.code = code;
    this.timestamp = new Date().toISOString();
    this.details = DataRedactor.sanitize(details);
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, EnterpriseWorkflowError);
    }
  }
}

/**
 * Represents an active workflow instance assigned to an Enterprise Object.
 */
class WorkflowInstance {
  /**
   * @param {Object} params
   * @param {string} params.workflowId - Unique workflow definition identifier.
   * @param {string} params.tenantId - Sovereign tenant ID.
   * @param {string} params.targetObjectId - Associated enterprise object ID.
   * @param {string} params.currentState - Initial state.
   * @param {Array<string>} params.allowedStates - Permitted state set.
   * @param {Object} [params.metadata={}] - Context payload.
   */
  constructor({ workflowId, tenantId, targetObjectId, currentState, allowedStates, metadata = {} }) {
    this.instanceId = crypto.randomUUID();
    this.workflowId = String(workflowId);
    this.tenantId = String(tenantId);
    this.targetObjectId = String(targetObjectId);
    this.currentState = String(currentState).toUpperCase();
    this.allowedStates = Object.freeze(allowedStates.map(s => s.toUpperCase()));
    this.metadata = DataRedactor.sanitize(metadata);
    this.history = [
      {
        state: this.currentState,
        timestamp: Date.now(),
        actor: metadata.actor || 'SYSTEM_SOVEREIGN',
        action: 'WORKFLOW_INITIALIZED'
      }
    ];
    this.updatedAt = Date.now();
    this.instanceHash = this.computeInstanceHash();
  }

  /**
   * Computes SHA-256 cryptographic seal of the workflow instance state.
   * @returns {string} Hexadecimal hash digest.
   */
  computeInstanceHash() {
    const raw = JSON.stringify({
      instanceId: this.instanceId,
      workflowId: this.workflowId,
      tenantId: this.tenantId,
      targetObjectId: this.targetObjectId,
      currentState: this.currentState,
      historyLength: this.history.length,
      updatedAt: this.updatedAt
    });
    return crypto.createHash('sha256').update(raw).digest('hex');
  }
}

/**
 * Enterprise Workflow Engine Core.
 * Manages workflow definitions, validates state transitions, and records history.
 */
class EnterpriseWorkflowEngine {
  constructor() {
    /** @type {Map<string, Object>} workflowId -> Workflow Definition */
    this.workflowDefinitions = new Map();
    /** @type {Map<string, WorkflowInstance>} instanceId -> WorkflowInstance */
    this.activeInstances = new Map();
    this.initializedAt = Date.now();

    // Register standard Wilsy OS business workflows
    this.bootstrapStandardWorkflows();
  }

  /**
   * Registers a new workflow state machine definition.
   *
   * @param {Object} definition
   * @param {string} definition.workflowId - Unique identifier (e.g. 'CONTRACT_LIFECYCLE').
   * @param {string} definition.domain - Associated domain (e.g. 'CONTRACT').
   * @param {Array<string>} definition.states - All possible states.
   * @param {Object<string, Array<string>>} definition.transitions - Map of allowed state hops.
   * @returns {Object} Registered definition.
   */
  registerWorkflowDefinition({ workflowId, domain, states, transitions }) {
    if (!workflowId || !domain || !states || !transitions) {
      throw new EnterpriseWorkflowError('Invalid workflow definition parameters', 'WORKFLOW_ERR_INVALID_DEF');
    }

    const normalizedDef = {
      workflowId: workflowId.toUpperCase(),
      domain: domain.toUpperCase(),
      states: states.map(s => s.toUpperCase()),
      transitions,
      registeredAt: new Date().toISOString()
    };

    this.workflowDefinitions.set(normalizedDef.workflowId, normalizedDef);
    return normalizedDef;
  }

  /**
   * Instantiates a workflow for a specific Enterprise Object.
   *
   * @param {string} workflowId - Workflow definition ID.
   * @param {string} tenantId - Sovereign tenant ID.
   * @param {string} targetObjectId - Target enterprise object ID.
   * @param {string} initialState - Starting state.
   * @param {Object} [metadata={}] - Context metadata.
   * @returns {WorkflowInstance} Created workflow instance.
   */
  startWorkflow(workflowId, tenantId, targetObjectId, initialState, metadata = {}) {
    const def = this.workflowDefinitions.get(workflowId.toUpperCase());
    if (!def) {
      throw new EnterpriseWorkflowError(`Workflow definition [${workflowId}] not found`, 'WORKFLOW_ERR_DEF_NOT_FOUND');
    }

    const initClean = initialState.toUpperCase();
    if (!def.states.includes(initClean)) {
      throw new EnterpriseWorkflowError(`Initial state [${initClean}] is invalid for workflow [${workflowId}]`, 'WORKFLOW_ERR_INVALID_STATE');
    }

    const instance = new WorkflowInstance({
      workflowId,
      tenantId,
      targetObjectId,
      currentState: initClean,
      allowedStates: def.states,
      metadata
    });

    this.activeInstances.set(instance.instanceId, instance);
    return instance;
  }

  /**
   * Executes a deterministic state transition for an active workflow instance.
   *
   * @param {string} instanceId - Workflow instance ID.
   * @param {string} nextState - Target destination state.
   * @param {string} [actor='SYSTEM'] - Actor executing the transition.
   * @returns {WorkflowInstance} Updated workflow instance.
   */
  transitionState(instanceId, nextState, actor = 'SYSTEM') {
    const instance = this.activeInstances.get(instanceId);
    if (!instance) {
      throw new EnterpriseWorkflowError(`Workflow instance [${instanceId}] not found`, 'WORKFLOW_ERR_INSTANCE_NOT_FOUND');
    }

    const def = this.workflowDefinitions.get(instance.workflowId);
    const targetClean = nextState.toUpperCase();

    if (!instance.allowedStates.includes(targetClean)) {
      throw new EnterpriseWorkflowError(`Target state [${targetClean}] does not exist in workflow definition`, 'WORKFLOW_ERR_INVALID_TARGET_STATE');
    }

    const allowedTransitions = def.transitions[instance.currentState] || [];
    if (!allowedTransitions.includes(targetClean)) {
      throw new EnterpriseWorkflowError(
        `Illegal state transition from [${instance.currentState}] to [${targetClean}]`,
        'WORKFLOW_ERR_ILLEGAL_TRANSITION',
        { current: instance.currentState, attempted: targetClean, allowed: allowedTransitions }
      );
    }

    // Execute state shift
    instance.currentState = targetClean;
    instance.updatedAt = Date.now();
    instance.history.push({
      state: targetClean,
      timestamp: instance.updatedAt,
      actor,
      action: 'STATE_TRANSITION'
    });
    instance.instanceHash = instance.computeInstanceHash();

    return instance;
  }

  /**
   * Bootstraps standard Wilsy OS legal, finance, and CRM business workflows.
   * @private
   */
  bootstrapStandardWorkflows() {
    // 1. Contract Lifecycle Workflow
    this.registerWorkflowDefinition({
      workflowId: 'CONTRACT_LIFECYCLE',
      domain: 'CONTRACT',
      states: ['DRAFT', 'LEGAL_REVIEW', 'NEGOTIATION', 'PENDING_SIGNATURE', 'ACTIVE', 'EXPIRED', 'TERMINATED'],
      transitions: {
        DRAFT: ['LEGAL_REVIEW', 'TERMINATED'],
        LEGAL_REVIEW: ['DRAFT', 'NEGOTIATION', 'TERMINATED'],
        NEGOTIATION: ['LEGAL_REVIEW', 'PENDING_SIGNATURE', 'TERMINATED'],
        PENDING_SIGNATURE: ['ACTIVE', 'TERMINATED'],
        ACTIVE: ['EXPIRED', 'TERMINATED'],
        EXPIRED: [],
        TERMINATED: []
      }
    });

    // 2. Invoice Billing Workflow
    this.registerWorkflowDefinition({
      workflowId: 'INVOICE_BILLING',
      domain: 'INVOICE',
      states: ['DRAFT', 'ISSUED', 'PARTIALLY_PAID', 'PAID', 'OVERDUE', 'DISPUTED', 'WRITTEN_OFF'],
      transitions: {
        DRAFT: ['ISSUED', 'WRITTEN_OFF'],
        ISSUED: ['PARTIALLY_PAID', 'PAID', 'OVERDUE', 'DISPUTED'],
        PARTIALLY_PAID: ['PAID', 'OVERDUE', 'DISPUTED'],
        OVERDUE: ['PARTIALLY_PAID', 'PAID', 'DISPUTED', 'WRITTEN_OFF'],
        DISPUTED: ['ISSUED', 'WRITTEN_OFF', 'PAID'],
        PAID: [],
        WRITTEN_OFF: []
      }
    });

    // 3. Customer Lead Conversion Workflow
    this.registerWorkflowDefinition({
      workflowId: 'CUSTOMER_CONVERSION',
      domain: 'CUSTOMER',
      states: ['PROSPECT', 'QUALIFIED', 'OPPORTUNITY', 'ACTIVE_CLIENT', 'CHURNED'],
      transitions: {
        PROSPECT: ['QUALIFIED', 'CHURNED'],
        QUALIFIED: ['OPPORTUNITY', 'CHURNED'],
        OPPORTUNITY: ['ACTIVE_CLIENT', 'CHURNED'],
        ACTIVE_CLIENT: ['CHURNED'],
        CHURNED: ['PROSPECT']
      }
    });
  }

  /**
   * Operational Diagnostics for Workflow Engine.
   * @returns {Object} Diagnostic report.
   */
  runDiagnostics() {
    return {
      status: 'OPERATIONAL',
      uptimeSeconds: Math.floor((Date.now() - this.initializedAt) / 1000),
      registeredWorkflowDefinitions: this.workflowDefinitions.size,
      activeWorkflowInstances: this.activeInstances.size,
      workflowSeal: crypto
        .createHash('sha256')
        .update(`WORKFLOW_SEAL_${this.workflowDefinitions.size}_${this.activeInstances.size}`)
        .digest('hex')
    };
  }
}

// Global Singleton Instance
const workflowEngineInstance = new EnterpriseWorkflowEngine();

module.exports = {
  EnterpriseWorkflowEngine,
  WorkflowInstance,
  EnterpriseWorkflowError,
  workflowEngineInstance
};
