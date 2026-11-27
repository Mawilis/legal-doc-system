/**
 * TITLE: WILSY OS Unified Task Header
 * VERSION: v1.1.0-SHARED-EOS-STATUS-COLOURS
 * AUTHORITY: WILSY OS Core Governance
 * EPITOME: One task-detail header used by Projects and My Work without changing
 *          EOS source ownership or granting any task action.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/UnifiedTaskHeader.jsx
 * COLLABORATION / OWNERSHIP: ProjectTasksPanel, MyWorkWorkspace and Python EOS
 *                              source-owned task service adapters.
 * CERTIFICATION / UPDATE DATE: 2026-11-27
 * CHANGELOG: v1.1.0-SHARED-EOS-STATUS-COLOURS uses the same source-state semantic badge as Projects rows and People on shared task details across My Work, Calendar and Daily Attention.
 * CHANGELOG: v1.0.0-CANONICAL-SOURCE-NEUTRAL-TASK-PRESENTATION establishes one
 *            responsive, accessible task header shared by Projects and My Work.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Presentation-only, no network access or data persistence.
 * TENANT BOUNDARY: Caller independently validates tenant/principal/source scope.
 * FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS exclusively.
 */
import React from 'react';
import { workStatusClasses } from '../../theme/workStatus.js';

export default function UnifiedTaskHeader({
  kind = 'Task', source, title, status, due, owner,
  onClose, closeLabel = 'Close', closeRef = null, primaryControl = null,
  reviewNavigation = null, actions = null, titleId,
}) {
  return <header className="shrink-0 border-b border-slate-200 bg-white px-5 py-4 sm:px-7">
    <div className="flex items-center justify-between gap-3">
      <p className="min-w-0 text-xs font-bold uppercase tracking-wide text-slate-600">
        {kind} · {source} work
      </p>
      {primaryControl}
      <button type="button" ref={closeRef} onClick={onClose}
        className="inline-flex min-h-11 items-center rounded-lg border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-800 hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-700"
        aria-label={closeLabel}>{closeLabel}</button>
    </div>
    {reviewNavigation}
    <h2 id={titleId} className="mt-3 break-words text-2xl font-bold leading-tight text-slate-950">{title}</h2>
    <div className="mt-3 flex flex-wrap items-center gap-2 text-sm">
      <span className={workStatusClasses(status)}>{status}</span>
      <span className="rounded-md border border-slate-200 px-3 py-1.5 text-slate-800">{due || 'No due date'}</span>
      {owner && <span className="rounded-md border border-slate-200 px-3 py-1.5 text-slate-800">{owner}</span>}
    </div>
    {actions && <nav className="mt-3 flex flex-wrap gap-2" aria-label="Task execution actions">{actions}</nav>}
  </header>;
}

/*
 * ARTIFACT: UnifiedTaskHeader.jsx
 * VERSION: v1.1.0-SHARED-EOS-STATUS-COLOURS
 * AUTHORITY BOUNDARY: Shared UI only; all commands remain source-owned.
 * TENANT POSTURE: Caller validates exact tenant, principal and source identity.
 * FAIL-CLOSED POSTURE: No actions or authority created by this presentation component.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
