/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - DYNAMIC QUICK PANEL [V34.0.0-OMEGA-FINAL]                                                                                   ║
 * ║ [LEARNING ALGORITHM | FREQUENTLY USED COMMANDS | OMNIVERSAL TELEMETRY | BEHAVIORAL INTELLIGENCE]                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 34.0.0-OMEGA-FINAL | PRODUCTION READY | BILLION DOLLAR SPEC                                                                   ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/sovereign/QuickPanel.jsx                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated 10/10 production readiness, telemetry helper unification, and ARIA accessibility.    ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Implemented frequency sorting and action forwarding.                                            ║
 * ║ • AI Engineering (Gemini) - BIBLICAL UPGRADE: Injected async Telemetry broadcasting. Quick Panel strikes now appear in the Live Feed.  ║
 * ║ • AI Engineering (Gemini) - OMEGA FINAL: Integrated CSS Module binding, execution safety try/catch, and ARIA roles for F500 specs.     ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { useCallback, useMemo, useState } from 'react';
import {
  Activity,
  Brain,
  CheckCircle2,
  Command,
  Gauge,
  RotateCcw,
  ShieldCheck,
  Sparkles,
  Zap
} from 'lucide-react';
import { useCommandUsage } from '../../contexts/CommandUsageContext';
import { broadcastTelemetry } from '../../utils/telemetryHelper'; // 🛡️ Institutional Telemetry Bridge
import styles from './QuickPanel.module.css';

/**
 * @function classifyCommand
 * @description Converts a command into a boardroom-readable operating class without hard-coded totals.
 * @param {Object} command - Command surface item from FounderDashboard.
 * @returns {string} Institutional class used for behavioral grouping.
 * @collaboration Wilson Khanyezi mandated live command truth instead of stale counters.
 */
const classifyCommand = (command = {}) => {
  if (command.id?.startsWith('CAPABILITY_')) return 'Capability';
  if (command.id?.startsWith('MODULE_')) return 'Module';
  if (command.description?.toLowerCase?.().includes('report')) return 'Report';
  if (command.handler) return 'Action';
  return 'Command';
};

/**
 * @function getCommandUsageCount
 * @description Reads command usage from the persistent behavioral model.
 * @param {Map} usageMap - CommandUsageContext persistence map.
 * @param {string} commandId - Command identifier.
 * @returns {number} Recorded usage count.
 * @collaboration Keeps the quick surface evidence-backed and trained by real operator behavior.
 */
const getCommandUsageCount = (usageMap, commandId) => Number(usageMap?.get(commandId) || 0);

/**
 * @function buildRecommendedCommands
 * @description Selects high-value commands when the behavioral model has not learned enough yet.
 * @param {Array} commands - Full command mesh.
 * @param {Map} usageMap - Command usage history.
 * @param {number} limit - Maximum commands to return.
 * @returns {Array} Recommended commands.
 * @collaboration Prevents the panel from becoming a dead placeholder before usage telemetry matures.
 */
const buildRecommendedCommands = (commands = [], usageMap = new Map(), limit = 6) => {
  const priority = {
    Capability: 4,
    Report: 3,
    Action: 2,
    Module: 1,
    Command: 0
  };

  return [...commands]
    .filter((command) => typeof command?.handler === 'function')
    .sort((left, right) => {
      const leftScore = priority[classifyCommand(left)] + getCommandUsageCount(usageMap, left.id);
      const rightScore = priority[classifyCommand(right)] + getCommandUsageCount(usageMap, right.id);
      return rightScore - leftScore || String(left.label).localeCompare(String(right.label));
    })
    .slice(0, limit);
};

/**
 * @function buildQuickPanelMetrics
 * @description Computes live behavioral and command mesh metrics from actual props and usage storage.
 * @param {Array} commands - Full command mesh.
 * @param {Array} frequentCommands - Learned frequent commands.
 * @param {Map} usageMap - Command usage history.
 * @returns {Object} Metric packet for the quick panel.
 * @collaboration Replaces stale static command numbers with real operating telemetry.
 */
const buildQuickPanelMetrics = (commands = [], frequentCommands = [], usageMap = new Map()) => {
  const executionCount = Array.from(usageMap.values()).reduce((sum, value) => sum + Number(value || 0), 0);
  const trainedCount = Array.from(usageMap.keys()).filter((id) => commands.some((command) => command.id === id)).length;
  const capabilityCount = commands.length;
  const behaviorScore = capabilityCount
    ? Math.min(100, Math.round(((trainedCount / capabilityCount) * 60) + Math.min(executionCount, 40)))
    : 0;

  return {
    behaviorScore,
    capabilityCount,
    executionCount,
    frequentCount: frequentCommands.length,
    trainedCount
  };
};

