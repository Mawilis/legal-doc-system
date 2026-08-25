/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - EXECUTIVE OPERATING CONSOLE [V1.0.0-PRODUCTION-GRADE]                                                                     ║
 * ║ [EPITOME: FG217 VISUAL SHELL OF THE OPERATING SYSTEM | DECLARATIVE RENDERER OVER KERNEL ABI]                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-PRODUCTION-GRADE | BILLION-DOLLAR ENTERPRISE SOFTWARE | BIBLICAL WORTH COMPLIANT                                       ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/operating-console/ExecutiveOperatingConsole.jsx          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Mandated the visual transformation of Wilsy OS into a live operating shell.                         ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Constructed the zero-local-state declarative console grid.                                   ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React from 'react';
import { useDashboard } from '../../hooks/useDashboard';
import { useExecution } from '../../hooks/useExecution';

import ConsoleHeader from './ConsoleHeader';
import RuntimePanel from './RuntimePanel';
import ExecutionPanel from './ExecutionPanel';
import EventTimeline from './EventTimeline';
import ArtifactExplorer from './ArtifactExplorer';
import GovernancePanel from './GovernancePanel';
import PredictionPanel from './PredictionPanel';
import DigitalTwinPanel from './DigitalTwinPanel';
import RepositoryPanel from './RepositoryPanel';
import VersionPanel from './VersionPanel';
import ReportsPanel from './ReportsPanel';
import SystemHealthPanel from './SystemHealthPanel';

/**
 * @function ExecutiveOperatingConsole
 * @description Master console rendering the visual shell of the Wilsy OS Kernel.
 * @returns {JSX.Element} Rendered sovereign operating console.
 * @collaboration Functions as the visual operating environment of Wilsy OS.
 */
export default function ExecutiveOperatingConsole() {
  const { dashboard, loading, error, refresh } = useDashboard(3000);
  const { executeCommand, isExecuting, lastResult } = useExecution();

  const handleAction = async (actionName) => {
    try {
      await executeCommand(actionName);
      refresh();
    } catch (err) {
      console.error(`[WILSY-CONSOLE] Action ${actionName} failed:`, err);
    }
  };

  if (loading && !dashboard) {
    return (
      <div style={{ background: '#090d16', color: '#38bdf8', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'monospace' }}>
        [WILSY OS KERNEL] CONNECTING TO SOVEREIGN RUNTIME...
      </div>
    );
  }

  const d = dashboard || {};

  return (
    <div data-wilsy-operating-console="true" style={{ padding: '24px', background: '#090d16', color: '#f8fafc', minHeight: '100vh', fontFamily: 'monospace' }}>
      <ConsoleHeader onAction={handleAction} isExecuting={isExecuting} />

      {error && (
        <div style={{ background: '#7f1d1d', border: '1px solid #f87171', color: '#fecaca', padding: '10px 14px', borderRadius: '4px', marginBottom: '20px', fontSize: '11px' }}>
          KERNEL TELEMETRY SYNC WARNING: {error}
        </div>
      )}

      {/* Grid Layout matching the FG217 Blueprint */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
        <RuntimePanel runtime={d.runtime} />
        <ExecutionPanel lastResult={lastResult} isExecuting={isExecuting} />
        <RepositoryPanel repository={d.repository} />

        <DigitalTwinPanel digitalTwin={d.digitalTwin} />
        <GovernancePanel governance={d.governance} />
        <PredictionPanel predictions={d.predictions} />

        <EventTimeline events={d.events} />
        <ArtifactExplorer artifacts={d.artifacts} />
        <ReportsPanel reports={d.reports} />

        <VersionPanel versioning={d.versioning} />
        <SystemHealthPanel engines={d.engines} />
      </div>
    </div>
  );
}
