/**
 * TITLE: WILSY OS Unified Task Execution Readiness
 * VERSION: v1.0.0-SOURCE-NEUTRAL-EXECUTION-READINESS
 * AUTHORITY: WILSY OS Core Governance
 * EPITOME: One source-neutral task-readiness panel; every fact is supplied by
 *          the owning source and unknown records remain explicitly unverified.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/workspaces/UnifiedTaskReadiness.jsx
 * COLLABORATION / OWNERSHIP: ProjectTasksPanel, MyWorkWorkspace, Python EOS source adapters.
 * CERTIFICATION / UPDATE DATE: 2026-11-26
 * CHANGELOG: v1.0.0-SOURCE-NEUTRAL-EXECUTION-READINESS extracts the same
 *            task readiness presentation for Projects and non-Projects tasks.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: No IO, state mutation, fabricated facts or dynamic authority.
 * TENANT BOUNDARY: Caller must independently verify source and authenticated scope.
 * FINANCIAL AUTHORITY BOUNDARY: No financial commands; Kennel EOS exclusively.
 */
import React from 'react';

export default function UnifiedTaskReadiness({
  revision = null, description, facts = [], actions = null,
  footnote = 'Task lifecycle does not certify supporting evidence, approvals or completion. Review the independently authorized source before changing state.',
}) {
  return <section className="mt-5 rounded-xl border border-blue-200 bg-blue-50 p-4"
    aria-label="Source-verified task execution readiness">
    <div className="flex flex-wrap items-start justify-between gap-2">
      <div>
        <h3 className="text-base font-bold text-blue-950">Execution readiness</h3>
        <p className="mt-1 text-sm text-blue-900">{description
          || 'Current EOS task facts. Evidence, approvals and execution remain independently governed.'}</p>
      </div>
      {revision !== null && <span className="rounded-md border border-blue-200 bg-white px-2 py-1 text-xs font-semibold text-blue-950">
        Revision {revision}
      </span>}
    </div>
    <dl className="mt-3 grid gap-2 sm:grid-cols-2">
      {facts.map(fact => <div key={fact.label} className="rounded-lg border border-blue-200 bg-white p-3">
        <dt className="text-xs font-semibold text-slate-600">{fact.label}</dt>
        <dd className="mt-1 break-words text-sm font-bold text-slate-950">{fact.value == null ? 'Not verified by this source' : fact.value}</dd>
      </div>)}
    </dl>
    {actions && <div className="mt-3 flex flex-wrap gap-2" aria-label="Task execution evidence actions">{actions}</div>}
    <p className="mt-3 text-xs leading-relaxed text-blue-950">{footnote}</p>
  </section>;
}

/*
 * ARTIFACT: UnifiedTaskReadiness.jsx
 * VERSION: v1.0.0-SOURCE-NEUTRAL-EXECUTION-READINESS
 * AUTHORITY BOUNDARY: Presentation only, independent EOS source ownership unchanged.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