/**
 * @function buildCommandClassMatrix
 * @description Creates a real command class distribution for investor-grade command transparency.
 * @param {Array} commands - Full command mesh.
 * @returns {Array} Ordered command class counts.
 * @collaboration Shows the OS breadth as evidence, not fixed marketing copy.
 */
const buildCommandClassMatrix = (commands = []) => {
  const matrix = commands.reduce((acc, command) => {
    const group = classifyCommand(command);
    acc[group] = (acc[group] || 0) + 1;
    return acc;
  }, {});

  return Object.entries(matrix)
    .sort((left, right) => right[1] - left[1])
    .map(([label, value]) => ({ label, value }));
};

/**
 * @component QuickPanel
 * @description Behavioral command cockpit that surfaces learned commands, live capability counts,
 * execution receipts, and fallback high-value actions when the operator model is still learning.
 * @param {Object} props - Component properties.
 * @param {Array} props.allCommands - Live command mesh supplied by FounderDashboard.
 * @param {Function} props.onExecute - Command execution bridge.
 * @param {string} props.sessionId - Optional session anchor for forensic telemetry.
 * @returns {JSX.Element} Quick command intelligence panel.
 * @collaboration Wilson Khanyezi requested an operating system surface, not a passive component.
 */
const QuickPanel = ({ allCommands = [], onExecute, sessionId }) => {
  const { getFrequentCommands, recordCommand, resetUsage, usageMap } = useCommandUsage();
  const [executionReceipt, setExecutionReceipt] = useState(null);

  const frequentIds = getFrequentCommands(8);
  const frequentCommands = useMemo(() => {
    return frequentIds
      .map(id => allCommands.find(cmd => cmd.id === id))
      .filter(Boolean);
  }, [frequentIds, allCommands]);

  const recommendedCommands = useMemo(
    () => buildRecommendedCommands(allCommands, usageMap, 6),
    [allCommands, usageMap]
  );

  const visibleCommands = frequentCommands.length ? frequentCommands : recommendedCommands;
  const metrics = useMemo(
    () => buildQuickPanelMetrics(allCommands, frequentCommands, usageMap),
    [allCommands, frequentCommands, usageMap]
  );
  const classMatrix = useMemo(() => buildCommandClassMatrix(allCommands), [allCommands]);
  const isLearningMode = frequentCommands.length === 0;

  /**
   * @function handleExecute
   * @description Executes a quick command with forensic telemetry, receipt state, and failure containment.
   * @param {Object} cmd - Command selected by the operator.
   * @returns {Promise<void>} Resolves after command execution and telemetry broadcast.
   * @collaboration Every command strike must leave evidence, duration, and operator context.
   */
  const handleExecute = useCallback(async (cmd) => {
    const startedAt = performance.now();
    recordCommand(cmd.id);
    setExecutionReceipt({
      command: cmd.label,
      mode: classifyCommand(cmd),
      status: 'RUNNING',
      message: 'Execution strike in progress.'
    });

    try {
      // 🛡️ FORENSIC BROADCAST: Push to the global root before execution
      await broadcastTelemetry('GLOBAL_ROOT', 'QUICK_PANEL', 'COMMAND_EXECUTED', cmd.id, {
        commandClass: classifyCommand(cmd),
        commandCount: allCommands.length,
        sessionId: sessionId || 'QUICK_PANEL',
        timestamp: new Date().toISOString()
      });

      // ⚙️ INITIATE STRIKE
      const result = onExecute ? onExecute(cmd.handler) : cmd.handler?.();
      if (result && typeof result.then === 'function') {
        await result;
      }

      const duration = Math.max(1, Math.round(performance.now() - startedAt));
      setExecutionReceipt({
        command: cmd.label,
        duration,
        mode: classifyCommand(cmd),
        status: 'SEALED',
        message: `Forensic command receipt sealed in ${duration}ms.`
      });
    } catch (err) {
      // 💥 FRACTURE CONTAINMENT: Log and broadcast the failure without crashing the dashboard
      console.error('💥 [QuickPanel] Execution fracture:', err.message);
      await broadcastTelemetry('GLOBAL_ROOT', 'QUICK_PANEL', 'COMMAND_FAILURE', cmd.id, { error: err.message });
      setExecutionReceipt({
        command: cmd.label,
        mode: classifyCommand(cmd),
        status: 'FRACTURE',
        message: err.message || 'Command failed before completion.'
      });
    }
  }, [allCommands.length, onExecute, recordCommand, sessionId]);

  /**
   * @function handleResetLearning
   * @description Clears the behavioral model and records a local receipt for the reset.
   * @returns {void}
   * @collaboration Gives the founder direct control over command training evidence.
   */
  const handleResetLearning = useCallback(() => {
    resetUsage();
    setExecutionReceipt({
      command: 'Behavioral model reset',
      mode: 'Learning',
      status: 'RESET',
      message: 'Quick Panel learning baseline restored.'
    });
  }, [resetUsage]);

  return (
    <div className={styles.panel}>
      <div className={styles.sovereignAura} />
      <div className={styles.header}>
        <div>
          <div className={styles.title}>
            BEHAVIORAL QUICK PANEL
          </div>
          <p className={styles.subtitle}>
            Live command mesh, trained behavior and execution receipts.
          </p>
        </div>
        <div className={styles.statusPill}>
          {isLearningMode ? <Brain size={13} /> : <Activity size={13} />}
          {isLearningMode ? 'LEARNING' : 'TRAINED'}
        </div>
      </div>

      <div className={styles.metricsGrid} aria-label="Quick panel command intelligence">
        <div className={styles.metricCard}>
          <Command size={15} />
          <span>Capabilities</span>
          <strong>{metrics.capabilityCount}</strong>
        </div>
        <div className={styles.metricCard}>
          <Gauge size={15} />
          <span>Trained</span>
          <strong>{metrics.trainedCount}</strong>
        </div>
        <div className={styles.metricCard}>
          <Zap size={15} />
          <span>Executions</span>
          <strong>{metrics.executionCount}</strong>
        </div>
        <div className={styles.metricCard}>
          <ShieldCheck size={15} />
          <span>Readiness</span>
          <strong>{metrics.behaviorScore}%</strong>
        </div>
      </div>

      {isLearningMode ? (
        <div className={styles.modeNote}>
          <Sparkles size={14} />
          <span>Behavioral history is still forming. Showing high-value operating commands from the live mesh.</span>
        </div>
      ) : null}

      <div className={styles.sectionHeader}>
        <span>{isLearningMode ? 'RECOMMENDED STRIKES' : 'FREQUENT STRIKES'}</span>
        <strong>{visibleCommands.length}</strong>
      </div>

      <div className={styles.commandList}>
        {visibleCommands.map(cmd => (
          <button
            key={cmd.id}
            onClick={() => handleExecute(cmd)}
            className={styles.commandButton}
            aria-label={`Execute ${cmd.label}`}
          >
            <div className={styles.icon}>{cmd.icon}</div>
            <div className={styles.textBlock}>
              <span className={styles.label}>{cmd.label}</span>
              {cmd.description && (
                <span className={styles.description}>{cmd.description}</span>
              )}
              <span className={styles.commandMeta}>
                {classifyCommand(cmd)} • {getCommandUsageCount(usageMap, cmd.id)} executions
              </span>
            </div>
          </button>
        ))}
      </div>

      {visibleCommands.length === 0 ? (
        <div className={styles.emptyState}>
          <span>NO EXECUTABLE COMMANDS REGISTERED.</span>
          <strong>WIRE COMMANDS INTO FOUNDERDASHBOARD TO ACTIVATE THIS PANEL.</strong>
        </div>
      ) : null}

      <div className={styles.meshGrid} aria-label="Command class distribution">
        {classMatrix.slice(0, 4).map((entry) => (
          <div key={entry.label} className={styles.meshCell}>
            <span>{entry.label}</span>
            <strong>{entry.value}</strong>
          </div>
        ))}
      </div>

      {executionReceipt ? (
        <div
          className={`${styles.receipt} ${
            executionReceipt.status === 'FRACTURE' ? styles.receiptError : styles.receiptSuccess
          }`}
        >
          <CheckCircle2 size={15} />
          <div>
            <span>{executionReceipt.status} • {executionReceipt.mode}</span>
            <strong>{executionReceipt.command}</strong>
            <p>{executionReceipt.message}</p>
          </div>
        </div>
      ) : null}

      <div className={styles.panelActions}>
        <button type="button" className={styles.resetButton} onClick={handleResetLearning}>
          <RotateCcw size={13} />
          Reset Learning
        </button>
        <span>Session: {sessionId || 'QUICK_PANEL'}</span>
      </div>
    </div>
  );
};

export default QuickPanel;
